"""DESIGN: tracks-current-state — B.6 mutation test for natality validate_linked_parquets.py.

Per C8.12 §15: the validator compares parquet row counts against zip-implied
row counts derived from record-length constants. The mutation monkey-patches
`_zip_implied_rows` to return None for every year (so the comparison records
a row-count-mismatch failure) — this is a structural mutation: it does not
require the per-year linked parquets to exist on disk for the patch to fire,
but the validator iterates `--linked-dir` glob to find parquets first; if
that directory is empty / absent, the validator runs but has no rows to
compare and `failures` stays empty.

Skip-if-linked-parquet-dir-missing-or-empty: the monorepo's
`natality/output/linked/` is the canonical input dir; on this build it is
absent (linked parquets live in the natality build dir, not the monorepo).
Test SKIPs cleanly in that case; runs the mutation when inputs are present.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.
"""

from __future__ import annotations

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = REPO_ROOT / "natality/scripts/05_validate/validate_linked_parquets.py"
LINKED_DIR = REPO_ROOT / "natality/output/linked"
RAW_LINKED_DIR = REPO_ROOT / "raw_data/linked"


def _has_any_linked_parquet() -> bool:
    if not LINKED_DIR.is_dir():
        return False
    return any(LINKED_DIR.glob("*.parquet"))


def test_validate_linked_parquets_catches_zip_implied_mismatch() -> None:
    if not VALIDATOR.exists():
        pytest.skip(f"{VALIDATOR.relative_to(REPO_ROOT)} not on disk")
    if not _has_any_linked_parquet():
        pytest.skip(
            f"{LINKED_DIR.relative_to(REPO_ROOT)} absent / empty; "
            "linked parquets live outside the monorepo on this build "
            "(C8.11 soft-flag (e); C8.7b orchestrator scope)."
        )
    if not RAW_LINKED_DIR.exists():
        pytest.skip(f"{RAW_LINKED_DIR.relative_to(REPO_ROOT)} not on disk")

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=[
            "_orig_zir = v._zip_implied_rows",
            "v._zip_implied_rows = lambda zip_path, year: (_orig_zir(zip_path, year) or 0) - 1",
        ],
        cli_args=["--years", "2005-2005"],
    )
    assert_mutation_caught(result, fail_markers=["FAILURES:", "Row count mismatch"])
