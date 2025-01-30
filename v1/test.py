from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torchaudio
from jiwer import wer
import librosa
import matplotlib.pyplot as plt
import numpy as np
import torch


# Paths to the fine-tuned model
# MODEL_PATH = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/wav2vec2-finetuned"
# PROCESSOR_PATH = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/wav2vec2-processor"

MODEL_NAME = "facebook/wav2vec2-base-960h"

# Load the fine-tuned model and processor
print("Loading fine-tuned Wav2Vec2 model...")
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
print("Model loaded successfully!")


# Function to transcribe audio using the fine-tuned model
def transcribe(audio_path):
    try:
        # Load audio file
        audio, rate = torchaudio.load(audio_path)
        print(f"Original Sampling Rate: {rate}")

        # Convert to mono if stereo
        if audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)
            print("Converted audio to mono.")

        # Resample to 16 kHz
        resampler = torchaudio.transforms.Resample(orig_freq=rate, new_freq=16000)
        audio = resampler(audio).squeeze().numpy()
        print(f"Resampled Audio Shape: {audio.shape}")

        # Process audio
        input_values = processor(audio, sampling_rate=16000, return_tensors="pt").input_values
        print(f"Input Values Shape: {input_values.shape}")

        # Get logits
        logits = model(input_values).logits
        print(f"Logits Shape: {logits.shape}")

        # Decode logits
        predicted_ids = logits.argmax(dim=-1)
        print(f"Predicted IDs: {predicted_ids}")
        transcription = processor.decode(predicted_ids[0])
        print(f"Decoded Transcription: {transcription}")

        return transcription
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""




# Function to calculate the pronunciation score
def calculate_pronunciation_score(reference, transcription):

    try:
        # Calculate Word Error Rate (WER)
        error_rate = wer(reference, transcription)
        pronunciation_score = max(0, 1 - error_rate) * 100  # Convert to percentage
        return pronunciation_score
    except Exception as e:
        print(f"Error calculating pronunciation score: {e}")
        return 0.0


# Function to calculate the fluency score
def calculate_fluency_score(audio_path, transcription):

    try:
        # Load audio file
        audio, sr = librosa.load(audio_path, sr=16000)

        # Speech rate: words per second
        word_count = len(transcription.split())
        duration = librosa.get_duration(y=audio, sr=sr)
        speech_rate = word_count / duration

        # Pause detection
        intervals = librosa.effects.split(audio, top_db=20)
        pauses = [(intervals[i][0] - intervals[i - 1][1]) / sr for i in range(1, len(intervals))]
        avg_pause_duration = np.mean(pauses) if pauses else 0

        # Combine features into a fluency score (custom formula)
        fluency_score = (speech_rate * 10) - (avg_pause_duration * 20)
        fluency_score = max(0, min(100, fluency_score))  # Normalize to 0-100
        return fluency_score
    except Exception as e:
        print(f"Error calculating fluency score: {e}")
        return 0.0


# Function to calculate the final score
def calculate_final_score(pronunciation_score, fluency_score):

    final_score = (0.6 * pronunciation_score) + (0.4 * fluency_score)
    return final_score


# Example Usage
if __name__ == "__main__":
    # Paths
    audio_path = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/test.wav"
    reference_text = "the quick brown fox jumps over the lazy dog"


    audio, sr = librosa.load(audio_path, sr=16000)

    print(f"Audio Duration: {librosa.get_duration(y=audio, sr=sr)} seconds")
    plt.plot(audio)
    plt.title("Waveform")
    plt.show()

    # Transcription
    print("Transcribing audio...")
    transcription = transcribe(audio_path)
    print(f"Transcription: {transcription}")

    # Pronunciation Score
    pronunciation_score = calculate_pronunciation_score(reference_text, transcription)
    print(f"Pronunciation Score: {pronunciation_score:.2f}%")

    # Fluency Score
    fluency_score = calculate_fluency_score(audio_path, transcription)
    print(f"Fluency Score: {fluency_score:.2f}%")

    # Final Score
    final_score = calculate_final_score(pronunciation_score, fluency_score)
    print(f"Final Score: {final_score:.2f}%")
