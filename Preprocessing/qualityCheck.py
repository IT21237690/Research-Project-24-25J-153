from tokenizers import Tokenizer

# Load your trained tokenizer
tokenizer = Tokenizer.from_file("./Preprocessing/custom_tokenizer.json")

# Sample texts from your dataset to test tokenization quality
sample_texts = [
    "Say 'Hello' to your friend.",
    "What should you say when you meet someone?",
    "The lion was caught in a net, but the mouse bit the net and saved the lion.",
    "Where does the bee live?",
]

# Tokenize each sample and display results
for text in sample_texts:
    encoded = tokenizer.encode(text)
    tokens = encoded.tokens  # List of tokenized words/subwords
    token_ids = encoded.ids  # List of token IDs
    
    # Display original text and tokenized output
    print(f"Original Text: {text}")
    print(f"Tokens: {tokens}")
    print(f"Token IDs: {token_ids}")
    print("-" * 50)
