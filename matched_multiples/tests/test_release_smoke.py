"""DESIGN: tracks-current-state — matched-multiples release smoke suite.

Authored at C8.16 DO sub-step 3 (2026-05-14); extended at RD.2 (2026-05-24) and
RD.2 Table 2 follow-on (2026-05-24). Twelve test functions pinning the
matched-multiples release surface:
harmonized parquet row+column shape, 3-window coverage, schema↔parquet column parity,
record-type domain, Table 1 Total-column byte-exact reproduction for all three windows
(1995-1997, 1995-2000, 2016-2020), residence-status suppression in 2016-2020, and
cause-of-death scoping to infant-death rows.

Run from the monorepo root with:
    uv run pytest matched_multiples/tests/

Tests skip cleanly if the harmonized parquet is missing (it's gitignored;
re-derivable via matched_multiples/scripts/03_harmonize/harmonize_matched_multiples.py).
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

_SUBPROJECT_ROOT = Path(__file__).resolve().parent.parent
_HARMONIZED = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_harmonized.parquet"
_SCHEMA_CSV = _SUBPROJECT_ROOT / "harmonized_schema.csv"

# Post-C8.16 state. Re-pin at every authorized canonical mutation
# per DESIGN: tracks-current-state.
EXPECTED_ROWS = 1_665_568
EXPECTED_COLS = 24
EXPECTED_WINDOWS = ("1995-1997", "1995-2000", "2016-2020")
EXPECTED_WINDOW_ROWS = {
    "1995-1997": 324_490,
    "1995-2000": 699_144,
    "2016-2020": 641_934,
}
EXPECTED_RECORD_TYPES = frozenset({"survivor", "infant_death", "fetal_death"})

# 2016-2020 PDF Table 1 'Total' column cells (PDF sha256 ed5e96ab…)
PDF_2016_TARGETS = {
    "total": 641_934,
    "live_birth": 633_734,
    "survivor": 626_541,
    "infant_death": 7_193,
    "fetal_death": 8_200,
}

# 1995-1997 / 1995-2000 Table 1 Total-column equivalents (BIRTHID@1 totals;
# committed in external_validation_targets.csv at RD.2).
PDF_1995_1997_TARGETS = {
    "total": 324_490,
    "live_birth": 317_622,
    "survivor": 307_152,
    "infant_death": 10_470,
    "fetal_death": 6_868,
}
PDF_1995_2000_TARGETS = {
    "total": 699_144,
    "live_birth": 684_998,
    "survivor": 662_779,
    "infant_death": 22_219,
    "fetal_death": 14_146,
}


def _load() -> pd.DataFrame:
    if not _HARMONIZED.exists():
        pytest.skip(f"harmonized parquet not present at {_HARMONIZED}")
    return pq.read_table(_HARMONIZED).to_pandas()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_harmonized_loads_and_total_rows():
    df = _load()
    assert len(df) == EXPECTED_ROWS, (
        f"row drift: {len(df)} vs {EXPECTED_ROWS}"
    )
    assert df.shape[1] == EXPECTED_COLS, (
        f"col drift: {df.shape[1]} vs {EXPECTED_COLS}"
    )


def test_schema_columns_match_parquet():
    df = _load()
    schema = pd.read_csv(_SCHEMA_CSV)
    schema_cols = list(schema["harmonized_name"])
    assert schema_cols == list(df.columns), (
        f"order/identity mismatch:\n  schema only: {set(schema_cols)-set(df.columns)}\n"
        f"  parquet only: {set(df.columns)-set(schema_cols)}"
    )


def test_three_windows_exactly():
    df = _load()
    windows = sorted(df["data_window"].unique())
    assert tuple(windows) == EXPECTED_WINDOWS


def test_per_window_row_counts():
    df = _load()
    for window, expected in EXPECTED_WINDOW_ROWS.items():
        actual = int((df["data_window"] == window).sum())
        assert actual == expected, (
            f"window {window}: {actual} vs expected {expected}"
        )


def test_record_type_domain():
    df = _load()
    types = set(df["record_type"].dropna().unique())
    assert types == EXPECTED_RECORD_TYPES


TABLE2_TOTAL_COMPLETE_TWINS = {
    "1995-1997": 150_987,
    "1995-2000": 323_806,
}


def _table2_total_complete_twin_sets(sub: pd.DataFrame) -> int:
    twin = sub[(sub["set_size"] == 2) & (sub["set_complete"] == 1)]
    n_sets = 0
    for _, g in twin.groupby("set_id"):
        sexes = sorted(x for x in g["sex_infant"].tolist() if x in ("M", "F"))
        if len(sexes) != 2:
            continue
        ages = g["maternal_age"].dropna().unique()
        if len(ages) != 1:
            continue
        n_sets += 1
    return n_sets


def _table1_actuals(sub: pd.DataFrame) -> dict[str, int]:
    return {
        "total": len(sub),
        "live_birth": int(sub["record_type"].isin(["survivor", "infant_death"]).sum()),
        "survivor": int((sub["record_type"] == "survivor").sum()),
        "infant_death": int((sub["record_type"] == "infant_death").sum()),
        "fetal_death": int((sub["record_type"] == "fetal_death").sum()),
    }


def test_1995_1997_table_1_total_column():
    df = _load()
    sub = df[df["data_window"] == "1995-1997"]
    actual = _table1_actuals(sub)
    for k, expected in PDF_1995_1997_TARGETS.items():
        assert actual[k] == expected, (
            f"1995-1997 {k}: {actual[k]} vs Table 1 Total column {expected}"
        )


def test_1995_2000_table_1_total_column():
    df = _load()
    sub = df[df["data_window"] == "1995-2000"]
    actual = _table1_actuals(sub)
    for k, expected in PDF_1995_2000_TARGETS.items():
        assert actual[k] == expected, (
            f"1995-2000 {k}: {actual[k]} vs Table 1 Total column {expected}"
        )


@pytest.mark.parametrize("window", ["1995-1997", "1995-2000"])
def test_table2_total_complete_twin_sets(window: str):
    df = _load()
    sub = df[df["data_window"] == window]
    actual = _table2_total_complete_twin_sets(sub)
    expected = TABLE2_TOTAL_COMPLETE_TWINS[window]
    assert actual == expected, (
        f"{window} Table 2 total complete twin sets: {actual} vs {expected}"
    )


def test_2016_2020_pdf_table_1():
    df = _load()
    sub = df[df["data_window"] == "2016-2020"]
    actual = _table1_actuals(sub)
    for k, expected in PDF_2016_TARGETS.items():
        assert actual[k] == expected, (
            f"2016-2020 {k}: {actual[k]} vs PDF Table 1 {expected}"
        )


def test_residence_status_suppressed_in_2016_2020():
    df = _load()
    n = int(
        ((df["data_window"] == "2016-2020") & df["residence_status"].notna()).sum()
    )
    assert n == 0, f"residence_status leaked into 2016-2020 ({n} non-null)"


def test_cause_of_death_only_on_infant_death():
    df = _load()
    leak = int(
        ((df["record_type"] != "infant_death") & df["cause_of_death_icd"].notna()).sum()
    )
    assert leak == 0, (
        f"cause_of_death_icd populated on {leak} non-infant-death rows"
    )


# ---------------------------------------------------------------------------
# Layout-CSV continuity (no gaps / no overlaps / sum-of-lengths invariant)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "layout_csv,expected_end",
    [
        ("record_layout_1995_1997.csv", 502),
        ("record_layout_1995_2000.csv", 754),
        ("record_layout_2016_2020.csv", 157),
    ],
)
def test_layout_csv_continuity(layout_csv, expected_end):
    path = _SUBPROJECT_ROOT / layout_csv
    fields = []
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fields.append((
                int(row["position_start"]),
                int(row["position_end"]),
                int(row["length"]),
            ))
    assert fields, f"empty layout: {layout_csv}"
    for start, end, length in fields:
        assert end - start + 1 == length, (
            f"{layout_csv} row start={start} end={end} length={length} mismatch"
        )
    # No gap, no overlap; chain start_i = end_{i-1}+1.
    for prev, cur in zip(fields, fields[1:]):
        assert cur[0] == prev[1] + 1, (
            f"{layout_csv} gap/overlap between end={prev[1]} and start={cur[0]}"
        )
    # Last position equals expected_end
    assert fields[-1][1] == expected_end, (
        f"{layout_csv} ends at {fields[-1][1]}, expected {expected_end}"
    )
