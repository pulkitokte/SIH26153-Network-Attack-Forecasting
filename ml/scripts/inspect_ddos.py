import pandas as pd
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "raw" / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"

print("=" * 70)
print("CICIDS2017 - DDoS DATA INSPECTION")
print("=" * 70)

print("\nLoading DDoS dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"\nRows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# ---------------------------------------------------------
# Column names
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("COLUMN NAMES")
print("=" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")

# ---------------------------------------------------------
# Data types
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("DATA TYPES")
print("=" * 70)

print(df.dtypes.value_counts())

# ---------------------------------------------------------
# Label distribution
# ---------------------------------------------------------

df.columns = df.columns.str.strip()

print("\n" + "=" * 70)
print("LABEL DISTRIBUTION")
print("=" * 70)

print(df["Label"].value_counts())

# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing = df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values found.")
else:
    print(missing)

# ---------------------------------------------------------
# Infinite values
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("INFINITE VALUES")
print("=" * 70)

numeric_df = df.select_dtypes(include=np.number)

inf_counts = np.isinf(numeric_df).sum()
inf_counts = inf_counts[inf_counts > 0]

if len(inf_counts) == 0:
    print("No infinite values found.")
else:
    print(inf_counts)

# ---------------------------------------------------------
# Negative values
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("NEGATIVE VALUES")
print("=" * 70)

negative_counts = (numeric_df < 0).sum()
negative_counts = negative_counts[negative_counts > 0]

if len(negative_counts) == 0:
    print("No negative values found.")
else:
    print(negative_counts)

# ---------------------------------------------------------
# Duplicate rows
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATES")
print("=" * 70)

print(f"Duplicate rows: {df.duplicated().sum():,}")

# ---------------------------------------------------------
# Timestamp check
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("TIMESTAMP CHECK")
print("=" * 70)

timestamp_columns = [
    col for col in df.columns
    if "time" in col.lower() or "date" in col.lower()
]

if timestamp_columns:
    print("Possible timestamp/date columns:")
    for col in timestamp_columns:
        print(f"  - {col}")
else:
    print("NO timestamp/date column found.")

# ---------------------------------------------------------
# First 5 rows
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FIRST 5 ROWS")
print("=" * 70)

print(df.head().to_string())

# ---------------------------------------------------------
# Final
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)

print("\nOriginal dataset was NOT modified.")