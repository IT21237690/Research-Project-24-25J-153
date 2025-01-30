import torch
from transformers import T5Tokenizer, T5Config
from model import CustomT5WithStyle, load_pretrained_t5_small_into_custom

def run_inference():
    # --------------------------------------------------
    # 1. Setup: Load tokenizer and model
    # --------------------------------------------------
    model_name = "t5-small"
    tokenizer = T5Tokenizer.from_pretrained(model_name)

    # Optional: ensure your special tokens are added if you used them in training
    special_tokens_dict = {"additional_special_tokens": ["[SAQ]", "[JSQ]"]}
    tokenizer.add_special_tokens(special_tokens_dict)

    # Build our custom model (same config as training)
    config = T5Config.from_pretrained(model_name)
    model = CustomT5WithStyle(config, style_emb_size=32)

    # If needed, load the pretrained T5 weights first (only if your custom model didn't already)
    # load_pretrained_t5_small_into_custom(model)
    model.resize_token_embeddings(len(tokenizer))
    # --------------------------------------------------
    # 2. Load the fine-tuned checkpoint
    # --------------------------------------------------
    # Point to your saved model path
    saved_model_path = "/home/minidu-tissera/PycharmProjects/Research-Project/v11/QG/Models/custom_qg_model_finetiuned.pt"
    model.load_state_dict(torch.load(saved_model_path, map_location="cpu"))
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # --------------------------------------------------
    # 3. Example Inference
    # --------------------------------------------------
    passage = ("We watch movies together.")

    # SAQ example
    style_id = torch.tensor([0], dtype=torch.long, device=device)  # 0 => SAQ
    saq_input = "[SAQ] " + passage
    enc = tokenizer(saq_input, return_tensors="pt").to(device)
    saq_ids = model.custom_generate(
        input_ids=enc["input_ids"],
        attention_mask=enc["attention_mask"],
        style_ids=style_id,
        max_length=20,
        num_beams=1
    )
    saq_question = tokenizer.decode(saq_ids[0], skip_special_tokens=True)
    print("Generated SAQ:", saq_question)

    # JSQ example
    style_id = torch.tensor([1], dtype=torch.long, device=device)  # 1 => JSQ
    jsq_input = "[JSQ] " + passage
    enc = tokenizer(jsq_input, return_tensors="pt").to(device)
    jsq_ids = model.custom_generate(
        input_ids=enc["input_ids"],
        attention_mask=enc["attention_mask"],
        style_ids=style_id,
        max_length=20,
        num_beams=1
    )
    jsq_question = tokenizer.decode(jsq_ids[0], skip_special_tokens=True)
    print("Generated JSQ:", jsq_question)


if __name__ == "__main__":
    run_inference()
