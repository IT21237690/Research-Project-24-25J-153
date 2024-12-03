from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa
import sys

# Load pre-trained Wav2Vec model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
def transcribe(audio_path):
    # Load and preprocess audio
    speech_array, sampling_rate = librosa.load(audio_path, sr=16000)
    inputs = processor(speech_array, sampling_rate=16000, return_tensors="pt", padding=True)
    print("inside wave2vec script")

    # Perform inference
    with torch.no_grad():
        logits = model(inputs.input_values).logits

    # Decode transcription
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription

if __name__ == "__main__":
    audio_file_path = sys.argv[1]
    print(transcribe(audio_file_path))
