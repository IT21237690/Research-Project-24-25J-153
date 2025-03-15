import joblib
import pandas as pd

MODEL_PATH = "app/model/adjustment_model_optimized.pkl"

def load_adjustment_model():
    """
    Load the trained difficulty adjustment model.
    """
    return joblib.load(MODEL_PATH)

def predict_adjustment(model, current_difficulty, similarity, reward):
    """
    Predicts difficulty adjustment based on features that match training data.
    """
    features = pd.DataFrame([[current_difficulty, similarity, reward]],
                            columns=['current_difficulty', 'answer_similarity', 'user_reward'])  # Removed "readability"
    return model.predict(features)[0]


