from pydantic import BaseModel

class QARequest(BaseModel):
    question: str
    context: str

class QAResponse(BaseModel):
    answer: str
