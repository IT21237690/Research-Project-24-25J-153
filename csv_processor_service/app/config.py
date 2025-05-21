from qdrant_client import QdrantClient
from pymongo import MongoClient



# Initialize MongoDB client (update URI, database, and collection as needed)
MONGO_URI = "mongodb+srv://dbuser:dbuser123@researchproject.ojxgd.mongodb.net/?retryWrites=true&w=majority&appName=ResearchProject"
DATABASE_NAME = "rp_db"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
uploads_collection = db["files"]

# Qdrant Configuration
QDRANT_HOST = "20.193.146.113"
QDRANT_PORT = 6333
COLLECTION_NAME = "passages_collection"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output size

# Initialize Qdrant Client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Check if the collection already exists
all_collections = qdrant_client.get_collections()
existing_collections = {c.name for c in all_collections.collections}

if COLLECTION_NAME not in existing_collections:
    # Only create the collection if it does not already exist
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={"size": VECTOR_SIZE, "distance": "Cosine"},
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")
else:
    print(f"Collection '{COLLECTION_NAME}' already exists. Proceeding without recreating.")
