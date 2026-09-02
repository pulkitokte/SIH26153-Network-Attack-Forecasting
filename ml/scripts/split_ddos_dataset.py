import pandas as pd
from pathlib import Path

# =========================================================
# CICIDS2017 - Episode-Level Train / Validation / Test Split
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

OUTPUT_DIR = BASE_DIR / "processed"

TRAIN_FILE = OUTPUT_DIR / "ddos_train.csv"
VAL_FILE = OUTPUT_DIR / "ddos_validation.csv"
TEST_FILE = OUTPUT_DIR / "ddos_test.csv"

print("=" * 75)
print("CICIDS2017 - EPISODE-LEVEL DATASET SPLIT")
print("=" * 75)

# ---------------------------------------------------------
# Load
# ---------------------------------------------------------

print("\nLoading prepared dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Total rows    : {len(df):,}")
print(f"Total columns : {len(df.columns):,}")

# ---------------------------------------------------------
# Validate required metadata
# ---------------------------------------------------------

required_columns = [
    "episode_id",
    "sequence_phase",
    "sequence_position",
    "Label"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column missing: {column}"
        )

# ---------------------------------------------------------
# Get episodes
# ---------------------------------------------------------

episodes = sorted(
    df["episode_id"].unique()
)

print(f"\nTotal episodes: {len(episodes)}")

# We expect 21 episodes
if len(episodes) != 21:

    raise ValueError(
        f"Expected 21 episodes, found {len(episodes)}"
    )

# ---------------------------------------------------------
# Split by complete episodes
# ---------------------------------------------------------

train_episodes = episodes[:15]
validation_episodes = episodes[15:18]
test_episodes = episodes[18:21]

print("\n" + "=" * 75)
print("EPISODE ALLOCATION")
print("=" * 75)

print(
    "\nTRAIN episodes:"
    f"\n{train_episodes}"
)

print(
    "\nVALIDATION episodes:"
    f"\n{validation_episodes}"
)

print(
    "\nTEST episodes:"
    f"\n{test_episodes}"
)

# ---------------------------------------------------------
# Create datasets
# ---------------------------------------------------------

train_df = df[
    df["episode_id"].isin(train_episodes)
].copy()

validation_df = df[
    df["episode_id"].isin(validation_episodes)
].copy()

test_df = df[
    df["episode_id"].isin(test_episodes)
].copy()

# ---------------------------------------------------------
# Sort explicitly by episode and sequence position
# ---------------------------------------------------------

sort_columns = [
    "episode_id",
    "sequence_position"
]

train_df = train_df.sort_values(
    sort_columns
).reset_index(drop=True)

validation_df = validation_df.sort_values(
    sort_columns
).reset_index(drop=True)

test_df = test_df.sort_values(
    sort_columns
).reset_index(drop=True)

# ---------------------------------------------------------
# Validate no episode overlap
# ---------------------------------------------------------

train_set = set(train_df["episode_id"])
validation_set = set(validation_df["episode_id"])
test_set = set(test_df["episode_id"])

if train_set & validation_set:
    raise ValueError(
        "Episode overlap between TRAIN and VALIDATION!"
    )

if train_set & test_set:
    raise ValueError(
        "Episode overlap between TRAIN and TEST!"
    )

if validation_set & test_set:
    raise ValueError(
        "Episode overlap between VALIDATION and TEST!"
    )

# ---------------------------------------------------------
# Print dataset sizes
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("DATASET SIZES")
print("=" * 75)

print(
    f"\nTRAIN       : {len(train_df):,} rows"
)

print(
    f"VALIDATION  : {len(validation_df):,} rows"
)

print(
    f"TEST        : {len(test_df):,} rows"
)

print(
    f"TOTAL       : "
    f"{len(train_df) + len(validation_df) + len(test_df):,} rows"
)

# ---------------------------------------------------------
# Label distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("LABEL DISTRIBUTION")
print("=" * 75)

print("\nTRAIN:")
print(train_df["Label"].value_counts())

print("\nVALIDATION:")
print(validation_df["Label"].value_counts())

print("\nTEST:")
print(test_df["Label"].value_counts())

# ---------------------------------------------------------
# Episode distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE DISTRIBUTION")
print("=" * 75)

print("\nTRAIN:")
print(
    train_df.groupby(
        ["episode_id", "sequence_phase"]
    ).size()
)

print("\nVALIDATION:")
print(
    validation_df.groupby(
        ["episode_id", "sequence_phase"]
    ).size()
)

print("\nTEST:")
print(
    test_df.groupby(
        ["episode_id", "sequence_phase"]
    ).size()
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SAVING DATASETS")
print("=" * 75)

train_df.to_csv(
    TRAIN_FILE,
    index=False
)

validation_df.to_csv(
    VAL_FILE,
    index=False
)

test_df.to_csv(
    TEST_FILE,
    index=False
)

print(
    f"\nTRAIN file:"
    f"\n{TRAIN_FILE}"
)

print(
    f"\nVALIDATION file:"
    f"\n{VAL_FILE}"
)

print(
    f"\nTEST file:"
    f"\n{TEST_FILE}"
)

# ---------------------------------------------------------
# Final validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FINAL VALIDATION")
print("=" * 75)

total_split_rows = (
    len(train_df)
    + len(validation_df)
    + len(test_df)
)

if total_split_rows != len(df):

    raise ValueError(
        "Split row count does not match original dataset!"
    )

print(
    "\n[OK] No episode overlap."
)

print(
    "[OK] All rows accounted for."
)

print(
    "[OK] Episode order preserved."
)

print(
    "\nOriginal prepared dataset was NOT modified."
)

print("=" * 75)
print("SUCCESS")
print("=" * 75)