import json
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, processors, decoders, normalizers
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.normalizers import NFD, Lowercase, StripAccents
from tokenizers.processors import TemplateProcessing

# Load your dataset
with open('Datasets/grade3.json', 'r') as file:
    dataset = json.load(file)

# Extract passages and questions from the dataset
texts = []
for item in dataset:
    if item.get("passage"):
        texts.append(item["passage"])
    for question in item["questions"]:
        texts.append(question["question"])
        if "answer" in question:
            texts.append(question["answer"])

# Initialize a Byte-Pair Encoding (BPE) tokenizer
tokenizer = Tokenizer(models.BPE())
tokenizer.normalizer = normalizers.Sequence([NFD(), Lowercase(), StripAccents()])
tokenizer.pre_tokenizer = Whitespace()

# Train the tokenizer on the extracted texts
trainer = trainers.BpeTrainer(vocab_size=5000, min_frequency=1, special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"])
tokenizer.train_from_iterator(texts, trainer=trainer)

# Post-processing (optional): add template processing for input/output formatting
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[("[CLS]", tokenizer.token_to_id("[CLS]")), ("[SEP]", tokenizer.token_to_id("[SEP]"))]
)

# Save the tokenizer for future use
tokenizer.save("Preprocessing/custom_tokenizer.json")

# Tokenize your dataset
tokenized_data = []
for item in dataset:
    tokenized_item = {
        "passage": tokenizer.encode(item["passage"]).ids if item.get("passage") else None,
        "questions": []
    }
    for question in item["questions"]:
        tokenized_question = {
            "question": tokenizer.encode(question["question"]).ids,
            "answer": tokenizer.encode(question["answer"]).ids if "answer" in question else None
        }
        tokenized_item["questions"].append(tokenized_question)
    tokenized_data.append(tokenized_item)

# Optional: Save the tokenized data for later use
with open('Datasets/tokenized_grade3.json', 'w') as f:
    json.dump(tokenized_data, f, indent=4)

print("Tokenization complete and saved to tokenized_grade3.json")
