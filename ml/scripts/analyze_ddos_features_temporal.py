import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CICIDS2017 - Temporal Feature Analysis
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "ddos_temporal_feature_analysis.txt"
)

print("=" * 75)
print("CICIDS2017 - DDoS TEMPORAL FEATURE ANALYSIS")
print("=" * 75)

# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("\nLoading prepared dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

df.columns = df.columns.str.strip()

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")

# ---------------------------------------------------------
# Features we specifically care about
# ---------------------------------------------------------

candidate_features = [
    "Flow Packets/s",
    "Flow Bytes/s",
    "Total Fwd Packets",
    "Total Backward Packets",
    "SYN Flag Count",
    "RST Flag Count",
    "Packet Length Mean",
    "Packet Length Std",
    "Flow Duration",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Average Packet Size"
]

features = [
    feature
    for feature in candidate_features
    if feature in df.columns
]

print("\nFeatures available for analysis:")

for feature in features:
    print(f"  - {feature}")

# ---------------------------------------------------------
# Test episodes
# ---------------------------------------------------------

test_episodes = [19, 20, 21]

# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def safe_mean(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    series = series.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return series.mean()


# ---------------------------------------------------------
# Analyze each episode
# ---------------------------------------------------------

all_results = []

for episode_id in test_episodes:

    print("\n" + "=" * 75)
    print(f"EPISODE {episode_id}")
    print("=" * 75)

    episode = df[
        df["episode_id"] == episode_id
    ].copy()

    episode = episode.sort_values(
        "sequence_position"
    )

    pre_attack = episode[
        episode["sequence_phase"] == "pre_attack"
    ].copy()

    attack = episode[
        episode["sequence_phase"] == "attack"
    ].copy()

    # -----------------------------------------------------
    # Divide pre-attack into 10 blocks of 100
    # -----------------------------------------------------

    print("\nPRE-ATTACK FEATURE PROGRESSION")

    block_results = []

    for block_id, start in enumerate(
        range(0, 1000, 100),
        start=1
    ):

        block = pre_attack.iloc[
            start:start + 100
        ]

        result = {
            "episode_id": episode_id,
            "phase": "pre_attack",
            "block": block_id,
            "start_flow": start,
            "end_flow": start + len(block) - 1
        }

        for feature in features:

            result[feature] = safe_mean(
                block[feature]
            )

        block_results.append(result)

    block_df = pd.DataFrame(
        block_results
    )

    # -----------------------------------------------------
    # Print compact progression
    # -----------------------------------------------------

    print(
        "\n"
        + block_df[
            ["block"] + features
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    all_results.extend(
        block_results
    )

    # -----------------------------------------------------
    # Compare last 100 pre-attack vs first 100 attack
    # -----------------------------------------------------

    last_pre = pre_attack.iloc[
        -100:
    ]

    first_attack = attack.iloc[
        :100
    ]

    print(
        "\n"
        + "-" * 75
    )

    print(
        "LAST 100 PRE-ATTACK vs FIRST 100 ATTACK"
    )

    print(
        "-" * 75
    )

    for feature in features:

        pre_value = safe_mean(
            last_pre[feature]
        )

        attack_value = safe_mean(
            first_attack[feature]
        )

        if (
            pd.notna(pre_value)
            and pd.notna(attack_value)
            and pre_value != 0
        ):

            percentage_change = (
                (attack_value - pre_value)
                / abs(pre_value)
            ) * 100

        else:

            percentage_change = np.nan

        print(
            f"\n{feature}"
        )

        print(
            f"  Last 100 pre-attack : "
            f"{pre_value:.6f}"
        )

        print(
            f"  First 100 attack    : "
            f"{attack_value:.6f}"
        )

        if pd.notna(percentage_change):

            print(
                f"  Change              : "
                f"{percentage_change:+.2f}%"
            )


# ---------------------------------------------------------
# Combined test-episode analysis
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("COMBINED TEST EPISODE ANALYSIS")
print("=" * 75)

test_df = df[
    df["episode_id"].isin(test_episodes)
].copy()

combined_summary = []

for feature in features:

    pre = test_df[
        test_df["sequence_phase"] == "pre_attack"
    ][feature]

    attack = test_df[
        test_df["sequence_phase"] == "attack"
    ][feature]

    pre = pd.to_numeric(
        pre,
        errors="coerce"
    ).replace(
        [np.inf, -np.inf],
        np.nan
    )

    attack = pd.to_numeric(
        attack,
        errors="coerce"
    ).replace(
        [np.inf, -np.inf],
        np.nan
    )

    pre_mean = pre.mean()
    attack_mean = attack.mean()

    if (
        pd.notna(pre_mean)
        and pre_mean != 0
    ):

        change = (
            (attack_mean - pre_mean)
            / abs(pre_mean)
        ) * 100

    else:

        change = np.nan

    combined_summary.append({
        "feature": feature,
        "pre_attack_mean": pre_mean,
        "attack_mean": attack_mean,
        "percentage_change": change
    })

combined_df = pd.DataFrame(
    combined_summary
)

print(
    combined_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)

# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - DDoS TEMPORAL FEATURE ANALYSIS\n"
    )

    report.write("=" * 75 + "\n\n")

    report.write(
        "Test episodes: 19, 20, 21\n\n"
    )

    report.write(
        "Combined test-episode comparison:\n\n"
    )

    report.write(
        combined_df.to_string(
            index=False
        )
    )

    report.write("\n\n")

    report.write(
        "Purpose:\n"
    )

    report.write(
        "Determine whether network-flow features "
        "show measurable temporal changes before "
        "DDoS attack onset.\n"
    )

print("\n" + "=" * 75)
print("ANALYSIS COMPLETE")
print("=" * 75)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print(
    "\nNo dataset was modified."
)

print("=" * 75)