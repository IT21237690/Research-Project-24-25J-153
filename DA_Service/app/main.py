from fastapi import FastAPI, HTTPException
from .models import DifficultyRequest, DifficultyResponse
from .services.retrieval_service import retrieve_passages
from .services.qg_service import generate_question
from .services.qa_service import evaluate_answer
from .services.adjustment_service import load_adjustment_model, predict_adjustment
from .services.db import results_collection  # Import MongoDB collection

app = FastAPI(title="Difficulty Adjustment Microservice")

# Load the ML adjustment model at startup
ml_model = load_adjustment_model()


@app.get("/")
def root():
    return {"message": "Welcome to the Difficulty Adjustment API"}


@app.post("/adjust_difficulty/{user_id}", response_model=DifficultyResponse)
async def adjust_difficulty(user_id: str, payload: DifficultyRequest):
    """
    Handles the full pipeline: Retrieves passages, generates a question, evaluates the answer,
    predicts difficulty adjustments, and saves the evaluation data to MongoDB.
    """
    try:
        # Retrieve passages matching difficulty
        retrieved = retrieve_passages(payload.current_difficulty, top_k=1)  # Use only 1 passage
        if not retrieved:
            raise HTTPException(status_code=404, detail="No passages found for the given difficulty.")

        selected = retrieved[0]
        passage_text = selected.payload.get("passage", "")
        readability = selected.payload.get("flesch_reading_ease", None)  # Extract readability

        # Generate a question from the passage
        question = generate_question(passage_text)
        if question.strip().lower() == "no question generated":
            raise HTTPException(status_code=500, detail="Question Generation failed.")

        # Evaluate the user answer via QA microservice
        reward, gold_answer, similarity = evaluate_answer(payload.user_answer, passage_text, question)

        # Pass readability to the prediction function
        predicted_adjustment = predict_adjustment(ml_model, payload.current_difficulty, similarity, reward)

        # Update difficulty ensuring it stays within bounds (0 to 120)
        new_difficulty = max(0, min(120, payload.current_difficulty + predicted_adjustment))

        # Save evaluation data to MongoDB
        record = {
            "user_id": user_id,
            "question": question,
            "user_answer": payload.user_answer,
            "gold_answer": gold_answer,
            "passage": passage_text,
            "similarity": similarity,
            "predicted_adjustment": predicted_adjustment,
            "updated_difficulty": new_difficulty,
            "readability": readability
        }
        results_collection.insert_one(record)

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
