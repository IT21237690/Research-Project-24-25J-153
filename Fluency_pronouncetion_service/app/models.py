import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
import numpy as np


class PronunciationDataset(Dataset):
    """Custom Dataset for Pronunciation Features"""

    def __init__(self, df):
        self.df = df
        self.features = np.vstack(df["whisper_embedding"].values)  # Load embeddings (e.g., actual_dim=768)
        self.prosodic = df[["avg_pitch", "avg_intensity"]].values  # Load prosodic features

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        hubert_emb = torch.tensor(self.features[idx], dtype=torch.float32)
        prosody_features = torch.tensor(self.prosodic[idx], dtype=torch.float32)
        return hubert_emb, prosody_features


class ProsodyAwareModel(nn.Module):
    def __init__(self, actual_hubert_dim=768, prosody_dim=2, target_hubert_dim=1024, embedding_dim=128):
        """
        actual_hubert_dim: the dimension of the embeddings produced by your ASR model (e.g., 768 for Whisper).
        target_hubert_dim: the dimension expected by downstream parts of your prosody model (e.g., 1024).
        """
        super().__init__()
        self.actual_hubert_dim = actual_hubert_dim
        self.prosody_dim = prosody_dim
        self.target_hubert_dim = target_hubert_dim

        # Projection layer to map from actual to target dimension if needed
        if actual_hubert_dim != target_hubert_dim:
            self.projection = nn.Linear(actual_hubert_dim, target_hubert_dim)
        else:
            self.projection = nn.Identity()

        # Define input_dim as target_hubert_dim plus prosodic features
        self.input_dim = target_hubert_dim + prosody_dim

        self.attn = nn.Sequential(
            nn.Linear(prosody_dim, 16),
            nn.Tanh(),
            nn.Linear(16, prosody_dim),
            nn.Softmax(dim=-1)
        )

        self.encoder = nn.Sequential(
            nn.Linear(self.input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, hubert_emb, prosodic_features):
        """
        hubert_emb: expected shape (batch, actual_hubert_dim) or (batch, seq_len, actual_hubert_dim)
        prosodic_features: expected shape (batch, prosody_dim)
        """
        # If hubert_emb is 2D, add a sequence dimension
        if hubert_emb.dim() == 2:
            hubert_emb = hubert_emb.unsqueeze(1)  # (batch, 1, actual_hubert_dim)
        # Project the embeddings to target_hubert_dim
        # First, flatten to combine batch and seq_len dimensions, apply projection, then reshape back.
        batch_size, seq_len, _ = hubert_emb.shape
        hubert_flat = hubert_emb.view(-1, self.actual_hubert_dim)  # (batch*seq_len, actual_hubert_dim)
        projected = self.projection(hubert_flat)  # (batch*seq_len, target_hubert_dim)
        projected = projected.view(batch_size, seq_len, self.target_hubert_dim)  # (batch, seq_len, target_hubert_dim)

        # Handle prosodic features
        if prosodic_features.dim() == 3:
            prosodic_features = prosodic_features.squeeze(1)  # (batch, prosody_dim)

        weights = self.attn(prosodic_features)  # (batch, prosody_dim)
        weighted_prosody = prosodic_features * weights  # (batch, prosody_dim)
        weighted_prosody = weighted_prosody.unsqueeze(1).expand(-1, seq_len, -1)  # (batch, seq_len, prosody_dim)

        # Fuse projected embeddings with prosodic features
        fusion = torch.cat([projected, weighted_prosody], dim=-1)  # (batch, seq_len, target_hubert_dim + prosody_dim)

        # Verify the concatenated dimension
        assert fusion.shape[-1] == self.input_dim, f"Expected last dim {self.input_dim}, but got {fusion.shape[-1]}"

        # Aggregate across time and pass through encoder
        fused_embedding = fusion.mean(dim=1)  # (batch, input_dim)
        return self.encoder(fused_embedding)


class TripletLoss(nn.Module):
    """Triplet Loss for Contrastive Learning"""

    def __init__(self, margin=0.3):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        pos_dist = F.pairwise_distance(anchor, positive)
        neg_dist = F.pairwise_distance(anchor, negative)
        loss = F.relu(pos_dist - neg_dist + self.margin).mean()
        return loss
