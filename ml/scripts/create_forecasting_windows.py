import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# CICIDS2017 - TEMPORAL FORECASTING WINDOW GENERATOR
#
# Observation window : 100 flows
# Forecast horizon    : next 100 flows
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

OUTPUT_DIR = BASE_DIR / "processed"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "ddos_forecasting_windows_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "forecasting_window_report.txt"
)

OBSERVATION_WINDOW = 100
FORECAST_HORIZON = 100

TEST_EPISODES = [19, 20, 21]

print("=" * 75)
print("CICIDS2017 - TEMPORAL FORECASTING WINDOW GENERATOR")
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
print(f"Columns : {len(df.columns):,}")

# ---------------------------------------------------------
# IMPORTANT:
# We only use actual feature columns.
# Metadata and labels are not used as model inputs.
# ---------------------------------------------------------

metadata_columns = [
    "Label",
    "episode_id",
    "sequence_phase",
    "sequence_position"
]

feature_columns = [
    c for c in df.columns
    if c not in metadata_columns
]

print(
    f"\nFeature columns available: "
    f"{len(feature_columns)}"
)

# ---------------------------------------------------------
# Create one forecasting example
# from each episode.
#
# For each starting point:
#
# Past 100 flows
#       ↓
# Future 100 flows
#
# Target = 1 if ANY future flow is DDoS
#         0 otherwise
# ---------------------------------------------------------

windows = []

episodes = sorted(
    df["episode_id"].unique()
)

print(
    f"\nEpisodes found: {len(episodes)}"
)

for episode_id in episodes:

    episode = df[
        df["episode_id"] == episode_id
    ].copy()

    episode = episode.sort_values(
        "sequence_position"
    ).reset_index(drop=True)

    total_rows = len(episode)

    episode_windows = 0

    for start in range(
        0,
        total_rows
        - OBSERVATION_WINDOW
        - FORECAST_HORIZON
        + 1,
        OBSERVATION_WINDOW
    ):

        observation_start = start

        observation_end = (
            start + OBSERVATION_WINDOW
        )

        future_start = observation_end

        future_end = (
            future_start
            + FORECAST_HORIZON
        )

        observation = episode.iloc[
            observation_start:observation_end
        ]

        future = episode.iloc[
            future_start:future_end
        ]

        if len(observation) != OBSERVATION_WINDOW:
            continue

        if len(future) != FORECAST_HORIZON:
            continue

        # -------------------------------------------------
        # Forecast target
        # -------------------------------------------------

        future_has_ddos = (
            future["Label"] == "DDoS"
        ).any()

        target = int(
            future_has_ddos
        )

        # -------------------------------------------------
        # Record only metadata here.
        #
        # Actual feature sequences remain represented
        # by their episode + positions and will be
        # constructed separately for the neural model.
        # -------------------------------------------------

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
                    future[
                        "sequence_position"
                    ].iloc[0]
                ),

            "forecast_end_position":
                int(
                    future[
                        "sequence_position"
                    ].iloc[-1]
                ),

            "observation_label_start":
                observation[
                    "Label"
                ].iloc[0],

            "observation_label_end":
                observation[
                    "Label"
                ].iloc[-1],

            "forecast_contains_ddos":
                target,

            "forecast_ddos_count":
                int(
                    (
                        future["Label"]
                        == "DDoS"
                    ).sum()
                ),

            "forecast_benign_count":
                int(
                    (
                        future["Label"]
                        == "BENIGN"
                    ).sum()
                )
        })

        episode_windows += 1

    print(
        f"Episode {episode_id:02d}: "
        f"{episode_windows} windows"
    )


# ---------------------------------------------------------
# Convert to dataframe
# ---------------------------------------------------------

windows_df = pd.DataFrame(
    windows
)

print("\n" + "=" * 75)
print("WINDOW DATASET SUMMARY")
print("=" * 75)

print(
    f"\nTotal windows: "
    f"{len(windows_df):,}"
)

print(
    "\nForecast target distribution:"
)

print(
    windows_df[
        "forecast_contains_ddos"
    ].value_counts()
    .sort_index()
)

# ---------------------------------------------------------
# Check target meaning
# ---------------------------------------------------------

print(
    "\nTarget meaning:"
)

print(
    "0 = no DDoS in next 100 flows"
)

print(
    "1 = DDoS appears in next 100 flows"
)

# ---------------------------------------------------------
# Check for leakage
# ---------------------------------------------------------

print(
    "\n" + "=" * 75
)

print(
    "LEAKAGE CHECK"
)

print(
    "=" * 75
)

leakage_found = False

for _, row in windows_df.iterrows():

    observation_end = (
        row[
            "observation_end_position"
        ]
    )

    forecast_start = (
        row[
            "forecast_start_position"
        ]
    )

    if forecast_start <= observation_end:

        leakage_found = True

        print(
            "LEAKAGE FOUND:",
            row["window_id"]
        )

        break

if not leakage_found:

    print(
        "[OK] Observation and forecast "
        "windows do not overlap."
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
        "CICIDS2017 - TEMPORAL FORECASTING WINDOW REPORT\n"
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
        f"{FORECAST_HORIZON} flows\n\n"
    )

    report.write(
        f"Total windows: "
        f"{len(windows_df):,}\n\n"
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
        "Target distribution:\n"
    )

    report.write(
        str(
            windows_df[
                "forecast_contains_ddos"
            ].value_counts()
        )
    )

    report.write("\n\n")

    report.write(
        "Episode distribution:\n"
    )

    report.write(
        str(
            windows_df[
                "episode_id"
            ].value_counts()
            .sort_index()
        )
    )

print(
    "\n" + "=" * 75
)

print(
    "SUCCESS"
)

print(
    "=" * 75
)

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