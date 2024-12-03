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
    DataCollator
)

class DataCollatorForWav2Vec2:
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, features):
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



# Constants
DATA_PATH = "/home/bhagya/Documents/Research/pp1/dataset"
OUTPUT_MODEL_PATH = "/home/bhagya/Documents/Research/pp1/wav2vec2_finetuned"
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

def preprocess(batch):
    try:
        audio_path = os.path.join(DATA_PATH, "audio", batch["audio"])
        if not os.path.exists(audio_path):
            print(f"[ERROR] Audio file not found: {audio_path}")
            return None
        
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
        with open(transcription_path, "r") as f:
            transcription = f.read().strip()
        
        # Tokenize transcription with padding (for text)
        batch["labels"] = processor.tokenizer(transcription, padding=True, return_tensors="pt").input_ids[0].numpy().astype('int64')  # Ensure consistency in labels
        
        return batch
    except Exception as e:
        print(f"[ERROR] Failed to process {batch['audio']}: {e}")
        return None




# Apply preprocessing with progress bar
print("[INFO] Preprocessing dataset...")
dataset = dataset.map(preprocess, remove_columns=["audio", "transcription"], num_proc=4)
print("[INFO] Dataset preprocessing complete.")

# Fine-Tuning Wav2Vec 2.0
print("[INFO] Setting up Wav2Vec2 model...")
model = Wav2Vec2ForCTC.from_pretrained(HUGGINGFACE_MODEL_NAME, vocab_size=processor.tokenizer.vocab_size)
tokenizer = processor.tokenizer  # The tokenizer is used for padding

training_args = TrainingArguments(
    output_dir=OUTPUT_MODEL_PATH,
    evaluation_strategy="no",  # Avoid evaluation if no eval_dataset is provided
    save_strategy="epoch",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=1e-4,
    warmup_steps=500,
    num_train_epochs=10,
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
    tokenizer=tokenizer,  # Use the tokenizer directly for padding and other operations
    data_collator=data_collator,  # Use the custom data collator for padding

    # tokenizer=processor.feature_extractor,
    # data_collator=data_collator,  # Ensure padding is handled in the collator

)

print("[INFO] Starting fine-tuning...")
trainer.train()
print("[INFO] Fine-tuning complete. Saving the model...")
trainer.save_model(OUTPUT_MODEL_PATH)
processor.save_pretrained(OUTPUT_MODEL_PATH)
print(f"[INFO] Model saved at {OUTPUT_MODEL_PATH}.")

# Generate Kaldi data files
print("[INFO] Generating Kaldi data files...")
os.makedirs("kaldi_data", exist_ok=True)
with open("kaldi_data/wav.scp", "w") as wav_scp, open("kaldi_data/text", "w") as text, open("kaldi_data/utt2spk", "w") as utt2spk:
    for idx, row in tqdm(paths_df.iterrows(), total=len(paths_df), desc="Generating Kaldi files"):
        utt_id = f"utt{idx+1}"
        wav_path = os.path.join(DATA_PATH, "audio", row["audio"])
        wav_scp.write(f"{utt_id} {wav_path}\n")
        
        transcription_path = os.path.join(DATA_PATH, "transcriptions", row["transcription"])
        with open(transcription_path, "r") as f:
            transcription = f.read().strip()
        text.write(f"{utt_id} {transcription}\n")
        utt2spk.write(f"{utt_id} speaker{idx % 10}\n")
print("[INFO] Kaldi data files generated in kaldi_data/.")

# Generate Feedback using Hugging Face Text Generation
print("[INFO] Generating pronunciation feedback...")
feedback_generator = pipeline("text-generation", model="gpt2")

def get_feedback(transcription):
    prompt = f"Analyze the following transcription: '{transcription}'. Feedback: Identify pronunciation issues and suggest corrections."
    response = feedback_generator(prompt, max_length=150, num_return_sequences=1)
    return response[0]["generated_text"]

for idx, row in tqdm(paths_df.iterrows(), total=len(paths_df), desc="Generating Feedback"):
    transcription_path = os.path.join(DATA_PATH, "transcriptions", row["transcription"])
    with open(transcription_path, "r") as f:
        transcription = f.read().strip()
    feedback = get_feedback(transcription)
    print(f"Feedback for {row['audio']}:\n{feedback}\n")

print("[INFO] All tasks completed successfully!")
