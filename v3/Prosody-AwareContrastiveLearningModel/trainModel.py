import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from v3.model  import PronunciationDataset, ProsodyAwareModel, TripletLoss

FEATURES_CSV = "/home/bhagya-peramuna/PycharmProjects/Bhagya-Reserch/v3/Prosody-AwareContrastiveLearningModel/features.csv"

# Load extracted features
df = pd.read_csv(FEATURES_CSV)
df["wav2vec_embedding"] = df["wav2vec_embedding"].apply(lambda x: np.array(eval(x)))

# Create dataset & dataloader
dataset = PronunciationDataset(df)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Initialize Model, Loss, Optimizer
model = ProsodyAwareModel()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = TripletLoss()

# Training Loop
num_epochs = 20
for epoch in range(num_epochs):
    total_loss = 0
    for wav2vec_emb, prosody in dataloader:
        optimizer.zero_grad()

        anchor = model(wav2vec_emb, prosody)
        positive = model(wav2vec_emb, prosody)  # Simulating positive samples
        negative = model(wav2vec_emb.roll(1, 0), prosody)  # Negative samples (shifted batch)

        loss = criterion(anchor, positive, negative)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch + 1}/{num_epochs} | Loss: {total_loss / len(dataloader):.4f}")

# Save the trained model
MODEL_PATH = "/v3/models/prosody_contrastive_model.pth"
torch.save(model.state_dict(), MODEL_PATH)
print(f"✅ Model training complete! Model saved at {MODEL_PATH}")
