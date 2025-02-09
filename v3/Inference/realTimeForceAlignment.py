import torch
import torchaudio
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from pyctcdecode import build_ctcdecoder
import pronouncing

# ✅ Load Wav2Vec2 Processor & Model for Forced Alignment
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
asr_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h").eval()

# ✅ Get Wav2Vec2 Vocabulary for Phoneme Decoding
vocab_dict = processor.tokenizer.get_vocab()
labels = [token for token, _ in sorted(vocab_dict.items(), key=lambda x: x[1])]
decoder = build_ctcdecoder(labels)


def align_audio_with_text(audio_path, reference_text):
    """
    Aligns user speech with reference text using CTC-based alignment.
    Returns word-level and phoneme-level timestamps.
    """
    try:
        print(f"🔹 Processing audio for forced alignment: {audio_path}")

        # ✅ Load and preprocess audio
        waveform, sample_rate = torchaudio.load(audio_path)
        print(f"📢 Loaded waveform shape: {waveform.shape}, Sample Rate: {sample_rate}")

        # ✅ Convert stereo to mono if needed
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            print("📢 Converted audio to mono")

        if sample_rate != 16000:
            waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)
            print("📢 Resampled audio to 16kHz")

        # ✅ Convert waveform to numpy & extract model inputs
        waveform = waveform.squeeze().numpy()
        inputs = processor(waveform, sampling_rate=16000, return_tensors="pt", padding=True)

        # ✅ Perform ASR inference
        with torch.no_grad():
            logits = asr_model(**inputs).logits.cpu().numpy()[0]

        # ✅ Decode the transcript using CTC decoder
        decoded_text = decoder.decode(logits).lower()
        print(f"✅ Decoded Text: {decoded_text}")

        # ✅ Extract word-level timestamps
        word_timestamps = decoder.decode_beams(logits, beam_width=5)[0][2]
        word_alignment = []
        for word, (start, end) in word_timestamps:
            word_alignment.append({
                "word": word.lower(),  # Convert to lowercase for matching
                "start": start / 100,  # Convert ms to seconds
                "end": end / 100
            })

        # ✅ Match decoded words with reference words
        reference_words = reference_text.lower().split()
        aligned_words = [word_info for word_info in word_alignment if word_info["word"] in reference_words]

        # ✅ Extract phoneme timestamps
        phoneme_alignment = []
        for word_info in aligned_words:
            phonemes = get_phonemes(word_info["word"])
            if phonemes:
                phoneme_alignment.extend(distribute_phonemes(word_info, phonemes))

        print(f"🔍 Detected Words: {[w['word'] for w in aligned_words]}")
        print(f"🔍 Detected Phonemes: {[p['phoneme'] for p in phoneme_alignment]}")

        return aligned_words, phoneme_alignment

    except Exception as e:
        print(f"❌ Error in forced alignment: {e}")
        return None, None


def get_phonemes(word):
    """
    Converts a word to phonemes using CMU Pronouncing Dictionary.
    """
    phoneme_list = pronouncing.phones_for_word(word)

    if phoneme_list:
        return phoneme_list[0].split()  # Return first pronunciation

    # ✅ Fallback method (Letter-based phonemes)
    return [char.upper() + "0" for char in word]


def distribute_phonemes(word_info, phonemes):
    """
    Distributes phonemes evenly over the word's duration.
    """
    start_time = word_info["start"]
    end_time = word_info["end"]
    duration = end_time - start_time
    num_phones = len(phonemes)

    if num_phones == 0:
        return []

    phone_duration = duration / num_phones
    return [
        {
            "phoneme": phoneme,
            "start": start_time + i * phone_duration,
            "end": start_time + (i + 1) * phone_duration
        }
        for i, phoneme in enumerate(phonemes)
    ]

