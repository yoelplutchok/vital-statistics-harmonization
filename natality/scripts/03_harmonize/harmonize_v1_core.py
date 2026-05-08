#!/usr/bin/env python3
"""
Harmonize yearly extracts (1990–2020) into a single stacked Parquet file.

Handles three distinct layout eras:
- 1990–2002: unrevised 1989 certificate only (different field names, years-based education,
              Y/N medical flags, LMP-only gestation, numeric sex)
- 2003–2013: dual certificate transition (parallel unrevised/revised fields)
- 2014–2020: revised 2003 certificate only (obstetric estimate gestation, CIG_R recodes)

Output is written in a memory-bounded streaming fashion.
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
        "--yearly-parquet-dir",
        type=Path,
        default=repo_root / "output" / "yearly_clean",
        help="Directory containing natality_{year}_core.parquet",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v2_harmonized.parquet",
        help="Output Parquet path",
    )
    p.add_argument(
        "--years",
        type=str,
        default="1990-2024",
        help="Comma years or range like 1990-2024 (default = full V2 coverage)",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=500_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def _trim(arr: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    return pc.utf8_trim_whitespace(arr)


def _to_int_or_null(
    arr: pa.Array | pa.ChunkedArray, out_type: pa.DataType
) -> pa.Array | pa.ChunkedArray:
    trimmed = _trim(arr)
    # Replace blanks with null before casting (avoids parse failures on "").
    trimmed_or_null = pc.if_else(
        pc.equal(trimmed, ""), pa.scalar(None, type=pa.string()), trimmed
    )
    return pc.cast(trimmed_or_null, out_type, safe=False)


def _to_str_or_null(arr: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    trimmed = _trim(arr)
    return pc.if_else(
        pc.equal(trimmed, ""), pa.scalar(None, type=pa.string()), trimmed
    )


def _max_recode6_ignoring_unknown(
    a: pa.Array | pa.ChunkedArray,
    b: pa.Array | pa.ChunkedArray,
    c: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Elementwise max of recode6 arrays where 6 means unknown/not stated.

    Returns:
    - max of known values 0-5 if any known value exists
    - 6 if no known values exist but any input is 6
    - null if all inputs are null
    """
    int8 = pa.int8()
    unknown = pa.scalar(6, type=int8)
    null_i8 = pa.scalar(None, type=int8)

    def _known(x: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
        return pc.if_else(pc.equal(x, unknown), null_i8, x)

    a_k = _known(a)
    b_k = _known(b)
    c_k = _known(c)
    max_ab = pc.max_element_wise(a_k, b_k)
    max_known = pc.max_element_wise(max_ab, c_k)

    any_unknown = pc.or_(
        pc.or_(
            pc.fill_null(pc.equal(a, unknown), False),
            pc.fill_null(pc.equal(b, unknown), False),
        ),
        pc.fill_null(pc.equal(c, unknown), False),
    )
    return pc.if_else(pc.and_(pc.is_null(max_known), any_unknown), unknown, max_known)


def _cigs_count_to_recode6(
    count: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map cigarette count (00-97; 98=98+; 99=unknown) to NCHS-style recode6:
    0=nonsmoker; 1=1-5; 2=6-10; 3=11-20; 4=21-40; 5=41+; 6=unknown/not stated.
    """
    int8 = pa.int8()
    null_i8 = pa.scalar(None, type=int8)
    out = pc.if_else(pc.is_null(count), null_i8, null_i8)
    out = pc.if_else(pc.equal(count, 0), pa.scalar(0, type=int8), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 1), pc.less_equal(count, 5)),
        pa.scalar(1, type=int8),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 6), pc.less_equal(count, 10)),
        pa.scalar(2, type=int8),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 11), pc.less_equal(count, 20)),
        pa.scalar(3, type=int8),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(count, 21), pc.less_equal(count, 40)),
        pa.scalar(4, type=int8),
        out,
    )
    # 41+ (including 98=98+)
    out = pc.if_else(pc.greater_equal(count, 41), pa.scalar(5, type=int8), out)
    # Unknown/not stated (99) must override 41+.
    out = pc.if_else(pc.equal(count, 99), pa.scalar(6, type=int8), out)
    return out


def _dmeduc_years_to_cat4(
    dmeduc: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map 1990–2002 education-in-years (00-17, 99=unknown) to 4-category:
    lt_hs (0-11), hs_grad (12), some_college (13-15), ba_plus (16-17).
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(dmeduc), null_s, null_s)
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 0), pc.less_equal(dmeduc, 11)),
        pa.scalar("lt_hs"),
        out,
    )
    out = pc.if_else(pc.equal(dmeduc, 12), pa.scalar("hs_grad"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 13), pc.less_equal(dmeduc, 15)),
        pa.scalar("some_college"),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(dmeduc, 16), pc.less_equal(dmeduc, 17)),
        pa.scalar("ba_plus"),
        out,
    )
    # 99 (unknown) → null
    return out


def _mrace_detail_to_bridged4(
    mrace: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map 1990–2002 detail race code (01-78) to approximate bridged 4-category:
    1=White, 2=Black, 3=AIAN, 4=Asian/PI.  Codes 09+ (other) → null.

    This is an approximate crosswalk; the official NCHS bridged race was
    only introduced with the 2003 certificate transition.
    """
    int8 = pa.int8()
    null_i8 = pa.scalar(None, type=int8)
    out = pc.if_else(pc.is_null(mrace), null_i8, null_i8)
    # 01 = White
    out = pc.if_else(pc.equal(mrace, 1), pa.scalar(1, type=int8), out)
    # 02 = Black
    out = pc.if_else(pc.equal(mrace, 2), pa.scalar(2, type=int8), out)
    # 03 = American Indian (includes Aleut/Eskimo in some years)
    out = pc.if_else(pc.equal(mrace, 3), pa.scalar(3, type=int8), out)
    # 04-08 = various Asian/Pacific Islander categories
    out = pc.if_else(
        pc.and_(pc.greater_equal(mrace, 4), pc.less_equal(mrace, 8)),
        pa.scalar(4, type=int8),
        out,
    )
    # 18-68 = additional Asian/PI detail codes (added from 1992)
    out = pc.if_else(
        pc.and_(pc.greater_equal(mrace, 18), pc.less_equal(mrace, 68)),
        pa.scalar(4, type=int8),
        out,
    )
    # 09 and others → null (no bridge available)
    return out


def _meduc_to_cat4(
    meduc: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(meduc), null_s, null_s)
    out = pc.if_else(
        pc.or_(pc.equal(meduc, 1), pc.equal(meduc, 2)),
        pa.scalar("lt_hs"),
        out,
    )
    out = pc.if_else(pc.equal(meduc, 3), pa.scalar("hs_grad"), out)
    out = pc.if_else(
        pc.or_(pc.equal(meduc, 4), pc.equal(meduc, 5)),
        pa.scalar("some_college"),
        out,
    )
    out = pc.if_else(
        pc.or_(
            pc.or_(pc.equal(meduc, 6), pc.equal(meduc, 7)),
            pc.equal(meduc, 8),
        ),
        pa.scalar("ba_plus"),
        out,
    )
    # meduc==9 (unknown) remains null
    return out


def _meduc_rec_to_cat4(
    meduc_rec: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(meduc_rec), null_s, null_s)
    out = pc.if_else(
        pc.or_(pc.equal(meduc_rec, 1), pc.equal(meduc_rec, 2)),
        pa.scalar("lt_hs"),
        out,
    )
    out = pc.if_else(pc.equal(meduc_rec, 3), pa.scalar("hs_grad"), out)
    out = pc.if_else(pc.equal(meduc_rec, 4), pa.scalar("some_college"), out)
    out = pc.if_else(pc.equal(meduc_rec, 5), pa.scalar("ba_plus"), out)
    # meduc_rec==6 (not stated) remains null
    return out


def _month_to_trimester(
    month: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Convert prenatal care start month to trimester labels:
    - none: month==0
    - 1st: 1-3
    - 2nd: 4-6
    - 3rd: 7-10
    - unknown: month==99
    - null: month is null
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(month), null_s, null_s)
    out = pc.if_else(pc.equal(month, 99), pa.scalar("unknown"), out)
    out = pc.if_else(pc.equal(month, 0), pa.scalar("none"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 1), pc.less_equal(month, 3)),
        pa.scalar("1st"),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 4), pc.less_equal(month, 6)),
        pa.scalar("2nd"),
        out,
    )
    out = pc.if_else(
        pc.and_(pc.greater_equal(month, 7), pc.less_equal(month, 10)),
        pa.scalar("3rd"),
        out,
    )
    return out


def _yn_to_bool(
    arr: pa.Array | pa.ChunkedArray,
    true_values: tuple[str, ...] = ("Y",),
) -> pa.Array | pa.ChunkedArray:
    """Map Y/N/U (or C/P/N/U) string field to bool.
    true_values map to True, 'N' maps to False, all else to null."""
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
    """Map ORRACEF/FRACEHISP combined code to 5-category string.

    Two coding schemes exist:
      ORRACEF (1990-2002) and FRACEHISP (2003-2013) share the same codes:
        1-5→Hispanic, 6→NH_white, 7→NH_black, 8→NH_other, 9→null.
      FRACEHISP (2014+) uses a different scheme:
        1→NH_white, 2→NH_black, 3-6→NH_other, 7→Hispanic, 8-9→null.
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(code), null_s, null_s)

    if is_2014_plus:
        # FRACEHISP 2014+: 1=NH White, 2=NH Black, 3=NH AIAN,
        # 4=NH Asian, 5=NH NHOPI, 6=NH Multirace, 7=Hispanic,
        # 8=Origin unknown, 9=Unknown
        out = pc.if_else(pc.equal(code, 1), pa.scalar("NH_white"), out)
        out = pc.if_else(pc.equal(code, 2), pa.scalar("NH_black"), out)
        out = pc.if_else(
            pc.and_(pc.greater_equal(code, 3), pc.less_equal(code, 6)),
            pa.scalar("NH_other"), out,
        )
        out = pc.if_else(pc.equal(code, 7), pa.scalar("Hispanic"), out)
        # Codes 8-9 → null (origin unknown / unknown)
    else:
        # ORRACEF (1990-2002) / FRACEHISP (2003-2013): 1-5=Hispanic
        # subcategories, 6=NH White, 7=NH Black, 8=NH Other Races,
        # 9=Origin unknown
        out = pc.if_else(
            pc.and_(pc.greater_equal(code, 1), pc.less_equal(code, 5)),
            pa.scalar("Hispanic"), out,
        )
        out = pc.if_else(pc.equal(code, 6), pa.scalar("NH_white"), out)
        out = pc.if_else(pc.equal(code, 7), pa.scalar("NH_black"), out)
        out = pc.if_else(pc.equal(code, 8), pa.scalar("NH_other"), out)
        # Code 9 → null (origin unknown)
    return out


def _pldel_to_facility(
    pldel: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map 1990–2002 PLDEL code to harmonized birth facility string.
    1=Hospital→hospital, 2=Birth Center→birth_center, 3=Clinic→clinic_other,
    4=Residence→home, 5=Other→clinic_other, 9/blank→null.
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(pldel), null_s, null_s)
    out = pc.if_else(pc.equal(pldel, 1), pa.scalar("hospital"), out)
    out = pc.if_else(pc.equal(pldel, 2), pa.scalar("birth_center"), out)
    out = pc.if_else(pc.equal(pldel, 3), pa.scalar("clinic_other"), out)
    out = pc.if_else(pc.equal(pldel, 4), pa.scalar("home"), out)
    out = pc.if_else(pc.equal(pldel, 5), pa.scalar("clinic_other"), out)
    # 9 = unknown → null
    return out


def _bfacil_to_facility(
    bfacil: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map 2003+ UBFACIL/BFACIL code to harmonized birth facility string.
    1=Hospital→hospital, 2=Birth Center→birth_center, 3-5=Home→home,
    6=Clinic→clinic_other, 7=Other→clinic_other, 9/blank→null.
    """
    null_s = pa.scalar(None, type=pa.string())
    out = pc.if_else(pc.is_null(bfacil), null_s, null_s)
    out = pc.if_else(pc.equal(bfacil, 1), pa.scalar("hospital"), out)
    out = pc.if_else(pc.equal(bfacil, 2), pa.scalar("birth_center"), out)
    out = pc.if_else(
        pc.and_(pc.greater_equal(bfacil, 3), pc.less_equal(bfacil, 5)),
        pa.scalar("home"),
        out,
    )
    out = pc.if_else(pc.equal(bfacil, 6), pa.scalar("clinic_other"), out)
    out = pc.if_else(pc.equal(bfacil, 7), pa.scalar("clinic_other"), out)
    # 9 = unknown → null
    return out


def _fagerec11_to_cat(
    rec11: pa.Array | pa.ChunkedArray,
) -> pa.Array | pa.ChunkedArray:
    """
    Map FAGEREC11 (01-11) to a categorical string matching `father_age_cat`
    buckets.  Used to recover categorical father age for years where raw
    single-year age (FAGECOMB/UFAGECOMB) is blank (notably 2012).

    NCHS FAGEREC11 coding:
      01 = Under 15 → "<20"
      02 = 15-19   → "<20"
      03 = 20-24   → "20-24"
      04 = 25-29   → "25-29"
      05 = 30-34   → "30-34"
      06 = 35-39   → "35-39"
      07 = 40-44   → "40+"
      08 = 45-49   → "40+"
      09 = 50-54   → "40+"
      10 = 55+     → "40+"
      11 = Not stated → null
    """
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
    # rec11 == 11 (not stated) and anything else stays null
    return out


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


def main() -> None:
    args = parse_args()
    years = _parse_years(args.years)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    out_schema = pa.schema(
        [
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
            # Paternal demographics
            ("father_hispanic", pa.bool_()),
            ("father_race_ethnicity_5", pa.string()),
            ("father_education_cat4", pa.string()),
            # Congenital anomalies (2014+ only)
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
            # Infections (2014+ only)
            ("infection_gonorrhea", pa.bool_()),
            ("infection_syphilis", pa.bool_()),
            ("infection_chlamydia", pa.bool_()),
            ("infection_hep_b", pa.bool_()),
            ("infection_hep_c", pa.bool_()),
            # Prior cesarean count and fertility (2014+ only)
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
        ]
    )

    writer: pq.ParquetWriter | None = None
    try:
        for year in years:
            in_path = args.yearly_parquet_dir / f"natality_{year}_core.parquet"
            if not in_path.is_file():
                raise FileNotFoundError(in_path)

            pf = pq.ParquetFile(in_path)
            cols = set(pf.schema_arrow.names)

            # Detect era from available columns.
            is_pre2003 = "DMAGE" in cols  # 1990–2002 have DMAGE; 2003+ have MAGER
            is_post2013 = "OEGEST_COMB" in cols  # 2014+ have obstetric estimate

            # Year-varying column name resolution (2003+ era)
            marital_col = "DMAR" if "DMAR" in cols else "MAR"
            visits_col = "PREVIS" if "PREVIS" in cols else ("NPREVIS" if "NPREVIS" in cols else "UPREVIS")
            hisp_col = "MHISP_R" if "MHISP_R" in cols else ("ORMOTH" if "ORMOTH" in cols else "UMHISP")
            race_bridged_col = "MBRACE" if "MBRACE" in cols else "MRACEREC"
            race_detail_col = "MRACE6" if "MRACE6" in cols else "MRACE"

            for batch in pf.iter_batches(batch_size=args.batch_rows):
                # === Year ===
                year_arr = pc.cast(_get_col(batch, "year"), pa.int16())

                null_s = pa.scalar(None, type=pa.string())
                revised_s = pa.scalar("revised_2003", type=pa.string())
                unrevised_s = pa.scalar("unrevised_1989", type=pa.string())
                unknown_s = pa.scalar("unknown", type=pa.string())

                # === RESTATUS ===
                restatus = _to_int_or_null(_get_col(batch, "RESTATUS"), pa.int8())
                is_foreign = pc.equal(restatus, pa.scalar(4, type=pa.int8()))

                if is_pre2003:
                    # ============================================================
                    # 1990–2002 era: unrevised certificate only
                    # ============================================================

                    # Certificate revision: always unrevised_1989
                    cert_rev = pc.if_else(pc.is_null(year_arr), null_s, unrevised_s)

                    # Maternal age
                    mager = _to_int_or_null(_get_col(batch, "DMAGE"), pa.int16())

                    # Marital status
                    marital = _to_int_or_null(_get_col(batch, "DMAR"), pa.int8())
                    marital_rpt_flag = pa.nulls(batch.num_rows, type=pa.bool_())

                    # Birth order (9-category recodes → same semantics as LBO_REC/TBO_REC)
                    lbo = _to_int_or_null(_get_col(batch, "LIVORD9"), pa.int8())
                    tbo = _to_int_or_null(_get_col(batch, "TOTORD9"), pa.int8())

                    # Hispanic origin
                    hisp_origin = _to_int_or_null(_get_col(batch, "ORMOTH"), pa.int8())
                    is_hisp = pc.and_(
                        pc.greater_equal(hisp_origin, pa.scalar(1, type=pa.int8())),
                        pc.less_equal(hisp_origin, pa.scalar(5, type=pa.int8())),
                    )
                    is_nonhisp = pc.equal(hisp_origin, pa.scalar(0, type=pa.int8()))
                    maternal_hisp = pc.if_else(
                        is_hisp,
                        pa.scalar(True),
                        pc.if_else(is_nonhisp, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
                    )

                    # Race: approximate bridged-4 from MRACE detail code
                    mrace_detail = _to_int_or_null(_get_col(batch, "MRACE"), pa.int16())
                    race_bridged = _mrace_detail_to_bridged4(mrace_detail)
                    race_detail = _to_str_or_null(_get_col(batch, "MRACE"))
                    # MRACE15 is not in 1990-2002 files.
                    race_detail_15 = pa.nulls(batch.num_rows, type=pa.string())

                    # NH race/ethnicity 5-category. Use fill_null-guarded conditions to
                    # avoid pyarrow's non-Kleene pc.and_ wiping Hispanic labels when
                    # race_bridged is null (e.g. MRACE detail codes that bridge to null).
                    def _safe_cond(*parts):
                        from functools import reduce
                        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

                    race_eth = pc.if_else(
                        pc.fill_null(pc.equal(maternal_hisp, pa.scalar(True)), False),
                        pa.scalar("Hispanic"),
                        null_s,
                    )
                    is_nh = pc.fill_null(pc.equal(maternal_hisp, pa.scalar(False)), False)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)), pa.scalar("NH_white"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)), pa.scalar("NH_black"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)), pa.scalar("NH_aian"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)), pa.scalar("NH_asian_pi"), race_eth)

                    race_bridge = pc.if_else(
                        pc.is_null(year_arr), null_s, pa.scalar("approximate_pre2003"),
                    )

                    # Education: years of schooling (00-17) → cat4
                    dmeduc = _to_int_or_null(_get_col(batch, "DMEDUC"), pa.int16())
                    educ_cat4 = _dmeduc_years_to_cat4(dmeduc)

                    # Prenatal care start month (MONPRE)
                    pn_start_month = _to_int_or_null(_get_col(batch, "MONPRE"), pa.int16())
                    pn_start_trim = _month_to_trimester(pn_start_month)

                    # Prenatal visits
                    previs = _to_int_or_null(_get_col(batch, "NPREVIS"), pa.int16())

                    # Medical risk factors: individual Y/N/unknown (1/2/9) flags
                    # Map to same coding as URF_ variables (1=yes, 2=no, 9=unknown)
                    diab = _to_int_or_null(_get_col(batch, "DIABETES"), pa.int8())
                    chyp = _to_int_or_null(_get_col(batch, "CHYPER"), pa.int8())
                    phyp = _to_int_or_null(_get_col(batch, "PHYPER"), pa.int8())

                    # Smoking: TOBACCO (1=yes, 2=no, 9=unknown), CIGAR6 (recode)
                    tobacco = _to_int_or_null(_get_col(batch, "TOBACCO"), pa.int8())
                    smoke_any = pc.if_else(
                        pc.equal(tobacco, 1),
                        pa.scalar(True),
                        pc.if_else(
                            pc.equal(tobacco, 2),
                            pa.scalar(False),
                            pa.scalar(None, type=pa.bool_()),
                        ),
                    )
                    smoke_intensity = _to_int_or_null(_get_col(batch, "CIGAR6"), pa.int8())
                    # Nat2000-2002 CIGAR6 uses 9 for unknown; 2003+ convention is 6.
                    # Remap 9→6 here so the column has uniform unknown-encoding across
                    # 1990-2024 (schema allows only 0-6).
                    smoke_intensity = pc.if_else(
                        pc.fill_null(pc.equal(smoke_intensity, 9), False),
                        pa.scalar(6, type=pa.int8()),
                        smoke_intensity,
                    )
                    cig0_r = pa.nulls(batch.num_rows, type=pa.int8())  # not available

                    # Plurality
                    plur = _to_int_or_null(_get_col(batch, "DPLURAL"), pa.int8())

                    # Sex: numeric 1=M, 2=F → string "M"/"F"
                    csex = _to_int_or_null(_get_col(batch, "CSEX"), pa.int8())
                    sex = pc.if_else(
                        pc.equal(csex, 1),
                        pa.scalar("M"),
                        pc.if_else(pc.equal(csex, 2), pa.scalar("F"), null_s),
                    )

                    # Gestation: LMP-based only
                    gest_weeks = _to_int_or_null(_get_col(batch, "DGESTAT"), pa.int16())
                    gest_src = pc.if_else(
                        pc.is_null(gest_weeks),
                        null_s,
                        pa.scalar("lmp"),
                    )
                    preterm_r3 = _to_int_or_null(_get_col(batch, "GESTAT3"), pa.int8())

                    # Birthweight
                    dbwt = _to_int_or_null(_get_col(batch, "DBIRWT"), pa.int32())

                    # Delivery method: DELMETH5 (1-5; recode 5=not stated → 9 for consistency)
                    delmeth5 = _to_int_or_null(_get_col(batch, "DELMETH5"), pa.int8())
                    dmeth = pc.if_else(
                        pc.equal(delmeth5, 5),
                        pa.scalar(9, type=pa.int8()),
                        delmeth5,
                    )

                    # Apgar5
                    apgar5 = _to_int_or_null(_get_col(batch, "FMAPS"), pa.int16())

                    # BMI: not available pre-2014
                    bmi_pp = pa.nulls(batch.num_rows, type=pa.float32())
                    bmi_pp_r6 = pa.nulls(batch.num_rows, type=pa.int8())

                    # Father's age (DFAGE: 10-98, 99=unknown)
                    fage = _to_int_or_null(_get_col(batch, "DFAGE"), pa.int16())
                    # Null out-of-range: valid range 10-98; 99=unknown, <10 or >98 are invalid
                    fage = pc.if_else(
                        pc.and_(
                            pc.greater_equal(fage, pa.scalar(10, type=pa.int16())),
                            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
                        ),
                        fage,
                        pa.scalar(None, type=pa.int16()),
                    )
                    # FAGEREC11 is not in 1990-2002 files; this column is null for that era.
                    fage_cat_rec11 = pa.nulls(batch.num_rows, type=pa.string())

                    # Birth facility (PLDEL)
                    pldel = _to_int_or_null(_get_col(batch, "PLDEL"), pa.int8())
                    birth_fac = _pldel_to_facility(pldel)

                    # Attendant at birth (BIRATTND: 1-5, 9=unknown)
                    attend = _to_int_or_null(_get_col(batch, "BIRATTND"), pa.int8())
                    attend = pc.if_else(
                        pc.equal(attend, pa.scalar(9, type=pa.int8())),
                        pa.scalar(None, type=pa.int8()),
                        attend,
                    )

                    # Payment source: not available pre-2014
                    pay_rec = pa.nulls(batch.num_rows, type=pa.int8())

                    # Prior cesarean: not available pre-2014
                    prior_ces = pa.nulls(batch.num_rows, type=pa.bool_())

                    # Father's Hispanic origin (ORFATH: same coding as ORMOTH)
                    fath_hisp_origin = _to_int_or_null(_get_col(batch, "ORFATH"), pa.int8())
                    fath_is_hisp = pc.and_(
                        pc.greater_equal(fath_hisp_origin, pa.scalar(1, type=pa.int8())),
                        pc.less_equal(fath_hisp_origin, pa.scalar(5, type=pa.int8())),
                    )
                    fath_is_nonhisp = pc.equal(fath_hisp_origin, pa.scalar(0, type=pa.int8()))
                    father_hisp = pc.if_else(
                        fath_is_hisp, pa.scalar(True),
                        pc.if_else(fath_is_nonhisp, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
                    )

                    # Father's race/ethnicity 5-category (ORRACEF)
                    orracef = _to_int_or_null(_get_col(batch, "ORRACEF"), pa.int8())
                    father_race_eth = _racehisp_combined_to_5cat(orracef, is_2014_plus=False)

                    # Father's education (DFEDUC: years 00-17, 99=unknown)
                    # Available 1990-1994 only; blank for 1995-2002 → null
                    dfeduc = _to_int_or_null(_get_col(batch, "DFEDUC"), pa.int16())
                    father_educ_cat4 = _dmeduc_years_to_cat4(dfeduc)

                    # 2014+-only fields: all null for 1990-2002
                    n = batch.num_rows
                    ca_list = [pa.nulls(n, type=pa.bool_()) for _ in range(12)]
                    ip_list = [pa.nulls(n, type=pa.bool_()) for _ in range(5)]
                    prior_ces_count = pa.nulls(n, type=pa.int8())
                    fert_drugs = pa.nulls(n, type=pa.bool_())
                    art = pa.nulls(n, type=pa.bool_())
                    pre_preg_diab = pa.nulls(n, type=pa.bool_())
                    gest_diab = pa.nulls(n, type=pa.bool_())
                    nicu = pa.nulls(n, type=pa.bool_())
                    wtgain = pa.nulls(n, type=pa.int16())
                    indl = pa.nulls(n, type=pa.bool_())
                    bfed = pa.nulls(n, type=pa.bool_())

                else:
                    # ============================================================
                    # 2003–2020 era: dual certificate or revised-only
                    # ============================================================

                    # Maternal age: 2003 has MAGER41 (41-category recode), 2004+ has MAGER
                    mager41_raw = _get_col_optional(batch, "MAGER41")
                    if mager41_raw is not None:
                        # Convert mager41 recode to single-year age:
                        # 01 → 14 (under 15), 02 → 15, 03 → 16, ..., 36 → 49,
                        # 37 → 50, 38 → 51, 39 → 52, 40 → 53, 41 → 54.
                        # General formula: code 1 → 14; codes 2-41 → code + 13.
                        # 99 or invalid → null.
                        mager41 = _to_int_or_null(mager41_raw, pa.int16())
                        mager = pc.if_else(
                            pc.equal(mager41, 1),
                            pa.scalar(14, type=pa.int16()),
                            pc.add(mager41, pa.scalar(13, type=pa.int16())),
                        )
                        # Null out invalid/unknown codes
                        mager = pc.if_else(
                            pc.or_(pc.equal(mager41, 99), pc.greater(mager41, 41)),
                            pa.scalar(None, type=pa.int16()),
                            mager,
                        )
                    else:
                        mager = _to_int_or_null(_get_col(batch, "MAGER"), pa.int16())

                    marital = _to_int_or_null(_get_col(batch, marital_col), pa.int8())

                    # Marital reporting flag (F_MAR_P: 0=non-reporting state, 1=reporting; 2014+ only)
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

                    # Birth order recodes
                    lbo = _to_int_or_null(_get_col(batch, "LBO_REC"), pa.int8())
                    tbo = _to_int_or_null(_get_col(batch, "TBO_REC"), pa.int8())

                    # Hispanic origin and bridged race
                    hisp_origin = _to_int_or_null(_get_col(batch, hisp_col), pa.int8())
                    is_hisp = pc.and_(
                        pc.greater_equal(hisp_origin, pa.scalar(1, type=pa.int8())),
                        pc.less_equal(hisp_origin, pa.scalar(5, type=pa.int8())),
                    )
                    is_nonhisp = pc.equal(hisp_origin, pa.scalar(0, type=pa.int8()))
                    maternal_hisp = pc.if_else(
                        is_hisp,
                        pa.scalar(True),
                        pc.if_else(is_nonhisp, pa.scalar(False), pa.scalar(None, type=pa.bool_())),
                    )

                    race_bridged = _to_int_or_null(_get_col(batch, race_bridged_col), pa.int8())

                    # NH race/ethnicity (5-category) as strings.
                    # Use fill_null(False) on every component of compound conditions because
                    # pyarrow's pc.and_ is NOT Kleene-aware: pc.and_(True, null) = null (not null-unknown),
                    # which would cause pc.if_else(null_cond, new, current) to overwrite the current
                    # value with null. This was the root cause of the 2020+ race_eth 100%-null bug.
                    def _safe_cond(*parts):
                        from functools import reduce
                        return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))

                    race_eth = pc.if_else(
                        pc.fill_null(pc.equal(maternal_hisp, pa.scalar(True)), False),
                        pa.scalar("Hispanic"),
                        null_s,
                    )
                    is_nh = pc.fill_null(pc.equal(maternal_hisp, pa.scalar(False)), False)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 1)), pa.scalar("NH_white"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 2)), pa.scalar("NH_black"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 3)), pa.scalar("NH_aian"), race_eth)
                    race_eth = pc.if_else(_safe_cond(is_nh, pc.equal(race_bridged, 4)), pa.scalar("NH_asian_pi"), race_eth)

                    # Race detail (within-era)
                    race_detail_raw = _get_col(batch, race_detail_col)
                    race_detail = _to_str_or_null(race_detail_raw)
                    # 2014+ MRACE6 is a 1-digit field ('1'..'6'); 1990-2013 MRACE is
                    # 2-digit zero-padded ('01'..'78'). Zero-pad 2014+ values so the
                    # maternal_race_detail column has a uniform 2-digit format across
                    # the full 1990-2024 span. A user filtering `== '01'` would
                    # otherwise silently drop all 2014+ White rows.
                    if race_detail_col == "MRACE6":
                        race_detail = pc.utf8_lpad(race_detail, 2, "0")

                    # MRACE15 — 15-category detail race recode (AUDIT D6).
                    # Populated for revised-cert rows 2003-2013 and all 2014+ rows.
                    # Gives detail race for 2003-2013 revised rows where MRACE@141-142
                    # is blank (~61-91% of 2008-2013 rows).
                    mrace15_raw = _get_col_optional(batch, "MRACE15")
                    if mrace15_raw is not None:
                        race_detail_15 = _to_str_or_null(mrace15_raw)
                        # Null the NCHS "99" unknown sentinel (present in some 2015
                        # rows; invariant mrace15_invalid_when_nonnull requires the
                        # output frame be {01..15} ∪ null).
                        race_detail_15 = pc.if_else(
                            pc.fill_null(pc.equal(race_detail_15, pa.scalar("99")), False),
                            pa.scalar(None, type=pa.string()),
                            race_detail_15,
                        )
                    else:
                        race_detail_15 = pa.nulls(batch.num_rows, type=pa.string())

                    # For 2020+, MBRACE is null (NCHS dropped bridged race).
                    # Reconstruct race_eth from MRACE6 detail codes for non-Hispanic births.
                    # MRACE6: 1=White, 2=Black, 3=AIAN, 4=Asian, 5=NHOPI, 6=Multiracial(→null).
                    # (Single-byte field at position 107 per UserGuide2021.pdf p13.)
                    if is_post2013:
                        needs_fill = _safe_cond(is_nh, pc.is_null(race_bridged))
                        rd_int = _to_int_or_null(race_detail_raw, pa.int16())
                        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 1)), pa.scalar("NH_white"), race_eth)
                        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 2)), pa.scalar("NH_black"), race_eth)
                        race_eth = pc.if_else(_safe_cond(needs_fill, pc.equal(rd_int, 3)), pa.scalar("NH_aian"), race_eth)
                        race_eth = pc.if_else(
                            _safe_cond(needs_fill, pc.or_(pc.equal(rd_int, 4), pc.equal(rd_int, 5))),
                            pa.scalar("NH_asian_pi"), race_eth,
                        )
                        # code 6 (multiracial, ~3%) stays null — cannot be bridged to single group

                    # Race bridge method: nchs_bridged for 2003-2019, approximate_from_detail for 2020+
                    race_bridge = pc.if_else(
                        pc.less(year_arr, pa.scalar(2020, type=pa.int16())),
                        pa.scalar("nchs_bridged"),
                        pa.scalar("approximate_from_detail"),
                    )

                    # Education (cat4) — revised MEDUC vs unrevised MEDUC_REC
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

                    # Certificate revision indicator
                    if year >= 2014:
                        cert_rev = pc.if_else(pc.is_null(year_arr), null_s, revised_s)
                    elif year <= 2002:
                        cert_rev = pc.if_else(pc.is_null(year_arr), null_s, unrevised_s)
                    else:
                        has_meduc = pc.invert(pc.is_null(meduc))
                        has_mrace = pc.invert(pc.is_null(race_detail))
                        cert_rev = pc.if_else(has_meduc, revised_s, null_s)
                        cert_rev = pc.if_else(
                            pc.and_(pc.is_null(cert_rev), has_mrace),
                            unrevised_s,
                            cert_rev,
                        )
                        cert_rev = pc.if_else(pc.is_null(cert_rev), unknown_s, cert_rev)

                    # Prenatal care start month (revised PRECARE vs unrevised MPCB)
                    precare_raw = _get_col(batch, "PRECARE")
                    precare = _to_int_or_null(precare_raw, pa.int16())
                    mpcb_raw = _get_col_optional(batch, "MPCB")
                    mpcb = (
                        _to_int_or_null(mpcb_raw, pa.int16())
                        if mpcb_raw is not None
                        else pa.nulls(batch.num_rows, type=pa.int16())
                    )
                    pn_start_month = pc.if_else(pc.is_null(precare), mpcb, precare)
                    pn_start_trim = _month_to_trimester(pn_start_month)

                    previs = _to_int_or_null(_get_col(batch, visits_col), pa.int16())

                    # Diabetes / hypertension source selection (AUDIT D4):
                    # - 2003-2015: URF_DIAB/CHYPER/PHYPER exist in the public-use record
                    #   and carry the consolidated 1/2/9 risk-factor codes directly.
                    # - 2016+: NCHS removed URF_* from the record (bytes 1331-1333 are
                    #   filler FILLER_X in UserGuide2016+.pdf). Derive from RF_PDIAB/
                    #   RF_GDIAB (combined via OR), RF_PHYPE, RF_GHYPE (Y/N/U each).
                    # Decision is per-year (not per-batch) to avoid inconsistency within
                    # the same year if batch ordering ever causes the URF_* block to be
                    # partly populated in one batch and blank in another.
                    use_rf_fallback = year >= 2016

                    if use_rf_fallback:
                        rf_pd = _get_col_optional(batch, "RF_PDIAB")
                        rf_gd = _get_col_optional(batch, "RF_GDIAB")
                        if rf_pd is not None and rf_gd is not None:
                            pd_yes = _yn_to_bool(rf_pd)
                            gd_yes = _yn_to_bool(rf_gd)
                            either = pc.or_(pc.fill_null(pd_yes, False), pc.fill_null(gd_yes, False))
                            both_known = pc.and_(pc.is_valid(pd_yes), pc.is_valid(gd_yes))
                            # 1=yes (either), 2=no (both known and neither), null otherwise
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

                    # Smoking
                    cig0_r_raw = _get_col_optional(batch, "CIG0_R")
                    cig0_r = (
                        _to_int_or_null(cig0_r_raw, pa.int8())
                        if cig0_r_raw is not None
                        else pa.nulls(batch.num_rows, type=pa.int8())
                    )

                    # Preferred revised-era recodes when present (2014+)
                    cig1_r_raw = _get_col_optional(batch, "CIG1_R")
                    cig2_r_raw = _get_col_optional(batch, "CIG2_R")
                    cig3_r_raw = _get_col_optional(batch, "CIG3_R")

                    if cig1_r_raw is not None and cig2_r_raw is not None and cig3_r_raw is not None:
                        cig1_r = _to_int_or_null(cig1_r_raw, pa.int8())
                        cig2_r = _to_int_or_null(cig2_r_raw, pa.int8())
                        cig3_r = _to_int_or_null(cig3_r_raw, pa.int8())
                        smoke_intensity = _max_recode6_ignoring_unknown(cig1_r, cig2_r, cig3_r)
                    else:
                        # Unrevised recode plus revised trimester counts (2003-2013)
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
                            cig_rec6,
                            trimester_max,
                            pa.nulls(batch.num_rows, type=pa.int8()),
                        )

                    is_smoker = pc.and_(
                        pc.greater_equal(smoke_intensity, 1),
                        pc.less_equal(smoke_intensity, 5),
                    )
                    is_nonsmoker = pc.equal(smoke_intensity, 0)
                    smoke_any = pc.if_else(
                        is_smoker,
                        pa.scalar(True),
                        pc.if_else(
                            is_nonsmoker, pa.scalar(False), pa.scalar(None, type=pa.bool_())
                        ),
                    )

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
                        pc.is_null(gest_weeks),
                        null_s,
                        pc.if_else(
                            pc.is_null(oegest),
                            pa.scalar("combined"),
                            pa.scalar("obstetric_estimate"),
                        ),
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
                    # 2003-2004: DMETH_REC at position 401 stores DELMETH5-style codes
                    # (1=vag, 2=VBAC, 3=primary CS, 4=repeat CS, 5=not stated, 6/7=rare).
                    # Remap 5/6/7 → 9 to align the "not stated" sentinel with 1990-2002 and 2005+.
                    if year in (2003, 2004):
                        dmeth = pc.if_else(
                            pc.fill_null(pc.greater_equal(dmeth, pa.scalar(5, type=pa.int8())), False),
                            pa.scalar(9, type=pa.int8()),
                            dmeth,
                        )

                    apgar5_raw = _get_col_optional(batch, "APGAR5")
                    apgar5 = (
                        _to_int_or_null(apgar5_raw, pa.int16())
                        if apgar5_raw is not None
                        else pa.nulls(batch.num_rows, type=pa.int16())
                    )

                    # BMI: available 2014+ (positions 283-286 = xx.x, 287 = recode)
                    bmi_raw = _get_col_optional(batch, "BMI")
                    bmi_r_raw = _get_col_optional(batch, "BMI_R")
                    if bmi_raw is not None:
                        # Parse float; blank→null, 99.9=unknown→null
                        bmi_str = bmi_raw.cast(pa.string())
                        stripped = pc.utf8_trim_whitespace(bmi_str)
                        is_blank = pc.equal(stripped, pa.scalar(""))
                        # Replace blanks with "NaN" so cast doesn't fail
                        castable = pc.if_else(is_blank, pa.scalar("NaN"), stripped)
                        bmi_float = pc.cast(castable, pa.float32(), safe=False)
                        bmi_pp = pc.if_else(
                            pc.or_(pc.is_nan(bmi_float),
                                   pc.greater_equal(bmi_float, pa.scalar(99.0, type=pa.float32()))),
                            pa.scalar(None, type=pa.float32()),
                            bmi_float,
                        )
                        bmi_pp_r6 = _to_int_or_null(bmi_r_raw, pa.int8())
                        # 9 = unknown → null
                        bmi_pp_r6 = pc.if_else(
                            pc.equal(bmi_pp_r6, pa.scalar(9, type=pa.int8())),
                            pa.scalar(None, type=pa.int8()),
                            bmi_pp_r6,
                        )
                    else:
                        bmi_pp = pa.nulls(batch.num_rows, type=pa.float32())
                        bmi_pp_r6 = pa.nulls(batch.num_rows, type=pa.int8())

                    # Father's age
                    # Layout history:
                    #   2003-2005: single-year age at UFAGECOMB@184-185 only (FAGECOMB blank).
                    #   2006-2011: FAGECOMB@182-183 populated on revised-cert rows (~28%→65%→86%);
                    #              UFAGECOMB@184-185 still populated across all rows. The two agree
                    #              100% in the overlap (verified across 2.1M sampled rows).
                    #   2012:      UFAGECOMB@184-185 blank; FAGECOMB@182-183 populated on revised-
                    #              cert rows only (~36%). Gives ~77% father_age population overall
                    #              (for categorical coverage of unrevised rows, use FAGEREC11).
                    #   2013:      UFAGECOMB blank; FAGECOMB@182-183 populated on ~90% of rows.
                    #   2014+:     FAGECOMB@147-148 (revised-cert only; 100% revised-cert from 2014).
                    # Strategy: prefer FAGECOMB when non-null, fall back to UFAGECOMB.
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
                    # Null out-of-range: valid range 9-98; 99=unknown, <9 or >98 are invalid
                    fage = pc.if_else(
                        pc.and_(
                            pc.greater_equal(fage, pa.scalar(9, type=pa.int16())),
                            pc.less_equal(fage, pa.scalar(98, type=pa.int16())),
                        ),
                        fage,
                        pa.scalar(None, type=pa.int16()),
                    )

                    # Categorical father-age fallback from FAGEREC11 (2005-2013 only).
                    # Recovers categorical age for 2012 where raw single-year age is blank.
                    fagerec11_raw = _get_col_optional(batch, "FAGEREC11")
                    if fagerec11_raw is not None:
                        fagerec11 = _to_int_or_null(fagerec11_raw, pa.int8())
                        fage_cat_rec11 = _fagerec11_to_cat(fagerec11)
                    else:
                        fage_cat_rec11 = pa.nulls(batch.num_rows, type=pa.string())

                    # Birth facility (BFACIL for 2014+ revised, UBFACIL for 2003-2013 unrevised/national)
                    # UBFACIL uses the same coding as PLDEL (3=clinic, 4=residence, 5=other)
                    # BFACIL uses revised coding (3-5=home variants, 6=clinic, 7=other)
                    if "BFACIL" in cols:
                        bfacil_raw = _to_int_or_null(_get_col(batch, "BFACIL"), pa.int8())
                        birth_fac = _bfacil_to_facility(bfacil_raw)
                    else:
                        ubfacil_raw = _to_int_or_null(_get_col(batch, "UBFACIL"), pa.int8())
                        birth_fac = _pldel_to_facility(ubfacil_raw)

                    # Attendant at birth (ATTEND: 1-5, 9=unknown)
                    attend = _to_int_or_null(_get_col(batch, "ATTEND"), pa.int8())
                    attend = pc.if_else(
                        pc.equal(attend, pa.scalar(9, type=pa.int8())),
                        pa.scalar(None, type=pa.int8()),
                        attend,
                    )

                    # Payment source (PAY_REC: 2014+ only)
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

                    # Prior cesarean (RF_CESAR: 2014+ only; Y/N/U)
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

                    # Father's Hispanic origin (FHISP_R for 2014+, UFHISP for 2003-2013)
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

                    # Father's race/ethnicity 5-category (FRACEHISP)
                    fracehisp = _to_int_or_null(_get_col(batch, "FRACEHISP"), pa.int8())
                    father_race_eth = _racehisp_combined_to_5cat(fracehisp, is_2014_plus=(year >= 2014))

                    # Father's education (FEDUC: 1-8 categories, 9=unknown)
                    # Available 2009+ (partial 2009-2010 from 2003-revision states); blank for 2003-2008 → null
                    feduc_raw = _get_col_optional(batch, "FEDUC")
                    if feduc_raw is not None:
                        feduc = _to_int_or_null(feduc_raw, pa.int8())
                        father_educ_cat4 = _meduc_to_cat4(feduc)
                    else:
                        father_educ_cat4 = pa.nulls(batch.num_rows, type=pa.string())

                    # Congenital anomalies (2014+ only; Y/N/U or C/P/N/U)
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

                    # Infections (2014+ only; Y/N/U)
                    _IP_FIELDS = ["IP_GON", "IP_SYPH", "IP_CHLAM", "IP_HEPB", "IP_HEPC"]
                    ip_list = []
                    for fname in _IP_FIELDS:
                        raw = _get_col_optional(batch, fname)
                        ip_list.append(_yn_to_bool(raw) if raw is not None
                                       else pa.nulls(batch.num_rows, type=pa.bool_()))

                    # Prior cesarean count (RF_CESARN: 00-30, 99=unknown)
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

                    # Fertility treatment (RF_FEDRG: Y/N/X/U; RF_ARTEC: Y/N/U)
                    rf_fedrg_raw = _get_col_optional(batch, "RF_FEDRG")
                    fert_drugs = (_yn_to_bool(rf_fedrg_raw) if rf_fedrg_raw is not None
                                  else pa.nulls(batch.num_rows, type=pa.bool_()))
                    rf_artec_raw = _get_col_optional(batch, "RF_ARTEC")
                    art = (_yn_to_bool(rf_artec_raw) if rf_artec_raw is not None
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

                # === Build output table (same schema for all eras) ===
                out_tbl = pa.Table.from_arrays(
                    [
                        year_arr,
                        restatus,
                        is_foreign,
                        cert_rev,
                        mager,
                        lbo,
                        tbo,
                        marital,
                        marital_rpt_flag,
                        hisp_origin,
                        maternal_hisp,
                        race_bridged,
                        race_eth,
                        race_detail,
                        race_detail_15,
                        race_bridge,
                        educ_cat4,
                        pn_start_month,
                        pn_start_trim,
                        previs,
                        smoke_any,
                        smoke_intensity,
                        cig0_r,
                        diab,
                        chyp,
                        phyp,
                        plur,
                        sex,
                        gest_weeks,
                        gest_src,
                        preterm_r3,
                        dbwt,
                        dmeth,
                        apgar5,
                        bmi_pp,
                        bmi_pp_r6,
                        fage,
                        fage_cat_rec11,
                        birth_fac,
                        attend,
                        pay_rec,
                        prior_ces,
                        father_hisp,
                        father_race_eth,
                        father_educ_cat4,
                        *ca_list,
                        *ip_list,
                        prior_ces_count,
                        fert_drugs,
                        art,
                        pre_preg_diab,
                        gest_diab,
                        nicu,
                        wtgain,
                        indl,
                        bfed,
                    ],
                    schema=out_schema,
                )

                if writer is None:
                    writer = pq.ParquetWriter(str(args.out), out_schema)
                writer.write_table(out_tbl)
    finally:
        if writer is not None:
            writer.close()

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

