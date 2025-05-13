from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime
from .retrieval_service import retrieve_passages
from .services import process_csv_and_insert_to_qdrant  # Use relative import
from .models import FileUploadResponse, PassageResponse, FileData  # Use relative import
from .config import uploads_collection
import pytz
import base64


app = FastAPI(title="Passage Processing API", version="1.0")

# Add CORSMiddleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_csv/{user_id}", response_model=FileUploadResponse)
async def upload_csv(user_id: str, file: UploadFile = File(...)):
    """
    API endpoint for uploading CSV, processing data, storing in Qdrant,
    and saving the uploaded file metadata into MongoDB.

    The file is saved to MongoDB with the following fields:
      - file_name: the name of the uploaded file
      - file: the file contents (as bytes)
      - userid: user_id passed as a path parameter
      - uploaded_date: the current UTC datetime
    """
    try:
        # Read file contents
        contents = await file.read()

        # Process CSV and insert passages into Qdrant
        message = process_csv_and_insert_to_qdrant(contents)

        # Convert current time to Sri Lankan time (Asia/Colombo)
        sl_timezone = pytz.timezone("Asia/Colombo")
        uploaded_date = datetime.datetime.now(sl_timezone)

        # Save the uploaded file to MongoDB
        upload_document = {
            "file_name": file.filename,
            "file": contents,  # you might consider storing as binary if needed
            "userid": user_id,
            "uploaded_date": uploaded_date
        }
        uploads_collection.insert_one(upload_document)

        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

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


@app.get("/files/{user_id}", response_model=List[FileData])
async def get_uploaded_files(user_id: str):
    """
    Retrieve all uploaded files for a given user id from MongoDB.
    """
    try:
        # Query the MongoDB collection for documents with the given user_id
        results = list(uploads_collection.find({"userid": user_id}))
        if not results:
            raise HTTPException(status_code=404, detail="No files found for the given user id.")

        files = []
        for doc in results:
            file_data = doc.get("file")
            # If file_data is stored as bytes, encode to base64 string
            if isinstance(file_data, bytes):
                file_data_b64 = base64.b64encode(file_data).decode("utf-8")
            else:
                file_data_b64 = str(file_data)

            file_entry = FileData(
                file_name=doc.get("file_name"),
                file=file_data_b64,
                userid=doc.get("userid"),
                uploaded_date=doc.get("uploaded_date")
            )
            files.append(file_entry)

        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {e}")
