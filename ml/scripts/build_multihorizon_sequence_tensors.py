import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CICIDS2017 - MULTI-HORIZON SEQUENCE TENSOR BUILDER
#
# Observation window : 100 flows
# Features           : 68 numerical columns
# Horizons           : 50, 100, 200, 500
#
# Inputs are taken ONLY from the observation region.
# Forecast-region flows are never used as model inputs.
#
# This script does not modify:
#   processed/ddos_features_v1.csv
#   processed/ddos_multihorizon_windows_v1.csv
#   any existing model or forecasting script
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

WINDOW_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_multihorizon_windows_v1.csv"
)

OUTPUT_DIR = BASE_DIR / "processed"

OBSERVATION_LENGTH = 100
EXPECTED_FEATURES = 68
HORIZONS = [50, 100, 200, 500]

EXPECTED_SHAPES = {
    "train": (13515, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    "validation": (2703, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    "test": (2703, OBSERVATION_LENGTH, EXPECTED_FEATURES),
}

TRAIN_EPISODES = set(range(1, 16))
VALIDATION_EPISODES = set(range(16, 19))
TEST_EPISODES = set(range(19, 22))

METADATA_COLUMNS = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position",
]

FORBIDDEN_FEATURE_SUBSTRINGS = (
    "ddos_next_",
    "ddos_count_next_",
    "ddos_ratio_next_",
)


print("=" * 75)
print("CICIDS2017 - MULTI-HORIZON SEQUENCE TENSOR BUILDER")
print("=" * 75)

print("\nThis script is read-only on source CSVs.")
print("No existing model or generator will be modified.")


# ============================================================
# LOAD
# ============================================================

print("\nLoading feature dataset...")

features_df = pd.read_csv(
    FEATURE_FILE,
    low_memory=False
)

features_df.columns = features_df.columns.str.strip()

features_df = features_df.sort_values(
    ["episode_id", "sequence_position"]
).reset_index(drop=True)

print(f"Feature rows    : {len(features_df):,}")
print(f"Feature columns : {len(features_df.columns):,}")

print("\nLoading multi-horizon forecasting windows...")

windows_df = pd.read_csv(
    WINDOW_FILE,
    low_memory=False
)

windows_df.columns = windows_df.columns.str.strip()

print(f"Forecasting windows : {len(windows_df):,}")
print(f"Window columns      : {len(windows_df.columns):,}")


# ============================================================
# FEATURE SELECTION (same convention as build_sequence_tensors.py)
# ============================================================

print("\n" + "=" * 75)
print("FEATURE SELECTION")
print("=" * 75)

missing_metadata = [
    column
    for column in METADATA_COLUMNS
    if column not in features_df.columns
]

if missing_metadata:
    raise ValueError(
        "Feature dataset is missing metadata columns: "
        + ", ".join(missing_metadata)
    )

feature_columns = [
    column
    for column in features_df.columns
    if column not in METADATA_COLUMNS
]

leaked_target_features = [
    column
    for column in feature_columns
    if any(
        token in column
        for token in FORBIDDEN_FEATURE_SUBSTRINGS
    )
    or column in {
        "window_id",
        "dataset_split",
        "forecast_start_position",
        "forecast_end_position",
        "Label",
    }
]

if leaked_target_features:
    raise ValueError(
        "Forecast target / metadata columns were selected "
        "as input features: "
        + ", ".join(leaked_target_features)
    )

if len(feature_columns) != EXPECTED_FEATURES:
    raise ValueError(
        f"Expected {EXPECTED_FEATURES} numerical features, "
        f"found {len(feature_columns)}"
    )

print(f"\nFeatures used : {len(feature_columns)}")
print("Excluded metadata columns:")
for column in METADATA_COLUMNS:
    print(f"  - {column}")

print("\n[OK] No forecast target columns are included in X.")


# ============================================================
# FEATURE MATRIX AND POSITION LOOKUP
# ============================================================

print("\nConverting feature data to NumPy...")

feature_matrix = features_df[feature_columns].to_numpy(
    dtype=np.float32
)

episode_array = features_df["episode_id"].to_numpy()
position_array = features_df["sequence_position"].to_numpy()

print("Building fast position lookup...")

position_lookup = {
    (int(episode_id), int(position)): idx
    for idx, (episode_id, position)
    in enumerate(zip(episode_array, position_array))
}

print("Lookup ready.")


# ============================================================
# REQUIRED WINDOW COLUMNS
# ============================================================

required_window_columns = [
    "window_id",
    "episode_id",
    "observation_start_position",
    "observation_end_position",
    "observation_length",
    "dataset_split",
]

for horizon in HORIZONS:
    required_window_columns.append(f"ddos_next_{horizon}")

missing_window_columns = [
    column
    for column in required_window_columns
    if column not in windows_df.columns
]

if missing_window_columns:
    raise ValueError(
        "Forecasting window CSV is missing required columns: "
        + ", ".join(missing_window_columns)
    )


# ============================================================
# BUILD TENSORS
# ============================================================

n_windows = len(windows_df)

print("\nConstructing sequence tensors...")
print(
    f"Windows to process: {n_windows:,}  "
    f"(observation={OBSERVATION_LENGTH}, "
    f"features={EXPECTED_FEATURES})"
)

X = np.empty(
    (n_windows, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    dtype=np.float32,
)

y_by_horizon = {
    horizon: np.empty(n_windows, dtype=np.int64)
    for horizon in HORIZONS
}

metadata_rows = []

for counter, window in enumerate(
    windows_df.itertuples(index=False),
    start=0
):

    episode_id = int(window.episode_id)
    start_position = int(window.observation_start_position)
    end_position = int(window.observation_end_position)
    observation_length = int(window.observation_length)

    if observation_length != OBSERVATION_LENGTH:
        raise ValueError(
            f"window_id={int(window.window_id)} has "
            f"observation_length={observation_length}, "
            f"expected {OBSERVATION_LENGTH}"
        )

    if end_position - start_position + 1 != OBSERVATION_LENGTH:
        raise ValueError(
            f"window_id={int(window.window_id)} observation "
            f"span is {end_position - start_position + 1}, "
            f"expected {OBSERVATION_LENGTH}"
        )

    forecast_start_position = end_position + 1

    indices = []

    for position in range(start_position, end_position + 1):
        key = (episode_id, position)

        if key not in position_lookup:
            raise ValueError(
                "Missing feature row for "
                f"episode={episode_id}, position={position}"
            )

        indices.append(position_lookup[key])

    if len(indices) != OBSERVATION_LENGTH:
        raise ValueError(
            f"window_id={int(window.window_id)} resolved "
            f"{len(indices)} observation rows, "
            f"expected {OBSERVATION_LENGTH}"
        )

    # Observation-only slice: never include the first forecast flow.
    if position_lookup.get(
        (episode_id, forecast_start_position)
    ) in indices:
        raise ValueError(
            f"window_id={int(window.window_id)} included the "
            "first forecast position in the observation sequence."
        )

    sequence = feature_matrix[indices]

    if sequence.shape != (OBSERVATION_LENGTH, EXPECTED_FEATURES):
        raise ValueError(
            f"Invalid sequence shape for window_id="
            f"{int(window.window_id)}: {sequence.shape}"
        )

    X[counter] = sequence

    targets = {}
    for horizon in HORIZONS:
        target_value = int(
            getattr(window, f"ddos_next_{horizon}")
        )
        y_by_horizon[horizon][counter] = target_value
        targets[horizon] = target_value

    metadata_rows.append({
        "window_id": int(window.window_id),
        "episode_id": episode_id,
        "observation_start_position": start_position,
        "observation_end_position": end_position,
        "observation_length": observation_length,
        "forecast_start_position": forecast_start_position,
        "dataset_split": str(window.dataset_split),
        "y50": targets[50],
        "y100": targets[100],
        "y200": targets[200],
        "y500": targets[500],
    })

    processed = counter + 1
    if processed % 2000 == 0 or processed == n_windows:
        print(
            f"  Processed {processed:,} / {n_windows:,}"
        )

metadata_df = pd.DataFrame(metadata_rows)

if len(metadata_df) != n_windows:
    raise ValueError(
        "Metadata row count does not equal the number of windows: "
        f"{len(metadata_df)} != {n_windows}"
    )


# ============================================================
# SPLIT BY EPISODE
# ============================================================

train_mask = metadata_df["episode_id"].between(1, 15).to_numpy()
validation_mask = metadata_df["episode_id"].between(16, 18).to_numpy()
test_mask = metadata_df["episode_id"].between(19, 21).to_numpy()

split_masks = {
    "train": train_mask,
    "validation": validation_mask,
    "test": test_mask,
}

X_split = {
    name: X[mask]
    for name, mask in split_masks.items()
}

y_split = {
    horizon: {
        name: y_by_horizon[horizon][mask]
        for name, mask in split_masks.items()
    }
    for horizon in HORIZONS
}


# ============================================================
# REPORT: SHAPES
# ============================================================

print("\n" + "=" * 75)
print("TENSOR SHAPES")
print("=" * 75)

print("\nInput:")
print(f"  Feature matrix : {feature_matrix.shape}")
print(f"  Windows        : {n_windows:,}")
print(f"  Sequence length: {OBSERVATION_LENGTH}")
print(f"  Feature count  : {EXPECTED_FEATURES}")

print("\nOutput X:")
for name in ("train", "validation", "test"):
    print(f"  X_{name:<10} : {X_split[name].shape}")

print("\nOutput y:")
for horizon in HORIZONS:
    print(f"  Horizon {horizon}:")
    for name in ("train", "validation", "test"):
        print(
            f"    y{horizon}_{name:<10} : "
            f"{y_split[horizon][name].shape}"
        )


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("VALIDATION")
print("=" * 75)

failures = []


def check(condition, message):
    if condition:
        print(f"[OK] {message}")
        return True
    print(f"[FAIL] {message}")
    failures.append(message)
    return False


nan_count = int(np.isnan(X).sum())
inf_count = int(np.isinf(X).sum())

print(f"\nNaN values in X : {nan_count}")
print(f"Inf values in X : {inf_count}")

check(nan_count == 0, "NaN count = 0")
check(inf_count == 0, "Inf count = 0")

for name in ("train", "validation", "test"):
    expected = EXPECTED_SHAPES[name]
    actual = X_split[name].shape
    check(
        actual == expected,
        f"X_{name} shape is {expected}, got {actual}",
    )

    for horizon in HORIZONS:
        y_shape = y_split[horizon][name].shape
        expected_y = (expected[0],)
        check(
            y_shape == expected_y,
            f"y{horizon}_{name} shape is {expected_y}, got {y_shape}",
        )
        check(
            len(X_split[name]) == len(y_split[horizon][name]),
            f"y{horizon}_{name} length matches X_{name}",
        )

        unique_targets = set(
            np.unique(y_split[horizon][name]).tolist()
        )
        check(
            unique_targets.issubset({0, 1}),
            f"y{horizon}_{name} contains only 0/1 "
            f"(unique={sorted(unique_targets)})",
        )

check(
    X.shape == (n_windows, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    f"Full X shape is {(n_windows, OBSERVATION_LENGTH, EXPECTED_FEATURES)}",
)

check(
    len(metadata_df) == n_windows,
    f"Metadata row count equals total windows ({n_windows:,})",
)

check(
    (
        metadata_df["observation_end_position"] + 1
        == metadata_df["forecast_start_position"]
    ).all(),
    "forecast_start_position = observation_end_position + 1",
)

check(
    (
        metadata_df["observation_end_position"]
        - metadata_df["observation_start_position"]
        + 1
        == OBSERVATION_LENGTH
    ).all(),
    "Each sequence uses observation_start_position "
    "through observation_end_position (100 flows)",
)

check(
    len(leaked_target_features) == 0,
    "No forecast target columns included among input features",
)


# ============================================================
# TARGET DISTRIBUTIONS
# ============================================================

print("\n" + "=" * 75)
print("TARGET DISTRIBUTIONS")
print("=" * 75)

for horizon in HORIZONS:
    print(f"\nHorizon {horizon} (y{horizon}):")
    for name in ("train", "validation", "test"):
        counts = (
            pd.Series(y_split[horizon][name])
            .value_counts()
            .sort_index()
        )
        n0 = int(counts.get(0, 0))
        n1 = int(counts.get(1, 0))
        total = n0 + n1
        rate = (n1 / total) if total else float("nan")
        print(
            f"  {name:<10}  0={n0:,}  1={n1:,}  "
            f"positive_rate={rate:.4f}"
        )


# ============================================================
# SPLIT DISTRIBUTIONS AND EPISODE SEPARATION
# ============================================================

print("\n" + "=" * 75)
print("SPLIT DISTRIBUTIONS")
print("=" * 75)

print("\nWindows per split:")
print(
    metadata_df["dataset_split"]
    .value_counts()
    .reindex(["TRAIN", "VALIDATION", "TEST"])
)

print("\nStored dataset_split vs episode assignment:")
split_mismatch = 0
for split_name, expected_episodes, mask in (
    ("TRAIN", TRAIN_EPISODES, train_mask),
    ("VALIDATION", VALIDATION_EPISODES, validation_mask),
    ("TEST", TEST_EPISODES, test_mask),
):
    stored = metadata_df.loc[mask, "dataset_split"]
    mismatch = int((stored != split_name).sum())
    split_mismatch += mismatch
    print(f"  {split_name:<11} mismatches={mismatch}")

check(
    split_mismatch == 0,
    "Stored dataset_split matches episode assignment",
)

print("\n" + "=" * 75)
print("EPISODE SEPARATION")
print("=" * 75)

train_eps = set(
    metadata_df.loc[train_mask, "episode_id"].astype(int)
)
val_eps = set(
    metadata_df.loc[validation_mask, "episode_id"].astype(int)
)
test_eps = set(
    metadata_df.loc[test_mask, "episode_id"].astype(int)
)

print("\nTRAIN:", sorted(train_eps))
print("VALIDATION:", sorted(val_eps))
print("TEST:", sorted(test_eps))

check(
    train_eps == TRAIN_EPISODES,
    "TRAIN episodes are exactly 1-15",
)
check(
    val_eps == VALIDATION_EPISODES,
    "VALIDATION episodes are exactly 16-18",
)
check(
    test_eps == TEST_EPISODES,
    "TEST episodes are exactly 19-21",
)

overlap_tv = train_eps & val_eps
overlap_tt = train_eps & test_eps
overlap_vt = val_eps & test_eps

check(
    len(overlap_tv) == 0,
    "No TRAIN / VALIDATION episode overlap",
)
check(
    len(overlap_tt) == 0,
    "No TRAIN / TEST episode overlap",
)
check(
    len(overlap_vt) == 0,
    "No VALIDATION / TEST episode overlap",
)

if overlap_tv or overlap_tt or overlap_vt:
    print(f"  Overlaps: {overlap_tv | overlap_tt | overlap_vt}")


# ============================================================
# SAVE ONLY IF VALID
# ============================================================

print("\n" + "=" * 75)
print("SAVING")
print("=" * 75)

if failures:
    print("\nOne or more validation checks failed:")
    for item in failures:
        print(f"  - {item}")
    print("\nNo tensor files were written.")
    print("=" * 75)
    print("FAIL")
    print("=" * 75)
    raise RuntimeError(
        f"{len(failures)} validation check(s) failed. "
        "Tensor files were not saved."
    )

output_files = {
    "multihorizon_X_train.npy": X_split["train"],
    "multihorizon_X_validation.npy": X_split["validation"],
    "multihorizon_X_test.npy": X_split["test"],
}

for horizon in HORIZONS:
    output_files[f"multihorizon_y{horizon}_train.npy"] = (
        y_split[horizon]["train"]
    )
    output_files[f"multihorizon_y{horizon}_validation.npy"] = (
        y_split[horizon]["validation"]
    )
    output_files[f"multihorizon_y{horizon}_test.npy"] = (
        y_split[horizon]["test"]
    )

for filename, array in output_files.items():
    path = OUTPUT_DIR / filename
    np.save(path, array)
    print(f"[OK] {path.name}  {array.shape}")

metadata_path = OUTPUT_DIR / "multihorizon_sequence_metadata.csv"
metadata_df.to_csv(metadata_path, index=False)
print(
    f"[OK] {metadata_path.name}  "
    f"rows={len(metadata_df):,}"
)

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print("\nOriginal feature and window CSVs were NOT modified.")
print("No model was trained.")
print("=" * 75)
