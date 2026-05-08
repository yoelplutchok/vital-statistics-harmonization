# Codebook: U.S. Fetal Death Harmonized Dataset (V2.0, 1992-2022)

This codebook documents every variable in the harmonized and derived datasets.

- **Harmonized file**: `fetal_death_harmonized.parquet` (1,634,195 rows × 73 columns)
- **Derived file**: `fetal_death_derived.parquet` (1,634,195 rows × 89 columns)

(In the GitHub source repository these live under `output/harmonized/`. In the Zenodo deposit they are at the deposit root.)

All variables are stored as strings in the Parquet files. Numeric values should be cast after loading.

Year coverage: **1992-2002** (V2 era, 1989-revision uniform; 700,704 rows) **+ 2005-2022** (V1 era, 2003-revision transition; 933,491 rows). Years **2003 and 2004** are deferred to V2.1.

---

## Comparability Classes

Each variable is assigned a comparability class indicating cross-year usability:

| Class | Meaning |
|-------|---------|
| **full** | Same concept and coding across all available years (after any in-pipeline normalization). Safe for cross-year analysis. |
| **partial** | Same concept but coding, range, or availability differs across eras. Use with documented caveats. |
| **within_era** | Available only in one or two eras, OR carries semantically incompatible values across eras. NOT comparable across eras. |

V2 cross-era code-system fixes — split between **5 value-level normalizations (B1, B2, B3, B4, B6)**, **3 `within_era` columns** (B5 `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail` — do NOT cross-era `groupby`), and **1 partial relabel** (`maternal_age`, downgraded `full → partial`) — are summarized in [About This Release](ABOUT_THIS_RELEASE.md) and [Comparability §10](COMPARABILITY.md).

---

## Variable availability matrix (era summary)

| Era | Years | Source layout | Records | version_flag |
|---|---|---|---|---|
| **1992 era** | 1992-2002 | `FETAL_1992_2002_FIELDS` (360 bytes) | 700,704 | `S` (synthesized, since 1989 revision was the only revision) |
| 2006 era | 2005-2013 | `FETAL_2005_2006_FIELDS` (3351/801/3338 bytes) | 510,528 | mixed `A`/`S` |
| 2014 era | 2014-2017 | `FETAL_2014_2017_FIELDS` (3050 bytes) | 204,923 | mixed `A`/`S` |
| 2022 era | 2018-2022 | `FETAL_2018_2022_FIELDS` (2652 bytes) | 218,040 | `A` only |

V1 sub-era subtotals: 510,528 + 204,923 + 218,040 = 933,491. Plus 700,704 V2 = 1,634,195 total.

The "Years" column in the variable tables below uses these era labels.

---

## Harmonized Variables (73 columns)

### Record Identification

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `data_year` | Data year (added by pipeline) | 1992-2022 | full | All | int32 sibling of `delivery_year`, computed as `int(delivery_year)` during harmonization. Always equal to `int(delivery_year)` for every row (verified 1,634,195/1,634,195 in V2.0). Recommended filter/join key for cross-year analyses. |
| `version_flag` | Revision flag | A, S | full | All | A=2003 revision; S=1989 revision. **Synthesized to `S` for 1992-2002** (no native VERSION field in 1989-rev files) |
| `tabulation_flag` | NCHS tabulated subset flag | 1, 2 | partial | All | 1=exclude from NVSR tabulations; 2=include. NCHS's compound criterion (typically "GA >= 20 weeks OR BW >= 350g when GA unknown") — not a pure GA cutoff. ~5,400 V1 flag-2 rows (almost all in 2014+) have `gestational_age_combined < 20`, and ~63,700 flag-1 rows across all 29 years (~42,200 in V1 alone) have GA >= 20 (use `gestational_age_combined` directly when you need a pure GA filter). Field name and position changed across eras (V2:TABFLAG; V1 2006:TABFLG; V1 2014+:OE_TABFLG) |
| `delivery_year` | Year of delivery | 1992-2022 | partial | All | Same concept; field positions differ by era. V2 sources from DELYR (190-193) |
| `residence_status` | Residence status | 1-4 | full | All | 1=Resident; 2=Intrastate NR; 3=Interstate NR; 4=Foreign |

### Maternal Demographics

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `maternal_age` | Mother's single year of age | 10-54;99 | partial | All | V2 1989-rev: exact single-year age (observed 10-54; 99=Unknown). V1 2003-rev: top-coded 50+, bottom-coded 12-. 150 V2 rows fall outside the V1 boundary-coded range (108 at age 50-54; 42 at age 10-11) |
| `maternal_age_recode14` | Mother's age recode 14 | 1-14 | full | 2006/2014/2022 eras | Blank for V2 (1992 has MAGE12 12-cat at different position; not mapped) |
| `maternal_age_recode9` | Mother's age recode 9 | 1-9 | full | 2006/2014/2022 eras | Blank for V2 (1992 has MAGE8 8-cat with different bins; not mapped) |
| `maternal_race_multi` | Mother's race recode 31 | 1-30 | within_era | 2014+ | Multi-race recode. Version A only. Not in V2 or 2006 era |
| `maternal_race_recode6` | Mother's race recode 6 | 1-6 | within_era | 2014+ | 6-category recode. Version A only |
| `maternal_race_bridged` | Mother's bridged race | 1-4 | partial | 1992-2017 (not in 2018+) | 1=White; 2=Black; 3=AIAN; 4=API. **V2 recoded by harmonize.py** from raw MRACE 2-digit (01→1, 02→2, 03→3, 04-78→4, 99→blank). 2018+ blank because field discontinued in layout |
| `maternal_race_bridged_detail` | Mother's bridged race detail | 01-14;18;21-24;28;38;48;58;68;78;99 | **within_era** | 1992 era + 2006 era | **WARNING**: V2 (1992-2002) carries raw 1989-rev MRACE codes (01-07 single + 18/28/38/48/58/68/78 Asian/PI subcodes + 99 Unknown). V1 2006 carries raw MBRACE (01-14 single + 21-24 bridged). Codes 04-07 mean DIFFERENT subgroups across eras. Do not cross-era groupby |
| `hispanic_origin` | Mother's Hispanic origin | 0-9 | full | All | 0=Non-Hispanic; 1=Mexican; 2=PR; 3=Cuban; 4=C/S American; 5=Other; 9=Unknown. V2-era Hispanic-origin reporting was incomplete in OK (all years 100% unknown), MD (1992-1998), and MA (1992-1997). See [Comparability §11](COMPARABILITY.md) |
| `race_hispanic_combined` | Bridged race/Hispanic combined | 1-9 | partial | 1992-2017 | Same semantic structure across eras. Not in 2018+ |
| `race_hispanic_revised` | Race/Hispanic revised | 1-8 | within_era | 2014+ | Multi-race/Hispanic recode. Version A only |
| `maternal_education` | Mother's education (revised) | 1-9 | full | 2006/2014/2022 eras | 1=8th grade or less through 8=Doctorate. Version A only. **Blank for 2007-2013** (NCHS data limitation) and **blank for V2 1992-2002** (revised education added in 2003 revision; V2 uses `maternal_education_unrevised` instead) |
| `maternal_education_unrevised` | Mother's education (unrevised) | 0-99 | within_era | 1992-2002, 2005-2006 | Years-of-school coding. V2 sources from DMEDUC (82-83); V1 2005-2006 sources from UMEDUC (S-version only). **Blank for 2007-2013** (NCHS did not include UMEDUC in those V1 public-use years). Not in 2014+ |
| `marital_status` | Marital status | 1, 2, 9 | within_era | 1992-2013 | 1=Married; 2=Unmarried; 9=Unknown. Not in 2014+ public-use layouts |
| `maternal_nativity` | Mother's nativity | 1-3 | within_era | 2014+ | 1=Native; 2=Foreign; 3=Unknown. Version A only |

### Paternal Demographics

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `paternal_age_combined` | Father's combined age | 10-99 | full | All | 99=Unknown. Version A only for V1 → **blank for 2007-2013**. V2 populates from raw DFAGE (161-162) for all 700,704 records |
| `paternal_age_recode11` | Father's age recode 11 | 01-11 | full | All | 11-category recode. **V2 recoded by harmonize.py** from 12-category 1989-rev FAGE11 (V2 codes `10`=55-59 + `11`=60-98 collapsed to V1 code `10`=55+; V2 code `12`=Unknown remapped to V1 code `11`=Unknown). Full 12-cat detail preserved in yearly raw parquets |

### Pregnancy and Obstetric

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `live_birth_order` | Live birth order recode | 0-9 | full | All | 9=Unknown |
| `plurality` | Plurality recode | 1-9 | partial | All | 1=Single through 5=Quintuplet+. 2022 era max is 4. 9=Unknown. **Louisiana 1992-1994 reports 9 for essentially all in-state records** (state non-reporting). 1,686 of the 1,713 V2 plurality=9 rows are LA-occurrence 1992-1994 (the remainder are scattered across other state-years). See [Comparability §11](COMPARABILITY.md) |
| `prenatal_care_month` | Month prenatal care began (revised) | 0-99 | full | 2006/2014/2022 eras | 00=No care; 01-10=Month; 99=Unknown. Version A only. Blank for V2 (revised PRECARE is 2003+) |
| `prenatal_care_month_unrevised` | Month prenatal care began (unrevised) | 0-99 | within_era | 1992-2002, 2005-2006 | V2 sources from MONPRE (113-114); V1 2005-2006 from MPCB (S-version only). **Blank for 2007-2013** (NCHS did not include MPCB in those V1 public-use years). Not in 2014+ |
| `prenatal_care_recode` | Prenatal care recode | 1-5 | full | 2006/2014/2022 eras | 5-category revised recode. Version A only. Blank for V2 |
| `prior_cesarean` | Previous cesareans (Y/N) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 (RF_CESAR is 2003+) |
| `prior_cesarean_number` | Previous cesareans count | 0-99 | full | 2006/2014/2022 eras | 99=Unknown. Version A only. Blank for V2 |

### Fetal Characteristics

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `fetal_sex` | Sex of fetus | M, F, U | full | All | U=Unknown. **V2 recoded by harmonize.py** from raw FSEX numeric `1/2/9` to V1 alphabetic `M/F/U`. High unknown rate (~45-53%) for early-GA deaths, all eras |
| `gestational_age_clinical` | Clinical/OE gestation (unedited) | 0-99 | partial | All | Field name changed across eras. V2 sources from CLINGEST (216-217) — clinical estimate of gestation in the 1989 era |
| `gestational_age_oe_edited` | Obstetric estimate edited | 2-99 | within_era | 2014+ | NCHS standard tabulation item. Blank for V2 (OE concept is 2014+) |
| `gestational_age_combined` | Combined gestation (weeks) | 2-99 | full | All | 02-47 weeks; 99=Unknown. **Primary GA variable.** V2 sources from DGESTAT (197-198). NB: 3 V2 1992 rows have non-canonical single-digit values (`'2'`, `'3'`, `'4'`) due to upstream NCHS bytes `'2 '`, `'3 '`, `'4 '` being whitespace-stripped in harmonize; tiny scale (3/700,704), all rows have BIRWT=9999 |
| `gestational_age_recode12` | Gestation recode 12 | 1-12 | partial | All | Bin boundaries differ slightly across V1 sub-eras and 1989-revision (see [Comparability §6](COMPARABILITY.md)) |
| `gestational_age_recode5` | Gestation recode 5 | 1-5 | full | All | 5-category recode. Same coding all eras |
| `oe_gest_recode12` | OE gestation recode 12 | 1-12 | within_era | 2014+ | NCHS standard recode. Blank for V2 |
| `oe_gest_recode5` | OE gestation recode 5 | 1-5 | within_era | 2014+ | NCHS standard recode. Blank for V2 |
| `birthweight` | Birth weight (grams) | 1-9999 | full | All | 9999=Not stated. **Primary BW variable.** V2 sources from DBIRWT (207-210); 397,397 V2 rows have BW=9999, driven by TABFLAG=1 (<20wk) records where BW is typically not captured |
| `birthweight_recode14` | Birth weight recode 14 | 1-14 | full | All | 14-category gram-range recode |
| `birthweight_recode4` | Birth weight recode 4 | 1-4 | full | All | 4-category recode. 4=Not stated |
| `fetal_presentation` | Fetal presentation | 1-3, 9 | full | 2006/2014/2022 eras | 1=Cephalic; 2=Breech; 3=Other; 9=Unknown. Version A only. Blank for V2 (ME_PRES is 2003+; 1992 has BREECH (273) but as a labor complication, not a presentation item) |
| `estimated_time_fetal_death` | Estimated time of fetal death | N, L, A, U | within_era | 2014+ | Version A only. Blank for V2 |
| `gestation_imputed_flag` | Gestation imputed flag | blank, 1 | full | All | 1=Imputed |
| `obgest_used_flag` | OE gestation used flag | blank, 1 | full | 2006/2014/2022 eras | 1=Used. Blank for V2 (OE-used flag is 2014+) |

### Maternal Risk Factors

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `prepregnancy_diabetes` | Prepregnancy diabetes (revised) | Y, N, U | full | 2006/2014/2022 eras | Version A only. 2005-2013 also has X=Not on certificate. Blank for V2 |
| `gestational_diabetes` | Gestational diabetes (revised) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `diabetes_unrevised` | Diabetes (unrevised combined) | 1, 2, 8, 9 | partial | 1992-2017 | 1=Yes/Reported; 2=No/Not reported; 9=Unknown/Not classifiable. V2 1989-era 9 = "Not classifiable"; V1 9 = "Unknown/Not stated" — slight semantic shift in unknown bucket. Not in 2018+ |
| `prepregnancy_hypertension` | Prepregnancy hypertension (revised) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `gestational_hypertension` | Gestational hypertension (revised) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `chronic_hypertension_unrevised` | Chronic hypertension (unrevised) | 1, 2, 8, 9 | partial | 1992-2017 | Same Reported/Yes wording shift as `diabetes_unrevised`. Not in 2018+ |
| `pregnancy_hypertension_unrevised` | Pregnancy hypertension (unrevised) | 1, 2, 8, 9 | partial | 1992-2017 | Same wording shift. Not in 2018+ |
| `eclampsia` | Eclampsia (revised) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `eclampsia_unrevised` | Eclampsia (unrevised) | 1, 2, 8, 9 | partial | 1992-2017 | Same wording shift. Not in 2018+ |
| `tobacco_use_revised` | Tobacco use (revised Y/N) | Y, N, U | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `tobacco_cig_1st_tri` | Cigarettes 1st trimester | 0-99 | full | 2006/2014/2022 eras | 99=Unknown. Version A only. Blank for V2 |
| `tobacco_cig_2nd_tri` | Cigarettes 2nd trimester | 0-99 | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `tobacco_cig_3rd_tri` | Cigarettes 3rd trimester | 0-99 | full | 2006/2014/2022 eras | Version A only. Blank for V2 |
| `tobacco_cig_prepreg` | Cigarettes before pregnancy | 0-99 | within_era | 2014+ | Version A only. Blank for V2 |
| `tobacco_use_unrevised` | Tobacco use (unrevised) | 1, 2, 9 | within_era | 1992-2002, 2005-2006 | V2 sources from TOBACCO (245); V1 2005-2006 from TOBUSE (S-version only). **Blank for 2007-2013** (NCHS did not include TOBUSE in those V1 public-use years). Not in 2014+ |
| `prepregnancy_bmi` | Pre-pregnancy BMI | 13.0-69.9; 99.9 | within_era | 2014+ | Valid range 13.0-69.9; 99.9=Unknown. Version A only. Blank for V2 |
| `prepregnancy_bmi_recode` | Pre-pregnancy BMI recode | 1-9 | within_era | 2014+ | 6-category recode. Version A only. Blank for V2 |

### Delivery

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `delivery_method_recode` | Delivery method (simple) | 1, 2, 9 | full | All | 1=Vaginal; 2=C-section; 9=Not stated. **V2 collapsed by harmonize.py** from 6-category 1989-rev DELMETH6 (`{1,2}→1`, `{3,4,5}→2`, `6→9`). V1 has documented `3` anomaly (2,553 rows in 2006-2013 — see [Comparability §7-bis]). Full 6-cat detail in yearly raw parquets |
| `delivery_method_revised` | Delivery method (revised) | 1-9 | within_era | 2014+ | 6-category revised recode. Version A only. Blank for V2 |
| `delivery_route` | Route/method of delivery | 1-4, 9 | full | 2006/2014/2022 eras | 1=Spontaneous; 2=Forceps; 3=Vacuum; 4=Cesarean; 9=Unknown. Version A only. Blank for V2 |
| `attendant` | Attendant at delivery | 1-5, 9 | full | All | 1=MD; 2=DO; 3=CNM; 4=Other midwife; 5=Other; 9=Unknown |
| `delivery_place_revised` | Delivery place (revised) | 1-9 | full | 2006/2014/2022 eras | 7-category revised. Version A only. Blank for V2 |
| `delivery_place_unrevised` | Delivery place (unrevised) | 1-9 | **within_era** | 1992-2017 | **WARNING**: V2 PLDEL (1=Hospital, 2=Doctor/home/public, 3=En route, 9=Unknown) and V1 UBFACIL (1=Hospital, 2=Birth Center, 3=Home intended, 4=Home unintended, 5=Other, 9=Unknown) use INCOMPATIBLE place taxonomies. Codes 2 and 3 mean different things across eras. Do not cross-era groupby |
| `delivery_place_recode` | Delivery place recode | 1-3 | full | All | 1=Hospital; 2=Not in hospital; 3=Unknown. **V2 re-derived by harmonize.py** from raw PLDEL ({1,3}→1, 2→2, 9→3) since V2's PLDEL2 conflates Unknown into 2 |
| `breech_unrevised` | Breech delivery (unrevised) | 1, 2, 8, 9 | **within_era** | 1992-2017 | **WARNING**: V2 BREECH = "Breech/Malpresentation" (broader: includes any malpresentation) vs V1 ULD_BREECH = "Breech Delivery" (narrower: actual breech-position only). Different clinical concepts in the same column. Do not cross-era groupby |

### Morbidity

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `uterine_rupture` | Ruptured uterus | Y, N, U | within_era | 2014+ | Version A only. Blank for V2 (MM_RUPT is 2003+; 1992 RUPTURE at pos 265 is 'Premature rupture of membrane' — different item) |
| `icu_admission` | Admit to intensive care | Y, N, U | within_era | 2014+ | Version A only. Blank for V2 |

### Cause of Death

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `cause_icd10` | ICD-10 cause code | 5-char ICD-10 | within_era | 2014+ | Blank for 1992-2013. ~50% missing for 2018+ |
| `cause_recode124` | Cause recode 124 | 2-143 | within_era | 2014+ | 124-category NCHS recode |
| `cause_reporting_flag` | Cause reporting flag | 0, 1 | within_era | 2014+ | 1=Cause reported |

---

**Note on reporting flags**: The individual reporting flags (F_MEDUC, F_CLINEST, F_TOBACO, F_RF_PDIAB, V2-era ORIGM/EDUCM/PNCF/etc.) are available in the per-year raw Parquet files (bundled in `fetal_death_yearly_raw_1992-2022.zip`; in the GitHub source repo they live under `output/yearly_clean/`). They are not carried through to the harmonized schema because each flag is era-specific with different positions and naming conventions. Researchers who need item-level reporting flags should work directly with the raw yearly files.

---

## Derived Variables (16 additional columns)

These variables are computed from harmonized fields and added in the derived file. All 16 compute correctly on V2 with the V2 sentinels handled appropriately. Two are intentionally blank for V2 (see notes).

### Gestational Age Indicators

| Variable | Label | Logic | Notes |
|----------|-------|-------|-------|
| `ga_gte20wks` | GA >= 20 weeks | "1" if GA >= 20; "0" if GA < 20; "" if GA unknown (DGESTAT=99 / COMBGEST=99) | |
| `ga_gte28wks` | GA >= 28 weeks | "1" if GA >= 28; "0" if GA < 28; "" if GA unknown | WHO stillbirth threshold |
| `preterm` | Preterm (< 37 weeks) | "1" if GA < 37; "0" if GA >= 37; "" if unknown | |
| `very_preterm` | Very preterm (< 32 weeks) | "1" if GA < 32; "0" if GA >= 32; "" if unknown | |
| `extremely_preterm` | Extremely preterm (< 28 weeks) | "1" if GA < 28; "0" if GA >= 28; "" if unknown | |

### Birthweight Indicators

| Variable | Label | Logic | Notes |
|----------|-------|-------|-------|
| `bw_gte350g` | BW >= 350 grams | "1" if BW >= 350; "0" if BW < 350; "" if unknown (BW=9999) | Common reporting threshold |
| `bw_gte500g` | BW >= 500 grams | "1" if BW >= 500; "0" if BW < 500; "" if unknown | Common analytic threshold |
| `bw_gte1000g` | BW >= 1000 grams | "1" if BW >= 1000; "0" if BW < 1000; "" if unknown | WHO stillbirth threshold |
| `lbw` | Low birthweight (< 2500g) | "1" if BW < 2500; "0" if BW >= 2500; "" if unknown | |
| `vlbw` | Very low birthweight (< 1500g) | "1" if BW < 1500; "0" if BW >= 1500; "" if unknown | |

### Composite Definitions

| Variable | Label | Logic | Notes |
|----------|-------|-------|-------|
| `meets_who_stillbirth` | WHO stillbirth definition | "1" if GA >= 28 OR BW >= 1000g; "0" if both known and neither met; "" if indeterminate | Three-valued OR logic |
| `meets_20wk_threshold` | Meets 20-week threshold | Same as `ga_gte20wks` | Alias for clarity |

### Categorical Recodes

| Variable | Label | Logic | Notes |
|----------|-------|-------|-------|
| `maternal_age_cat` | Maternal age category | <20, 20-24, 25-29, 30-34, 35-39, 40+ | "" if age unknown. V2 ages 50-54 (108 rows) correctly fall in 40+ bucket |
| `education_cat4` | Education 4-level | < HS, HS grad, Some college, BA+ | "" if education unknown or blank. **Blank for all V2 records** (V2 populates `maternal_education_unrevised` years-of-school instead of the revised 1-9 categorical scale that the derivation maps from). Cross-era education trends require building a 1989→2003 binning bridge — not provided by V2.0 |
| `singleton` | Singleton indicator | "1" if plurality=1; "0" if plurality>1; "" if unknown (plurality=9 or blank) | V2: 1,713 blanks total, of which 1,686 are Louisiana 1992-1994 non-reporters (DPLURAL=9, LA-occurrence); the remaining 27 are scattered V2 plurality=9 records across other state-years |

### Cause-of-Death Grouping

| Variable | Label | Logic | Notes |
|----------|-------|-------|-------|
| `cause_group` | Broad cause group | Groups ICD-10 codes into categories | **Blank for 1992-2013** (no ICD-10 in V2 public-use file; cause-of-death added 2014+ only) |

Cause group mapping:

| ICD-10 Codes | Group |
|--------------|-------|
| Q00-Q99 | Congenital anomalies |
| P95 | Unspecified cause |
| P02 | Placenta/cord/membranes |
| P01 | Pregnancy complications |
| P00 | Maternal conditions |
| Other P codes | Other perinatal |
| All others | Other |

---

## Data Quality Notes

1. **Version-A-only fields**: Many variables (education, tobacco, risk factors, cause of death, prenatal care) are only collected on the 2003 revision certificate. Filter to `version_flag == 'A'` when using these. By 2018, all V1 records are version A. **All V2 records are `version_flag == 'S'`** (synthesized; the 1989-revision raw files have no native VERSION field), so version-A-only fields are uniformly blank for 1992-2002.

2. **Sentinel values**: The harmonized file retains original sentinel values that indicate "unknown" or "not stated": `gestational_age_combined=99`, `birthweight=9999`, `prenatal_care_month=99`, `maternal_education=9`, `hispanic_origin=9`, `fetal_sex=U`, `plurality=9`, `delivery_method_recode=9`, `tobacco_use_revised=U`, `prepregnancy_bmi=99.9`. NCHS top-codes maternal age at 50 in V1, so the "age=99 = unknown" convention does not appear in V1. The V2 1989-rev DMAGE permits `99=Unknown` per the 1992 user guide but in practice 0 V2 rows use it (NCHS imputes maternal age in this era). The derived file handles sentinels automatically — derived variables convert sentinels to NaN before computing thresholds, so indicators like `ga_gte20wks` and `bw_gte350g` correctly return "" (unknown) for sentinel-coded records. When working directly with harmonized (non-derived) fields, filter or convert these sentinel values before analysis.

3. **2007-2013 V1 data gaps**: `maternal_education` and `paternal_age_combined` are blank for all V1 records in 2007-2013 (including A-version) due to NCHS public-use file limitations. `paternal_age_recode11` IS available for those years. V2 `paternal_age_combined` is populated for all 700,704 records.

4. **Cause-of-death availability**: `cause_icd10` is blank for 1992-2013 (not in public-use file pre-2014). For 2014+, ~47-51% of records may lack cause data depending on jurisdiction reporting.

5. **V2 cross-era code-system fixes**: Five harmonized columns are **value-level normalized** inside `harmonize.py` for the V2 era to match the V1 coding system — B1 `fetal_sex`, B2 `delivery_method_recode`, B3 `maternal_race_bridged`, B4 `paternal_age_recode11`, B6 `delivery_place_recode`. Three columns (`maternal_race_bridged_detail`, `delivery_place_unrevised`, `breech_unrevised`) carry incompatible content per era and are explicitly **relabeled to `within_era`** with WARNINGs in this codebook and in the schema (no value normalization is possible because the underlying concepts/categories don't map 1:1). Note that B5 (`breech_unrevised`) is one of the relabels, not a value normalization. The B-fix derivations are documented in [About This Release](ABOUT_THIS_RELEASE.md).

6. **V2 documented data quirks** (faithfully preserved):
   - Louisiana plurality non-reporting 1992-1994 (≈99% of LA resident records have `plurality=9`).
   - Oklahoma Hispanic-origin non-reporting (100% `hispanic_origin=9` for all 11 V2 years).
   - Maryland Hispanic-origin non-reporting 1992-1998; Massachusetts 1992-1997.
   - 108 V2 rows (1997-2002) have `maternal_age` 50-54 (outside the 1992-guide-documented range of 10-49); real NCHS bytes preserved.
   - 3 V2 1992 rows have non-canonical single-digit `gestational_age_combined` (`'2'`/`'3'`/`'4'` instead of zero-padded `'02'`/`'03'`/`'04'`) due to upstream NCHS data-quality issue; all three rows have `birthweight=9999`.

---

## Source Crosswalk

For the complete raw-field-to-harmonized mapping by era (4 eras: 1992, 2006, 2014, 2022), see `variable_crosswalk_working.csv` (in the GitHub source repo: `metadata/variable_crosswalk_working.csv`).
For the full schema definition including allowed_values, see `harmonized_schema.csv`.
For the full 1989-revision 360-byte layout, see `record_layout_1992.csv` and `V2_1992_LAYOUT_DECISIONS.md`.
