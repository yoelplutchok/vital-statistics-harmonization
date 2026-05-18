#!/usr/bin/env python3
"""
Harmonize linked birth-infant death Parquet files (2005-2015) into a single
stacked file with both birth-side and death-side harmonized columns.

Birth-side columns match the natality V2 harmonized schema.
Death-side columns are new: infant_death, age_at_death_days, age_at_death_recode5,
underlying_cause_icd10, cause_recode_130, manner_of_death, record_weight.

Output is written in a memory-bounded streaming fashion.

Usage:
  python harmonize_linked_v3.py
  python harmonize_linked_v3.py --years 2010-2015
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--linked-dir",
        type=Path,
        default=repo_root / "output" / "linked",
        help="Directory containing linked_{year}_denomplus.parquet",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v3_linked_harmonized.parquet",
        help="Output Parquet path",
    )
    p.add_argument(
        "--years", type=str, default="2005-2023",
        help="Comma years or range like 2005-2023 (default = full V3 linked coverage)",
    )
    p.add_argument(
        "--batch-rows", type=int, default=500_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


# ---------------------------------------------------------------------------
# Arrow helper functions (same as harmonize_v1_core.py)
# ---------------------------------------------------------------------------

def _trim(arr: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    return pc.utf8_trim_whitespace(arr)


def _to_int_or_null(
    arr: pa.Array | pa.ChunkedArray, out_type: pa.DataType
) -> pa.Array | pa.ChunkedArray:
    trimmed = _trim(arr)
    trimmed_or_null = pc.if_else(
        pc.equal(trimmed, ""), pa.scalar(None, type=pa.string()), trimmed
    )
    return pc.cast(trimmed_or_null, out_type, safe=False)


def _to_float_or_null(
    arr: pa.Array | pa.ChunkedArray, out_type: pa.DataType = pa.float64()
) -> pa.Array | pa.ChunkedArray:
    trimmed = _trim(arr)
    trimmed_or_null = pc.if_else(
        pc.equal(trimmed, ""), pa.scalar(None, type=pa.string()), trimmed
    )
    return pc.cast(trimmed_or_null, out_type, safe=False)


def _to_str_or_null(arr: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    trimmed = _trim(arr)
    return pc.if_else(
        pc.equal(trimmed, ""), pa.scalar(None, type=pa.string()), trimmed
    )


def _get_col(batch: pa.RecordBatch, name: str) -> pa.Array:
    idx = batch.schema.get_field_index(name)
    if idx == -1:
        raise KeyError(name)
    return batch.column(idx)


def _get_col_optional(batch: pa.RecordBatch, name: str) -> pa.Array | None:
    idx = batch.schema.get_field_index(name)
    if idx == -1:
        return None
    return batch.column(idx)


def _meduc_to_cat4(meduc: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(meduc), null_s, null_s)
    out = pc.if_else(
        pc.or_(pc.equal(meduc, 1), pc.equal(meduc, 2)),
        pa.scalar("lt_hs"), out,
    )
    out = pc.if_else(pc.equal(meduc, 3), pa.scalar("hs_grad"), out)
    out = pc.if_else(
        pc.or_(pc.equal(meduc, 4), pc.equal(meduc, 5)),
        pa.scalar("some_college"), out,
    )
    out = pc.if_else(
        pc.or_(pc.or_(pc.equal(meduc, 6), pc.equal(meduc, 7)), pc.equal(meduc, 8)),
        pa.scalar("ba_plus"), out,
    )
    return out


def _meduc_rec_to_cat4(meduc_rec: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(meduc_rec), null_s, null_s)
    out = pc.if_else(
        pc.or_(pc.equal(meduc_rec, 1), pc.equal(meduc_rec, 2)),
        pa.scalar("lt_hs"), out,
    )
    out = pc.if_else(pc.equal(meduc_rec, 3), pa.scalar("hs_grad"), out)
    out = pc.if_else(pc.equal(meduc_rec, 4), pa.scalar("some_college"), out)
    out = pc.if_else(pc.equal(meduc_rec, 5), pa.scalar("ba_plus"), out)
    return out


def _month_to_trimester(month: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(month), null_s, null_s)
    out = pc.if_else(pc.equal(month, 99), pa.scalar("unknown"), out)
    out = pc.if_else(pc.equal(month, 0), pa.scalar("none"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 1), pc.less_equal(month, 3)),
        pa.scalar("1st"), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 4), pc.less_equal(month, 6)),
        pa.scalar("2nd"), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 7), pc.less_equal(month, 10)),
        pa.scalar("3rd"), out,
    )
    return out


def _max_recode6_ignoring_unknown(
    a: pa.Array | pa.ChunkedArray,
    b: pa.Array | pa.ChunkedArray,
    c: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    int8 = pa.int8()
    unknown = pa.scalar(6, type=int8)
    null_i8 = pa.scalar(None, type=int8)

    def _known(x):
        return pc.if_else(pc.equal(x, unknown), null_i8, x)

    max_known = pc.max_element_wise(
        pc.max_element_wise(_known(a), _known(b)), _known(c)
    )
    any_unknown = pc.or_(
        pc.or_(
            pc.fill_null(pc.equal(a, unknown), False),
            pc.fill_null(pc.equal(b, unknown), False),
        ),
        pc.fill_null(pc.equal(c, unknown), False),
    )
    return pc.if_else(pc.and_(pc.is_null(max_known), any_unknown), unknown, max_known)


def _fagerec11_to_cat(
    rec11: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map FAGEREC11 (01-11) to a categorical string matching father_age_cat buckets."""
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(rec11), null_s, null_s)
    out = pc.if_else(
        pc.or_(pc.equal(rec11, 1), pc.equal(rec11, 2)),
        pa.scalar("<20"), out,
    )
    out = pc.if_else(pc.equal(rec11, 3), pa.scalar("20-24"), out)
    out = pc.if_else(pc.equal(rec11, 4), pa.scalar("25-29"), out)
    out = pc.if_else(pc.equal(rec11, 5), pa.scalar("30-34"), out)
    out = pc.if_else(pc.equal(rec11, 6), pa.scalar("35-39"), out)
    out = pc.if_else(
        pc.and_(
            pc.fill_null(pc.greater_equal(rec11, 7), False),
            pc.fill_null(pc.less_equal(rec11, 10), False),
        ),
        pa.scalar("40+"), out,
    )
    return out


def _cigs_count_to_recode6(count: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    int8 = pa.int8()
    null_i8 = pa.scalar(None, type=int8)
    out = pc.if_else(pc.is_null(count), null_i8, null_i8)
    out = pc.if_else(pc.equal(count, 0), pa.scalar(0, type=int8), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 1), pc.less_equal(count, 5)),
        pa.scalar(1, type=int8), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 6), pc.less_equal(count, 10)),
        pa.scalar(2, type=int8), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 11), pc.less_equal(count, 20)),
        pa.scalar(3, type=int8), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 21), pc.less_equal(count, 40)),
        pa.scalar(4, type=int8), out,
    )
    out = pc.if_else(pc.greater_equal(count, 41), pa.scalar(5, type=int8), out)
    out = pc.if_else(pc.equal(count, 99), pa.scalar(6, type=int8), out)
    return out


# ---------------------------------------------------------------------------
# Output schema: birth-side (same as V2) + death-side columns
# ---------------------------------------------------------------------------

OUT_SCHEMA = pa.schema([
    # Birth-side (same as natality V2 harmonized)
    ("data_year", pa.int16()),
    ("residence_status", pa.int8()),
    ("is_foreign_resident", pa.bool_()),
    ("certificate_revision", pa.string()),
    ("maternal_age", pa.int16()),
    ("live_birth_order_recode", pa.int8()),
    ("total_birth_order_recode", pa.int8()),
    ("marital_status", pa.int8()),
    ("marital_reporting_flag", pa.bool_()),
    ("hispanic_origin", pa.int8()),
    ("maternal_hispanic", pa.bool_()),
    ("maternal_race_bridged", pa.int8()),
    ("maternal_race_ethnicity_5", pa.string()),
    ("maternal_race_detail", pa.string()),
    ("maternal_race_detail_15cat", pa.string()),
    ("race_bridge_method", pa.string()),
    ("maternal_education_cat4", pa.string()),
    ("prenatal_care_start_month", pa.int16()),
    ("prenatal_care_start_trimester", pa.string()),
    ("prenatal_visits", pa.int16()),
    ("smoking_any_during_pregnancy", pa.bool_()),
    ("smoking_intensity_max_recode6", pa.int8()),
    ("smoking_pre_pregnancy_recode6", pa.int8()),
    ("diabetes_any", pa.int8()),
    ("hypertension_chronic", pa.int8()),
    ("hypertension_gestational", pa.int8()),
    ("plurality_recode", pa.int8()),
    ("infant_sex", pa.string()),
    ("gestational_age_weeks", pa.int16()),
    ("gestational_age_weeks_source", pa.string()),
    ("preterm_recode3", pa.int8()),
    ("birthweight_grams", pa.int32()),
    ("delivery_method_recode", pa.int8()),
    ("apgar5", pa.int16()),
    ("bmi_prepregnancy", pa.float32()),
    ("bmi_prepregnancy_recode6", pa.int8()),
    ("father_age", pa.int16()),
    ("father_age_cat_from_rec11", pa.string()),
    ("birth_facility", pa.string()),
    ("attendant_at_birth", pa.int8()),
    ("payment_source_recode", pa.int8()),
    ("prior_cesarean", pa.bool_()),
    ("father_hispanic", pa.bool_()),
    ("father_race_ethnicity_5", pa.string()),
    ("father_education_cat4", pa.string()),
    ("ca_anencephaly", pa.bool_()),
    ("ca_spina_bifida", pa.bool_()),
    ("ca_cchd", pa.bool_()),
    ("ca_cdh", pa.bool_()),
    ("ca_omphalocele", pa.bool_()),
    ("ca_gastroschisis", pa.bool_()),
    ("ca_limb_reduction", pa.bool_()),
    ("ca_cleft_lip", pa.bool_()),
    ("ca_cleft_palate", pa.bool_()),
    ("ca_down_syndrome", pa.bool_()),
    ("ca_chromosomal_disorder", pa.bool_()),
    ("ca_hypospadias", pa.bool_()),
    ("infection_gonorrhea", pa.bool_()),
    ("infection_syphilis", pa.bool_()),
    ("infection_chlamydia", pa.bool_()),
    ("infection_hep_b", pa.bool_()),
    ("infection_hep_c", pa.bool_()),
    ("prior_cesarean_count", pa.int8()),
    ("fertility_enhancing_drugs", pa.bool_()),
    ("assisted_reproductive_tech", pa.bool_()),
    # Clinical detail (2014+ only)
    ("pre_pregnancy_diabetes", pa.bool_()),
    ("gestational_diabetes", pa.bool_()),
    ("nicu_admission", pa.bool_()),
    ("weight_gain_pounds", pa.int16()),
    ("induction_of_labor", pa.bool_()),
    ("breastfed_at_discharge", pa.bool_()),
    # Death-side (V3 linked additions)
    ("infant_death", pa.bool_()),
    ("age_at_death_days", pa.int16()),
    ("age_at_death_recode5", pa.int8()),
    ("underlying_cause_icd10", pa.string()),
    ("cause_recode_130", pa.int16()),
    # C8.18 DO step 5c-i: within_era ICD-9 cause representation for the
    # cohort 1983-1998 backward extension (H7 fetal-death sibling-parity:
    # cause_icd10 is within_era there too — ICD-9/10 are NOT fabricated
    # into one cross-era column). underlying_cause_icd10 / cause_recode_130
    # go NULL for cohort birth-year 1983-1998 (the ICD-9 era; §15.D DO
    # step 1 default-null + revision-tagged, DECISION_LOG 2026-05-17T05:30Z);
    # these two carry the ICD-9 signal there and are NULL for 1999+.
    ("underlying_cause_icd9", pa.string()),
    ("cause_recode_61", pa.int16()),
    ("manner_of_death", pa.int8()),
    ("record_weight", pa.float64()),
])


def _yn_to_bool(
    arr: pa.Array | pa.ChunkedArray,
    true_values: tuple[str, ...] = ("Y",),
) -> pa.Array | pa.ChunkedArray:
    """Map Y/N/U (or C/P/N/U) string field to bool."""
    s = _to_str_or_null(arr)
    null_b = pa.scalar(None, type=pa.bool_())
    out = pc.if_else(pc.is_null(s), null_b, null_b)
    out = pc.if_else(pc.equal(s, pa.scalar("N")), pa.scalar(False), out)
    for tv in true_values:
        out = pc.if_else(pc.equal(s, pa.scalar(tv)), pa.scalar(True), out)
    return out


def _racehisp_combined_to_5cat(
    code: pa.Array | pa.ChunkedArray,
    is_2014_plus: bool,
) -> pa.Array | pa.ChunkedArray:
    """Map FRACEHISP combined code to 5-category string.

    Two coding schemes exist:
      FRACEHISP (2003-2013): 1-5→Hispanic, 6→NH_white, 7→NH_black,
        8→NH_other, 9→null.
      FRACEHISP (2014+): 1→NH_white, 2→NH_black, 3-6→NH_other,
        7→Hispanic, 8-9→null.
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(code), null_s, null_s)

    if is_2014_plus:
        out = pc.if_else(pc.equal(code, 1), pa.scalar("NH_white"), out)
        out = pc.if_else(pc.equal(code, 2), pa.scalar("NH_black"), out)
        out = pc.if_else(
            pc.and_(pc.greater_equal(code, 3), pc.less_equal(code, 6)),
            pa.scalar("NH_other"), out,
        )
        out = pc.if_else(pc.equal(code, 7), pa.scalar("Hispanic"), out)
    else:
        out = pc.if_else(
            pc.and_(pc.greater_equal(code, 1), pc.less_equal(code, 5)),
            pa.scalar("Hispanic"), out,
        )
        out = pc.if_else(pc.equal(code, 6), pa.scalar("NH_white"), out)
        out = pc.if_else(pc.equal(code, 7), pa.scalar("NH_black"), out)
        out = pc.if_else(pc.equal(code, 8), pa.scalar("NH_other"), out)
    return out


def _pldel_to_facility(
    pldel: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map unrevised PLDEL/UBFACIL code to harmonized birth facility string.
    1=Hospital, 2=Birth Center, 3=Clinic, 4=Residence, 5=Other, 9=Unknown."""
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(pldel), null_s, null_s)
    out = pc.if_else(pc.equal(pldel, 1), pa.scalar("hospital"), out)
    out = pc.if_else(pc.equal(pldel, 2), pa.scalar("birth_center"), out)
    out = pc.if_else(pc.equal(pldel, 3), pa.scalar("clinic_other"), out)
    out = pc.if_else(pc.equal(pldel, 4), pa.scalar("home"), out)
    out = pc.if_else(pc.equal(pldel, 5), pa.scalar("clinic_other"), out)
    return out


def _bfacil_to_facility(
    bfacil: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map revised-era BFACIL code to harmonized birth facility string."""
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(bfacil), null_s, null_s)
    out = pc.if_else(pc.equal(bfacil, 1), pa.scalar("hospital"), out)
    out = pc.if_else(pc.equal(bfacil, 2), pa.scalar("birth_center"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(bfacil, 3), pc.less_equal(bfacil, 5)),
        pa.scalar("home"), out,
    )
    out = pc.if_else(pc.equal(bfacil, 6), pa.scalar("clinic_other"), out)
    out = pc.if_else(pc.equal(bfacil, 7), pa.scalar("clinic_other"), out)
    return out


# ---------------------------------------------------------------------------
# C8.18 DO step 5c-i — per-cohort-era harmonize architecture
# ---------------------------------------------------------------------------
# The linked cohort 1983-2004 denominator(-plus) birth section IS a birth
# certificate of the SAME revision natality already harmonizes
# (`harmonize_v1_core.py`): 1989-1991 = 1989-revision == natality V2
# 1990-2002 (`is_pre2003`); 1983-1988 = 1968/1978-revision ~= natality
# `is_pre1989`; 2003/2004 = the 2003-revision transition. So the cohort
# birth-side map ALIASES the cohort raw names onto the natality V1-core
# era recodes (H7 sibling-parity — reuse, do NOT re-derive). ICD-9 (cohort
# birth-year 1983-1998) vs ICD-10 (1999+) is a within_era split per the
# §15.D DO step 1 default-null + revision-tagged decision (DECISION_LOG
# 2026-05-17T05:30:00Z): underlying_cause_icd9 / cause_recode_61 carry the
# ICD-9 era; underlying_cause_icd10 / cause_recode_130 are NULL there.
#
# §15.D DO step 5c is decomposed -> 5c-i / 5c-ii / 5c-iii (the 5->5a/5b/5c
# + 4->4a/4b/4c + 3->3a/3b precedent; §2 cheap-before-expensive / §9-#8;
# soft-flag (ii) §11 human-merge). THIS sub-step = 5c-i: the architecture
# + the within_era ICD-9 cause-column shape + the **1989-1991 reference
# era** end-to-end (lowest risk: single-member denominator-plus, ICD-9,
# closest to natality V2). 5c-ii = 1995-2002 + 2003 + 2004; 5c-iii = the
# keyless 1983-1988 link_segment den/num one-row-per-birth encoding.


def _dmeduc_years_to_cat4(
    dmeduc: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map 1989-revision education-in-years (00-17, 99=unknown) to the
    4-category harmonized value: lt_hs (0-11), hs_grad (12),
    some_college (13-15), ba_plus (16-17), 99/other -> null.

    Byte-identical to ``harmonize_v1_core._dmeduc_years_to_cat4`` (H7
    fetal-death/natality sibling-parity — the natality V2 1990-2002 +
    pre-1989 DMEDUC recode; asserted equal in
    ``test_linked_cohort_5c_harmonize_smoke.py``). Duplicated locally,
    not imported, to match this file's existing helper-duplication
    pattern ("Arrow helper functions (same as harmonize_v1_core.py)").
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(dmeduc), null_s, null_s)
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 0), pc.less_equal(dmeduc, 11)),
        pa.scalar("lt_hs"), out,
    )
    out = pc.if_else(pc.equal(dmeduc, 12), pa.scalar("hs_grad"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 13), pc.less_equal(dmeduc, 15)),
        pa.scalar("some_college"), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 16), pc.less_equal(dmeduc, 17)),
        pa.scalar("ba_plus"), out,
    )
    return out


def _mrace_detail_to_bridged4(
    mrace: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map 1989-revision detail race code (01-78) to the approximate
    bridged 4-category: 1=White, 2=Black, 3=AIAN, 4=Asian/PI; 09/other
    -> null. Byte-identical to
    ``harmonize_v1_core._mrace_detail_to_bridged4`` (H7 sibling-parity;
    asserted equal in the 5c SMOKE). Approximate crosswalk (official
    NCHS bridged race began with the 2003 transition) -> race_bridge
    method "approximate_pre2003".
    """
    int8 = pa.int8()
    null_i8 = pa.scalar(None, type=int8)
    out = pc.if_else(pc.is_null(mrace), null_i8, null_i8)
    out = pc.if_else(pc.equal(mrace, 1), pa.scalar(1, type=int8), out)
    out = pc.if_else(pc.equal(mrace, 2), pa.scalar(2, type=int8), out)
    out = pc.if_else(pc.equal(mrace, 3), pa.scalar(3, type=int8), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(mrace, 4), pc.less_equal(mrace, 8)),
        pa.scalar(4, type=int8), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(mrace, 18), pc.less_equal(mrace, 68)),
        pa.scalar(4, type=int8), out,
    )
    return out


def _detail_order_to_recode9(
    detail: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map the cohort detail birth order (DLIVORD 01-31 / DTOTORD 01-40,
    99=unknown) to the natality 9-category recode shape (schema
    allowed_values 1-7|8|9): 1-7 passthrough, 8-49 -> 8 (8 or more),
    99 -> 9 (unknown/not stated), blank/out-of-range -> null. The cohort
    1989-1991 denominator-plus carries only detail order (no LIVORD9 /
    TOTORD9 recode like natality 1990-2002), so the standard NCHS
    birth-order-9 recode is synthesized from detail (the natality
    is_pre1989 conservative-mapping precedent; SMOKE-edge-verified).
    """
    int8 = pa.int8()
    null_i8 = pa.scalar(None, type=int8)
    out = pc.if_else(pc.is_null(detail), null_i8, null_i8)
    out = pc.if_else(
        pc.and_(pc.greater_equal(detail, 1), pc.less_equal(detail, 7)),
        pc.cast(detail, int8), out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(detail, 8), pc.less_equal(detail, 49)),
        pa.scalar(8, type=int8), out,
    )
    out = pc.if_else(pc.equal(detail, 99), pa.scalar(9, type=int8), out)
    return out


def _mager41_to_age(
    mager41: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """Map the 2003-revision MAGER41 (01-41) age-of-mother recode to a
    single-year age: code 1 -> 14 (under 15); codes 2-41 -> code + 13
    (so 41 -> 54); 99 or > 41 -> null. Byte-identical to the
    ``harmonize_v1_core`` inline ``is_2003revised`` MAGER41 conversion
    (H7 fetal-death/natality sibling-parity; the cohort 2003 ``MAGER41``
    AND the cohort 2004 ``MAGER`` @89-90 are BOTH this recode-41, NOT a
    single-year age — field_specs 4b/4c + the 2026-05-19T20:00:00Z
    real-data probe; asserted equal in
    ``test_linked_cohort_5cii_b_harmonize_smoke.py``). Duplicated
    locally, not imported, to match this file's existing
    helper-duplication pattern.
    """
    i16 = pa.int16()
    age = pc.if_else(
        pc.equal(mager41, 1),
        pa.scalar(14, type=i16),
        pc.add(mager41, pa.scalar(13, type=i16)),
    )
    age = pc.if_else(
        pc.or_(pc.equal(mager41, 99), pc.greater(mager41, 41)),
        pa.scalar(None, type=i16),
        age,
    )
    return age


def _cohort_era(year: int) -> str | None:
    """Classify a linked year into its cohort-harmonize era, or None for
    the canonical >= 2005 v3 path (the cohort branch must NOT fire there
    -> the shipped 2005-2023 product is byte-identical, §9-#7-safe).

    1983-1988 -> "1983_1988" (keyless two-segment; 5c-iii)
    1989-1991 -> "1989_1991" (single-member denominator-plus; 5c-i)
    1995-2002 -> "1995_2002" (5c-ii)
    2003      -> "2003"      (5c-ii)
    2004      -> "2004"      (5c-ii)
    >= 2005   -> None        (canonical path; existing body unchanged)

    1992-1994 (the permanent NCHS linkage gap) and any year < 1983 are
    neither a configured cohort era nor the canonical path -> ValueError
    (§2 fail-closed; mirrors the parser `_layout_for_linked_year`
    dispatcher discipline — never silently route a gap/pre-series year
    through the 2005+ harmonize body).
    """
    if 1983 <= year <= 1988:
        return "1983_1988"
    if 1989 <= year <= 1991:
        return "1989_1991"
    if 1995 <= year <= 2002:
        return "1995_2002"
    if year == 2003:
        return "2003"
    if year == 2004:
        return "2004"
    if year >= 2005:
        return None
    raise ValueError(
        f"Year {year} is not a configured linked cohort era and not the "
        f"canonical >=2005 path. Supported cohort: 1983-1991 + 1995-2004 "
        f"(1992-1994 = the permanent NCHS linkage gap; pre-1983 has no "
        f"NCHS public-use cohort-linked series)."
    )


def _harmonize_cohort_1995_2002(batch: pa.RecordBatch, year: int) -> pa.Table:
    """Harmonize one batch of a 1995-2002 cohort denominator-plus parquet
    into the (extended) OUT_SCHEMA — C8.18 DO step 5c-ii-a.

    1995-2002 is the **1989-revision** birth certificate (== natality V2
    1990-2002 == the 5c-i 1989-1991 reference era's recode family); the
    birth-side map ALIASES the cohort raw names onto the natality V1-core
    1989-revision recodes (H7 sibling-parity — reuse the
    `_dmeduc_years_to_cat4` / `_mrace_detail_to_bridged4` /
    `_detail_order_to_recode9` / `_month_to_trimester` / `_pldel_to_facility`
    helpers; do NOT re-derive). Authored as a SEPARATE function (not a
    shared helper with the 1989-1991 branch) so the 5c-i-verified
    1989-1991 inline body in `_harmonize_cohort_batch` stays
    byte-untouched (§9-#7; this file's existing explicit-per-era
    helper-duplication pattern).

    Deltas vs the 5c-i 1989-1991 map (real-data-verified at the
    Convention-3 snapshot, PRE_FLIGHT_LOG 2026-05-19T14:00:00Z on
    LinkCO95US / LinkCO99US):
      * prenatal_visits source = NPREVIST (1995-2002) vs NPREVIS (1989-91).
      * NO DFEDUC on the 1995-2002 birth section -> father_education_cat4
        conservatively null (faithful "not on this file").
      * RECWT present (1995-2002 den-plus locs 223-230) -> record_weight
        float64 (1989-1991 had no RECWT field).
      * the within_era ICD-9/ICD-10 split keys on cohort BIRTH YEAR
        (§15.D DO step 1; DECISION_LOG 2026-05-17T05:30Z + 2026-05-19
        T11:00Z): cohort 1995-1998 = ICD-9 -> underlying_cause_icd9 /
        cause_recode_61 (UCOD / UCODR); cohort 1999-2002 = ICD-10 ->
        underlying_cause_icd10 / cause_recode_130. The other pair stays
        null (the §15.D DO-step-1 default-null + revision-tagged shape;
        the data is unambiguous — ICD-9 numeric e.g. "7980" vs ICD-10
        alpha-prefixed e.g. "P073").
      * NO MANNER on the 1995-2002 den-plus -> manner_of_death null.
    Composite multi-field blocks (MEDRISK / OBSTETRC / LABOR / DELMETH /
    NEWBORN / CONGENIT) stay conservatively NULL (soft-flag (gg) leaf
    decomposition = DO step 6; the natality is_pre1989 / 5c-i precedent).
    """
    if _cohort_era(year) != "1995_2002":
        raise ValueError(
            f"_harmonize_cohort_1995_2002 is era-scoped to 1995-2002; got "
            f"year {year} (era {_cohort_era(year)!r}). The sanctioned entry "
            f"is the _harmonize_cohort_batch dispatch (§2 fail-closed — "
            f"never silently mis-harmonize a wrong-era batch)."
        )

    n = batch.num_rows
    null_s = pa.scalar(None, type=pa.string())

    def opt_str(name: str) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_str_or_null(c) if c is not None else pa.nulls(n, pa.string())

    def opt_int(name: str, t: pa.DataType) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_int_or_null(c, t) if c is not None else pa.nulls(n, t)

    def _safe_cond(*parts):
        from functools import reduce
        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

    # Default EVERY OUT_SCHEMA column to a typed null; override the
    # fields the 1995-2002 cohort denominator-plus actually carries.
    out: dict[str, pa.Array] = {
        f.name: pa.nulls(n, type=f.type) for f in OUT_SCHEMA
    }

    year_arr = pc.cast(_get_col(batch, "year"), pa.int16())
    out["data_year"] = year_arr
    out["certificate_revision"] = pc.if_else(
        pc.is_null(year_arr), null_s, pa.scalar("unrevised_1989"),
    )

    restatus = opt_int("RESSTATB", pa.int8())
    out["residence_status"] = restatus
    out["is_foreign_resident"] = pc.equal(restatus, pa.scalar(4, type=pa.int8()))

    out["maternal_age"] = opt_int("DMAGE", pa.int16())
    out["live_birth_order_recode"] = _detail_order_to_recode9(
        opt_int("DLIVORD", pa.int16())
    )
    out["total_birth_order_recode"] = _detail_order_to_recode9(
        opt_int("DTOTORD", pa.int16())
    )
    out["marital_status"] = opt_int("DMAR", pa.int8())

    hisp = opt_int("ORMOTH", pa.int8())
    out["hispanic_origin"] = hisp
    is_hisp = pc.and_(
        pc.greater_equal(hisp, pa.scalar(1, type=pa.int8())),
        pc.less_equal(hisp, pa.scalar(5, type=pa.int8())),
    )
    is_nonhisp = pc.equal(hisp, pa.scalar(0, type=pa.int8()))
    mat_hisp = pc.if_else(
        is_hisp, pa.scalar(True),
        pc.if_else(is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    out["maternal_hispanic"] = mat_hisp

    mrace_detail = opt_int("MRACE", pa.int16())
    race_bridged = _mrace_detail_to_bridged4(mrace_detail)
    out["maternal_race_bridged"] = race_bridged
    out["maternal_race_detail"] = opt_str("MRACE")
    race_eth = pc.if_else(
        pc.fill_null(pc.equal(mat_hisp, pa.scalar(True)), False),
        pa.scalar("Hispanic"), null_s,
    )
    is_nh = pc.fill_null(pc.equal(mat_hisp, pa.scalar(False)), False)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)),
                          pa.scalar("NH_white"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)),
                          pa.scalar("NH_black"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)),
                          pa.scalar("NH_aian"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)),
                          pa.scalar("NH_asian_pi"), race_eth)
    out["maternal_race_ethnicity_5"] = race_eth
    out["race_bridge_method"] = pc.if_else(
        pc.is_null(year_arr), null_s, pa.scalar("approximate_pre2003"),
    )

    out["maternal_education_cat4"] = _dmeduc_years_to_cat4(
        opt_int("DMEDUC", pa.int16())
    )

    pn_month = opt_int("MONPRE", pa.int16())
    out["prenatal_care_start_month"] = pn_month
    out["prenatal_care_start_trimester"] = _month_to_trimester(pn_month)
    # DELTA vs the 5c-i 1989-1991 map: 1995-2002 carries NPREVIST (not
    # the 1989-1991 NPREVIS) for the prenatal-visit count.
    out["prenatal_visits"] = opt_int("NPREVIST", pa.int16())

    out["plurality_recode"] = opt_int("DPLURAL", pa.int8())

    csex = opt_int("CSEX", pa.int8())
    out["infant_sex"] = pc.if_else(
        pc.equal(csex, pa.scalar(1, type=pa.int8())), pa.scalar("M"),
        pc.if_else(pc.equal(csex, pa.scalar(2, type=pa.int8())),
                   pa.scalar("F"), null_s),
    )

    gw = opt_int("GESTAT", pa.int16())
    _keep = pc.or_(
        pc.fill_null(pc.and_(
            pc.greater_equal(gw, pa.scalar(17, type=pa.int16())),
            pc.less_equal(gw, pa.scalar(47, type=pa.int16())),
        ), False),
        pc.fill_null(pc.equal(gw, pa.scalar(99, type=pa.int16())), False),
    )
    gw = pc.if_else(_keep, gw, pa.scalar(None, type=pa.int16()))
    out["gestational_age_weeks"] = gw
    out["gestational_age_weeks_source"] = pc.if_else(
        pc.is_null(gw), null_s, pa.scalar("lmp"),
    )

    out["birthweight_grams"] = opt_int("DBIRWT", pa.int32())
    out["apgar5"] = opt_int("FMAPS", pa.int16())

    fage = opt_int("DFAGE", pa.int16())
    fage = pc.if_else(
        pc.and_(
            pc.greater_equal(fage, pa.scalar(9, type=pa.int16())),
            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
        ),
        fage, pa.scalar(None, type=pa.int16()),
    )
    out["father_age"] = fage

    out["birth_facility"] = _pldel_to_facility(opt_int("PLDEL", pa.int8()))

    attend = opt_int("BIRATTND", pa.int8())
    out["attendant_at_birth"] = pc.if_else(
        pc.equal(attend, pa.scalar(9, type=pa.int8())),
        pa.scalar(None, type=pa.int8()), attend,
    )

    forig = opt_int("ORFATH", pa.int8())
    f_is_hisp = pc.and_(
        pc.greater_equal(forig, pa.scalar(1, type=pa.int8())),
        pc.less_equal(forig, pa.scalar(5, type=pa.int8())),
    )
    f_is_nonhisp = pc.equal(forig, pa.scalar(0, type=pa.int8()))
    out["father_hispanic"] = pc.if_else(
        f_is_hisp, pa.scalar(True),
        pc.if_else(f_is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    # DELTA: the 1995-2002 birth section carries NO DFEDUC (verified on
    # real LinkCO95/99 data) -> father_education_cat4 stays null (the
    # default; faithful "not on this file", not a parser bug).

    # === Death-side: the 1995-2002 cohort denominator-plus "plus"
    # (AGED@211-213 .. RECWT@223-230) — within_era ICD-9/ICD-10 split ===
    aged = opt_int("AGED", pa.int16())
    # A 1995-2002 denominator-plus row is a linked infant death IFF the
    # appended death "plus" carries an age at death (blank for survivors,
    # 000-364 days for deaths) — the value-driven signal (no MATCHS-code
    # assumption; the SMOKE Tier-1 independently cross-checks it against
    # MATCHS in {1,2} on real LinkCO95/99 data, §7-#13).
    infant_death = pc.invert(pc.is_null(aged))
    out["infant_death"] = pc.fill_null(infant_death, False)
    out["age_at_death_days"] = aged
    out["age_at_death_recode5"] = opt_int("AGER5", pa.int8())

    # within_era ICD-9 (cohort birth-year 1995-1998) vs ICD-10
    # (1999-2002), keyed on the cohort BIRTH YEAR (§15.D DO step 1; the
    # 5c-i resolved cause-column shape). Each 1995-2002 file is one
    # cohort year, so `year` selects the revision for the whole batch.
    ucod = opt_str("UCOD")
    ucodr = opt_int("UCODR", pa.int16())
    if year <= 1998:
        out["underlying_cause_icd9"] = ucod          # ICD-9, populated
        out["cause_recode_61"] = ucodr               # 61-cause ICD-9
        # underlying_cause_icd10 / cause_recode_130 stay null (default)
    else:
        out["underlying_cause_icd10"] = ucod         # ICD-10, populated
        out["cause_recode_130"] = ucodr              # 130-cause ICD-10
        # underlying_cause_icd9 / cause_recode_61 stay null (default)

    # RECWT present on the 1995-2002 den-plus (locs 223-230; the
    # 1989-1991 era had none -> null there). manner_of_death is NOT on
    # the 1995-2002 den-plus death section -> null (faithful "not on
    # this file"; the richer numerator MANNER/multiple-cause = DO 6).
    recwt = _get_col_optional(batch, "RECWT")
    out["record_weight"] = (
        _to_float_or_null(recwt, pa.float64())
        if recwt is not None else pa.nulls(n, type=pa.float64())
    )

    return pa.Table.from_arrays(
        [out[f.name] for f in OUT_SCHEMA], schema=OUT_SCHEMA,
    )


def _harmonize_cohort_2003_2004(batch: pa.RecordBatch, year: int) -> pa.Table:
    """Harmonize one batch of a 2003 OR 2004 cohort denominator-plus
    parquet into the (extended) OUT_SCHEMA — C8.18 DO step 5c-ii-b.

    2003 + 2004 are the **2003-revision dual-certificate transition**
    (the natality V1-core ``is_2003revised`` analog). ONE function
    handles BOTH (ONE §15.D sub-step 5c-ii-b, ONE cert revision; the
    2003-vs-2004 deltas are pure raw-name aliasing — ``MAGER41``↔
    ``MAGER`` @89-90; ``DBWT``↔``BRTHWGT`` @467-470; the death
    match-status ``MATCHS``↔``FLGND`` is NOT consumed here, the
    harmonizer is AGED-value-driven — resolved via ``_get_col_optional``
    name-fallback, the natality V1-core single ``is_2003revised`` branch
    pattern; §9-#8 PRE_FLIGHT_LOG 2026-05-19T20:00:00Z (B)).

    The birth section ALIASES the cohort raw names onto the natality
    V1-core 2003-rev recodes (H7 sibling-parity — reuse ``_meduc_to_cat4``
    / ``_meduc_rec_to_cat4`` / ``_month_to_trimester`` /
    ``_fagerec11_to_cat`` / ``_pldel_to_facility`` /
    ``_mrace_detail_to_bridged4`` + the NEW ``_mager41_to_age``; do NOT
    re-derive). Authored as a SEPARATE function (not a shared helper
    with the 1989-1991 / 1995-2002 branches) so the 5c-i-verified
    1989-1991 inline body + the 5c-ii-a ``_harmonize_cohort_1995_2002``
    stay byte-untouched (§9-#7; the file's explicit-per-era
    helper-duplication pattern).

    Dual-cert handled faithfully via the natality V1-core coalesce
    (real-data-verified at the Convention-3 snapshot, PRE_FLIGHT_LOG
    2026-05-19T20:00:00Z (A) on LinkCO03US/LinkCO04US — the public-use
    cohort 2003/2004 den-plus is predominantly REVISION='S'
    1989-unrevised, so MEDUC/PRECARE/MBRACE are blank there and the
    1989-unrevised siblings UMEDUC/MEDUC_REC/MPCB/MRACE carry the
    values):
      * ``certificate_revision`` = has_MEDUC -> revised_2003 ; else
        has_MRACE -> unrevised_1989 ; else unknown (the natality V1-core
        has_meduc/has_mrace heuristic; matches the schema `derivation`
        column + REVISION@7 S/A semantics).
      * ``maternal_education_cat4`` = if_else(is_null(_meduc_to_cat4(
        MEDUC)), _meduc_rec_to_cat4(MEDUC_REC), _meduc_to_cat4(MEDUC))
        (byte-identical to natality V1-core 2003-rev education).
      * ``prenatal_care_start_month`` = if_else(is_null(PRECARE), MPCB,
        PRECARE) (natality V1-core dual-cert).
      * ``maternal_age`` = _mager41_to_age(MAGER41 [2003] / MAGER
        [2004]); ``gestational_age_weeks_source`` = "combined" (2003-rev
        COMBGEST; the per-era delta vs the 5c-ii-a "lmp"); ``MANNER``
        present -> ``manner_of_death`` (NEW vs 1995-2002); ``RECWT``
        present -> ``record_weight``; ALL ICD-10 (cohort 2003/2004
        >= 1999 -> ``underlying_cause_icd10`` / ``cause_recode_130``;
        the ICD-9 cols null — the 5c-i resolved shape, §15.D DO step 1).

    Composite multi-field blocks (MEDRISK / OBSTETRC / LABOR / DELMETH /
    NEWBORN / CONGENIT / ENTITY / RECORD) + smoking / diabetes /
    hypertension / preterm_recode3 / father_race_ethnicity_5 /
    father_education_cat4 / payment / prior_cesarean stay conservatively
    NULL (soft-flag (gg) leaf decomposition = DO step 6; the natality
    is_pre1989 / 5c-i / 5c-ii-a conservative-mapping precedent).
    """
    if _cohort_era(year) not in ("2003", "2004"):
        raise ValueError(
            f"_harmonize_cohort_2003_2004 is era-scoped to 2003-2004; got "
            f"year {year} (era {_cohort_era(year)!r}). The sanctioned entry "
            f"is the _harmonize_cohort_batch dispatch (§2 fail-closed — "
            f"never silently mis-harmonize a wrong-era batch)."
        )

    n = batch.num_rows
    null_s = pa.scalar(None, type=pa.string())

    def opt_str(name: str) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_str_or_null(c) if c is not None else pa.nulls(n, pa.string())

    def opt_int(name: str, t: pa.DataType) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_int_or_null(c, t) if c is not None else pa.nulls(n, t)

    def _safe_cond(*parts):
        from functools import reduce
        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

    # Default EVERY OUT_SCHEMA column to a typed null; override the
    # fields the 2003-revision cohort denominator-plus actually carries.
    out: dict[str, pa.Array] = {
        f.name: pa.nulls(n, type=f.type) for f in OUT_SCHEMA
    }

    year_arr = pc.cast(_get_col(batch, "year"), pa.int16())
    out["data_year"] = year_arr

    # === Dual-certificate revision (natality V1-core has_meduc/has_mrace
    # heuristic; matches the schema `derivation` column + REVISION@7 S/A;
    # H7). MEDUC (2003-rev 1-byte) is blank on S-rev rows; MRACE detail
    # is populated on both. ===
    meduc = opt_int("MEDUC", pa.int8())
    race_detail_str = opt_str("MRACE")
    has_meduc = pc.invert(pc.is_null(meduc))
    has_mrace = pc.invert(pc.is_null(race_detail_str))
    cert = pc.if_else(has_meduc, pa.scalar("revised_2003"), null_s)
    cert = pc.if_else(
        pc.and_(pc.is_null(cert), has_mrace),
        pa.scalar("unrevised_1989"), cert,
    )
    cert = pc.if_else(pc.is_null(cert), pa.scalar("unknown"), cert)
    out["certificate_revision"] = cert

    restatus = opt_int("RESTATUS", pa.int8())
    out["residence_status"] = restatus
    out["is_foreign_resident"] = pc.equal(restatus, pa.scalar(4, type=pa.int8()))

    # Maternal age: cohort 2003 = MAGER41, cohort 2004 = MAGER, BOTH the
    # 2003-rev recode-41 @89-90 (field_specs 4b/4c; the 2026-05-19
    # T20:00:00Z probe) -> the natality V1-core MAGER41 conversion.
    age_recode41 = opt_int("MAGER41", pa.int16())
    if _get_col_optional(batch, "MAGER41") is None:
        age_recode41 = opt_int("MAGER", pa.int16())
    out["maternal_age"] = _mager41_to_age(age_recode41)

    # Birth order: the cohort 2003/2004 den-plus carries the NCHS
    # LBO_REC / TBO_REC 1-9 recode directly (1-7 count, 8 = 8+, 9 =
    # unknown) — no detail-order synthesis needed (the 5c-ii-a
    # _detail_order_to_recode9 was for the 1989-rev DLIVORD detail).
    out["live_birth_order_recode"] = opt_int("LBO_REC", pa.int8())
    out["total_birth_order_recode"] = opt_int("TBO_REC", pa.int8())
    out["marital_status"] = opt_int("MAR", pa.int8())

    hisp = opt_int("UMHISP", pa.int8())
    out["hispanic_origin"] = hisp
    is_hisp = pc.and_(
        pc.greater_equal(hisp, pa.scalar(1, type=pa.int8())),
        pc.less_equal(hisp, pa.scalar(5, type=pa.int8())),
    )
    is_nonhisp = pc.equal(hisp, pa.scalar(0, type=pa.int8()))
    mat_hisp = pc.if_else(
        is_hisp, pa.scalar(True),
        pc.if_else(is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    out["maternal_hispanic"] = mat_hisp

    mrace_detail = opt_int("MRACE", pa.int16())
    race_bridged = _mrace_detail_to_bridged4(mrace_detail)
    out["maternal_race_bridged"] = race_bridged
    out["maternal_race_detail"] = opt_str("MRACE")
    race_eth = pc.if_else(
        pc.fill_null(pc.equal(mat_hisp, pa.scalar(True)), False),
        pa.scalar("Hispanic"), null_s,
    )
    is_nh = pc.fill_null(pc.equal(mat_hisp, pa.scalar(False)), False)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)),
                          pa.scalar("NH_white"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)),
                          pa.scalar("NH_black"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)),
                          pa.scalar("NH_aian"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)),
                          pa.scalar("NH_asian_pi"), race_eth)
    out["maternal_race_ethnicity_5"] = race_eth
    out["race_bridge_method"] = pc.if_else(
        pc.is_null(year_arr), null_s, pa.scalar("approximate_pre2003"),
    )

    # Education (dual-cert coalesce; byte-identical to natality V1-core
    # 2003-rev): revised MEDUC -> _meduc_to_cat4; else unrevised
    # MEDUC_REC -> _meduc_rec_to_cat4.
    meduc_cat = _meduc_to_cat4(meduc)
    meduc_rec_cat = _meduc_rec_to_cat4(opt_int("MEDUC_REC", pa.int8()))
    out["maternal_education_cat4"] = pc.if_else(
        pc.is_null(meduc_cat), meduc_rec_cat, meduc_cat,
    )

    # Prenatal care start month (dual-cert: revised PRECARE vs unrevised
    # MPCB; natality V1-core).
    precare = opt_int("PRECARE", pa.int16())
    mpcb = opt_int("MPCB", pa.int16())
    pn_month = pc.if_else(pc.is_null(precare), mpcb, precare)
    out["prenatal_care_start_month"] = pn_month
    out["prenatal_care_start_trimester"] = _month_to_trimester(pn_month)
    out["prenatal_visits"] = opt_int("UPREVIS", pa.int16())

    out["plurality_recode"] = opt_int("DPLURAL", pa.int8())

    # SEX is already decoded to "M"/"F" by the parser (the 2026-05-19
    # T20:00:00Z probe) — NOT the 1989-rev CSEX int 1/2.
    sex = opt_str("SEX")
    out["infant_sex"] = pc.if_else(
        pc.equal(sex, pa.scalar("M")), pa.scalar("M"),
        pc.if_else(pc.equal(sex, pa.scalar("F")), pa.scalar("F"), null_s),
    )

    gw = opt_int("COMBGEST", pa.int16())
    _keep = pc.or_(
        pc.fill_null(pc.and_(
            pc.greater_equal(gw, pa.scalar(17, type=pa.int16())),
            pc.less_equal(gw, pa.scalar(47, type=pa.int16())),
        ), False),
        pc.fill_null(pc.equal(gw, pa.scalar(99, type=pa.int16())), False),
    )
    gw = pc.if_else(_keep, gw, pa.scalar(None, type=pa.int16()))
    out["gestational_age_weeks"] = gw
    # 2003-rev COMBGEST = the combined LMP/clinical gestation (the
    # natality V1-core "combined" source; schema-documented "combined for
    # 2003-2013"; the per-era delta vs the 5c-ii-a/5c-i "lmp" GESTAT).
    out["gestational_age_weeks_source"] = pc.if_else(
        pc.is_null(gw), null_s, pa.scalar("combined"),
    )

    # Birth weight grams: cohort 2003 = DBWT, cohort 2004 = BRTHWGT
    # (both @467-470; field_specs 4b/4c).
    bw = opt_int("DBWT", pa.int32())
    if _get_col_optional(batch, "DBWT") is None:
        bw = opt_int("BRTHWGT", pa.int32())
    out["birthweight_grams"] = bw
    out["apgar5"] = opt_int("APGAR5", pa.int16())

    # Father age: UFAGECOMB (schema-documented "2003-2011: UFAGECOMB
    # @184-185; 99 -> null; clip 9-98").
    fage = opt_int("UFAGECOMB", pa.int16())
    fage = pc.if_else(
        pc.and_(
            pc.greater_equal(fage, pa.scalar(9, type=pa.int16())),
            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
        ),
        fage, pa.scalar(None, type=pa.int16()),
    )
    out["father_age"] = fage
    out["father_age_cat_from_rec11"] = _fagerec11_to_cat(
        opt_int("FAGEREC11", pa.int16())
    )

    out["birth_facility"] = _pldel_to_facility(opt_int("UBFACIL", pa.int8()))

    attend = opt_int("ATTEND", pa.int8())
    out["attendant_at_birth"] = pc.if_else(
        pc.equal(attend, pa.scalar(9, type=pa.int8())),
        pa.scalar(None, type=pa.int8()), attend,
    )

    forig = opt_int("UFHISP", pa.int8())
    f_is_hisp = pc.and_(
        pc.greater_equal(forig, pa.scalar(1, type=pa.int8())),
        pc.less_equal(forig, pa.scalar(5, type=pa.int8())),
    )
    f_is_nonhisp = pc.equal(forig, pa.scalar(0, type=pa.int8()))
    out["father_hispanic"] = pc.if_else(
        f_is_hisp, pa.scalar(True),
        pc.if_else(f_is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    # NO clean father-education value field on the cohort 2003/2004
    # den-plus (F_MEDUC@571 is an EDIT FLAG, not a value) ->
    # father_education_cat4 stays null (faithful "not on this file"; the
    # 5c-ii-a no-DFEDUC precedent). father_race_ethnicity_5 conservatively
    # null (soft-flag (gg); the receipt HALT 8 conservative-NULL set).

    # === Death-side: the 2003/2004 cohort den-plus "plus" — ALL ICD-10
    # (cohort birth-year >= 1999; the 5c-i resolved shape, §15.D DO
    # step 1). MANNER present (NEW vs 1995-2002). ===
    aged = opt_int("AGED", pa.int16())
    # A den-plus row is a linked infant death IFF the appended death
    # "plus" carries an age at death (blank for survivors, 000-366 days
    # for deaths) — the value-driven signal (no match-status-code
    # assumption; the SMOKE Tier-1 independently cross-checks it against
    # the era-correct AND era-independent match-status == "1" on real
    # LinkCO03/04 data, §7-#13; 2003 uses MATCHS, 2004 uses FLGND).
    infant_death = pc.invert(pc.is_null(aged))
    out["infant_death"] = pc.fill_null(infant_death, False)
    out["age_at_death_days"] = aged
    out["age_at_death_recode5"] = opt_int("AGER5", pa.int8())
    out["underlying_cause_icd10"] = opt_str("UCOD")    # ICD-10, populated
    out["cause_recode_130"] = opt_int("UCODR130", pa.int16())
    # underlying_cause_icd9 / cause_recode_61 stay null (default) — cohort
    # 2003/2004 birth-year >= 1999 = ICD-10 (the 5c-i resolved shape).
    out["manner_of_death"] = opt_int("MANNER", pa.int8())
    recwt = _get_col_optional(batch, "RECWT")
    out["record_weight"] = (
        _to_float_or_null(recwt, pa.float64())
        if recwt is not None else pa.nulls(n, type=pa.float64())
    )

    return pa.Table.from_arrays(
        [out[f.name] for f in OUT_SCHEMA], schema=OUT_SCHEMA,
    )


def _harmonize_cohort_batch(batch: pa.RecordBatch, year: int) -> pa.Table:
    """Harmonize one batch of a cohort-linked denominator(-plus) parquet
    (year <= 2004) into the (extended) OUT_SCHEMA.

    Per-cohort-era dispatch (the §15.D DO step 5c decomposition):
      * 1989-1991 (5c-i) — the inline reference-era body below.
      * 1995-2002 (5c-ii-a) — `_harmonize_cohort_1995_2002` (the 1989-rev
        sibling of 1989-1991; §15.D DO step 5c-ii decomposed ->
        5c-ii-a/5c-ii-b at the Convention-3 snapshot, PRE_FLIGHT_LOG
        2026-05-19T14:00:00Z; the 5c->5c-i/5c-ii/5c-iii precedent).
      * 2003 + 2004 (5c-ii-b) — `_harmonize_cohort_2003_2004` (the
        2003-revision dual-certificate transition; the natality V1-core
        `is_2003revised` analog; one function for both years, the
        2003-vs-2004 deltas pure raw-name aliasing; PRE_FLIGHT_LOG
        2026-05-19T20:00:00Z).
      * the keyless 1983-1988 link_segment den/num one-row-per-birth
        encoding (5c-iii) RAISES NotImplementedError (§2 fail-closed — a
        premature DO step 6 on those years halts loudly rather than
        silently mis-harmonizing).

    Birth-side = the cohort raw names ALIASED onto the natality V1-core
    revision recodes (H7 sibling-parity). Death-side = the within_era
    ICD-9 / ICD-10 representation keyed on cohort birth year
    (underlying_cause_icd9 / cause_recode_61 for <=1998;
    underlying_cause_icd10 / cause_recode_130 for >=1999 — §15.D DO
    step 1 default-null + revision-tagged). Composite multi-field blocks
    (MEDRISK / OBSTETRC / LABOR / DELMTH / CONGENIT) are conservatively
    NULL; per-condition leaf decomposition = soft-flag (gg) DO step 6
    (the natality is_pre1989 conservative-mapping precedent).
    """
    era = _cohort_era(year)
    if era == "1995_2002":
        return _harmonize_cohort_1995_2002(batch, year)
    if era in ("2003", "2004"):
        return _harmonize_cohort_2003_2004(batch, year)
    if era != "1989_1991":
        raise NotImplementedError(
            f"C8.18 DO step 5c-i/5c-ii-a/5c-ii-b implement the 1989-1991 "
            f"+ 1995-2002 + 2003 + 2004 cohort eras; year {year} (era "
            f"{era!r}) is the keyless 1983-1988 link_segment den/num "
            f"one-row-per-birth encoding, configured at DO step 5c-iii."
        )

    n = batch.num_rows
    null_s = pa.scalar(None, type=pa.string())

    def opt_str(name: str) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_str_or_null(c) if c is not None else pa.nulls(n, pa.string())

    def opt_int(name: str, t: pa.DataType) -> pa.Array:
        c = _get_col_optional(batch, name)
        return _to_int_or_null(c, t) if c is not None else pa.nulls(n, t)

    def _safe_cond(*parts):
        from functools import reduce
        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

    # Default EVERY OUT_SCHEMA column to a typed null; override the
    # fields the 1989-revision cohort denominator-plus actually carries.
    out: dict[str, pa.Array] = {
        f.name: pa.nulls(n, type=f.type) for f in OUT_SCHEMA
    }

    year_arr = pc.cast(_get_col(batch, "year"), pa.int16())
    out["data_year"] = year_arr
    out["certificate_revision"] = pc.if_else(
        pc.is_null(year_arr), null_s, pa.scalar("unrevised_1989"),
    )

    restatus = opt_int("RESSTATB", pa.int8())
    out["residence_status"] = restatus
    out["is_foreign_resident"] = pc.equal(restatus, pa.scalar(4, type=pa.int8()))

    out["maternal_age"] = opt_int("DMAGE", pa.int16())
    out["live_birth_order_recode"] = _detail_order_to_recode9(
        opt_int("DLIVORD", pa.int16())
    )
    out["total_birth_order_recode"] = _detail_order_to_recode9(
        opt_int("DTOTORD", pa.int16())
    )
    out["marital_status"] = opt_int("DMAR", pa.int8())

    hisp = opt_int("ORMOTH", pa.int8())
    out["hispanic_origin"] = hisp
    is_hisp = pc.and_(
        pc.greater_equal(hisp, pa.scalar(1, type=pa.int8())),
        pc.less_equal(hisp, pa.scalar(5, type=pa.int8())),
    )
    is_nonhisp = pc.equal(hisp, pa.scalar(0, type=pa.int8()))
    mat_hisp = pc.if_else(
        is_hisp, pa.scalar(True),
        pc.if_else(is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    out["maternal_hispanic"] = mat_hisp

    mrace_detail = opt_int("MRACE", pa.int16())
    race_bridged = _mrace_detail_to_bridged4(mrace_detail)
    out["maternal_race_bridged"] = race_bridged
    out["maternal_race_detail"] = opt_str("MRACE")
    race_eth = pc.if_else(
        pc.fill_null(pc.equal(mat_hisp, pa.scalar(True)), False),
        pa.scalar("Hispanic"), null_s,
    )
    is_nh = pc.fill_null(pc.equal(mat_hisp, pa.scalar(False)), False)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)),
                          pa.scalar("NH_white"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)),
                          pa.scalar("NH_black"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)),
                          pa.scalar("NH_aian"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)),
                          pa.scalar("NH_asian_pi"), race_eth)
    out["maternal_race_ethnicity_5"] = race_eth
    out["race_bridge_method"] = pc.if_else(
        pc.is_null(year_arr), null_s, pa.scalar("approximate_pre2003"),
    )

    out["maternal_education_cat4"] = _dmeduc_years_to_cat4(
        opt_int("DMEDUC", pa.int16())
    )

    pn_month = opt_int("MONPRE", pa.int16())
    out["prenatal_care_start_month"] = pn_month
    out["prenatal_care_start_trimester"] = _month_to_trimester(pn_month)
    out["prenatal_visits"] = opt_int("NPREVIS", pa.int16())

    out["plurality_recode"] = opt_int("DPLURAL", pa.int8())

    csex = opt_int("CSEX", pa.int8())
    out["infant_sex"] = pc.if_else(
        pc.equal(csex, pa.scalar(1, type=pa.int8())), pa.scalar("M"),
        pc.if_else(pc.equal(csex, pa.scalar(2, type=pa.int8())),
                   pa.scalar("F"), null_s),
    )

    gw = opt_int("GESTAT", pa.int16())
    _keep = pc.or_(
        pc.fill_null(pc.and_(
            pc.greater_equal(gw, pa.scalar(17, type=pa.int16())),
            pc.less_equal(gw, pa.scalar(47, type=pa.int16())),
        ), False),
        pc.fill_null(pc.equal(gw, pa.scalar(99, type=pa.int16())), False),
    )
    gw = pc.if_else(_keep, gw, pa.scalar(None, type=pa.int16()))
    out["gestational_age_weeks"] = gw
    out["gestational_age_weeks_source"] = pc.if_else(
        pc.is_null(gw), null_s, pa.scalar("lmp"),
    )

    out["birthweight_grams"] = opt_int("DBIRWT", pa.int32())
    out["apgar5"] = opt_int("FMAPS", pa.int16())

    fage = opt_int("DFAGE", pa.int16())
    fage = pc.if_else(
        pc.and_(
            pc.greater_equal(fage, pa.scalar(9, type=pa.int16())),
            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
        ),
        fage, pa.scalar(None, type=pa.int16()),
    )
    out["father_age"] = fage

    out["birth_facility"] = _pldel_to_facility(opt_int("PLDEL", pa.int8()))

    attend = opt_int("BIRATTND", pa.int8())
    out["attendant_at_birth"] = pc.if_else(
        pc.equal(attend, pa.scalar(9, type=pa.int8())),
        pa.scalar(None, type=pa.int8()), attend,
    )

    forig = opt_int("ORFATH", pa.int8())
    f_is_hisp = pc.and_(
        pc.greater_equal(forig, pa.scalar(1, type=pa.int8())),
        pc.less_equal(forig, pa.scalar(5, type=pa.int8())),
    )
    f_is_nonhisp = pc.equal(forig, pa.scalar(0, type=pa.int8()))
    out["father_hispanic"] = pc.if_else(
        f_is_hisp, pa.scalar(True),
        pc.if_else(f_is_nonhisp, pa.scalar(False),
                   pa.scalar(None, type=pa.bool_())),
    )
    out["father_education_cat4"] = _dmeduc_years_to_cat4(
        opt_int("DFEDUC", pa.int16())
    )

    # === Death-side: the 1989-1991 cohort denominator-plus "plus"
    # (AGED..UCODR61 @213-225) — ICD-9 within_era (§15.D DO step 1) ===
    aged = opt_int("AGED", pa.int16())
    # A 1989-1991 denominator-plus row is a linked infant death IFF the
    # appended death "plus" carries an age at death (blank for survivors,
    # 000-364 days for deaths) — the value-driven signal (no MATCHS-code
    # assumption). The SMOKE Tier-1 independently cross-checks this
    # against MATCHS in {1,2} on real LinkCO90 data (a disagreement is a
    # §7-#13 halt surfaced at the cheap moment, not at DO step 6).
    infant_death = pc.invert(pc.is_null(aged))
    out["infant_death"] = pc.fill_null(infant_death, False)
    out["age_at_death_days"] = aged
    out["age_at_death_recode5"] = opt_int("AGER5", pa.int8())
    # ICD-9 within_era (cohort 1989-1991 deaths occur 1989-1992, all
    # NCHS-coded ICD-9 — US mortality ICD-9 through 1998). The ICD-10
    # columns are NULL here (§15.D DO step 1 default-null + revision-
    # tagged); H7 fetal-death sibling-parity (cause_icd10 within_era).
    out["underlying_cause_icd9"] = opt_str("UCOD")
    out["cause_recode_61"] = opt_int("UCODR61", pa.int16())
    out["underlying_cause_icd10"] = pa.nulls(n, type=pa.string())
    out["cause_recode_130"] = pa.nulls(n, type=pa.int16())
    # manner_of_death + record_weight are NOT on the 225-byte 1989-1991
    # cohort denominator-plus (no MANNER / RECWT field) -> null (faithful
    # "not on this file", not a parser bug).

    return pa.Table.from_arrays(
        [out[f.name] for f in OUT_SCHEMA], schema=OUT_SCHEMA,
    )


def _harmonize_batch(batch: pa.RecordBatch, year: int) -> pa.Table:
    """Harmonize one batch of linked records (birth + death sides)."""
    # C8.18 DO step 5c-i: a cohort year (<= 2004) routes to the
    # per-cohort-era path; year >= 2005 -> _cohort_era is None and the
    # existing 2005+ body below is byte-untouched (the canonical v3
    # 2005-2023 product is byte-identical; §9-#7-safe).
    if _cohort_era(year) is not None:
        return _harmonize_cohort_batch(batch, year)
    cols = set(batch.schema.names)
    is_post2013 = "OEGEST_COMB" in cols
    null_s = pa.scalar(None, type=pa.string())
    revised_s = pa.scalar("revised_2003", type=pa.string())
    unrevised_s = pa.scalar("unrevised_1989", type=pa.string())
    unknown_s = pa.scalar("unknown", type=pa.string())

    # === Year ===
    year_arr = pc.cast(_get_col(batch, "year"), pa.int16())

    # === RESTATUS ===
    restatus = _to_int_or_null(_get_col(batch, "RESTATUS"), pa.int8())
    is_foreign = pc.equal(restatus, pa.scalar(4, type=pa.int8()))

    # Year-varying column names
    marital_col = "DMAR" if "DMAR" in cols else "MAR"
    visits_col = "PREVIS" if "PREVIS" in cols else "UPREVIS"
    hisp_col = "MHISP_R" if "MHISP_R" in cols else "UMHISP"
    race_bridged_col = "MBRACE" if "MBRACE" in cols else "MRACEREC"
    race_detail_col = "MRACE6" if "MRACE6" in cols else "MRACE"

    # === Maternal age ===
    mager = _to_int_or_null(_get_col(batch, "MAGER"), pa.int16())

    # === Marital status ===
    marital = _to_int_or_null(_get_col(batch, marital_col), pa.int8())

    # === Marital reporting flag (F_MAR_P: 0=non-reporting, 1=reporting; 2014+ only) ===
    f_mar_p_raw = _get_col_optional(batch, "F_MAR_P")
    if f_mar_p_raw is not None:
        f_mar_p = _to_int_or_null(f_mar_p_raw, pa.int8())
        marital_rpt_flag = pc.if_else(
            pc.equal(f_mar_p, pa.scalar(1, type=pa.int8())),
            pa.scalar(True),
            pc.if_else(
                pc.equal(f_mar_p, pa.scalar(0, type=pa.int8())),
                pa.scalar(False),
                pa.scalar(None, type=pa.bool_()),
            ),
        )
    else:
        marital_rpt_flag = pa.nulls(batch.num_rows, type=pa.bool_())

    # === Birth order ===
    lbo = _to_int_or_null(_get_col(batch, "LBO_REC"), pa.int8())
    tbo = _to_int_or_null(_get_col(batch, "TBO_REC"), pa.int8())

    # === Hispanic origin ===
    hisp_origin = _to_int_or_null(_get_col(batch, hisp_col), pa.int8())
    is_hisp = pc.and_(
        pc.greater_equal(hisp_origin, pa.scalar(1, type=pa.int8())),
        pc.less_equal(hisp_origin, pa.scalar(5, type=pa.int8())),
    )
    is_nonhisp = pc.equal(hisp_origin, pa.scalar(0, type=pa.int8()))
    maternal_hisp = pc.if_else(
        is_hisp, pa.scalar(True),
        pc.if_else(is_nonhisp, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
    )

    # === Race ===
    race_bridged = _to_int_or_null(_get_col(batch, race_bridged_col), pa.int8())
    race_detail = _to_str_or_null(_get_col(batch, race_detail_col))
    # 2014+ MRACE6 is a 1-digit field ('1'..'6'); 2005-2013 MRACE is 2-digit
    # zero-padded ('01'..'78'). Zero-pad 2014+ values so maternal_race_detail
    # has a uniform 2-digit format across the full linked span (matches
    # natality V2 behavior).
    if race_detail_col == "MRACE6":
        race_detail = pc.utf8_lpad(race_detail, 2, "0")

    # MRACE15 — 15-category detail race recode.  Populated 2014+ in linked files
    # (the 2014-2020 denom-plus layout inherits from PUBLIC_US_2014_2015_FIELDS).
    # Null for 2005-2013 linked (NCHS does not expose MRACE15 in the denom-plus
    # 2005-2013 format).
    mrace15_raw = _get_col_optional(batch, "MRACE15")
    if mrace15_raw is not None:
        race_detail_15 = _to_str_or_null(mrace15_raw)
        # Null the NCHS "99" unknown sentinel (match natality V2 behavior).
        race_detail_15 = pc.if_else(
            pc.fill_null(pc.equal(race_detail_15, pa.scalar("99")), False),
            pa.scalar(None, type=pa.string()),
            race_detail_15,
        )
    else:
        race_detail_15 = pa.nulls(batch.num_rows, type=pa.string())

    # Use fill_null(False) on each component of compound conditions because pyarrow's
    # pc.and_ is NOT Kleene-aware. See harmonize_v1_core.py for details.
    def _safe_cond(*parts):
        from functools import reduce
        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

    race_eth = pc.if_else(
        pc.fill_null(pc.equal(maternal_hisp, pa.scalar(True)), False),
        pa.scalar("Hispanic"), null_s,
    )
    is_nh = pc.fill_null(pc.equal(maternal_hisp, pa.scalar(False)), False)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)), pa.scalar("NH_white"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)), pa.scalar("NH_black"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)), pa.scalar("NH_aian"), race_eth)
    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)), pa.scalar("NH_asian_pi"), race_eth)

    # 2020+ race reconstruction: for non-Hispanic births where race_bridged is null,
    # reconstruct maternal_race_ethnicity_5 from MRACE6 detail codes (1-byte field).
    if is_post2013:
        needs_fill = _safe_cond(is_nh, pc.is_null(race_bridged))
        rd_int = _to_int_or_null(_get_col(batch, race_detail_col), pa.int16())
        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 1)), pa.scalar("NH_white"), race_eth)
        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 2)), pa.scalar("NH_black"), race_eth)
        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 3)), pa.scalar("NH_aian"), race_eth)
        race_eth = pc.if_else(
            _safe_cond(needs_fill, pc.or_(pc.equal(rd_int, 4), pc.equal(rd_int, 5))),
            pa.scalar("NH_asian_pi"), race_eth,
        )
        # code 6 (multiracial, ~3%) stays null — cannot be bridged to single group

    # Race bridge method: nchs_bridged for years < 2020, approximate_from_detail for 2020+
    race_bridge = pc.if_else(
        pc.less(year_arr, pa.scalar(2020, type=pa.int16())),
        pa.scalar("nchs_bridged"),
        pa.scalar("approximate_from_detail"),
    )

    # === Education ===
    meduc = _to_int_or_null(_get_col(batch, "MEDUC"), pa.int8())
    meduc_rec_raw = _get_col_optional(batch, "MEDUC_REC")
    meduc_rec = (
        _to_int_or_null(meduc_rec_raw, pa.int8())
        if meduc_rec_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int8())
    )
    meduc_cat = _meduc_to_cat4(meduc)
    meduc_rec_cat = _meduc_rec_to_cat4(meduc_rec)
    educ_cat4 = pc.if_else(pc.is_null(meduc_cat), meduc_rec_cat, meduc_cat)

    # === Certificate revision ===
    if year >= 2014:
        cert_rev = pc.if_else(pc.is_null(year_arr), null_s, revised_s)
    else:
        has_meduc = pc.invert(pc.is_null(meduc))
        has_mrace = pc.invert(pc.is_null(race_detail))
        cert_rev = pc.if_else(has_meduc, revised_s, null_s)
        cert_rev = pc.if_else(
            pc.and_(pc.is_null(cert_rev), has_mrace), unrevised_s, cert_rev,
        )
        cert_rev = pc.if_else(pc.is_null(cert_rev), unknown_s, cert_rev)

    # === Prenatal care ===
    precare = _to_int_or_null(_get_col(batch, "PRECARE"), pa.int16())
    mpcb_raw = _get_col_optional(batch, "MPCB")
    mpcb = (
        _to_int_or_null(mpcb_raw, pa.int16())
        if mpcb_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int16())
    )
    pn_start_month = pc.if_else(pc.is_null(precare), mpcb, precare)
    pn_start_trim = _month_to_trimester(pn_start_month)
    previs = _to_int_or_null(_get_col(batch, visits_col), pa.int16())

    # === Medical risk factors ===
    # AUDIT D10: mirror the natality V2 per-year URF_* → RF_* fallback. The
    # linked 2016-2023 files use the same public-use natality byte layout and
    # should therefore apply the RF_PDIAB/RF_GDIAB/RF_PHYPE/RF_GHYPE fallback
    # for year >= 2016 to stay consistent with V2 diabetes_any / hypertension_*.
    use_rf_fallback = year >= 2016

    if use_rf_fallback:
        rf_pd = _get_col_optional(batch, "RF_PDIAB")
        rf_gd = _get_col_optional(batch, "RF_GDIAB")
        if rf_pd is not None and rf_gd is not None:
            pd_yes = _yn_to_bool(rf_pd)
            gd_yes = _yn_to_bool(rf_gd)
            either = pc.or_(pc.fill_null(pd_yes, False), pc.fill_null(gd_yes, False))
            both_known = pc.and_(pc.is_valid(pd_yes), pc.is_valid(gd_yes))
            diab = pc.if_else(either, pa.scalar(1, type=pa.int8()),
                    pc.if_else(both_known, pa.scalar(2, type=pa.int8()),
                               pa.scalar(None, type=pa.int8())))
        else:
            diab = pa.nulls(batch.num_rows, type=pa.int8())
        rf_ch = _get_col_optional(batch, "RF_PHYPE")
        if rf_ch is not None:
            ch_yes = _yn_to_bool(rf_ch)
            chyp = pc.if_else(pc.fill_null(ch_yes, False), pa.scalar(1, type=pa.int8()),
                    pc.if_else(pc.is_valid(ch_yes), pa.scalar(2, type=pa.int8()),
                               pa.scalar(None, type=pa.int8())))
        else:
            chyp = pa.nulls(batch.num_rows, type=pa.int8())
        rf_gh = _get_col_optional(batch, "RF_GHYPE")
        if rf_gh is not None:
            gh_yes = _yn_to_bool(rf_gh)
            phyp = pc.if_else(pc.fill_null(gh_yes, False), pa.scalar(1, type=pa.int8()),
                    pc.if_else(pc.is_valid(gh_yes), pa.scalar(2, type=pa.int8()),
                               pa.scalar(None, type=pa.int8())))
        else:
            phyp = pa.nulls(batch.num_rows, type=pa.int8())
    else:
        diab = _to_int_or_null(_get_col(batch, "URF_DIAB"), pa.int8())
        chyp = _to_int_or_null(_get_col(batch, "URF_CHYPER"), pa.int8())
        phyp = _to_int_or_null(_get_col(batch, "URF_PHYPER"), pa.int8())

    # === Smoking ===
    cig0_r_raw = _get_col_optional(batch, "CIG0_R")
    cig0_r = (
        _to_int_or_null(cig0_r_raw, pa.int8())
        if cig0_r_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int8())
    )

    cig1_r_raw = _get_col_optional(batch, "CIG1_R")
    cig2_r_raw = _get_col_optional(batch, "CIG2_R")
    cig3_r_raw = _get_col_optional(batch, "CIG3_R")

    if cig1_r_raw is not None and cig2_r_raw is not None and cig3_r_raw is not None:
        cig1_r = _to_int_or_null(cig1_r_raw, pa.int8())
        cig2_r = _to_int_or_null(cig2_r_raw, pa.int8())
        cig3_r = _to_int_or_null(cig3_r_raw, pa.int8())
        smoke_intensity = _max_recode6_ignoring_unknown(cig1_r, cig2_r, cig3_r)
    else:
        cig_rec6_raw = _get_col_optional(batch, "CIG_REC6")
        cig_rec6 = (
            _to_int_or_null(cig_rec6_raw, pa.int8())
            if cig_rec6_raw is not None
            else pa.nulls(batch.num_rows, type=pa.int8())
        )
        c1 = _to_int_or_null(_get_col(batch, "CIG_1"), pa.int16())
        c2 = _to_int_or_null(_get_col(batch, "CIG_2"), pa.int16())
        c3 = _to_int_or_null(_get_col(batch, "CIG_3"), pa.int16())
        r1 = _cigs_count_to_recode6(c1)
        r2 = _cigs_count_to_recode6(c2)
        r3 = _cigs_count_to_recode6(c3)
        trimester_max = _max_recode6_ignoring_unknown(r1, r2, r3)
        smoke_intensity = _max_recode6_ignoring_unknown(
            cig_rec6, trimester_max, pa.nulls(batch.num_rows, type=pa.int8()),
        )

    is_smoker = pc.and_(pc.greater_equal(smoke_intensity, 1), pc.less_equal(smoke_intensity, 5))
    is_nonsmoker = pc.equal(smoke_intensity, 0)
    smoke_any = pc.if_else(
        is_smoker, pa.scalar(True),
        pc.if_else(is_nonsmoker, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
    )

    # === Plurality, sex, gestation, birthweight, delivery, apgar ===
    plur = _to_int_or_null(_get_col(batch, "DPLURAL"), pa.int8())
    sex = _to_str_or_null(_get_col(batch, "SEX"))

    combgest = _to_int_or_null(_get_col(batch, "COMBGEST"), pa.int16())
    oegest_raw = _get_col_optional(batch, "OEGEST_COMB")
    oegest = (
        _to_int_or_null(oegest_raw, pa.int16())
        if oegest_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int16())
    )
    gest_weeks = pc.if_else(pc.is_null(oegest), combgest, oegest)
    gest_src = pc.if_else(
        pc.is_null(gest_weeks), null_s,
        pc.if_else(pc.is_null(oegest), pa.scalar("combined"), pa.scalar("obstetric_estimate")),
    )

    gestrec3 = _to_int_or_null(_get_col(batch, "GESTREC3"), pa.int8())
    oegest_r3_raw = _get_col_optional(batch, "OEGEST_R3")
    oegest_r3 = (
        _to_int_or_null(oegest_r3_raw, pa.int8())
        if oegest_r3_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int8())
    )
    preterm_r3 = pc.if_else(pc.is_null(oegest_r3), gestrec3, oegest_r3)

    dbwt = _to_int_or_null(_get_col(batch, "DBWT"), pa.int32())
    dmeth = _to_int_or_null(_get_col(batch, "DMETH_REC"), pa.int8())

    apgar5_raw = _get_col_optional(batch, "APGAR5")
    apgar5 = (
        _to_int_or_null(apgar5_raw, pa.int16())
        if apgar5_raw is not None
        else pa.nulls(batch.num_rows, type=pa.int16())
    )

    # === BMI (pre-pregnancy): available 2014+ ===
    bmi_raw = _get_col_optional(batch, "BMI")
    bmi_r_raw = _get_col_optional(batch, "BMI_R")
    if bmi_raw is not None:
        bmi_str = bmi_raw.cast(pa.string())
        stripped = pc.utf8_trim_whitespace(bmi_str)
        is_blank = pc.equal(stripped, pa.scalar(""))
        castable = pc.if_else(is_blank, pa.scalar("NaN"), stripped)
        bmi_float = pc.cast(castable, pa.float32(), safe=False)
        bmi_pp = pc.if_else(
            pc.or_(pc.is_nan(bmi_float),
                   pc.greater_equal(bmi_float, pa.scalar(99.0, type=pa.float32()))),
            pa.scalar(None, type=pa.float32()),
            bmi_float,
        )
        bmi_pp_r6 = _to_int_or_null(bmi_r_raw, pa.int8())
        bmi_pp_r6 = pc.if_else(
            pc.equal(bmi_pp_r6, pa.scalar(9, type=pa.int8())),
            pa.scalar(None, type=pa.int8()),
            bmi_pp_r6,
        )
    else:
        bmi_pp = pa.nulls(batch.num_rows, type=pa.float32())
        bmi_pp_r6 = pa.nulls(batch.num_rows, type=pa.int8())

    # === Father's age ===
    # AUDIT D2 parity with V2: prefer FAGECOMB (revised-cert) when present,
    # fall back to UFAGECOMB (unrevised).  For 2005-2011 linked this resolves
    # UFAGECOMB; for 2012-2013 linked it picks up FAGECOMB@182-183 (the field
    # NCHS moved for 2013 natality also lives here in the linked denom-plus
    # layout); for 2014+ it reads FAGECOMB@147-148.
    fagecomb_raw = _get_col_optional(batch, "FAGECOMB")
    ufagecomb_raw = _get_col_optional(batch, "UFAGECOMB")
    if fagecomb_raw is not None:
        fagecomb = _to_int_or_null(fagecomb_raw, pa.int16())
    else:
        fagecomb = pa.nulls(batch.num_rows, type=pa.int16())
    if ufagecomb_raw is not None:
        ufagecomb = _to_int_or_null(ufagecomb_raw, pa.int16())
    else:
        ufagecomb = pa.nulls(batch.num_rows, type=pa.int16())
    fage = pc.if_else(pc.is_null(fagecomb), ufagecomb, fagecomb)
    # Null out-of-range: valid 9-98; 99=unknown, <9 or >98 are invalid
    fage = pc.if_else(
        pc.and_(
            pc.greater_equal(fage, pa.scalar(9, type=pa.int16())),
            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
        ),
        fage,
        pa.scalar(None, type=pa.int16()),
    )

    # Categorical father-age fallback from FAGEREC11 (2005-2013 linked only).
    # Recovers categorical age for 2012 linked births where raw age is blank.
    fagerec11_raw = _get_col_optional(batch, "FAGEREC11")
    if fagerec11_raw is not None:
        fagerec11 = _to_int_or_null(fagerec11_raw, pa.int8())
        fage_cat_rec11 = _fagerec11_to_cat(fagerec11)
    else:
        fage_cat_rec11 = pa.nulls(batch.num_rows, type=pa.string())

    # UBFACIL uses unrevised coding (same as PLDEL: 3=clinic, 4=residence, 5=other)
    # BFACIL uses revised coding (3-5=home, 6=clinic, 7=other)
    if "BFACIL" in cols:
        bfacil_raw = _to_int_or_null(_get_col(batch, "BFACIL"), pa.int8())
        birth_fac = _bfacil_to_facility(bfacil_raw)
    else:
        ubfacil_raw = _to_int_or_null(_get_col(batch, "UBFACIL"), pa.int8())
        birth_fac = _pldel_to_facility(ubfacil_raw)

    attend = _to_int_or_null(_get_col(batch, "ATTEND"), pa.int8())
    attend = pc.if_else(
        pc.equal(attend, pa.scalar(9, type=pa.int8())),
        pa.scalar(None, type=pa.int8()),
        attend,
    )

    pay_rec_raw = _get_col_optional(batch, "PAY_REC")
    if pay_rec_raw is not None:
        pay_rec = _to_int_or_null(pay_rec_raw, pa.int8())
        pay_rec = pc.if_else(
            pc.equal(pay_rec, pa.scalar(9, type=pa.int8())),
            pa.scalar(None, type=pa.int8()),
            pay_rec,
        )
    else:
        pay_rec = pa.nulls(batch.num_rows, type=pa.int8())

    rf_cesar_raw = _get_col_optional(batch, "RF_CESAR")
    if rf_cesar_raw is not None:
        rf_str = _to_str_or_null(rf_cesar_raw)
        prior_ces = pc.if_else(
            pc.equal(rf_str, pa.scalar("Y")),
            pa.scalar(True),
            pc.if_else(
                pc.equal(rf_str, pa.scalar("N")),
                pa.scalar(False),
                pa.scalar(None, type=pa.bool_()),
            ),
        )
    else:
        prior_ces = pa.nulls(batch.num_rows, type=pa.bool_())

    # === Father Hispanic, race/ethnicity, education ===
    fath_hisp_col = "FHISP_R" if "FHISP_R" in cols else "UFHISP"
    fath_hisp_origin = _to_int_or_null(_get_col(batch, fath_hisp_col), pa.int8())
    fath_is_hisp = pc.and_(
        pc.greater_equal(fath_hisp_origin, pa.scalar(1, type=pa.int8())),
        pc.less_equal(fath_hisp_origin, pa.scalar(5, type=pa.int8())),
    )
    fath_is_nonhisp = pc.equal(fath_hisp_origin, pa.scalar(0, type=pa.int8()))
    father_hisp = pc.if_else(
        fath_is_hisp, pa.scalar(True),
        pc.if_else(fath_is_nonhisp, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
    )

    fracehisp = _to_int_or_null(_get_col(batch, "FRACEHISP"), pa.int8())
    father_race_eth = _racehisp_combined_to_5cat(fracehisp, is_2014_plus=(year >= 2014))

    feduc_raw = _get_col_optional(batch, "FEDUC")
    if feduc_raw is not None:
        feduc = _to_int_or_null(feduc_raw, pa.int8())
        father_educ_cat4 = _meduc_to_cat4(feduc)
    else:
        father_educ_cat4 = pa.nulls(batch.num_rows, type=pa.string())

    # === Congenital anomalies, infections, fertility (2014+ only) ===
    _CA_FIELDS = [
        ("CA_ANEN", ("Y",)), ("CA_MNSB", ("Y",)), ("CA_CCHD", ("Y",)),
        ("CA_CDH", ("Y",)), ("CA_OMPH", ("Y",)), ("CA_GAST", ("Y",)),
        ("CA_LIMB", ("Y",)), ("CA_CLEFT", ("Y",)), ("CA_CLPAL", ("Y",)),
        ("CA_DOWN", ("Y", "C", "P")), ("CA_DISOR", ("Y", "C", "P")),
        ("CA_HYPO", ("Y",)),
    ]
    ca_list = []
    for fname, tv in _CA_FIELDS:
        raw = _get_col_optional(batch, fname)
        ca_list.append(_yn_to_bool(raw, true_values=tv) if raw is not None
                       else pa.nulls(batch.num_rows, type=pa.bool_()))

    _IP_FIELDS = ["IP_GON", "IP_SYPH", "IP_CHLAM", "IP_HEPB", "IP_HEPC"]
    ip_list = []
    for fname in _IP_FIELDS:
        raw = _get_col_optional(batch, fname)
        ip_list.append(_yn_to_bool(raw) if raw is not None
                       else pa.nulls(batch.num_rows, type=pa.bool_()))

    rf_cesarn_raw = _get_col_optional(batch, "RF_CESARN")
    if rf_cesarn_raw is not None:
        prior_ces_count = _to_int_or_null(rf_cesarn_raw, pa.int8())
        prior_ces_count = pc.if_else(
            pc.equal(prior_ces_count, pa.scalar(99, type=pa.int8())),
            pa.scalar(None, type=pa.int8()),
            prior_ces_count,
        )
    else:
        prior_ces_count = pa.nulls(batch.num_rows, type=pa.int8())

    rf_fedrg_raw = _get_col_optional(batch, "RF_FEDRG")
    fert_drugs = (_yn_to_bool(rf_fedrg_raw) if rf_fedrg_raw is not None
                  else pa.nulls(batch.num_rows, type=pa.bool_()))
    rf_artec_raw = _get_col_optional(batch, "RF_ARTEC")
    art_concep = (_yn_to_bool(rf_artec_raw) if rf_artec_raw is not None
                  else pa.nulls(batch.num_rows, type=pa.bool_()))

    # Pre-pregnancy diabetes (RF_PDIAB: Y/N/U; 2014+ only)
    rf_pdiab_raw = _get_col_optional(batch, "RF_PDIAB")
    pre_preg_diab = (_yn_to_bool(rf_pdiab_raw) if rf_pdiab_raw is not None
                     else pa.nulls(batch.num_rows, type=pa.bool_()))

    # Gestational diabetes (RF_GDIAB: Y/N/U; 2014+ only)
    rf_gdiab_raw = _get_col_optional(batch, "RF_GDIAB")
    gest_diab = (_yn_to_bool(rf_gdiab_raw) if rf_gdiab_raw is not None
                 else pa.nulls(batch.num_rows, type=pa.bool_()))

    # NICU admission (AB_NICU: Y/N/U; 2014+ only)
    ab_nicu_raw = _get_col_optional(batch, "AB_NICU")
    nicu = (_yn_to_bool(ab_nicu_raw) if ab_nicu_raw is not None
            else pa.nulls(batch.num_rows, type=pa.bool_()))

    # Weight gain in pounds (WTGAIN: 00-97, 99=unknown; 2014+ only)
    wtgain_raw = _get_col_optional(batch, "WTGAIN")
    if wtgain_raw is not None:
        wtgain = _to_int_or_null(wtgain_raw, pa.int16())
        wtgain = pc.if_else(
            pc.equal(wtgain, pa.scalar(99, type=pa.int16())),
            pa.scalar(None, type=pa.int16()),
            wtgain,
        )
    else:
        wtgain = pa.nulls(batch.num_rows, type=pa.int16())

    # Induction of labor (LD_INDL: Y/N/U; 2014+ only)
    ld_indl_raw = _get_col_optional(batch, "LD_INDL")
    indl = (_yn_to_bool(ld_indl_raw) if ld_indl_raw is not None
            else pa.nulls(batch.num_rows, type=pa.bool_()))

    # Breastfed at discharge (BFED: Y/N/U; 2014+ only)
    bfed_raw = _get_col_optional(batch, "BFED")
    bfed = (_yn_to_bool(bfed_raw) if bfed_raw is not None
            else pa.nulls(batch.num_rows, type=pa.bool_()))

    # ====================================================================
    # DEATH-SIDE harmonization
    # ====================================================================

    # Infant death flag: normalize FLGND
    # 2005-2013: FLGND=1 (death), FLGND=2 (survivor)
    # 2014-2015: FLGND=1 (death), FLGND=blank (survivor)
    flgnd = _to_str_or_null(_get_col(batch, "FLGND"))
    infant_death = pc.equal(flgnd, pa.scalar("1"))
    # If FLGND is null (blank in 2014+), that means survivor → False
    infant_death = pc.fill_null(infant_death, False)

    # Age at death in days (AGED): 3-char field, blank for survivors
    aged_raw = _to_int_or_null(_get_col(batch, "AGED"), pa.int16())
    # Null for survivors (was blank → null via _to_int_or_null)
    age_at_death_days = aged_raw

    # Age at death 5-category recode (AGER5)
    # 1=under 1 hour, 2=1-23 hours, 3=1-6 days, 4=7-27 days, 5=28 days-1 year
    ager5_raw = _to_int_or_null(_get_col(batch, "AGER5"), pa.int8())
    age_at_death_recode5 = ager5_raw

    # Underlying cause of death (ICD-10 code)
    ucod = _to_str_or_null(_get_col(batch, "UCOD"))
    underlying_cause_icd10 = ucod

    # 130-cause recode
    ucodr130_raw = _to_int_or_null(_get_col(batch, "UCODR130"), pa.int16())
    cause_recode_130 = ucodr130_raw

    # Manner of death
    # 1=accident, 2=suicide, 3=homicide, 4=pending investigation,
    # 5=could not determine, 6=self-inflicted, 7=natural, blank=not applicable
    manner = _to_int_or_null(_get_col(batch, "MANNER"), pa.int8())
    manner_of_death = manner

    # Record weight (RECWT): float field
    recwt = _to_float_or_null(_get_col(batch, "RECWT"), pa.float64())
    record_weight = recwt

    # === Build output table ===
    return pa.Table.from_arrays(
        [
            # Birth-side
            year_arr, restatus, is_foreign, cert_rev, mager, lbo, tbo,
            marital, marital_rpt_flag, hisp_origin, maternal_hisp, race_bridged, race_eth,
            race_detail, race_detail_15, race_bridge, educ_cat4, pn_start_month, pn_start_trim, previs,
            smoke_any, smoke_intensity, cig0_r, diab, chyp, phyp,
            plur, sex, gest_weeks, gest_src, preterm_r3, dbwt, dmeth, apgar5,
            bmi_pp, bmi_pp_r6,
            fage, fage_cat_rec11, birth_fac, attend, pay_rec, prior_ces,
            father_hisp, father_race_eth, father_educ_cat4,
            *ca_list, *ip_list,
            prior_ces_count, fert_drugs, art_concep,
            pre_preg_diab, gest_diab, nicu, wtgain, indl, bfed,
            # Death-side
            infant_death, age_at_death_days, age_at_death_recode5,
            underlying_cause_icd10, cause_recode_130,
            # C8.18 DO step 5c-i: the within_era ICD-9 cause columns are
            # NULL for the 2005-2023 ICD-10 slice (this is the canonical
            # path; the cohort branch never fires for year >= 2005). This
            # is the intended v3->v4 ADDITIVE schema extension — existing
            # 2005-2023 column VALUES are byte-identical (§9-#7-safe;
            # zero canonical mutation at 5c-i, the parquet is not re-run).
            pa.nulls(batch.num_rows, type=pa.string()),   # underlying_cause_icd9
            pa.nulls(batch.num_rows, type=pa.int16()),    # cause_recode_61
            manner_of_death,
            record_weight,
        ],
        schema=OUT_SCHEMA,
    )


def main() -> None:
    args = parse_args()
    years = _parse_years(args.years)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    writer: pq.ParquetWriter | None = None
    total = 0
    try:
        for year in years:
            in_path = args.linked_dir / f"linked_{year}_denomplus.parquet"
            if not in_path.is_file():
                raise FileNotFoundError(in_path)

            pf = pq.ParquetFile(in_path)
            yr_rows = 0
            for batch in pf.iter_batches(batch_size=args.batch_rows):
                out_tbl = _harmonize_batch(batch, year)
                if writer is None:
                    writer = pq.ParquetWriter(str(args.out), OUT_SCHEMA)
                writer.write_table(out_tbl)
                yr_rows += batch.num_rows
            total += yr_rows
            print(f"  {year}: {yr_rows:,} rows")
    finally:
        if writer is not None:
            writer.close()

    print(f"\nWrote {total:,} rows to {args.out}")


if __name__ == "__main__":
    main()
