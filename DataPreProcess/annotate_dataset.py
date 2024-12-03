import os
import whisper

# Load Whisper model (small for faster processing or large for better accuracy)
model = whisper.load_model("small")

def transcribe_audio(audio_path):
    """
    Transcribe the audio file using the Whisper model.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: Transcription text.
    """
    result = model.transcribe(audio_path)
    return result['text']

def process_dataset(input_dir, output_dir):
    """
    Process all audio files in a categorized dataset directory, transcribe them, and save annotations.

    Args:
        input_dir (str): Path to the root input directory containing categorized folders with .wav files.
        output_dir (str): Path to the root output directory to save transcriptions.

    Returns:
        None
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Walk through all subdirectories in the dataset
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".wav"):
                # Full path to the audio file
                audio_path = os.path.join(root, filename)

                # Create the corresponding output folder structure
                relative_path = os.path.relpath(root, input_dir)
                transcription_dir = os.path.join(output_dir, relative_path)
                os.makedirs(transcription_dir, exist_ok=True)

                # Generate the transcription file path
                transcription_file = os.path.join(transcription_dir, f"{os.path.splitext(filename)[0]}.txt")

                # Transcribe the audio and save the result
                print(f"Transcribing: {audio_path}...")
                transcription = transcribe_audio(audio_path)
                with open(transcription_file, "w") as f:
                    f.write(transcription)
                print(f"Saved transcription to: {transcription_file}")

# Example usage
input_dataset_dir = "../low dataset"  # Path to the root directory of the categorized dataset
output_transcriptions_dir = "../annotated_transcriptions"  # Output directory to save transcriptions

process_dataset(
    input_dir=input_dataset_dir,
    output_dir=output_transcriptions_dir
)

