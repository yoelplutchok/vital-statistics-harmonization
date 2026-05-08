#!/usr/bin/env python3
"""
Parse NCHS linked birth-infant death cohort denominator-plus files.

Reads the denominator-plus member from a LinkCO{yy}US.zip and extracts
birth-side fields (reusing natality field specs) plus death-side fields
(age at death, cause of death, manner, record weight, etc.).

Example (sample):
  python parse_linked_year.py --zip ../../raw_data/linked/LinkCO15US.zip --year 2015 \
    --max-rows 100000 --out ../../output/linked/linked_2015_denomplus_sample.parquet

Full file:
  python parse_linked_year.py --zip ../../raw_data/linked/LinkCO15US.zip --year 2015 \
    --out ../../output/linked/linked_2015_denomplus.parquet
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from field_specs import (
    LINKED_BIRTH_2005_2013_FIELDS,
    LINKED_BIRTH_2014_2020_FIELDS,
    LINKED_DEATH_2005_2013_FIELDS,
    LINKED_DEATH_2014_2020_FIELDS,
    LINKED_DENOMPLUS_RECLEN_2005_2013,
    LINKED_DENOMPLUS_RECLEN_2014_2020,
)
from zip_text_stream import iter_lines_from_zip


def _slice_field(record: bytes, start: int, end: int) -> str:
    """start/end are 1-based inclusive (NCHS)."""
    return record[start - 1 : end].decode("latin-1")


def _find_denomplus_member(zip_path: Path) -> str:
    """Find the denominator-plus member in a linked zip archive."""
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if "DENOM" in name.upper():
                return name
    raise RuntimeError(
        f"No denominator-plus member found in {zip_path}. "
        f"Members: {_list_members(zip_path)}"
    )


def _list_members(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as zf:
        return zf.namelist()


def _layout_for_linked_year(
    year: int,
) -> tuple[int, list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    """Return (expected_reclen, birth_fields, death_fields) for the linked denominator-plus."""
    if 2005 <= year <= 2013:
        return (
            LINKED_DENOMPLUS_RECLEN_2005_2013,
            LINKED_BIRTH_2005_2013_FIELDS,
            LINKED_DEATH_2005_2013_FIELDS,
        )
    if 2014 <= year <= 2020:
        return (
            LINKED_DENOMPLUS_RECLEN_2014_2020,
            LINKED_BIRTH_2014_2020_FIELDS,
            LINKED_DEATH_2014_2020_FIELDS,
        )
    raise ValueError(
        f"Year {year} not yet configured for linked files. Supported: 2005-2020."
    )


def iter_parsed_records(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    expected_len, birth_fields, death_fields = _layout_for_linked_year(year)
    member = _find_denomplus_member(zip_path)
    print(f"Reading member: {member}", file=sys.stderr)

    all_fields = birth_fields + death_fields
    line_iter = iter_lines_from_zip(zip_path, member_name=member)
    n = 0
    bad_len = 0
    try:
        for raw_line in line_iter:
            rec = raw_line.rstrip(b"\r\n")
            if not rec:
                continue
            if len(rec) != expected_len:
                bad_len += 1
                if bad_len <= 3:
                    print(
                        f"warning: expected {expected_len} bytes, got {len(rec)}",
                        file=sys.stderr,
                    )
                continue

            d: dict[str, str | int] = {"year": year}
            for name, a, b in all_fields:
                d[name] = _slice_field(rec, a, b)
            yield d
            n += 1
            if max_rows is not None and n >= max_rows:
                break
    finally:
        line_iter.close()
    if bad_len:
        print(f"Skipped {bad_len:,} lines with unexpected length", file=sys.stderr)


def run_parse(
    zip_path: Path,
    year: int,
    out: Path,
    *,
    max_rows: int | None = None,
    chunk_rows: int | None = None,
) -> int:
    if chunk_rows is None and max_rows is None:
        chunk_rows = 250_000

    out.parent.mkdir(parents=True, exist_ok=True)

    if chunk_rows is None:
        rows = list(iter_parsed_records(zip_path, year, max_rows=max_rows))
        if not rows:
            raise RuntimeError("No rows parsed; check zip path and record width.")
        tbl = pa.Table.from_pylist(rows)
        pq.write_table(tbl, str(out))
        print(f"Wrote {len(rows):,} rows to {out}")
        return len(rows)

    writer: pq.ParquetWriter | None = None
    buffer: list[dict[str, str | int]] = []
    total = 0
    try:
        for row in iter_parsed_records(zip_path, year, max_rows=max_rows):
            buffer.append(row)
            if len(buffer) >= chunk_rows:
                tbl = pa.Table.from_pylist(buffer)
                if writer is None:
                    writer = pq.ParquetWriter(str(out), tbl.schema)
                writer.write_table(tbl)
                total += len(buffer)
                buffer.clear()
        if buffer:
            tbl = pa.Table.from_pylist(buffer)
            if writer is None:
                writer = pq.ParquetWriter(str(out), tbl.schema)
            writer.write_table(tbl)
            total += len(buffer)
    finally:
        if writer is not None:
            writer.close()

    if total == 0:
        raise RuntimeError("No rows parsed; check zip path and record width.")
    print(f"Wrote {total:,} rows to {out}")
    return total


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to LinkCO{yy}US.zip")
    p.add_argument("--year", type=int, required=True, help="Cohort birth year (e.g. 2015)")
    p.add_argument("--max-rows", type=int, default=None, help="Stop after N rows")
    p.add_argument("--chunk-rows", type=int, default=None, help="Chunk size for streaming writes")
    p.add_argument("--out", type=Path, required=True, help="Output Parquet path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    chunk_rows = args.chunk_rows
    if chunk_rows is None and args.max_rows is None:
        chunk_rows = 250_000
    elif chunk_rows is None and args.max_rows is not None:
        chunk_rows = None

    try:
        run_parse(
            args.zip, args.year, args.out,
            max_rows=args.max_rows, chunk_rows=chunk_rows,
        )
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
