from difflib import SequenceMatcher

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from .models import DifficultyRequest, DifficultyResponse  # Removed PassageResponse
from .services.qa_service import evaluate_answer
from .services.adjustment_service import load_adjustment_model, predict_adjustment
from .services.db import results_collection, users_collection  # MongoDB collections

app = FastAPI(title="Difficulty Adjustment Microservice")

# Add CORSMiddleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the ML adjustment model at startup
ml_model = load_adjustment_model()


@app.get("/")
def root():
    return {"message": "Welcome to the Difficulty Adjustment API"}


@app.post("/adjust_difficulty/{user_id}/{grade}", response_model=DifficultyResponse)
async def adjust_difficulty(user_id: str, grade: int, payload: DifficultyRequest):
    """
    Evaluates the user's answer and adjusts the difficulty level accordingly.

    For 'saq' (short answer questions):
      - Uses the QA microservice to evaluate the user's answer.

    For 'jsq' (jumbled sentence questions):
      - Skips the QA service.
      - Uses the passage (correct sentence) as the gold answer.
      - Computes similarity between the user's answer and the passage.

    In both cases, the system then predicts a difficulty adjustment,
    updates the user's difficulty (ensuring bounds 0 to 120),
    and logs evaluation data to MongoDB.
    """
    try:
        # Use the passage and question provided in the payload
        passage_text = payload.passage
        question = payload.question

        if payload.question_type.lower() == "saq":
            # Evaluate using the QA microservice as usual.
            reward, gold_answer, similarity = evaluate_answer(payload.user_answer, passage_text, question)
        elif payload.question_type.lower() == "jsq":
            # For jumble sentence questions, treat the passage as the correct sentence.
            gold_answer = passage_text
            similarity = SequenceMatcher(None, payload.user_answer.lower(), gold_answer.lower()).ratio()
            reward = 1.0 if similarity >= 0.7 else (-1.0 if similarity <= 0.3 else 0.0)
        else:
            # If question_type is not recognized, default to standard evaluation.
            reward, gold_answer, similarity = evaluate_answer(payload.user_answer, passage_text, question)

        # Predict difficulty adjustment using the ML model
        predicted_adjustment = predict_adjustment(ml_model, payload.current_difficulty, similarity, reward)

        # Update difficulty ensuring it stays within bounds (0 to 120)
        new_difficulty = max(0, min(120, payload.current_difficulty + predicted_adjustment))

        # Log evaluation data to MongoDB
        record = {
            "user_id": user_id,
            "question": question,
            "user_answer": payload.user_answer,
            "gold_answer": gold_answer,
            "passage": passage_text,
            "similarity": similarity,
            "predicted_adjustment": predicted_adjustment,
            "updated_difficulty": new_difficulty,
            "grade": grade,
            "question_type": payload.question_type,
        }
        results_collection.insert_one(record)

        # Update the user's difficulty level in MongoDB
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"currentDifficulty": new_difficulty}}
        )

        return DifficultyResponse(
            question=question,
            gold_answer=gold_answer,
            user_answer=payload.user_answer,
            similarity=similarity,
            reward=reward,
            predicted_adjustment=predicted_adjustment,
            updated_difficulty=new_difficulty,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/update_score/{user_id}/{final_fluency_score}/{current_flesch_score}")
def update_score(user_id: str,final_fluency_score: str, current_flesch_score: str):
    """
    Computes an updated Flesch score based on the final fluency score and current Flesch score.

    For a high fluency score, we want the updated score to be much closer to the challenging target,
    and for a low fluency score, much closer to an easier target.

    Parameters:
      - current_flesch_score (float): The current Flesch Reading Ease score.
      - final_fluency_score (float): The composite fluency score in [0, 1].

    Returns:
      - updated_score (float): The new Flesch score after adjustment.
    """

    # Convert string parameters to float
    final_fluency_score = float(final_fluency_score)
    current_flesch_score = float(current_flesch_score)
    # Compute target Flesch: lower is more challenging, higher is easier.
    target_flesch = 100 - (final_fluency_score * 50)

    # Define a scaling factor that amplifies the weight.
    # Here, we choose a factor (e.g., 2.5) so that for final_fluency_score=0.9,
    # the weight on the target becomes 1.0, and for final_fluency_score=0.5 it’s 0.
    # This means:
    # - For final_fluency_score >= 0.5, weight_target scales as (final_fluency_score - 0.5)*2.5 (clipped to 1.0)
    # - For final_fluency_score < 0.5, weight_target scales as (0.5 - final_fluency_score)*2.5 (clipped to 1.0)

    if final_fluency_score >= 0.5:
        weight_target = min(1.0, (final_fluency_score - 0.5) * 2.5)
    else:
        weight_target = min(1.0, (0.5 - final_fluency_score) * 2.5)

    # Updated score blends current and target based on weight_target.
    # When weight_target is 1, the updated score equals target_flesch.
    updated_score = (current_flesch_score * (1 - weight_target)) + (target_flesch * weight_target)


    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"fluencyDifficulty": updated_score}}
    )
    return {"updated_score": updated_score}



