import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from pathlib import Path


# =========================================================
# CICIDS2017 - GRU EARLY-WARNING EVALUATION
#
# Purpose:
# Measure HOW EARLY the GRU predicts an upcoming DDoS.
#
# Observation:
#   100 historical flows
#
# Forecast:
#   next 100 flows
#
# We evaluate predictions chronologically inside each
# held-out test episode.
# =========================================================


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_FILE = (
    MODEL_DIR /
    "ddos_gru_forecaster.pt"
)

WINDOW_FILE = (
    DATA_DIR /
    "ddos_forecasting_windows_v2.csv"
)

METADATA_FILE = (
    DATA_DIR /
    "sequence_metadata.csv"
)

X_TEST_FILE = (
    DATA_DIR /
    "X_test.npy"
)


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

THRESHOLD = 0.65

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)


print("=" * 75)
print("CICIDS2017 - GRU EARLY-WARNING EVALUATION")
print("=" * 75)

print(
    f"\nDevice: {DEVICE}"
)

print(
    f"Decision threshold: {THRESHOLD}"
)


# ---------------------------------------------------------
# GRU model
# ---------------------------------------------------------

class GRUForecaster(nn.Module):

    def __init__(
        self,
        input_size=68,
        hidden_size=64,
        num_layers=2,
        dropout=0.25
    ):

        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.classifier = nn.Sequential(
            nn.Linear(
                hidden_size,
                32
            ),
            nn.ReLU(),
            nn.Dropout(
                dropout
            ),
            nn.Linear(
                32,
                1
            )
        )

    def forward(self, x):

        output, _ = self.gru(x)

        final_state = (
            output[:, -1, :]
        )

        logits = self.classifier(
            final_state
        ).squeeze(1)

        return logits


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

print("\nLoading trained GRU...")

checkpoint = torch.load(
    MODEL_FILE,
    map_location=DEVICE
)

model = GRUForecaster().to(DEVICE)

model.load_state_dict(
    checkpoint[
        "model_state_dict"
    ]
)

model.eval()

print(
    "[OK] GRU model loaded."
)


# ---------------------------------------------------------
# Load test sequences
# ---------------------------------------------------------

print(
    "\nLoading test sequences..."
)

X_test = np.load(
    X_TEST_FILE
)

print(
    f"Test sequences: {X_test.shape}"
)


# ---------------------------------------------------------
# Generate probabilities
# ---------------------------------------------------------

print(
    "\nGenerating GRU predictions..."
)

X_tensor = torch.tensor(
    X_test,
    dtype=torch.float32
).to(DEVICE)

with torch.no_grad():

    logits = model(
        X_tensor
    )

    probabilities = (
        torch.sigmoid(
            logits
        )
        .cpu()
        .numpy()
    )


predictions = (
    probabilities >= THRESHOLD
).astype(int)


# ---------------------------------------------------------
# Load metadata
# ---------------------------------------------------------

print(
    "\nLoading sequence metadata..."
)

metadata = pd.read_csv(
    METADATA_FILE
)

test_metadata = metadata[
    metadata["episode_id"]
    .between(19, 21)
].copy()

test_metadata = (
    test_metadata
    .sort_values(
        ["episode_id",
         "observation_start_position"]
    )
    .reset_index(drop=True)
)


if len(test_metadata) != len(
    probabilities
):

    raise ValueError(
        "Test metadata count does not "
        "match X_test count."
    )


test_metadata[
    "probability"
] = probabilities

test_metadata[
    "prediction"
] = predictions


# ---------------------------------------------------------
# Determine actual DDoS onset
#
# For each episode, the first attack begins at
# the forecast position corresponding to the first
# positive forecasting window.
# ---------------------------------------------------------

print(
    "\n" + "=" * 75
)

print(
    "EPISODE-LEVEL EARLY WARNING"
)

print(
    "=" * 75
)


episode_results = []


for episode_id in sorted(
    test_metadata[
        "episode_id"
    ].unique()
):

    episode = test_metadata[
        test_metadata[
            "episode_id"
        ] == episode_id
    ].copy()

    episode = episode.sort_values(
        "observation_start_position"
    )


    # First actual DDoS forecast target
    positive_windows = episode[
        episode["target"] == 1
    ]


    if positive_windows.empty:

        print(
            f"\nEpisode {episode_id}: "
            "No positive target."
        )

        continue


    first_positive = (
        positive_windows.iloc[0]
    )


    attack_start = int(
        first_positive[
            "forecast_start_position"
        ]
    )


    # -----------------------------------------------------
    # Predictions BEFORE actual attack
    # -----------------------------------------------------

    pre_attack_predictions = (
        episode[
            episode[
                "observation_end_position"
            ] < attack_start
        ]
    )


    positive_predictions = (
        pre_attack_predictions[
            pre_attack_predictions[
                "prediction"
            ] == 1
        ]
    )


    if positive_predictions.empty:

        print(
            f"\nEpisode {episode_id}: "
            f"No early warning before "
            f"attack start {attack_start}."
        )

        episode_results.append({

            "episode_id":
                episode_id,

            "attack_start":
                attack_start,

            "early_warning":
                0,

            "warning_position":
                None,

            "lead_flows":
                0

        })

        continue


    # First chronological positive prediction

    first_warning = (
        positive_predictions.iloc[0]
    )


    warning_position = int(
        first_warning[
            "observation_end_position"
        ]
    )


    # Number of flows between the end of
    # observation and attack onset

    lead_flows = (
        attack_start
        - warning_position
    )


    print(
        f"\nEpisode {episode_id}:"
    )

    print(
        f"  Attack starts at flow : "
        f"{attack_start}"
    )

    print(
        f"  First warning at flow  : "
        f"{warning_position}"
    )

    print(
        f"  Lead time               : "
        f"{lead_flows} flows"
    )

    print(
        f"  Warning probability     : "
        f"{first_warning['probability']:.4f}"
    )


    episode_results.append({

        "episode_id":
            episode_id,

        "attack_start":
            attack_start,

        "early_warning":
            1,

        "warning_position":
            warning_position,

        "lead_flows":
            lead_flows,

        "warning_probability":
            float(
                first_warning[
                    "probability"
                ]
            )

    })


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

results = pd.DataFrame(
    episode_results
)


print(
    "\n" + "=" * 75
)

print(
    "EARLY-WARNING SUMMARY"
)

print(
    "=" * 75
)


if not results.empty:

    warnings = results[
        results["early_warning"] == 1
    ]


    total_episodes = len(
        results
    )

    warned_episodes = len(
        warnings
    )


    warning_rate = (
        warned_episodes
        / total_episodes
    )


    print(
        f"\nTest episodes          : "
        f"{total_episodes}"
    )

    print(
        f"Episodes warned        : "
        f"{warned_episodes}"
    )

    print(
        f"Early-warning rate     : "
        f"{warning_rate:.2%}"
    )


    if not warnings.empty:

        print(
            f"\nMean lead time         : "
            f"{warnings['lead_flows'].mean():.2f} flows"
        )

        print(
            f"Median lead time       : "
            f"{warnings['lead_flows'].median():.2f} flows"
        )

        print(
            f"Minimum lead time      : "
            f"{warnings['lead_flows'].min():.0f} flows"
        )

        print(
            f"Maximum lead time      : "
            f"{warnings['lead_flows'].max():.0f} flows"
        )


# ---------------------------------------------------------
# Save detailed results
# ---------------------------------------------------------

OUTPUT_FILE = (
    DATA_DIR /
    "gru_early_warning_results.csv"
)

REPORT_FILE = (
    REPORT_DIR /
    "gru_early_warning_report.txt"
)


test_metadata.to_csv(
    OUTPUT_FILE,
    index=False
)


with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - GRU EARLY-WARNING EVALUATION\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Threshold: {THRESHOLD}\n"
    )

    report.write(
        f"Test episodes: "
        f"{len(results)}\n"
    )

    report.write(
        f"Episodes warned: "
        f"{len(results[results['early_warning'] == 1])}\n"
    )

    if not warnings.empty:

        report.write(
            f"Mean lead flows: "
            f"{warnings['lead_flows'].mean():.2f}\n"
        )

        report.write(
            f"Median lead flows: "
            f"{warnings['lead_flows'].median():.2f}\n"
        )

        report.write(
            f"Minimum lead flows: "
            f"{warnings['lead_flows'].min():.0f}\n"
        )

        report.write(
            f"Maximum lead flows: "
            f"{warnings['lead_flows'].max():.0f}\n"
        )

    report.write(
        "\n\nEpisode details:\n"
    )

    report.write(
        results.to_string(
            index=False
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
    f"\nDetailed predictions saved to:\n"
    f"{OUTPUT_FILE}"
)

print(
    f"\nReport saved to:\n"
    f"{REPORT_FILE}"
)

print("=" * 75)