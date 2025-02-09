import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score

# ✅ Load Extracted Features (From Feature Extraction Step)
features_df = pd.read_csv("/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/features.csv")

# ✅ Select Relevant Features for Scoring
numeric_features = ["pronunciation_score", "speaking_rate", "avg_pause", "abnormal_phones"]

# ✅ Normalize Features for Better Training Stability
scaler = MinMaxScaler()
features_df[numeric_features] = scaler.fit_transform(features_df[numeric_features])

# ✅ Define the Target Score
# If expert ratings are available, use them; otherwise, use computed scores
if "expert_score" in features_df.columns:
    target = features_df["expert_score"]
    print("✅ Using expert ratings as target variable")
else:
    # Compute a pseudo-ground-truth score if expert ratings are unavailable
    print("⚠️ No expert ratings found, computing weighted score instead")
    pronunciation_weight, fluency_weight = 0.6, 0.4  # Adjustable weights
    target = pronunciation_weight * features_df["pronunciation_score"] + \
             fluency_weight * (features_df["speaking_rate"] - features_df["avg_pause"] - features_df["abnormal_phones"])

# ✅ Split Data into Training & Testing Sets
X_train, X_test, y_train, y_test = train_test_split(
    features_df[numeric_features], target, test_size=0.2, random_state=42
)

# ✅ Train XGBoost Regression Model
xgb_model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100, max_depth=3)
xgb_model.fit(X_train, y_train)

# ✅ Evaluate Model Performance
y_pred = xgb_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"📊 Model Performance:")
print(f"✅ RMSE: {rmse:.4f}")
print(f"✅ R² Score: {r2:.4f}")

# ✅ Save the trained model for later use
xgb_model.save_model("/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/datasets/scoring_model.bin")
print("✅ Scoring model saved successfully!")

# ✅ Plot Prediction vs. Actual Scores
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], linestyle="--", color="red")
plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.title("XGBoost Regression: Predicted vs. Actual Scores")
plt.show()
