"""DESIGN: tracks-current-state — B.6 mutation test for natality compare_external_targets_v1.py.

Per C8.12 §15: this validator accepts `--targets` pointing at the
external_validation_targets_v1.csv. The mutation writes a tempdir-CSV with
a SINGLE row asserting `resident_births,2005,resident,0,0` — i.e., zero
expected resident births with tolerance 0, an impossible target given the
~4M actual resident-births count for 2005. The validator computes the real
count, finds it far exceeds tolerance, increments `n_fail`, and exits
`SystemExit(2)`.

This is the cleanest mutation pattern for CSV-targets-driven validators: no
module-level constant patching needed; the violation is injected via the
CLI-passed input.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.

Skip-if-natality-v2-derived-parquet-missing.
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

VALIDATOR = REPO_ROOT / "natality/scripts/05_validate/compare_external_targets_v1.py"
NAT_V2_PARQUET = Path.home() / "Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet"

MUTATED_TARGETS_CSV = textwrap.dedent(
    """\
    metric_id,data_year,universe,expected_value,tolerance_abs,value_source,notes
    resident_births,2005,resident,0,0,"B.6 mutation test — impossible expected value","B.6 mutation: real value is ~4M, expected=0; validator should FAIL"
    """
)


def test_compare_external_targets_v1_catches_impossible_target(tmp_path: Path) -> None:
    for required in (VALIDATOR, NAT_V2_PARQUET):
        if not required.exists():
            pytest.skip(f"{required} not on disk")

    targets_path = tmp_path / "mutated_targets_v1.csv"
    targets_path.write_text(MUTATED_TARGETS_CSV)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    result = run_validator_with_args(
        VALIDATOR,
        cli_args=[
            "--in", str(NAT_V2_PARQUET),
            "--targets", str(targets_path),
            "--out-dir", str(out_dir),
        ],
    )
    # This validator writes per-row `status=fail` to the comparison CSV/MD,
    # not stdout; stdout carries only "Wrote ..." paths.
    assert_mutation_caught(
        result,
        output_files_with_fail_text=[
            out_dir / "external_validation_v1_comparison.csv",
            out_dir / "external_validation_v1_comparison.md",
        ],
    )
