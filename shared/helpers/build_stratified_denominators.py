"""DESIGN: tracks-current-state

Build the joint-use stratified live-birth denominator (long-format CSV).

Reads the natality v2.7.0 full harmonized parquet
(`natality_v2_harmonized_derived.parquet`, 84 columns), applies the
canonical residence filter (`residence_status != 4`), renames natality
join-key columns to canonical fetal_death-style names via
`shared.helpers.canonical_join_keys`, derives the NVSR-standard
6-category maternal age band, and writes one CSV row per
(data_year, maternal_age_band, maternal_race_bridged, hispanic_origin)
cell with a `live_births` count.

NOTE: The residents-only convenience parquet drops `restatus` after
filtering. To keep the residence filter audit-explicit in this script,
the full harmonized parquet is the canonical input.

Year scope: 1992-2002 + 2005-2024 (31 joint-coverage years between
natality 1968-2024 and fetal-death 1982-2024 excl. 2003-2004).

Bridged-race coverage gap: rows for 2018-2022 have
`maternal_race_bridged = NaN` because NCHS dropped MBRACE from the public-
use file for those years. Joint-use rate computation by bridged race is
limited to 1992-2002 + 2005-2017 (24 years) without further work.

Usage:
    python shared/helpers/build_stratified_denominators.py \
        --natality-parquet /path/to/natality_v2_residents_only.parquet \
        --output fetal_death/stratified_denominators.csv \
        [--tier {0|1|2|full}]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.helpers.canonical_join_keys import (
    derive_maternal_age_band,
    to_canonical_natality,
)

JOINT_COVERAGE_YEARS: list[int] = list(range(1992, 2003)) + list(range(2005, 2025))

# v2.8.0+ natality parquets ship canonical names; v2.7.0 Zenodo used legacy names.
NATALITY_READ_COLUMNS_LEGACY: list[str] = [
    "year",
    "restatus",
    "maternal_age",
    "maternal_race_bridged4",
    "maternal_hispanic_origin",
]
NATALITY_READ_COLUMNS_CANONICAL: list[str] = [
    "data_year",
    "residence_status",
    "maternal_age",
    "maternal_race_bridged",
    "hispanic_origin",
]

GROUPBY_COLUMNS: list[str] = [
    "data_year",
    "maternal_age_band",
    "maternal_race_bridged",
    "hispanic_origin",
]


def synthetic_fixture() -> pd.DataFrame:
    """Hand-constructed 8-row natality fixture for Tier-0 SMOKE."""
    return pd.DataFrame(
        {
            "year": [2010, 2010, 2010, 2010, 2010, 2010, 2010, 2018],
            "restatus": [1, 1, 1, 1, 2, 4, 1, 1],
            "maternal_age": [17, 22, 22, 28, 42, 25, 99, 30],
            "maternal_race_bridged4": [
                pd.array([1, 1, 1, 2, 4, 1, 1, pd.NA], dtype="Int8")
            ][0],
            "maternal_hispanic_origin": [0, 0, 0, 1, 0, 0, 0, 0],
        }
    )


def build(df_natality: pd.DataFrame) -> pd.DataFrame:
    df = to_canonical_natality(df_natality)
    df = df[df["residence_status"] != 4].copy()
    df["maternal_age_band"] = derive_maternal_age_band(df["maternal_age"])
    grouped = (
        df.groupby(GROUPBY_COLUMNS, observed=True, dropna=False)
        .size()
        .reset_index(name="live_births")
    )
    grouped["maternal_race_bridged"] = grouped["maternal_race_bridged"].astype("Int8")
    grouped["hispanic_origin"] = grouped["hispanic_origin"].astype("Int8")
    return grouped.sort_values(GROUPBY_COLUMNS, na_position="last").reset_index(drop=True)


def write_csv_deterministic(df: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--natality-parquet",
        type=Path,
        required=False,
        help="Path to natality harmonized parquet. Required for tiers 1/2/full.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--tier",
        choices=["0", "1", "2", "full"],
        default="full",
        help="0=synthetic fixture; 1=100 rows of 2022; 2=full 2022; full=all joint years.",
    )
    args = parser.parse_args()

    if args.tier == "0":
        df = synthetic_fixture()
    else:
        if args.natality_parquet is None or not args.natality_parquet.exists():
            sys.exit(
                f"--natality-parquet required for tier {args.tier} and must exist; "
                f"got {args.natality_parquet}"
            )
        import pyarrow.parquet as pq

        schema_names = set(pq.read_schema(args.natality_parquet).names)
        cols = (
            NATALITY_READ_COLUMNS_CANONICAL
            if "data_year" in schema_names
            else NATALITY_READ_COLUMNS_LEGACY
        )
        df = pd.read_parquet(args.natality_parquet, columns=cols)
        if args.tier == "full":
            year_col = "data_year" if "data_year" in df.columns else "year"
            df = df[df[year_col].isin(JOINT_COVERAGE_YEARS)]
        year_col = "data_year" if "data_year" in df.columns else "year"
        if args.tier == "1":
            df = df[df[year_col] == 2022].head(100)
        elif args.tier == "2":
            df = df[df[year_col] == 2022]

    result = build(df)
    sha = write_csv_deterministic(result, args.output)

    print(f"tier={args.tier}")
    res_col = (
        "residence_status"
        if "residence_status" in df.columns
        else ("restatus" if "restatus" in df.columns else None)
    )
    n_res = len(df[df[res_col] != 4]) if res_col else "n/a"
    print(f"input_rows_after_filter={n_res}")
    print(f"output_rows={len(result)}")
    print(f"output_path={args.output}")
    print(f"output_sha256={sha}")
    print(f"sum_live_births={int(result['live_births'].sum()):,}")
    print(f"years={sorted(result['data_year'].unique().tolist())}")
    if args.tier == "full":
        per_year = result.groupby("data_year", observed=True)["live_births"].sum().sort_index()
        print("per_year_totals:")
        for year, total in per_year.items():
            print(f"  {int(year)}: {int(total):,}")


if __name__ == "__main__":
    main()
