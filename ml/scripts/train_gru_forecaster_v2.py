import numpy as np
import pandas as pd
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

BATCH_SIZE = 32
HIDDEN_SIZE = 96
NUM_LAYERS = 2
DROPOUT = 0.30

LEARNING_RATE = 0.0005
WEIGHT_DECAY = 1e-4

MAX_EPOCHS = 60
PATIENCE = 10

THRESHOLDS = np.arange(
    0.10,
    0.96,
    0.05
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


print("=" * 75)
print("CICIDS2017 - GRU DDoS EARLY-WARNING FORECASTER V2")
print("=" * 75)

print(f"\nDevice: {DEVICE}")


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading sequence tensors...")

X_train = np.load(
    DATA_DIR / "X_train.npy"
).astype(np.float32)

y_train = np.load(
    DATA_DIR / "y_train.npy"
).astype(np.float32)

X_validation = np.load(
    DATA_DIR / "X_validation.npy"
).astype(np.float32)

y_validation = np.load(
    DATA_DIR / "y_validation.npy"
).astype(np.float32)

X_test = np.load(
    DATA_DIR / "X_test.npy"
).astype(np.float32)

y_test = np.load(
    DATA_DIR / "y_test.npy"
).astype(np.float32)


print(f"X_train      : {X_train.shape}")
print(f"X_validation : {X_validation.shape}")
print(f"X_test       : {X_test.shape}")


# ============================================================
# DATA LOADERS
# ============================================================

train_dataset = TensorDataset(
    torch.tensor(X_train),
    torch.tensor(y_train)
)

validation_dataset = TensorDataset(
    torch.tensor(X_validation),
    torch.tensor(y_validation)
)

test_dataset = TensorDataset(
    torch.tensor(X_test),
    torch.tensor(y_test)
)


train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# MODEL
# ============================================================

class GRUForecasterV2(nn.Module):

    def __init__(
        self,
        input_size,
        hidden_size=96,
        num_layers=2,
        dropout=0.30
    ):

        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.norm = nn.LayerNorm(
            hidden_size
        )

        self.classifier = nn.Sequential(
            nn.Linear(
                hidden_size,
                48
            ),

            nn.ReLU(),

            nn.Dropout(
                dropout
            ),

            nn.Linear(
                48,
                1
            )
        )


    def forward(self, x):

        output, hidden = self.gru(x)

        # Use final temporal representation
        last_state = output[:, -1, :]

        last_state = self.norm(
            last_state
        )

        logits = self.classifier(
            last_state
        )

        return logits.squeeze(1)


# ============================================================
# CREATE MODEL
# ============================================================

input_size = X_train.shape[2]

model = GRUForecasterV2(
    input_size=input_size,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT
).to(DEVICE)


print("\nModel:")
print(model)


# ============================================================
# CLASS IMBALANCE
# ============================================================

negative_count = int(
    (y_train == 0).sum()
)

positive_count = int(
    (y_train == 1).sum()
)

positive_weight = (
    negative_count / positive_count
)


print("\nTraining negatives :", negative_count)
print("Training positives :", positive_count)

print(
    f"Positive class weight : "
    f"{positive_weight:.4f}"
)


# ============================================================
# LOSS / OPTIMIZER
# ============================================================

criterion = nn.BCEWithLogitsLoss(
    pos_weight=torch.tensor(
        positive_weight,
        dtype=torch.float32,
        device=DEVICE
    )
)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
)


# ============================================================
# TRAINING FUNCTIONS
# ============================================================

def run_epoch(
    model,
    loader,
    training=True
):

    if training:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    total_samples = 0

    for X_batch, y_batch in loader:

        X_batch = X_batch.to(
            DEVICE
        )

        y_batch = y_batch.to(
            DEVICE
        )

        if training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(
            training
        ):

            logits = model(
                X_batch
            )

            loss = criterion(
                logits,
                y_batch
            )

            if training:

                loss.backward()

                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    max_norm=1.0
                )

                optimizer.step()

        batch_size = (
            X_batch.size(0)
        )

        total_loss += (
            loss.item()
            * batch_size
        )

        total_samples += batch_size

    return (
        total_loss
        / total_samples
    )


def predict_probabilities(
    model,
    loader
):

    model.eval()

    probabilities = []

    with torch.no_grad():

        for X_batch, _ in loader:

            X_batch = X_batch.to(
                DEVICE
            )

            logits = model(
                X_batch
            )

            probs = torch.sigmoid(
                logits
            )

            probabilities.extend(
                probs.cpu().numpy()
            )

    return np.array(
        probabilities
    )


# ============================================================
# TRAINING
# ============================================================

print("\n" + "=" * 75)
print("TRAINING V2")
print("=" * 75)

best_val_loss = float(
    "inf"
)

best_state = None

epochs_without_improvement = 0


for epoch in range(
    1,
    MAX_EPOCHS + 1
):

    train_loss = run_epoch(
        model,
        train_loader,
        training=True
    )

    val_loss = run_epoch(
        model,
        validation_loader,
        training=False
    )

    print(
        f"Epoch {epoch:02d}/{MAX_EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    if val_loss < best_val_loss:

        best_val_loss = val_loss

        best_state = {
            key: value.detach().cpu().clone()
            for key, value
            in model.state_dict().items()
        }

        epochs_without_improvement = 0

    else:

        epochs_without_improvement += 1

        if (
            epochs_without_improvement
            >= PATIENCE
        ):

            print(
                "\nEarly stopping triggered."
            )

            break


# ============================================================
# RESTORE BEST MODEL
# ============================================================

model.load_state_dict(
    best_state
)

model.to(DEVICE)

print("\nBest model restored.")

print(
    f"Best validation loss: "
    f"{best_val_loss:.4f}"
)


# ============================================================
# VALIDATION THRESHOLD SEARCH
# ============================================================

print("\n" + "=" * 75)
print("VALIDATION THRESHOLD SEARCH")
print("=" * 75)

validation_probs = (
    predict_probabilities(
        model,
        validation_loader
    )
)

best_threshold = 0.50
best_f1 = -1.0


for threshold in THRESHOLDS:

    validation_pred = (
        validation_probs
        >= threshold
    ).astype(int)

    score = f1_score(
        y_validation.astype(int),
        validation_pred,
        zero_division=0
    )

    print(
        f"Threshold={threshold:.2f} "
        f"F1={score:.4f}"
    )

    if score > best_f1:

        best_f1 = score
        best_threshold = float(
            threshold
        )


print(
    f"\nSelected threshold: "
    f"{best_threshold:.2f}"
)

print(
    f"Validation F1: "
    f"{best_f1:.4f}"
)


# ============================================================
# FINAL TEST EVALUATION
# ============================================================

print("\n" + "=" * 75)
print("FINAL TEST EVALUATION")
print("=" * 75)

test_probs = (
    predict_probabilities(
        model,
        test_loader
    )
)

test_pred = (
    test_probs
    >= best_threshold
).astype(int)


cm = confusion_matrix(
    y_test.astype(int),
    test_pred
)

print("\nConfusion Matrix:")
print(cm)


print("\nClassification Report:")

print(
    classification_report(
        y_test.astype(int),
        test_pred,
        target_names=[
            "No DDoS",
            "DDoS"
        ],
        zero_division=0
    )
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
    test_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    test_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_pred,
    zero_division=0
)


tn, fp, fn, tp = cm.ravel()

false_alarm_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0
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


# ============================================================
# SAVE MODEL
# ============================================================

MODEL_FILE = (
    MODEL_DIR
    / "ddos_gru_forecaster_v2.pt"
)

torch.save(
    {
        "model_state_dict":
            model.state_dict(),

        "input_size":
            input_size,

        "hidden_size":
            HIDDEN_SIZE,

        "num_layers":
            NUM_LAYERS,

        "dropout":
            DROPOUT,

        "threshold":
            best_threshold,

        "seed":
            SEED
    },
    MODEL_FILE
)


# ============================================================
# SAVE TEST PREDICTIONS
# ============================================================

prediction_file = (
    DATA_DIR
    / "gru_v2_test_predictions.csv"
)

prediction_df = pd.DataFrame({
    "actual": y_test.astype(int),
    "probability": test_probs,
    "prediction": test_pred
})

prediction_df.to_csv(
    prediction_file,
    index=False
)


# ============================================================
# SAVE REPORT
# ============================================================

REPORT_FILE = (
    REPORT_DIR
    / "gru_forecasting_v2_report.txt"
)


with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - GRU FORECASTING V2\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Device: {DEVICE}\n"
    )

    report.write(
        f"Input shape: {X_train.shape}\n"
    )

    report.write(
        f"Hidden size: {HIDDEN_SIZE}\n"
    )

    report.write(
        f"GRU layers: {NUM_LAYERS}\n"
    )

    report.write(
        f"Dropout: {DROPOUT}\n"
    )

    report.write(
        f"Learning rate: {LEARNING_RATE}\n"
    )

    report.write(
        f"Weight decay: {WEIGHT_DECAY}\n"
    )

    report.write(
        f"Best validation loss: "
        f"{best_val_loss:.6f}\n"
    )

    report.write(
        f"Selected threshold: "
        f"{best_threshold:.4f}\n"
    )

    report.write(
        f"Validation F1: "
        f"{best_f1:.4f}\n\n"
    )

    report.write(
        "TEST RESULTS\n"
    )

    report.write(
        "-" * 75 + "\n"
    )

    report.write(
        str(cm)
        + "\n\n"
    )

    report.write(
        classification_report(
            y_test.astype(int),
            test_pred,
            target_names=[
                "No DDoS",
                "DDoS"
            ],
            zero_division=0
        )
    )

    report.write(
        f"\nROC-AUC: {roc_auc:.4f}\n"
    )

    report.write(
        f"PR-AUC: {pr_auc:.4f}\n"
    )

    report.write(
        f"Precision: {precision:.4f}\n"
    )

    report.write(
        f"Recall: {recall:.4f}\n"
    )

    report.write(
        f"F1: {f1:.4f}\n"
    )

    report.write(
        f"False Alarm Rate: "
        f"{false_alarm_rate:.4f}\n"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    f"\nModel saved to:\n{MODEL_FILE}"
)

print(
    f"\nPredictions saved to:\n"
    f"{prediction_file}"
)

print(
    f"\nReport saved to:\n"
    f"{REPORT_FILE}"
)

print(
    "\nV2 test evaluation completed."
)

print("=" * 75)