"""DESIGN: tracks-current-state

C8.18 DO step 5c-i SMOKE — the per-cohort-era **harmonize architecture**
in ``harmonize_linked_v3.py``: a ``_cohort_era(year)`` classifier + a
no-op-for-2005+ ``_prepare_cohort_batch`` alias/synthesis pass + the
within_era ICD-9 cause-column-shape (``underlying_cause_icd9`` +
``cause_recode_61`` added to ``OUT_SCHEMA``; ``underlying_cause_icd10`` /
``cause_recode_130`` null for the ICD-9 era) + the **1989-1991 reference
era** mapped end-to-end (the lowest-risk verifiable substrate-first
increment: single-member denominator-plus, 1989-rev cert == natality V2
1990-2002, ICD-9).

Sibling of the 3a/3b/4a/4b/4c/5a/5b cohort smokes; kept separate so each
sub-step stays independently re-runnable (the C8.18 DO sub-step-isolation
precedent). DO step 5c-i adds (to ``harmonize_linked_v3``) ``_cohort_era``
(NEW) + ``_prepare_cohort_batch`` (NEW) + ``_harmonize_cohort_batch``
(NEW) + a top-of-``_harmonize_batch`` cohort branch + 2 within_era ICD-9
columns on ``OUT_SCHEMA`` + the local ``_dmeduc_years_to_cat4`` /
``_mrace_detail_to_bridged4`` sibling-parity recodes; the existing 2005+
body is byte-untouched (the cohort branch fires only for year ≤ 2004 →
the canonical v3 2005-2023 path byte-identical; §9-#7-safe). The parser
``_layout_for_linked_year`` / ``_numerator_layout_for_linked_year``
dispatchers are NOT touched, so this harness adds NO new-year
``pytest.raises`` parser pin (the L17 stale-pin class does not apply:
5c-i configures no new parser dispatcher year).

SHAPE-not-VALUE (Convention 1; §4.2.1): asserts STRUCTURAL invariants —
``_cohort_era`` partitions years into the 5 cohort eras vs None (≥2005
canonical) vs ValueError (the 1992-1994 permanent gap / pre-1983); the
harmonized batch has schema == the extended ``OUT_SCHEMA`` with the 2
NEW within_era ICD-9 columns present and the ICD-10 cause columns
**null for the ICD-9 era** (the §15.D DO-step-1 default-null +
revision-tagged decision); an unimplemented cohort era *raises*
``NotImplementedError`` (fail-closed, L3 — 5c-i is scoped to 1989-1991;
1995-2004 = 5c-ii, the keyless 1983-1988 = 5c-iii); the cohort
education/race recodes are byte-identical to the natality V1-core
siblings (H7 sibling-parity, asserted by feeding the SAME array to
both). No mutable annotation value is pinned (the planted synthetic
inputs are fixed; reclens/field names are fixed NCHS facts; the OUT
column COUNT is asserted as ``old + 2`` structurally, not a frozen int).

Construction model (the DO step 5c-i Convention-3 snapshot,
PRE_FLIGHT_LOG 2026-05-19T11:00:00Z + DECISION_LOG 2026-05-19T11:00:00Z;
§15.D DO step 1 DECISION_LOG 2026-05-17T05:30:00Z): the linked cohort
denominator(-plus) birth section IS a birth certificate of the SAME
revision natality already harmonizes, so the cohort birth-side map
aliases the cohort raw names onto the natality V1-core era recodes
(reuse, H7 sibling-parity — do NOT re-derive). ICD-9 (cohort birth-year
1983-1998) vs ICD-10 (1999+) is a within_era split: the new
``underlying_cause_icd9`` / ``cause_recode_61`` carry the ICD-9 era;
``underlying_cause_icd10`` / ``cause_recode_130`` are null for it.

Tier 0 (synthetic, always runs): the ``_cohort_era`` partition + L3
negatives; a synthetic 1989-1991 cohort RecordBatch harmonized
end-to-end (planted anchors recovered; ICD-9 default-null verified;
fail-closed on the 5c-ii/5c-iii eras); the H7 sibling-parity recode
equivalence vs ``harmonize_v1_core``.

Tier 1 (real data, skipif the gitignored out-of-tree cohort zip is
absent): a real ~300-record ``LinkCO90.zip`` denominator-plus parsed via
``iter_parsed_records`` then harmonized — schema == the extended
``OUT_SCHEMA``; ``data_year``==1990; ``certificate_revision`` ==
``unrevised_1989``; ``underlying_cause_icd10`` / ``cause_recode_130``
100% null (the ICD-9 era default-null); ``maternal_age`` plausible;
``infant_sex`` ∈ {M,F,null}; ``infant_death`` ⟺ ``age_at_death_days``
populated (the value-consistency cross-check, L3).
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pytest

_IMPORT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
_HARM_DIR = Path(__file__).resolve().parents[1] / "scripts" / "03_harmonize"
for _d in (_IMPORT_DIR, _HARM_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from field_specs import (  # noqa: E402
    LINKED_BIRTH_1989_1991_FIELDS,
    LINKED_DEATH_1989_1991_FIELDS,
)
from parse_linked_year import iter_parsed_records  # noqa: E402

# These symbols are NEW at DO step 5c-i — importing them BEFORE the DO
# makes this harness fail collection (RED), proving it genuinely
# exercises the 5c-i code (§9-#9 / L3, not a rubber-stamp).
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _harmonize_batch,
    _dmeduc_years_to_cat4,
    _detail_order_to_recode9,
    _mrace_detail_to_bridged4,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# Tier 0: the _cohort_era partition (classifier + L3 negatives)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "year,expected",
    [
        (1983, "1983_1988"), (1985, "1983_1988"), (1988, "1983_1988"),
        (1989, "1989_1991"), (1990, "1989_1991"), (1991, "1989_1991"),
        (1995, "1995_2002"), (1998, "1995_2002"), (2002, "1995_2002"),
        (2003, "2003"), (2004, "2004"),
        # ≥2005 = the canonical v3 path (the cohort branch must NOT fire)
        (2005, None), (2013, None), (2014, None), (2023, None),
    ],
)
def test_tier0_cohort_era_partition(year, expected):
    assert _cohort_era(year) == expected


@pytest.mark.parametrize("year", [1992, 1993, 1994, 1982, 1970])
def test_tier0_cohort_era_failclosed_gap_and_pre1983(year):
    """L3 / §2 fail-closed: the 1992-1994 permanent NCHS linkage gap (and
    any pre-1983 year) is neither a configured cohort era nor the
    canonical ≥2005 path — it must RAISE, never silently route to the
    2005+ harmonize body (which would mis-harmonize / produce garbage)."""
    with pytest.raises(ValueError):
        _cohort_era(year)


# --------------------------------------------------------------------------
# Tier 0: OUT_SCHEMA shape — the within_era ICD-9 cause columns (Conv. 1)
# --------------------------------------------------------------------------

def test_tier0_out_schema_has_within_era_icd9_columns():
    names = OUT_SCHEMA.names
    # the 2 NEW within_era ICD-9 columns are present, typed per the
    # H7 sibling-parity decision (string code + int16 recode)
    assert "underlying_cause_icd9" in names
    assert "cause_recode_61" in names
    assert OUT_SCHEMA.field("underlying_cause_icd9").type == pa.string()
    assert OUT_SCHEMA.field("cause_recode_61").type == pa.int16()
    # the existing ICD-10 cause columns are still present (NOT renamed —
    # the §15.D default-null decision keeps them; they go null for the
    # ICD-9 era, they are not repurposed)
    assert "underlying_cause_icd10" in names
    assert "cause_recode_130" in names
    # exactly 2 columns added vs the documented pre-5c-i death-side set
    # (asserted structurally: the 2 NEW names are the only ICD-9 ones)
    icd9_cols = [n for n in names if n.endswith("_icd9") or n == "cause_recode_61"]
    assert set(icd9_cols) == {"underlying_cause_icd9", "cause_recode_61"}


# --------------------------------------------------------------------------
# Tier 0: H7 sibling-parity — the cohort recodes == natality V1-core
# --------------------------------------------------------------------------

def test_tier0_h7_sibling_parity_recodes():
    """The linked cohort education/race recodes MUST be byte-identical to
    the natality V1-core siblings (H7: both products must agree on a
    shared concept). Feed the SAME array to both implementations and
    assert equality (a real discriminating check, not a rubber-stamp)."""
    import importlib

    v1 = importlib.import_module("harmonize_v1_core")

    educ_in = pa.array([0, 8, 11, 12, 13, 15, 16, 17, 99, None], type=pa.int16())
    assert _dmeduc_years_to_cat4(educ_in).to_pylist() == \
        v1._dmeduc_years_to_cat4(educ_in).to_pylist()

    race_in = pa.array([1, 2, 3, 4, 8, 9, 18, 68, 77, None], type=pa.int16())
    assert _mrace_detail_to_bridged4(race_in).to_pylist() == \
        v1._mrace_detail_to_bridged4(race_in).to_pylist()


def test_tier0_detail_order_to_recode9_edges():
    """The detail-order → 9-category recode (linked cohort has only
    DLIVORD/DTOTORD detail, not the natality LIVORD9/TOTORD9 recode):
    1-7 passthrough, 8+ collapse to 8, 99 → 9 (unknown), blank → null
    (the standard NCHS birth-order-9 shape; schema allowed_values
    1-7|8|9). A real discriminating check, not a rubber-stamp."""
    inp = pa.array([1, 7, 8, 15, 31, 40, 99, None], type=pa.int16())
    assert _detail_order_to_recode9(inp).to_pylist() == \
        [1, 7, 8, 8, 8, 8, 9, None]


# --------------------------------------------------------------------------
# Tier 0: a synthetic 1989-1991 cohort batch harmonized end-to-end
# --------------------------------------------------------------------------

def _synthetic_1989_1991_batch(planted: list[dict[str, str]]) -> pa.RecordBatch:
    """Build a RecordBatch shaped exactly like the parser's 1989-1991
    denominator-plus output: every LINKED_BIRTH/_DEATH_1989_1991 field as
    a string column + an int ``year`` column (the parser injects it)."""
    field_names = (
        [f[0] for f in LINKED_BIRTH_1989_1991_FIELDS]
        + [f[0] for f in LINKED_DEATH_1989_1991_FIELDS]
    )
    cols: dict[str, list] = {name: [] for name in field_names}
    years: list[int] = []
    for row in planted:
        for name in field_names:
            cols[name].append(row.get(name, ""))
        years.append(int(row.get("year", 1990)))
    arrays = [pa.array(cols[n], type=pa.string()) for n in field_names]
    arrays.append(pa.array(years, type=pa.int64()))
    return pa.RecordBatch.from_arrays(arrays, names=field_names + ["year"])


def test_tier0_1989_1991_reference_era_end_to_end():
    # one survivor (no death section) + one linked infant death (ICD-9)
    batch = _synthetic_1989_1991_batch([
        {  # survivor: MATCHS=3, AGED blank
            "year": "1990", "MATCHS": "3", "BIRYR": "1990", "RESSTATB": "1",
            "DMAGE": "27", "ORMOTH": "0", "MRACE": "01", "DMEDUC": "12",
            "DMAR": "1", "CSEX": "1", "DPLURAL": "1", "DBIRWT": "3402",
            "GESTAT": "39", "MONPRE": "02", "NPREVIS": "12", "DFAGE": "29",
            "PLDEL": "1", "BIRATTND": "1", "DLIVORD": "01", "DTOTORD": "01",
        },
        {  # linked infant death: MATCHS=1, AGED + ICD-9 UCOD populated
            "year": "1990", "MATCHS": "1", "BIRYR": "1990", "RESSTATB": "1",
            "DMAGE": "19", "ORMOTH": "1", "MRACE": "02", "DMEDUC": "10",
            "DMAR": "2", "CSEX": "2", "DPLURAL": "1", "DBIRWT": "1200",
            "GESTAT": "28", "MONPRE": "00", "NPREVIS": "03", "DFAGE": "22",
            "PLDEL": "1", "BIRATTND": "1", "DLIVORD": "02", "DTOTORD": "02",
            "AGED": "012", "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
        },
    ])
    out = _harmonize_batch(batch, 1990)

    # schema == the extended OUT_SCHEMA; row-count conserved (H6)
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == 2

    d = out.to_pydict()
    # birth-side anchors recovered via the natality-sibling recodes
    assert d["data_year"] == [1990, 1990]
    assert d["certificate_revision"] == ["unrevised_1989", "unrevised_1989"]
    assert d["maternal_age"] == [27, 19]
    assert d["infant_sex"] == ["M", "F"]
    assert d["maternal_race_bridged"] == [1, 2]            # MRACE 01→1, 02→2
    assert d["maternal_education_cat4"] == ["hs_grad", "lt_hs"]  # 12, 10 years
    assert d["maternal_hispanic"] == [False, True]         # ORMOTH 0, 1
    assert d["birthweight_grams"] == [3402, 1200]
    assert d["plurality_recode"] == [1, 1]
    assert d["marital_status"] == [1, 2]
    assert d["live_birth_order_recode"] == [1, 2]    # DLIVORD 01/02 → recode9
    assert d["total_birth_order_recode"] == [1, 2]   # DTOTORD 01/02 → recode9
    # composite-block fields (smoking/diabetes/delivery-method/congenital)
    # are conservatively null at 5c-i (leaf decomposition = soft-flag (gg)
    # DO step 5c-ii/6; the natality is_pre1989 conservative-null precedent)
    assert d["smoking_any_during_pregnancy"] == [None, None]
    assert d["diabetes_any"] == [None, None]
    assert d["delivery_method_recode"] == [None, None]

    # death-side: the ICD-9 within_era default-null decision (§15.D DO-1)
    assert d["infant_death"] == [False, True]
    assert d["age_at_death_days"] == [None, 12]
    assert d["underlying_cause_icd9"] == [None, "7980"]    # ICD-9, populated
    assert d["cause_recode_61"] == [None, 54]              # UCODR61 → int16
    assert d["underlying_cause_icd10"] == [None, None]     # NULL for ICD-9 era
    assert d["cause_recode_130"] == [None, None]           # NULL for ICD-9 era


@pytest.mark.parametrize(
    "year,era_phase",
    [(1985, "5c-iii"), (1995, "5c-ii"), (2002, "5c-ii"), (2003, "5c-ii"),
     (2004, "5c-ii")],
)
def test_tier0_unimplemented_cohort_eras_failclosed(year, era_phase):
    """L3 / §2 fail-closed: 5c-i implements ONLY 1989-1991. The other
    cohort eras must RAISE NotImplementedError (so a premature DO step 6
    on those years halts loudly rather than silently mis-harmonizing) —
    the keyless 1983-1988 is 5c-iii; 1995-2004 is 5c-ii."""
    # a 1-row batch with just `year` (+ a token col) is enough to reach
    # the cohort-era dispatch (the NotImplementedError fires before any
    # field access for the unconfigured eras)
    batch = pa.RecordBatch.from_arrays(
        [pa.array(["x"], type=pa.string()), pa.array([year], type=pa.int64())],
        names=["TOKEN", "year"],
    )
    with pytest.raises(NotImplementedError):
        _harmonize_batch(batch, year)


# --------------------------------------------------------------------------
# Tier 1: real LinkCO90 denominator-plus parsed then harmonized
# --------------------------------------------------------------------------

def test_tier1_real_1990_parse_then_harmonize():
    zp = LINKED_RAW_DIR / "LinkCO90.zip"
    if not zp.exists():
        pytest.skip("raw 1990 cohort zip absent (gitignored, out-of-tree)")

    rows = list(iter_parsed_records(zp, 1990, max_rows=300))
    assert rows, "no parsed rows"
    assert all("link_segment" not in r for r in rows), (
        "1989-1991 is a single-member denominator-plus (no link_segment; "
        "the keyless link_segment is 1983-1988 only)"
    )
    batch = pa.RecordBatch.from_pylist(rows)
    out = _harmonize_batch(batch, 1990)

    # schema == the extended OUT_SCHEMA; H6 row-count conservation
    assert out.schema.equals(OUT_SCHEMA)
    assert out.num_rows == len(rows)

    d = out.to_pydict()
    assert set(d["data_year"]) == {1990}
    assert set(d["certificate_revision"]) == {"unrevised_1989"}

    # the §15.D DO-step-1 ICD-9 default-null: cohort 1990 deaths are
    # ICD-9 → the ICD-10 cause columns are 100% null; the ICD-9 columns
    # carry the signal for the death rows.
    assert all(v is None for v in d["underlying_cause_icd10"]), (
        "cohort 1990 = ICD-9 era; underlying_cause_icd10 must be null"
    )
    assert all(v is None for v in d["cause_recode_130"]), (
        "cohort 1990 = ICD-9 era; cause_recode_130 must be null"
    )

    # maternal_age plausible (schema domain 10-54 ∪ null)
    ages = [a for a in d["maternal_age"] if a is not None]
    assert ages, "no maternal_age parsed"
    assert min(ages) >= 10 and max(ages) <= 54, f"maternal_age out of range: {min(ages)}-{max(ages)}"

    # infant_sex enum
    assert set(d["infant_sex"]) <= {"M", "F", None}

    # INDEPENDENT cross-check (L3 / §7-#13): the harmonizer derives
    # infant_death from AGED-non-blank; MATCHS@1 is the *separate*
    # NCHS match-status field (the 5b/3b model: linked infant deaths =
    # MATCHS ∈ {1,2}; surviving births = MATCHS 3). On real cohort data
    # the two signals MUST agree row-for-row — a disagreement means the
    # infant_death derivation (or the MATCHS interpretation) is wrong and
    # is a §7 halt surfaced here at the cheap SMOKE moment, not at the
    # expensive DO step 6 re-harmonize / NCHS-cohort-report VERIFY.
    matchs = [str(r.get("MATCHS", "")).strip() for r in rows]
    death_by_matchs = [m in ("1", "2") for m in matchs]
    death_by_aged = [a is not None for a in d["age_at_death_days"]]
    assert d["infant_death"] == death_by_aged, "infant_death must == AGED-non-blank"
    assert death_by_aged == death_by_matchs, (
        "infant_death (AGED-derived) disagrees with MATCHS∈{1,2} on real "
        f"LinkCO90 data — §7-#13 halt. AGED-deaths={sum(death_by_aged)}, "
        f"MATCHS-deaths={sum(death_by_matchs)}"
    )
    # the death rows carry the ICD-9 underlying cause; survivors do not
    for is_death, icd9 in zip(d["infant_death"], d["underlying_cause_icd9"]):
        if is_death:
            assert icd9 is not None and icd9.strip() != "", (
                "infant-death row missing ICD-9 underlying cause"
            )
