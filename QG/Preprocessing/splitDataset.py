import torch
import json
from sklearn.model_selection import train_test_split
from transformers import T5Tokenizer

# Load dataset from JSON file
with open('/home/minidu-tissera/PycharmProjects/Research-Project/v8/Datasets/formatted_data.json', 'r') as f:  # Replace with the path to your JSON file
    dataset = json.load(f)

# Initialize the tokenizer for the model (T5 in this case)
tokenizer = T5Tokenizer.from_pretrained("t5-small")

# Tokenize the dataset (inputs and outputs)
tokenized_data = []

for item in dataset:
    input_text = item['input']
    output_text = item['output']
    task = item['task']

    # Convert task to integer encoding
    task_encoding = 0 if task == "SAQ" else 1

    # Tokenize the input and output
    input_encoding = tokenizer(input_text, padding='max_length', truncation=True, max_length=256, return_tensors='pt')
    output_encoding = tokenizer(output_text, padding='max_length', truncation=True, max_length=64, return_tensors='pt')

    # Add the tokenized data to the list
    tokenized_data.append({
        'input_ids': input_encoding['input_ids'].squeeze(0),  # Squeeze to remove unnecessary batch dimension
        'attention_mask': input_encoding['attention_mask'].squeeze(0),
        'decoder_input_ids': output_encoding['input_ids'].squeeze(0),  # Decoder input for output
        'task': torch.tensor(task_encoding, dtype=torch.long)
    })

# Split the data into training (70%) and temp_data (30%)
train_data, temp_data = train_test_split(tokenized_data, test_size=0.3, random_state=42)

# Further split temp_data into validation (20%) and test (10%)
val_data, test_data = train_test_split(temp_data, test_size=0.33, random_state=42)

# Convert datasets into PyTorch tensors
def create_tensor_dataset(data):
    return {
        'input_ids': torch.stack([d['input_ids'] for d in data]),
        'attention_mask': torch.stack([d['attention_mask'] for d in data]),
        'decoder_input_ids': torch.stack([d['decoder_input_ids'] for d in data]),
        'task': torch.stack([d['task'] for d in data])
    }

train_tensor = create_tensor_dataset(train_data)
val_tensor = create_tensor_dataset(val_data)
test_tensor = create_tensor_dataset(test_data)

# Save the datasets as .pt files
torch.save(train_tensor, '/home/minidu-tissera/PycharmProjects/Research-Project/v8/Training/train_dataset.pt')
torch.save(val_tensor, '/home/minidu-tissera/PycharmProjects/Research-Project/v8/Training/val_dataset.pt')
torch.save(test_tensor, '/home/minidu-tissera/PycharmProjects/Research-Project/v8/Training/test_dataset.pt')

# Print the shapes of the datasets
print("Training Dataset Shapes:")
print(train_tensor['input_ids'].shape)
print(train_tensor['attention_mask'].shape)
print(train_tensor['decoder_input_ids'].shape)
print(train_tensor['task'].shape)

print("\nValidation Dataset Shapes:")
print(val_tensor['input_ids'].shape)
print(val_tensor['attention_mask'].shape)
print(val_tensor['decoder_input_ids'].shape)
print(val_tensor['task'].shape)

print("\nTest Dataset Shapes:")
print(test_tensor['input_ids'].shape)
print(test_tensor['attention_mask'].shape)
print(test_tensor['decoder_input_ids'].shape)
print(test_tensor['task'].shape)

# Summary of dataset
print(f"\nTraining data: {len(train_tensor['input_ids'])} samples")
print(f"Validation data: {len(val_tensor['input_ids'])} samples")
print(f"Test data: {len(test_tensor['input_ids'])} samples")
