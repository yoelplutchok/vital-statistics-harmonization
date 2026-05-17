"""DESIGN: tracks-current-state

C8.18 DO step 4b SMOKE — 2003 cohort linked layout (783-byte
Denominator-PLUS + 1142-byte Numerator; 2003-revision transition).

Sibling of ``test_linked_cohort_1995_2002_layout_smoke.py`` (4a) +
the 3a/3b cohort smokes; kept separate so each sub-step stays
independently re-runnable (C8.17 DO5a/5b + C8.18 DO3a/3b/4a
sub-step-isolation precedent).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
of the additive ``field_specs.py`` 2003 layouts (record-length
constants = the documented fixed-width contract, byte-exact-confirmed
against the LinkCO03Guide p17 File Characteristics + the zip-member
uncompressed-size arithmetic; contiguity + in-bounds + non-overlap;
the den-plus + numerator section boundaries; the additive single-year
2003 dispatcher branches; the 3a/3b/4a/2005/2014 dispatchers
unregressed — H10/HALT-13) plus, on the real SHA-anchored cohort zip,
value-distribution + encoding invariants (L13-extension: byte position
alone is not trusted; the C8.18 DO3a SMOKE-Tier-1 catch is the
governing precedent). No mutable annotation value is pinned (record
lengths 783 / 1142 are fixed historical NCHS facts).

The prior C8.18 DO step 4 PRE-FLIGHT *assumption* "2003 numerator =
1259" was FALSIFIED at the DO step 4b Convention-3 snapshot: the
LinkCO03Guide p17 + exact zip-member arithmetic give 1142
(27,843 x (1142+2 CRLF) = 31,852,392 = VS03LKBC.USNUMPUB) and 783
(4,096,151 x 785 = 3,215,478,535 = VS03LKBC.USDENPUB); the SHAPE
tests below pin the corrected 783/1142.

Tier 0 (synthetic, always runs): hand-built den-plus (783) +
numerator (1142) records with planted values at documented positions
+ a position-shift NEGATIVE check (L3: proves the slicing
discriminates position, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip OR
the 7z DEFLATE64 decompressor absent): first records of
VS03LKBC.US{DEN,NUM}PUB streamed via ``7z e -so`` (LinkCO03US.zip
members are DEFLATE64 — stdlib ``zipfile`` raises NotImplementedError;
the bounded DO-step-4b tooling decision is the CLI 7z stream, NOT a
zipfile-deflate64 dependency, scoped to the single cohort year 2003).
Empirical block size = reclen + CR/LF (FIX_LOG 2026-05-14 L13
arithmetic-class defense), ASCII-decodability, DOB_YY == 2003 for
every sampled record, MATCHS domain (den-plus {1,2}, numerator {1}),
RECWT format, DBWT 4-digit grams, AGED / EANUM plausibility, ICD-10
alpha UCOD (2003 cohort = all ICD-10), and DTHYR in [2003, 2004].
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

_SPEC_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
if str(_SPEC_DIR) not in sys.path:
    sys.path.insert(0, str(_SPEC_DIR))

from field_specs import (  # noqa: E402
    LINKED_BIRTH_2003_FIELDS,
    LINKED_DEATH_2003_FIELDS,
    LINKED_DENOMPLUS_RECLEN_2003,
    LINKED_NUM_DEATH_2003_FIELDS,
    LINKED_NUM_RECLEN_2003,
)
from parse_linked_year import (  # noqa: E402
    _layout_for_linked_year,
    _numerator_layout_for_linked_year,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
ZIP_2003 = LINKED_RAW_DIR / "LinkCO03US.zip"


# --------------------------------------------------------------------------
# SHAPE: structural invariants of the 2003 layout substrate
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
    # 783 / 1142 are NCHS-guide-documented fixed-width record lengths
    # (LinkCO03Guide p17 File Characteristics: Denominator US 783 /
    # Numerator US 1142). Byte-exact-confirmed via the zip-member
    # uncompressed-size arithmetic: 4,096,151 x (783+2) = 3,215,478,535
    # = VS03LKBC.USDENPUB; 27,843 x (1142+2) = 31,852,392 =
    # VS03LKBC.USNUMPUB. The prior "1259" assumption was FALSIFIED.
    # Fixed historical facts (not a mutable annotation pin).
    assert LINKED_DENOMPLUS_RECLEN_2003 == 783
    assert LINKED_NUM_RECLEN_2003 == 1142


def test_denplus_layout_contiguous_and_well_formed():
    # Den-plus (783) = birth section 1-750 (LINKED_BIRTH_2003) + death
    # "plus" 751-783 (LINKED_DEATH_2003). Both contiguous; together
    # they tile [1,783] with no gap/overlap.
    _assert_layout_well_formed(
        LINKED_BIRTH_2003_FIELDS, LINKED_DENOMPLUS_RECLEN_2003, "2003_birth"
    )
    _assert_layout_well_formed(
        LINKED_DEATH_2003_FIELDS, LINKED_DENOMPLUS_RECLEN_2003, "2003_plus"
    )
    assert min(f[1] for f in LINKED_BIRTH_2003_FIELDS) == 1
    assert max(f[2] for f in LINKED_BIRTH_2003_FIELDS) == 750     # birth ends @750
    assert min(f[1] for f in LINKED_DEATH_2003_FIELDS) == 751     # "plus" starts @751
    assert max(f[2] for f in LINKED_DEATH_2003_FIELDS) == 783     # den-plus ends @783
    combined = sorted(
        LINKED_BIRTH_2003_FIELDS + LINKED_DEATH_2003_FIELDS, key=lambda f: f[1]
    )
    assert combined[0][1] == 1 and combined[-1][2] == 783
    for prev, cur in zip(combined, combined[1:]):
        assert cur[1] == prev[2] + 1, f"den-plus not contiguous: {prev} then {cur}"
    # anchors verified byte-exact vs the LinkCO03Guide DETAIL (pp20-55)
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_2003_FIELDS}
    assert b["REVISION"] == (7, 7)        # S=1989-unrev / A=2003-rev
    assert b["IDNUMBER"] == (10, 14)      # num<->den-plus join key (p20)
    assert b["DOB_YY"] == (15, 18)        # birth year (== 2003)
    assert b["DPLURAL"] == (423, 423)
    assert b["SEX"] == (436, 436)
    assert b["DBWT"] == (467, 470)        # grams (NOT 81-84 = 1995-2002)
    assert b["COMBGEST"] == (451, 452)
    d = {f[0]: (f[1], f[2]) for f in LINKED_DEATH_2003_FIELDS}
    assert d["MATCHS"] == (751, 751)      # 2003: @751 (NOT @1 = 1995-2002)
    assert d["AGED"] == (755, 757)
    assert d["UCOD"] == (767, 770)        # ICD-10 (2003 cohort all ICD-10)
    assert d["UCODR130"] == (772, 774)
    assert d["RECWT"] == (776, 783)       # den-plus ends here


def test_numerator_layout_contiguous_and_well_formed():
    # Numerator (1142) = birth 1-750 + death "plus" 751-783 (REUSE the
    # den-plus specs) + numerator-only mortality 784-1142.
    _assert_layout_well_formed(
        LINKED_NUM_DEATH_2003_FIELDS, LINKED_NUM_RECLEN_2003, "2003_num_death"
    )
    assert min(f[1] for f in LINKED_NUM_DEATH_2003_FIELDS) == 784
    assert max(f[2] for f in LINKED_NUM_DEATH_2003_FIELDS) == 1142
    full = sorted(
        LINKED_BIRTH_2003_FIELDS
        + LINKED_DEATH_2003_FIELDS
        + LINKED_NUM_DEATH_2003_FIELDS,
        key=lambda f: f[1],
    )
    assert full[0][1] == 1 and full[-1][2] == 1142
    for prev, cur in zip(full, full[1:]):
        assert cur[1] == prev[2] + 1, f"numerator not contiguous: {prev} then {cur}"
    names = [f[0] for f in full]
    assert len(names) == len(set(names)), "numerator field-name collision"
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_2003_FIELDS}
    assert d["EANUM"] == (786, 787)       # 00-20
    assert d["ENTITY"] == (788, 927)      # 20 x 7-byte entity-axis
    assert d["RANUM"] == (930, 931)       # 00-20
    assert d["RECORD"] == (932, 1031)     # 20 x 5-byte record-axis
    assert d["DTHYR"] == (1071, 1074)     # year of death (cohort..+1)
    assert d["DTHMON"] == (1141, 1142)    # numerator ends @1142


def test_denominator_dispatcher_additive_branch():
    reclen, birth, death = _layout_for_linked_year(2003)
    assert reclen == 783
    assert birth is LINKED_BIRTH_2003_FIELDS
    assert death is LINKED_DEATH_2003_FIELDS
    # 2004 is now configured (C8.18 DO step 4c) — this minimal Edit is
    # bundled into the 4c commit per L17 / §4.2.1 (this harness is
    # DESIGN: tracks-current-state; the stale "2004 raises ValueError"
    # pin would otherwise FAIL on the correct 4c mutation).
    # 1992-1994 = the permanent NCHS linkage gap (remaining negative case)
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _layout_for_linked_year(y)


def test_numerator_dispatcher_additive_branch():
    reclen, birth, death = _numerator_layout_for_linked_year(2003)
    assert reclen == 1142
    assert birth is LINKED_BIRTH_2003_FIELDS
    # numerator death = den-plus "plus" 751-783 + mortality 784-1142
    assert death == LINKED_DEATH_2003_FIELDS + LINKED_NUM_DEATH_2003_FIELDS
    # 2004 now configured (C8.18 DO step 4c; L17 bundle per §4.2.1)
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _numerator_layout_for_linked_year(y)
    with pytest.raises(ValueError):
        _numerator_layout_for_linked_year(2005)  # numerator dispatcher = cohort only


def test_prior_substep_dispatchers_unregressed():
    # H10/HALT-13: the 4b additive single-year-2003 branches must NOT
    # perturb the 3a/3b/4a/2005/2014 dispatcher returns.
    assert _layout_for_linked_year(1983)[0] == 91
    assert _layout_for_linked_year(1989)[0] == 225
    assert _layout_for_linked_year(1996)[0] == 230
    assert _layout_for_linked_year(2002)[0] == 230
    assert _layout_for_linked_year(2008)[0] == 900
    assert _layout_for_linked_year(2018)[0] == 1384
    assert _numerator_layout_for_linked_year(1985)[0] == 500
    assert _numerator_layout_for_linked_year(1990)[0] == 535
    assert _numerator_layout_for_linked_year(2002)[0] == 535


# --------------------------------------------------------------------------
# Tier 0: synthetic record — value recovery + position-shift NEGATIVE check
# --------------------------------------------------------------------------

def _slice(rec: bytes, start: int, end: int) -> str:
    return rec[start - 1 : end].decode("latin-1")


def _plant(rec: bytearray, pos: tuple[int, int], value: str):
    s, e = pos
    field = value.ljust(e - s + 1)[: e - s + 1]
    rec[s - 1 : e] = field.encode("latin-1")


def test_tier0_synthetic_783byte_denplus_recovery_and_negative():
    rl, birth, death = _layout_for_linked_year(2003)
    assert rl == 783
    rec = bytearray(b" " * 783)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    _plant(rec, b["REVISION"], "A")        # @7 2003-revised
    _plant(rec, b["IDNUMBER"], "01234")    # @10-14
    _plant(rec, b["DOB_YY"], "2003")       # @15-18
    _plant(rec, b["DBWT"], "3402")         # @467-470 grams
    _plant(rec, b["SEX"], "1")             # @436
    _plant(rec, d["MATCHS"], "2")          # @751 surviving infant
    _plant(rec, d["RECWT"], "1.000000")    # @776-783
    rec = bytes(rec)
    assert _slice(rec, *b["REVISION"]) == "A"
    assert _slice(rec, *b["IDNUMBER"]) == "01234"
    assert _slice(rec, *b["DOB_YY"]) == "2003"
    assert _slice(rec, *b["DBWT"]) == "3402"
    assert _slice(rec, *b["SEX"]) == "1"
    assert _slice(rec, *d["MATCHS"]) == "2"
    assert _slice(rec, *d["RECWT"]) == "1.000000"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = b["DOB_YY"]
    assert _slice(rec, s + 1, e + 1) != "2003"


def test_tier0_synthetic_1142byte_numerator_recovery_and_negative():
    rl, birth, death = _numerator_layout_for_linked_year(2003)
    assert rl == 1142
    rec = bytearray(b" " * 1142)
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # NOTE: in the 2003 layout MATCHS is @751 (LINKED_DEATH_2003), NOT
    # @1 like 1995-2002 (LINKED_BIRTH) -> it lives in the `death` dict.
    _plant(rec, d["MATCHS"], "1")          # @751 matched infant death
    _plant(rec, b["DOB_YY"], "2003")       # @15-18
    _plant(rec, d["AGED"], "045")          # @755-757 ("plus")
    _plant(rec, d["UCOD"], "P073")         # @767-770 ICD-10
    _plant(rec, d["EANUM"], "03")          # @786-787 (mortality section)
    _plant(rec, d["DTHYR"], "2004")        # @1071-1074
    _plant(rec, d["DTHMON"], "06")         # @1141-1142
    rec = bytes(rec)
    assert _slice(rec, *d["MATCHS"]) == "1"
    assert _slice(rec, *b["DOB_YY"]) == "2003"
    assert _slice(rec, *d["AGED"]) == "045"
    assert _slice(rec, *d["UCOD"]) == "P073"
    assert _slice(rec, *d["EANUM"]) == "03"
    assert _slice(rec, *d["DTHYR"]) == "2004"
    assert _slice(rec, *d["DTHMON"]) == "06"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted UCOD
    s, e = d["UCOD"]
    assert _slice(rec, s + 1, e + 1) != "P073"


# --------------------------------------------------------------------------
# Tier 1: real cohort data — encoding + value-distribution (DEFLATE64 / 7z)
# --------------------------------------------------------------------------

def _member(zip_path: Path, substr: str) -> str:
    # listing works on DEFLATE64 zips (only decompression fails);
    # member naming is VS03LKBC.US{DEN,NUM,UNM}PUB.
    with zipfile.ZipFile(zip_path) as zf:
        return next(m for m in zf.namelist() if substr in m.upper())


def _read_first_records(zip_path: Path, member_substr: str, n: int, reclen: int):
    """Stream first n records of a DEFLATE64 member via `7z e -so`.

    The LinkCO03US.zip members are DEFLATE64 (compress_type=9); stdlib
    `zipfile` raises NotImplementedError. The DO-step-4b tooling
    decision is the CLI `7z` stream (homebrew p7zip), NOT a
    zipfile-deflate64 dependency (single cohort year; preserves the
    C8.5a pinned-env SHA; the 3.2 GB den-plus member is streamed, not
    extracted). Block size is empirically derived (data + CR/LF) — the
    FIX_LOG 2026-05-14 L13 arithmetic-class defense.
    """
    member = _member(zip_path, member_substr)
    block = reclen + 2  # CR + LF (confirmed at the DO step 4b PRE-FLIGHT)
    proc = subprocess.Popen(
        ["7z", "e", "-so", str(zip_path), member],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    buf = b""
    try:
        while len(buf) < block * n:
            chunk = proc.stdout.read(block * n - len(buf))
            if not chunk:
                break  # EOF
            buf += chunk
    finally:
        proc.stdout.close()
        proc.terminate()
    assert len(buf) >= block * n, f"{zip_path.name}: short read ({len(buf)} < {block*n})"
    # confirm CR/LF terminator + empirical record framing
    assert buf[reclen : reclen + 2] == b"\r\n", (
        f"{zip_path.name}: expected CR/LF at byte {reclen} (block framing)"
    )
    recs = [buf[i * block : i * block + reclen] for i in range(n)]
    return recs


_REQUIRE = pytest.mark.skipif(
    not ZIP_2003.exists() or shutil.which("7z") is None,
    reason="raw cohort zip absent (gitignored, out-of-tree) or 7z (DEFLATE64) unavailable",
)


@_REQUIRE
def test_tier1_real_denplus_2003():
    recs = _read_first_records(ZIP_2003, "DEN", 300, LINKED_DENOMPLUS_RECLEN_2003)
    rl, birth, death = _layout_for_linked_year(2003)
    assert rl == 783
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    # encoding (ASCII-not-EBCDIC) + alignment + block size, jointly:
    assert all(_slice(r, *b["DOB_YY"]) == "2003" for r in recs), (
        "LinkCO03US den-plus DOB_YY != 2003 (encoding/alignment)"
    )
    # den-plus carries surviving infants + matched deaths; MATCHS in
    # {1,2} (3=unmatched is unlinked-file-only); never empty
    ms = {_slice(r, *d["MATCHS"]) for r in recs}
    assert ms <= {"1", "2"}, f"den-plus MATCHS domain {ms}"
    assert "2" in ms, "expected surviving (MATCHS=2) in den-plus"
    # REVISION flag domain (2003 transition): S (1989-unrev) / A (2003-rev)
    assert {_slice(r, *b["REVISION"]) for r in recs} <= {"S", "A"}
    # birthweight numeric grams @467-470 (sentinel 9999=NS allowed)
    dbw = [_slice(r, *b["DBWT"]).strip() for r in recs]
    assert all(v.isdigit() and len(v) == 4 for v in dbw), (
        "DBWT@467-470 not 4-digit grams (layout)"
    )
    assert any(200 <= int(v) <= 9000 for v in dbw)  # plausible live-birth grams
    # surviving live births weighted exactly 1.0 (den-plus ends @783)
    assert all(_slice(r, *d["RECWT"]).startswith("1.") for r in recs)
    assert any(_slice(r, *d["RECWT"]) == "1.000000" for r in recs)


@_REQUIRE
def test_tier1_real_numerator_2003_icd10():
    recs = _read_first_records(ZIP_2003, "NUM", 300, LINKED_NUM_RECLEN_2003)
    rl, birth, death = _numerator_layout_for_linked_year(2003)
    assert rl == 1142
    b = {f[0]: (f[1], f[2]) for f in birth}
    d = {f[0]: (f[1], f[2]) for f in death}
    assert all(_slice(r, *b["DOB_YY"]) == "2003" for r in recs), (
        "LinkCO03US numerator DOB_YY != 2003 (encoding/alignment)"
    )
    # numerator = linked infant deaths only -> MATCHS == 1 for all
    # (MATCHS@751 is in the `death` dict for 2003, not `birth`)
    assert {_slice(r, *d["MATCHS"]) for r in recs} == {"1"}, (
        "numerator MATCHS must be all 1 (linked infant deaths)"
    )
    # cert match key is a non-blank 5-char field
    assert all(_slice(r, *b["IDNUMBER"]).strip() for r in recs)
    # AGED 000-366 (sentinel-aware)
    aged = [_slice(r, *d["AGED"]).strip() for r in recs]
    assert all((not v) or (v.isdigit() and 0 <= int(v) <= 366) for v in aged)
    # entity/record-axis counts 00-20 (sentinel-aware)
    for fld in ("EANUM", "RANUM"):
        cnts = [_slice(r, *d[fld]).strip() for r in recs]
        assert all((not v) or (v.isdigit() and 0 <= int(v) <= 20) for v in cnts)
    # year of death within the cohort window [2003, 2004]
    yods = [_slice(r, *d["DTHYR"]).strip() for r in recs]
    assert all(y.isdigit() and 2003 <= int(y) <= 2004 for y in yods if y)
    assert all(1 <= int(_slice(r, *d["DTHMON"])) <= 12 for r in recs)
    # 2003 cohort -> ALL infant deaths are ICD-10 (deaths 2003-2004);
    # UCOD@767-770 is alpha (A00-Z99), NOT numeric ICD-9 (L13-extension
    # value-domain check at the constant byte position).
    ucods = [_slice(r, *d["UCOD"]).strip() for r in recs if _slice(r, *d["UCOD"]).strip()]
    assert ucods, "no non-blank UCOD among sampled deaths"
    assert sum(c[0].isalpha() for c in ucods) >= 0.8 * len(ucods), (
        f"expected ICD-10 alpha UCOD for the 2003 cohort (sample {ucods[:5]})"
    )
