import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CICIDS2017 - DDoS Feature Preparation
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_working_v1.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "ddos_feature_preparation.txt"
)

print("=" * 75)
print("CICIDS2017 - DDoS FEATURE PREPARATION")
print("=" * 75)

# ---------------------------------------------------------
# Load
# ---------------------------------------------------------

print("\nLoading working dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

df.columns = df.columns.str.strip()

print(f"Original rows    : {len(df):,}")
print(f"Original columns : {len(df.columns):,}")

# ---------------------------------------------------------
# Preserve metadata
# ---------------------------------------------------------

metadata_columns = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position"
]

for column in metadata_columns:

    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

# ---------------------------------------------------------
# Separate feature columns
# ---------------------------------------------------------

feature_columns = [
    column
    for column in df.columns
    if column not in metadata_columns
]

print(
    f"\nInitial feature columns: "
    f"{len(feature_columns)}"
)

# ---------------------------------------------------------
# Convert feature columns to numeric
# ---------------------------------------------------------

for column in feature_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# ---------------------------------------------------------
# Replace infinity with NaN
# ---------------------------------------------------------

print("\nHandling infinite values...")

infinite_counts = np.isinf(
    df[feature_columns]
).sum()

infinite_counts = infinite_counts[
    infinite_counts > 0
]

if len(infinite_counts) > 0:

    print("\nInfinite values found:")

    for column, count in infinite_counts.items():

        print(
            f"  {column}: "
            f"{int(count):,}"
        )

else:

    print("No infinite values found.")

df[feature_columns] = df[
    feature_columns
].replace(
    [np.inf, -np.inf],
    np.nan
)

# ---------------------------------------------------------
# Missing values
# ---------------------------------------------------------

print("\nMissing values after infinity conversion:")

missing_counts = df[
    feature_columns
].isna().sum()

missing_counts = missing_counts[
    missing_counts > 0
]

if len(missing_counts) > 0:

    for column, count in missing_counts.items():

        print(
            f"  {column}: "
            f"{int(count):,}"
        )

else:

    print("No missing feature values.")

# ---------------------------------------------------------
# Median imputation
# ---------------------------------------------------------

print("\nApplying median imputation...")

for column in feature_columns:

    if df[column].isna().any():

        median_value = df[column].median()

        if pd.isna(median_value):

            raise ValueError(
                f"Cannot calculate median for: {column}"
            )

        df[column] = df[column].fillna(
            median_value
        )

print("Median imputation complete.")

# ---------------------------------------------------------
# Remove constant columns
# ---------------------------------------------------------

print("\nChecking constant features...")

constant_columns = [
    column
    for column in feature_columns
    if df[column].nunique(dropna=False) <= 1
]

if constant_columns:

    print("\nConstant columns removed:")

    for column in constant_columns:

        print(f"  - {column}")

    df = df.drop(
        columns=constant_columns
    )

    feature_columns = [
        column
        for column in feature_columns
        if column not in constant_columns
    ]

else:

    print("No constant columns found.")

# ---------------------------------------------------------
# Final validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FINAL FEATURE DATASET")
print("=" * 75)

print(
    f"\nRows: "
    f"{len(df):,}"
)

print(
    f"Feature columns: "
    f"{len(feature_columns):,}"
)

print(
    f"Total columns including metadata: "
    f"{len(df.columns):,}"
)

# Check remaining NaN
remaining_nan = df[
    feature_columns
].isna().sum().sum()

# Check remaining infinity
remaining_inf = np.isinf(
    df[feature_columns]
).sum().sum()

print(
    f"\nRemaining NaN values : "
    f"{remaining_nan:,}"
)

print(
    f"Remaining Inf values : "
    f"{remaining_inf:,}"
)

if remaining_nan != 0:
    raise ValueError(
        "NaN values remain after preprocessing."
    )

if remaining_inf != 0:
    raise ValueError(
        "Infinite values remain after preprocessing."
    )

# ---------------------------------------------------------
# Label distribution
# ---------------------------------------------------------

print("\nLabel distribution:")

print(
    df["Label"].value_counts()
)

# ---------------------------------------------------------
# Episode validation
# ---------------------------------------------------------

print("\nEpisode distribution:")

print(
    df.groupby(
        ["episode_id", "sequence_phase"]
    ).size()
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - DDoS FEATURE PREPARATION\n"
    )

    report.write("=" * 75 + "\n\n")

    report.write(
        f"Input rows: {len(df):,}\n"
    )

    report.write(
        f"Final feature columns: "
        f"{len(feature_columns)}\n\n"
    )

    report.write(
        "Removed constant columns:\n"
    )

    for column in constant_columns:

        report.write(
            f"- {column}\n"
        )

    report.write(
        "\nInfinite values were replaced "
        "with NaN and median imputation "
        "was applied.\n"
    )

    report.write(
        f"\nRemaining NaN: {remaining_nan}\n"
    )

    report.write(
        f"Remaining Inf: {remaining_inf}\n"
    )

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    f"\nOutput:"
    f"\n{OUTPUT_FILE}"
)

print(
    f"\nReport:"
    f"\n{REPORT_FILE}"
)

print(
    "\nOriginal raw dataset was NOT modified."
)

print("=" * 75)