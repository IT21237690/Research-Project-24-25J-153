import random
import json

# Define replacement mappings for nouns, verbs, and other elements
replacements = {
    "nouns": ["dog", "cat", "bird", "fish", "rabbit", "tree", "house", "car", "ball", "book"],
    "verbs": ["is sitting", "is lying", "is running", "is jumping", "is flying", "is walking"],
    "locations": ["on the mat", "under the table", "in the park", "in the house", "in the garden"],
}

# Function to load the existing dataset (replace 'your_dataset_file.json' with actual filename)
def load_existing_dataset(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to determine the difficulty based on passage length
def determine_difficulty(passage_text):
    word_count = len(passage_text.split())
    if word_count < 10:
        return "easy"
    elif word_count <= 20:
        return "medium"
    else:
        return "hard"

# Function to generate short-answer questions based on a passage
def generate_short_answer_questions(passage):
    new_questions = []

    # Remove any existing MCQs (we assume the original MCQs are present)
    passage["Questions"] = [q for q in passage["Questions"] if q["type"] != "mcq"]

    # Generate new short-answer questions based on passage content
    new_questions.append({
        "type": "short_answer",
        "question": "Where does Tom go to play?",
        "answer": "Park",  # Adjust based on passage details
        "explanation": "The passage says Tom goes to the park every day."
    })
    new_questions.append({
        "type": "short_answer",
        "question": "What does Tom like to play?",
        "answer": "Football",  # Adjust based on passage details
        "explanation": "It is mentioned in the first sentence that Tom likes to play football."
    })

    # Add a scrambled sentence question
    sentence = passage["passage"]
    scrambled_sentence = " ".join(random.sample(sentence.split(), len(sentence.split())))
    new_questions.append({
        "type": "Unscramble the following sentence:",
        "question": f"{scrambled_sentence}",
        "answer": sentence,
        "explanation": "The student needs to unscramble the words back into the original sentence."
    })

    passage["Questions"] = new_questions  # Replace with newly generated short-answer questions
    return passage

# Function to augment the dataset by generating new passages and questions
def augment_dataset(existing_data, num_passages):
    augmented_data = []

    for i in range(num_passages):
        base_passage = random.choice(existing_data)  # Pick a random passage from existing data

        # Determine difficulty based on passage length
        base_passage["difficulty"] = determine_difficulty(base_passage["passage"])

        augmented_passage = generate_short_answer_questions(base_passage)  # Modify passage
        augmented_data.append(augmented_passage)

    return augmented_data

# Load your existing dataset (change filename if necessary)
filename = "Datasets/testData.json"  # Replace with the actual path to your dataset
existing_data = load_existing_dataset(filename)

# Augment the dataset (generate 100 new passages with short-answer questions)
augmented_dataset = augment_dataset(existing_data, 300)

# Save the augmented dataset to a new JSON file
output_path = "Datasets/testdatafinal.json"
with open(output_path, "w") as file:
    json.dump(augmented_dataset, file, indent=4)

print(f"Augmented dataset saved to {output_path}")
