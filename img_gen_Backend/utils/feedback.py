import difflib
import language_tool_python
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Initialize LanguageTool
tool = language_tool_python.LanguageTool('en-US')

# Grammar correction using your trained model
def correct_grammar(text, tokenizer, model):
    inputs = tokenizer(
        f"grammar: {text}",
        return_tensors="pt",
        max_length=128,
        truncation=True
    )
    outputs = model.generate(**inputs)
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return corrected

# Generate feedback
def generate_feedback(original, tokenizer, model):
    """Generate feedback using both LanguageTool and your trained model"""
    # Step 1: Correct grammar using your model
    corrected = correct_grammar(original, tokenizer, model)
    
    # Step 2: Check grammar errors using LanguageTool
    matches = tool.check(original)
    
    # Step 3: Format the feedback
    feedback = "Feedback Report!✨\n"
    
    # Add error count
    feedback += f"Found {len(matches)} grammar error(s)\n\n"
    
    # Add suggestions (keep only this part)
    feedback += "Suggestions for you to keep in mind: \n"
    if matches:
        for match in matches[:3]:  # Show top 3 errors
            feedback += f"{match.ruleId}: {match.message}\n"
            if match.replacements:
                feedback += f"Suggested fix: {match.replacements[0]}\n"
    else:
        feedback += "No grammar suggestions.\n"
    
    return feedback, corrected
