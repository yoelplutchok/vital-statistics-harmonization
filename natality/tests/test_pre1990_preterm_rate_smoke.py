"""
DESIGN: tracks-current-state — RD.1b Phase B pre-1990 preterm_rate_pct smoke.

Asserts SAMPWT-weighted preterm% from yearly raw parquets (1980-1988, GESTREC3
codes 1|2 denominator) and unweighted GESTAT3 (1989) match MVSR Advance Reports
within tolerance. Skipped when build-host parquets absent.
"""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_YEARLY = Path.home() / "Desktop" / "natality-harmonization" / "output" / "yearly_clean"
MONOREPO_YEARLY = REPO_ROOT / "output" / "yearly_clean"

# MVSR Advance Report narrative preterm% (resident; <37 weeks; known gestation).
MVSR_PRETERM: dict[int, tuple[float, float]] = {
    1980: (8.9, 0.05),
    1984: (9.4, 0.05),
    1985: (9.8, 0.05),
    1989: (10.6, 0.05),
}


def _yearly_dir() -> Path | None:
    if BUILD_YEARLY.is_dir() and any(BUILD_YEARLY.glob("natality_*_raw.parquet")):
        return BUILD_YEARLY
    if MONOREPO_YEARLY.is_dir() and any(MONOREPO_YEARLY.glob("natality_*_raw.parquet")):
        return MONOREPO_YEARLY
    return None


def _weighted_preterm_gestrec3(yearly_dir: Path, year: int) -> float:
    raw = yearly_dir / f"natality_{year}_raw.parquet"
    t = pq.read_table(raw, columns=["RESTATUS", "GESTREC3", "SAMPWT"])
    w_den = w_num = 0.0
    for rs, g3, sw in zip(
        t["RESTATUS"].to_pylist(),
        t["GESTREC3"].to_pylist(),
        t["SAMPWT"].to_pylist(),
        strict=True,
    ):
        if str(rs).strip() == "4":
            continue
        g = str(g3).strip()
        if g not in ("1", "2"):
            continue
        wt = 2.0 if str(sw).strip() == "2" else 1.0
        w_den += wt
        if g == "1":
            w_num += wt
    return w_num / w_den * 100.0


def _unweighted_preterm_gestat3_1989(yearly_dir: Path) -> float:
    raw = yearly_dir / "natality_1989_raw.parquet"
    t = pq.read_table(raw, columns=["RESTATUS", "GESTAT3"])
    den = num = 0
    for rs, g3 in zip(t["RESTATUS"].to_pylist(), t["GESTAT3"].to_pylist(), strict=True):
        if str(rs).strip() == "4":
            continue
        g = str(g3).strip()
        if g not in ("1", "2"):
            continue
        den += 1
        if g == "1":
            num += 1
    return num / den * 100.0


@pytest.fixture(scope="module")
def yearly_dir() -> Path:
    d = _yearly_dir()
    if d is None:
        pytest.skip("yearly_clean raw parquets not present (build host required)")
    return d


@pytest.mark.parametrize("year", [y for y in sorted(MVSR_PRETERM) if y <= 1988])
def test_pre1990_preterm_rate_weighted_matches_mvsr(yearly_dir: Path, year: int) -> None:
    expected, tol = MVSR_PRETERM[year]
    actual = _weighted_preterm_gestrec3(yearly_dir, year)
    assert abs(actual - expected) <= tol + 1e-9, f"{year}: actual={actual:.4f} expected={expected}"


def test_pre1990_preterm_rate_1989_unweighted_matches_mvsr(yearly_dir: Path) -> None:
    expected, tol = MVSR_PRETERM[1989]
    actual = _unweighted_preterm_gestat3_1989(yearly_dir)
    assert abs(actual - expected) <= tol + 1e-9, f"1989: actual={actual:.4f} expected={expected}"
