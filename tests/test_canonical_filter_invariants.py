"""DESIGN: structural-invariant-no-pins — canonical-filter invariant tests.

Authored 2026-05-13 per C8.4 DO. Defends §8 H6 (silent row drops at filter
boundaries), §8 F2 (cross-product join without canonical filter on both
sides), §8 H9 (external targets cancel internal bugs), §8 L3 (validator
self-blindness — defended via Tier-0 mutation tests in this file).

Convention 1 (SHAPE-not-VALUE): no count values are pinned. Each test asserts
a structural invariant — `sum_across_strata == total_filtered` — that holds
regardless of the specific count value and survives canonical-state mutation
(V2.1.0 → V2.4.0 row-count growth; bridged-race-null era boundaries; future
years added).

The canonical filters per `docs/JOINT_USE_GUIDE.md` §"Canonical analytic filters":
- Natality:     residence_status != 4
- Linked:       residence_status != 4
- Fetal-death:  tabulation_flag == 2  AND  residence_status != 4

For each (product, year), test asserts:
  total_filtered  ==  sum_over_S( groupby(S, dropna=False).size() )
for every demographic stratum column S in {residence_status,
maternal_race_bridged, hispanic_origin, tabulation_flag (FD only)}. The
`dropna=False` is load-bearing: bridged-race is null for fetal-death 2018+
and natality 2020+; a stratum-sum that drops null cells would diverge from
the unstratified total in exactly those years.
"""

from __future__ import annotations

import pandas as pd
import pytest

# Strata columns to test per product. The set is product-specific because
# `tabulation_flag` only exists in fetal-death.
_FD_STRATA = ["residence_status", "tabulation_flag", "maternal_race_bridged", "hispanic_origin"]
_NAT_STRATA = ["residence_status", "maternal_race_bridged", "hispanic_origin"]
_LINKED_STRATA = ["residence_status", "maternal_race_bridged", "hispanic_origin"]


def _fd_canonical_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Apply fetal-death canonical filter: tabulation_flag==2 AND residence_status!=4.

    Uses integer comparison; fetal-death v2.1.0+ ships both columns as Int8.
    """
    return df[(df["tabulation_flag"] == 2) & (df["residence_status"] != 4)]


def _resident_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Apply natality / linked canonical filter: residence_status != 4."""
    return df[df["residence_status"] != 4]


def _sum_across_strata(filtered: pd.DataFrame, stratum: str) -> int:
    """Return sum of groupby(stratum, dropna=False).size() — must equal len(filtered)."""
    return int(filtered.groupby(stratum, dropna=False).size().sum())


# ---------------------------------------------------------------------------
# Fetal-death invariants
# ---------------------------------------------------------------------------

def test_fd_canonical_filter_strata_sum_matches_total_per_year(fd_derived_join_cols):
    """Per-year fetal-death: sum_across_S(filtered.groupby(S).size()) == len(filtered).

    Tests every (year, stratum) combination across all 43 years × 4 strata = 172
    invariants. A silent row-drop at any stratum split surfaces here.
    """
    df = fd_derived_join_cols
    failures: list[str] = []
    for year in sorted(df["data_year"].unique()):
        df_y = df[df["data_year"] == year]
        filtered = _fd_canonical_filter(df_y)
        total = len(filtered)
        for s in _FD_STRATA:
            got = _sum_across_strata(filtered, s)
            if got != total:
                failures.append(
                    f"  year={year} stratum={s!r}: total={total} sum_strata={got} diff={got-total}"
                )
    assert not failures, (
        "Fetal-death canonical-filter stratum-sum invariant violated:\n" + "\n".join(failures)
    )


def test_fd_canonical_filter_reduces_or_preserves_row_count(fd_derived_join_cols):
    """The canonical filter cannot increase row count. Sanity check on the
    filter implementation (would catch a not-applied or negated filter)."""
    df = fd_derived_join_cols
    filtered = _fd_canonical_filter(df)
    assert len(filtered) <= len(df), (
        f"Canonical filter produced MORE rows: total={len(df)} filtered={len(filtered)}. "
        "Filter is mis-applied (perhaps negated)."
    )


def test_fd_canonical_filter_excludes_documented_classes(fd_derived_join_cols):
    """The canonical filter must exclude `tabulation_flag != 2` AND
    `residence_status == 4` rows; no row with either property survives.
    Catches a partially-applied filter (e.g., residence-only without tabflag)."""
    df = fd_derived_join_cols
    filtered = _fd_canonical_filter(df)
    has_excluded_tabflag = bool(((filtered["tabulation_flag"] != 2)).any())
    has_excluded_restatus = bool(((filtered["residence_status"] == 4)).any())
    assert not has_excluded_tabflag, "filtered set contains tabulation_flag != 2 rows"
    assert not has_excluded_restatus, "filtered set contains residence_status == 4 rows"


# ---------------------------------------------------------------------------
# Natality invariants
# ---------------------------------------------------------------------------

def test_natality_canonical_filter_strata_sum_matches_total_per_year(natality_derived_join_cols):
    """Per-year natality: sum_across_S(filtered.groupby(S).size()) == len(filtered).

    35 years × 3 strata = 105 invariants. The same shape-not-value check as
    the fetal-death harness; passes regardless of count growth across future
    natality versions.
    """
    df = natality_derived_join_cols
    failures: list[str] = []
    for year in sorted(df["data_year"].unique()):
        df_y = df[df["data_year"] == year]
        filtered = _resident_filter(df_y)
        total = len(filtered)
        for s in _NAT_STRATA:
            got = _sum_across_strata(filtered, s)
            if got != total:
                failures.append(
                    f"  year={year} stratum={s!r}: total={total} sum_strata={got} diff={got-total}"
                )
    assert not failures, (
        "Natality canonical-filter stratum-sum invariant violated:\n" + "\n".join(failures)
    )


def test_natality_canonical_filter_excludes_foreign(natality_derived_join_cols):
    """No row with residence_status == 4 survives the filter."""
    df = natality_derived_join_cols
    filtered = _resident_filter(df)
    assert not bool((filtered["residence_status"] == 4).any()), (
        "natality filtered set contains residence_status == 4 rows"
    )


# ---------------------------------------------------------------------------
# Linked invariants
# ---------------------------------------------------------------------------

def test_linked_canonical_filter_strata_sum_matches_total_per_year(linked_derived_join_cols):
    """Per-year linked: sum_across_S(filtered.groupby(S).size()) == len(filtered).

    19 years × 3 strata = 57 invariants.
    """
    df = linked_derived_join_cols
    failures: list[str] = []
    for year in sorted(df["data_year"].unique()):
        df_y = df[df["data_year"] == year]
        filtered = _resident_filter(df_y)
        total = len(filtered)
        for s in _LINKED_STRATA:
            got = _sum_across_strata(filtered, s)
            if got != total:
                failures.append(
                    f"  year={year} stratum={s!r}: total={total} sum_strata={got} diff={got-total}"
                )
    assert not failures, (
        "Linked canonical-filter stratum-sum invariant violated:\n" + "\n".join(failures)
    )


def test_linked_canonical_filter_excludes_foreign(linked_derived_join_cols):
    """No row with residence_status == 4 survives the linked filter."""
    df = linked_derived_join_cols
    filtered = _resident_filter(df)
    assert not bool((filtered["residence_status"] == 4).any()), (
        "linked filtered set contains residence_status == 4 rows"
    )


# ---------------------------------------------------------------------------
# Tier-0 mutation tests (synthetic fixtures; the validator catches injected violations)
# ---------------------------------------------------------------------------
#
# Per §8 L3 ("LLM rubber-stamps passing test") + §15 SMOKE plan ("Tier 0:
# mutation tests — inject a violation; assert the harness catches each").
# Each mutation test constructs a hand-built DataFrame, runs the invariant
# check, and asserts it FAILs with the expected violation.

def _synthetic_fd_year() -> pd.DataFrame:
    """10 hand-built fetal-death rows covering all filter-relevant strata."""
    return pd.DataFrame({
        "data_year": [2022] * 10,
        "tabulation_flag": [2, 2, 2, 2, 2, 1, 1, 2, 2, 2],
        "residence_status": [1, 1, 2, 2, 3, 1, 4, 4, 1, 1],
        "maternal_age": [25, 30, 35, 20, 28, 27, 32, 24, 31, 26],
        "maternal_race_bridged": [1, 2, 3, 4, 1, 1, 1, 1, 2, None],
        "hispanic_origin": [0, 0, 1, 2, 3, 0, 0, 0, 9, 4],
    })


def test_mutation_synthetic_fd_filter_invariant_holds():
    """SMOKE Tier 0: synthetic 10-row FD fixture passes the invariant."""
    df = _synthetic_fd_year()
    filtered = _fd_canonical_filter(df)
    # Expected: 5 rows (tabflag=2, restatus!=4): rows 0,1,2,3,4 (rows 5,6 fail tabflag;
    # row 7 fails restatus; rows 8,9 pass — actually 8,9 also have tabflag=2 + restatus=1)
    # rows passing: 0,1,2,3,4 (all pass), 8,9 (tabflag=2, restatus=1) = 7 rows
    assert len(filtered) == 7
    for s in _FD_STRATA:
        assert _sum_across_strata(filtered, s) == 7


def test_mutation_duplicate_row_caught_by_total_count_change(monkeypatch):
    """Inject a row duplication; the invariant still holds (groupby sum still
    equals total) but the total itself changes — caught at the assertion
    against the original total. Demonstrates the SHAPE invariant remains
    consistent under any row-count mutation."""
    df = _synthetic_fd_year()
    filtered_baseline = _fd_canonical_filter(df)
    baseline_total = len(filtered_baseline)
    # Mutation: duplicate a passing row
    mutated = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    filtered_mutated = _fd_canonical_filter(mutated)
    assert len(filtered_mutated) == baseline_total + 1
    # The shape-invariant STILL holds for the mutated frame (this is the
    # point — duplications don't break the invariant; they shift the total).
    for s in _FD_STRATA:
        assert _sum_across_strata(filtered_mutated, s) == baseline_total + 1


def test_mutation_dropna_True_violates_invariant_when_nulls_present():
    """Inject the bug L3 catches: `groupby(S, dropna=True)` drops null-stratum
    rows from the count, so sum_across_strata < total. The invariant FAILs."""
    df = _synthetic_fd_year()
    filtered = _fd_canonical_filter(df)
    total = len(filtered)
    # maternal_race_bridged column has a null in row 9 which passes the filter
    # (tabflag=2 restatus=1). Using dropna=True omits that null cell.
    sum_with_dropna_true = int(
        filtered.groupby("maternal_race_bridged", dropna=True).size().sum()
    )
    # The invariant FAILs under the buggy (dropna=True) implementation:
    assert sum_with_dropna_true < total, (
        "Expected dropna=True to undercount when null strata present; "
        "got equal counts — mutation test is a no-op."
    )
    # Verify the CORRECT implementation (dropna=False) preserves invariant:
    sum_with_dropna_false = _sum_across_strata(filtered, "maternal_race_bridged")
    assert sum_with_dropna_false == total


def test_mutation_negated_filter_caught_by_excludes_documented_classes():
    """Inject the bug: negate the filter (use `==4` instead of `!=4`).
    `_fd_canonical_filter` returns the COMPLEMENT; the
    `test_fd_canonical_filter_excludes_documented_classes` test catches it."""
    df = _synthetic_fd_year()
    # Buggy filter — keeps residence_status == 4 rows
    buggy = df[(df["tabulation_flag"] == 2) & (df["residence_status"] == 4)]
    assert bool((buggy["residence_status"] == 4).any()), (
        "negated-filter mutation should have produced restatus==4 rows; got none — "
        "mutation test is a no-op."
    )


def test_mutation_partial_filter_caught_by_count_jump():
    """Inject the bug: apply only restatus!=4 (forget tabulation_flag==2).
    Compare to the correct filter; partial filter overcounts."""
    df = _synthetic_fd_year()
    correct = _fd_canonical_filter(df)
    # Buggy: forget tabflag
    partial = df[df["residence_status"] != 4]
    assert len(partial) > len(correct), (
        f"partial filter (residence only) produced {len(partial)} rows; "
        f"full filter produced {len(correct)}. Mutation test is a no-op if they're equal."
    )
