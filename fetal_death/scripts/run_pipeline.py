#!/usr/bin/env python3
"""End-to-end pipeline runner: parse 29 NCHS fetal-death zips and produce
the V2.0 harmonized + derived parquets.

Stages
------
  1. Parse each yearly zip into output/yearly_clean/fetal_death_{year}_raw.parquet
  2. Harmonize all years into output/harmonized/fetal_death_harmonized.parquet
  3. Derive 16 indicators into output/harmonized/fetal_death_derived.parquet
  4. Run external validation against NVSR 57-08 / NVSR 73-09

Usage
-----
    python scripts/run_pipeline.py            # run everything
    python scripts/run_pipeline.py --skip-parse   # reuse existing yearly_clean
    python scripts/run_pipeline.py --years 2014 2015  # parse a subset, then re-harmonize+derive

Prerequisites
-------------
- raw_data/fetal_death/Fetal{YYYY}US.zip for 1992-2013
- raw_data/fetal_death/Fetal{YYYY}US_COD.zip for 2014-2022
- pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "raw_data/fetal_death"
YEARLY_DIR = REPO_ROOT / "output/yearly_clean"
HARMONIZED_DIR = REPO_ROOT / "output/harmonized"

V2_YEARS = list(range(1992, 2003))         # 1989-revision uniform
V1_PRE_COD_YEARS = list(range(2005, 2014)) # mixed A/S, no COD
V1_COD_YEARS = list(range(2014, 2023))     # COD variant
ALL_YEARS = V2_YEARS + V1_PRE_COD_YEARS + V1_COD_YEARS  # 29 years; 2003-2004 deferred


def _zip_path(year: int) -> Path:
    """Map a year to its NCHS zip filename. 2014+ uses the _COD variant."""
    suffix = "US_COD.zip" if year >= 2014 else "US.zip"
    return RAW_DIR / f"Fetal{year}{suffix}"


def _run(cmd: list[str]) -> None:
    print(f"\n+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def parse_year(year: int) -> None:
    zip_path = _zip_path(year)
    if not zip_path.exists():
        sys.exit(f"missing {zip_path} — download from CDC FTP before running.")
    out = YEARLY_DIR / f"fetal_death_{year}_raw.parquet"
    YEARLY_DIR.mkdir(parents=True, exist_ok=True)
    _run([
        sys.executable, "scripts/01_import/parse_fetal_year.py",
        "--zip", str(zip_path),
        "--year", str(year),
        "--out", str(out),
    ])


def harmonize(years: list[int]) -> None:
    HARMONIZED_DIR.mkdir(parents=True, exist_ok=True)
    out = HARMONIZED_DIR / "fetal_death_harmonized.parquet"
    _run([
        sys.executable, "scripts/03_harmonize/harmonize.py",
        "--years", *map(str, years),
        "--out", str(out),
    ])


def derive() -> None:
    inp = HARMONIZED_DIR / "fetal_death_harmonized.parquet"
    out = HARMONIZED_DIR / "fetal_death_derived.parquet"
    _run([
        sys.executable, "scripts/04_derive/derive.py",
        "--input", str(inp),
        "--out", str(out),
    ])


def validate() -> None:
    _run([sys.executable, "scripts/05_validate/validate_external_v2.py"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--years", type=int, nargs="*", default=ALL_YEARS,
        help="Years to parse (default: all 29). Harmonize+derive always run on the full set.",
    )
    parser.add_argument("--skip-parse", action="store_true", help="Reuse existing yearly parquets.")
    parser.add_argument("--skip-validate", action="store_true", help="Skip the external validation step.")
    args = parser.parse_args()

    if not args.skip_parse:
        for y in args.years:
            parse_year(y)

    harmonize(ALL_YEARS)
    derive()

    if not args.skip_validate:
        validate()

    print("\nDone. Artifacts:")
    print(f"  {HARMONIZED_DIR / 'fetal_death_harmonized.parquet'}")
    print(f"  {HARMONIZED_DIR / 'fetal_death_derived.parquet'}")


if __name__ == "__main__":
    main()
