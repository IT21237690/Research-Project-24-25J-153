import csv
import json

train_phonemes_file = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/train_phonemes.csv"
val_phonemes_file = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/val_phonemes.csv"
test_phonemes_file = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/test_phonemes.csv"

def gather_phonemes(csv_file):
    """Reads phoneme sequences from csv_file, returns a set of all unique phonemes."""
    phoneme_set = set()
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pseq = row["phoneme_sequence"]
            # Split on spaces to get each phoneme token
            phones = pseq.split()
            for ph in phones:
                phoneme_set.add(ph)
    return phoneme_set

all_phonemes = set()
for f in [train_phonemes_file, val_phonemes_file, test_phonemes_file]:
    all_phonemes |= gather_phonemes(f)

print(f"Total unique phonemes: {len(all_phonemes)}")
print(all_phonemes)


vocab_list = sorted(list(all_phonemes))
# Insert special tokens
# Typically for CTC, we only need the "blank" as an extra.
# But you can also have <pad>, <unk>, etc.

# Let's define the blank token ID as 0
# Then phonemes follow
vocab_dict = {}
vocab_dict["<pad>"] = 0
for i, ph in enumerate(vocab_list, start=1):
    vocab_dict[ph] = i

# Optionally define other special tokens if needed
# e.g. <unk> or <s> etc.

print(vocab_dict)

with open("/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/phoneme_vocab.json", "w", encoding="utf-8") as f:
    json.dump(vocab_dict, f, ensure_ascii=False, indent=2)
