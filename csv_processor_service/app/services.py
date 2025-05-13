import pandas as pd
import uuid  # Generate unique IDs
from qdrant_client.http.models import PointStruct, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
from .config import qdrant_client, COLLECTION_NAME, VECTOR_SIZE
from .utils import compute_flesch_reading_ease, get_embedding


def ensure_collection_exists():
    """Ensure the Qdrant collection exists. Create it if it doesn't exist, but do not delete existing data."""
    try:
        collections = qdrant_client.get_collections()
        existing_collections = {collection.name for collection in collections.collections}

        if COLLECTION_NAME not in existing_collections:
            # Create collection without deleting existing data
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance="Cosine"),
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully.")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists. Proceeding with insertion.")

    except UnexpectedResponse as e:
        raise RuntimeError(f"Failed to check or create collection: {e}")


def process_csv_and_insert_to_qdrant(contents: bytes):
    """
    Process CSV, compute readability scores, generate embeddings,
    and insert new data into Qdrant without overwriting existing data.
    """
    # Ensure collection exists before proceeding
    ensure_collection_exists()

    try:
        df = pd.read_csv(pd.io.common.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise ValueError(f"Invalid CSV file: {e}")

    if "Passage" not in df.columns:
        raise ValueError("CSV file must contain a 'Passage' column.")

    points = []

    for _, row in df.iterrows():
        passage = row["Passage"]
        if pd.isna(passage) or str(passage).strip() == "":
            continue

        flesch_score = compute_flesch_reading_ease(passage)
        vector = get_embedding(passage)
        grade = row["Grade"] if "Grade" in df.columns else None

        payload = {
            "passage": passage,
            "flesch_reading_ease": flesch_score,
            "grade": grade
        }

        # Generate a unique ID using UUID
        unique_id = str(uuid.uuid4())

        points.append(PointStruct(id=unique_id, vector=vector, payload=payload))

    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        return "Successfully inserted new passages into Qdrant without overwriting existing data."

    return "No valid passages found in the CSV."