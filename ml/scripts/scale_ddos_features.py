import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler

# =========================================================
# CICIDS2017 - Training-Only Feature Scaling
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

TRAIN_FILE = PROCESSED_DIR / "ddos_train.csv"
VAL_FILE = PROCESSED_DIR / "ddos_validation.csv"
TEST_FILE = PROCESSED_DIR / "ddos_test.csv"

TRAIN_OUTPUT = PROCESSED_DIR / "ddos_train_scaled.csv"
VAL_OUTPUT = PROCESSED_DIR / "ddos_validation_scaled.csv"
TEST_OUTPUT = PROCESSED_DIR / "ddos_test_scaled.csv"

SCALER_FILE = MODEL_DIR / "ddos_standard_scaler.joblib"

print("=" * 75)
print("CICIDS2017 - TRAINING-ONLY FEATURE SCALING")
print("=" * 75)

# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_FILE, low_memory=False)
val_df = pd.read_csv(VAL_FILE, low_memory=False)
test_df = pd.read_csv(TEST_FILE, low_memory=False)

print(f"Train rows      : {len(train_df):,}")
print(f"Validation rows : {len(val_df):,}")
print(f"Test rows       : {len(test_df):,}")

# ---------------------------------------------------------
# Metadata columns
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

print(f"\nFeature columns: {len(feature_columns)}")

# Make sure all splits have identical features
if feature_columns != [
    column
    for column in val_df.columns
    if column not in metadata_columns
]:
    raise ValueError(
        "Validation feature columns do not match training."
    )

if feature_columns != [
    column
    for column in test_df.columns
    if column not in metadata_columns
]:
    raise ValueError(
        "Test feature columns do not match training."
    )

# ---------------------------------------------------------
# Extract feature matrices
# ---------------------------------------------------------

X_train = train_df[feature_columns].copy()
X_val = val_df[feature_columns].copy()
X_test = test_df[feature_columns].copy()

# ---------------------------------------------------------
# Final numeric validation
# ---------------------------------------------------------

for name, X in [
    ("TRAIN", X_train),
    ("VALIDATION", X_val),
    ("TEST", X_test)
]:

    if X.isnull().any().any():

        raise ValueError(
            f"{name} contains NaN values."
        )

    if np.isinf(X.to_numpy()).any():

        raise ValueError(
            f"{name} contains infinite values."
        )

# ---------------------------------------------------------
# Fit scaler ONLY on TRAIN
# ---------------------------------------------------------

print("\nFitting StandardScaler on TRAIN only...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

print("Scaler fitted.")

# ---------------------------------------------------------
# Transform validation and test
# ---------------------------------------------------------

print("\nTransforming validation set...")

X_val_scaled = scaler.transform(X_val)

print("Transforming test set...")

X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------
# Convert back to DataFrames
# ---------------------------------------------------------

train_scaled = train_df[metadata_columns].copy()
val_scaled = val_df[metadata_columns].copy()
test_scaled = test_df[metadata_columns].copy()

train_scaled[feature_columns] = X_train_scaled
val_scaled[feature_columns] = X_val_scaled
test_scaled[feature_columns] = X_test_scaled

# ---------------------------------------------------------
# Save scaled datasets
# ---------------------------------------------------------

print("\nSaving scaled datasets...")

train_scaled.to_csv(
    TRAIN_OUTPUT,
    index=False
)

val_scaled.to_csv(
    VAL_OUTPUT,
    index=False
)

test_scaled.to_csv(
    TEST_OUTPUT,
    index=False
)

# ---------------------------------------------------------
# Save scaler
# ---------------------------------------------------------

joblib.dump(
    scaler,
    SCALER_FILE
)

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SCALING VALIDATION")
print("=" * 75)

print(
    f"\nTrain shape      : {train_scaled.shape}"
)

print(
    f"Validation shape : {val_scaled.shape}"
)

print(
    f"Test shape       : {test_scaled.shape}"
)

print(
    "\nTraining feature mean "
    "(average absolute):",
    np.mean(np.abs(X_train_scaled.mean(axis=0)))
)

print(
    "Training feature std "
    "(average):",
    np.mean(X_train_scaled.std(axis=0))
)

print("\nLabel distribution:")

print("\nTRAIN:")
print(train_scaled["Label"].value_counts())

print("\nVALIDATION:")
print(val_scaled["Label"].value_counts())

print("\nTEST:")
print(test_scaled["Label"].value_counts())

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print("\nSaved files:")

print(TRAIN_OUTPUT)
print(VAL_OUTPUT)
print(TEST_OUTPUT)
print(SCALER_FILE)

print(
    "\nScaler was fitted ONLY on training data."
)

print("=" * 75)