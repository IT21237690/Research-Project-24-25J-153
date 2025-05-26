import os
import shutil
import difflib
import torch
import torchaudio
import librosa
import numpy as np
import requests
import re
import string
import joblib
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from jiwer import wer, cer
from catboost import CatBoostRegressor
from .models import ProsodyAwareModel
from .utils import normalize_text, transcribe_audio, extract_whisper_embeddings, extract_prosody_features, run_gentle_alignment
from starlette.middleware.cors import CORSMiddleware
from .db import results_collection  # MongoDB collections

app = FastAPI()


# Add CORSMiddleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Load Models
# -----------------------
MODEL_PATH = "/host_data/whisper-finetuned-final"
SCORING_MODEL_PATH = "/host_data/catboost_scoring_model.cbm"
PROSODY_MODEL_PATH = "/host_data/prosody_contrastive_model.pth"
SCALER_PATH = "/host_data/minmax_scaler.pkl"

processor = WhisperProcessor.from_pretrained(MODEL_PATH)
asr_model = WhisperForConditionalGeneration.from_pretrained(MODEL_PATH)
asr_model.eval()

cat_model = CatBoostRegressor()
cat_model.load_model(SCORING_MODEL_PATH)

prosody_model = ProsodyAwareModel()
prosody_model.load_state_dict(torch.load(PROSODY_MODEL_PATH, map_location=torch.device("cpu")))
prosody_model.eval()

scaler = joblib.load(SCALER_PATH)


@app.post("/{user_id}/analyze")
async def analyze_speech(user_id: str,file: UploadFile = File(...), reference_text: str = Form(...)):
    try:
        # Ensure the temp directory exists
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        # Sanitize filename
        safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        temp_audio_path = os.path.join(temp_dir, safe_filename)

        # Save uploaded file
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. ASR Transcription using Whisper
        predicted_text = transcribe_audio(temp_audio_path)
        normalized_reference = normalize_text(reference_text)
        normalized_predicted = normalize_text(predicted_text)

        # 2. Compute WER and CER
        wer_score = wer(normalized_reference, normalized_predicted)
        cer_score = cer(normalized_reference, normalized_predicted)
        pronunciation_score = max(0, 1 - (wer_score + cer_score) / 2)

        # 3. Identify mispronounced words
        ref_words = normalized_reference.split()
        pred_words = normalized_predicted.split()
        diff = list(difflib.ndiff(ref_words, pred_words))
        mispronounced_words = [word[2:] for word in diff if word.startswith('- ')]

        # 4. Compute fluency using Gentle forced alignment
        alignment = run_gentle_alignment(temp_audio_path, reference_text)
        if alignment:
            word_timings = [word["end"] - word["start"] for word in alignment["words"] if "start" in word and "end" in word]
            speaking_rate = len(alignment["words"]) / (word_timings[-1] if word_timings else 1)
            avg_pause = np.mean(np.diff(word_timings)) if len(word_timings) > 1 else 0
            abnormal_phones = wer_score
        else:
            speaking_rate, avg_pause, abnormal_phones = 0, 0, 0

        # 5. Extract Whisper embeddings and prosody features
        whisper_embedding = extract_whisper_embeddings(temp_audio_path)
        prosody_features = extract_prosody_features(temp_audio_path)

        # 6. Pronunciation scoring with the prosody-aware model
        with torch.no_grad():
            whisper_tensor = torch.tensor(whisper_embedding, dtype=torch.float32).unsqueeze(0)
            prosody_tensor = torch.tensor(prosody_features, dtype=torch.float32).unsqueeze(0)
            pronunciation_embedding = prosody_model(whisper_tensor, prosody_tensor)
        pronunciation_embedding = pronunciation_embedding.squeeze().numpy()

        # 7. Score prediction using the CatBoost regression model
        input_features = np.concatenate(
            ([pronunciation_score, speaking_rate, avg_pause, abnormal_phones], pronunciation_embedding)
        )
        input_features = input_features.reshape(1, -1)
        input_features = scaler.transform(input_features)
        predicted_score = cat_model.predict(input_features)[0]

        # 8. Final score adjustments
        if len(normalized_reference.split()) != len(normalized_predicted.split()):
            final_score = 0.0
        elif pronunciation_score < 0.5:
            final_score = predicted_score * pronunciation_score
        else:
            final_score = predicted_score

        # Cleanup temporary file
        os.remove(temp_audio_path)

        # Log evaluation data to MongoDB
        record = {
            "user_id": user_id,
            "ReferenceText": reference_text,
            "PronunciationScore": pronunciation_score,
            "SpeakingRate(words/sec)": speaking_rate,
            "AveragePauseDuration (sec)": avg_pause,
            "AbnormalPhones(approx)": abnormal_phones,
            "FinalFluencyScore": final_score,
            "MispronouncedWords": mispronounced_words
        }
        results_collection.insert_one(record)

        return {
            "Reference Text": reference_text,
            "Predicted Text": predicted_text,
            "WER": wer_score,
            "CER": cer_score,
            "pronunciationScore": pronunciation_score,
            "Speaking Rate (words/sec)": speaking_rate,
            "Average Pause Duration (sec)": avg_pause,
            "Abnormal Phones (approx)": abnormal_phones,
            "fluencyScore": final_score,
            "mispronouncedWords": mispronounced_words
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
