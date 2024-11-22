import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AdamW, get_linear_schedule_with_warmup
from datasets import load_dataset, Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
import json


# Load your dataset (replace with your actual dataset path)
def load_data():
    # Load the JSON file with your dataset
    with open('Datasets/grade3_with_embeddings.json', 'r') as file:
        data = json.load(file)

    # Extract passages and questions for training the model
    texts = []
    for entry in data:
        passage = entry["passage"]
        for question in entry["questions"]:
            # Combine passage and question for training (adjust if needed)
            if question["type"] == "mcq" or question["type"] == "short_answer":
                texts.append(f"{passage} Question: {question['question']} Answer: {question['answer']}")

    return texts


# Tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # Set padding token

# Model: GPT2 for language modeling (adjust for your needs)
model = GPT2LMHeadModel.from_pretrained("gpt2")


# Data Preparation
def encode_texts(texts):
    """Tokenizes the input texts"""
    return tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")


# Prepare the data
texts = load_data()
encoded_data = encode_texts(texts)


# Create a PyTorch Dataset
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encoded_data):
        self.input_ids = encoded_data['input_ids']
        self.attention_mask = encoded_data['attention_mask']

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx]
        }


# Create DataLoader
dataset = CustomDataset(encoded_data)
train_dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Optimizer and Scheduler
optimizer = AdamW(model.parameters(), lr=5e-5)
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0,
                                            num_training_steps=len(train_dataloader) * 3)  # 3 epochs


# Training Loop
def train(model, train_dataloader, optimizer, scheduler):
    model.train()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    for epoch in range(3):  # Train for 3 epochs (adjust if needed)
        epoch_loss = 0
        for batch in tqdm(train_dataloader, desc=f"Epoch {epoch + 1}"):
            # Move tensors to device
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            # Forward pass
            outputs = model(input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss
            epoch_loss += loss.item()

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

        avg_loss = epoch_loss / len(train_dataloader)
        print(f"Epoch {epoch + 1} - Loss: {avg_loss}")

    # Save the fine-tuned model
    model.save_pretrained("Model/fine_tuned_model")
    tokenizer.save_pretrained("Model/tokenizer")


# Start Training
train(model, train_dataloader, optimizer, scheduler)
