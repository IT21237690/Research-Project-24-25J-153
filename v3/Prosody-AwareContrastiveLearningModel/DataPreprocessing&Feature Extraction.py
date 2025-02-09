import os
import numpy as np
import pandas as pd
import torchaudio
import parselmouth
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from tqdm import tqdm

# Load Wav2Vec2 model & processor
MODEL_NAME = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
wav2vec_model = Wav2Vec2Model.from_pretrained(MODEL_NAME).eval()

# Paths
DATA_DIR = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/Raw_data"  # Change this to your dataset path
FEATURES_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/Prosody-AwareContrastiveLearningModel/features.csv"

# Function to extract Wav2Vec2 embeddings
def extract_wav2vec2_embedding(audio_path):
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)
    inputs = processor(waveform.squeeze().numpy(), return_tensors="pt", sampling_rate=16000, padding=True)
    with torch.no_grad():
        outputs = wav2vec_model(**inputs).last_hidden_state.mean(dim=1)  # Average over time
    return outputs.squeeze().numpy()

# Function to extract prosodic features
def extract_prosodic_features(audio_path):
    sound = parselmouth.Sound(audio_path)
    pitch = sound.to_pitch()
    intensity = sound.to_intensity()

    pitch_values = pitch.selected_array['frequency']
    intensity_values = intensity.values.T.flatten()

    avg_pitch = np.mean(pitch_values[pitch_values > 0])  # Ignore 0 values
    avg_intensity = np.mean(intensity_values)
    return avg_pitch, avg_intensity

# Process all files
data = []
for file in tqdm(os.listdir(DATA_DIR)):
    if file.endswith(".wav"):
        audio_path = os.path.join(DATA_DIR, file)
        try:
            wav2vec_embedding = extract_wav2vec2_embedding(audio_path)
            avg_pitch, avg_intensity = extract_prosodic_features(audio_path)
            data.append({
                "audio_path": audio_path,
                "wav2vec_embedding": wav2vec_embedding.tolist(),
                "avg_pitch": avg_pitch,
                "avg_intensity": avg_intensity
            })
        except Exception as e:
            print(f"Error processing {file}: {e}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(FEATURES_CSV, index=False)
print(f"✅ Feature extraction complete! Data saved to {FEATURES_CSV}")
