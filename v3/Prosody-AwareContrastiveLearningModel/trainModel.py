import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import PronunciationDataset, ProsodyAwareModel, TripletLoss

FEATURES_CSV = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/Prosody-AwareContrastiveLearningModel/featuresforprosody.csv"

# ✅ Load extracted features
df = pd.read_csv(FEATURES_CSV)

# ✅ Convert stored embeddings & features to NumPy arrays
df["whisper_embedding"] = df["whisper_embedding"].apply(
    lambda x: np.array(eval(x)))  # Convert HuBERT embeddings (1024-d)
df["avg_pitch"] = df["avg_pitch"].astype(float)
df["avg_intensity"] = df["avg_intensity"].astype(float)

# ✅ Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")

# ✅ Create dataset & dataloader
dataset = PronunciationDataset(df)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4,
                        pin_memory=True if device == "cuda" else False)

# ✅ Initialize Model, Loss, Optimizer
model = ProsodyAwareModel(actual_hubert_dim=768, prosody_dim=2, target_hubert_dim=1024, embedding_dim=128).to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = TripletLoss().to(device)  # Move loss function to GPU if needed

num_epochs = 20
loss_history = []
accuracy_history = []

# ✅ Training Loop with Progress Tracking
for epoch in range(num_epochs):
    model.train()
    total_loss = 0.0
    total_acc = 0.0
    num_batches = 0

    for whisper_emb, prosody in dataloader:
        # ✅ Move data to GPU
        whisper_emb, prosody = whisper_emb.to(device), prosody.to(device)

        optimizer.zero_grad()

        # ✅ Forward pass: compute anchor, positive and negative embeddings.
        anchor = model(whisper_emb, prosody)
        positive = model(whisper_emb, prosody)  # Simulating positive samples
        negative = model(whisper_emb.roll(1, 0), prosody.roll(1, 0))  # Shift for negative samples

        # ✅ Compute loss
        loss = criterion(anchor, positive, negative)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # ✅ Compute triplet accuracy (proxy metric)
        # Calculate Euclidean distances for anchor-positive and anchor-negative pairs
        with torch.no_grad():
            pos_dist = torch.norm(anchor - positive, p=2, dim=1)
            neg_dist = torch.norm(anchor - negative, p=2, dim=1)
            batch_acc = (pos_dist < neg_dist).float().mean().item()
        total_acc += batch_acc
        num_batches += 1

    avg_loss = total_loss / num_batches
    avg_acc = total_acc / num_batches
    loss_history.append(avg_loss)
    accuracy_history.append(avg_acc)

    print(f"✅ Epoch {epoch + 1}/{num_epochs} | Loss: {avg_loss:.4f} | Triplet Accuracy: {avg_acc:.4f}")

# ✅ Plotting Training Loss and Accuracy
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(range(1, num_epochs + 1), loss_history, marker='o')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss over Epochs')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(range(1, num_epochs + 1), accuracy_history, marker='o', color='orange')
plt.xlabel('Epoch')
plt.ylabel('Triplet Accuracy')
plt.title('Training Triplet Accuracy over Epochs')
plt.grid(True)

plt.tight_layout()
plt.show()

# ✅ Save the trained model
MODEL_PATH = "/home/minidu-tissera/PycharmProjects/Bhagya-Reserch/v3/models/prosody_contrastive_model.pth"
torch.save(model.state_dict(), MODEL_PATH)
print(f"✅ Model training complete! Model saved at {MODEL_PATH}")
