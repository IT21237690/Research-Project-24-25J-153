# utils/data_utils.py
import random
import re
from sklearn.model_selection import train_test_split

BASE_SENTENCES = [
    "The cat sits on the mat.",
    "She is reading an interesting book.",
    "They have three apples and two oranges.",
    "We went to the park yesterday.",
    "He plays football every Saturday."
]

ERROR_RULES = {
    'articles': [
        (r'\b(a)\s+([aeiou])', r'an \2'),          # a → an before vowels
        (r'\b(an)\s+([^aeiou])', r'a \2'),         # an → a before consonants
        (r'\bthe\b', '')                           # Remove unnecessary 'the'
    ],
    'verb_tense': [
        (r'\b(sits)\b', 'sit'),                    # Present simple 3rd person → base
        (r'\b(read)\b', 'reading'),                 # Base form → present continuous
        (r'\b(went)\b', 'go'),                      # Past → base
        (r'\b(plays)\b', 'play')                   # 3rd person → base
    ],
    'prepositions': [
        (r'\b(on)\b', 'in'),                       # on → in
        (r'\b(in)\b', 'at'),                        # in → at
        (r'\b(to)\b', 'towards')                    # to → towards
    ]
}

def introduce_errors(sentence):
    """Guarantee at least one error per sentence"""
    original = sentence
    attempts = 0
    
    while sentence == original and attempts < 5:
        error_type = random.choice(list(ERROR_RULES.keys()))
        pattern, replacement = random.choice(ERROR_RULES[error_type])
        
        # Apply substitution only if pattern exists
        if re.search(pattern, sentence, flags=re.IGNORECASE):
            sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
        
        attempts += 1
    
    return sentence if sentence != original else f"ERROR: {original}"

def generate_data_pairs(num_samples=1000):
    """Generate guaranteed incorrect/correct pairs"""
    pairs = []
    for _ in range(num_samples):
        base = random.choice(BASE_SENTENCES)
        corrupted = introduce_errors(base)
        
        # Ensure we have a valid error
        if corrupted.startswith("ERROR:"):
            continue  # Skip failed attempts
        pairs.append((corrupted, base))
    
    return pairs

def prepare_semantic_data():
    """Generate training data with guaranteed errors"""
    pairs = generate_data_pairs()
    
    # Filter out any remaining identical pairs
    filtered_pairs = [(inc, cor) for inc, cor in pairs if inc != cor]
    
    # Split and save
    train, val = train_test_split(filtered_pairs, test_size=0.2)
    
    with open('data/train.txt', 'w') as f:
        f.write('\n'.join([f"{inc}\t{cor}" for inc, cor in train]))
    
    with open('data/val.txt', 'w') as f:
        f.write('\n'.join([f"{inc}\t{cor}" for inc, cor in val]))

if __name__ == '__main__':
    prepare_semantic_data()