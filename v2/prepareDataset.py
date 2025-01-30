import os
import csv
import random
import re

# -------------------------------------------------
# USER CONFIG: Adjust these paths/params as needed
# -------------------------------------------------
DATA_DIR = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/Raw_data"  # folder containing all .wav files
TRAIN_SPLIT = 0.70
VAL_SPLIT = 0.20
TEST_SPLIT = 0.10
OUTPUT_DIR = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets"  # where to save the CSV files (train.csv, val.csv, test.csv)

# for reproducible shuffling:
random.seed(42)

# -------------------------------------------------
# 1. Gather .wav files and create (audio_path, transcript) pairs
# -------------------------------------------------
all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.wav')]

metadata = []
for fname in all_files:
    # Full path to the audio file
    audio_path = os.path.join(DATA_DIR, fname)

    # The text is everything before '.wav'
    # e.g. "hello world (1).wav" -> raw_transcription = "hello world (1)"
    raw_transcription = fname[:-4]  # remove the last 4 chars ".wav"

    # Remove any parentheses and the text inside them:
    # e.g. "hello world (1)" -> "hello world "
    transcription = re.sub(r"\(.*?\)", "", raw_transcription)

    # Clean up extra spaces, underscores, etc. as needed
    # (Example removing underscores):
    # transcription = transcription.replace("_", " ")

    # Strip leading/trailing whitespace
    transcription = transcription.strip()

    metadata.append((audio_path, transcription))

# -------------------------------------------------
# 2. Shuffle the data
# -------------------------------------------------
random.shuffle(metadata)

# -------------------------------------------------
# 3. Split into train, val, test
# -------------------------------------------------
total_count = len(metadata)
train_count = int(TRAIN_SPLIT * total_count)
val_count = int(VAL_SPLIT * total_count)
test_count = total_count - train_count - val_count

train_data = metadata[:train_count]
val_data = metadata[train_count: train_count + val_count]
test_data = metadata[train_count + val_count:]

print(f"Total: {total_count}")
print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")


# -------------------------------------------------
# 4. Write CSV files (train.csv, val.csv, test.csv)
# -------------------------------------------------
def write_csv(data, filename):
    with open(os.path.join(OUTPUT_DIR, filename), mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # header
        writer.writerow(["audio_path", "transcript"])
        # rows
        for row in data:
            writer.writerow(row)


write_csv(train_data, "train.csv")
write_csv(val_data, "val.csv")
write_csv(test_data, "test.csv")

print("CSV files generated: train.csv, val.csv, test.csv")
