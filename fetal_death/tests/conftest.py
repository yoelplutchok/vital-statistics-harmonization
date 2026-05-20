"""Shared fixtures for the fetal-death release smoke suite (V2.3.0 / V3b).

The output parquet files are reproducible from the scripts but are not
committed (see .gitignore). When they are missing, fixtures cause the
relevant tests to skip with a clear instruction rather than fail.

Monorepo paths: parquets live at the monorepo root's `output/harmonized/`
(via symlinks to the standalone build dir); schema CSV is at the flat
`fetal_death/harmonized_schema.csv` (no `metadata/` subdir). Adapted
2026-05-12 per C8.1 DO-1 (monorepo-migration path-drift fix; sibling of
FIX_LOG 2026-05-12T01:30Z).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

SUBPROJECT_ROOT = Path(__file__).resolve().parent.parent
MONOREPO_ROOT = SUBPROJECT_ROOT.parent

HARMONIZED_PARQUET = MONOREPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"
DERIVED_PARQUET = MONOREPO_ROOT / "output/harmonized/fetal_death_derived.parquet"
SCHEMA_CSV = SUBPROJECT_ROOT / "harmonized_schema.csv"


def _require(path: Path) -> Path:
    if not path.exists():
        try:
            rel = path.relative_to(MONOREPO_ROOT)
        except ValueError:
            rel = path
        pytest.skip(
            f"{rel} not present. "
            "Run the pipeline (fetal_death/scripts/01_import → 04_derive) before running smoke tests."
        )
    return path


@pytest.fixture(scope="session")
def harmonized_path() -> Path:
    return _require(HARMONIZED_PARQUET)


@pytest.fixture(scope="session")
def derived_path() -> Path:
    return _require(DERIVED_PARQUET)


@pytest.fixture(scope="session")
def schema_df() -> pd.DataFrame:
    df = pd.read_csv(SCHEMA_CSV)
    return df[~df["harmonized_name"].astype(str).str.startswith("#")]


@pytest.fixture(scope="session")
def harmonized_year_invariants(harmonized_path: Path) -> pd.DataFrame:
    """Read only the columns needed for year/version-flag invariant checks.

    The full file is 1.6M rows; reading three columns keeps the suite under
    a couple of seconds even on a cold cache.
    """
    return pd.read_parquet(
        harmonized_path,
        columns=["data_year", "delivery_year", "version_flag"],
    )


@pytest.fixture(scope="session")
def harmonized_full(harmonized_path: Path) -> pd.DataFrame:
    """Full harmonized parquet (2.4M x 73, v2.4.0). Used by the years_available lock
    and other tests that need every column."""
    return pd.read_parquet(harmonized_path)


@pytest.fixture(scope="session")
def nvsr_anchor_columns(harmonized_path: Path) -> pd.DataFrame:
    """Three columns needed for the NVSR-comparable anchor."""
    return pd.read_parquet(
        harmonized_path,
        columns=["data_year", "tabulation_flag", "residence_status"],
    )


@pytest.fixture(scope="session")
def paternal_age_column(harmonized_path: Path) -> pd.Series:
    """One column for the B4 invariant test."""
    return pd.read_parquet(
        harmonized_path,
        columns=["paternal_age_recode11"],
    )["paternal_age_recode11"]


@pytest.fixture(scope="session")
def harmonized_metadata(harmonized_path: Path) -> pq.FileMetaData:
    return pq.ParquetFile(harmonized_path).metadata


@pytest.fixture(scope="session")
def derived_metadata(derived_path: Path) -> pq.FileMetaData:
    return pq.ParquetFile(derived_path).metadata
