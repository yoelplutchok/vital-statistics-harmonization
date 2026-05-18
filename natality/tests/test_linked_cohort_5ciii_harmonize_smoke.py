"""DESIGN: tracks-current-state

[6a-RECWT update — DECISION_LOG 2026-05-22T02:00:00Z, §3
append-only-supersede / §4.2.1/Convention-2/L17] The (A′) finding
narrative below (``record_weight`` conservatively NULL for ALL
1983-1988) is **SUPERSEDED for 1983-1984**: the 6a-RECWT re-derivation
FALSIFIED the head-sample artifact — LinkCO83Guide.pdf p13 places
``1.f Record weight`` at Denominator byte 91 (the 3a transcription is
correct) and Σ(RECWT@91 over the full 1983 den) == guide "By
occurrence" 3,643,001 byte-exact. So ``record_weight`` =
``float(RECWT@91)`` for year ∈ {1983,1984} (the 50%-non-VSCP weighted
sample); NULL for 1985-1988 (full files; the genuine 1988 byte-91
anomaly is harmless — soft-flag (ll) carry). The (A′) all-NULL stays
correct for 1985-1988; the per-row assertions below were L17-reframed
in the SAME 6a-RECWT commit.

C8.18 DO step 5c-iii SMOKE — the **keyless 1983-1988 ``link_segment``
den/num one-row-per-birth harmonized encoding** in
``harmonize_linked_v3._harmonize_cohort_1983_1988``: the highest-risk
methodology-laden cohort sub-step (the natality ``is_pre1989``
1968/1978-revision analog; the RESOLVED 5b two-file construction).

1983-1988 carry NO record-level public-use key (the C8.18 DO step 3b
finding). The RESOLVED 5b model (do NOT re-open) yields the lossless
union of two segments discriminated by ``link_segment``:

  * ``link_segment="den"`` — every 91-byte ``LinkCO{yy}USden.dat``
    record (the aggregate birth denominator; ALL live births, one row
    per birth, NO death section). Harmonized ``infant_death`` =
    **NULL/unknown** (un-linkable per-record — the documented
    within-era structural difference = Phase-D D.4); death-side NULL.
  * ``link_segment="num"`` — every 500-byte ``LinkCO{yy}USnum.dat``
    record (locs 1-91 the deceased infant's birth covariates + locs
    194-500 the ICD-9 mortality section). Harmonized
    ``infant_death`` = **True** (the self-contained linked-infant-death
    set); death-side from the numerator.

The encoding MUST NOT fabricate a record-level join (there is no key);
the cohort IMR is ``count(link_segment="num") / count(link_segment=
"den")`` per stratum — NOT a per-birth ``infant_death`` filter (which
is the 1989+ form). The birth-side (shared locs 1-91, BOTH segments)
ALIASES the cohort raw names onto the natality V1-core ``is_pre1989``
recodes (H7 sibling-parity — reuse ``_dmeduc_years_to_cat4`` /
``_month_to_trimester`` / ``_pldel_to_facility`` + the NEW
``_mrace1digit_to_bridged4`` byte-identical to ``harmonize_v1_core
._mrace1digit_to_bridged4``; do NOT re-derive). ICD-9 (cohort
birth-year 1983-1988 ≤ 1998 → ``underlying_cause_icd9`` /
``cause_recode_61`` populated on num rows; the ICD-10 cols null — the
§15.D DO step 1 / 5c-i resolved within_era shape; do NOT re-open).

``link_segment`` is appended to ``OUT_SCHEMA`` (80→81; the v3→v4
ADDITIVE code-schema extension — the 5c-i ICD-9-columns precedent;
the 5b self-check #6 mandate "5c must preserve the keyless-era den/num
provenance"; the harmonized_schema.csv row + the v3→v4 version bump are
DO step 6, Anti-Pattern #6). It is "den"/"num" for 1983-1988 and NULL
for every other era (single denominator-plus / 2005+ — faithful "not
applicable: there is exactly one segment").

A NEW Convention-3 finding (PRE_FLIGHT_LOG 2026-05-20T00:00:00Z (A′);
L13-extension recurrence, year-axis): the 3a ``LINKED_BIRTH_1983_1988_
FIELDS`` (transcribed from the 1983 guide; only anchor fields
value-verified) is NOT byte-stable at the trailing ``RECWT@91`` across
1983→1988 (clean "1" for 1983/1985; == ``DMRACE@57`` 5000/5000 for
1988). Resolved within 5c-iii scope via the faithful no-patch choice:
**``record_weight`` conservatively NULL for ALL 1983-1988** (the
5c-i/1989-1991 NULL-record_weight precedent; the cohort IMR =
num/den does not use it; ``field_specs.py`` left UNTOUCHED — the full
per-year (1984-1988) non-anchor re-verification is the DO-step-6
NCHS-per-year-cohort-count VERIFY = soft-flag (ll)).

Sibling of the 3a/3b/4a/4b/4c/5a/5b/5c-i/5c-ii-a/5c-ii-b cohort
smokes; kept separate so each sub-step stays independently re-runnable
(the C8.18 DO sub-step-isolation precedent). DO step 5c-iii adds (to
``harmonize_linked_v3``) ``_mrace1digit_to_bridged4`` (NEW) +
``_harmonize_cohort_1983_1988`` (NEW) + ``("link_segment",
pa.string())`` to ``OUT_SCHEMA`` + the matching 2005+ ``pa.nulls``
entry + a 2-line ``if era == "1983_1988": return …`` dispatch
prepended in ``_harmonize_cohort_batch``; the 5c-i 1989-1991 inline
body + the 5c-ii-a ``_harmonize_cohort_1995_2002`` + the 5c-ii-b
``_harmonize_cohort_2003_2004`` + the 2005+ body's existing array
entries are byte-untouched (the 1983-1988 branch fires only for year
∈ {1983..1988} → the canonical v3 2005-2023 + the 5c-i/5c-ii-a/5c-ii-b
paths byte-identical, just gaining a link_segment=NULL column;
§9-#7-safe). The parser/field_specs are NOT touched. The 3 stale
keyless-1983-1988 ``NotImplementedError`` pins in the 5c-ii-b /
5c-ii-a / 5c-i harnesses are fixed by minimal ``tracks-current-state``
Edits bundled in the SAME 5c-iii commit per §4.2.1/Convention-2/L17
(5c-iii implements the LAST unimplemented cohort era → NO unimplemented
era remains; the genuine residual §2 fail-closed is the ``_cohort_era``
ValueError for the 1992-1994 permanent gap / pre-1983).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants
— the harmonized batch schema == ``OUT_SCHEMA`` (incl. link_segment);
den→infant_death NULL / num→infant_death True; the within_era ICD-9
cause shape; record_weight NULL (the (A′) finding); the birth-side H7
``is_pre1989`` ALIAS; ``_mrace1digit_to_bridged4`` byte-identical to
the natality V1-core sibling; the prior verified eras unperturbed
(regression-lock). No mutable annotation value is pinned (planted
synthetic inputs are fixed; reclens/field names are fixed NCHS facts).

Tier 0 (synthetic, always runs): the 1983-1988 ``_cohort_era``
partition; the den (infant_death NULL) + num (infant_death True,
ICD-9) two-segment encoding; the mixed-batch union; the birth-side H7
ALIAS; record_weight NULL; link_segment ∈ OUT_SCHEMA + NULL for other
eras; the ``_mrace1digit_to_bridged4`` edges + H7 parity; the
fail-closed negatives; the 1989-1991 + 1995-2002 + 2003/2004
regression-locks.

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): real ``LinkCO83.zip`` (1983) + ``LinkCO88.zip`` (1988)
parsed via ``iter_parsed_records`` (the RESOLVED 5b den/num union)
then harmonized — schema == ``OUT_SCHEMA``; den n ≫ num n (H6);
den rows infant_death NULL + link_segment "den"; num rows
infant_death True + link_segment "num" + ICD-9 numeric underlying
cause (0 alpha-prefixed; the ICD-10 cols 100% null); age_at_death_days
100% null (NO AGED in 1983-1988); record_weight 100% null (the (A′)
decision, real-data-asserted).
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
    LINKED_BIRTH_1983_1988_FIELDS,
    LINKED_NUM_DEATH_1983_1988_FIELDS,
)
import pyarrow.parquet as pq  # noqa: E402

# ``_expected_parsed_schema`` is NEW at DO step 5c-iii (the bundled,
# human-authorized minimal RESOLVED-5b ``run_parse`` root-cause fix for
# the §7 ``from_pylist`` schema-from-first-record den/num drop) —
# importing it BEFORE the DO also makes this harness RED (§9-#9 / L3).
from parse_linked_year import (  # noqa: E402
    _expected_parsed_schema,
    iter_parsed_records,
    run_parse,
)

# ``_harmonize_cohort_1983_1988`` + ``_mrace1digit_to_bridged4`` are NEW
# at DO step 5c-iii — importing them BEFORE the DO makes this harness
# fail collection (RED), proving it genuinely exercises the 5c-iii code
# (§9-#9 / L3, not a rubber-stamp).
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _dmeduc_years_to_cat4,
    _harmonize_batch,
    _harmonize_cohort_1983_1988,
    _mrace1digit_to_bridged4,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"

_BIRTH_NAMES = [f[0] for f in LINKED_BIRTH_1983_1988_FIELDS]
_DEATH_NAMES = [f[0] for f in LINKED_NUM_DEATH_1983_1988_FIELDS]


# --------------------------------------------------------------------------
# synthetic batch builder — shaped exactly like the parser's 1983-1988
# two-file output: every birth field (locs 1-91, BOTH segments) + the
# numerator death fields (locs 194-500, num only) as string columns + an
# int ``year`` column + a string ``link_segment`` column the parser injects.
# den rows supply "" for the num-only death fields (the harmonizer gates
# the death-side on link_segment=="num" anyway).
# --------------------------------------------------------------------------

def _two_file_batch(planted) -> pa.RecordBatch:
    names = _BIRTH_NAMES + _DEATH_NAMES
    cols: dict[str, list] = {n: [] for n in names}
    years: list[int] = []
    segs: list[str] = []
    for row in planted:
        for n in names:
            cols[n].append(row.get(n, ""))
        years.append(int(row["year"]))
        segs.append(row["link_segment"])
    arrays = [pa.array(cols[n], type=pa.string()) for n in names]
    arrays.append(pa.array(years, type=pa.int64()))
    arrays.append(pa.array(segs, type=pa.string()))
    return pa.RecordBatch.from_arrays(arrays, names=names + ["year", "link_segment"])


def _den_row(year=1985, **over):
    base = {
        "year": str(year), "link_segment": "den",
        "MATCHS": "3", "BIRYR": str(year), "RESSTAT": "1",
        "DMRACE": "1", "ORMOTH": "88", "DMAGE": "24", "DMEDUC": "12",
        "DMAR": "1", "DGEST": "40", "CSEX": "1", "DBIRWT": "3500",
        "DPLURAL": "1", "APGAR5": "09", "PLDEL": "1", "BIRATTND": "1",
        "RECWT": "1", "DFAGE": "28", "DFEDUC": "16", "DLIVORD": "01",
        "LIVORD9": "1", "DTOTORD": "01", "TOTORD9": "1", "DMPCB": "02",
        "NPREVIS": "11",
    }
    base.update(over)
    return base


def _num_row(year=1985, **over):
    base = {
        "year": str(year), "link_segment": "num",
        "MATCHS": "1", "BIRYR": str(year), "RESSTAT": "1",
        "DMRACE": "2", "ORMOTH": "00", "DMAGE": "19", "DMEDUC": "10",
        "DMAR": "2", "DGEST": "30", "CSEX": "2", "DBIRWT": "1100",
        "DPLURAL": "1", "APGAR5": "06", "PLDEL": "1", "BIRATTND": "1",
        "RECWT": "1", "DFAGE": "22", "DFEDUC": "12", "DLIVORD": "02",
        "LIVORD9": "2", "DTOTORD": "02", "TOTORD9": "2", "DMPCB": "05",
        "NPREVIS": "03",
        # numerator mortality section (locs 194-500): ICD-9; NO AGED
        "YOD": str(year), "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
    }
    base.update(over)
    return base


# --------------------------------------------------------------------------
# Tier 0: _cohort_era partition (regression-lock; unchanged by 5c-iii)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [1983, 1984, 1985, 1986, 1987, 1988])
def test_tier0_1983_1988_cohort_era(year):
    assert _cohort_era(year) == "1983_1988"


# --------------------------------------------------------------------------
# Tier 0: the DEN segment — infant_death NULL/unknown (un-linkable
# aggregate denominator; the documented within-era structural diff =
# Phase-D D.4) + the birth-side H7 is_pre1989 ALIAS
# --------------------------------------------------------------------------

def test_tier0_den_segment_birth_map_and_infant_death_null():
    out = _harmonize_batch(_two_file_batch([_den_row(1985)]), 1985)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == 1
    d = out.to_pydict()

    # birth-side H7 is_pre1989 ALIAS
    assert d["data_year"] == [1985]
    assert d["certificate_revision"] == ["unrevised_1968"]   # natality is_pre1989 parity
    assert d["residence_status"] == [1]
    assert d["is_foreign_resident"] == [False]
    assert d["maternal_age"] == [24]                          # DMAGE
    assert d["maternal_race_bridged"] == [1]                   # DMRACE 1 (1-digit) → White
    assert d["maternal_race_detail"] == ["1"]
    assert d["race_bridge_method"] == ["approximate_pre2003"]
    assert d["maternal_education_cat4"] == ["hs_grad"]         # DMEDUC 12
    assert d["father_education_cat4"] == ["ba_plus"]           # DFEDUC 16
    assert d["marital_status"] == [1]                          # DMAR
    assert d["live_birth_order_recode"] == [1]                 # LIVORD9 native
    assert d["total_birth_order_recode"] == [1]                # TOTORD9 native
    assert d["prenatal_care_start_month"] == [2]               # DMPCB
    assert d["prenatal_care_start_trimester"] == ["1st"]
    assert d["prenatal_visits"] == [11]                        # NPREVIS
    assert d["plurality_recode"] == [1]                        # DPLURAL
    assert d["infant_sex"] == ["M"]                            # CSEX 1
    assert d["gestational_age_weeks"] == [40]                  # DGEST (17-47∪99 keep)
    assert d["gestational_age_weeks_source"] == ["lmp"]
    assert d["birthweight_grams"] == [3500]                    # DBIRWT
    assert d["apgar5"] == [9]                                  # APGAR5 raw
    assert d["father_age"] == [28]                             # DFAGE (10-98 keep)
    assert d["birth_facility"] == ["hospital"]                 # PLDEL 1
    assert d["attendant_at_birth"] == [1]                      # BIRATTND

    # conservative NULL (H7 is_pre1989 + soft-flag (gg) + the (A′) finding)
    assert d["hispanic_origin"] == [None]                      # 2-digit ORMOTH → null
    assert d["maternal_hispanic"] == [None]
    assert d["father_hispanic"] == [None]
    assert d["maternal_race_ethnicity_5"] == [None]
    assert d["record_weight"] == [None]                        # 1985 full file → NULL (6a-RECWT scope=1983-1984 ONLY)
    assert d["maternal_race_detail_15cat"] == [None]
    assert d["smoking_any_during_pregnancy"] == [None]
    assert d["delivery_method_recode"] == [None]
    assert d["preterm_recode3"] == [None]
    assert d["father_race_ethnicity_5"] == [None]

    # DEN death-side: infant_death NULL (un-linkable; NOT False, NOT True)
    assert d["infant_death"] == [None]
    assert d["age_at_death_days"] == [None]
    assert d["age_at_death_recode5"] == [None]
    assert d["underlying_cause_icd9"] == [None]
    assert d["cause_recode_61"] == [None]
    assert d["underlying_cause_icd10"] == [None]
    assert d["cause_recode_130"] == [None]
    assert d["manner_of_death"] == [None]
    assert d["link_segment"] == ["den"]


# --------------------------------------------------------------------------
# Tier 0: the NUM segment — infant_death True + ICD-9 within_era +
# NO age_at_death_days (no AGED in 1983-1988) + record_weight NULL
# --------------------------------------------------------------------------

def test_tier0_num_segment_infant_death_true_icd9():
    out = _harmonize_batch(_two_file_batch([_num_row(1985)]), 1985)
    assert out.schema.equals(OUT_SCHEMA)
    d = out.to_pydict()

    assert d["data_year"] == [1985]
    assert d["certificate_revision"] == ["unrevised_1968"]
    assert d["maternal_race_bridged"] == [2]                  # DMRACE 2 → Black
    assert d["maternal_education_cat4"] == ["lt_hs"]           # DMEDUC 10
    assert d["infant_sex"] == ["F"]                            # CSEX 2
    assert d["birthweight_grams"] == [1100]
    assert d["gestational_age_weeks"] == [30]

    # NUM death-side: linked-infant-death set → infant_death True
    assert d["infant_death"] == [True]
    # the 1983-1988 numerator carries NO AGED (only AGER5/AGER76/AGER38
    # recodes) → age_at_death_days NULL (faithful "not on this file");
    # age_at_death_recode5 = AGER5.
    assert d["age_at_death_days"] == [None]
    assert d["age_at_death_recode5"] == [3]                    # AGER5
    # ICD-9 within_era (cohort birth-year 1985 ≤ 1998; §15.D DO step 1 /
    # 5c-i resolved shape) — the ICD-10 cols NULL.
    assert d["underlying_cause_icd9"] == ["7980"]              # UCOD ICD-9
    assert d["cause_recode_61"] == [54]                        # UCODR61
    assert d["underlying_cause_icd10"] == [None]
    assert d["cause_recode_130"] == [None]
    # no MANNER in the 1983-1988 numerator → manner_of_death NULL
    assert d["manner_of_death"] == [None]
    # 1985 = full file (Record count == by-occurrence) → record_weight
    # NULL (the §7-scoped 6a-RECWT fix populates 1983-1984 ONLY).
    assert d["record_weight"] == [None]
    assert d["link_segment"] == ["num"]


# --------------------------------------------------------------------------
# Tier 0: a MIXED den+num batch (the parser's lossless union) — per-row
# segment semantics; schema == OUT_SCHEMA; H6 (no rows dropped/added)
# --------------------------------------------------------------------------

def test_tier0_mixed_den_num_batch():
    planted = [
        _den_row(1986), _num_row(1986), _den_row(1986),
        _num_row(1986, UCOD="769 ", UCODR61="500", AGER5="5"),
    ]
    out = _harmonize_batch(_two_file_batch(planted), 1986)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == 4                                   # H6: union, lossless
    d = out.to_pydict()
    assert d["link_segment"] == ["den", "num", "den", "num"]
    assert d["infant_death"] == [None, True, None, True]
    assert d["underlying_cause_icd9"] == [None, "7980", None, "769"]
    assert d["age_at_death_recode5"] == [None, 3, None, 5]
    assert set(d["data_year"]) == {1986}


# --------------------------------------------------------------------------
# Tier 0: gestational_age_weeks keep-filter (H7 is_pre1989 17-47 ∪ 99)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("dgest,expected", [
    ("17", 17), ("40", 40), ("47", 47), ("48", None), ("52", None),
    ("99", 99), ("16", None),
])
def test_tier0_gestational_age_keep_filter(dgest, expected):
    d = _harmonize_batch(
        _two_file_batch([_den_row(1985, DGEST=dgest)]), 1985
    ).to_pydict()
    assert d["gestational_age_weeks"] == [expected]


# --------------------------------------------------------------------------
# Tier 0: _mrace1digit_to_bridged4 (NEW) edges + H7 sibling-parity
# --------------------------------------------------------------------------

@pytest.mark.parametrize("code,expected", [
    (0, 4), (1, 1), (2, 2), (3, 3), (4, 4), (5, 4), (6, 4), (8, 4),
    (7, None), (9, None),
])
def test_tier0_mrace1digit_to_bridged4_edges(code, expected):
    out = _mrace1digit_to_bridged4(pa.array([code], type=pa.int16())).to_pylist()
    assert out == [expected]


def test_tier0_mrace1digit_to_bridged4_null_passthrough():
    out = _mrace1digit_to_bridged4(pa.array([None], type=pa.int16())).to_pylist()
    assert out == [None]


def test_tier0_h7_sibling_parity_recodes():
    """The NEW ``_mrace1digit_to_bridged4`` + the reused
    ``_dmeduc_years_to_cat4`` are byte-identical to the natality V1-core
    siblings (H7 sibling-parity on the shared concepts)."""
    import importlib

    v1 = importlib.import_module("harmonize_v1_core")
    mr = pa.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, None], type=pa.int16())
    assert _mrace1digit_to_bridged4(mr).to_pylist() == \
        v1._mrace1digit_to_bridged4(mr).to_pylist()
    ed = pa.array([0, 8, 11, 12, 13, 15, 16, 17, 88, 99, None], type=pa.int16())
    assert _dmeduc_years_to_cat4(ed).to_pylist() == \
        v1._dmeduc_years_to_cat4(ed).to_pylist()


# --------------------------------------------------------------------------
# Tier 0: link_segment ∈ OUT_SCHEMA + NULL for every non-1983-1988 era
# (the v3→v4 ADDITIVE schema extension; 1989+/2005+ have no segment split)
# --------------------------------------------------------------------------

def test_tier0_link_segment_in_out_schema():
    assert "link_segment" in OUT_SCHEMA.names
    assert OUT_SCHEMA.field("link_segment").type == pa.string()
    assert OUT_SCHEMA.names[-1] == "link_segment"             # appended last


def test_tier0_link_segment_null_for_1989_1991():
    """A 1989-1991 single-member denominator-plus batch → link_segment
    auto-defaults NULL (no segment split; the dict-pattern era functions
    + the byte-untouched 2005+ body)."""
    from field_specs import (
        LINKED_BIRTH_1989_1991_FIELDS, LINKED_DEATH_1989_1991_FIELDS,
    )
    names = ([f[0] for f in LINKED_BIRTH_1989_1991_FIELDS]
             + [f[0] for f in LINKED_DEATH_1989_1991_FIELDS])
    row = {
        "MATCHS": "1", "BIRYR": "1990", "RESSTATB": "1", "DMAGE": "24",
        "ORMOTH": "0", "MRACE": "01", "DMEDUC": "12", "DMAR": "1",
        "CSEX": "1", "DPLURAL": "1", "DBIRWT": "1100", "GESTAT": "29",
        "MONPRE": "01", "NPREVIS": "04", "DFAGE": "26", "PLDEL": "1",
        "BIRATTND": "1", "DLIVORD": "01", "DTOTORD": "01",
        "AGED": "008", "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
    }
    arrays = [pa.array([row.get(n, "")], type=pa.string()) for n in names]
    arrays.append(pa.array([1990], type=pa.int64()))
    batch = pa.RecordBatch.from_arrays(arrays, names=names + ["year"])
    d = _harmonize_batch(batch, 1990).to_pydict()
    assert d["link_segment"] == [None]
    assert d["infant_death"] == [True]                        # 5c-i path intact


# --------------------------------------------------------------------------
# Tier 0: fail-closed negatives
# --------------------------------------------------------------------------

def test_tier0_direct_function_rejects_non_1983_1988():
    """``_harmonize_cohort_1983_1988`` is era-scoped; the sanctioned
    entry is the ``_harmonize_cohort_batch`` dispatch — calling it on a
    non-1983-1988 year must NOT silently mis-harmonize (§2 fail-closed)."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([1990], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises((ValueError, AssertionError)):
        _harmonize_cohort_1983_1988(batch, 1990)


@pytest.mark.parametrize("gap_year", [1992, 1993, 1994, 1979])
def test_tier0_residual_failclosed_gap_and_pre1983(gap_year):
    """5c-iii implements the LAST unimplemented cohort era → NO
    ``NotImplementedError`` is raised for any real cohort year. The
    genuine residual §2 fail-closed is the ``_cohort_era`` ValueError
    for the 1992-1994 permanent NCHS linkage gap / pre-1983 (a premature
    DO step 6 on those years halts loudly, not silently mis-routed
    through the 2005+ body)."""
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()),
         pa.array([gap_year], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises(ValueError):
        _harmonize_batch(batch, gap_year)


# --------------------------------------------------------------------------
# Tier 0: the prior verified eras UNPERTURBED (regression-lock) — they
# now also carry link_segment=NULL (auto-defaulted; byte-untouched)
# --------------------------------------------------------------------------

def test_tier0_1995_2002_regression_unperturbed():
    from field_specs import (
        LINKED_BIRTH_1995_2002_FIELDS, LINKED_DEATH_1995_2002_FIELDS,
    )
    names = ([f[0] for f in LINKED_BIRTH_1995_2002_FIELDS]
             + [f[0] for f in LINKED_DEATH_1995_2002_FIELDS])
    row = {
        "MATCHS": "1", "BIRYR": "1996", "RESSTATB": "1", "DMAGE": "18",
        "ORMOTH": "1", "MRACE": "02", "DMEDUC": "10", "DMAR": "2",
        "CSEX": "2", "DPLURAL": "1", "DBIRWT": "0980", "GESTAT": "27",
        "MONPRE": "00", "NPREVIST": "02", "DFAGE": "21", "PLDEL": "1",
        "BIRATTND": "1", "DLIVORD": "02", "DTOTORD": "02", "FMAPS": "03",
        "ORFATH": "1", "RECWT": "1.487213",
        "AGED": "021", "AGER5": "3", "UCOD": "7980", "UCODR": "054",
    }
    arrays = [pa.array([row.get(n, "")], type=pa.string()) for n in names]
    arrays.append(pa.array([1996], type=pa.int64()))
    batch = pa.RecordBatch.from_arrays(arrays, names=names + ["year"])
    d = _harmonize_batch(batch, 1996).to_pydict()
    assert d["certificate_revision"] == ["unrevised_1989"]
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd9"] == ["7980"]              # cohort 1996 = ICD-9
    assert d["record_weight"] == [pytest.approx(1.487213)]
    assert d["link_segment"] == [None]                         # no segment split


def test_tier0_2003_2004_regression_unperturbed():
    from field_specs import (
        LINKED_BIRTH_2003_FIELDS, LINKED_DEATH_2003_FIELDS,
    )
    names = ([f[0] for f in LINKED_BIRTH_2003_FIELDS]
             + [f[0] for f in LINKED_DEATH_2003_FIELDS])
    row = {
        "year": "2003", "DOB_YY": "2003", "REVISION": "S", "RESTATUS": "1",
        "MAGER41": "15", "MRACE": "01", "MRACEREC": "1", "UMHISP": "0",
        "MAR": "1", "UMEDUC": "16", "MEDUC_REC": "5", "LBO_REC": "1",
        "TBO_REC": "1", "MPCB": "02", "UPREVIS": "13", "DPLURAL": "1",
        "SEX": "M", "COMBGEST": "40", "DBWT": "3500", "APGAR5": "09",
        "ATTEND": "1", "UBFACIL": "1", "FAGEREC11": "04", "UFHISP": "0",
        "UFAGECOMB": "30", "MATCHS": "1", "AGED": "021", "AGER5": "3",
        "MANNER": "1", "UCOD": "P073", "UCODR130": "115", "RECWT": "1.49",
    }
    arrays = [pa.array([row.get(n, "")], type=pa.string()) for n in names]
    arrays.append(pa.array([2003], type=pa.int64()))
    batch = pa.RecordBatch.from_arrays(arrays, names=names + ["year"])
    d = _harmonize_batch(batch, 2003).to_pydict()
    assert d["maternal_age"] == [28]                           # MAGER41 15 → 28
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd10"] == ["P073"]             # cohort 2003 = ICD-10
    assert d["manner_of_death"] == [1]
    assert d["link_segment"] == [None]                         # no segment split


# --------------------------------------------------------------------------
# Tier 1: real LinkCO83 (1983) + LinkCO88 (1988) parsed (the RESOLVED 5b
# den/num union) then harmonized
# --------------------------------------------------------------------------

def _real_parse_harmonize(zip_name: str, year: int):
    zp = LINKED_RAW_DIR / zip_name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {zip_name} absent (gitignored, out-of-tree)")
    rows = list(iter_parsed_records(zp, year, max_rows=500))
    assert rows, "no parsed rows"
    # the RESOLVED 5b two-file model: every 1983-1988 row carries
    # link_segment ∈ {den, num} (NOT a single denominator-plus)
    assert all(r.get("link_segment") in ("den", "num") for r in rows)
    # Build the batch with the EXPLICIT UNIFIED den∪num column set (every
    # birth field + every numerator death field + year + link_segment),
    # filling den rows' num-only death keys with "" (→ null via the
    # harmonizer's _to_* coercion) — i.e. exactly what a CORRECTLY
    # schema-unified parquet looks like. NOTE: ``pa.*.from_pylist``
    # infers the schema from the FIRST record only; since
    # ``_iter_two_file_1983_1988`` yields ALL den rows (no death keys)
    # BEFORE any num row, a naive ``from_pylist(rows)`` SILENTLY DROPS
    # the entire numerator ICD-9 mortality section. That is a latent
    # defect in the RESOLVED-5b ``parse_linked_year.run_parse``
    # materialization (it uses ``pa.Table.from_pylist``) that would
    # bite the DO-step-6 1983-1988 re-harmonize — surfaced at this
    # Convention-3/SMOKE cheap-check + raised as a §7 forward-looking
    # HALT for DO step 6 (PRE_FLIGHT_LOG 2026-05-20 (A″) / LESSONS /
    # STATUS). Here the harness constructs the input faithfully so the
    # 5c-iii harmonize ENCODING is genuinely SMOKE-verified on real
    # den/num data (the §9-#4 fix-the-test-correctly discipline — the
    # harmonize code is correct; only the test-input construction was
    # mis-copied from the 5c-ii-b homogeneous-dict pattern).
    names = list(dict.fromkeys(
        [n for r in rows for n in r.keys()
         if n not in ("year", "link_segment")]
    ))
    cols = [
        pa.array([str(r.get(n, "")) for r in rows], type=pa.string())
        for n in names
    ]
    cols.append(pa.array([int(r["year"]) for r in rows], type=pa.int64()))
    cols.append(pa.array([r["link_segment"] for r in rows], type=pa.string()))
    batch = pa.RecordBatch.from_arrays(
        cols, names=names + ["year", "link_segment"]
    )
    out = _harmonize_batch(batch, year)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == len(rows)
    return rows, out.to_pydict()


def _assert_real_1983_1988(rows, d, year):
    assert set(d["data_year"]) == {year}
    assert set(d["certificate_revision"]) == {"unrevised_1968"}
    seg = d["link_segment"]
    assert set(seg) == {"den", "num"}, "both segments present (the 5b union)"
    n_den = seg.count("den")
    n_num = seg.count("num")
    # Both segments materialized + non-empty in the capped union. NOTE:
    # ``iter_parsed_records(max_rows=N)`` caps EACH segment INDEPENDENTLY
    # (the RESOLVED 5b per-segment-cap refinement, PRE_FLIGHT_LOG
    # 2026-05-19T08:30:00Z) so a bounded SMOKE sample fills BOTH to the
    # cap (den == num == N here) — the den ≫ num H6 row-count
    # conservation is a FULL-PARSE property (max_rows=None), gated at the
    # DO-step-6 NCHS-per-year-cohort-count §15.D VERIFY, NOT a
    # per-segment-capped-SMOKE invariant (§9-#4: assert the SMOKE-scale
    # invariant correctly, do NOT mis-size it to the full-file property).
    assert n_den > 0 and n_num > 0, f"{year}: den={n_den} num={n_num}"

    for i, s in enumerate(seg):
        if s == "den":
            # un-linkable aggregate denominator → infant_death NULL
            assert d["infant_death"][i] is None
            assert d["age_at_death_days"][i] is None
            assert d["age_at_death_recode5"][i] is None
            assert d["underlying_cause_icd9"][i] is None
        else:  # num — the self-contained linked-infant-death set
            assert d["infant_death"][i] is True
            # NO AGED in the 1983-1988 numerator (faithful)
            assert d["age_at_death_days"][i] is None

    # within_era ICD-9 (cohort ≤ 1998): the ICD-10 cols 100% null;
    # num rows carry numeric (non-alpha) ICD-9 underlying cause.
    assert all(v is None for v in d["underlying_cause_icd10"])
    assert all(v is None for v in d["cause_recode_130"])
    icd9 = [
        c for c, s in zip(d["underlying_cause_icd9"], seg)
        if s == "num" and c is not None and c.strip()
    ]
    assert icd9, f"{year}: num rows must carry ICD-9 underlying cause"
    assert all(not c.strip()[:1].isalpha() for c in icd9), (
        f"{year}: ICD-9 underlying cause must be numeric (0 alpha-prefixed; "
        "the §15.D DO step 1 / 5c-i resolved ≤1998 shape)"
    )
    # C8.18 DO step 6a-RECWT (DECISION_LOG 2026-05-22T02:00:00Z; the
    # 5c-iii (A′) all-NULL SUPERSEDED for 1983-1984, correct 1985-1988).
    # 1983-1984 = the documented 50%-non-VSCP weighted sample →
    # record_weight = float(RECWT@91) ∈ {1.0,2.0} (the bounded head
    # sample is all weight-1 VSCP — the den file is ordered by
    # State-of-occurrence; the weight-2 non-VSCP records cluster later).
    # 1985-1988 = full files → NULL (the §7 1983-1984-ONLY scope; the
    # genuine 1988 byte-91 anomaly is harmless — no weighting needed;
    # soft-flag (ll) carry).
    if year in (1983, 1984):
        assert all(w is not None for w in d["record_weight"]), (
            f"{year}: record_weight must be non-NULL (the 6a-RECWT "
            "root-cause fix; the head sample is all weight-1 VSCP)"
        )
        assert set(d["record_weight"]) <= {1.0, 2.0}, (
            f"{year}: RECWT@91 weight domain must be {{1.0,2.0}}"
        )
    else:
        assert all(w is None for w in d["record_weight"]), (
            f"{year}: record_weight must stay NULL (full file; the §7 "
            "scope = 1983-1984 ONLY; soft-flag (ll))"
        )
    # manner_of_death NULL (no MANNER in the 1983-1988 numerator)
    assert all(m is None for m in d["manner_of_death"])
    # maternal_age plausible on the mapped rows
    ages = [a for a in d["maternal_age"] if a is not None]
    assert ages and min(ages) >= 10 and max(ages) <= 60


def test_tier1_real_1983():
    rows, d = _real_parse_harmonize("LinkCO83.zip", 1983)
    _assert_real_1983_1988(rows, d, 1983)


def test_tier1_real_1988():
    rows, d = _real_parse_harmonize("LinkCO88.zip", 1988)
    _assert_real_1983_1988(rows, d, 1988)


# --------------------------------------------------------------------------
# Tier 0 + Tier 1: the bundled RESOLVED-5b ``run_parse`` §7 root-cause
# fix — ``_expected_parsed_schema`` + a lossless 1983-1988 _raw parquet
# (the §7 finding: ``pa.*.from_pylist`` infers the schema from the
# FIRST record only; ``_iter_two_file_1983_1988`` yields ALL den rows
# (no death keys) BEFORE any num row → a naive materialization SILENTLY
# DROPS the numerator ICD-9 mortality section / crashes the chunked
# write at the den→num boundary. The human-authorized minimal fix
# passes an explicit unified den∪num schema for 1983-1988 ONLY; every
# homogeneous year stays byte-identical, §9-#7.)
# --------------------------------------------------------------------------

def test_tier0_expected_parsed_schema_unified_for_1983_1988():
    for y in (1983, 1985, 1988):
        sch = _expected_parsed_schema(y)
        assert sch is not None
        names = set(sch.names)
        # the numerator ICD-9 mortality section MUST be in the schema
        # (the §7 silent-drop target)
        for col in ("UCOD", "UCODR61", "AGER5"):
            assert col in names, f"{y}: {col} missing from unified schema"
        # the shared birth section + the parser-injected columns
        for col in ("BIRYR", "DMRACE", "DMEDUC", "year", "link_segment"):
            assert col in names
        assert sch.field("year").type == pa.int64()
        assert sch.field("link_segment").type == pa.string()
        assert sch.field("UCOD").type == pa.string()


@pytest.mark.parametrize("year", [1990, 1996, 2003, 2004, 2010, 2023])
def test_tier0_expected_parsed_schema_none_for_homogeneous(year):
    """Every non-1983-1988 (homogeneous single-member) year → None, so
    ``run_parse`` keeps the original ``from_pylist(rows)``/``tbl.schema``
    path byte-identical (§9-#7 — the byte-exact shipped parquets)."""
    assert _expected_parsed_schema(year) is None


def test_tier1_run_parse_preserves_numerator_section(tmp_path):
    """The §7 end-to-end gate: ``run_parse`` on a real 1983-1988 zip
    must write a _raw parquet that KEEPS the numerator ICD-9 mortality
    section (UCOD/AGER5/UCODR61) — den rows null there, num rows valued
    — and that parquet must harmonize (the DO-step-6 path) with the
    1983-1988 ICD-9 cause populated on num rows. A pre-fix
    ``from_pylist(rows)`` would have dropped UCOD entirely."""
    zp = LINKED_RAW_DIR / "LinkCO83.zip"
    if not zp.exists():
        pytest.skip("raw cohort zip LinkCO83.zip absent (gitignored)")
    out = tmp_path / "linked_1983_raw.parquet"
    n = run_parse(zp, 1983, out, max_rows=300)   # single-list path
    assert n > 0 and out.exists()
    pf = pq.ParquetFile(out)
    schema_names = set(pf.schema_arrow.names)
    for col in ("UCOD", "UCODR61", "AGER5", "link_segment"):
        assert col in schema_names, (
            f"run_parse DROPPED {col} from the 1983-1988 _raw parquet "
            "(the §7 from_pylist-first-record defect — the fix did not take)"
        )
    tbl = pf.read()
    seg = tbl.column("link_segment").to_pylist()
    ucod = tbl.column("UCOD").to_pylist()
    # den rows null UCOD; num rows carry the ICD-9 underlying cause
    assert any(s == "num" for s in seg) and any(s == "den" for s in seg)
    num_ucod = [u for u, s in zip(ucod, seg) if s == "num" and u and u.strip()]
    den_ucod = [u for u, s in zip(ucod, seg) if s == "den"]
    assert num_ucod, "num rows lost their ICD-9 UCOD (the §7 defect)"
    assert all(u in (None, "") for u in den_ucod), "den rows must have null UCOD"
    # the DO-step-6 path: the read-back parquet harmonizes with ICD-9
    # populated on num rows (proves the fix unblocks 5c-iii end-to-end)
    hd = _harmonize_batch(tbl.combine_chunks().to_batches()[0], 1983).to_pydict()
    icd9_num = [
        c for c, s in zip(hd["underlying_cause_icd9"], hd["link_segment"])
        if s == "num" and c is not None and c.strip()
    ]
    assert icd9_num, "harmonized num rows lost underlying_cause_icd9"
    assert all(not c.strip()[:1].isalpha() for c in icd9_num)  # ICD-9 numeric
