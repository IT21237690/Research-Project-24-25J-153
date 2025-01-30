import os
import pandas as pd
import librosa
import json
from sklearn.model_selection import train_test_split
import re

# Paths
AUDIO_FOLDER = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/Raw_data"  # Folder containing .wav files
OUTPUT_FOLDER = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/dataset"  # Folder to save processed dataset
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Step 1: Create Metadata
def create_metadata(audio_folder):
    data = []
    for file in os.listdir(audio_folder):
        if file.endswith(".wav"):
            # Remove patterns like "(7)" from the filename before extracting transcription
            clean_name = re.sub(r"\(\d+\)", "", os.path.splitext(file)[0]).strip()
            transcription = clean_name.replace("_", " ")  # Convert underscores to spaces
            file_path = os.path.join(audio_folder, file)

            # Load audio file and get duration
            audio, sr = librosa.load(file_path, sr=16000)
            duration = librosa.get_duration(y=audio, sr=sr)

            data.append({
                "audio_path": file_path,
                "transcription": transcription,
                "duration": duration
            })
    return pd.DataFrame(data)

# Step 2: Split Dataset
def split_dataset(metadata, test_size=0.2, val_size=0.1):
    train_val, test = train_test_split(metadata, test_size=test_size, random_state=42)
    train, val = train_test_split(train_val, test_size=val_size / (1 - test_size), random_state=42)
    return train, val, test

# Step 3: Save Dataset
def save_dataset_splits(train, val, test, output_folder):
    train.to_csv(os.path.join(output_folder, "train.csv"), index=False)
    val.to_csv(os.path.join(output_folder, "val.csv"), index=False)
    test.to_csv(os.path.join(output_folder, "test.csv"), index=False)

# Execute the steps
if __name__ == "__main__":
    # Generate metadata
    metadata = create_metadata(AUDIO_FOLDER)

    # Split into train, validation, and test sets
    train_df, val_df, test_df = split_dataset(metadata)

    # Save the splits
    save_dataset_splits(train_df, val_df, test_df, OUTPUT_FOLDER)

    print(f"Dataset splits saved to: {OUTPUT_FOLDER}")
