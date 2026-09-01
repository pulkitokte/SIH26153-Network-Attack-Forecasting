import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CICIDS2017 - Isolation Forest Score Analysis
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"
REPORT_DIR = BASE_DIR / "reports"

TRAIN_FILE = PROCESSED_DIR / "ddos_train_if_scored.csv"
VAL_FILE = PROCESSED_DIR / "ddos_validation_if_scored.csv"
TEST_FILE = PROCESSED_DIR / "ddos_test_if_scored.csv"

REPORT_FILE = REPORT_DIR / "isolation_forest_score_analysis.txt"

print("=" * 75)
print("CICIDS2017 - ISOLATION FOREST SCORE ANALYSIS")
print("=" * 75)

# ---------------------------------------------------------
# Load
# ---------------------------------------------------------

print("\nLoading scored datasets...")

train = pd.read_csv(TRAIN_FILE, low_memory=False)
val = pd.read_csv(VAL_FILE, low_memory=False)
test = pd.read_csv(TEST_FILE, low_memory=False)

# ---------------------------------------------------------
# Basic score statistics
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("ANOMALY SCORE STATISTICS")
print("=" * 75)

for name, df in [
    ("TRAIN", train),
    ("VALIDATION", val),
    ("TEST", test)
]:

    print(f"\n{name}")

    for label in ["BENIGN", "DDoS"]:

        subset = df[df["Label"] == label]

        scores = subset["if_anomaly_score"]

        print(
            f"\n  {label}"
        )

        print(
            f"    Count  : {len(scores):,}"
        )

        print(
            f"    Mean   : {scores.mean():.6f}"
        )

        print(
            f"    Median : {scores.median():.6f}"
        )

        print(
            f"    Std    : {scores.std():.6f}"
        )

        print(
            f"    Min    : {scores.min():.6f}"
        )

        print(
            f"    Max    : {scores.max():.6f}"
        )

# ---------------------------------------------------------
# Pre-attack vs attack
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("PRE-ATTACK VS ATTACK")
print("=" * 75)

for name, df in [
    ("TRAIN", train),
    ("VALIDATION", val),
    ("TEST", test)
]:

    print(f"\n{name}")

    for phase in ["pre_attack", "attack"]:

        subset = df[
            df["sequence_phase"] == phase
        ]

        scores = subset["if_anomaly_score"]

        print(
            f"  {phase:<12} "
            f"mean={scores.mean():.6f} "
            f"median={scores.median():.6f} "
            f"std={scores.std():.6f}"
        )

# ---------------------------------------------------------
# Episode-level analysis
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE-LEVEL ANALYSIS")
print("=" * 75)

episode_table = []

for episode_id in sorted(
    test["episode_id"].unique()
):

    episode = test[
        test["episode_id"] == episode_id
    ]

    pre = episode[
        episode["sequence_phase"] == "pre_attack"
    ]

    attack = episode[
        episode["sequence_phase"] == "attack"
    ]

    pre_mean = pre[
        "if_anomaly_score"
    ].mean()

    attack_mean = attack[
        "if_anomaly_score"
    ].mean()

    pre_anomaly_rate = (
        pre["if_anomaly_flag"].mean()
        * 100
    )

    attack_anomaly_rate = (
        attack["if_anomaly_flag"].mean()
        * 100
    )

    episode_table.append({
        "episode_id": episode_id,
        "pre_attack_mean": pre_mean,
        "attack_mean": attack_mean,
        "score_change": attack_mean - pre_mean,
        "pre_attack_anomaly_pct": pre_anomaly_rate,
        "attack_anomaly_pct": attack_anomaly_rate
    })

episode_df = pd.DataFrame(
    episode_table
)

print(
    episode_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)

# ---------------------------------------------------------
# Threshold analysis
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("ANOMALY THRESHOLD ANALYSIS")
print("=" * 75)

test_scores = test[
    "if_anomaly_score"
]

thresholds = np.percentile(
    test_scores,
    [90, 95, 97, 98, 99]
)

for threshold in thresholds:

    predictions = (
        test_scores >= threshold
    )

    benign = test[
        test["Label"] == "BENIGN"
    ]

    ddos = test[
        test["Label"] == "DDoS"
    ]

    benign_detection = (
        (
            benign["if_anomaly_score"]
            >= threshold
        ).mean()
        * 100
    )

    ddos_detection = (
        (
            ddos["if_anomaly_score"]
            >= threshold
        ).mean()
        * 100
    )

    print(
        f"\nThreshold: {threshold:.6f}"
    )

    print(
        f"  BENIGN flagged : "
        f"{benign_detection:.2f}%"
    )

    print(
        f"  DDoS flagged   : "
        f"{ddos_detection:.2f}%"
    )

# ---------------------------------------------------------
# Pre-attack progression
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("PRE-ATTACK PROGRESSION")
print("=" * 75)

# Look at the 1000 pre-attack flows
# in blocks of 100.

for episode_id in sorted(
    test["episode_id"].unique()
):

    episode = test[
        test["episode_id"] == episode_id
    ]

    pre = episode[
        episode["sequence_phase"] == "pre_attack"
    ].copy()

    pre = pre.sort_values(
        "sequence_position"
    )

    print(
        f"\nEpisode {episode_id}"
    )

    for start in range(
        0,
        len(pre),
        100
    ):

        block = pre.iloc[
            start:start + 100
        ]

        if len(block) == 0:
            continue

        mean_score = block[
            "if_anomaly_score"
        ].mean()

        anomaly_pct = (
            block[
                "if_anomaly_flag"
            ].mean()
            * 100
        )

        print(
            f"  flows "
            f"{start:04d}-{start + len(block) - 1:04d}: "
            f"score={mean_score:.6f}, "
            f"anomaly={anomaly_pct:.2f}%"
        )

# ---------------------------------------------------------
# Write report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "CICIDS2017 - ISOLATION FOREST SCORE ANALYSIS\n"
    )

    f.write("=" * 75 + "\n\n")

    f.write(
        "Episode-level test analysis\n\n"
    )

    f.write(
        episode_df.to_string(
            index=False
        )
    )

    f.write("\n\n")

    f.write(
        "Interpretation should focus on whether "
        "anomaly scores increase before attack onset "
        "and whether attack flows receive higher scores "
        "than pre-attack flows.\n"
    )

print("\n" + "=" * 75)
print("ANALYSIS COMPLETE")
print("=" * 75)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print("=" * 75)