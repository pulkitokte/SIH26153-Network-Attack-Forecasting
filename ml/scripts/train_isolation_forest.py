import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


# =========================================================
# CICIDS2017 - Isolation Forest Anomaly Detector
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


TRAIN_FILE = PROCESSED_DIR / "ddos_train_scaled.csv"
VAL_FILE = PROCESSED_DIR / "ddos_validation_scaled.csv"
TEST_FILE = PROCESSED_DIR / "ddos_test_scaled.csv"

MODEL_FILE = MODEL_DIR / "ddos_isolation_forest.joblib"

TRAIN_OUTPUT = PROCESSED_DIR / "ddos_train_if_scored.csv"
VAL_OUTPUT = PROCESSED_DIR / "ddos_validation_if_scored.csv"
TEST_OUTPUT = PROCESSED_DIR / "ddos_test_if_scored.csv"

REPORT_FILE = REPORT_DIR / "isolation_forest_report.txt"


print("=" * 75)
print("CICIDS2017 - ISOLATION FOREST ANOMALY DETECTION")
print("=" * 75)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

print("\nLoading scaled datasets...")

train_df = pd.read_csv(
    TRAIN_FILE,
    low_memory=False
)

val_df = pd.read_csv(
    VAL_FILE,
    low_memory=False
)

test_df = pd.read_csv(
    TEST_FILE,
    low_memory=False
)

print(f"TRAIN rows      : {len(train_df):,}")
print(f"VALIDATION rows : {len(val_df):,}")
print(f"TEST rows       : {len(test_df):,}")


# ---------------------------------------------------------
# Metadata
# ---------------------------------------------------------

metadata_columns = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position"
]


# ---------------------------------------------------------
# Feature columns
# ---------------------------------------------------------

feature_columns = [
    column
    for column in train_df.columns
    if column not in metadata_columns
]

print(
    f"\nFeature columns: {len(feature_columns)}"
)


# ---------------------------------------------------------
# IMPORTANT:
# Train Isolation Forest ONLY on BENIGN TRAIN flows
# ---------------------------------------------------------

train_benign = train_df[
    train_df["Label"] == "BENIGN"
].copy()

print(
    f"\nBENIGN training flows used "
    f"for baseline: {len(train_benign):,}"
)

if len(train_benign) == 0:
    raise ValueError(
        "No BENIGN training flows found."
    )


X_train_benign = train_benign[
    feature_columns
]


# ---------------------------------------------------------
# Train Isolation Forest
# ---------------------------------------------------------

print("\nTraining Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train_benign
)

print("Isolation Forest training complete.")


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

joblib.dump(
    model,
    MODEL_FILE
)

print(
    f"\nModel saved to:\n{MODEL_FILE}"
)


# ---------------------------------------------------------
# Function to score datasets
# ---------------------------------------------------------

def score_dataset(df, name):

    X = df[feature_columns]

    # sklearn decision_function:
    # higher = more normal
    # lower = more anomalous

    raw_score = model.decision_function(X)

    # Convert so higher = more anomalous
    anomaly_score = -raw_score

    predictions = model.predict(X)

    # sklearn:
    # +1 = normal
    # -1 = anomaly

    anomaly_flag = (
        predictions == -1
    ).astype(int)

    result = df.copy()

    result["if_anomaly_score"] = anomaly_score

    result["if_anomaly_flag"] = anomaly_flag

    return result


# ---------------------------------------------------------
# Score all datasets
# ---------------------------------------------------------

print("\nScoring TRAIN...")

train_scored = score_dataset(
    train_df,
    "TRAIN"
)

print("Scoring VALIDATION...")

val_scored = score_dataset(
    val_df,
    "VALIDATION"
)

print("Scoring TEST...")

test_scored = score_dataset(
    test_df,
    "TEST"
)


# ---------------------------------------------------------
# Print anomaly counts
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("ANOMALY COUNTS")
print("=" * 75)

for name, df in [
    ("TRAIN", train_scored),
    ("VALIDATION", val_scored),
    ("TEST", test_scored)
]:

    count = df["if_anomaly_flag"].sum()

    percentage = (
        count / len(df)
    ) * 100

    print(
        f"{name:<12}: "
        f"{count:>6,} anomalies "
        f"({percentage:>6.2f}%)"
    )


# ---------------------------------------------------------
# Compare anomaly detection with actual labels
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("TEST PERFORMANCE")
print("=" * 75)

y_test = (
    test_scored["Label"] == "DDoS"
).astype(int)

y_pred = test_scored[
    "if_anomaly_flag"
]

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)

print("\nClassification Report:")

report = classification_report(
    y_test,
    y_pred,
    target_names=[
        "BENIGN",
        "DDoS"
    ],
    zero_division=0
)

print(report)


# ---------------------------------------------------------
# ROC-AUC using anomaly score
# ---------------------------------------------------------

try:

    auc = roc_auc_score(
        y_test,
        test_scored["if_anomaly_score"]
    )

    print(
        f"ROC-AUC: {auc:.4f}"
    )

except Exception as error:

    auc = None

    print(
        f"ROC-AUC could not be calculated: "
        f"{error}"
    )


# ---------------------------------------------------------
# Save scored datasets
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SAVING SCORED DATASETS")
print("=" * 75)

train_scored.to_csv(
    TRAIN_OUTPUT,
    index=False
)

val_scored.to_csv(
    VAL_OUTPUT,
    index=False
)

test_scored.to_csv(
    TEST_OUTPUT,
    index=False
)

print(
    f"\nTRAIN:\n{TRAIN_OUTPUT}"
)

print(
    f"\nVALIDATION:\n{VAL_OUTPUT}"
)

print(
    f"\nTEST:\n{TEST_OUTPUT}"
)


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report_file:

    report_file.write(
        "CICIDS2017 - ISOLATION FOREST REPORT\n"
    )

    report_file.write(
        "=" * 75 + "\n\n"
    )

    report_file.write(
        "Training strategy:\n"
    )

    report_file.write(
        "Isolation Forest was fitted ONLY "
        "on BENIGN TRAIN flows.\n\n"
    )

    report_file.write(
        f"Training BENIGN flows: "
        f"{len(train_benign):,}\n"
    )

    report_file.write(
        f"Number of estimators: "
        f"200\n"
    )

    report_file.write(
        f"Contamination: "
        f"0.05\n\n"
    )

    report_file.write(
        "TEST CONFUSION MATRIX\n"
    )

    report_file.write(
        str(cm) + "\n\n"
    )

    report_file.write(
        "TEST CLASSIFICATION REPORT\n"
    )

    report_file.write(
        report + "\n"
    )

    if auc is not None:

        report_file.write(
            f"\nROC-AUC: {auc:.4f}\n"
        )


print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    "\nIsolation Forest model trained "
    "on BENIGN training traffic."
)

print(
    f"\nModel:\n{MODEL_FILE}"
)

print(
    f"\nReport:\n{REPORT_FILE}"
)

print("\nOriginal datasets were NOT modified.")

print("=" * 75)