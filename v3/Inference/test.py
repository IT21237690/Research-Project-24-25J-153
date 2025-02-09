import numpy as np
import pronouncing
import torch
import torchaudio
import xgboost as xgb
import parselmouth
from transformers import Wav2Vec2Processor, Wav2Vec2Model

from v3.FeatureExtraction import calculate_fluency
from v3.model import ProsodyAwareModel  # Trained pronunciation model
from v3.Inference.realTimeForceAlignment import align_audio_with_text  # Forced alignment

# ✅ Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")

# ✅ Load Wav2Vec2 Processor & Model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h").to(device)
wav2vec_model.eval()

# ✅ Load trained pronunciation model
contrastive_model_path = "/v3/Prosody-AwareContrastiveLearningModel/prosody_contrastive_model.pth"
prosody_model = ProsodyAwareModel().to(device)
prosody_model.load_state_dict(torch.load(contrastive_model_path, map_location=device))
prosody_model.eval()

# ✅ Load trained XGBoost scoring model
scoring_model_path = "/v3/datasets/scoring_model.bin"
scoring_model = xgb.XGBRegressor()
scoring_model.load_model(scoring_model_path)

# ✅ Disable gradient computation
torch.set_grad_enabled(False)

def extract_features(audio_path):
    """Extract Wav2Vec2 embeddings & prosodic features."""
    print(f"🔹 Extracting features for: {audio_path}")
    try:
        # ✅ Load audio file
        waveform, sample_rate = torchaudio.load(audio_path)
        print(f"📢 Loaded waveform: {waveform.shape}, Sample Rate: {sample_rate}")

        # ✅ Convert stereo to mono if needed
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)  # Convert stereo to mono
            print("📢 Converted audio to mono")

        if sample_rate != 16000:
            waveform = torchaudio.transforms.Resample(sample_rate, 16000)(waveform)
            print("📢 Resampled audio to 16kHz")

        waveform = waveform.to(device)

        # ✅ Extract Wav2Vec2 embeddings
        inputs = processor(waveform.squeeze().cpu().numpy(), return_tensors="pt", sampling_rate=16000, padding=True).to(device)
        with torch.no_grad():
            wav2vec_embedding = wav2vec_model(**inputs).last_hidden_state.mean(dim=1).squeeze()

        print(f"✅ Extracted Wav2Vec2 Embedding Shape: {wav2vec_embedding.shape}")

        if len(wav2vec_embedding.shape) == 1:
            wav2vec_embedding = wav2vec_embedding.unsqueeze(0)  # Convert to [1, embedding_dim]

        # ✅ Extract prosodic features
        sound = parselmouth.Sound(audio_path)
        pitch = sound.to_pitch()
        intensity = sound.to_intensity()

        avg_pitch = np.mean(pitch.selected_array['frequency'][pitch.selected_array['frequency'] > 0]) if len(pitch.selected_array['frequency']) > 0 else 0
        avg_intensity = np.mean(intensity.values.T.flatten()) if len(intensity.values.T.flatten()) > 0 else 0

        prosody_features = torch.tensor([avg_pitch, avg_intensity], dtype=torch.float32).unsqueeze(0).to(device)

        print(f"✅ Extracted Prosodic Features: Pitch={avg_pitch}, Intensity={avg_intensity}")
        return wav2vec_embedding, prosody_features

    except Exception as e:
        print(f"❌ Error extracting features from {audio_path}: {e}")
        return None, None




def get_expected_phonemes(reference_text):
    """Convert reference text into expected phoneme sequence."""
    words = reference_text.split()
    expected_phonemes = []

    for word in words:
        phoneme_list = pronouncing.phones_for_word(word)
        if phoneme_list:
            expected_phonemes.extend(phoneme_list[0].split())  # Take first pronunciation
        else:
            expected_phonemes.extend([char.upper() + "0" for char in word])  # Fallback (letter-level)

    return expected_phonemes


def calculate_per(expected_phonemes, detected_phonemes):
    """Compute Phoneme Error Rate (PER) - measures how different detected phonemes are from reference."""
    ref_len, detected_len = len(expected_phonemes), len(detected_phonemes)
    if ref_len == 0:
        return 1.0  # If no reference phonemes exist, return max error

    dp = np.zeros((ref_len + 1, detected_len + 1))
    for i in range(ref_len + 1):
        dp[i, 0] = i
    for j in range(detected_len + 1):
        dp[0, j] = j

    for i in range(1, ref_len + 1):
        for j in range(1, detected_len + 1):
            cost = 0 if expected_phonemes[i - 1] == detected_phonemes[j - 1] else 1
            dp[i, j] = min(dp[i - 1, j] + 1, dp[i, j - 1] + 1, dp[i - 1, j - 1] + cost)

    return dp[ref_len, detected_len] / ref_len


def predict_pronunciation_score(audio_path, reference_text, phoneme_alignment):
    """Compute pronunciation score using contrastive learning AND phoneme accuracy."""
    print(f"🔹 Predicting pronunciation score for: {audio_path}")

    # Extract phonemes from reference text
    expected_phonemes = get_expected_phonemes(reference_text)
    print(f"🔍 Expected Phonemes: {expected_phonemes}")

    # Extract detected phonemes from forced alignment
    detected_phonemes = [p["phoneme"] for p in phoneme_alignment]
    print(f"🔍 Detected Phonemes: {detected_phonemes}")

    # Compute phoneme error rate (PER)
    per_score = calculate_per(expected_phonemes, detected_phonemes)
    print(f"✅ Computed Phoneme Error Rate (PER): {per_score}")

    # Get pronunciation embedding score from contrastive model
    wav2vec_emb, prosody_features = extract_features(audio_path)
    if wav2vec_emb is None or prosody_features is None:
        return None  # Skip processing if feature extraction failed

    with torch.no_grad():
        embedding = prosody_model(wav2vec_emb, prosody_features)

    base_pronunciation_score = float(embedding.norm().cpu())

    # **Adjust pronunciation score using PER (lower PER = better pronunciation)**
    final_score = base_pronunciation_score * (1 - per_score)
    print(f"✅ Adjusted Pronunciation Score: {final_score} (Base: {base_pronunciation_score})")

    return final_score


def predict_fluency_score(features_dict, per_score):
    """Compute final pronunciation fluency score using the XGBoost scoring model."""
    print("🔹 Predicting fluency score...")
    try:
        feature_values = np.array([
            features_dict["pronunciation_score"],
            features_dict["speaking_rate"],
            features_dict["avg_pause"],
            features_dict["abnormal_phones"]
        ]).reshape(1, -1)

        base_fluency_score = scoring_model.predict(feature_values)[0]
        print(f"✅ Base Fluency Score: {base_fluency_score}")

        # **Apply a penalty if PER is too high (i.e., words don't match)**
        adjusted_fluency_score = base_fluency_score * (1 - per_score)
        adjusted_fluency_score = round(max(0, adjusted_fluency_score), 3)  # Ensure score is not negative

        print(f"✅ Adjusted Fluency Score: {adjusted_fluency_score} (Penalty from PER: {per_score})")
        return adjusted_fluency_score

    except Exception as e:
        print(f"❌ Error predicting fluency score: {e}")
        return None


def process_audio(reference_text, audio_path):
    """Process a new audio file for real-time scoring."""
    print(f"\n🔹 Processing new audio for scoring: {audio_path}")
    print(f"📜 Reference Sentence: {reference_text}")

    try:
        # ✅ Step 1: Perform Forced Alignment
        print("🔹 Running Forced Alignment...")
        word_alignment, phoneme_alignment = align_audio_with_text(audio_path, reference_text)
        if word_alignment is None or phoneme_alignment is None:
            print("❌ Forced alignment failed.")
            return None

        print("✅ Forced alignment successful!")

        # ✅ Step 2: Compute Pronunciation Score
        pronunciation_score = predict_pronunciation_score(audio_path, reference_text, phoneme_alignment)
        if pronunciation_score is None:
            print("❌ Skipping due to pronunciation extraction failure.")
            return None

        # ✅ Step 3: Compute Fluency Features
        print("🔹 Computing fluency metrics...")
        fluency_metrics = calculate_fluency(word_alignment, phoneme_alignment)
        print(f"✅ Fluency Features: {fluency_metrics}")

        # ✅ Step 4: Compute Phoneme Error Rate (PER)
        expected_phonemes = get_expected_phonemes(reference_text)
        detected_phonemes = [p["phoneme"] for p in phoneme_alignment]
        per_score = calculate_per(expected_phonemes, detected_phonemes)
        print(f"✅ Computed Phoneme Error Rate (PER): {per_score}")

        # ✅ Step 5: Compute Final Score using XGBoost
        features_dict = {
            "pronunciation_score": pronunciation_score,
            "speaking_rate": fluency_metrics["speaking_rate"],
            "avg_pause": fluency_metrics["avg_pause"],
            "abnormal_phones": fluency_metrics["abnormal_phones"]
        }

        final_score = predict_fluency_score(features_dict, per_score)

        result = {
            "reference_text": reference_text,
            "pronunciation_score": pronunciation_score,
            "fluency_score": final_score,
            "features": features_dict
        }

        print("\n✅ Processing Complete! Final Results:")
        print(f"📜 Reference Sentence: {result['reference_text']}")
        print(f"📊 Pronunciation Score: {result['pronunciation_score']}")
        print(f"📊 Fluency Score: {result['fluency_score']}")
        return result

    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        return None


# ✅ Example Usage: Predict score for a user’s spoken sentence
reference_text = "the quick brown fox jumps over the lazy dog"
audio_path = "/v3/test.wav"

result = process_audio(reference_text, audio_path)
# the quick brown fox jumps over the lazy dog