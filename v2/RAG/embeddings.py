import json
from sentence_transformers import SentenceTransformer

# Initialize the Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')


# Function to generate embeddings and update dataset
def generate_embeddings(input_file, output_file):
    # Read the original dataset from the input JSON file
    with open(input_file, 'r') as f:
        dataset = json.load(f)

    # Process each passage in the dataset to generate embeddings
    for entry in dataset:
        passage = entry["passage"]

        # Generate the embedding for the passage
        embedding = model.encode(passage)

        # Add the embedding to the entry
        entry["embedding"] = embedding.tolist()  # Convert numpy array to list for JSON serialization

    # Save the updated dataset with embeddings to a new output file
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=4)

    print(f"Updated dataset with embeddings saved to {output_file}")


# Example usage
input_file = 'Datasets/testData.json'  # Path to your original dataset file
output_file = 'Datasets/testData_embedding.json'  # Path to save the updated dataset

generate_embeddings(input_file, output_file)
