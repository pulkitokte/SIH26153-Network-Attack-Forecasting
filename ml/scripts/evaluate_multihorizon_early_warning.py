import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# ============================================================
# CICIDS2017 - MULTI-HORIZON EARLY-WARNING EVALUATION
#
# Converts TEST predictions into episode-level lead-time
# analysis. Classification metrics and temporal early-warning
# metrics are reported separately.
#
# Read-only on existing files. Does not retrain, change
# thresholds, or modify datasets / tensors / models.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "processed"
REPORT_DIR = BASE_DIR / "reports"
METADATA_DIR = BASE_DIR / "metadata"

PREDICTION_FILE = DATA_DIR / "multihorizon_gru_test_predictions.csv"
TEMPORAL_METADATA_FILE = (
    METADATA_DIR / "test_episode_temporal_metadata.csv"
)
RESULTS_FILE = DATA_DIR / "multihorizon_early_warning_results.csv"
REPORT_FILE = REPORT_DIR / "multihorizon_early_warning_report.txt"

TEST_EPISODES = [19, 20, 21]
HORIZONS = [50, 100, 200, 500]

# Validation-selected thresholds. Do not retune.
THRESHOLDS = {
    50: 0.30,
    100: 0.55,
    200: 0.45,
    500: 0.35,
}

LEAD_SUCCESS_LEVELS = [10, 50, 100, 200, 500]


# ============================================================
# LOGGING
# ============================================================

class ReportLogger:
    def __init__(self):
        self.lines = []

    def log(self, *args, sep=" ", end="\n"):
        text = sep.join(str(arg) for arg in args) + end
        self.lines.append(text)
        print(text, end="", flush=True)

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(self.lines), encoding="utf-8")


logger = ReportLogger()
log = logger.log


def fmt_optional(value, digits=0):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    if digits == 0:
        return f"{int(value)}"
    return f"{value:.{digits}f}"


def compute_horizon_classification(y_true, y_score, y_pred):
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)
    y_pred = np.asarray(y_pred).astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    far_den = fp + tn
    far = float(fp / far_den) if far_den > 0 else 0.0

    return {
        "precision": float(
            precision_score(y_true, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, y_pred, zero_division=0)
        ),
        "f1": float(
            f1_score(y_true, y_pred, zero_division=0)
        ),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "pr_auc": float(average_precision_score(y_true, y_score)),
        "far": far,
    }


EXPECTED_TEMPORAL_COLUMNS = [
    "episode_id",
    "flow_start",
    "flow_end",
    "ddos_flows",
    "attack_start",
]

EXPECTED_ATTACK_START = {
    19: 37000,
    20: 39000,
    21: 41000,
}


def load_test_temporal_metadata(path):
    if not path.exists():
        raise ValueError(
            f"TEST temporal metadata file not found: {path}"
        )

    metadata = pd.read_csv(path)
    metadata.columns = metadata.columns.str.strip()

    actual_columns = list(metadata.columns)
    if actual_columns != EXPECTED_TEMPORAL_COLUMNS:
        raise ValueError(
            "TEST temporal metadata columns must be exactly "
            f"{EXPECTED_TEMPORAL_COLUMNS}, got {actual_columns}"
        )

    for column in EXPECTED_TEMPORAL_COLUMNS:
        if not pd.api.types.is_numeric_dtype(metadata[column]):
            raise ValueError(
                f"TEST temporal metadata column {column} "
                "must be numeric/integer."
            )
        if metadata[column].isnull().any():
            raise ValueError(
                f"TEST temporal metadata column {column} "
                "contains missing values."
            )
        if not np.array_equal(
            metadata[column].to_numpy(),
            metadata[column].to_numpy(dtype=np.int64),
        ):
            raise ValueError(
                f"TEST temporal metadata column {column} "
                "must contain integer values."
            )
        metadata[column] = metadata[column].astype(int)

    episode_ids = metadata["episode_id"].tolist()
    if episode_ids != TEST_EPISODES:
        raise ValueError(
            "TEST temporal metadata episode IDs must be exactly "
            f"{TEST_EPISODES}, got {episode_ids}"
        )

    if metadata["episode_id"].duplicated().any():
        raise ValueError(
            "TEST temporal metadata contains duplicate episode_id values."
        )

    for row in metadata.itertuples(index=False):
        episode_id = int(row.episode_id)
        flow_start = int(row.flow_start)
        flow_end = int(row.flow_end)
        ddos_flows = int(row.ddos_flows)
        attack_start = int(row.attack_start)

        if not (flow_start < attack_start <= flow_end):
            raise ValueError(
                f"Episode {episode_id}: expected "
                "flow_start < attack_start <= flow_end, "
                f"got flow_start={flow_start}, "
                f"attack_start={attack_start}, "
                f"flow_end={flow_end}"
            )

        if ddos_flows <= 0:
            raise ValueError(
                f"Episode {episode_id}: ddos_flows must be > 0, "
                f"got {ddos_flows}"
            )

        expected_start = EXPECTED_ATTACK_START[episode_id]
        if attack_start != expected_start:
            raise ValueError(
                f"Episode {episode_id}: attack_start must be "
                f"{expected_start}, got {attack_start}"
            )

    return metadata


# ============================================================
# HEADER
# ============================================================

log("=" * 75)
log("CICIDS2017 - MULTI-HORIZON EARLY-WARNING EVALUATION")
log("=" * 75)
log("\nThis script is read-only.")
log("TEST episodes only: 19, 20, 21")
log("Thresholds are the existing validation-selected values.")
log("No model is retrained. No source file is modified.")


# ============================================================
# LOAD
# ============================================================

log("\n" + "=" * 75)
log("LOAD FILES")
log("=" * 75)

predictions = pd.read_csv(PREDICTION_FILE)
predictions.columns = predictions.columns.str.strip()

log(f"\nPredictions : {PREDICTION_FILE.name}")
log(f"  Rows    : {len(predictions):,}")
log(f"  Columns : {list(predictions.columns)}")

required_pred_columns = [
    "window_id",
    "episode_id",
    "observation_start_position",
    "observation_end_position",
]
for horizon in HORIZONS:
    required_pred_columns.extend(
        [
            f"target_{horizon}",
            f"probability_{horizon}",
            f"prediction_{horizon}",
        ]
    )

missing = [
    column
    for column in required_pred_columns
    if column not in predictions.columns
]
if missing:
    raise ValueError(
        "Prediction CSV is missing columns: " + ", ".join(missing)
    )

pred_episodes = sorted(predictions["episode_id"].astype(int).unique())
log(f"  Episodes in prediction CSV: {pred_episodes}")

if pred_episodes != TEST_EPISODES:
    raise ValueError(
        "Prediction CSV episodes are not exactly TEST 19-21: "
        f"{pred_episodes}"
    )

if set(predictions["episode_id"].astype(int)) & set(range(1, 19)):
    raise ValueError(
        "TRAIN/VALIDATION episodes leaked into the prediction CSV."
    )

log("\nValidating saved predictions against fixed validation thresholds...")
for horizon in HORIZONS:
    prob_col = f"probability_{horizon}"
    pred_col = f"prediction_{horizon}"
    expected_pred = (
        predictions[prob_col].to_numpy(dtype=float)
        >= THRESHOLDS[horizon]
    ).astype(int)
    actual_pred = predictions[pred_col].to_numpy(dtype=int)
    n_mismatch = int(np.sum(actual_pred != expected_pred))
    if n_mismatch:
        raise ValueError(
            f"Horizon {horizon}: {n_mismatch} saved prediction(s) "
            "do not match int(probability >= "
            f"{THRESHOLDS[horizon]:.2f}). Thresholds must not be "
            "recalculated on TEST data."
        )
    log(
        f"  {horizon}-flow threshold {THRESHOLDS[horizon]:.2f}: "
        "prediction column matches probability cutoff"
    )

temporal_metadata = load_test_temporal_metadata(
    TEMPORAL_METADATA_FILE
)

log(f"\nTemporal metadata : {TEMPORAL_METADATA_FILE.name}")
log("  Loaded verified source-derived TEST episode metadata.")
log("  ddos_features_v1.csv is not required.")


# ============================================================
# ATTACK START FROM TEST TEMPORAL METADATA
# ============================================================

log("\n" + "=" * 75)
log("ATTACK START POSITIONS (TEST TEMPORAL METADATA)")
log("=" * 75)
log(
    "\nAttack-start positions are loaded from the verified "
    "source-derived TEST temporal metadata."
)

attack_start_by_episode = {}

for episode_id in TEST_EPISODES:
    row = temporal_metadata.loc[
        temporal_metadata["episode_id"] == episode_id
    ].iloc[0]

    flow_start = int(row["flow_start"])
    flow_end = int(row["flow_end"])
    ddos_flows = int(row["ddos_flows"])
    attack_start = int(row["attack_start"])
    attack_start_by_episode[episode_id] = attack_start

    log(f"\nEpisode {episode_id}:")
    log(f"  Flow range     : {flow_start} .. {flow_end}")
    log(f"  Attack starts  : {attack_start}")
    log(f"  DDoS flows     : {ddos_flows:,}")


# ============================================================
# EARLY-WARNING DEFINITION
# ============================================================

log("\n" + "=" * 75)
log("EARLY-WARNING DEFINITION")
log("=" * 75)
log(
    """
A warning is issued after a 100-flow observation window.

first_warning_flow = observation_end_position
of the earliest TEST window where:
  prediction == 1
  AND probability >= validation-selected threshold

This is the last observed flow. Forecast-region flows are
never used as model observations.

lead_time_flows = attack_start_flow - first_warning_flow

Counted as early warning only if:
  first_warning_flow < attack_start_flow
  i.e. lead_time_flows > 0

A warning at the attack-start flow has lead time 0 and is
NOT counted as a positive-lead-time early warning.
""".rstrip()
)

log("\nValidation-selected thresholds:")
for horizon in HORIZONS:
    log(f"  {horizon}-flow : {THRESHOLDS[horizon]:.2f}")


# ============================================================
# PER-EPISODE ANALYSIS
# ============================================================

log("\n" + "=" * 75)
log("PER-EPISODE EARLY WARNING")
log("=" * 75)

episode_rows = []

for episode_id in TEST_EPISODES:
    attack_start = attack_start_by_episode[episode_id]
    group = (
        predictions[predictions["episode_id"] == episode_id]
        .sort_values(
            ["observation_start_position", "observation_end_position"]
        )
        .reset_index(drop=True)
    )

    if group.empty:
        raise ValueError(
            f"No prediction windows for TEST episode {episode_id}."
        )

    # Observation windows must stay before / at the last pre-attack flow.
    obs_end_max = int(group["observation_end_position"].max())
    obs_start_min = int(group["observation_start_position"].min())

    log(f"\nEpisode {episode_id:02d}")
    log(f"Attack starts at flow: {attack_start}")
    log(
        f"Observation windows: "
        f"{obs_start_min}-{obs_end_max} "
        f"({len(group)} windows)"
    )

    for horizon in HORIZONS:
        threshold = THRESHOLDS[horizon]
        prob_col = f"probability_{horizon}"
        pred_col = f"prediction_{horizon}"
        target_col = f"target_{horizon}"

        qualifying = group[
            (group[pred_col] == 1)
            & (group[prob_col] >= threshold)
        ]

        row = {
            "episode_id": episode_id,
            "horizon": horizon,
            "threshold": threshold,
            "attack_start_flow": attack_start,
            "n_windows": len(group),
            "observation_start_min": obs_start_min,
            "observation_end_max": obs_end_max,
            "first_warning_flow": np.nan,
            "observation_start_position": np.nan,
            "observation_end_position": np.nan,
            "forecast_start_position": np.nan,
            "lead_time_flows": np.nan,
            "probability": np.nan,
            "window_target": np.nan,
            "warned_early": 0,
            "warning_at_or_after_attack": 0,
            "no_warning": 0,
            "first_warning_is_true_positive_forecast": 0,
        }

        log(f"\n{horizon}-flow:")

        if qualifying.empty:
            row["no_warning"] = 1
            log("  First warning: No early warning")
            log("  Lead time: N/A")
            log("  Probability: N/A")
            episode_rows.append(row)
            continue

        first = qualifying.iloc[0]
        warning_flow = int(first["observation_end_position"])
        obs_start = int(first["observation_start_position"])
        forecast_start = warning_flow + 1
        probability = float(first[prob_col])
        window_target = int(first[target_col])
        lead_time = attack_start - warning_flow

        row["first_warning_flow"] = warning_flow
        row["observation_start_position"] = obs_start
        row["observation_end_position"] = warning_flow
        row["forecast_start_position"] = forecast_start
        row["lead_time_flows"] = lead_time
        row["probability"] = probability
        row["window_target"] = window_target
        row["first_warning_is_true_positive_forecast"] = int(
            window_target == 1
        )

        if warning_flow < attack_start:
            row["warned_early"] = 1
            log(f"  First warning: {warning_flow}")
            log(f"  Lead time: {lead_time} flows")
            log(f"  Probability: {probability:.6f}")
        else:
            row["warning_at_or_after_attack"] = 1
            log("  First warning: No early warning")
            log(
                f"  (First predicted warning is at flow "
                f"{warning_flow}, which is at/after attack start "
                f"{attack_start}; lead time={lead_time})"
            )
            log(f"  Probability: {probability:.6f}")

        episode_rows.append(row)


results_df = pd.DataFrame(episode_rows)


# ============================================================
# CLASSIFICATION VS TEMPORAL METRICS
# ============================================================

log("\n" + "=" * 75)
log("1. FORECASTING CLASSIFICATION PERFORMANCE (TEST)")
log("=" * 75)
log(
    "\nThese metrics describe window-level DDoS detection."
)
log("They are NOT lead-time / early-warning metrics.")
log(
    "Metrics are computed directly from the saved TEST "
    "prediction CSV using the existing validation-selected "
    "thresholds."
)

classification_metrics = {}
for horizon in HORIZONS:
    classification_metrics[horizon] = compute_horizon_classification(
        y_true=predictions[f"target_{horizon}"],
        y_score=predictions[f"probability_{horizon}"],
        y_pred=predictions[f"prediction_{horizon}"],
    )

log(
    f"\n{'Horizon':<10}{'F1':>8}{'Recall':>10}{'Prec':>10}"
    f"{'Acc':>10}{'ROC-AUC':>10}{'PR-AUC':>10}{'FAR':>10}"
)
for horizon in HORIZONS:
    m = classification_metrics[horizon]
    log(
        f"{horizon:<10}{m['f1']:8.4f}{m['recall']:10.4f}"
        f"{m['precision']:10.4f}{m['accuracy']:10.4f}"
        f"{m['roc_auc']:10.4f}{m['pr_auc']:10.4f}{m['far']:10.4f}"
    )


log("\n" + "=" * 75)
log("2. TEMPORAL EARLY-WARNING PERFORMANCE (TEST EPISODES)")
log("=" * 75)

horizon_summaries = []

for horizon in HORIZONS:
    subset = results_df[results_df["horizon"] == horizon]
    n_eval = len(subset)
    n_warned = int(subset["warned_early"].sum())
    n_none = int(subset["no_warning"].sum())
    n_late = int(subset["warning_at_or_after_attack"].sum())
    warned = subset[subset["warned_early"] == 1]
    warning_rate = n_warned / n_eval if n_eval else 0.0

    if n_warned:
        leads = warned["lead_time_flows"].astype(float)
        mean_lead = float(leads.mean())
        median_lead = float(leads.median())
        min_lead = float(leads.min())
        max_lead = float(leads.max())
        avg_prob = float(warned["probability"].mean())
        earliest_idx = warned["first_warning_flow"].astype(float).idxmin()
        earliest_prob = float(warned.loc[earliest_idx, "probability"])
        n_tp_first = int(
            warned["first_warning_is_true_positive_forecast"].sum()
        )
    else:
        mean_lead = median_lead = min_lead = max_lead = np.nan
        avg_prob = earliest_prob = np.nan
        n_tp_first = 0

    success = {}
    for level in LEAD_SUCCESS_LEVELS:
        n_ok = int(
            (
                subset["warned_early"].eq(1)
                & subset["lead_time_flows"].ge(level)
            ).sum()
        )
        success[level] = {
            "count": n_ok,
            "rate": n_ok / n_eval if n_eval else 0.0,
        }

    horizon_summaries.append({
        "horizon": horizon,
        "episodes_evaluated": n_eval,
        "episodes_warned": n_warned,
        "warning_rate": warning_rate,
        "mean_lead": mean_lead,
        "median_lead": median_lead,
        "min_lead": min_lead,
        "max_lead": max_lead,
        "earliest_warning_probability": earliest_prob,
        "average_first_warning_probability": avg_prob,
        "false_or_no_warning_episodes": n_none + n_late,
        "no_warning_episodes": n_none,
        "warnings_at_or_after_attack": n_late,
        "first_warnings_true_positive_forecast": n_tp_first,
        "success": success,
    })

    log(f"\n--- {horizon}-flow horizon ---")
    log(f"Episodes evaluated              : {n_eval}")
    log(f"Episodes warned (lead time > 0) : {n_warned}")
    log(f"Early-warning rate              : {warning_rate:.2%}")
    log(f"Mean lead time                  : {fmt_optional(mean_lead, 2)}")
    log(f"Median lead time                : {fmt_optional(median_lead, 2)}")
    log(f"Minimum lead time               : {fmt_optional(min_lead, 0)}")
    log(f"Maximum lead time               : {fmt_optional(max_lead, 0)}")
    log(
        f"Earliest warning probability    : "
        f"{fmt_optional(earliest_prob, 6)}"
    )
    log(
        f"Average first-warning probability: "
        f"{fmt_optional(avg_prob, 6)}"
    )
    log(f"False/no-warning episodes       : {n_none + n_late}")
    log(f"  No warning at all             : {n_none}")
    log(f"  Warning at/after attack start : {n_late}")
    log(
        f"First warnings that were also "
        f"true-positive forecasts : {n_tp_first}/{n_warned}"
    )

    log("\nLead-time success rates:")
    for level in LEAD_SUCCESS_LEVELS:
        item = success[level]
        log(
            f"  >= {level:>3} flows early : "
            f"{item['count']}/{n_eval} "
            f"({item['rate']:.2%})"
        )


# ============================================================
# COMPARISON TABLE
# ============================================================

log("\n" + "=" * 75)
log("OPERATIONAL HORIZON COMPARISON")
log("=" * 75)
log(
    "\nThis table is temporal early-warning performance, "
    "not classification F1."
)

header = (
    f"{'Horizon':<10}"
    f"{'Episodes Warned':>17}"
    f"{'Warning Rate':>14}"
    f"{'Mean Lead':>12}"
    f"{'Median Lead':>13}"
    f"{'>=50 Flow Success':>19}"
    f"{'>=100 Flow Success':>20}"
    f"{'>=200 Flow Success':>20}"
)
log("\n" + header)
log("-" * len(header))

for item in horizon_summaries:
    log(
        f"{item['horizon']:<10}"
        f"{item['episodes_warned']:>17}"
        f"{item['warning_rate']:>13.1%}"
        f"{fmt_optional(item['mean_lead'], 1):>12}"
        f"{fmt_optional(item['median_lead'], 1):>13}"
        f"{item['success'][50]['rate']:>18.1%}"
        f"{item['success'][100]['rate']:>19.1%}"
        f"{item['success'][200]['rate']:>19.1%}"
    )


# ============================================================
# SAVE RESULTS
# ============================================================

save_df = results_df.copy()
for column in [
    "first_warning_flow",
    "observation_start_position",
    "observation_end_position",
    "forecast_start_position",
    "lead_time_flows",
    "window_target",
]:
    save_df[column] = save_df[column].astype("Int64")

save_df.to_csv(RESULTS_FILE, index=False)
logger.save(REPORT_FILE)

log("\n" + "=" * 75)
log("SAVED OUTPUTS")
log("=" * 75)
log(f"\nResults : {RESULTS_FILE}")
log(f"Report  : {REPORT_FILE}")
log("\nExisting predictions, tensors, models, and reports were not modified.")

log("\n" + "=" * 75)
log("MULTI-HORIZON EARLY-WARNING EVALUATION COMPLETE")
log("=" * 75)

log("\n" + header)
log("-" * len(header))
for item in horizon_summaries:
    log(
        f"{item['horizon']:<10}"
        f"{item['episodes_warned']:>17}"
        f"{item['warning_rate']:>13.1%}"
        f"{fmt_optional(item['mean_lead'], 1):>12}"
        f"{fmt_optional(item['median_lead'], 1):>13}"
        f"{item['success'][50]['rate']:>18.1%}"
        f"{item['success'][100]['rate']:>19.1%}"
        f"{item['success'][200]['rate']:>19.1%}"
    )
log("=" * 75)

# Re-save so the COMPLETE banner is included in the report.
logger.save(REPORT_FILE)
