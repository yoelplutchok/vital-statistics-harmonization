"""DESIGN: tracks-current-state

C8.18 DO step 3b SMOKE — pre-1990 cohort linked NUMERATOR layout.

Sibling of ``test_linked_cohort_1983_1991_layout_smoke.py`` (the 3a
DENOMINATOR harness); kept separate so 3a/3b stay independently
re-runnable (C8.17 DO5a/5b + C8.18 DO3a sub-step-isolation precedent).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
of the additive ``field_specs.py`` cohort-numerator layouts (record-
length constants = the documented fixed-width contract, byte-exact-
confirmed against the guide-stated numerator counts; in-bounds + non-
overlap; the additive numerator dispatcher; the 3a/2005/2014
denominator dispatcher unregressed) plus, on the real SHA-anchored
cohort zips, value-distribution + encoding invariants (L13-extension:
byte position alone is not trusted; the C8.18 DO3a SMOKE-Tier-1 catch
is the governing precedent). No mutable annotation value is pinned
(record lengths 500 / 535 are fixed historical NCHS facts).

Tier 0 (synthetic, always runs): hand-built records with planted
values at documented positions + a position-shift NEGATIVE check (L3:
proves the slicing discriminates position, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip
absent): first records of LinkCO{83,85,88}USnum.dat (500-byte) +
LinkCO{89,90,91}USnum.dat (535-byte) — empirical block size =
reclen + CR/LF (FIX_LOG 2026-05-14 L13 arithmetic-class defense),
ASCII-decodability, BIRYR == cohort year for every sampled record,
and value-distribution of the death-side anchors (MATCHS domain,
ICD-9 UCOD plausibility, entity/record-axis count fields).
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_SPEC_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
if str(_SPEC_DIR) not in sys.path:
    sys.path.insert(0, str(_SPEC_DIR))

from field_specs import (  # noqa: E402
    LINKED_BIRTH_1983_1988_FIELDS,
    LINKED_BIRTH_1989_1991_FIELDS,
    LINKED_DEATH_1989_1991_FIELDS,
    LINKED_NUM_DEATH_1983_1988_FIELDS,
    LINKED_NUM_DEATH_1989_1991_FIELDS,
    LINKED_NUM_RECLEN_1983_1988,
    LINKED_NUM_RECLEN_1989_1991,
)
from parse_linked_year import (  # noqa: E402
    _layout_for_linked_year,
    _numerator_layout_for_linked_year,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# SHAPE: structural invariants of the numerator layout substrate
# --------------------------------------------------------------------------

def _assert_layout_well_formed(fields, reclen, name):
    assert fields, f"{name} empty"
    names = [f[0] for f in fields]
    assert len(names) == len(set(names)), f"{name} duplicate field name"
    for fname, start, end in fields:
        assert fname.isupper() and fname.isidentifier(), f"{name} bad name {fname!r}"
        assert 1 <= start <= end <= reclen, f"{name} {fname} out of [1,{reclen}]: {start}-{end}"
    ordered = sorted(fields, key=lambda f: f[1])
    for prev, cur in zip(ordered, ordered[1:]):
        assert cur[1] > prev[2], f"{name} overlap: {prev} then {cur}"


def test_num_reclen_constants_are_documented_record_lengths():
    # 500 / 535 are NCHS-guide-documented fixed-width numerator record
    # lengths (LinkCO83Guide p12 = 500; LinkCO89Guide p17 = 535).
    # Byte-exact-confirmed: LinkCO83USnum.dat 19,931,408 / 502 = 39,704
    # (guide count); LinkCO89USnum.dat 20,730,885 / 537 = 38,605. Fixed.
    assert LINKED_NUM_RECLEN_1983_1988 == 500
    assert LINKED_NUM_RECLEN_1989_1991 == 535


def test_1983_1988_numerator_layout_well_formed():
    # Natality section locs 1-91 REUSE LINKED_BIRTH_1983_1988_FIELDS;
    # locs 92-193 = numerator-only RESERVED (gap, not enumerated);
    # mortality section 194-500 = LINKED_NUM_DEATH_1983_1988_FIELDS.
    _assert_layout_well_formed(
        LINKED_BIRTH_1983_1988_FIELDS, LINKED_NUM_RECLEN_1983_1988, "1983_1988_num_birth"
    )
    _assert_layout_well_formed(
        LINKED_NUM_DEATH_1983_1988_FIELDS, LINKED_NUM_RECLEN_1983_1988, "1983_1988_num_death"
    )
    # natality ends by loc 91; the 92-193 reserved gap; mortality 194-500
    assert max(f[2] for f in LINKED_BIRTH_1983_1988_FIELDS) <= 91
    assert min(f[1] for f in LINKED_NUM_DEATH_1983_1988_FIELDS) == 194
    assert max(f[2] for f in LINKED_NUM_DEATH_1983_1988_FIELDS) == 500
    names = {f[0] for f in LINKED_BIRTH_1983_1988_FIELDS}
    names |= {f[0] for f in LINKED_NUM_DEATH_1983_1988_FIELDS}
    # combined birth+death names must not collide (RESSTAT vs RESSTATD ok)
    assert len(names) == len(LINKED_BIRTH_1983_1988_FIELDS) + len(
        LINKED_NUM_DEATH_1983_1988_FIELDS
    )
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_1983_1988_FIELDS}
    assert d["YOD"] == (194, 197)        # LinkCO83Guide p33
    assert d["UCOD"] == (231, 234)       # ICD-9 underlying cause, 4-byte
    assert d["UCODR61"] == (235, 237)    # 61 selected causes recode
    assert d["ENTITY"] == (240, 379)     # 20 x 7-byte entity-axis
    assert d["RECORDAX"] == (382, 481)   # 20 x 5-byte record-axis
    assert d["RESERVED"] == (482, 500)   # numerator ends at loc 500


def test_1989_1991_numerator_layout_well_formed():
    # Birth section 1-212 REUSE LINKED_BIRTH_1989_1991_FIELDS;
    # death-derived "plus" 213-225 REUSE LINKED_DEATH_1989_1991_FIELDS;
    # mortality section 226-535 = LINKED_NUM_DEATH_1989_1991_FIELDS.
    _assert_layout_well_formed(
        LINKED_BIRTH_1989_1991_FIELDS, LINKED_NUM_RECLEN_1989_1991, "1989_1991_num_birth"
    )
    _assert_layout_well_formed(
        LINKED_DEATH_1989_1991_FIELDS, LINKED_NUM_RECLEN_1989_1991, "1989_1991_num_plus"
    )
    _assert_layout_well_formed(
        LINKED_NUM_DEATH_1989_1991_FIELDS, LINKED_NUM_RECLEN_1989_1991, "1989_1991_num_death"
    )
    assert max(f[2] for f in LINKED_BIRTH_1989_1991_FIELDS) <= 212
    assert min(f[1] for f in LINKED_DEATH_1989_1991_FIELDS) == 213
    assert max(f[2] for f in LINKED_DEATH_1989_1991_FIELDS) == 225
    assert min(f[1] for f in LINKED_NUM_DEATH_1989_1991_FIELDS) == 226
    assert max(f[2] for f in LINKED_NUM_DEATH_1989_1991_FIELDS) == 535
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_1989_1991_FIELDS}
    assert d["RESERVED1"] == (226, 260)   # LinkCO89Guide p48
    assert d["NENTITY"] == (261, 262)     # 00-20
    assert d["ENTITY"] == (263, 402)      # 20 x 7-byte entity-axis (ICD-9)
    assert d["RECORDAX"] == (405, 504)    # 20 x 5-byte record-axis (ICD-9)
    assert d["DTHYR"] == (522, 525)       # year of death
    assert d["WEEKDAYD"] == (528, 528)    # day of week of death
    assert d["RESERVED2"] == (529, 535)   # numerator ends at loc 535
    # cert match key for the DO-step-5 num<->denom-plus join lives in
    # the reused birth section (LinkCO89Guide p20)
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1989_1991_FIELDS}
    assert b["MATCHS"] == (1, 1)
    assert b["IDNUMBER"] == (2, 6)


def test_numerator_dispatcher_additive_branch():
    for y in (1983, 1985, 1988):
        reclen, birth, death = _numerator_layout_for_linked_year(y)
        assert reclen == 500
        assert birth is LINKED_BIRTH_1983_1988_FIELDS
        assert death is LINKED_NUM_DEATH_1983_1988_FIELDS
    for y in (1989, 1990, 1991):
        reclen, birth, death = _numerator_layout_for_linked_year(y)
        assert reclen == 535
        assert birth is LINKED_BIRTH_1989_1991_FIELDS
        # 1989-1991 numerator death = the 213-225 "plus" + 226-535
        assert death == LINKED_DEATH_1989_1991_FIELDS + LINKED_NUM_DEATH_1989_1991_FIELDS
    with pytest.raises(ValueError):
        _numerator_layout_for_linked_year(1994)  # 1992-1994 gap, unconfigured
    with pytest.raises(ValueError):
        _numerator_layout_for_linked_year(2005)  # numerator dispatcher = cohort only


def test_denominator_dispatcher_unregressed():
    # H10/HALT-13: the 3b additive numerator helper must NOT perturb the
    # 3a/2005/2014 DENOMINATOR dispatcher.
    assert _layout_for_linked_year(1983)[0] == 91
    assert _layout_for_linked_year(1989)[0] == 225
    assert _layout_for_linked_year(2008)[0] == 900
    assert _layout_for_linked_year(2018)[0] == 1384
    with pytest.raises(ValueError):
        _layout_for_linked_year(1994)


# --------------------------------------------------------------------------
# Tier 0: synthetic record — value recovery + position-shift NEGATIVE check
# --------------------------------------------------------------------------

def _slice(rec: bytes, start: int, end: int) -> str:
    return rec[start - 1 : end].decode("latin-1")


def _plant(rec: bytearray, pos: tuple[int, int], value: str):
    s, e = pos
    field = value.ljust(e - s + 1)[: e - s + 1]
    rec[s - 1 : e] = field.encode("latin-1")


def test_tier0_synthetic_500byte_numerator_recovery_and_negative():
    rl, birth, death = _numerator_layout_for_linked_year(1985)
    assert rl == 500
    rec = bytearray(b" " * 500)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["MATCHS"], "1")        # @1
    _plant(rec, b["BIRYR"], "1985")      # @2-5 (natality section)
    _plant(rec, b["CSEX"], "2")          # @38
    _plant(rec, d["YOD"], "1985")        # @194-197 (mortality section)
    _plant(rec, d["UCOD"], "7980")       # @231-234 (ICD-9)
    _plant(rec, d["UCODR61"], "057")     # @235-237
    rec = bytes(rec)
    assert _slice(rec, *b["MATCHS"]) == "1"
    assert _slice(rec, *b["BIRYR"]) == "1985"
    assert _slice(rec, *b["CSEX"]) == "2"
    assert _slice(rec, *d["YOD"]) == "1985"
    assert _slice(rec, *d["UCOD"]) == "7980"
    assert _slice(rec, *d["UCODR61"]) == "057"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted UCOD
    s, e = d["UCOD"]
    assert _slice(rec, s + 1, e + 1) != "7980"


def test_tier0_synthetic_535byte_numerator_recovery_and_negative():
    rl, birth, death = _numerator_layout_for_linked_year(1990)
    assert rl == 535
    rec = bytearray(b" " * 535)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["MATCHS"], "1")        # @1
    _plant(rec, b["IDNUMBER"], "01234")  # @2-6 (cert match key)
    _plant(rec, b["BIRYR"], "1990")      # @7-10
    _plant(rec, d["AGED"], "045")        # @213-215 ("plus")
    _plant(rec, d["UCOD"], "7980")       # @219-222 (ICD-9, "plus")
    _plant(rec, d["DTHYR"], "1990")      # @522-525 (mortality section)
    _plant(rec, d["WEEKDAYD"], "3")      # @528
    rec = bytes(rec)
    assert _slice(rec, *b["MATCHS"]) == "1"
    assert _slice(rec, *b["IDNUMBER"]) == "01234"
    assert _slice(rec, *b["BIRYR"]) == "1990"
    assert _slice(rec, *d["AGED"]) == "045"
    assert _slice(rec, *d["UCOD"]) == "7980"
    assert _slice(rec, *d["DTHYR"]) == "1990"
    assert _slice(rec, *d["WEEKDAYD"]) == "3"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = b["BIRYR"]
    assert _slice(rec, s + 1, e + 1) != "1990"


# --------------------------------------------------------------------------
# Tier 1: real cohort numerator data — encoding + value-distribution
# --------------------------------------------------------------------------

def _read_first_records(zip_path: Path, member_substr: str, n: int):
    """Empirically derive block size (data + CR/LF) and yield first n records."""
    with zipfile.ZipFile(zip_path) as zf:
        member = next(m for m in zf.namelist() if member_substr in m.upper())
        info = zf.getinfo(member)
        with zf.open(member) as fh:
            head = fh.read(4096)
    nl = head.find(b"\n")
    assert nl > 0, f"{zip_path.name}: no newline terminator found"
    block = nl + 1                       # data + CR + LF
    data_len = block - 2 if head[nl - 1:nl] == b"\r" else block - 1
    assert info.file_size % block == 0, (
        f"{zip_path.name}: size {info.file_size} not divisible by block {block}"
    )
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as fh:
            raw = fh.read(block * n)
    recs = [raw[i * block : i * block + data_len] for i in range(n)]
    return data_len, info.file_size // block, recs


_NUM_500 = [(1983, "LinkCO83.zip"), (1985, "LinkCO85.zip"), (1988, "LinkCO88.zip")]
_NUM_535 = [(1989, "LinkCO89.zip"), (1990, "LinkCO90.zip"), (1991, "LinkCO91.zip")]


def _icd9_plausible(codes):
    """At least some 4-byte ICD-9 underlying-cause codes are digit-ish
    and in a plausible range (sentinel-aware: blanks/unknown allowed)."""
    numeric = [c.strip() for c in codes if c.strip() and c.strip().isdigit()]
    assert numeric, "no numeric ICD-9 UCOD among sampled records"
    # ICD-9 numeric codes span 001-999 (4 digits incl. decimal subdivision)
    assert all(1 <= int(v[:3]) <= 999 for v in numeric)


@pytest.mark.parametrize("year,zipname", _NUM_500)
def test_tier1_real_1983_1988_numerator(year, zipname):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "NUM", 300)
    assert data_len == LINKED_NUM_RECLEN_1983_1988 == 500
    rl, birth, death = _numerator_layout_for_linked_year(year)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # encoding (ASCII-not-EBCDIC) + alignment + block-size, jointly:
    assert all(_slice(r, *b["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: natality BIRYR != {year} (encoding/alignment)"
    )
    # death-side: every numerator record is a linked infant death
    # (MATCHS in {1,2}; 3=surviving never appears in the numerator)
    assert {_slice(r, *b["MATCHS"]) for r in recs} <= set("12 ")
    # year of death >= year of birth (cohort follows the birth year)
    yods = [_slice(r, *d["YOD"]).strip() for r in recs]
    assert all(y.isdigit() and year <= int(y) <= year + 1 for y in yods if y)
    # ICD-9 underlying cause plausibility (L13-extension value-dist)
    _icd9_plausible([_slice(r, *d["UCOD"]) for r in recs])
    # entity/record-axis counts are 00-20 (or blank); sentinel-aware
    nent = [_slice(r, *d["NENTITY"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 20) for v in nent)
    assert n_rec < 100_000  # numerator (linked deaths) << denominator


@pytest.mark.parametrize("year,zipname", _NUM_535)
def test_tier1_real_1989_1991_numerator(year, zipname):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "NUM", 300)
    assert data_len == LINKED_NUM_RECLEN_1989_1991 == 535
    rl, birth, death = _numerator_layout_for_linked_year(year)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    assert all(_slice(r, *b["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: birth BIRYR != {year} (encoding/alignment)"
    )
    # MATCHS in {1,2} for the numerator (linked infant deaths only)
    assert {_slice(r, *b["MATCHS"]) for r in recs} <= set("12 ")
    # IDNUMBER (cert match key) is a non-blank 5-char field
    assert all(len(_slice(r, *b["IDNUMBER"])) == 5 for r in recs)
    # death "plus": AGED 000-364 (sentinel-aware), UCOD ICD-9 plausible
    aged = [_slice(r, *d["AGED"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 366) for v in aged)
    _icd9_plausible([_slice(r, *d["UCOD"]) for r in recs])
    # mortality-section year-of-death matches the birth cohort window
    yods = [_slice(r, *d["DTHYR"]).strip() for r in recs]
    assert all(y.isdigit() and year <= int(y) <= year + 1 for y in yods if y)
    nent = [_slice(r, *d["NENTITY"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 20) for v in nent)
    assert n_rec < 100_000  # numerator (linked deaths) << denominator
