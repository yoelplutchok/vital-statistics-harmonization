"""DESIGN: tracks-current-state

C8.18 DO step 3a SMOKE — pre-1990 cohort linked DENOMINATOR layout.

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants of
the additive ``field_specs.py`` cohort-denominator layouts (record-length
constants = the documented fixed-width contract; in-bounds + non-overlap;
dispatcher branch; 2005/2014 additive-only regression guard) plus, on the
real SHA-anchored cohort zips, value-distribution + encoding invariants
(L13-extension: byte position alone is not trusted; HALT 5 EBCDIC-vs-ASCII).
No mutable annotation value is pinned (the record lengths 91 / 225 are
fixed historical NCHS facts, not evolving annotations).

Tier 0 (synthetic, always runs): hand-built records with planted values
at documented positions + a position-shift NEGATIVE check (L3: proves the
slicing discriminates position, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip absent):
first records of LinkCO{83,85,88}USden.dat (91-byte) + LinkCO{89,90,91}
USden.dat (225-byte) — empirical block-size = reclen + CR/LF (FIX_LOG
2026-05-14 L13 arithmetic-class defense), ASCII-decodability, and
BIRYR == cohort year for every sampled record (the single strongest
joint encoding + alignment + block-size assertion).
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
    LINKED_DEN_RECLEN_1983_1988,
    LINKED_DENOMPLUS_RECLEN_1989_1991,
)
from parse_linked_year import _layout_for_linked_year  # noqa: E402

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# SHAPE: structural invariants of the layout substrate
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
    # 91 / 225 are the NCHS-guide-documented fixed-width record lengths
    # (1983-1988 LinkCOxxUSden.dat = 91; 1989-1991 = 225). Fixed history.
    assert LINKED_DEN_RECLEN_1983_1988 == 91
    assert LINKED_DENOMPLUS_RECLEN_1989_1991 == 225


def test_1983_1988_layout_well_formed():
    _assert_layout_well_formed(
        LINKED_BIRTH_1983_1988_FIELDS, LINKED_DEN_RECLEN_1983_1988, "1983_1988_birth"
    )
    # Anchor positions transcribed from PRE_FLIGHT_LOG 2026-05-17T20:00:00Z
    d = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1983_1988_FIELDS}
    assert d["MATCHS"] == (1, 1)
    assert d["BIRYR"] == (2, 5)
    assert d["CSEX"] == (38, 38)
    assert d["DBIRWT"] == (43, 46)
    assert d["RECWT"] == (91, 91)  # "the denominator record ends in location 91"


def test_1989_1991_layout_well_formed():
    _assert_layout_well_formed(
        LINKED_BIRTH_1989_1991_FIELDS, LINKED_DENOMPLUS_RECLEN_1989_1991, "1989_1991_birth"
    )
    _assert_layout_well_formed(
        LINKED_DEATH_1989_1991_FIELDS, LINKED_DENOMPLUS_RECLEN_1989_1991, "1989_1991_death"
    )
    # birth section ends by loc 210; the appended death "plus" is 213-225
    assert max(f[2] for f in LINKED_BIRTH_1989_1991_FIELDS) <= 212
    assert min(f[1] for f in LINKED_DEATH_1989_1991_FIELDS) >= 213
    assert max(f[2] for f in LINKED_DEATH_1989_1991_FIELDS) == 225
    d = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1989_1991_FIELDS}
    assert d["MATCHS"] == (1, 1)
    assert d["BIRYR"] == (7, 10)    # LinkCO89Guide p20
    assert d["CSEX"] == (78, 78)    # detail p34: CSEXIMP@77, CSEX@78 (1 byte)
    assert d["DBIRWT"] == (79, 82)  # detail p34: DBIRWT 4-byte grams (not 79-85)


def test_dispatcher_additive_branch():
    for y in (1983, 1985, 1988):
        reclen, birth, death = _layout_for_linked_year(y)
        assert reclen == 91
        assert birth is LINKED_BIRTH_1983_1988_FIELDS
        assert death == []  # births-only denominator; numerator = DO step 3b
    for y in (1989, 1990, 1991):
        reclen, birth, death = _layout_for_linked_year(y)
        assert reclen == 225
        assert birth is LINKED_BIRTH_1989_1991_FIELDS
        assert death is LINKED_DEATH_1989_1991_FIELDS


def test_2005_2014_branches_unregressed():
    # additive-only guard: pre-existing branches keep their reclens
    assert _layout_for_linked_year(2008)[0] == 900
    assert _layout_for_linked_year(2018)[0] == 1384
    with pytest.raises(ValueError):
        _layout_for_linked_year(1994)  # 1992-1994 permanent gap, unconfigured


# --------------------------------------------------------------------------
# Tier 0: synthetic record — value recovery + position-shift NEGATIVE check
# --------------------------------------------------------------------------

def _slice(rec: bytes, start: int, end: int) -> str:
    return rec[start - 1 : end].decode("latin-1")


def test_tier0_synthetic_91byte_recovery_and_negative():
    rec = bytearray(b" " * 91)
    rec[0:1] = b"1"          # MATCHS @1
    rec[1:5] = b"1985"       # BIRYR @2-5
    rec[37:38] = b"2"        # CSEX @38
    rec[42:46] = b"3402"     # DBIRWT @43-46
    rec[49:50] = b"1"        # DPLURAL @50
    rec[90:91] = b"1"        # RECWT @91
    rec = bytes(rec)
    d = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1983_1988_FIELDS}
    assert _slice(rec, *d["MATCHS"]) == "1"
    assert _slice(rec, *d["BIRYR"]) == "1985"
    assert _slice(rec, *d["CSEX"]) == "2"
    assert _slice(rec, *d["DBIRWT"]) == "3402"
    assert _slice(rec, *d["RECWT"]) == "1"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = d["BIRYR"]
    assert _slice(rec, s + 1, e + 1) != "1985"


def _plant(rec: bytearray, pos: tuple[int, int], value: str):
    s, e = pos
    field = value.ljust(e - s + 1)[: e - s + 1]
    rec[s - 1 : e] = field.encode("latin-1")


def test_tier0_synthetic_225byte_recovery_and_negative():
    db = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1989_1991_FIELDS}
    dd = {f[0]: (f[1], f[2]) for f in LINKED_DEATH_1989_1991_FIELDS}
    rec = bytearray(b" " * 225)
    _plant(rec, db["MATCHS"], "3")        # @1
    _plant(rec, db["BIRYR"], "1990")      # @7-10
    _plant(rec, db["CSEX"], "1")          # @78 (1 byte)
    _plant(rec, db["DBIRWT"], "3402")     # @79-82 (4 bytes)
    _plant(rec, db["DPLURAL"], "1")       # @87
    _plant(rec, dd["AGED"], "007")        # @213-215 (death "plus")
    _plant(rec, dd["UCODR61"], "010")     # @223-225
    rec = bytes(rec)
    assert _slice(rec, *db["MATCHS"]) == "3"
    assert _slice(rec, *db["BIRYR"]) == "1990"
    assert _slice(rec, *db["CSEX"]) == "1"
    assert _slice(rec, *db["DBIRWT"]) == "3402"
    assert _slice(rec, *db["DPLURAL"]) == "1"
    assert _slice(rec, *dd["AGED"]) == "007"
    assert _slice(rec, *dd["UCODR61"]) == "010"
    # NEGATIVE (L3): a shifted slice must NOT recover the planted year
    s, e = db["BIRYR"]
    assert _slice(rec, s + 1, e + 1) != "1990"


# --------------------------------------------------------------------------
# Tier 1: real cohort data — encoding + value-distribution (L13-extension)
# --------------------------------------------------------------------------

def _read_first_records(zip_path: Path, member_substr: str, n: int):
    """Empirically derive block size (data + CR/LF) and yield first n records."""
    with zipfile.ZipFile(zip_path) as zf:
        member = next(m for m in zf.namelist() if member_substr in m.upper())
        info = zf.getinfo(member)
        with zf.open(member) as fh:
            head = fh.read(2048)
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


_COHORT_91 = [(1983, "LinkCO83.zip"), (1985, "LinkCO85.zip"), (1988, "LinkCO88.zip")]
_COHORT_225 = [(1989, "LinkCO89.zip"), (1990, "LinkCO90.zip"), (1991, "LinkCO91.zip")]


@pytest.mark.parametrize("year,zipname", _COHORT_91)
def test_tier1_real_1983_1988_denominator(year, zipname):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "DEN", 300)
    assert data_len == LINKED_DEN_RECLEN_1983_1988 == 91
    d = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1983_1988_FIELDS}
    # encoding (ASCII-not-EBCDIC) + alignment + block-size, jointly:
    assert all(_slice(r, *d["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: BIRYR != {year} for some record (encoding/alignment)"
    )
    # value-distribution (SHAPE: domain/dtype/distribution invariants),
    # sentinel-aware (H4: 9999 = birthweight not-stated is documented data):
    assert {_slice(r, *d["MATCHS"]) for r in recs} <= set("123 ")
    sexes = [_slice(r, *d["CSEX"]) for r in recs]
    assert set(sexes) <= set("12 ")
    assert sexes.count("1") > 0 and sexes.count("2") > 0  # both sexes present
    plur = [_slice(r, *d["DPLURAL"]) for r in recs]
    assert set(plur) <= set("123456789 ")
    assert plur.count("1") > len(plur) // 2  # singletons dominate
    numeric_bw = [
        int(v) for v in (_slice(r, *d["DBIRWT"]).strip() for r in recs)
        if v.isdigit() and v != "9999"
    ]
    assert numeric_bw and all(200 <= g <= 9000 for g in numeric_bw)
    assert n_rec > 2_000_000  # plausible US-cohort birth count


@pytest.mark.parametrize("year,zipname", _COHORT_225)
def test_tier1_real_1989_1991_denominator_plus(year, zipname):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zp}")
    data_len, n_rec, recs = _read_first_records(zp, "DEN", 300)
    assert data_len == LINKED_DENOMPLUS_RECLEN_1989_1991 == 225
    d = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1989_1991_FIELDS}
    assert all(_slice(r, *d["BIRYR"]) == str(year) for r in recs), (
        f"{zipname}: BIRYR != {year} for some record (encoding/alignment)"
    )
    assert {_slice(r, *d["MATCHS"]) for r in recs} <= set("123 ")
    sexes = [_slice(r, *d["CSEX"]) for r in recs]
    assert set(sexes) <= set("12 ")
    assert sexes.count("1") > 0 and sexes.count("2") > 0
    plur = [_slice(r, *d["DPLURAL"]) for r in recs]
    assert set(plur) <= set("123456789 ")
    assert plur.count("1") > len(plur) // 2  # singletons dominate
    numeric_bw = [
        int(v) for v in (_slice(r, *d["DBIRWT"]).strip() for r in recs)
        if v.isdigit() and v != "9999"
    ]
    assert numeric_bw and all(200 <= g <= 9000 for g in numeric_bw)
    assert n_rec > 2_000_000
