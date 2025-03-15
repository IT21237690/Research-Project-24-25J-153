import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, Range
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Qdrant Configuration
QDRANT_HOST = "research-project-qdrant-1"
QDRANT_PORT = 6333
COLLECTION_NAME = "passages_collection"

# Sentence Embeddings Model
MODEL_NAME = "all-MiniLM-L6-v2"
embedder = SentenceTransformer(MODEL_NAME, device='cpu')
VECTOR_SIZE = embedder.get_sentence_embedding_dimension()

# Initialize Qdrant Client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def retrieve_passages(target_difficulty, grade, top_k=5):
    """
    Retrieves passages from Qdrant based on target difficulty and grade.
    Logs the retrieved passages for debugging.
    """
    try:
        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="flesch_reading_ease",
                    range=Range(gte=target_difficulty - 10, lte=target_difficulty + 10)
                ),
                FieldCondition(
                    key="grade",
                    match={"value": grade}
                )
            ]
        )

        dummy_vector = [0.0] * VECTOR_SIZE
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=dummy_vector,
            query_filter=filter_condition,
            limit=top_k,
            with_payload=True
        )

        # Log the retrieved passages
        if search_result:
            logging.info(f"Retrieved {len(search_result)} passages from Qdrant for difficulty {target_difficulty} and grade {grade}:")
            for idx, passage in enumerate(search_result):
                passage_text = passage.payload.get("passage", "No passage found")
                readability = passage.payload.get("flesch_reading_ease", "Unknown")
                logging.info(f"Passage {idx + 1}: (Flesch Reading Ease: {readability}) {passage_text[:200]}...")
        else:
            logging.warning(f"No passages found for difficulty {target_difficulty} and grade {grade}.")

        return search_result

    except Exception as e:
        logging.error(f"Error retrieving passages from Qdrant: {str(e)}")
        return []
