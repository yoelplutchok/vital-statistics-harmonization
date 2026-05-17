"""DESIGN: tracks-current-state

C8.18 DO step 4a SMOKE — 1995-2002 cohort linked layout (230-byte
Denominator-PLUS + 535-byte Numerator).

Sibling of ``test_linked_cohort_1983_1991_layout_smoke.py`` (3a) +
``test_linked_cohort_1983_1991_numerator_smoke.py`` (3b); kept
separate so each sub-step stays independently re-runnable (C8.17
DO5a/5b + C8.18 DO3a/3b sub-step-isolation precedent).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
of the additive ``field_specs.py`` 1995-2002 layouts (record-length
constants = the documented fixed-width contract, byte-exact-confirmed
against the guide-stated counts; contiguity + in-bounds + non-overlap;
the den-plus + numerator section boundaries; the additive den-plus +
numerator dispatcher branches; the 3a/3b/2005/2014 dispatchers
unregressed — H10/HALT-13) plus, on the real SHA-anchored cohort zips,
value-distribution + encoding invariants (L13-extension: byte position
alone is not trusted; the C8.18 DO3a SMOKE-Tier-1 catch is the
governing precedent). No mutable annotation value is pinned (record
lengths 230 / 535 are fixed historical NCHS facts).

Tier 0 (synthetic, always runs): hand-built den-plus (230) + numerator
(535) records with planted values at documented positions + a
position-shift NEGATIVE check (L3: proves the slicing discriminates
position, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip
absent): first records of LinkCO{95,98,99,02}US{Den,Num}.dat spanning
the 1998->1999 ICD-9->ICD-10 boundary — empirical block size =
reclen + CR/LF (FIX_LOG 2026-05-14 L13 arithmetic-class defense),
ASCII-decodability, BIRYR == cohort year for every sampled record,
MATCHS domain (den-plus {1,2}, numerator {1}), RECWT format, AGED /
EANUM / DTHYR plausibility, and the decisive within-era UCOD
value-domain split (numeric ICD-9 1995-98 vs alpha ICD-10 1999-2002
at the SAME byte position 216-219 — the record length is constant
across the boundary, proving one shared byte layout).
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
    LINKED_BIRTH_1995_2002_FIELDS,
    LINKED_DEATH_1995_2002_FIELDS,
    LINKED_DENOMPLUS_RECLEN_1995_2002,
    LINKED_NUM_DEATH_1995_2002_FIELDS,
    LINKED_NUM_RECLEN_1995_2002,
)
from parse_linked_year import (  # noqa: E402
    _layout_for_linked_year,
    _numerator_layout_for_linked_year,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# SHAPE: structural invariants of the 1995-2002 layout substrate
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


def test_reclen_constants_are_documented_record_lengths():
    # 230 / 535 are NCHS-guide-documented fixed-width record lengths
    # (LinkCO95Guide p15-16 Den 230 / Num 535; LinkCO99Guide p16-17
    # byte-identical for the ICD-10 1999-2002 sub-era). Byte-exact-
    # confirmed at the C8.18 DO step 4 PRE-FLIGHT (LinkCO95USDen.dat
    # 905,498,784 / 232 = 3,903,012 = guide count). Fixed historical
    # facts (not a mutable annotation pin).
    assert LINKED_DENOMPLUS_RECLEN_1995_2002 == 230
    assert LINKED_NUM_RECLEN_1995_2002 == 535


def test_denplus_layout_contiguous_and_well_formed():
    # Den-plus (230) = birth section 1-210 (LINKED_BIRTH_1995_2002) +
    # death "plus" 211-230 (LINKED_DEATH_1995_2002). Both contiguous;
    # together they tile [1,230] with no gap/overlap.
    _assert_layout_well_formed(
        LINKED_BIRTH_1995_2002_FIELDS, LINKED_DENOMPLUS_RECLEN_1995_2002, "1995_2002_birth"
    )
    _assert_layout_well_formed(
        LINKED_DEATH_1995_2002_FIELDS, LINKED_DENOMPLUS_RECLEN_1995_2002, "1995_2002_plus"
    )
    assert LINKED_BIRTH_1995_2002_FIELDS[0][:2] == ("MATCHS", 1)        # loc 1
    assert min(f[1] for f in LINKED_BIRTH_1995_2002_FIELDS) == 1
    assert max(f[2] for f in LINKED_BIRTH_1995_2002_FIELDS) == 210      # birth ends @210
    assert min(f[1] for f in LINKED_DEATH_1995_2002_FIELDS) == 211      # "plus" starts @211
    assert max(f[2] for f in LINKED_DEATH_1995_2002_FIELDS) == 230      # den-plus ends @230
    # the combined den-plus tiles [1,230] exactly (no gap, no overlap)
    combined = sorted(
        LINKED_BIRTH_1995_2002_FIELDS + LINKED_DEATH_1995_2002_FIELDS, key=lambda f: f[1]
    )
    assert combined[0][1] == 1 and combined[-1][2] == 230
    for prev, cur in zip(combined, combined[1:]):
        assert cur[1] == prev[2] + 1, f"den-plus not contiguous: {prev} then {cur}"
    # anchors verified byte-exact vs the LinkCO95Guide DETAIL
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1995_2002_FIELDS}
    assert b["IDNUMBER"] == (2, 6)        # num<->denom-plus join key (p20)
    assert b["BIRYR"] == (7, 10)
    assert b["DBIRWT"] == (81, 84)        # grams (NOT 79-82 — 1989-1991 reuse FALSIFIED)
    assert b["CSEX"] == (79, 79)
    assert b["DPLURAL"] == (89, 89)
    d = {f[0]: (f[1], f[2]) for f in LINKED_DEATH_1995_2002_FIELDS}
    assert d["AGED"] == (211, 213)
    assert d["UCOD"] == (216, 219)        # ICD-9 1995-98 / ICD-10 1999-2002
    assert d["UCODR"] == (220, 222)
    assert d["RECWT"] == (223, 230)       # den-plus ends here


def test_numerator_layout_contiguous_and_well_formed():
    # Numerator (535) = birth 1-210 + death "plus" 211-230 (REUSE the
    # den-plus specs) + numerator-only mortality 231-535.
    _assert_layout_well_formed(
        LINKED_NUM_DEATH_1995_2002_FIELDS, LINKED_NUM_RECLEN_1995_2002, "1995_2002_num_death"
    )
    assert min(f[1] for f in LINKED_NUM_DEATH_1995_2002_FIELDS) == 231
    assert max(f[2] for f in LINKED_NUM_DEATH_1995_2002_FIELDS) == 535
    # full numerator tiles [1,535] exactly
    full = sorted(
        LINKED_BIRTH_1995_2002_FIELDS
        + LINKED_DEATH_1995_2002_FIELDS
        + LINKED_NUM_DEATH_1995_2002_FIELDS,
        key=lambda f: f[1],
    )
    assert full[0][1] == 1 and full[-1][2] == 535
    for prev, cur in zip(full, full[1:]):
        assert cur[1] == prev[2] + 1, f"numerator not contiguous: {prev} then {cur}"
    names = [f[0] for f in full]
    assert len(names) == len(set(names)), "numerator field-name collision"
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_1995_2002_FIELDS}
    assert d["RESERVED1"] == (231, 260)   # reserved gap RECWT@230 -> MULTCOND@261
    assert d["EANUM"] == (261, 262)       # 00-20
    assert d["ENTITY"] == (263, 402)      # 20 x 7-byte entity-axis
    assert d["RECORD"] == (405, 504)      # 20 x 5-byte record-axis
    assert d["DTHYR"] == (524, 527)       # year of death (NOT 522-525 = 1989-1991)
    assert d["WEEKDAYD"] == (532, 532)
    assert d["R9"] == (533, 535)          # numerator ends at 535


def test_denominator_dispatcher_additive_branch():
    for y in (1995, 1998, 1999, 2002):
        reclen, birth, death = _layout_for_linked_year(y)
        assert reclen == 230
        assert birth is LINKED_BIRTH_1995_2002_FIELDS
        assert death is LINKED_DEATH_1995_2002_FIELDS
    # 1992-1994 = permanent NCHS linkage gap (unconfigured)
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _layout_for_linked_year(y)


def test_numerator_dispatcher_additive_branch():
    for y in (1995, 1998, 1999, 2002):
        reclen, birth, death = _numerator_layout_for_linked_year(y)
        assert reclen == 535
        assert birth is LINKED_BIRTH_1995_2002_FIELDS
        # numerator death = den-plus "plus" 211-230 + mortality 231-535
        assert death == LINKED_DEATH_1995_2002_FIELDS + LINKED_NUM_DEATH_1995_2002_FIELDS
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _numerator_layout_for_linked_year(y)
    with pytest.raises(ValueError):
        _numerator_layout_for_linked_year(2005)  # numerator dispatcher = cohort only


def test_prior_substep_dispatchers_unregressed():
    # H10/HALT-13: the 4a additive 1995-2002 branches must NOT perturb
    # the 3a/3b/2005/2014 dispatcher returns.
    assert _layout_for_linked_year(1983)[0] == 91
    assert _layout_for_linked_year(1989)[0] == 225
    assert _layout_for_linked_year(2008)[0] == 900
    assert _layout_for_linked_year(2018)[0] == 1384
    assert _numerator_layout_for_linked_year(1985)[0] == 500
    assert _numerator_layout_for_linked_year(1990)[0] == 535


# --------------------------------------------------------------------------
# Tier 0: synthetic record — value recovery + position-shift NEGATIVE check
# --------------------------------------------------------------------------

def _slice(rec: bytes, start: int, end: int) -> str:
    return rec[start - 1 : end].decode("latin-1")


def _plant(rec: bytearray, pos: tuple[int, int], value: str):
    s, e = pos
    field = value.ljust(e - s + 1)[: e - s + 1]
    rec[s - 1 : e] = field.encode("latin-1")


def test_tier0_synthetic_230byte_denplus_recovery_and_negative():
    rl, birth, death = _layout_for_linked_year(1996)
    assert rl == 230
    rec = bytearray(b" " * 230)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["MATCHS"], "2")          # @1 surviving infant
    _plant(rec, b["IDNUMBER"], "01234")    # @2-6
    _plant(rec, b["BIRYR"], "1996")        # @7-10
    _plant(rec, b["DBIRWT"], "3402")       # @81-84 grams
    _plant(rec, b["CSEX"], "1")            # @79
    _plant(rec, d["RECWT"], "1.000000")    # @223-230
    rec = bytes(rec)
    assert _slice(rec, *b["MATCHS"]) == "2"
    assert _slice(rec, *b["IDNUMBER"]) == "01234"
    assert _slice(rec, *b["BIRYR"]) == "1996"
    assert _slice(rec, *b["DBIRWT"]) == "3402"
    assert _slice(rec, *b["CSEX"]) == "1"
    assert _slice(rec, *d["RECWT"]) == "1.000000"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = b["BIRYR"]
    assert _slice(rec, s + 1, e + 1) != "1996"


def test_tier0_synthetic_535byte_numerator_recovery_and_negative():
    rl, birth, death = _numerator_layout_for_linked_year(2001)
    assert rl == 535
    rec = bytearray(b" " * 535)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["MATCHS"], "1")          # @1 matched infant death
    _plant(rec, b["BIRYR"], "2001")        # @7-10
    _plant(rec, d["AGED"], "045")          # @211-213 ("plus")
    _plant(rec, d["UCOD"], "P073")         # @216-219 ICD-10
    _plant(rec, d["EANUM"], "03")          # @261-262 (mortality section)
    _plant(rec, d["DTHYR"], "2001")        # @524-527
    _plant(rec, d["WEEKDAYD"], "4")        # @532
    rec = bytes(rec)
    assert _slice(rec, *b["MATCHS"]) == "1"
    assert _slice(rec, *b["BIRYR"]) == "2001"
    assert _slice(rec, *d["AGED"]) == "045"
    assert _slice(rec, *d["UCOD"]) == "P073"
    assert _slice(rec, *d["EANUM"]) == "03"
    assert _slice(rec, *d["DTHYR"]) == "2001"
    assert _slice(rec, *d["WEEKDAYD"]) == "4"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted UCOD
    s, e = d["UCOD"]
    assert _slice(rec, s + 1, e + 1) != "P073"


# --------------------------------------------------------------------------
# Tier 1: real cohort data — encoding + value-distribution + ICD boundary
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


# (cohort, zip, is_icd10) — spans the 1998->1999 ICD-9->ICD-10 boundary
# + 2002 (uppercase members LinkCO02US{DEN,NUM}.dat)
_COHORTS = [
    (1995, "LinkCO95US.zip", False),
    (1998, "LinkCO98US.zip", False),
    (1999, "LinkCO99US.zip", True),
    (2002, "LinkCO02US.zip", True),
]


@pytest.mark.parametrize("year,zipname,is_icd10", _COHORTS)
def test_tier1_real_denplus(year, zipname, is_icd10):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "DEN", 300)
    assert data_len == LINKED_DENOMPLUS_RECLEN_1995_2002 == 230
    rl, birth, death = _layout_for_linked_year(year)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # encoding (ASCII-not-EBCDIC) + alignment + block size, jointly:
    assert all(_slice(r, *b["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: den-plus BIRYR != {year} (encoding/alignment)"
    )
    # den-plus carries surviving infants + matched deaths; MATCHS in
    # {1,2} (3=unmatched is unlinked-file-only); never empty
    ms = {_slice(r, *b["MATCHS"]) for r in recs}
    assert ms <= {"1", "2"}, f"{zipname}: den-plus MATCHS domain {ms}"
    assert "2" in ms, f"{zipname}: expected surviving (MATCHS=2) in den-plus"
    # birthweight numeric grams (sentinel 9999=NS allowed); 1989-1991
    # reuse FALSIFIED -> DBIRWT must be 4 digits at 81-84, not '1 05'
    dbw = [_slice(r, *b["DBIRWT"]).strip() for r in recs]
    assert all(v.isdigit() and len(v) == 4 for v in dbw), (
        f"{zipname}: DBIRWT@81-84 not 4-digit grams (layout/reuse-falsification)"
    )
    assert any(200 <= int(v) <= 9000 for v in dbw)  # plausible live-birth grams
    # surviving live births weighted exactly 1.0 (LinkCO95Guide p51)
    assert all(_slice(r, *d["RECWT"]).startswith("1.") for r in recs)
    assert any(_slice(r, *d["RECWT"]) == "1.000000" for r in recs)
    assert n_rec > 1_000_000  # den-plus = one row per birth (millions)


@pytest.mark.parametrize("year,zipname,is_icd10", _COHORTS)
def test_tier1_real_numerator_and_icd_boundary(year, zipname, is_icd10):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "NUM", 300)
    assert data_len == LINKED_NUM_RECLEN_1995_2002 == 535
    rl, birth, death = _numerator_layout_for_linked_year(year)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    assert all(_slice(r, *b["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: numerator BIRYR != {year} (encoding/alignment)"
    )
    # numerator = linked infant deaths only -> MATCHS == 1 for all
    assert {_slice(r, *b["MATCHS"]) for r in recs} == {"1"}, (
        f"{zipname}: numerator MATCHS must be all 1 (linked infant deaths)"
    )
    # cert match key is a non-blank 5-char field
    assert all(_slice(r, *b["IDNUMBER"]).strip() for r in recs)
    # AGED 000-364 (sentinel-aware)
    aged = [_slice(r, *d["AGED"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 366) for v in aged)
    # entity/record-axis counts 00-20 (sentinel-aware)
    for fld in ("EANUM", "RANUM"):
        cnts = [_slice(r, *d[fld]).strip() for r in recs]
        assert all((not v) or (v.isdigit() and 0 <= int(v) <= 20) for v in cnts)
    # year of death within the cohort window [cohort, cohort+1]
    yods = [_slice(r, *d["DTHYR"]).strip() for r in recs]
    assert all(y.isdigit() and year <= int(y) <= year + 1 for y in yods if y)
    assert all(1 <= int(_slice(r, *d["DTHMON"])) <= 12 for r in recs)
    # DECISIVE within-era value-domain check (L13-extension): the SAME
    # byte position 216-219 holds numeric ICD-9 (1995-98) vs alpha
    # ICD-10 (1999-2002); the record length is constant across the
    # boundary -> one shared byte layout, only the UCOD domain changes.
    ucods = [_slice(r, *d["UCOD"]).strip() for r in recs if _slice(r, *d["UCOD"]).strip()]
    assert ucods, f"{zipname}: no non-blank UCOD among sampled deaths"
    if is_icd10:
        # ICD-10: first char is a letter (A00-Z99)
        assert sum(c[0].isalpha() for c in ucods) >= 0.8 * len(ucods), (
            f"{zipname}: expected ICD-10 alpha UCOD (sample {ucods[:5]})"
        )
    else:
        # ICD-9: numeric (001-999, no leading 'E' letter in these positions)
        assert sum(c[:3].isdigit() for c in ucods) >= 0.8 * len(ucods), (
            f"{zipname}: expected ICD-9 numeric UCOD (sample {ucods[:5]})"
        )
    assert n_rec < 200_000  # numerator (linked deaths) << den-plus
