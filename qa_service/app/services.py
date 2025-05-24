from transformers import pipeline
from huggingface_hub import snapshot_download

# Model directory
MODEL_DIR = "/host_data/QA_Model"

# # Download the model if not already present
# Download the model if not already present
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
    snapshot_download(
        repo_id="deepset/roberta-base-squad2",  # Replace with the model you want
        repo_type="model",
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False
    )

# Load the model with CPU enforcement
qa_pipeline = pipeline("question-answering", model=MODEL_DIR, tokenizer=MODEL_DIR, device=-1)  # Force CPU

def get_answer(question: str, context: str) -> str:
    result = qa_pipeline({"question": question, "context": context})
    return result["answer"]
