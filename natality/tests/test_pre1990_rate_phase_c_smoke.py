"""
DESIGN: tracks-current-state — RD.1b Phase C pre-1990 rate smoke (1968-1979 anchors).

SHAPE-not-VALUE: asserts MVSR/IOM-cited targets are within tolerance on build-host
yearly raw parquets when present. Skipped when parquets absent.
"""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_YEARLY = Path.home() / "Desktop" / "natality-harmonization" / "output" / "yearly_clean"
MONOREPO_YEARLY = REPO_ROOT / "output" / "yearly_clean"

# Anchor years: early (1968 GESTREC), mid (1972-1974 MVSR), late (1978-1979).
LBW_TARGETS: dict[int, tuple[float, float]] = {
    1968: (8.2, 0.05),
    1972: (7.7, 0.05),
    1979: (6.9, 0.05),
}

PRETERM_TARGETS: dict[int, tuple[float, float]] = {
    1968: (8.9, 0.05),
    1972: (9.6, 0.05),
    1979: (8.9, 0.05),
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
    schema_names = pq.ParquetFile(raw).schema_arrow.names
    bw_col = "DBIRWT" if "DBIRWT" in schema_names else "DBWT"
    cols = ["RESTATUS", bw_col]
    if year >= 1972:
        cols.append("SAMPWT")
    t = pq.read_table(raw, columns=cols)
    w_den = w_num = 0.0
    for rs, bw_raw, *rest in zip(
        t["RESTATUS"].to_pylist(),
        t[bw_col].to_pylist(),
        *[t[c].to_pylist() for c in cols[2:]],
        strict=True,
    ):
        if str(rs).strip() == "4":
            continue
        grams = _parse_grams(bw_raw)
        if grams is None:
            continue
        if year <= 1971:
            wt = 2.0
        else:
            wt = 2.0 if str(rest[0]).strip() == "2" else 1.0
        w_den += wt
        if grams < 2500:
            w_num += wt
    return w_num / w_den * 100.0


def _weighted_preterm_rate(yearly_dir: Path, year: int) -> float:
    raw = yearly_dir / f"natality_{year}_raw.parquet"
    if year == 1968:
        t = pq.read_table(raw, columns=["RESTATUS", "GESTREC"])
        w_den = w_num = 0.0
        for rs, gr in zip(t["RESTATUS"].to_pylist(), t["GESTREC"].to_pylist(), strict=True):
            if str(rs).strip() == "4":
                continue
            g = str(gr).strip()
            if g == "9" or g == "":
                continue
            try:
                code = int(g)
            except ValueError:
                continue
            if code < 0 or code > 8:
                continue
            w_den += 2.0
            if code <= 4:
                w_num += 2.0
        return w_num / w_den * 100.0

    cols = ["RESTATUS", "GESTREC3"]
    if year >= 1972:
        cols.append("SAMPWT")
    t = pq.read_table(raw, columns=cols)
    w_den = w_num = 0.0
    for rs, g3, *rest in zip(
        t["RESTATUS"].to_pylist(),
        t["GESTREC3"].to_pylist(),
        *[t[c].to_pylist() for c in cols[2:]],
        strict=True,
    ):
        if str(rs).strip() == "4":
            continue
        g = str(g3).strip()
        if g not in ("1", "2"):
            continue
        if year <= 1971:
            wt = 2.0
        else:
            wt = 2.0 if str(rest[0]).strip() == "2" else 1.0
        w_den += wt
        if g == "1":
            w_num += wt
    return w_num / w_den * 100.0


@pytest.fixture(scope="module")
def yearly_dir() -> Path:
    d = _yearly_dir()
    if d is None:
        pytest.skip("yearly_clean raw parquets not present (build host required)")
    return d


@pytest.mark.parametrize("year", sorted(LBW_TARGETS))
def test_phase_c_lbw_rate_anchor(yearly_dir: Path, year: int) -> None:
    expected, tol = LBW_TARGETS[year]
    actual = _weighted_lbw_rate(yearly_dir, year)
    assert abs(actual - expected) <= tol + 1e-9, f"{year}: actual={actual:.3f} expected={expected}"


@pytest.mark.parametrize("year", sorted(PRETERM_TARGETS))
def test_phase_c_preterm_rate_anchor(yearly_dir: Path, year: int) -> None:
    expected, tol = PRETERM_TARGETS[year]
    actual = _weighted_preterm_rate(yearly_dir, year)
    assert abs(actual - expected) <= tol + 1e-9, f"{year}: actual={actual:.3f} expected={expected}"
