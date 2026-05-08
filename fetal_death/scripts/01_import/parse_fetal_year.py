#!/usr/bin/env python3
"""
Parse NCHS U.S. public-use fetal death fixed-width records from a zip file.

Example (single year):
  python parse_fetal_year.py --zip ../../raw_data/fetal_death/Fetal2022US_COD.zip \
    --year 2022 --out ../../output/yearly_clean/fetal_death_2022_raw.parquet

Sample (first 1000 rows):
  python parse_fetal_year.py --zip ../../raw_data/fetal_death/Fetal2022US_COD.zip \
    --year 2022 --max-rows 1000 --out ../../output/yearly_clean/fetal_death_2022_sample.parquet

Requires: pandas, pyarrow
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from field_specs import layout_for_year
from zip_text_stream import iter_lines_from_zip


def _slice_field(record: bytes, start: int, end: int) -> str:
    """Extract field from record. start/end are 1-based inclusive (NCHS convention)."""
    return record[start - 1 : end].decode("latin-1")


def iter_parsed_records(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    expected_len, fields = layout_for_year(year)

    line_iter = iter_lines_from_zip(zip_path)
    n = 0
    bad_len = 0
    try:
        for raw_line in line_iter:
            rec = raw_line.rstrip(b"\r\n")
            if not rec:
                continue

            if len(rec) != expected_len:
                bad_len += 1
                if bad_len <= 5:
                    print(
                        f"warning: year {year}: expected {expected_len} bytes, "
                        f"got {len(rec)} (line {n + bad_len})",
                        file=sys.stderr,
                    )
                continue

            d: dict[str, str | int] = {"year": year}
            for name, a, b in fields:
                d[name] = _slice_field(rec, a, b)
            yield d
            n += 1
            if max_rows is not None and n >= max_rows:
                break
    finally:
        line_iter.close()

    print(f"Year {year}: parsed {n:,} records", file=sys.stderr)
    if bad_len:
        print(
            f"  Skipped {bad_len:,} lines with unexpected length", file=sys.stderr
        )


def run_parse(
    zip_path: Path,
    year: int,
    out: Path,
    *,
    max_rows: int | None = None,
    chunk_rows: int | None = None,
) -> int:
    """Parse fetal death zip to Parquet. Returns row count written."""
    if chunk_rows is None and max_rows is None:
        chunk_rows = 50_000  # fetal death files are small (~25-50K records)

    out.parent.mkdir(parents=True, exist_ok=True)

    if chunk_rows is None:
        rows = list(iter_parsed_records(zip_path, year, max_rows=max_rows))
        if not rows:
            raise RuntimeError("No rows parsed; check zip path and record width.")
        df = pd.DataFrame(rows)
        df.to_parquet(out, index=False)
        print(f"Wrote {len(df):,} rows to {out}")
        return len(df)

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


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to fetal death zip")
    p.add_argument("--year", type=int, required=True, help="Data year (e.g. 2022)")
    p.add_argument("--max-rows", type=int, default=None, help="Row cap (default: all)")
    p.add_argument("--out", type=Path, required=True, help="Output Parquet path")
    args = p.parse_args()

    try:
        run_parse(args.zip, args.year, args.out, max_rows=args.max_rows)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
