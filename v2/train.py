import os
import numpy as np
import jiwer
import torch
from datasets import load_dataset
from transformers import (
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor,
    Wav2Vec2Processor,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Trainer
)

from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class CustomDataCollatorCTCWithPadding:
    processor: Any
    padding: Union[bool, str] = True

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        # 1. Separate the audio inputs from the labels
        input_features = [{"input_values": f["input_values"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]

        # 2. Pad the audio inputs (input_values)
        batch_audio = self.processor.feature_extractor.pad(
            input_features,
            padding=self.padding,
            return_tensors="pt"
        )

        # 3. Pad the labels
        with self.processor.as_target_processor():
            batch_labels = self.processor.tokenizer.pad(
                label_features,
                padding=self.padding,
                return_tensors="pt"
            )

        # Replace the tokenizer's pad token in the labels with -100 for the CTC loss
        labels = batch_labels["input_ids"].masked_fill(
            batch_labels["input_ids"] == self.processor.tokenizer.pad_token_id, -100
        )

        # Return a dictionary containing the model inputs
        batch_audio["labels"] = labels
        return batch_audio


# 1) Load your phoneme tokenizer
tokenizer = Wav2Vec2CTCTokenizer(
    "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/phoneme_vocab.json",
    unk_token="<unk>",
    pad_token="<pad>",
    word_delimiter_token="|"
)

# 2) Create feature extractor & processor
feature_extractor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    do_normalize=True,
    return_attention_mask=True
)

processor = Wav2Vec2Processor(
    feature_extractor=feature_extractor,
    tokenizer=tokenizer
)

# 3) Load a pretrained Wav2Vec2ForCTC model with custom vocab_size
vocab_size = len(tokenizer)
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-base-960h",
    vocab_size=vocab_size,
    ignore_mismatched_sizes=True
)

print("Model final classification head:", model.lm_head)

# -----------------------------------------------------------------------------
# 4) Load Dataset (CSV) and Map to input_values & labels
# -----------------------------------------------------------------------------
import torchaudio

data_files = {
    "train": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/train_phonemes.csv",
    "validation": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/val_phonemes.csv",
    "test": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/test_phonemes.csv"
}

dataset = load_dataset("csv", data_files=data_files)
print(dataset)


def load_audio_and_encode(batch):
    audio_path = batch["audio_path"]
    speech, sr = torchaudio.load(audio_path)

    # Convert to mono if needed:
    if speech.shape[0] > 1:
        speech = speech.mean(dim=0, keepdim=True)

    # Resample if not 16k
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        speech = resampler(speech)
        sr = 16000

    speech = speech.squeeze().numpy()

    # 2. Extract audio features
    audio_features = feature_extractor(
        speech,
        sampling_rate=sr,
        return_tensors="pt"
    )

    # 3. Convert phoneme_sequence -> list of IDs
    phonemes = batch["phoneme_sequence"].split()
    input_ids = tokenizer.convert_tokens_to_ids(phonemes)

    batch["input_values"] = audio_features["input_values"][0]
    batch["attention_mask"] = audio_features["attention_mask"][0]
    batch["labels"] = input_ids
    return batch


dataset = dataset.map(
    load_audio_and_encode,
    remove_columns=dataset["train"].column_names,
    num_proc=1
)

print("Mapped dataset structure:", dataset)

# -----------------------------------------------------------------------------
# 5) Define Data Collator for CTC
# -----------------------------------------------------------------------------
data_collator = CustomDataCollatorCTCWithPadding(
    processor=processor,
    padding=True
)


# -----------------------------------------------------------------------------
# 6) Define a Metric (Phoneme-level WER or PER)
#    We'll treat each phoneme as a "word" for WER.
# -----------------------------------------------------------------------------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    pred_str = []
    label_str = []

    for i in range(len(labels)):
        # Gather non-padded label IDs (CTC uses -100 for padding)
        label_ids = labels[i][labels[i] != -100].tolist()
        # Convert IDs -> phoneme tokens
        label_tokens = tokenizer.convert_ids_to_tokens(label_ids)
        # Join them with spaces
        label_phonemes = " ".join(label_tokens)
        label_str.append(label_phonemes)

        # Same for predictions
        pred_ids = predictions[i]

        # Collapse repeated tokens for CTC
        pred_ids_collapsed = []
        prev_id = None
        for pid in pred_ids:
            if pid != prev_id and pid != -100:
                pred_ids_collapsed.append(pid)
            prev_id = pid

        pred_tokens = tokenizer.convert_ids_to_tokens(pred_ids_collapsed)
        pred_phonemes = " ".join(pred_tokens)
        pred_str.append(pred_phonemes)

    # JiWER on phoneme sequences => effectively phoneme error rate
    wer_value = jiwer.wer(label_str, pred_str)
    return {"wer": wer_value}


# -----------------------------------------------------------------------------
# 7) Define Training Arguments
# -----------------------------------------------------------------------------
training_args = TrainingArguments(
    output_dir="./ctc_model_output",
    overwrite_output_dir=True,
    num_train_epochs=5,  # tweak for your dataset size
    per_device_train_batch_size=2,  # adjust per GPU memory
    per_device_eval_batch_size=2,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps=200,
    learning_rate=1e-4,
    warmup_steps=200,
    save_total_limit=1,
    fp16=True,  # if your GPU supports AMP
    report_to="none"  # or "tensorboard", "wandb", etc.
)

# -----------------------------------------------------------------------------
# 8) Initialize Trainer
# -----------------------------------------------------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=feature_extractor,  # or just processor
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

# -----------------------------------------------------------------------------
# 9) Train
# -----------------------------------------------------------------------------
trainer.train()

# -----------------------------------------------------------------------------
# 10) Evaluate on Test Set & Save
# -----------------------------------------------------------------------------
test_results = trainer.evaluate(dataset["test"])
print("Test Set Results:", test_results)

# Save final model & processor
trainer.save_model("./final_ctc_model")
processor.save_pretrained("./final_ctc_processor")

print("Training completed and model saved!")
