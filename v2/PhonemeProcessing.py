import csv
import os
import re
from phonemizer import phonemize
from phonemizer.separator import Separator

# -----------------------------------------------------------------------------
# Paths to the CSV files generated in Step 1 (Data Preparation & Organization)
# -----------------------------------------------------------------------------
TRAIN_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/train.csv"
VAL_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/val.csv"
TEST_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/test.csv"

# Output CSVs (with phoneme columns)
TRAIN_PHONEMES_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/train_phonemes.csv"
VAL_PHONEMES_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/val_phonemes.csv"
TEST_PHONEMES_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/test_phonemes.csv"


# -----------------------------------------------------------------------------
# 1. Text Normalization Function
# -----------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """
    Converts text to lowercase, removes punctuation, and trims extra spaces.
    Customize as needed if you want to keep certain punctuation or handle
    numbers differently, etc.
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation (except spaces and word characters)
    text = re.sub(r"[^\w\s]", "", text)
    # Replace multiple whitespace with a single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing spaces
    text = text.strip()
    return text


# -----------------------------------------------------------------------------
# 2. Phonemizer Wrapper Function
# -----------------------------------------------------------------------------
def text_to_phonemes(text: str) -> str:
    """
    Converts an English sentence into a phoneme sequence (IPA),
    using phonemizer with eSpeak as the default backend.

    Returns: A string of phonemes separated by spaces
             (e.g. "h ə ˈl oʊ w ɝ l d").
    """
    # Important: ensure the word and phone separators differ.
    # Here, we remove the word and syllable separators entirely,
    # leaving only a space between phones.
    sep = Separator(phone=" ", word="", syllable="")

    phoneme_seq = phonemize(
        text,
        language="en-us",
        backend="espeak",
        strip=True,
        separator=sep,
        preserve_punctuation=False  # punctuation is removed in normalization
    )
    return phoneme_seq


# -----------------------------------------------------------------------------
# 3. Main Function: Process CSV Files
# -----------------------------------------------------------------------------
def process_csv(input_csv, output_csv):
    """
    Reads each row from input_csv, normalizes the transcript text, converts it
    to phonemes, and writes [audio_path, transcript, phoneme_sequence] to output_csv.
    """
    with open(input_csv, "r", encoding="utf-8") as fin, \
            open(output_csv, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["audio_path", "transcript", "phoneme_sequence"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            audio_path = row["audio_path"]
            transcript_raw = row["transcript"]

            # Clean/normalize transcript
            transcript_clean = normalize_text(transcript_raw)

            # Convert transcript to phonemes
            phoneme_seq = text_to_phonemes(transcript_clean)

            writer.writerow({
                "audio_path": audio_path,
                "transcript": transcript_clean,  # or keep the original raw text
                "phoneme_sequence": phoneme_seq
            })


# -----------------------------------------------------------------------------
# 4. Run on train, val, test CSVs
# -----------------------------------------------------------------------------
process_csv(TRAIN_CSV, TRAIN_PHONEMES_CSV)
process_csv(VAL_CSV, VAL_PHONEMES_CSV)
process_csv(TEST_CSV, TEST_PHONEMES_CSV)

print("Phoneme conversion complete!")
print(f"Created: {TRAIN_PHONEMES_CSV}, {VAL_PHONEMES_CSV}, {TEST_PHONEMES_CSV}")
