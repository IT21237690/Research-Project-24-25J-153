import os
import librosa
import soundfile as sf
import pandas as pd
from tqdm import tqdm

# Define directories
INPUT_DIR = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/Raw_data"
OUTPUT_DIR = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/processed_audio"
METADATA_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/metadata.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_metadata(input_dir, output_csv):
    """Create metadata CSV from audio filenames"""
    metadata = []

    audio_files = [os.path.join(root, f)
                   for root, _, files in os.walk(input_dir)
                   for f in files if f.endswith('.wav')]

    for audio_path in audio_files:
        filename = os.path.basename(audio_path)
        transcript = os.path.splitext(filename)[0].replace('_', ' ')  # Extract transcript
        metadata.append({'audio_path': audio_path, 'text': transcript.lower()})

    df = pd.DataFrame(metadata)
    df.to_csv(output_csv, index=False)
    print(f"Metadata CSV created at {output_csv} with {len(df)} entries")
    return df


def preprocess_audio(input_path, output_path, target_sr=16000):
    """Resample and normalize audio files"""
    try:
        y, orig_sr = librosa.load(input_path, sr=None)

        if orig_sr != target_sr:
            y = librosa.resample(y, orig_sr, target_sr)

        # Normalize audio amplitude (peak normalization)
        y = librosa.util.normalize(y) * 0.9  # Ensure values do not exceed [-1,1]

        sf.write(output_path, y, target_sr, subtype='PCM_16')
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")


def batch_preprocess(input_dir, output_dir, metadata_csv):
    """Process all audio files and update metadata"""
    df = pd.read_csv(metadata_csv)
    processed_paths = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        input_path = row['audio_path']
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)

        if not os.path.exists(output_path):
            preprocess_audio(input_path, output_path)

        processed_paths.append(output_path)

    df['processed_path'] = processed_paths
    df.to_csv(metadata_csv, index=False)
    print(f"Processing complete. {len(df)} files processed successfully")


# Execute Steps
metadata_df = create_metadata(INPUT_DIR, METADATA_CSV)
batch_preprocess(INPUT_DIR, OUTPUT_DIR, METADATA_CSV)
