import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CICIDS2017 - MULTI-HORIZON SEQUENCE TENSOR VALIDATION
#
# Read-only checks against generated tensors and metadata.
# This script does not modify any dataset, tensor, model,
# or generator.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"
REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "multihorizon_tensor_validation_report.txt"
)

OBSERVATION_LENGTH = 100
EXPECTED_FEATURES = 68
HORIZONS = [50, 100, 200, 500]

SPLITS = ("train", "validation", "test")

EXPECTED_X_SHAPES = {
    "train": (13515, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    "validation": (2703, OBSERVATION_LENGTH, EXPECTED_FEATURES),
    "test": (2703, OBSERVATION_LENGTH, EXPECTED_FEATURES),
}

EXPECTED_SPLIT_COUNTS = {
    "train": 13515,
    "validation": 2703,
    "test": 2703,
}

EXPECTED_EPISODES = {
    "train": set(range(1, 16)),
    "validation": set(range(16, 19)),
    "test": set(range(19, 22)),
}

EXPECTED_POSITIVES = {
    50: {"train": 750, "validation": 150, "test": 150},
    100: {"train": 1500, "validation": 300, "test": 300},
    200: {"train": 3000, "validation": 600, "test": 600},
    500: {"train": 7500, "validation": 1500, "test": 1500},
}

METADATA_SPLIT_NAMES = {
    "train": "TRAIN",
    "validation": "VALIDATION",
    "test": "TEST",
}

EXPECTED_METADATA_ROWS = 18921

REQUIRED_METADATA_COLUMNS = [
    "window_id",
    "episode_id",
    "observation_start_position",
    "observation_end_position",
    "observation_length",
    "forecast_start_position",
    "dataset_split",
    "y50",
    "y100",
    "y200",
    "y500",
]


# ============================================================
# LOGGING
# ============================================================

class ReportLogger:
    def __init__(self):
        self.lines = []

    def log(self, *args, sep=" ", end="\n"):
        text = sep.join(str(arg) for arg in args) + end
        self.lines.append(text)
        print(text, end="")

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(self.lines), encoding="utf-8")


logger = ReportLogger()
log = logger.log
checks = []


def record_check(name, status, details=""):
    checks.append(
        {
            "name": name,
            "status": status,
            "details": details,
        }
    )
    suffix = f"  {details}" if details else ""
    log(f"[{status}] {name}{suffix}")


def tensor_path(name, split):
    return PROCESSED_DIR / f"multihorizon_{name}_{split}.npy"


# ============================================================
# HEADER
# ============================================================

log("=" * 75)
log("CICIDS2017 - MULTI-HORIZON SEQUENCE TENSOR VALIDATION")
log("=" * 75)
log("\nThis is a read-only validation.")
log("No tensor, dataset, model, or generator will be modified.")


# ============================================================
# LOAD TENSORS
# ============================================================

log("\n" + "=" * 75)
log("LOAD TENSORS")
log("=" * 75)

X = {}
y = {horizon: {} for horizon in HORIZONS}
missing_files = []

for split in SPLITS:
    path = tensor_path("X", split)
    log(f"\nLoading {path.name}")
    if not path.exists():
        missing_files.append(str(path))
        log("  [FAIL] File not found")
        continue
    X[split] = np.load(path, mmap_mode="r")
    log(f"  shape={X[split].shape}  dtype={X[split].dtype}")

    for horizon in HORIZONS:
        y_path = tensor_path(f"y{horizon}", split)
        log(f"Loading {y_path.name}")
        if not y_path.exists():
            missing_files.append(str(y_path))
            log("  [FAIL] File not found")
            continue
        y[horizon][split] = np.load(y_path)
        log(
            f"  shape={y[horizon][split].shape}  "
            f"dtype={y[horizon][split].dtype}"
        )

if missing_files:
    record_check(
        "Required tensor files exist",
        "FAIL",
        "Missing: " + "; ".join(missing_files),
    )
    log("\nOVERALL: [FAIL]")
    logger.save(REPORT_FILE)
    raise FileNotFoundError(
        "One or more tensor files are missing."
    )

record_check("Required tensor files exist", "OK")


# ============================================================
# LOAD METADATA
# ============================================================

log("\n" + "=" * 75)
log("LOAD METADATA")
log("=" * 75)

metadata_path = (
    PROCESSED_DIR / "multihorizon_sequence_metadata.csv"
)
log(f"\nMetadata file: {metadata_path}")

if not metadata_path.exists():
    record_check("Metadata file exists", "FAIL")
    log("\nOVERALL: [FAIL]")
    logger.save(REPORT_FILE)
    raise FileNotFoundError(str(metadata_path))

metadata = pd.read_csv(metadata_path)
metadata.columns = metadata.columns.str.strip()

log(f"Rows    : {len(metadata):,}")
log(f"Columns : {len(metadata.columns):,}")
log("Columns : " + ", ".join(metadata.columns.tolist()))

record_check("Metadata file exists", "OK")

missing_meta_cols = [
    column
    for column in REQUIRED_METADATA_COLUMNS
    if column not in metadata.columns
]

if missing_meta_cols:
    record_check(
        "Metadata columns",
        "FAIL",
        "Missing: " + ", ".join(missing_meta_cols),
    )
else:
    record_check("Metadata columns", "OK")


# ============================================================
# X SHAPES
# ============================================================

log("\n" + "=" * 75)
log("X SHAPES")
log("=" * 75)

for split in SPLITS:
    expected = EXPECTED_X_SHAPES[split]
    actual = tuple(X[split].shape)
    log(f"\n{split.upper()}")
    log(f"  Expected : {expected}")
    log(f"  Actual   : {actual}")
    if actual == expected:
        record_check(f"X_{split} shape", "OK", str(actual))
    else:
        record_check(
            f"X_{split} shape",
            "FAIL",
            f"expected {expected}, got {actual}",
        )


# ============================================================
# TARGET LENGTHS AND BINARY VALUES
# ============================================================

log("\n" + "=" * 75)
log("TARGET LENGTHS AND VALUE CHECKS")
log("=" * 75)

for split in SPLITS:
    n_x = X[split].shape[0]
    log(f"\n{split.upper()}  X rows={n_x:,}")

    for horizon in HORIZONS:
        target = np.asarray(y[horizon][split])
        n_y = target.shape[0]
        unique_vals = np.unique(target)

        length_ok = (
            target.ndim == 1
            and n_y == n_x
            and n_y == EXPECTED_SPLIT_COUNTS[split]
        )
        binary_ok = set(unique_vals.tolist()).issubset({0, 1})

        log(
            f"  y{horizon}: shape={target.shape}  "
            f"unique={unique_vals.tolist()}"
        )

        if length_ok:
            record_check(
                f"y{horizon}_{split} length matches X",
                "OK",
                str(target.shape),
            )
        else:
            record_check(
                f"y{horizon}_{split} length matches X",
                "FAIL",
                (
                    f"target shape={target.shape}, "
                    f"X rows={n_x}, "
                    f"expected rows={EXPECTED_SPLIT_COUNTS[split]}"
                ),
            )

        if binary_ok:
            record_check(
                f"y{horizon}_{split} is binary 0/1",
                "OK",
            )
        else:
            record_check(
                f"y{horizon}_{split} is binary 0/1",
                "FAIL",
                f"unique values={unique_vals.tolist()}",
            )


# ============================================================
# TARGET DISTRIBUTIONS
# ============================================================

log("\n" + "=" * 75)
log("TARGET DISTRIBUTIONS")
log("=" * 75)

for horizon in HORIZONS:
    log(f"\n--- {horizon}-flow horizon ---")

    for split in SPLITS:
        target = np.asarray(y[horizon][split])
        n0 = int((target == 0).sum())
        n1 = int((target == 1).sum())
        total = n0 + n1
        expected_pos = EXPECTED_POSITIVES[horizon][split]
        rate = (n1 / total) if total else float("nan")

        log(
            f"  {split.upper():<11} "
            f"0={n0:,}  1={n1:,}  "
            f"positive_rate={rate:.4f}  "
            f"expected_positives={expected_pos:,}"
        )

        if n1 == expected_pos:
            record_check(
                f"{horizon}-flow {split} positives",
                "OK",
                f"{n1:,}",
            )
        else:
            record_check(
                f"{horizon}-flow {split} positives",
                "FAIL",
                f"expected {expected_pos:,}, got {n1:,}",
            )


# ============================================================
# NAN / INF / SEQUENCE / FEATURES
# ============================================================

log("\n" + "=" * 75)
log("NaN / INF / SEQUENCE STRUCTURE")
log("=" * 75)

total_nan = 0
total_inf = 0

for split in SPLITS:
    x_split = np.asarray(X[split])
    nan_count = int(np.isnan(x_split).sum())
    inf_count = int(np.isinf(x_split).sum())
    seq_len = x_split.shape[1] if x_split.ndim == 3 else None
    n_features = x_split.shape[2] if x_split.ndim == 3 else None
    total_nan += nan_count
    total_inf += inf_count

    log(f"\n{split.upper()}")
    log(f"  NaN count       : {nan_count}")
    log(f"  Inf count       : {inf_count}")
    log(f"  Sequence length : {seq_len}")
    log(f"  Feature count   : {n_features}")

    if seq_len == OBSERVATION_LENGTH:
        record_check(
            f"X_{split} sequence length = 100",
            "OK",
        )
    else:
        record_check(
            f"X_{split} sequence length = 100",
            "FAIL",
            f"got {seq_len}",
        )

    if n_features == EXPECTED_FEATURES:
        record_check(
            f"X_{split} feature count = 68",
            "OK",
        )
    else:
        record_check(
            f"X_{split} feature count = 68",
            "FAIL",
            f"got {n_features}",
        )

log(f"\nTotal NaN in all X tensors: {total_nan}")
log(f"Total Inf in all X tensors: {total_inf}")

if total_nan == 0:
    record_check("NaN count = 0", "OK")
else:
    record_check("NaN count = 0", "FAIL", f"count={total_nan}")

if total_inf == 0:
    record_check("Inf count = 0", "OK")
else:
    record_check("Inf count = 0", "FAIL", f"count={total_inf}")


# ============================================================
# METADATA SPLITS AND EPISODES
# ============================================================

log("\n" + "=" * 75)
log("METADATA VALIDATION")
log("=" * 75)

n_meta = len(metadata)
log(f"\nTotal metadata rows: {n_meta:,}")
log(f"Expected           : {EXPECTED_METADATA_ROWS:,}")

if n_meta == EXPECTED_METADATA_ROWS:
    record_check("Metadata total rows = 18,921", "OK")
else:
    record_check(
        "Metadata total rows = 18,921",
        "FAIL",
        f"got {n_meta:,}",
    )

if "dataset_split" in metadata.columns:
    split_counts = (
        metadata["dataset_split"]
        .value_counts()
        .reindex(["TRAIN", "VALIDATION", "TEST"])
    )
    log("\ndataset_split counts:")
    log(str(split_counts))

    for split in SPLITS:
        label = METADATA_SPLIT_NAMES[split]
        actual_count = int((metadata["dataset_split"] == label).sum())
        expected_count = EXPECTED_SPLIT_COUNTS[split]
        if actual_count == expected_count:
            record_check(
                f"Metadata {label} count",
                "OK",
                f"{actual_count:,}",
            )
        else:
            record_check(
                f"Metadata {label} count",
                "FAIL",
                f"expected {expected_count:,}, got {actual_count:,}",
            )
else:
    record_check(
        "Metadata split counts",
        "FAIL",
        "dataset_split column is missing",
    )

if "episode_id" in metadata.columns:
    episodes_by_split = {}
    for split in SPLITS:
        label = METADATA_SPLIT_NAMES[split]
        if "dataset_split" in metadata.columns:
            subset = metadata[metadata["dataset_split"] == label]
        else:
            subset = metadata.iloc[0:0]
        episodes = set(subset["episode_id"].astype(int).tolist())
        episodes_by_split[split] = episodes
        expected = EXPECTED_EPISODES[split]
        log(f"\n{label} episodes: {sorted(episodes)}")
        log(f"Expected        : {sorted(expected)}")
        if episodes == expected:
            record_check(
                f"{label} episodes",
                "OK",
                f"{min(expected)}-{max(expected)}",
            )
        else:
            record_check(
                f"{label} episodes",
                "FAIL",
                (
                    f"expected {sorted(expected)}, "
                    f"got {sorted(episodes)}"
                ),
            )

    overlap_tv = (
        episodes_by_split["train"]
        & episodes_by_split["validation"]
    )
    overlap_tt = (
        episodes_by_split["train"]
        & episodes_by_split["test"]
    )
    overlap_vt = (
        episodes_by_split["validation"]
        & episodes_by_split["test"]
    )

    if overlap_tv or overlap_tt or overlap_vt:
        record_check(
            "No episode overlap",
            "FAIL",
            (
                f"TRAIN∩VAL={sorted(overlap_tv)}, "
                f"TRAIN∩TEST={sorted(overlap_tt)}, "
                f"VAL∩TEST={sorted(overlap_vt)}"
            ),
        )
    else:
        record_check("No episode overlap", "OK")
else:
    record_check(
        "Episode split",
        "FAIL",
        "episode_id column is missing",
    )


# ============================================================
# METADATA ORDERING MATCHES TENSOR ORDERING
# ============================================================

log("\n" + "=" * 75)
log("METADATA / TENSOR ALIGNMENT")
log("=" * 75)

log(
    "\nTensors were built in metadata row order, then split "
    "by episode_id. Each split tensor must match the "
    "corresponding metadata subset in that same order."
)

if "dataset_split" not in metadata.columns:
    record_check(
        "Metadata ordering matches tensors",
        "FAIL",
        "Cannot align without dataset_split",
    )
else:
    alignment_failures = []

    for split in SPLITS:
        label = METADATA_SPLIT_NAMES[split]
        subset = metadata[metadata["dataset_split"] == label]

        log(f"\n{label}:")
        log(f"  metadata rows : {len(subset):,}")
        log(f"  X rows        : {X[split].shape[0]:,}")

        if len(subset) != X[split].shape[0]:
            alignment_failures.append(
                f"{label} row count {len(subset)} != "
                f"X rows {X[split].shape[0]}"
            )
            continue

        for horizon in HORIZONS:
            meta_col = f"y{horizon}"
            if meta_col not in subset.columns:
                alignment_failures.append(
                    f"{label} missing metadata column {meta_col}"
                )
                continue

            meta_targets = subset[meta_col].to_numpy(dtype=np.int64)
            tensor_targets = np.asarray(
                y[horizon][split]
            ).astype(np.int64, copy=False)

            if meta_targets.shape != tensor_targets.shape:
                alignment_failures.append(
                    f"{label} y{horizon} shape "
                    f"{meta_targets.shape} != "
                    f"{tensor_targets.shape}"
                )
                continue

            n_mismatch = int(
                np.sum(meta_targets != tensor_targets)
            )
            if n_mismatch:
                alignment_failures.append(
                    f"{label} y{horizon}: {n_mismatch:,} "
                    "positions disagree with metadata"
                )
            else:
                log(
                    f"  y{horizon} matches metadata in order"
                )

    if alignment_failures:
        record_check(
            "Metadata ordering matches tensors",
            "FAIL",
            alignment_failures[0]
            if len(alignment_failures) == 1
            else (
                f"{len(alignment_failures)} issues. First: "
                + alignment_failures[0]
            ),
        )
        for item in alignment_failures:
            log(f"  - {item}")
    else:
        record_check(
            "Metadata ordering matches tensors",
            "OK",
            "All split targets match metadata row order",
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

log("\n" + "=" * 75)
log("FINAL VALIDATION")
log("=" * 75)

n_ok = sum(1 for item in checks if item["status"] == "OK")
n_warn = sum(1 for item in checks if item["status"] == "WARNING")
n_fail = sum(1 for item in checks if item["status"] == "FAIL")

log("")
for item in checks:
    extra = f"  {item['details']}" if item["details"] else ""
    log(f"[{item['status']}] {item['name']}{extra}")

log("\n" + "-" * 75)
log(f"Summary: {n_ok} OK, {n_warn} WARNING, {n_fail} FAIL")

if n_fail:
    log("\nFailed checks:")
    for item in checks:
        if item["status"] != "FAIL":
            continue
        log(f"  - {item['name']}: {item['details']}")
    overall = "FAIL"
else:
    overall = "OK"

log(f"\nOVERALL: [{overall}]")

log("\n" + "=" * 75)
log("VALIDATION COMPLETE")
log("=" * 75)

logger.save(REPORT_FILE)

log(f"\nReport saved to:\n{REPORT_FILE}")
log("\nNo tensor, dataset, model, or generator was modified.")
log("=" * 75)
