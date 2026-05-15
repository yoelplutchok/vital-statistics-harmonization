#!/usr/bin/env python3
"""
Parse NCHS U.S. public-use natality fixed-width records 1968-1989.

Sibling of `parse_public_us_year.py` (1990-2024). Authored at C8.17 DO step 5a
(2026-05-14). The 1990+ parser is left untouched (H10 reproducibility / sibling-
pipeline H7 discipline) — pre-1990 + 1990+ share field_specs.py but read from
distinct parser modules so a refactor of one cannot accidentally drift the other.

Era-tag dispatch by year (see field_specs.py module docstring):
- 1968          → 81 bytes, PUBLIC_US_1968_FIELDS (35 fields)
- 1969-1971     → 215 bytes, PUBLIC_US_1969_1971_FIELDS (71 fields)
- 1972-1973     → 215 bytes, PUBLIC_US_1972_1977_FIELDS (95 fields)
- 1974-1979     → 213 bytes, PUBLIC_US_1972_1977_FIELDS (95 fields)
- 1980          → 215 bytes, PUBLIC_US_1972_1977_FIELDS (95 fields)
- 1981          → 213 OR 214 bytes (MIXED; trailing-whitespace stripping anomaly),
                  PUBLIC_US_1972_1977_FIELDS (95 fields). MVP positions 1-212 are
                  byte-identical to other 1972-1988 years; the variable-length tail
                  at pos 213-214 is not exposed in the MVP field list, so both
                  record-length variants parse correctly via positions 1-212 only.
- 1982-1988     → 215 bytes, PUBLIC_US_1972_1977_FIELDS (95 fields). Pos 214-215
                  carry NCHS-internal flags (uniform '0' / '1' empirically); not
                  exposed in MVP.
- 1989          → 350 bytes, PUBLIC_US_1990_2002_FIELDS (37 fields). 1989 inherits
                  the 1989-revision-cert V2 layout byte-exact per C8.17 DO step 4
                  L13-extension probe; DATAYEAR at pos 1-4 = "1989" (4-byte) is the
                  hard distinguishing feature vs the single-digit DATAYEAR encoding
                  used 1968-1988.

Each parsed row carries an explicit `year` column (the kwarg-passed integer year)
so downstream consumers can disambiguate the single-digit-DATAYEAR ambiguity
1968/1978/1988 ("8") and 1969/1979/1989 ("9").

Example (full parse):
  python parse_public_us_pre1990_year.py --zip ~/Desktop/natality-harmonization/raw_data/Nat1985.zip \\
    --year 1985 --out ~/Desktop/natality-harmonization/output/yearly_clean/natality_1985_raw.parquet
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from field_specs import (  # noqa: E402
    PUBLIC_US_1968_FIELDS,
    PUBLIC_US_1969_1971_FIELDS,
    PUBLIC_US_1972_1977_FIELDS,
    PUBLIC_US_1990_2002_FIELDS,
    RECORD_LEN_1968,
    RECORD_LEN_1969_1971,
    RECORD_LEN_1972_1973,
    RECORD_LEN_1974_1977,
    RECORD_LEN_1978_1979,
    RECORD_LEN_1980_1988,
    RECORD_LEN_1990,
)
from zip_text_stream import iter_lines_from_zip  # noqa: E402

# Field type for one byte-position tuple: (name, start, end) 1-based inclusive.
FieldSpec = tuple[str, int, int]


def _slice_field(record: bytes, start: int, end: int) -> str:
    """start/end are 1-based inclusive (NCHS)."""
    return record[start - 1 : end].decode("latin-1")


def _layout_for_year(year: int) -> tuple[int, int, list[FieldSpec]]:
    """Return (min_record_len, max_record_len, fields) for the era-tag containing `year`.

    `min_record_len == max_record_len` for all years except 1981 (mixed 213/214).
    All MVP fields (the tuple lists in field_specs.py) end at positions <= min_record_len,
    so byte slicing is safe for any record where `min_record_len <= len(rec) <= max_record_len`.
    """
    if year == 1968:
        return RECORD_LEN_1968, RECORD_LEN_1968, PUBLIC_US_1968_FIELDS
    if 1969 <= year <= 1971:
        return RECORD_LEN_1969_1971, RECORD_LEN_1969_1971, PUBLIC_US_1969_1971_FIELDS
    if 1972 <= year <= 1973:
        return RECORD_LEN_1972_1973, RECORD_LEN_1972_1973, PUBLIC_US_1972_1977_FIELDS
    if 1974 <= year <= 1977:
        return RECORD_LEN_1974_1977, RECORD_LEN_1974_1977, PUBLIC_US_1972_1977_FIELDS
    if 1978 <= year <= 1979:
        return RECORD_LEN_1978_1979, RECORD_LEN_1978_1979, PUBLIC_US_1972_1977_FIELDS
    if year == 1980:
        return RECORD_LEN_1980_1988, RECORD_LEN_1980_1988, PUBLIC_US_1972_1977_FIELDS
    if year == 1981:
        # MIXED on-disk record length: 2,802,433 @ 213-byte + 516,621 @ 214-byte
        # (trailing-whitespace-stripping inconsistency, not a field-position shift).
        # MVP positions 1-212 are byte-identical to other 1972-1988 years.
        return 213, 214, PUBLIC_US_1972_1977_FIELDS
    if 1982 <= year <= 1988:
        return RECORD_LEN_1980_1988, RECORD_LEN_1980_1988, PUBLIC_US_1972_1977_FIELDS
    if year == 1989:
        # 1989-revision certificate rollout; inherits 1990-2002 V2 layout byte-exact
        # per C8.17 DO step 4 L13-extension probe.
        return RECORD_LEN_1990, RECORD_LEN_1990, PUBLIC_US_1990_2002_FIELDS
    raise ValueError(
        f"Year {year} not in pre-1990 era (1968-1989). For 1990+ use parse_public_us_year.py."
    )


def iter_parsed_records(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    """Per-record dict generator. Kept for SMOKE-test and small-sample callers.

    For full-file parsing use `run_parse()` which delegates to the bulk
    numpy-vectorized path below (10-50x faster than this per-row loop on
    95-field 1972-1988 records).
    """
    min_len, max_len, fields = _layout_for_year(year)

    line_iter = iter_lines_from_zip(zip_path)
    n = 0
    bad_len = 0
    try:
        for raw_line in line_iter:
            rec = raw_line.rstrip(b"\r\n")
            if not rec:
                continue

            if not (min_len <= len(rec) <= max_len):
                bad_len += 1
                if bad_len <= 3:
                    if min_len == max_len:
                        msg = f"warning: expected {min_len} bytes, got {len(rec)}"
                    else:
                        msg = (
                            f"warning: expected {min_len}-{max_len} bytes, got {len(rec)}"
                        )
                    print(msg, file=sys.stderr)
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
        print(
            f"Skipped {bad_len:,} lines with unexpected length", file=sys.stderr
        )


def _build_chunk_columns(
    chunk_buf: bytes,
    n_records: int,
    record_len: int,
    fields: list[FieldSpec],
    year: int,
) -> dict[str, np.ndarray]:
    """Vectorized fixed-width slicing on a per-chunk bytes buffer.

    Each record in `chunk_buf` has exactly `record_len` bytes (the parser
    right-pads under-length 1981 records with trailing 0x20 to reach max_len).
    Per-column extraction uses `arr[:, a-1:b]` non-contiguous view → contiguous
    copy → bytes view → unicode astype, all C-level numpy ops. Returns a dict
    of numpy arrays consumable by `pa.Table.from_pydict` byte-for-byte
    equivalently to `pa.Table.from_pylist(list_of_dicts)` for pure-ASCII inputs.
    """
    arr = np.frombuffer(chunk_buf, dtype=np.uint8).reshape(n_records, record_len)
    cols: dict[str, np.ndarray] = {
        "year": np.full(n_records, year, dtype=np.int64),
    }
    for name, a, b in fields:
        width = b - a + 1
        # arr[:, a-1:b] is a non-contiguous view; copy to contiguous buffer first,
        # then reinterpret the per-row strides as fixed-width bytes scalars.
        col_bytes = np.ascontiguousarray(arr[:, a - 1 : b]).view(f"S{width}").reshape(-1)
        # Decode bytes → unicode via Latin-1 (matches the per-row path's
        # `_slice_field(rec, a, b)` behavior). Latin-1 never errors on bytes
        # 0x00-0xFF; ASCII-only fields decode identically. A single 0xe7 byte
        # surfaced empirically in 1973's source data at C8.17 DO step 5a's
        # first bulk-parse attempt; the explicit `latin-1` decode handles it.
        cols[name] = np.char.decode(col_bytes, "latin-1")
    return cols


def parse_year_chunks(
    zip_path: Path,
    year: int,
    chunk_rows: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, np.ndarray]]:
    """Yield bulk-decoded chunks of up to `chunk_rows` records each.

    Bulk path: accumulate raw line bytes (right-padded to max_len for 1981
    variable-length records) in a bytearray, flush at chunk boundaries via
    `_build_chunk_columns`. ~10-50x faster than the per-record dict path
    on wide (95-field) 1972-1988 records.
    """
    min_len, max_len, fields = _layout_for_year(year)
    pad_bytes = b" " * max_len  # reused for 1981 right-padding

    line_iter = iter_lines_from_zip(zip_path)
    chunk_buf = bytearray()
    n_in_chunk = 0
    n_total = 0
    bad_len = 0
    try:
        for raw_line in line_iter:
            rec = raw_line.rstrip(b"\r\n")
            if not rec:
                continue
            n = len(rec)
            if not (min_len <= n <= max_len):
                bad_len += 1
                if bad_len <= 3:
                    if min_len == max_len:
                        msg = f"warning: expected {min_len} bytes, got {n}"
                    else:
                        msg = (
                            f"warning: expected {min_len}-{max_len} bytes, got {n}"
                        )
                    print(msg, file=sys.stderr)
                continue
            if n < max_len:
                rec = rec + pad_bytes[: max_len - n]
            chunk_buf += rec
            n_in_chunk += 1
            n_total += 1

            if n_in_chunk >= chunk_rows:
                yield _build_chunk_columns(
                    bytes(chunk_buf), n_in_chunk, max_len, fields, year
                )
                chunk_buf.clear()
                n_in_chunk = 0
                if max_rows is not None and n_total >= max_rows:
                    return

            if max_rows is not None and n_total >= max_rows:
                break

        if n_in_chunk > 0:
            yield _build_chunk_columns(
                bytes(chunk_buf), n_in_chunk, max_len, fields, year
            )
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
    """
    Parse pre-1990 natality zip to Parquet. Returns row count written.

    Mirrors `parse_public_us_year.py:run_parse` so downstream orchestration is
    interface-symmetric across the 1968-2024 envelope, but delegates to the
    bulk numpy-vectorized path `parse_year_chunks` (10-50x faster than the
    per-row dict path on wide 1972-1988 records).
    """
    if chunk_rows is None and max_rows is None:
        chunk_rows = 250_000

    out.parent.mkdir(parents=True, exist_ok=True)

    if chunk_rows is None:
        # Small-sample path: collect all rows in memory via the per-record
        # generator (used by SMOKE-test callers with `max_rows` set).
        rows = list(iter_parsed_records(zip_path, year, max_rows=max_rows))
        if not rows:
            raise RuntimeError("No rows parsed; check zip path and record width.")
        df = pd.DataFrame(rows)
        df.to_parquet(out, index=False)
        print(f"Wrote {len(df):,} rows to {out}")
        return len(df)

    # Bulk chunked path: vectorized fixed-width slicing per chunk.
    writer: pq.ParquetWriter | None = None
    total = 0
    for cols in parse_year_chunks(
        zip_path, year, chunk_rows=chunk_rows, max_rows=max_rows
    ):
        n = len(next(iter(cols.values())))
        tbl = pa.Table.from_pydict(cols)
        if writer is None:
            writer = pq.ParquetWriter(str(out), tbl.schema)
        writer.write_table(tbl)
        total += n
    if writer is not None:
        writer.close()

    if total == 0:
        raise RuntimeError("No rows parsed; check zip path and record width.")
    print(f"Wrote {total:,} rows to {out}")
    return total


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to Nat{year}.zip")
    p.add_argument("--year", type=int, required=True, help="Vital data year (1968-1989)")
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
        chunk_rows = None  # small-sample path

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
