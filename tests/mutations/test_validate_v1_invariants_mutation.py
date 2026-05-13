"""DESIGN: tracks-current-state — B.6 mutation test for natality validate_v1_invariants.py.

Per C8.12 §15: this validator has no `--targets` CSV; its FAIL surfaces are
(i) the upfront required-columns precondition (line 114-141: raises
RuntimeError if any of ~23 required columns is missing from the parquet
schema), and (ii) the per-violation aggregation across all row-groups
yielding `any_fail = True` then `raise SystemExit(2)`.

This test exercises surface (i) — the cheap (<5s) precondition path — by
monkey-patching `pq.ParquetFile` at the validator's module-attribute scope
so that `schema_arrow.names` reports `data_year` as missing. The validator
finds `data_year` in its `required` set, computes `missing - cols = {'data_year'}`,
and raises `RuntimeError("Missing required columns: ['data_year']")`. The
RuntimeError propagates to the subprocess returncode != 0 with the
identifying message in stderr.

Choosing surface (i) over surface (ii) avoids scanning the 138M-row natality
v2 derived parquet (~60-120s); surface (ii) requires it. The precondition
check is itself a Tier-0 fail-closed defense per §2 — a validator that does
not notice its required columns are absent would silently rubber-stamp a
corrupted parquet.

Convention 1 SHAPE-not-VALUE; L14 AND-of-rows aggregation.

Skip-if-natality-v2-derived-parquet-missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.mutations._runner import (
    REPO_ROOT,
    assert_mutation_caught,
    run_validator_with_module_mutation,
)

VALIDATOR = REPO_ROOT / "natality/scripts/05_validate/validate_v1_invariants.py"
NAT_V2_PARQUET = Path.home() / "Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet"


# Bootstrap that swaps `pq.ParquetFile` for a wrapper that drops one required
# column from the reported schema. Trailing newlines preserved so the
# subsequent mutation statements remain syntactically separate.
_PATCH_SCHEMA_DROP_DATA_YEAR = """\
_b6_orig_pf_cls = v.pq.ParquetFile

class _B6FakeSchema:
    def __init__(self, inner):
        self._inner = inner
    @property
    def names(self):
        return [n for n in self._inner.names if n != 'data_year']
    def __getattr__(self, k):
        return getattr(self._inner, k)

class _B6FakePF:
    def __init__(self, *a, **kw):
        self._inner = _b6_orig_pf_cls(*a, **kw)
    @property
    def schema_arrow(self):
        return _B6FakeSchema(self._inner.schema_arrow)
    def __getattr__(self, k):
        return getattr(self._inner, k)

v.pq.ParquetFile = _B6FakePF
"""


def test_validate_v1_invariants_catches_missing_required_column(tmp_path: Path) -> None:
    for required in (VALIDATOR, NAT_V2_PARQUET):
        if not required.exists():
            pytest.skip(f"{required} not on disk")

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    result = run_validator_with_module_mutation(
        VALIDATOR,
        mutations=[_PATCH_SCHEMA_DROP_DATA_YEAR],
        cli_args=[
            "--in", str(NAT_V2_PARQUET),
            "--out-dir", str(out_dir),
            "--years", "2005",
        ],
    )
    assert_mutation_caught(
        result,
        fail_markers=["Missing required columns", "RuntimeError"],
    )
