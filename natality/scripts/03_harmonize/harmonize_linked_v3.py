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
    ("year", pa.int16()),
    ("restatus", pa.int8()),
    ("is_foreign_resident", pa.bool_()),
    ("certificate_revision", pa.string()),
    ("maternal_age", pa.int16()),
    ("live_birth_order_recode", pa.int8()),
    ("total_birth_order_recode", pa.int8()),
    ("marital_status", pa.int8()),
    ("marital_reporting_flag", pa.bool_()),
    ("maternal_hispanic_origin", pa.int8()),
    ("maternal_hispanic", pa.bool_()),
    ("maternal_race_bridged4", pa.int8()),
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


def _harmonize_batch(batch: pa.RecordBatch, year: int) -> pa.Table:
    """Harmonize one batch of linked records (birth + death sides)."""
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
            underlying_cause_icd10, cause_recode_130, manner_of_death,
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
