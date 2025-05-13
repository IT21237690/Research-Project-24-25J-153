from pydantic import BaseModel
import datetime


class FileUploadResponse(BaseModel):
    message: str


class PassageResponse(BaseModel):
    passage: str
    readability: float | None
    grade: int

class FileData(BaseModel):
    file_name: str
    file: str  # base64 encoded file data
    userid: str
    uploaded_date: datetime.datetime