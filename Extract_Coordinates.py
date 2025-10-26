#!/usr/bin/env python3
"""
extract_coords_fixed_simple.py

Simple parser for TRC.out-style files. Edit the INPUT_PATH and OUTPUT_JSON
variables below (and set WRITE_CSV True/False) before running.

Behavior:
- Looks for lines containing "ROW NUMBER" and "SECTION NUMBER" and one of:
    "X COORDINATES"
    "R_THETA OF UPPER BLADE SURFACE"
    "BLADE TANGENTIAL THICKNESS"
    "STREAM SURFACE RADIUS"
- Skips header metadata lines like "FAC1, XSHIFT = 1.00000000 0.00000000"
- Collects consecutive numeric-only lines and stores them as flat float lists
- Writes JSON to OUTPUT_JSON. Optionally writes per-block CSVs under CSV_DIR.
"""

from pathlib import Path
import re
import json
import csv
import sys

# -----------------------------
# USER CONFIGURE PATHS HERE
# -----------------------------
# Put the input file path here. On Windows either use forward slashes or raw strings:
# e.g. Path(r"C:\Users\samar\Downloads\TRC.out") or Path("C:/Users/samar/Downloads/TRC.out")
INPUT_PATH = Path("C:/Users/samar/Downloads/TRC.out")

# Output JSON path (where to write extracted JSON)
OUTPUT_JSON = Path("C:/Users/samar/Downloads/extracted_coords_fixed.json")

# If True, CSVs will be written to the same folder as OUTPUT_JSON with suffix "_csv"
WRITE_CSV = True

# -----------------------------
# Internal config (do not edit)
# -----------------------------
TARGET_LABELS = [
    "X  COORDINATES",
    "R_THETA OF UPPER BLADE SURFACE",
    "BLADE TANGENTIAL THICKNESS",
    "STREAM SURFACE RADIUS"
]

FLOAT_RE = re.compile(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?")

def contains_nonexp_letters(s: str) -> bool:
    """Return True if the string contains alphabetic letters other than 'E'/'e'."""
    return bool(re.search(r'[A-DF-Za-df-z]', s))

def is_numeric_data_line(s: str) -> bool:
    """True if the line likely contains only numeric data to be collected."""
    if '=' in s:
        return False
    if contains_nonexp_letters(s):
        return False
    return bool(FLOAT_RE.search(s))

def parse_trc_file(path: Path):
    """Parse the file and return (data_dict, found_any_flag)."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    text = path.read_text()
    lines = text.splitlines()
    data = {}
    n = len(lines)
    i = 0
    found_any = False

    while i < n:
        up = lines[i].upper()
        if "ROW NUMBER" in up and "SECTION NUMBER" in up:
            # parse row and section numbers
            mr = re.search(r"ROW NUMBER\s+(\d+)", up)
            ms = re.search(r"SECTION NUMBER\s+(\d+)", up)
            rownum = mr.group(1) if mr else "UNKNOWN"
            secnum = ms.group(1) if ms else "UNKNOWN"

            # find the target label on same line or next line
            found_label = None
            for lab in TARGET_LABELS:
                if lab in up:
                    found_label = lab
                    break
            if not found_label and (i + 1) < n:
                nextup = lines[i+1].upper()
                for lab in TARGET_LABELS:
                    if lab in nextup:
                        found_label = lab
                        i += 1  # advance to the label line
                        break
            if not found_label:
                i += 1
                continue

            # skip metadata lines (like "FAC1, XSHIFT = ...") until numeric-only data starts
            j = i + 1
            while j < n and not is_numeric_data_line(lines[j]):
                j += 1

            # collect consecutive numeric-only lines
            nums = []
            while j < n and is_numeric_data_line(lines[j]):
                for tok in FLOAT_RE.findall(lines[j]):
                    try:
                        nums.append(float(tok))
                    except Exception:
                        pass
                j += 1

            # store parsed numbers
            found_any = True
            rkey = f"row_{rownum}"
            skey = f"section_{secnum}"
            data.setdefault(rkey, {})
            data[rkey].setdefault(skey, {})
            data[rkey][skey][found_label] = nums

            # continue scanning from j
            i = j
            continue

        i += 1

    return data, found_any

def write_csv_blocks(data: dict, out_dir: Path):
    """Write one CSV per (row,section,label) under out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for rkey, rdict in data.items():
        for skey, sdict in rdict.items():
            for label, arr in sdict.items():
                safe_label = label.replace(" ", "_").replace("/", "_")
                fname = f"{rkey}__{skey}__{safe_label}.csv"
                with (out_dir / fname).open("w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([label])
                    for v in arr:
                        writer.writerow([v])

def main():
    try:
        data, ok = parse_trc_file(INPUT_PATH)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    if not ok:
        print("No coordinate blocks found in the input file for the requested labels.", file=sys.stderr)
        sys.exit(3)

    # write JSON
    OUTPUT_JSON.write_text(json.dumps(data, indent=2))
    print(f"Wrote extracted JSON to: {OUTPUT_JSON}")

    # optionally write CSVs
    if WRITE_CSV:
        csv_dir = OUTPUT_JSON.parent / (OUTPUT_JSON.stem + "_csv")
        write_csv_blocks(data, csv_dir)
        print(f"Wrote CSVs to directory: {csv_dir}")

    # print short summary
    print("Summary:")
    for rkey, rdict in data.items():
        print(f"  {rkey}:")
        for skey, sdict in rdict.items():
            print(f"    {skey}:")
            for label, arr in sdict.items():
                preview = arr[:8]
                print(f"      {label:30s} -> {len(arr)} values; first 8: {preview}")

if __name__ == "__main__":
    main()
