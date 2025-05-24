import re
import string
import torch
import torchaudio
import librosa
import numpy as np
import requests
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import noisereduce as nr  # Noise reduction


MODEL_PATH = "/host_data/whisper-finetuned-final"
processor = WhisperProcessor.from_pretrained(MODEL_PATH)
asr_model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
asr_model.eval()
# -----------------------
# Function to normalize text by lowercasing and removing punctuation
# -----------------------
def normalize_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text


# -----------------------
# Function to extract Whisper embeddings using encoder outputs with padding/truncation
# -----------------------
def extract_whisper_embeddings(audio_path):
    waveform, sr = torchaudio.load(audio_path)
    waveform = torchaudio.functional.resample(waveform, sr, 16000)

    if waveform.dim() > 1:
        waveform = waveform.mean(dim=0, keepdim=True)  # Convert to mono if needed

    # # **Apply Noise Reduction**
    # waveform_np = waveform.squeeze().numpy()
    # reduced_noise_waveform = nr.reduce_noise(y=waveform_np, sr=16000) 

    # Convert waveform to input features (log-mel spectrogram)
    inputs = processor(
        waveform.squeeze().numpy(),
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )
    input_features = inputs.input_features  # (batch, feature_size, time)

    # Ensure the time dimension is exactly 3000
    desired_length = 3000
    current_length = input_features.shape[-1]

    if current_length < desired_length:
        pad_amount = desired_length - current_length
        input_features = torch.nn.functional.pad(input_features, (0, pad_amount), mode="constant", value=0)
    elif current_length > desired_length:
        input_features = input_features[:, :, :desired_length]

    with torch.no_grad():
        # Pass through the Whisper encoder to get hidden states
        encoder_outputs = asr_model.model.encoder(input_features).last_hidden_state  # (batch, seq_len, hidden_size)
        # Average over time to produce a fixed-length embedding
        embedding = encoder_outputs.mean(dim=1)

    return embedding.squeeze().numpy()


# -----------------------
# Function to extract prosody features
# -----------------------
def extract_prosody_features(audio_path):
    y, sr = librosa.load(audio_path, sr=16000)
    pitch = librosa.yin(y, fmin=50, fmax=400)
    avg_pitch = np.nanmean(pitch)  # Average pitch (Hz)
    avg_intensity = np.mean(librosa.feature.rms(y=y))  # Average intensity (energy)
    return np.array([avg_pitch, avg_intensity])


# -----------------------
# Function to run forced alignment using Gentle Docker
# -----------------------
def run_gentle_alignment(audio_path, transcript):
    url = "http://20.193.146.113:8765/transcriptions?async=false"

    with open(audio_path, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {"transcript": transcript}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error in forced alignment: {response.text}")
        return None


# -----------------------
# Function to transcribe audio using Whisper's generate() method
# -----------------------
def transcribe_audio(audio_path):
    waveform, sr = torchaudio.load(audio_path)
    waveform = torchaudio.functional.resample(waveform, sr, 16000)

    if waveform.dim() > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Convert waveform to input features (log-mel spectrogram)
    inputs = processor(
        waveform.squeeze().numpy(),
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )
    input_features = inputs.input_features  # shape: (batch, feature_size, time)

    # Ensure the time dimension is exactly 3000
    desired_length = 3000
    current_length = input_features.shape[-1]

    if current_length < desired_length:
        pad_amount = desired_length - current_length
        input_features = torch.nn.functional.pad(input_features, (0, pad_amount), mode="constant", value=0)
    elif current_length > desired_length:
        input_features = input_features[:, :, :desired_length]

    with torch.no_grad():
        generated_ids = asr_model.generate(input_features)

    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return transcription
