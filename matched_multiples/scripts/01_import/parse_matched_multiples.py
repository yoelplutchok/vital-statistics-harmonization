#!/usr/bin/env python3
"""
Parse NCHS U.S. public-use matched-multiples fixed-width records.

Three windows are supported, each shipping its own record layout CSV:

  - 1995-1997  (sets9597.public; 502-byte content; 324,490 records)
  - 1995-2000  (Sets9500.public; 754-byte content; 699,144 records)
  - 2016-2020  (MULTIPLES.TXT;   variable 155-157 bytes; 641,934 records)

The parser reads the appropriate matched_multiples/record_layout_<window>.csv
(1-indexed byte positions, mirroring NCHS user-guide convention) and slices
each record into one column per documented field. Fields are preserved as
raw latin-1 strings; numeric coercion + sentinel handling happen at
03_harmonize/.

Example:
  python parse_matched_multiples.py --zip /tmp/c8_16_zip_probe/2016-2020.zip \\
    --window 2016-2020 \\
    --out ../../output/yearly_clean/matched_multiples_2016_2020_raw.parquet

Sample (first 1000 rows):
  python parse_matched_multiples.py --zip /tmp/c8_16_zip_probe/2016-2020.zip \\
    --window 2016-2020 --max-rows 1000 \\
    --out ../../output/yearly_clean/matched_multiples_2016_2020_sample.parquet
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from zip_text_stream import iter_lines_from_zip  # noqa: E402

_SUBPROJECT_ROOT = _SCRIPT_DIR.parent.parent  # matched_multiples/

# Per-window content length (no \r\n terminator). 2016-2020 is variable 155-157
# due to UCODR130 right-trim of trailing blanks; max content = 157.
_WINDOWS: dict[str, dict[str, object]] = {
    "1995-1997": {
        "layout_csv": _SUBPROJECT_ROOT / "record_layout_1995_1997.csv",
        "expected_len": 502,
        "variable_length": False,
    },
    "1995-2000": {
        "layout_csv": _SUBPROJECT_ROOT / "record_layout_1995_2000.csv",
        "expected_len": 754,
        "variable_length": False,
    },
    "2016-2020": {
        "layout_csv": _SUBPROJECT_ROOT / "record_layout_2016_2020.csv",
        "expected_len": 157,
        "variable_length": True,  # records 155-157 bytes; pad short to 157
    },
}


def _load_layout(layout_csv: Path) -> list[tuple[str, int, int]]:
    """Return [(field_name, start_1idx, end_1idx_inclusive)] from layout CSV."""
    fields: list[tuple[str, int, int]] = []
    with layout_csv.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = row["field_name"].strip()
            start = int(row["position_start"])
            end = int(row["position_end"])
            fields.append((name, start, end))
    return fields


def _slice_field(record: bytes, start: int, end: int) -> str:
    """Extract field (1-indexed inclusive byte positions, NCHS convention)."""
    return record[start - 1 : end].decode("latin-1")


def iter_parsed_records(
    zip_path: Path,
    window: str,
    max_rows: int | None = None,
) -> Iterator[dict[str, str]]:
    spec = _WINDOWS[window]
    expected_len: int = int(spec["expected_len"])
    variable_length: bool = bool(spec["variable_length"])
    fields = _load_layout(spec["layout_csv"])  # type: ignore[arg-type]

    line_iter = iter_lines_from_zip(zip_path)
    n = 0
    bad_len = 0
    try:
        for raw_line in line_iter:
            rec = raw_line.rstrip(b"\r\n")
            if not rec:
                continue

            if variable_length:
                if len(rec) > expected_len:
                    # No record should exceed max content; flag and skip.
                    bad_len += 1
                    if bad_len <= 5:
                        print(
                            f"warning: window {window}: record exceeds max "
                            f"{expected_len} bytes (got {len(rec)}; line "
                            f"{n + bad_len})",
                            file=sys.stderr,
                        )
                    continue
                if len(rec) < expected_len:
                    rec = rec.ljust(expected_len, b" ")
            else:
                if len(rec) != expected_len:
                    bad_len += 1
                    if bad_len <= 5:
                        print(
                            f"warning: window {window}: expected {expected_len}"
                            f" bytes, got {len(rec)} (line {n + bad_len})",
                            file=sys.stderr,
                        )
                    continue

            d: dict[str, str] = {"window": window}
            for name, a, b in fields:
                d[name] = _slice_field(rec, a, b)
            yield d
            n += 1
            if max_rows is not None and n >= max_rows:
                break
    finally:
        line_iter.close()

    print(f"Window {window}: parsed {n:,} records", file=sys.stderr)
    if bad_len:
        print(
            f"  Skipped {bad_len:,} lines with unexpected length",
            file=sys.stderr,
        )


def run_parse(
    zip_path: Path,
    window: str,
    out: Path,
    *,
    max_rows: int | None = None,
    chunk_rows: int | None = None,
) -> int:
    """Parse matched-multiples zip to Parquet. Returns row count written."""
    if window not in _WINDOWS:
        raise ValueError(
            f"Unknown window {window!r}; expected one of {sorted(_WINDOWS)}"
        )

    if chunk_rows is None and max_rows is None:
        chunk_rows = 100_000  # ~300K-700K records per window

    out.parent.mkdir(parents=True, exist_ok=True)

    if chunk_rows is None:
        rows = list(iter_parsed_records(zip_path, window, max_rows=max_rows))
        if not rows:
            raise RuntimeError("No rows parsed; check zip path and window arg.")
        df = pd.DataFrame(rows)
        df.to_parquet(out, index=False)
        print(f"Wrote {len(df):,} rows to {out}")
        return len(df)

    writer: pq.ParquetWriter | None = None
    buffer: list[dict[str, str]] = []
    total = 0
    try:
        for row in iter_parsed_records(zip_path, window, max_rows=max_rows):
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
        raise RuntimeError("No rows parsed; check zip path and window arg.")
    print(f"Wrote {total:,} rows to {out}")
    return total


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to matched-multiples zip")
    p.add_argument(
        "--window",
        type=str,
        required=True,
        choices=sorted(_WINDOWS),
        help="Data window (1995-1997 | 1995-2000 | 2016-2020)",
    )
    p.add_argument("--max-rows", type=int, default=None, help="Row cap (default: all)")
    p.add_argument("--out", type=Path, required=True, help="Output Parquet path")
    args = p.parse_args()

    try:
        run_parse(args.zip, args.window, args.out, max_rows=args.max_rows)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
