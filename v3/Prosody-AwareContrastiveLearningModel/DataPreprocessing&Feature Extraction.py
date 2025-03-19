import os
import numpy as np
import pandas as pd
import torchaudio
import parselmouth
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from tqdm import tqdm
import torch.nn.functional as F

# ✅ Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")

# ✅ Load your fine-tuned Whisper model & processor
MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/whisper-finetuned-final"
processor = WhisperProcessor.from_pretrained(MODEL_PATH)
whisper_model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH).to(device).eval()

# Paths
DATA_DIR = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/Raw_data"
FEATURES_CSV = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/Prosody-AwareContrastiveLearningModel/featuresforprosody.csv"


# Function to extract Whisper embeddings (using the encoder outputs)
def extract_whisper_embedding(audio_path):
    waveform, sample_rate = torchaudio.load(audio_path)

    # ✅ Ensure waveform is mono and resampled to 16kHz
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)

    # ✅ Move waveform to device
    waveform = waveform.to(device)

    # ✅ Process the waveform to extract input features (log-mel spectrogram)
    inputs = processor(waveform.squeeze().cpu().numpy(), sampling_rate=16000, return_tensors="pt", padding=True).to(
        device)
    input_features = inputs.input_features  # shape: (batch, feature_size, time)

    # ✅ Ensure the time dimension is exactly 3000
    desired_length = 3000
    current_length = input_features.shape[-1]
    if current_length < desired_length:
        pad_amount = desired_length - current_length
        input_features = F.pad(input_features, (0, pad_amount), mode="constant", value=0)
    elif current_length > desired_length:
        input_features = input_features[:, :, :desired_length]

    with torch.no_grad():
        # ✅ Pass through the Whisper encoder
        encoder_outputs = whisper_model.model.encoder(input_features).last_hidden_state  # (batch, seq_len, hidden_size)
        # ✅ Average the encoder outputs over the time dimension to obtain a fixed-length embedding
        embedding = encoder_outputs.mean(dim=1)

    return embedding.squeeze().cpu().numpy()


# Function to extract prosodic features
def extract_prosodic_features(audio_path):
    sound = parselmouth.Sound(audio_path)
    pitch = sound.to_pitch()
    intensity = sound.to_intensity()

    pitch_values = pitch.selected_array['frequency']
    intensity_values = intensity.values.T.flatten()

    avg_pitch = np.mean(pitch_values[pitch_values > 0])  # Ignore zero values
    avg_intensity = np.mean(intensity_values)

    return avg_pitch, avg_intensity


# Process all files
data = []
for file in tqdm(os.listdir(DATA_DIR)):
    if file.endswith(".wav"):
        audio_path = os.path.join(DATA_DIR, file)
        try:
            # Extract Whisper embeddings (which will be 768-dimensional if that's your model's hidden size)
            whisper_embedding = extract_whisper_embedding(audio_path)
            avg_pitch, avg_intensity = extract_prosodic_features(audio_path)
            data.append({
                "audio_path": audio_path,
                "whisper_embedding": whisper_embedding.tolist(),  # Using a descriptive column name
                "avg_pitch": avg_pitch,
                "avg_intensity": avg_intensity
            })
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(FEATURES_CSV, index=False)
print(f"✅ Feature extraction complete! Data saved to {FEATURES_CSV}")
