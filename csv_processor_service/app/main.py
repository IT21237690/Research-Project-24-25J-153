from fastapi import FastAPI, UploadFile, File, HTTPException
from .services import process_csv_and_insert_to_qdrant  # Use relative import
from .models import FileUploadResponse  # Use relative import

app = FastAPI(title="Passage Processing API", version="1.0")

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
