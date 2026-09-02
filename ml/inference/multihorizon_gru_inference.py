import torch
import torch.nn as nn


class MultiHorizonGRU(nn.Module):
    def __init__(self, input_size=68, hidden_size=96, num_layers=2, dropout=0.30):
        super().__init__()
        self.gru = nn.GRU(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=dropout)
        self.norm = nn.LayerNorm(hidden_size)
        self.shared = nn.Sequential(nn.Linear(hidden_size, 48), nn.ReLU(), nn.Dropout(dropout))
        self.head_50 = nn.Linear(48, 1)
        self.head_100 = nn.Linear(48, 1)
        self.head_200 = nn.Linear(48, 1)
        self.head_500 = nn.Linear(48, 1)

    def forward(self, x):
        output, _hidden = self.gru(x)
        last_state = output[:, -1, :]
        last_state = self.norm(last_state)
        shared = self.shared(last_state)
        return (self.head_50(shared).squeeze(1), self.head_100(shared).squeeze(1), self.head_200(shared).squeeze(1), self.head_500(shared).squeeze(1))


class MultiHorizonGRUInference:
    def __init__(self, checkpoint_path):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device("cpu")
        self.checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model = MultiHorizonGRU(**self.checkpoint["architecture"])
        self.model.load_state_dict(self.checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        self.horizons = self.checkpoint["horizons"]
        self.thresholds = self.checkpoint["thresholds"]

    def predict(self, sequence):
        x = torch.tensor(sequence, dtype=torch.float32, device=self.device).unsqueeze(0) if not isinstance(sequence, torch.Tensor) else sequence.to(dtype=torch.float32, device=self.device)
        if x.ndim == 2:
            x = x.unsqueeze(0)
        if tuple(x.shape[1:]) != (100, 68):
            raise ValueError(f"Expected input shape (100, 68), got {tuple(x.shape[1:])}")
        if not torch.isfinite(x).all():
            raise ValueError("Input sequence contains NaN or infinite values")
        with torch.no_grad():
            logits = self.model(x)
        probabilities = {h: float(torch.sigmoid(logit)[0].item()) for h, logit in zip(self.horizons, logits)}
        predictions = {h: int(probabilities[h] >= float(self.thresholds[h])) for h in self.horizons}
        return {"probabilities": probabilities, "thresholds": self.thresholds, "predictions": predictions}
