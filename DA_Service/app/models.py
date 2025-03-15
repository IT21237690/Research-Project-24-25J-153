from pydantic import BaseModel


class DifficultyRequest(BaseModel):
    current_difficulty: int
    user_answer: str
    passage: str          # Add this field
    question: str         # Add this field


class DifficultyResponse(BaseModel):
    question: str
    gold_answer: str
    user_answer: str
    similarity: float
    reward: float
    predicted_adjustment: float
    updated_difficulty: float


