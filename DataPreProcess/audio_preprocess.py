from pydub import AudioSegment, silence
import os

def preprocess_audio(input_dir, output_dir, normalized_dir, chunk_dir, min_silence_len=500, silence_thresh=-40):
    """
    Preprocess all audio files in a directory and its subdirectories: normalize and split based on silence.

    Args:
        input_dir (str): Path to the input directory containing .wav files.
        output_dir (str): Root output directory to save processed audio.
        normalized_dir (str): Directory to save normalized audio.
        chunk_dir (str): Directory to save audio chunks.
        min_silence_len (int): Minimum silence length in ms to consider for splitting.
        silence_thresh (int): Silence threshold in dBFS to consider for splitting.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(normalized_dir, exist_ok=True)
    os.makedirs(chunk_dir, exist_ok=True)

    # Walk through all directories and subdirectories
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".wav"):
                file_path = os.path.join(root, filename)
                print(f"Processing {file_path}...")

                # Step 1: Normalize audio
                audio = AudioSegment.from_wav(file_path)
                normalized_audio = audio.set_frame_rate(16000).set_channels(1)
                
                # Create a subfolder structure in the normalized output directory
                relative_path = os.path.relpath(root, input_dir)
                normalized_subdir = os.path.join(normalized_dir, relative_path)
                os.makedirs(normalized_subdir, exist_ok=True)
                normalized_path = os.path.join(normalized_subdir, filename)
                normalized_audio.export(normalized_path, format="wav")
                print(f"Normalized audio saved to {normalized_path}")

                # Step 2: Split audio on silence
                chunks = silence.split_on_silence(
                    normalized_audio,
                    min_silence_len=min_silence_len,
                    silence_thresh=silence_thresh
                )

                # Save chunks in the chunk directory with a similar subfolder structure
                chunk_subdir = os.path.join(chunk_dir, relative_path)
                os.makedirs(chunk_subdir, exist_ok=True)
                for i, chunk in enumerate(chunks):
                    chunk_name = f"{os.path.splitext(filename)[0]}_chunk{i}.wav"
                    chunk_path = os.path.join(chunk_subdir, chunk_name)
                    chunk.export(chunk_path, format="wav")
                    print(f"Chunk saved to {chunk_path}")

    print("Audio preprocessing completed.")

# Example usage
input_audio_dir = "../low dataset"  # Input directory containing .wav files
output_dir = "../processed_audio"  # Root output directory
normalized_audio_dir = os.path.join(output_dir, "normalized")
audio_chunk_dir = os.path.join(output_dir, "chunks")

preprocess_audio(
    input_dir=input_audio_dir,
    output_dir=output_dir,
    normalized_dir=normalized_audio_dir,
    chunk_dir=audio_chunk_dir,
    min_silence_len=500,  
    silence_thresh=-40   
)

