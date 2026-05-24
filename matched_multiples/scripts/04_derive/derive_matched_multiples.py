#!/usr/bin/env python3
"""
DESIGN: tracks-current-state

Add derived ICD-10-underlying-cause columns for cross-window infant-death
analysis without mutating canonical ``cause_of_death_icd``.

Reads:
  matched_multiples/output/harmonized/matched_multiples_harmonized.parquet

Writes:
  matched_multiples/output/harmonized/matched_multiples_derived.parquet
    (all 24 harmonized columns + 3 derived columns)

Derived columns:
  - cause_of_death_icd10_derived: ICD-10 code (native or GEM-mapped from ICD-9)
  - cause_of_death_icd10_derived_source: native_icd10 | gem_from_icd9 | gem_unmapped
  - cause_of_death_icd10_gem_approximate: 1 if GEM row was approximate, else 0/NA

Usage:
  uv run python matched_multiples/scripts/04_derive/derive_matched_multiples.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from icd9_to_icd10_gem import load_gem_tables, map_nchs_ucod  # noqa: E402

_SUBPROJECT_ROOT = _SCRIPT_DIR.parents[1]
_DEFAULT_IN = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_harmonized.parquet"
_DEFAULT_OUT = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_derived.parquet"

DERIVED_COLS = (
    "cause_of_death_icd10_derived",
    "cause_of_death_icd10_derived_source",
    "cause_of_death_icd10_gem_approximate",
)


def add_icd10_derived(df: pd.DataFrame, gem_path: Path | None = None) -> pd.DataFrame:
    """Attach ICD-10 derived cause columns; harmonized columns unchanged."""
    out = df.copy()
    by_key = load_gem_tables(gem_path)

    is_id = out["record_type"] == "infant_death"
    rev = out["cause_of_death_icd_revision"]
    icd = out["cause_of_death_icd"].astype(str).str.strip().replace("", pd.NA)

    derived = pd.Series(pd.NA, index=out.index, dtype="string")
    source = pd.Series(pd.NA, index=out.index, dtype="string")
    approx = pd.Series(pd.NA, index=out.index, dtype="Int64")

    native = is_id & rev.eq(10) & icd.notna()
    derived = derived.mask(native, icd)
    source = source.mask(native, "native_icd10")
    approx = approx.mask(native, 0)

    icd9_rows = is_id & rev.eq(9) & icd.notna()
    for idx in out.index[icd9_rows]:
        code = icd.loc[idx]
        i10, flag = map_nchs_ucod(str(code), by_key)
        if i10:
            derived.loc[idx] = i10
            source.loc[idx] = "gem_from_icd9"
            approx.loc[idx] = 1 if flag else 0
        else:
            source.loc[idx] = "gem_unmapped"

    out["cause_of_death_icd10_derived"] = derived
    out["cause_of_death_icd10_derived_source"] = source
    out["cause_of_death_icd10_gem_approximate"] = approx
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=_DEFAULT_IN)
    p.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    p.add_argument("--gem", type=Path, default=None, help="Override 2018_I9gem.txt path")
    args = p.parse_args()

    if not args.input.is_file():
        print(f"HALT: missing input {args.input}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_parquet(args.input)
    harm_cols = list(df.columns)
    df = add_icd10_derived(df, args.gem)
    assert list(df.columns) == harm_cols + list(DERIVED_COLS)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)
    n_id = (df["record_type"] == "infant_death").sum()
    n_derived = df["cause_of_death_icd10_derived"].notna().sum()
    print(
        f"Wrote {len(df):,} rows × {len(df.columns)} cols to {args.out}\n"
        f"  infant_death: {n_id:,}; icd10_derived populated: {n_derived:,}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
