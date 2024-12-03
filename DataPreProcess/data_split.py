import pandas as pd
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv('../dataset/train.csv')

# Ensure dataset is large enough to handle the splits
assert len(df) > 20, "Dataset is too small for this split!"

# Step 1: Split into Training (80%) and Temp (20%)
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)

# Step 2: Split Temp into Validation (15%) and Test (5%)
val_df, test_df = train_test_split(temp_df, test_size=0.25, random_state=42)  # 0.25 x 20% = 5%

# Save the splits to separate CSV files
train_df.to_csv('../dataset/train.csv', index=False)
val_df.to_csv('../dataset/validation.csv', index=False)
test_df.to_csv('../dataset/test.csv', index=False)

# Print the counts for each split
print(f"Training set size: {len(train_df)}")
print(f"Validation set size: {len(val_df)}")
print(f"Test set size: {len(test_df)}")

