import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Define the test audio file (update path as needed)
test_audio = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/Inference/myself.wav"

# ----------------------------
# Load the Pretrained (General) Whisper Model
# ----------------------------
processor_pretrained = WhisperProcessor.from_pretrained("openai/whisper-small")
model_pretrained = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
model_pretrained.eval()

# ----------------------------
# Load the Fine-Tuned Whisper Model and Processor
# ----------------------------
fine_tuned_model_path = "/v3/models/whisper-finetuned-final"
fine_tuned_processor_path = "/v3/models/whisper-finetuned-final"

processor_finetuned = WhisperProcessor.from_pretrained(fine_tuned_processor_path)
model_finetuned = WhisperForConditionalGeneration.from_pretrained(fine_tuned_model_path)
model_finetuned.eval()

# ----------------------------
# Load and Prepare the Audio
# ----------------------------
# Load the audio using torchaudio
waveform, sr = torchaudio.load(test_audio)

# Resample to 16kHz if necessary
if sr != 16000:
    waveform = torchaudio.functional.resample(waveform, sr, 16000)

# Convert to mono if necessary
if waveform.shape[0] > 1:
    waveform = waveform.mean(dim=0, keepdim=True)
waveform = waveform.squeeze()

# ----------------------------
# Prepare Inputs for Each Model
# ----------------------------
# For the pretrained (general) model
inputs_pretrained = processor_pretrained(waveform, return_tensors="pt", sampling_rate=16000, language='en')
# For the fine-tuned model
inputs_finetuned = processor_finetuned(waveform, return_tensors="pt", sampling_rate=16000, language='en')


# ----------------------------
# Run Inference with Both Models
# ----------------------------
with torch.no_grad():
    # Whisper models use the generate() method to produce transcriptions
    generated_ids_pretrained = model_pretrained.generate(inputs_pretrained.input_features)
    generated_ids_finetuned = model_finetuned.generate(inputs_finetuned.input_features)

# Decode the generated token IDs to text (skip special tokens)
predicted_text_pretrained = processor_pretrained.batch_decode(generated_ids_pretrained, skip_special_tokens=True)[0]
predicted_text_finetuned = processor_finetuned.batch_decode(generated_ids_finetuned, skip_special_tokens=True)[0]

# ----------------------------
# Display the Results
# ----------------------------
print("Original (Pretrained) Model Transcription:")
print(predicted_text_pretrained)
print("\nFine-tuned Model Transcription:")
print(predicted_text_finetuned)
