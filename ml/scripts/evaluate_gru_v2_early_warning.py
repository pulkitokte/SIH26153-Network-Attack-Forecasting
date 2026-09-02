import numpy as np
import pandas as pd
from pathlib import Path

import torch
import torch.nn as nn


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_FILE = MODEL_DIR / "ddos_gru_forecaster_v2.pt"

X_TEST_FILE = DATA_DIR / "X_test.npy"
METADATA_FILE = DATA_DIR / "sequence_metadata.csv"


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


print("=" * 75)
print("CICIDS2017 - GRU V2 EARLY-WARNING EVALUATION")
print("=" * 75)

print(f"\nDevice: {DEVICE}")


# ============================================================
# MODEL
# ============================================================

class GRUForecasterV2(nn.Module):

    def __init__(
        self,
        input_size,
        hidden_size=96,
        num_layers=2,
        dropout=0.30
    ):

        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.norm = nn.LayerNorm(
            hidden_size
        )

        self.classifier = nn.Sequential(
            nn.Linear(
                hidden_size,
                48
            ),

            nn.ReLU(),

            nn.Dropout(
                dropout
            ),

            nn.Linear(
                48,
                1
            )
        )


    def forward(self, x):

        output, _ = self.gru(x)

        last_state = output[:, -1, :]

        last_state = self.norm(
            last_state
        )

        logits = self.classifier(
            last_state
        )

        return logits.squeeze(1)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading trained GRU V2...")

checkpoint = torch.load(
    MODEL_FILE,
    map_location=DEVICE
)

input_size = checkpoint["input_size"]
hidden_size = checkpoint["hidden_size"]
num_layers = checkpoint["num_layers"]
dropout = checkpoint["dropout"]
threshold = checkpoint["threshold"]


model = GRUForecasterV2(
    input_size=input_size,
    hidden_size=hidden_size,
    num_layers=num_layers,
    dropout=dropout
).to(DEVICE)


model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


print("[OK] GRU V2 loaded.")

print(
    f"Decision threshold: {threshold:.2f}"
)


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test sequences...")

X_test = np.load(
    X_TEST_FILE
).astype(np.float32)

print(
    f"Test sequences: {X_test.shape}"
)


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating GRU V2 predictions...")

X_tensor = torch.tensor(
    X_test,
    dtype=torch.float32
).to(DEVICE)


with torch.no_grad():

    logits = model(
        X_tensor
    )

    probabilities = torch.sigmoid(
        logits
    ).cpu().numpy()


predictions = (
    probabilities >= threshold
).astype(int)


# ============================================================
# LOAD METADATA
# ============================================================

print("\nLoading sequence metadata...")

metadata = pd.read_csv(
    METADATA_FILE
)

# sequence_metadata.csv contains metadata for all
# generated sequences in the same order as the tensors.
# X_test.npy corresponds to the final 273 TEST sequences.

test_metadata = metadata.tail(
    len(probabilities)
).reset_index(drop=True)


if len(test_metadata) != len(
    probabilities
):

    raise ValueError(
        "Metadata/test sequence count mismatch."
    )


test_metadata["probability"] = (
    probabilities
)

test_metadata["prediction"] = (
    predictions
)


# ============================================================
# EPISODE-LEVEL ANALYSIS
# ============================================================

print("\n" + "=" * 75)
print("EPISODE-LEVEL EARLY WARNING V2")
print("=" * 75)


episode_results = []


for episode_id, group in test_metadata.groupby(
    "episode_id"
):

    group = group.sort_values(
        "observation_start_position"
    ).reset_index(drop=True)


    # First forecast window that contains DDoS
    positive_windows = group[
        group["target"] == 1
    ]


    if positive_windows.empty:

        print(
            f"\nEpisode {episode_id}: "
            "No positive forecast window found."
        )

        continue


    attack_start = int(
        positive_windows.iloc[0][
            "forecast_start_position"
        ]
    )


    # Only warnings BEFORE attack
    warnings = group[
        (group["prediction"] == 1)
        &
        (
            group["observation_end_position"]
            < attack_start
        )
    ]


    if warnings.empty:

        print(
            f"\nEpisode {episode_id}: "
            "NO EARLY WARNING"
        )

        episode_results.append({
            "episode_id": episode_id,
            "attack_start": attack_start,
            "warning_position": None,
            "lead_flows": 0,
            "warning_probability": 0.0,
            "warned": 0
        })

        continue


    first_warning = warnings.iloc[0]


    warning_position = int(
        first_warning[
            "observation_end_position"
        ]
    )


    lead_time = (
        attack_start
        - warning_position
    )


    probability = float(
        first_warning[
            "probability"
        ]
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
        f"  Lead time              : "
        f"{lead_time} flows"
    )

    print(
        f"  Warning probability    : "
        f"{probability:.4f}"
    )


    episode_results.append({
        "episode_id": episode_id,
        "attack_start": attack_start,
        "warning_position": warning_position,
        "lead_flows": lead_time,
        "warning_probability": probability,
        "warned": 1
    })


# ============================================================
# SUMMARY
# ============================================================

results_df = pd.DataFrame(
    episode_results
)


print("\n" + "=" * 75)
print("V2 EARLY-WARNING SUMMARY")
print("=" * 75)


total_episodes = len(
    results_df
)

warned_episodes = int(
    results_df["warned"].sum()
)


warning_rate = (
    warned_episodes / total_episodes
    if total_episodes > 0
    else 0
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


warned = results_df[
    results_df["warned"] == 1
]


if not warned.empty:

    print(
        f"\nMean lead time         : "
        f"{warned['lead_flows'].mean():.2f} flows"
    )

    print(
        f"Median lead time       : "
        f"{warned['lead_flows'].median():.2f} flows"
    )

    print(
        f"Minimum lead time      : "
        f"{warned['lead_flows'].min():.0f} flows"
    )

    print(
        f"Maximum lead time      : "
        f"{warned['lead_flows'].max():.0f} flows"
    )


# ============================================================
# WARNING HORIZONS
# ============================================================

print("\n" + "=" * 75)
print("V2 WARNING HORIZON ANALYSIS")
print("=" * 75)


for horizon in [
    200,
    100,
    50,
    10,
    1
]:

    achieved = int(
        (
            results_df["lead_flows"]
            >= horizon
        ).sum()
    )


    rate = (
        achieved / total_episodes
        if total_episodes > 0
        else 0
    )


    print(
        f"\nAt least {horizon:>3} flows early:"
    )

    print(
        f"  Episodes achieved : "
        f"{achieved}/{total_episodes}"
    )

    print(
        f"  Success rate      : "
        f"{rate:.2%}"
    )


# ============================================================
# SAVE REPORT
# ============================================================

REPORT_FILE = (
    REPORT_DIR
    / "gru_v2_early_warning_report.txt"
)


with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "CICIDS2017 - GRU V2 EARLY-WARNING EVALUATION\n"
    )

    report.write(
        "=" * 75 + "\n\n"
    )

    report.write(
        f"Decision threshold: {threshold:.4f}\n\n"
    )

    report.write(
        "EPISODE RESULTS\n"
    )

    report.write(
        "-" * 75 + "\n"
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
        f"Early-warning rate: "
        f"{warning_rate:.4%}\n"
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