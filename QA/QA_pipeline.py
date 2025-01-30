from huggingface_hub import snapshot_download
from transformers import pipeline

# 1) Download the model to your desired folder (e.g., "./my_specific_folder").
#    By default, snapshot_download would place files in a cache directory, but
#    here we control exactly where they go using 'local_dir'.
model_dir = snapshot_download(
    repo_id="deepset/roberta-base-squad2",  # The model ID on Hugging Face
    repo_type="model",
    local_dir="/home/minidu-tissera/PycharmProjects/Research-Project/v11/Models/QA_Model",       # Specify your custom folder path
    local_dir_use_symlinks=False           # True by default on some platforms, set to False to copy actual files
)

print("Model downloaded to:", model_dir)
# This should print something like "./my_specific_folder"

# 2) Load the QA pipeline FROM that local folder.
#    We pass the same folder for both 'model' and 'tokenizer'.
qa_pipeline = pipeline(
    "question-answering",
    model=model_dir,
    tokenizer=model_dir
)

# 3) Test the pipeline.
context = "We watch movies together."
question = "What does the person watch together?"

result = qa_pipeline({"question": question, "context": context})
print(result)
# Expected output: {'score': ..., 'start': 65, 'end': 89, 'answer': 'milk and cookies'}
