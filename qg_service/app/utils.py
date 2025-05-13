import textstat
from sentence_transformers import SentenceTransformer

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_flesch_reading_ease(passage: str):
    """Compute the Flesch Reading Ease score for a passage."""
    try:
        return textstat.flesch_reading_ease(passage)
    except Exception as e:
        print(f"Error processing passage: {e}")
        return None

def get_embedding(passage: str):
    """Generate a sentence embedding for the passage."""
    return embedding_model.encode(passage).tolist()
