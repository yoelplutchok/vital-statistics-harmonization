#!/usr/bin/env python3
"""
Batch driver: parse all linked cohort denominator-plus files to Parquet.

Usage:
  python parse_all_linked_years.py                     # default: 2005-2015
  python parse_all_linked_years.py --years 2010-2015   # specific range
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from parse_linked_year import run_parse


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--years", type=str, default="2005-2015",
        help="Comma years or range like 2005-2015",
    )
    p.add_argument(
        "--linked-dir", type=Path, default=repo / "raw_data" / "linked",
        help="Directory containing LinkCO{yy}US.zip files",
    )
    p.add_argument(
        "--out-dir", type=Path, default=repo / "output" / "linked",
        help="Output directory for Parquet files",
    )
    args = p.parse_args()
    years = _parse_years(args.years)

    results: list[tuple[int, int, float]] = []
    for year in years:
        yy = f"{year % 100:02d}"
        zip_path = args.linked_dir / f"LinkCO{yy}US.zip"
        out_path = args.out_dir / f"linked_{year}_denomplus.parquet"

        if not zip_path.is_file():
            print(f"SKIP {year}: {zip_path} not found", file=sys.stderr)
            continue

        print(f"\n{'='*60}")
        print(f"Parsing {year} from {zip_path.name}")
        print(f"{'='*60}")
        t0 = time.time()
        try:
            n = run_parse(zip_path, year, out_path)
            elapsed = time.time() - t0
            results.append((year, n, elapsed))
        except Exception as e:
            print(f"ERROR {year}: {e}", file=sys.stderr)
            results.append((year, -1, time.time() - t0))

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    total_rows = 0
    for year, n, elapsed in results:
        status = f"{n:>12,} rows" if n > 0 else "FAILED"
        print(f"  {year}: {status}  ({elapsed:.1f}s)")
        if n > 0:
            total_rows += n
    print(f"  Total: {total_rows:,} rows across {sum(1 for _,n,_ in results if n>0)} years")


if __name__ == "__main__":
    main()
