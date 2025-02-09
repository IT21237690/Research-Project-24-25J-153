import torch
import torchaudio
import pronouncing
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from pyctcdecode import build_ctcdecoder
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

from v3.datasetPreparation import METADATA_CSV

MODEL_NAME = "facebook/wav2vec2-base-960h"


def load_models():
    """Load Wav2Vec2 model and tokenizer"""
    processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
    vocab_dict = processor.tokenizer.get_vocab()
    labels = [token for token, _ in sorted(vocab_dict.items(), key=lambda x: x[1])]

    decoder = build_ctcdecoder(labels, kenlm_model_path=None)
    return processor, model, decoder


def get_phonemes(word):
    """
    Retrieve phonemes for a given word using CMU Pronouncing Dictionary.
    Falls back to letter-based phonemes if the word is not in the dictionary.
    """
    phones = pronouncing.phones_for_word(word.lower())

    if phones:
        return phones[0].split()  # Extract phonemes from CMU dictionary

    # Fallback: Convert letters to pseudo-phonemes (A → A0, B → B0, etc.)
    return [f"{letter.upper()}0" for letter in word]  # Example: 'cat' → ['C0', 'A0', 'T0']


def distribute_phoneme_timestamps(word_info, phonemes):
    """
    Evenly distribute phoneme timestamps across the word duration.
    """
    start, end = word_info['start'], word_info['end']
    duration = end - start
    num_phonemes = len(phonemes)

    if num_phonemes == 0:
        return []

    phoneme_duration = duration / num_phonemes

    return [
        {"phoneme": phonemes[i], "start": start + i * phoneme_duration, "end": start + (i + 1) * phoneme_duration}
        for i in range(num_phonemes)
    ]


def process_audio(file_path, transcript, processor, model, decoder):
    """Align phonemes and words with timestamps"""
    waveform, sample_rate = torchaudio.load(file_path)

    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)

    audio = waveform.squeeze().numpy()
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits.cpu().numpy()[0]

    text = decoder.decode(logits)
    alignment = decoder.decode_beams(logits, beam_width=5)[0]

    word_alignment = [{"word": w, "start": s / 100, "end": e / 100} for w, (s, e) in alignment[2]]

    phoneme_alignment = []
    for word_info in word_alignment:
        phonemes = get_phonemes(word_info["word"])  # Extract phonemes for each word
        phoneme_alignment.extend(distribute_phoneme_timestamps(word_info, phonemes))

    return {
        "decoded_text": text,
        "word_alignment": word_alignment,
        "phoneme_alignment": phoneme_alignment
    }


def batch_process(metadata_csv, output_csv):
    """Process all files in metadata"""
    processor, model, decoder = load_models()
    df = pd.read_csv(metadata_csv)
    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        try:
            alignment = process_audio(row['processed_path'], row['text'], processor, model, decoder)
            results.append({
                "audio_path": row['processed_path'],
                "word_alignment": json.dumps(alignment['word_alignment']),
                "phoneme_alignment": json.dumps(alignment['phoneme_alignment']),
                "text": alignment["decoded_text"]
            })
        except Exception as e:
            print(f"Error processing {row['processed_path']}: {str(e)}")

    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"Alignment results saved to {output_csv}")


if __name__ == "__main__":
    batch_process(METADATA_CSV, "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/alignment_results.csv")
