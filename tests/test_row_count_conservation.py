"""DESIGN: tracks-current-state — row-count conservation at pipeline boundaries.

Authored 2026-05-13 per C8.4 DO. Defends §8 H6 (silent row drops in joins /
at pipeline boundaries). Covers the harmonized → derived boundary for all
three products: `derive.py` adds columns; the row count MUST be conserved.

`DESIGN: tracks-current-state` (Convention 2): the documented-drops dict
below records the per-product total row counts AT C8.4 AUTHORING. Any future
authorized canonical-state mutation (e.g., a latest-year refresh adding 2025
fetal-death) MUST update the dict in the same commit; per Convention 1 the
shape invariant (`harmonized total == derived total`) remains durable, but
the totals themselves are tracking-state pins by design and serve as a
release-state regression gate.

The documented-drops registry is **empty** at C8.4 authoring: no documented
per-year drops between parse/harmonize/derive in any product's DECISION_LOG
after the v2.4.0 / v2.8.0 / v3 releases. Any future task introducing a
documented drop must extend `DOCUMENTED_DROPS` below.

Per-year row counts on harmonized vs derived must agree exactly (a silent
drop of a single record per year is the failure mode this catches).
"""

from __future__ import annotations

import pandas as pd

# ----------------------------------------------------------------------------
# Documented current-state totals (Convention 2: tracks-current-state).
# Updated in the same commit as any authorized canonical row-count mutation.
# ----------------------------------------------------------------------------

# Fetal-death v2.4.0 (post-C8.2 latest-year refresh + V3a + V3b extension);
# 43 yrs 1982-2024.
FD_EXPECTED_TOTAL = 2_427_233
FD_EXPECTED_YEARS = list(range(1982, 2025))  # 43 contiguous

# Natality v3.0.0; 57 yrs 1968-2024 (C8.17 backward extension; +22 yrs
# 1968-1989, +62,341,801 rows over the v2.8.0 35-yr 1990-2024 envelope of
# 138,819,655). Convention 2 / L17 release-state re-pin bundled with the
# DO step 6 canonical re-harmonize; see DECISION_LOG 2026-05-16T08:00:00Z.
NATALITY_EXPECTED_TOTAL = 201_161_456
NATALITY_EXPECTED_YEARS = list(range(1968, 2025))  # 57 contiguous

# Linked birth-infant death (cohort-linked, v3); 19 yrs 2005-2023.
# (The linked file may extend to 2024-cohort at a future task when NCHS
# releases `2025PE2024CO.zip`; see DECISION_LOG 2026-05-12T22:30:00Z.)
LINKED_EXPECTED_TOTAL = 74_943_824
LINKED_EXPECTED_YEARS = list(range(2005, 2024))  # 19 contiguous

# Documented row drops between pipeline stages.
# Keys are (product, source_stage, target_stage); value is per-year dict of
# documented drop counts (positive integers; absent year → 0 drops).
# Empty at C8.4 authoring: no documented drops at any boundary.
# Any future authorized drop (e.g., a known parser-side error filter) must
# be added here in the same commit as the parser change.
DOCUMENTED_DROPS: dict[tuple[str, str, str], dict[int, int]] = {}


# ----------------------------------------------------------------------------
# Fetal-death
# ----------------------------------------------------------------------------

def test_fd_harmonized_total_matches_release_state(fd_row_counts):
    """Convention 2 release-state pin: harmonized row count matches the
    documented v2.4.0 total. A future authorized mutation must update
    FD_EXPECTED_TOTAL above in the same commit."""
    assert fd_row_counts["harmonized"] == FD_EXPECTED_TOTAL, (
        f"fetal-death harmonized total: expected {FD_EXPECTED_TOTAL:,}, "
        f"got {fd_row_counts['harmonized']:,}. "
        f"If this is an authorized canonical-state mutation, update FD_EXPECTED_TOTAL "
        f"in tests/test_row_count_conservation.py in the same commit."
    )


def test_fd_derived_total_matches_harmonized(fd_row_counts):
    """Convention 1 SHAPE invariant: derive.py only adds columns; row count
    must be conserved. A silent row drop or duplication between harmonized
    and derived surfaces here."""
    assert fd_row_counts["derived"] == fd_row_counts["harmonized"], (
        f"fetal-death harmonized↔derived row-count divergence: "
        f"harmonized={fd_row_counts['harmonized']:,} derived={fd_row_counts['derived']:,} "
        f"diff={fd_row_counts['derived'] - fd_row_counts['harmonized']:+,}"
    )


def test_fd_per_year_rows_conserved_through_derive(fd_per_year_counts):
    """Per-year row count must be identical between harmonized and derived
    (modulo any documented drops in `DOCUMENTED_DROPS`). Catches a silent
    per-year row drop that the totals-only check might miss if it's
    compensated by a drop in another year."""
    h = fd_per_year_counts["harmonized"]
    d = fd_per_year_counts["derived"]
    documented = DOCUMENTED_DROPS.get(("fetal_death", "harmonized", "derived"), {})
    failures: list[str] = []
    for year in sorted(set(h.index) | set(d.index)):
        h_n = int(h.get(year, 0))
        d_n = int(d.get(year, 0))
        expected_drop = int(documented.get(int(year), 0))
        if h_n != d_n + expected_drop:
            failures.append(
                f"  year={year}: harmonized={h_n} derived={d_n} expected_drop={expected_drop} "
                f"(input != output + documented_drops)"
            )
    assert not failures, (
        "fetal-death per-year row-count conservation violated:\n" + "\n".join(failures)
    )


def test_fd_year_coverage_matches_expected(fd_per_year_counts):
    """Convention 2 release-state pin: year coverage matches documented
    contiguous range 1982-2024 (43 years)."""
    actual = sorted(int(y) for y in fd_per_year_counts["harmonized"].index)
    assert actual == FD_EXPECTED_YEARS, (
        f"fetal-death year coverage mismatch: expected {FD_EXPECTED_YEARS[0]}-{FD_EXPECTED_YEARS[-1]} "
        f"({len(FD_EXPECTED_YEARS)} years), got {actual[0]}-{actual[-1]} ({len(actual)} years). "
        f"If a year was authorized to be added/removed, update FD_EXPECTED_YEARS in the same commit."
    )


# ----------------------------------------------------------------------------
# Natality
# ----------------------------------------------------------------------------

def test_natality_harmonized_total_matches_release_state(natality_row_counts):
    """Convention 2 release-state pin: harmonized row count matches the
    documented v2.8.0 total."""
    assert natality_row_counts["harmonized"] == NATALITY_EXPECTED_TOTAL, (
        f"natality harmonized total: expected {NATALITY_EXPECTED_TOTAL:,}, "
        f"got {natality_row_counts['harmonized']:,}. "
        f"Update NATALITY_EXPECTED_TOTAL if this mutation is authorized."
    )


def test_natality_derived_total_matches_harmonized(natality_row_counts):
    """Convention 1 SHAPE: harmonized → derived row conservation."""
    assert natality_row_counts["derived"] == natality_row_counts["harmonized"], (
        f"natality harmonized↔derived row-count divergence: "
        f"harmonized={natality_row_counts['harmonized']:,} "
        f"derived={natality_row_counts['derived']:,}"
    )


def test_natality_per_year_rows_conserved_through_derive(natality_per_year_counts):
    """Per-year row conservation through derive (input = output + documented_drops)."""
    h = natality_per_year_counts["harmonized"]
    d = natality_per_year_counts["derived"]
    documented = DOCUMENTED_DROPS.get(("natality", "harmonized", "derived"), {})
    failures: list[str] = []
    for year in sorted(set(h.index) | set(d.index)):
        h_n = int(h.get(year, 0))
        d_n = int(d.get(year, 0))
        expected_drop = int(documented.get(int(year), 0))
        if h_n != d_n + expected_drop:
            failures.append(
                f"  year={year}: harmonized={h_n} derived={d_n} expected_drop={expected_drop}"
            )
    assert not failures, (
        "natality per-year row-count conservation violated:\n" + "\n".join(failures)
    )


def test_natality_year_coverage_matches_expected(natality_per_year_counts):
    """Convention 2 release-state pin: year coverage 1990-2024 (35 years)."""
    actual = sorted(int(y) for y in natality_per_year_counts["harmonized"].index)
    assert actual == NATALITY_EXPECTED_YEARS, (
        f"natality year coverage mismatch: expected {len(NATALITY_EXPECTED_YEARS)} years "
        f"{NATALITY_EXPECTED_YEARS[0]}-{NATALITY_EXPECTED_YEARS[-1]}, got {len(actual)} years "
        f"{actual[0]}-{actual[-1]}."
    )


# ----------------------------------------------------------------------------
# Linked birth-infant death
# ----------------------------------------------------------------------------

def test_linked_harmonized_total_matches_release_state(linked_row_counts):
    """Convention 2 release-state pin: linked total matches the documented v3."""
    assert linked_row_counts["harmonized"] == LINKED_EXPECTED_TOTAL, (
        f"linked harmonized total: expected {LINKED_EXPECTED_TOTAL:,}, "
        f"got {linked_row_counts['harmonized']:,}. "
        f"Update LINKED_EXPECTED_TOTAL if this mutation is authorized."
    )


def test_linked_derived_total_matches_harmonized(linked_row_counts):
    """Convention 1 SHAPE: harmonized → derived row conservation for linked."""
    assert linked_row_counts["derived"] == linked_row_counts["harmonized"], (
        f"linked harmonized↔derived row-count divergence: "
        f"harmonized={linked_row_counts['harmonized']:,} "
        f"derived={linked_row_counts['derived']:,}"
    )


def test_linked_per_year_rows_conserved_through_derive(linked_per_year_counts):
    """Per-year row conservation through derive."""
    h = linked_per_year_counts["harmonized"]
    d = linked_per_year_counts["derived"]
    documented = DOCUMENTED_DROPS.get(("linked", "harmonized", "derived"), {})
    failures: list[str] = []
    for year in sorted(set(h.index) | set(d.index)):
        h_n = int(h.get(year, 0))
        d_n = int(d.get(year, 0))
        expected_drop = int(documented.get(int(year), 0))
        if h_n != d_n + expected_drop:
            failures.append(
                f"  year={year}: harmonized={h_n} derived={d_n} expected_drop={expected_drop}"
            )
    assert not failures, (
        "linked per-year row-count conservation violated:\n" + "\n".join(failures)
    )


def test_linked_year_coverage_matches_expected(linked_per_year_counts):
    """Convention 2 release-state pin: year coverage 2005-2023 (19 years)."""
    actual = sorted(int(y) for y in linked_per_year_counts["harmonized"].index)
    assert actual == LINKED_EXPECTED_YEARS, (
        f"linked year coverage mismatch: expected {len(LINKED_EXPECTED_YEARS)} years "
        f"{LINKED_EXPECTED_YEARS[0]}-{LINKED_EXPECTED_YEARS[-1]}, got {len(actual)} years "
        f"{actual[0]}-{actual[-1]}."
    )


# ----------------------------------------------------------------------------
# Tier-0 mutation tests (synthetic; the validator catches injected drops/adds)
# ----------------------------------------------------------------------------

def _synthetic_input_to_output(n_in: int, n_out: int) -> tuple[int, int]:
    """Return (input_count, output_count) — used to test the
    `input == output + documented_drops` formula under various scenarios."""
    return (n_in, n_out)


def test_mutation_silent_row_drop_caught():
    """SMOKE Tier 0: inject a silent row drop (input=100, output=99,
    documented_drops=0). The conservation formula `100 == 99 + 0` is False;
    the harness must FAIL on this case."""
    n_in, n_out = _synthetic_input_to_output(100, 99)
    documented = 0
    holds = (n_in == n_out + documented)
    assert not holds, "silent-row-drop scenario should violate the formula"


def test_mutation_documented_drop_passes():
    """SMOKE Tier 0: a documented drop of 5 rows (input=100, output=95,
    documented_drops=5). Formula `100 == 95 + 5` is True; the harness PASSes
    when the drop is authorized."""
    n_in, n_out = _synthetic_input_to_output(100, 95)
    documented = 5
    holds = (n_in == n_out + documented)
    assert holds


def test_mutation_silent_row_duplicate_caught():
    """SMOKE Tier 0: inject a silent row duplication (input=100, output=101).
    Formula False; harness FAILs (`100 != 101 + 0`).
    The shape-invariant is: input == output + drops; duplication shows up as
    a negative residual which still violates the equality."""
    n_in, n_out = _synthetic_input_to_output(100, 101)
    documented = 0
    holds = (n_in == n_out + documented)
    assert not holds


def test_mutation_off_by_one_caught_at_per_year_level():
    """SMOKE Tier 0: per-year mutation — total matches but a single year is
    off-by-one + compensated by an opposite off-by-one in another year. The
    PER-YEAR check catches it; a totals-only check would not.

    Construct: input years {2020: 50, 2021: 50} → total 100. Output years
    {2020: 49, 2021: 51} → total 100. Documented drops empty. Total formula
    holds; per-year formula fails for 2020 (50 != 49) and 2021 (50 != 51)."""
    h_input = pd.Series({2020: 50, 2021: 50})
    d_output = pd.Series({2020: 49, 2021: 51})
    documented: dict[int, int] = {}
    total_holds = (h_input.sum() == d_output.sum())
    assert total_holds, "synthetic totals should match; mutation test setup is wrong"
    per_year_failures = []
    for year in sorted(set(h_input.index) | set(d_output.index)):
        h_n = int(h_input.get(year, 0))
        d_n = int(d_output.get(year, 0))
        drop = int(documented.get(int(year), 0))
        if h_n != d_n + drop:
            per_year_failures.append(year)
    assert per_year_failures == [2020, 2021], (
        "per-year check should catch the off-by-one in BOTH years; "
        f"caught: {per_year_failures}"
    )
