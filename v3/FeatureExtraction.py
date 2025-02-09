import numpy as np
import pandas as pd
import parselmouth
import json
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from tqdm import tqdm
from scipy.stats import zscore

from v3.model import ProsodyAwareModel  # Import trained model architecture

# ✅ Check if GPU is available and use it
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")  # Should print 'cuda' if GPU is available

# ✅ Load Wav2Vec2 Processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")

# ✅ Load Wav2Vec2 Model and move to GPU
wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h").to(device)
wav2vec_model.eval()

# ✅ Load the trained pronunciation model
model_path = "/v3/models/prosody_contrastive_model.pth"
model = ProsodyAwareModel().to(device)  # Move model to GPU
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# ✅ Disable gradient computation globally
torch.set_grad_enabled(False)

# ✅ Debugging: Ensure models are NOT in training mode
print(f"Model in training mode? {model.training}")  # Should print False
print(f"Wav2Vec2 in training mode? {wav2vec_model.training}")  # Should print False


def extract_features(audio_path):
    """Extract Wav2Vec2 embeddings & prosodic features using GPU"""
    try:
        # ✅ Load audio file
        waveform, sample_rate = torchaudio.load(audio_path)
        if sample_rate != 16000:
            waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)

        # ✅ Move waveform to GPU
        waveform = waveform.to(device)

        # ✅ Extract Wav2Vec2 embeddings (on GPU)
        inputs = processor(waveform.squeeze().cpu().numpy(), return_tensors="pt", sampling_rate=16000, padding=True).to(device)
        with torch.no_grad():
            wav2vec_embedding = wav2vec_model(**inputs).last_hidden_state.mean(dim=1).squeeze()

        # ✅ Extract prosodic features (remains on CPU)
        sound = parselmouth.Sound(audio_path)
        pitch = sound.to_pitch()
        intensity = sound.to_intensity()

        avg_pitch = np.mean(pitch.selected_array['frequency'][pitch.selected_array['frequency'] > 0])  # Ignore zeros
        avg_intensity = np.mean(intensity.values.T.flatten())

        return wav2vec_embedding, torch.tensor([avg_pitch, avg_intensity], dtype=torch.float32).to(device)

    except Exception as e:
        print(f"❌ Error extracting features from {audio_path}: {e}")
        return None, None


def predict_pronunciation_score(audio_path):
    """Compute pronunciation score using trained contrastive model"""
    wav2vec_emb, prosody_features = extract_features(audio_path)

    if wav2vec_emb is None or prosody_features is None:
        return None  # Skip processing if feature extraction failed

    with torch.no_grad():  # ✅ Ensure inference mode
        embedding = model(wav2vec_emb.unsqueeze(0), prosody_features.unsqueeze(0))  # ✅ Keep batch dimension

    return float(embedding.norm().cpu())  # ✅ Move result back to CPU for numerical processing


def calculate_fluency(word_alignment, phoneme_alignment):
    """Compute fluency metrics"""
    try:
        duration = max(w['end'] for w in word_alignment) if word_alignment else 0
        words_per_sec = len(word_alignment) / duration if duration > 0 else 0

        pauses = []
        prev_end = 0
        for word in word_alignment:
            if prev_end > 0:
                pauses.append(word['start'] - prev_end)
            prev_end = word['end']
        avg_pause = np.mean(pauses) if pauses else 0

        phone_durations = [p['end'] - p['start'] for p in phoneme_alignment]
        abnormal_duration_count = np.sum(np.abs(zscore(phone_durations)) > 2) if phone_durations else 0

        return {'speaking_rate': words_per_sec, 'avg_pause': avg_pause, 'abnormal_phones': abnormal_duration_count}

    except Exception as e:
        print(f"❌ Error calculating fluency metrics: {e}")
        return {"speaking_rate": 0, "avg_pause": 0, "abnormal_phones": 0}


def process_file(row):
    """Process a single file for pronunciation & fluency analysis"""
    try:
        word_alignment = json.loads(row['word_alignment'])
        phoneme_alignment = json.loads(row['phoneme_alignment'])

        # ✅ Compute pronunciation score using contrastive learning model
        pronunciation_score = predict_pronunciation_score(row['audio_path'])
        if pronunciation_score is None:
            return None  # Skip this file if feature extraction failed

        # ✅ Compute fluency features
        fluency_metrics = calculate_fluency(word_alignment, phoneme_alignment)

        return {
            'audio_path': row['audio_path'],
            'pronunciation_score': pronunciation_score,
            'speaking_rate': fluency_metrics["speaking_rate"],
            'avg_pause': fluency_metrics["avg_pause"],
            'abnormal_phones': fluency_metrics["abnormal_phones"]
        }

    except Exception as e:
        print(f"❌ Error processing {row['audio_path']}: {e}")
        return None


def main(alignment_csv, output_csv):
    """Main feature extraction pipeline"""
    df = pd.read_csv(alignment_csv)

    results = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        features = process_file(row)
        if features is not None:  # Only add valid results
            results.append(features)

    # ✅ Save extracted features
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"✅ Features saved to {output_csv}")


if __name__ == "__main__":
    main(
        "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/alignment_results.csv",
        "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/features.csv"
    )
