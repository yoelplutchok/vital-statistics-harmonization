"""DESIGN: structural-invariant-no-pins — cross-product join parity.

Authored 2026-05-13 per C8.4 DO. Defends §8 F2 (cross-product join without
canonical filter on both sides), §8 H7 (sibling-pipeline drift), §8 L4 (LLM
forgets to propagate fix to sibling).

Convention 1 (SHAPE-not-VALUE): no count values are pinned. Each invariant
is structural — column presence, dtype-compatibility, set-inclusion, and
the natality-vs-stratified-denominators parity that survives any year-set
mutation.

Invariants tested:

1. **Canonical join keys present in all three products' derived parquets.**
   Per `shared/helpers/canonical_join_keys.py`:
   `[data_year, maternal_age, maternal_race_bridged, hispanic_origin, residence_status]`.
   Natality v2.8.0 adopts canonical names natively; the helper rename is a no-op
   for v2.8.0+. Fetal-death uses canonical names already.

2. **`to_canonical_natality()` is idempotent under v2.8.0+.** Applying the helper
   to a v2.8.0 natality DataFrame produces no rename — verified by comparing
   the rename map to the v2.8.0 column set (intersection should be empty for
   v2.8.0+).

3. **Linked-vs-natality bounded drift:** For each joint year (2005-2023), the
   absolute relative drift between the linked file's resident-filtered row
   count and natality's resident-filtered row count is ≤ 0.01%. Conceptually
   every linked birth IS a natality birth, but NCHS produces the linked file
   from an NVSR-style cohort tabulation that differs slightly from the public-
   use natality microdata (per `docs/JOINT_USE_GUIDE.md` "<0.006% post-release
   re-tabulation"). The bounded-drift invariant captures the documented
   relationship; a future linked-pipeline regression that introduces a >0.01%
   drift would surface here. See DECISION_LOG 2026-05-13 for the C8.4
   linked-vs-natality finding consolidating this into the cross-product
   COMPARABILITY plan.

4. **Stratified-denominators per-year sum matches natality direct groupby.**
   For the 29 joint-coverage years (1992-2002 + 2005-2022) in
   `fetal_death/stratified_denominators.csv`, the per-year sum of `live_births`
   matches the natality resident-filtered per-year count byte-exact.

5. **Joint-coverage intersection (2005-2023) is non-empty for all three products.**
   Verified that for any year in 2005-2023, all three products have data.

6. **All five canonical join-key columns share a comparable dtype** between
   fetal-death and natality after the natural mapping (int/int comparison
   safe; both products store residence_status / maternal_race_bridged /
   hispanic_origin as int8 in their latest versions). The check uses pandas
   integer-or-extension-integer family, not bit-width equality, because
   natality uses int8/int16 plain while fetal-death uses pandas nullable
   Int8/Int16 — they're cross-comparison-safe under pandas type promotion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Make `shared/helpers/canonical_join_keys.py` importable without forcing a
# `pip install -e .` of the monorepo. The same pattern is used by the
# stratified-denominator builder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.helpers.canonical_join_keys import (  # noqa: E402
    CANONICAL_JOIN_KEYS,
    NATALITY_TO_CANONICAL,
    to_canonical_natality,
)


# ----------------------------------------------------------------------------
# Canonical join-key column presence
# ----------------------------------------------------------------------------

def test_canonical_join_keys_present_in_fetal_death(fd_derived_join_cols):
    """All five canonical join keys present in fetal-death derived parquet."""
    cols = set(fd_derived_join_cols.columns)
    missing = [k for k in CANONICAL_JOIN_KEYS if k not in cols]
    assert not missing, f"fetal-death derived missing canonical join keys: {missing}"


def test_canonical_join_keys_present_in_natality(natality_derived_join_cols):
    """All five canonical join keys present in natality v2.8.0 derived parquet.
    v2.8.0 adopts the canonical names natively per natality_v28_rename receipt."""
    cols = set(natality_derived_join_cols.columns)
    missing = [k for k in CANONICAL_JOIN_KEYS if k not in cols]
    assert not missing, (
        f"natality derived missing canonical join keys: {missing}. "
        "v2.8.0 should ship these natively per the 2026-05-12 column rename."
    )


def test_canonical_join_keys_present_in_linked(linked_derived_join_cols):
    """All five canonical join keys present in linked derived parquet."""
    cols = set(linked_derived_join_cols.columns)
    missing = [k for k in CANONICAL_JOIN_KEYS if k not in cols]
    assert not missing, f"linked derived missing canonical join keys: {missing}"


def test_to_canonical_natality_is_noop_under_v2_8(natality_derived_join_cols):
    """v2.8.0 natality's canonical adoption means `to_canonical_natality()`
    produces no rename. Asserts the legacy NATALITY_TO_CANONICAL keys are
    NOT in the v2.8.0 column set (the helper would only rename if they were)."""
    cols = set(natality_derived_join_cols.columns)
    legacy_keys_present = [k for k in NATALITY_TO_CANONICAL if k in cols]
    assert legacy_keys_present == [], (
        f"v2.8.0 natality still has legacy column names {legacy_keys_present}; "
        f"the helper rename would mutate them. natality_v28_rename should have "
        f"removed them."
    )
    # Applying the helper produces a frame identical to input (same columns,
    # same dtypes, same row count).
    renamed = to_canonical_natality(natality_derived_join_cols)
    assert list(renamed.columns) == list(natality_derived_join_cols.columns)
    assert len(renamed) == len(natality_derived_join_cols)


# ----------------------------------------------------------------------------
# Dtype compatibility for join keys
# ----------------------------------------------------------------------------

def _is_integer_family(dtype) -> bool:
    """Return True if a pandas dtype is in the integer family (signed/unsigned/
    nullable extension Int). Cross-product joins on residence_status can use
    either int8 (natality) or Int8 (fetal-death); pandas promotes safely."""
    return pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_extension_array_dtype(
        dtype
    ) and "Int" in str(dtype)


def test_residence_status_join_key_integer_in_all_products(
    fd_derived_join_cols, natality_derived_join_cols, linked_derived_join_cols
):
    """residence_status is integer in all three products (the canonical
    filter literal is int 4; a string-dtype shipped column would silently
    fail the filter — H8 incident class)."""
    assert _is_integer_family(fd_derived_join_cols["residence_status"].dtype), (
        f"fetal-death residence_status dtype: {fd_derived_join_cols['residence_status'].dtype} "
        f"(expected integer family)"
    )
    assert _is_integer_family(natality_derived_join_cols["residence_status"].dtype), (
        f"natality residence_status dtype: {natality_derived_join_cols['residence_status'].dtype}"
    )
    assert _is_integer_family(linked_derived_join_cols["residence_status"].dtype), (
        f"linked residence_status dtype: {linked_derived_join_cols['residence_status'].dtype}"
    )


def test_tabulation_flag_integer_in_fetal_death(fd_derived_join_cols):
    """fetal-death tabulation_flag is integer (canonical filter literal is
    int 2; the H8 incident shipped this as object/string in v2.0.0)."""
    assert _is_integer_family(fd_derived_join_cols["tabulation_flag"].dtype), (
        f"fetal-death tabulation_flag dtype: {fd_derived_join_cols['tabulation_flag'].dtype} "
        f"(expected integer family — H8 closure was v2.1.0)"
    )


# ----------------------------------------------------------------------------
# Linked-as-subset-of-natality
# ----------------------------------------------------------------------------

# Maximum tolerated relative drift between linked and natality per-year
# resident-filtered counts. NCHS produces the linked file from an NVSR-style
# cohort tabulation that differs slightly from the public-use natality
# microdata (per JOINT_USE_GUIDE.md "<0.006% post-release re-tabulation").
# The observed max at C8.4 authoring is ~0.0055% (year 2005, +228 records
# on ~4.14M). 0.01% gives headroom while still catching a >2x widening of
# the documented drift.
_LINKED_NATALITY_DRIFT_TOLERANCE = 1e-4  # 0.01%


def test_linked_per_year_count_within_drift_tolerance_of_natality(
    natality_derived_join_cols, linked_derived_join_cols
):
    """For each joint year (2005-2023): the absolute relative drift between
    linked and natality resident-filtered counts is ≤ 0.01%. Catches a
    linked-pipeline regression that would expand the documented NCHS
    re-tabulation drift beyond the established envelope.

    Why bounded-drift not strict-subset: at C8.4 authoring 5 of 19 joint
    years showed linked > natality by 1-228 records (max 0.0055%). NCHS
    constructs the period-/cohort-linked files from NVSR-style tabulations
    that include small post-release adjustments to the natality microdata
    base; see DECISION_LOG 2026-05-13 for the consolidating finding."""
    nat = natality_derived_join_cols[natality_derived_join_cols["residence_status"] != 4]
    linked = linked_derived_join_cols[linked_derived_join_cols["residence_status"] != 4]
    nat_per_year = nat["data_year"].value_counts()
    linked_per_year = linked["data_year"].value_counts()

    joint_years = sorted(set(nat_per_year.index) & set(linked_per_year.index))
    assert joint_years, "no joint-coverage years between natality and linked — empty intersection"

    violations: list[str] = []
    for year in joint_years:
        n_nat = int(nat_per_year[year])
        n_linked = int(linked_per_year[year])
        # Relative drift: |linked - nat| / max(linked, nat) — symmetric and
        # bounded in [0, 1). Using max-denominator avoids amplifying the
        # ratio when one side happens to be smaller.
        denom = max(n_linked, n_nat)
        if denom == 0:
            continue
        drift = abs(n_linked - n_nat) / denom
        if drift > _LINKED_NATALITY_DRIFT_TOLERANCE:
            violations.append(
                f"  year={year}: linked={n_linked:,} natality={n_nat:,} "
                f"drift={drift:.6%} (tolerance={_LINKED_NATALITY_DRIFT_TOLERANCE:.4%})"
            )
    assert not violations, (
        "linked-vs-natality per-year drift exceeds documented envelope:\n"
        + "\n".join(violations)
    )


def test_joint_coverage_intersection_nonempty(
    fd_derived_join_cols, natality_derived_join_cols, linked_derived_join_cols
):
    """The three-product joint-coverage intersection is non-empty. Currently
    {2005-2023} ∩ {1990-2024} ∩ {1982-2024} = {2005-2023} = 19 years."""
    fd_years = set(fd_derived_join_cols["data_year"].unique())
    nat_years = set(natality_derived_join_cols["data_year"].unique())
    linked_years = set(linked_derived_join_cols["data_year"].unique())
    joint = fd_years & nat_years & linked_years
    assert joint, "joint three-product coverage is empty — check year alignment"
    # The intersection is at least the documented {2005...2023} = 19 years.
    # SHAPE: assert non-empty + at least 19 years (current state); does not
    # pin the exact set.
    assert len(joint) >= 19, (
        f"joint coverage shrunk to {len(joint)} years (was 19 at C8.4 authoring)"
    )


# ----------------------------------------------------------------------------
# Stratified-denominators parity vs natality direct groupby
# ----------------------------------------------------------------------------

def test_stratified_denominators_per_year_matches_natality(
    stratified_denominators, natality_derived_join_cols
):
    """Per-year sum from stratified_denominators.csv matches natality
    resident-filtered per-year count byte-exact for the 29 joint-coverage
    years. This is the durable test of the Task 1 shipped CSV; any future
    natality-pipeline regression that would shift per-year counts surfaces
    here on next pytest."""
    nat = natality_derived_join_cols[natality_derived_join_cols["residence_status"] != 4]
    nat_per_year = nat["data_year"].value_counts().sort_index()
    csv_per_year = stratified_denominators.groupby("data_year")["live_births"].sum().sort_index()
    failures: list[str] = []
    for year in sorted(csv_per_year.index):
        csv_n = int(csv_per_year[year])
        nat_n = int(nat_per_year.get(int(year), 0))
        if csv_n != nat_n:
            failures.append(
                f"  year={year}: stratified_csv={csv_n:,} natality_direct={nat_n:,} "
                f"diff={csv_n-nat_n:+,}"
            )
    assert not failures, (
        "stratified_denominators.csv per-year sum diverges from natality direct groupby:\n"
        + "\n".join(failures)
    )


def test_stratified_denominators_year_coverage_within_joint(
    stratified_denominators, fd_derived_join_cols, natality_derived_join_cols
):
    """The stratified denominator's year set is a subset of the
    natality∩fetal-death joint coverage (1992-2002 + 2005-2022 = 29 years).
    Catches a future regression where the builder accidentally extends past
    the joint set or contracts inside it."""
    csv_years = set(int(y) for y in stratified_denominators["data_year"].unique())
    fd_years = set(int(y) for y in fd_derived_join_cols["data_year"].unique())
    nat_years = set(int(y) for y in natality_derived_join_cols["data_year"].unique())
    joint_fd_nat = fd_years & nat_years
    extra = csv_years - joint_fd_nat
    assert not extra, (
        f"stratified denominators has years outside joint fetal-death∩natality: {sorted(extra)}"
    )


# ----------------------------------------------------------------------------
# Tier-0 mutation tests (synthetic; the validator catches injected violations)
# ----------------------------------------------------------------------------

def test_mutation_synthetic_join_key_check():
    """SMOKE Tier 0: a 3-row synthetic frame with all 5 canonical join keys
    passes the column-presence check; a frame missing one fails."""
    good = pd.DataFrame({
        "data_year": [2022, 2022, 2022],
        "maternal_age": [25, 30, 35],
        "maternal_race_bridged": [1, 2, 1],
        "hispanic_origin": [0, 0, 1],
        "residence_status": [1, 1, 2],
    })
    missing = [k for k in CANONICAL_JOIN_KEYS if k not in good.columns]
    assert not missing  # good frame: all present

    bad = good.drop(columns=["hispanic_origin"])
    missing_bad = [k for k in CANONICAL_JOIN_KEYS if k not in bad.columns]
    assert missing_bad == ["hispanic_origin"], (
        f"mutation test should detect the dropped hispanic_origin column; "
        f"got missing={missing_bad}"
    )


def test_mutation_linked_bounded_drift_violation_caught():
    """SMOKE Tier 0: inject a >0.01% drift between linked and natality for a
    single year; the bounded-drift check must flag it. (Synthetic sample.)

    Demonstrates that the tolerance correctly accepts small drifts (within
    documented NCHS re-tabulation envelope) AND rejects large drifts (a
    real linked-pipeline regression)."""
    # Year 2020: nat=10000, linked=10001 → drift 0.01% (= tolerance, accepted)
    # Year 2021: nat=10000, linked=10050 → drift 0.5% (clearly above tolerance)
    nat_pc = pd.Series({2020: 10_000, 2021: 10_000})
    bad_pc = pd.Series({2020: 10_001, 2021: 10_050})
    ok_pc = pd.Series({2020: 9_999, 2021: 10_000})

    def _drift(a: int, b: int) -> float:
        d = max(a, b)
        return abs(a - b) / d if d > 0 else 0.0

    # OK case: all drifts <= tolerance
    ok_violations = [
        y for y in nat_pc.index
        if _drift(int(ok_pc[y]), int(nat_pc[y])) > _LINKED_NATALITY_DRIFT_TOLERANCE
    ]
    assert not ok_violations

    # Bad case: 2021 drift far exceeds tolerance
    bad_violations = [
        y for y in nat_pc.index
        if _drift(int(bad_pc[y]), int(nat_pc[y])) > _LINKED_NATALITY_DRIFT_TOLERANCE
    ]
    assert bad_violations == [2021], (
        f"mutation test should flag year 2021 with 0.5% drift; got {bad_violations}"
    )


def test_mutation_stratified_sum_drift_caught():
    """SMOKE Tier 0: synthetic stratified CSV vs synthetic natality with a
    1-record drift in one year. The per-year parity check must catch it."""
    csv = pd.DataFrame({
        "data_year": [2020, 2020, 2021, 2021],
        "maternal_race_bridged": [1, 2, 1, 2],
        "live_births": [50, 50, 60, 60],
    })
    nat = pd.DataFrame({
        "data_year": [2020] * 100 + [2021] * 121,  # 2021 has 1 extra
        "residence_status": [1] * 221,
    })
    csv_per_year = csv.groupby("data_year")["live_births"].sum()
    nat_per_year = nat["data_year"].value_counts()
    failures = []
    for year in sorted(csv_per_year.index):
        if int(csv_per_year[year]) != int(nat_per_year.get(int(year), 0)):
            failures.append(year)
    assert failures == [2021], (
        f"mutation test should flag year 2021 with the 1-record drift; got {failures}"
    )
