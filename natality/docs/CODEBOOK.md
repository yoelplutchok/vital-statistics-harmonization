# Codebook

This codebook is derived conceptually from `metadata/harmonized_schema.csv`. The CSV is the **canonical** machine-readable source of truth.

## Harmonized variables (1990–2024)

> **v3.0.0 scope note.** As of natality **v3.0.0** the product spans **1968–2024** (57 years; 201,161,456 records — see `ABOUT_THIS_RELEASE.md`). The per-variable availability/comparability rows below currently document the **1990–2024** era; the schema is identical (71 harmonized + 13 derived) and the 1990–2024 slice is byte-identical to v2.8. The pre-1990 (1968–1989) per-variable codebook extension (per-era availability, sentinel/coding differences, conservative-null fields) is **now provided** in the auto-generated **Appendix C8.20 — Per-variable historical evidence** at the end of this file — covering the full **1968–2024** natality envelope **+ the linked-v4 1983–2023 death-side**, every count derived from the gate-verified parquet by `scripts/_build_codebook_extensions.py` (deterministic; regenerate to reproduce byte-identically). The hand-authored per-variable rows below still document the **1990–2024** slice (the full-body re-paragraph is a tracked Phase-D doc-sync deferral); the appendix is the source of the pre-1990 + linked-cohort per-era evidence.

This is the current harmonized schema implemented by:

- `scripts/03_harmonize/harmonize_v1_core.py`
- `scripts/04_derive/derive_v1_core.py` (derived columns)

For full per-variable provenance, see `metadata/harmonized_schema.csv`.

### Record layout eras

| Era | Years | Record length | Certificate | Key differences |
|-----|-------|--------------|-------------|-----------------|
| Pre-2003 | 1990–2002 | 350 bytes | Unrevised 1989 | Different field names (DMAGE, CSEX, DBIRWT, etc.); education in years; individual medical risk flags; LMP-only gestation |
| Transition | 2003–2013 | 1350/1500/775 bytes | Dual (unrevised + revised) | Parallel fields; 2003 uses MAGER41 recode instead of single-year age; 2009–2013 blanks key unrevised fields |
| Revised-only | 2014–2024 | 1345 bytes | Revised 2003 | Obstetric estimate gestation; CIG_R recodes; unified risk factor flags |

### Harmonized columns

| harmonized_name | label | type | years | comparability | notes |
|---|---|---|---|---|---|
| `data_year` | Birth year | int16 | 1990–2024 | full | |
| `residence_status` | Resident status (NCHS) | int8 | 1990–2024 | full | Exclude `residence_status=4` to match NCHS residence-based totals |
| `is_foreign_resident` | Foreign-resident indicator | bool | 1990–2024 | full | `residence_status == 4` |
| `certificate_revision` | Certificate revision (1989 vs 2003) | string | 1990–2024 | full | `unrevised_1989` (1990–2013), `revised_2003` (2003–2024), `unknown` (2007–2013 when indeterminate) |
| `maternal_age` | Mother's age (single years) | int16 | 1990–2024 | partial | 1990–2002: `DMAGE`; 2003: approximate from `MAGER41` recode; 2004+: `MAGER` |
| `live_birth_order_recode` | Live birth order recode | int8 | 1990–2024 | full | 1990–2002: `LIVORD9`; 2003+: `LBO_REC` |
| `total_birth_order_recode` | Total birth order recode | int8 | 1990–2024 | full | 1990–2002: `TOTORD9`; 2003+: `TBO_REC` |
| `marital_status` | Marital status | int8 | 1990–2024 | partial | `DMAR` (1990–2002) vs `MAR` (2003–2013) vs `DMAR` (2014+). **California stopped reporting in 2017: ~11–12% null from 2017+.** Use `marital_reporting_flag` (2014+) to filter to reporting states. |
| `marital_reporting_flag` | Marital status reporting flag | bool | 2014–2024 | partial | Derived from `F_MAR_P`. True = state reports marital status; False = non-reporting state (California from 2017+). Null for all pre-2014 years. |
| `hispanic_origin` | Mother's Hispanic origin recode | int8 | 1990–2024 | partial | 1990–2002: `ORMOTH`; 2003–2013: `UMHISP`; 2014+: `MHISP_R` |
| `maternal_hispanic` | Maternal Hispanic indicator | bool | 1990–2024 | partial | Derived from `hispanic_origin` |
| `maternal_race_bridged` | Mother's bridged race (4 categories) | int8 | 1990–2019 | partial | 1990–2002: **approximate** bridge from `MRACE` detail codes; 2003–2019: official `MRACEREC`/`MBRACE`. **100% null for 2020–2024** — NCHS discontinued the bridged-race recode in the public-use file. Use `maternal_race_ethnicity_5` for 2020+ (reconstructed from MRACE6 detail codes). |
| `maternal_race_ethnicity_5` | Maternal race/ethnicity (NH race + Hispanic) | string | 1990–2024 | partial | Derived from Hispanic + bridged race (2003–2019) or MRACE6 detail (2020+). Multiracial (MRACE6=06, ~3%) → null for 2020+. |
| `maternal_race_detail` | Mother's race (detail code as reported) | string | 1990–2024 | within-era | 1990–2002: `MRACE` (1–78); 2003–2013: `MRACE` (primary field for both revisions; historical multiracial births in revised-cert states are rolled into code 78 / "not stated" in public-use); 2014+: `MRACE6` (1–6). Code frame differs across eras. |
| `maternal_race_detail_15cat` | Mother's race (15-category detail) | string | 2014–2024 | within-era | `MRACE15@108–109`. Values `01`–`15` (15=multiracial); NCHS `99` "unknown" sentinel is normalized to null by the harmonizer so the output frame is `{01..15} ∪ null`. The 15-category recode is only in the 2014+ public-use layout. Null for 1990–2013 (the bytes at positions 108–109 in pre-2014 files carry other data — the 2-letter alpha content at those positions in 2003/2004 raw records is NOT MRACE15 and was removed from the parse spec in the 2026-04-22 fix). |
| `race_bridge_method` | Race bridge derivation method | string | 1990–2024 | partial | `approximate_pre2003` (1990–2002), `nchs_bridged` (2003–2019), `approximate_from_detail` (2020–2024). |
| `maternal_education_cat4` | Maternal education (4-category) | string | 1990–2024 | partial | 1990–2002: years-of-schooling→cat4 crosswalk; 2003–2008: revised `MEDUC` + unrevised `MEDUC_REC`; 2009–2013: revised-only in V2 natality; 2014+: `MEDUC`. **V3 linked exception**: 2009/2010 unrevised-cert rows are populated on V3 linked (linked denominator-plus retains `MEDUC_REC`). See `docs/COMPARABILITY.md` §"V3 linked vs V2 natality: 2009–2010 unrevised-cert field retention". |
| `prenatal_care_start_month` | Month prenatal care began | int16 | 1990–2024 | partial | 1990–2002: `MONPRE`; 2003–2008: `PRECARE`+`MPCB`; 2009–2013: revised-only in V2 natality; 2014+: `PRECARE`. **V3 linked exception**: 2009/2010 unrevised-cert rows are populated on V3 linked. See `docs/COMPARABILITY.md` §"V3 linked vs V2 natality: 2009–2010 unrevised-cert field retention". |
| `prenatal_care_start_trimester` | Prenatal care start trimester | string | 1990–2024 | partial | Derived from start month |
| `prenatal_visits` | Number of prenatal visits | int16 | 1990–2024 | partial | 1990–2002: `NPREVIS`; 2003–2013: `UPREVIS`; 2014+: `PREVIS` |
| `smoking_any_during_pregnancy` | Any smoking during pregnancy | bool | 1990–2024 | partial | 1990–2002: from `TOBACCO` (independent of intensity); 2003+: derived from intensity recode |
| `smoking_intensity_max_recode6` | Max smoking intensity during pregnancy (recode6) | int8 | 1990–2024 | partial | 1990–2002: `CIGAR6`; 2003–2013: `CIG_REC6` + trimester counts (revised-only in V2 natality 2009–2013); 2014+: `CIG1_R`/`CIG2_R`/`CIG3_R`. **V3 linked exception**: 2009/2010 unrevised-cert rows are populated on V3 linked. See `docs/COMPARABILITY.md` §"V3 linked vs V2 natality: 2009–2010 unrevised-cert field retention". |
| `smoking_pre_pregnancy_recode6` | Smoking before pregnancy (recode6) | int8 | 2014–2024 | within-era | `CIG0_R`; not available before 2014 |
| `diabetes_any` | Diabetes (any type) | int8 | 1990–2024 | partial | 1990–2002: `DIABETES` (1=yes/2=no/9=unknown); 2003–2015: `URF_DIAB@331`; 2016–2024: derived from `RF_PDIAB@313` OR `RF_GDIAB@314` (URF_* is filler in 2016+ public-use files). 1=yes, 2=no, 9 or null=unknown. |
| `hypertension_chronic` | Chronic hypertension | int8 | 1990–2024 | partial | 1990–2002: `CHYPER`; 2003–2015: `URF_CHYPER@335`; 2016–2024: from `RF_PHYPE@315`. |
| `hypertension_gestational` | Pregnancy-associated hypertension | int8 | 1990–2024 | partial | 1990–2002: `PHYPER`; 2003–2015: `URF_PHYPER@336`; 2016–2024: from `RF_GHYPE@316`. |
| `plurality_recode` | Plurality recode | int8 | 1990–2024 | full | `DPLURAL` |
| `infant_sex` | Infant sex | string | 1990–2024 | full | 1990–2002: `CSEX` (1→"M", 2→"F"); 2003+: `SEX` |
| `gestational_age_weeks` | Gestational age (weeks) best available | int16 | 1990–2024 | partial | 1990–2002: `DGESTAT` (LMP); 2003–2013: `COMBGEST`; 2014+: `OEGEST_COMB` |
| `gestational_age_weeks_source` | Gestation source used | string | 1990–2024 | partial | `lmp` (1990–2002), `combined` (2003–2013), `obstetric_estimate` (2014+) |
| `preterm_recode3` | Preterm recode 3 best available | int8 | 1990–2024 | partial | 1990–2002: `GESTAT3`; 2003–2013: `GESTREC3`; 2014+: `OEGEST_R3` |
| `birthweight_grams` | Birthweight (grams) | int32 | 1990–2024 | full | 1990–2002: `DBIRWT`; 2003+: `DBWT`. `9999` = not stated |
| `delivery_method_recode` | Delivery method recode | int8 | 1990–2024 | partial | 1990–2004: `DELMETH5` codes (1=vaginal, 2=VBAC, 3=primary CS, 4=repeat CS, 5→9); 2005+: `DMETH_REC` (1=vaginal, 2=cesarean, 9=not stated). Cesarean binary (codes 3+4 pre-2005, code 2 post-2005) validated against NVSR rates 1990–2024 |
| `apgar5` | Five-minute Apgar score | int16 | 1990–2024 | full | 1990–2002: `FMAPS`; 2003+: `APGAR5`. `99` = not stated |
| `bmi_prepregnancy` | Pre-pregnancy BMI (continuous) | float32 | 2014–2024 | within-era | `99.9` → null sentinel. Not available before 2014 |
| `bmi_prepregnancy_recode6` | Pre-pregnancy BMI 6-category recode | int8 | 2014–2024 | within-era | 1=Underweight (<18.5); 2=Normal (18.5–24.9); 3=Overweight (25.0–29.9); 4=Obesity I (30.0–34.9); 5=Obesity II (35.0–39.9); 6=Extreme obesity III (40.0+). `9` → null sentinel. Not available before 2014 |
| `father_age` | Father's age (single years) | int16 | 1990–2024 | partial | 1990–2002: `DFAGE@154–155`; 2003–2011: `UFAGECOMB@184–185` (with `FAGECOMB@182–183` available on revised-cert rows 2006–2011 and used interchangeably — the two agree 100% in overlap); 2012: **`UFAGECOMB` blank**, harmonizer falls back to `FAGECOMB@182–183` on revised-cert rows (~77% population; ~23% null on unrevised-cert rows — for categorical coverage of those use `father_age_cat_from_rec11`); 2013: `FAGECOMB@182–183` (~90% population); 2014+: `FAGECOMB@147–148`. `99` → null; range-clipped to 9–98. |
| `father_age_cat_from_rec11` | Father age category (from FAGEREC11 recode) | string | 2005–2013 | within-era | `FAGEREC11@186–187` mapped to `<20` / `20-24` / `25-29` / `30-34` / `35-39` / `40+`. Recovers categorical father age for 2012 where raw single-year age is blank. Null for 1990–2002 and 2014+. |
| `birth_facility` | Birth facility type | string | 1990–2024 | partial | 1990–2002: `PLDEL@8`; 2003–2013: `UBFACIL@42`; 2014+: `BFACIL@32`. Values: `hospital`, `birth_center`, `clinic_other`, `home` |
| `attendant_at_birth` | Attendant at birth | int8 | 1990–2024 | partial | 1990–2002: `BIRATTND@10`; 2003: `ATTEND@408`; 2004: `ATTEND@408` (layout identical to 2003, not 2005 — despite the file's record length matching 2005); 2005–2013: `ATTEND@410`; 2014+: `ATTEND@433`. Values: 1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other; `9` → null. |
| `payment_source_recode` | Payment source recode | int8 | 2009–2024 | within-era | `PAY_REC`: 1=Medicaid, 2=Private, 3=Self-pay, 4=Other, 9→null. Available 2009+ (partial coverage 2009–2010 from 2003-revision states); full coverage 2014+. Null for 2005–2008 and 1990–2004 |
| `prior_cesarean` | Prior cesarean delivery | bool | 2005–2024 (partial 2005–2013) | partial | `RF_CESAR@324` for 2005–2013, `RF_CESAR@331` for 2014+. A revised-certificate field: populated only on revised-cert rows for 2005–2013 (coverage tracks cert adoption: 30.76% in 2005 → 90.24% in 2013); essentially complete (96%+) from 2014 on. Null for 1990–2004 — those public-use layouts do not carry a Y/N/U prior-cesarean field at all. For a 1990–2004 prior-cesarean tracer use `delivery_method_recode` codes 2 (VBAC) and 4 (repeat CS). Y→true, N→false, U/blank→null. |
| `father_hispanic` | Father Hispanic indicator | bool | 1990–2024 | partial | 1990–2002: `ORFATH`; 2003–2013: `UFHISP`; 2014+: `FHISP_R`. 0→false, 1–5→true, 9→null |
| `father_race_ethnicity_5` | Father race/ethnicity (5-category) | string | 1990–2024 | partial | 1990–2002: `ORRACEF`; 2003–2013: `FRACEHISP` (same codes as ORRACEF); 2014+: `FRACEHISP` (different coding: 1-6=NH race groups, 7=Hispanic). Values: `Hispanic`, `NH_white`, `NH_black`, `NH_other`, null. **Naming caveat**: the paternal version of this field effectively has only 4 non-null labels (no `NH_aian`/`NH_asian_pi`) because the source paternal detail is coarser than the maternal detail — NH AIAN, NH Asian, NH NHOPI, and NH Multiracial (2014+ FRACEHISP codes 3-6) all collapse to `NH_other`. The `_5` suffix mirrors `maternal_race_ethnicity_5`'s schema but should not be read as "paternal data resolves to 5 categories". |
| `father_education_cat4` | Father education (4-category) | string | 1990–1994, 2009–2024 | partial | 1990–1994: `DFEDUC` (years→cat4); 2009+: `FEDUC` (codes 1–8→cat4). **Null 1995–2008** (field dropped from public-use). Partial coverage 2009–2010 (2003-revision states only). Values: `lt_hs`, `hs_grad`, `some_college`, `ba_plus` |
| `ca_anencephaly` | Congenital anomaly: anencephaly | bool | 2014–2024 | within-era | `CA_ANEN`: Y→true, N→false, U/blank→null |
| `ca_spina_bifida` | Congenital anomaly: spina bifida | bool | 2014–2024 | within-era | `CA_MNSB`: Y→true, N→false, U/blank→null |
| `ca_cchd` | Congenital anomaly: cyanotic congenital heart disease | bool | 2014–2024 | within-era | `CA_CCHD`: Y→true, N→false, U/blank→null |
| `ca_cdh` | Congenital anomaly: congenital diaphragmatic hernia | bool | 2014–2024 | within-era | `CA_CDH`: Y→true, N→false, U/blank→null |
| `ca_omphalocele` | Congenital anomaly: omphalocele | bool | 2014–2024 | within-era | `CA_OMPH`: Y→true, N→false, U/blank→null |
| `ca_gastroschisis` | Congenital anomaly: gastroschisis | bool | 2014–2024 | within-era | `CA_GAST`: Y→true, N→false, U/blank→null |
| `ca_limb_reduction` | Congenital anomaly: limb reduction defect | bool | 2014–2024 | within-era | `CA_LIMB`: Y→true, N→false, U/blank→null |
| `ca_cleft_lip` | Congenital anomaly: cleft lip with/without cleft palate | bool | 2014–2024 | within-era | `CA_CLEFT`: Y→true, N→false, U/blank→null |
| `ca_cleft_palate` | Congenital anomaly: cleft palate alone | bool | 2014–2024 | within-era | `CA_CLPAL`: Y→true, N→false, U/blank→null |
| `ca_down_syndrome` | Congenital anomaly: Down syndrome | bool | 2014–2024 | within-era | `CA_DOWN`: C/P→true, N→false, U/blank→null (C=Confirmed, P=Pending) |
| `ca_chromosomal_disorder` | Congenital anomaly: suspected chromosomal disorder | bool | 2014–2024 | within-era | `CA_DISOR`: C/P→true, N→false, U/blank→null (C=Confirmed, P=Pending) |
| `ca_hypospadias` | Congenital anomaly: hypospadias | bool | 2014–2024 | within-era | `CA_HYPO`: Y→true, N→false, U/blank→null |
| `infection_gonorrhea` | Infection present: gonorrhea | bool | 2014–2024 | within-era | `IP_GON`: Y→true, N→false, U/blank→null |
| `infection_syphilis` | Infection present: syphilis | bool | 2014–2024 | within-era | `IP_SYPH`: Y→true, N→false, U/blank→null |
| `infection_chlamydia` | Infection present: chlamydia | bool | 2014–2024 | within-era | `IP_CHLAM`: Y→true, N→false, U/blank→null |
| `infection_hep_b` | Infection present: hepatitis B | bool | 2014–2024 | within-era | `IP_HEPB`: Y→true, N→false, U/blank→null |
| `infection_hep_c` | Infection present: hepatitis C | bool | 2014–2024 | within-era | `IP_HEPC`: Y→true, N→false, U/blank→null |
| `prior_cesarean_count` | Number of prior cesarean deliveries | int8 | 2005–2024 | partial | 2005–2013: `RF_CESARN@325-326` (revised-cert only; 30.7% populated in 2005 ramping to 90.2% in 2013 with cert adoption); 2014–2024: `RF_CESARN@332-333` (~96–100% coverage). 0–30 = count, 99→null. Null for 1990–2004. Follows the same revised-cert-only pattern as `prior_cesarean`, but with slightly lower coverage because some rows have `RF_CESAR` present while `RF_CESARN` is blank. |
| `fertility_enhancing_drugs` | Fertility-enhancing drugs used | bool | 2014–2024 | within-era | `RF_FEDRG`: Y→true, N→false, X(not applicable)/U→null. High null rate expected (X is the dominant code for births without fertility treatment) |
| `assisted_reproductive_tech` | Assisted reproductive technology used | bool | 2014–2024 | within-era | `RF_ARTEC`: Y→true, N→false, U/blank→null. High null rate expected (see `fertility_enhancing_drugs` note) |
| `pre_pregnancy_diabetes` | Pre-pregnancy diabetes | bool | 2014–2024 | within-era | `RF_PDIAB`: Y→true, N→false, U/blank→null. Finer-grained than `diabetes_any`; distinguishes pre-existing from gestational |
| `gestational_diabetes` | Gestational diabetes | bool | 2014–2024 | within-era | `RF_GDIAB`: Y→true, N→false, U/blank→null. Finer-grained than `diabetes_any` |
| `nicu_admission` | NICU admission | bool | 2014–2024 | within-era | `AB_NICU`: Y→true, N→false, U/blank→null |
| `weight_gain_pounds` | Weight gain during pregnancy (pounds) | int16 | 2014–2024 | within-era | `WTGAIN`: 0–97 = pounds, 99→null. Not available before 2014 |
| `induction_of_labor` | Induction of labor | bool | 2014–2024 | within-era | `LD_INDL`: Y→true, N→false, U/blank→null |
| `breastfed_at_discharge` | Breastfed at discharge | bool | 2014–2024 | within-era | `BFED`: Y→true, N→false, U/blank→null |

### Derived columns (added by `derive_v1_core.py`)

| derived_name | label | type | definition |
|---|---|---|---|
| `gestational_age_weeks_clean` | Gestation (weeks), sentinel-cleaned | int16 | `gestational_age_weeks` with 99→null |
| `birthweight_grams_clean` | Birthweight (grams), sentinel-cleaned | int32 | `birthweight_grams` with 9999→null |
| `apgar5_clean` | Five-minute Apgar, sentinel-cleaned | int16 | `apgar5` with 99→null |
| `low_birthweight` | Low birthweight (<2500g) | bool | `birthweight_grams_clean < 2500` |
| `very_low_birthweight` | Very low birthweight (<1500g) | bool | `birthweight_grams_clean < 1500` |
| `preterm_lt37` | Preterm (<37 weeks) | bool | `gestational_age_weeks_clean < 37` |
| `very_preterm_lt32` | Very preterm (<32 weeks) | bool | `gestational_age_weeks_clean < 32` |
| `singleton` | Singleton birth | bool | `plurality_recode == 1` |
| `maternal_age_cat` | Maternal age category | string | `<20`, `20-24`, `25-29`, `30-34`, `35-39`, `40+` |
| `father_age_cat` | Father age category | string | `<20`, `20-24`, `25-29`, `30-34`, `35-39`, `40+` |
| `diabetes_any_bool` | Diabetes (nullable boolean) | bool | `diabetes_any`: 1→true, 2→false, 9→null. Preferred for downstream analysis — sentinel 9 no longer passes `IS NOT NULL` |
| `hypertension_chronic_bool` | Chronic hypertension (nullable boolean) | bool | `hypertension_chronic`: 1→true, 2→false, 9→null |
| `hypertension_gestational_bool` | Gestational hypertension (nullable boolean) | bool | `hypertension_gestational`: 1→true, 2→false, 9→null |

## V3/v4: Linked birth-infant death variables (1983–2023; permanent 1992–1994 gap)

The linked harmonized file (`output/harmonized/natality_v3_linked_harmonized.parquet`; filename keeps the `v3` schema-family tag at linked **v4.0.0**) contains all the natality harmonized columns above, plus death-side columns from the NCHS cohort linked birth-infant death files. Coverage is **1983–2023** with a **permanent 1992–1994 NCHS-linkage gap** (NCHS suspended ALL birth-infant-death linkage for those three cohorts; `harmonized_schema.csv` `years_available` reads `"1983-2023 (linked; 1992-1994 gap)"`). For 1989+ there is one row per birth with death fields populated for infant deaths and null for survivors. **For the keyless 1983–1988 cohort era** the file is a two-file denominator/numerator pair tagged by `link_segment` (no per-record link key): compute infant mortality as `count(link_segment=='num') / count(link_segment=='den')` per stratum, NOT a per-birth `infant_death` filter. **For 1983–1984** apply `record_weight` (a documented 50%-non-VSCP weighted sample; weighted counts reproduce published cohort figures byte-exact). The pre-2005 cohort comparability detail (keyless 1983–1988, weighted 1983–1984, the 1989/1998/2002 numerator-file residual, the 1992–1994 gap) is in `docs/COMPARABILITY.md` §"Pre-2005 cohort backward extension"; per-variable historical-distribution panels for the pre-2005 cohort years (and every linked-v4 death-side variable, per the documented linked layout eras) are in the auto-generated **Appendix C8.20 — Per-variable historical evidence** at the end of this file (C8.20; deterministic, parquet-derived).

Implemented by:

- `scripts/01_import/parse_all_linked_years.py` (2005–2015 batch), `scripts/01_import/parse_linked_cohort_year.py` (2016–2023)
- `scripts/03_harmonize/harmonize_linked_v3.py`
- `scripts/04_derive/derive_linked_v3.py` (derived columns)

### Record layout eras (linked)

| Era | Years | Record length | Format | Key differences |
|-----|-------|--------------|--------|-----------------|
| 1983–1988 | 1983–1988 | keyless two-file (den + num `.dat`) | Cohort, no per-record link key | `link_segment` ∈ {den, num}; `infant_death` NULL on den / True on num; IMR = count(num)/count(den); ICD-9 cause (`underlying_cause_icd9`/`cause_recode_61`); `age_at_death_days` NULL (AGER5-only → `age_at_death_recode5`); **1983–1984 = 50%-non-VSCP RECWT-weighted sample** |
| 1989–2004 | 1989–2004 | denominator-plus | Cohort (death-side appended to the birth record) | `infant_death` FLGND/MATCHS-derived; ICD-9 cause 1989–1998, ICD-10 1999+; **1992–1994 = permanent NCHS-linkage gap (no file)**; documented numerator-file residual for 1989/1998/2002 (same NCHS class as the 2 differ-by-1 cells below) |
| 2005–2013 | 2005–2013 | 900 bytes | Denominator-plus (birth + death appended) | Death fields at positions 868–900; FLGND=1/2 coding; birthweight at 467–470 |
| 2014–2015 | 2014–2015 | 1384 bytes | Denominator-plus (birth + death appended) | Death fields at positions 1346–1384; FLGND=1/blank coding; birthweight at 512–515 |
| 2016–2023 | 2016–2023 | 1346 (denom) + 1743 (numer) | Period-cohort (separate files, merged by CO_SEQNUM) | Death fields from numerator at positions 1346–1384; FLGND=1/blank coding |

**Notes:**
- Linked file birthweight positions differ from natality files. The linked files use `BRTHWGT` (imputed birthweight) instead of `DBWT`.
- Starting 2019, age-at-death variables (AGED, AGER5, AGER22) are calculated from birth certificate time-of-birth, improving accuracy for deaths within 24 hours but creating a minor comparability break with 2005–2018.

### Death-side harmonized columns

| harmonized_name | label | type | values | notes |
|---|---|---|---|---|
| `infant_death` | Infant death indicator | bool | true/false | `years_available` 1983–2023 (1992–1994 gap). 1989–2004 FLGND/MATCHS-derived; 2005–2013 FLGND=1/2; 2014–2023 FLGND=1/blank. **1983–1988 keyless era: NULL on den rows / True on num rows** — use the `link_segment` count ratio there, not a per-birth filter |
| `age_at_death_days` | Age at death (days) | int16 | 0–365 or null | `years_available` 1989–2023 (1992–1994 gap). Null for survivors. **NULL for ALL 1983–1988** (the keyless numerator carries the AGER5 recode only — use `age_at_death_recode5`) |
| `age_at_death_recode5` | Age at death 5-category recode | int8 | 1–5 or null | 1=<1hr; 2=1–23hr; 3=1–6d; 4=7–27d; 5=28d+. Null for survivors. The day-precise-free age signal available for the keyless 1983–1988 era |
| `underlying_cause_icd10` | Underlying cause of death (ICD-10) | string | ICD-10 codes or null | `years_available` 1999–2023 (1992–1994 gap). **NULL for 1983–1998 (the ICD-9 era — use `underlying_cause_icd9`)**. Null for survivors |
| `underlying_cause_icd9` | Underlying cause of death (ICD-9) | string | ICD-9 codes or null | **NEW at v4 (C8.18).** The ICD-9-era cause representation; populated cohort years **1983–1998** (1992–1994 gap); NULL 1999+ (ICD-10 era) and for survivors. Cross-era ICD-10 view: `underlying_cause_icd10_derived` on the derived parquet (LINK-ICD10) |
| `cause_recode_130` | 130 Infant Cause of Death recode | int16 | 1–158 or null | NCHS 130-cause recode; residual codes 131–158 (including SIDS=135) are valid. Do NOT filter `<= 130` — drops ~23% of deaths including all SIDS. Null for survivors. ICD-10 era (1999+) |
| `cause_recode_61` | 61-cause ICD-9-era recode | int16 | 1–61 or null | **NEW at v4 (C8.18).** The ICD-9-era sibling of `cause_recode_130`; NCHS 61-cause recode, cohort years **1983–1998** (1992–1994 gap); NULL 1999+ and for survivors |
| `manner_of_death` | Manner of death | int8 | 1–7 or null | 1=accident; 3=homicide; 5=could not determine; 7=natural. Null for survivors. `years_available` 2003–2023 |
| `record_weight` | Record weight | float64 | 1.0+ or null | Weight to adjust for unlinked deaths / **the 1983–1984 50%-non-VSCP sampling**. `years_available` 1983–1984, 1995–2023 (1992–1994 gap). 1.0 for most survivors. **NULL for 1985–1994** (1985–1988 are full files — Record count == by-occurrence — so no sampling weight applies). **For 1983–1984 apply the weight** (Σ`record_weight` over the resident denominator) to reproduce published cohort figures |
| `link_segment` | Keyless den/num segment tag | string | den / num / null | **NEW at v4 (C8.18).** Populated only for the keyless **1983–1988** cohort era: `den` = the births-only denominator aggregate (`infant_death` NULL); `num` = the infant-death numerator (`infant_death` True). NULL for 1989+ (those eras have a per-record `infant_death`). Use `count(num)/count(den)` per stratum for the 1983–1988 cohort IMR |

### Death-side derived columns (added by `derive_linked_v3.py`)

| derived_name | label | type | definition |
|---|---|---|---|
| `neonatal_death` | Neonatal death (<28 days) | bool | `infant_death AND age_at_death_days < 28` |
| `postneonatal_death` | Postneonatal death (28–364 days) | bool | `infant_death AND age_at_death_days >= 28` |
| `cause_group` | Standard infant cause-of-death grouping | string | 13 categories based on ICD-10 underlying cause: `congenital_anomalies` (Q00–Q99), `short_gestation_lbw` (P07), `sids` (R95), `maternal_complications` (P01), `placenta_cord_membranes` (P02), `unintentional_injuries` (V01–X59), `bacterial_sepsis` (P36), `respiratory_distress` (P22), `nec` (P77), `circulatory` (I00–I99), `assault` (X85–Y09), `other_perinatal` (remaining P00–P96), `other` (all else). Null for survivors |
| `underlying_cause_icd10_derived` | Underlying cause (ICD-10 derived bridge) | string | ICD-10 code or null | **LINK-ICD10.** 1983–1998: CMS GEM from `underlying_cause_icd9`; 1999+: copy `underlying_cause_icd10`. Null for survivors / rows without cause |
| `underlying_cause_icd10_derived_source` | ICD-10 derived provenance | string | `native_icd10` / `gem_from_icd9` / `gem_unmapped` | Set when a death-side cause is present |
| `underlying_cause_icd10_gem_approximate` | GEM approximate flag | int8 | 0 / 1 / null | 1 when `source=gem_from_icd9` and CMS GEM row was approximate |

Plus birth-side derived columns: `gestational_age_weeks_clean`, `birthweight_grams_clean`, `apgar5_clean`, `low_birthweight`, `very_low_birthweight`, `preterm_lt37`, `very_preterm_lt32`, `singleton`, `maternal_age_cat`, `father_age_cat`, `diabetes_any_bool`, `hypertension_chronic_bool`, `hypertension_gestational_bool`.

## Next

- For comparability guidance and recommended trend-safe subsets, see `docs/COMPARABILITY.md`.

<!-- C8.20-GENERATED:BEGIN (do not hand-edit; regenerate via scripts/_build_codebook_extensions.py) -->

## Appendix C8.20 — Per-variable historical evidence (auto-generated)

> Auto-generated by `scripts/_build_codebook_extensions.py` — do **not** hand-edit; regenerate. Every count below is derived from the gate-verified parquet; era boundaries are documented NCHS layout constants (see `COMPARABILITY.md` + the layout-source CSVs + the C8.16/C8.17/C8.18/C8.2 receipts).
>
> Provenance: natality v3.0.0 derived `natality_v2_harmonized_derived.parquet` sha256[:12]=`acb5c48a9abf` · 201,161,456 rows; linked v4.0.0 derived `natality_v3_linked_harmonized_derived.parquet` sha256[:12]=`f630d8cf20db` · 149,386,620 rows (1992-1994 permanent NCHS-linkage gap) · builder `scripts/_build_codebook_extensions.py` — natality columns (1968-2024)
>
> Era partition: `1968-1971` · `1972-1977` · `1978-1988` · `1989-2002` · `2003-2013` · `2014-2024`

**Variable index:** [`data_year`](#c820-natality-data_year) · [`residence_status`](#c820-natality-residence_status) · [`is_foreign_resident`](#c820-natality-is_foreign_resident) · [`certificate_revision`](#c820-natality-certificate_revision) · [`maternal_age`](#c820-natality-maternal_age) · [`live_birth_order_recode`](#c820-natality-live_birth_order_recode) · [`total_birth_order_recode`](#c820-natality-total_birth_order_recode) · [`marital_status`](#c820-natality-marital_status) · [`marital_reporting_flag`](#c820-natality-marital_reporting_flag) · [`hispanic_origin`](#c820-natality-hispanic_origin) · [`maternal_hispanic`](#c820-natality-maternal_hispanic) · [`maternal_race_bridged`](#c820-natality-maternal_race_bridged) · [`maternal_race_ethnicity_5`](#c820-natality-maternal_race_ethnicity_5) · [`maternal_race_detail`](#c820-natality-maternal_race_detail) · [`maternal_race_detail_15cat`](#c820-natality-maternal_race_detail_15cat) · [`race_bridge_method`](#c820-natality-race_bridge_method) · [`maternal_education_cat4`](#c820-natality-maternal_education_cat4) · [`prenatal_care_start_month`](#c820-natality-prenatal_care_start_month) · [`prenatal_care_start_trimester`](#c820-natality-prenatal_care_start_trimester) · [`prenatal_visits`](#c820-natality-prenatal_visits) · [`smoking_any_during_pregnancy`](#c820-natality-smoking_any_during_pregnancy) · [`smoking_intensity_max_recode6`](#c820-natality-smoking_intensity_max_recode6) · [`smoking_pre_pregnancy_recode6`](#c820-natality-smoking_pre_pregnancy_recode6) · [`diabetes_any`](#c820-natality-diabetes_any) · [`hypertension_chronic`](#c820-natality-hypertension_chronic) · [`hypertension_gestational`](#c820-natality-hypertension_gestational) · [`plurality_recode`](#c820-natality-plurality_recode) · [`infant_sex`](#c820-natality-infant_sex) · [`gestational_age_weeks`](#c820-natality-gestational_age_weeks) · [`gestational_age_weeks_source`](#c820-natality-gestational_age_weeks_source) · [`preterm_recode3`](#c820-natality-preterm_recode3) · [`birthweight_grams`](#c820-natality-birthweight_grams) · [`delivery_method_recode`](#c820-natality-delivery_method_recode) · [`apgar5`](#c820-natality-apgar5) · [`bmi_prepregnancy`](#c820-natality-bmi_prepregnancy) · [`bmi_prepregnancy_recode6`](#c820-natality-bmi_prepregnancy_recode6) · [`father_age`](#c820-natality-father_age) · [`father_age_cat_from_rec11`](#c820-natality-father_age_cat_from_rec11) · [`birth_facility`](#c820-natality-birth_facility) · [`attendant_at_birth`](#c820-natality-attendant_at_birth) · [`payment_source_recode`](#c820-natality-payment_source_recode) · [`prior_cesarean`](#c820-natality-prior_cesarean) · [`father_hispanic`](#c820-natality-father_hispanic) · [`father_race_ethnicity_5`](#c820-natality-father_race_ethnicity_5) · [`father_education_cat4`](#c820-natality-father_education_cat4) · [`ca_anencephaly`](#c820-natality-ca_anencephaly) · [`ca_spina_bifida`](#c820-natality-ca_spina_bifida) · [`ca_cchd`](#c820-natality-ca_cchd) · [`ca_cdh`](#c820-natality-ca_cdh) · [`ca_omphalocele`](#c820-natality-ca_omphalocele) · [`ca_gastroschisis`](#c820-natality-ca_gastroschisis) · [`ca_limb_reduction`](#c820-natality-ca_limb_reduction) · [`ca_cleft_lip`](#c820-natality-ca_cleft_lip) · [`ca_cleft_palate`](#c820-natality-ca_cleft_palate) · [`ca_down_syndrome`](#c820-natality-ca_down_syndrome) · [`ca_chromosomal_disorder`](#c820-natality-ca_chromosomal_disorder) · [`ca_hypospadias`](#c820-natality-ca_hypospadias) · [`infection_gonorrhea`](#c820-natality-infection_gonorrhea) · [`infection_syphilis`](#c820-natality-infection_syphilis) · [`infection_chlamydia`](#c820-natality-infection_chlamydia) · [`infection_hep_b`](#c820-natality-infection_hep_b) · [`infection_hep_c`](#c820-natality-infection_hep_c) · [`prior_cesarean_count`](#c820-natality-prior_cesarean_count) · [`fertility_enhancing_drugs`](#c820-natality-fertility_enhancing_drugs) · [`assisted_reproductive_tech`](#c820-natality-assisted_reproductive_tech) · [`pre_pregnancy_diabetes`](#c820-natality-pre_pregnancy_diabetes) · [`gestational_diabetes`](#c820-natality-gestational_diabetes) · [`nicu_admission`](#c820-natality-nicu_admission) · [`weight_gain_pounds`](#c820-natality-weight_gain_pounds) · [`induction_of_labor`](#c820-natality-induction_of_labor) · [`breastfed_at_discharge`](#c820-natality-breastfed_at_discharge) · [`gestational_age_weeks_clean`](#c820-natality-gestational_age_weeks_clean) · [`birthweight_grams_clean`](#c820-natality-birthweight_grams_clean) · [`apgar5_clean`](#c820-natality-apgar5_clean) · [`low_birthweight`](#c820-natality-low_birthweight) · [`very_low_birthweight`](#c820-natality-very_low_birthweight) · [`preterm_lt37`](#c820-natality-preterm_lt37) · [`very_preterm_lt32`](#c820-natality-very_preterm_lt32) · [`singleton`](#c820-natality-singleton) · [`maternal_age_cat`](#c820-natality-maternal_age_cat) · [`father_age_cat`](#c820-natality-father_age_cat) · [`diabetes_any_bool`](#c820-natality-diabetes_any_bool) · [`hypertension_chronic_bool`](#c820-natality-hypertension_chronic_bool) · [`hypertension_gestational_bool`](#c820-natality-hypertension_gestational_bool)

### `data_year` <a id="c820-natality-data_year"></a>

_Schema note:_ 1968-2024

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1970`: 1,868,900 (25.95%); `1969`: 1,800,103 (25.00%); `1971`: 1,781,774 (24.74%); `1968`: 1,750,782 (24.31%) | 0.00% |
| `1972-1977` | 13,086,752 | `1977`: 2,772,206 (21.18%); `1976`: 2,463,852 (18.83%); `1975`: 2,232,406 (17.06%); `1974`: 2,029,150 (15.51%); `1973`: 1,839,736 (14.06%); `1972`: 1,749,402 (13.37%) | 0.00% |
| `1978-1988` | 38,007,797 | `1988`: 3,913,793 (10.30%); `1987`: 3,813,216 (10.03%); `1985`: 3,765,064 (9.91%); `1986`: 3,760,695 (9.89%); `1982`: 3,376,813 (8.88%); `1984`: 3,360,871 (8.84%); `1983`: 3,337,883 (8.78%); `1981`: 3,319,054 (8.73%); _(+3 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `1990`: 4,162,917 (7.42%); `1991`: 4,115,342 (7.34%); `1992`: 4,069,428 (7.26%); `2000`: 4,063,823 (7.25%); `1989`: 4,045,693 (7.22%); `2001`: 4,031,531 (7.19%); `2002`: 4,027,376 (7.18%); `1993`: 4,004,523 (7.14%); _(+6 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `2007`: 4,324,008 (9.56%); `2006`: 4,273,225 (9.45%); `2008`: 4,255,156 (9.41%); `2005`: 4,145,619 (9.17%); `2009`: 4,137,836 (9.15%); `2004`: 4,118,907 (9.11%); `2003`: 4,096,092 (9.06%); `2010`: 4,007,105 (8.86%); _(+3 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `2014`: 3,998,175 (9.62%); `2015`: 3,988,733 (9.59%); `2016`: 3,956,112 (9.52%); `2017`: 3,864,754 (9.30%); `2018`: 3,801,534 (9.14%); `2019`: 3,757,582 (9.04%); `2022`: 3,676,029 (8.84%); `2021`: 3,669,928 (8.83%); _(+3 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`1972`, `1973`, `1974`, `1975`, `1976`, `1977`}; dropped {`1968`, `1969`, `1970`, `1971`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: added {`1978`, `1979`, `1980`, `1981`, `1982`, `1983`, `1984`, `1985`, `1986`, `1987`, `1988`}; dropped {`1972`, `1973`, `1974`, `1975`, `1976`, `1977`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`1989`, `1990`, `1991`, `1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`}; dropped {`1978`, `1979`, `1980`, `1981`, `1982`, `1983`, `1984`, `1985`, `1986`, `1987`, `1988`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`2003`, `2004`, `2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`}; dropped {`1989`, `1990`, `1991`, `1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`2014`, `2015`, `2016`, `2017`, `2018`, `2019`, `2020`, `2021`, `2022`, `2023`, `2024`}; dropped {`2003`, `2004`, `2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`} _(codes ≥0.05% of an era)_

### `residence_status` <a id="c820-natality-residence_status"></a>

_Schema note:_ 1|2|3|4 — Code 4 indicates foreign resident. Use to exclude foreign residents for residence-based totals.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 5,861,994 (81.40%); `2`: 1,153,627 (16.02%); `3`: 178,942 (2.48%); `4`: 6,996 (0.10%) | 0.00% |
| `1972-1977` | 13,086,752 | `1`: 10,271,580 (78.49%); `2`: 2,448,247 (18.71%); `3`: 334,935 (2.56%); `4`: 31,990 (0.24%) | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 29,180,268 (76.77%); `2`: 7,816,419 (20.57%); `3`: 961,783 (2.53%); `4`: 49,327 (0.13%) | 0.00% |
| `1989-2002` | 56,068,430 | `1`: 42,527,979 (75.85%); `2`: 12,206,926 (21.77%); `3`: 1,272,613 (2.27%); `4`: 60,912 (0.11%) | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 33,109,197 (73.22%); `2`: 11,064,969 (24.47%); `3`: 964,330 (2.13%); `4`: 82,232 (0.18%) | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 28,729,344 (69.10%); `2`: 11,727,882 (28.21%); `3`: 1,020,622 (2.45%); `4`: 98,342 (0.24%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `is_foreign_resident` <a id="c820-natality-is_foreign_resident"></a>

_Schema note:_ true|false

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `false`: 7,194,563 (99.90%); `true`: 6,996 (0.10%) | 0.00% |
| `1972-1977` | 13,086,752 | `false`: 13,054,762 (99.76%); `true`: 31,990 (0.24%) | 0.00% |
| `1978-1988` | 38,007,797 | `false`: 37,958,470 (99.87%); `true`: 49,327 (0.13%) | 0.00% |
| `1989-2002` | 56,068,430 | `false`: 56,007,518 (99.89%); `true`: 60,912 (0.11%) | 0.00% |
| `2003-2013` | 45,220,728 | `false`: 45,138,496 (99.82%); `true`: 82,232 (0.18%) | 0.00% |
| `2014-2024` | 41,576,190 | `false`: 41,477,848 (99.76%); `true`: 98,342 (0.24%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `certificate_revision` <a id="c820-natality-certificate_revision"></a>

_Schema note:_ unrevised_1968|unrevised_1989|revised_2003|unknown — Use to define revision-consistent analytic subsets, especially for variables that are revised-only in some years. The unrevised_1968 value (1968-1988, the 1968-revision certificate era…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `unrevised_1968`: 7,201,559 (100.00%) | 0.00% |
| `1972-1977` | 13,086,752 | `unrevised_1968`: 13,086,752 (100.00%) | 0.00% |
| `1978-1988` | 38,007,797 | `unrevised_1968`: 38,007,797 (100.00%) | 0.00% |
| `1989-2002` | 56,068,430 | `unrevised_1989`: 56,068,430 (100.00%) | 0.00% |
| `2003-2013` | 45,220,728 | `revised_2003`: 25,865,955 (57.20%); `unrevised_1989`: 18,648,416 (41.24%); `unknown`: 706,357 (1.56%) | 0.00% |
| `2014-2024` | 41,576,190 | `revised_2003`: 41,576,190 (100.00%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`unrevised_1989`}; dropped {`unrevised_1968`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`revised_2003`, `unknown`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`unknown`, `unrevised_1989`} _(codes ≥0.05% of an era)_

### `maternal_age` <a id="c820-natality-maternal_age"></a>

_Schema note:_ 10-54 (see User Guides) — 2003 is from MAGER41 recode (code 1→14; codes 2-41→N+13; 99/other→null).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `22`: 566,792 (7.87%); `21`: 566,380 (7.86%); `23`: 550,516 (7.64%); `20`: 520,832 (7.23%); `24`: 516,380 (7.17%); `25`: 474,173 (6.58%); `19`: 462,402 (6.42%); `26`: 435,172 (6.04%); _(+32 more codes)_ | 0.00% |
| `1972-1977` | 13,086,752 | `23`: 945,169 (7.22%); `24`: 941,247 (7.19%); `25`: 932,704 (7.13%); `22`: 925,383 (7.07%); `21`: 900,301 (6.88%); `26`: 869,132 (6.64%); `20`: 864,099 (6.60%); `19`: 799,950 (6.11%); _(+32 more codes)_ | 0.00% |
| `1978-1988` | 38,007,797 | `25`: 2,591,645 (6.82%); `24`: 2,568,524 (6.76%); `26`: 2,547,473 (6.70%); `23`: 2,521,713 (6.63%); `27`: 2,441,892 (6.42%); `22`: 2,417,463 (6.36%); `21`: 2,295,233 (6.04%); `28`: 2,281,835 (6.00%); _(+32 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `28`: 3,201,167 (5.71%); `27`: 3,188,410 (5.69%); `29`: 3,182,247 (5.68%); `26`: 3,127,476 (5.58%); `30`: 3,056,556 (5.45%); `25`: 3,049,691 (5.44%); `24`: 2,955,515 (5.27%); `23`: 2,899,451 (5.17%); _(+37 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `28`: 2,568,491 (5.68%); `29`: 2,552,800 (5.65%); `27`: 2,545,655 (5.63%); `26`: 2,499,603 (5.53%); `30`: 2,473,180 (5.47%); `25`: 2,439,096 (5.39%); `24`: 2,366,767 (5.23%); `31`: 2,355,260 (5.21%); _(+35 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `30`: 2,621,852 (6.31%); `31`: 2,609,054 (6.28%); `29`: 2,594,514 (6.24%); `28`: 2,507,427 (6.03%); `32`: 2,486,937 (5.98%); `27`: 2,377,058 (5.72%); `33`: 2,301,170 (5.53%); `26`: 2,241,042 (5.39%); _(+31 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`13`}; dropped {`45`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: dropped {`13`, `44`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`44`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`45`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`46`}; dropped {`14`} _(codes ≥0.05% of an era)_

### `live_birth_order_recode` <a id="c820-natality-live_birth_order_recode"></a>

_Schema note:_ 1-7|8|9 — 9 indicates unknown/not stated.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 2,081,796 (28.91%); `2`: 1,487,811 (20.66%); `3`: 834,381 (11.59%); `4`: 441,738 (6.13%); `5`: 234,973 (3.26%); `6`: 127,919 (1.78%); `8`: 112,002 (1.56%); `7`: 72,733 (1.01%); _(+1 more codes)_ | 24.31% |
| `1972-1977` | 13,086,752 | `1`: 5,393,260 (41.21%); `2`: 4,039,153 (30.86%); `3`: 1,857,996 (14.20%); `4`: 789,479 (6.03%); `5`: 359,253 (2.75%); `9`: 231,616 (1.77%); `6`: 179,673 (1.37%); `8`: 138,755 (1.06%); _(+1 more codes)_ | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 15,901,874 (41.84%); `2`: 12,347,985 (32.49%); `3`: 5,853,499 (15.40%); `4`: 2,175,484 (5.72%); `5`: 815,733 (2.15%); `6`: 348,756 (0.92%); `9`: 217,575 (0.57%); `8`: 183,112 (0.48%); _(+1 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `1`: 22,650,013 (40.40%); `2`: 18,075,697 (32.24%); `3`: 9,159,058 (16.34%); `4`: 3,542,360 (6.32%); `5`: 1,313,791 (2.34%); `6`: 541,618 (0.97%); `9`: 287,702 (0.51%); `8`: 252,906 (0.45%); _(+1 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 18,023,993 (39.86%); `2`: 14,311,212 (31.65%); `3`: 7,522,475 (16.64%); `4`: 3,080,951 (6.81%); `5`: 1,153,601 (2.55%); `6`: 466,910 (1.03%); `9`: 242,560 (0.54%); `8`: 211,004 (0.47%); _(+1 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 15,931,851 (38.32%); `2`: 13,230,287 (31.82%); `3`: 6,990,702 (16.81%); `4`: 3,055,890 (7.35%); `5`: 1,217,167 (2.93%); `6`: 516,236 (1.24%); `8`: 253,861 (0.61%); `7`: 236,027 (0.57%); _(+1 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `9` | 57,424 | 0.80% |
| `1968-1971` | _null/blank_ | 1,750,782 | 24.31% |
| `1972-1977` | `9` | 231,616 | 1.77% |
| `1978-1988` | `9` | 217,575 | 0.57% |
| `1989-2002` | `9` | 287,702 | 0.51% |
| `2003-2013` | `9` | 242,560 | 0.54% |
| `2014-2024` | `9` | 144,169 | 0.35% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `total_birth_order_recode` <a id="c820-natality-total_birth_order_recode"></a>

_Schema note:_ 1-7|8|9 — 9 indicates unknown/not stated.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 1,981,483 (27.51%); `2`: 1,422,251 (19.75%); `3`: 841,684 (11.69%); `4`: 475,486 (6.60%); `5`: 269,629 (3.74%); `6`: 154,669 (2.15%); `8`: 152,740 (2.12%); `7`: 92,012 (1.28%); _(+1 more codes)_ | 24.31% |
| `1972-1977` | 13,086,752 | `1`: 4,997,100 (38.18%); `2`: 3,884,556 (29.68%); `3`: 1,990,490 (15.21%); `4`: 942,393 (7.20%); `5`: 462,218 (3.53%); `6`: 239,611 (1.83%); `9`: 235,635 (1.80%); `8`: 200,698 (1.53%); _(+1 more codes)_ | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 13,456,804 (35.41%); `2`: 11,647,976 (30.65%); `3`: 6,696,575 (17.62%); `4`: 3,132,313 (8.24%); `5`: 1,408,580 (3.71%); `6`: 644,572 (1.70%); `8`: 360,533 (0.95%); `9`: 346,719 (0.91%); _(+1 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `1`: 18,450,764 (32.91%); `2`: 16,364,755 (29.19%); `3`: 10,401,048 (18.55%); `4`: 5,380,579 (9.60%); `5`: 2,603,763 (4.64%); `6`: 1,232,586 (2.20%); `8`: 666,447 (1.19%); `7`: 604,246 (1.08%); _(+1 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 14,921,255 (33.00%); `2`: 12,827,362 (28.37%); `3`: 8,250,158 (18.24%); `4`: 4,412,042 (9.76%); `5`: 2,193,318 (4.85%); `6`: 1,056,881 (2.34%); `8`: 604,959 (1.34%); `7`: 530,354 (1.17%); _(+1 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 13,036,488 (31.36%); `2`: 11,561,075 (27.81%); `3`: 7,605,006 (18.29%); `4`: 4,317,262 (10.38%); `5`: 2,282,381 (5.49%); `6`: 1,168,432 (2.81%); `8`: 762,282 (1.83%); `7`: 610,923 (1.47%); _(+1 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `9` | 60,823 | 0.84% |
| `1968-1971` | _null/blank_ | 1,750,782 | 24.31% |
| `1972-1977` | `9` | 235,635 | 1.80% |
| `1978-1988` | `9` | 346,719 | 0.91% |
| `1989-2002` | `9` | 364,242 | 0.65% |
| `2003-2013` | `9` | 424,399 | 0.94% |
| `2014-2024` | `9` | 232,341 | 0.56% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `marital_status` <a id="c820-natality-marital_status"></a>

_Schema note:_ 1|2|9 — 1=married; 2=unmarried; 9=unknown/not stated. California stopped reporting marital status starting 2017: ~11-12% null from 2017 onward (0% null 1990-2016). Use marital_reporting_flag to identify non-reporting-state births.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `1`: 38,394,433 (68.48%); `2`: 17,673,997 (31.52%) | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 27,562,328 (60.95%); `2`: 17,658,400 (39.05%) | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 22,834,546 (54.92%); `2`: 15,298,691 (36.80%) | 8.28% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `2014-2024` | _null/blank_ | 3,442,953 | 8.28% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`1`, `2`} _(codes ≥0.05% of an era)_

### `marital_reporting_flag` <a id="c820-natality-marital_reporting_flag"></a>

_Schema note:_ true|false|null — True=state reports marital status to NCHS; False=non-reporting state (California from 2017+). Null for all pre-2014 years. Use to distinguish non-reporting-state births from genuine unknowns when marital_status is null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `true`: 37,753,773 (90.81%); `false`: 3,822,417 (9.19%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `hispanic_origin` <a id="c820-natality-hispanic_origin"></a>

_Schema note:_ 0|1|2|3|4|5|9 — 0=non-Hispanic; 1-5 specific Hispanic origin; 9=unknown/not stated. Blanks can occur due to nonreporting.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `0`: 45,300,913 (80.80%); `1`: 6,825,062 (12.17%); `4`: 1,370,276 (2.44%); `9`: 883,765 (1.58%); `2`: 802,801 (1.43%); `5`: 711,124 (1.27%); `3`: 174,489 (0.31%) | 0.00% |
| `2003-2013` | 45,220,728 | `0`: 34,161,955 (75.54%); `1`: 7,130,687 (15.77%); `4`: 1,613,069 (3.57%); `5`: 1,077,946 (2.38%); `2`: 724,883 (1.60%); `9`: 328,746 (0.73%); `3`: 183,442 (0.41%) | 0.00% |
| `2014-2024` | 41,576,190 | `0`: 31,073,870 (74.74%); `1`: 5,712,341 (13.74%); `4`: 1,878,518 (4.52%); `5`: 1,496,636 (3.60%); `2`: 766,389 (1.84%); `9`: 377,724 (0.91%); `3`: 270,712 (0.65%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 883,765 | 1.58% |
| `2003-2013` | `9` | 328,746 | 0.73% |
| `2014-2024` | `9` | 377,724 | 0.91% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`0`, `1`, `2`, `3`, `4`, `5`, `9`} _(codes ≥0.05% of an era)_

### `maternal_hispanic` <a id="c820-natality-maternal_hispanic"></a>

_Schema note:_ true|false — Null when Hispanic origin is missing or unknown.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 45,300,913 (80.80%); `true`: 9,883,752 (17.63%) | 1.58% |
| `2003-2013` | 45,220,728 | `false`: 34,161,955 (75.54%); `true`: 10,730,027 (23.73%) | 0.73% |
| `2014-2024` | 41,576,190 | `false`: 31,073,870 (74.74%); `true`: 10,124,596 (24.35%) | 0.91% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 883,765 | 1.58% |
| `2003-2013` | _null/blank_ | 328,746 | 0.73% |
| `2014-2024` | _null/blank_ | 377,724 | 0.91% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `maternal_race_bridged` <a id="c820-natality-maternal_race_bridged"></a>

_Schema note:_ 1|2|3|4 — 1=White; 2=Black; 3=AIAN; 4=Asian/PI. 1990-2002 uses approximate crosswalk (not official NCHS bridged race). 100% NULL for 2020-2024 — NCHS discontinued the bridged-race recode; for 2020+ use maternal_race_ethnicity_5 (which is…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 5,990,741 (83.19%); `2`: 1,085,176 (15.07%); `4`: 48,913 (0.68%); `3`: 43,864 (0.61%) | 0.46% |
| `1972-1977` | 13,086,752 | `1`: 10,730,462 (81.99%); `2`: 2,080,216 (15.90%); `4`: 100,506 (0.77%); `3`: 85,704 (0.65%) | 0.69% |
| `1978-1988` | 38,007,797 | `1`: 30,649,745 (80.64%); `2`: 5,993,530 (15.77%); `4`: 906,519 (2.39%); `3`: 314,477 (0.83%) | 0.38% |
| `1989-2002` | 56,068,430 | `1`: 44,316,022 (79.04%); `2`: 8,846,701 (15.78%); `4`: 1,937,340 (3.46%); `3`: 553,491 (0.99%) | 0.74% |
| `2003-2013` | 45,220,728 | `1`: 34,925,326 (77.23%); `2`: 7,060,363 (15.61%); `4`: 2,722,451 (6.02%); `3`: 512,588 (1.13%) | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 17,514,669 (42.13%); `2`: 3,864,903 (9.30%); `4`: 1,728,533 (4.16%); `3`: 258,785 (0.62%) | 43.80% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 32,865 | 0.46% |
| `1972-1977` | _null/blank_ | 89,864 | 0.69% |
| `1978-1988` | _null/blank_ | 143,526 | 0.38% |
| `1989-2002` | _null/blank_ | 414,876 | 0.74% |
| `2014-2024` | _null/blank_ | 18,209,300 | 43.80% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `maternal_race_ethnicity_5` <a id="c820-natality-maternal_race_ethnicity_5"></a>

_Schema note:_ NH_white|NH_black|NH_aian|NH_asian_pi|Hispanic — Null when Hispanic origin is missing/unknown or race is multiracial (MRACE6=06 for 2020+, ~3% of births). See race_bridge_method for derivation era.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `NH_white`: 33,968,474 (60.58%); `Hispanic`: 9,883,752 (17.63%); `NH_black`: 8,561,048 (15.27%); `NH_asian_pi`: 1,868,888 (3.33%); `NH_aian`: 505,592 (0.90%) | 2.28% |
| `2003-2013` | 45,220,728 | `NH_white`: 24,576,256 (54.35%); `Hispanic`: 10,730,027 (23.73%); `NH_black`: 6,557,391 (14.50%); `NH_asian_pi`: 2,584,022 (5.71%); `NH_aian`: 444,286 (0.98%) | 0.73% |
| `2014-2024` | 41,576,190 | `NH_white`: 21,504,882 (51.72%); `Hispanic`: 10,124,596 (24.35%); `NH_black`: 6,033,719 (14.51%); `NH_asian_pi`: 2,756,005 (6.63%); `NH_aian`: 338,924 (0.82%) | 1.97% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 1,280,676 | 2.28% |
| `2003-2013` | _null/blank_ | 328,746 | 0.73% |
| `2014-2024` | _null/blank_ | 818,064 | 1.97% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`Hispanic`, `NH_aian`, `NH_asian_pi`, `NH_black`, `NH_white`} _(codes ≥0.05% of an era)_

### `maternal_race_detail` <a id="c820-natality-maternal_race_detail"></a>

_Schema note:_ See User Guides by era — Code frame differs across eras; do not treat as a single comparable series.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 5,990,741 (83.19%); `2`: 1,085,176 (15.07%); `3`: 43,864 (0.61%); `7`: 21,936 (0.30%); `5`: 15,747 (0.22%); `4`: 13,091 (0.18%); `8`: 11,703 (0.16%); `9`: 10,929 (0.15%); _(+2 more codes)_ | 0.00% |
| `1972-1977` | 13,086,752 | `1`: 10,730,462 (81.99%); `2`: 2,080,216 (15.90%); `3`: 85,704 (0.65%); `7`: 69,904 (0.53%); `8`: 34,745 (0.27%); `4`: 28,546 (0.22%); `5`: 24,278 (0.19%); `9`: 19,960 (0.15%); _(+2 more codes)_ | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 30,649,745 (80.64%); `2`: 5,993,530 (15.77%); `0`: 480,554 (1.26%); `3`: 314,477 (0.83%); `8`: 164,005 (0.43%); `4`: 137,898 (0.36%); `9`: 118,784 (0.31%); `5`: 73,469 (0.19%); _(+2 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `01`: 44,316,022 (79.04%); `02`: 8,846,701 (15.78%); `03`: 553,491 (0.99%); `07`: 418,498 (0.75%); `78`: 406,196 (0.72%); `04`: 384,274 (0.69%); `08`: 234,053 (0.42%); `68`: 225,712 (0.40%); _(+8 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `01`: 14,214,636 (31.43%); `02`: 3,133,413 (6.93%); `78`: 273,770 (0.61%); `03`: 262,013 (0.58%); `18`: 177,143 (0.39%); `04`: 157,311 (0.35%); `07`: 140,426 (0.31%); `68`: 133,459 (0.30%); _(+6 more codes)_ | 58.76% |
| `2014-2024` | 41,576,190 | `01`: 30,592,680 (73.58%); `02`: 6,485,148 (15.60%); `04`: 2,710,539 (6.52%); `06`: 1,108,308 (2.67%); `03`: 401,294 (0.97%); `05`: 143,756 (0.35%); `09`: 2,923 (0.01%) | 0.32% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `9` | 10,929 | 0.15% |
| `1972-1977` | `9` | 19,960 | 0.15% |
| `1978-1988` | `9` | 118,784 | 0.31% |
| `2003-2013` | _null/blank_ | 26,572,312 | 58.76% |
| `2014-2024` | _null/blank_ | 131,542 | 0.32% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1972-1977`→`1978-1988`: added {`0`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `18`, `28`, `48`, `68`, `78`}; dropped {`0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: dropped {`06`, `08`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`06`}; dropped {`07`, `18`, `28`, `48`, `68`, `78`} _(codes ≥0.05% of an era)_

### `maternal_race_detail_15cat` <a id="c820-natality-maternal_race_detail_15cat"></a>

_Schema note:_ 01-15 — 15=multiracial. Populated 2014+. NCHS does not expose MRACE15 in 2003-2013 public-use files — null for all 1990-2013 rows.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `01`: 30,592,680 (73.58%); `02`: 6,485,148 (15.60%); `15`: 1,108,308 (2.67%); `04`: 805,326 (1.94%); `05`: 572,085 (1.38%); `10`: 542,547 (1.30%); `03`: 401,294 (0.97%); `06`: 344,043 (0.83%); _(+7 more codes)_ | 0.32% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 134,465 | 0.32% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `13`, `14`, `15`} _(codes ≥0.05% of an era)_

### `race_bridge_method` <a id="c820-natality-race_bridge_method"></a>

_Schema note:_ approximate_pre2003|nchs_bridged|approximate_from_detail — approximate_pre2003 for 1990-2002 (crosswalk from MRACE detail); nchs_bridged for 2003-2019 (official NCHS MBRACE/MRACEREC); approximate_from_detail for 2020-2024 (reconstructed …

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `approximate_pre2003`: 7,201,559 (100.00%) | 0.00% |
| `1972-1977` | 13,086,752 | `approximate_pre2003`: 13,086,752 (100.00%) | 0.00% |
| `1978-1988` | 38,007,797 | `approximate_pre2003`: 38,007,797 (100.00%) | 0.00% |
| `1989-2002` | 56,068,430 | `approximate_pre2003`: 56,068,430 (100.00%) | 0.00% |
| `2003-2013` | 45,220,728 | `nchs_bridged`: 45,220,728 (100.00%) | 0.00% |
| `2014-2024` | 41,576,190 | `nchs_bridged`: 23,366,890 (56.20%); `approximate_from_detail`: 18,209,300 (43.80%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`nchs_bridged`}; dropped {`approximate_pre2003`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`approximate_from_detail`} _(codes ≥0.05% of an era)_

### `maternal_education_cat4` <a id="c820-natality-maternal_education_cat4"></a>

_Schema note:_ lt_hs|hs_grad|some_college|ba_plus — Expect substantial missingness in 2009-2013 corresponding to unrevised areas. For revision-consistent analyses in 2009-2013, restrict to `certificate_revision == 'revised_2003'`.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `hs_grad`: 1,635,891 (22.72%); `lt_hs`: 1,085,669 (15.08%); `some_college`: 470,901 (6.54%); `ba_plus`: 300,499 (4.17%) | 51.50% |
| `1972-1977` | 13,086,752 | `hs_grad`: 4,538,510 (34.68%); `lt_hs`: 2,855,899 (21.82%); `some_college`: 1,536,765 (11.74%); `ba_plus`: 1,132,489 (8.65%) | 23.10% |
| `1978-1988` | 38,007,797 | `hs_grad`: 12,999,299 (34.20%); `lt_hs`: 6,636,309 (17.46%); `some_college`: 5,827,151 (15.33%); `ba_plus`: 4,754,301 (12.51%) | 20.50% |
| `1989-2002` | 56,068,430 | `hs_grad`: 18,799,448 (33.53%); `lt_hs`: 12,344,963 (22.02%); `ba_plus`: 11,767,559 (20.99%); `some_college`: 11,722,329 (20.91%) | 2.56% |
| `2003-2013` | 45,220,728 | `hs_grad`: 11,248,763 (24.88%); `ba_plus`: 11,121,281 (24.59%); `some_college`: 10,393,110 (22.98%); `lt_hs`: 8,306,631 (18.37%) | 9.18% |
| `2014-2024` | 41,576,190 | `ba_plus`: 13,704,015 (32.96%); `some_college`: 11,315,662 (27.22%); `hs_grad`: 10,592,573 (25.48%); `lt_hs`: 5,147,511 (12.38%) | 1.96% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 3,708,599 | 51.50% |
| `1972-1977` | _null/blank_ | 3,023,089 | 23.10% |
| `1978-1988` | _null/blank_ | 7,790,737 | 20.50% |
| `1989-2002` | _null/blank_ | 1,434,131 | 2.56% |
| `2003-2013` | _null/blank_ | 4,150,943 | 9.18% |
| `2014-2024` | _null/blank_ | 816,429 | 1.96% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `prenatal_care_start_month` <a id="c820-natality-prenatal_care_start_month"></a>

_Schema note:_ 0-10|99 — 00 indicates no prenatal care; 99 indicates unknown/not stated. Expect substantial missingness in 2009-2013.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `2`: 1,757,256 (24.40%); `3`: 1,140,266 (15.83%); `4`: 512,152 (7.11%); `5`: 306,788 (4.26%); `6`: 203,740 (2.83%); `7`: 141,379 (1.96%); `8`: 83,719 (1.16%); `0`: 74,612 (1.04%); _(+1 more codes)_ | 40.94% |
| `1972-1977` | 13,086,752 | `2`: 4,175,914 (31.91%); `3`: 3,049,828 (23.30%); `4`: 1,276,429 (9.75%); `1`: 948,051 (7.24%); `5`: 716,506 (5.48%); `6`: 433,841 (3.32%); `7`: 285,387 (2.18%); `8`: 167,952 (1.28%); _(+2 more codes)_ | 13.81% |
| `1978-1988` | 38,007,797 | `2`: 14,531,558 (38.23%); `3`: 8,611,764 (22.66%); `1`: 5,051,312 (13.29%); `4`: 3,575,221 (9.41%); `5`: 2,003,932 (5.27%); `6`: 1,211,045 (3.19%); `7`: 803,846 (2.11%); `0`: 609,825 (1.60%); _(+2 more codes)_ | 2.46% |
| `1989-2002` | 56,068,430 | `2`: 22,249,722 (39.68%); `1`: 10,892,444 (19.43%); `3`: 10,855,464 (19.36%); `4`: 4,329,417 (7.72%); `5`: 2,427,042 (4.33%); `6`: 1,467,474 (2.62%); `99`: 1,334,554 (2.38%); `7`: 951,473 (1.70%); _(+3 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `2`: 14,696,063 (32.50%); `3`: 11,219,940 (24.81%); `1`: 4,949,061 (10.94%); `4`: 3,921,902 (8.67%); `5`: 1,977,733 (4.37%); `99`: 1,479,025 (3.27%); `6`: 1,191,528 (2.63%); `7`: 774,675 (1.71%); _(+4 more codes)_ | 8.03% |
| `2014-2024` | 41,576,190 | `2`: 15,838,065 (38.09%); `3`: 12,918,101 (31.07%); `4`: 3,697,551 (8.89%); `1`: 2,300,211 (5.53%); `5`: 1,842,208 (4.43%); `6`: 1,127,363 (2.71%); `99`: 1,042,318 (2.51%); `7`: 893,753 (2.15%); _(+4 more codes)_ | 0.51% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `9` | 33,191 | 0.46% |
| `1968-1971` | _null/blank_ | 2,948,456 | 40.94% |
| `1972-1977` | `9` | 66,943 | 0.51% |
| `1972-1977` | _null/blank_ | 1,807,279 | 13.81% |
| `1978-1988` | `9` | 203,272 | 0.53% |
| `1978-1988` | _null/blank_ | 934,132 | 2.46% |
| `1989-2002` | `9` | 229,337 | 0.41% |
| `1989-2002` | `99` | 1,334,554 | 2.38% |
| `2003-2013` | `9` | 245,391 | 0.54% |
| `2003-2013` | `99` | 1,479,025 | 3.27% |
| `2003-2013` | _null/blank_ | 3,631,349 | 8.03% |
| `2014-2024` | `9` | 266,497 | 0.64% |
| `2014-2024` | `99` | 1,042,318 | 2.51% |
| `2014-2024` | _null/blank_ | 211,965 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`1`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`99`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`10`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`10`} _(codes ≥0.05% of an era)_

### `prenatal_care_start_trimester` <a id="c820-natality-prenatal_care_start_trimester"></a>

_Schema note:_ 1st|2nd|3rd|none|unknown

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1st`: 2,897,522 (40.23%); `2nd`: 1,022,680 (14.20%); `3rd`: 258,289 (3.59%); `none`: 74,612 (1.04%) | 40.94% |
| `1972-1977` | 13,086,752 | `1st`: 8,173,793 (62.46%); `2nd`: 2,426,776 (18.54%); `3rd`: 520,282 (3.98%); `none`: 158,622 (1.21%) | 13.81% |
| `1978-1988` | 38,007,797 | `1st`: 28,194,634 (74.18%); `2nd`: 6,790,198 (17.87%); `3rd`: 1,479,008 (3.89%); `none`: 609,825 (1.60%) | 2.46% |
| `1989-2002` | 56,068,430 | `1st`: 43,997,630 (78.47%); `2nd`: 8,223,933 (14.67%); `3rd`: 1,727,672 (3.08%); `unknown`: 1,334,554 (2.38%); `none`: 784,641 (1.40%) | 0.00% |
| `2003-2013` | 45,220,728 | `1st`: 30,865,064 (68.25%); `2nd`: 7,091,163 (15.68%); `3rd`: 1,572,863 (3.48%); `unknown`: 1,479,025 (3.27%); `none`: 581,264 (1.29%) | 8.03% |
| `2014-2024` | 41,576,190 | `1st`: 31,056,377 (74.70%); `2nd`: 6,667,122 (16.04%); `3rd`: 1,829,099 (4.40%); `unknown`: 1,042,318 (2.51%); `none`: 769,309 (1.85%) | 0.51% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 2,948,456 | 40.94% |
| `1972-1977` | _null/blank_ | 1,807,279 | 13.81% |
| `1978-1988` | _null/blank_ | 934,132 | 2.46% |
| `2003-2013` | _null/blank_ | 3,631,349 | 8.03% |
| `2014-2024` | _null/blank_ | 211,965 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`unknown`} _(codes ≥0.05% of an era)_

### `prenatal_visits` <a id="c820-natality-prenatal_visits"></a>

_Schema note:_ 0-98|99 — 99 indicates unknown/not stated. Cap differs by era (49 for 1990-2013; 98 for 2014+).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `12`: 10,269,341 (18.32%); `10`: 7,518,888 (13.41%); `14`: 4,643,301 (8.28%); `15`: 4,494,010 (8.02%); `13`: 4,376,709 (7.81%); `11`: 4,207,384 (7.50%); `9`: 3,155,282 (5.63%); `8`: 3,064,000 (5.46%); _(+43 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `12`: 7,710,069 (17.05%); `10`: 6,437,768 (14.24%); `11`: 3,853,539 (8.52%); `13`: 3,802,576 (8.41%); `14`: 3,482,534 (7.70%); `15`: 3,306,879 (7.31%); `9`: 2,851,201 (6.31%); `8`: 2,564,378 (5.67%); _(+43 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `12`: 6,291,714 (15.13%); `10`: 5,559,171 (13.37%); `11`: 4,220,522 (10.15%); `13`: 3,816,132 (9.18%); `14`: 3,119,722 (7.50%); `9`: 2,847,189 (6.85%); `8`: 2,408,992 (5.79%); `15`: 2,402,079 (5.78%); _(+92 more codes)_ | 0.51% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 3,155,282 | 5.63% |
| `1989-2002` | `99` | 1,776,870 | 3.17% |
| `2003-2013` | `9` | 2,851,201 | 6.31% |
| `2003-2013` | `99` | 1,552,411 | 3.43% |
| `2014-2024` | `9` | 2,847,189 | 6.85% |
| `2014-2024` | `98` | 56 | 0.00% |
| `2014-2024` | `99` | 994,716 | 2.39% |
| `2014-2024` | _null/blank_ | 211,965 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`0`, `1`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `2`, `20`, `21`, `22`, `23`, `24`, `25`, `3`, `30`, `4`, `5`, `6`, `7`, `8`, `9`, `99`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`26`, `27`, `28`} _(codes ≥0.05% of an era)_

### `smoking_any_during_pregnancy` <a id="c820-natality-smoking_any_during_pregnancy"></a>

_Schema note:_ true|false — 1990-2002 uses independent source field; 2003+ derives from intensity. 2009-2013 revised-only.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 37,702,053 (67.24%); `true`: 6,373,024 (11.37%) | 21.39% |
| `2003-2013` | 45,220,728 | `false`: 32,672,657 (72.25%); `true`: 3,474,883 (7.68%) | 20.06% |
| `2014-2024` | 41,576,190 | `false`: 38,774,799 (93.26%); `true`: 2,327,631 (5.60%) | 1.14% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 11,993,353 | 21.39% |
| `2003-2013` | _null/blank_ | 9,073,188 | 20.06% |
| `2014-2024` | _null/blank_ | 473,760 | 1.14% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `smoking_intensity_max_recode6` <a id="c820-natality-smoking_intensity_max_recode6"></a>

_Schema note:_ 0|1|2|3|4|5|6 — 2009-2013 revised-only.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `0`: 37,702,051 (67.24%); `6`: 12,465,902 (22.23%); `2`: 2,383,833 (4.25%); `3`: 1,774,182 (3.16%); `1`: 1,471,297 (2.62%); `4`: 260,081 (0.46%); `5`: 11,084 (0.02%) | 0.00% |
| `2003-2013` | 45,220,728 | `0`: 32,672,657 (72.25%); `6`: 4,793,361 (10.60%); `2`: 1,405,344 (3.11%); `1`: 1,126,816 (2.49%); `3`: 840,702 (1.86%); `4`: 87,641 (0.19%); `5`: 14,380 (0.03%) | 9.46% |
| `2014-2024` | 41,576,190 | `0`: 38,774,799 (93.26%); `2`: 906,450 (2.18%); `1`: 765,577 (1.84%); `3`: 583,142 (1.40%); `6`: 261,795 (0.63%); `4`: 56,983 (0.14%); `5`: 15,479 (0.04%) | 0.51% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `2003-2013` | _null/blank_ | 4,279,827 | 9.46% |
| `2014-2024` | _null/blank_ | 211,965 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`0`, `1`, `2`, `3`, `4`, `6`} _(codes ≥0.05% of an era)_

### `smoking_pre_pregnancy_recode6` <a id="c820-natality-smoking_pre_pregnancy_recode6"></a>

_Schema note:_ 0|1|2|3|4|5|6 — Not directly comparable to pregnancy smoking measures in earlier years.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `0`: 38,094,313 (91.63%); `2`: 1,010,580 (2.43%); `3`: 1,009,743 (2.43%); `1`: 801,731 (1.93%); `6`: 265,701 (0.64%); `4`: 152,431 (0.37%); `5`: 29,726 (0.07%) | 0.51% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 211,965 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`0`, `1`, `2`, `3`, `4`, `5`, `6`} _(codes ≥0.05% of an era)_

### `diabetes_any` <a id="c820-natality-diabetes_any"></a>

_Schema note:_ 1|2|8|9 — 1=yes; 2=no; 8=factor not on certificate (2000-2003 only, ~5-6k rows/year, per Nat200Xdoc.pdf p.46); 9=unknown/not classifiable. Source-field decision is per-year (not per-batch). Prefer diabetes_any_bool (derived) which maps 8…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `2`: 53,247,937 (94.97%); `1`: 1,440,320 (2.57%); `9`: 1,363,916 (2.43%); `8`: 16,257 (0.03%) | 0.00% |
| `2003-2013` | 45,220,728 | `2`: 42,939,971 (94.96%); `1`: 2,087,115 (4.62%); `9`: 187,500 (0.41%); `8`: 6,142 (0.01%) | 0.00% |
| `2014-2024` | 41,576,190 | `2`: 38,177,660 (91.83%); `1`: 3,343,700 (8.04%); `9`: 10,947 (0.03%) | 0.11% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 1,363,916 | 2.43% |
| `2003-2013` | `9` | 187,500 | 0.41% |
| `2014-2024` | `9` | 10,947 | 0.03% |
| `2014-2024` | _null/blank_ | 43,883 | 0.11% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`9`} _(codes ≥0.05% of an era)_

### `hypertension_chronic` <a id="c820-natality-hypertension_chronic"></a>

_Schema note:_ 1|2|8|9 — 1=yes; 2=no; 8=factor not on certificate (2000-2003 only, per Nat200Xdoc.pdf p.46); 9=unknown/not classifiable. Prefer hypertension_chronic_bool (derived) which maps 8 and 9 → null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `2`: 54,300,775 (96.85%); `9`: 1,363,916 (2.43%); `1`: 387,482 (0.69%); `8`: 16,257 (0.03%) | 0.00% |
| `2003-2013` | 45,220,728 | `2`: 44,484,310 (98.37%); `1`: 542,776 (1.20%); `9`: 187,500 (0.41%); `8`: 6,142 (0.01%) | 0.00% |
| `2014-2024` | 41,576,190 | `2`: 40,557,110 (97.55%); `1`: 964,250 (2.32%); `9`: 10,947 (0.03%) | 0.11% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 1,363,916 | 2.43% |
| `2003-2013` | `9` | 187,500 | 0.41% |
| `2014-2024` | `9` | 10,947 | 0.03% |
| `2014-2024` | _null/blank_ | 43,883 | 0.11% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`9`} _(codes ≥0.05% of an era)_

### `hypertension_gestational` <a id="c820-natality-hypertension_gestational"></a>

_Schema note:_ 1|2|8|9 — 1=yes; 2=no; 8=factor not on certificate (2000-2003 only, per Nat200Xdoc.pdf p.46); 9=unknown/not classifiable. Prefer hypertension_gestational_bool (derived) which maps 8 and 9 → null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `2`: 52,848,789 (94.26%); `1`: 1,839,468 (3.28%); `9`: 1,363,916 (2.43%); `8`: 16,257 (0.03%) | 0.00% |
| `2003-2013` | 45,220,728 | `2`: 43,166,032 (95.46%); `1`: 1,861,054 (4.12%); `9`: 187,500 (0.41%); `8`: 6,142 (0.01%) | 0.00% |
| `2014-2024` | 41,576,190 | `2`: 38,319,646 (92.17%); `1`: 3,201,714 (7.70%); `9`: 10,947 (0.03%) | 0.11% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 1,363,916 | 2.43% |
| `2003-2013` | `9` | 187,500 | 0.41% |
| `2014-2024` | `9` | 10,947 | 0.03% |
| `2014-2024` | _null/blank_ | 43,883 | 0.11% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`9`} _(codes ≥0.05% of an era)_

### `plurality_recode` <a id="c820-natality-plurality_recode"></a>

_Schema note:_ 1|2|3|4|5

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 3,465,124 (48.12%); `2`: 66,361 (0.92%); `3`: 1,028 (0.01%); `4`: 34 (0.00%); `5`: 9 (0.00%) | 50.95% |
| `1972-1977` | 13,086,752 | `1`: 12,837,419 (98.09%); `2`: 245,151 (1.87%); `3`: 3,962 (0.03%); `4`: 168 (0.00%); `5`: 52 (0.00%) | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 37,221,120 (97.93%); `2`: 769,405 (2.02%); `3`: 17,272 (0.05%) | 0.00% |
| `1989-2002` | 56,068,430 | `1`: 54,531,045 (97.26%); `2`: 1,460,649 (2.61%); `3`: 70,385 (0.13%); `4`: 5,548 (0.01%); `5`: 803 (0.00%) | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 43,677,573 (96.59%); `2`: 1,475,260 (3.26%); `3`: 63,331 (0.14%); `4`: 3,851 (0.01%); `5`: 713 (0.00%) | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 40,202,299 (96.70%); `2`: 1,336,402 (3.21%); `3`: 35,461 (0.09%); `4`: 1,831 (0.00%); `5`: 197 (0.00%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 3,669,003 | 50.95% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`3`} _(codes ≥0.05% of an era)_

### `infant_sex` <a id="c820-natality-infant_sex"></a>

_Schema note:_ M|F

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `M`: 3,694,154 (51.30%); `F`: 3,507,405 (48.70%) | 0.00% |
| `1972-1977` | 13,086,752 | `M`: 6,712,262 (51.29%); `F`: 6,374,490 (48.71%) | 0.00% |
| `1978-1988` | 38,007,797 | `M`: 19,478,663 (51.25%); `F`: 18,529,134 (48.75%) | 0.00% |
| `1989-2002` | 56,068,430 | `M`: 28,693,720 (51.18%); `F`: 27,374,710 (48.82%) | 0.00% |
| `2003-2013` | 45,220,728 | `M`: 23,144,604 (51.18%); `F`: 22,076,124 (48.82%) | 0.00% |
| `2014-2024` | 41,576,190 | `M`: 21,264,168 (51.15%); `F`: 20,312,022 (48.85%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `gestational_age_weeks` <a id="c820-natality-gestational_age_weeks"></a>

_Schema note:_ 17-47|99 — 99 indicates unknown/not stated. Series breaks at 2003 and 2014 transitions.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `40`: 1,294,054 (17.97%); `99`: 1,039,401 (14.43%); `39`: 840,453 (11.67%); `41`: 687,461 (9.55%); `38`: 487,036 (6.76%); `42`: 354,875 (4.93%); `37`: 237,878 (3.30%); `43`: 160,526 (2.23%); _(+24 more codes)_ | 20.97% |
| `1972-1977` | 13,086,752 | `99`: 2,142,462 (16.37%); `40`: 1,867,369 (14.27%); `39`: 1,598,682 (12.22%); `41`: 1,359,181 (10.39%); `38`: 889,964 (6.80%); `42`: 718,681 (5.49%); `37`: 431,383 (3.30%); `43`: 333,684 (2.55%); _(+24 more codes)_ | 20.35% |
| `1978-1988` | 38,007,797 | `40`: 7,637,129 (20.09%); `39`: 7,108,647 (18.70%); `41`: 5,296,905 (13.94%); `38`: 4,043,000 (10.64%); `99`: 3,500,216 (9.21%); `42`: 2,614,065 (6.88%); `37`: 1,958,393 (5.15%); `43`: 1,138,711 (3.00%); _(+24 more codes)_ | 0.51% |
| `1989-2002` | 56,068,430 | `39`: 12,790,210 (22.81%); `40`: 12,240,737 (21.83%); `38`: 8,307,968 (14.82%); `41`: 6,857,778 (12.23%); `37`: 4,149,339 (7.40%); `42`: 2,507,862 (4.47%); `36`: 2,221,266 (3.96%); `35`: 1,314,137 (2.34%); _(+24 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `39`: 12,185,631 (26.95%); `40`: 8,693,798 (19.23%); `38`: 8,156,448 (18.04%); `37`: 4,065,843 (8.99%); `41`: 3,861,305 (8.54%); `36`: 2,034,540 (4.50%); `42`: 1,259,689 (2.79%); `35`: 1,151,674 (2.55%); _(+24 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `39`: 15,658,559 (37.66%); `40`: 7,953,149 (19.13%); `38`: 6,961,472 (16.74%); `37`: 4,378,887 (10.53%); `41`: 2,279,321 (5.48%); `36`: 1,659,821 (3.99%); `35`: 802,563 (1.93%); `34`: 579,491 (1.39%); _(+24 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `99` | 1,039,401 | 14.43% |
| `1968-1971` | _null/blank_ | 1,510,225 | 20.97% |
| `1972-1977` | `99` | 2,142,462 | 16.37% |
| `1972-1977` | _null/blank_ | 2,663,463 | 20.35% |
| `1978-1988` | `99` | 3,500,216 | 9.21% |
| `1978-1988` | _null/blank_ | 193,520 | 0.51% |
| `1989-2002` | `99` | 583,437 | 1.04% |
| `2003-2013` | `99` | 178,149 | 0.39% |
| `2014-2024` | `99` | 33,664 | 0.08% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: dropped {`24`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: added {`22`, `23`, `24`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`22`, `43`, `44`, `45`, `46`, `47`} _(codes ≥0.05% of an era)_

### `gestational_age_weeks_source` <a id="c820-natality-gestational_age_weeks_source"></a>

_Schema note:_ lmp|combined|obstetric_estimate

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `lmp`: 5,691,334 (79.03%) | 20.97% |
| `1972-1977` | 13,086,752 | `lmp`: 10,423,289 (79.65%) | 20.35% |
| `1978-1988` | 38,007,797 | `lmp`: 37,814,277 (99.49%) | 0.51% |
| `1989-2002` | 56,068,430 | `lmp`: 56,068,430 (100.00%) | 0.00% |
| `2003-2013` | 45,220,728 | `combined`: 45,220,728 (100.00%) | 0.00% |
| `2014-2024` | 41,576,190 | `obstetric_estimate`: 41,576,190 (100.00%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 1,510,225 | 20.97% |
| `1972-1977` | _null/blank_ | 2,663,463 | 20.35% |
| `1978-1988` | _null/blank_ | 193,520 | 0.51% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`combined`}; dropped {`lmp`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`obstetric_estimate`}; dropped {`combined`} _(codes ≥0.05% of an era)_

### `preterm_recode3` <a id="c820-natality-preterm_recode3"></a>

_Schema note:_ 1|2|3 — 1=under 37 weeks; 2=37+; 3=not stated.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `2`: 2,919,395 (40.54%); `3`: 786,205 (10.92%); `1`: 304,566 (4.23%) | 44.32% |
| `1972-1977` | 13,086,752 | `2`: 7,587,842 (57.98%); `3`: 2,142,462 (16.37%); `1`: 743,386 (5.68%) | 19.97% |
| `1978-1988` | 38,007,797 | `2`: 31,197,440 (82.08%); `3`: 3,500,216 (9.21%); `1`: 3,310,141 (8.71%) | 0.00% |
| `1989-2002` | 56,068,430 | `2`: 49,262,854 (87.86%); `1`: 6,222,139 (11.10%); `3`: 583,437 (1.04%) | 0.00% |
| `2003-2013` | 45,220,728 | `2`: 39,545,565 (87.45%); `1`: 5,497,014 (12.16%); `3`: 178,149 (0.39%) | 0.00% |
| `2014-2024` | 41,576,190 | `2`: 37,357,286 (89.85%); `1`: 4,185,240 (10.07%); `3`: 33,664 (0.08%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 3,191,393 | 44.32% |
| `1972-1977` | _null/blank_ | 2,613,062 | 19.97% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `birthweight_grams` <a id="c820-natality-birthweight_grams"></a>

_Schema note:_ 227-8165|9999 — 9999 indicates not stated.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `3175`: 189,836 (2.64%); `3402`: 175,660 (2.44%); `3289`: 168,960 (2.35%); `3232`: 161,020 (2.24%); `3629`: 158,655 (2.20%); `3260`: 158,161 (2.20%); `3345`: 158,097 (2.20%); `3374`: 154,131 (2.14%); _(+3087 more codes)_ | 0.00% |
| `1972-1977` | 13,086,752 | `3175`: 318,216 (2.43%); `3402`: 310,876 (2.38%); `3289`: 299,334 (2.29%); `3345`: 288,885 (2.21%); `3629`: 285,723 (2.18%); `3232`: 284,304 (2.17%); `3260`: 283,998 (2.17%); `3374`: 279,783 (2.14%); _(+3999 more codes)_ | 0.00% |
| `1978-1988` | 38,007,797 | `3402`: 789,181 (2.08%); `3175`: 756,410 (1.99%); `3289`: 747,953 (1.97%); `3260`: 742,828 (1.95%); `3345`: 738,122 (1.94%); `3515`: 737,321 (1.94%); `3430`: 727,797 (1.91%); `3629`: 722,580 (1.90%); _(+6092 more codes)_ | 0.00% |
| `1989-2002` | 56,068,430 | `3402`: 947,687 (1.69%); `3430`: 942,822 (1.68%); `3260`: 939,590 (1.68%); `3345`: 937,271 (1.67%); `3515`: 912,308 (1.63%); `3175`: 894,208 (1.59%); `3289`: 891,092 (1.59%); `3374`: 867,442 (1.55%); _(+6392 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `3260`: 672,181 (1.49%); `3430`: 651,616 (1.44%); `3345`: 649,285 (1.44%); `3175`: 619,631 (1.37%); `3402`: 606,936 (1.34%); `3515`: 589,534 (1.30%); `3090`: 575,640 (1.27%); `3289`: 567,059 (1.25%); _(+6303 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `3260`: 448,356 (1.08%); `3430`: 431,064 (1.04%); `3090`: 385,765 (0.93%); `3600`: 366,876 (0.88%); `3345`: 343,664 (0.83%); `3175`: 333,412 (0.80%); `3515`: 309,995 (0.75%); `2920`: 300,816 (0.72%); _(+6376 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `999` | 2 | 0.00% |
| `1968-1971` | `9999` | 31,621 | 0.44% |
| `1972-1977` | `999` | 2 | 0.00% |
| `1972-1977` | `9999` | 32,999 | 0.25% |
| `1978-1988` | `999` | 30 | 0.00% |
| `1978-1988` | `9999` | 62,174 | 0.16% |
| `1989-2002` | `999` | 162 | 0.00% |
| `1989-2002` | `9999` | 62,687 | 0.11% |
| `2003-2013` | `999` | 252 | 0.00% |
| `2003-2013` | `9999` | 46,187 | 0.10% |
| `2014-2024` | `999` | 423 | 0.00% |
| `2014-2024` | `9999` | 36,961 | 0.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`4791`, `4820`}; dropped {`1531`, `1559`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: added {`2700`, `2800`, `2860`, `2880`, `2900`, `2940`, `2950`, `2960`, `2980`, `3000`, `3020`, `3040`, `3050`, `3060`, `3080`, `3100`, `3118`, `3120`, `3140`, `3150`, `3160`, `3170`, `3180`, `3200`, `3203`, `3210`, `3220`, `3230`, `3240`, `3250`, `3270`, `3280`, `3290`, `3300`, `3310`, `3320`, `3330`, `3340`, `3350`, `3360`, `3370`, `3380`, `3400`, `3410`, `3420`, `3440`, `3450`, `3460`, `3470`, `3480`, `3500`, `3520`, `3530`, `3540`, `3550`, `3560`, `3570`, `3580`, `3620`, `3630`, `3640`, `3650`, `3660`, `3680`, `3685`, `3700`, `3720`, `3740`, `3750`, `3760`, `3770`, `3780`, `3800`, `3820`, `3840`, `3860`, `3870`, `3880`, `3900`, `4000`}; dropped {`1361`, `1474`, `1588`, `1616`, `1644`, `1673`, `1729`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`2551`, `2636`, `2820`, `2840`, `2850`, `2870`, `2890`, `2910`, `2930`, `2970`, `2976`, `2990`, `3010`, `3030`, `3061`, `3070`, `3110`, `3130`, `3146`, `3190`, `3225`, `3231`, `3288`, `3316`, `3373`, `3375`, `3390`, `3445`, `3458`, `3490`, `3510`, `3543`, `3590`, `3610`, `3615`, `3628`, `3670`, `3690`, `3710`, `3713`, `3730`, `3790`, `3798`, `3810`, `3830`, `3850`, `3855`, `3890`, `3910`, `3920`, `3940`, `4025`, `4110`, `4252`, `4337`}; dropped {`1701`, `1758`, `2700`, `4734`, `4763`, `4791`, `4820`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`2664`, `2690`, `2700`, `2710`, `2720`, `2721`, `2730`, `2740`, `2749`, `2760`, `2770`, `2780`, `2790`, `2806`, `2810`, `2830`, `2885`, `2891`, `2895`, `2905`, `2915`, `2925`, `2935`, `2945`, `2955`, `2965`, `2975`, `2985`, `2995`, `3015`, `3025`, `3035`, `3045`, `3055`, `3065`, `3075`, `3085`, `3095`, `3105`, `3115`, `3125`, `3135`, `3145`, `3155`, `3165`, `3185`, `3195`, `3205`, `3215`, `3235`, `3245`, `3255`, `3265`, `3275`, `3285`, `3295`, `3305`, `3315`, `3325`, `3335`, `3355`, `3365`, `3385`, `3395`, `3401`, `3405`, `3415`, `3425`, `3435`, `3455`, `3465`, `3475`, `3485`, `3495`, `3505`, `3525`, `3535`, `3545`, `3555`, `3565`, `3575`, `3585`, `3595`, `3605`, `3625`, `3635`, `3645`, `3655`, `3665`, `3675`, `3695`, `3705`, `3715`, `3725`, `3735`, `3745`, `3755`, `3765`, `3775`, `3785`, `3883`, `3930`, `3950`, `3960`, `3970`, `3980`}; dropped {`1786`, `1843`, `4337`, `4593`, `4621`, `4649`, `4678`, `4706`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`2300`, `2320`, `2330`, `2340`, `2350`, `2360`, `2370`, `2380`, `2390`, `2400`, `2420`, `2430`, `2440`, `2450`, `2460`, `2470`, `2480`, `2490`, `2500`, `2510`, `2520`, `2530`, `2540`, `2550`, `2560`, `2570`, `2590`, `2600`, `2610`, `2620`, `2630`, `2640`, `2650`, `2660`, `2670`, `2680`, `2735`, `2745`, `2755`, `2765`, `2775`, `2785`, `2795`, `2805`, `2815`, `2825`, `2845`, `2855`, `2865`, `2875`, `3795`, `3805`, `3815`, `3825`, `3835`, `3845`, `3865`, `3875`, `3885`, `3895`, `3905`, `3915`, `3990`, `4010`, `4020`, `4030`, `4040`, `4050`, `4060`, `4070`, `4080`, `4090`, `4100`, `4120`, `4130`, `4140`, `4150`, `4160`, `4170`, `4180`, `4190`, `4200`, `4210`, `4220`, `4230`, `4280`}; dropped {`1814`, `1871`, `1899`, `1928`, `1956`, `1985`, `2013`, `2636`, `2664`, `2721`, `2749`, `2806`, `2891`, `3401`, `3798`, `3883`, `4253`, `4338`, `4451`, `4479`, `4508`, `4536`, `4564`} _(codes ≥0.05% of an era)_

### `delivery_method_recode` <a id="c820-natality-delivery_method_recode"></a>

_Schema note:_ 1990-2004: 1|2|3|4|9 (1=vaginal, 2=VBAC, 3=primary CS, 4=repeat CS, 9=not stated); 2005-2024: 1|2|9 (1=vaginal, 2=cesarean, 9=not stated) — Two coding frames with boundary at 2005 (NOT 2003). Cesarean binary crosswalk: codes 3+4 pre-2005…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `1`: 41,417,992 (73.87%); `3`: 7,679,548 (13.70%); `4`: 4,595,593 (8.20%); `2`: 1,328,671 (2.37%); `9`: 1,046,626 (1.87%) | 0.00% |
| `2003-2013` | 45,220,728 | `1`: 30,805,060 (68.12%); `2`: 11,960,703 (26.45%); `3`: 1,426,513 (3.15%); `4`: 885,558 (1.96%); `9`: 142,894 (0.32%) | 0.00% |
| `2014-2024` | 41,576,190 | `1`: 28,232,814 (67.91%); `2`: 13,312,484 (32.02%); `9`: 30,892 (0.07%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 1,046,626 | 1.87% |
| `2003-2013` | `9` | 142,894 | 0.32% |
| `2014-2024` | `9` | 30,892 | 0.07% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`1`, `2`, `3`, `4`, `9`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`3`, `4`} _(codes ≥0.05% of an era)_

### `apgar5` <a id="c820-natality-apgar5"></a>

_Schema note:_ 0-10|99 — 99 indicates unknown/not stated.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `9`: 34,259,509 (61.10%); `99`: 12,878,187 (22.97%); `10`: 4,588,126 (8.18%); `8`: 3,062,452 (5.46%); `7`: 653,668 (1.17%); `6`: 256,137 (0.46%); `5`: 112,264 (0.20%); `1`: 85,882 (0.15%); _(+4 more codes)_ | 0.00% |
| `2003-2013` | 45,220,728 | `9`: 34,937,950 (77.26%); `8`: 3,909,445 (8.65%); `99`: 3,188,091 (7.05%); `10`: 1,737,944 (3.84%); `7`: 724,935 (1.60%); `6`: 271,493 (0.60%); `5`: 139,879 (0.31%); `1`: 90,271 (0.20%); _(+4 more codes)_ | 0.00% |
| `2014-2024` | 41,576,190 | `9`: 34,215,083 (82.29%); `8`: 4,556,175 (10.96%); `10`: 893,233 (2.15%); `7`: 866,503 (2.08%); `6`: 343,507 (0.83%); `5`: 179,435 (0.43%); `99`: 173,906 (0.42%); `4`: 102,899 (0.25%); _(+4 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 34,259,509 | 61.10% |
| `1989-2002` | `99` | 12,878,187 | 22.97% |
| `2003-2013` | `9` | 34,937,950 | 77.26% |
| `2003-2013` | `99` | 3,188,091 | 7.05% |
| `2014-2024` | `9` | 34,215,083 | 82.29% |
| `2014-2024` | `99` | 173,906 | 0.42% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`0`, `1`, `10`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `99`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: dropped {`0`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`0`} _(codes ≥0.05% of an era)_

### `bmi_prepregnancy` <a id="c820-natality-bmi_prepregnancy"></a>

_Schema note:_ 13.0-69.9|null — Sentinel 99.9→null. Null for all years before 2014. Available only on revised 2003 certificate.

**(i) Historical-value distribution (per era)** — _continuous numeric: per-era summary statistics over raw non-null values (quantiles = nearest-rank on the weighted ECDF, rank ⌈p·N⌉; values formatted `%.6g`); documented sentinel codes are listed in (ii) and are **not** trimmed here_

| Era | n | non-null | null/blank | distinct | min | p25 | median | mean | p75 | max |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `1968-1971` | 7,201,559 | 0 | 100.00% | 0 | — | — | — | — | — | — |
| `1972-1977` | 13,086,752 | 0 | 100.00% | 0 | — | — | — | — | — | — |
| `1978-1988` | 38,007,797 | 0 | 100.00% | 0 | — | — | — | — | — | — |
| `1989-2002` | 56,068,430 | 0 | 100.00% | 0 | — | — | — | — | — | — |
| `2003-2013` | 45,220,728 | 0 | 100.00% | 0 | — | — | — | — | — | — |
| `2014-2024` | 41,576,190 | 40,321,196 | 3.02% | 570 | 13 | 22.3 | 25.7 | 27.2851 | 30.9 | 69.9 |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 1,254,994 | 3.02% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Continuous numeric variable — no discrete code frame; see the per-era summary statistics in (i). (A frequency/code-frame diff is not meaningful for a continuous measurement.)

### `bmi_prepregnancy_recode6` <a id="c820-natality-bmi_prepregnancy_recode6"></a>

_Schema note:_ 1|2|3|4|5|6 — 1=Underweight (<18.5); 2=Normal (18.5-24.9); 3=Overweight (25.0-29.9); 4=Obesity I (30.0-34.9); 5=Obesity II (35.0-39.9); 6=Extreme Obesity III (>=40.0). Sentinel 9→null. Null for all years before 2014.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `2`: 16,670,438 (40.10%); `3`: 10,813,906 (26.01%); `4`: 6,252,243 (15.04%); `5`: 3,104,494 (7.47%); `6`: 2,230,533 (5.36%); `1`: 1,249,582 (3.01%) | 3.02% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 1,254,994 | 3.02% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`1`, `2`, `3`, `4`, `5`, `6`} _(codes ≥0.05% of an era)_

### `father_age` <a id="c820-natality-father_age"></a>

_Schema note:_ 9-98|null — 99→null; range-clipped to 9-98. For categorical (5-year-bucket) father age that also covers unrevised-cert 2005-2013 rows, see father_age_cat_from_rec11.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `23`: 354,884 (4.93%); `24`: 352,548 (4.90%); `26`: 342,629 (4.76%); `25`: 340,676 (4.73%); `27`: 332,449 (4.62%); `22`: 315,768 (4.38%); `28`: 306,733 (4.26%); `29`: 264,688 (3.68%); _(+81 more codes)_ | 30.93% |
| `1972-1977` | 13,086,752 | `25`: 861,491 (6.58%); `26`: 851,778 (6.51%); `27`: 824,776 (6.30%); `24`: 803,464 (6.14%); `28`: 778,457 (5.95%); `23`: 751,001 (5.74%); `29`: 712,634 (5.45%); `22`: 654,589 (5.00%); _(+77 more codes)_ | 11.00% |
| `1978-1988` | 38,007,797 | `27`: 2,265,853 (5.96%); `28`: 2,255,320 (5.93%); `26`: 2,209,588 (5.81%); `29`: 2,166,846 (5.70%); `25`: 2,133,677 (5.61%); `30`: 2,074,719 (5.46%); `24`: 1,952,716 (5.14%); `31`: 1,848,932 (4.86%); _(+81 more codes)_ | 13.29% |
| `1989-2002` | 56,068,430 | `30`: 2,895,728 (5.16%); `29`: 2,857,599 (5.10%); `31`: 2,806,303 (5.01%); `28`: 2,764,635 (4.93%); `32`: 2,654,752 (4.73%); `27`: 2,629,735 (4.69%); `26`: 2,463,856 (4.39%); `33`: 2,450,942 (4.37%); _(+81 more codes)_ | 15.16% |
| `2003-2013` | 45,220,728 | `30`: 2,202,747 (4.87%); `31`: 2,184,971 (4.83%); `29`: 2,163,352 (4.78%); `32`: 2,114,440 (4.68%); `28`: 2,093,633 (4.63%); `33`: 2,003,378 (4.43%); `27`: 1,992,426 (4.41%); `26`: 1,877,330 (4.15%); _(+81 more codes)_ | 15.23% |
| `2014-2024` | 41,576,190 | `32`: 2,250,814 (5.41%); `31`: 2,245,804 (5.40%); `33`: 2,185,725 (5.26%); `30`: 2,175,188 (5.23%); `34`: 2,069,261 (4.98%); `29`: 2,051,274 (4.93%); `28`: 1,903,456 (4.58%); `35`: 1,901,973 (4.57%); _(+80 more codes)_ | 11.98% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `98` | 13 | 0.00% |
| `1968-1971` | _null/blank_ | 2,227,641 | 30.93% |
| `1972-1977` | _null/blank_ | 1,439,610 | 11.00% |
| `1978-1988` | `98` | 13 | 0.00% |
| `1978-1988` | _null/blank_ | 5,053,037 | 13.29% |
| `1989-2002` | `98` | 2 | 0.00% |
| `1989-2002` | _null/blank_ | 8,499,644 | 15.16% |
| `2003-2013` | `9` | 18 | 0.00% |
| `2003-2013` | `98` | 9 | 0.00% |
| `2003-2013` | _null/blank_ | 6,887,181 | 15.23% |
| `2014-2024` | `9` | 2 | 0.00% |
| `2014-2024` | `98` | 18 | 0.00% |
| `2014-2024` | _null/blank_ | 4,980,607 | 11.98% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`16`, `53`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: dropped {`53`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`53`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`54`, `55`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`56`} _(codes ≥0.05% of an era)_

### `father_age_cat_from_rec11` <a id="c820-natality-father_age_cat_from_rec11"></a>

_Schema note:_ <20|20-24|25-29|30-34|35-39|40+|null — Recovers categorical father age for 2012 + the cohort 2003-2004 era where raw single-year age is blank. Null for 1990-2002 and 2014+. C8.18 v4: cohort 2003-2004 added (5c-ii-b).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | `30-34`: 8,621,858 (19.07%); `25-29`: 8,251,784 (18.25%); `35-39`: 5,442,883 (12.04%); `20-24`: 5,190,632 (11.48%); `40+`: 3,336,423 (7.38%); `<20`: 1,106,921 (2.45%) | 29.35% |
| `2014-2024` | 41,576,190 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 13,270,227 | 29.35% |
| `2014-2024` | _null/blank_ | 41,576,190 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`20-24`, `25-29`, `30-34`, `35-39`, `40+`, `<20`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`20-24`, `25-29`, `30-34`, `35-39`, `40+`, `<20`} _(codes ≥0.05% of an era)_

### `birth_facility` <a id="c820-natality-birth_facility"></a>

_Schema note:_ hospital|birth_center|clinic_other|home|null — Coarse 4-category harmonization across eras.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | `hospital`: 6,725,283 (51.39%); `birth_center`: 666,264 (5.09%); `home`: 63,928 (0.49%); `clinic_other`: 9,442 (0.07%) | 42.96% |
| `1978-1988` | 38,007,797 | `hospital`: 37,588,835 (98.90%); `birth_center`: 393,230 (1.03%); `clinic_other`: 19,018 (0.05%) | 0.02% |
| `1989-2002` | 56,068,430 | `hospital`: 55,477,127 (98.95%); `home`: 349,168 (0.62%); `birth_center`: 180,693 (0.32%); `clinic_other`: 50,637 (0.09%) | 0.02% |
| `2003-2013` | 45,220,728 | `hospital`: 44,717,160 (98.89%); `home`: 316,603 (0.70%); `birth_center`: 153,982 (0.34%); `clinic_other`: 29,717 (0.07%) | 0.01% |
| `2014-2024` | 41,576,190 | `hospital`: 40,577,888 (97.60%); `home`: 495,600 (1.19%); `birth_center`: 241,762 (0.58%); `clinic_other`: 46,805 (0.11%) | 0.52% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 5,621,835 | 42.96% |
| `1978-1988` | _null/blank_ | 6,714 | 0.02% |
| `1989-2002` | _null/blank_ | 10,805 | 0.02% |
| `2003-2013` | _null/blank_ | 3,266 | 0.01% |
| `2014-2024` | _null/blank_ | 214,135 | 0.52% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`birth_center`, `clinic_other`, `home`, `hospital`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: dropped {`home`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`home`} _(codes ≥0.05% of an era)_

### `attendant_at_birth` <a id="c820-natality-attendant_at_birth"></a>

_Schema note:_ 1|2|3|4|5|null — 1=MD; 2=DO; 3=CNM; 4=other midwife; 5=other; 9→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `1`: 7,128,213 (98.98%); `3`: 46,968 (0.65%); `2`: 17,708 (0.25%); `4`: 8,670 (0.12%) | 0.00% |
| `1972-1977` | 13,086,752 | `1`: 12,939,702 (98.88%); `3`: 61,101 (0.47%); `4`: 44,730 (0.34%); `2`: 41,219 (0.31%) | 0.00% |
| `1978-1988` | 38,007,797 | `1`: 37,607,853 (98.95%); `3`: 165,970 (0.44%); `4`: 126,671 (0.33%); `2`: 107,303 (0.28%) | 0.00% |
| `1989-2002` | 56,068,430 | `1`: 50,150,595 (89.45%); `3`: 3,228,557 (5.76%); `2`: 2,058,482 (3.67%); `5`: 340,853 (0.61%); `4`: 230,706 (0.41%) | 0.11% |
| `2003-2013` | 45,220,728 | `1`: 38,840,268 (85.89%); `3`: 3,449,717 (7.63%); `2`: 2,356,900 (5.21%); `5`: 269,711 (0.60%); `4`: 264,301 (0.58%) | 0.09% |
| `2014-2024` | 41,576,190 | `1`: 33,148,541 (79.73%); `3`: 4,105,671 (9.88%); `2`: 3,479,700 (8.37%); `4`: 418,208 (1.01%); `5`: 396,993 (0.95%) | 0.07% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1989-2002` | _null/blank_ | 59,237 | 0.11% |
| `2003-2013` | _null/blank_ | 39,831 | 0.09% |
| `2014-2024` | _null/blank_ | 27,077 | 0.07% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`5`} _(codes ≥0.05% of an era)_

### `payment_source_recode` <a id="c820-natality-payment_source_recode"></a>

_Schema note:_ 1|2|3|4|null — 1=Medicaid; 2=Private insurance; 3=Self-pay; 4=Other. 9→null. Null for 2005-2008 (filler). Partial coverage 2009-2010 (2003-revision states) in V2 natality. Full coverage 2014+. **V3 LINKED CAVEAT**: 100% NULL for 2009-201…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | `2`: 7,505,867 (16.60%); `1`: 7,066,943 (15.63%); `4`: 813,853 (1.80%); `3`: 714,233 (1.58%) | 64.39% |
| `2014-2024` | 41,576,190 | `2`: 20,525,206 (49.37%); `1`: 17,246,357 (41.48%); `3`: 1,770,113 (4.26%); `4`: 1,517,710 (3.65%) | 1.24% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 29,119,832 | 64.39% |
| `2014-2024` | _null/blank_ | 516,804 | 1.24% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`1`, `2`, `3`, `4`} _(codes ≥0.05% of an era)_

### `prior_cesarean` <a id="c820-natality-prior_cesarean"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null. RF_CESAR is revised-certificate-only; coverage tracks cert-revision adoption (30.8% of rows populated in 2005 → 90.2% in 2013 → ~96-100% 2014+). Null for 1990-2004 — those public-use layou…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | `false`: 21,430,647 (47.39%); `true`: 3,356,616 (7.42%) | 45.19% |
| `2014-2024` | 41,576,190 | `false`: 34,963,738 (84.10%); `true`: 6,346,219 (15.26%) | 0.64% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 20,433,465 | 45.19% |
| `2014-2024` | _null/blank_ | 266,233 | 0.64% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `father_hispanic` <a id="c820-natality-father_hispanic"></a>

_Schema note:_ true|false|null — 0→false; 1-5→true; 9→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 38,631,415 (68.90%); `true`: 8,631,109 (15.39%) | 15.71% |
| `2003-2013` | 45,220,728 | `false`: 29,311,452 (64.82%); `true`: 9,359,442 (20.70%) | 14.48% |
| `2014-2024` | 41,576,190 | `false`: 27,467,726 (66.07%); `true`: 8,767,749 (21.09%) | 12.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 8,805,906 | 15.71% |
| `2003-2013` | _null/blank_ | 6,549,834 | 14.48% |
| `2014-2024` | _null/blank_ | 5,340,715 | 12.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `father_race_ethnicity_5` <a id="c820-natality-father_race_ethnicity_5"></a>

_Schema note:_ Hispanic|NH_white|NH_black|NH_other|null — Code 8 maps to NH_other for 1990-2002 (pre-2003) but null for 2003+ (semantic shift: code 8 = origin unknown).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `NH_white`: 30,449,941 (54.31%); `Hispanic`: 8,631,109 (15.39%); `NH_black`: 5,634,862 (10.05%); `NH_other`: 2,546,612 (4.54%) | 15.71% |
| `2003-2013` | 45,220,728 | `NH_white`: 21,621,275 (47.81%); `Hispanic`: 9,359,442 (20.70%); `NH_black`: 4,868,463 (10.77%); `NH_other`: 2,821,714 (6.24%) | 14.48% |
| `2014-2024` | 41,576,190 | `NH_white`: 18,945,055 (45.57%); `Hispanic`: 8,721,801 (20.98%); `NH_black`: 4,828,532 (11.61%); `NH_other`: 3,235,733 (7.78%) | 14.06% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 8,805,906 | 15.71% |
| `2003-2013` | _null/blank_ | 6,549,834 | 14.48% |
| `2014-2024` | _null/blank_ | 5,845,069 | 14.06% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`Hispanic`, `NH_black`, `NH_other`, `NH_white`} _(codes ≥0.05% of an era)_

### `father_education_cat4` <a id="c820-natality-father_education_cat4"></a>

_Schema note:_ lt_hs|hs_grad|some_college|ba_plus|null — Null 1995-2008 (dropped from public-use). Partial coverage 2009-2010 (2003-revision states only) in V2 natality. Uses _dmeduc_years_to_cat4 for 1990-1994; _meduc_to_cat4 for 2009+. **V3 LINKED CA…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `hs_grad`: 1,318,690 (18.31%); `lt_hs`: 843,511 (11.71%); `ba_plus`: 515,909 (7.16%); `some_college`: 468,282 (6.50%) | 56.31% |
| `1972-1977` | 13,086,752 | `hs_grad`: 3,670,219 (28.05%); `lt_hs`: 1,917,788 (14.65%); `ba_plus`: 1,718,666 (13.13%); `some_college`: 1,519,289 (11.61%) | 32.56% |
| `1978-1988` | 38,007,797 | `hs_grad`: 10,729,017 (28.23%); `ba_plus`: 6,067,997 (15.97%); `some_college`: 4,843,178 (12.74%); `lt_hs`: 4,165,693 (10.96%) | 32.10% |
| `1989-2002` | 56,068,430 | `hs_grad`: 7,567,804 (13.50%); `ba_plus`: 4,795,457 (8.55%); `some_college`: 3,682,587 (6.57%); `lt_hs`: 3,526,655 (6.29%) | 65.09% |
| `2003-2013` | 45,220,728 | `hs_grad`: 4,038,373 (8.93%); `ba_plus`: 3,860,352 (8.54%); `some_college`: 3,578,719 (7.91%); `lt_hs`: 2,393,424 (5.29%) | 69.33% |
| `2014-2024` | 41,576,190 | `ba_plus`: 11,237,287 (27.03%); `hs_grad`: 10,712,825 (25.77%); `some_college`: 9,116,363 (21.93%); `lt_hs`: 4,562,909 (10.97%) | 14.30% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 4,055,167 | 56.31% |
| `1972-1977` | _null/blank_ | 4,260,790 | 32.56% |
| `1978-1988` | _null/blank_ | 12,201,912 | 32.10% |
| `1989-2002` | _null/blank_ | 36,495,927 | 65.09% |
| `2003-2013` | _null/blank_ | 31,349,860 | 69.33% |
| `2014-2024` | _null/blank_ | 5,946,806 | 14.30% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `ca_anencephaly` <a id="c820-natality-ca_anencephaly"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,281,337 (99.29%); `true`: 4,025 (0.01%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_spina_bifida` <a id="c820-natality-ca_spina_bifida"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,279,685 (99.29%); `true`: 5,677 (0.01%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_cchd` <a id="c820-natality-ca_cchd"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,259,590 (99.24%); `true`: 25,772 (0.06%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `ca_cdh` <a id="c820-natality-ca_cdh"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,280,069 (99.29%); `true`: 5,293 (0.01%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_omphalocele` <a id="c820-natality-ca_omphalocele"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,281,276 (99.29%); `true`: 4,086 (0.01%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_gastroschisis` <a id="c820-natality-ca_gastroschisis"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,276,493 (99.28%); `true`: 8,869 (0.02%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_limb_reduction` <a id="c820-natality-ca_limb_reduction"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,280,171 (99.29%); `true`: 5,191 (0.01%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_cleft_lip` <a id="c820-natality-ca_cleft_lip"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,263,814 (99.25%); `true`: 21,548 (0.05%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `ca_cleft_palate` <a id="c820-natality-ca_cleft_palate"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,275,853 (99.28%); `true`: 9,509 (0.02%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_down_syndrome` <a id="c820-natality-ca_down_syndrome"></a>

_Schema note:_ true|false|null — C=Confirmed/P=Pending→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,263,589 (99.25%); `true`: 21,773 (0.05%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `ca_chromosomal_disorder` <a id="c820-natality-ca_chromosomal_disorder"></a>

_Schema note:_ true|false|null — C=Confirmed/P=Pending→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,267,190 (99.26%); `true`: 18,172 (0.04%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`} _(codes ≥0.05% of an era)_

### `ca_hypospadias` <a id="c820-natality-ca_hypospadias"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,262,171 (99.24%); `true`: 23,191 (0.06%) | 0.70% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 290,828 | 0.70% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `infection_gonorrhea` <a id="c820-natality-infection_gonorrhea"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,103,967 (98.86%); `true`: 119,812 (0.29%) | 0.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 352,411 | 0.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `infection_syphilis` <a id="c820-natality-infection_syphilis"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,151,239 (98.98%); `true`: 72,540 (0.17%) | 0.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 352,411 | 0.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `infection_chlamydia` <a id="c820-natality-infection_chlamydia"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 40,480,025 (97.36%); `true`: 743,754 (1.79%) | 0.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 352,411 | 0.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `infection_hep_b` <a id="c820-natality-infection_hep_b"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,140,828 (98.95%); `true`: 82,951 (0.20%) | 0.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 352,411 | 0.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `infection_hep_c` <a id="c820-natality-infection_hep_c"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 41,045,295 (98.72%); `true`: 178,484 (0.43%) | 0.85% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 352,411 | 0.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `prior_cesarean_count` <a id="c820-natality-prior_cesarean_count"></a>

_Schema note:_ 0-30|null — 0-30=count; 99→null. RF_CESARN is revised-certificate-only (same population as RF_CESAR / prior_cesarean); coverage tracks cert-revision adoption (30.7% populated in 2005 → 90.2% in 2013 → ~96-100% 2014+). Null for 1990-2004 …

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | `0`: 21,430,647 (47.39%); `1`: 2,383,735 (5.27%); `2`: 735,567 (1.63%); `3`: 166,734 (0.37%); `4`: 30,794 (0.07%); `5`: 6,277 (0.01%); `6`: 1,469 (0.00%); `7`: 432 (0.00%); _(+11 more codes)_ | 45.26% |
| `2014-2024` | 41,576,190 | `0`: 34,963,738 (84.10%); `1`: 4,359,115 (10.48%); `2`: 1,458,080 (3.51%); `3`: 401,328 (0.97%); `4`: 89,076 (0.21%); `5`: 19,919 (0.05%); `6`: 4,781 (0.01%); `7`: 1,253 (0.00%); _(+7 more codes)_ | 0.67% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | `9` | 162 | 0.00% |
| `2003-2013` | _null/blank_ | 20,464,707 | 45.26% |
| `2014-2024` | `9` | 134 | 0.00% |
| `2014-2024` | _null/blank_ | 278,333 | 0.67% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2002`→`2003-2013`: added {`0`, `1`, `2`, `3`, `4`} _(codes ≥0.05% of an era)_

### `fertility_enhancing_drugs` <a id="c820-natality-fertility_enhancing_drugs"></a>

_Schema note:_ true|false|null — Y→true; N→false; X(not applicable)/U→null. High null rate: X is the dominant code.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 472,911 (1.14%); `true`: 320,307 (0.77%) | 98.09% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 40,782,972 | 98.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `assisted_reproductive_tech` <a id="c820-natality-assisted_reproductive_tech"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `true`: 544,115 (1.31%); `false`: 249,103 (0.60%) | 98.09% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 40,782,972 | 98.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `pre_pregnancy_diabetes` <a id="c820-natality-pre_pregnancy_diabetes"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null. Finer-grained than diabetes_any; distinguishes pre-existing from gestational.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 40,893,422 (98.36%); `true`: 416,535 (1.00%) | 0.64% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 266,233 | 0.64% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `gestational_diabetes` <a id="c820-natality-gestational_diabetes"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null. Finer-grained than diabetes_any.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 38,397,407 (92.35%); `true`: 2,912,550 (7.01%) | 0.64% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 266,233 | 0.64% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `nicu_admission` <a id="c820-natality-nicu_admission"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 37,513,730 (90.23%); `true`: 3,787,689 (9.11%) | 0.66% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 274,771 | 0.66% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `weight_gain_pounds` <a id="c820-natality-weight_gain_pounds"></a>

_Schema note:_ 0-98|null — 0-97=pounds; 98=top-code (98+ lbs); 99→null. ~6k rows/year at 98. Not available before 2014.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `30`: 1,855,406 (4.46%); `20`: 1,530,340 (3.68%); `25`: 1,414,784 (3.40%); `35`: 1,273,325 (3.06%); `40`: 1,182,730 (2.84%); `0`: 1,137,218 (2.74%); `28`: 1,101,838 (2.65%); `27`: 1,062,222 (2.55%); _(+91 more codes)_ | 3.25% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | `9` | 331,017 | 0.80% |
| `2014-2024` | `98` | 62,083 | 0.15% |
| `2014-2024` | _null/blank_ | 1,350,853 | 3.25% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`0`, `1`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `2`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `3`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `4`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `49`, `5`, `50`, `51`, `52`, `53`, `54`, `55`, `56`, `57`, `58`, `59`, `6`, `60`, `61`, `62`, `63`, `64`, `65`, `66`, `67`, `68`, `69`, `7`, `70`, `71`, `72`, `73`, `74`, `75`, `76`, `77`, `8`, `80`, `9`, `98`} _(codes ≥0.05% of an era)_

### `induction_of_labor` <a id="c820-natality-induction_of_labor"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `false`: 29,500,137 (70.95%); `true`: 11,833,989 (28.46%) | 0.58% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 242,064 | 0.58% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `breastfed_at_discharge` <a id="c820-natality-breastfed_at_discharge"></a>

_Schema note:_ true|false|null — Y→true; N→false; U/blank→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | — | 100.00% |
| `2003-2013` | 45,220,728 | — | 100.00% |
| `2014-2024` | 41,576,190 | `true`: 29,855,533 (71.81%); `false`: 6,195,940 (14.90%) | 13.29% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 56,068,430 | 100.00% |
| `2003-2013` | _null/blank_ | 45,220,728 | 100.00% |
| `2014-2024` | _null/blank_ | 5,524,717 | 13.29% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2013`→`2014-2024`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `gestational_age_weeks_clean` <a id="c820-natality-gestational_age_weeks_clean"></a>

_Schema note:_ 12-47|null

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `40`: 1,294,054 (17.97%); `39`: 840,453 (11.67%); `41`: 687,461 (9.55%); `38`: 487,036 (6.76%); `42`: 354,875 (4.93%); `37`: 237,878 (3.30%); `43`: 160,526 (2.23%); `36`: 145,054 (2.01%); _(+23 more codes)_ | 35.40% |
| `1972-1977` | 13,086,752 | `40`: 1,867,369 (14.27%); `39`: 1,598,682 (12.22%); `41`: 1,359,181 (10.39%); `38`: 889,964 (6.80%); `42`: 718,681 (5.49%); `37`: 431,383 (3.30%); `43`: 333,684 (2.55%); `36`: 243,620 (1.86%); _(+23 more codes)_ | 36.72% |
| `1978-1988` | 38,007,797 | `40`: 7,637,129 (20.09%); `39`: 7,108,647 (18.70%); `41`: 5,296,905 (13.94%); `38`: 4,043,000 (10.64%); `42`: 2,614,065 (6.88%); `37`: 1,958,393 (5.15%); `43`: 1,138,711 (3.00%); `36`: 1,092,718 (2.87%); _(+23 more codes)_ | 9.72% |
| `1989-2002` | 56,068,430 | `39`: 12,790,210 (22.81%); `40`: 12,240,737 (21.83%); `38`: 8,307,968 (14.82%); `41`: 6,857,778 (12.23%); `37`: 4,149,339 (7.40%); `42`: 2,507,862 (4.47%); `36`: 2,221,266 (3.96%); `35`: 1,314,137 (2.34%); _(+23 more codes)_ | 1.04% |
| `2003-2013` | 45,220,728 | `39`: 12,185,631 (26.95%); `40`: 8,693,798 (19.23%); `38`: 8,156,448 (18.04%); `37`: 4,065,843 (8.99%); `41`: 3,861,305 (8.54%); `36`: 2,034,540 (4.50%); `42`: 1,259,689 (2.79%); `35`: 1,151,674 (2.55%); _(+23 more codes)_ | 0.39% |
| `2014-2024` | 41,576,190 | `39`: 15,658,559 (37.66%); `40`: 7,953,149 (19.13%); `38`: 6,961,472 (16.74%); `37`: 4,378,887 (10.53%); `41`: 2,279,321 (5.48%); `36`: 1,659,821 (3.99%); `35`: 802,563 (1.93%); `34`: 579,491 (1.39%); _(+23 more codes)_ | 0.08% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 2,549,626 | 35.40% |
| `1972-1977` | _null/blank_ | 4,805,925 | 36.72% |
| `1978-1988` | _null/blank_ | 3,693,736 | 9.72% |
| `1989-2002` | _null/blank_ | 583,437 | 1.04% |
| `2003-2013` | _null/blank_ | 178,149 | 0.39% |
| `2014-2024` | _null/blank_ | 33,664 | 0.08% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: dropped {`24`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: added {`22`, `23`, `24`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: dropped {`22`, `43`, `44`, `45`, `46`, `47`} _(codes ≥0.05% of an era)_

### `birthweight_grams_clean` <a id="c820-natality-birthweight_grams_clean"></a>

_Schema note:_ 100-8165|null

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `3175`: 189,836 (2.64%); `3402`: 175,660 (2.44%); `3289`: 168,960 (2.35%); `3232`: 161,020 (2.24%); `3629`: 158,655 (2.20%); `3260`: 158,161 (2.20%); `3345`: 158,097 (2.20%); `3374`: 154,131 (2.14%); _(+3086 more codes)_ | 0.44% |
| `1972-1977` | 13,086,752 | `3175`: 318,216 (2.43%); `3402`: 310,876 (2.38%); `3289`: 299,334 (2.29%); `3345`: 288,885 (2.21%); `3629`: 285,723 (2.18%); `3232`: 284,304 (2.17%); `3260`: 283,998 (2.17%); `3374`: 279,783 (2.14%); _(+3998 more codes)_ | 0.25% |
| `1978-1988` | 38,007,797 | `3402`: 789,181 (2.08%); `3175`: 756,410 (1.99%); `3289`: 747,953 (1.97%); `3260`: 742,828 (1.95%); `3345`: 738,122 (1.94%); `3515`: 737,321 (1.94%); `3430`: 727,797 (1.91%); `3629`: 722,580 (1.90%); _(+6091 more codes)_ | 0.16% |
| `1989-2002` | 56,068,430 | `3402`: 947,687 (1.69%); `3430`: 942,822 (1.68%); `3260`: 939,590 (1.68%); `3345`: 937,271 (1.67%); `3515`: 912,308 (1.63%); `3175`: 894,208 (1.59%); `3289`: 891,092 (1.59%); `3374`: 867,442 (1.55%); _(+6391 more codes)_ | 0.11% |
| `2003-2013` | 45,220,728 | `3260`: 672,181 (1.49%); `3430`: 651,616 (1.44%); `3345`: 649,285 (1.44%); `3175`: 619,631 (1.37%); `3402`: 606,936 (1.34%); `3515`: 589,534 (1.30%); `3090`: 575,640 (1.27%); `3289`: 567,059 (1.25%); _(+6302 more codes)_ | 0.10% |
| `2014-2024` | 41,576,190 | `3260`: 448,356 (1.08%); `3430`: 431,064 (1.04%); `3090`: 385,765 (0.93%); `3600`: 366,876 (0.88%); `3345`: 343,664 (0.83%); `3175`: 333,412 (0.80%); `3515`: 309,995 (0.75%); `2920`: 300,816 (0.72%); _(+6375 more codes)_ | 0.09% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | `999` | 2 | 0.00% |
| `1968-1971` | _null/blank_ | 31,621 | 0.44% |
| `1972-1977` | `999` | 2 | 0.00% |
| `1972-1977` | _null/blank_ | 32,999 | 0.25% |
| `1978-1988` | `999` | 30 | 0.00% |
| `1978-1988` | _null/blank_ | 62,174 | 0.16% |
| `1989-2002` | `999` | 162 | 0.00% |
| `1989-2002` | _null/blank_ | 62,687 | 0.11% |
| `2003-2013` | `999` | 252 | 0.00% |
| `2003-2013` | _null/blank_ | 46,187 | 0.10% |
| `2014-2024` | `999` | 423 | 0.00% |
| `2014-2024` | _null/blank_ | 36,961 | 0.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1968-1971`→`1972-1977`: added {`4791`, `4820`}; dropped {`1531`, `1559`} _(codes ≥0.05% of an era)_
- `1972-1977`→`1978-1988`: added {`2700`, `2800`, `2860`, `2880`, `2900`, `2940`, `2950`, `2960`, `2980`, `3000`, `3020`, `3040`, `3050`, `3060`, `3080`, `3100`, `3118`, `3120`, `3140`, `3150`, `3160`, `3170`, `3180`, `3200`, `3203`, `3210`, `3220`, `3230`, `3240`, `3250`, `3270`, `3280`, `3290`, `3300`, `3310`, `3320`, `3330`, `3340`, `3350`, `3360`, `3370`, `3380`, `3400`, `3410`, `3420`, `3440`, `3450`, `3460`, `3470`, `3480`, `3500`, `3520`, `3530`, `3540`, `3550`, `3560`, `3570`, `3580`, `3620`, `3630`, `3640`, `3650`, `3660`, `3680`, `3685`, `3700`, `3720`, `3740`, `3750`, `3760`, `3770`, `3780`, `3800`, `3820`, `3840`, `3860`, `3870`, `3880`, `3900`, `4000`}; dropped {`1361`, `1474`, `1588`, `1616`, `1644`, `1673`, `1729`} _(codes ≥0.05% of an era)_
- `1978-1988`→`1989-2002`: added {`2551`, `2636`, `2820`, `2840`, `2850`, `2870`, `2890`, `2910`, `2930`, `2970`, `2976`, `2990`, `3010`, `3030`, `3061`, `3070`, `3110`, `3130`, `3146`, `3190`, `3225`, `3231`, `3288`, `3316`, `3373`, `3375`, `3390`, `3445`, `3458`, `3490`, `3510`, `3543`, `3590`, `3610`, `3615`, `3628`, `3670`, `3690`, `3710`, `3713`, `3730`, `3790`, `3798`, `3810`, `3830`, `3850`, `3855`, `3890`, `3910`, `3920`, `3940`, `4025`, `4110`, `4252`, `4337`}; dropped {`1701`, `1758`, `2700`, `4734`, `4763`, `4791`, `4820`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: added {`2664`, `2690`, `2700`, `2710`, `2720`, `2721`, `2730`, `2740`, `2749`, `2760`, `2770`, `2780`, `2790`, `2806`, `2810`, `2830`, `2885`, `2891`, `2895`, `2905`, `2915`, `2925`, `2935`, `2945`, `2955`, `2965`, `2975`, `2985`, `2995`, `3015`, `3025`, `3035`, `3045`, `3055`, `3065`, `3075`, `3085`, `3095`, `3105`, `3115`, `3125`, `3135`, `3145`, `3155`, `3165`, `3185`, `3195`, `3205`, `3215`, `3235`, `3245`, `3255`, `3265`, `3275`, `3285`, `3295`, `3305`, `3315`, `3325`, `3335`, `3355`, `3365`, `3385`, `3395`, `3401`, `3405`, `3415`, `3425`, `3435`, `3455`, `3465`, `3475`, `3485`, `3495`, `3505`, `3525`, `3535`, `3545`, `3555`, `3565`, `3575`, `3585`, `3595`, `3605`, `3625`, `3635`, `3645`, `3655`, `3665`, `3675`, `3695`, `3705`, `3715`, `3725`, `3735`, `3745`, `3755`, `3765`, `3775`, `3785`, `3883`, `3930`, `3950`, `3960`, `3970`, `3980`}; dropped {`1786`, `1843`, `4337`, `4593`, `4621`, `4649`, `4678`, `4706`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`2300`, `2320`, `2330`, `2340`, `2350`, `2360`, `2370`, `2380`, `2390`, `2400`, `2420`, `2430`, `2440`, `2450`, `2460`, `2470`, `2480`, `2490`, `2500`, `2510`, `2520`, `2530`, `2540`, `2550`, `2560`, `2570`, `2590`, `2600`, `2610`, `2620`, `2630`, `2640`, `2650`, `2660`, `2670`, `2680`, `2735`, `2745`, `2755`, `2765`, `2775`, `2785`, `2795`, `2805`, `2815`, `2825`, `2845`, `2855`, `2865`, `2875`, `3795`, `3805`, `3815`, `3825`, `3835`, `3845`, `3865`, `3875`, `3885`, `3895`, `3905`, `3915`, `3990`, `4010`, `4020`, `4030`, `4040`, `4050`, `4060`, `4070`, `4080`, `4090`, `4100`, `4120`, `4130`, `4140`, `4150`, `4160`, `4170`, `4180`, `4190`, `4200`, `4210`, `4220`, `4230`, `4280`}; dropped {`1814`, `1871`, `1899`, `1928`, `1956`, `1985`, `2013`, `2636`, `2664`, `2721`, `2749`, `2806`, `2891`, `3401`, `3798`, `3883`, `4253`, `4338`, `4451`, `4479`, `4508`, `4536`, `4564`} _(codes ≥0.05% of an era)_

### `apgar5_clean` <a id="c820-natality-apgar5_clean"></a>

_Schema note:_ 0-10|null — Sentinel 99→null.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `9`: 34,259,509 (61.10%); `10`: 4,588,126 (8.18%); `8`: 3,062,452 (5.46%); `7`: 653,668 (1.17%); `6`: 256,137 (0.46%); `5`: 112,264 (0.20%); `1`: 85,882 (0.15%); `4`: 60,573 (0.11%); _(+3 more codes)_ | 22.97% |
| `2003-2013` | 45,220,728 | `9`: 34,937,950 (77.26%); `8`: 3,909,445 (8.65%); `10`: 1,737,944 (3.84%); `7`: 724,935 (1.60%); `6`: 271,493 (0.60%); `5`: 139,879 (0.31%); `1`: 90,271 (0.20%); `4`: 81,585 (0.18%); _(+3 more codes)_ | 7.05% |
| `2014-2024` | 41,576,190 | `9`: 34,215,083 (82.29%); `8`: 4,556,175 (10.96%); `10`: 893,233 (2.15%); `7`: 866,503 (2.08%); `6`: 343,507 (0.83%); `5`: 179,435 (0.43%); `4`: 102,899 (0.25%); `1`: 84,715 (0.20%); _(+3 more codes)_ | 0.42% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | `9` | 34,259,509 | 61.10% |
| `1989-2002` | _null/blank_ | 12,878,187 | 22.97% |
| `2003-2013` | `9` | 34,937,950 | 77.26% |
| `2003-2013` | _null/blank_ | 3,188,091 | 7.05% |
| `2014-2024` | `9` | 34,215,083 | 82.29% |
| `2014-2024` | _null/blank_ | 173,906 | 0.42% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`0`, `1`, `10`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`} _(codes ≥0.05% of an era)_
- `1989-2002`→`2003-2013`: dropped {`0`} _(codes ≥0.05% of an era)_
- `2003-2013`→`2014-2024`: added {`0`} _(codes ≥0.05% of an era)_

### `low_birthweight` <a id="c820-natality-low_birthweight"></a>

_Schema note:_ true|false — Null when birthweight is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `false`: 6,598,882 (91.63%); `true`: 571,056 (7.93%) | 0.44% |
| `1972-1977` | 13,086,752 | `false`: 12,090,361 (92.39%); `true`: 963,392 (7.36%) | 0.25% |
| `1978-1988` | 38,007,797 | `false`: 35,342,935 (92.99%); `true`: 2,602,688 (6.85%) | 0.16% |
| `1989-2002` | 56,068,430 | `false`: 51,880,227 (92.53%); `true`: 4,125,516 (7.36%) | 0.11% |
| `2003-2013` | 45,220,728 | `false`: 41,509,075 (91.79%); `true`: 3,665,466 (8.11%) | 0.10% |
| `2014-2024` | 41,576,190 | `false`: 38,085,346 (91.60%); `true`: 3,453,883 (8.31%) | 0.09% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 31,621 | 0.44% |
| `1972-1977` | _null/blank_ | 32,999 | 0.25% |
| `1978-1988` | _null/blank_ | 62,174 | 0.16% |
| `1989-2002` | _null/blank_ | 62,687 | 0.11% |
| `2003-2013` | _null/blank_ | 46,187 | 0.10% |
| `2014-2024` | _null/blank_ | 36,961 | 0.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `very_low_birthweight` <a id="c820-natality-very_low_birthweight"></a>

_Schema note:_ true|false — Null when birthweight is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `false`: 7,083,948 (98.37%); `true`: 85,990 (1.19%) | 0.44% |
| `1972-1977` | 13,086,752 | `false`: 12,902,780 (98.59%); `true`: 150,973 (1.15%) | 0.25% |
| `1978-1988` | 38,007,797 | `false`: 37,493,333 (98.65%); `true`: 452,290 (1.19%) | 0.16% |
| `1989-2002` | 56,068,430 | `false`: 55,239,656 (98.52%); `true`: 766,087 (1.37%) | 0.11% |
| `2003-2013` | 45,220,728 | `false`: 44,516,598 (98.44%); `true`: 657,943 (1.45%) | 0.10% |
| `2014-2024` | 41,576,190 | `false`: 40,968,001 (98.54%); `true`: 571,228 (1.37%) | 0.09% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 31,621 | 0.44% |
| `1972-1977` | _null/blank_ | 32,999 | 0.25% |
| `1978-1988` | _null/blank_ | 62,174 | 0.16% |
| `1989-2002` | _null/blank_ | 62,687 | 0.11% |
| `2003-2013` | _null/blank_ | 46,187 | 0.10% |
| `2014-2024` | _null/blank_ | 36,961 | 0.09% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `preterm_lt37` <a id="c820-natality-preterm_lt37"></a>

_Schema note:_ true|false — Null when gestational age is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `false`: 4,218,269 (58.57%); `true`: 433,664 (6.02%) | 35.40% |
| `1972-1977` | 13,086,752 | `false`: 7,537,441 (57.60%); `true`: 743,386 (5.68%) | 36.72% |
| `1978-1988` | 38,007,797 | `false`: 31,003,920 (81.57%); `true`: 3,310,141 (8.71%) | 9.72% |
| `1989-2002` | 56,068,430 | `false`: 49,262,854 (87.86%); `true`: 6,222,139 (11.10%) | 1.04% |
| `2003-2013` | 45,220,728 | `false`: 39,545,565 (87.45%); `true`: 5,497,014 (12.16%) | 0.39% |
| `2014-2024` | 41,576,190 | `false`: 37,357,286 (89.85%); `true`: 4,185,240 (10.07%) | 0.08% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 2,549,626 | 35.40% |
| `1972-1977` | _null/blank_ | 4,805,925 | 36.72% |
| `1978-1988` | _null/blank_ | 3,693,736 | 9.72% |
| `1989-2002` | _null/blank_ | 583,437 | 1.04% |
| `2003-2013` | _null/blank_ | 178,149 | 0.39% |
| `2014-2024` | _null/blank_ | 33,664 | 0.08% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `very_preterm_lt32` <a id="c820-natality-very_preterm_lt32"></a>

_Schema note:_ true|false — Null when gestational age is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `false`: 4,569,284 (63.45%); `true`: 82,649 (1.15%) | 35.40% |
| `1972-1977` | 13,086,752 | `false`: 8,143,064 (62.22%); `true`: 137,763 (1.05%) | 36.72% |
| `1978-1988` | 38,007,797 | `false`: 33,681,816 (88.62%); `true`: 632,245 (1.66%) | 9.72% |
| `1989-2002` | 56,068,430 | `false`: 54,413,450 (97.05%); `true`: 1,071,543 (1.91%) | 1.04% |
| `2003-2013` | 45,220,728 | `false`: 44,150,801 (97.63%); `true`: 891,778 (1.97%) | 0.39% |
| `2014-2024` | 41,576,190 | `false`: 40,888,788 (98.35%); `true`: 653,738 (1.57%) | 0.08% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 2,549,626 | 35.40% |
| `1972-1977` | _null/blank_ | 4,805,925 | 36.72% |
| `1978-1988` | _null/blank_ | 3,693,736 | 9.72% |
| `1989-2002` | _null/blank_ | 583,437 | 1.04% |
| `2003-2013` | _null/blank_ | 178,149 | 0.39% |
| `2014-2024` | _null/blank_ | 33,664 | 0.08% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `singleton` <a id="c820-natality-singleton"></a>

_Schema note:_ true|false — Null when plurality_recode is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `true`: 3,465,124 (48.12%); `false`: 67,432 (0.94%) | 50.95% |
| `1972-1977` | 13,086,752 | `true`: 12,837,419 (98.09%); `false`: 249,333 (1.91%) | 0.00% |
| `1978-1988` | 38,007,797 | `true`: 37,221,120 (97.93%); `false`: 786,677 (2.07%) | 0.00% |
| `1989-2002` | 56,068,430 | `true`: 54,531,045 (97.26%); `false`: 1,537,385 (2.74%) | 0.00% |
| `2003-2013` | 45,220,728 | `true`: 43,677,573 (96.59%); `false`: 1,543,155 (3.41%) | 0.00% |
| `2014-2024` | 41,576,190 | `true`: 40,202,299 (96.70%); `false`: 1,373,891 (3.30%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 3,669,003 | 50.95% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `maternal_age_cat` <a id="c820-natality-maternal_age_cat"></a>

_Schema note:_ <20|20-24|25-29|30-34|35-39|40+

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `20-24`: 2,720,900 (37.78%); `25-29`: 1,903,401 (26.43%); `<20`: 1,256,847 (17.45%); `30-34`: 839,939 (11.66%); `35-39`: 369,857 (5.14%); `40+`: 110,615 (1.54%) | 0.00% |
| `1972-1977` | 13,086,752 | `20-24`: 4,576,199 (34.97%); `25-29`: 3,862,807 (29.52%); `<20`: 2,443,065 (18.67%); `30-34`: 1,589,422 (12.15%); `35-39`: 494,868 (3.78%); `40+`: 120,391 (0.92%) | 0.00% |
| `1978-1988` | 38,007,797 | `25-29`: 11,948,667 (31.44%); `20-24`: 11,913,495 (31.34%); `30-34`: 6,616,021 (17.41%); `<20`: 5,290,113 (13.92%); `35-39`: 1,942,793 (5.11%); `40+`: 296,708 (0.78%) | 0.00% |
| `1989-2002` | 56,068,430 | `25-29`: 15,748,991 (28.09%); `20-24`: 14,246,377 (25.41%); `30-34`: 12,625,691 (22.52%); `<20`: 6,989,275 (12.47%); `35-39`: 5,431,460 (9.69%); `40+`: 1,026,636 (1.83%) | 0.00% |
| `2003-2013` | 45,220,728 | `25-29`: 12,605,645 (27.88%); `20-24`: 11,034,056 (24.40%); `30-34`: 10,738,731 (23.75%); `35-39`: 5,283,397 (11.68%); `<20`: 4,310,112 (9.53%); `40+`: 1,248,787 (2.76%) | 0.00% |
| `2014-2024` | 41,576,190 | `30-34`: 12,104,150 (29.11%); `25-29`: 11,816,028 (28.42%); `20-24`: 7,927,330 (19.07%); `35-39`: 6,284,881 (15.12%); `<20`: 1,987,038 (4.78%); `40+`: 1,456,763 (3.50%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `father_age_cat` <a id="c820-natality-father_age_cat"></a>

_Schema note:_ <20|20-24|25-29|30-34|35-39|40+ — Null when father_age is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | `25-29`: 1,587,175 (22.04%); `20-24`: 1,480,862 (20.56%); `30-34`: 881,842 (12.25%); `35-39`: 437,773 (6.08%); `40+`: 314,829 (4.37%); `<20`: 271,437 (3.77%) | 30.93% |
| `1972-1977` | 13,086,752 | `25-29`: 4,029,136 (30.79%); `20-24`: 3,241,033 (24.77%); `30-34`: 2,261,403 (17.28%); `35-39`: 902,929 (6.90%); `<20`: 640,984 (4.90%); `40+`: 571,657 (4.37%) | 11.00% |
| `1978-1988` | 38,007,797 | `25-29`: 11,031,284 (29.02%); `30-34`: 8,199,054 (21.57%); `20-24`: 7,377,714 (19.41%); `35-39`: 3,494,177 (9.19%); `40+`: 1,636,453 (4.31%); `<20`: 1,216,078 (3.20%) | 13.29% |
| `1989-2002` | 56,068,430 | `30-34`: 13,022,657 (23.23%); `25-29`: 13,009,390 (23.20%); `20-24`: 8,436,663 (15.05%); `35-39`: 7,384,139 (13.17%); `40+`: 3,834,528 (6.84%); `<20`: 1,881,409 (3.36%) | 15.16% |
| `2003-2013` | 45,220,728 | `30-34`: 10,357,518 (22.90%); `25-29`: 9,867,205 (21.82%); `35-39`: 6,513,900 (14.40%); `20-24`: 6,294,376 (13.92%); `40+`: 3,972,851 (8.79%); `<20`: 1,327,697 (2.94%) | 15.23% |
| `2014-2024` | 41,576,190 | `30-34`: 10,926,792 (26.28%); `25-29`: 8,704,689 (20.94%); `35-39`: 7,374,017 (17.74%); `20-24`: 4,501,050 (10.83%); `40+`: 4,391,111 (10.56%); `<20`: 697,924 (1.68%) | 11.98% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 2,227,641 | 30.93% |
| `1972-1977` | _null/blank_ | 1,439,610 | 11.00% |
| `1978-1988` | _null/blank_ | 5,053,037 | 13.29% |
| `1989-2002` | _null/blank_ | 8,499,644 | 15.16% |
| `2003-2013` | _null/blank_ | 6,887,181 | 15.23% |
| `2014-2024` | _null/blank_ | 4,980,607 | 11.98% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `diabetes_any_bool` <a id="c820-natality-diabetes_any_bool"></a>

_Schema note:_ true|false|null — Null when unknown (sentinel 9 or pre-2004 code 8 "factor not on certificate") or source field is missing. Preferred over diabetes_any for downstream analysis — avoids sentinel codes passing IS NOT NULL filters.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 53,247,937 (94.97%); `true`: 1,440,320 (2.57%) | 2.46% |
| `2003-2013` | 45,220,728 | `false`: 42,939,971 (94.96%); `true`: 2,087,115 (4.62%) | 0.43% |
| `2014-2024` | 41,576,190 | `false`: 38,177,660 (91.83%); `true`: 3,343,700 (8.04%) | 0.13% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 1,380,173 | 2.46% |
| `2003-2013` | _null/blank_ | 193,642 | 0.43% |
| `2014-2024` | _null/blank_ | 54,830 | 0.13% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `hypertension_chronic_bool` <a id="c820-natality-hypertension_chronic_bool"></a>

_Schema note:_ true|false|null — Null when unknown (sentinel 9 or pre-2004 code 8 "factor not on certificate") or source field is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 54,300,775 (96.85%); `true`: 387,482 (0.69%) | 2.46% |
| `2003-2013` | 45,220,728 | `false`: 44,484,310 (98.37%); `true`: 542,776 (1.20%) | 0.43% |
| `2014-2024` | 41,576,190 | `false`: 40,557,110 (97.55%); `true`: 964,250 (2.32%) | 0.13% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 1,380,173 | 2.46% |
| `2003-2013` | _null/blank_ | 193,642 | 0.43% |
| `2014-2024` | _null/blank_ | 54,830 | 0.13% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `hypertension_gestational_bool` <a id="c820-natality-hypertension_gestational_bool"></a>

_Schema note:_ true|false|null — Null when unknown (sentinel 9 or pre-2004 code 8 "factor not on certificate") or source field is missing.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1968-1971` | 7,201,559 | — | 100.00% |
| `1972-1977` | 13,086,752 | — | 100.00% |
| `1978-1988` | 38,007,797 | — | 100.00% |
| `1989-2002` | 56,068,430 | `false`: 52,848,789 (94.26%); `true`: 1,839,468 (3.28%) | 2.46% |
| `2003-2013` | 45,220,728 | `false`: 43,166,032 (95.46%); `true`: 1,861,054 (4.12%) | 0.43% |
| `2014-2024` | 41,576,190 | `false`: 38,319,646 (92.17%); `true`: 3,201,714 (7.70%) | 0.13% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1968-1971` | _null/blank_ | 7,201,559 | 100.00% |
| `1972-1977` | _null/blank_ | 13,086,752 | 100.00% |
| `1978-1988` | _null/blank_ | 38,007,797 | 100.00% |
| `1989-2002` | _null/blank_ | 1,380,173 | 2.46% |
| `2003-2013` | _null/blank_ | 193,642 | 0.43% |
| `2014-2024` | _null/blank_ | 54,830 | 0.13% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1978-1988`→`1989-2002`: added {`false`, `true`} _(codes ≥0.05% of an era)_

## Appendix C8.20 — Per-variable historical evidence (auto-generated)

> Auto-generated by `scripts/_build_codebook_extensions.py` — do **not** hand-edit; regenerate. Every count below is derived from the gate-verified parquet; era boundaries are documented NCHS layout constants (see `COMPARABILITY.md` + the layout-source CSVs + the C8.16/C8.17/C8.18/C8.2 receipts).
>
> Provenance: natality v3.0.0 derived `natality_v2_harmonized_derived.parquet` sha256[:12]=`acb5c48a9abf` · 201,161,456 rows; linked v4.0.0 derived `natality_v3_linked_harmonized_derived.parquet` sha256[:12]=`f630d8cf20db` · 149,386,620 rows (1992-1994 permanent NCHS-linkage gap) · builder `scripts/_build_codebook_extensions.py` — linked-v4 death-side columns (1983-2023; 1992-1994 gap)
>
> Era partition: `1983-1988` · `1989-2004` · `2005-2013` · `2014-2015` · `2016-2023`

**Variable index:** [`infant_death`](#c820-natality-linked-infant_death) · [`age_at_death_days`](#c820-natality-linked-age_at_death_days) · [`age_at_death_recode5`](#c820-natality-linked-age_at_death_recode5) · [`underlying_cause_icd10`](#c820-natality-linked-underlying_cause_icd10) · [`cause_recode_130`](#c820-natality-linked-cause_recode_130) · [`underlying_cause_icd9`](#c820-natality-linked-underlying_cause_icd9) · [`cause_recode_61`](#c820-natality-linked-cause_recode_61) · [`manner_of_death`](#c820-natality-linked-manner_of_death) · [`record_weight`](#c820-natality-linked-record_weight) · [`link_segment`](#c820-natality-linked-link_segment) · [`neonatal_death`](#c820-natality-linked-neonatal_death) · [`postneonatal_death`](#c820-natality-linked-postneonatal_death) · [`cause_group`](#c820-natality-linked-cause_group)

### `infant_death` <a id="c820-natality-linked-infant_death"></a>

_Schema note:_ true|false — v4 linked cohort (C8.18). 1983-1988 keyless era: infant_death is NULL on den / True on num — the cohort IMR there = count(link_segment='num') / count(link_segment='den') per stratum, NOT a per-birth infant_death filter (the …

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | `true`: 230,102 (1.04%) | 98.96% |
| `1989-2004` | 52,253,538 | `false`: 51,865,677 (99.26%); `true`: 387,861 (0.74%) | 0.00% |
| `2005-2013` | 37,006,070 | `false`: 36,773,396 (99.37%); `true`: 232,674 (0.63%) | 0.00% |
| `2014-2015` | 7,986,908 | `false`: 7,940,259 (99.42%); `true`: 46,649 (0.58%) | 0.00% |
| `2016-2023` | 29,950,846 | `false`: 29,784,233 (99.44%); `true`: 166,613 (0.56%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 21,959,156 | 98.96% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`false`} _(codes ≥0.05% of an era)_

### `age_at_death_days` <a id="c820-natality-linked-age_at_death_days"></a>

_Schema note:_ 0-365|null — v4 linked cohort. NULL for ALL 1983-1988 — the keyless num segment carries the AGER5 recode only, no day-precise AGED (5c-iii). Null for survivors. For 1983-1988 age-at-death use age_at_death_recode5.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `0`: 151,437 (0.29%); `1`: 17,398 (0.03%); `2`: 12,935 (0.02%); `3`: 8,325 (0.02%); `4`: 5,852 (0.01%); `5`: 4,731 (0.01%); `7`: 4,177 (0.01%); `6`: 4,150 (0.01%); _(+358 more codes)_ | 99.26% |
| `2005-2013` | 37,006,070 | `0`: 94,090 (0.25%); `1`: 9,234 (0.02%); `2`: 7,062 (0.02%); `3`: 4,431 (0.01%); `4`: 3,353 (0.01%); `5`: 2,781 (0.01%); `6`: 2,531 (0.01%); `7`: 2,487 (0.01%); _(+358 more codes)_ | 99.37% |
| `2014-2015` | 7,986,908 | `0`: 19,152 (0.24%); `1`: 1,955 (0.02%); `2`: 1,413 (0.02%); `3`: 896 (0.01%); `4`: 690 (0.01%); `5`: 569 (0.01%); `7`: 505 (0.01%); `8`: 504 (0.01%); _(+357 more codes)_ | 99.42% |
| `2016-2023` | 29,950,846 | `0`: 64,697 (0.22%); `2`: 5,793 (0.02%); `1`: 5,777 (0.02%); `3`: 3,602 (0.01%); `4`: 2,700 (0.01%); `5`: 2,274 (0.01%); `6`: 2,123 (0.01%); `7`: 2,007 (0.01%); _(+357 more codes)_ | 99.44% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |
| `1989-2004` | `9` | 3,576 | 0.01% |
| `1989-2004` | `98` | 661 | 0.00% |
| `1989-2004` | `99` | 722 | 0.00% |
| `1989-2004` | _null/blank_ | 51,865,677 | 99.26% |
| `2005-2013` | `9` | 2,201 | 0.01% |
| `2005-2013` | `98` | 372 | 0.00% |
| `2005-2013` | `99` | 400 | 0.00% |
| `2005-2013` | _null/blank_ | 36,773,396 | 99.37% |
| `2014-2015` | `9` | 427 | 0.01% |
| `2014-2015` | `98` | 71 | 0.00% |
| `2014-2015` | `99` | 82 | 0.00% |
| `2014-2015` | _null/blank_ | 7,940,259 | 99.42% |
| `2016-2023` | `9` | 1,705 | 0.01% |
| `2016-2023` | `98` | 301 | 0.00% |
| `2016-2023` | `99` | 268 | 0.00% |
| `2016-2023` | _null/blank_ | 29,784,233 | 99.44% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`0`} _(codes ≥0.05% of an era)_

### `age_at_death_recode5` <a id="c820-natality-linked-age_at_death_recode5"></a>

_Schema note:_ 1|2|3|4|5|null — 1=<1hr; 2=1-23hr; 3=1-6d; 4=7-27d; 5=28d+. v4 linked cohort (populated every cohort era incl. 1983-1988). Null for survivors / den rows.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | `5`: 81,472 (0.37%); `2`: 62,467 (0.28%); `3`: 37,239 (0.17%); `4`: 24,665 (0.11%); `1`: 24,259 (0.11%) | 98.96% |
| `1989-2004` | 52,253,538 | `5`: 133,400 (0.26%); `2`: 99,228 (0.19%); `3`: 53,391 (0.10%); `1`: 52,209 (0.10%); `4`: 49,633 (0.09%) | 99.26% |
| `2005-2013` | 37,006,070 | `5`: 78,324 (0.21%); `2`: 59,731 (0.16%); `1`: 34,359 (0.09%); `4`: 30,868 (0.08%); `3`: 29,392 (0.08%) | 99.37% |
| `2014-2015` | 7,986,908 | `5`: 15,455 (0.19%); `2`: 12,355 (0.15%); `1`: 6,797 (0.09%); `4`: 6,034 (0.08%); `3`: 6,008 (0.08%) | 99.42% |
| `2016-2023` | 29,950,846 | `5`: 57,463 (0.19%); `2`: 41,869 (0.14%); `1`: 22,828 (0.08%); `3`: 22,269 (0.07%); `4`: 22,184 (0.07%) | 99.44% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 21,959,156 | 98.96% |
| `1989-2004` | _null/blank_ | 51,865,677 | 99.26% |
| `2005-2013` | _null/blank_ | 36,773,396 | 99.37% |
| `2014-2015` | _null/blank_ | 7,940,259 | 99.42% |
| `2016-2023` | _null/blank_ | 29,784,233 | 99.44% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `underlying_cause_icd10` <a id="c820-natality-linked-underlying_cause_icd10"></a>

_Schema note:_ ICD-10 codes|null — v4 linked cohort. NULL for 1983-1998 (the ICD-9 era — use underlying_cause_icd9). Null for survivors. ICD-10 is internally consistent 1999-2023; it is NOT cross-revision comparable with the ICD-9 underlying_cause_icd9…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `P072`: 19,759 (0.04%); `R95`: 13,867 (0.03%); `P073`: 6,433 (0.01%); `R99`: 6,161 (0.01%); `P220`: 5,255 (0.01%); `P011`: 4,119 (0.01%); `Q249`: 3,887 (0.01%); `P369`: 3,403 (0.01%); _(+1679 more codes)_ | 99.68% |
| `2005-2013` | 37,006,070 | `P072`: 29,992 (0.08%); `R95`: 18,407 (0.05%); `R99`: 9,361 (0.03%); `P073`: 9,227 (0.02%); `P011`: 7,163 (0.02%); `W75`: 6,050 (0.02%); `Q249`: 5,190 (0.01%); `P220`: 5,113 (0.01%); _(+1759 more codes)_ | 99.37% |
| `2014-2015` | 7,986,908 | `P072`: 6,240 (0.08%); `R95`: 3,134 (0.04%); `R99`: 2,320 (0.03%); `P073`: 1,830 (0.02%); `W75`: 1,796 (0.02%); `P011`: 1,510 (0.02%); `Q249`: 1,010 (0.01%); `Q913`: 969 (0.01%); _(+1068 more codes)_ | 99.42% |
| `2016-2023` | 29,950,846 | `P072`: 20,094 (0.07%); `R95`: 11,175 (0.04%); `R99`: 9,308 (0.03%); `W75`: 7,489 (0.03%); `P073`: 5,955 (0.02%); `P011`: 5,165 (0.02%); `Q913`: 3,529 (0.01%); `Q249`: 3,281 (0.01%); _(+1565 more codes)_ | 99.44% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |
| `1989-2004` | _null/blank_ | 52,088,253 | 99.68% |
| `2005-2013` | _null/blank_ | 36,773,396 | 99.37% |
| `2014-2015` | _null/blank_ | 7,940,259 | 99.42% |
| `2016-2023` | _null/blank_ | 29,784,233 | 99.44% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2004`→`2005-2013`: added {`P072`} _(codes ≥0.05% of an era)_

### `cause_recode_130` <a id="c820-natality-linked-cause_recode_130"></a>

_Schema note:_ 1-158|null — NCHS 130-cause recode with residual codes 131-158 ("all other" / era residual categories; SIDS=135 is in this range). v4 linked cohort. NULL for 1983-1998 (ICD-9 era — use cause_recode_61). Null for survivors. Do NOT filter …

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `89`: 20,450 (0.04%); `135`: 13,867 (0.03%); `123`: 9,015 (0.02%); `117`: 7,382 (0.01%); `136`: 6,583 (0.01%); `90`: 6,482 (0.01%); `96`: 5,728 (0.01%); `106`: 4,490 (0.01%); _(+117 more codes)_ | 99.68% |
| `2005-2013` | 37,006,070 | `89`: 30,538 (0.08%); `135`: 18,407 (0.05%); `117`: 11,906 (0.03%); `123`: 11,183 (0.03%); `136`: 9,971 (0.03%); `90`: 9,259 (0.03%); `76`: 7,163 (0.02%); `146`: 6,050 (0.02%); _(+115 more codes)_ | 99.37% |
| `2014-2015` | 7,986,908 | `89`: 6,368 (0.08%); `135`: 3,134 (0.04%); `117`: 2,524 (0.03%); `136`: 2,433 (0.03%); `123`: 2,237 (0.03%); `90`: 1,838 (0.02%); `146`: 1,796 (0.02%); `76`: 1,510 (0.02%); _(+112 more codes)_ | 99.42% |
| `2016-2023` | 29,950,846 | `89`: 20,464 (0.07%); `135`: 11,175 (0.04%); `117`: 9,992 (0.03%); `136`: 9,627 (0.03%); `146`: 7,489 (0.03%); `123`: 7,399 (0.02%); `90`: 6,005 (0.02%); `76`: 5,165 (0.02%); _(+114 more codes)_ | 99.44% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |
| `1989-2004` | `9` | 1,703 | 0.00% |
| `1989-2004` | `98` | 499 | 0.00% |
| `1989-2004` | `99` | 360 | 0.00% |
| `1989-2004` | _null/blank_ | 52,088,253 | 99.68% |
| `2005-2013` | `9` | 2,025 | 0.01% |
| `2005-2013` | `98` | 725 | 0.00% |
| `2005-2013` | `99` | 416 | 0.00% |
| `2005-2013` | _null/blank_ | 36,773,396 | 99.37% |
| `2014-2015` | `9` | 347 | 0.00% |
| `2014-2015` | `98` | 101 | 0.00% |
| `2014-2015` | `99` | 106 | 0.00% |
| `2014-2015` | _null/blank_ | 7,940,259 | 99.42% |
| `2016-2023` | `9` | 1,095 | 0.00% |
| `2016-2023` | `98` | 364 | 0.00% |
| `2016-2023` | `99` | 347 | 0.00% |
| `2016-2023` | _null/blank_ | 29,784,233 | 99.44% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-2004`→`2005-2013`: added {`89`} _(codes ≥0.05% of an era)_

### `underlying_cause_icd9` <a id="c820-natality-linked-underlying_cause_icd9"></a>

_Schema note:_ ICD-9 codes|null — v4 linked cohort (NEW at C8.18 DO step 6b; the ICD-9-era cause representation, the H7 fetal-death sibling-parity decision — DECISION_LOG 2026-05-17T05:30:00Z default-null + revision-tagged). Populated for cohort birth-…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | `7980`: 31,228 (0.14%); `769`: 20,396 (0.09%); `7798`: 13,843 (0.06%); `7650`: 12,408 (0.06%); `7708`: 9,363 (0.04%); `7651`: 6,733 (0.03%); `7469`: 5,381 (0.02%); `7485`: 5,337 (0.02%); _(+1381 more codes)_ | 98.96% |
| `1989-2004` | 52,253,538 | `7980`: 27,845 (0.05%); `7650`: 20,023 (0.04%); `769`: 14,103 (0.03%); `7798`: 8,945 (0.02%); `7708`: 7,080 (0.01%); `7651`: 7,007 (0.01%); `7485`: 6,391 (0.01%); `7469`: 5,444 (0.01%); _(+1357 more codes)_ | 99.57% |
| `2005-2013` | 37,006,070 | — | 100.00% |
| `2014-2015` | 7,986,908 | — | 100.00% |
| `2016-2023` | 29,950,846 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 21,959,156 | 98.96% |
| `1989-2004` | _null/blank_ | 52,031,002 | 99.57% |
| `2005-2013` | _null/blank_ | 37,006,070 | 100.00% |
| `2014-2015` | _null/blank_ | 7,986,908 | 100.00% |
| `2016-2023` | _null/blank_ | 29,950,846 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: dropped {`7650`, `769`, `7798`} _(codes ≥0.05% of an era)_
- `1989-2004`→`2005-2013`: dropped {`7980`} _(codes ≥0.05% of an era)_

### `cause_recode_61` <a id="c820-natality-linked-cause_recode_61"></a>

_Schema note:_ 1-61|null — v4 linked cohort (NEW at C8.18 DO step 6b; the ICD-9-era sibling of cause_recode_130). NCHS 61-cause ICD-9-era recode. Populated cohort birth-year 1983-1998 (death rows); NULL for 1999+ (ICD-10 era — use cause_recode_130) and…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | `590`: 31,228 (0.14%); `510`: 20,990 (0.09%); `500`: 20,396 (0.09%); `440`: 19,141 (0.09%); `570`: 17,774 (0.08%); `290`: 14,624 (0.07%); `680`: 10,713 (0.05%); `400`: 8,179 (0.04%); _(+53 more codes)_ | 98.96% |
| `1989-2004` | 52,253,538 | `590`: 27,845 (0.05%); `440`: 27,030 (0.05%); `510`: 15,591 (0.03%); `290`: 14,543 (0.03%); `500`: 14,103 (0.03%); `570`: 13,970 (0.03%); `680`: 10,665 (0.02%); `400`: 9,604 (0.02%); _(+53 more codes)_ | 99.57% |
| `2005-2013` | 37,006,070 | — | 100.00% |
| `2014-2015` | 7,986,908 | — | 100.00% |
| `2016-2023` | 29,950,846 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 21,959,156 | 98.96% |
| `1989-2004` | _null/blank_ | 52,031,002 | 99.57% |
| `2005-2013` | _null/blank_ | 37,006,070 | 100.00% |
| `2014-2015` | _null/blank_ | 7,986,908 | 100.00% |
| `2016-2023` | _null/blank_ | 29,950,846 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: dropped {`290`, `500`, `510`, `570`} _(codes ≥0.05% of an era)_
- `1989-2004`→`2005-2013`: dropped {`440`, `590`} _(codes ≥0.05% of an era)_

### `manner_of_death` <a id="c820-natality-linked-manner_of_death"></a>

_Schema note:_ 1-7|null — 1=accident; 3=homicide; 5=could not determine; 7=natural. v4 linked cohort. NULL for 1983-2002 — the 1983-1988 keyless num + the 1989-2002 denominator-plus carry no MANNER (only cohort 2003-2004 + 2005-2023 do). Null for survi…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `7`: 29,853 (0.06%); `5`: 2,231 (0.00%); `1`: 2,128 (0.00%); `4`: 881 (0.00%); `3`: 648 (0.00%) | 99.93% |
| `2005-2013` | 37,006,070 | `7`: 144,821 (0.39%); `5`: 16,763 (0.05%); `1`: 10,926 (0.03%); `4`: 3,168 (0.01%); `3`: 2,868 (0.01%) | 99.52% |
| `2014-2015` | 7,986,908 | `7`: 32,406 (0.41%); `5`: 4,372 (0.05%); `1`: 2,645 (0.03%); `4`: 617 (0.01%); `3`: 548 (0.01%) | 99.49% |
| `2016-2023` | 29,950,846 | `7`: 119,734 (0.40%); `5`: 17,896 (0.06%); `1`: 11,008 (0.04%); `4`: 2,686 (0.01%); `3`: 2,210 (0.01%) | 99.49% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |
| `1989-2004` | _null/blank_ | 52,217,797 | 99.93% |
| `2005-2013` | _null/blank_ | 36,827,524 | 99.52% |
| `2014-2015` | _null/blank_ | 7,946,320 | 99.49% |
| `2016-2023` | _null/blank_ | 29,797,312 | 99.49% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`7`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2015`: added {`5`} _(codes ≥0.05% of an era)_

### `record_weight` <a id="c820-natality-linked-record_weight"></a>

_Schema note:_ 1.0+|null — Weight to adjust for unlinked deaths / the 1983-1984 50%-non-VSCP sampling. 1.0 for survivors. NULL for 1985-1994 — 1985-1988 are full files (Record count == by-occurrence; no weighting; the 1988 trailing-byte anomaly is docu…

**(i) Historical-value distribution (per era)** — _continuous numeric: per-era summary statistics over raw non-null values (quantiles = nearest-rank on the weighted ECDF, rank ⌈p·N⌉; values formatted `%.6g`); documented sentinel codes are listed in (ii) and are **not** trimmed here_

| Era | n | non-null | null/blank | distinct | min | p25 | median | mean | p75 | max |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `1983-1988` | 22,189,258 | 6,783,382 | 69.43% | 2 | 1 | 1 | 1 | 1.09012 | 1 | 2 |
| `1989-2004` | 52,253,538 | 39,929,013 | 23.59% | 541 | 1 | 1 | 1 | 1.00011 | 1 | 1.29787 |
| `2005-2013` | 37,006,070 | 37,006,070 | 0.00% | 411 | 1 | 1 | 1 | 1.00008 | 1 | 1.28571 |
| `2014-2015` | 7,986,908 | 7,986,906 | 0.00% | 67 | 1 | 1 | 1 | 1.00004 | 1 | 1.06557 |
| `2016-2023` | 29,950,846 | 29,950,846 | 0.00% | 271 | 1 | 1 | 1 | 1.00005 | 1 | 1.2 |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 15,405,876 | 69.43% |
| `1989-2004` | _null/blank_ | 12,324,525 | 23.59% |
| `2014-2015` | _null/blank_ | 2 | 0.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Continuous numeric variable — no discrete code frame; see the per-era summary statistics in (i). (A frequency/code-frame diff is not meaningful for a continuous measurement.)

### `link_segment` <a id="c820-natality-linked-link_segment"></a>

_Schema note:_ den|num|null — NEW at C8.18 DO step 6b (v3->v4 ADDITIVE schema extension; the 5c-i within_era-ICD-9-columns precedent). den = the births-only aggregate denominator (infant_death NULL); num = the self-contained linked-infant-death numerat…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | `den`: 21,959,156 (98.96%); `num`: 230,102 (1.04%) | 0.00% |
| `1989-2004` | 52,253,538 | — | 100.00% |
| `2005-2013` | 37,006,070 | — | 100.00% |
| `2014-2015` | 7,986,908 | — | 100.00% |
| `2016-2023` | 29,950,846 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1989-2004` | _null/blank_ | 52,253,538 | 100.00% |
| `2005-2013` | _null/blank_ | 37,006,070 | 100.00% |
| `2014-2015` | _null/blank_ | 7,986,908 | 100.00% |
| `2016-2023` | _null/blank_ | 29,950,846 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: dropped {`den`, `num`} _(codes ≥0.05% of an era)_

### `neonatal_death` <a id="c820-natality-linked-neonatal_death"></a>

_Schema note:_ true|false — v4 linked derived. False for survivors. NULL for 1983-1988 (derived from age_at_death_days which is AGER5-only there — no day-precise neonatal split; use age_at_death_recode5 codes 1-3 vs 4-5 for the 1983-1988 keyless era).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `false`: 51,999,077 (99.51%); `true`: 254,461 (0.49%) | 0.00% |
| `2005-2013` | 37,006,070 | `false`: 36,851,720 (99.58%); `true`: 154,350 (0.42%) | 0.00% |
| `2014-2015` | 7,986,908 | `false`: 7,955,714 (99.61%); `true`: 31,194 (0.39%) | 0.00% |
| `2016-2023` | 29,950,846 | `false`: 29,841,696 (99.64%); `true`: 109,150 (0.36%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `postneonatal_death` <a id="c820-natality-linked-postneonatal_death"></a>

_Schema note:_ true|false — v4 linked derived. False for survivors. NULL for 1983-1988 (age_at_death_days AGER5-only there; use age_at_death_recode5 code 5 for the 1983-1988 keyless era).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `false`: 52,120,138 (99.74%); `true`: 133,400 (0.26%) | 0.00% |
| `2005-2013` | 37,006,070 | `false`: 36,927,746 (99.79%); `true`: 78,324 (0.21%) | 0.00% |
| `2014-2015` | 7,986,908 | `false`: 7,971,453 (99.81%); `true`: 15,455 (0.19%) | 0.00% |
| `2016-2023` | 29,950,846 | `false`: 29,893,383 (99.81%); `true`: 57,463 (0.19%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`false`, `true`} _(codes ≥0.05% of an era)_

### `cause_group` <a id="c820-natality-linked-cause_group"></a>

_Schema note:_ congenital_anomalies|short_gestation_lbw|other_perinatal|other|sids|maternal_complications|unintentional_injuries|placenta_cord_membranes|bacterial_sepsis|respiratory_distress|circulatory|nec|assault — v4 linked derived. Null for survivo…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1983-1988` | 22,189,258 | — | 100.00% |
| `1989-2004` | 52,253,538 | `congenital_anomalies`: 33,279 (0.06%); `other_perinatal`: 28,123 (0.05%); `short_gestation_lbw`: 26,932 (0.05%); `other`: 23,855 (0.05%); `sids`: 13,867 (0.03%); `maternal_complications`: 9,281 (0.02%); `placenta_cord_membranes`: 6,111 (0.01%); `respiratory_distress`: 5,728 (0.01%); _(+5 more codes)_ | 99.68% |
| `2005-2013` | 37,006,070 | `congenital_anomalies`: 47,502 (0.13%); `short_gestation_lbw`: 39,797 (0.11%); `other_perinatal`: 36,343 (0.10%); `other`: 32,730 (0.09%); `sids`: 18,407 (0.05%); `maternal_complications`: 14,664 (0.04%); `unintentional_injuries`: 10,498 (0.03%); `placenta_cord_membranes`: 9,291 (0.03%); _(+5 more codes)_ | 99.37% |
| `2014-2015` | 7,986,908 | `congenital_anomalies`: 9,553 (0.12%); `short_gestation_lbw`: 8,206 (0.10%); `other_perinatal`: 7,343 (0.09%); `other`: 6,840 (0.09%); `sids`: 3,134 (0.04%); `maternal_complications`: 3,079 (0.04%); `unintentional_injuries`: 2,475 (0.03%); `placenta_cord_membranes`: 1,860 (0.02%); _(+5 more codes)_ | 99.42% |
| `2016-2023` | 29,950,846 | `congenital_anomalies`: 33,972 (0.11%); `other_perinatal`: 28,721 (0.10%); `short_gestation_lbw`: 26,469 (0.09%); `other`: 24,590 (0.08%); `sids`: 11,175 (0.04%); `unintentional_injuries`: 10,047 (0.03%); `maternal_complications`: 9,948 (0.03%); `placenta_cord_membranes`: 5,634 (0.02%); _(+5 more codes)_ | 99.44% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1983-1988` | _null/blank_ | 22,189,258 | 100.00% |
| `1989-2004` | _null/blank_ | 52,088,253 | 99.68% |
| `2005-2013` | _null/blank_ | 36,773,396 | 99.37% |
| `2014-2015` | _null/blank_ | 7,940,259 | 99.42% |
| `2016-2023` | _null/blank_ | 29,784,233 | 99.44% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1983-1988`→`1989-2004`: added {`congenital_anomalies`, `other_perinatal`, `short_gestation_lbw`} _(codes ≥0.05% of an era)_
- `1989-2004`→`2005-2013`: added {`other`} _(codes ≥0.05% of an era)_

<!-- C8.20-GENERATED:END -->
