import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 1.1: Load the dataset with embeddings
with open("Datasets/grade3_with_embeddings.json", "r") as file:
    dataset = json.load(file)


# Step 1.2: Define a function to retrieve relevant passages
def retrieve_relevant_passages(query, dataset, top_k=3):
    # Encode the query
    query_embedding = model.encode([query])

    # Extract all the passage embeddings from the dataset
    passage_embeddings = [entry["embedding"] for entry in dataset]

    # Compute cosine similarity between query and passages
    similarities = cosine_similarity(query_embedding, passage_embeddings)

    # Get the indices of the top-k most similar passages
    top_k_indices = np.argsort(similarities[0])[::-1][:top_k]

    # Retrieve the top-k most similar passages
    top_passages = [dataset[i] for i in top_k_indices]

    return top_passages


# Step 1.3: Example usage
query = "What should you do to greet someone?"
top_k_passages = retrieve_relevant_passages(query, dataset, top_k=3)

# Print the top-k passages
for idx, passage in enumerate(top_k_passages, 1):
    print(f"Passage {idx}: {passage['passage']}")
