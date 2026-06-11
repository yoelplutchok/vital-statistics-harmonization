"""DESIGN: tracks-current-state — C8.22 pre-computed cross-tab CSV builder SMOKE.

SHAPE-not-VALUE (NEXT_STEPS.md §4.2.1 / Convention 1): asserts STRUCTURAL
invariants of the builder's pure logic + the generated CSV folder (canonical
filter / known-denominator / era-cesarean / bridged-race-NULL classifiers
behave per the mirrored canonical-validator definitions; H6 row-count
conservation; deterministic byte-identical re-render; expected files + columns)
that survive authorized canonical drift — NOT mutable per-year cell counts
pinned at authoring time (those grow when the data envelope grows).

The few pinned numbers here are FROZEN NCHS/NVSR validation facts (e.g. 2022
fetal deaths >=20wk resident == 20,202), not mutable annotations: the
harmonized data must keep reproducing them or it IS a regression — exactly what
this assertion is for (L17 frozen-validation-fact pin, not stale-annotation
pin).

§9-#9: this harness (the fixture the builder must pass) is authored BEFORE the
builder. Tier 0 runs the pure classifiers on hand-built synthetic fixtures (no
parquet I/O). Tier 1 asserts SHAPE on the generated CSV folder if the DO build
has run (skips cleanly otherwise — CI/memory-safe; the heavy parquet
reconciliation is the DO/VERIFY phase).
"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_BUILDER = _REPO / "scripts" / "_build_published_tabulations.py"
_OUT_DIR = _REPO / "csv" / "published_tabulations"

# The 10 curated tabulations (2026-05-23T18:00:00Z). SHAPE pin:
# the SET of deliverables is a structural contract, not a mutable value.
_EXPECTED_CSVS = {
    "natality_births_by_year.csv",
    "natality_births_by_year_x_maternal_race.csv",
    "natality_births_by_year_x_maternal_age.csv",
    "natality_rates_lbw_preterm_singleton_by_year.csv",
    "natality_rates_cesarean_multiple_by_year.csv",
    "fetal_death_counts_by_year.csv",
    "fetal_mortality_rate_by_year.csv",
    "fetal_mortality_rate_by_year_x_maternal_race.csv",
    "linked_imr_by_year.csv",
    "linked_imr_by_year_x_maternal_race.csv",
}


def _load():
    spec = importlib.util.spec_from_file_location("_pubtab", _BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pt():
    assert _BUILDER.exists(), f"builder missing: {_BUILDER}"
    return _load()


# ── Tier 0: pure classifiers, synthetic fixtures, no parquet I/O ────────────

def test_race_label_mapping(pt):
    """Bridged-race codes {1,2,3,4} -> canonical labels; NULL/other -> the
    explicit 'Not stated / not bridged' bucket (NEVER dropped — H6/D5)."""
    assert pt.race_label(1) == "White"
    assert pt.race_label(2) == "Black"
    assert pt.race_label(3) == "AIAN"
    assert pt.race_label(4) == "Asian or Pacific Islander"
    # NULL and any out-of-frame code collapse to the explicit not-stated bucket
    assert pt.race_label(None) == pt.NOT_STATED_RACE
    assert pt.race_label(9) == pt.NOT_STATED_RACE
    assert pt.race_label(0) == pt.NOT_STATED_RACE
    assert pt.NOT_STATED_RACE  # non-empty sentinel string (never "")


def test_cesarean_era_crosswalk(pt):
    """Mirror of compare_external_targets_v1.py: <=2004 DELMETH5-style
    (cesarean = code 3|4, known = 1..4); >=2005 DMETH_REC (cesarean = code 2,
    known = 1|2). Returns (is_known, is_cesarean)."""
    # 1990-2004 frame
    assert pt.cesarean_classify(3, 2000) == (True, True)   # primary CS
    assert pt.cesarean_classify(4, 2000) == (True, True)   # repeat CS
    assert pt.cesarean_classify(1, 2000) == (True, False)  # vaginal
    assert pt.cesarean_classify(2, 2000) == (True, False)  # VBAC (vaginal)
    assert pt.cesarean_classify(9, 2000) == (False, False)  # not stated
    assert pt.cesarean_classify(None, 2000) == (False, False)
    # 2003-2004 transition years use the <=2004 (DELMETH5-style) rule
    assert pt.cesarean_classify(4, 2003) == (True, True)
    assert pt.cesarean_classify(3, 2004) == (True, True)
    # 2005+ frame
    assert pt.cesarean_classify(2, 2010) == (True, True)   # cesarean
    assert pt.cesarean_classify(1, 2010) == (True, False)  # vaginal
    assert pt.cesarean_classify(9, 2010) == (False, False)  # not stated
    assert pt.cesarean_classify(None, 2022) == (False, False)


def test_age_band_nchs_standard(pt):
    """NCHS-standard maternal-age bands; NULL/out-of-range -> Not stated."""
    assert pt.age_band(13) == "<15"
    assert pt.age_band(14) == "<15"
    assert pt.age_band(15) == "15-19"
    assert pt.age_band(19) == "15-19"
    assert pt.age_band(20) == "20-24"
    assert pt.age_band(29) == "25-29"
    assert pt.age_band(40) == "40-44"
    assert pt.age_band(44) == "40-44"
    assert pt.age_band(45) == "45+"
    assert pt.age_band(54) == "45+"
    assert pt.age_band(None) == pt.NOT_STATED_AGE
    assert pt.age_band(99) == pt.NOT_STATED_AGE  # sentinel -> not stated (§7-#7)
    assert pt.NOT_STATED_AGE


def test_h6_conservation_helper(pt):
    """The builder's row-count conservation check: a stratified breakdown must
    sum back to the unstratified total (H6) — true even when an explicit
    not-stated bucket carries the NULLs."""
    strata = {"White": 70, "Black": 20, pt.NOT_STATED_RACE: 10}
    assert pt.assert_conserves(strata, 100) is True
    with pytest.raises(AssertionError):
        pt.assert_conserves({"White": 70, "Black": 20}, 100)  # dropped NULLs


def test_deterministic_csv_writer(pt, tmp_path):
    """write_tabulation is deterministic: identical input -> byte-identical
    file; rows are sorted by the declared key order; '\\n' line endings; no
    trailing whitespace/timestamps."""
    rows = [
        {"data_year": 2001, "v": 2},
        {"data_year": 2000, "v": 1},
    ]
    cols = ["data_year", "v"]
    p1 = tmp_path / "a.csv"
    p2 = tmp_path / "b.csv"
    pt.write_tabulation(p1, cols, rows, sort_key=lambda r: (r["data_year"],))
    pt.write_tabulation(p2, cols, rows, sort_key=lambda r: (r["data_year"],))
    b1 = p1.read_bytes()
    assert b1 == p2.read_bytes()                        # deterministic
    assert b1.endswith(b"\n") and b"\r" not in b1       # \n only
    txt = p1.read_text().splitlines()
    assert txt[0] == "data_year,v"                      # header
    assert txt[1].startswith("2000") and txt[2].startswith("2001")  # sorted


def test_rate_formatting_is_fixed_precision(pt):
    """Rates use fixed-precision formatting (no platform float drift) so the
    CSVs are byte-identical across machines/runs."""
    assert pt.fmt_rate(20202, 3667758 + 20202, 1000, 2) == "5.48"
    assert pt.fmt_rate(0, 0, 1000, 2) == ""             # empty den -> blank
    assert pt.fmt_pct(819, 10000, 2) == "8.19"


# ── Tier 1: SHAPE of the generated folder (skips if DO build not yet run) ───

def _require_built():
    if not _OUT_DIR.is_dir() or not any(_OUT_DIR.glob("*.csv")):
        pytest.skip("csv/published_tabulations/ not built yet (DO phase)")


def test_expected_csvs_present(pt):
    _require_built()
    present = {p.name for p in _OUT_DIR.glob("*.csv")}
    assert present == _EXPECTED_CSVS, f"CSV set drift: {present ^ _EXPECTED_CSVS}"
    assert (_OUT_DIR / "README.md").is_file()


def test_csvs_well_formed_and_nonempty(pt):
    _require_built()
    for p in sorted(_OUT_DIR.glob("*.csv")):
        b = p.read_bytes()
        assert b and b.endswith(b"\n") and b"\r" not in b, p.name
        with p.open(newline="") as f:
            rows = list(csv.reader(f))
        assert len(rows) >= 2, p.name                   # header + >=1 data row
        ncol = len(rows[0])
        assert all(len(r) == ncol for r in rows), f"ragged: {p.name}"


def test_no_state_or_geography_column(pt):
    """D1: public-use NCHS has no sub-national geography — no cross-tab may
    ship a state/county/region column (the structural guarantee that the
    'per-state' §15.D text was correctly substituted, not faked)."""
    _require_built()
    banned = ("state", "county", "fips", "region", "division", "geo")
    for p in sorted(_OUT_DIR.glob("*.csv")):
        with p.open(newline="") as f:
            header = next(csv.reader(f))
        for h in header:
            assert not any(b in h.lower() for b in banned), f"{p.name}:{h}"


def test_h6_row_count_conservation_in_generated(pt):
    """H6: in every *_x_maternal_race / *_x_maternal_age tab, the per-year
    strata (incl. the explicit not-stated bucket) sum to the unstratified
    year total in its sibling by-year tab."""
    _require_built()
    pt.verify_generated_conservation(_OUT_DIR)  # raises AssertionError on drift


def test_frozen_nvsr_cells_reconcile(pt):
    """FROZEN NVSR validation facts the harmonized data must keep reproducing
    (NOT mutable annotations): if these drift it is a real regression."""
    _require_built()
    facts = pt.frozen_nvsr_checkpoints(_OUT_DIR)
    # fetal deaths >=20wk resident, 2022 == 20,202 (NVSR 73-09)
    assert facts["fetal_2022_ge20wk"] == 20202
    # natality resident live births, 2022 == 3,667,758 (v1 NVSR target)
    assert facts["natality_2022_births"] == 3667758
    # linked unweighted IMR, 2023 == 5.49 (validated imr_per_1000 target)
    assert facts["linked_2023_imr"] == "5.49"
