import librosa
import librosa.display
import numpy as np
import os
import matplotlib.pyplot as plt

def extract_features(audio_path, output_dir, n_mfcc=13, sr=16000, n_mels=128, fmax=8000):
    """
    Extract MFCC and Mel-spectrogram features and save them to the specified output directory.

    Args:
        audio_path (str): Path to the input audio file.
        output_dir (str): Directory to save extracted features.
        n_mfcc (int): Number of MFCCs to extract.
        sr (int): Sampling rate for loading audio.
        n_mels (int): Number of Mel bands for the spectrogram.
        fmax (int): Maximum frequency for the Mel-spectrogram.

    Returns:
        None
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=sr)

    # Extract MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(audio_path))[0]}_mfcc.npy")
    np.save(mfcc_path, mfcc)
    print(f"MFCC saved to {mfcc_path}")

    # Extract Mel-spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=fmax)
    spectrogram_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(audio_path))[0]}_melspectrogram.png")

    # Save Mel-spectrogram visualization
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(S, ref=np.max), y_axis='mel', x_axis='time', sr=sr)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-Spectrogram')
    plt.tight_layout()
    plt.savefig(spectrogram_path)
    plt.close()
    print(f"Mel-spectrogram saved to {spectrogram_path}")

def process_directory(input_dir, output_dir, n_mfcc=13, sr=16000, n_mels=128, fmax=8000):
    """
    Process all audio files in a directory for feature extraction, maintaining the folder structure.

    Args:
        input_dir (str): Path to the input directory with audio files.
        output_dir (str): Directory to save extracted features.
        n_mfcc (int): Number of MFCCs to extract.
        sr (int): Sampling rate for loading audio.
        n_mels (int): Number of Mel bands for the spectrogram.
        fmax (int): Maximum frequency for the Mel-spectrogram.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".wav"):
                audio_path = os.path.join(root, filename)

                # Compute the relative path and create the corresponding output folder
                relative_path = os.path.relpath(root, input_dir)
                target_dir = os.path.join(output_dir, relative_path)
                os.makedirs(target_dir, exist_ok=True)

                print(f"Processing {audio_path}...")
                extract_features(audio_path, target_dir, n_mfcc, sr, n_mels, fmax)

# Example usage
input_normalized_dir = "/home/bhagya/Documents/Research/pp1/processed_audio/normalized"  # Use the normalized dataset
output_feature_dir = "/home/bhagya/Documents/Research/pp1/processed_audio/data_features"

process_directory(
    input_dir=input_normalized_dir,
    output_dir=output_feature_dir,
    n_mfcc=13,
    sr=16000,
    n_mels=128,
    fmax=8000
)
