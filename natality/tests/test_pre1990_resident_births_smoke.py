"""
DESIGN: tracks-current-state — RD.1 pre-1990 resident_births SAMPWT weighting smoke.

Asserts the weighted-resident formula used by compare_external_targets_v1.py
matches CDC e6fc-ccez for anchor years across the 50% sample, SAMPWT, and 1989
unweighted eras. Requires build-host yearly_clean parquets (skipped if absent).
"""

from __future__ import annotations

import csv
import io
import urllib.request
from pathlib import Path

import pyarrow.parquet as pq
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_YEARLY = Path.home() / "Desktop" / "natality-harmonization" / "output" / "yearly_clean"
MONOREPO_YEARLY = REPO_ROOT / "output" / "yearly_clean"


def _yearly_dir() -> Path | None:
    if BUILD_YEARLY.is_dir() and any(BUILD_YEARLY.glob("natality_*_raw.parquet")):
        return BUILD_YEARLY
    if MONOREPO_YEARLY.is_dir() and any(MONOREPO_YEARLY.glob("natality_*_raw.parquet")):
        return MONOREPO_YEARLY
    return None


def _cdc_resident_births(year: int) -> int:
    url = "https://data.cdc.gov/resource/e6fc-ccez.csv?$limit=50000"
    if not hasattr(_cdc_resident_births, "_cache"):
        with urllib.request.urlopen(url) as r:
            _cdc_resident_births._cache = {  # type: ignore[attr-defined]
                int(row["year"]): int(row["birth_number"])
                for row in csv.DictReader(io.TextIOWrapper(r))
            }
    return _cdc_resident_births._cache[year]  # type: ignore[attr-defined]


def _weighted_resident(yearly_dir: Path, year: int) -> int:
    raw = yearly_dir / f"natality_{year}_raw.parquet"
    names = pq.ParquetFile(raw).schema_arrow.names
    if year <= 1971:
        t = pq.read_table(raw, columns=["RESTATUS"])
        resident = sum(1 for v in t["RESTATUS"].to_pylist() if str(v).strip() != "4")
        return resident * 2
    t = pq.read_table(raw, columns=["RESTATUS", "SAMPWT"])
    total = 0.0
    for rs, sw in zip(t["RESTATUS"].to_pylist(), t["SAMPWT"].to_pylist(), strict=True):
        if str(rs).strip() == "4":
            continue
        total += 2.0 if str(sw).strip() == "2" else 1.0
    return int(total)


@pytest.fixture(scope="module")
def yearly_dir() -> Path:
    d = _yearly_dir()
    if d is None:
        pytest.skip("yearly_clean raw parquets not present (build host required)")
    return d


@pytest.mark.parametrize("year", [1968, 1972, 1978, 1984, 1988])
def test_pre1990_weighted_resident_matches_cdc(yearly_dir: Path, year: int) -> None:
    assert _weighted_resident(yearly_dir, year) == _cdc_resident_births(year)


def test_1989_resident_from_derived_parquet_matches_cdc() -> None:
    derived_candidates = [
        Path.home() / "Desktop" / "natality-harmonization" / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet",
        REPO_ROOT / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet",
    ]
    derived = next((p for p in derived_candidates if p.is_file()), None)
    if derived is None:
        pytest.skip("natality derived parquet not present")
    import pyarrow.compute as pc
    import pyarrow as pa

    t = pq.read_table(derived, columns=["data_year", "is_foreign_resident"], filters=[("data_year", "=", 1989)])
    foreign = t["is_foreign_resident"]
    resident = int(
        pc.sum(
            pc.cast(pc.invert(pc.fill_null(foreign, True)), pa.int64())
        ).as_py()
    )
    assert resident == _cdc_resident_births(1989)
