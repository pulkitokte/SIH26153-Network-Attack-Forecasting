import numpy as np
import pandas as pd
from pathlib import Path


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

PREDICTION_FILE = DATA_DIR / "multihorizon_gru_test_predictions.csv"
FEATURE_FILE = DATA_DIR / "ddos_features_v1.csv"
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

# TEST classification metrics from the already-trained model.
# These are forecasting metrics, not temporal lead-time metrics.
CLASSIFICATION_METRICS = {
    50: {
        "f1": 0.4093,
        "recall": 1.0000,
        "precision": 0.2573,
        "roc_auc": 0.9455,
        "pr_auc": 0.3681,
        "far": 0.1696,
    },
    100: {
        "f1": 0.6577,
        "recall": 0.9833,
        "precision": 0.4941,
        "roc_auc": 0.9492,
        "pr_auc": 0.7019,
        "far": 0.1257,
    },
    200: {
        "f1": 0.7927,
        "recall": 0.8317,
        "precision": 0.7572,
        "roc_auc": 0.9225,
        "pr_auc": 0.7726,
        "far": 0.0761,
    },
    500: {
        "f1": 0.7151,
        "recall": 1.0000,
        "precision": 0.5566,
        "roc_auc": 0.7644,
        "pr_auc": 0.8423,
        "far": 0.9933,
    },
}


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

features = pd.read_csv(
    FEATURE_FILE,
    usecols=["Label", "episode_id", "sequence_position"],
    low_memory=False,
)
features.columns = features.columns.str.strip()
features["Label"] = features["Label"].astype(str).str.strip()
features["episode_id"] = features["episode_id"].astype(int)
features["sequence_position"] = features["sequence_position"].astype(int)

log(f"\nFeatures    : {FEATURE_FILE.name}")
log("  Using Label, episode_id, sequence_position only.")


# ============================================================
# ATTACK START FROM SOURCE FEATURES
# ============================================================

log("\n" + "=" * 75)
log("ATTACK START POSITIONS (SOURCE FEATURES)")
log("=" * 75)
log("\nAttack start = first DDoS sequence_position in the episode.")

attack_start_by_episode = {}

for episode_id in TEST_EPISODES:
    episode_flows = features[features["episode_id"] == episode_id]
    if episode_flows.empty:
        raise ValueError(
            f"No source flows found for TEST episode {episode_id}."
        )

    ddos_flows = episode_flows[episode_flows["Label"] == "DDoS"]
    if ddos_flows.empty:
        raise ValueError(
            f"TEST episode {episode_id} has no DDoS flows."
        )

    attack_start = int(ddos_flows["sequence_position"].min())
    attack_start_by_episode[episode_id] = attack_start

    log(f"\nEpisode {episode_id}:")
    log(
        f"  Flow range     : "
        f"{int(episode_flows['sequence_position'].min())} "
        f".. {int(episode_flows['sequence_position'].max())}"
    )
    log(f"  Attack starts  : {attack_start}")
    log(f"  DDoS flows     : {len(ddos_flows):,}")


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
log("Copied from the already-trained model evaluation.")

log(
    f"\n{'Horizon':<10}{'F1':>8}{'Recall':>10}{'Prec':>10}"
    f"{'ROC-AUC':>10}{'PR-AUC':>10}{'FAR':>10}"
)
for horizon in HORIZONS:
    m = CLASSIFICATION_METRICS[horizon]
    log(
        f"{horizon:<10}{m['f1']:8.4f}{m['recall']:10.4f}"
        f"{m['precision']:10.4f}{m['roc_auc']:10.4f}"
        f"{m['pr_auc']:10.4f}{m['far']:10.4f}"
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
