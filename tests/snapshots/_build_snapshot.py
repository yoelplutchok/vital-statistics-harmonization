"""Baseline-builder for the B.12 per-parquet-column SHA snapshot.

Run once per authorized parquet reshape; commits the produced CSV under
this directory with a versioned `v<X>_<UTC>_columns.csv` filename. The
sibling test module imports `column_sha256_map` for re-verification.

Usage (regenerate baseline):

    uv run python -m tests.snapshots._build_snapshot

Per-column hashing walks the parquet by row group, projecting all
columns of the row group at once (one sequential pass per parquet),
then folds each chunk's Arrow buffers into a per-column SHA-256. This
is deterministic for the same on-disk parquet across re-reads on the
same pyarrow build. Re-snapshot is triggered by §11 plan-update when a
parquet is intentionally reshaped (e.g., the C8.13 dict-encoding pass).
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from pathlib import Path

import pyarrow.parquet as pq

MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
_FD_BUILD = Path.home() / "Desktop/fetal-death-harmonization-build/output/harmonized"
_NAT_BUILD = Path.home() / "Desktop/natality-harmonization/output/harmonized"

# Canonical 4-parquet universe matching tests/conftest.py.
PARQUETS: Mapping[str, Path] = {
    "fetal_death_harmonized": _FD_BUILD / "fetal_death_harmonized.parquet",
    "fetal_death_derived": _FD_BUILD / "fetal_death_derived.parquet",
    "natality_v2_harmonized_derived": _NAT_BUILD / "natality_v2_harmonized_derived.parquet",
    "natality_v3_linked_harmonized_derived": _NAT_BUILD / "natality_v3_linked_harmonized_derived.parquet",
}

BASELINE_DIR = Path(__file__).resolve().parent


def column_sha256_map(parquet_path: Path) -> dict[str, str]:
    """Return {column_name: sha256_hex} for every column in the parquet.

    Reads one row group at a time across all columns; for each chunk's
    Arrow buffers, feeds the raw bytes into the per-column hasher. A
    null buffer slot is fed `b"\\x00"` so that the absence of validity
    or offset buffers contributes deterministically to the hash.
    """
    pf = pq.ParquetFile(parquet_path)
    columns = pf.schema_arrow.names
    hashers = {col: hashlib.sha256() for col in columns}

    for rg_idx in range(pf.num_row_groups):
        table = pf.read_row_group(rg_idx)
        for col_idx, col_name in enumerate(columns):
            arr = table.column(col_idx)
            h = hashers[col_name]
            for chunk in arr.chunks:
                for buf in chunk.buffers():
                    if buf is None:
                        h.update(b"\x00")
                    else:
                        h.update(memoryview(buf))
    return {col: h.hexdigest() for col, h in hashers.items()}


def write_baseline_csv(out_path: Path) -> int:
    """Compute SHAs for every column of every parquet, write to CSV.

    Returns the total row count written. Skips parquets that do not
    exist on disk (with a printed note); a baseline regeneration in an
    environment without one of the parquets is a partial regeneration.
    """
    rows: list[dict[str, str | int]] = []
    for parquet_name, path in PARQUETS.items():
        if not path.exists():
            print(f"SKIP {parquet_name}: {path} not on disk")
            continue
        print(f"Hashing {parquet_name} ({path}) ...")
        pf = pq.ParquetFile(path)
        n_rows = pf.metadata.num_rows
        shas = column_sha256_map(path)
        for col_idx, col_name in enumerate(pf.schema_arrow.names):
            arrow_type = str(pf.schema_arrow.field(col_name).type)
            rows.append(
                {
                    "parquet": parquet_name,
                    "column_name": col_name,
                    "column_index": col_idx,
                    "arrow_type": arrow_type,
                    "row_count": n_rows,
                    "column_sha256": shas[col_name],
                }
            )

    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["parquet", "column_name", "column_index", "arrow_type", "row_count", "column_sha256"],
        )
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def load_baseline_csv(path: Path) -> list[dict[str, str]]:
    """Return baseline rows as list of dicts (canonical schema)."""
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def latest_baseline_path() -> Path:
    """Return the most recent `v<X>_<UTC>_columns.csv` under this dir."""
    candidates = sorted(BASELINE_DIR.glob("v*_columns.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"no baseline file matching v*_columns.csv in {BASELINE_DIR}. "
            "Regenerate via `uv run python -m tests.snapshots._build_snapshot`."
        )
    return candidates[-1]


def main() -> None:
    # Single canonical baseline per session; UTC timestamp from the
    # session's commit context. Update the literal below at each authorized
    # re-snapshot, alongside a §11 plan-update entry.
    # v2 re-snap: C8.17 DO step 6 canonical 1968-2024 re-harmonize
    # (natality_v2 84-col block changes; the other 3 parquets' per-column
    # SHAs are byte-identical to the v1 baseline). v1 baseline retained
    # (Anti-Pattern #10). See 2026-05-16T08:00:00Z.
    # v3 re-snap: C8.18 DO step 6b linked v3->v4 1983-2023 re-harmonize
    # (the natality_v3_linked_harmonized_derived block changes — 1983-2004
    # rows added + the new link_segment / underlying_cause_icd9 /
    # cause_recode_61 columns; FD + natality_v2 per-column SHAs are
    # byte-identical to the v2 baseline). v1 + v2 baselines retained
    # (Anti-Pattern #10). See 2026-05-23T02:00:00Z.
    out = BASELINE_DIR / "v3_2026-05-23T02-00-00Z_columns.csv"
    n = write_baseline_csv(out)
    print(f"wrote {n} rows to {out}")


if __name__ == "__main__":
    main()
