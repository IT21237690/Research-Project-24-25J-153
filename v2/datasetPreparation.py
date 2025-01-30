from datasets import load_dataset
import torchaudio
from v2.TokenizerandModel import feature_extractor, tokenizer

data_files = {
    "train": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/train_phonemes.csv",
    "validation": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/val_phonemes.csv",
    "test": "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/test_phonemes.csv"
}
dataset = load_dataset("csv", data_files=data_files)
print(dataset)


def load_audio_and_encode(batch):
    # 1. Load audio
    audio_path = batch["audio_path"]
    speech, sr = torchaudio.load(audio_path)

    # Convert to mono if needed:
    if speech.shape[0] > 1:
        speech = speech.mean(dim=0, keepdim=True)

    # Resample if not 16k
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        speech = resampler(speech)
        sr = 16000

    speech = speech.squeeze().numpy()

    # 2. Use processor's feature extractor for the audio
    audio_features = feature_extractor(
        speech,
        sampling_rate=sr,
        return_tensors="pt"
    )

    # 3. Convert phoneme_sequence -> list of IDs
    phonemes = batch["phoneme_sequence"].split()
    input_ids = tokenizer.convert_tokens_to_ids(phonemes)

    batch["input_values"] = audio_features["input_values"][0]
    batch["attention_mask"] = audio_features["attention_mask"][0]
    batch["labels"] = input_ids
    return batch

dataset = dataset.map(load_audio_and_encode, remove_columns=dataset["train"].column_names, num_proc=1)
