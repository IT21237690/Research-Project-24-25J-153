import json

# Load the JSON file
input_file = "Datasets/Main/finalDataset1.json"  # Replace with your file name
output_file = "Datasets/Main/finalDataset.json"

with open(input_file, "r") as file:
    data = json.load(file)

# Function to replace the string in the dataset
def replace_unscramble_type(data):
    for passage in data:
        for question in passage.get("Questions", []):
            if question.get("type") == 2:
                question["type"] =1
    return data

# Update the dataset
updated_data = replace_unscramble_type(data)

# Save the updated JSON file
with open(output_file, "w") as file:
    json.dump(updated_data, file, indent=4)

print(f"Updated dataset saved to {output_file}.")
