"""DESIGN: tracks-current-state — asserts each of the 340 canonical parquet
columns hashes identically to the most-recent committed baseline under
tests/snapshots/v<X>_<UTC>_columns.csv.

B.12 of C8.12 (mutation tests + L13/L14 audits + SHA-stability + snapshot
regression). Defends H10 (provenance / reproducibility drift) at the
column-content level: subtle drift (a derived-column recomputation, an
upstream NCHS silently-reformatted year, a dtype coercion that changes
in-place) that would not change row count or schema is caught by per-
column hash equality.

Convention 1 SHAPE-not-VALUE for the structural anchors (340 total
columns; 73 + 89 + 84 + 94 per-parquet split). The per-column SHA test
IS value-pinning by design — that is exactly what a regression baseline
asserts. Re-snapshot is triggered ONLY by an authorized §11 plan-update
(e.g., C8.13's dictionary-encoding reshape), which produces a sibling
`v<X+1>_<UTC>_columns.csv` and a DECISION_LOG entry naming the cause.

Skip-if-parquet-missing: each per-parquet sub-check skips if its parquet
is not on disk, so a CI environment without canonical parquets gates on
whatever subset IS present.
"""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

from tests.snapshots._build_snapshot import (
    PARQUETS,
    column_sha256_map,
    latest_baseline_path,
    load_baseline_csv,
)

EXPECTED_COLUMN_COUNTS = {
    "fetal_death_harmonized": 73,
    "fetal_death_derived": 89,
    "natality_v2_harmonized_derived": 84,
    "natality_v3_linked_harmonized_derived": 94,
}
EXPECTED_TOTAL = sum(EXPECTED_COLUMN_COUNTS.values())  # 340


def _baseline_by_parquet() -> dict[str, list[dict[str, str]]]:
    rows = load_baseline_csv(latest_baseline_path())
    by: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by.setdefault(r["parquet"], []).append(r)
    return by


def test_baseline_anchor_row_count() -> None:
    """340 = 73 + 89 + 84 + 94 columns total in the committed baseline."""
    rows = load_baseline_csv(latest_baseline_path())
    assert len(rows) == EXPECTED_TOTAL, (
        f"expected {EXPECTED_TOTAL} baseline rows (73+89+84+94); got {len(rows)}"
    )


def test_baseline_per_parquet_column_counts() -> None:
    """Each canonical parquet contributes the expected count."""
    by = _baseline_by_parquet()
    actual = {name: len(rs) for name, rs in by.items()}
    assert actual == EXPECTED_COLUMN_COUNTS, (
        f"per-parquet column counts diverged from baseline: "
        f"expected={EXPECTED_COLUMN_COUNTS}, actual={actual}"
    )


@pytest.mark.parametrize("parquet_name", list(EXPECTED_COLUMN_COUNTS))
def test_per_column_sha_matches_baseline(parquet_name: str) -> None:
    """Each column's SHA-256 matches the committed baseline byte-exact.

    Parametrized so the four parquets are independent skip surfaces. If a
    column drifts, the message names every mismatched column with the
    truncated expected/actual SHA pair; cap at the first 5 to keep the
    output skim-readable.
    """
    path: Path = PARQUETS[parquet_name]
    if not path.exists():
        pytest.skip(f"{path} not on disk; run pipeline before B.12 verify.")

    by = _baseline_by_parquet()
    expected_rows = by.get(parquet_name)
    if not expected_rows:
        pytest.fail(
            f"baseline has no entries for {parquet_name}; regenerate via "
            "`uv run python -m tests.snapshots._build_snapshot`."
        )
    expected = {r["column_name"]: r["column_sha256"] for r in expected_rows}

    # Schema-name parity check: the column SET must match before per-column
    # hash equality is meaningful. Renaming a column is an authorized §11
    # event; bare drift is not.
    pf = pq.ParquetFile(path)
    actual_names = set(pf.schema_arrow.names)
    expected_names = set(expected)
    if actual_names != expected_names:
        missing = expected_names - actual_names
        added = actual_names - expected_names
        raise AssertionError(
            f"{parquet_name} column-name set drifted from baseline: "
            f"missing={sorted(missing)[:5]} added={sorted(added)[:5]}"
        )

    actual = column_sha256_map(path)
    mismatches = [
        (col, expected[col], actual[col])
        for col in expected
        if actual[col] != expected[col]
    ]
    if mismatches:
        first = mismatches[:5]
        raise AssertionError(
            f"{parquet_name}: {len(mismatches)} of {len(expected)} columns "
            f"drifted from baseline. First {len(first)}:\n"
            + "\n".join(
                f"  {col}: baseline={exp[:16]}… actual={act[:16]}…"
                for col, exp, act in first
            )
        )
