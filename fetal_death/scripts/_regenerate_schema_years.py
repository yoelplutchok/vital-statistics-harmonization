#!/usr/bin/env python3
"""Regenerate the `years_available` column of `fetal_death/harmonized_schema.csv`
from the actual non-blank year coverage in the harmonized parquet.

Background
----------
The schema CSV historically used a five-sub-era shorthand mixed with literal
year ranges, applied inconsistently — 36 of 73 rows did not match the data
under a literal interpretation (AUDIT_PUBLICATION_REPORT_2 finding F1). This
script writes the canonical literal-year-range form for every column.

Usage
-----
    python fetal_death/scripts/_regenerate_schema_years.py            # rewrite in place
    python fetal_death/scripts/_regenerate_schema_years.py --check    # exit 1 on drift

A pytest test (`test_schema_years_available_matches_data` in
`fetal_death/tests/test_release_smoke.py`) runs the same computation and locks
the schema in CI.

Monorepo paths
--------------
This module is the monorepo-adapted sibling of the standalone-build
`scripts/_regenerate_schema_years.py`. Monorepo layout differs: the parquet
lives at `<monorepo_root>/output/harmonized/` (via symlinks), and the schema
CSV is at `fetal_death/harmonized_schema.csv` (flat — no `metadata/` subdir).
Copied 2026-05-12 per C8.1 DO-1 (path-drift fix for monorepo migration).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

_SUBPROJECT_ROOT = Path(__file__).resolve().parent.parent
_MONOREPO_ROOT = _SUBPROJECT_ROOT.parent
HARMONIZED_PARQUET = _MONOREPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"
SCHEMA_CSV = _SUBPROJECT_ROOT / "harmonized_schema.csv"


def years_to_canonical_string(years: set[int]) -> str:
    """Format a set of int years as "1992-2002, 2005-2022" style."""
    if not years:
        return ""
    sorted_years = sorted(int(y) for y in years)
    spans: list[str] = []
    start = prev = sorted_years[0]
    for y in sorted_years[1:]:
        if y == prev + 1:
            prev = y
        else:
            spans.append(f"{start}-{prev}" if start != prev else str(start))
            start = prev = y
    spans.append(f"{start}-{prev}" if start != prev else str(start))
    return ", ".join(spans)


def compute_years_available(df: pd.DataFrame) -> dict[str, str]:
    """For each column, return the canonical non-blank-year-range string."""
    out: dict[str, str] = {}
    for col in df.columns:
        if col == "data_year":
            years = set(int(y) for y in df["data_year"].unique())
        else:
            series = df[col]
            if series.dtype == object:
                non_blank = series.notna() & (series.astype(str).str.strip() != "")
            else:
                non_blank = series.notna()
            years = set(int(y) for y in df.loc[non_blank, "data_year"].unique())
        out[col] = years_to_canonical_string(years)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the schema would change instead of writing it.",
    )
    args = parser.parse_args()

    if not HARMONIZED_PARQUET.exists():
        sys.exit(
            f"{HARMONIZED_PARQUET} not present. Run the pipeline first "
            "(fetal_death/scripts/01_import → 03_harmonize)."
        )

    df = pd.read_parquet(HARMONIZED_PARQUET)
    canonical = compute_years_available(df)

    schema = pd.read_csv(SCHEMA_CSV)
    drifted: list[tuple[str, str, str]] = []
    new_values: list[str] = []
    for _, row in schema.iterrows():
        name = row["harmonized_name"]
        target = canonical.get(name, "")
        current = "" if pd.isna(row["years_available"]) else str(row["years_available"])
        if current != target:
            drifted.append((name, current, target))
        new_values.append(target)

    if not drifted:
        print(f"OK: schema years_available matches data for all {len(schema)} columns.")
        return

    print(f"Drift detected for {len(drifted)} column(s):")
    for name, current, target in drifted:
        print(f"  {name}")
        print(f"    current: {current!r}")
        print(f"    target:  {target!r}")

    if args.check:
        sys.exit(1)

    schema["years_available"] = new_values
    schema.to_csv(SCHEMA_CSV, index=False)
    print(f"\nWrote {SCHEMA_CSV} with corrected years_available column.")


if __name__ == "__main__":
    main()
