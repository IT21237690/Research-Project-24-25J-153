import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from catboost import CatBoostRegressor, Pool
import joblib

# ✅ Paths
FEATURES_CSV = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/datasets/features.csv"
MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/catboost_scoring_model.cbm"

# ✅ Load Extracted Features (From Feature Extraction Step)
df = pd.read_csv(FEATURES_CSV)

# ✅ Ensure no missing values
df.fillna(0, inplace=True)

# ✅ Select Features for Scoring Model:
# Assume the CSV now contains the original four features plus 128 embedding features
base_features = ["pronunciation_score", "speaking_rate", "avg_pause", "abnormal_phones"]
embedding_features = [f"embed_{i}" for i in range(128)]
all_features = base_features + embedding_features

# Check if all required columns are present
missing_cols = set(all_features) - set(df.columns)
if missing_cols:
    raise ValueError(f"The following expected columns are missing from the CSV: {missing_cols}")

# ✅ Normalize Features for Stability
scaler = MinMaxScaler()
df[all_features] = scaler.fit_transform(df[all_features])

# ✅ Define Target Score
if "expert_score" in df.columns:
    target = df["expert_score"]
    print("✅ Using expert ratings as target variable")
else:
    print("⚠️ No expert ratings found, computing weighted score instead")
    pronunciation_weight, fluency_weight = 0.7, 0.3
    target = (
        pronunciation_weight * df["pronunciation_score"] +
        fluency_weight * (df["speaking_rate"] - df["avg_pause"] - df["abnormal_phones"])
    )

# ✅ Split Data into Training & Testing Sets
X_train, X_test, y_train, y_test = train_test_split(
    df[all_features], target, test_size=0.2, random_state=42
)

# ================= Novelty Part: Hyperparameter Tuning via GridSearchCV =================
# Define a reduced parameter grid for CatBoostRegressor to reduce computational load
param_grid = {
    'depth': [4, 5],            # Reduced depth options
    'learning_rate': [0.05, 0.1],
    'iterations': [300]         # Lower number of iterations
}

# Define monotonic constraints: enforce a positive relationship for "pronunciation_score" (first feature)
# and no constraints (0) for all remaining features.
monotonic_constraints = [1] + [0] * (len(all_features) - 1)

# Initialize a base CatBoostRegressor with silent training for grid search
cat_model = CatBoostRegressor(
    loss_function='RMSE',
    eval_metric='RMSE',
    random_state=42,
    task_type="CPU",    # Run on CPU only
    verbose=0,          # Suppress output during grid search
    monotone_constraints=monotonic_constraints
)

# Wrap training data in a Pool object (optional but recommended)
train_pool = Pool(X_train, y_train)

# Setup GridSearchCV with 5-fold CV
grid_search = GridSearchCV(estimator=cat_model, param_grid=param_grid, cv=5, scoring='r2', n_jobs=-1)
grid_search.fit(X_train, y_train)

print("📊 Best Parameters from GridSearchCV:", grid_search.best_params_)
print("✅ Best CV R² Score:", grid_search.best_score_)

# Use the best estimator from grid search for final training
best_cat_model = grid_search.best_estimator_

# ================= End of Novelty Part =================

# ✅ Train CatBoost Regression Model with Early Stopping
best_cat_model.fit(
    X_train, y_train,
    eval_set=(X_test, y_test),
    early_stopping_rounds=50,
    verbose=200  # This will now show progress updates every 200 iterations
)

# ✅ Cross-Validation for Robustness
cv_scores = cross_val_score(best_cat_model, X_train, y_train, cv=5, scoring="r2")
print(f"📊 Cross-Validation R² Scores: {cv_scores}")
print(f"✅ Mean CV R² Score: {np.mean(cv_scores):.4f}")

# ✅ Evaluate Model Performance on the Test Set
y_pred = best_cat_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"📊 Final Model Performance:")
print(f"✅ RMSE: {rmse:.4f}")
print(f"✅ R² Score: {r2:.4f}")

# Save the fitted scaler to disk
scaler_path = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/minmax_scaler.pkl"
joblib.dump(scaler, scaler_path)
print(f"✅ Scaler saved at: {scaler_path}")

# ✅ Save the trained model
best_cat_model.save_model(MODEL_PATH)
print(f"✅ Scoring model saved at: {MODEL_PATH}")

# ✅ Plot Predicted vs. Actual Scores
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.5, label="Predictions")
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], linestyle="--", color="red", label="Ideal Fit")
plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.title("CatBoost Regression: Predicted vs. Actual Scores")
plt.legend()
plt.show()

# ✅ Feature Importance Plot (For better model interpretability)
feature_importances = best_cat_model.get_feature_importance(Pool(X_train, y_train))
plt.figure(figsize=(12, 6))
plt.bar(range(len(all_features)), feature_importances, tick_label=all_features)
plt.xticks(rotation=90)
plt.xlabel("Features")
plt.ylabel("Importance")
plt.title("Feature Importances from CatBoost Model")
plt.tight_layout()
plt.show()
