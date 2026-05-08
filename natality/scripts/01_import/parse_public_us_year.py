#!/usr/bin/env python3
"""
Parse NCHS U.S. public-use natality fixed-width records from a Nat{year}us.zip.

Example:
  python parse_public_us_year.py --zip ../../raw_data/Nat2014us.zip --year 2014 \\
    --max-rows 100000 --out ../../output/yearly_clean/natality_2014_core_sample.parquet

Full file (streams in chunks; avoids loading millions of rows into RAM):
  python parse_public_us_year.py --zip ../../raw_data/Nat2014us.zip --year 2014 \\
    --out ../../output/yearly_clean/natality_2014_core.parquet

Requires: pandas, pyarrow (see requirements.txt). For deflate64/PPMd zips (e.g. 2009–2013 and some later years), `7z` on PATH.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Allow running as script from repo root or this directory
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from field_specs import (
    PUBLIC_US_1990_2002_FIELDS,
    PUBLIC_US_2003_FIELDS,
    PUBLIC_US_2004_FIELDS,
    PUBLIC_US_2005_2010_FIELDS,
    PUBLIC_US_2014_2015_FIELDS,
    RECORD_LEN_1990,
    RECORD_LEN_2003,
    RECORD_LEN_2004,
    RECORD_LEN_2005,
    RECORD_LEN_2010,
    RECORD_LEN_2014_2015,
)
from zip_text_stream import iter_lines_from_zip


def _slice_field(record: bytes, start: int, end: int) -> str:
    """start/end are 1-based inclusive (NCHS)."""
    return record[start - 1 : end].decode("latin-1")


def _layout_for_year(
    year: int,
) -> tuple[int | None, list[tuple[str, int, int]], bool]:
    """Return (expected_len, fields, filter_rectype).

    expected_len may be None for 2003–2004 where the record length varies by
    year and is auto-detected from the first line.
    filter_rectype is True for 1990–1993 combined US+territory files where
    we keep only RECTYPE=1 (US) records.
    """
    if 1990 <= year <= 1993:
        # These files contain only US records (no territories).
        # Position 5 mirrors RESTATUS (residence/occurrence), NOT a US-vs-territory flag.
        # Filtering on it discards ~970K valid cross-state births per year.
        return RECORD_LEN_1990, PUBLIC_US_1990_2002_FIELDS, False
    if 1994 <= year <= 2002:
        return RECORD_LEN_1990, PUBLIC_US_1990_2002_FIELDS, False
    if year == 2003:
        return RECORD_LEN_2003, PUBLIC_US_2003_FIELDS, False
    if year == 2004:
        return RECORD_LEN_2004, PUBLIC_US_2004_FIELDS, False
    if year == 2005:
        return RECORD_LEN_2005, PUBLIC_US_2005_2010_FIELDS, False
    if 2006 <= year <= 2013:
        return RECORD_LEN_2010, PUBLIC_US_2005_2010_FIELDS, False
    if 2014 <= year <= 2024:
        return RECORD_LEN_2014_2015, PUBLIC_US_2014_2015_FIELDS, False
    raise ValueError(
        f"Year {year} not configured yet. Supported now: 1990-2024."
    )


def iter_parsed_records(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    expected_len, fields, filter_rectype = _layout_for_year(year)

    line_iter = iter_lines_from_zip(zip_path)
    n = 0
    bad_len = 0
    skipped_territory = 0
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

            # 1990–1993 combined files: keep only US records (RECTYPE=1).
            if filter_rectype:
                rectype = rec[4:5]  # position 5, 0-indexed = 4
                if rectype != b"1":
                    skipped_territory += 1
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
    if bad_len:
        print(f"Skipped {bad_len:,} lines with unexpected length", file=sys.stderr)
    if skipped_territory:
        print(
            f"Skipped {skipped_territory:,} territory records (RECTYPE != 1)",
            file=sys.stderr,
        )


def run_parse(
    zip_path: Path,
    year: int,
    out: Path,
    *,
    max_rows: int | None = None,
    chunk_rows: int | None = None,
) -> int:
    """
    Parse natality zip to Parquet. Returns row count written.

    If chunk_rows is set, writes with PyArrow ParquetWriter (bounded memory).
    If chunk_rows is None and max_rows is set, uses a single in-memory DataFrame.
    If both are None (full file), defaults chunk_rows to 250_000.
    """
    if chunk_rows is None and max_rows is None:
        chunk_rows = 250_000

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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to Nat{year}us.zip")
    p.add_argument("--year", type=int, required=True, help="Vital data year (e.g. 2014)")
    p.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Stop after this many data rows (default: all)",
    )
    p.add_argument(
        "--chunk-rows",
        type=int,
        default=None,
        help="Stream to Parquet in chunks of this size (default: 250000 when "
        "--max-rows omitted; omit to load all rows in memory when --max-rows set)",
    )
    p.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output Parquet path (parent dirs created if needed)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    chunk_rows = args.chunk_rows
    if chunk_rows is None and args.max_rows is None:
        chunk_rows = 250_000
    elif chunk_rows is None and args.max_rows is not None:
        chunk_rows = None  # small-sample path: one DataFrame unless user also passed chunk-rows

    try:
        run_parse(
            args.zip,
            args.year,
            args.out,
            max_rows=args.max_rows,
            chunk_rows=chunk_rows,
        )
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
