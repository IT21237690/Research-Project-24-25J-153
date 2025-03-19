import os
import librosa
import torch
import re
from torch.utils.data import Dataset
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrainerCallback,
)
from transformers.trainer_utils import get_last_checkpoint

from torch.nn.utils.rnn import pad_sequence
from typing import List, Dict, Any


# -------------------------------
# Custom Dataset for Children's Speech
# -------------------------------
class ChildrensSpeechDataset(Dataset):
    def __init__(self, data_dir: str, processor: WhisperProcessor, sampling_rate: int = 16000):
        """
        Assumes that each .wav file in data_dir is named with its transcription.
        For example: "the_quick_brown_fox.wav" -> transcription: "the quick brown fox"
        It also removes any trailing parenthesized numbers from the filename.
        """
        self.data_dir = data_dir
        self.processor = processor
        self.sampling_rate = sampling_rate
        # Get list of .wav files in the directory
        self.file_paths = [
            os.path.join(data_dir, fname) for fname in os.listdir(data_dir) if fname.endswith(".wav")
        ]

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        file_path = self.file_paths[idx]
        basename = os.path.basename(file_path)
        # Remove file extension and replace underscores with spaces
        transcription = os.path.splitext(basename)[0].replace('_', ' ')
        # Remove any trailing number inside parentheses (e.g., " (3)")
        transcription = re.sub(r'\s*\(\d+\)$', '', transcription)
        # Load the audio file with librosa at the target sampling rate
        audio, _ = librosa.load(file_path, sr=self.sampling_rate)
        return {"audio": audio, "transcription": transcription}



class ClearGpuCacheCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return control


# -------------------------------
# Preprocessing Function
# -------------------------------
def preprocess_function(sample: Dict[str, any]) -> Dict[str, torch.Tensor]:
    """
    Process a single sample: convert raw audio into input features and tokenize the transcription.
    """
    # Use the processor's feature extractor to process raw audio
    input_features = processor.feature_extractor(
        sample["audio"], sampling_rate=16000, return_tensors="pt"
    ).input_features[0]  # remove batch dimension

    # Directly tokenize the transcription (no context manager needed)
    labels = processor.tokenizer(sample["transcription"], return_tensors="pt").input_ids[0]

    # Replace any padding token IDs in labels with -100 so they are ignored in loss computation.
    labels[labels == processor.tokenizer.pad_token_id] = -100

    return {"input_features": input_features, "labels": labels}


# -------------------------------
# Data Collator for Padding
# -------------------------------
def data_collator(features: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """
    Pads a batch of features so that they can be converted into tensors.
    """
    input_features = [f["input_features"] for f in features]
    labels = [f["labels"] for f in features]

    # Pad input features using the processor's built-in pad function.
    batch_inputs = processor.feature_extractor.pad(
        {"input_features": input_features}, return_tensors="pt"
    )

    # Pad labels manually using PyTorch's pad_sequence.
    batch_labels = pad_sequence(labels, batch_first=True, padding_value=processor.tokenizer.pad_token_id)

    return {"input_features": batch_inputs["input_features"], "labels": batch_labels}


# -------------------------------
# Main Fine-Tuning Script
# -------------------------------

# Choose the model size. Here we use "openai/whisper-small" for a good trade-off on a 3.8GB GPU.
model_name = "openai/whisper-small"

# Load the processor and model.
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# Configure the model to transcribe English. This sets the forced decoder tokens.
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")

# Define the path to your dataset directory (update this to your own path)
data_dir = "/v3/Raw_data"  # e.g., "/home/user/childrens_speech/"
dataset = ChildrensSpeechDataset(data_dir, processor)

# Preprocess the dataset. Here, we preprocess each sample once and store the result.
# If you prefer on-the-fly processing, you can integrate the preprocess_function into your DataLoader.
preprocessed_data = [preprocess_function(sample) for sample in dataset]

# Define training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/whisper-finetuned",
    per_device_train_batch_size=2,  # Adjust based on your GPU memory
    num_train_epochs=10,             # Set as needed
    learning_rate=1e-5,             # Starting learning rate; tune as necessary
    fp16=False,                    # Enable mixed precision training (if supported by your GPU)
    logging_strategy="epoch",     # Log metrics at the end of every epoch
    logging_dir="/v3/models/logs",  # Directory to save log files
    save_strategy="epoch",        # Save model checkpoints at the end of each epoch
    eval_strategy="no",           # No evaluation set specified; disable evaluation
    save_total_limit=1,           # Keep only the latest checkpoint
    remove_unused_columns=False,
    gradient_accumulation_steps=4,
    use_cpu=True,
)


# Create the Trainer object.
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=preprocessed_data,
    data_collator=data_collator,
    tokenizer=processor.feature_extractor,  # used for padding input features
    callbacks=[ClearGpuCacheCallback()],
)


# Check for the last checkpoint in the output directory.
last_checkpoint = get_last_checkpoint(training_args.output_dir)
if last_checkpoint is not None:
    print(f"Resuming training from checkpoint: {last_checkpoint}")
else:
    print("No checkpoint found, starting training from scratch.")


# Start fine-tuning, resuming from the last checkpoint if it exists.
trainer.train(resume_from_checkpoint=last_checkpoint)

# Save the final model (optional)
final_model_dir = "/v3/models/whisper-finetuned-final"
trainer.save_model(final_model_dir)

# Save the used processor as well so that it can be loaded with the fine-tuned model later.
processor.save_pretrained(final_model_dir)
