from fastapi import FastAPI
from .services import get_answer
from .models import QARequest, QAResponse

app = FastAPI(title="Question Answering API")

@app.get("/")
def root():
    return {"message": "Welcome to the Question Answering API"}

@app.post("/qa", response_model=QAResponse)
async def question_answer(payload: QARequest):
    answer = get_answer(payload.question, payload.context)
    return {"answer": answer}
