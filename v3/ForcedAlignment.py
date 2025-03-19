import os
import json
import requests
import pandas as pd
import pronouncing
from tqdm import tqdm

# URL of the Gentle Forced Aligner running inside Docker
GENTLE_API_URL = "http://localhost:8765/transcriptions?async=false"

# Path to metadata CSV
METADATA_CSV = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/datasets/metadata.csv"
OUTPUT_CSV = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/datasets/alignment_results.csv"


def get_phonemes(word):
    """
    Retrieve phonemes for a given word using CMU Pronouncing Dictionary.
    Falls back to letter-based phonemes if the word is not in the dictionary.
    """
    phones = pronouncing.phones_for_word(word.lower())
    if phones:
        return phones[0].split()  # Get first pronunciation

    # Fallback: Convert letters to pseudo-phonemes (A → A0, B → B0, etc.)
    return [f"{letter.upper()}0" for letter in word]


def distribute_phoneme_timestamps(word_info, phonemes):
    """
    Evenly distribute phoneme timestamps within the word's duration.
    """
    start, end = word_info.get("start", 0), word_info.get("end", 0)
    duration = end - start
    num_phonemes = len(phonemes)

    if num_phonemes == 0 or duration <= 0:
        return []

    phoneme_duration = duration / num_phonemes  # Evenly distribute

    return [
        {"phoneme": phonemes[i], "start": start + i * phoneme_duration, "end": start + (i + 1) * phoneme_duration}
        for i in range(num_phonemes)
    ]


def align_audio_gentle(audio_path, transcript):
    """Send request to Gentle Forced Aligner and process the response."""
    try:
        files = {
            'audio': open(audio_path, 'rb'),
            'transcript': (None, transcript)  # Send transcript as text
        }

        # Send request to Gentle API
        response = requests.post(GENTLE_API_URL, files=files)
        response_data = response.json()

        # Ensure response contains words
        if "words" not in response_data:
            print(f"⚠️ Warning: No words aligned for {audio_path}")
            return {"word_alignment": [], "phoneme_alignment": []}

        # Process word alignment
        word_alignment = []
        phoneme_alignment = []

        for word_info in response_data["words"]:
            if "alignedWord" not in word_info or "start" not in word_info or "end" not in word_info:
                continue  # Skip misaligned words

            word = word_info["alignedWord"]
            word_alignment.append({
                "word": word,
                "start": word_info["start"],
                "end": word_info["end"]
            })

            # Get phonemes for the word
            phonemes = get_phonemes(word)
            phoneme_alignment.extend(distribute_phoneme_timestamps(word_info, phonemes))

        return {
            "word_alignment": word_alignment,
            "phoneme_alignment": phoneme_alignment
        }

    except Exception as e:
        print(f"❌ Error processing {audio_path}: {str(e)}")
        return {"word_alignment": [], "phoneme_alignment": []}  # Return empty results


def batch_process(metadata_csv, output_csv):
    """Process all files using Gentle with a progress bar."""
    df = pd.read_csv(metadata_csv)
    results = []

    with tqdm(total=len(df), desc="Processing Audio Files", unit="file") as progress_bar:
        for _, row in df.iterrows():
            try:
                alignment = align_audio_gentle(row["processed_path"], row["text"])

                results.append({
                    "audio_path": row["processed_path"],
                    "word_alignment": json.dumps(alignment["word_alignment"]),  # Store as JSON string
                    "phoneme_alignment": json.dumps(alignment["phoneme_alignment"]),  # Store phoneme alignment
                    "text": row["text"]  # Ensure transcript is saved
                })
            except Exception as e:
                print(f"❌ Critical error processing {row['processed_path']}: {str(e)}")
            finally:
                progress_bar.update(1)

    # ✅ Save results to CSV
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"✅ Alignment results saved to {output_csv}")


if __name__ == "__main__":
    batch_process(METADATA_CSV, OUTPUT_CSV)
