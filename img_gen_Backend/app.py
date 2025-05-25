# Your existing imports...
from flask import Flask, request, jsonify
import random
import pandas as pd
from transformers import T5ForConditionalGeneration, T5Tokenizer
from image_generator import ImageGenerator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from PIL import Image
import base64
from io import BytesIO
from flask_cors import CORS
from utils.feedback import generate_feedback, correct_grammar

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize image generator and grammar models
from authtoken import auth_token
image_gen = ImageGenerator(auth_token)

try:
    grammar_tokenizer = T5Tokenizer.from_pretrained("host_data/grammar_model")
    grammar_model = T5ForConditionalGeneration.from_pretrained("host_data/grammar_model")
except Exception as e:
    print(f"Error loading grammar model: {str(e)}")
    raise

# Load prompts
csv_path = "Dataset_Image_gen.csv" # Correct for Docker
#csv_path = "D:\\SLIIT\\Year 04\\Research\\Datasets\\Dataset_Image_gen.csv"
df = pd.read_csv(csv_path)
prompts = df.iloc[:, 0].tolist()  # Assuming the prompts are in the first column

# Helper function to convert PIL image to base64
def pil_to_base64(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# API to generate an image from a random prompt
@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        prompt = random.choice(prompts)
        generated_image = image_gen.generate(prompt)
        image_base64 = pil_to_base64(generated_image)
        return jsonify({"image": image_base64, "prompt": prompt}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to check grammar
@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "Text is required!"}), 400
    
    try:
        feedback, corrected = generate_feedback(text, grammar_tokenizer, grammar_model)
        return jsonify({"feedback": feedback, "corrected_text": corrected}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to check similarity
@app.route('/check-similarity', methods=['POST'])
def check_similarity():
    data = request.json
    text = data.get('text', '')
    prompt = data.get('prompt', '')
    
    if not text or not prompt:
        return jsonify({"error": "Text and prompt are required!"}), 400

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([prompt, text])
        similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]

        if similarity_score > 0.8:
            similarity_feedback = "Great match! Your description closely matches the image."
        elif similarity_score > 0.5:
            similarity_feedback = "Good match! Your description is reasonably similar to the image."
        elif similarity_score > 0.3:
            similarity_feedback = "Moderate match. Try focusing more on the key elements from the image."
        else:
            similarity_feedback = "Low similarity! Try to focus more on the key details from the image."

        return jsonify({"similarity_score": similarity_score, "feedback": similarity_feedback}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to display final score
@app.route('/final-score', methods=['POST'])
def final_score():
    try:
        similarity_scores = request.json.get("similarity_scores", [])
        if similarity_scores:
            avg_score = sum(similarity_scores) / len(similarity_scores)
        else:
            avg_score = 0

        if avg_score > 0.8:
            feedback_text = "Great job! Your descriptions are very accurate."
        elif avg_score > 0.5:
            feedback_text = "Good effort! There's room for improvement."
        else:
            feedback_text = "Needs improvement. Focus on details and accuracy."

        return jsonify({"final_score": avg_score, "feedback": feedback_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
