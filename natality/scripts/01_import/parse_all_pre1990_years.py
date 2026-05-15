#!/usr/bin/env python3
"""
Parse natality years 1968-1989 from raw_data/Nat{year}.zip into
output/yearly_clean/natality_{year}_raw.parquet.

Sibling of `parse_all_v1_years.py` (1990-2024). Authored at C8.17 DO step 5a
(2026-05-14). Uses chunked Parquet writes (default 250k rows) to keep memory
bounded for the larger 1980s years (~3.9M records each at 215 bytes/record).

Usage (from repo root or this directory):
  python parse_all_pre1990_years.py
  python parse_all_pre1990_years.py --years 1968-1971
  python parse_all_pre1990_years.py --years 1981 --chunk-rows 100000

Defaults to the full 1968-1989 envelope (22 years) and writes outputs to the
natality build dir's yearly_clean/ (sibling of the 1990-2024 _core.parquet
files), keyed by the `_raw` suffix to distinguish "pre-1990 raw parser output;
needs harmonize.py extension at C8.17 DO step 5b" from the V2 `_core` output.
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

from parse_public_us_pre1990_year import run_parse  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--raw-dir",
        type=Path,
        default=_REPO_ROOT / "raw_data",
        help="Directory containing Nat{year}.zip (default: <natality-build>/raw_data)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "yearly_clean",
        help="Directory for natality_{year}_raw.parquet",
    )
    p.add_argument(
        "--years",
        type=str,
        default="1968-1989",
        help="Comma years or range like 1968-1989",
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
    failures: list[int] = []
    for year in years:
        z = args.raw_dir / f"Nat{year}.zip"
        if not z.is_file():
            print(f"skip {year}: missing {z}", file=sys.stderr)
            continue
        out = args.out_dir / f"natality_{year}_raw.parquet"
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
            failures.append(year)
            continue
        dt = time.perf_counter() - t0
        print(
            f"    {n:,} rows in {dt:.1f}s ({n / max(dt, 1e-9):,.0f} rows/s)",
            flush=True,
        )

    if failures:
        print(f"FAILED years: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
