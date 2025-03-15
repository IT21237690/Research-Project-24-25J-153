from pydantic import BaseModel

class DifficultyRequest(BaseModel):
    current_difficulty: float
    user_answer: str

class DifficultyResponse(BaseModel):
    question: str
    gold_answer: str
    user_answer: str
    similarity: float
    reward: float
    predicted_adjustment: float
    updated_difficulty: float

class PassageResponse(BaseModel):
    passage: str
    readability: float | None
    grade: int
