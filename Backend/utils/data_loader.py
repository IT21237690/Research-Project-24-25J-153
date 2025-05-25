from transformers import T5Tokenizer
import torch

class GrammarDataset(torch.utils.data.Dataset):
    def __init__(self, file_path, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.samples = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "|||" not in line:
                    print(f"Skipping invalid line: {line}")  # Warning for debugging
                    continue
                
                parts = line.split("|||")
                if len(parts) != 2:
                    print(f"Skipping malformed line: {line}")  # Handle unexpected format
                    continue
                
                incorrect, correct = parts
                self.samples.append((incorrect.strip(), correct.strip()))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        src, tgt = self.samples[idx]
        inputs = self.tokenizer(
            f"grammar: {src}", 
            max_length=self.max_length, 
            truncation=True, 
            padding="max_length",
            return_tensors="pt"
        )
        targets = self.tokenizer(
            tgt, 
            max_length=self.max_length, 
            truncation=True, 
            padding="max_length",
            return_tensors="pt"
        )
        return {
            "input_ids": inputs.input_ids.squeeze(),
            "attention_mask": inputs.attention_mask.squeeze(),
            "labels": targets.input_ids.squeeze()
        }
