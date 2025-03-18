from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

def load_model():
    try:
        model = T5ForConditionalGeneration.from_pretrained("models/grammar_model")
        tokenizer = T5Tokenizer.from_pretrained("models/grammar_model")
        print("✅ Model loaded successfully")
        return model, tokenizer
    except Exception as e:
        print(f"❌ Loading failed: {e}")
        raise

def test_model():
    model, tokenizer = load_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    test_cases = [
        ("he go to school", "He goes to school"),
        ("i has a apple", "I have an apple"),
        ("they is happy", "They are happy")
    ]

    for original, expected in test_cases:
        input_text = f"grammar: {original}"
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding='max_length'
        ).to(device)

        print(f"\nInput: {original}")
        print("Input tokens:", inputs.input_ids.cpu().numpy()[0])

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=128,
                num_beams=4,
                early_stopping=True
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Expected: {expected}")
        print(f"Actual:   {decoded}")

if __name__ == "__main__":
    test_model()