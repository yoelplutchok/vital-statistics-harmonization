"""DESIGN: tracks-current-state

C8.18 DO step 5c-ii-a SMOKE — the **1995-2002 cohort birth-side map** in
``harmonize_linked_v3._harmonize_cohort_1995_2002``: the 1989-revision
sibling of the 5c-i-verified 1989-1991 reference era (same raw
field-name family + recode set as natality V2 1990-2002 == the 5c-i
1989-1991 map), with the documented per-era deltas — ``NPREVIST`` (not
``NPREVIS``); NO ``DFEDUC`` on the 1995-2002 birth section
(``father_education_cat4`` conservatively null); ``RECWT`` present
(``record_weight`` float64; the 1989-1991 era had none); the within_era
ICD-9 (cohort birth-year 1995-1998) vs ICD-10 (1999-2002) split keyed
on cohort birth year (§15.D DO step 1; DECISION_LOG 2026-05-17T05:30Z +
2026-05-19T11:00Z); NO ``MANNER`` (``manner_of_death`` null).

§15.D DO step 5c-ii was decomposed → **5c-ii-a / 5c-ii-b** at the
Convention-3 PRE-FLIGHT snapshot (PRE_FLIGHT_LOG 2026-05-19T14:00:00Z;
the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii precedent; §2 cheap-before-
expensive / §9-#8): 1995-2002 = the 1989-rev low-risk sibling of the
verified 1989-1991 (this harness); 2003 + 2004 = the 2003-rev
transition (5c-ii-b, its own SMOKE'd sub-step); the keyless 1983-1988
``link_segment`` encoding = 5c-iii.

Sibling of the 3a/3b/4a/4b/4c/5a/5b/5c-i cohort smokes; kept separate
so each sub-step stays independently re-runnable (the C8.18 DO
sub-step-isolation precedent). DO step 5c-ii-a adds (to
``harmonize_linked_v3``) ``_harmonize_cohort_1995_2002`` (NEW) + a
2-line ``if era == "1995_2002": return …`` dispatch prepended in
``_harmonize_cohort_batch``; the existing 5c-i 1989-1991 inline body +
the 2005+ body are byte-untouched (the 1995-2002 branch fires only for
1995 ≤ year ≤ 2002 → the canonical v3 2005-2023 path AND the
5c-i-verified 1989-1991 path byte-identical; §9-#7-safe). The parser
``_layout_for_linked_year`` / ``_numerator_layout_for_linked_year``
dispatchers are NOT touched (the parser already handles 1995-2002 via
DO step 4a/5a), so this harness adds NO new-year parser ``pytest.raises``
pin (the L17 stale-pin class does not apply here; the ONE 5c-i stale
pin — its ``test_tier0_unimplemented_cohort_eras_failclosed`` 1995/2002
rows — is fixed by a minimal ``tracks-current-state`` Edit bundled in
the SAME 5c-ii-a commit per §4.2.1/Convention-2/L17).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants —
the harmonized batch schema == ``OUT_SCHEMA``; the ICD-9/ICD-10 cause
columns populate per the cohort-birth-year split with the OTHER pair
null; the 1989-rev recodes are byte-identical to the natality V1-core
siblings (H7, asserted by feeding the SAME array to both); the
per-era deltas (RECWT→record_weight present; father_education_cat4
null; manner_of_death null) hold; 2003/2004 (5c-ii-b) + 1983-1988
(5c-iii) still RAISE NotImplementedError (fail-closed L3); the
5c-i-verified 1989-1991 path is unperturbed (regression-lock). No
mutable annotation value is pinned (planted synthetic inputs are
fixed; reclens/field names are fixed NCHS facts).

Tier 0 (synthetic, always runs): the cohort-birth-year ICD split
(1996 ICD-9 / 2000 ICD-10) end-to-end; the deltas; the fail-closed
negatives; the 1989-1991 regression-lock; the H7 recode equivalence.

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): real ``LinkCO95US.zip`` (cohort 1995, ICD-9) +
``LinkCO99US.zip`` (cohort 1999, ICD-10) parsed via
``iter_parsed_records`` then harmonized — schema == ``OUT_SCHEMA``;
the ICD split holds 100%; ``infant_death`` (AGED-derived) ⟺
``MATCHS == 1`` row-for-row (the independent §7-#13 cross-check; the
den-plus linked-infant-death code is uniformly MATCHS==1 across the
1989-1991 + 1995-2002 eras — real-data-verified, PRE_FLIGHT_LOG
ADDENDUM 2026-05-19T15:00:00Z); ``record_weight`` a non-null float.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pyarrow as pa
import pytest

_IMPORT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
_HARM_DIR = Path(__file__).resolve().parents[1] / "scripts" / "03_harmonize"
for _d in (_IMPORT_DIR, _HARM_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from field_specs import (  # noqa: E402
    LINKED_BIRTH_1989_1991_FIELDS,
    LINKED_BIRTH_1995_2002_FIELDS,
    LINKED_DEATH_1989_1991_FIELDS,
    LINKED_DEATH_1995_2002_FIELDS,
)
from parse_linked_year import iter_parsed_records  # noqa: E402

# ``_harmonize_cohort_1995_2002`` is NEW at DO step 5c-ii-a — importing
# it BEFORE the DO makes this harness fail collection (RED), proving it
# genuinely exercises the 5c-ii-a code (§9-#9 / L3, not a rubber-stamp).
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _harmonize_batch,
    _harmonize_cohort_1995_2002,
    _dmeduc_years_to_cat4,
    _mrace_detail_to_bridged4,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# synthetic batch builder — shaped exactly like the parser's 1995-2002
# denominator-plus output (every LINKED_BIRTH/_DEATH_1995_2002 field as a
# string column + an int ``year`` column the parser injects)
# --------------------------------------------------------------------------

def _synthetic_1995_2002_batch(planted: list[dict[str, str]]) -> pa.RecordBatch:
    field_names = (
        [f[0] for f in LINKED_BIRTH_1995_2002_FIELDS]
        + [f[0] for f in LINKED_DEATH_1995_2002_FIELDS]
    )
    cols: dict[str, list] = {name: [] for name in field_names}
    years: list[int] = []
    for row in planted:
        for name in field_names:
            cols[name].append(row.get(name, ""))
        years.append(int(row["year"]))
    arrays = [pa.array(cols[n], type=pa.string()) for n in field_names]
    arrays.append(pa.array(years, type=pa.int64()))
    return pa.RecordBatch.from_arrays(arrays, names=field_names + ["year"])


def _synthetic_1989_1991_batch(planted: list[dict[str, str]]) -> pa.RecordBatch:
    field_names = (
        [f[0] for f in LINKED_BIRTH_1989_1991_FIELDS]
        + [f[0] for f in LINKED_DEATH_1989_1991_FIELDS]
    )
    cols: dict[str, list] = {name: [] for name in field_names}
    years: list[int] = []
    for row in planted:
        for name in field_names:
            cols[name].append(row.get(name, ""))
        years.append(int(row["year"]))
    arrays = [pa.array(cols[n], type=pa.string()) for n in field_names]
    arrays.append(pa.array(years, type=pa.int64()))
    return pa.RecordBatch.from_arrays(arrays, names=field_names + ["year"])


# survivor (MATCHS=3, AGED blank) + linked infant death (AGED + cause)
def _two_row_1995_2002(year: int, ucod: str, ucodr: str) -> pa.RecordBatch:
    return _synthetic_1995_2002_batch([
        {  # survivor
            "year": str(year), "MATCHS": "3", "BIRYR": str(year),
            "RESSTATB": "1", "DMAGE": "28", "ORMOTH": "0", "MRACE": "01",
            "DMEDUC": "16", "DMAR": "1", "CSEX": "1", "DPLURAL": "1",
            "DBIRWT": "3500", "GESTAT": "40", "MONPRE": "02",
            "NPREVIST": "13", "DFAGE": "30", "PLDEL": "1", "BIRATTND": "1",
            "DLIVORD": "01", "DTOTORD": "01", "FMAPS": "09",
            "ORFATH": "0", "RECWT": "1.000000",
        },
        {  # linked infant death
            "year": str(year), "MATCHS": "1", "BIRYR": str(year),
            "RESSTATB": "1", "DMAGE": "18", "ORMOTH": "1", "MRACE": "02",
            "DMEDUC": "10", "DMAR": "2", "CSEX": "2", "DPLURAL": "1",
            "DBIRWT": "0980", "GESTAT": "27", "MONPRE": "00",
            "NPREVIST": "02", "DFAGE": "21", "PLDEL": "1", "BIRATTND": "1",
            "DLIVORD": "02", "DTOTORD": "02", "FMAPS": "03",
            "ORFATH": "1", "RECWT": "1.487213",
            "AGED": "021", "AGER5": "3", "UCOD": ucod, "UCODR": ucodr,
        },
    ])


# --------------------------------------------------------------------------
# Tier 0: _cohort_era partition (regression-lock; unchanged by 5c-ii-a)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [1995, 1996, 1998, 1999, 2000, 2002])
def test_tier0_1995_2002_cohort_era(year):
    assert _cohort_era(year) == "1995_2002"


# --------------------------------------------------------------------------
# Tier 0: cohort-birth-year ICD-9 (1995-1998) vs ICD-10 (1999-2002) split
# --------------------------------------------------------------------------

def test_tier0_cohort_1996_icd9_end_to_end():
    """Cohort 1996 = ICD-9 era: underlying_cause_icd9 / cause_recode_61
    carry the signal; underlying_cause_icd10 / cause_recode_130 NULL
    (§15.D DO step 1 default-null + revision-tagged, keyed on cohort
    birth year ≤ 1998)."""
    out = _harmonize_batch(_two_row_1995_2002(1996, "7980", "054"), 1996)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == 2
    d = out.to_pydict()

    # birth-side anchors via the natality 1989-rev sibling recodes
    assert d["data_year"] == [1996, 1996]
    assert d["certificate_revision"] == ["unrevised_1989", "unrevised_1989"]
    assert d["maternal_age"] == [28, 18]
    assert d["infant_sex"] == ["M", "F"]
    assert d["maternal_race_bridged"] == [1, 2]
    assert d["maternal_education_cat4"] == ["ba_plus", "lt_hs"]   # 16, 10 yrs
    assert d["maternal_hispanic"] == [False, True]                # ORMOTH 0,1
    assert d["birthweight_grams"] == [3500, 980]
    assert d["marital_status"] == [1, 2]
    assert d["live_birth_order_recode"] == [1, 2]
    assert d["prenatal_visits"] == [13, 2]    # NPREVIST (the 1995-2002 delta)

    # per-era deltas vs the 5c-i 1989-1991 map
    assert d["record_weight"] == [1.0, pytest.approx(1.487213)]   # RECWT present
    assert d["father_education_cat4"] == [None, None]             # no DFEDUC
    assert d["manner_of_death"] == [None, None]                   # no MANNER
    # composite blocks conservatively null (soft-flag (gg) DO step 6)
    assert d["smoking_any_during_pregnancy"] == [None, None]
    assert d["delivery_method_recode"] == [None, None]

    # death-side: the ICD-9 within_era split
    assert d["infant_death"] == [False, True]
    assert d["age_at_death_days"] == [None, 21]
    assert d["underlying_cause_icd9"] == [None, "7980"]
    assert d["cause_recode_61"] == [None, 54]
    assert d["underlying_cause_icd10"] == [None, None]   # NULL for ICD-9 era
    assert d["cause_recode_130"] == [None, None]         # NULL for ICD-9 era


def test_tier0_cohort_2000_icd10_end_to_end():
    """Cohort 2000 = ICD-10 era: the INVERSE — underlying_cause_icd10 /
    cause_recode_130 carry the signal; the ICD-9 columns NULL."""
    out = _harmonize_batch(_two_row_1995_2002(2000, "P073", "115"), 2000)
    assert out.schema.equals(OUT_SCHEMA)
    d = out.to_pydict()
    assert d["data_year"] == [2000, 2000]
    assert d["certificate_revision"] == ["unrevised_1989", "unrevised_1989"]
    assert d["infant_death"] == [False, True]
    assert d["underlying_cause_icd10"] == [None, "P073"]   # ICD-10 populated
    assert d["cause_recode_130"] == [None, 115]
    assert d["underlying_cause_icd9"] == [None, None]      # NULL for ICD-10 era
    assert d["cause_recode_61"] == [None, None]            # NULL for ICD-10 era
    assert d["record_weight"] == [1.0, pytest.approx(1.487213)]


@pytest.mark.parametrize("year", [1995, 1998])
def test_tier0_icd9_subera_boundary(year):
    out = _harmonize_batch(_two_row_1995_2002(year, "7670", "049"), year)
    d = out.to_pydict()
    assert d["underlying_cause_icd9"][1] == "7670"
    assert d["underlying_cause_icd10"][1] is None


@pytest.mark.parametrize("year", [1999, 2002])
def test_tier0_icd10_subera_boundary(year):
    out = _harmonize_batch(_two_row_1995_2002(year, "Q900", "118"), year)
    d = out.to_pydict()
    assert d["underlying_cause_icd10"][1] == "Q900"
    assert d["underlying_cause_icd9"][1] is None


# --------------------------------------------------------------------------
# Tier 0: fail-closed — the keyless 1983-1988 (5c-iii) still RAISES
# (L17 tracks-current-state: 2003/2004 IMPLEMENTED at 5c-ii-b — the
# pins trimmed in the SAME 5c-ii-b commit per §4.2.1/Convention-2/L17)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [1983, 1985, 1988])
def test_tier0_unimplemented_eras_still_failclosed(year):
    """L3 / §2 fail-closed: 5c-ii-a implements 1995-2002; 5c-ii-b adds
    2003 + 2004 (the 2003-rev transition). The keyless 1983-1988
    link_segment encoding (5c-iii) MUST still RAISE NotImplementedError
    so a premature DO step 6 on those years halts loudly rather than
    silently mis-harmonizing."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([year], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises(NotImplementedError):
        _harmonize_batch(batch, year)


def test_tier0_direct_function_rejects_non_1995_2002():
    """``_harmonize_cohort_1995_2002`` is era-scoped; calling it on a
    non-1995-2002 year is a programming error (the dispatch in
    ``_harmonize_cohort_batch`` is the only sanctioned entry) — it must
    NOT silently mis-harmonize a wrong-era batch."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([1990], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises((ValueError, AssertionError)):
        _harmonize_cohort_1995_2002(batch, 1990)


# --------------------------------------------------------------------------
# Tier 0: the 5c-i-verified 1989-1991 path is UNPERTURBED (regression-lock)
# --------------------------------------------------------------------------

def test_tier0_1989_1991_regression_unperturbed():
    """5c-ii-a is purely additive; the 5c-i 1989-1991 inline body is
    byte-untouched. A planted 1990 batch must still harmonize exactly as
    5c-i did (cert_rev unrevised_1989; ICD-9 default-null; the
    AGED-derived infant_death)."""
    batch = _synthetic_1989_1991_batch([
        {
            "year": "1990", "MATCHS": "1", "BIRYR": "1990", "RESSTATB": "1",
            "DMAGE": "24", "ORMOTH": "0", "MRACE": "01", "DMEDUC": "12",
            "DMAR": "1", "CSEX": "1", "DPLURAL": "1", "DBIRWT": "1100",
            "GESTAT": "29", "MONPRE": "01", "NPREVIS": "04", "DFAGE": "26",
            "PLDEL": "1", "BIRATTND": "1", "DLIVORD": "01", "DTOTORD": "01",
            "AGED": "008", "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
        },
    ])
    out = _harmonize_batch(batch, 1990)
    assert out.schema.equals(OUT_SCHEMA)
    d = out.to_pydict()
    assert d["certificate_revision"] == ["unrevised_1989"]
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd9"] == ["7980"]
    assert d["cause_recode_61"] == [54]
    assert d["underlying_cause_icd10"] == [None]
    assert d["cause_recode_130"] == [None]


# --------------------------------------------------------------------------
# Tier 0: H7 sibling-parity — the 1995-2002 recodes == natality V1-core
# --------------------------------------------------------------------------

def test_tier0_h7_sibling_parity_recodes():
    import importlib

    v1 = importlib.import_module("harmonize_v1_core")
    educ_in = pa.array([0, 8, 11, 12, 13, 15, 16, 17, 99, None], type=pa.int16())
    assert _dmeduc_years_to_cat4(educ_in).to_pylist() == \
        v1._dmeduc_years_to_cat4(educ_in).to_pylist()
    race_in = pa.array([1, 2, 3, 4, 8, 9, 18, 68, 77, None], type=pa.int16())
    assert _mrace_detail_to_bridged4(race_in).to_pylist() == \
        v1._mrace_detail_to_bridged4(race_in).to_pylist()


# --------------------------------------------------------------------------
# Tier 1: real LinkCO95 (ICD-9) + LinkCO99 (ICD-10) parsed then harmonized
# --------------------------------------------------------------------------

def _real_parse_harmonize(zip_name: str, year: int):
    zp = LINKED_RAW_DIR / zip_name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {zip_name} absent (gitignored, out-of-tree)")
    rows = list(iter_parsed_records(zp, year, max_rows=400))
    assert rows, "no parsed rows"
    assert all("link_segment" not in r for r in rows), (
        "1995-2002 is a single-member denominator-plus (no link_segment; "
        "the keyless link_segment is 1983-1988 only)"
    )
    batch = pa.RecordBatch.from_pylist(rows)
    out = _harmonize_batch(batch, year)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == len(rows)
    return rows, out.to_pydict()


def _assert_real_common(rows, d, year):
    assert set(d["data_year"]) == {year}
    assert set(d["certificate_revision"]) == {"unrevised_1989"}
    ages = [a for a in d["maternal_age"] if a is not None]
    assert ages and min(ages) >= 10 and max(ages) <= 54
    assert set(d["infant_sex"]) <= {"M", "F", None}
    # RECWT present on the 1995-2002 den-plus → record_weight non-null float
    rw = [w for w in d["record_weight"] if w is not None]
    assert rw, "record_weight all-null (RECWT must parse for 1995-2002)"
    assert all(isinstance(w, float) and w >= 1.0 for w in rw)
    # INDEPENDENT §7-#13 cross-check: infant_death is derived from
    # AGED-non-blank; MATCHS is the SEPARATE NCHS match-status field. The
    # den-plus linked-infant-death code is uniformly **MATCHS == 1**
    # (matched birth↔infant-death) across BOTH the 1989-1991 and the
    # 1995-2002 eras (real-data-verified, PRE_FLIGHT_LOG ADDENDUM
    # 2026-05-19T15:00:00Z); the SURVIVOR code is era-dependent (3 for
    # 1989-1991, 2 for 1995-2002 per field_specs.py:1222) — so the
    # imprecise `m in {1,2}` framing would sweep in 1995-2002 survivors.
    # On real cohort data the two signals MUST agree row-for-row.
    matchs = [str(r.get("MATCHS", "")).strip() for r in rows]
    death_by_matchs = [m == "1" for m in matchs]
    death_by_aged = [a is not None for a in d["age_at_death_days"]]
    assert d["infant_death"] == death_by_aged, "infant_death must == AGED-non-blank"
    assert death_by_aged == death_by_matchs, (
        "infant_death (AGED-derived) disagrees with MATCHS==1 on real "
        f"{year} data — §7-#13 halt. AGED={sum(death_by_aged)}, "
        f"MATCHS1={sum(death_by_matchs)}"
    )


def test_tier1_real_1995_icd9():
    rows, d = _real_parse_harmonize("LinkCO95US.zip", 1995)
    _assert_real_common(rows, d, 1995)
    # cohort 1995 = ICD-9 era: the ICD-10 cause columns are 100% null;
    # the ICD-9 columns carry the signal for the death rows.
    assert all(v is None for v in d["underlying_cause_icd10"])
    assert all(v is None for v in d["cause_recode_130"])
    for is_death, icd9 in zip(d["infant_death"], d["underlying_cause_icd9"]):
        if is_death:
            assert icd9 is not None and icd9.strip() != "", (
                "1995 infant-death row missing ICD-9 underlying cause"
            )


def test_tier1_real_1999_icd10():
    rows, d = _real_parse_harmonize("LinkCO99US.zip", 1999)
    _assert_real_common(rows, d, 1999)
    # cohort 1999 = ICD-10 era: the INVERSE — the ICD-9 cause columns
    # are 100% null; the ICD-10 columns carry the signal.
    assert all(v is None for v in d["underlying_cause_icd9"])
    assert all(v is None for v in d["cause_recode_61"])
    for is_death, icd10 in zip(d["infant_death"], d["underlying_cause_icd10"]):
        if is_death:
            assert icd10 is not None and icd10.strip() != "", (
                "1999 infant-death row missing ICD-10 underlying cause"
            )
