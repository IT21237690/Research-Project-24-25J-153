import torch
from .models import model, tokenizer, DEVICE


def generate_question(passage: str, question_type: str):
    """Generate a question given a passage and question type ('SAQ' or 'JSQ')."""

    # Map question type to style ID
    style_mapping = {"SAQ": 0, "JSQ": 1}
    if question_type not in style_mapping:
        raise ValueError("Invalid question type. Choose 'SAQ' or 'JSQ'.")

    # Prepare input for the model
    style_id = torch.tensor([style_mapping[question_type]], dtype=torch.long, device=DEVICE)
    input_text = f"[{question_type}] {passage}"
    enc = tokenizer(input_text, return_tensors="pt").to(DEVICE)

    # Generate question
    output_ids = model.custom_generate(
        input_ids=enc["input_ids"],
        attention_mask=enc["attention_mask"],
        style_ids=style_id,
        max_length=20,
        num_beams=1
    )

    question = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return question
