"""DESIGN: tracks-current-state — B.6 mutation test for natality compare_external_targets_v3_linked.py.

Per C8.12 §15: mirror of test_compare_external_targets_v1_mutation.py — the
mutation writes a tempdir-CSV with a single impossible target row
(`resident_births,2005,resident,0,0`) and passes it via `--targets`. The
validator computes the real 2005 resident-births count from the V3 linked
derived parquet, finds it far exceeds the zero expected value, increments
`n_fail`, and exits `SystemExit(1)`.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.

Skip-if-V3-linked-derived-parquet-missing.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_args,
)

VALIDATOR = REPO_ROOT / "natality/scripts/05_validate/compare_external_targets_v3_linked.py"
NAT_V3_LINKED_PARQUET = (
    Path.home()
    / "Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet"
)

MUTATED_TARGETS_CSV = textwrap.dedent(
    """\
    metric_id,data_year,universe,expected_value,tolerance_abs,value_source,notes
    resident_births,2005,resident,0,0,"B.6 mutation test — impossible expected value","B.6 mutation: real value is ~4M, expected=0; validator should FAIL"
    """
)


def test_compare_external_targets_v3_linked_catches_impossible_target(tmp_path: Path) -> None:
    for required in (VALIDATOR, NAT_V3_LINKED_PARQUET):
        if not required.exists():
            pytest.skip(f"{required} not on disk")

    targets_path = tmp_path / "mutated_targets_v3_linked.csv"
    targets_path.write_text(MUTATED_TARGETS_CSV)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    result = run_validator_with_args(
        VALIDATOR,
        cli_args=[
            "--in", str(NAT_V3_LINKED_PARQUET),
            "--targets", str(targets_path),
            "--out-dir", str(out_dir),
        ],
    )
    # This validator does print "FAILURES DETECTED" to stdout in addition to
    # writing per-row fails to the comparison CSV; check both for robustness.
    assert_mutation_caught(
        result,
        fail_markers=["FAILURES DETECTED", "Fail:"],
        output_files_with_fail_text=[
            out_dir / "external_validation_v3_linked_comparison.csv",
            out_dir / "external_validation_v3_linked_comparison.md",
        ],
    )
