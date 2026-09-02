"""
SIH26153 — Day 1 (Pragati): Dataset exploration + feature documentation
-------------------------------------------------------------------------
Usage:
    1. Download CICIDS2017 CSVs (or NSL-KDD .txt/.csv) into a local folder,
       e.g. ./data/CICIDS2017/
    2. pip install pandas numpy
    3. python explore_dataset.py --data_dir ./data/CICIDS2017 --dataset cicids2017

For CICIDS2017, the 8 daily files are typically named like:
    Monday-WorkingHours.pcap_ISCX.csv
    Tuesday-WorkingHours.pcap_ISCX.csv
    Wednesday-workingHours.pcap_ISCX.csv
    Thursday-...-WebAttacks.pcap_ISCX.csv
    Thursday-...-Infilteration.pcap_ISCX.csv
    Friday-...-DDos.pcap_ISCX.csv
    Friday-...-PortScan.pcap_ISCX.csv
    Friday-...-Morning.pcap_ISCX.csv

For NSL-KDD, use KDDTrain+.txt and KDDTest+.txt (no header row — 41 features
+ label + difficulty; column names are added manually, see NSL_KDD_COLUMNS below).
"""

import argparse
import glob
import os
import pandas as pd
import numpy as np

# NSL-KDD has no header row in the raw files — official 41 feature names + label + difficulty
NSL_KDD_COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "attack_type", "difficulty_level"
]


def load_cicids2017(data_dir: str) -> pd.DataFrame:
    """Load and concatenate all CICIDS2017 daily CSVs in a folder."""
    files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")
    print(f"Found {len(files)} CSV file(s):")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        # CICIDS2017 columns often have leading/trailing whitespace
        df.columns = df.columns.str.strip()
        df["__source_file__"] = os.path.basename(f)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_nsl_kdd(data_dir: str) -> pd.DataFrame:
    """Load NSL-KDD train/test text files (no header)."""
    files = sorted(glob.glob(os.path.join(data_dir, "*.txt"))) + \
            sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No NSL-KDD files found in {data_dir}")
    frames = []
    for f in files:
        df = pd.read_csv(f, header=None, names=NSL_KDD_COLUMNS)
        df["__source_file__"] = os.path.basename(f)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def document_features(df: pd.DataFrame, label_col: str, out_path: str):
    """Generate a Markdown feature documentation report."""
    lines = []
    lines.append("# Feature Documentation\n")
    lines.append(f"- Total rows: **{len(df):,}**")
    lines.append(f"- Total columns: **{df.shape[1]}**")
    if label_col in df.columns:
        lines.append(f"- Label column: `{label_col}`")
        lines.append(f"- Class distribution:\n")
        counts = df[label_col].value_counts()
        lines.append("| Class | Count | % |")
        lines.append("|---|---|---|")
        for cls, cnt in counts.items():
            lines.append(f"| {cls} | {cnt:,} | {cnt/len(df)*100:.2f}% |")
    lines.append("\n## Column Summary\n")
    lines.append("| # | Column | Dtype | Non-Null | Nulls | Unique | Min | Max |")
    lines.append("|---|---|---|---|---|---|---|---|")

    for i, col in enumerate(df.columns, start=1):
        s = df[col]
        non_null = s.notna().sum()
        nulls = s.isna().sum()
        unique = s.nunique()
        try:
            col_min = f"{s.min():.3g}" if pd.api.types.is_numeric_dtype(s) else str(s.dropna().unique()[:1])
            col_max = f"{s.max():.3g}" if pd.api.types.is_numeric_dtype(s) else ""
        except Exception:
            col_min, col_max = "", ""
        lines.append(f"| {i} | {col} | {s.dtype} | {non_null:,} | {nulls:,} | {unique:,} | {col_min} | {col_max} |")

    # Flag potential data quality issues
    lines.append("\n## Data Quality Notes\n")
    inf_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and np.isinf(df[c]).any()]
    null_cols = [c for c in df.columns if df[c].isna().any()]
    const_cols = [c for c in df.columns if df[c].nunique() <= 1]
    lines.append(f"- Columns with infinite values: {inf_cols if inf_cols else 'None'}")
    lines.append(f"- Columns with missing values: {null_cols if null_cols else 'None'}")
    lines.append(f"- Constant / zero-variance columns (candidates to drop): {const_cols if const_cols else 'None'}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nFeature documentation written to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Explore and document network attack dataset structure")
    parser.add_argument("--data_dir", required=True, help="Folder containing dataset files")
    parser.add_argument("--dataset", choices=["cicids2017", "nslkdd"], required=True)
    parser.add_argument("--out", default="feature_documentation.md")
    args = parser.parse_args()

    if args.dataset == "cicids2017":
        df = load_cicids2017(args.data_dir)
        label_col = "Label"
    else:
        df = load_nsl_kdd(args.data_dir)
        label_col = "attack_type"

    print("\n=== Shape ===")
    print(df.shape)

    print("\n=== First 5 rows ===")
    print(df.head())

    print("\n=== Dtypes ===")
    print(df.dtypes.value_counts())

    document_features(df, label_col, args.out)


if __name__ == "__main__":
    main()
