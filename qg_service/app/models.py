import torch
from transformers import T5Tokenizer, T5Config
from .config import MODEL_NAME, MODEL_PATH, DEVICE
from .QGmodel import CustomT5WithStyle  # Ensure this is correctly implemented

# Load Tokenizer
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)

# Ensure special tokens are added
special_tokens_dict = {"additional_special_tokens": ["[SAQ]", "[JSQ]"]}
tokenizer.add_special_tokens(special_tokens_dict)

# Load Model Configuration
config = T5Config.from_pretrained(MODEL_NAME)
model = CustomT5WithStyle(config, style_emb_size=32)

# 🔹 **Resize token embeddings BEFORE loading weights** 🔹
model.resize_token_embeddings(len(tokenizer))

# Load the fine-tuned weights
state_dict = torch.load(MODEL_PATH, map_location="cpu")

# 🔹 **Ignore size mismatch errors for embedding layers** 🔹
missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)

print(f"Missing keys: {missing_keys}")  # Debugging information
print(f"Unexpected keys: {unexpected_keys}")

# Move model to the correct device
model.to(DEVICE)
model.eval()  # Set model to evaluation mode
