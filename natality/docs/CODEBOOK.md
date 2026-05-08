# Codebook

This codebook is derived conceptually from `metadata/harmonized_schema.csv`. The CSV is the **canonical** machine-readable source of truth.

## Harmonized variables (1990–2024)

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
| `year` | Birth year | int16 | 1990–2024 | full | |
| `restatus` | Resident status (NCHS) | int8 | 1990–2024 | full | Exclude `restatus=4` to match NCHS residence-based totals |
| `is_foreign_resident` | Foreign-resident indicator | bool | 1990–2024 | full | `restatus == 4` |
| `certificate_revision` | Certificate revision (1989 vs 2003) | string | 1990–2024 | full | `unrevised_1989` (1990–2013), `revised_2003` (2003–2024), `unknown` (2007–2013 when indeterminate) |
| `maternal_age` | Mother's age (single years) | int16 | 1990–2024 | partial | 1990–2002: `DMAGE`; 2003: approximate from `MAGER41` recode; 2004+: `MAGER` |
| `live_birth_order_recode` | Live birth order recode | int8 | 1990–2024 | full | 1990–2002: `LIVORD9`; 2003+: `LBO_REC` |
| `total_birth_order_recode` | Total birth order recode | int8 | 1990–2024 | full | 1990–2002: `TOTORD9`; 2003+: `TBO_REC` |
| `marital_status` | Marital status | int8 | 1990–2024 | partial | `DMAR` (1990–2002) vs `MAR` (2003–2013) vs `DMAR` (2014+). **California stopped reporting in 2017: ~11–12% null from 2017+.** Use `marital_reporting_flag` (2014+) to filter to reporting states. |
| `marital_reporting_flag` | Marital status reporting flag | bool | 2014–2024 | partial | Derived from `F_MAR_P`. True = state reports marital status; False = non-reporting state (California from 2017+). Null for all pre-2014 years. |
| `maternal_hispanic_origin` | Mother's Hispanic origin recode | int8 | 1990–2024 | partial | 1990–2002: `ORMOTH`; 2003–2013: `UMHISP`; 2014+: `MHISP_R` |
| `maternal_hispanic` | Maternal Hispanic indicator | bool | 1990–2024 | partial | Derived from `maternal_hispanic_origin` |
| `maternal_race_bridged4` | Mother's bridged race (4 categories) | int8 | 1990–2019 | partial | 1990–2002: **approximate** bridge from `MRACE` detail codes; 2003–2019: official `MRACEREC`/`MBRACE`. **100% null for 2020–2024** — NCHS discontinued the bridged-race recode in the public-use file. Use `maternal_race_ethnicity_5` for 2020+ (reconstructed from MRACE6 detail codes). |
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

## V3: Linked birth-infant death variables (2005–2023)

The V3 linked harmonized file (`output/harmonized/natality_v3_linked_harmonized.parquet`) contains all the natality harmonized columns above, plus death-side columns from the NCHS cohort linked birth-infant death files. One row per birth; death fields are populated for infant deaths and null for survivors.

Implemented by:

- `scripts/01_import/parse_all_linked_years.py` (2005–2015 batch), `scripts/01_import/parse_linked_cohort_year.py` (2016–2023)
- `scripts/03_harmonize/harmonize_linked_v3.py`
- `scripts/04_derive/derive_linked_v3.py` (derived columns)

### Record layout eras (linked)

| Era | Years | Record length | Format | Key differences |
|-----|-------|--------------|--------|-----------------|
| 2005–2013 | 2005–2013 | 900 bytes | Denominator-plus (birth + death appended) | Death fields at positions 868–900; FLGND=1/2 coding; birthweight at 467–470 |
| 2014–2015 | 2014–2015 | 1384 bytes | Denominator-plus (birth + death appended) | Death fields at positions 1346–1384; FLGND=1/blank coding; birthweight at 512–515 |
| 2016–2023 | 2016–2023 | 1346 (denom) + 1743 (numer) | Period-cohort (separate files, merged by CO_SEQNUM) | Death fields from numerator at positions 1346–1384; FLGND=1/blank coding |

**Notes:**
- Linked file birthweight positions differ from natality files. The linked files use `BRTHWGT` (imputed birthweight) instead of `DBWT`.
- Starting 2019, age-at-death variables (AGED, AGER5, AGER22) are calculated from birth certificate time-of-birth, improving accuracy for deaths within 24 hours but creating a minor comparability break with 2005–2018.

### Death-side harmonized columns

| harmonized_name | label | type | values | notes |
|---|---|---|---|---|
| `infant_death` | Infant death indicator | bool | true/false | FLGND=1 → true; FLGND=2 or blank → false |
| `age_at_death_days` | Age at death (days) | int16 | 0–365 or null | Null for survivors |
| `age_at_death_recode5` | Age at death 5-category recode | int8 | 1–5 or null | 1=<1hr; 2=1–23hr; 3=1–6d; 4=7–27d; 5=28d+. Null for survivors |
| `underlying_cause_icd10` | Underlying cause of death (ICD-10) | string | ICD-10 codes or null | Null for survivors |
| `cause_recode_130` | 130 Infant Cause of Death recode | int16 | 1–158 or null | NCHS 130-cause recode; residual codes 131–158 (including SIDS=135) are valid. Do NOT filter `<= 130` — drops ~23% of deaths including all SIDS. Null for survivors |
| `manner_of_death` | Manner of death | int8 | 1–7 or null | 1=accident; 3=homicide; 5=could not determine; 7=natural. Null for survivors |
| `record_weight` | Record weight | float64 | 1.0+ or null | Adjusts for unlinked deaths; 1.0 for most survivors |

### Death-side derived columns (added by `derive_linked_v3.py`)

| derived_name | label | type | definition |
|---|---|---|---|
| `neonatal_death` | Neonatal death (<28 days) | bool | `infant_death AND age_at_death_days < 28` |
| `postneonatal_death` | Postneonatal death (28–364 days) | bool | `infant_death AND age_at_death_days >= 28` |
| `cause_group` | Standard infant cause-of-death grouping | string | 13 categories based on ICD-10 underlying cause: `congenital_anomalies` (Q00–Q99), `short_gestation_lbw` (P07), `sids` (R95), `maternal_complications` (P01), `placenta_cord_membranes` (P02), `unintentional_injuries` (V01–X59), `bacterial_sepsis` (P36), `respiratory_distress` (P22), `nec` (P77), `circulatory` (I00–I99), `assault` (X85–Y09), `other_perinatal` (remaining P00–P96), `other` (all else). Null for survivors |

Plus birth-side derived columns: `gestational_age_weeks_clean`, `birthweight_grams_clean`, `apgar5_clean`, `low_birthweight`, `very_low_birthweight`, `preterm_lt37`, `very_preterm_lt32`, `singleton`, `maternal_age_cat`, `father_age_cat`, `diabetes_any_bool`, `hypertension_chronic_bool`, `hypertension_gestational_bool`.

## Next

- For comparability guidance and recommended trend-safe subsets, see `docs/COMPARABILITY.md`.
