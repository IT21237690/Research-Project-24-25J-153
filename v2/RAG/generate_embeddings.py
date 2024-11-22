from sentence_transformers import SentenceTransformer
import json


def generate_embeddings(chunks, model_name='all-MiniLM-L6-v2'):
    """
    Generates embeddings for a list of text chunks.
    Args:
        chunks (list): List of text chunks.
        model_name (str): Pre-trained SentenceTransformer model name.
    Returns:
        list: List of embeddings.
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks)
    return embeddings


if __name__ == "__main__":
    with open("Datasets/chunked_text.json", "r", encoding="utf-8") as file:
        chunks = json.load(file)

    embeddings = generate_embeddings(chunks)

    # Combine chunks and embeddings
    knowledge_base = [{"chunk": chunk, "embedding": embedding.tolist()} for chunk, embedding in zip(chunks, embeddings)]

    with open("Datasets/knowledge_base_grade4.json", "w", encoding="utf-8") as file:
        json.dump(knowledge_base, file, indent=4)

    print("Embeddings generated and saved to 'knowledge_base.json'")
