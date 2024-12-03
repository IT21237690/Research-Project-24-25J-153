import os
import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np

# Define paths
base_folder = "../voice_dataset"  # Adjust path as needed relative to script location
output_base_folder = "../Cleaned Voice dataset"  # Location for cleaned files

# Ensure output folder exists
os.makedirs(output_base_folder, exist_ok=True)

# Function to detect low-energy segments (potential noise)
def get_noise_profile(audio, sr, threshold=0.02, segment_duration=0.5):
    frame_length = int(segment_duration * sr)
    hop_length = frame_length // 2  # Overlapping frames for smoother analysis
    rms_energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length).flatten()
    low_energy_indices = np.where(rms_energy < threshold)[0]
    if len(low_energy_indices) > 0:
        # Use detected low-energy segments as noise profile
        noise_start = low_energy_indices[0] * hop_length
        noise_end = min(noise_start + frame_length, len(audio))
        return audio[noise_start:noise_end]
    else:
        # Default to first segment if no clear noise detected
        return audio[:frame_length]

# Function to preprocess audio
def preprocess_audio(file_path, output_path):
    try:
        # Load the audio file
        # audio, sr = librosa.load(file_path, sr=None)  # Load with original sampling rate
        audio, sr = librosa.load(file_path, sr=16000, mono=True)

        # Get noise profile dynamically
        noise_sample = get_noise_profile(audio, sr)
        
        # Noise reduction using dynamic noise profile
        reduced_noise = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample)
        
        # Save cleaned audio
        sf.write(output_path, reduced_noise, sr)
        print(f"Processed and saved: {output_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Recursive function to process folder structure
def process_folder(input_folder, output_folder):
    for item in os.listdir(input_folder):
        input_path = os.path.join(input_folder, item)
        output_path = os.path.join(output_folder, item)
        
        if os.path.isdir(input_path):
            # Create corresponding directory in the output folder
            os.makedirs(output_path, exist_ok=True)
            # Recur into subfolder
            process_folder(input_path, output_path)
        elif item.endswith(('.wav', '.mp3')):
            # Process audio file
            preprocess_audio(input_path, output_path)

# Start processing
process_folder(base_folder, output_base_folder)

print("All files processed and saved.")
