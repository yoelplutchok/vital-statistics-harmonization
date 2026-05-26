"""DESIGN: tracks-current-state — LINK-ICD10 ICD-10 derived layer smoke tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

_NATALITY_BUILD = Path.home() / "Desktop/natality-harmonization/output/harmonized"
LINKED_HARMONIZED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized.parquet"
LINKED_DERIVED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized_derived.parquet"

_MONOREPO = Path(__file__).resolve().parents[2]
_GEM = _MONOREPO / "matched_multiples" / "metadata" / "icd_gem" / "2018_I9gem.txt"

HARMONIZED_SHA = "ea89ab3c009de00cddb88aad84aa50fde376a47f96b6865113a600fb5a0907c7"
EXPECTED_ROWS = 149_386_620
EXPECTED_COLS = 100
DERIVED_ONLY = (
    "underlying_cause_icd10_derived",
    "underlying_cause_icd10_derived_source",
    "underlying_cause_icd10_gem_approximate",
)


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def linked_derived_df() -> pd.DataFrame:
    if not LINKED_DERIVED_PARQUET.exists():
        pytest.skip(f"linked derived parquet missing at {LINKED_DERIVED_PARQUET}")
    cols = list(
        pq.read_schema(LINKED_DERIVED_PARQUET).names
    )
    if not all(c in cols for c in DERIVED_ONLY):
        pytest.skip("LINK-ICD10 derived columns not yet in linked derived parquet")
    return pq.read_table(
        LINKED_DERIVED_PARQUET,
        columns=[
            "data_year",
            "underlying_cause_icd9",
            "underlying_cause_icd10",
            *DERIVED_ONLY,
        ],
    ).to_pandas()


def test_harmonized_gate_sha_unchanged():
    if not LINKED_HARMONIZED_PARQUET.exists():
        pytest.skip("linked harmonized parquet not present")
    assert _sha256(LINKED_HARMONIZED_PARQUET) == HARMONIZED_SHA


def test_linked_derived_row_and_column_shape():
    if not LINKED_DERIVED_PARQUET.exists():
        pytest.skip("linked derived parquet not present")
    meta = pq.ParquetFile(LINKED_DERIVED_PARQUET).metadata
    assert meta.num_rows == EXPECTED_ROWS
    assert meta.num_columns == EXPECTED_COLS


def test_icd10_derived_only_when_cause_present(linked_derived_df: pd.DataFrame):
    has_cause = (
        linked_derived_df["underlying_cause_icd9"].notna()
        | linked_derived_df["underlying_cause_icd10"].notna()
    )
    leak = (
        ~has_cause & linked_derived_df["underlying_cause_icd10_derived"].notna()
    ).sum()
    assert leak == 0


def test_native_icd10_rows_match_canonical_ucod(linked_derived_df: pd.DataFrame):
    sub = linked_derived_df[
        linked_derived_df["underlying_cause_icd10_derived_source"] == "native_icd10"
    ]
    assert len(sub) > 0
    assert (
        sub["underlying_cause_icd10_derived"].astype(str)
        == sub["underlying_cause_icd10"].astype(str)
    ).all()


def test_gem_coverage_on_icd9_deaths(linked_derived_df: pd.DataFrame):
    icd9 = linked_derived_df[linked_derived_df["underlying_cause_icd9"].notna()]
    mapped = (
        icd9["underlying_cause_icd10_derived_source"] == "gem_from_icd9"
    ).mean()
    assert mapped >= 0.95


def test_icd9_era_populates_derived_1983_1998(linked_derived_df: pd.DataFrame):
    era = linked_derived_df[
        (linked_derived_df["data_year"] >= 1983)
        & (linked_derived_df["data_year"] <= 1998)
        & linked_derived_df["underlying_cause_icd9"].notna()
    ]
    assert len(era) > 0
    assert era["underlying_cause_icd10_derived"].notna().mean() >= 0.95


def test_gem_source_file_present():
    assert _GEM.is_file()
    assert _GEM.stat().st_size > 400_000
