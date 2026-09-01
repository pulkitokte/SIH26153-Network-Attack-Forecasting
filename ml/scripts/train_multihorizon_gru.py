import numpy as np
import pandas as pd
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# ============================================================
# CICIDS2017 - MULTI-HORIZON GRU FORECASTER
#
# Shared GRU encoder with four independent binary heads:
#   y50, y100, y200, y500
#
# This script only loads existing tensors/metadata.
# It does not regenerate windows, modify CSVs/tensors,
# change episode splits, or train Isolation Forest.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

MODEL_FILE = MODEL_DIR / "multihorizon_gru.pt"
PREDICTION_FILE = DATA_DIR / "multihorizon_gru_test_predictions.csv"
REPORT_FILE = REPORT_DIR / "multihorizon_gru_training_report.txt"

HORIZONS = [50, 100, 200, 500]
SPLITS = ("train", "validation", "test")

SEED = 42
BATCH_SIZE = 64
HIDDEN_SIZE = 96
NUM_LAYERS = 2
DROPOUT = 0.30
LEARNING_RATE = 1e-3
MAX_EPOCHS = 60
PATIENCE = 8
GRAD_CLIP = 1.0

THRESHOLDS = np.round(np.arange(0.10, 0.96, 0.05), 2)

EXPECTED_X_SHAPES = {
    "train": (13515, 100, 68),
    "validation": (2703, 100, 68),
    "test": (2703, 100, 68),
}


# ============================================================
# LOGGING
# ============================================================

class ReportLogger:
    def __init__(self):
        self.lines = []

    def log(self, *args, sep=" ", end="\n"):
        text = sep.join(str(arg) for arg in args) + end
        self.lines.append(text)
        print(text, end="", flush=True)

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(self.lines), encoding="utf-8")


logger = ReportLogger()
log = logger.log


# ============================================================
# REPRODUCIBILITY
# ============================================================

np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

DATALOADER_GENERATOR = torch.Generator()
DATALOADER_GENERATOR.manual_seed(SEED)


# ============================================================
# MODEL
# ============================================================

class MultiHorizonGRU(nn.Module):
    """Shared GRU encoder with four independent horizon heads."""

    def __init__(
        self,
        input_size=68,
        hidden_size=96,
        num_layers=2,
        dropout=0.30,
    ):
        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout,
        )

        self.norm = nn.LayerNorm(hidden_size)

        self.shared = nn.Sequential(
            nn.Linear(hidden_size, 48),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        self.head_50 = nn.Linear(48, 1)
        self.head_100 = nn.Linear(48, 1)
        self.head_200 = nn.Linear(48, 1)
        self.head_500 = nn.Linear(48, 1)

    def forward(self, x):
        output, _hidden = self.gru(x)
        last_state = output[:, -1, :]
        last_state = self.norm(last_state)
        shared = self.shared(last_state)

        logit_50 = self.head_50(shared).squeeze(1)
        logit_100 = self.head_100(shared).squeeze(1)
        logit_200 = self.head_200(shared).squeeze(1)
        logit_500 = self.head_500(shared).squeeze(1)

        return logit_50, logit_100, logit_200, logit_500


# ============================================================
# METRICS
# ============================================================

def evaluate_horizon(y_true, y_prob, y_pred):
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    y_prob = np.asarray(y_prob).astype(float)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    n_pos = int((y_true == 1).sum())
    n_neg = int((y_true == 0).sum())

    precision = float(
        precision_score(y_true, y_pred, zero_division=0)
    )
    recall = float(
        recall_score(y_true, y_pred, zero_division=0)
    )
    f1 = float(
        f1_score(y_true, y_pred, zero_division=0)
    )
    accuracy = float(
        accuracy_score(y_true, y_pred)
    )

    if n_pos == 0 or n_neg == 0:
        roc_auc = float("nan")
    else:
        roc_auc = float(roc_auc_score(y_true, y_prob))

    pr_auc = float(
        average_precision_score(y_true, y_prob)
    )

    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    return {
        "cm": cm,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "false_alarm_rate": far,
    }


def print_horizon_metrics(title, metrics):
    log(f"\n{title}")
    log("-" * 75)
    log("Confusion Matrix [rows=true 0/1, cols=pred 0/1]:")
    log(str(metrics["cm"]))
    log(f"TN={metrics['tn']}  FP={metrics['fp']}  "
        f"FN={metrics['fn']}  TP={metrics['tp']}")
    log(f"Positive examples : {metrics['n_pos']:,}")
    log(f"Negative examples : {metrics['n_neg']:,}")
    log(f"Precision         : {metrics['precision']:.4f}")
    log(f"Recall            : {metrics['recall']:.4f}")
    log(f"F1                : {metrics['f1']:.4f}")
    log(f"Accuracy          : {metrics['accuracy']:.4f}")
    log(f"ROC-AUC           : {metrics['roc_auc']:.4f}")
    log(f"PR-AUC            : {metrics['pr_auc']:.4f}")
    log(f"False Alarm Rate  : {metrics['false_alarm_rate']:.4f}")


# ============================================================
# HEADER
# ============================================================

log("=" * 75)
log("CICIDS2017 - MULTI-HORIZON GRU FORECASTER")
log("=" * 75)
log(f"\nDevice: {DEVICE}")
log(f"Seed  : {SEED}")


# ============================================================
# LOAD TENSORS
# ============================================================

log("\n" + "=" * 75)
log("LOAD TENSORS")
log("=" * 75)

X = {}
y = {horizon: {} for horizon in HORIZONS}

for split in SPLITS:
    x_path = DATA_DIR / f"multihorizon_X_{split}.npy"
    log(f"\nLoading {x_path.name}")
    X[split] = np.load(x_path).astype(np.float32)
    log(f"  {X[split].shape}")

    expected = EXPECTED_X_SHAPES[split]
    if tuple(X[split].shape) != expected:
        raise ValueError(
            f"Unexpected X_{split} shape {X[split].shape}, "
            f"expected {expected}"
        )

    for horizon in HORIZONS:
        y_path = DATA_DIR / f"multihorizon_y{horizon}_{split}.npy"
        y[horizon][split] = np.load(y_path).astype(np.float32)
        if y[horizon][split].shape[0] != X[split].shape[0]:
            raise ValueError(
                f"y{horizon}_{split} length "
                f"{y[horizon][split].shape[0]} does not match "
                f"X_{split} length {X[split].shape[0]}"
            )

log("\nDataset shapes:")
for split in SPLITS:
    log(f"  X_{split:<10} {X[split].shape}")
    for horizon in HORIZONS:
        log(
            f"  y{horizon}_{split:<7} {y[horizon][split].shape}"
        )


# ============================================================
# LOAD METADATA (TEST ALIGNMENT ONLY)
# ============================================================

metadata_path = DATA_DIR / "multihorizon_sequence_metadata.csv"
metadata = pd.read_csv(metadata_path)
metadata.columns = metadata.columns.str.strip()

test_metadata = (
    metadata[metadata["dataset_split"] == "TEST"]
    .reset_index(drop=True)
)

if len(test_metadata) != X["test"].shape[0]:
    raise ValueError(
        "TEST metadata rows do not match X_test: "
        f"{len(test_metadata)} != {X['test'].shape[0]}"
    )


# ============================================================
# DATA LOADERS
# ============================================================

def make_dataset(split):
    tensors = [torch.tensor(X[split], dtype=torch.float32)]
    for horizon in HORIZONS:
        tensors.append(
            torch.tensor(y[horizon][split], dtype=torch.float32)
        )
    return TensorDataset(*tensors)


train_loader = DataLoader(
    make_dataset("train"),
    batch_size=BATCH_SIZE,
    shuffle=True,
    generator=DATALOADER_GENERATOR,
)

validation_loader = DataLoader(
    make_dataset("validation"),
    batch_size=BATCH_SIZE,
    shuffle=False,
)

test_loader = DataLoader(
    make_dataset("test"),
    batch_size=BATCH_SIZE,
    shuffle=False,
)


# ============================================================
# TRAINING CLASS COUNTS AND POSITIVE WEIGHTS
# ============================================================

log("\n" + "=" * 75)
log("TRAINING CLASS COUNTS AND POSITIVE WEIGHTS")
log("=" * 75)
log("\nPositive-class weights are computed from TRAIN only.")

pos_weights = {}
train_class_counts = {}

for horizon in HORIZONS:
    y_train = y[horizon]["train"]
    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    if n_pos == 0:
        raise ValueError(
            f"TRAIN y{horizon} has zero positive examples."
        )
    weight = n_neg / n_pos
    pos_weights[horizon] = weight
    train_class_counts[horizon] = {
        "negative": n_neg,
        "positive": n_pos,
    }
    log(f"\nHorizon {horizon}:")
    log(f"  TRAIN negatives : {n_neg:,}")
    log(f"  TRAIN positives : {n_pos:,}")
    log(f"  pos_weight      : {weight:.6f}")


# ============================================================
# MODEL / LOSS / OPTIMIZER
# ============================================================

input_size = X["train"].shape[2]

model = MultiHorizonGRU(
    input_size=input_size,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT,
).to(DEVICE)

log("\n" + "=" * 75)
log("ARCHITECTURE")
log("=" * 75)
log(str(model))

criteria = {
    horizon: nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(
            pos_weights[horizon],
            dtype=torch.float32,
            device=DEVICE,
        )
    )
    for horizon in HORIZONS
}

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
)


def unpack_batch(batch):
    x_batch = batch[0].to(DEVICE)
    y_batches = {
        horizon: batch[i + 1].to(DEVICE)
        for i, horizon in enumerate(HORIZONS)
    }
    return x_batch, y_batches


def run_epoch(loader, training):
    if training:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    horizon_loss = {horizon: 0.0 for horizon in HORIZONS}
    n_samples = 0

    for batch in loader:
        x_batch, y_batches = unpack_batch(batch)

        if training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(training):
            logits = model(x_batch)
            losses = []
            for i, horizon in enumerate(HORIZONS):
                horizon_item = criteria[horizon](
                    logits[i],
                    y_batches[horizon],
                )
                losses.append(horizon_item)
                horizon_loss[horizon] += (
                    horizon_item.item() * x_batch.size(0)
                )

            loss = losses[0] + losses[1] + losses[2] + losses[3]

            if training:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    max_norm=GRAD_CLIP,
                )
                optimizer.step()

        total_loss += loss.item() * x_batch.size(0)
        n_samples += x_batch.size(0)

    avg_total = total_loss / n_samples
    avg_horizon = {
        horizon: horizon_loss[horizon] / n_samples
        for horizon in HORIZONS
    }
    return avg_total, avg_horizon


def predict_logits(loader):
    model.eval()
    collected = {horizon: [] for horizon in HORIZONS}

    with torch.no_grad():
        for batch in loader:
            x_batch, _y_batches = unpack_batch(batch)
            logits = model(x_batch)
            for i, horizon in enumerate(HORIZONS):
                collected[horizon].append(
                    logits[i].detach().cpu().numpy()
                )

    return {
        horizon: np.concatenate(collected[horizon], axis=0)
        for horizon in HORIZONS
    }


def logits_to_probs(logit_dict):
    return {
        horizon: 1.0 / (1.0 + np.exp(-logit_dict[horizon]))
        for horizon in HORIZONS
    }


# ============================================================
# TRAINING
# ============================================================

log("\n" + "=" * 75)
log("TRAINING")
log("=" * 75)
log(f"\nBatch size     : {BATCH_SIZE}")
log(f"Max epochs     : {MAX_EPOCHS}")
log(f"Patience       : {PATIENCE}")
log(f"Learning rate  : {LEARNING_RATE}")
log(f"Optimizer      : Adam")
log("Early stopping : validation total loss")
log("Thresholds     : selected from VALIDATION only")

history = []
best_val_loss = float("inf")
best_state = None
best_epoch = 0
epochs_without_improvement = 0

for epoch in range(1, MAX_EPOCHS + 1):
    train_loss, train_horizon = run_epoch(
        train_loader,
        training=True,
    )
    val_loss, val_horizon = run_epoch(
        validation_loader,
        training=False,
    )

    history.append({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_loss": val_loss,
        "val_50": val_horizon[50],
        "val_100": val_horizon[100],
        "val_200": val_horizon[200],
        "val_500": val_horizon[500],
    })

    log(f"\nEpoch {epoch:02d}/{MAX_EPOCHS}")
    log(f"Train Loss      : {train_loss:.6f}")
    log(f"Validation Loss : {val_loss:.6f}")
    log(f"Val50  : {val_horizon[50]:.6f}")
    log(f"Val100 : {val_horizon[100]:.6f}")
    log(f"Val200 : {val_horizon[200]:.6f}")
    log(f"Val500 : {val_horizon[500]:.6f}")

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_epoch = epoch
        best_state = {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        }
        epochs_without_improvement = 0
        log("  -> New best validation loss. Checkpoint stored.")
    else:
        epochs_without_improvement += 1
        log(
            f"  -> No improvement "
            f"({epochs_without_improvement}/{PATIENCE})."
        )
        if epochs_without_improvement >= PATIENCE:
            log("\nEarly stopping triggered.")
            break

if best_state is None:
    raise RuntimeError("Training produced no checkpoint.")

model.load_state_dict(best_state)
model.to(DEVICE)

log("\nBest model restored.")
log(f"Best epoch           : {best_epoch}")
log(f"Best validation loss : {best_val_loss:.6f}")


# ============================================================
# VALIDATION THRESHOLD SEARCH
# ============================================================

log("\n" + "=" * 75)
log("VALIDATION THRESHOLD SEARCH")
log("=" * 75)
log("\nTEST data is not used for threshold selection.")

val_logits = predict_logits(validation_loader)
val_probs = logits_to_probs(val_logits)

selected_thresholds = {}
validation_f1 = {}

for horizon in HORIZONS:
    log(f"\n--- Horizon {horizon} ---")
    y_true = y[horizon]["validation"].astype(int)
    probs = val_probs[horizon]

    best_threshold = 0.50
    best_f1 = -1.0

    for threshold in THRESHOLDS:
        pred = (probs >= threshold).astype(int)
        score = float(
            f1_score(y_true, pred, zero_division=0)
        )
        log(f"  Threshold={threshold:.2f}  F1={score:.4f}")
        if score > best_f1:
            best_f1 = score
            best_threshold = float(threshold)

    selected_thresholds[horizon] = best_threshold
    validation_f1[horizon] = best_f1

log("\nSelected validation thresholds:")
for horizon in HORIZONS:
    log(
        f"  {horizon}-flow selected threshold : "
        f"{selected_thresholds[horizon]:.2f}  "
        f"(Validation F1={validation_f1[horizon]:.4f})"
    )


# ============================================================
# FINAL TEST EVALUATION
# ============================================================

log("\n" + "=" * 75)
log("FINAL MULTI-HORIZON TEST EVALUATION")
log("=" * 75)
log("\nTEST is evaluated once after validation threshold selection.")

test_logits = predict_logits(test_loader)
test_probs = logits_to_probs(test_logits)
test_preds = {}
test_metrics = {}

for horizon in HORIZONS:
    test_preds[horizon] = (
        test_probs[horizon] >= selected_thresholds[horizon]
    ).astype(int)
    test_metrics[horizon] = evaluate_horizon(
        y[horizon]["test"],
        test_probs[horizon],
        test_preds[horizon],
    )
    print_horizon_metrics(
        f"{horizon}-FLOW HORIZON",
        test_metrics[horizon],
    )


# ============================================================
# SAVE MODEL
# ============================================================

torch.save(
    {
        "model_state_dict": model.state_dict(),
        "architecture": {
            "input_size": input_size,
            "hidden_size": HIDDEN_SIZE,
            "num_layers": NUM_LAYERS,
            "dropout": DROPOUT,
        },
        "horizons": HORIZONS,
        "thresholds": selected_thresholds,
        "validation_f1": validation_f1,
        "pos_weights": pos_weights,
        "best_epoch": best_epoch,
        "best_validation_loss": best_val_loss,
        "seed": SEED,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "patience": PATIENCE,
        "max_epochs": MAX_EPOCHS,
    },
    MODEL_FILE,
)


# ============================================================
# SAVE TEST PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame({
    "window_id": test_metadata["window_id"].to_numpy(),
    "episode_id": test_metadata["episode_id"].to_numpy(),
    "observation_start_position": (
        test_metadata["observation_start_position"].to_numpy()
    ),
    "observation_end_position": (
        test_metadata["observation_end_position"].to_numpy()
    ),
    "target_50": y[50]["test"].astype(int),
    "target_100": y[100]["test"].astype(int),
    "target_200": y[200]["test"].astype(int),
    "target_500": y[500]["test"].astype(int),
    "probability_50": test_probs[50],
    "probability_100": test_probs[100],
    "probability_200": test_probs[200],
    "probability_500": test_probs[500],
    "prediction_50": test_preds[50],
    "prediction_100": test_preds[100],
    "prediction_200": test_preds[200],
    "prediction_500": test_preds[500],
})

if len(prediction_df) != X["test"].shape[0]:
    raise ValueError(
        "Prediction CSV row count does not match X_test."
    )

# Confirm metadata targets still match tensor targets.
for horizon in HORIZONS:
    meta_col = f"y{horizon}"
    if meta_col in test_metadata.columns:
        if not np.array_equal(
            test_metadata[meta_col].to_numpy(dtype=int),
            y[horizon]["test"].astype(int),
        ):
            raise ValueError(
                f"TEST metadata {meta_col} does not match "
                "tensor order. Predictions were not saved."
            )

prediction_df.to_csv(PREDICTION_FILE, index=False)


# ============================================================
# COMPLETE REPORT TAIL
# ============================================================

log("\n" + "=" * 75)
log("SAVED OUTPUTS")
log("=" * 75)
log(f"\nModel       : {MODEL_FILE}")
log(f"Predictions : {PREDICTION_FILE}")
log(f"Report      : {REPORT_FILE}")

log("\n" + "=" * 75)
log("MULTI-HORIZON GRU TRAINING COMPLETE")
log("=" * 75)

log("\nFinal TEST metrics:")
for horizon in HORIZONS:
    m = test_metrics[horizon]
    log(
        f"\n{horizon}-flow: "
        f"F1={m['f1']:.4f}  "
        f"Recall={m['recall']:.4f}  "
        f"Precision={m['precision']:.4f}  "
        f"ROC-AUC={m['roc_auc']:.4f}  "
        f"PR-AUC={m['pr_auc']:.4f}  "
        f"FAR={m['false_alarm_rate']:.4f}"
    )

log("\nExisting datasets and tensors were NOT modified.")
log("TEST was not used during training or threshold selection.")
log("=" * 75)

logger.save(REPORT_FILE)
