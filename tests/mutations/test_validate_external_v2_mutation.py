"""DESIGN: tracks-current-state — B.6 mutation test for fetal_death validate_external_v2.py.

Per C8.12 §15: mutates `NVSR57_FETAL_DEATHS_GTE20[1995]` from 27,294 to
999,999 — an impossible single-year fetal-death count — and asserts the
validator's V2-era count comparison catches it via `sys.exit(1)`.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.
"""

from __future__ import annotations

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = REPO_ROOT / "fetal_death/scripts/05_validate/validate_external_v2.py"
HARM_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"


def test_validate_external_v2_catches_inflated_nvsr57_expected() -> None:
    for required in (VALIDATOR, HARM_PARQUET):
        if not required.exists():
            pytest.skip(f"{required.relative_to(REPO_ROOT)} not on disk")

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=["v.NVSR57_FETAL_DEATHS_GTE20[1995] = 999_999"],
    )
    assert_mutation_caught(result, fail_markers=["Failures:", "FAIL"])
