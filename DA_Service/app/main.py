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