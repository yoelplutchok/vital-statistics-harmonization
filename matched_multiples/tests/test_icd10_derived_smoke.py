"""DESIGN: tracks-current-state — RD.4 ICD-10 derived layer smoke tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

_SUBPROJECT_ROOT = Path(__file__).resolve().parent.parent
_HARMONIZED = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_harmonized.parquet"
_DERIVED = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_derived.parquet"
_DERIVED_SCHEMA = _SUBPROJECT_ROOT / "metadata" / "derived_schema.csv"
_GEM = _SUBPROJECT_ROOT / "metadata" / "icd_gem" / "2018_I9gem.txt"

HARMONIZED_SHA = "adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549"
EXPECTED_ROWS = 1_665_568
EXPECTED_HARM_COLS = 24
EXPECTED_DERIVED_COLS = 27
DERIVED_ONLY = (
    "cause_of_death_icd10_derived",
    "cause_of_death_icd10_derived_source",
    "cause_of_death_icd10_gem_approximate",
)


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def derived_df() -> pd.DataFrame:
    if not _DERIVED.exists():
        pytest.skip(f"derived parquet missing at {_DERIVED}")
    return pq.read_table(_DERIVED).to_pandas()


def test_harmonized_gate_sha_unchanged():
    if not _HARMONIZED.exists():
        pytest.skip("harmonized parquet not present")
    assert _sha256(_HARMONIZED) == HARMONIZED_SHA


def test_derived_row_and_column_shape(derived_df: pd.DataFrame):
    assert len(derived_df) == EXPECTED_ROWS
    assert len(derived_df.columns) == EXPECTED_DERIVED_COLS


def test_derived_schema_csv_lists_derived_columns():
    schema = pd.read_csv(_DERIVED_SCHEMA)
    names = set(schema["harmonized_name"])
    assert names == set(DERIVED_ONLY)


def test_harmonized_columns_unchanged_in_derived(derived_df: pd.DataFrame):
    if not _HARMONIZED.exists():
        pytest.skip("harmonized parquet not present")
    harm = pq.read_table(_HARMONIZED).to_pandas()
    for col in harm.columns:
        pd.testing.assert_series_equal(
            harm[col], derived_df[col], check_names=True
        )


def test_icd10_derived_only_on_infant_death(derived_df: pd.DataFrame):
    leak = (
        (derived_df["record_type"] != "infant_death")
        & derived_df["cause_of_death_icd10_derived"].notna()
    ).sum()
    assert leak == 0


def test_native_icd10_rows_match_canonical_cause(derived_df: pd.DataFrame):
    sub = derived_df[
        derived_df["cause_of_death_icd10_derived_source"] == "native_icd10"
    ]
    assert len(sub) > 0
    assert (
        sub["cause_of_death_icd10_derived"].astype(str)
        == sub["cause_of_death_icd"].astype(str)
    ).all()


def test_gem_coverage_on_icd9_infant_deaths(derived_df: pd.DataFrame):
    icd9 = derived_df[
        (derived_df["record_type"] == "infant_death")
        & (derived_df["cause_of_death_icd_revision"] == 9)
    ]
    mapped = (icd9["cause_of_death_icd10_derived_source"] == "gem_from_icd9").mean()
    assert mapped >= 0.95


def test_gem_source_file_present():
    assert _GEM.is_file()
    assert _GEM.stat().st_size > 400_000
