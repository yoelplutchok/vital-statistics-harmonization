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
    LINKED_BIRTH_2003_FIELDS,
    LINKED_DEATH_2003_FIELDS,
    LINKED_NUM_DEATH_2003_FIELDS,
    LINKED_DENOMPLUS_RECLEN_2003,
    LINKED_NUM_RECLEN_2003,
    LINKED_BIRTH_2004_FIELDS,
    LINKED_DEATH_2004_FIELDS,
    LINKED_NUM_DEATH_2004_FIELDS,
    LINKED_DENOMPLUS_RECLEN_2004,
    LINKED_NUM_RECLEN_2004,
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
    """Find the denominator(-plus) member in a linked zip archive (cross-era).

    C8.18 DO step 5a broadens this finder to span the cohort-linked
    member-naming conventions across all eras (probed at the DO step 5a
    PRE-FLIGHT, PRE_FLIGHT_LOG 2026-05-19T05:00:00Z):

      1983-1991  ``LinkCO{yy}USden.dat``   (no ``US`` zip suffix)
      1995-2002  ``LinkCO{yy}US{Den,DEN}.dat``
      2003       ``VS03LKBC.USDENPUB``     (DEFLATE64; ``iter_lines_from_zip``
                                            auto-shells to ``7z``)
      2004 / 2005+ ``VS{yy}LKBC.DUSDENOM``

    Two rules, **behavior-preserving for the canonical 2005-2023 path**
    (§9-#7-safe):

      Rule 1 (DENOM-first) — the FIRST member whose upper-name contains
      ``"DENOM"``. This is the pre-5a rule verbatim, so the 2004/2005+
      ``DUSDENOM`` selection is **byte-identical** to before (the
      canonical v3 2005-2015 ``parse_linked_year`` build is unperturbed;
      2016-2023 uses ``parse_linked_cohort_year``, a different finder).

      Rule 2 (cross-era fallback, only if no ``"DENOM"`` member exists) —
      the UNIQUE member whose upper-name contains ``"DEN"`` and not
      ``"NUM"`` / ``"UNL"`` / ``"UNM"`` (covers 1983-1991 ``USden``,
      1995-2002 ``USDen`` / ``USDEN``, 2003 ``USDENPUB``). Zero or >1
      candidates -> ``RuntimeError`` (§2 fail-closed; never silently
      pick a wrong member).
    """
    members = _list_members(zip_path)
    # Rule 1 — DENOM-first (pre-5a behavior; 2004/2005+ unchanged).
    for name in members:
        if "DENOM" in name.upper():
            return name
    # Rule 2 — cross-era fallback for the 1983-2003 cohort members
    # ("DEN" but not "DENOM"); must resolve to exactly one member.
    candidates = [
        name
        for name in members
        if "DEN" in name.upper()
        and not any(tok in name.upper() for tok in ("NUM", "UNL", "UNM"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError(
        f"No unique denominator(-plus) member in {zip_path}. "
        f"DENOM-rule matched none; cross-era 'DEN'-not-NUM/UNL "
        f"candidates={candidates}; members={members}"
    )


def _list_members(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as zf:
        return zf.namelist()


def _find_numerator_member(zip_path: Path) -> str:
    """Find the cohort NUMERATOR member in a linked zip archive.

    C8.18 DO step 5b. The symmetric ``"NUM"`` sibling of
    ``_find_denomplus_member`` (5a). One fail-closed rule — unlike
    ``_find_denomplus_member`` there is NO behavior-preservation
    constraint: the canonical v3 2005-2023 build reads only the
    denominator-plus, so no shipped path calls this finder; it is used
    by ``_iter_two_file_1983_1988`` (the keyless 1983-1988 era) and by
    the DO step 6 re-harmonize.

      The UNIQUE member whose upper-name contains ``"NUM"`` and not
      ``"UNL"`` / ``"UNM"``. Cross-era-correct by name analysis:

        1983-1991  ``LinkCO{yy}USnum.dat``
        1995-2002  ``LinkCO{yy}US{Num,NUM}.dat``
        2003/2004  ``VS0{3,4}LKBC.USNUMPUB``

      The denominator (``USden`` / ``USDEN`` / ``USDENPUB`` /
      ``DUSDENOM`` — ``"DENOM"`` has no ``"NUM"``) and unlinked
      (``USUnl`` / ``USUNL`` = ``"UNL"``; ``USUNMPUB`` = ``"UNM"``, not
      ``"NUM"``) members never contain ``"NUM"`` — the positive test
      alone is unique; the ``not UNL/UNM`` guard is defense-in-depth +
      symmetry with the 5a finder. Zero or >1 candidates ->
      ``RuntimeError`` (§2 fail-closed; never silently pick wrong).
    """
    members = _list_members(zip_path)
    candidates = [
        name
        for name in members
        if "NUM" in name.upper()
        and not any(tok in name.upper() for tok in ("UNL", "UNM"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError(
        f"No unique numerator member in {zip_path}. "
        f"'NUM'-not-UNL/UNM candidates={candidates}; members={members}"
    )


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
    C8.18 DO step 4b adds 2003 (additive): a 783-byte Denominator-PLUS
    (birth cert 1-750 + death "plus" 751-783 incl. RECWT@776-783),
    2003-revision transition (REVISION@7 S=1989-unrev / A=2003-rev; one
    fixed-width layout regardless), authored FRESH from the LinkCO03Guide
    DETAIL (the prior "2003 numerator = 1259" assumption was FALSIFIED ->
    1142; L13-extension; never assume same-model==same-layout).
    C8.18 DO step 4c adds 2004 (additive): a 900-byte Denominator-PLUS
    (birth cert 1-867 + death "plus" 868-900 incl. RECWT@893-900),
    2003-revision transition continued, authored FRESH from the
    LinkCO04Guide DETAIL (the receipt-note "2004 = 900/1142"
    extrapolation was FALSIFIED -> numerator 1259, and the "den-plus ==
    LINKED_BIRTH_2005_2013" hypothesis was FALSIFIED -> 2003-rev cohort
    layout; L13-extension). 2004 = DEFLATE (NOT DEFLATE64 like 2003).
    1992-1994 is the permanent NCHS linkage gap (unconfigured -> ValueError).
    The two-file numerator left-join + the `_find_denomplus_member`
    "DEN"-vs-"DENOM" support (+ the DEFLATE64-at-2003 decompressor =
    CLI 7z stream) are C8.18 DO step 5 parser concerns; this
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
    if year == 2003:
        # C8.18 DO step 4b: 783-byte Denominator-PLUS (birth cert
        # 1-750 + death "plus" 751-783 incl. RECWT@776-783; den-plus
        # ends @783 per the LinkCO03Guide p55 divider). 2003-revision
        # transition (REVISION@7 S=1989-unrev / A=2003-rev); one
        # fixed-width layout regardless of revision. Authored FRESH
        # from the LinkCO03Guide DETAIL (L13-extension; the prior
        # "1259 numerator" assumption was FALSIFIED -> 1142).
        return (
            LINKED_DENOMPLUS_RECLEN_2003,
            LINKED_BIRTH_2003_FIELDS,
            LINKED_DEATH_2003_FIELDS,
        )
    if year == 2004:
        # C8.18 DO step 4c: 900-byte Denominator-PLUS (birth cert
        # 1-867 + death "plus" 868-900 incl. RECWT@893-900; den-plus
        # ends @900). 2003-revision transition continued (REVISION@7
        # S=1989-unrev / A=2003-rev); one fixed-width layout regardless.
        # Authored FRESH from the LinkCO04Guide DETAIL (L13-extension;
        # the receipt-note "2004 = 900/1142" extrapolation was FALSIFIED
        # -> 1259, and the "den-plus == LINKED_BIRTH_2005_2013"
        # hypothesis was FALSIFIED -> 2003-rev cohort layout). The
        # death "plus" 868-900 == the LINKED_DEATH_2005_2013 model
        # (value-verified on real 2004 data). LinkCO04US.zip = DEFLATE
        # (stdlib-fine; NOT DEFLATE64 like 2003).
        return (
            LINKED_DENOMPLUS_RECLEN_2004,
            LINKED_BIRTH_2004_FIELDS,
            LINKED_DEATH_2004_FIELDS,
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
        f"Supported: 1983-1991 + 1995-2004 (cohort denominator-plus), 2005-2020. "
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
    (RESERVED1@231-260 + multiple-cause + death geo/date). C8.18 DO
    step 4b adds 2003 (additive): 1142-byte numerator = birth 1-750
    REUSE LINKED_BIRTH_2003_FIELDS, death "plus" 751-783 REUSE
    LINKED_DEATH_2003_FIELDS, numerator-only mortality 784-1142
    (multiple-cause ENTITY/RECORD + death geo/date; ICD-10 throughout
    — 2003 cohort). The prior "2003 numerator = 1259" assumption was
    FALSIFIED -> 1142 (guide p17 + byte-exact zip-member arithmetic;
    L13-extension). C8.18 DO step 4c adds 2004 (additive): 1259-byte
    numerator = birth 1-867 REUSE LINKED_BIRTH_2004_FIELDS, death
    "plus" 868-900 REUSE LINKED_DEATH_2004_FIELDS, numerator-only
    mortality 901-1259 (ENTITY/RECORD + death geo/date; ICD-10 — 2004
    cohort). The receipt-note "2004 = 900/1142" extrapolation was
    FALSIFIED -> numerator 1259 (guide p18 + zip-member arithmetic;
    L13-extension; never assume same-model==same-layout).
    1992-1994 = the permanent NCHS linkage gap
    (unconfigured -> ValueError). The two-file num/den construction,
    the numerator<->denominator-plus join (1989-1991 key =
    MATCHS,IDNUMBER; 1995-2002 key = IDNUMBER@2-6 per LinkCO95Guide
    p20; 2003/2004 key = IDNUMBER@10-14 per LinkCO0{3,4}Guide p20),
    `_find_denomplus_member` "DEN"/"NUM" support, the DEFLATE64-at-2003
    decompressor (CLI 7z stream), and the harmonize path are C8.18 DO
    step 5 concerns; this function only returns the layout substrate
    (no zip I/O).
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
    if year == 2003:
        # C8.18 DO step 4b: 1142-byte numerator (NOT 1259 — the prior
        # assumption was FALSIFIED; guide p17 + zip-member arithmetic
        # 27,843 x (1142+2 CRLF) = 31,852,392 = VS03LKBC.USNUMPUB).
        # birth 1-750 + death "plus" 751-783 (REUSE the den-plus
        # specs) + numerator-only mortality 784-1142. ICD-10
        # throughout (2003 cohort -> deaths 2003-2004).
        return (
            LINKED_NUM_RECLEN_2003,
            LINKED_BIRTH_2003_FIELDS,
            LINKED_DEATH_2003_FIELDS + LINKED_NUM_DEATH_2003_FIELDS,
        )
    if year == 2004:
        # C8.18 DO step 4c: 1259-byte numerator (the receipt-note
        # "2004 = 900/1142" extrapolation was FALSIFIED; guide p18 +
        # zip-member arithmetic 27,763 x (1259+2 CRLF) = 35,009,143 =
        # VS04LKBC.USNUMPUB). birth 1-867 + death "plus" 868-900
        # (REUSE the den-plus specs) + numerator-only mortality
        # 901-1259. ICD-10 throughout (2004 cohort -> deaths 2004-2005).
        return (
            LINKED_NUM_RECLEN_2004,
            LINKED_BIRTH_2004_FIELDS,
            LINKED_DEATH_2004_FIELDS + LINKED_NUM_DEATH_2004_FIELDS,
        )
    raise ValueError(
        f"Year {year} not configured for the cohort numerator. "
        f"Supported: 1983-1991 + 1995-2004 (cohort numerator). "
        f"(Denominator layouts: see _layout_for_linked_year.)"
    )


def _iter_two_file_1983_1988(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    """The keyless 1983-1988 self-contained-numerator + aggregate-
    denominator construction (C8.18 DO step 5b).

    1983-1988 carry NO record-level public-use key (the C8.18 DO step
    3b byte-confirmed finding), so a record-level numerator<->
    denominator join is impossible; fabricating a proxy key would
    violate §2 fail-closed. The per-year ``_raw`` representation is the
    **lossless union** of two source segments, discriminated by a
    synthetic ``link_segment`` column:

      ``link_segment="den"`` — every 91-byte ``LinkCO{yy}USden.dat``
        record via ``LINKED_BIRTH_1983_1988_FIELDS`` (the aggregate
        birth denominator: ALL live births, one row per birth, no
        death section — the den file carries none).

      ``link_segment="num"`` — every 500-byte ``LinkCO{yy}USnum.dat``
        record via ``LINKED_BIRTH_1983_1988_FIELDS`` (locs 1-91, the
        deceased infant's own birth covariates) +
        ``LINKED_NUM_DEATH_1983_1988_FIELDS`` (locs 194-500, the ICD-9
        mortality section); the self-contained linked-infant-death set
        (MATCHS in {1,2}; locs 92-193 numerator-only reserved, not
        enumerated per DO step 3b).

    Lossless; H6 row-count conservation (den rows == guide-stated
    births; num rows == guide-stated infant deaths). The harmonized
    one-row-per-birth / ``infant_death`` / ``record_weight`` semantics
    for the keyless era are DO step 5c (the den segment = one row per
    birth with ``infant_death`` null/unknown per-record since
    un-linkable; the num segment = the within-era infant-death detail
    surface — a documented within-era structural difference, not a
    silent deviation: COMPARABILITY / harmonized_schema notes at
    5c/6 + the manuscript Coverage paragraph = Phase-D D.4;
    DECISION_LOG 2026-05-19T08:00:00Z).

    ``max_rows`` caps **each segment independently** (up to
    ``max_rows`` den rows + up to ``max_rows`` num rows), so a bounded
    sample represents BOTH segments — a single shared counter would
    fill entirely from the multi-million-row den segment and never
    reach the num segment (surfaced + refined at the DO step 5b SMOKE;
    PRE_FLIGHT_LOG 2026-05-19T08:00:00Z addendum). ``max_rows=None``
    yields the full files (lossless; the DO step 6 re-harmonize).
    """
    den_member = _find_denomplus_member(zip_path)            # 5a -> USden
    den_len, den_birth, den_death = _layout_for_linked_year(year)  # (91, BIRTH, [])
    num_member = _find_numerator_member(zip_path)             # -> USnum
    num_len, num_birth, num_death = _numerator_layout_for_linked_year(year)

    for seg, member, expected_len, fields in (
        ("den", den_member, den_len, den_birth + den_death),
        ("num", num_member, num_len, num_birth + num_death),
    ):
        print(f"Reading {seg} member: {member}", file=sys.stderr)
        line_iter = iter_lines_from_zip(zip_path, member_name=member)
        bad_len = 0
        n = 0  # per-segment counter (independent cap; see docstring)
        try:
            for raw_line in line_iter:
                rec = raw_line.rstrip(b"\r\n")
                if not rec:
                    continue
                if len(rec) != expected_len:
                    bad_len += 1
                    if bad_len <= 3:
                        print(
                            f"warning [{seg}]: expected {expected_len} bytes, "
                            f"got {len(rec)}",
                            file=sys.stderr,
                        )
                    continue
                d: dict[str, str | int] = {"year": year, "link_segment": seg}
                for name, a, b in fields:
                    d[name] = _slice_field(rec, a, b)
                yield d
                n += 1
                if max_rows is not None and n >= max_rows:
                    break  # cap THIS segment; continue to the next
        finally:
            line_iter.close()
        if bad_len:
            print(
                f"Skipped {bad_len:,} {seg} lines with unexpected length",
                file=sys.stderr,
            )


def iter_parsed_records(
    zip_path: Path,
    year: int,
    max_rows: int | None = None,
) -> Iterator[dict[str, str | int]]:
    if 1983 <= year <= 1988:
        # C8.18 DO step 5b: the keyless pre-2005 cohort-linked era is a
        # two-file (births-only denominator + self-contained numerator)
        # construction, NOT a single denominator-PLUS member. The
        # 1989-2004 + 2005+ single-member body below is byte-untouched
        # (§9-#7-safe; the 5a behavior-preserving discipline).
        yield from _iter_two_file_1983_1988(zip_path, year, max_rows=max_rows)
        return
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


def _expected_parsed_schema(year: int) -> pa.Schema | None:
    """The explicit unified parquet schema ``iter_parsed_records``
    emits for ``year`` — or ``None`` for the homogeneous single-member
    years, whose existing ``pa.Table.from_pylist(rows)`` inference is
    correct and MUST stay byte-identical (the shipped single-member
    parquets; §9-#7).

    The keyless 1983-1988 two-file construction (the RESOLVED 5b model)
    yields a HETEROGENEOUS den/num union: ``link_segment="den"`` rows
    carry only the 91-byte birth section; ``link_segment="num"`` rows
    add the 194-500 ICD-9 mortality section. ``_iter_two_file_1983_1988``
    yields ALL den rows BEFORE any num row, and ``pa.*.from_pylist``
    infers the Arrow schema from the FIRST record's keys ONLY — so a
    naive materialization SILENTLY DROPS the entire numerator ICD-9
    mortality section (single-chunk path) / the chunked
    ``ParquetWriter`` is fixed to a den-only schema and CRASHES at the
    den->num boundary. This helper returns the deterministic den∪num
    column union (from the parser's OWN layout dispatchers — the same
    ``_layout_for_linked_year`` + ``_numerator_layout_for_linked_year``
    ``_iter_two_file_1983_1988`` itself uses; no data scan, no new
    layout logic) so ``run_parse`` materializes the 1983-1988 _raw
    parquet LOSSLESSLY (H6 column-conservation). C8.18 DO step 5c-iii:
    a §7 latent defect in the RESOLVED-5b ``run_parse`` surfaced at the
    5c-iii Convention-3/SMOKE cheap-check; the human-authorized minimal
    root-cause fix (PRE_FLIGHT_LOG 2026-05-20T00:00:00Z addendum +
    DECISION_LOG + LESSONS; anti-pattern #7 fix-the-root-cause).
    """
    if not (1983 <= year <= 1988):
        return None
    _dl, den_birth, den_death = _layout_for_linked_year(year)
    _nl, num_birth, num_death = _numerator_layout_for_linked_year(year)
    names: list[str] = []
    for nm, _a, _b in den_birth + den_death + num_birth + num_death:
        if nm not in names:
            names.append(nm)
    return pa.schema(
        [(nm, pa.string()) for nm in names]
        + [("year", pa.int64()), ("link_segment", pa.string())]
    )


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

    # 1983-1988 ONLY: an explicit unified den∪num schema (the keyless
    # two-file construction is per-row heterogeneous; from_pylist infers
    # from the first record only). None for every homogeneous year →
    # the original from_pylist(rows)/tbl.schema path byte-untouched
    # (§9-#7 — the byte-exact shipped single-member parquets).
    _schema = _expected_parsed_schema(year)

    def _tbl(recs):
        return (
            pa.Table.from_pylist(recs, schema=_schema)
            if _schema is not None else pa.Table.from_pylist(recs)
        )

    if chunk_rows is None:
        rows = list(iter_parsed_records(zip_path, year, max_rows=max_rows))
        if not rows:
            raise RuntimeError("No rows parsed; check zip path and record width.")
        tbl = _tbl(rows)
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
                tbl = _tbl(buffer)
                if writer is None:
                    writer = pq.ParquetWriter(
                        str(out),
                        _schema if _schema is not None else tbl.schema,
                    )
                writer.write_table(tbl)
                total += len(buffer)
                buffer.clear()
        if buffer:
            tbl = _tbl(buffer)
            if writer is None:
                writer = pq.ParquetWriter(
                    str(out),
                    _schema if _schema is not None else tbl.schema,
                )
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
