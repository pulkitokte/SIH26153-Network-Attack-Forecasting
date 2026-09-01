import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_FILE = (
    BASE_DIR
    / "processed"
    / "gru_early_warning_results.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "gru_warning_horizon_analysis.txt"
)

print("=" * 75)
print("CICIDS2017 - GRU WARNING HORIZON ANALYSIS")
print("=" * 75)

print("\nLoading early-warning results...")

df = pd.read_csv(RESULT_FILE)

print(f"Rows loaded: {len(df):,}")

# ---------------------------------------------------------
# Episode-level results
# ---------------------------------------------------------

episode_df = (
    df[
        [
            "episode_id",
            "target",
            "observation_start_position",
            "observation_end_position",
            "forecast_start_position",
            "forecast_end_position",
            "probability",
            "prediction"
        ]
    ]
    .drop_duplicates()
)

# ---------------------------------------------------------
# Load actual episode-level early warning results
# ---------------------------------------------------------

# The previous evaluation produced one result per episode.
# Reconstruct first warning before actual attack onset.

results = []

for episode_id, group in df.groupby("episode_id"):

    group = group.sort_values(
        "observation_start_position"
    )

    positive_target = group[
        group["target"] == 1
    ]

    if positive_target.empty:
        continue

    attack_start = int(
        positive_target.iloc[0][
            "forecast_start_position"
        ]
    )

    warnings = group[
        (group["prediction"] == 1)
        &
        (
            group["observation_end_position"]
            < attack_start
        )
    ]

    if warnings.empty:

        results.append({
            "episode_id": episode_id,
            "attack_start": attack_start,
            "warning_position": None,
            "lead_flows": 0,
            "early_warning": 0
        })

    else:

        first_warning = warnings.iloc[0]

        warning_position = int(
            first_warning[
                "observation_end_position"
            ]
        )

        lead_flows = (
            attack_start
            - warning_position
        )

        results.append({
            "episode_id": episode_id,
            "attack_start": attack_start,
            "warning_position": warning_position,
            "lead_flows": lead_flows,
            "early_warning": 1
        })

results_df = pd.DataFrame(results)

print("\n" + "=" * 75)
print("EPISODE RESULTS")
print("=" * 75)

print()

print(
    results_df.to_string(
        index=False
    )
)

# ---------------------------------------------------------
# Warning horizon analysis
# ---------------------------------------------------------

horizons = [
    200,
    100,
    50,
    10,
    1
]

print("\n" + "=" * 75)
print("WARNING HORIZON ANALYSIS")
print("=" * 75)

horizon_results = []

total_episodes = len(
    results_df
)

for horizon in horizons:

    successful = (
        results_df["lead_flows"]
        >= horizon
    ).sum()

    rate = (
        successful
        / total_episodes
        if total_episodes > 0
        else 0
    )

    print(
        f"\nAt least {horizon:>3} flows early:"
    )

    print(
        f"  Episodes achieved : "
        f"{successful}/{total_episodes}"
    )

    print(
        f"  Success rate      : "
        f"{rate:.2%}"
    )

    horizon_results.append({
        "required_lead_flows": horizon,
        "episodes_achieved": successful,
        "total_episodes": total_episodes,
        "success_rate": rate
    })

horizon_df = pd.DataFrame(
    horizon_results
)

# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

warned = results_df[
    results_df["early_warning"] == 1
]

print("\n" + "=" * 75)
print("LEAD-TIME STATISTICS")
print("=" * 75)

if not warned.empty:

    print(
        f"\nMean lead time   : "
        f"{warned['lead_flows'].mean():.2f} flows"
    )

    print(
        f"Median lead time : "
        f"{warned['lead_flows'].median():.2f} flows"
    )

    print(
        f"Minimum lead time: "
        f"{warned['lead_flows'].min():.0f} flows"
    )

    print(
        f"Maximum lead time: "
        f"{warned['lead_flows'].max():.0f} flows"
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
        "CICIDS2017 - GRU WARNING HORIZON ANALYSIS\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        "EPISODE RESULTS\n\n"
    )

    report.write(
        results_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )

    report.write(
        "WARNING HORIZON ANALYSIS\n\n"
    )

    report.write(
        horizon_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )

    if not warned.empty:

        report.write(
            f"Mean lead time: "
            f"{warned['lead_flows'].mean():.2f} flows\n"
        )

        report.write(
            f"Median lead time: "
            f"{warned['lead_flows'].median():.2f} flows\n"
        )

        report.write(
            f"Minimum lead time: "
            f"{warned['lead_flows'].min():.0f} flows\n"
        )

        report.write(
            f"Maximum lead time: "
            f"{warned['lead_flows'].max():.0f} flows\n"
        )

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print("=" * 75)