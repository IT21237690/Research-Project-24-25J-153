import os
import numpy as np
import librosa
import pandas as pd
import json
import matplotlib.pyplot as plt
from tqdm import tqdm

# Paths
METADATA_FILE = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/dataset/train.json"  # Updated to use JSON
FEATURE_OUTPUT = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/features"
os.makedirs(FEATURE_OUTPUT, exist_ok=True)

# Load metadata
with open(METADATA_FILE, "r") as f:
    metadata = json.load(f)

# Step 1: Extract Features
def extract_features(audio_path, sr=16000, n_mfcc=13):
    try:
        # Load audio
        audio, _ = librosa.load(audio_path, sr=sr)

        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        mfccs_mean = np.mean(mfccs, axis=1)  # Mean over time axis

        # Extract spectrogram
        spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

        return mfccs_mean, spectrogram_db
    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None, None

# Step 2: Save Features
def save_features(metadata, output_folder):
    features = []
    print(f"Processing {len(metadata)} files...")

    for idx, row in tqdm(enumerate(metadata), total=len(metadata), desc="Extracting Features", unit="file"):
        audio_path = row["audio_path"]
        transcription = row["transcription"]

        # Extract MFCCs and spectrogram
        mfccs_mean, spectrogram_db = extract_features(audio_path)

        if mfccs_mean is None or spectrogram_db is None:
            continue

        # Save spectrogram as an image (optional)
        spectrogram_path = os.path.join(output_folder, f"spectrogram_{idx}.png")
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(spectrogram_db, sr=16000, x_axis="time", y_axis="mel")
        plt.colorbar(format="%+2.0f dB")
        plt.title("Mel-Spectrogram")
        plt.tight_layout()
        plt.savefig(spectrogram_path)
        plt.close()

        # Store features
        features.append({
            "audio_path": audio_path,
            "transcription": transcription,
            "mfccs_mean": mfccs_mean.tolist(),
            "spectrogram_path": spectrogram_path
        })

    # Save features as a JSON file
    features_file = os.path.join(output_folder, "features.json")
    with open(features_file, "w") as f:
        json.dump(features, f, indent=4)
    print(f"Features saved to: {features_file}")


# Execute feature extraction
if __name__ == "__main__":
    save_features(metadata, FEATURE_OUTPUT)
    print(f"Feature extraction completed! Features saved in: {FEATURE_OUTPUT}")
