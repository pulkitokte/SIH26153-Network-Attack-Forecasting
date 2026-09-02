import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from pathlib import Path

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)

# =========================================================
# CICIDS2017 - GRU DDoS EARLY-WARNING FORECASTER
#
# Input:
#   100 historical flows × 68 features
#
# Output:
#   Probability that DDoS appears in the NEXT 100 flows
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

MODEL_FILE = MODEL_DIR / "ddos_gru_forecaster.pt"
REPORT_FILE = REPORT_DIR / "gru_forecasting_report.txt"

SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 75)
print("CICIDS2017 - GRU DDoS EARLY-WARNING FORECASTER")
print("=" * 75)

print(f"\nDevice: {DEVICE}")

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("\nLoading sequence tensors...")

X_train = np.load(DATA_DIR / "X_train.npy")
y_train = np.load(DATA_DIR / "y_train.npy")

X_validation = np.load(DATA_DIR / "X_validation.npy")
y_validation = np.load(DATA_DIR / "y_validation.npy")

X_test = np.load(DATA_DIR / "X_test.npy")
y_test = np.load(DATA_DIR / "y_test.npy")

print(f"X_train      : {X_train.shape}")
print(f"X_validation : {X_validation.shape}")
print(f"X_test       : {X_test.shape}")

# ---------------------------------------------------------
# Convert to PyTorch tensors
# ---------------------------------------------------------

X_train_tensor = torch.tensor(
    X_train,
    dtype=torch.float32
)

y_train_tensor = torch.tensor(
    y_train,
    dtype=torch.float32
)

X_validation_tensor = torch.tensor(
    X_validation,
    dtype=torch.float32
)

y_validation_tensor = torch.tensor(
    y_validation,
    dtype=torch.float32
)

X_test_tensor = torch.tensor(
    X_test,
    dtype=torch.float32
)

y_test_tensor = torch.tensor(
    y_test,
    dtype=torch.float32
)

train_dataset = TensorDataset(
    X_train_tensor,
    y_train_tensor
)

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True
)

# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

class GRUForecaster(nn.Module):

    def __init__(
        self,
        input_size=68,
        hidden_size=64,
        num_layers=2,
        dropout=0.25
    ):

        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )

    def forward(self, x):

        output, hidden = self.gru(x)

        # Representation from final time step
        final_state = output[:, -1, :]

        logits = self.classifier(
            final_state
        ).squeeze(1)

        return logits


model = GRUForecaster().to(DEVICE)

print("\nModel:")
print(model)

# ---------------------------------------------------------
# Class imbalance handling
# ---------------------------------------------------------

positive_count = np.sum(y_train == 1)
negative_count = np.sum(y_train == 0)

pos_weight_value = (
    negative_count / positive_count
)

pos_weight = torch.tensor(
    [pos_weight_value],
    dtype=torch.float32,
    device=DEVICE
)

print(
    f"\nTraining negatives : {negative_count}"
)

print(
    f"Training positives : {positive_count}"
)

print(
    f"Positive class weight : "
    f"{pos_weight_value:.4f}"
)

criterion = nn.BCEWithLogitsLoss(
    pos_weight=pos_weight
)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001,
    weight_decay=1e-4
)

# ---------------------------------------------------------
# Evaluation helper
# ---------------------------------------------------------

def get_probabilities(
    model,
    X,
    batch_size=256
):

    model.eval()

    probabilities = []

    dataset = TensorDataset(
        torch.tensor(
            X,
            dtype=torch.float32
        )
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False
    )

    with torch.no_grad():

        for batch in loader:

            inputs = batch[0].to(DEVICE)

            logits = model(inputs)

            probs = torch.sigmoid(
                logits
            )

            probabilities.extend(
                probs.cpu().numpy()
            )

    return np.asarray(
        probabilities
    )


# ---------------------------------------------------------
# Training
# ---------------------------------------------------------

EPOCHS = 40
PATIENCE = 7

best_val_loss = float("inf")
patience_counter = 0

print("\n" + "=" * 75)
print("TRAINING")
print("=" * 75)

for epoch in range(1, EPOCHS + 1):

    model.train()

    running_loss = 0.0
    samples_seen = 0

    for inputs, targets in train_loader:

        inputs = inputs.to(DEVICE)
        targets = targets.to(DEVICE)

        optimizer.zero_grad()

        logits = model(inputs)

        loss = criterion(
            logits,
            targets
        )

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=1.0
        )

        optimizer.step()

        batch_size = inputs.size(0)

        running_loss += (
            loss.item() * batch_size
        )

        samples_seen += batch_size

    train_loss = (
        running_loss / samples_seen
    )

    # Validation loss
    model.eval()

    with torch.no_grad():

        val_inputs = (
            X_validation_tensor
            .to(DEVICE)
        )

        val_targets = (
            y_validation_tensor
            .to(DEVICE)
        )

        val_logits = model(
            val_inputs
        )

        val_loss = criterion(
            val_logits,
            val_targets
        ).item()

    print(
        f"Epoch {epoch:02d}/{EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    # Early stopping
    if val_loss < best_val_loss:

        best_val_loss = val_loss
        patience_counter = 0

        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "input_size": 68,

                "sequence_length": 100,

                "hidden_size": 64,

                "num_layers": 2,

                "best_val_loss":
                    best_val_loss
            },
            MODEL_FILE
        )

    else:

        patience_counter += 1

        if patience_counter >= PATIENCE:

            print(
                "\nEarly stopping triggered."
            )

            break

# ---------------------------------------------------------
# Load best model
# ---------------------------------------------------------

checkpoint = torch.load(
    MODEL_FILE,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

print(
    "\nBest model restored."
)

print(
    f"Best validation loss: "
    f"{checkpoint['best_val_loss']:.4f}"
)

# ---------------------------------------------------------
# Validation threshold search
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("VALIDATION THRESHOLD SEARCH")
print("=" * 75)

validation_probs = get_probabilities(
    model,
    X_validation
)

thresholds = np.arange(
    0.10,
    0.91,
    0.05
)

best_threshold = 0.50
best_f1 = -1

for threshold in thresholds:

    predictions = (
        validation_probs >= threshold
    ).astype(int)

    score = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )

    print(
        f"Threshold={threshold:.2f} "
        f"F1={score:.4f}"
    )

    if score > best_f1:

        best_f1 = score
        best_threshold = threshold

print(
    f"\nSelected threshold: "
    f"{best_threshold:.2f}"
)

print(
    f"Validation F1: "
    f"{best_f1:.4f}"
)

# ---------------------------------------------------------
# Final TEST evaluation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FINAL TEST EVALUATION")
print("=" * 75)

test_probs = get_probabilities(
    model,
    X_test
)

test_predictions = (
    test_probs >= best_threshold
).astype(int)

cm = confusion_matrix(
    y_test,
    test_predictions
)

roc_auc = roc_auc_score(
    y_test,
    test_probs
)

pr_auc = average_precision_score(
    y_test,
    test_probs
)

precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

tn, fp, fn, tp = cm.ravel()

false_alarm_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0
)

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        target_names=[
            "No DDoS",
            "DDoS"
        ],
        zero_division=0
    )
)

print(
    f"ROC-AUC : {roc_auc:.4f}"
)

print(
    f"PR-AUC  : {pr_auc:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1       : {f1:.4f}"
)

print(
    f"False Alarm Rate: "
    f"{false_alarm_rate:.4f}"
)

# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - GRU DDoS FORECASTING REPORT\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        "Architecture: 2-layer GRU\n"
    )

    report.write(
        "Input: 100 flows × 68 features\n"
    )

    report.write(
        "Target: DDoS in next 100 flows\n\n"
    )

    report.write(
        f"Best validation loss: "
        f"{checkpoint['best_val_loss']:.6f}\n"
    )

    report.write(
        f"Selected threshold: "
        f"{best_threshold:.2f}\n\n"
    )

    report.write(
        "Confusion Matrix:\n"
    )

    report.write(
        str(cm) + "\n\n"
    )

    report.write(
        classification_report(
            y_test,
            test_predictions,
            target_names=[
                "No DDoS",
                "DDoS"
            ],
            zero_division=0
        )
    )

    report.write(
        f"\nROC-AUC: {roc_auc:.6f}\n"
    )

    report.write(
        f"PR-AUC: {pr_auc:.6f}\n"
    )

    report.write(
        f"Precision: {precision:.6f}\n"
    )

    report.write(
        f"Recall: {recall:.6f}\n"
    )

    report.write(
        f"F1: {f1:.6f}\n"
    )

    report.write(
        f"False Alarm Rate: "
        f"{false_alarm_rate:.6f}\n"
    )

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    f"\nModel saved to:\n{MODEL_FILE}"
)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print(
    "\nTest set was evaluated only after "
    "validation-based threshold selection."
)

print("=" * 75)