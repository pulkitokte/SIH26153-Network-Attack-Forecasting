import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

REPORT_FILE = REPORT_DIR / "label_inventory.txt"

CHUNK_SIZE = 50_000

print("=" * 75)
print("CICIDS2017 - COMPLETE LABEL INVENTORY")
print("=" * 75)

print(f"\nRaw data folder:")
print(RAW_DIR)

if not RAW_DIR.exists():
    raise FileNotFoundError(f"Raw folder not found: {RAW_DIR}")

csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV files found inside raw folder.")

print(f"\nCSV files found: {len(csv_files)}")

# ---------------------------------------------------------
# Overall counters
# ---------------------------------------------------------

overall_labels = {}
overall_rows = 0

# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

with open(REPORT_FILE, "w", encoding="utf-8") as report:

    report.write("=" * 75 + "\n")
    report.write("CICIDS2017 - COMPLETE LABEL INVENTORY\n")
    report.write("=" * 75 + "\n\n")

    # -----------------------------------------------------
    # Process every CSV
    # -----------------------------------------------------

    for file_number, csv_file in enumerate(csv_files, start=1):

        print("\n" + "-" * 75)
        print(f"[{file_number}/{len(csv_files)}] Processing:")
        print(csv_file.name)
        print("-" * 75)

        report.write("\n" + "-" * 75 + "\n")
        report.write(f"FILE: {csv_file.name}\n")
        report.write("-" * 75 + "\n")

        file_rows = 0
        file_labels = {}

        first_chunk = True

        try:

            for chunk in pd.read_csv(
                csv_file,
                low_memory=False,
                chunksize=CHUNK_SIZE
            ):

                # Clean column names
                chunk.columns = chunk.columns.str.strip()

                if "Label" not in chunk.columns:
                    raise ValueError(
                        f"'Label' column not found in {csv_file.name}"
                    )

                # Clean labels
                labels = chunk["Label"].astype(str).str.strip()

                # Count rows
                file_rows += len(chunk)

                # Count labels in this chunk
                counts = labels.value_counts()

                for label, count in counts.items():

                    file_labels[label] = (
                        file_labels.get(label, 0) + int(count)
                    )

                    overall_labels[label] = (
                        overall_labels.get(label, 0) + int(count)
                    )

                # Print header information only once
                if first_chunk:
                    print(f"Columns: {len(chunk.columns)}")
                    first_chunk = False

        except Exception as error:

            print(f"ERROR processing {csv_file.name}")
            print(error)

            report.write(f"ERROR: {error}\n")
            continue

        overall_rows += file_rows

        # -------------------------------------------------
        # Display file results
        # -------------------------------------------------

        print(f"Rows: {file_rows:,}")
        print("\nLabels:")

        report.write(f"Rows: {file_rows:,}\n\n")
        report.write("Labels:\n")

        for label, count in sorted(
            file_labels.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            percentage = (count / file_rows) * 100

            print(
                f"  {label:<35} "
                f"{count:>12,} "
                f"({percentage:>6.2f}%)"
            )

            report.write(
                f"  {label:<35} "
                f"{count:>12,} "
                f"({percentage:>6.2f}%)\n"
            )

    # -----------------------------------------------------
    # Overall results
    # -----------------------------------------------------

    print("\n")
    print("=" * 75)
    print("OVERALL CICIDS2017 LABEL DISTRIBUTION")
    print("=" * 75)

    report.write("\n\n")
    report.write("=" * 75 + "\n")
    report.write("OVERALL CICIDS2017 LABEL DISTRIBUTION\n")
    report.write("=" * 75 + "\n\n")

    print(f"\nTotal rows across all files: {overall_rows:,}")

    report.write(
        f"Total rows across all files: {overall_rows:,}\n\n"
    )

    for label, count in sorted(
        overall_labels.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        percentage = (count / overall_rows) * 100

        print(
            f"{label:<35} "
            f"{count:>12,} "
            f"({percentage:>6.2f}%)"
        )

        report.write(
            f"{label:<35} "
            f"{count:>12,} "
            f"({percentage:>6.2f}%)\n"
        )

    # -----------------------------------------------------
    # Unique labels
    # -----------------------------------------------------

    print("\n")
    print("=" * 75)
    print("UNIQUE LABELS FOUND")
    print("=" * 75)

    report.write("\n\n")
    report.write("=" * 75 + "\n")
    report.write("UNIQUE LABELS FOUND\n")
    report.write("=" * 75 + "\n\n")

    for label in sorted(overall_labels):

        print(f"  - {label}")
        report.write(f"  - {label}\n")

print("\n")
print("=" * 75)
print("INVENTORY COMPLETE")
print("=" * 75)

print(f"\nReport saved to:")
print(REPORT_FILE)

print("\nOriginal dataset was NOT modified.")
print("=" * 75)