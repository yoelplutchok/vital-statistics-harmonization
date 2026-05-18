"""DESIGN: tracks-current-state

C8.18 DO step 5c-ii-b SMOKE — the **2003 + 2004 cohort birth-side maps**
in ``harmonize_linked_v3._harmonize_cohort_2003_2004``: the
2003-revision dual-certificate transition (the natality V1-core
``is_2003revised`` analog). One function handles BOTH 2003 + 2004 (ONE
§15.D sub-step, ONE cert revision; the 2003-vs-2004 deltas are pure
raw-name aliasing — ``MAGER41``↔``MAGER``; ``DBWT``↔``BRTHWGT``; the
death match-status ``MATCHS``↔``FLGND`` — handled via
``_get_col_optional`` name-fallback, the natality V1-core single
``is_2003revised`` branch pattern; §9-#8 PRE_FLIGHT_LOG
2026-05-19T20:00:00Z (B)).

The 2003-rev cohort birth section ALIASES the cohort raw names onto the
natality V1-core 2003-rev recodes (H7 sibling-parity — reuse
``_meduc_to_cat4`` / ``_meduc_rec_to_cat4`` / ``_month_to_trimester`` /
``_fagerec11_to_cat`` / ``_pldel_to_facility`` / ``_mrace_detail_to_bridged4``
+ the NEW ``_mager41_to_age`` byte-identical to the natality V1-core
inline MAGER41 conversion; do NOT re-derive). Dual-cert handled
faithfully via the natality V1-core coalesce (``maternal_education_cat4``
= ``if_else(is_null(_meduc_to_cat4(MEDUC)), _meduc_rec_to_cat4(MEDUC_REC),
…)``; ``prenatal_care_start_month`` = ``if_else(is_null(PRECARE), MPCB,
PRECARE)``; ``certificate_revision`` = ``has_meduc``/``has_mrace`` →
revised_2003 / unrevised_1989 / unknown). All ICD-10 (cohort birth-year
2003/2004 ≥ 1999 → ``underlying_cause_icd10``/``cause_recode_130``
populated; the ICD-9 cols null — the 5c-i resolved shape, §15.D DO
step 1). ``MANNER`` present → ``manner_of_death`` (NEW vs the 1995-2002
era which had none); ``RECWT`` present → ``record_weight``.

§15.D DO step 5c-ii was decomposed → 5c-ii-a / 5c-ii-b at the
Convention-3 snapshot (PRE_FLIGHT_LOG 2026-05-19T14:00:00Z; the
5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii precedent; §2/§9-#8): 1995-2002 =
the 1989-rev sibling (5c-ii-a, shipped); 2003 + 2004 = the 2003-rev
transition (this harness); the keyless 1983-1988 ``link_segment``
encoding = 5c-iii.

Sibling of the 3a/3b/4a/4b/4c/5a/5b/5c-i/5c-ii-a cohort smokes; kept
separate so each sub-step stays independently re-runnable (the C8.18
DO sub-step-isolation precedent). DO step 5c-ii-b adds (to
``harmonize_linked_v3``) ``_mager41_to_age`` (NEW) + ``_harmonize_cohort_2003_2004``
(NEW) + a 2-line ``if era in ("2003","2004"): return …`` dispatch
prepended in ``_harmonize_cohort_batch``; the 5c-i 1989-1991 inline
body + the 5c-ii-a ``_harmonize_cohort_1995_2002`` + the 2005+ body
are byte-untouched (the 2003/2004 branch fires only for year ∈
{2003,2004} → the canonical v3 2005-2023 path + the 5c-i 1989-1991 +
the 5c-ii-a 1995-2002 paths byte-identical; §9-#7-safe). The parser
dispatchers are NOT touched (the parser already handles 2003/2004 via
DO step 4b/4c/5a). The 2 stale 2003/2004 ``NotImplementedError`` pins
in the 5c-ii-a + 5c-i harnesses are fixed by minimal
``tracks-current-state`` Edits bundled in the SAME 5c-ii-b commit per
§4.2.1/Convention-2/L17.

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants —
the harmonized batch schema == ``OUT_SCHEMA``; the dual-cert coalesce +
the MAGER41→single-year recode + the ICD-10-only cause shape + the
per-era deltas (record_weight present; manner_of_death present;
gestational_age_weeks_source == "combined"; father_age_cat_from_rec11
populated) hold; the 2003-rev recodes are byte-identical to the
natality V1-core siblings (H7); the 1992-1994 permanent gap / pre-1983
still RAISES ValueError (fail-closed L3 — the keyless 1983-1988
IMPLEMENTED at 5c-iii; L17 tracks-current-state, the `[1983,1985,1988]`
keyless pin reframed in the 5c-iii commit per §4.2.1/Convention-2); the
5c-i-verified 1989-1991 + the 5c-ii-a-verified 1995-2002 paths are
unperturbed (regression-lock). No mutable annotation value is pinned (planted
synthetic inputs are fixed; reclens/field names are fixed NCHS facts).

Tier 0 (synthetic, always runs): the 2003/2004 ``_cohort_era``
partition; the S-rev + A-rev dual-cert end-to-end; the MAGER41→age
recode; the all-ICD-10 cause shape; the per-era deltas; the
fail-closed negatives; the 1989-1991 + 1995-2002 regression-locks;
the H7 recode equivalence.

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): real ``LinkCO03US.zip`` (cohort 2003, DEFLATE64) +
``LinkCO04US.zip`` (cohort 2004, DEFLATE) parsed via
``iter_parsed_records`` then harmonized — schema == ``OUT_SCHEMA``;
all cause ICD-10 (the ICD-9 cols 100% null); ``infant_death``
(AGED-derived) ⟺ match-status == "1" row-for-row (the independent
§7-#13 cross-check; the den-plus linked-infant-death code is
uniformly ``MATCHS``/``FLGND`` == "1" across ALL eras —
real-data-verified, PRE_FLIGHT_LOG 2026-05-19T20:00:00Z (A));
``record_weight`` a non-null float; ``manner_of_death`` present.
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
    LINKED_BIRTH_2003_FIELDS,
    LINKED_BIRTH_2004_FIELDS,
    LINKED_DEATH_2003_FIELDS,
    LINKED_DEATH_2004_FIELDS,
)
from parse_linked_year import iter_parsed_records  # noqa: E402

# ``_harmonize_cohort_2003_2004`` + ``_mager41_to_age`` are NEW at DO
# step 5c-ii-b — importing them BEFORE the DO makes this harness fail
# collection (RED), proving it genuinely exercises the 5c-ii-b code
# (§9-#9 / L3, not a rubber-stamp).
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _harmonize_batch,
    _harmonize_cohort_2003_2004,
    _mager41_to_age,
    _meduc_to_cat4,
    _meduc_rec_to_cat4,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# synthetic batch builders — shaped exactly like the parser's 2003 / 2004
# denominator-plus output (every LINKED_BIRTH/_DEATH_<yr> field as a string
# column + an int ``year`` column the parser injects)
# --------------------------------------------------------------------------

def _synthetic_batch(planted, birth_fields, death_fields) -> pa.RecordBatch:
    field_names = [f[0] for f in birth_fields] + [f[0] for f in death_fields]
    cols: dict[str, list] = {name: [] for name in field_names}
    years: list[int] = []
    for row in planted:
        for name in field_names:
            cols[name].append(row.get(name, ""))
        years.append(int(row["year"]))
    arrays = [pa.array(cols[n], type=pa.string()) for n in field_names]
    arrays.append(pa.array(years, type=pa.int64()))
    return pa.RecordBatch.from_arrays(arrays, names=field_names + ["year"])


def _synthetic_2003(planted) -> pa.RecordBatch:
    return _synthetic_batch(planted, LINKED_BIRTH_2003_FIELDS,
                            LINKED_DEATH_2003_FIELDS)


def _synthetic_2004(planted) -> pa.RecordBatch:
    return _synthetic_batch(planted, LINKED_BIRTH_2004_FIELDS,
                            LINKED_DEATH_2004_FIELDS)


# A 2003 S-rev (1989-unrevised) survivor + a linked infant death.
# S-rev → MEDUC/PRECARE/MBRACE blank; UMEDUC/MEDUC_REC/MPCB/MRACE/MRACEREC
# carry the values (the dual-cert coalesce + has_meduc/has_mrace cert-rev
# heuristic resolve it). All ICD-10 (cohort 2003 ≥ 1999).
def _rows_2003_srev():
    return [
        {  # survivor: MATCHS=2 (the 1995-2002/2003 survivor code), AGED blank
            "year": "2003", "DOB_YY": "2003", "REVISION": "S",
            "RESTATUS": "1", "MAGER41": "15", "MRACE": "01", "MRACEREC": "1",
            "MBRACE": "", "UMHISP": "0", "MAR": "1", "MEDUC": "",
            "UMEDUC": "16", "MEDUC_REC": "5", "LBO_REC": "1", "TBO_REC": "1",
            "PRECARE": "", "MPCB": "02", "UPREVIS": "13", "DPLURAL": "1",
            "SEX": "M", "COMBGEST": "40", "GESTREC3": "2", "DBWT": "3500",
            "APGAR5": "09", "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "04",
            "UFHISP": "0", "UFAGECOMB": "30", "MATCHS": "2",
        },
        {  # linked infant death: MATCHS=1, AGED + ICD-10 cause + MANNER
            "year": "2003", "DOB_YY": "2003", "REVISION": "S",
            "RESTATUS": "1", "MAGER41": "01", "MRACE": "02", "MRACEREC": "2",
            "MBRACE": "", "UMHISP": "1", "MAR": "2", "MEDUC": "",
            "UMEDUC": "10", "MEDUC_REC": "1", "LBO_REC": "2", "TBO_REC": "2",
            "PRECARE": "", "MPCB": "05", "UPREVIS": "02", "DPLURAL": "1",
            "SEX": "F", "COMBGEST": "27", "GESTREC3": "1", "DBWT": "0980",
            "APGAR5": "03", "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "03",
            "UFHISP": "1", "UFAGECOMB": "21", "MATCHS": "1",
            "AGED": "021", "AGER5": "3", "MANNER": "1",
            "UCOD": "P073", "UCODR130": "115", "RECWT": "1.487213",
        },
    ]


# --------------------------------------------------------------------------
# Tier 0: _cohort_era partition (regression-lock; unchanged by 5c-ii-b)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year,era", [(2003, "2003"), (2004, "2004")])
def test_tier0_2003_2004_cohort_era(year, era):
    assert _cohort_era(year) == era


# --------------------------------------------------------------------------
# Tier 0: 2003 S-rev (1989-unrevised) dual-cert end-to-end
# --------------------------------------------------------------------------

def test_tier0_2003_srev_end_to_end():
    out = _harmonize_batch(_synthetic_2003(_rows_2003_srev()), 2003)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == 2
    d = out.to_pydict()

    assert d["data_year"] == [2003, 2003]
    # S-rev: MEDUC blank + MRACE populated → unrevised_1989 (the natality
    # V1-core has_meduc/has_mrace dual-cert heuristic; H7).
    assert d["certificate_revision"] == ["unrevised_1989", "unrevised_1989"]
    # MAGER41 15 → 15+13 = 28 ; MAGER41 01 → 14 (the natality V1-core
    # inline MAGER41 conversion; H7).
    assert d["maternal_age"] == [28, 14]
    assert d["infant_sex"] == ["M", "F"]
    assert d["maternal_race_bridged"] == [1, 2]            # MRACE detail 01/02
    assert d["race_bridge_method"] == ["approximate_pre2003"] * 2
    # MEDUC blank → _meduc_to_cat4 null → fallback _meduc_rec_to_cat4:
    # MEDUC_REC 5 → ba_plus ; MEDUC_REC 1 → lt_hs (the dual-cert coalesce).
    assert d["maternal_education_cat4"] == ["ba_plus", "lt_hs"]
    assert d["maternal_hispanic"] == [False, True]         # UMHISP 0,1
    assert d["father_hispanic"] == [False, True]           # UFHISP 0,1
    assert d["marital_status"] == [1, 2]                   # MAR
    assert d["live_birth_order_recode"] == [1, 2]          # LBO_REC direct
    assert d["total_birth_order_recode"] == [1, 2]         # TBO_REC direct
    # PRECARE blank → fallback MPCB (2,5) → trimester 1st,2nd
    assert d["prenatal_care_start_month"] == [2, 5]
    assert d["prenatal_care_start_trimester"] == ["1st", "2nd"]
    assert d["prenatal_visits"] == [13, 2]                 # UPREVIS raw
    assert d["plurality_recode"] == [1, 1]                  # DPLURAL
    assert d["gestational_age_weeks"] == [40, 27]           # COMBGEST
    assert d["gestational_age_weeks_source"] == ["combined", "combined"]
    assert d["birthweight_grams"] == [3500, 980]            # DBWT
    assert d["apgar5"] == [9, 3]                            # APGAR5 raw
    assert d["father_age"] == [30, 21]                      # UFAGECOMB
    assert d["father_age_cat_from_rec11"] == ["25-29", "20-24"]  # FAGEREC11 04,03
    assert d["birth_facility"] == ["hospital", "hospital"]  # UBFACIL 1
    assert d["attendant_at_birth"] == [1, 1]               # ATTEND

    # per-era deltas vs the 5c-ii-a 1995-2002 map
    assert d["record_weight"] == [None, pytest.approx(1.487213)]  # survivor no RECWT planted
    assert d["manner_of_death"] == [None, 1]               # MANNER (NEW vs 1995-2002)
    # composite blocks conservatively null (soft-flag (gg) DO step 6)
    assert d["smoking_any_during_pregnancy"] == [None, None]
    assert d["delivery_method_recode"] == [None, None]
    assert d["preterm_recode3"] == [None, None]
    assert d["father_race_ethnicity_5"] == [None, None]
    assert d["father_education_cat4"] == [None, None]
    assert d["maternal_race_detail_15cat"] == [None, None]

    # death-side: ALL ICD-10 (cohort 2003 ≥ 1999; the 5c-i resolved shape)
    assert d["infant_death"] == [False, True]
    assert d["age_at_death_days"] == [None, 21]
    assert d["age_at_death_recode5"] == [None, 3]
    assert d["underlying_cause_icd10"] == [None, "P073"]
    assert d["cause_recode_130"] == [None, 115]
    assert d["underlying_cause_icd9"] == [None, None]      # NULL for ICD-10 era
    assert d["cause_recode_61"] == [None, None]            # NULL for ICD-10 era


# --------------------------------------------------------------------------
# Tier 0: 2003 A-rev (2003-revised) — MEDUC populated → revised_2003
# --------------------------------------------------------------------------

def test_tier0_2003_arev_cert_and_meduc():
    out = _harmonize_batch(_synthetic_2003([
        {
            "year": "2003", "DOB_YY": "2003", "REVISION": "A",
            "RESTATUS": "1", "MAGER41": "20", "MRACE": "01", "MRACEREC": "1",
            "MBRACE": "1", "UMHISP": "0", "MAR": "1", "MEDUC": "6",
            "UMEDUC": "", "MEDUC_REC": "", "LBO_REC": "1", "TBO_REC": "1",
            "PRECARE": "01", "MPCB": "", "UPREVIS": "12", "DPLURAL": "1",
            "SEX": "M", "COMBGEST": "39", "GESTREC3": "2", "DBWT": "3300",
            "APGAR5": "09", "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "05",
            "UFHISP": "0", "UFAGECOMB": "33", "MATCHS": "2",
        },
    ]), 2003)
    d = out.to_pydict()
    # A-rev: MEDUC nonblank → revised_2003 (H7 has_meduc heuristic)
    assert d["certificate_revision"] == ["revised_2003"]
    # MEDUC 6 → _meduc_to_cat4 → ba_plus (the revised path)
    assert d["maternal_education_cat4"] == ["ba_plus"]
    assert d["maternal_age"] == [33]                       # MAGER41 20 → 33
    # PRECARE 01 (revised) used directly (not MPCB) → trimester 1st
    assert d["prenatal_care_start_month"] == [1]
    assert d["prenatal_care_start_trimester"] == ["1st"]
    assert d["father_age_cat_from_rec11"] == ["30-34"]     # FAGEREC11 05


# --------------------------------------------------------------------------
# Tier 0: 2004 — MAGER (not MAGER41), BRTHWGT (not DBWT), FLGND (not MATCHS)
# --------------------------------------------------------------------------

def test_tier0_2004_end_to_end():
    out = _harmonize_batch(_synthetic_2004([
        {  # survivor
            "year": "2004", "DOB_YY": "2004", "REVISION": "S",
            "RESTATUS": "1", "MAGER": "16", "MRACE": "01", "MRACEREC": "1",
            "MBRACE": "", "UMHISP": "0", "MAR": "1", "MEDUC": "",
            "UMEDUC": "12", "MEDUC_REC": "3", "LBO_REC": "1", "TBO_REC": "1",
            "PRECARE": "", "MPCB": "03", "UPREVIS": "11", "DPLURAL": "1",
            "SEX": "M", "COMBGEST": "39", "GESTREC3": "2", "BRTHWGT": "3400",
            "APGAR5": "09", "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "06",
            "UFHISP": "0", "UFAGECOMB": "35", "FLGND": "2",
        },
        {  # linked infant death
            "year": "2004", "DOB_YY": "2004", "REVISION": "S",
            "RESTATUS": "1", "MAGER": "10", "MRACE": "03", "MRACEREC": "3",
            "MBRACE": "", "UMHISP": "0", "MAR": "2", "MEDUC": "",
            "UMEDUC": "11", "MEDUC_REC": "2", "LBO_REC": "3", "TBO_REC": "3",
            "PRECARE": "", "MPCB": "99", "UPREVIS": "99", "DPLURAL": "1",
            "SEX": "F", "COMBGEST": "30", "GESTREC3": "1", "BRTHWGT": "1100",
            "APGAR5": "06", "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "11",
            "UFHISP": "9", "UFAGECOMB": "99", "FLGND": "1",
            "AGED": "008", "AGER5": "3", "MANNER": "7",
            "UCOD": "Q913", "UCODR130": "130", "RECWT": "1.142857",
        },
    ]), 2004)
    assert out.schema.equals(OUT_SCHEMA)
    d = out.to_pydict()
    assert d["data_year"] == [2004, 2004]
    assert d["certificate_revision"] == ["unrevised_1989", "unrevised_1989"]
    assert d["maternal_age"] == [29, 23]                   # MAGER41-recode: 16→16+13=29, 10→10+13=23
    assert d["infant_sex"] == ["M", "F"]
    assert d["birthweight_grams"] == [3400, 1100]          # BRTHWGT
    assert d["maternal_education_cat4"] == ["hs_grad", "lt_hs"]  # MEDUC_REC 3,2
    assert d["father_age"] == [35, None]                   # UFAGECOMB 35; 99→null
    assert d["father_age_cat_from_rec11"] == ["35-39", None]  # FAGEREC11 06; 11→null
    assert d["prenatal_care_start_month"] == [3, 99]       # MPCB fallback
    assert d["prenatal_care_start_trimester"] == ["1st", "unknown"]  # 99→unknown
    # death-side ICD-10 (cohort 2004 ≥ 1999)
    assert d["infant_death"] == [False, True]
    assert d["underlying_cause_icd10"] == [None, "Q913"]
    assert d["cause_recode_130"] == [None, 130]
    assert d["underlying_cause_icd9"] == [None, None]
    assert d["manner_of_death"] == [None, 7]
    assert d["record_weight"] == [None, pytest.approx(1.142857)]


# --------------------------------------------------------------------------
# Tier 0: MAGER41 → single-year age recode edges (H7; the natality formula)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("code,expected", [
    (1, 14), (2, 15), (15, 28), (37, 50), (41, 54), (42, None), (99, None),
])
def test_tier0_mager41_to_age_edges(code, expected):
    out = _mager41_to_age(pa.array([code], type=pa.int16())).to_pylist()
    assert out == [expected]


def test_tier0_mager41_to_age_null_passthrough():
    out = _mager41_to_age(pa.array([None], type=pa.int16())).to_pylist()
    assert out == [None]


# --------------------------------------------------------------------------
# Tier 0: residual §2 fail-closed = the 1992-1994 gap / pre-1983
# (L17 tracks-current-state: 5c-iii IMPLEMENTED the keyless 1983-1988 —
# the `[1983,1985,1988]` NotImplementedError pin went stale; reframed
# in the SAME 5c-iii commit per §4.2.1/Convention-2/L17. ALL cohort
# eras 1983-1991 + 1995-2004 are now implemented; the genuine residual
# fail-closed is the `_cohort_era` ValueError raised UPSTREAM for the
# 1992-1994 permanent NCHS linkage gap / pre-1983.)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [1992, 1993, 1994, 1979])
def test_tier0_gap_pre1983_still_failclosed(year):
    """L3 / §2 fail-closed: 5c-iii implements the keyless 1983-1988
    link_segment encoding (the LAST unimplemented cohort era). NO
    NotImplementedError is raised for any real cohort year now; the
    residual fail-closed is the `_cohort_era` ValueError for the
    1992-1994 permanent NCHS linkage gap / pre-1983 — a premature DO
    step 6 on those years halts loudly rather than silently
    mis-harmonized through the 2005+ body."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([year], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises(ValueError):
        _harmonize_batch(batch, year)


def test_tier0_direct_function_rejects_non_2003_2004():
    """``_harmonize_cohort_2003_2004`` is era-scoped; calling it on a
    non-2003/2004 year is a programming error (the dispatch in
    ``_harmonize_cohort_batch`` is the only sanctioned entry) — it must
    NOT silently mis-harmonize a wrong-era batch."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([1990], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises((ValueError, AssertionError)):
        _harmonize_cohort_2003_2004(batch, 1990)


# --------------------------------------------------------------------------
# Tier 0: the 5c-i 1989-1991 + 5c-ii-a 1995-2002 paths UNPERTURBED
# --------------------------------------------------------------------------

def test_tier0_1989_1991_regression_unperturbed():
    """5c-ii-b is purely additive; the 5c-i 1989-1991 inline body is
    byte-untouched (the cohort branch fires only for year ∈ {2003,2004})."""
    from field_specs import (
        LINKED_BIRTH_1989_1991_FIELDS, LINKED_DEATH_1989_1991_FIELDS,
    )
    batch = _synthetic_batch([
        {
            "year": "1990", "MATCHS": "1", "BIRYR": "1990", "RESSTATB": "1",
            "DMAGE": "24", "ORMOTH": "0", "MRACE": "01", "DMEDUC": "12",
            "DMAR": "1", "CSEX": "1", "DPLURAL": "1", "DBIRWT": "1100",
            "GESTAT": "29", "MONPRE": "01", "NPREVIS": "04", "DFAGE": "26",
            "PLDEL": "1", "BIRATTND": "1", "DLIVORD": "01", "DTOTORD": "01",
            "AGED": "008", "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
        },
    ], LINKED_BIRTH_1989_1991_FIELDS, LINKED_DEATH_1989_1991_FIELDS)
    d = _harmonize_batch(batch, 1990).to_pydict()
    assert d["certificate_revision"] == ["unrevised_1989"]
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd9"] == ["7980"]
    assert d["cause_recode_61"] == [54]
    assert d["underlying_cause_icd10"] == [None]


def test_tier0_1995_2002_regression_unperturbed():
    """The 5c-ii-a 1995-2002 path is byte-untouched by 5c-ii-b."""
    from field_specs import (
        LINKED_BIRTH_1995_2002_FIELDS, LINKED_DEATH_1995_2002_FIELDS,
    )
    batch = _synthetic_batch([
        {
            "year": "1996", "MATCHS": "1", "BIRYR": "1996", "RESSTATB": "1",
            "DMAGE": "18", "ORMOTH": "1", "MRACE": "02", "DMEDUC": "10",
            "DMAR": "2", "CSEX": "2", "DPLURAL": "1", "DBIRWT": "0980",
            "GESTAT": "27", "MONPRE": "00", "NPREVIST": "02", "DFAGE": "21",
            "PLDEL": "1", "BIRATTND": "1", "DLIVORD": "02", "DTOTORD": "02",
            "FMAPS": "03", "ORFATH": "1", "RECWT": "1.487213",
            "AGED": "021", "AGER5": "3", "UCOD": "7980", "UCODR": "054",
        },
    ], LINKED_BIRTH_1995_2002_FIELDS, LINKED_DEATH_1995_2002_FIELDS)
    d = _harmonize_batch(batch, 1996).to_pydict()
    assert d["certificate_revision"] == ["unrevised_1989"]
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd9"] == ["7980"]          # cohort 1996 = ICD-9
    assert d["underlying_cause_icd10"] == [None]
    assert d["record_weight"] == [pytest.approx(1.487213)]


# --------------------------------------------------------------------------
# Tier 0: H7 sibling-parity — the 2003-rev recodes == natality V1-core
# --------------------------------------------------------------------------

def test_tier0_h7_sibling_parity_recodes():
    import importlib

    v1 = importlib.import_module("harmonize_v1_core")
    # _meduc_to_cat4 / _meduc_rec_to_cat4 byte-identical to natality V1-core
    meduc_in = pa.array([1, 2, 3, 4, 5, 6, 7, 8, 9, None], type=pa.int8())
    assert _meduc_to_cat4(meduc_in).to_pylist() == \
        v1._meduc_to_cat4(meduc_in).to_pylist()
    mrec_in = pa.array([1, 2, 3, 4, 5, 6, None], type=pa.int8())
    assert _meduc_rec_to_cat4(mrec_in).to_pylist() == \
        v1._meduc_rec_to_cat4(mrec_in).to_pylist()
    # _mager41_to_age byte-identical to the natality V1-core INLINE
    # is_2003revised MAGER41 conversion (code 1→14; codes 2-41→code+13;
    # 99|>41→null) — replicated here as the H7 reference.
    import pyarrow.compute as pc
    m = pa.array([1, 2, 15, 37, 41, 42, 99, None], type=pa.int16())
    ref = pc.if_else(pc.equal(m, 1), pa.scalar(14, type=pa.int16()),
                     pc.add(m, pa.scalar(13, type=pa.int16())))
    ref = pc.if_else(pc.or_(pc.equal(m, 99), pc.greater(m, 41)),
                     pa.scalar(None, type=pa.int16()), ref)
    assert _mager41_to_age(m).to_pylist() == ref.to_pylist()


# --------------------------------------------------------------------------
# Tier 1: real LinkCO03 (2003) + LinkCO04 (2004) parsed then harmonized
# --------------------------------------------------------------------------

def _real_parse_harmonize(zip_name: str, year: int):
    zp = LINKED_RAW_DIR / zip_name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {zip_name} absent (gitignored, out-of-tree)")
    rows = list(iter_parsed_records(zp, year, max_rows=600))
    assert rows, "no parsed rows"
    assert all("link_segment" not in r for r in rows), (
        "2003/2004 is a single-member denominator-plus (no link_segment; "
        "the keyless link_segment is 1983-1988 only)"
    )
    batch = pa.RecordBatch.from_pylist(rows)
    out = _harmonize_batch(batch, year)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == len(rows)
    return rows, out.to_pydict()


def _assert_real_common(rows, d, year, match_field):
    assert set(d["data_year"]) == {year}
    assert set(d["certificate_revision"]) <= {
        "unrevised_1989", "revised_2003", "unknown",
    }
    ages = [a for a in d["maternal_age"] if a is not None]
    assert ages and min(ages) >= 10 and max(ages) <= 60
    assert set(d["infant_sex"]) <= {"M", "F", None}
    assert set(d["gestational_age_weeks_source"]) <= {"combined", None}
    # RECWT present on the 2003/2004 den-plus → record_weight non-null float
    rw = [w for w in d["record_weight"] if w is not None]
    assert rw, "record_weight all-null (RECWT must parse for 2003/2004)"
    assert all(isinstance(w, float) and w >= 1.0 for w in rw)
    # ALL ICD-10 (cohort 2003/2004 ≥ 1999; the ICD-9 cols 100% null)
    assert all(v is None for v in d["underlying_cause_icd9"])
    assert all(v is None for v in d["cause_recode_61"])
    for is_death, icd10 in zip(d["infant_death"], d["underlying_cause_icd10"]):
        if is_death:
            assert icd10 is not None and icd10.strip() != "", (
                f"{year} infant-death row missing ICD-10 underlying cause"
            )
    # INDEPENDENT §7-#13 cross-check: infant_death is derived from
    # AGED-non-blank; the match-status field (MATCHS for 2003, FLGND for
    # 2004) is the SEPARATE NCHS field. The den-plus linked-infant-death
    # code is uniformly **match-status == "1"** across ALL cohort eras
    # (real-data-verified, PRE_FLIGHT_LOG 2026-05-19T20:00:00Z (A); the
    # SURVIVOR code is "2" for 1995-2002/2003/2004, "3" for 1989-1991 —
    # so the loose `m in {1,2}` would sweep in 2003/2004 survivors). On
    # real cohort data the two signals MUST agree row-for-row.
    ms = [str(r.get(match_field, "")).strip() for r in rows]
    death_by_match = [m == "1" for m in ms]
    death_by_aged = [a is not None for a in d["age_at_death_days"]]
    assert d["infant_death"] == death_by_aged, "infant_death must == AGED-non-blank"
    assert death_by_aged == death_by_match, (
        f"infant_death (AGED-derived) disagrees with {match_field}==1 on "
        f"real {year} data — §7-#13 halt. AGED={sum(death_by_aged)}, "
        f"{match_field}1={sum(death_by_match)}"
    )
    # MANNER present on the 2003/2004 den-plus death "plus" (NEW vs
    # 1995-2002) → manner_of_death non-null for at least the death rows
    mod_deaths = [
        m for m, dn in zip(d["manner_of_death"], death_by_aged) if dn
    ]
    if mod_deaths:
        assert any(m is not None for m in mod_deaths), (
            "manner_of_death all-null on death rows (MANNER must parse)"
        )


def test_tier1_real_2003():
    rows, d = _real_parse_harmonize("LinkCO03US.zip", 2003)
    _assert_real_common(rows, d, 2003, "MATCHS")


def test_tier1_real_2004():
    rows, d = _real_parse_harmonize("LinkCO04US.zip", 2004)
    _assert_real_common(rows, d, 2004, "FLGND")
