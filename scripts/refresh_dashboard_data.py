r"""
refresh_dashboard_data.py

Reads the refurbishment tracker Excel file (from your OneDrive folder on this
laptop) and writes dashboard_data.json in the repo root. The dashboard page
(index.html) reads that JSON.

Run it directly to test:  python scripts\refresh_dashboard_data.py
"""

import datetime
import json
import os
import shutil
import sys
import tempfile
import time
import warnings

warnings.filterwarnings("ignore")  # openpyxl warns about Excel extensions it ignores

try:
    from openpyxl import load_workbook
except ImportError:
    print("[refresh] ERROR: openpyxl is not installed. Run:  pip install openpyxl")
    sys.exit(1)

# ---------------------------------------------------------------------------
# SETTINGS - change these to match your laptop
# ---------------------------------------------------------------------------

# Full path to the tracker in your synced OneDrive folder.
# Tip: in File Explorer, Shift + right-click the file -> "Copy as path", paste
# it between the quotes below and remove the outer quote marks it adds.
TRACKER_PATH = r"C:\Users\engin\OneDrive\002.Operations\Refurbishment_Tracker (2).xlsx"

# Set to False to leave rand stock values out of the public data file.
INCLUDE_VALUES = True

# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO_ROOT, "dashboard_data.json")
TRACKER_PATH = os.environ.get("TRACKER_PATH", TRACKER_PATH)

COLUMNS = {
    "Job ID": "job_id", "SKU": "sku", "Product": "product", "Brand": "brand",
    "Unit": "unit", "Unit Stock Value (R)": "value", "Category": "category",
    "Assigned To": "team", "Date Allocated": "date_allocated",
    "Target Date": "target_date", "Status": "status",
    "Parts Required": "parts_required", "Parts Ordered": "parts_ordered",
    "Parts Received": "parts_received", "Date Completed": "date_completed",
    "Notes": "notes",
}
DATE_FIELDS = {"date_allocated", "target_date", "parts_ordered", "parts_received", "date_completed"}


def clean(value, field):
    if value is None:
        return None
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime("%Y-%m-%d")
    if field == "value":
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None
    if field in DATE_FIELDS and isinstance(value, (int, float)):
        # Excel date serial stored as a number
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(value))).isoformat()
    text = str(value).strip()
    return text or None


def open_workbook(path):
    """Copy the file first, so reading works even while Excel has it open."""
    last_error = None
    for _ in range(3):
        try:
            tmp_dir = tempfile.mkdtemp()
            tmp = os.path.join(tmp_dir, "tracker.xlsx")
            shutil.copy2(path, tmp)
            return load_workbook(tmp, data_only=True, read_only=True)
        except Exception as error:  # file busy while OneDrive syncs, etc.
            last_error = error
            time.sleep(5)
    raise last_error


def main():
    if not os.path.exists(TRACKER_PATH):
        print(f"[refresh] ERROR: tracker not found at:\n  {TRACKER_PATH}\n"
              "Check TRACKER_PATH at the top of this script.")
        sys.exit(1)

    wb = open_workbook(TRACKER_PATH)
    if "Tracker" not in wb.sheetnames:
        print("[refresh] ERROR: the workbook has no sheet called 'Tracker'.")
        sys.exit(1)

    # Find the header row (the one that starts with "Job ID")
    rows = list(wb["Tracker"].iter_rows(values_only=True))
    header_index = next((i for i, r in enumerate(rows) if r and str(r[0] or "").strip() == "Job ID"), None)
    if header_index is None:
        print("[refresh] ERROR: no 'Job ID' header row on the Tracker sheet.")
        sys.exit(1)
    header = [str(h).strip() if h is not None else "" for h in rows[header_index]]
    positions = {field: header.index(name) for name, field in COLUMNS.items() if name in header}

    units = []
    for row in rows[header_index + 1:]:
        if not row or row[0] is None or not str(row[0]).strip():
            continue
        unit = {field: clean(row[pos] if pos < len(row) else None, field) for field, pos in positions.items()}
        if not INCLUDE_VALUES:
            unit.pop("value", None)
        units.append(unit)

    # Team names from the Lists sheet (column A, below "Teams")
    teams = []
    if "Lists" in wb.sheetnames:
        started = False
        for (cell,) in wb["Lists"].iter_rows(min_col=1, max_col=1, values_only=True):
            text = str(cell).strip() if cell is not None else ""
            if not started:
                started = text == "Teams"
                continue
            if not text or text.lower().startswith("rename"):
                break
            teams.append(text)

    modified = datetime.datetime.fromtimestamp(os.path.getmtime(TRACKER_PATH)).astimezone()
    data = {
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "file_modified": modified.isoformat(timespec="seconds"),
        "source_file": os.path.basename(TRACKER_PATH),
        "include_values": INCLUDE_VALUES,
        "teams": teams,
        "units": units,
    }

    # Only rewrite the file when the tracker content changed, so git sees no
    # change (and nothing gets pushed) when nobody edited the tracker.
    if os.path.exists(OUTPUT):
        try:
            with open(OUTPUT, encoding="utf-8") as f:
                old = json.load(f)
            if old.get("units") == units and old.get("teams") == teams and old.get("include_values") == INCLUDE_VALUES:
                print(f"[refresh] Tracker unchanged ({len(units)} units).")
                return
        except Exception:
            pass

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"[refresh] Wrote {len(units)} units and {len(teams)} teams to dashboard_data.json")


if __name__ == "__main__":
    main()
