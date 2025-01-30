import re
import torch
import torchaudio
import torchaudio.functional as AF
import numpy as np
from phonemizer import phonemize
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

# ---------------- USER CONFIG ----------------
MODEL_DIR = "./final_ctc_model"
PROCESSOR_DIR = "./final_ctc_processor"
AUDIO_PATH = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/Raw_data/nature gives fruits vegetables and grains (3).wav"
REFERENCE_TEXT = "nature gives fruits vegetables and grains"
# ---------------------------------------------

def text_to_phonemes(text: str) -> str:
    """Converts text to lowercase, strips punctuation, and phonemizes (IPA)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    phones = phonemize(
        text,
        language="en-us",
        backend="espeak",
        strip=True,
        preserve_punctuation=False
    )
    return phones

def get_log_probs(model, processor, audio_path):
    """
    Loads audio, processes it, runs the CTC model,
    and returns frame-level log probabilities: [time, vocab_size].
    """
    waveform, sr = torchaudio.load(audio_path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != 16000:
        waveform = torchaudio.transforms.Resample(sr, 16000)(waveform)
        sr = 16000

    # Convert to numpy for the HF processor
    samples = waveform.squeeze().numpy()
    inputs = processor(
        samples,
        sampling_rate=sr,
        return_tensors="pt"
    )

    with torch.no_grad():
        logits = model(**inputs).logits  # [1, time, vocab_size]
    # Convert to log_softmax for forced_align
    log_probs = torch.log_softmax(logits, dim=-1)[0]  # [time, vocab_size]
    return log_probs  # still a PyTorch tensor, shape [time, vocab_size]

def forced_align_torchaudio(model, processor, audio_path, text):
    phoneme_str = text_to_phonemes(text)
    phoneme_tokens = phoneme_str.split()
    reference_ids = processor.tokenizer.convert_tokens_to_ids(phoneme_tokens)

    log_probs = get_log_probs(model, processor, audio_path)

    # Use positional arguments here:
    blank_id = processor.tokenizer.pad_token_id or 0
    alignment_frames = AF.forced_align(log_probs, reference_ids, blank_id)

    waveform, sr = torchaudio.load(audio_path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(0, keepdim=True)
    audio_length_s = waveform.shape[-1] / sr
    num_frames = log_probs.shape[0]
    frame_duration = audio_length_s / num_frames

    results = []
    for token_id, (start_f, end_f) in zip(reference_ids, alignment_frames):
        start_time = start_f * frame_duration
        end_time = end_f * frame_duration
        tok = processor.tokenizer.convert_ids_to_tokens([token_id])[0]
        results.append((tok, start_time, end_time))

    return results


if __name__ == "__main__":
    processor = Wav2Vec2Processor.from_pretrained(PROCESSOR_DIR)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_DIR).eval()

    alignment = forced_align_torchaudio(model, processor, AUDIO_PATH, REFERENCE_TEXT)
    for ph, start_s, end_s in alignment:
        print(f"{ph}\t{start_s:.2f}\t{end_s:.2f}")
