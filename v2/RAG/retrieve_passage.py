from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np


def retrieve_passage(query, knowledge_base, model_name='all-MiniLM-L6-v2', top_k=3):
    """
    Retrieves the most relevant passages based on a query.
    Args:
        query (str): The input query.
        knowledge_base (list): List of passages and their embeddings.
        model_name (str): Pre-trained SentenceTransformer model name.
        top_k (int): Number of top results to return.
    Returns:
        list: Top-k most relevant passages.
    """
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query])

    embeddings = np.array([kb["embedding"] for kb in knowledge_base])
    similarities = cosine_similarity(query_embedding, embeddings).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]

    return [(knowledge_base[i]["chunk"], similarities[i]) for i in top_indices]


if __name__ == "__main__":
    with open("Datasets/knowledge_base_grade4.json", "r", encoding="utf-8") as file:
        knowledge_base = json.load(file)

    query = input("Enter your query: ")
    results = retrieve_passage(query, knowledge_base)

    print("\nTop results:")
    for i, (chunk, score) in enumerate(results):
        print(f"{i + 1}. (Score: {score:.4f})\n{chunk}\n")
