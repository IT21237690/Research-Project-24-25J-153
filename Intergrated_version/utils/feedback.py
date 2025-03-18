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
    
    # Step 3: Create a word-level comparison between original and corrected text
    original_words = original.split()
    corrected_words = corrected.split()
    
    # Use difflib.SequenceMatcher for word-level comparison
    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    changes = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Words replaced (better formatting)
            old_phrase = " ".join(original_words[i1:i2])
            new_phrase = " ".join(corrected_words[j1:j2])
            changes.append(f"Replace: '{old_phrase}' → '{new_phrase}'")
        elif tag == 'delete':
            # Words deleted
            deleted_phrase = " ".join(original_words[i1:i2])
            changes.append(f"Remove: '{deleted_phrase}'")
        elif tag == 'insert':
            # Words inserted
            inserted_phrase = " ".join(corrected_words[j1:j2])
            changes.append(f"Add: '{inserted_phrase}'")
    
    # Step 4: Format the feedback
    feedback = "=== Grammar Feedback ===\n"
    
    # Add error count
    feedback += f"Found {len(matches)} grammar error(s)\n\n"
    
    # Add corrections
    feedback += "=== Corrections ===\n"
    if changes:
        feedback += "\n".join(changes) + "\n"
    else:
        feedback += "No changes needed!\n"
    
    # Add suggestions
    feedback += "\n=== Suggestions ===\n"
    if matches:
        for match in matches[:3]:  # Show top 3 errors
            feedback += f"- {match.ruleId}: {match.message}\n"
            if match.replacements:
                feedback += f"  Suggested fix: {match.replacements[0]}\n"
    else:
        feedback += "No grammar suggestions.\n"
    
    return feedback, corrected
