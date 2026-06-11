"""DESIGN: tracks-current-state — B.6 mutation test for matched_multiples validate_matched_multiples.py.

Injects an impossible 2016-2020 PDF Table 1 total (expected=0 vs ~642k actual).
The validator must emit per-row FAIL and exit non-zero (L14).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = (
    REPO_ROOT / "matched_multiples/scripts/05_validate/validate_matched_multiples.py"
)
MM_HARMONIZED = (
    REPO_ROOT
    / "matched_multiples/output/harmonized/matched_multiples_harmonized.parquet"
)
VALIDATION_CSV = REPO_ROOT / "matched_multiples/validation_results.csv"


def test_validate_matched_multiples_catches_impossible_2016_total() -> None:
    for required in (VALIDATOR, MM_HARMONIZED):
        if not required.exists():
            pytest.skip(f"{required} not on disk")

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=[
            'v._TARGETS_2016_2020 = [("total", "mutation", 0)]',
        ],
    )
    assert_mutation_caught(
        result,
        fail_markers=["FAIL", "*** "],
        output_files_with_fail_text=[VALIDATION_CSV],
    )
