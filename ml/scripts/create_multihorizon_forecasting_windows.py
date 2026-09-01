import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_multihorizon_windows_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "multihorizon_forecasting_report.txt"
)


# ============================================================
# CONFIGURATION
# ============================================================

OBSERVATION_LENGTH = 100

FORECAST_HORIZONS = [
    50,
    100,
    200,
    500
]


print("=" * 75)
print("CICIDS2017 - MULTI-HORIZON FORECASTING WINDOW GENERATOR")
print("=" * 75)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading prepared feature dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df):,}")


required_columns = [
    "Label",
    "episode_id",
    "sequence_position"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column missing: {column}"
        )


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    ["episode_id", "sequence_position"]
).reset_index(drop=True)


# ============================================================
# GENERATE WINDOWS
# ============================================================

print("\nGenerating multi-horizon windows...")

windows = []

window_id = 0


for episode_id, episode in df.groupby(
    "episode_id",
    sort=True
):

    episode = episode.sort_values(
        "sequence_position"
    ).reset_index(drop=True)


    episode_length = len(episode)


    print(
        f"\nEpisode {episode_id:02d}: "
        f"{episode_length:,} flows"
    )


    episode_windows = 0


    # We require the complete 500-flow horizon.
    max_start = (
        episode_length
        - OBSERVATION_LENGTH
        - max(FORECAST_HORIZONS)
        + 1
    )


    for start in range(
        max_start
    ):

        observation_start = start

        observation_end = (
            start
            + OBSERVATION_LENGTH
            - 1
        )


        # ----------------------------------------------------
        # Safety: observation window must contain NO DDoS
        # ----------------------------------------------------

        observation_labels = (
            episode.iloc[
                observation_start:
                observation_end + 1
            ]["Label"]
        )


        if (
            observation_labels
            .eq("DDoS")
            .any()
        ):

            continue


        row = {

            "window_id": window_id,

            "episode_id": int(
                episode_id
            ),

            "observation_start_position":
                int(
                    episode.iloc[
                        observation_start
                    ]["sequence_position"]
                ),

            "observation_end_position":
                int(
                    episode.iloc[
                        observation_end
                    ]["sequence_position"]
                ),

            "observation_length":
                OBSERVATION_LENGTH
        }


        # ----------------------------------------------------
        # Future horizons
        # ----------------------------------------------------

        for horizon in FORECAST_HORIZONS:

            forecast_start = (
                observation_end + 1
            )

            forecast_end = (
                forecast_start
                + horizon
                - 1
            )


            future_labels = (
                episode.iloc[
                    forecast_start:
                    forecast_end + 1
                ]["Label"]
            )


            ddos_count = int(
                (
                    future_labels
                    == "DDoS"
                ).sum()
            )


            row[
                f"ddos_count_next_{horizon}"
            ] = ddos_count


            row[
                f"ddos_next_{horizon}"
            ] = int(
                ddos_count > 0
            )


            row[
                f"ddos_ratio_next_{horizon}"
            ] = (
                ddos_count
                / horizon
            )


        windows.append(row)

        window_id += 1
        episode_windows += 1


    print(
        f"  Windows created: "
        f"{episode_windows}"
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

windows_df = pd.DataFrame(
    windows
)


if windows_df.empty:

    raise ValueError(
        "No forecasting windows were generated."
    )


# ============================================================
# DATASET SPLIT BY EPISODE
# ============================================================

TRAIN_EPISODES = set(
    range(1, 16)
)

VALIDATION_EPISODES = set(
    range(16, 19)
)

TEST_EPISODES = set(
    range(19, 22)
)


def assign_split(episode_id):

    if episode_id in TRAIN_EPISODES:
        return "TRAIN"

    if episode_id in VALIDATION_EPISODES:
        return "VALIDATION"

    if episode_id in TEST_EPISODES:
        return "TEST"

    return "UNKNOWN"


windows_df["dataset_split"] = (
    windows_df["episode_id"]
    .apply(assign_split)
)


# ============================================================
# VALIDATE SPLIT
# ============================================================

if (
    windows_df["dataset_split"]
    == "UNKNOWN"
).any():

    raise ValueError(
        "Some episodes could not be assigned "
        "to a dataset split."
    )


# ============================================================
# SAFETY CHECK
# ============================================================

print("\n" + "=" * 75)
print("SAFETY VALIDATION")
print("=" * 75)


# Check observations contain no DDoS
print(
    "\nObservation windows containing DDoS:"
)

observation_ddos = 0


for _, row in windows_df.iterrows():

    episode = df[
        df["episode_id"]
        == row["episode_id"]
    ]


    obs = episode[
        (
            episode["sequence_position"]
            >= row[
                "observation_start_position"
            ]
        )
        &
        (
            episode["sequence_position"]
            <= row[
                "observation_end_position"
            ]
        )
    ]


    observation_ddos += int(
        (
            obs["Label"]
            == "DDoS"
        ).any()
    )


print(
    observation_ddos
)


if observation_ddos == 0:

    print(
        "[OK] No DDoS exists inside "
        "observation windows."
    )

else:

    raise ValueError(
        "DDoS found inside observation windows."
    )


# ============================================================
# HORIZON SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("HORIZON TARGET DISTRIBUTION")
print("=" * 75)


for horizon in FORECAST_HORIZONS:

    column = (
        f"ddos_next_{horizon}"
    )

    counts = (
        windows_df[column]
        .value_counts()
        .sort_index()
    )


    print(
        f"\nNext {horizon} flows:"
    )

    print(
        f"  No DDoS : "
        f"{counts.get(0, 0):,}"
    )

    print(
        f"  DDoS    : "
        f"{counts.get(1, 0):,}"
    )


# ============================================================
# SPLIT DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("DATASET SPLIT")
print("=" * 75)

print(
    windows_df[
        "dataset_split"
    ].value_counts()
)


# ============================================================
# EPISODE DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("WINDOWS PER EPISODE")
print("=" * 75)

print(
    windows_df[
        "episode_id"
    ].value_counts()
    .sort_index()
)


# ============================================================
# SAVE
# ============================================================

windows_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - MULTI-HORIZON FORECASTING\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Observation length: "
        f"{OBSERVATION_LENGTH}\n"
    )

    report.write(
        f"Forecast horizons: "
        f"{FORECAST_HORIZONS}\n\n"
    )

    report.write(
        f"Total windows: "
        f"{len(windows_df):,}\n\n"
    )


    report.write(
        "HORIZON DISTRIBUTION\n"
    )

    report.write(
        "-" * 75 + "\n"
    )


    for horizon in FORECAST_HORIZONS:

        column = (
            f"ddos_next_{horizon}"
        )

        counts = (
            windows_df[column]
            .value_counts()
            .sort_index()
        )


        report.write(
            f"\nNext {horizon} flows:\n"
        )

        report.write(
            f"  No DDoS: "
            f"{counts.get(0, 0):,}\n"
        )

        report.write(
            f"  DDoS: "
            f"{counts.get(1, 0):,}\n"
        )


    report.write(
        "\n\nDATASET SPLIT\n"
    )

    report.write(
        str(
            windows_df[
                "dataset_split"
            ].value_counts()
        )
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
    "\nOriginal prepared dataset was NOT modified."
)

print("=" * 75)