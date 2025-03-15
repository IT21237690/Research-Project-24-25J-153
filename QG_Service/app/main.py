from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .services import generate_question

# Initialize FastAPI app
app = FastAPI(title="Question Generation API", version="1.0")

# Request Body Model
class QuestionRequest(BaseModel):
    passage: str
    question_type: str  # Either "SAQ" or "JSQ"

# API Endpoint for question generation
@app.post("/generate_question/")
async def generate_question_api(request: QuestionRequest):
    """
    Generate a question from a passage.
    """
    try:
        question = generate_question(request.passage, request.question_type)
        return {"generated_question": question}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {e}")

# Run with: uvicorn app.main:app --reload
