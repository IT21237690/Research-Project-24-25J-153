from pydantic import BaseModel

class FileUploadResponse(BaseModel):
    message: str


class PassageResponse(BaseModel):
    passage: str
    readability: float | None
    grade: int
