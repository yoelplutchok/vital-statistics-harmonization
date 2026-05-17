"""DESIGN: tracks-current-state

C8.18 DO step 4c SMOKE — 2004 cohort linked layout (900-byte
Denominator-PLUS + 1259-byte Numerator; 2003-revision transition
continued).

Sibling of ``test_linked_cohort_2003_layout_smoke.py`` (4b) +
``test_linked_cohort_1995_2002_layout_smoke.py`` (4a) + the 3a/3b
cohort smokes; kept separate so each sub-step stays independently
re-runnable (C8.17 DO5a/5b + C8.18 DO3a/3b/4a/4b sub-step-isolation
precedent).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
of the additive ``field_specs.py`` 2004 layouts (record-length
constants = the documented fixed-width contract, byte-exact-confirmed
against the LinkCO04Guide p18 File Characteristics + the zip-member
uncompressed-size arithmetic; contiguity + in-bounds + non-overlap;
the den-plus + numerator section boundaries; the additive single-year
2004 dispatcher branches; the 3a/3b/4a/4b/2005/2014 dispatchers
unregressed — H10/HALT-13) plus, on the real SHA-anchored cohort zip,
value-distribution + encoding invariants (L13-extension: byte position
alone is not trusted; the C8.18 DO3a SMOKE-Tier-1 catch is the
governing precedent). No mutable annotation value is pinned (record
lengths 900 / 1259 are fixed historical NCHS facts).

TWO L13-extension findings resolved at the DO step 4c Convention-3
snapshot (both were non-binding RECEIPTS/C8.18_step4b forward-looking
extrapolations/hypotheses explicitly flagged for value-verification):
the receipt-note "2004 = 900/1142" extrapolation was FALSIFIED ->
numerator 1259 (LinkCO04Guide p18 + exact zip-member arithmetic:
27,763 x (1259+2 CRLF) = 35,009,143 = VS04LKBC.USNUMPUB ; 4,118,956 x
(900+2) = 3,715,298,312 = VS04LKBC.DUSDENOM); and the "2004 den-plus
== LINKED_BIRTH_2005_2013" hypothesis was FALSIFIED -> the 2003-rev
*cohort* layout (FILLER@1-6 + REVISION@7 + IDNUMBER@10-14, diverging
from LINKED_BIRTH_2003 at ~576 onward). The SHAPE tests below pin the
corrected 900/1259.

Tier 0 (synthetic, always runs): hand-built den-plus (900) +
numerator (1259) records with planted values at documented positions
+ a position-shift NEGATIVE check (L3: proves the slicing
discriminates position, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): first records of VS04LKBC.DUSDENOM / VS04LKBC.USNUMPUB read
via stdlib ``zipfile`` (LinkCO04US.zip members are DEFLATE — stdlib
decompresses; NO DEFLATE64 / 7z needed, unlike the single cohort
year 2003). Empirical block size = reclen + CR/LF (FIX_LOG
2026-05-14 L13 arithmetic-class defense), ASCII-decodability,
DOB_YY == 2004 for every sampled record, FLGND domain (den-plus
{1,2}, numerator {1}), RECWT format, BRTHWGT 4-digit grams, AGED /
EANUM plausibility, ICD-10 alpha UCOD (2004 cohort = all ICD-10),
and DTHYR in [2004, 2005].
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
    LINKED_BIRTH_2004_FIELDS,
    LINKED_DEATH_2004_FIELDS,
    LINKED_DENOMPLUS_RECLEN_2004,
    LINKED_NUM_DEATH_2004_FIELDS,
    LINKED_NUM_RECLEN_2004,
)
from parse_linked_year import (  # noqa: E402
    _layout_for_linked_year,
    _numerator_layout_for_linked_year,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
ZIP_2004 = LINKED_RAW_DIR / "LinkCO04US.zip"


# --------------------------------------------------------------------------
# SHAPE: structural invariants of the 2004 layout substrate
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
    # 900 / 1259 are NCHS-guide-documented fixed-width record lengths
    # (LinkCO04Guide p18 File Characteristics: Denominator US 900 /
    # Numerator US 1259). Byte-exact-confirmed via the zip-member
    # uncompressed-size arithmetic: 4,118,956 x (900+2) = 3,715,298,312
    # = VS04LKBC.DUSDENOM; 27,763 x (1259+2) = 35,009,143 =
    # VS04LKBC.USNUMPUB. The receipt-note "1142" extrapolation was
    # FALSIFIED. Fixed historical facts (not a mutable annotation pin).
    assert LINKED_DENOMPLUS_RECLEN_2004 == 900
    assert LINKED_NUM_RECLEN_2004 == 1259


def test_denplus_layout_contiguous_and_well_formed():
    # Den-plus (900) = birth section 1-867 (LINKED_BIRTH_2004) + death
    # "plus" 868-900 (LINKED_DEATH_2004). Both contiguous; together
    # they tile [1,900] with no gap/overlap.
    _assert_layout_well_formed(
        LINKED_BIRTH_2004_FIELDS, LINKED_DENOMPLUS_RECLEN_2004, "2004_birth"
    )
    _assert_layout_well_formed(
        LINKED_DEATH_2004_FIELDS, LINKED_DENOMPLUS_RECLEN_2004, "2004_plus"
    )
    assert min(f[1] for f in LINKED_BIRTH_2004_FIELDS) == 1
    assert max(f[2] for f in LINKED_BIRTH_2004_FIELDS) == 867     # birth ends @867
    assert min(f[1] for f in LINKED_DEATH_2004_FIELDS) == 868     # "plus" starts @868
    assert max(f[2] for f in LINKED_DEATH_2004_FIELDS) == 900     # den-plus ends @900
    combined = sorted(
        LINKED_BIRTH_2004_FIELDS + LINKED_DEATH_2004_FIELDS, key=lambda f: f[1]
    )
    assert combined[0][1] == 1 and combined[-1][2] == 900
    for prev, cur in zip(combined, combined[1:]):
        assert cur[1] == prev[2] + 1, f"den-plus not contiguous: {prev} then {cur}"
    # anchors verified byte-exact vs the LinkCO04Guide DETAIL (pp21-57)
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_2004_FIELDS}
    assert b["REVISION"] == (7, 7)        # S=1989-unrev / A=2003-rev
    assert b["IDNUMBER"] == (10, 14)      # num<->den-plus join key (p18)
    assert b["DOB_YY"] == (15, 18)        # birth year (== 2004)
    assert b["DPLURAL"] == (423, 423)
    assert b["SEX"] == (436, 436)
    assert b["BRTHWGT"] == (467, 470)     # grams (2003-sibling DBWT; same pos)
    assert b["COMBGEST"] == (451, 452)
    assert b["MRACE1E"] == (800, 802)     # relocated vs 2003 @683 (2004 divergence)
    d = {f[0]: (f[1], f[2]) for f in LINKED_DEATH_2004_FIELDS}
    assert d["FLGND"] == (868, 868)       # 2004: @868 (== 2005-2013 model; NOT @751 = 2003)
    assert d["AGED"] == (872, 874)
    assert d["UCOD"] == (884, 887)        # ICD-10 (2004 cohort all ICD-10)
    assert d["UCODR130"] == (889, 891)
    assert d["RECWT"] == (893, 900)       # den-plus ends here


def test_numerator_layout_contiguous_and_well_formed():
    # Numerator (1259) = birth 1-867 + death "plus" 868-900 (REUSE the
    # den-plus specs) + numerator-only mortality 901-1259.
    _assert_layout_well_formed(
        LINKED_NUM_DEATH_2004_FIELDS, LINKED_NUM_RECLEN_2004, "2004_num_death"
    )
    assert min(f[1] for f in LINKED_NUM_DEATH_2004_FIELDS) == 901
    assert max(f[2] for f in LINKED_NUM_DEATH_2004_FIELDS) == 1259
    full = sorted(
        LINKED_BIRTH_2004_FIELDS
        + LINKED_DEATH_2004_FIELDS
        + LINKED_NUM_DEATH_2004_FIELDS,
        key=lambda f: f[1],
    )
    assert full[0][1] == 1 and full[-1][2] == 1259
    for prev, cur in zip(full, full[1:]):
        assert cur[1] == prev[2] + 1, f"numerator not contiguous: {prev} then {cur}"
    names = [f[0] for f in full]
    assert len(names) == len(set(names)), "numerator field-name collision"
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_2004_FIELDS}
    assert d["EANUM"] == (903, 904)       # 00-20
    assert d["ENTITY"] == (905, 1044)     # 20 x 7-byte entity-axis
    assert d["RANUM"] == (1047, 1048)     # 00-20
    assert d["RECORD"] == (1049, 1148)    # 20 x 5-byte record-axis
    assert d["DTHYR"] == (1188, 1191)     # year of death (cohort..+1)
    assert d["DOD_MM"] == (1258, 1259)    # numerator ends @1259


def test_denominator_dispatcher_additive_branch():
    reclen, birth, death = _layout_for_linked_year(2004)
    assert reclen == 900
    assert birth is LINKED_BIRTH_2004_FIELDS
    assert death is LINKED_DEATH_2004_FIELDS
    # 2003 (4b) + 2004 (this step) now both configured for the
    # denominator dispatcher; 1992-1994 = the permanent NCHS linkage gap
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _layout_for_linked_year(y)


def test_numerator_dispatcher_additive_branch():
    reclen, birth, death = _numerator_layout_for_linked_year(2004)
    assert reclen == 1259
    assert birth is LINKED_BIRTH_2004_FIELDS
    # numerator death = den-plus "plus" 868-900 + mortality 901-1259
    assert death == LINKED_DEATH_2004_FIELDS + LINKED_NUM_DEATH_2004_FIELDS
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _numerator_layout_for_linked_year(y)
    with pytest.raises(ValueError):
        _numerator_layout_for_linked_year(2005)  # numerator dispatcher = cohort only


def test_prior_substep_dispatchers_unregressed():
    # H10/HALT-13: the 4c additive single-year-2004 branches must NOT
    # perturb the 3a/3b/4a/4b/2005/2014 dispatcher returns.
    assert _layout_for_linked_year(1983)[0] == 91
    assert _layout_for_linked_year(1989)[0] == 225
    assert _layout_for_linked_year(1996)[0] == 230
    assert _layout_for_linked_year(2002)[0] == 230
    assert _layout_for_linked_year(2003)[0] == 783      # 4b unregressed
    assert _layout_for_linked_year(2008)[0] == 900
    assert _layout_for_linked_year(2018)[0] == 1384
    assert _numerator_layout_for_linked_year(1985)[0] == 500
    assert _numerator_layout_for_linked_year(1990)[0] == 535
    assert _numerator_layout_for_linked_year(2002)[0] == 535
    assert _numerator_layout_for_linked_year(2003)[0] == 1142   # 4b unregressed


# --------------------------------------------------------------------------
# Tier 0: synthetic record — value recovery + position-shift NEGATIVE check
# --------------------------------------------------------------------------

def _slice(rec: bytes, start: int, end: int) -> str:
    return rec[start - 1 : end].decode("latin-1")


def _plant(rec: bytearray, pos: tuple[int, int], value: str):
    s, e = pos
    field = value.ljust(e - s + 1)[: e - s + 1]
    rec[s - 1 : e] = field.encode("latin-1")


def test_tier0_synthetic_900byte_denplus_recovery_and_negative():
    rl, birth, death = _layout_for_linked_year(2004)
    assert rl == 900
    rec = bytearray(b" " * 900)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["REVISION"], "A")        # @7 2003-revised
    _plant(rec, b["IDNUMBER"], "01234")    # @10-14
    _plant(rec, b["DOB_YY"], "2004")       # @15-18
    _plant(rec, b["BRTHWGT"], "3402")      # @467-470 grams
    _plant(rec, b["SEX"], "1")             # @436
    _plant(rec, d["FLGND"], "2")           # @868 surviving infant
    _plant(rec, d["RECWT"], "1.000000")    # @893-900
    rec = bytes(rec)
    assert _slice(rec, *b["REVISION"]) == "A"
    assert _slice(rec, *b["IDNUMBER"]) == "01234"
    assert _slice(rec, *b["DOB_YY"]) == "2004"
    assert _slice(rec, *b["BRTHWGT"]) == "3402"
    assert _slice(rec, *b["SEX"]) == "1"
    assert _slice(rec, *d["FLGND"]) == "2"
    assert _slice(rec, *d["RECWT"]) == "1.000000"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = b["DOB_YY"]
    assert _slice(rec, s + 1, e + 1) != "2004"


def test_tier0_synthetic_1259byte_numerator_recovery_and_negative():
    rl, birth, death = _numerator_layout_for_linked_year(2004)
    assert rl == 1259
    rec = bytearray(b" " * 1259)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # NOTE: in the 2004 layout FLGND is @868 (LINKED_DEATH_2004, the
    # 2005-2013 model), NOT @751 like 2003 -> it lives in the `death` dict.
    _plant(rec, d["FLGND"], "1")           # @868 matched infant death
    _plant(rec, b["DOB_YY"], "2004")       # @15-18
    _plant(rec, d["AGED"], "045")          # @872-874 ("plus")
    _plant(rec, d["UCOD"], "P073")         # @884-887 ICD-10
    _plant(rec, d["EANUM"], "03")          # @903-904 (mortality section)
    _plant(rec, d["DTHYR"], "2005")        # @1188-1191
    _plant(rec, d["DOD_MM"], "06")         # @1258-1259
    rec = bytes(rec)
    assert _slice(rec, *d["FLGND"]) == "1"
    assert _slice(rec, *b["DOB_YY"]) == "2004"
    assert _slice(rec, *d["AGED"]) == "045"
    assert _slice(rec, *d["UCOD"]) == "P073"
    assert _slice(rec, *d["EANUM"]) == "03"
    assert _slice(rec, *d["DTHYR"]) == "2005"
    assert _slice(rec, *d["DOD_MM"]) == "06"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted UCOD
    s, e = d["UCOD"]
    assert _slice(rec, s + 1, e + 1) != "P073"


# --------------------------------------------------------------------------
# Tier 1: real cohort data — encoding + value-distribution (DEFLATE/zipfile)
# --------------------------------------------------------------------------

def _member(zip_path: Path, substr: str) -> str:
    # member naming is VS04LKBC.{DUSDENOM,USNUMPUB,USUNMPUB}; "DEN"
    # matches DUSDENOM, "NUM" matches USNUMPUB.
    with zipfile.ZipFile(zip_path) as zf:
        return next(m for m in zf.namelist() if substr in m.upper())


def _read_first_records(zip_path: Path, member_substr: str, n: int, reclen: int):
    """Stream first n records of a DEFLATE member via stdlib zipfile.

    LinkCO04US.zip members are DEFLATE (compress_type=8); stdlib
    ``zipfile`` decompresses directly (NO DEFLATE64 / 7z needed —
    unlike the single cohort year 2003). Block size is empirically
    derived (data + CR/LF) — the FIX_LOG 2026-05-14 L13
    arithmetic-class defense.
    """
    member = _member(zip_path, member_substr)
    block = reclen + 2  # CR + LF (confirmed at the DO step 4c PRE-FLIGHT)
    with zipfile.ZipFile(zip_path) as zf, zf.open(member) as f:
        buf = f.read(block * n)
    assert len(buf) >= block * n, f"{zip_path.name}: short read ({len(buf)} < {block*n})"
    # confirm CR/LF terminator + empirical record framing
    assert buf[reclen : reclen + 2] == b"\r\n", (
        f"{zip_path.name}: expected CR/LF at byte {reclen} (block framing)"
    )
    return [buf[i * block : i * block + reclen] for i in range(n)]


_REQUIRE = pytest.mark.skipif(
    not ZIP_2004.exists(),
    reason="raw cohort zip absent (gitignored, out-of-tree)",
)


@_REQUIRE
def test_tier1_real_denplus_2004():
    recs = _read_first_records(ZIP_2004, "DEN", 300, LINKED_DENOMPLUS_RECLEN_2004)
    rl, birth, death = _layout_for_linked_year(2004)
    assert rl == 900
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # encoding (ASCII-not-EBCDIC) + alignment + block size, jointly:
    assert all(_slice(r, *b["DOB_YY"]) == "2004" for r in recs), (
        "LinkCO04US den-plus DOB_YY != 2004 (encoding/alignment)"
    )
    # den-plus carries surviving infants + matched deaths; FLGND in
    # {1,2}; never empty
    fs = {_slice(r, *d["FLGND"]) for r in recs}
    assert fs <= {"1", "2"}, f"den-plus FLGND domain {fs}"
    assert "2" in fs, "expected surviving (FLGND=2) in den-plus"
    # REVISION flag domain (2003 transition continued): S / A
    assert {_slice(r, *b["REVISION"]) for r in recs} <= {"S", "A"}
    # birthweight numeric grams @467-470 (sentinel 9999=NS allowed)
    dbw = [_slice(r, *b["BRTHWGT"]).strip() for r in recs]
    assert all(v.isdigit() and len(v) == 4 for v in dbw), (
        "BRTHWGT@467-470 not 4-digit grams (layout)"
    )
    assert any(200 <= int(v) <= 9000 for v in dbw)  # plausible live-birth grams
    # surviving live births weighted exactly 1.0 (den-plus ends @900)
    assert all(_slice(r, *d["RECWT"]).startswith("1.") for r in recs)
    assert any(_slice(r, *d["RECWT"]) == "1.000000" for r in recs)


@_REQUIRE
def test_tier1_real_numerator_2004_icd10():
    recs = _read_first_records(ZIP_2004, "NUM", 300, LINKED_NUM_RECLEN_2004)
    rl, birth, death = _numerator_layout_for_linked_year(2004)
    assert rl == 1259
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    assert all(_slice(r, *b["DOB_YY"]) == "2004" for r in recs), (
        "LinkCO04US numerator DOB_YY != 2004 (encoding/alignment)"
    )
    # numerator = linked infant deaths only -> FLGND == 1 for all
    # (FLGND@868 is in the `death` dict for 2004, not `birth`)
    assert {_slice(r, *d["FLGND"]) for r in recs} == {"1"}, (
        "numerator FLGND must be all 1 (linked infant deaths)"
    )
    # cert match key is a non-blank 5-char field in the numerator
    assert all(_slice(r, *b["IDNUMBER"]).strip() for r in recs)
    # AGED 000-366 (sentinel-aware)
    aged = [_slice(r, *d["AGED"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 366) for v in aged)
    # entity/record-axis counts 00-20 (sentinel-aware)
    for fld in ("EANUM", "RANUM"):
        cnts = [_slice(r, *d[fld]).strip() for r in recs]
        assert all((not v) or (v.isdigit() and 0 <= int(v) <= 20) for v in cnts)
    # year of death within the cohort window [2004, 2005]
    yods = [_slice(r, *d["DTHYR"]).strip() for r in recs]
    assert all(y.isdigit() and 2004 <= int(y) <= 2005 for y in yods if y)
    assert all(1 <= int(_slice(r, *d["DOD_MM"])) <= 12 for r in recs)
    # 2004 cohort -> ALL infant deaths are ICD-10 (deaths 2004-2005);
    # UCOD@884-887 is alpha (A00-Z99), NOT numeric ICD-9 (L13-extension
    # value-domain check at the constant byte position).
    ucods = [_slice(r, *d["UCOD"]).strip() for r in recs if _slice(r, *d["UCOD"]).strip()]
    assert ucods, "no non-blank UCOD among sampled deaths"
    assert sum(c[0].isalpha() for c in ucods) >= 0.8 * len(ucods), (
        f"expected ICD-10 alpha UCOD for the 2004 cohort (sample {ucods[:5]})"
    )
