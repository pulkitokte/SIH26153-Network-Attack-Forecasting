import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "raw" / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"

print("=" * 75)
print("CICIDS2017 - DDoS SEQUENCE / LABEL BOUNDARY ANALYSIS")
print("=" * 75)

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

df.columns = df.columns.str.strip()
df["Label"] = df["Label"].astype(str).str.strip()

print(f"\nTotal rows: {len(df):,}")

# ---------------------------------------------------------
# Basic label runs
# ---------------------------------------------------------

labels = df["Label"].tolist()

runs = []

start = 0
current_label = labels[0]

for i in range(1, len(labels)):

    if labels[i] != current_label:

        runs.append({
            "label": current_label,
            "start": start,
            "end": i - 1,
            "length": i - start
        })

        start = i
        current_label = labels[i]

# Final run
runs.append({
    "label": current_label,
    "start": start,
    "end": len(labels) - 1,
    "length": len(labels) - start
})

# ---------------------------------------------------------
# Print runs
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("LABEL RUNS")
print("=" * 75)

print(f"\nTotal contiguous label regions: {len(runs)}")

for number, run in enumerate(runs, start=1):

    print(
        f"{number:03d}. "
        f"{run['label']:<10} "
        f"start={run['start']:<8,} "
        f"end={run['end']:<8,} "
        f"length={run['length']:,}"
    )

# ---------------------------------------------------------
# DDoS regions
# ---------------------------------------------------------

ddos_runs = [
    run for run in runs
    if run["label"].lower() == "ddos"
]

print("\n" + "=" * 75)
print("DDoS REGIONS")
print("=" * 75)

print(f"\nNumber of DDoS regions: {len(ddos_runs)}")

for number, run in enumerate(ddos_runs, start=1):

    print(
        f"DDoS region {number}: "
        f"rows {run['start']:,} → {run['end']:,} "
        f"({run['length']:,} flows)"
    )

# ---------------------------------------------------------
# Transition points
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("LABEL TRANSITIONS")
print("=" * 75)

transitions = []

for i in range(1, len(labels)):

    if labels[i] != labels[i - 1]:

        transitions.append({
            "row": i,
            "from": labels[i - 1],
            "to": labels[i]
        })

print(f"\nTotal transitions: {len(transitions)}")

for transition in transitions:

    print(
        f"Row {transition['row']:,}: "
        f"{transition['from']} → {transition['to']}"
    )

# ---------------------------------------------------------
# DDoS boundaries
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("DDoS BOUNDARIES")
print("=" * 75)

first_ddos = df.index[df["Label"] == "DDoS"].min()
last_ddos = df.index[df["Label"] == "DDoS"].max()

print(f"\nFirst DDoS row : {first_ddos:,}")
print(f"Last DDoS row  : {last_ddos:,}")

# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

REPORT_FILE = BASE_DIR / "reports" / "ddos_sequence_analysis.txt"

with open(REPORT_FILE, "w", encoding="utf-8") as report:

    report.write("=" * 75 + "\n")
    report.write("CICIDS2017 - DDoS SEQUENCE / LABEL BOUNDARY ANALYSIS\n")
    report.write("=" * 75 + "\n\n")

    report.write(f"Total rows: {len(df):,}\n")
    report.write(f"Total contiguous label regions: {len(runs)}\n\n")

    report.write("LABEL RUNS\n")
    report.write("-" * 75 + "\n")

    for number, run in enumerate(runs, start=1):

        report.write(
            f"{number:03d}. "
            f"{run['label']:<10} "
            f"start={run['start']:<8,} "
            f"end={run['end']:<8,} "
            f"length={run['length']:,}\n"
        )

    report.write("\nDDoS REGIONS\n")
    report.write("-" * 75 + "\n")

    for number, run in enumerate(ddos_runs, start=1):

        report.write(
            f"DDoS region {number}: "
            f"rows {run['start']:,} → {run['end']:,} "
            f"({run['length']:,} flows)\n"
        )

    report.write("\nLABEL TRANSITIONS\n")
    report.write("-" * 75 + "\n")

    for transition in transitions:

        report.write(
            f"Row {transition['row']:,}: "
            f"{transition['from']} → {transition['to']}\n"
        )

    report.write("\nDDoS BOUNDARIES\n")
    report.write("-" * 75 + "\n")

    report.write(f"First DDoS row: {first_ddos:,}\n")
    report.write(f"Last DDoS row: {last_ddos:,}\n")

print("\n" + "=" * 75)
print("ANALYSIS COMPLETE")
print("=" * 75)

print(f"\nReport saved to:")
print(REPORT_FILE)

print("\nOriginal dataset was NOT modified.")