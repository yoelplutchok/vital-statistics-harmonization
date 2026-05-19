"""Shared fixtures for monorepo-root cross-product invariant tests (C8.4).

Loads all three HVS parquets at session scope. Session-scope fixtures mean a
single pytest run reads each parquet exactly once even when many tests consume
it. The `_require()` skip-if-missing protocol mirrors the per-subproject
conftests so test runs in environments without the parquets fail cleanly
rather than erroring at collection.

Paths mirror the per-subproject conftests:
- fetal_death parquets live at the monorepo root's `output/harmonized/` (via
  the existing symlink to `~/Desktop/fetal-death-harmonization-build/output/harmonized/`).
- natality + linked parquets live in the natality build dir
  `~/Desktop/natality-harmonization/output/harmonized/` (the natality build dir
  predates the monorepo migration; an absolute path is used until a future
  monorepo `output/natality/` symlink is added).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

MONOREPO_ROOT = Path(__file__).resolve().parent.parent

FD_HARMONIZED_PARQUET = MONOREPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"
FD_DERIVED_PARQUET = MONOREPO_ROOT / "output/harmonized/fetal_death_derived.parquet"

_NATALITY_BUILD = Path.home() / "Desktop/natality-harmonization/output/harmonized"
NATALITY_HARMONIZED_PARQUET = _NATALITY_BUILD / "natality_v2_harmonized.parquet"
NATALITY_DERIVED_PARQUET = _NATALITY_BUILD / "natality_v2_harmonized_derived.parquet"
LINKED_HARMONIZED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized.parquet"
LINKED_DERIVED_PARQUET = _NATALITY_BUILD / "natality_v3_linked_harmonized_derived.parquet"

STRATIFIED_DENOMINATORS_CSV = MONOREPO_ROOT / "fetal_death/stratified_denominators.csv"


def _require(path: Path) -> Path:
    if not path.exists():
        try:
            rel = path.relative_to(MONOREPO_ROOT)
        except ValueError:
            rel = path
        pytest.skip(
            f"{rel} not present. "
            "Run the relevant subproject pipeline before running cross-product invariant tests."
        )
    return path


@pytest.fixture(scope="session")
def fd_derived_join_cols() -> pd.DataFrame:
    """Columns needed for fetal-death canonical-filter + join-key invariants."""
    path = _require(FD_DERIVED_PARQUET)
    return pd.read_parquet(
        path,
        columns=[
            "data_year",
            "tabulation_flag",
            "residence_status",
            "maternal_age",
            "maternal_race_bridged",
            "hispanic_origin",
        ],
    )


@pytest.fixture(scope="session")
def fd_row_counts() -> dict[str, int]:
    """Total row counts of the fetal-death harmonized + derived parquets."""
    harmonized = _require(FD_HARMONIZED_PARQUET)
    derived = _require(FD_DERIVED_PARQUET)
    return {
        "harmonized": pq.ParquetFile(harmonized).metadata.num_rows,
        "derived": pq.ParquetFile(derived).metadata.num_rows,
    }


@pytest.fixture(scope="session")
def fd_per_year_counts() -> dict[str, pd.Series]:
    """Per-year row counts (harmonized + derived) of the fetal-death parquets."""
    h_path = _require(FD_HARMONIZED_PARQUET)
    d_path = _require(FD_DERIVED_PARQUET)
    h_years = pd.read_parquet(h_path, columns=["data_year"])["data_year"]
    d_years = pd.read_parquet(d_path, columns=["data_year"])["data_year"]
    return {
        "harmonized": h_years.value_counts().sort_index(),
        "derived": d_years.value_counts().sort_index(),
    }


@pytest.fixture(scope="session")
def natality_derived_join_cols() -> pd.DataFrame:
    """Columns needed for natality canonical-filter + join-key invariants.

    138.8M rows × 5 narrow columns is ~2GB in-memory; pyarrow column-projection
    keeps the read under a couple of seconds.
    """
    path = _require(NATALITY_DERIVED_PARQUET)
    return pd.read_parquet(
        path,
        columns=[
            "data_year",
            "residence_status",
            "maternal_age",
            "maternal_race_bridged",
            "hispanic_origin",
        ],
    )


@pytest.fixture(scope="session")
def natality_row_counts() -> dict[str, int]:
    """Total row counts of the natality harmonized + derived parquets."""
    harmonized = _require(NATALITY_HARMONIZED_PARQUET)
    derived = _require(NATALITY_DERIVED_PARQUET)
    return {
        "harmonized": pq.ParquetFile(harmonized).metadata.num_rows,
        "derived": pq.ParquetFile(derived).metadata.num_rows,
    }


@pytest.fixture(scope="session")
def natality_per_year_counts() -> dict[str, pd.Series]:
    """Per-year row counts of the natality parquets."""
    h_path = _require(NATALITY_HARMONIZED_PARQUET)
    d_path = _require(NATALITY_DERIVED_PARQUET)
    h_years = pd.read_parquet(h_path, columns=["data_year"])["data_year"]
    d_years = pd.read_parquet(d_path, columns=["data_year"])["data_year"]
    return {
        "harmonized": h_years.value_counts().sort_index(),
        "derived": d_years.value_counts().sort_index(),
    }


@pytest.fixture(scope="session")
def linked_derived_join_cols() -> pd.DataFrame:
    """Columns needed for linked canonical-filter + join-key invariants."""
    path = _require(LINKED_DERIVED_PARQUET)
    return pd.read_parquet(
        path,
        columns=[
            "data_year",
            "residence_status",
            "maternal_age",
            "maternal_race_bridged",
            "hispanic_origin",
            # C8.18 v4: the keyless 1983-1988 cohort era stacks den+num
            # (link_segment ∈ {den,num}; NULL for 1989+ one-row-per-birth).
            # Cross-product birth-count parity must count den (births), not
            # the stacked numerator — so the fixture exposes link_segment.
            "link_segment",
        ],
    )


@pytest.fixture(scope="session")
def linked_row_counts() -> dict[str, int]:
    """Total row counts of the linked harmonized + derived parquets."""
    harmonized = _require(LINKED_HARMONIZED_PARQUET)
    derived = _require(LINKED_DERIVED_PARQUET)
    return {
        "harmonized": pq.ParquetFile(harmonized).metadata.num_rows,
        "derived": pq.ParquetFile(derived).metadata.num_rows,
    }


@pytest.fixture(scope="session")
def linked_per_year_counts() -> dict[str, pd.Series]:
    """Per-year row counts of the linked parquets."""
    h_path = _require(LINKED_HARMONIZED_PARQUET)
    d_path = _require(LINKED_DERIVED_PARQUET)
    h_years = pd.read_parquet(h_path, columns=["data_year"])["data_year"]
    d_years = pd.read_parquet(d_path, columns=["data_year"])["data_year"]
    return {
        "harmonized": h_years.value_counts().sort_index(),
        "derived": d_years.value_counts().sort_index(),
    }


@pytest.fixture(scope="session")
def stratified_denominators() -> pd.DataFrame:
    """Joint-use stratified denominators (29 yrs × per-stratum cells)."""
    path = _require(STRATIFIED_DENOMINATORS_CSV)
    return pd.read_csv(path)
