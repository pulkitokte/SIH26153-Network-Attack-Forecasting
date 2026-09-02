import pandas as pd
from pathlib import Path

# =========================================================
# CICIDS2017 - GENUINE EARLY-WARNING WINDOWS V2
#
# Observation : 100 flows
# Forecast    : next 100 flows
# Step        : 10 flows
#
# IMPORTANT:
# Observation must contain ONLY BENIGN traffic.
#
# Target:
# 0 = next 100 flows remain BENIGN
# 1 = DDoS starts within next 100 flows
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_forecasting_windows_v2.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "forecasting_window_v2_report.txt"
)

OBSERVATION_WINDOW = 100
FORECAST_HORIZON = 100
STEP_SIZE = 10

print("=" * 75)
print("CICIDS2017 - GENUINE EARLY-WARNING WINDOW GENERATOR V2")
print("=" * 75)

print("\nLoading prepared dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

df = df.sort_values(
    ["episode_id", "sequence_position"]
).reset_index(drop=True)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df):,}")

windows = []

episodes = sorted(
    df["episode_id"].unique()
)

print(
    f"\nEpisodes found: {len(episodes)}"
)

# ---------------------------------------------------------
# Process each episode independently
# ---------------------------------------------------------

for episode_id in episodes:

    episode = df[
        df["episode_id"] == episode_id
    ].copy()

    episode = episode.sort_values(
        "sequence_position"
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # Find first DDoS flow
    # -----------------------------------------------------

    ddos_indices = episode.index[
        episode["Label"] == "DDoS"
    ].tolist()

    if not ddos_indices:

        print(
            f"Episode {episode_id:02d}: "
            "NO DDoS FOUND"
        )

        continue

    first_ddos_index = ddos_indices[0]

    episode_windows = 0
    positive_windows = 0
    negative_windows = 0

    # -----------------------------------------------------
    # Generate windows
    #
    # Observation must finish BEFORE first DDoS.
    # Forecast can cross into DDoS.
    # -----------------------------------------------------

    max_observation_start = (
        first_ddos_index
        - OBSERVATION_WINDOW
    )

    for start in range(
        0,
        max_observation_start + 1,
        STEP_SIZE
    ):

        observation_start = start

        observation_end = (
            start + OBSERVATION_WINDOW
        )

        forecast_start = observation_end

        forecast_end = (
            forecast_start
            + FORECAST_HORIZON
        )

        if forecast_end > len(episode):

            break

        observation = episode.iloc[
            observation_start:observation_end
        ]

        forecast = episode.iloc[
            forecast_start:forecast_end
        ]

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if (
            observation["Label"] == "DDoS"
        ).any():

            continue

        # -------------------------------------------------
        # Target:
        #
        # 1 if DDoS appears in forecast horizon
        # 0 otherwise
        # -------------------------------------------------

        ddos_count = int(
            (
                forecast["Label"]
                == "DDoS"
            ).sum()
        )

        target = int(
            ddos_count > 0
        )

        windows.append({

            "window_id": len(windows),

            "episode_id": episode_id,

            "observation_start_position":
                int(
                    observation[
                        "sequence_position"
                    ].iloc[0]
                ),

            "observation_end_position":
                int(
                    observation[
                        "sequence_position"
                    ].iloc[-1]
                ),

            "forecast_start_position":
                int(
                    forecast[
                        "sequence_position"
                    ].iloc[0]
                ),

            "forecast_end_position":
                int(
                    forecast[
                        "sequence_position"
                    ].iloc[-1]
                ),

            "observation_ddos_count":
                int(
                    (
                        observation["Label"]
                        == "DDoS"
                    ).sum()
                ),

            "forecast_ddos_count":
                ddos_count,

            "forecast_benign_count":
                int(
                    (
                        forecast["Label"]
                        == "BENIGN"
                    ).sum()
                ),

            "target":
                target
        })

        episode_windows += 1

        if target == 1:
            positive_windows += 1
        else:
            negative_windows += 1

    print(
        f"Episode {episode_id:02d}: "
        f"{episode_windows} windows | "
        f"negative={negative_windows} | "
        f"positive={positive_windows}"
    )


# ---------------------------------------------------------
# Create dataframe
# ---------------------------------------------------------

windows_df = pd.DataFrame(
    windows
)

print("\n" + "=" * 75)
print("V2 DATASET SUMMARY")
print("=" * 75)

print(
    f"\nTotal windows: "
    f"{len(windows_df):,}"
)

print("\nTarget distribution:")

print(
    windows_df["target"]
    .value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Safety validation
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("SAFETY VALIDATION")
print("=" * 75)

# Observation must contain zero DDoS
bad_observation_windows = windows_df[
    windows_df["observation_ddos_count"] > 0
]

print(
    "\nObservation windows containing DDoS:"
)

print(
    len(bad_observation_windows)
)

if len(bad_observation_windows) == 0:

    print(
        "[OK] No DDoS exists inside "
        "observation windows."
    )

else:

    raise ValueError(
        "ERROR: DDoS found inside "
        "observation window."
    )

# ---------------------------------------------------------
# Positive target validation
# ---------------------------------------------------------

bad_positive_windows = windows_df[
    (
        (windows_df["target"] == 1)
        &
        (windows_df["forecast_ddos_count"] == 0)
    )
]

if len(bad_positive_windows) == 0:

    print(
        "[OK] Every positive window "
        "contains future DDoS."
    )

else:

    raise ValueError(
        "ERROR: Invalid positive target."
    )

# ---------------------------------------------------------
# Episode distribution
# ---------------------------------------------------------

print(
    "\nWindows per episode:"
)

print(
    windows_df[
        "episode_id"
    ].value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Target by episode
# ---------------------------------------------------------

print(
    "\nTarget distribution by episode:"
)

print(
    pd.crosstab(
        windows_df["episode_id"],
        windows_df["target"]
    )
)

# ---------------------------------------------------------
# Split by episode
# ---------------------------------------------------------

train_episodes = list(range(1, 16))
validation_episodes = list(range(16, 19))
test_episodes = list(range(19, 22))

windows_df["dataset_split"] = (
    windows_df["episode_id"].apply(
        lambda x:
            "TRAIN"
            if x in train_episodes
            else (
                "VALIDATION"
                if x in validation_episodes
                else "TEST"
            )
    )
)

print(
    "\nDataset split:"
)

print(
    windows_df[
        "dataset_split"
    ].value_counts()
)

print(
    "\nTarget distribution by split:"
)

print(
    pd.crosstab(
        windows_df["dataset_split"],
        windows_df["target"]
    )
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

windows_df.to_csv(
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
        "CICIDS2017 - GENUINE EARLY-WARNING WINDOWS V2\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Observation window: "
        f"{OBSERVATION_WINDOW} flows\n"
    )

    report.write(
        f"Forecast horizon: "
        f"{FORECAST_HORIZON} flows\n"
    )

    report.write(
        f"Step size: "
        f"{STEP_SIZE} flows\n\n"
    )

    report.write(
        "Target definition:\n"
    )

    report.write(
        "0 = no DDoS in next 100 flows\n"
    )

    report.write(
        "1 = DDoS appears in next 100 flows\n\n"
    )

    report.write(
        f"Total windows: "
        f"{len(windows_df):,}\n\n"
    )

    report.write(
        "Target distribution:\n"
    )

    report.write(
        str(
            windows_df[
                "target"
            ].value_counts()
            .sort_index()
        )
    )

    report.write("\n\n")

    report.write(
        "Target distribution by split:\n"
    )

    report.write(
        str(
            pd.crosstab(
                windows_df["dataset_split"],
                windows_df["target"]
            )
        )
    )

    report.write("\n\n")

    report.write(
        "Observation DDoS leakage check:\n"
    )

    report.write(
        f"Bad windows: "
        f"{len(bad_observation_windows)}\n"
    )

print("\n" + "=" * 75)
print("SUCCESS")
print("=" * 75)

print(
    f"\nOutput:\n{OUTPUT_FILE}"
)

print(
    f"\nReport:\n{REPORT_FILE}"
)

print(
    "\nOriginal dataset was NOT modified."
)

print("=" * 75)