"""DESIGN: tracks-current-state — B.6 mutation test for fetal_death validate_external.py.

Per C8.12 §15 + STATUS 2026-05-13T21:00:00Z: spawns `validate_external.py`
in a subprocess with the `NVSR_FETAL_DEATHS[2022]` module-level constant
mutated to an impossible value. The validator's hardcoded 2022 expected
count is 20,202; the mutation bumps it to 999,999 (orders-of-magnitude larger
than any plausible single-year fetal-death count). The validator's per-year
comparison should flag the 2022 row as FAIL and `sys.exit(1)` should propagate.

Convention 1 SHAPE-not-VALUE: asserts STRUCTURAL invariant (non-zero
returncode AND a FAIL marker in captured output), NOT the literal exit code
or the exact wording of the FAIL message. L14 AND-of-rows aggregation: both
conditions must hold.

Skip-if-parquet-missing per the established `_require()`-style pattern.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = REPO_ROOT / "fetal_death/scripts/05_validate/validate_external.py"
HARM_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"
DERIVED_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_derived.parquet"


def test_validate_external_catches_inflated_nvsr_expected() -> None:
    for required in (VALIDATOR, HARM_PARQUET, DERIVED_PARQUET):
        if not required.exists():
            pytest.skip(f"{required.relative_to(REPO_ROOT)} not on disk")

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=["v.NVSR_FETAL_DEATHS[2022] = 999_999"],
    )
    assert_mutation_caught(result, fail_markers=["Failures:", "FAIL"])
