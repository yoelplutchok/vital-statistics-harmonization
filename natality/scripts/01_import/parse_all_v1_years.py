#!/usr/bin/env python3
"""
Parse natality years from raw_data/Nat{year}us.zip (or Nat{year}.zip for 1990-1993)
into output/yearly_clean/natality_{year}_core.parquet.

Uses chunked Parquet writes (default 250k rows) to keep memory bounded.

Usage (from repo root or this directory):
  python parse_all_v1_years.py
  python parse_all_v1_years.py --years 1990-2004 --chunk-rows 300000
  python parse_all_v1_years.py --years 2005-2015
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parents[1]
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from parse_public_us_year import run_parse


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--raw-dir",
        type=Path,
        default=_REPO_ROOT / "raw_data",
        help="Directory containing Nat{year}us.zip",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "yearly_clean",
        help="Directory for natality_{year}_core.parquet",
    )
    p.add_argument(
        "--years",
        type=str,
        default="2005-2015",
        help="Comma years or range like 2005-2015",
    )
    p.add_argument(
        "--chunk-rows",
        type=int,
        default=250_000,
        help="Rows per Parquet row group / chunk",
    )
    return p.parse_args()


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def main() -> None:
    args = parse_args()
    years = _parse_years(args.years)
    for year in years:
        # 1990-1993 files don't have "us" suffix (combined US+territory files).
        if year <= 1993:
            z = args.raw_dir / f"Nat{year}.zip"
        else:
            z = args.raw_dir / f"Nat{year}us.zip"
        if not z.is_file():
            print(f"skip {year}: missing {z}", file=sys.stderr)
            continue
        out = args.out_dir / f"natality_{year}_core.parquet"
        t0 = time.perf_counter()
        print(f"=== {year} -> {out.name} ===", flush=True)
        try:
            n = run_parse(
                z,
                year,
                out,
                max_rows=None,
                chunk_rows=args.chunk_rows,
            )
        except Exception as e:
            print(f"ERROR {year}: {e}", file=sys.stderr)
            sys.exit(1)
        dt = time.perf_counter() - t0
        print(f"    {n:,} rows in {dt:.1f}s ({n / max(dt, 1e-9):,.0f} rows/s)", flush=True)


if __name__ == "__main__":
    main()
