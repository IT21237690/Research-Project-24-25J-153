from evaluate import load  # Use evaluate instead of datasets.load_metric
import torch
from datasets import Dataset, DatasetDict
from transformers import (
    Wav2Vec2ForCTC,
    Wav2Vec2Processor,
    Trainer,
    TrainingArguments,
)
from transformers.trainer_callback import TrainerCallback
import torchaudio
import json
from typing import Dict, List, Union
import logging

# Configure logging
logging.basicConfig(
    filename="/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/logs/training.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger(__name__)

wer_metric = load("wer")

# Paths
TRAIN_FILE = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/dataset/train.json"
VAL_FILE = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/dataset/val.json"
TEST_FILE = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/dataset/test.json"
MODEL_NAME = "facebook/wav2vec2-base-960h"

# Custom Data Collator with Padding
class CustomDataCollatorCTCWithPadding:
    def __init__(self, processor, padding=True):
        self.processor = processor
        self.padding = padding

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_values = [feature["input_values"] for feature in features]
        labels = [feature["labels"] for feature in features]

        # Pad input values
        batch = self.processor.feature_extractor.pad(
            {"input_values": input_values},
            padding=self.padding,
            return_tensors="pt",
        )

        # Pad labels
        labels_batch = self.processor.tokenizer.pad(
            {"input_ids": labels},
            padding=self.padding,
            return_tensors="pt",
        )

        # Replace padding with -100 for loss calculation
        labels_batch["input_ids"] = labels_batch["input_ids"].masked_fill(
            labels_batch["input_ids"] == self.processor.tokenizer.pad_token_id, -100
        )

        # Validate target_lengths
        target_lengths = (labels_batch["input_ids"] != -100).sum(dim=1)
        if (target_lengths < 0).any():
            raise ValueError(f"Invalid target_lengths detected: {target_lengths}")

        # Add labels to batch
        batch["labels"] = labels_batch["input_ids"]

        return batch



# Step 1: Load Dataset
def load_custom_dataset(train_file, val_file, test_file):
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(val_file, "r") as f:
        val_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)

    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)
    test_dataset = Dataset.from_list(test_data)

    train_dataset = train_dataset.rename_columns({"audio_path": "path", "transcription": "text"})
    val_dataset = val_dataset.rename_columns({"audio_path": "path", "transcription": "text"})
    test_dataset = test_dataset.rename_columns({"audio_path": "path", "transcription": "text"})

    return DatasetDict({"train": train_dataset, "validation": val_dataset, "test": test_dataset})


# Step 2: Preprocessing
def preprocess(batch):
    audio, rate = torchaudio.load(batch["path"])
    resampler = torchaudio.transforms.Resample(orig_freq=rate, new_freq=16000)
    audio = resampler(audio).squeeze().numpy()

    # Normalize amplitude
    audio = audio / max(abs(audio)) if max(abs(audio)) != 0 else audio

    batch["input_values"] = processor(audio, sampling_rate=16000).input_values[0]

    # Tokenize text for labels
    labels = processor.tokenizer(batch["text"], padding=False, truncation=True).input_ids
    if not labels:
        logger.warning(f"Empty labels for transcription: {batch['text']}")
        labels = [processor.tokenizer.pad_token_id]  # Use pad_token_id as a fallback
    batch["labels"] = labels

    return batch



# Define a function to compute evaluation metrics
def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = torch.argmax(torch.tensor(pred_logits), dim=-1)
    pred_texts = processor.batch_decode(pred_ids, skip_special_tokens=True)

    label_ids = pred.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    label_texts = processor.batch_decode(label_ids, skip_special_tokens=True)

    logger.info(f"Predictions: {pred_texts}")
    logger.info(f"References: {label_texts}")

    # Handle empty references or predictions
    filtered_preds = []
    filtered_labels = []
    for pred_text, label_text in zip(pred_texts, label_texts):
        if label_text.strip():  # Ensure reference is not empty
            filtered_preds.append(pred_text)
            filtered_labels.append(label_text)
        else:
            logger.warning(f"Empty or invalid reference. Prediction: {pred_text}")

    if not filtered_labels:
        logger.error("No valid references available for WER computation.")
        return {"wer": float("nan")}

    wer = wer_metric.compute(predictions=filtered_preds, references=filtered_labels)
    logger.info(f"Computed WER: {wer}")
    return {"wer": wer}



# Custom logging callback
class LogResultsCallback(TrainerCallback):
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics:
            logger.info(f"Epoch {state.epoch:.1f} | Evaluation Metrics: {metrics}")
            print(f"Epoch {state.epoch:.1f} | Evaluation Metrics: {metrics}")  # Log to terminal as well


# Load processor and model
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME, pad_token_id=processor.tokenizer.pad_token_id)

# Load and preprocess dataset
dataset = load_custom_dataset(TRAIN_FILE, VAL_FILE, TEST_FILE)
dataset = dataset.map(preprocess, remove_columns=["path", "text", "duration"] if "duration" in dataset["train"].column_names else ["path", "text"])

# Use a data collator for dynamic padding
data_collator = CustomDataCollatorCTCWithPadding(processor=processor, padding=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/wav2vec2-finetuned",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=15,
    logging_dir="/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/logs",  # Logging directory
    logging_steps=500,  # Log every 500 steps
    save_strategy="epoch",  # Save checkpoint after every epoch
    save_total_limit=1,  # Keep only the latest checkpoint
    learning_rate=1e-5,
    warmup_steps=1000,
    eval_strategy="epoch",  # Run validation after every epoch
    eval_accumulation_steps=4,  # Accumulate eval steps to handle large batches
    fp16=False,  # Enable mixed precision
    dataloader_num_workers=2,
    disable_tqdm=False,  # Show progress bar in terminal
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    data_collator=data_collator,
    callbacks=[LogResultsCallback()],  # Log evaluation results
    compute_metrics=compute_metrics,  # Add metric computation
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/wav2vec2-finetuned")
processor.save_pretrained("/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/wav2vec2-processor")

print("Fine-tuning complete!")
