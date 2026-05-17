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
    LINKED_BIRTH_1983_1988_FIELDS,
    LINKED_BIRTH_1989_1991_FIELDS,
    LINKED_DEATH_1989_1991_FIELDS,
    LINKED_DEN_RECLEN_1983_1988,
    LINKED_DENOMPLUS_RECLEN_1989_1991,
    LINKED_NUM_DEATH_1983_1988_FIELDS,
    LINKED_NUM_DEATH_1989_1991_FIELDS,
    LINKED_NUM_RECLEN_1983_1988,
    LINKED_NUM_RECLEN_1989_1991,
    LINKED_BIRTH_1995_2002_FIELDS,
    LINKED_DEATH_1995_2002_FIELDS,
    LINKED_NUM_DEATH_1995_2002_FIELDS,
    LINKED_DENOMPLUS_RECLEN_1995_2002,
    LINKED_NUM_RECLEN_1995_2002,
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
    """Return (expected_reclen, birth_fields, death_fields) for the linked denominator-plus.

    C8.18 DO step 3a adds the pre-1990 cohort denominator layouts (additive;
    the 2005/2014 branches below are byte-untouched). 1983-1988 is a
    births-only 91-byte Denominator (no death section in this file; the
    500-byte numerator carries death detail -> DO step 3b). 1989-1991 is a
    225-byte Denominator-PLUS (birth cert + appended death-derived section).
    C8.18 DO step 4a adds 1995-2002 (additive): a 230-byte
    Denominator-PLUS (birth cert 1-210 + death "plus" 211-230 incl.
    RECWT@223-230), authored FRESH from the LinkCO95Guide DETAIL (the
    1995-2002-reuses-1989-1991 hypothesis was FALSIFIED; L13-extension).
    1992-1994 is the permanent NCHS linkage gap (unconfigured -> ValueError).
    The two-file numerator left-join + the `_find_denomplus_member`
    "DEN"-vs-"DENOM" support are C8.18 DO step 5 parser concerns; this
    function only returns the layout substrate.
    """
    if 1983 <= year <= 1988:
        return (
            LINKED_DEN_RECLEN_1983_1988,
            LINKED_BIRTH_1983_1988_FIELDS,
            [],
        )
    if 1989 <= year <= 1991:
        return (
            LINKED_DENOMPLUS_RECLEN_1989_1991,
            LINKED_BIRTH_1989_1991_FIELDS,
            LINKED_DEATH_1989_1991_FIELDS,
        )
    if 1995 <= year <= 2002:
        # C8.18 DO step 4a: 230-byte Denominator-PLUS (birth cert
        # 1-210 + death "plus" 211-230 incl. RECWT@223-230). Authored
        # FRESH from the LinkCO95Guide DETAIL (the 1995-2002-reuses-
        # 1989-1991 hypothesis was FALSIFIED; L13-extension). One layout
        # spans 1995-2002 (ICD-9 1995-98 / ICD-10 1999-2002 = a
        # within-era UCOD@216-219 value-domain, not a byte shift).
        return (
            LINKED_DENOMPLUS_RECLEN_1995_2002,
            LINKED_BIRTH_1995_2002_FIELDS,
            LINKED_DEATH_1995_2002_FIELDS,
        )
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
        f"Year {year} not yet configured for linked files. "
        f"Supported: 1983-1991 + 1995-2002 (cohort denominator-plus), 2005-2020. "
        f"(1992-1994 = the permanent NCHS linkage gap.)"
    )


def _numerator_layout_for_linked_year(
    year: int,
) -> tuple[int, list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    """Return (expected_reclen, birth_fields, death_fields) for the cohort NUMERATOR.

    C8.18 DO step 3b adds the pre-1990 cohort NUMERATOR layouts
    (additive; `_layout_for_linked_year` above + the 2005/2014 +
    3a-denominator branches are byte-untouched, H10/HALT-13).
    1983-1988 numerator = 500-byte: natality locs 1-91 REUSE
    LINKED_BIRTH_1983_1988_FIELDS (the deceased infant's birth
    covariates; the NCHS shared "Denominator Record and Natality
    Section" layout), locs 92-193 = numerator-only reserved (not
    enumerated), mortality locs 194-500. 1989-1991 numerator =
    535-byte: birth locs 1-212 REUSE LINKED_BIRTH_1989_1991_FIELDS,
    death-derived "plus" locs 213-225 REUSE LINKED_DEATH_1989_1991_FIELDS,
    mortality locs 226-535. C8.18 DO step 4a adds 1995-2002 (additive):
    535-byte numerator = birth locs 1-210 REUSE
    LINKED_BIRTH_1995_2002_FIELDS, death "plus" 211-230 REUSE
    LINKED_DEATH_1995_2002_FIELDS, numerator-only mortality 231-535
    (RESERVED1@231-260 + multiple-cause + death geo/date). 1992-1994 =
    the permanent NCHS linkage gap (unconfigured -> ValueError). The
    two-file num/den construction, the numerator<->denominator-plus
    join (1989-1991 key = MATCHS,IDNUMBER; 1995-2002 key = IDNUMBER@2-6
    per LinkCO95Guide p20), `_find_denomplus_member` "DEN"/"NUM"
    support, and the harmonize path are C8.18 DO step 5 concerns; this
    function only returns the layout substrate (no zip I/O).
    """
    if 1983 <= year <= 1988:
        return (
            LINKED_NUM_RECLEN_1983_1988,
            LINKED_BIRTH_1983_1988_FIELDS,
            LINKED_NUM_DEATH_1983_1988_FIELDS,
        )
    if 1989 <= year <= 1991:
        return (
            LINKED_NUM_RECLEN_1989_1991,
            LINKED_BIRTH_1989_1991_FIELDS,
            LINKED_DEATH_1989_1991_FIELDS + LINKED_NUM_DEATH_1989_1991_FIELDS,
        )
    if 1995 <= year <= 2002:
        # C8.18 DO step 4a: 535-byte numerator = birth 1-210 + death
        # "plus" 211-230 (REUSE the den-plus specs) + numerator-only
        # mortality 231-535 (RESERVED1@231-260 + multiple-cause +
        # death geo/date). Authored FRESH from the LinkCO95Guide
        # DETAIL (L13-extension; reuse-of-1989-1991 FALSIFIED).
        return (
            LINKED_NUM_RECLEN_1995_2002,
            LINKED_BIRTH_1995_2002_FIELDS,
            LINKED_DEATH_1995_2002_FIELDS + LINKED_NUM_DEATH_1995_2002_FIELDS,
        )
    raise ValueError(
        f"Year {year} not configured for the cohort numerator. "
        f"Supported: 1983-1991 + 1995-2002 (cohort numerator). "
        f"(Denominator layouts: see _layout_for_linked_year.)"
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
