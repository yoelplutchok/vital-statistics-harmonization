"""DESIGN: tracks-current-state — fetal-death release smoke suite, post-V3b (v2.3.0).

Nine tests that must pass before any vN.x.x release. Each guards an invariant
that an audit or a previous regression specifically called out. Per Convention 1
(NEXT_STEPS §4.2.1), most assertions are SHAPE-not-VALUE; the row-count and
year-set pins are explicitly tracks-current-state (re-pin at every authorized
data extension; do not treat as regression if the canonical state advanced).

  1. Both parquet artifacts load and have the post-V3b advertised row count.
  2. Schema CSV column set equals the harmonized parquet column set
     (the bug B-PUB-3 caught: schema declared 72 cols, parquet had 73).
  3. Year coverage is exactly the 41 contiguous years documented in README.md
     (1982-2022 after V3a + V3b + V2.1 extensions completed 2026-05-12).
  4. data_year == int(delivery_year) holds row-by-row
     (the B-PUB-3 promise that data_year is a faithful int sibling).
  5. Every pre-2003 row (1982-2002) carries version_flag='S' — V3b, V3a and V2
     all synthesize 'S' in harmonize.py (the source files have no native
     VERSION field for these eras; regressed once during B4 development).
     2003-2004 (V2.1) is intentionally excluded — those years are the
     state-staggered revision-rollout transition with mixed 'S'/'A' flags;
     2005+ (V1) uses native source-data VERSION values.
  6. Schema CSV `years_available` strings match the actual non-blank year
     ranges in the parquet for every column. Closes AUDIT_PUBLICATION_2 F1.
  7. Per-year row counts are within +/-5% of the published reference.
     Catches a year that silently shrinks or duplicates while the year set
     itself is unchanged (gap in test 3).
  8. paternal_age_recode11 contains no value '12' anywhere. The B4 V2 recode
     maps V2 12->11; regressed once during B4 development.
  9. NVSR-comparable count for 2010 reconciles to the 24,258 anchor used in
     this audit (tabulation_flag=='2' & residence_status!='4').

Run from the monorepo root with:
    pytest fetal_death/tests/

Tests skip cleanly if the parquet files are not present, since they are
reproducible artifacts excluded from version control.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Allow importing the schema regenerator helper. The tests pin schema content
# to the parquet by re-running its years-available computation in-process.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _regenerate_schema_years import compute_years_available  # noqa: E402

# Post-V3b state (2026-05-12; tag `task7_v3b-complete` at b0c8b4a + later
# v2.3.0 polish). Re-pin at every authorized data extension per the DESIGN:
# tracks-current-state contract.
EXPECTED_ROW_COUNT = 2_352_011
EXPECTED_HARMONIZED_COLS = 73  # SHAPE invariant; preserved through V2.1 + V3a + V3b
EXPECTED_DERIVED_COLS = 89     # SHAPE invariant; preserved through V2.1 + V3a + V3b
EXPECTED_YEARS = tuple(range(1982, 2023))  # 41 contiguous years 1982-2022

# Per-year row counts at current release. Drift +/-5% triggers test 7.
# V3b (1982-1988): 421,125 records (62,352 + 60,584 + 59,863 + 59,690 + 59,343 + 59,358 + 59,935)
# V3a (1989-1991): 188,909 records
# V2 (1992-2002): 700,704 records
# V2.1 (2003-2004): 107,782 records
# V1 (2005-2022): 933,491 records
EXPECTED_YEAR_ROWS = {
    1982: 62352, 1983: 60584, 1984: 59863, 1985: 59690, 1986: 59343,
    1987: 59358, 1988: 59935, 1989: 61295, 1990: 64349, 1991: 63265,
    1992: 70929, 1993: 71181, 1994: 66091, 1995: 63170, 1996: 65163,
    1997: 64002, 1998: 63438, 1999: 63875, 2000: 63132, 2001: 54442,
    2002: 55281, 2003: 54497, 2004: 53285, 2005: 53333, 2006: 52714,
    2007: 60973, 2008: 60154, 2009: 56685, 2010: 58079, 2011: 58361,
    2012: 56201, 2013: 54028, 2014: 52872, 2015: 51490, 2016: 51391,
    2017: 49170, 2018: 47676, 2019: 46007, 2020: 41816, 2021: 42428,
    2022: 40113,
}

# 2010 NVSR-comparable anchor: tabulation_flag=='2' & residence_status!='4'.
# Verified during AUDIT_PUBLICATION_2 (2026-05-02); re-verified post-V3b
# (V3b extension did not touch era==2010 records; B7 TABFLG correction fires
# only on era=='2003', so 2010 anchor unchanged).
NVSR_2010_ANCHOR = 24258


def test_release_parquet_files_loadable(harmonized_metadata, derived_metadata) -> None:
    assert harmonized_metadata.num_rows == EXPECTED_ROW_COUNT
    assert derived_metadata.num_rows == EXPECTED_ROW_COUNT
    assert harmonized_metadata.num_columns == EXPECTED_HARMONIZED_COLS
    assert derived_metadata.num_columns == EXPECTED_DERIVED_COLS


def test_schema_csv_matches_harmonized_columns(schema_df, harmonized_path) -> None:
    schema_names = set(schema_df["harmonized_name"])
    parquet_names = set(pq.ParquetFile(harmonized_path).schema_arrow.names)

    assert len(schema_df) == EXPECTED_HARMONIZED_COLS, (
        f"schema row count {len(schema_df)} != {EXPECTED_HARMONIZED_COLS}"
    )
    assert schema_names == parquet_names, (
        f"schema/parquet column mismatch:\n"
        f"  schema only: {sorted(schema_names - parquet_names)}\n"
        f"  parquet only: {sorted(parquet_names - schema_names)}"
    )


def test_year_coverage_is_41_contiguous_years(harmonized_year_invariants: pd.DataFrame) -> None:
    years = tuple(sorted(harmonized_year_invariants["data_year"].unique().tolist()))
    assert years == EXPECTED_YEARS, f"unexpected year set: {years}"
    # Contiguity invariant: every year 1982..2022 present (V2.1 added 2003-2004;
    # V3a added 1989-1991; V3b added 1982-1988).
    assert years[0] == 1982
    assert years[-1] == 2022
    assert len(years) == 41


def test_data_year_equals_int_delivery_year(harmonized_year_invariants: pd.DataFrame) -> None:
    df = harmonized_year_invariants
    mismatches = (df["data_year"] != df["delivery_year"].astype(int)).sum()
    assert mismatches == 0, (
        f"{mismatches} rows where data_year != int(delivery_year). "
        "B-PUB-3 invariant violated."
    )


def test_pre_2003_version_flag_is_S(harmonized_year_invariants: pd.DataFrame) -> None:
    """V3b (1982-1988, era=='1985'), V3a (1989-1991, era=='1989') and V2
    (1992-2002, era=='1992') all synthesize version_flag='S' in harmonize.py
    because the source files have no native VERSION field for these eras.

    2003-2004 (V2.1) is intentionally excluded: those years are the
    state-staggered 1989-rev → 2003-rev transition with mixed 'S'/'A' flags.
    2005+ (V1) uses native source VERSION values (also mixed 'S'/'A')."""
    df = harmonized_year_invariants
    pre_2003 = df[df["data_year"].between(1982, 2002)]
    assert len(pre_2003) > 0, "pre-2003 era slice unexpectedly empty"
    non_s = (pre_2003["version_flag"] != "S").sum()
    assert non_s == 0, (
        f"{non_s} pre-2003 rows (1982-2002) have version_flag != 'S'. "
        "harmonize.py is supposed to synthesize 'S' for the V3b + V3a + V2 eras."
    )


def test_schema_years_available_matches_data(schema_df, harmonized_full) -> None:
    """For every column, schema's `years_available` must match the actual
    non-blank year coverage in the parquet. Closes AUDIT_PUBLICATION_2 F1.

    The reference is computed by re-running scripts/_regenerate_schema_years.py
    in-process. To regenerate after a parquet change:
        python scripts/_regenerate_schema_years.py
    """
    canonical = compute_years_available(harmonized_full)
    drift: list[str] = []
    for _, row in schema_df.iterrows():
        name = row["harmonized_name"]
        target = canonical.get(name, "")
        current = "" if pd.isna(row["years_available"]) else str(row["years_available"])
        if current != target:
            drift.append(f"  {name}: schema={current!r}  data={target!r}")
    assert not drift, (
        "schema/parquet years_available drift "
        "(run scripts/_regenerate_schema_years.py to regenerate):\n"
        + "\n".join(drift)
    )


def test_per_year_row_counts_within_5pct(harmonized_year_invariants: pd.DataFrame) -> None:
    """Each year's row count is within +/-5% of the V2.0 published value.
    Catches a year silently shrinking or duplicating while the year set
    is unchanged (test 3 only checks set equality)."""
    actual = harmonized_year_invariants.value_counts("data_year").to_dict()
    drift: list[str] = []
    for year, expected in EXPECTED_YEAR_ROWS.items():
        got = int(actual.get(year, 0))
        if got == 0:
            drift.append(f"  {year}: 0 rows (expected ~{expected:,})")
            continue
        ratio = got / expected
        if not 0.95 <= ratio <= 1.05:
            drift.append(f"  {year}: {got:,} rows ({ratio:.2%} of expected {expected:,})")
    assert not drift, "per-year row count drift > 5%:\n" + "\n".join(drift)


def test_paternal_age_recode11_no_v2_residue(paternal_age_column: pd.Series) -> None:
    """No row anywhere may carry paternal_age_recode11 == '12'.

    The V2 raw FAGE11 is 12-category; harmonize.py B4 collapses {10,11}->10
    and 12->11 to match the V1 11-category scheme. A regression that bypasses
    the recode would leave V2 '12' values in place.
    """
    bad = (paternal_age_column.astype(str).str.strip() == "12").sum()
    assert bad == 0, (
        f"{bad} rows have paternal_age_recode11 == '12'. "
        "B4 recode bypassed: V2 raw FAGE11 was not remapped to V1 11-category scheme."
    )


def test_nvsr_comparable_2010_count(nvsr_anchor_columns: pd.DataFrame) -> None:
    """The 2010 NVSR-comparable subset reconciles to the audit anchor.

    Uses int literals consistent with v2.1.0 H8 fix (FIX_LOG 2026-05-12T01:30Z:
    tabulation_flag, residence_status, maternal_age, maternal_race_bridged,
    hispanic_origin cast from object/string to Int8/Int16).
    """
    df = nvsr_anchor_columns
    sub = df[
        (df["data_year"] == 2010)
        & (df["tabulation_flag"] == 2)
        & (df["residence_status"] != 4)
    ]
    assert len(sub) == NVSR_2010_ANCHOR, (
        f"2010 NVSR-comparable count is {len(sub):,}, "
        f"expected {NVSR_2010_ANCHOR:,} (AUDIT_PUBLICATION_2 anchor)."
    )
