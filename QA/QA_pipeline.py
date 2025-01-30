from huggingface_hub import snapshot_download
from transformers import pipeline


model_dir = snapshot_download(
    repo_id="deepset/roberta-base-squad2",  # The model ID on Hugging Face
    repo_type="model",
    local_dir="/home/minidu-tissera/PycharmProjects/Research-Project/v11/Models/QA_Model",       
    local_dir_use_symlinks=False          
)

print("Model downloaded to:", model_dir)

qa_pipeline = pipeline(
    "question-answering",
    model=model_dir,
    tokenizer=model_dir
)


context = "We watch movies together."
question = "What does the person watch together?"

result = qa_pipeline({"question": question, "context": context})
print(result)
# Expected output: {'score': ..., 'start': 65, 'end': 89, 'answer': 'milk and cookies'}
