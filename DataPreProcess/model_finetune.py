import os
import json
import pandas as pd
import torchaudio
from tqdm import tqdm
from datasets import Dataset
from transformers import (
    Wav2Vec2Processor,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Trainer,
    pipeline,
)

class DataCollatorForWav2Vec2:
    def _init_(self, processor):
        self.processor = processor

    def _call_(self, features):
        # Extract input_values and labels
        input_values = [feature['input_values'] for feature in features]
        labels = [feature['labels'] for feature in features]

        # Prepare a dictionary for input_values and labels
        input_dict = {"input_values": input_values}
        label_dict = {"input_ids": labels}

        # Use the processor's padding method for input_values (audio) and labels (text)
        input_values = self.processor.feature_extractor.pad(input_dict, padding=True, return_tensors="pt")["input_values"]
        labels = self.processor.tokenizer.pad(label_dict, padding=True, return_tensors="pt")["input_ids"]

        # Return the padded batch
        batch = {
            'input_values': input_values,
            'labels': labels
        }

        return batch

def preprocess(batch):
    try:
        audio_path = os.path.join(DATA_PATH, "audio", batch["audio"])
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load the audio file
        audio, sampling_rate = torchaudio.load(audio_path)

        # Resample to the target sampling rate of 16kHz
        resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
        audio = resampler(audio).squeeze()

        # Ensure that the audio is float32 (standard for audio features)
        audio = audio.numpy().astype('float32')  # Convert to numpy array with float32 dtype

        # Apply processor with padding (for audio)
        input_values = processor.feature_extractor(audio, sampling_rate=16000, padding=True, return_tensors="pt").input_values[0]
        batch["input_values"] = input_values.numpy().astype('float32')  # Ensure consistency in input values

        # Load transcription
        transcription_path = os.path.join(DATA_PATH, "transcriptions", batch["transcription"])
        with open(transcription_path, "r", encoding="utf-8") as f:  # Ensure UTF-8 encoding
            transcription = f.read().strip()

        # Tokenize transcription with padding (for text)
        batch["labels"] = processor.tokenizer(transcription, padding=True, return_tensors="pt").input_ids[0].numpy().astype('int64')  # Ensure consistency in labels

        return batch
    except Exception as e:a
    print(f"[ERROR] Failed to process {batch['audio']}: {e}")
    return {}  # Return an empty dictionary instead of None


if _name_ == '_main_':
    # Constants
    DATA_PATH = "../dataset"
    OUTPUT_MODEL_PATH = "../wav2vec2_finetuned"
    HUGGINGFACE_MODEL_NAME = "facebook/wav2vec2-base"

    # Load paths.json
    print("[INFO] Loading paths.json...")
    with open(os.path.join(DATA_PATH, "path_file.json"), "r") as f:
        paths = json.load(f)

    # Convert JSON to Pandas DataFrame
    paths_df = pd.DataFrame(paths)
    assert "audio" in paths_df.columns and "transcription" in paths_df.columns, \
        "[ERROR] The JSON file must have 'audio' and 'transcription' keys."

    # Convert to Hugging Face Dataset
    print("[INFO] Preparing dataset...")
    dataset = Dataset.from_pandas(paths_df)

    # Initialize Wav2Vec2 processor
    processor = Wav2Vec2Processor.from_pretrained(HUGGINGFACE_MODEL_NAME)

    # Apply preprocessing with filtering invalid entries
    print("[INFO] Preprocessing dataset...")
    dataset = dataset.map(preprocess, remove_columns=["audio", "transcription"], num_proc=1)
    dataset = dataset.filter(lambda x: x != {})  # Filter out empty dictionaries
    print("[INFO] Dataset preprocessing complete.")

    # Fine-Tuning Wav2Vec 2.0
    print("[INFO] Setting up Wav2Vec2 model...")
    model = Wav2Vec2ForCTC.from_pretrained(HUGGINGFACE_MODEL_NAME, vocab_size=processor.tokenizer.vocab_size)

    training_args = TrainingArguments(
        output_dir=OUTPUT_MODEL_PATH,
        eval_strategy="no",  # Avoid evaluation if no eval_dataset is provided
        save_strategy="epoch",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=1e-4,
        warmup_steps=500,
        num_train_epochs=3,
        fp16=False,
        save_total_limit=2,
        logging_dir="./logs",
        logging_steps=10,
        dataloader_num_workers=4,
    )

    data_collator = DataCollatorForWav2Vec2(processor=processor)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=processor.tokenizer,  # Use the tokenizer directly for padding and other operations
        data_collator=data_collator,  # Use the custom data collator for padding
    )

    print("[INFO] Starting fine-tuning...")
    trainer.train()
    print("[INFO] Fine-tuning complete. Saving the model...")
    trainer.save_model(OUTPUT_MODEL_PATH)
    processor.save_pretrained(OUTPUT_MODEL_PATH)
    print(f"[INFO] Model saved at {OUTPUT_MODEL_PATH}.")