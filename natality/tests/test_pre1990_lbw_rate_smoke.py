"""
DESIGN: tracks-current-state — RD.1b Phase A pre-1990 lbw_rate_pct smoke.

Asserts SAMPWT-weighted LBW% from yearly raw parquets (1980-1988) matches
childstats.gov HEALTH1.B within tolerance. Skipped when build-host parquets absent.
"""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_YEARLY = Path.home() / "Desktop" / "natality-harmonization" / "output" / "yearly_clean"
MONOREPO_YEARLY = REPO_ROOT / "output" / "yearly_clean"

CHILDSTATS_LBW: dict[int, tuple[float, float]] = {
    1980: (6.8, 0.05),
    1985: (6.8, 0.05),
    1988: (6.9, 0.05),
}


def _yearly_dir() -> Path | None:
    if BUILD_YEARLY.is_dir() and any(BUILD_YEARLY.glob("natality_*_raw.parquet")):
        return BUILD_YEARLY
    if MONOREPO_YEARLY.is_dir() and any(MONOREPO_YEARLY.glob("natality_*_raw.parquet")):
        return MONOREPO_YEARLY
    return None


def _parse_grams(raw_value: object) -> int | None:
    if raw_value is None:
        return None
    try:
        grams = int(str(raw_value).strip())
    except ValueError:
        return None
    if grams <= 0 or grams == 9999:
        return None
    return grams


def _weighted_lbw_rate(yearly_dir: Path, year: int) -> float:
    raw = yearly_dir / f"natality_{year}_raw.parquet"
    t = pq.read_table(raw, columns=["RESTATUS", "DBIRWT", "SAMPWT"])
    w_den = w_num = 0.0
    for rs, bw_raw, sw in zip(
        t["RESTATUS"].to_pylist(),
        t["DBIRWT"].to_pylist(),
        t["SAMPWT"].to_pylist(),
        strict=True,
    ):
        if str(rs).strip() == "4":
            continue
        grams = _parse_grams(bw_raw)
        if grams is None:
            continue
        wt = 2.0 if str(sw).strip() == "2" else 1.0
        w_den += wt
        if grams < 2500:
            w_num += wt
    return w_num / w_den * 100.0


@pytest.fixture(scope="module")
def yearly_dir() -> Path:
    d = _yearly_dir()
    if d is None:
        pytest.skip("yearly_clean raw parquets not present (build host required)")
    return d


@pytest.mark.parametrize("year", sorted(CHILDSTATS_LBW))
def test_pre1990_lbw_rate_matches_childstats(yearly_dir: Path, year: int) -> None:
    expected, tol = CHILDSTATS_LBW[year]
    actual = _weighted_lbw_rate(yearly_dir, year)
    assert abs(actual - expected) <= tol + 1e-9, f"{year}: actual={actual:.3f} expected={expected}"
