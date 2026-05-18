"""DESIGN: tracks-current-state

C8.18 DO step 5a SMOKE — cross-era denominator-member finder +
den-plus parse verification for the 4 self-contained
**denominator-PLUS** cohort eras (1989-1991, 1995-2002, 2003
[DEFLATE64], 2004).

Sibling of the 3a/3b/4a/4b/4c cohort-layout smokes; kept separate so
each sub-step stays independently re-runnable (the C8.17 DO5a/5b +
C8.18 DO3a/3b/4a/4b/4c sub-step-isolation precedent). DO step 5a only
broadens ``parse_linked_year._find_denomplus_member``; the
``_layout_for_linked_year`` / ``_numerator_layout_for_linked_year``
dispatchers + the 3a/3b/4a/4b/4c + 2005/2014 specs are byte-untouched
(H10/HALT-13) — so this harness adds NO new-year ``pytest.raises``
pin (the L17 stale-pin class does not apply to 5a).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
— the den member resolves *uniquely* per era's member-naming
convention; an ambiguous / den-absent archive *raises* (fail-closed,
L3); the resolved member's first record matches the state-on-disk
``field_specs.py`` reclen contract; the cohort-year anchor decodes to
the cohort year under latin-1 (ASCII + alignment + block-size,
jointly); and the canonical 2004/2005 selection is **byte-identical**
to the pre-broadening ``"DENOM"`` rule (regression lock — no prior
test pinned ``_find_denomplus_member``). No mutable annotation value
is pinned (reclens 225/230/783/900 are fixed historical NCHS facts;
member names are fixed NCHS file conventions).

Resolution model (the DO step 5a Convention-3 snapshot): the den-plus
member alone yields one-row-per-birth + death-"plus" for the 4
self-contained denominator-PLUS cohort eras; the 1983-1988 pure
two-file self-contained-numerator + aggregate-denominator construction
+ the numerator-member finder = DO step 5b; the harmonize per-cohort
field mapping + ICD-9 default-null/revision-tagged + cause_recode_130
per-era = DO step 5c (soft-flag (gg)). The DEFLATE64-at-2003 ``7z``
stream is ALREADY wired (``zip_text_stream.iter_lines_from_zip``
shells to ``7z x -so`` for ``compress_type ∉ {STORED, DEFLATED}`` —
added for natality 2009-2013 DEFLATE64 / 2015 PPMd — and
``parse_linked_year.iter_parsed_records`` already calls it); 5a needs
only the member-finder broadening for 2003.

Tier 0 (synthetic zips in tmp, always runs): tiny real archives with
each era's member-name set; the den member resolves; den-absent /
ambiguous / numerator-only archives raise (L3 — proves the finder
discriminates, not a rubber-stamp).

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent; 2003 additionally skipif ``7z`` absent): the real
``iter_parsed_records`` end-to-end path (``_find_denomplus_member`` +
``iter_lines_from_zip`` + ``_layout_for_linked_year`` +
``_slice_field``) on 1989 / 1995 / 2002 / 2003[DEFLATE64] / 2004 —
cohort-year == the cohort year for every sampled record — plus the
2005 regression (selection byte-identical to the ``"DENOM"`` rule).
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import pytest

_SPEC_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
if str(_SPEC_DIR) not in sys.path:
    sys.path.insert(0, str(_SPEC_DIR))

from parse_linked_year import (  # noqa: E402
    _find_denomplus_member,
    _layout_for_linked_year,
    iter_parsed_records,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
_HAS_7Z = shutil.which("7z") is not None


# --------------------------------------------------------------------------
# Tier 0: synthetic archives — per-era resolution + fail-closed negatives
# --------------------------------------------------------------------------

def _make_zip(tmp_path: Path, members: list[str]) -> Path:
    """Build a tiny real .zip with the given member names (1-byte each)."""
    zp = tmp_path / "probe.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for m in members:
            zf.writestr(m, b"x")
    return zp


# (era label, member set, expected den member) — the real NCHS
# cohort-linked member-naming conventions, probed at the DO step 5a
# PRE-FLIGHT (2026-05-19T05:00:00Z).
_ERA_MEMBERS = [
    ("1983-1991", ["LinkCO83USnum.dat", "LinkCO83USden.dat"], "LinkCO83USden.dat"),
    (
        "1995-2002 (mixed-case)",
        ["LinkCO95USDen.dat", "LinkCO95USNum.dat", "LinkCO95USUnl.dat"],
        "LinkCO95USDen.dat",
    ),
    (
        "1995-2002 (upper)",
        ["LinkCO02USDEN.dat", "LinkCO02USNUM.dat", "LinkCO02USUNL.dat"],
        "LinkCO02USDEN.dat",
    ),
    (
        "2003",
        ["VS03LKBC.USDENPUB", "VS03LKBC.USNUMPUB", "VS03LKBC.USUNMPUB"],
        "VS03LKBC.USDENPUB",
    ),
    (
        "2004 / 2005+ (DENOM rule)",
        ["VS04LKBC.USNUMPUB", "VS04LKBC.DUSDENOM", "VS04LKBC.USUNMPUB"],
        "VS04LKBC.DUSDENOM",
    ),
]


@pytest.mark.parametrize("label,members,expected", _ERA_MEMBERS,
                         ids=[e[0] for e in _ERA_MEMBERS])
def test_tier0_denmember_resolves_per_era(tmp_path, label, members, expected):
    zp = _make_zip(tmp_path, members)
    assert _find_denomplus_member(zp) == expected, label


@pytest.mark.parametrize(
    "members",
    [
        ["VS04LKBC.USNUMPUB", "VS04LKBC.DUSDENOM", "VS04LKBC.USUNMPUB"],
        ["VS05LKBC.DUSDENOM", "VS05LKBC.USNUMPUB", "VS05LKBC.USUNMPUB"],
    ],
    ids=["2004", "2005"],
)
def test_tier0_2004_2005_resolved_by_unchanged_DENOM_rule(tmp_path, members):
    # Regression lock: the canonical 2004/2005 selection MUST still be
    # the member containing "DENOM" (the pre-broadening rule). The
    # broadening only ADDS a fallback for the 1983-2003 cohort members
    # whose names contain "DEN" but not "DENOM"; it must not change the
    # 2004/2005 result (§9-#7-safe, behavior-preserving).
    zp = _make_zip(tmp_path, members)
    got = _find_denomplus_member(zp)
    assert "DENOM" in got.upper(), got


@pytest.mark.parametrize(
    "members",
    [
        pytest.param(["LinkCO83USnum.dat", "LinkCO83USUnl.dat"], id="num+unl-only"),
        pytest.param(["VS03LKBC.USNUMPUB", "VS03LKBC.USUNMPUB"], id="2003-num+unl-only"),
        pytest.param([], id="empty-archive"),
        pytest.param(
            ["LinkCO95USDen.dat", "LinkCO95USDEN2.dat", "LinkCO95USNum.dat"],
            id="ambiguous-two-DEN",
        ),
    ],
)
def test_tier0_failclosed_negative(tmp_path, members):
    """L3: a den-absent or ambiguous archive must RAISE, never silently
    pick a wrong member (§2 fail-closed; §9-#4 — the test discriminates,
    it is not a rubber-stamp)."""
    zp = _make_zip(tmp_path, members)
    with pytest.raises(RuntimeError):
        _find_denomplus_member(zp)


# --------------------------------------------------------------------------
# Tier 1: real cohort data — the real iter_parsed_records end-to-end path
# --------------------------------------------------------------------------

def _cohort_year_field(fields) -> str:
    names = {f[0] for f in fields}
    for nm in ("BIRYR", "DOB_YY"):
        if nm in names:
            return nm
    raise AssertionError(f"no cohort-year anchor in {sorted(names)[:8]}")


# (year, zip name, expected den member, needs_7z)
_TIER1 = [
    (1989, "LinkCO89.zip", "LinkCO89USden.dat", False),
    (1995, "LinkCO95US.zip", "LinkCO95USDen.dat", False),
    (2002, "LinkCO02US.zip", "LinkCO02USDEN.dat", False),
    (2003, "LinkCO03US.zip", "VS03LKBC.USDENPUB", True),   # DEFLATE64
    (2004, "LinkCO04US.zip", "VS04LKBC.DUSDENOM", False),
]


@pytest.mark.parametrize("year,zipname,expect_den,needs_7z", _TIER1,
                         ids=[f"{y}" for y, *_ in _TIER1])
def test_tier1_denmember_and_denplus_parse(year, zipname, expect_den, needs_7z):
    zp = LINKED_RAW_DIR / zipname
    if not zp.exists():
        pytest.skip(f"raw cohort zip absent (gitignored, out-of-tree): {zipname}")
    if needs_7z and not _HAS_7Z:
        pytest.skip("7z absent — required for the 2003 DEFLATE64 member")

    # the broadened finder resolves the era's den member uniquely
    assert _find_denomplus_member(zp) == expect_den

    # the real end-to-end parse path (finder + iter_lines_from_zip,
    # which auto-shells to 7z for the 2003 DEFLATE64 member, +
    # _layout_for_linked_year + _slice_field): every sampled record
    # decodes with the cohort-year anchor == the cohort year, which
    # jointly proves member-resolution + reclen + ASCII + alignment.
    reclen, birth, death = _layout_for_linked_year(year)
    yf = _cohort_year_field(birth + death)
    rows = list(iter_parsed_records(zp, year, max_rows=200))
    assert len(rows) == 200, f"{zipname}: only {len(rows)} records parsed"
    assert {str(r[yf]).strip() for r in rows} == {str(year)}, (
        f"{zipname}: {yf} != {year} (member/reclen/encoding/alignment)"
    )


def test_tier1_2005_regression_unchanged():
    """The canonical 2005-2015 path must be byte-identical: the 2005
    den member still resolves via the unchanged "DENOM" rule (DO step
    5a must not perturb the shipped v3 2005-2023 product)."""
    zp = LINKED_RAW_DIR / "LinkCO05US.zip"
    if not zp.exists():
        pytest.skip("raw 2005 zip absent (gitignored, out-of-tree)")
    got = _find_denomplus_member(zp)
    assert got == "VS05LKBC.DUSDENOM"
    assert "DENOM" in got.upper()
