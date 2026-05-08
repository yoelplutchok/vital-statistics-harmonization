# Comparability across years (1990–2024)

This document records comparability decisions for the harmonized U.S. natality microdata.

Canonical sources of truth:

- `metadata/variable_crosswalk_working.csv`: benchmark-year crosswalk evidence and field-level notes
- `metadata/harmonized_schema.csv`: per-variable provenance, derivation rules, and comparability class

## Guiding policy

- **Default analysis universe**: use **resident births** only (exclude foreign residents: `restatus == 4`). This matches NCHS “residence-based” tabulations used throughout validation.
- **Prefer deterministic transforms**: when a variable is “partial,” the pipeline provides an explicit derivation and labels the break/coverage issue rather than silently imputing.
- **When coverage differs by certificate revision**: use `certificate_revision` to define revision-consistent subsets.

## Comparability class definitions

- **full**: stable concept + coding across the full 1990–2024 range; trend-safe after documented sentinel handling.
- **partial**: usable across years, but has known breaks (coding changes, revision-coverage differences, or definitional series breaks). Trend work must follow the rules below.
- **within-era**: meaningful only within an era (e.g., 1990–2002 vs 2003–2013 vs 2014–2024, or revision-specific coding frames). Not trend-safe across eras.
- **excluded**: not shipped because the public-use files do not support a reliable harmonization.

## `certificate_revision` values

The harmonized `certificate_revision` column takes one of four values:

- `"unrevised_1989"` — all 1990–2002 records; 2003–2013 records inferred to be on the 1989 unrevised certificate (no `MEDUC`, `MRACEREC` populated).
- `"revised_2003"` — all 2014–2024 records; 2003–2013 records inferred to be on the 2003 revised certificate (`MEDUC` populated).
- `"unknown"` — 2003–2013 records where neither heuristic fires (both `MEDUC` and `MRACEREC` are null). Non-trivial: 2009 has 101,544 such rows (2.45 %); 2013 has 30,482 (0.77 %); other 2003–2013 years are smaller.
- `null` — only if the `year` column itself is null (should never occur).

**Rule**: analyses that use `certificate_revision == 'revised_2003'` as a filter silently drop the `"unknown"` bucket. For 2009–2013 revision-consistent subsets, consider whether to include or exclude `"unknown"` records explicitly.

## Known structural breaks / constraints

1. **1990–2002 → 2003 certificate transition**
   - The 2003 revised certificate introduced new field names, coding frames, and measurement methods. Fields like education changed from years-of-schooling (0–17) to categorical codes (1–8).
   - The harmonization maps 1990–2002 fields to the common schema via explicit crosswalks (e.g., `_dmeduc_years_to_cat4()`), but the underlying measurement differs.

2. **1990–2002 race bridge is approximate**
   - Official NCHS bridged race was introduced with the 2003 certificate. For 1990–2002, `maternal_race_bridged4` uses an **approximate** crosswalk from `MRACE` detail codes (01→White, 02→Black, 03→AIAN, 04-08/18-68→Asian/PI, 09+→null).
   - This is adequate for broad race-group tabulations but should not be treated as equivalent to the official NCHS bridged race available from 2003.

3. **2003 maternal age is a recode**
   - The 2003 public-use file suppresses single-year maternal age (all 99) and provides only `MAGER41` (41-category recode, values 01–41). The harmonization converts this to approximate single-year age via `code + 13` (so 02→15, …, 41→54), with code 01 mapping to 14 (bucket "<15"). MAGER41 values of 99 or >41 map to null. Note: the 2003 recode does **not** expose any ages ≥55; they are lost to null. Distinct single years 50, 51, 52, 53, 54 ARE present (from codes 37–41) — they are NOT collapsed to 50.

4. **1990–2002 smoking: independent source fields**
   - `smoking_any_during_pregnancy` comes from `TOBACCO` (yes/no/unknown) and `smoking_intensity_max_recode6` comes from `CIGAR6`. These are **independent** source fields, so ~429K records (428,755 verified) have smoker status with unknown intensity. From 2003 onward, `smoke_any` is derived from intensity, ensuring internal consistency.

5. **Gestation source breaks (three eras)**
   - 1990–2002: **LMP-only** (`DGESTAT`; source = `lmp`)
   - 2003–2013: **combined gestation** (`COMBGEST`; source = `combined`)
   - 2014–2024: **obstetric estimate** (`OEGEST_COMB`; source = `obstetric_estimate`)
   - Each transition changes the preterm rate level. Do not assume gestation-based outcomes are continuous across 2003 or 2014. Use `gestational_age_weeks_source` to identify or stratify.

6. **2009–2013 “U-only” fields are blank in the public-use files**
   - Empirically confirmed by scanning the raw zips: unrevised-only (“U”) fields such as `DMEDUC`, `MEDUC_REC`, `MPCB`, `TOBUSE`, `CIGS`, `CIG_REC6` are **entirely blank** in 2009–2013.
   - Consequence: **education, prenatal-care initiation, and smoking measures are effectively revised-only** in 2009–2013 and have substantial missingness for unrevised records.

7. **Race/ethnicity depends on bridged/imputed constructs**
   - Bridged race and Hispanic-origin recodes are broadly usable, but the bridging/editing context changes over time; cross-year race/ethnicity is treated as **partial**.
   - Starting 2020, NCHS no longer provides bridged race in the public-use natality file. `maternal_race_bridged4` is null for 2020–2024. However, `maternal_race_ethnicity_5` is now **reconstructed** from `MRACE6` detail codes for 2020+ (01→NH_white, 02→NH_black, 03→NH_aian, 04/05→NH_asian_pi). Multiracial births (MRACE6=06, ~3%) remain null because they cannot be bridged to a single race group. Use `race_bridge_method` to identify the derivation era.

8. **Marital status: California stopped reporting in 2017**
   - `marital_status` is blank (null) for ~11–12% of births starting 2017. This is exclusively from California, which ceased providing record-level marital status to NCHS due to state statutory restrictions.
   - The data is truly absent at the source: `DMAR`, `MAR_P` (paternity acknowledged), and `MAR_IMP` (imputed flag) are all blank for affected records. NCHS does not impute these values.
   - **Impact**: 0% missing 1990–2016; ~11–12% missing 2017–2024. Any trend analysis using `marital_status` across the 2017 boundary is affected.
   - **Use `marital_reporting_flag`** (derived from `F_MAR_P`, available 2014+) to distinguish non-reporting-state births (flag = false) from reporting-state births with genuine unknown status.
   - **Rule**: for Kitagawa decompositions or trend analyses, either (a) restrict to `marital_reporting_flag == true` for 2017+ years, (b) exclude `marital_status` from the model for windows spanning 2017, or (c) use only 2003–2016 for models that include marital status.

9. **Smoking missingness varies substantially across years**
   - `smoking_any_during_pregnancy` null rates range from 0.4% (2016+) to 44% (2009), driven by two mechanisms:
     - **2003–2008**: Item-level nonresponse (`CIG_REC6 = 6`, "not stated"), affecting 7–20% of births. Both revised and unrevised certificate records are affected.
     - **2009–2013**: Structural missingness for unrevised-certificate records. NCHS stopped carrying forward unrevised smoking data into the CIG fields, so unrevised records have 100% null smoking. As states adopted the revised certificate, the null rate fell from 44% (2009) to 14% (2013).
   - **2014+**: All states on revised certificate; null rate < 5% (2014) declining to < 0.5% (2016+).
   - **Rule**: for trend analyses using smoking, be aware that the "known-smoking" population changes substantially across years. Treating unknown as a Kitagawa stratum conflates measurement coverage with population composition.

## Variable decisions (summary)

### Full comparability (trend-safe 1990–2024)

- **Counts/universe**: `year`, `restatus`, `is_foreign_resident`, `certificate_revision`
- **Core demographics**: `live_birth_order_recode`, `total_birth_order_recode`
- **Infant/birth**: `plurality_recode`, `infant_sex`, `birthweight_grams`, `apgar5`
- **Derived from full variables**: `birthweight_grams_clean`, `apgar5_clean`, `low_birthweight`, `very_low_birthweight`, `singleton`, `maternal_age_cat`

### Partial comparability (usable with explicit rules)

- **Maternal age**
  - **Why partial**: 2003 uses `MAGER41` recode (41-category) converted to approximate single-year age. All other years have true single-year age.
  - **Rule**: the 2003 approximation is adequate for age-group analyses but not for precise single-year-of-age work.

- **Race/ethnicity**
  - **Primary construct**: `maternal_race_ethnicity_5` (derived from `maternal_hispanic` + `maternal_race_bridged4` or `maternal_race_detail`)
  - **Why partial**: three derivation methods across eras (see `race_bridge_method`): 1990–2002 uses approximate bridge from detail codes; 2003–2019 uses official NCHS bridged race; 2020–2024 reconstructs from MRACE6 detail codes (multiracial code 06, ~3% of births, maps to null).
  - **Rule**: treat as a consistent *high-level* series, but document that bridging method differs by era. Use `race_bridge_method` to identify derivation context. For 2020+, analyses excluding nulls will drop ~3% multiracial births.

- **Marital status**
  - **Primary construct**: `marital_status`
  - **Why partial**: California stopped reporting record-level marital status to NCHS in 2017. As a result, `marital_status` is null for ~11–12% of births from 2017 onward (0% null through 2016).
  - **Rule**: for trend analyses spanning 2017, either (a) use `marital_reporting_flag == true` to restrict to reporting-state births (available 2014+), (b) exclude `marital_status` from models that span the 2017 boundary, or (c) use 2003–2016 as the analysis window when marital status is needed.

- **Education**
  - **Primary construct**: `maternal_education_cat4`
  - **Why partial**: 1990–2002 uses years-of-schooling→cat4 crosswalk (conceptually different from category-based education); 2003+ uses revision-specific fields; 2009–2013 is revised-only.
  - **Rule**:
    - 1990–2002: `_dmeduc_years_to_cat4()` maps 0–11→lt_hs, 12→hs_grad, 13–15→some_college, 16–17→ba_plus, 99→null.
    - 2003–2008: combine revised `MEDUC` with unrevised `MEDUC_REC`.
    - 2009–2013: revised-only → use `certificate_revision == 'revised_2003'` for consistent analysis.

- **Prenatal care initiation**
  - **Primary constructs**: `prenatal_care_start_month`, `prenatal_care_start_trimester`
  - **Why partial**: 1990–2002 uses `MONPRE`; 2003+ uses revision-specific fields; 2009–2013 is revised-only.
  - **Rule**: same revised-only guidance as education for 2009–2013.

- **Smoking during pregnancy**
  - **Primary constructs**: `smoking_any_during_pregnancy`, `smoking_intensity_max_recode6`
  - **Why partial**: 1990–2002 derives `smoke_any` from `TOBACCO` and intensity from `CIGAR6` independently (~429K records with smoker+unknown intensity). 2003+ derives `smoke_any` from intensity. 2009–2013 is revised-only.
  - **Missingness varies substantially**: null rates range from <0.5% (2016+) to 44% (2009). Two mechanisms: (a) 2003–2008 item-level nonresponse (`CIG_REC6 = 6` "not stated", 7–20%); (b) 2009–2013 structural missingness for unrevised-certificate records (100% null on unrevised births, declining from 44% to 14% as states adopted the revised form).
  - **Rule**: for 1990–2002, expect some inconsistency between `smoke_any` and `smoke_intensity`. For 2003–2013, use `certificate_revision == 'revised_2003'` for consistent smoking data. For decomposition analyses, be aware that treating "smoking unknown" as a population stratum conflates measurement coverage with population composition.

- **Gestation + preterm**
  - **Primary constructs**: `gestational_age_weeks`, `preterm_recode3`, `preterm_lt37`, `very_preterm_lt32`
  - **Why partial**: three distinct measurement sources across eras (LMP, combined, obstetric estimate). Each transition changes the preterm rate level.
  - **Rule**: use `gestational_age_weeks_source` to stratify. Recommended gestation-era subsets:
    - 1990–2002: `gestational_age_weeks_source == 'lmp'`
    - 2003–2013: `gestational_age_weeks_source == 'combined'`
    - 2014–2024: `gestational_age_weeks_source == 'obstetric_estimate'`

- **Medical risk factors** (`diabetes_any`, `hypertension_chronic`, `hypertension_gestational`)
  - **Why partial**: 1990–2002 uses individual Y/N/unknown flags (`DIABETES`, `CHYPER`, `PHYPER`); 2003+ uses combined U/R flags (`URF_DIAB`, `URF_CHYPER`, `URF_PHYPER`). Coding is harmonized (1=yes, 2=no, 9=unknown) but underlying ascertainment changed with the certificate revision.
  - **Sentinel warning**: the value 9 (unknown) is not null and passes `IS NOT NULL` filters. Use the derived boolean versions (`diabetes_any_bool`, `hypertension_chronic_bool`, `hypertension_gestational_bool`) which map 9→null for correct complete-case analysis.

- **Delivery method**
  - **Primary construct**: `delivery_method_recode`
  - **Why partial**: two distinct coding frames with the boundary at **2005** (not 2003):
    - **1990–2004 (DELMETH5-style)**: 1=vaginal, 2=VBAC, 3=primary cesarean, 4=repeat cesarean, 9=not stated. In 2003–2004, the field is labeled "DMETH_REC" at position 401 but still uses DELMETH5 codes. The pipeline remaps the raw "not stated" sentinel (and rare codes 6/7, unknown-prior-CS variants) to `9` so the not-stated marker is identical across 1990–2004 and 2005+.
    - **2005+ (DMETH_REC)**: 1=vaginal, 2=cesarean, 9=not stated.
  - **Cesarean crosswalk**: for 1990–2004, cesarean = codes 3 + 4 among known (1–4). For 2005+, cesarean = code 2 among known (1–2). This crosswalk is validated against NVSR published cesarean rates for 1990–2024 (all within 0.07 pct-pts).
  - **Rule**: the cesarean/vaginal binary is comparable across the full 1990–2024 range via the crosswalk above. Finer categories (primary vs repeat cesarean, VBAC) are available only for 1990–2004.

- **Father's age** (`father_age`)
  - **Why partial**: 1990–2002 uses `DFAGE`; 2003+ uses various recodes/combined age fields. `99` → null.
  - **Rule**: usable for broad age-group analyses across all years.

- **Birth facility** (`birth_facility`)
  - **Why partial**: 1990–2002 uses `PLDEL@8`; 2003–2013 uses `UBFACIL@42` (same coding as PLDEL); 2014+ uses `BFACIL@32` (revised-certificate coding with more facility types). Coarse 4-category mapping (hospital, birth_center, clinic_other, home) is comparable across eras.
  - **Null-rate spike 2014–2015**: 2014 has 3.58% null (142,900 blank raw `BFACIL` bytes in `Nat2014us.zip`); 2015 has 1.74%. 2016+ is 0%. Falls below the 5 pct-pt threshold of `harmonized_missingness_breaks.csv` so it is not flagged there.

- **Attendant at birth** (`attendant_at_birth`)
  - **Why partial**: coding is harmonized (1=MD, 2=DO, 3=CNM, etc.) but underlying certification/reporting context changed with the 2003 certificate.

- **Prior cesarean** (`prior_cesarean`, `prior_cesarean_count`)
  - **Availability**: `RF_CESAR` (Y/N/U) and `RF_CESARN` (0–30 count) are revised-certificate-only fields. In the 2005–2013 layout they live at bytes 324 and 325–326; in the 2014+ layout at bytes 331 and 332–333. Both are null for 1990–2004 (those public-use layouts carry no Y/N/U prior-cesarean field). Coverage on the remaining years tracks revised-cert adoption: `prior_cesarean` is populated on 30.8% of rows in 2005, 77.1% in 2010, 90.2% in 2013, and ~96–100% from 2014+; `prior_cesarean_count` follows the same pattern but is slightly lower in every year because a few thousand rows per year have known `RF_CESAR` with blank `RF_CESARN` (for example, 30.69% vs 30.75% in 2005 and 90.15% vs 90.24% in 2013).
  - **Rule**: for 2005–2013, restrict to `certificate_revision == 'revised_2003'` (or drop nulls) for a revision-consistent subset; for 2014–2024, the field is populated on essentially every row. For a cross-era "any prior cesarean" signal before 2005, use `delivery_method_recode` codes 2/4 (VBAC / repeat-cesarean tracer for 1990–2004; no equivalent exists for 2005–2013 unrevised-cert public-use rows).

- **Father Hispanic origin** (`father_hispanic`)
  - **Why partial**: 1990–2002 uses `ORFATH`; 2003–2013 uses `UFHISP`; 2014+ uses `FHISP_R`. All use 0=non-Hispanic, 1–5=Hispanic coding, but reporting context and item non-response rates differ by era.

- **Father race/ethnicity** (`father_race_ethnicity_5`)
  - **Why partial**: three coding frames across eras:
    - **1990–2002** (`ORRACEF`): 1–5 → Hispanic subcategories; 6 → `NH_white`; 7 → `NH_black`; 8 → `NH_other`; 9 → null.
    - **2003–2013** (`FRACEHISP`, same frame as ORRACEF): same mapping as above — code 8 → `NH_other`, code 9 → null.
    - **2014+** (`FRACEHISP`, new frame): 1 → `NH_white`; 2 → `NH_black`; 3–6 → `NH_other` (NH AIAN, NH Asian, NH NHOPI, NH Multiracial all collapse here because paternal race detail is coarser than maternal); 7 → `Hispanic`; 8 → null (origin unknown); 9 → null (unknown).
  - **Allowed output labels** (same across all eras): `Hispanic`, `NH_white`, `NH_black`, `NH_other`, null. Note that `NH_other` is produced in all three eras — just from different source codes — which is a departure from `maternal_race_ethnicity_5`'s 5-label schema.

- **Father education** (`father_education_cat4`)
  - **Why partial**: 1990–1994 uses `DFEDUC` (years-of-schooling→cat4); 2009+ uses `FEDUC` (categorical codes→cat4). **Null for 1995–2008** (field dropped from public-use files). Partial coverage 2009–2010 (2003-revision early-adopter states only; ~58–65% non-null). Full coverage 2011+.

### Within-era only

- `maternal_race_detail` (1990–2002 MRACE detail codes vs 2003–2013 MRACE vs 2014+ MRACE6; not a single comparable series). Values are stored as 2-digit zero-padded strings across the full span (`'01'..'06'` for 2014+ MRACE6 and `'01'..'78'` for 1990–2013 MRACE). Note that the code frame itself still differs across eras — use `maternal_race_ethnicity_5` for cross-era trend work.
- `smoking_pre_pregnancy_recode6` (2014–2024 only; `CIG0_R`)
- `bmi_prepregnancy`, `bmi_prepregnancy_recode6` (2014–2024 only; NCHS positions 283-287. Null for all pre-2014 years.)
- `payment_source_recode` (2009–2024; partial coverage 2009–2010 from early-adopter states; near-full coverage 2011+; complete 2014+. Null for all pre-2009 years.)
- `fertility_enhancing_drugs` (2014–2024 only; `RF_FEDRG`. Note: high null rate because X="Not Applicable" → null.)
- `assisted_reproductive_tech` (2014–2024 only; `RF_ARTEC`.)
- `pre_pregnancy_diabetes` (2014–2024 only; `RF_PDIAB`. Finer-grained than `diabetes_any`.)
- `gestational_diabetes` (2014–2024 only; `RF_GDIAB`. Finer-grained than `diabetes_any`.)
- `nicu_admission` (2014–2024 only; `AB_NICU`.)
- `weight_gain_pounds` (2014–2024 only; `WTGAIN`. 0–97 = pounds, 99→null.)
- `induction_of_labor` (2014–2024 only; `LD_INDL`.)
- `breastfed_at_discharge` (2014–2024 only; `BFED`.)
- 12 congenital anomaly bools: `ca_anencephaly`, `ca_spina_bifida`, `ca_cchd`, `ca_cdh`, `ca_omphalocele`, `ca_gastroschisis`, `ca_limb_reduction`, `ca_cleft_lip`, `ca_cleft_palate`, `ca_down_syndrome`, `ca_chromosomal_disorder`, `ca_hypospadias` (2014–2024 only. `ca_down_syndrome` and `ca_chromosomal_disorder` use C/P/N/U coding where C=Confirmed and P=Pending both map to true.)
- 5 infection bools: `infection_gonorrhea`, `infection_syphilis`, `infection_chlamydia`, `infection_hep_b`, `infection_hep_c` (2014–2024 only.)

### Excluded

- `maternal_nativity`
  - **Reason**: `MBCNTRY` appears blank/suppressed in the 2005–2013 public-use files and `MBSTATE_REC` is a non-comparable 2014-only recode. Excluded rather than shipping a misleading within-era series.

## Recommended analytic subsets

- **Residents-only** (default): `is_foreign_resident == false`
- **Revision-consistent subset** (for education/prenatal care/smoking in 2009–2013): `certificate_revision == 'revised_2003'`
- **Gestation-era subsets**:
  - 1990–2002: `gestational_age_weeks_source == 'lmp'`
  - 2003–2013: `gestational_age_weeks_source == 'combined'`
  - 2014–2024: `gestational_age_weeks_source == 'obstetric_estimate'`

## V3 Linked birth-infant death comparability (2005–2023)

The V3 linked file shares all birth-side comparability constraints from V2 above. Additional death-side considerations:

### Death-side variables (full comparability within scope)

- **`infant_death`**: stable across all 19 years. FLGND coding differs (1/2 for 2005-2013; 1/blank for 2014-2023) but is normalized to a consistent boolean.
- **`age_at_death_days`**: comparable 2005-2018. **Minor break at 2019**: NCHS switched to calculating age at death from birth certificate time-of-birth (not death certificate). This improves sub-24-hour accuracy but means the `<1 hour` and `1 day` categories are not perfectly comparable with earlier years. Total neonatal/postneonatal splits are minimally affected.
- **`underlying_cause_icd10`**: ICD-10 throughout (2005-2023). Comparable, though coding rule updates occur periodically.
- **`cause_recode_130`**: NCHS 130-cause infant death recode. Consistent across the period.
- **`record_weight`**: populated for every row (survivors = `1.0`; deaths ≥ `1.0`). NCHS recommends **not** applying the weight for cohort analyses — use unweighted data. For 2016–2023 (period-cohort source format), survivor rows do not carry a weight field in the raw NCHS files; the pipeline explicitly fills `1.0` for survivors so the column is usable without `fill_null` guards.
  - **Known minor quirk**: there are exactly **2 survivor rows** (1 in 2014, 1 in 2015) where `record_weight` is null. These come from the upstream NCHS denominator-plus files (not introduced by the pipeline) and are plausible ordinary births. The `record_weight_null_when_survivor` invariant in `scripts/05_validate/validate_v1_invariants.py` will report these as 2 when run against the V3 Parquet (the V2 invariants report shows 0 only because V2 natality has no `record_weight` column; the invariant silently skips). The companion invariant `record_weight_null_when_death` (added 2026-04-22) reports 0 — no death has a null weight. If you need `record_weight` non-null for downstream analysis, filter with `record_weight.fill_null(1.0)` or drop those two rows explicitly.

### Linked vs natality row-count deltas

The V3 linked Parquet has slightly more rows than the V2 natality Parquet in a handful of years:

| Year | V2 natality rows | V3 linked rows | Δ |
|-----:|------:|------:|----:|
| 2005 | 4,145,619 | 4,145,887 | +268 |
| 2006 | 4,273,225 | 4,273,264 | +39 |
| 2008 | 4,255,156 | 4,255,188 | +32 |
| 2011 | 3,961,220 | 3,961,221 | +1 |
| 2012 | 3,960,796 | 3,960,797 | +1 |
| all other years | — | — | 0 |

These deltas come from NCHS's cohort-linked-file construction: the cohort denominator carries a handful of late-filed or amended birth records that were not in the originally-published annual natality file. The rows are valid births; the pipeline does not alter them. If you are joining V2 and V3 by birth-level key (not possible for the public-use files, which have no shared ID), expect a small residual from these deltas. For aggregate rates, the difference is ≤7 parts per 100,000 and below any NVSR comparison tolerance.

### V3 linked vs V2 natality: 2009–2010 unrevised-cert field retention

**The linked denominator-plus file for 2005–2013 retains three revised-only fields that the natality 2009–2010 public-use files drop.** Concretely, on 2009 and 2010 unrevised-certificate rows:

| Column | V2 natality non-null fraction | V3 linked non-null fraction |
|---|---:|---:|
| `maternal_education_cat4` (2009 unrev, 1.22 M rows) | 0.0 % | **99.2 %** (1,210,388 / 1,219,573) |
| `maternal_education_cat4` (2010 unrev, 807 k rows) | 0.0 % | **99.4 %** (802,508 / 807,008) |
| `prenatal_care_start_month` (2009 + 2010 unrev, 2.03 M rows) | 0.0 % | **100 %** |
| `smoking_intensity_max_recode6` (2009 + 2010 unrev, 2.03 M rows) | 0.0 % | **100 %** |

This is a **genuine upstream difference** in what NCHS retains in each file family — not a pipeline bug. The natality 2009–2010 public-use layout drops the unrevised-only `MEDUC_REC` / `MPCB` / `CIG_1-3` bytes; the linked denominator-plus layout retains them at positions the harmonizer can still read.

**Consequence.** If you need to analyze education, prenatal-care start, or smoking on the full 2009–2010 universe (revised + unrevised), use the V3 linked parquet — not the V2 natality one. Note however that V3's universe for those two years is still *births linked to infant-death files*, which includes all births regardless of death outcome but may have marginally different late-filed-record composition than V2 (see "Linked vs natality row-count deltas" above — ≤7 ppm). For 2011–2013 both V2 and V3 are null on unrevised rows (NCHS dropped the fields from the linked layout too starting 2011), matching the codebook entry for `maternal_education_cat4`.

**Validator treatment.** The `unrevised_2009_2013_has_educ`, `unrevised_2009_2013_has_pnmonth`, and `unrevised_2009_2013_has_smokeint` invariants are V2-only expectations. `scripts/05_validate/validate_v1_invariants.py` auto-detects V3 linked input by the presence of the `infant_death` column and skips those three invariants (they appear in the V3 report with a `_(skipped — V2-only, …)_` note). For V2 natality they remain hard-zero checks.

### V3 linked vs V2 natality: 2009–2010 fields blanked in linked-only

**The opposite asymmetry from above also exists**: two V2 fields with partial 2009–2010 coverage are 100% NULL in V3 linked for those two years, because the bytes are blank across the entire LinkCO denominator-plus zip:

| Column | V2 natality non-null fraction | V3 linked non-null fraction |
|---|---:|---:|
| `payment_source_recode` (2009, 4.14 M rows) | 66.74 % (PAY_REC@413 partially populated) | **0 %** (PAY_REC@413 blank in entire LinkCO09 file) |
| `payment_source_recode` (2010, 4.01 M rows) | 75.69 % | **0 %** (LinkCO10 blank) |
| `father_education_cat4` (2009, 4.14 M rows) | 57.71 % (FEDUC@197 partially populated) | **0 %** (FEDUC@197 blank in entire LinkCO09 file) |
| `father_education_cat4` (2010, 4.01 M rows) | 65.45 % | **0 %** (LinkCO10 blank) |

This is a **genuine upstream NCHS limitation** — verified by raw-byte probe of `LinkCO09US.zip` and `LinkCO10US.zip`: bytes 197 (FEDUC) and 413 (PAY_REC) are space across the first 200,000 records of each file. The 2011 LinkCO file contains data starting at ~3.4 % non-blank.

**Consequence.** If you need to analyze payment source or father's education on 2009–2010, use the V2 natality parquet — not the V3 linked one. V3 coverage matches V2 from 2011 onward.

### Linked vs natality birthweight: small systematic offset

Mean `birthweight_grams_clean` on the V3 linked birth-side runs ~0.6–0.9 g lower than on V2 natality in every year 2005–2023 (sign is constant; never positive). The corresponding LBW rate runs ~0.02–0.03 percentage points higher in V3. The bias stems from differences in how the linked denominator file lays out birth-side fields (see also the upstream NCHS denominator-plus / period-cohort layouts) — both V2 and V3 still pass every NCHS NVSR external target because the bias sits below NVSR rounding precision. **Recommendation**: for natality-rate comparisons (LBW, mean birthweight, etc.) prefer V2; use V3 only when the death linkage is required for the analysis. Do not pool V2 and V3 birth-side birthweight in the same trend without acknowledging the offset.

### Linked file format transition (2016)

The raw data format changed from denominator-plus (2005-2015) to period-cohort (2016-2023). This is handled transparently by the pipeline and does not affect the harmonized output schema.

### Bridged race dropped in 2020

Starting with 2020 data, NCHS no longer provides bridged race in the linked file. The `maternal_race_bridged4` field may have different coverage or derivation for 2020. For race/ethnicity trend work, consider using 2005-2019 or using `maternal_race_detail` / `maternal_race_ethnicity_5` with awareness of this change.

### Recommended linked analysis subsets

- **Residents-only** (default): `is_foreign_resident == false`
- **Consistent age-at-death**: 2005-2018 for sub-day age categories; 2005-2023 for neonatal/postneonatal
- **Consistent race/ethnicity**: 2005-2019 for bridged race; 2005-2023 for Hispanic origin

## Known pitfalls for multi-decade trend analyses

This section consolidates the most common traps for downstream users running analyses across multiple years. Each pitfall is documented in detail in the variable-specific sections above; this is a one-stop checklist.

### 1. Variables with structural null-rate breaks

These variables have sharp changes in null rates at specific year boundaries. A `WHERE variable IS NOT NULL` filter silently changes the composition of your analysis sample at these transitions.

| Variable | Break year(s) | Null rate change | Mechanism |
|----------|--------------|------------------|-----------|
| `marital_status` | 2017 | 0% → ~11–12% | California stopped reporting |
| `smoking_any_during_pregnancy` | 2009 | ~7% → ~44% | Unrevised-certificate records lost smoking data in public-use files |
| `smoking_any_during_pregnancy` | 2014 | ~14% → ~5% | All states on revised certificate |
| `maternal_education_cat4` | 2009 | ~0% → ~35% | Same mechanism as smoking (revised-only) |
| `maternal_race_ethnicity_5` | 2020 | ~0% → ~3% | Multiracial births (MRACE6=06) cannot be bridged; now reconstructed from detail codes |
| `maternal_race_bridged4` | 2020 | ~0% → 100% | NCHS dropped bridged race from public-use file |
| `father_age` | 2012, 2013 | 13% → 23% → 21% → 16% | 2012–2013: `UFAGECOMB@184-185` carries the harmonizer's raw single-year father age through 2011, but NCHS blanked it starting in 2012 while revised-cert rows carried `FAGECOMB@182-183`. `father_age` is therefore populated for revised-cert rows only in 2012–2013 (~77–79% populated after the 99→null cleanup). For categorical (5-year-bucket) father age that covers unrevised-cert 2012 rows too, use `father_age_cat_from_rec11` (derived from `FAGEREC11`). |
| `father_age_cat_from_rec11` | pre-2005, post-2013 | fully null outside 2005–2013 | FAGEREC11 recode is only in the 2005–2013 public-use layout. |
| `prior_cesarean` | 2005 onset, 2014 cert-migration completion | Pre-2005 100% null → 2005 ~69% null → 2014 ~4% null | `RF_CESAR` is a revised-certificate-only field: `RF_CESAR@324` for 2005–2013, `RF_CESAR@331` for 2014+. Coverage tracks the revised-cert adoption curve (30.8% of rows populated in 2005 → 90.2% in 2013 → 96%+ in 2014+). Null for 1990–2004 — those public-use layouts do not carry a Y/N/U prior-cesarean field at all. |
| `attendant_at_birth` | none | consistently ~0.1–0.2% null | Populated for all years 1990–2024. (Note: 2004 uses byte 408, not 410 as the adjacent 2005-record-length file might suggest — 2004 is layout-identical to 2003 for this field.) |
| `father_education_cat4` | 1995/2009 | 0% → 100% → ~40% | Field dropped 1995–2008; partially restored 2009+ |

**Rule**: before running any cross-year analysis, check the null-rate profile of every variable in your model using `output/validation/harmonized_missingness_by_year.csv`. Any null-rate jump > 5 percentage points between adjacent years is flagged in `harmonized_missingness_breaks.csv`.

### 2. Sentinel unknowns that pass `IS NOT NULL`

The raw harmonized fields `diabetes_any`, `hypertension_chronic`, and `hypertension_gestational` use integer coding (1=yes, 2=no, **9=unknown**). The sentinel value 9 is not null, so `WHERE diabetes_any IS NOT NULL` includes unknowns in the denominator.

**Fix**: use the derived boolean versions (`diabetes_any_bool`, `hypertension_chronic_bool`, `hypertension_gestational_bool`) which map 9→null. These are consistent with `smoking_any_during_pregnancy` (already boolean).

Similarly, `gestational_age_weeks` uses 99=unknown and `birthweight_grams` uses 9999=unknown. Use the `_clean` versions (`gestational_age_weeks_clean`, `birthweight_grams_clean`) which map sentinels to null.

### 3. Complete-case sample bias

When filtering on high-missingness variables, the "known" sample is not a random subset. Key examples:

- **Smoking 2009–2013**: only revised-certificate records have smoking data. Revised states in 2009 were disproportionately small, rural, and Western. Complete-case analyses of smoking in 2009 effectively exclude the largest states.
- **Marital status 2017+**: excluding California removes ~12% of U.S. births — a population with distinct demographic and health profiles (high Hispanic share, high cost-of-living urban centers).
- **Education 2009–2013**: same revised-only issue as smoking.

**Rule**: for models that span these periods, either (a) restrict to revision-consistent subsets (`certificate_revision == 'revised_2003'`), (b) exclude the affected variable, or (c) model the missingness explicitly.

### 4. Gestation source changes affect outcome levels

The preterm rate shifts at **2003** (LMP→combined) and **2014** (combined→obstetric estimate). These are not trend artifacts — the underlying measurement changed. A naïve time series of preterm rate will show level shifts at both transitions.

**Rule**: use `gestational_age_weeks_source` to stratify or restrict to a single era. Recommended windows: 1990–2002 (LMP), 2003–2013 (combined), 2014–2024 (obstetric estimate).

### 4a. 2003 single-year maternal age has a phantom spike at age 14

The 2003 public-use file suppresses single-year maternal age below 15 and exposes only the MAGER41 recode (code 01 = "Under 15 years"). The harmonizer maps code 01 → age=14 and codes 02–41 → age N+13. As a result, in 2003 every birth to a mother under 15 is coded as maternal_age=14 exactly; ages 10–13 are all zero. Aggregate bucketed analyses (`maternal_age_cat`, `<15` row of NVSR Table 1) are correct; **single-year-age analyses** will see a spurious peak at age=14 and a hole at ages 10–13 for 2003.

**Rule**: for cross-year single-year-age comparisons that include 2003, use `maternal_age_cat` (buckets `<20`, `20–24`, …) or restrict to `maternal_age >= 15`. Do not use age=14 as a single-year comparison point across 2003.

### 4b. Pre-2005 prior_cesarean has no Y/N/U source in the public-use file

`prior_cesarean` and `prior_cesarean_count` are null for **1990–2004** because those public-use layouts have no `RF_CESAR` / `RF_CESARN` field at all. From **2005–2013**, both columns are available only on revised-cert rows; from **2014+**, both are near-complete. For 1990–2004, the `delivery_method_recode` codes `2` (VBAC) and `4` (repeat CS) are the closest tracer; once the delivery-method coding changes at 2005, there is no single-series substitute for the unrevised-cert rows in 2005–2013.

**Rule**: any "prior cesarean rate over time" plot that spans the 2005 boundary must either (a) treat 2005–2013 as a revised-cert-only subset via `certificate_revision == 'revised_2003'`, (b) state the 2005–2013 coverage break explicitly, or (c) use `delivery_method_recode` tracer codes only for the 1990–2004 segment and leave the unrevised-cert gap in 2005–2013 explicit.

### 5. Recommended model specifications by time window

| Window | Safe variables | Variables to exclude or handle with care |
|--------|---------------|------------------------------------------|
| 1990–2024 (full) | birthweight, plurality, sex, maternal age (approx for 2003) | gestation (3 eras), education (3 eras + gap), smoking (2 sources + gap), marital (2017 break), race (3 bridge methods) |
| 2003–2016 | All partial variables (revision-consistent subset: `certificate_revision == 'revised_2003'`) | Pre-2003 variables use different definitions |
| 2014–2024 | All variables including within-era (BMI, congenital anomalies, infections, payment source) | marital (2017 break), race_bridged4 (2020 drop) |
| 2003–2013 | Gestation (combined source), education, smoking (on revised subset) | Unrevised-certificate records have gaps |

## Change log

- 2026-03-19 (Session 13): Finalized benchmark-year crosswalk decisions for key V1 domains; documented 2009–2013 public-use blanking of U-only fields; excluded nativity; defined revision-consistent analysis guidance.
- 2026-03-19 (Session 16): Expanded to 1990–2020 scope. Added 1990–2002 era breaks (certificate transition, approximate race bridge, LMP gestation, independent smoking fields, years-based education, MAGER41 recode for 2003). Updated gestation era guidance to three eras.
- 2026-03-23 (Session 18): Added V3 linked birth-infant death comparability section (2005-2020). Documented age-at-death 2019 break, bridged race 2020 change, record weight guidance.
- 2026-03-24 (Session 19): Extended year range from 1990-2020 to 1990-2023. Added BMI within-era entry (2014-2024).
- 2026-03-26 (Session 20): Added 5 new harmonized variables: father_age, birth_facility, attendant_at_birth, payment_source_recode, prior_cesarean.
- 2026-03-27 (Session 21): Added 23 new harmonized variables: father_hispanic, father_race_ethnicity_5, father_education_cat4, 12 congenital anomaly bools, 5 infection bools, prior_cesarean_count, fertility_enhancing_drugs, assisted_reproductive_tech. Extended payment_source_recode to 2009+. Classified new variables as partial (paternal demographics) or within-era (2014+ clinical fields).
- 2026-03-29 (Session 23): Rewrote delivery method section with validated cesarean crosswalk. Documented that 2003–2004 files store DELMETH5-style codes at the DMETH_REC position (boundary at 2005, not 2003). Cesarean binary (codes 3+4 pre-2005, code 2 post-2005) validated against NVSR published rates 1990–2024.
- 2026-03-30 (Session 24): Seven improvements from LBW-IMR divergence lessons learned: (1) added `marital_reporting_flag` from F_MAR_P (2014+); (2) added unified missingness diagnostics script; (3) reconstructed `maternal_race_ethnicity_5` for 2020-2024 from MRACE6 detail codes, added `race_bridge_method`; (4) added derived nullable booleans for diabetes/HTN (sentinel 9→null); (5) added "Known pitfalls for multi-decade trend analyses" section; (6) added null-rate discontinuity detection to invariants validator; (7) added parquet versioning with SHA-256 provenance.
- 2026-04-22: Field-position + parser-completeness corrections from a byte-level audit pass.
  - **2004 `attendant_at_birth`**: the prior release read `ATTEND` at byte 410 (2005's position). Correct position is byte 408 (same as 2003). Fix restored 4,118,907 rows from 100% null to ~0.22% null — matches 2003/2005 exactly.
  - **2012–2013 `father_age`**: by 2012, NCHS had blanked the public-use `UFAGECOMB@184-185` field while revised-cert rows carried `FAGECOMB@182-183`. The parser now reads both and prefers `FAGECOMB` when non-null. Fix restored ~3.1M rows for 2013; as a side effect, 2012 revised-cert rows also gained `FAGECOMB@182-183` coverage that was previously null.
  - **`prior_cesarean` 2005–2013**: `RF_CESAR@324` and `RF_CESARN@325-326` are revised-certificate fields first present in 2005 and populated only on revised-cert rows. They were previously not parsed pre-2014, leaving `prior_cesarean` and `prior_cesarean_count` null for all 2005–2013 rows. Now populated on revised-cert rows across 2005–2013 (30.8% → 90.2% coverage, tracking cert adoption).
  - **2016+ diabetes / hypertension source**: the `URF_DIAB`/`URF_CHYPER`/`URF_PHYPER` tail block at bytes 1331–1333 exists only in the 2014–2015 User Guides; bytes 571–1330 are `FILLER_X` in 2016+. The harmonizer now selects source fields per-year rather than per-batch: 1990–2002 → `DIABETES`/`CHYPER`/`PHYPER`; 2003–2015 → `URF_*` (which really are at 1331–1333 for 2014–2015); 2016+ → `RF_PDIAB`/`RF_GDIAB`/`RF_PHYPE`/`RF_GHYPE` at bytes 313–316.
  - **Linked cohort merge**: 2016–2023 period-cohort files are merged on the NCHS-documented composite key `(CO_SEQNUM, CO_YOD)` rather than CO_SEQNUM alone, with an explicit assertion that same-year and next-year numerator keysets are disjoint.
  - **New columns**: `father_age_cat_from_rec11` (categorical 5-year-bucket father age derived from `FAGEREC11`, populated 2005–2013) and `maternal_race_detail_15cat` (MRACE15 15-category mother's race, populated 2014+).
  - **V3 linked schema** now mirrors V2 exactly (78 harmonized + 16 derived = 94, up from 76 + 16 = 92 in the prior release).
  - **Validator hygiene**: 13 raw `pc.and_` sites in the invariants validator wrapped with `_safe_and` to prevent a null year or null cert_rev from silently suppressing violation counts. Neonatal/postneonatal booleans made three-valued: `False` for survivors, `True`/`False` for deaths with known age, `null` for deaths with unknown age (currently none).
  - Net pipeline effect: ~49 million row-variable cells newly populated across the 2004–2013 window. All 41 internal invariants still pass with zero violations on V2 natality (V3 linked: 38 pass clean + 1 within a documented exception budget of 2 + 3 V2-only invariants skipped); V2 183/183 and V3 linked 35/35 external targets still pass.
