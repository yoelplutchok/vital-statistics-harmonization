"""DESIGN: tracks-current-state

C8.18 DO step 5b SMOKE — the 1983-1988 **self-contained-numerator +
aggregate-denominator** two-file construction + a cross-era
**numerator-member finder** (the symmetric ``"NUM"`` sibling of 5a's
``_find_denomplus_member`` ``"DEN"`` rule).

Sibling of the 3a/3b/4a/4b/4c/5a cohort smokes; kept separate so each
sub-step stays independently re-runnable (the C8.17 DO5a/5b + C8.18
DO3a/3b/4a/4b/4c/5a sub-step-isolation precedent). DO step 5b adds
``parse_linked_year._find_numerator_member`` (NEW) +
``_iter_two_file_1983_1988`` (NEW) + a top-of-``iter_parsed_records``
1983-1988 branch; the ``_layout_for_linked_year`` /
``_numerator_layout_for_linked_year`` dispatchers + the 3a/3b/4a/4b/4c
+ 2005/2014 specs + ``_find_denomplus_member`` (5a) are byte-untouched
(H10/HALT-13) — so this harness adds NO new-year ``pytest.raises`` pin
(the L17 stale-pin class does not apply to 5b: no new dispatcher year
is configured; 1983-1988 were already configured by 3a/3b; 1992-1994
still raise via the unchanged dispatchers).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
— the numerator member resolves *uniquely* per era's member-naming
convention; a num-absent / ambiguous archive *raises* (fail-closed,
L3); the 1983-1988 two-file construction yields the den segment then
the num segment, each tagged ``link_segment``, with den rows carrying
no death field and num rows carrying the mortality section, and
row-count conservation (den_n + num_n; H6); the canonical 2005+ path
is byte-identical (no ``link_segment`` key — regression lock). No
mutable annotation value is pinned (reclens 91/500 are fixed
historical NCHS facts; member names are fixed NCHS file conventions).

Construction model (the DO step 5b Convention-3 snapshot,
PRE_FLIGHT_LOG 2026-05-19T08:00:00Z + 2026-05-19T08:00:00Z):
1983-1988 carry NO record-level public-use key, so the standard NCHS
pre-2005 cohort-IMR construction is the lossless union of the 91-byte
births-only Denominator (the aggregate birth denominator) + the
500-byte self-contained Numerator (the linked-infant-death set), kept
side-by-side with a synthetic ``link_segment`` discriminator (no
fabricated join). The harmonized one-row-per-birth / infant_death /
record_weight semantics for the keyless era = DO step 5c (the den
segment = one row per birth, infant_death null/unknown per-record
since un-linkable; the num segment = the within-era infant-death
detail surface — a documented within-era structural difference, not a
silent deviation; manuscript Coverage = Phase-D D.4).

Tier 0 (synthetic zips in tmp, always runs): tiny real archives with
each era's member-name set; the num member resolves; den-only /
unlinked-only / empty / ambiguous archives raise (L3 — proves the
finder discriminates, not a rubber-stamp). A synthetic 2-member
1983-1988 zip exercises ``_iter_two_file_1983_1988`` end-to-end
(segment tagging + row-count conservation + a position-shift NEGATIVE).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): the real ``_iter_two_file_1983_1988`` end-to-end path on
LinkCO{83,85,88}.zip — den-segment BIRYR == the cohort year, the
num-member resolves to ``USnum.dat``, num-segment BIRYR == the cohort
year + MATCHS in {1,2} (linked deaths only) + den_n > num_n — plus
the 2005 regression (the existing single-member path carries no
``link_segment`` key).
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
    LINKED_DEN_RECLEN_1983_1988,
    LINKED_NUM_DEATH_1983_1988_FIELDS,
    LINKED_NUM_RECLEN_1983_1988,
)
from parse_linked_year import (  # noqa: E402
    _find_denomplus_member,
    _find_numerator_member,
    _iter_two_file_1983_1988,
    iter_parsed_records,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# Tier 0: synthetic archives — per-era numerator resolution + L3 negatives
# --------------------------------------------------------------------------

def _make_zip(tmp_path: Path, members: list[str], data: dict[str, bytes] | None = None) -> Path:
    """Build a tiny real DEFLATE .zip with the given member names."""
    zp = tmp_path / "probe.zip"
    data = data or {}
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in members:
            zf.writestr(m, data.get(m, b"x"))
    return zp


# (era label, member set, expected num member) — the real NCHS
# cohort-linked member-naming conventions (5a PRE-FLIGHT probe table).
_ERA_MEMBERS = [
    ("1983-1991", ["LinkCO83USden.dat", "LinkCO83USnum.dat", "LinkCO83USUnl.dat"],
     "LinkCO83USnum.dat"),
    ("1995-2002 (mixed-case)",
     ["LinkCO95USDen.dat", "LinkCO95USNum.dat", "LinkCO95USUnl.dat"],
     "LinkCO95USNum.dat"),
    ("1995-2002 (upper)",
     ["LinkCO02USDEN.dat", "LinkCO02USNUM.dat", "LinkCO02USUNL.dat"],
     "LinkCO02USNUM.dat"),
    ("2003", ["VS03LKBC.USDENPUB", "VS03LKBC.USNUMPUB", "VS03LKBC.USUNMPUB"],
     "VS03LKBC.USNUMPUB"),
    ("2004 / 2005+", ["VS04LKBC.DUSDENOM", "VS04LKBC.USNUMPUB", "VS04LKBC.USUNMPUB"],
     "VS04LKBC.USNUMPUB"),
]


@pytest.mark.parametrize("label,members,expected", _ERA_MEMBERS,
                         ids=[e[0] for e in _ERA_MEMBERS])
def test_tier0_numerator_member_resolves_per_era(tmp_path, label, members, expected):
    zp = _make_zip(tmp_path, members)
    assert _find_numerator_member(zp) == expected, label


@pytest.mark.parametrize(
    "members",
    [
        pytest.param(["LinkCO83USden.dat", "LinkCO83USUnl.dat"], id="den+unl-only"),
        pytest.param(["VS03LKBC.USDENPUB", "VS03LKBC.USUNMPUB"], id="2003-den+unm-only"),
        pytest.param([], id="empty-archive"),
        pytest.param(
            ["LinkCO95USNum.dat", "LinkCO95USNUM2.dat", "LinkCO95USDen.dat"],
            id="ambiguous-two-NUM",
        ),
    ],
)
def test_tier0_numerator_failclosed_negative(tmp_path, members):
    """L3: a num-absent or ambiguous archive must RAISE, never silently
    pick a wrong member (§2 fail-closed; §9-#4 — the test discriminates,
    it is not a rubber-stamp)."""
    zp = _make_zip(tmp_path, members)
    with pytest.raises(RuntimeError):
        _find_numerator_member(zp)


def test_tier0_numfinder_does_not_match_den_or_unlinked(tmp_path):
    """The "NUM"-not-"UNL"/"UNM" rule must not be fooled by the den
    ("DENOM" has no "NUM") or unlinked ("UNM"/"UNL") member names."""
    zp = _make_zip(tmp_path, ["VS05LKBC.DUSDENOM", "VS05LKBC.USNUMPUB",
                              "VS05LKBC.USUNMPUB"])
    assert _find_numerator_member(zp) == "VS05LKBC.USNUMPUB"
    # and the den finder still resolves DENOM (5a regression, unchanged)
    assert _find_denomplus_member(zp) == "VS05LKBC.DUSDENOM"


# --------------------------------------------------------------------------
# Tier 0: the 1983-1988 two-file construction — segment tagging + H6
# --------------------------------------------------------------------------

def _rec(fields_pos: dict[str, tuple[int, int]], reclen: int,
         planted: dict[str, str]) -> bytes:
    rec = bytearray(b" " * reclen)
    for name, val in planted.items():
        s, e = fields_pos[name]
        f = val.ljust(e - s + 1)[: e - s + 1]
        rec[s - 1 : e] = f.encode("latin-1")
    return bytes(rec) + b"\r\n"


def _build_1983_1988_zip(tmp_path: Path, n_den: int, n_num: int) -> Path:
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1983_1988_FIELDS}
    d = {f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_1983_1988_FIELDS}
    den_blob = b"".join(
        _rec(b, LINKED_DEN_RECLEN_1983_1988,
             {"MATCHS": "3" if i % 2 else "1", "BIRYR": "1985"})
        for i in range(n_den)
    )
    num_blob = b"".join(
        _rec({**b, **d}, LINKED_NUM_RECLEN_1983_1988,
             {"MATCHS": "1", "BIRYR": "1985", "YOD": "1985", "UCOD": "7980"})
        for i in range(n_num)
    )
    return _make_zip(
        tmp_path,
        ["LinkCO85USden.dat", "LinkCO85USnum.dat", "LinkCO85USUnl.dat"],
        {"LinkCO85USden.dat": den_blob, "LinkCO85USnum.dat": num_blob},
    )


def test_tier0_two_file_construction_segments_and_conservation(tmp_path):
    zp = _build_1983_1988_zip(tmp_path, n_den=5, n_num=3)
    rows = list(_iter_two_file_1983_1988(zp, 1985, max_rows=None))
    # H6 row-count conservation: every den + num record preserved
    assert len(rows) == 5 + 3
    den = [r for r in rows if r["link_segment"] == "den"]
    num = [r for r in rows if r["link_segment"] == "num"]
    assert len(den) == 5 and len(num) == 3
    # den emitted before num (aggregate-denominator first, then numerator)
    assert [r["link_segment"] for r in rows] == ["den"] * 5 + ["num"] * 3
    # every row carries the cohort year + the discriminator
    assert all(r["year"] == 1985 for r in rows)
    assert all(r["BIRYR"] == "1985" for r in rows)
    # den segment = births-only: NO death field key (no death section)
    assert all("UCOD" not in r and "YOD" not in r for r in den)
    # num segment = self-contained: birth covariates + mortality section
    assert all(r["UCOD"] == "7980" and r["YOD"] == "1985" for r in num)
    assert all("MATCHS" in r for r in den + num)


def test_tier0_two_file_construction_maxrows_per_segment_cap(tmp_path):
    # max_rows caps EACH segment independently (a bounded sample must
    # represent BOTH segments; a single shared counter would fill
    # entirely from the multi-million-row den segment and never reach
    # num — surfaced + refined at the DO step 5b SMOKE, PRE_FLIGHT_LOG
    # 2026-05-19T08:00:00Z addendum).
    zp = _build_1983_1988_zip(tmp_path, n_den=8, n_num=5)
    rows = list(_iter_two_file_1983_1988(zp, 1985, max_rows=3))
    # 3 den (capped) + 3 num (capped), den first
    assert [r["link_segment"] for r in rows] == ["den"] * 3 + ["num"] * 3
    # a segment with fewer rows than the cap yields all of them
    rows2 = list(_iter_two_file_1983_1988(zp, 1985, max_rows=6))
    assert [r["link_segment"] for r in rows2] == ["den"] * 6 + ["num"] * 5


def test_tier0_two_file_construction_skips_bad_length(tmp_path):
    """A record of the wrong width is skipped (bad_len), not yielded
    mis-sliced (L3 / §2 fail-closed)."""
    b = {f[0]: (f[1], f[2]) for f in LINKED_BIRTH_1983_1988_FIELDS}
    good = _rec(b, LINKED_DEN_RECLEN_1983_1988, {"MATCHS": "1", "BIRYR": "1985"})
    short = b"TOO_SHORT\r\n"
    den_blob = good + short + good
    num_blob = _rec({**b, **{f[0]: (f[1], f[2]) for f in LINKED_NUM_DEATH_1983_1988_FIELDS}},
                    LINKED_NUM_RECLEN_1983_1988, {"MATCHS": "1", "BIRYR": "1985"})
    zp = _make_zip(
        tmp_path, ["LinkCO85USden.dat", "LinkCO85USnum.dat"],
        {"LinkCO85USden.dat": den_blob, "LinkCO85USnum.dat": num_blob},
    )
    rows = list(_iter_two_file_1983_1988(zp, 1985, max_rows=None))
    # the short den line is skipped; 2 good den + 1 num survive
    assert [r["link_segment"] for r in rows] == ["den", "den", "num"]


def test_tier0_position_shift_negative(tmp_path):
    """L3: the construction must slice the documented positions; a
    1-byte-shifted expectation must NOT recover the planted value."""
    zp = _build_1983_1988_zip(tmp_path, n_den=1, n_num=1)
    num = [r for r in _iter_two_file_1983_1988(zp, 1985, max_rows=None)
           if r["link_segment"] == "num"][0]
    assert num["UCOD"] == "7980"
    # a harness that "passed" regardless of slicing would be a
    # rubber-stamp; the planted UCOD is exactly 4 bytes at 231-234, so a
    # blank-padded neighbour field must differ.
    assert num["UCODR61"] != "7980"


# --------------------------------------------------------------------------
# Tier 1: real cohort data — the real _iter_two_file_1983_1988 path
# --------------------------------------------------------------------------

_TIER1 = [(1983, "LinkCO83.zip"), (1985, "LinkCO85.zip"), (1988, "LinkCO88.zip")]


@pytest.mark.parametrize("year,zipname", _TIER1, ids=[f"{y}" for y, _ in _TIER1])
def test_tier1_two_file_construction_real(year, zipname):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zipname}")

    # the two finders resolve the era's den + num members uniquely
    assert _find_denomplus_member(zp) == f"LinkCO{year % 100:02d}USden.dat"
    assert _find_numerator_member(zp) == f"LinkCO{year % 100:02d}USnum.dat"

    # the real end-to-end two-file construction: den segment then num
    # segment, cohort-year anchor == the cohort year for every sampled
    # record (jointly proves member-resolution + reclen + ASCII +
    # alignment, the FIX_LOG 2026-05-14 L13 arithmetic-class defense).
    rows = list(_iter_two_file_1983_1988(zp, year, max_rows=400))
    den = [r for r in rows if r["link_segment"] == "den"]
    num = [r for r in rows if r["link_segment"] == "num"]
    assert den, f"{zipname}: no den-segment rows"
    assert num, f"{zipname}: no num-segment rows (max_rows too small?)"
    assert {r["BIRYR"] for r in den} == {str(year)}, (
        f"{zipname}: den BIRYR != {year} (member/reclen/encoding/alignment)"
    )
    assert {r["BIRYR"] for r in num} == {str(year)}, (
        f"{zipname}: num BIRYR != {year}"
    )
    # numerator = linked infant deaths only (MATCHS in {1,2}; 3=surviving
    # never appears in the numerator); den carries no death field.
    assert {r["MATCHS"] for r in num} <= set("12 ")
    assert all("UCOD" not in r for r in den)
    assert all("UCOD" in r for r in num)


def test_tier1_full_year_den_exceeds_num():
    """Sanity: across a full year the births denominator vastly exceeds
    the linked-infant-death numerator (a mis-resolved member or a
    swapped segment would invert this)."""
    zp = LINKED_RAW_DIR / "LinkCO85.zip"
    if not zp.exists():
        pytest.skip("raw 1985 cohort zip absent (gitignored, out-of-tree)")
    den_n = 0
    num_n = 0
    for r in _iter_two_file_1983_1988(zp, 1985, max_rows=None):
        if r["link_segment"] == "den":
            den_n += 1
        else:
            num_n += 1
    assert den_n > 0 and num_n > 0
    assert den_n > num_n * 10, f"den={den_n:,} not >> num={num_n:,}"


def test_tier1_2005_regression_unchanged():
    """The canonical 2005+ single-member path must be byte-identical:
    iter_parsed_records(2005) must NOT route through the two-file
    branch and must carry NO ``link_segment`` key (DO step 5b must not
    perturb the shipped v3 2005-2023 product)."""
    zp = LINKED_RAW_DIR / "LinkCO05US.zip"
    if not zp.exists():
        pytest.skip("raw 2005 zip absent (gitignored, out-of-tree)")
    rows = list(iter_parsed_records(zp, 2005, max_rows=10))
    assert len(rows) == 10
    assert all("link_segment" not in r for r in rows)
