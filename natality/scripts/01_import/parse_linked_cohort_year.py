#!/usr/bin/env python3
"""
Parse NCHS linked birth-infant death period-cohort files (2016-2020+).

Starting with the 2017PE2016CO release, NCHS switched to a period-cohort format:
  - Denominator file (1346 bytes): natality record + FLGND at pos 1346
  - Numerator files (1743 bytes): natality + death-side fields at 1347+
  - Each zip contains two period years: (Y)PE(Y-1)CO has Y-1 and Y denom/numer

To create a cohort file for year Y:
  1. Read the Y denominator (all births in year Y)
  2. Read the Y numerator, filter DOB_YY=Y (same-year deaths)
  3. Read the Y+1 numerator, filter DOB_YY=Y (next-year deaths)
  4. Merge death fields onto denominator by CO_SEQNUM

Output is equivalent to the 2005-2015 denominator-plus format: one row per birth,
with death-side fields populated for deaths and null for survivors.

Example:
  python parse_linked_cohort_year.py \\
    --zip ../../raw_data/linked/2017PE2016CO.zip --year 2016 \\
    --out ../../output/linked/linked_2016_denomplus.parquet
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from field_specs import LINKED_BIRTH_2014_2020_FIELDS

# Death-side fields in the NUMERATOR file (positions 1347-1743).
# These match the 2014-2020 denominator-plus death positions exactly.
NUMERATOR_DEATH_FIELDS: list[tuple[str, int, int]] = [
    ("FLGND", 1346, 1346),       # Match status (always 1 in numerator)
    ("AGED", 1356, 1358),        # Age at death in days (AGEDX in user guide)
    ("AGER5", 1359, 1359),       # Infant age recode 5 (AGER5X)
    ("AGER22", 1360, 1361),      # Infant age recode 22 (AGER22X)
    ("MANNER", 1362, 1362),      # Manner of death
    ("DISPO", 1363, 1363),       # Method of disposition
    ("AUTOPSY", 1364, 1364),     # Autopsy
    ("PLACE_INJ", 1366, 1366),   # Place of injury
    ("UCOD", 1368, 1371),        # Underlying cause of death (ICD-10)
    ("UCODR130", 1373, 1375),    # 130 Infant Cause of Death recode
    ("RECWT", 1377, 1384),       # Record weight
]

DENOMINATOR_RECLEN = 1346
NUMERATOR_RECLEN = 1743


def _slice(rec: bytes, start: int, end: int) -> str:
    """1-based inclusive slice."""
    return rec[start - 1 : end].decode("latin-1")


def _find_members(zip_path: Path) -> dict[str, list[str]]:
    """Identify denominator and numerator members by year in the zip.

    Returns dict like:
      {'2016': {'denom': 'VS16...DENPUB...', 'numer': 'VS16...NUMPUB...'},
       '2017': {'denom': 'VS17...DENPUB...', 'numer': 'VS17...NUMPUB...'}}
    """
    with zipfile.ZipFile(zip_path) as zf:
        members = zf.namelist()

    result: dict[str, dict[str, str]] = {}
    for name in members:
        upper = name.upper()
        # Extract year from VS{YY}LINK or VS{YYYY}LINK (2021PE2020CO uses 4-digit)
        m = re.search(r"VS(\d{2,4})LINK", upper)
        if not m:
            continue
        yy = m.group(1)
        full_year = f"20{yy}" if len(yy) == 2 else yy

        if "DENPUB" in upper or "DENOMUS" in upper or "DENOM" in upper:
            result.setdefault(full_year, {})["denom"] = name
        elif "NUMPUB" in upper or "DETAILUS" in upper or "NUMER" in upper:
            result.setdefault(full_year, {})["numer"] = name

    return result


def _read_numerator_deaths(
    zip_path: Path,
    member: str,
    cohort_year: int,
) -> dict[tuple[str, str], dict[str, str]]:
    """Read numerator, filter to DOB_YY=cohort_year, return dict keyed by
    (CO_SEQNUM, CO_YOD) — the composite key documented in 21PE20CO_linkedUG.pdf
    as the correct merge key (AUDIT D7).  CO_YOD is at positions 372-375
    (year of death, 4 digits)."""
    deaths: dict[tuple[str, str], dict[str, str]] = {}
    cohort_str = str(cohort_year)

    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as f:
            for line in f:
                rec = line.rstrip(b"\r\n")
                if len(rec) != NUMERATOR_RECLEN:
                    continue
                dob_yy = _slice(rec, 9, 12)
                if dob_yy != cohort_str:
                    continue

                seqnum = _slice(rec, 365, 371).strip()
                co_yod = _slice(rec, 372, 375).strip()
                if not seqnum:
                    continue

                d: dict[str, str] = {}
                for name, a, b in NUMERATOR_DEATH_FIELDS:
                    d[name] = _slice(rec, a, b)
                deaths[(seqnum, co_yod)] = d

    return deaths


def run_parse(
    zip_path: Path,
    cohort_year: int,
    out: Path,
    *,
    max_rows: int | None = None,
    chunk_rows: int = 250_000,
) -> int:
    """Parse a period-cohort zip into a denominator-plus-style Parquet."""
    out.parent.mkdir(parents=True, exist_ok=True)

    members = _find_members(zip_path)
    cohort_str = str(cohort_year)
    next_str = str(cohort_year + 1)

    # Identify the two years in the zip
    yy_short = str(cohort_year)[-2:]
    yy_next = str(cohort_year + 1)[-2:]

    if cohort_str not in members or "denom" not in members[cohort_str]:
        raise RuntimeError(
            f"No denominator for {cohort_year} in {zip_path}. "
            f"Available years: {sorted(members.keys())}"
        )

    denom_member = members[cohort_str]["denom"]
    print(f"Denominator: {denom_member}", file=sys.stderr)

    # Build death lookup from both numerators — composite key (seqnum, co_yod).
    death_lookup: dict[tuple[str, str], dict[str, str]] = {}

    # Same-year numerator (deaths in cohort_year)
    if cohort_str in members and "numer" in members[cohort_str]:
        numer1 = members[cohort_str]["numer"]
        print(f"Reading {numer1} (same-year deaths) ...", file=sys.stderr)
        d1 = _read_numerator_deaths(zip_path, numer1, cohort_year)
        print(f"  {len(d1):,} deaths in {cohort_year} born in {cohort_year}", file=sys.stderr)
        death_lookup.update(d1)

    # Next-year numerator (deaths in cohort_year+1) — AUDIT D7: assert that the
    # same-year and next-year keysets are disjoint.  They must be, because the
    # composite key includes year-of-death; a collision would indicate a data
    # error upstream that would silently overwrite the same-year record.
    if next_str in members and "numer" in members[next_str]:
        numer2 = members[next_str]["numer"]
        print(f"Reading {numer2} (next-year deaths) ...", file=sys.stderr)
        d2 = _read_numerator_deaths(zip_path, numer2, cohort_year)
        print(f"  {len(d2):,} deaths in {cohort_year+1} born in {cohort_year}", file=sys.stderr)
        overlap = set(death_lookup).intersection(d2)
        if overlap:
            raise RuntimeError(
                f"CO_SEQNUM+CO_YOD collision between same-year and next-year "
                f"numerator files for cohort {cohort_year}: {len(overlap)} overlapping keys. "
                f"First few: {list(overlap)[:5]}"
            )
        death_lookup.update(d2)

    total_deaths = len(death_lookup)
    print(f"Total cohort deaths: {total_deaths:,}", file=sys.stderr)

    # Now stream the denominator and merge
    birth_fields = LINKED_BIRTH_2014_2020_FIELDS
    # Build blank-death template with space-padded strings (consistent with
    # 2005-2015 denominator-plus format where survivor records have blank bytes).
    # EXCEPTION: RECWT is filled with "1.000000" for survivors to match the NCHS
    # 2005-2015 convention (where denominator-plus survivor rows carry RECWT=1.000000).
    # Leaving RECWT blank breaks the "every survivor has weight 1.0" invariant.
    blank_death: dict[str, str] = {}
    for name, a, b in NUMERATOR_DEATH_FIELDS:
        field_len = b - a + 1
        if name == "RECWT":
            blank_death[name] = "1.000000"[:field_len].ljust(field_len)
        else:
            blank_death[name] = " " * field_len

    writer: pq.ParquetWriter | None = None
    buffer: list[dict[str, str | int]] = []
    total = 0
    matched_deaths = 0

    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(denom_member) as f:
            for line in f:
                rec = line.rstrip(b"\r\n")
                if len(rec) != DENOMINATOR_RECLEN:
                    continue

                row: dict[str, str | int] = {"year": cohort_year}

                # Birth-side fields
                for name, a, b in birth_fields:
                    row[name] = _slice(rec, a, b)

                # Look up death fields by (CO_SEQNUM, CO_YOD).  The denominator
                # doesn't carry CO_YOD (births don't have a year-of-death), so
                # we try both the cohort year and the next year in turn —
                # matching NCHS's documented merge approach (AUDIT D7).
                seqnum = _slice(rec, 365, 371).strip()
                match = None
                if seqnum:
                    k1 = (seqnum, cohort_str)
                    k2 = (seqnum, next_str)
                    if k1 in death_lookup:
                        match = death_lookup[k1]
                    elif k2 in death_lookup:
                        match = death_lookup[k2]
                if match is not None:
                    row.update(match)
                    matched_deaths += 1
                else:
                    # Survivor: set FLGND to blank (consistent with 2014-2015 convention)
                    row.update(blank_death)

                buffer.append(row)

                if len(buffer) >= chunk_rows:
                    tbl = pa.Table.from_pylist(buffer)
                    if writer is None:
                        writer = pq.ParquetWriter(str(out), tbl.schema)
                    writer.write_table(tbl)
                    total += len(buffer)
                    buffer.clear()

                if max_rows is not None and (total + len(buffer)) >= max_rows:
                    break

    if buffer:
        tbl = pa.Table.from_pylist(buffer)
        if writer is None:
            writer = pq.ParquetWriter(str(out), tbl.schema)
        writer.write_table(tbl)
        total += len(buffer)

    if writer is not None:
        writer.close()

    if total == 0:
        raise RuntimeError("No rows parsed.")

    unmatched = total_deaths - matched_deaths
    print(
        f"Wrote {total:,} rows to {out}\n"
        f"  Deaths matched: {matched_deaths:,} / {total_deaths:,}",
        file=sys.stderr,
    )
    if unmatched > 0:
        print(f"  WARNING: {unmatched:,} deaths not matched to denominator", file=sys.stderr)

    return total


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True, help="Path to {YYYY}PE{YYYY}CO.zip")
    p.add_argument("--year", type=int, required=True, help="Cohort birth year (e.g. 2016)")
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--chunk-rows", type=int, default=250_000)
    p.add_argument("--out", type=Path, required=True, help="Output Parquet path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        run_parse(args.zip, args.year, args.out, max_rows=args.max_rows, chunk_rows=args.chunk_rows)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
