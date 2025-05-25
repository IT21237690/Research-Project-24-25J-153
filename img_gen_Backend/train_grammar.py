from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from transformers import DataCollatorForSeq2Seq
from torch.utils.data import Dataset
import torch

class GrammarDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=128):
        self.data = []
        with open(file_path, 'r') as f:
            for line in f:
                inc, cor = line.strip().split('\t')
                self.data.append((inc, cor))
        
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        src = f"grammar: {self.data[idx][0]}"
        tgt = self.data[idx][1]
        
        inputs = self.tokenizer(
            src, 
            max_length=self.max_length,
            truncation=True,
            padding='max_length'
        )
        
        targets = self.tokenizer(
            tgt,
            max_length=self.max_length,
            truncation=True,
            padding='max_length'
        )
        
        return {
            'input_ids': torch.tensor(inputs.input_ids),
            'attention_mask': torch.tensor(inputs.attention_mask),
            'labels': torch.tensor(targets.input_ids)
        }

def train_model():
    # Initialize model and tokenizer
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    
    # Load datasets
    train_dataset = GrammarDataset("data/train.txt", tokenizer)
    val_dataset = GrammarDataset("data/val.txt", tokenizer)
    
    # Training configuration
    training_args = TrainingArguments(
        output_dir="./models/grammar_model",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer)
    )
    
    # Start training
    trainer.train()
    
    # Save final model
    model.save_pretrained("./models/grammar_model")
    tokenizer.save_pretrained("./models/grammar_model")

if __name__ == "__main__":
    train_model()