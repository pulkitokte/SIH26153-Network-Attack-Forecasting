import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CICIDS2017 - FAST SEQUENCE TENSOR BUILDER
#
# Observation window : 100 flows
# Features            : 68
#
# Uses V2 forecasting windows.
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

WINDOW_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_forecasting_windows_v2.csv"
)

OUTPUT_DIR = BASE_DIR / "processed"

print("=" * 75)
print("CICIDS2017 - FAST SEQUENCE TENSOR BUILDER")
print("=" * 75)

# ---------------------------------------------------------
# Load feature dataset
# ---------------------------------------------------------

print("\nLoading feature dataset...")

features_df = pd.read_csv(
    FEATURE_FILE,
    low_memory=False
)

features_df = features_df.sort_values(
    ["episode_id", "sequence_position"]
).reset_index(drop=True)

print(
    f"Feature rows    : {len(features_df):,}"
)

print(
    f"Feature columns : {len(features_df.columns):,}"
)

# ---------------------------------------------------------
# Load V2 windows
# ---------------------------------------------------------

print("\nLoading V2 forecasting windows...")

windows_df = pd.read_csv(
    WINDOW_FILE,
    low_memory=False
)

print(
    f"Forecasting windows : {len(windows_df):,}"
)

# ---------------------------------------------------------
# Identify 68 actual features
# ---------------------------------------------------------

metadata_columns = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position"
]

feature_columns = [
    column
    for column in features_df.columns
    if column not in metadata_columns
]

if len(feature_columns) != 68:

    raise ValueError(
        f"Expected 68 features, "
        f"found {len(feature_columns)}"
    )

print(
    f"\nFeatures used : {len(feature_columns)}"
)

# ---------------------------------------------------------
# Convert complete feature matrix to NumPy
# ---------------------------------------------------------

print(
    "\nConverting feature data to NumPy..."
)

feature_matrix = features_df[
    feature_columns
].to_numpy(
    dtype=np.float32
)

episode_array = features_df[
    "episode_id"
].to_numpy()

position_array = features_df[
    "sequence_position"
].to_numpy()

# ---------------------------------------------------------
# Create direct lookup:
# (episode_id, position) -> row index
# ---------------------------------------------------------

print(
    "Building fast position lookup..."
)

position_lookup = {
    (int(ep), int(pos)): idx
    for idx, (ep, pos)
    in enumerate(
        zip(
            episode_array,
            position_array
        )
    )
}

print(
    "Lookup ready."
)

# ---------------------------------------------------------
# Build tensors
# ---------------------------------------------------------

X = []
y = []
metadata = []

print(
    "\nConstructing sequence tensors..."
)

for counter, window in enumerate(
    windows_df.itertuples(index=False),
    start=1
):

    episode_id = int(
        window.episode_id
    )

    start_position = int(
        window.observation_start_position
    )

    end_position = int(
        window.observation_end_position
    )

    target = int(
        window.target
    )

    positions = range(
        start_position,
        end_position + 1
    )

    indices = []

    for position in positions:

        key = (
            episode_id,
            position
        )

        if key not in position_lookup:

            raise ValueError(
                "Missing row for "
                f"episode={episode_id}, "
                f"position={position}"
            )

        indices.append(
            position_lookup[key]
        )

    sequence = feature_matrix[
        indices
    ]

    if sequence.shape != (100, 68):

        raise ValueError(
            f"Invalid sequence shape: "
            f"{sequence.shape}"
        )

    X.append(sequence)

    y.append(target)

    metadata.append({

        "window_id":
            int(window.window_id),

        "episode_id":
            episode_id,

        "observation_start_position":
            start_position,

        "observation_end_position":
            end_position,

        "forecast_start_position":
            int(
                window.forecast_start_position
            ),

        "forecast_end_position":
            int(
                window.forecast_end_position
            ),

        "target":
            target
    })

    if counter % 250 == 0:

        print(
            f"  Processed "
            f"{counter:,} / "
            f"{len(windows_df):,}"
        )

# ---------------------------------------------------------
# Convert to NumPy
# ---------------------------------------------------------

X = np.asarray(
    X,
    dtype=np.float32
)

y = np.asarray(
    y,
    dtype=np.int64
)

metadata_df = pd.DataFrame(
    metadata
)

# ---------------------------------------------------------
# Episode-based split
# ---------------------------------------------------------

train_mask = (
    metadata_df["episode_id"]
    .between(1, 15)
    .to_numpy()
)

validation_mask = (
    metadata_df["episode_id"]
    .between(16, 18)
    .to_numpy()
)

test_mask = (
    metadata_df["episode_id"]
    .between(19, 21)
    .to_numpy()
)

X_train = X[train_mask]
y_train = y[train_mask]

X_validation = X[validation_mask]
y_validation = y[validation_mask]

X_test = X[test_mask]
y_test = y[test_mask]

# ---------------------------------------------------------
# Shapes
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("TENSOR SHAPES")
print("=" * 75)

print(
    f"\nX_train      : {X_train.shape}"
)

print(
    f"y_train      : {y_train.shape}"
)

print(
    f"X_validation : {X_validation.shape}"
)

print(
    f"y_validation : {y_validation.shape}"
)

print(
    f"X_test       : {X_test.shape}"
)

print(
    f"y_test       : {y_test.shape}"
)

# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("VALIDATION")
print("=" * 75)

nan_count = np.isnan(X).sum()
inf_count = np.isinf(X).sum()

print(
    f"\nNaN values : {nan_count}"
)

print(
    f"Inf values : {inf_count}"
)

print(
    f"Sequence length : {X.shape[1]}"
)

print(
    f"Feature count   : {X.shape[2]}"
)

# ---------------------------------------------------------
# Target distribution
# ---------------------------------------------------------

print("\nTarget distribution:")

print(
    "\nTRAIN:"
)

print(
    pd.Series(y_train)
    .value_counts()
    .sort_index()
)

print(
    "\nVALIDATION:"
)

print(
    pd.Series(y_validation)
    .value_counts()
    .sort_index()
)

print(
    "\nTEST:"
)

print(
    pd.Series(y_test)
    .value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Episode separation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE SEPARATION")
print("=" * 75)

train_eps = set(
    metadata_df[
        train_mask
    ]["episode_id"]
)

val_eps = set(
    metadata_df[
        validation_mask
    ]["episode_id"]
)

test_eps = set(
    metadata_df[
        test_mask
    ]["episode_id"]
)

print(
    "\nTRAIN:"
)

print(
    sorted(train_eps)
)

print(
    "\nVALIDATION:"
)

print(
    sorted(val_eps)
)

print(
    "\nTEST:"
)

print(
    sorted(test_eps)
)

if train_eps & val_eps:

    raise ValueError(
        "Train/validation episode overlap!"
    )

if train_eps & test_eps:

    raise ValueError(
        "Train/test episode overlap!"
    )

if val_eps & test_eps:

    raise ValueError(
        "Validation/test episode overlap!"
    )

print(
    "\n[OK] No episode overlap."
)

# ---------------------------------------------------------
# Final checks
# ---------------------------------------------------------

checks = [

    X_train.shape[1:] == (100, 68),

    X_validation.shape[1:] == (100, 68),

    X_test.shape[1:] == (100, 68),

    nan_count == 0,

    inf_count == 0,

    len(X_train) == len(y_train),

    len(X_validation) == len(y_validation),

    len(X_test) == len(y_test)

]

if not all(checks):

    raise RuntimeError(
        "One or more validation checks failed."
    )

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SAVING")
print("=" * 75)

np.save(
    OUTPUT_DIR / "X_train.npy",
    X_train
)

np.save(
    OUTPUT_DIR / "y_train.npy",
    y_train
)

np.save(
    OUTPUT_DIR / "X_validation.npy",
    X_validation
)

np.save(
    OUTPUT_DIR / "y_validation.npy",
    y_validation
)

np.save(
    OUTPUT_DIR / "X_test.npy",
    X_test
)

np.save(
    OUTPUT_DIR / "y_test.npy",
    y_test
)

metadata_df.to_csv(
    OUTPUT_DIR / "sequence_metadata.csv",
    index=False
)

print(
    "\n[OK] X_train.npy"
)

print(
    "[OK] y_train.npy"
)

print(
    "[OK] X_validation.npy"
)

print(
    "[OK] y_validation.npy"
)

print(
    "[OK] X_test.npy"
)

print(
    "[OK] y_test.npy"
)

print(
    "[OK] sequence_metadata.csv"
)

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    "\nOriginal datasets were NOT modified."
)

print("=" * 75)