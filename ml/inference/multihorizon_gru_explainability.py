from pathlib import Path
from typing import Any

import numpy as np

from ml.inference.multihorizon_gru_inference import MultiHorizonGRUInference


FEATURE_NAMES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Max",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Fwd Packet Length Std",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Fwd IAT Mean",
    "Fwd IAT Std",
    "Fwd IAT Max",
    "Fwd IAT Min",
    "Bwd IAT Total",
    "Bwd IAT Mean",
    "Bwd IAT Std",
    "Bwd IAT Max",
    "Bwd IAT Min",
    "Fwd PSH Flags",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "ECE Flag Count",
    "Down/Up Ratio",
    "Average Packet Size",
    "Avg Fwd Segment Size",
    "Avg Bwd Segment Size",
    "Fwd Header Length.1",
    "Subflow Fwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Bwd Packets",
    "Subflow Bwd Bytes",
    "Init_Win_bytes_forward",
    "Init_Win_bytes_backward",
    "act_data_pkt_fwd",
    "min_seg_size_forward",
    "Active Mean",
    "Active Std",
    "Active Max",
    "Active Min",
    "Idle Mean",
    "Idle Std",
    "Idle Max",
    "Idle Min",
]


class LocalTemporalFeaturePerturbation:
    """
    Reproducible local temporal feature perturbation for the frozen
    Multi-Horizon GRU.

    The method:
      1. Loads the TRAIN tensor.
      2. Computes a per-feature TRAIN-only median baseline.
      3. Runs the unchanged production inference on the original sequence.
      4. Replaces one feature at one timestep with its TRAIN median.
      5. Runs the same production inference again.
      6. Computes probability deltas:
         Delta P = P_perturbed - P_original.

    This is local model-sensitivity evidence for one forecast instance.
    It is not causal attribution or universal feature importance.
    """

    EXPECTED_OBSERVATION_LENGTH = 100
    EXPECTED_FEATURE_COUNT = 68

    def __init__(
        self,
        checkpoint_path: str | Path,
        train_tensor_path: str | Path,
    ) -> None:
        self.checkpoint_path = Path(checkpoint_path)
        self.train_tensor_path = Path(train_tensor_path)

        if len(FEATURE_NAMES) != self.EXPECTED_FEATURE_COUNT:
            raise RuntimeError(
                "Feature-name contract is invalid: "
                f"expected {self.EXPECTED_FEATURE_COUNT}, "
                f"found {len(FEATURE_NAMES)}."
            )

        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Checkpoint was not found: {self.checkpoint_path}"
            )

        if not self.train_tensor_path.exists():
            raise FileNotFoundError(
                f"TRAIN tensor was not found: {self.train_tensor_path}"
            )

        self.inference = MultiHorizonGRUInference(
            str(self.checkpoint_path)
        )

        train_tensor = np.load(
            self.train_tensor_path,
            allow_pickle=False,
        )

        if train_tensor.shape != (
            13515,
            self.EXPECTED_OBSERVATION_LENGTH,
            self.EXPECTED_FEATURE_COUNT,
        ):
            raise ValueError(
                "Unexpected TRAIN tensor shape: "
                f"{train_tensor.shape}. "
                "Expected (13515, 100, 68)."
            )

        if not np.isfinite(train_tensor).all():
            raise ValueError(
                "TRAIN tensor contains NaN or infinite values."
            )

        self.train_feature_medians = np.median(
            train_tensor,
            axis=(0, 1),
        ).astype(np.float32)

        if self.train_feature_medians.shape != (
            self.EXPECTED_FEATURE_COUNT,
        ):
            raise ValueError(
                "Unexpected TRAIN median shape: "
                f"{self.train_feature_medians.shape}."
            )

        if not np.isfinite(self.train_feature_medians).all():
            raise ValueError(
                "TRAIN-derived feature medians contain NaN or infinite values."
            )

    def explain(
        self,
        sequence: list[list[float]] | np.ndarray,
        feature_index: int,
        timestep: int,
    ) -> dict[str, Any]:
        """
        Explain one local feature/timestep perturbation.

        Args:
            sequence:
                Exactly 100 rows × 68 features.
            feature_index:
                Feature index from 0 through 67.
            timestep:
                Timestep index from 0 through 99.

        Returns:
            Structured local sensitivity evidence.
        """
        sequence_array = np.asarray(
            sequence,
            dtype=np.float32,
        )

        if sequence_array.shape != (
            self.EXPECTED_OBSERVATION_LENGTH,
            self.EXPECTED_FEATURE_COUNT,
        ):
            raise ValueError(
                "Expected sequence shape (100, 68), "
                f"got {sequence_array.shape}."
            )

        if not np.isfinite(sequence_array).all():
            raise ValueError(
                "Input sequence contains NaN or infinite values."
            )

        if not 0 <= feature_index < self.EXPECTED_FEATURE_COUNT:
            raise ValueError(
                f"Feature index must be between 0 and "
                f"{self.EXPECTED_FEATURE_COUNT - 1}, "
                f"got {feature_index}."
            )

        if not 0 <= timestep < self.EXPECTED_OBSERVATION_LENGTH:
            raise ValueError(
                f"Timestep must be between 0 and "
                f"{self.EXPECTED_OBSERVATION_LENGTH - 1}, "
                f"got {timestep}."
            )

        original_prediction = self.inference.predict(
            sequence_array.tolist()
        )

        perturbed_sequence = sequence_array.copy()

        baseline_value = float(
            self.train_feature_medians[feature_index]
        )

        original_value = float(
            perturbed_sequence[timestep, feature_index]
        )

        perturbed_sequence[timestep, feature_index] = baseline_value

        perturbed_prediction = self.inference.predict(
            perturbed_sequence.tolist()
        )

        probability_deltas = {
            str(horizon): (
                float(
                    perturbed_prediction["probabilities"][horizon]
                )
                - float(
                    original_prediction["probabilities"][horizon]
                )
            )
            for horizon in self.inference.horizons
        }

        return {
            "method": "Local Temporal Feature Perturbation",
            "interpretation": (
                "Local model-sensitivity evidence for this forecast "
                "instance; not causal attribution or universal feature "
                "importance."
            ),
            "feature_index": feature_index,
            "feature_name": FEATURE_NAMES[feature_index],
            "timestep": timestep,
            "original_value": original_value,
            "baseline_value": baseline_value,
            "baseline_source": "TRAIN tensor median",
            "original_probabilities": {
                str(horizon): float(
                    original_prediction["probabilities"][horizon]
                )
                for horizon in self.inference.horizons
            },
            "perturbed_probabilities": {
                str(horizon): float(
                    perturbed_prediction["probabilities"][horizon]
                )
                for horizon in self.inference.horizons
            },
            "probability_deltas": probability_deltas,
            "absolute_probability_deltas": {
                horizon: abs(delta)
                for horizon, delta in probability_deltas.items()
            },
            "thresholds": {
                str(horizon): float(
                    original_prediction["thresholds"][horizon]
                )
                for horizon in self.inference.horizons
            },
            "predictions": {
                str(horizon): int(
                    original_prediction["predictions"][horizon]
                )
                for horizon in self.inference.horizons
            },
        }


def build_default_explanation_engine(
    project_root: str | Path,
) -> LocalTemporalFeaturePerturbation:
    """
    Build the explanation engine using the repository's verified
    checkpoint and TRAIN tensor artifacts.
    """
    root = Path(project_root)

    return LocalTemporalFeaturePerturbation(
        checkpoint_path=root / "ml" / "models" / "multihorizon_gru.pt",
        train_tensor_path=root
        / "ml"
        / "processed"
        / "multihorizon_X_train.npy",
    )