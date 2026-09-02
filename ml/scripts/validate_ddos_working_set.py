import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_working_v1.csv"
)

print("=" * 75)
print("CICIDS2017 - DDoS WORKING DATASET VALIDATION")
print("=" * 75)

print("\nLoading working dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

df.columns = df.columns.str.strip()

print(f"\nRows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# ---------------------------------------------------------
# Required columns
# ---------------------------------------------------------

required_columns = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position"
]

print("\n" + "=" * 75)
print("REQUIRED COLUMNS")
print("=" * 75)

for column in required_columns:

    if column in df.columns:
        print(f"[OK] {column}")
    else:
        print(f"[MISSING] {column}")

# ---------------------------------------------------------
# Label distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("LABEL DISTRIBUTION")
print("=" * 75)

print(df["Label"].value_counts())

# ---------------------------------------------------------
# Phase distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SEQUENCE PHASE DISTRIBUTION")
print("=" * 75)

print(df["sequence_phase"].value_counts())

# ---------------------------------------------------------
# Episode validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE VALIDATION")
print("=" * 75)

episode_summary = (
    df.groupby(["episode_id", "sequence_phase"])
    .size()
    .unstack(fill_value=0)
)

print(episode_summary)

# ---------------------------------------------------------
# Sequence position
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SEQUENCE POSITION")
print("=" * 75)

positions = df["sequence_position"]

print(f"Minimum position: {positions.min():,}")
print(f"Maximum position: {positions.max():,}")
print(f"Unique positions: {positions.nunique():,}")

expected_positions = set(range(len(df)))
actual_positions = set(positions)

if actual_positions == expected_positions:
    print("[OK] Sequence positions are continuous.")
else:
    print("[WARNING] Sequence positions are not continuous.")

# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("MISSING VALUES")
print("=" * 75)

missing = df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values.")
else:
    print(missing)

# ---------------------------------------------------------
# Infinite values
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("INFINITE VALUES")
print("=" * 75)

numeric_df = df.select_dtypes(include=np.number)

inf_counts = np.isinf(numeric_df).sum()
inf_counts = inf_counts[inf_counts > 0]

if len(inf_counts) == 0:
    print("No infinite values.")
else:
    print(inf_counts)

# ---------------------------------------------------------
# Duplicate rows
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("DUPLICATES")
print("=" * 75)

print(
    f"Duplicate complete rows: "
    f"{df.duplicated().sum():,}"
)

# ---------------------------------------------------------
# Constant columns
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("CONSTANT COLUMNS")
print("=" * 75)

constant_columns = [
    column
    for column in df.columns
    if df[column].nunique(dropna=False) <= 1
]

if constant_columns:
    for column in constant_columns:
        print(column)
else:
    print("No constant columns.")

# ---------------------------------------------------------
# First and last rows per episode
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE BOUNDARIES")
print("=" * 75)

for episode_id in sorted(df["episode_id"].unique()):

    episode = df[df["episode_id"] == episode_id]

    print(
        f"Episode {episode_id:02d}: "
        f"rows={len(episode):,}, "
        f"first_position={episode['sequence_position'].min():,}, "
        f"last_position={episode['sequence_position'].max():,}"
    )

# ---------------------------------------------------------
# Final
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("VALIDATION COMPLETE")
print("=" * 75)

print("\nOriginal raw dataset was NOT modified.")