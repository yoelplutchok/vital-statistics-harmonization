#!/usr/bin/env python3
"""
Write residents-only subsets of V2 and V3 linked derived Parquet files.

Filters out foreign residents (is_foreign_resident == True) and the
is_foreign_resident column itself (redundant in the output).

Outputs:
  output/convenience/natality_v2_residents_only.parquet
  output/convenience/natality_v3_linked_residents_only.parquet
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def _get_git_hash() -> str:
    """Return short git hash or 'unknown' if not in a repo."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def filter_residents(in_path: Path, out_path: Path, batch_size: int = 500_000) -> None:
    """Stream Parquet, keep only residents, write to new file."""
    if not in_path.is_file():
        raise FileNotFoundError(in_path)

    pf = pq.ParquetFile(in_path)
    in_schema = pf.schema_arrow
    print(f"Reading {in_path.name} ({pf.metadata.num_rows:,} rows, {len(in_schema.names)} cols)")

    # Drop is_foreign_resident and restatus from output (redundant for residents-only)
    drop_cols = {"is_foreign_resident", "restatus"}
    out_fields = [f for f in in_schema if f.name not in drop_cols]
    out_schema = pa.schema(out_fields)

    # Embed pipeline version metadata in the parquet file
    git_hash = _get_git_hash()
    build_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    metadata = {
        b"pipeline_git_hash": git_hash.encode(),
        b"pipeline_build_timestamp": build_ts.encode(),
        b"pipeline_source_file": str(in_path.name).encode(),
    }
    # Merge with any existing schema metadata
    if out_schema.metadata:
        metadata.update(out_schema.metadata)
    out_schema = out_schema.with_metadata(metadata)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = pq.ParquetWriter(out_path, out_schema, compression="zstd")
    total_in = 0
    total_out = 0

    try:
        for batch in pf.iter_batches(batch_size=batch_size):
            total_in += batch.num_rows
            foreign = batch.column(batch.schema.get_field_index("is_foreign_resident"))
            # Keep rows where is_foreign_resident is explicitly False.
            # Wrap in fill_null(False) because pc.equal returns null on null inputs,
            # and batch.filter(null_mask) silently drops the row — we want explicit
            # behaviour: a null is_foreign_resident raises rather than silently drops.
            keep = pc.fill_null(pc.equal(foreign, pa.scalar(False)), False)
            null_count = int(pc.sum(pc.cast(pc.is_null(foreign), pa.int64())).as_py() or 0)
            if null_count:
                raise RuntimeError(
                    f"is_foreign_resident has {null_count} null rows in input batch — "
                    f"refusing to silently drop. Investigate upstream restatus parsing."
                )
            filtered = batch.filter(keep)

            if filtered.num_rows > 0:
                # Drop the redundant columns
                cols = [filtered.column(f.name) for f in out_fields]
                out_batch = pa.RecordBatch.from_arrays(cols, schema=out_schema)
                writer.write_batch(out_batch)
                total_out += out_batch.num_rows
    finally:
        writer.close()

    excluded = total_in - total_out
    print(f"  Wrote {total_out:,} resident rows to {out_path.name}")
    print(f"  Excluded {excluded:,} foreign-resident rows ({excluded / total_in * 100:.2f}%)")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v2-in", type=Path,
                    default=repo_root / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet")
    p.add_argument("--v3-in", type=Path,
                    default=repo_root / "output" / "harmonized" / "natality_v3_linked_harmonized_derived.parquet")
    p.add_argument("--out-dir", type=Path,
                    default=repo_root / "output" / "convenience")
    p.add_argument("--batch-size", type=int, default=500_000)
    p.add_argument("--skip-v2", action="store_true", help="Skip V2 natality")
    p.add_argument("--skip-v3", action="store_true", help="Skip V3 linked")
    args = p.parse_args()

    v2_out = args.out_dir / "natality_v2_residents_only.parquet"
    v3_out = args.out_dir / "natality_v3_linked_residents_only.parquet"

    if not args.skip_v2:
        filter_residents(args.v2_in, v2_out, args.batch_size)

    if not args.skip_v3:
        filter_residents(args.v3_in, v3_out, args.batch_size)

    # Write PROVENANCE.md with SHA-256 hashes for downstream verification.
    # Preserve any existing "## Previous build" / "## Supersedes" trailing blocks
    # so an audit trail of historic Zenodo-deposited SHAs survives a rebuild.
    provenance_path = args.out_dir / "PROVENANCE.md"
    git_hash = _get_git_hash()
    build_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    preserved_tail = ""
    if provenance_path.is_file():
        old = provenance_path.read_text(encoding="utf-8")
        # Find first occurrence of any preservation marker and keep everything from there on.
        markers = ["## Previous build", "## Supersedes", "## Earlier deposits"]
        first = min((old.find(m) for m in markers if old.find(m) >= 0), default=-1)
        if first >= 0:
            preserved_tail = "\n" + old[first:].rstrip() + "\n"

    prov_lines = [
        "# Convenience parquet provenance",
        "",
        f"- **Pipeline git hash**: `{git_hash}`",
        f"- **Build timestamp**: `{build_ts}`",
        "",
        "## SHA-256 checksums",
        "",
        "Use these to verify your copy matches the upstream build:",
        "",
        "```",
    ]
    for out_file in [v2_out, v3_out]:
        if out_file.is_file():
            sha = _sha256(out_file)
            prov_lines.append(f"{sha}  {out_file.name}")
    prov_lines.append("```")
    prov_lines.append("")
    body = "\n".join(prov_lines)
    if preserved_tail:
        body = body.rstrip() + preserved_tail
        print(f"  (preserved historical-build block from existing PROVENANCE.md)")
    provenance_path.write_text(body, encoding="utf-8")
    print(f"\nWrote {provenance_path}")
    print("Done.")


if __name__ == "__main__":
    main()
