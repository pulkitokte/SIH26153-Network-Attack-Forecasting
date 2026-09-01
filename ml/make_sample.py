import pandas as pd
from pathlib import Path

INPUT_FILE = Path("Tuesday-WorkingHours.pcap_ISCX.csv")
OUTPUT_FILE = Path("cicids_sample_5000.csv")

TARGET_SIZE = 5000
RANDOM_STATE = 42

print("=" * 60)
print("CICIDS2017 - Representative Sample Generator")
print("=" * 60)

print("\nLoading original dataset...")
df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Total rows loaded : {len(df):,}")
print(f"Total columns     : {len(df.columns):,}")

# Clean column names
df.columns = df.columns.str.strip()

# Check label column
if "Label" not in df.columns:
    raise ValueError(
        "ERROR: 'Label' column was not found.\n"
        f"Available columns: {list(df.columns)}"
    )

# Clean labels
df["Label"] = df["Label"].astype(str).str.strip()

# Remove completely empty rows
df = df.dropna(how="all").reset_index(drop=True)

print(f"Rows after cleanup: {len(df):,}")

# ----------------------------------------------------------
# Original label distribution
# ----------------------------------------------------------

label_counts = df["Label"].value_counts()

print("\nOriginal label distribution:")
print("-" * 60)

for label, count in label_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{label:<30} {count:>10,}  ({percentage:>6.2f}%)")

# ----------------------------------------------------------
# Calculate proportional sample sizes
# using the largest-remainder method
# ----------------------------------------------------------

total_rows = len(df)

ideal_sizes = (label_counts / total_rows) * TARGET_SIZE
sample_sizes = ideal_sizes.astype(int)

# Make sure every class that exists gets at least one row
for label in sample_sizes.index:
    if sample_sizes[label] == 0:
        sample_sizes[label] = 1

# Adjust total to exactly TARGET_SIZE
difference = TARGET_SIZE - sample_sizes.sum()

if difference > 0:
    # Give extra rows to classes with largest fractional parts
    fractional_parts = ideal_sizes - ideal_sizes.astype(int)

    order = fractional_parts.sort_values(ascending=False).index

    i = 0
    while difference > 0:
        label = order[i % len(order)]

        if sample_sizes[label] < label_counts[label]:
            sample_sizes[label] += 1
            difference -= 1

        i += 1

elif difference < 0:
    # Remove rows from largest classes first
    order = sample_sizes.sort_values(ascending=False).index

    i = 0
    while difference < 0:
        label = order[i % len(order)]

        if sample_sizes[label] > 1:
            sample_sizes[label] -= 1
            difference += 1

        i += 1

print("\nSample allocation:")
print("-" * 60)

for label in sample_sizes.index:
    print(f"{label:<30} {sample_sizes[label]:>10,}")

print(f"\nTotal sample rows: {sample_sizes.sum():,}")

# ----------------------------------------------------------
# Create stratified random sample
# ----------------------------------------------------------

print("\nCreating representative sample...")

parts = []

for label, n in sample_sizes.items():

    group = df[df["Label"] == label]

    sampled = group.sample(
        n=n,
        random_state=RANDOM_STATE
    )

    parts.append(sampled)

sample = pd.concat(parts, ignore_index=True)

# Shuffle final sample so labels aren't grouped together
sample = sample.sample(
    frac=1,
    random_state=RANDOM_STATE
).reset_index(drop=True)

# ----------------------------------------------------------
# Save
# ----------------------------------------------------------

sample.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("SUCCESS")
print("=" * 60)

print(f"Output file : {OUTPUT_FILE}")
print(f"Rows        : {len(sample):,}")
print(f"Columns     : {len(sample.columns):,}")

print("\nSample label distribution:")
print("-" * 60)

final_counts = sample["Label"].value_counts()

for label, count in final_counts.items():
    percentage = (count / len(sample)) * 100
    print(f"{label:<30} {count:>10,}  ({percentage:>6.2f}%)")

print("\nOriginal dataset was NOT modified.")
print("=" * 60)
