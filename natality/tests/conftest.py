"""Shared fixtures for the natality + linked-birth-infant-death release smoke
suite (v2.8.0).

The natality and linked parquets are reproducible from `natality/scripts/`
but are not committed (see .gitignore). When they are missing, fixtures
cause the relevant tests to skip with a clear instruction rather than fail.

Monorepo paths: parquets live in the standalone build dir
`~/Desktop/natality-harmonization/output/harmonized/` (the natality build dir
predates the monorepo migration; tests reach them via an absolute path
unless a future task copies them under the monorepo `output/`).

Authored 2026-05-12 per C8.1 DO-3 (B.2 dtype parity test for natality).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

SUBPROJECT_ROOT = Path(__file__).resolve().parent.parent
MONOREPO_ROOT = SUBPROJECT_ROOT.parent

# Per natality README + STATUS 2026-05-12, the v2.8.0 build dir holds the
# canonical parquets. Until a monorepo `output/` symlink is created for
# natality (parallel to fetal_death's symlinks), tests resolve absolute paths.
_NATALITY_BUILD = Path.home() / "Desktop/natality-harmonization/output/harmonized"
NATALITY_HARMONIZED_PARQUET = _NATALITY_BUILD / "natality_v2_harmonized.parquet"
NATALITY_DERIVED_PARQUET = _NATALITY_BUILD / "natality_v2_harmonized_derived.parquet"
LINKED_HARMONIZED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized.parquet"
LINKED_DERIVED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized_derived.parquet"

SCHEMA_CSV = SUBPROJECT_ROOT / "metadata/harmonized_schema.csv"


def _require(path: Path) -> Path:
    if not path.exists():
        pytest.skip(
            f"{path} not present. Run the natality pipeline before running smoke tests."
        )
    return path


@pytest.fixture(scope="session")
def schema_df() -> pd.DataFrame:
    df = pd.read_csv(SCHEMA_CSV)
    return df[~df["harmonized_name"].astype(str).str.startswith("#")]


@pytest.fixture(scope="session")
def natality_derived_path() -> Path:
    return _require(NATALITY_DERIVED_PARQUET)


@pytest.fixture(scope="session")
def linked_derived_path() -> Path:
    return _require(LINKED_DERIVED_PARQUET)
