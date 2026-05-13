"""DESIGN: tracks-current-state — B.6 mutation test for fetal_death validate_2022.py.

Per C8.12 §15: this validator hardcodes its expected counts as inline literals
in `main()` (e.g., `check("Total US file records", 40113, len(df))`), so the
cleanest module-level mutation point is the `check()` function itself. The
mutation replaces `check` with a wrapper that bumps every expected value by
+999,999 before the PASS/FAIL determination — every check then FAILs, the
n_fail summary at end is >0, and `sys.exit(1)` propagates.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.

Skip-if-2022-raw-parquet-missing (this validator reads the per-year raw
parquet, not the harmonized output).
"""

from __future__ import annotations

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = REPO_ROOT / "fetal_death/scripts/05_validate/validate_2022.py"
RAW_2022_PARQUET = REPO_ROOT / "output/yearly_clean/fetal_death_2022_raw.parquet"


def test_validate_2022_catches_inflated_expected_via_check_wrapper() -> None:
    for required in (VALIDATOR, RAW_2022_PARQUET):
        if not required.exists():
            pytest.skip(f"{required.relative_to(REPO_ROOT)} not on disk")

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=[
            "_orig_check = v.check",
            "v.check = lambda name, expected, actual, tolerance=0: "
            "_orig_check(name, expected + 999_999, actual, tolerance)",
        ],
    )
    assert_mutation_caught(result, fail_markers=["FAIL", "*** "])
