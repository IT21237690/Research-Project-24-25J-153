import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
import numpy as np
import pandas as pd

class PronunciationDataset(Dataset):
    def __init__(self, df):
        self.df = df
        self.features = np.vstack(df["wav2vec_embedding"].values)
        self.prosodic = df[["avg_pitch", "avg_intensity"]].values

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        wav2vec_emb = torch.tensor(self.features[idx], dtype=torch.float32)
        prosody_features = torch.tensor(self.prosodic[idx], dtype=torch.float32)
        return wav2vec_emb, prosody_features

class ProsodyAwareModel(nn.Module):
    def __init__(self, input_dim=770, embedding_dim=128):
        super().__init__()

        # Attention-based prosodic feature fusion
        self.attn = nn.Sequential(
            nn.Linear(2, 16),
            nn.Tanh(),
            nn.Linear(16, 2),
            nn.Softmax(dim=-1)
        )

        # Feature encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, wav2vec_emb, prosodic_features):
        weights = self.attn(prosodic_features)
        weighted_prosody = prosodic_features * weights
        fusion = torch.cat([wav2vec_emb, weighted_prosody], dim=-1)

        return self.encoder(fusion)

class TripletLoss(nn.Module):
    def __init__(self, margin=0.3):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        pos_dist = F.pairwise_distance(anchor, positive)
        neg_dist = F.pairwise_distance(anchor, negative)
        loss = F.relu(pos_dist - neg_dist + self.margin).mean()
        return loss
