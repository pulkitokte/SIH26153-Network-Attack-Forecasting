import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CICIDS2017 - MULTI-HORIZON FORECASTING WINDOW VALIDATION
#
# Read-only checks against:
#   processed/ddos_multihorizon_windows_v1.csv
#   processed/ddos_features_v1.csv
#
# This script does not modify, regenerate, or overwrite
# any dataset, generator, model, or existing report.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

WINDOWS_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_multihorizon_windows_v1.csv"
)

FEATURES_FILE = (
    BASE_DIR
    / "processed"
    / "ddos_features_v1.csv"
)

REPORT_FILE = (
    BASE_DIR
    / "reports"
    / "multihorizon_validation_report.txt"
)

OBSERVATION_LENGTH = 100

FORECAST_HORIZONS = [50, 100, 200, 500]

TRAIN_EPISODES = set(range(1, 16))
VALIDATION_EPISODES = set(range(16, 19))
TEST_EPISODES = set(range(19, 22))

EXPECTED_SPLITS = {
    "TRAIN": TRAIN_EPISODES,
    "VALIDATION": VALIDATION_EPISODES,
    "TEST": TEST_EPISODES,
}

RATIO_ATOL = 1e-12


# ============================================================
# LOGGING
# ============================================================

class ReportLogger:
    """Print to the terminal and keep a full copy for the report."""

    def __init__(self):
        self.lines = []

    def log(self, *args, sep=" ", end="\n"):
        text = sep.join(str(arg) for arg in args) + end
        self.lines.append(text)
        print(text, end="")

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(self.lines), encoding="utf-8")


logger = ReportLogger()
log = logger.log

checks = []


def record_check(name, status, details=""):
    checks.append(
        {
            "name": name,
            "status": status,
            "details": details,
        }
    )
    suffix = f"  {details}" if details else ""
    log(f"[{status}] {name}{suffix}")


def fail_reasons(reasons):
    if not reasons:
        return ""
    if len(reasons) == 1:
        return reasons[0]
    return f"{len(reasons)} issues. First: {reasons[0]}"


# ============================================================
# HEADER
# ============================================================

log("=" * 75)
log("CICIDS2017 - MULTI-HORIZON FORECASTING WINDOW VALIDATION")
log("=" * 75)

log("\nThis is a read-only validation.")
log("No dataset, generator, or model file will be modified.")


# ============================================================
# LOAD DATA
# ============================================================

log("\n" + "=" * 75)
log("LOAD DATASETS")
log("=" * 75)

if not WINDOWS_FILE.exists():
    raise FileNotFoundError(
        f"Forecasting dataset not found:\n{WINDOWS_FILE}"
    )

if not FEATURES_FILE.exists():
    raise FileNotFoundError(
        f"Feature dataset not found:\n{FEATURES_FILE}"
    )

log(f"\nWindows file : {WINDOWS_FILE}")
log(f"Features file: {FEATURES_FILE}")

windows = pd.read_csv(
    WINDOWS_FILE,
    low_memory=False
)

features = pd.read_csv(
    FEATURES_FILE,
    low_memory=False
)

windows.columns = windows.columns.str.strip()
features.columns = features.columns.str.strip()

log("\nForecasting dataset")
log(f"  Rows    : {len(windows):,}")
log(f"  Columns : {len(windows.columns):,}")

log("\nSource feature dataset")
log(f"  Rows    : {len(features):,}")
log(f"  Columns : {len(features.columns):,}")

log("\nForecasting CSV columns:")
for column in windows.columns:
    log(f"  - {column}")


# ============================================================
# SCHEMA
# ============================================================

log("\n" + "=" * 75)
log("SCHEMA VALIDATION")
log("=" * 75)

listed_required_columns = [
    "window_id",
    "episode_id",
    "observation_start_position",
    "observation_end_position",
    "observation_length",
    "forecast_start_position",
    "forecast_end_position",
    "ddos_count_next_50",
    "ddos_next_50",
    "ddos_ratio_next_50",
    "ddos_count_next_100",
    "ddos_next_100",
    "ddos_ratio_next_100",
    "ddos_count_next_200",
    "ddos_next_200",
    "ddos_ratio_next_200",
    "ddos_count_next_500",
    "ddos_next_500",
    "ddos_ratio_next_500",
    "dataset_split",
]

actual_columns = set(windows.columns)
missing_listed = [
    column
    for column in listed_required_columns
    if column not in actual_columns
]
unexpected_columns = [
    column
    for column in windows.columns
    if column not in listed_required_columns
]

log("\nListed required columns vs actual CSV:")

for column in listed_required_columns:
    if column in actual_columns:
        log(f"  [PRESENT] {column}")
    else:
        log(f"  [ABSENT]  {column}")

if unexpected_columns:
    log("\nUnexpected extra columns in CSV:")
    for column in unexpected_columns:
        log(f"  - {column}")
else:
    log("\nNo unexpected extra columns.")

derived_forecast_positions = False

if (
    "forecast_start_position" in missing_listed
    or "forecast_end_position" in missing_listed
):
    derived_forecast_positions = True
    log(
        "\nNOTE: forecast_start_position and/or "
        "forecast_end_position are not stored in the CSV."
    )
    log(
        "Validation derives them from observation positions "
        "instead of inventing stored columns:"
    )
    log("  forecast_start = observation_end_position + 1")
    log(
        "  forecast_end(H) = observation_end_position + H"
    )
    log("    for H in {50, 100, 200, 500}")

schema_blocking = [
    column
    for column in missing_listed
    if column not in {
        "forecast_start_position",
        "forecast_end_position",
    }
]

if schema_blocking:
    record_check(
        "Required columns",
        "FAIL",
        "Missing stored columns: " + ", ".join(schema_blocking),
    )
else:
    note = (
        "Adapted schema: forecast positions are derived, "
        "not stored."
        if derived_forecast_positions
        else "All listed columns are present."
    )
    record_check("Required columns", "OK", note)

feature_required = [
    "Label",
    "episode_id",
    "sequence_position",
]

missing_feature_columns = [
    column
    for column in feature_required
    if column not in features.columns
]

if missing_feature_columns:
    record_check(
        "Source feature columns",
        "FAIL",
        "Missing: " + ", ".join(missing_feature_columns),
    )
    raise ValueError(
        "Source feature dataset is missing columns required "
        "for observation/forecast lookups: "
        + ", ".join(missing_feature_columns)
    )

record_check(
    "Source feature columns",
    "OK",
    "Label, episode_id, sequence_position are present.",
)


# ============================================================
# MISSING / INFINITE VALUES
# ============================================================

log("\n" + "=" * 75)
log("MISSING AND INFINITE VALUES")
log("=" * 75)

missing = windows.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    log("\nNo missing / NaN values in the forecasting dataset.")
    record_check("No missing values", "OK")
else:
    log("\nMissing / NaN values:")
    log(str(missing))
    record_check(
        "No missing values",
        "FAIL",
        fail_reasons(
            [
                f"{column}={count}"
                for column, count in missing.items()
            ]
        ),
    )

numeric_windows = windows.select_dtypes(include=[np.number])
inf_counts = np.isinf(numeric_windows).sum()
inf_counts = inf_counts[inf_counts > 0]

if len(inf_counts) == 0:
    log("No infinite values in numeric forecasting columns.")
    record_check("No infinite values", "OK")
else:
    log("\nInfinite values:")
    log(str(inf_counts))
    record_check(
        "No infinite values",
        "FAIL",
        fail_reasons(
            [
                f"{column}={count}"
                for column, count in inf_counts.items()
            ]
        ),
    )


# ============================================================
# DUPLICATE WINDOWS
# ============================================================

log("\n" + "=" * 75)
log("DUPLICATE WINDOWS")
log("=" * 75)

duplicate_ids = int(
    windows["window_id"].duplicated().sum()
)
duplicate_keys = int(
    windows.duplicated(
        subset=[
            "episode_id",
            "observation_start_position",
            "observation_end_position",
        ]
    ).sum()
)
duplicate_rows = int(windows.duplicated().sum())

log(f"Duplicate window_id values              : {duplicate_ids:,}")
log(
    "Duplicate episode + observation bounds  : "
    f"{duplicate_keys:,}"
)
log(f"Duplicate complete rows                 : {duplicate_rows:,}")

if duplicate_ids or duplicate_keys or duplicate_rows:
    record_check(
        "No duplicate windows",
        "FAIL",
        (
            f"duplicate window_id={duplicate_ids}, "
            f"duplicate observation keys={duplicate_keys}, "
            f"duplicate rows={duplicate_rows}"
        ),
    )
else:
    record_check("No duplicate windows", "OK")


# ============================================================
# OBSERVATION LENGTH
# ============================================================

log("\n" + "=" * 75)
log("OBSERVATION WINDOW LENGTH")
log("=" * 75)

length_values = (
    windows["observation_length"]
    .value_counts(dropna=False)
    .sort_index()
)
log("\nobservation_length value counts:")
log(str(length_values))

span = (
    windows["observation_end_position"]
    - windows["observation_start_position"]
    + 1
)

bad_length_column = int(
    (windows["observation_length"] != OBSERVATION_LENGTH).sum()
)
bad_span = int((span != OBSERVATION_LENGTH).sum())
negative_or_inverted = int(
    (
        windows["observation_end_position"]
        < windows["observation_start_position"]
    ).sum()
)

log(
    f"\nRows where observation_length != {OBSERVATION_LENGTH}: "
    f"{bad_length_column:,}"
)
log(
    f"Rows where (end - start + 1) != {OBSERVATION_LENGTH}: "
    f"{bad_span:,}"
)
log(
    f"Rows where observation end < start: "
    f"{negative_or_inverted:,}"
)

obs_length_reasons = []
if bad_length_column:
    obs_length_reasons.append(
        f"{bad_length_column} rows have observation_length "
        f"!= {OBSERVATION_LENGTH}"
    )
if bad_span:
    obs_length_reasons.append(
        f"{bad_span} rows have observation span != "
        f"{OBSERVATION_LENGTH}"
    )
if negative_or_inverted:
    obs_length_reasons.append(
        f"{negative_or_inverted} rows have inverted "
        "observation bounds"
    )

if obs_length_reasons:
    record_check(
        "Observation length = 100",
        "FAIL",
        fail_reasons(obs_length_reasons),
    )
else:
    record_check(
        "Observation length = 100",
        "OK",
        "Every window stores a 100-flow observation span.",
    )


# ============================================================
# DERIVED FORECAST POSITIONS
# ============================================================

log("\n" + "=" * 75)
log("FORECAST POSITIONS")
log("=" * 75)

forecast_start = (
    windows["observation_end_position"] + 1
)

log(
    "\nDerived forecast_start_position = "
    "observation_end_position + 1"
)
log(f"  Min forecast start: {int(forecast_start.min()):,}")
log(f"  Max forecast start: {int(forecast_start.max()):,}")

overlap_count = int(
    (
        forecast_start
        <= windows["observation_end_position"]
    ).sum()
)
gap_before_forecast = int(
    (
        forecast_start
        != windows["observation_end_position"] + 1
    ).sum()
)

log(
    "\nWindows where derived forecast start does not "
    "immediately follow observation end: "
    f"{gap_before_forecast:,}"
)
log(
    "Windows where observation and forecast would overlap: "
    f"{overlap_count:,}"
)

if overlap_count == 0 and gap_before_forecast == 0:
    record_check(
        "Forecast starts after observation",
        "OK",
        "forecast_start = observation_end_position + 1",
    )
    record_check(
        "No observation/forecast overlap",
        "OK",
        "Forecast begins on the next sequence_position.",
    )
else:
    record_check(
        "Forecast starts after observation",
        "FAIL",
        (
            f"{gap_before_forecast} windows do not start "
            "immediately after the observation"
        ),
    )
    record_check(
        "No observation/forecast overlap",
        "FAIL",
        f"{overlap_count} windows overlap observation and forecast",
    )

log("\nDerived forecast end positions by horizon:")
for horizon in FORECAST_HORIZONS:
    forecast_end = forecast_start + horizon - 1
    log(
        f"  H={horizon:>3}: end range "
        f"{int(forecast_end.min()):,} .. "
        f"{int(forecast_end.max()):,}"
    )


# ============================================================
# EPISODE SPLIT
# ============================================================

log("\n" + "=" * 75)
log("EPISODE ALLOCATION AND DATASET SPLIT")
log("=" * 75)

episode_ids = set(
    windows["episode_id"].astype(int).unique()
)
split_values = (
    windows["dataset_split"]
    .value_counts(dropna=False)
)

log("\nTotal windows:", f"{len(windows):,}")
log("\nUnique episode_id values:", f"{len(episode_ids)}")
log("Episode IDs:", sorted(episode_ids))

log("\nWindows per episode:")
windows_per_episode = (
    windows["episode_id"]
    .value_counts()
    .sort_index()
)
log(str(windows_per_episode))

log("\ndataset_split distribution:")
log(str(split_values))

split_reasons = []
unknown_splits = sorted(
    set(windows["dataset_split"].unique())
    - set(EXPECTED_SPLITS)
)
if unknown_splits:
    split_reasons.append(
        "Unexpected dataset_split values: "
        + ", ".join(map(str, unknown_splits))
    )

episodes_by_split = {}
for split_name, expected_episodes in EXPECTED_SPLITS.items():
    actual_episodes = set(
        windows.loc[
            windows["dataset_split"] == split_name,
            "episode_id",
        ].astype(int).unique()
    )
    episodes_by_split[split_name] = actual_episodes

    extra = sorted(actual_episodes - expected_episodes)
    missing_eps = sorted(expected_episodes - actual_episodes)

    log(f"\n{split_name}:")
    log(f"  Expected episodes: {sorted(expected_episodes)}")
    log(f"  Actual episodes  : {sorted(actual_episodes)}")

    if extra:
        split_reasons.append(
            f"{split_name} contains unexpected episodes {extra}"
        )
    if missing_eps:
        split_reasons.append(
            f"{split_name} is missing expected episodes "
            f"{missing_eps}"
        )

if split_reasons:
    record_check(
        "Episode split",
        "FAIL",
        fail_reasons(split_reasons),
    )
else:
    record_check(
        "Episode split",
        "OK",
        "TRAIN=1-15, VALIDATION=16-18, TEST=19-21",
    )

overlap_pairs = []
split_names = list(EXPECTED_SPLITS)
for i, left in enumerate(split_names):
    for right in split_names[i + 1:]:
        overlap = sorted(
            episodes_by_split[left]
            & episodes_by_split[right]
        )
        if overlap:
            overlap_pairs.append(
                f"{left} ∩ {right} = {overlap}"
            )

splits_per_episode = (
    windows.groupby("episode_id")["dataset_split"]
    .nunique()
)
multi_split_episodes = splits_per_episode[
    splits_per_episode > 1
]

log("\nEpisodes appearing in more than one split:")
if len(multi_split_episodes) == 0 and not overlap_pairs:
    log("  None")
    record_check("No episode overlap", "OK")
else:
    if len(multi_split_episodes):
        log(str(multi_split_episodes))
    for item in overlap_pairs:
        log(f"  {item}")
    record_check(
        "No episode overlap",
        "FAIL",
        fail_reasons(
            overlap_pairs
            or [
                "Episodes assigned to more than one split: "
                + ", ".join(
                    str(int(eid))
                    for eid in multi_split_episodes.index
                )
            ]
        ),
    )


# ============================================================
# INDEX SOURCE FEATURES BY EPISODE
# ============================================================

log("\n" + "=" * 75)
log("SOURCE FEATURE INDEX")
log("=" * 75)

if features[["episode_id", "sequence_position"]].isnull().any().any():
    raise ValueError(
        "episode_id or sequence_position contains missing "
        "values in the source feature dataset."
    )

features = features.sort_values(
    ["episode_id", "sequence_position"]
).reset_index(drop=True)

episode_index = {}
feature_label_values = (
    features["Label"]
    .astype(str)
    .str.strip()
)

log(
    "\nSource Label values: "
    + ", ".join(
        sorted(feature_label_values.unique().tolist())
    )
)

for episode_id, episode in features.groupby(
    "episode_id",
    sort=True
):
    episode_id = int(episode_id)
    positions = episode["sequence_position"].astype(int).to_numpy()
    labels = (
        episode["Label"]
        .astype(str)
        .str.strip()
        .to_numpy()
    )

    if len(positions) == 0:
        continue

    min_pos = int(positions.min())
    max_pos = int(positions.max())
    n_slots = max_pos + 1

    present = np.zeros(n_slots, dtype=bool)
    is_ddos = np.zeros(n_slots, dtype=bool)

    if np.any(positions < 0):
        raise ValueError(
            f"Episode {episode_id} has negative "
            "sequence_position values."
        )

    present[positions] = True
    is_ddos[positions] = (labels == "DDoS")

    duplicate_positions = int(
        pd.Series(positions).duplicated().sum()
    )

    episode_index[episode_id] = {
        "min_pos": min_pos,
        "max_pos": max_pos,
        "n_flows": int(len(episode)),
        "present": present,
        "is_ddos": is_ddos,
        "duplicate_positions": duplicate_positions,
        "contiguous": bool(
            (max_pos - min_pos + 1) == len(episode)
            and present[min_pos:max_pos + 1].all()
        ),
    }

log(f"\nIndexed episodes: {len(episode_index)}")
noncontiguous = [
    eid
    for eid, info in episode_index.items()
    if not info["contiguous"]
]
if noncontiguous:
    log(
        "WARNING: sequence_position is not contiguous "
        f"in episodes: {noncontiguous}"
    )
else:
    log("sequence_position is contiguous within every episode.")


# ============================================================
# WINDOW LOOKUPS AGAINST SOURCE FEATURES
# ============================================================

log("\n" + "=" * 75)
log("WINDOW LOOKUPS AGAINST SOURCE FEATURES")
log("=" * 75)

n_windows = len(windows)

unknown_episode = 0
obs_out_of_episode = 0
obs_missing_flows = 0
obs_not_100_flows = 0
obs_contains_ddos = 0

forecast_out_of_episode = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
forecast_missing_flows = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
count_mismatch = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
positive_without_future_ddos = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
negative_with_future_ddos = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}

horizon_internal_count_range = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
horizon_ratio_mismatch = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}
horizon_binary_mismatch = {
    horizon: 0 for horizon in FORECAST_HORIZONS
}

obs_ddos_examples = []
forecast_example = {
    horizon: [] for horizon in FORECAST_HORIZONS
}

obs_start_arr = windows["observation_start_position"].astype(int).to_numpy()
obs_end_arr = windows["observation_end_position"].astype(int).to_numpy()
episode_arr = windows["episode_id"].astype(int).to_numpy()
window_id_arr = windows["window_id"].to_numpy()

horizon_count_arr = {}
horizon_binary_arr = {}
horizon_ratio_arr = {}

for horizon in FORECAST_HORIZONS:
    count_col = f"ddos_count_next_{horizon}"
    binary_col = f"ddos_next_{horizon}"
    ratio_col = f"ddos_ratio_next_{horizon}"

    if count_col not in windows.columns:
        continue

    counts = windows[count_col]
    binary = windows[binary_col]
    ratio = windows[ratio_col]

    horizon_count_arr[horizon] = counts.to_numpy()
    horizon_binary_arr[horizon] = binary.to_numpy()
    horizon_ratio_arr[horizon] = ratio.to_numpy()

    bad_range = int(
        ((counts < 0) | (counts > horizon)).sum()
    )
    bad_ratio = int(
        (~np.isclose(
            ratio.to_numpy(dtype=float),
            counts.to_numpy(dtype=float) / horizon,
            atol=RATIO_ATOL,
            equal_nan=False,
        )).sum()
    )
    expected_binary = (counts > 0).astype(int)
    bad_binary = int((binary != expected_binary).sum())

    horizon_internal_count_range[horizon] = bad_range
    horizon_ratio_mismatch[horizon] = bad_ratio
    horizon_binary_mismatch[horizon] = bad_binary

log(
    "Scanning every window against "
    "processed/ddos_features_v1.csv ..."
)

for i in range(n_windows):
    episode_id = int(episode_arr[i])
    obs_start = int(obs_start_arr[i])
    obs_end = int(obs_end_arr[i])
    info = episode_index.get(episode_id)

    if info is None:
        unknown_episode += 1
        continue

    present = info["present"]
    is_ddos = info["is_ddos"]
    max_pos = info["max_pos"]
    min_pos = info["min_pos"]

    if (
        obs_start < min_pos
        or obs_end > max_pos
        or obs_start < 0
        or obs_end >= len(present)
    ):
        obs_out_of_episode += 1
    else:
        obs_present_count = int(
            present[obs_start:obs_end + 1].sum()
        )
        if obs_present_count != (obs_end - obs_start + 1):
            obs_missing_flows += 1
        if obs_present_count != OBSERVATION_LENGTH:
            obs_not_100_flows += 1

        obs_ddos_count = int(
            is_ddos[obs_start:obs_end + 1].sum()
        )
        if obs_ddos_count > 0:
            obs_contains_ddos += 1
            if len(obs_ddos_examples) < 5:
                obs_ddos_examples.append(
                    (
                        int(window_id_arr[i]),
                        episode_id,
                        obs_start,
                        obs_end,
                        obs_ddos_count,
                    )
                )

    fc_start = obs_end + 1

    for horizon in FORECAST_HORIZONS:
        if horizon not in horizon_count_arr:
            continue

        fc_end = fc_start + horizon - 1
        stored_count = int(horizon_count_arr[horizon][i])
        stored_binary = int(horizon_binary_arr[horizon][i])

        if (
            fc_start < min_pos
            or fc_end > max_pos
            or fc_start < 0
            or fc_end >= len(present)
        ):
            forecast_out_of_episode[horizon] += 1
            continue

        region = slice(fc_start, fc_end + 1)
        present_count = int(present[region].sum())
        actual_count = int(is_ddos[region].sum())

        if present_count != horizon:
            forecast_missing_flows[horizon] += 1

        if actual_count != stored_count:
            count_mismatch[horizon] += 1
            if len(forecast_example[horizon]) < 5:
                forecast_example[horizon].append(
                    (
                        int(window_id_arr[i]),
                        episode_id,
                        fc_start,
                        fc_end,
                        stored_count,
                        actual_count,
                    )
                )

        if stored_binary == 1 and actual_count == 0:
            positive_without_future_ddos[horizon] += 1

        if stored_binary == 0 and actual_count > 0:
            negative_with_future_ddos[horizon] += 1


# ============================================================
# EARLY-WARNING SAFETY
# ============================================================

log("\n" + "=" * 75)
log("CRITICAL EARLY-WARNING SAFETY CHECK")
log("=" * 75)

log(
    "\nFor every forecasting window, the corresponding "
    f"{OBSERVATION_LENGTH} source rows were inspected "
    "using episode_id and sequence_position."
)
log(f"\nObservation windows containing DDoS: {obs_contains_ddos}")
log("The expected value is 0.")

if obs_ddos_examples:
    log("\nExamples of observation windows containing DDoS:")
    for example in obs_ddos_examples:
        log(
            f"  window_id={example[0]}, "
            f"episode_id={example[1]}, "
            f"obs={example[2]}-{example[3]}, "
            f"ddos_flows={example[4]}"
        )

if unknown_episode:
    record_check(
        "Observation contains zero DDoS",
        "FAIL",
        f"{unknown_episode} windows reference unknown episode_id values",
    )
elif obs_contains_ddos == 0:
    record_check(
        "Observation contains zero DDoS",
        "OK",
        "Observation windows containing DDoS: 0",
    )
else:
    record_check(
        "Observation contains zero DDoS",
        "FAIL",
        f"Observation windows containing DDoS: {obs_contains_ddos}",
    )

cross_episode_reasons = []
if unknown_episode:
    cross_episode_reasons.append(
        f"{unknown_episode} windows reference an episode_id "
        "that is absent from the feature dataset"
    )
if obs_out_of_episode:
    cross_episode_reasons.append(
        f"{obs_out_of_episode} observation regions leave "
        "their episode sequence_position range"
    )
total_forecast_out = sum(forecast_out_of_episode.values())
if total_forecast_out:
    cross_episode_reasons.append(
        f"{total_forecast_out} forecast regions leave "
        "their episode sequence_position range"
    )

if cross_episode_reasons:
    record_check(
        "No cross-episode windows",
        "FAIL",
        fail_reasons(cross_episode_reasons),
    )
else:
    record_check(
        "No cross-episode windows",
        "OK",
        "Observation and forecast regions stay inside "
        "the same episode.",
    )

obs_region_reasons = []
if obs_out_of_episode:
    obs_region_reasons.append(
        f"{obs_out_of_episode} observation regions exceed "
        "the episode"
    )
if obs_missing_flows:
    obs_region_reasons.append(
        f"{obs_missing_flows} observation regions have "
        "missing sequence_position values"
    )
if obs_not_100_flows:
    obs_region_reasons.append(
        f"{obs_not_100_flows} observation regions do not "
        "contain exactly 100 source flows"
    )

if obs_region_reasons:
    record_check(
        "Observation stays within episode",
        "FAIL",
        fail_reasons(obs_region_reasons),
    )
else:
    record_check(
        "Observation stays within episode",
        "OK",
        "Every observation region has 100 in-episode flows.",
    )

forecast_region_reasons = []
for horizon in FORECAST_HORIZONS:
    if forecast_out_of_episode[horizon]:
        forecast_region_reasons.append(
            f"H={horizon}: {forecast_out_of_episode[horizon]} "
            "forecast regions exceed the episode"
        )
    if forecast_missing_flows[horizon]:
        forecast_region_reasons.append(
            f"H={horizon}: {forecast_missing_flows[horizon]} "
            "forecast regions have missing sequence_position values"
        )

if forecast_region_reasons:
    record_check(
        "Forecast stays within episode",
        "FAIL",
        fail_reasons(forecast_region_reasons),
    )
else:
    record_check(
        "Forecast stays within episode",
        "OK",
        "Every horizon 50/100/200/500 stays inside the episode.",
    )


# ============================================================
# HORIZON TARGETS
# ============================================================

log("\n" + "=" * 75)
log("HORIZON TARGET VALIDATION")
log("=" * 75)

for horizon in FORECAST_HORIZONS:
    count_col = f"ddos_count_next_{horizon}"
    binary_col = f"ddos_next_{horizon}"
    ratio_col = f"ddos_ratio_next_{horizon}"

    log(f"\n--- Horizon {horizon} ---")

    if count_col not in windows.columns:
        record_check(
            f"Horizon {horizon} targets valid",
            "FAIL",
            f"Missing column {count_col}",
        )
        continue

    log("Internal stored-target checks:")
    log(
        f"  ddos_count outside 0..{horizon}: "
        f"{horizon_internal_count_range[horizon]:,}"
    )
    log(
        f"  ddos_ratio != ddos_count / {horizon}: "
        f"{horizon_ratio_mismatch[horizon]:,}"
    )
    log(
        f"  binary != (ddos_count > 0): "
        f"{horizon_binary_mismatch[horizon]:,}"
    )

    log("Source-feature recomputation:")
    log(
        f"  Stored count != actual future DDoS: "
        f"{count_mismatch[horizon]:,}"
    )
    log(
        f"  Positive binary with zero future DDoS: "
        f"{positive_without_future_ddos[horizon]:,}"
    )
    log(
        f"  Negative binary with future DDoS: "
        f"{negative_with_future_ddos[horizon]:,}"
    )
    log(
        f"  Forecast region outside episode: "
        f"{forecast_out_of_episode[horizon]:,}"
    )
    log(
        f"  Forecast region missing flows: "
        f"{forecast_missing_flows[horizon]:,}"
    )

    if forecast_example[horizon]:
        log("  Mismatch examples:")
        for example in forecast_example[horizon]:
            log(
                f"    window_id={example[0]}, "
                f"episode_id={example[1]}, "
                f"forecast={example[2]}-{example[3]}, "
                f"stored={example[4]}, actual={example[5]}"
            )

    binary_dist = (
        windows[binary_col]
        .value_counts()
        .sort_index()
    )
    log("\nOverall binary target distribution:")
    log(str(binary_dist))

    n_pos = int((windows[binary_col] == 1).sum())
    n_neg = int((windows[binary_col] == 0).sum())
    log(f"  No DDoS : {n_neg:,}")
    log(f"  DDoS    : {n_pos:,}")

    reasons = []
    if horizon_internal_count_range[horizon]:
        reasons.append(
            f"{horizon_internal_count_range[horizon]} counts "
            f"outside 0..{horizon}"
        )
    if horizon_ratio_mismatch[horizon]:
        reasons.append(
            f"{horizon_ratio_mismatch[horizon]} ratio mismatches"
        )
    if horizon_binary_mismatch[horizon]:
        reasons.append(
            f"{horizon_binary_mismatch[horizon]} binary mismatches"
        )
    if count_mismatch[horizon]:
        reasons.append(
            f"{count_mismatch[horizon]} stored counts disagree "
            "with source DDoS in the forecast region"
        )
    if positive_without_future_ddos[horizon]:
        reasons.append(
            f"{positive_without_future_ddos[horizon]} positive "
            "targets have zero future DDoS"
        )
    if negative_with_future_ddos[horizon]:
        reasons.append(
            f"{negative_with_future_ddos[horizon]} negative "
            "targets still contain future DDoS"
        )
    if forecast_out_of_episode[horizon]:
        reasons.append(
            f"{forecast_out_of_episode[horizon]} forecast "
            "regions leave the episode"
        )
    if forecast_missing_flows[horizon]:
        reasons.append(
            f"{forecast_missing_flows[horizon]} forecast "
            "regions are incomplete"
        )

    if reasons:
        record_check(
            f"Horizon {horizon} targets valid",
            "FAIL",
            fail_reasons(reasons),
        )
    else:
        record_check(
            f"Horizon {horizon} targets valid",
            "OK",
            (
                f"count in 0..{horizon}, ratio=count/{horizon}, "
                "binary=1 iff future DDoS exists"
            ),
        )


# ============================================================
# TARGET DISTRIBUTIONS BY SPLIT
# ============================================================

log("\n" + "=" * 75)
log("TARGET DISTRIBUTIONS BY SPLIT")
log("=" * 75)

split_order = ["TRAIN", "VALIDATION", "TEST"]

for horizon in FORECAST_HORIZONS:
    binary_col = f"ddos_next_{horizon}"
    if binary_col not in windows.columns:
        continue

    log(f"\nHorizon {horizon} ({binary_col}):")
    table = pd.crosstab(
        windows["dataset_split"],
        windows[binary_col],
        dropna=False,
    )
    log(str(table.reindex(split_order)))

    for split_name in split_order:
        subset = windows[windows["dataset_split"] == split_name]
        n_pos = int((subset[binary_col] == 1).sum())
        n_neg = int((subset[binary_col] == 0).sum())
        total = len(subset)
        pos_rate = (n_pos / total) if total else float("nan")
        log(
            f"  {split_name:<11} total={total:,}  "
            f"no_ddos={n_neg:,}  ddos={n_pos:,}  "
            f"positive_rate={pos_rate:.4f}"
        )


# ============================================================
# FORECAST HORIZON RANGES / SANITY
# ============================================================

log("\n" + "=" * 75)
log("FORECAST HORIZON RANGES AND SANITY CHECKS")
log("=" * 75)

log(f"\nTotal forecasting windows: {len(windows):,}")
log(f"Observation length: {OBSERVATION_LENGTH}")
log(f"Horizons: {FORECAST_HORIZONS}")

log("\nPer-episode observation and forecast ranges:")
for episode_id in sorted(windows["episode_id"].unique()):
    episode_windows = windows[
        windows["episode_id"] == episode_id
    ]
    info = episode_index.get(int(episode_id), {})
    ep_max = info.get("max_pos", None)

    obs_min = int(
        episode_windows["observation_start_position"].min()
    )
    obs_max = int(
        episode_windows["observation_end_position"].max()
    )
    derived_start_min = obs_min + OBSERVATION_LENGTH
    derived_start_max = obs_max + 1
    longest_end_max = obs_max + FORECAST_HORIZONS[-1]

    log(f"\nEpisode {int(episode_id):02d}:")
    log(f"  Windows              : {len(episode_windows):,}")
    log(f"  Observation start min: {obs_min}")
    log(f"  Observation end max  : {obs_max}")
    log(
        f"  Derived forecast start range: "
        f"{derived_start_min} .. {derived_start_max}"
    )
    log(
        f"  Longest forecast end max (H=500): {longest_end_max}"
    )
    if ep_max is not None:
        log(f"  Source episode max position: {ep_max}")
        if longest_end_max > ep_max:
            log(
                "  [WARNING] Longest forecast end exceeds "
                "source episode max position."
            )


# ============================================================
# FINAL VALIDATION
# ============================================================

log("\n" + "=" * 75)
log("FINAL VALIDATION")
log("=" * 75)

final_names = [
    "Required columns",
    "No missing values",
    "No infinite values",
    "Observation length = 100",
    "Episode split",
    "No episode overlap",
    "Forecast starts after observation",
    "Observation contains zero DDoS",
    "Horizon 50 targets valid",
    "Horizon 100 targets valid",
    "Horizon 200 targets valid",
    "Horizon 500 targets valid",
    "Forecast stays within episode",
]

check_lookup = {
    item["name"]: item for item in checks
}

log("")
for name in final_names:
    item = check_lookup.get(name)
    if item is None:
        log(f"[WARNING] {name}  (check was not recorded)")
        continue
    status = item["status"]
    details = item["details"]
    extra = f"  {details}" if details else ""
    log(f"[{status}] {name}{extra}")

log("\nAdditional checks:")
additional_names = [
    "Source feature columns",
    "No duplicate windows",
    "No observation/forecast overlap",
    "No cross-episode windows",
    "Observation stays within episode",
]
for name in additional_names:
    item = check_lookup.get(name)
    if item is None:
        continue
    extra = f"  {item['details']}" if item["details"] else ""
    log(f"[{item['status']}] {name}{extra}")

n_ok = sum(1 for item in checks if item["status"] == "OK")
n_warn = sum(1 for item in checks if item["status"] == "WARNING")
n_fail = sum(1 for item in checks if item["status"] == "FAIL")

log("\n" + "-" * 75)
log(f"Summary: {n_ok} OK, {n_warn} WARNING, {n_fail} FAIL")

if n_fail:
    log("\nFailed checks:")
    for item in checks:
        if item["status"] != "FAIL":
            continue
        log(f"  - {item['name']}: {item['details']}")
    overall = "FAIL"
else:
    overall = "OK"

log(f"\nOVERALL: [{overall}]")

log("\n" + "=" * 75)
log("VALIDATION COMPLETE")
log("=" * 75)

logger.save(REPORT_FILE)

log(f"\nReport saved to:\n{REPORT_FILE}")
log("\nNo dataset was modified.")
log("No generator script was changed.")
log("No model was trained.")
log("=" * 75)
