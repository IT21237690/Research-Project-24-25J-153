from qdrant_client import QdrantClient

# Qdrant Configuration
QDRANT_HOST = "research-project-qdrant-1"
QDRANT_PORT = 6333
COLLECTION_NAME = "passages_collection"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output size

# Initialize Qdrant Client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Ensure collection exists
qdrant_client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config={"size": VECTOR_SIZE, "distance": "Cosine"}
)
