from transformers import Wav2Vec2CTCTokenizer, Wav2Vec2Processor, Wav2Vec2ForCTC

# 1. Load your phoneme tokenizer
tokenizer = Wav2Vec2CTCTokenizer(
    "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v2/datasets/phoneme_vocab.json",
    unk_token="<unk>",
    pad_token="<pad>",
    word_delimiter_token="|"  # or ""
)

# 2. Create feature extractor & processor
from transformers import Wav2Vec2FeatureExtractor
feature_extractor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    do_normalize=True,
    return_attention_mask=True
)

processor = Wav2Vec2Processor(
    feature_extractor=feature_extractor,
    tokenizer=tokenizer
)

# 3. Load a pretrained Wav2Vec2ForCTC model with custom vocab_size
vocab_size = len(tokenizer)
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-base-960h",
    vocab_size=vocab_size,
    ignore_mismatched_sizes=True
)

# Now the model.lm_head has output dimension == vocab_size
print(model.lm_head)
