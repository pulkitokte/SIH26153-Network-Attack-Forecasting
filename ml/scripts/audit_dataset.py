import pandas as pd
import numpy as np
from pathlib import Path

INPUT_FILE = Path("samples/cicids_sample_5000.csv")
REPORT_FILE = Path("reports/dataset_audit_report.txt")

print("=" * 70)
print("CICIDS2017 - DATASET AUDIT")
print("=" * 70)

# ----------------------------------------------------------
# Load dataset
# ----------------------------------------------------------

print("\n[1] Loading dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# Clean column names
df.columns = df.columns.str.strip()

# ----------------------------------------------------------
# Basic information
# ----------------------------------------------------------

print("\n[2] Dataset shape")
print("-" * 70)
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]:,}")

# ----------------------------------------------------------
# Column list
# ----------------------------------------------------------

print("\n[3] Column names")
print("-" * 70)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")

# ----------------------------------------------------------
# Data types
# ----------------------------------------------------------

print("\n[4] Data types")
print("-" * 70)

print(df.dtypes.to_string())

# ----------------------------------------------------------
# Label distribution
# ----------------------------------------------------------

print("\n[5] Label distribution")
print("-" * 70)

if "Label" in df.columns:

    label_counts = df["Label"].value_counts(dropna=False)

    for label, count in label_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{str(label):<35} {count:>8,} ({percentage:>6.2f}%)")

else:
    print("WARNING: Label column not found.")

# ----------------------------------------------------------
# Missing values
# ----------------------------------------------------------

print("\n[6] Missing values")
print("-" * 70)

missing = df.isna().sum()
missing = missing[missing > 0].sort_values(ascending=False)

if len(missing) == 0:
    print("No missing values found.")
else:
    print(missing.to_string())

# ----------------------------------------------------------
# Infinite values
# ----------------------------------------------------------

print("\n[7] Infinite values")
print("-" * 70)

numeric_df = df.select_dtypes(include=np.number)

infinite_counts = np.isinf(numeric_df).sum()
infinite_counts = infinite_counts[infinite_counts > 0].sort_values(
    ascending=False
)

if len(infinite_counts) == 0:
    print("No infinite values found.")
else:
    print(infinite_counts.to_string())

# ----------------------------------------------------------
# Duplicate rows
# ----------------------------------------------------------

print("\n[8] Duplicate rows")
print("-" * 70)

duplicate_count = df.duplicated().sum()

print(f"Duplicate rows : {duplicate_count:,}")
print(
    f"Duplicate percentage : "
    f"{(duplicate_count / len(df)) * 100:.2f}%"
)

# ----------------------------------------------------------
# Constant columns
# ----------------------------------------------------------

print("\n[9] Constant columns")
print("-" * 70)

constant_columns = []

for column in df.columns:

    unique_count = df[column].nunique(dropna=False)

    if unique_count <= 1:
        constant_columns.append(column)

if constant_columns:
    for column in constant_columns:
        print(column)
else:
    print("No constant columns found.")

# ----------------------------------------------------------
# Low-cardinality columns
# ----------------------------------------------------------

print("\n[10] Low-cardinality columns")
print("-" * 70)

for column in df.columns:

    unique_count = df[column].nunique(dropna=False)

    if unique_count <= 10:
        print(
            f"{column:<40} "
            f"unique values = {unique_count}"
        )

# ----------------------------------------------------------
# Numeric / non-numeric columns
# ----------------------------------------------------------

print("\n[11] Feature types")
print("-" * 70)

numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
non_numeric_columns = df.select_dtypes(exclude=np.number).columns.tolist()

print(f"Numeric columns     : {len(numeric_columns)}")
print(f"Non-numeric columns : {len(non_numeric_columns)}")

print("\nNumeric columns:")
for column in numeric_columns:
    print(f"  - {column}")

print("\nNon-numeric columns:")
for column in non_numeric_columns:
    print(f"  - {column}")

# ----------------------------------------------------------
# Suspicious identifier / metadata columns
# ----------------------------------------------------------

print("\n[12] Identifier / metadata columns")
print("-" * 70)

identifier_keywords = [
    "flow id",
    "source ip",
    "destination ip",
    "timestamp",
    "date",
    "time"
]

possible_identifier_columns = []

for column in df.columns:

    column_lower = column.lower()

    if any(keyword in column_lower for keyword in identifier_keywords):
        possible_identifier_columns.append(column)

if possible_identifier_columns:

    for column in possible_identifier_columns:
        print(column)

else:
    print("No obvious identifier/metadata columns detected.")

# ----------------------------------------------------------
# Numeric statistics
# ----------------------------------------------------------

print("\n[13] Numeric feature statistics")
print("-" * 70)

if len(numeric_columns) > 0:

    stats = df[numeric_columns].describe().T

    print(
        stats[
            [
                "count",
                "mean",
                "std",
                "min",
                "max"
            ]
        ].to_string()
    )

# ----------------------------------------------------------
# Highly suspicious values
# ----------------------------------------------------------

print("\n[14] Columns with very large values")
print("-" * 70)

for column in numeric_columns:

    max_value = df[column].max()

    if pd.notna(max_value) and abs(max_value) > 1e9:

        print(
            f"{column:<40} "
            f"max = {max_value}"
        )

# ----------------------------------------------------------
# Save report
# ----------------------------------------------------------

print("\n[15] Saving audit report...")

with open(REPORT_FILE, "w", encoding="utf-8") as file:

    file.write("=" * 70 + "\n")
    file.write("CICIDS2017 - DATASET AUDIT REPORT\n")
    file.write("=" * 70 + "\n\n")

    file.write(f"Rows    : {len(df):,}\n")
    file.write(f"Columns : {len(df.columns):,}\n\n")

    file.write("LABEL DISTRIBUTION\n")
    file.write("-" * 70 + "\n")

    if "Label" in df.columns:

        for label, count in df["Label"].value_counts(
            dropna=False
        ).items():

            percentage = (count / len(df)) * 100

            file.write(
                f"{str(label):<35} "
                f"{count:>8,} "
                f"({percentage:>6.2f}%)\n"
            )

    file.write("\nMISSING VALUES\n")
    file.write("-" * 70 + "\n")

    if len(missing) == 0:
        file.write("None\n")
    else:
        file.write(missing.to_string() + "\n")

    file.write("\nINFINITE VALUES\n")
    file.write("-" * 70 + "\n")

    if len(infinite_counts) == 0:
        file.write("None\n")
    else:
        file.write(infinite_counts.to_string() + "\n")

    file.write("\nDUPLICATES\n")
    file.write("-" * 70 + "\n")
    file.write(f"{duplicate_count:,}\n")

    file.write("\nCONSTANT COLUMNS\n")
    file.write("-" * 70 + "\n")

    if constant_columns:
        for column in constant_columns:
            file.write(column + "\n")
    else:
        file.write("None\n")

    file.write("\nNUMERIC COLUMNS\n")
    file.write("-" * 70 + "\n")

    for column in numeric_columns:
        file.write(column + "\n")

    file.write("\nNON-NUMERIC COLUMNS\n")
    file.write("-" * 70 + "\n")

    for column in non_numeric_columns:
        file.write(column + "\n")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)

print(f"\nReport saved as: {REPORT_FILE}")
print("\nOriginal sample dataset was NOT modified.")
print("=" * 70)