import pandas as pd
from pathlib import Path

# =========================================================
# CICIDS2017 - FORECASTING WINDOW VALIDATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_forecasting_windows_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "forecasting_window_validation.txt"
)

print("=" * 75)
print("CICIDS2017 - FORECASTING WINDOW VALIDATION")
print("=" * 75)

print("\nLoading forecasting windows...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Total windows: {len(df):,}")
print(f"Total columns: {len(df.columns):,}")

# ---------------------------------------------------------
# Basic target distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("TARGET DISTRIBUTION")
print("=" * 75)

print(
    df["forecast_contains_ddos"]
    .value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Observation labels
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("OBSERVATION WINDOW LABELS")
print("=" * 75)

print(
    "\nObservation start labels:"
)

print(
    df["observation_label_start"]
    .value_counts()
)

print(
    "\nObservation end labels:"
)

print(
    df["observation_label_end"]
    .value_counts()
)

# ---------------------------------------------------------
# Forecast DDoS count distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FORECAST DDoS COUNT")
print("=" * 75)

print(
    df["forecast_ddos_count"]
    .value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Windows where observation already contains DDoS
# ---------------------------------------------------------

observation_already_attack = df[
    (
        (df["observation_label_start"] == "DDoS")
        |
        (df["observation_label_end"] == "DDoS")
    )
]

print("\n" + "=" * 75)
print("OBSERVATION / ATTACK OVERLAP CHECK")
print("=" * 75)

print(
    "Windows where observation starts or ends "
    f"with DDoS: {len(observation_already_attack)}"
)

# ---------------------------------------------------------
# Episode distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("WINDOWS PER EPISODE")
print("=" * 75)

episode_counts = (
    df["episode_id"]
    .value_counts()
    .sort_index()
)

print(episode_counts)

# ---------------------------------------------------------
# Train / validation / test episode allocation
# ---------------------------------------------------------

train_episodes = list(range(1, 16))
validation_episodes = list(range(16, 19))
test_episodes = list(range(19, 22))

df["dataset_split"] = df[
    "episode_id"
].apply(
    lambda x:
        "TRAIN"
        if x in train_episodes
        else (
            "VALIDATION"
            if x in validation_episodes
            else "TEST"
        )
)

print("\n" + "=" * 75)
print("DATASET SPLIT")
print("=" * 75)

print(
    df["dataset_split"]
    .value_counts()
)

print(
    "\nTarget distribution by split:"
)

print(
    pd.crosstab(
        df["dataset_split"],
        df["forecast_contains_ddos"]
    )
)

# ---------------------------------------------------------
# Episode-level target distribution
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("EPISODE-LEVEL TARGET DISTRIBUTION")
print("=" * 75)

episode_target = pd.crosstab(
    df["episode_id"],
    df["forecast_contains_ddos"]
)

print(episode_target)

# ---------------------------------------------------------
# Forecast position analysis
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FORECAST POSITION RANGE")
print("=" * 75)

for episode_id in sorted(
    df["episode_id"].unique()
):

    episode = df[
        df["episode_id"] == episode_id
    ]

    print(
        f"\nEpisode {episode_id:02d}:"
    )

    print(
        f"  Windows       : {len(episode)}"
    )

    print(
        f"  First forecast position: "
        f"{episode['forecast_start_position'].min()}"
    )

    print(
        f"  Last forecast position : "
        f"{episode['forecast_end_position'].max()}"
    )

    print(
        f"  DDoS-positive windows  : "
        f"{episode['forecast_contains_ddos'].sum()}"
    )

# ---------------------------------------------------------
# Identify earliest positive forecasting window
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("FIRST DDoS FORECAST WINDOWS")
print("=" * 75)

for episode_id in sorted(
    df["episode_id"].unique()
):

    episode = df[
        df["episode_id"] == episode_id
    ]

    positive = episode[
        episode["forecast_contains_ddos"] == 1
    ]

    if len(positive) == 0:

        print(
            f"Episode {episode_id:02d}: "
            "No positive forecast window"
        )

        continue

    first = positive.iloc[0]

    print(
        f"Episode {episode_id:02d}: "
        f"window={first['window_id']}, "
        f"observation="
        f"{first['observation_start_position']}"
        f"-"
        f"{first['observation_end_position']}, "
        f"forecast="
        f"{first['forecast_start_position']}"
        f"-"
        f"{first['forecast_end_position']}, "
        f"DDoS flows="
        f"{first['forecast_ddos_count']}"
    )

# ---------------------------------------------------------
# Save validation report
# ---------------------------------------------------------

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - FORECASTING WINDOW VALIDATION\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Total windows: {len(df):,}\n\n"
    )

    report.write(
        "Target distribution:\n"
    )

    report.write(
        str(
            df[
                "forecast_contains_ddos"
            ].value_counts()
            .sort_index()
        )
    )

    report.write("\n\n")

    report.write(
        "Observation attack overlap:\n"
    )

    report.write(
        f"{len(observation_already_attack)} windows\n\n"
    )

    report.write(
        "Windows per episode:\n"
    )

    report.write(
        str(episode_counts)
    )

    report.write("\n\n")

    report.write(
        "Target distribution by split:\n"
    )

    report.write(
        str(
            pd.crosstab(
                df["dataset_split"],
                df["forecast_contains_ddos"]
            )
        )
    )

print("\n" + "=" * 75)
print("VALIDATION COMPLETE")
print("=" * 75)

print(
    f"\nReport saved to:\n{REPORT_FILE}"
)

print(
    "\nNo dataset was modified."
)

print("=" * 75)