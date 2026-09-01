import pandas as pd
from pathlib import Path

# =========================================================
# CICIDS2017 DDoS Working Dataset Generator
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "raw"
    / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
)

OUTPUT_DIR = BASE_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ddos_working_v1.csv"

# Number of flows to take from each meaningful DDoS episode
ATTACK_FLOWS_PER_EPISODE = 1000

# Number of benign flows immediately before each attack episode
BENIGN_FLOWS_BEFORE_ATTACK = 1000

MIN_DDOS_EPISODE_LENGTH = 500

print("=" * 75)
print("CICIDS2017 - DDoS WORKING DATASET GENERATOR")
print("=" * 75)

print("\nLoading original DDoS capture...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

df.columns = df.columns.str.strip()
df["Label"] = df["Label"].astype(str).str.strip()

print(f"Original rows: {len(df):,}")
print(f"Original columns: {len(df.columns):,}")

# ---------------------------------------------------------
# Find contiguous label regions
# ---------------------------------------------------------

labels = df["Label"].tolist()

runs = []

start = 0
current_label = labels[0]

for i in range(1, len(labels)):

    if labels[i] != current_label:

        runs.append({
            "label": current_label,
            "start": start,
            "end": i - 1,
            "length": i - start
        })

        start = i
        current_label = labels[i]

runs.append({
    "label": current_label,
    "start": start,
    "end": len(labels) - 1,
    "length": len(labels) - start
})

# ---------------------------------------------------------
# Select meaningful DDoS episodes
# ---------------------------------------------------------

ddos_runs = [
    run
    for run in runs
    if run["label"].lower() == "ddos"
    and run["length"] >= MIN_DDOS_EPISODE_LENGTH
]

print(f"\nMeaningful DDoS episodes found: {len(ddos_runs)}")

# ---------------------------------------------------------
# Extract ordered regions
# ---------------------------------------------------------

parts = []

for episode_id, run in enumerate(ddos_runs, start=1):

    attack_start = run["start"]
    attack_end = run["end"]

    # Take preceding benign flows
    benign_start = max(
        0,
        attack_start - BENIGN_FLOWS_BEFORE_ATTACK
    )

    benign_part = df.iloc[
        benign_start:attack_start
    ].copy()

    # Keep only BENIGN rows
    benign_part = benign_part[
        benign_part["Label"] == "BENIGN"
    ]

    # Keep last N benign flows before attack
    benign_part = benign_part.tail(
        BENIGN_FLOWS_BEFORE_ATTACK
    )

    # Take first N attack flows from episode
    attack_part = df.iloc[
        attack_start:
        min(
            attack_start + ATTACK_FLOWS_PER_EPISODE,
            attack_end + 1
        )
    ].copy()

    # Add episode metadata
    benign_part["episode_id"] = episode_id
    benign_part["sequence_phase"] = "pre_attack"

    attack_part["episode_id"] = episode_id
    attack_part["sequence_phase"] = "attack"

    parts.append(benign_part)
    parts.append(attack_part)

    print(
        f"Episode {episode_id:02d}: "
        f"BENIGN={len(benign_part):,}, "
        f"DDoS={len(attack_part):,}"
    )

# ---------------------------------------------------------
# Combine while preserving episode/order
# ---------------------------------------------------------

working_df = pd.concat(
    parts,
    ignore_index=True
)

# Add sequence position
working_df["sequence_position"] = range(
    len(working_df)
)

# ---------------------------------------------------------
# Basic validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("WORKING DATASET SUMMARY")
print("=" * 75)

print(f"\nRows    : {len(working_df):,}")
print(f"Columns : {len(working_df.columns):,}")

print("\nLabel distribution:")

label_counts = working_df["Label"].value_counts()

for label, count in label_counts.items():

    percentage = (
        count / len(working_df)
    ) * 100

    print(
        f"{label:<15} "
        f"{count:>10,} "
        f"({percentage:>6.2f}%)"
    )

print("\nEpisode distribution:")

episode_counts = (
    working_df
    .groupby(["episode_id", "sequence_phase"])
    .size()
)

print(episode_counts)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

working_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(f"\nOutput file:")
print(OUTPUT_FILE)

print(f"\nRows written: {len(working_df):,}")

print("\nOriginal raw dataset was NOT modified.")

print("=" * 75)