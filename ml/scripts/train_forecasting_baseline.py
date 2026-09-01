import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.linear_model import LogisticRegression
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
# CICIDS2017 - TEMPORAL FORECASTING BASELINE
#
# Input:
#   100-flow sequence × 68 features
#
# Baseline representation:
#   mean + std for each feature
#
# Model:
#   Logistic Regression
#
# Purpose:
#   Establish a non-neural temporal baseline before GRU/LSTM.
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "processed"

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "forecasting_baseline_report.txt"
)

print("=" * 75)
print("CICIDS2017 - TEMPORAL FORECASTING BASELINE")
print("=" * 75)

# ---------------------------------------------------------
# Load tensors
# ---------------------------------------------------------

print("\nLoading tensors...")

X_train = np.load(
    DATA_DIR / "X_train.npy"
)

y_train = np.load(
    DATA_DIR / "y_train.npy"
)

X_validation = np.load(
    DATA_DIR / "X_validation.npy"
)

y_validation = np.load(
    DATA_DIR / "y_validation.npy"
)

X_test = np.load(
    DATA_DIR / "X_test.npy"
)

y_test = np.load(
    DATA_DIR / "y_test.npy"
)

print(
    f"X_train      : {X_train.shape}"
)

print(
    f"X_validation : {X_validation.shape}"
)

print(
    f"X_test       : {X_test.shape}"
)

# ---------------------------------------------------------
# Convert sequence into statistical representation
#
# For every feature:
#   mean
#   standard deviation
#
# 68 features × 2 = 136 features
# ---------------------------------------------------------

def aggregate_sequences(X):

    means = np.mean(
        X,
        axis=1
    )

    stds = np.std(
        X,
        axis=1
    )

    return np.concatenate(
        [means, stds],
        axis=1
    )


print(
    "\nCreating statistical representations..."
)

X_train_agg = aggregate_sequences(
    X_train
)

X_validation_agg = aggregate_sequences(
    X_validation
)

X_test_agg = aggregate_sequences(
    X_test
)

print(
    f"Aggregated train shape      : "
    f"{X_train_agg.shape}"
)

print(
    f"Aggregated validation shape : "
    f"{X_validation_agg.shape}"
)

print(
    f"Aggregated test shape       : "
    f"{X_test_agg.shape}"
)

# ---------------------------------------------------------
# Train Logistic Regression
# ---------------------------------------------------------

print(
    "\nTraining Logistic Regression baseline..."
)

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

model.fit(
    X_train_agg,
    y_train
)

print(
    "Training complete."
)

# ---------------------------------------------------------
# Validation threshold selection
#
# We use validation data to select a threshold.
# Test set remains untouched until final evaluation.
# ---------------------------------------------------------

validation_probabilities = (
    model.predict_proba(
        X_validation_agg
    )[:, 1]
)

thresholds = np.arange(
    0.10,
    0.91,
    0.05
)

best_threshold = 0.50
best_f1 = -1

print(
    "\nValidation threshold search:"
)

for threshold in thresholds:

    predictions = (
        validation_probabilities
        >= threshold
    ).astype(int)

    current_f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )

    print(
        f"Threshold={threshold:.2f} "
        f"F1={current_f1:.4f}"
    )

    if current_f1 > best_f1:

        best_f1 = current_f1
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

print(
    "\n" + "=" * 75
)

print(
    "FINAL TEST EVALUATION"
)

print(
    "=" * 75
)

test_probabilities = (
    model.predict_proba(
        X_test_agg
    )[:, 1]
)

test_predictions = (
    test_probabilities
    >= best_threshold
).astype(int)

# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

cm = confusion_matrix(
    y_test,
    test_predictions
)

roc_auc = roc_auc_score(
    y_test,
    test_probabilities
)

pr_auc = average_precision_score(
    y_test,
    test_probabilities
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

print(
    "\nConfusion Matrix:"
)

print(cm)

print(
    "\nClassification Report:"
)

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

# ---------------------------------------------------------
# False alarm rate
# ---------------------------------------------------------

tn, fp, fn, tp = cm.ravel()

false_alarm_rate = (
    fp / (fp + tn)
    if (fp + tn) > 0
    else 0
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
        "CICIDS2017 - TEMPORAL FORECASTING BASELINE\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        "Model: Logistic Regression\n"
    )

    report.write(
        "Representation: mean + standard deviation "
        "over 100-flow observation window\n\n"
    )

    report.write(
        f"Selected threshold: "
        f"{best_threshold:.2f}\n\n"
    )

    report.write(
        "Confusion Matrix:\n"
    )

    report.write(
        str(cm)
    )

    report.write("\n\n")

    report.write(
        "Classification Report:\n"
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

print(
    "\n" + "=" * 75
)

print(
    "SUCCESS"
)

print(
    "=" * 75
)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print(
    "\nTest set was evaluated only after "
    "validation threshold selection."
)

print("=" * 75)