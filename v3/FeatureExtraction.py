import numpy as np
import pandas as pd
import json
import torch
import torchaudio
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from tqdm import tqdm
from scipy.stats import zscore
import math

from v3.Inference.model import ProsodyAwareModel  # Import trained pronunciation model

# ✅ Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
use_half = device.type == "cuda"  # Enable FP16 if using GPU
print(f"🔥 Using device: {device}")

# -----------------------
# Load Whisper Processor & Model (fine-tuned)
# -----------------------
MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/whisper-finetuned-final"
processor = WhisperProcessor.from_pretrained(MODEL_PATH)
whisper_model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH).to(device).eval()
if use_half:
    whisper_model.half()  # Convert model parameters to FP16 for efficiency
    # Force-convert positional embeddings (if needed)
    whisper_model.model.encoder.embed_positions.weight = whisper_model.model.encoder.embed_positions.weight.half()

# ✅ Load the trained pronunciation (prosody-aware) model
model_path = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/prosody_contrastive_model.pth"
model = ProsodyAwareModel().to(device).eval()
model.load_state_dict(torch.load(model_path, map_location=device))
if use_half:
    model.half()  # Convert prosody-aware model to FP16

# ✅ Disable gradient computation globally
torch.set_grad_enabled(False)

print(f"Prosody-aware model in training mode? {model.training}")      # Should print False
print(f"Whisper model in training mode? {whisper_model.training}")      # Should print False


def extract_prosody_features_librosa(audio_path, sr=16000):
    """
    Extract prosodic features using Librosa.
    Returns:
       avg_pitch: Average pitch in Hz using librosa.pyin (ignores unvoiced frames).
       avg_intensity: Average RMS energy as a proxy for intensity.
    """
    try:
        y, _ = librosa.load(audio_path, sr=sr)
        f0, voiced_flag, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7')
        )
        avg_pitch = np.nanmean(f0)
        rms = librosa.feature.rms(y=y)
        avg_intensity = np.mean(rms)
    except Exception as e:
        print(f"❌ Error extracting prosodic features with Librosa from {audio_path}: {e}")
        avg_pitch, avg_intensity = 0.0, 0.0

    return avg_pitch, avg_intensity


def extract_features(audio_path):
    """
    Efficiently extract Whisper embeddings & prosodic features using GPU.
    Returns:
      whisper_embedding (tensor): The embedding from Whisper (used as input to the contrastive model).
      prosody_tensor (tensor): A 2-element tensor containing [avg_pitch, avg_intensity].
    """
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        waveform = waveform.to(device)
        if use_half:
            waveform = waveform.half()

        with torch.no_grad():
            inputs = processor(
                waveform.squeeze().cpu().numpy(),
                return_tensors="pt",
                sampling_rate=16000,
                padding=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            if use_half:
                inputs['input_features'] = inputs['input_features'].half()
            desired_length = 3000
            current_length = inputs['input_features'].shape[-1]
            if current_length < desired_length:
                pad_amount = desired_length - current_length
                inputs['input_features'] = torch.nn.functional.pad(
                    inputs['input_features'], (0, pad_amount), mode="constant", value=0)
            elif current_length > desired_length:
                inputs['input_features'] = inputs['input_features'][:, :, :desired_length]
            encoder_outputs = whisper_model.model.encoder(inputs['input_features']).last_hidden_state
            whisper_embedding = encoder_outputs.mean(dim=1).squeeze()
            if use_half:
                whisper_embedding = whisper_embedding.half()

        avg_pitch, avg_intensity = extract_prosody_features_librosa(audio_path, sr=16000)
        del waveform, inputs
        dtype = torch.float16 if use_half else torch.float32
        prosody_tensor = torch.tensor([avg_pitch, avg_intensity], dtype=dtype).to(device)
        return whisper_embedding, prosody_tensor

    except Exception as e:
        print(f"❌ Error extracting features from {audio_path}: {e}")
        return None, None


def get_pronunciation_embedding(audio_path):
    """
    Extracts the contrastive embedding (128-dimensional) from the prosody-aware model
    and computes a normalized pronunciation score.
    Returns:
       normalized_score (float): A scalar score computed from the embedding norm.
       embedding_vector (list of 128 floats): The full embedding from the model.
    """
    whisper_emb, prosody_features = extract_features(audio_path)
    if whisper_emb is None or prosody_features is None:
        return None, None

    with torch.no_grad():
        embedding = model(whisper_emb.unsqueeze(0), prosody_features.unsqueeze(0))  # shape: [1, 128]
    score = float(embedding.norm().cpu())
    normalized_score = math.log(1 + score) * 10
    return round(normalized_score, 2), embedding.cpu().squeeze().tolist()


def calculate_fluency(word_alignment, phoneme_alignment):
    """
    Compute fluency metrics.
    Returns a dictionary with:
       - speaking_rate: Words per second.
       - avg_pause: Average pause duration.
       - abnormal_phones: Count of abnormal phoneme durations.
    """
    try:
        if not word_alignment or not phoneme_alignment:
            print("⚠️ Warning: Empty word/phoneme alignments detected.")
            return {"speaking_rate": 0, "avg_pause": 0, "abnormal_phones": 0}

        total_duration = word_alignment[-1]['end'] - word_alignment[0]['start']
        speaking_rate = len(word_alignment) / total_duration if total_duration > 0 else 0
        pauses = [
            word['start'] - prev_end
            for prev_end, word in zip([word_alignment[0]['start']] + [w['end'] for w in word_alignment[:-1]], word_alignment)
            if word['start'] - prev_end > 0
        ]
        avg_pause = np.mean(pauses) if pauses else 0
        phone_durations = [p['end'] - p['start'] for p in phoneme_alignment]
        abnormal_duration_count = int(np.sum(np.abs(zscore(phone_durations)) > 2)) if phone_durations else 0

        return {
            'speaking_rate': round(speaking_rate, 2),
            'avg_pause': round(avg_pause, 2),
            'abnormal_phones': abnormal_duration_count
        }

    except Exception as e:
        print(f"❌ Error calculating fluency metrics: {e}")
        return {"speaking_rate": 0, "avg_pause": 0, "abnormal_phones": 0}


def process_file(row):
    """
    Process a single file:
      - Loads alignments.
      - Computes pronunciation embedding and score.
      - Computes fluency metrics.
      - Returns a dictionary containing:
          * audio_path
          * pronunciation_score (scalar)
          * speaking_rate, avg_pause, abnormal_phones
          * 128 embedding values as embed_0, embed_1, ..., embed_127
    """
    try:
        word_alignment = json.loads(row.word_alignment)
        phoneme_alignment = json.loads(row.phoneme_alignment)
        pronunciation_score, embedding_vector = get_pronunciation_embedding(row.audio_path)
        if pronunciation_score is None or embedding_vector is None:
            return None
        fluency_metrics = calculate_fluency(word_alignment, phoneme_alignment)
        result = {
            'audio_path': row.audio_path,
            'pronunciation_score': pronunciation_score,
            'speaking_rate': fluency_metrics["speaking_rate"],
            'avg_pause': fluency_metrics["avg_pause"],
            'abnormal_phones': fluency_metrics["abnormal_phones"]
        }
        for i, val in enumerate(embedding_vector):
            result[f"embed_{i}"] = val
        return result

    except Exception as e:
        print(f"❌ Error processing {row.audio_path}: {e}")
        return None


def main(alignment_csv, output_csv):
    """Main pipeline with optimized GPU memory management."""
    df = pd.read_csv(alignment_csv)
    results = []
    batch_size = 16
    for i, row in tqdm(enumerate(df.itertuples(index=False), 1), total=len(df)):
        features = process_file(row)
        if features is not None:
            results.append(features)
        if i % batch_size == 0:
            torch.cuda.empty_cache()
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"✅ Features saved to {output_csv}")


if __name__ == "__main__":
    main(
        "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/datasets/alignment_results.csv",
        "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/datasets/features.csv"
    )
