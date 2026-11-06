#!/usr/bin/env python3
"""Validate a catalogue CSV before it is published.

Usage: validate.py <facebook|tiktok> <new.csv> <previous.csv>
Exit 0 = safe to publish, 1 = keep the previously published file.
"""
import csv
import os
import sys

REQUIRED = {
    "facebook": [
        "vehicle_id", "title", "description", "price", "image[0].url", "url",
        "body_style", "make", "model", "year", "vin",
    ],
    "tiktok": ["vehicle_id"],
}
MIN_RATIO = 0.5  # new feed must hold at least 50% of the previously published row count


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return reader.fieldnames or [], rows


def fail(msg):
    print(f"VALIDATION FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in REQUIRED:
        fail("usage: validate.py <facebook|tiktok> <new.csv> <previous.csv>")
    kind, new_path, old_path = sys.argv[1:4]

    header, rows = read_rows(new_path)
    missing = [c for c in REQUIRED[kind] if c not in header]
    if missing:
        fail(f"missing columns {missing} (got HTML or a changed template?)")
    if not rows:
        fail("no data rows")

    ids = [r.get("vehicle_id", "").strip() for r in rows]
    if any(not i for i in ids):
        fail("rows with empty vehicle_id")
    if len(set(ids)) != len(ids):
        fail("duplicate vehicle_id values")
    if kind == "facebook" and any(not r.get("url", "").strip() for r in rows):
        fail("rows with empty url")

    if os.path.exists(old_path):
        try:
            _, old_rows = read_rows(old_path)
        except Exception:
            old_rows = []
        if old_rows and len(rows) < MIN_RATIO * len(old_rows):
            fail(f"row count dropped from {len(old_rows)} to {len(rows)}")

    print(f"OK: {len(rows)} vehicles, {len(header)} columns ({kind})")


if __name__ == "__main__":
    main()
