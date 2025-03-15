from bson import ObjectId
from fastapi import FastAPI, HTTPException
from .models import DifficultyRequest, DifficultyResponse, PassageResponse
from .services.retrieval_service import retrieve_passages
from .services.qg_service import generate_question
from .services.qa_service import evaluate_answer
from .services.adjustment_service import load_adjustment_model, predict_adjustment
from .services.db import results_collection, users_collection  # Import MongoDB collection

app = FastAPI(title="Difficulty Adjustment Microservice")

# Load the ML adjustment model at startup
ml_model = load_adjustment_model()


@app.get("/")
def root():
    return {"message": "Welcome to the Difficulty Adjustment API"}


@app.post("/adjust_difficulty/{user_id}/{grade}", response_model=DifficultyResponse)
async def adjust_difficulty(user_id: str, grade: int, payload: DifficultyRequest):
    """
    Handles the full pipeline: Retrieves passages based on difficulty and grade, generates a question, evaluates the answer,
    predicts difficulty adjustments, updates the user's difficulty level, and saves evaluation data to MongoDB.

    Parameters:
    - user_id: Unique identifier for the user.
    - grade: Grade level to filter passages.
    - payload: Contains the current difficulty and user_answer.
    """
    try:
        # Retrieve passages matching difficulty and grade
        retrieved = retrieve_passages(payload.current_difficulty, grade, top_k=1)  # Use only 1 passage
        if not retrieved:
            raise HTTPException(status_code=404, detail="No passages found for the given difficulty and grade.")

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
            "readability": readability,
            "grade": grade
        }
        results_collection.insert_one(record)

        # ✅ Update the user's difficulty level in MongoDB
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


@app.get("/retrieve_passage/{difficulty}/{grade}", response_model=PassageResponse)
async def get_initial_passage(difficulty: float, grade: int):
    """
    Retrieves an initial passage based on the user's difficulty level and grade.

    Parameters:
    - difficulty: User's current difficulty level.
    - grade: User's grade level.

    Returns:
    - A passage that matches the difficulty and grade.
    """
    try:
        retrieved = retrieve_passages(difficulty, grade, top_k=1)  # Retrieve one passage
        if not retrieved:
            raise HTTPException(status_code=404, detail="No passages found for the given difficulty and grade.")

        selected = retrieved[0]
        passage_text = selected.payload.get("passage", "")
        readability = selected.payload.get("flesch_reading_ease", None)

        return PassageResponse(
            passage=passage_text,
            readability=readability,
            grade=grade
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
