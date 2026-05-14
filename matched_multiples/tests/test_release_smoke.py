"""DESIGN: tracks-current-state — matched-multiples release smoke suite.

Authored at C8.16 DO sub-step 3 (2026-05-14). Eight tests pinning the C8.16
release surface: harmonized parquet row+column shape, 3-window coverage,
schema↔parquet column parity, record-type domain, 2016-2020 PDF Table 1
byte-exact reproduction, residence-status suppression in 2016-2020, and
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


def test_2016_2020_pdf_table_1():
    df = _load()
    sub = df[df["data_window"] == "2016-2020"]
    actual = {
        "total": len(sub),
        "live_birth": int(sub["record_type"].isin(["survivor", "infant_death"]).sum()),
        "survivor": int((sub["record_type"] == "survivor").sum()),
        "infant_death": int((sub["record_type"] == "infant_death").sum()),
        "fetal_death": int((sub["record_type"] == "fetal_death").sum()),
    }
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
