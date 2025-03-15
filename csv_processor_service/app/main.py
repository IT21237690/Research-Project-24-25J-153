from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .retrieval_service import retrieve_passages
from .services import process_csv_and_insert_to_qdrant  # Use relative import
from .models import FileUploadResponse, PassageResponse  # Use relative import

app = FastAPI(title="Passage Processing API", version="1.0")

# Add CORSMiddleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_csv/", response_model=FileUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """API endpoint for uploading CSV, processing data, and storing in Qdrant."""
    try:
        contents = await file.read()
        message = process_csv_and_insert_to_qdrant(contents)
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
