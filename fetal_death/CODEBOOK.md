# Codebook: U.S. Fetal Death Harmonized Dataset (v2.4.0, 1982–2024)

This codebook documents every variable in the harmonized and derived datasets.

- **Harmonized file**: `fetal_death_harmonized.parquet` (2,427,233 rows × 73 columns)
- **Derived file**: `fetal_death_derived.parquet` (2,427,233 rows × 89 columns)

(In the GitHub source repository these live under `output/harmonized/`. In the Zenodo deposit they are at the deposit root.)

All variables are stored as strings in the Parquet files. Numeric values should be cast after loading.

Year coverage: **1982–2024, 43 contiguous years, 2,427,233 rows** across seven NCHS layout eras — **1982-1988** (V3b, 1978-revision; 421,125 rows) · **1989-1991** (V3a, early 1989-revision; 188,909) · **1992-2002** (V2, 1989-revision uniform; 700,704) · **2003-2004** (V2.1, 1989→2003 transition layouts; 107,782) · **2005-2013** (V1, 2003-revision staggered adoption; 510,528) · **2014-2017** (V1; 204,923) · **2018-2024** (V1, all 2003-revision; 293,262). Per-era counts are parquet-derived (Appendix C8.20); they sum byte-exact to 2,427,233. In the per-variable notes below, the legacy **"V2"** label refers to the pre-2003-revision S-synthesized eras (1982-2002 = V3b+V3a+V2; 1989-revision behaviour for 1989-2002, 1978-revision for 1982-1988) and **"V1"** to the 2003-revision-transition era (2005+); **2003-2004 (V2.1)** is the dual-certificate boundary.

> **v2.4.0 scope note (C8.20).** The envelope and cross-era narrative in this hand-authored body were **re-paragraphed to v2.4.0** (the `fetal-death-codebook-comparability-v240` task, 2026-05-23). The per-variable tables below give the **V2/V1-era detail narrative and remain accurate for those eras**; the complete per-variable, per-era value-distribution panels, sentinel-code disambiguation, and era-by-era coding-scheme diffs across **all 7 documented layout eras (incl. 1982-1991 V3b/V3a and 2003-2004 V2.1)** are in the auto-generated **Appendix C8.20 — Per-variable historical evidence** at the end of this file. Every count there is derived from the gate-verified parquet by `scripts/_build_codebook_extensions.py` (deterministic; regenerate to reproduce byte-identically) — it is the authoritative full-envelope per-variable evidence; do not hand-edit it.

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

Row counts and `version_flag` mix are parquet-derived (Appendix C8.20; fetal-death derived parquet sha256[:12]=`185c071ec76a`):

| Era | Years | Revision / source layout | Records | version_flag |
|---|---|---|---|---|
| **V3b** | 1982-1988 | 1978-revision (`record_layout_1982_1988.csv`) | 421,125 | `S` (synthesized; 1978-rev predates the 2003-rev A/S split) |
| **V3a** | 1989-1991 | early 1989-revision (1989-rev `record_layout` family) | 188,909 | `S` (synthesized; no native VERSION field) |
| **V2 (1992 era)** | 1992-2002 | 1989-revision uniform (`FETAL_1992_2002_FIELDS`, 360 bytes) | 700,704 | `S` (synthesized) |
| **V2.1** | 2003-2004 | 1989→2003 transition (`record_layout_2003.csv` / `record_layout_2004.csv`) | 107,782 | `S` 97.26% / `A` 2.74% |
| **V1 (2006 era)** | 2005-2013 | 2003-rev staggered adoption (`FETAL_2005_2006_FIELDS`) | 510,528 | `S` 59.73% / `A` 40.27% |
| **V1 (2014 era)** | 2014-2017 | 2003-revision (`FETAL_2014_2017_FIELDS`, 3050 bytes) | 204,923 | `A` 87.20% / `S` 12.80% |
| **V1 (2022 era)** | 2018-2024 | 2003-revision (`FETAL_2018_2024_FIELDS`) | 293,262 | `A` 100% |

Era row counts sum byte-exact to **2,427,233** (= the v2.4.0 total: 421,125 + 188,909 + 700,704 + 107,782 + 510,528 + 204,923 + 293,262).

**Pre-1992 and transition eras (V3b / V3a / V2.1).** 1982-1988 (V3b) uses the 1978-revision Standard Report of Fetal Death — it predates the 1989 revision, so `version_flag` is synthesized `S` and the 2003-revision-only ("Version A only") variables are uniformly blank. 1989-1991 (V3a) is the earliest slice of the same 1989-revision certificate as V2 (1992-2002) and follows the V2 variable-availability pattern. 2003-2004 (V2.1) is the dual-certificate 1989→2003 transition (distinct 1351-/1501-byte layouts; predominantly `S` with a small early-adopter `A` fraction). The cross-era `B`-normalization family (B1-B6; §5 below / [Comparability §10](COMPARABILITY.md)) is applied to the pre-2003-revision eras and was extended to V3a/V3b — notably **B3 race**, with a 1978-revision 1-digit-`MRACE` recode for V3b (documented null caveat for the 1978-rev "other/unknown" codes). **The exhaustive per-variable, per-era value-distribution / sentinel / coding-diff evidence for all seven eras is the auto-generated Appendix C8.20 — Per-variable historical evidence at the end of this file.** The per-variable tables that follow give the V2/V1 detail narrative (accurate for those eras); consult the appendix for the 1982-1991 (V3b/V3a) and 2003-2004 (V2.1) distributions.

The "Years" column in the variable tables below uses the V2/V1 era labels.

---

## Harmonized Variables (73 columns)

### Record Identification

| Variable | Label | Values | Comparability | Years | Notes |
|----------|-------|--------|---------------|-------|-------|
| `data_year` | Data year (added by pipeline) | 1982-2024 | full | All | int32 sibling of `delivery_year`, computed as `int(delivery_year)` during harmonization. Always equal to `int(delivery_year)` for every row. Recommended filter/join key for cross-year analyses (verified 2,427,233/2,427,233 in v2.4.0; see Appendix C8.20). |
| `version_flag` | Revision flag | A, S | full | All | A=2003 revision; S=1989 revision. **Synthesized to `S` for 1992-2002** (no native VERSION field in 1989-rev files) |
| `tabulation_flag` | NCHS tabulated subset flag | 1, 2 | partial | All | 1=exclude from NVSR tabulations; 2=include. NCHS's compound criterion (typically "GA >= 20 weeks OR BW >= 350g when GA unknown") — not a pure GA cutoff. a small share of flag-2 rows (almost all in 2014+) have `gestational_age_combined < 20`, and a non-trivial share of flag-1 rows have GA >= 20 (in the V2.0 1992-2022 slice this was ~5,400 and ~63,700 rows respectively; for the full v2.4.0 per-era `tabulation_flag` distribution see Appendix C8.20). Use `gestational_age_combined` directly when you need a pure GA filter. Field name and position changed across eras (V2:TABFLAG; V1 2006:TABFLG; V1 2014+:OE_TABFLG) |
| `delivery_year` | Year of delivery | 1982-2024 | partial | All | Same concept; field positions differ by era. V2 (1992-2002) sources from DELYR (190-193); V3b/V3a/V1 eras use their era-specific positions (see Appendix C8.20). |
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
| `plurality` | Plurality recode | 1-9 | partial | All | 1=Single through 5=Quintuplet+. 2022 era max is 4. 9=Unknown. **Louisiana 1992-1994 reports 9 for essentially all in-state records** (state non-reporting). In the V2 1992-2002 slice, 1,686 of the 1,713 plurality=9 rows are LA-occurrence 1992-1994 (the remainder are scattered across other 1992-2002 state-years); for the full v2.4.0 per-era `plurality` distribution see Appendix C8.20. See [Comparability §11](COMPARABILITY.md) |
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
| `birthweight` | Birth weight (grams) | 1-9999 | full | All | 9999=Not stated. **Primary BW variable.** V2 sources from DBIRWT (207-210); 397,397 V2 1992-2002-slice rows have BW=9999, driven by TABFLAG=1 (<20wk) records where BW is typically not captured; for the full v2.4.0 per-era `birthweight` distribution see Appendix C8.20 |
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

**Note on reporting flags**: The individual reporting flags (F_MEDUC, F_CLINEST, F_TOBACO, F_RF_PDIAB, V2-era ORIGM/EDUCM/PNCF/etc.) are available in the per-year raw Parquet files (one per data year 1982-2024; in the GitHub source repo they live under `output/yearly_clean/`, and they are bundled in the per-year raw archive in the Zenodo deposit). They are not carried through to the harmonized schema because each flag is era-specific with different positions and naming conventions. Researchers who need item-level reporting flags should work directly with the raw yearly files.

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
| `education_cat4` | Education 4-level | < HS, HS grad, Some college, BA+ | "" if education unknown or blank. **Blank for all V2 records** (V2 populates `maternal_education_unrevised` years-of-school instead of the revised 1-9 categorical scale that the derivation maps from). Cross-era education trends require building a 1989→2003 binning bridge — not provided by this resource |
| `singleton` | Singleton indicator | "1" if plurality=1; "0" if plurality>1; "" if unknown (plurality=9 or blank) | V2 1992-2002 slice: 1,713 blanks total, of which 1,686 are Louisiana 1992-1994 non-reporters (DPLURAL=9, LA-occurrence); the remaining 27 are scattered V2 1992-2002 plurality=9 records across other state-years; for the full v2.4.0 per-era `plurality` distribution underlying this derived flag see Appendix C8.20 |

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
   - The analogous documented quirks for the V3b (1982-1988), V3a (1989-1991), and V2.1 (2003-2004) eras — incl. the V3b 1978-revision 1-digit-`MRACE` recode and its null caveat, and the 2003-2004 dual-certificate handling — are in [`COMPARABILITY.md`](COMPARABILITY.md) and the per-era panels of Appendix C8.20.

---

## Source Crosswalk

For the complete raw-field-to-harmonized mapping by era, see `variable_crosswalk_working.csv` (in the GitHub source repo: `metadata/variable_crosswalk_working.csv`).
For the full schema definition including allowed_values, see `harmonized_schema.csv`.
For the per-era byte-position layouts, see `record_layout_*.csv` (e.g. `record_layout_1982_1988.csv` for the V3b 1978-revision, the 1989-rev `record_layout` family for V3a/V2, `record_layout_2003.csv`/`record_layout_2004.csv` for the V2.1 transition) and `V2_1992_LAYOUT_DECISIONS.md` for the 1989-revision 360-byte layout reconstruction notes.

<!-- C8.20-GENERATED:BEGIN (do not hand-edit; regenerate via scripts/_build_codebook_extensions.py) -->

## Appendix C8.20 — Per-variable historical evidence (auto-generated)

> Auto-generated by `scripts/_build_codebook_extensions.py` — do **not** hand-edit; regenerate. Every count below is derived from the gate-verified parquet; era boundaries are documented NCHS layout constants (see `COMPARABILITY.md` + the layout-source CSVs + the C8.16/C8.17/C8.18/C8.2 receipts).
>
> Provenance: fetal-death derived `fetal_death_derived.parquet` sha256[:12]=`185c071ec76a` · 2,427,233 rows · builder `scripts/_build_codebook_extensions.py`
>
> Era partition: `1982-1988` · `1989-1991` · `1992-2002` · `2003-2004` · `2005-2013` · `2014-2017` · `2018-2024`

**Variable index:** [`version_flag`](#c820-fetal_death-version_flag) · [`tabulation_flag`](#c820-fetal_death-tabulation_flag) · [`delivery_year`](#c820-fetal_death-delivery_year) · [`data_year`](#c820-fetal_death-data_year) · [`residence_status`](#c820-fetal_death-residence_status) · [`maternal_age`](#c820-fetal_death-maternal_age) · [`maternal_age_recode14`](#c820-fetal_death-maternal_age_recode14) · [`maternal_age_recode9`](#c820-fetal_death-maternal_age_recode9) · [`maternal_race_multi`](#c820-fetal_death-maternal_race_multi) · [`maternal_race_recode6`](#c820-fetal_death-maternal_race_recode6) · [`maternal_race_bridged`](#c820-fetal_death-maternal_race_bridged) · [`maternal_race_bridged_detail`](#c820-fetal_death-maternal_race_bridged_detail) · [`hispanic_origin`](#c820-fetal_death-hispanic_origin) · [`race_hispanic_combined`](#c820-fetal_death-race_hispanic_combined) · [`race_hispanic_revised`](#c820-fetal_death-race_hispanic_revised) · [`maternal_education`](#c820-fetal_death-maternal_education) · [`maternal_education_unrevised`](#c820-fetal_death-maternal_education_unrevised) · [`marital_status`](#c820-fetal_death-marital_status) · [`maternal_nativity`](#c820-fetal_death-maternal_nativity) · [`paternal_age_combined`](#c820-fetal_death-paternal_age_combined) · [`paternal_age_recode11`](#c820-fetal_death-paternal_age_recode11) · [`live_birth_order`](#c820-fetal_death-live_birth_order) · [`plurality`](#c820-fetal_death-plurality) · [`prenatal_care_month`](#c820-fetal_death-prenatal_care_month) · [`prenatal_care_month_unrevised`](#c820-fetal_death-prenatal_care_month_unrevised) · [`prenatal_care_recode`](#c820-fetal_death-prenatal_care_recode) · [`delivery_method_recode`](#c820-fetal_death-delivery_method_recode) · [`delivery_method_revised`](#c820-fetal_death-delivery_method_revised) · [`delivery_route`](#c820-fetal_death-delivery_route) · [`prior_cesarean`](#c820-fetal_death-prior_cesarean) · [`prior_cesarean_number`](#c820-fetal_death-prior_cesarean_number) · [`fetal_sex`](#c820-fetal_death-fetal_sex) · [`gestational_age_clinical`](#c820-fetal_death-gestational_age_clinical) · [`gestational_age_oe_edited`](#c820-fetal_death-gestational_age_oe_edited) · [`gestational_age_combined`](#c820-fetal_death-gestational_age_combined) · [`gestational_age_recode12`](#c820-fetal_death-gestational_age_recode12) · [`gestational_age_recode5`](#c820-fetal_death-gestational_age_recode5) · [`oe_gest_recode12`](#c820-fetal_death-oe_gest_recode12) · [`oe_gest_recode5`](#c820-fetal_death-oe_gest_recode5) · [`birthweight`](#c820-fetal_death-birthweight) · [`birthweight_recode14`](#c820-fetal_death-birthweight_recode14) · [`birthweight_recode4`](#c820-fetal_death-birthweight_recode4) · [`fetal_presentation`](#c820-fetal_death-fetal_presentation) · [`prepregnancy_diabetes`](#c820-fetal_death-prepregnancy_diabetes) · [`gestational_diabetes`](#c820-fetal_death-gestational_diabetes) · [`diabetes_unrevised`](#c820-fetal_death-diabetes_unrevised) · [`prepregnancy_hypertension`](#c820-fetal_death-prepregnancy_hypertension) · [`gestational_hypertension`](#c820-fetal_death-gestational_hypertension) · [`chronic_hypertension_unrevised`](#c820-fetal_death-chronic_hypertension_unrevised) · [`pregnancy_hypertension_unrevised`](#c820-fetal_death-pregnancy_hypertension_unrevised) · [`eclampsia`](#c820-fetal_death-eclampsia) · [`eclampsia_unrevised`](#c820-fetal_death-eclampsia_unrevised) · [`tobacco_use_revised`](#c820-fetal_death-tobacco_use_revised) · [`tobacco_cig_1st_tri`](#c820-fetal_death-tobacco_cig_1st_tri) · [`tobacco_cig_2nd_tri`](#c820-fetal_death-tobacco_cig_2nd_tri) · [`tobacco_cig_3rd_tri`](#c820-fetal_death-tobacco_cig_3rd_tri) · [`tobacco_cig_prepreg`](#c820-fetal_death-tobacco_cig_prepreg) · [`tobacco_use_unrevised`](#c820-fetal_death-tobacco_use_unrevised) · [`prepregnancy_bmi`](#c820-fetal_death-prepregnancy_bmi) · [`prepregnancy_bmi_recode`](#c820-fetal_death-prepregnancy_bmi_recode) · [`uterine_rupture`](#c820-fetal_death-uterine_rupture) · [`icu_admission`](#c820-fetal_death-icu_admission) · [`cause_icd10`](#c820-fetal_death-cause_icd10) · [`cause_recode124`](#c820-fetal_death-cause_recode124) · [`cause_reporting_flag`](#c820-fetal_death-cause_reporting_flag) · [`attendant`](#c820-fetal_death-attendant) · [`delivery_place_revised`](#c820-fetal_death-delivery_place_revised) · [`delivery_place_unrevised`](#c820-fetal_death-delivery_place_unrevised) · [`delivery_place_recode`](#c820-fetal_death-delivery_place_recode) · [`breech_unrevised`](#c820-fetal_death-breech_unrevised) · [`estimated_time_fetal_death`](#c820-fetal_death-estimated_time_fetal_death) · [`gestation_imputed_flag`](#c820-fetal_death-gestation_imputed_flag) · [`obgest_used_flag`](#c820-fetal_death-obgest_used_flag)

### `version_flag` <a id="c820-fetal_death-version_flag"></a>

_Schema note:_ A,S — A=2003 revision; S=1989 revision. Same coding all years. 1982-1988 and 1992-2002 files have no native VERSION field; harmonize.py synthesizes S (1978-rev predates 2003-rev split). In 2006 both A and S states present; by 2022 nearly…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `S`: 421,125 (100.00%) | 0.00% |
| `1989-1991` | 188,909 | `S`: 188,909 (100.00%) | 0.00% |
| `1992-2002` | 700,704 | `S`: 700,704 (100.00%) | 0.00% |
| `2003-2004` | 107,782 | `S`: 104,824 (97.26%); `A`: 2,958 (2.74%) | 0.00% |
| `2005-2013` | 510,528 | `S`: 304,962 (59.73%); `A`: 205,566 (40.27%) | 0.00% |
| `2014-2017` | 204,923 | `A`: 178,700 (87.20%); `S`: 26,223 (12.80%) | 0.00% |
| `2018-2024` | 293,262 | `A`: 293,262 (100.00%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`A`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`S`} _(codes ≥0.05% of an era)_

### `tabulation_flag` <a id="c820-fetal_death-tabulation_flag"></a>

_Schema note:_ 1-2 — Same concept (1=exclude <20wk; 2=include >=20wk). Field name and position changed between 2006 and 2014/2022. Use to filter tabulation-eligible records.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `2`: 211,192 (50.15%); `1`: 209,933 (49.85%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 96,793 (51.24%); `2`: 92,116 (48.76%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 399,603 (57.03%); `2`: 301,101 (42.97%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 55,693 (51.67%); `2`: 52,089 (48.33%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 284,370 (55.70%); `2`: 226,158 (44.30%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 110,299 (53.82%); `2`: 94,624 (46.18%) | 0.00% |
| `2018-2024` | 293,262 | `2`: 146,660 (50.01%); `1`: 146,602 (49.99%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `delivery_year` <a id="c820-fetal_death-delivery_year"></a>

_Schema note:_ 1982-2024 — Same concept (4-digit year); positions and field names differ across eras. V2 (1992-2002) sources from DELYR.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1982`: 62,352 (14.81%); `1983`: 60,584 (14.39%); `1988`: 59,935 (14.23%); `1984`: 59,863 (14.22%); `1985`: 59,690 (14.17%); `1987`: 59,358 (14.10%); `1986`: 59,343 (14.09%) | 0.00% |
| `1989-1991` | 188,909 | `1990`: 64,349 (34.06%); `1991`: 63,265 (33.49%); `1989`: 61,295 (32.45%) | 0.00% |
| `1992-2002` | 700,704 | `1993`: 71,181 (10.16%); `1992`: 70,929 (10.12%); `1994`: 66,091 (9.43%); `1996`: 65,163 (9.30%); `1997`: 64,002 (9.13%); `1999`: 63,875 (9.12%); `1998`: 63,438 (9.05%); `1995`: 63,170 (9.02%); _(+3 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `2003`: 54,497 (50.56%); `2004`: 53,285 (49.44%) | 0.00% |
| `2005-2013` | 510,528 | `2007`: 60,973 (11.94%); `2008`: 60,154 (11.78%); `2011`: 58,361 (11.43%); `2010`: 58,079 (11.38%); `2009`: 56,685 (11.10%); `2012`: 56,201 (11.01%); `2013`: 54,028 (10.58%); `2005`: 53,333 (10.45%); _(+1 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `2014`: 52,872 (25.80%); `2015`: 51,490 (25.13%); `2016`: 51,391 (25.08%); `2017`: 49,170 (23.99%) | 0.00% |
| `2018-2024` | 293,262 | `2018`: 47,676 (16.26%); `2019`: 46,007 (15.69%); `2021`: 42,428 (14.47%); `2020`: 41,816 (14.26%); `2022`: 40,113 (13.68%); `2023`: 39,574 (13.49%); `2024`: 35,648 (12.16%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1989`, `1990`, `1991`}; dropped {`1982`, `1983`, `1984`, `1985`, `1986`, `1987`, `1988`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: added {`1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`}; dropped {`1989`, `1990`, `1991`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`2003`, `2004`}; dropped {`1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`}; dropped {`2003`, `2004`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`2014`, `2015`, `2016`, `2017`}; dropped {`2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`2018`, `2019`, `2020`, `2021`, `2022`, `2023`, `2024`}; dropped {`2014`, `2015`, `2016`, `2017`} _(codes ≥0.05% of an era)_

### `data_year` <a id="c820-fetal_death-data_year"></a>

_Schema note:_ 1982-2024 — Convenience int32 sibling of `delivery_year`. Always equal to `int(delivery_year)` for every row (verified 2,427,233/2,427,233 in v2.4.0). Recommended filter/join key for cross-year analyses. Includes V2.1 transition years 20…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1982`: 62,352 (14.81%); `1983`: 60,584 (14.39%); `1988`: 59,935 (14.23%); `1984`: 59,863 (14.22%); `1985`: 59,690 (14.17%); `1987`: 59,358 (14.10%); `1986`: 59,343 (14.09%) | 0.00% |
| `1989-1991` | 188,909 | `1990`: 64,349 (34.06%); `1991`: 63,265 (33.49%); `1989`: 61,295 (32.45%) | 0.00% |
| `1992-2002` | 700,704 | `1993`: 71,181 (10.16%); `1992`: 70,929 (10.12%); `1994`: 66,091 (9.43%); `1996`: 65,163 (9.30%); `1997`: 64,002 (9.13%); `1999`: 63,875 (9.12%); `1998`: 63,438 (9.05%); `1995`: 63,170 (9.02%); _(+3 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `2003`: 54,497 (50.56%); `2004`: 53,285 (49.44%) | 0.00% |
| `2005-2013` | 510,528 | `2007`: 60,973 (11.94%); `2008`: 60,154 (11.78%); `2011`: 58,361 (11.43%); `2010`: 58,079 (11.38%); `2009`: 56,685 (11.10%); `2012`: 56,201 (11.01%); `2013`: 54,028 (10.58%); `2005`: 53,333 (10.45%); _(+1 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `2014`: 52,872 (25.80%); `2015`: 51,490 (25.13%); `2016`: 51,391 (25.08%); `2017`: 49,170 (23.99%) | 0.00% |
| `2018-2024` | 293,262 | `2018`: 47,676 (16.26%); `2019`: 46,007 (15.69%); `2021`: 42,428 (14.47%); `2020`: 41,816 (14.26%); `2022`: 40,113 (13.68%); `2023`: 39,574 (13.49%); `2024`: 35,648 (12.16%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1989`, `1990`, `1991`}; dropped {`1982`, `1983`, `1984`, `1985`, `1986`, `1987`, `1988`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: added {`1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`}; dropped {`1989`, `1990`, `1991`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`2003`, `2004`}; dropped {`1992`, `1993`, `1994`, `1995`, `1996`, `1997`, `1998`, `1999`, `2000`, `2001`, `2002`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`}; dropped {`2003`, `2004`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`2014`, `2015`, `2016`, `2017`}; dropped {`2005`, `2006`, `2007`, `2008`, `2009`, `2010`, `2011`, `2012`, `2013`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`2018`, `2019`, `2020`, `2021`, `2022`, `2023`, `2024`}; dropped {`2014`, `2015`, `2016`, `2017`} _(codes ≥0.05% of an era)_

### `residence_status` <a id="c820-fetal_death-residence_status"></a>

_Schema note:_ 1-4 — 1=Resident; 2=Intrastate nonresident; 3=Interstate nonresident; 4=Foreign resident. Same coding; positions differ in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 310,242 (73.67%); `2`: 96,814 (22.99%); `3`: 13,659 (3.24%); `4`: 410 (0.10%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 135,531 (71.74%); `2`: 47,377 (25.08%); `3`: 5,824 (3.08%); `4`: 177 (0.09%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 512,536 (73.15%); `2`: 167,271 (23.87%); `3`: 20,205 (2.88%); `4`: 692 (0.10%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 76,839 (71.29%); `2`: 27,628 (25.63%); `3`: 3,158 (2.93%); `4`: 157 (0.15%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 354,039 (69.35%); `2`: 141,077 (27.63%); `3`: 14,849 (2.91%); `4`: 563 (0.11%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 136,043 (66.39%); `2`: 62,184 (30.35%); `3`: 6,338 (3.09%); `4`: 358 (0.17%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 185,169 (63.14%); `2`: 96,801 (33.01%); `3`: 10,421 (3.55%); `4`: 871 (0.30%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `maternal_age` <a id="c820-fetal_death-maternal_age"></a>

_Schema note:_ 10-54;99 — V2 1989-rev DMAGE: exact single year (observed 10-54; 99=Unknown). V1 2003-rev MAGER: 12-50 with top-coded 50+ and bottom-coded 12-. 108 V2 rows have age 50-54 and 42 V2 rows have age 10-11 — outside V1 boundary-coded range. 0…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `26`: 24,890 (5.91%); `27`: 24,551 (5.83%); `25`: 24,549 (5.83%); `24`: 24,185 (5.74%); `28`: 23,690 (5.63%); `23`: 23,317 (5.54%); `29`: 22,511 (5.35%); `22`: 22,037 (5.23%); _(+32 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `27`: 10,527 (5.57%); `28`: 10,444 (5.53%); `29`: 10,422 (5.52%); `26`: 10,177 (5.39%); `30`: 9,804 (5.19%); `25`: 9,798 (5.19%); `24`: 9,385 (4.97%); `31`: 9,316 (4.93%); _(+32 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `30`: 35,651 (5.09%); `29`: 35,328 (5.04%); `31`: 34,579 (4.93%); `28`: 34,172 (4.88%); `27`: 33,438 (4.77%); `32`: 32,830 (4.69%); `26`: 31,455 (4.49%); `33`: 31,029 (4.43%); _(+37 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `28`: 25,433 (4.98%); `30`: 25,433 (4.98%); `29`: 25,000 (4.90%); `31`: 24,852 (4.87%); `26`: 24,006 (4.70%); `27`: 23,635 (4.63%); `32`: 23,626 (4.63%); `33`: 22,973 (4.50%); _(+31 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `32`: 10,923 (5.33%); `31`: 10,901 (5.32%); `30`: 10,851 (5.30%); `28`: 10,699 (5.22%); `29`: 10,507 (5.13%); `33`: 10,490 (5.12%); `34`: 10,149 (4.95%); `27`: 9,858 (4.81%); _(+31 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `31`: 16,806 (5.73%); `32`: 16,495 (5.62%); `33`: 16,198 (5.52%); `30`: 16,034 (5.47%); `29`: 15,879 (5.41%); `34`: 15,691 (5.35%); `28`: 15,492 (5.28%); `35`: 14,513 (4.95%); _(+31 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-1991`→`1992-2002`: added {`46`, `47`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: dropped {`13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`48`, `50`} _(codes ≥0.05% of an era)_

### `maternal_age_recode14` <a id="c820-fetal_death-maternal_age_recode14"></a>

_Schema note:_ 1-14 — 14-category recode. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `10`: 25,309 (23.48%); `09`: 23,866 (22.14%); `08`: 21,452 (19.90%); `11`: 18,704 (17.35%); `12`: 7,732 (7.17%); `07`: 3,480 (3.23%); `06`: 2,873 (2.67%); `05`: 1,772 (1.64%); _(+5 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `09`: 120,192 (23.54%); `10`: 118,956 (23.30%); `08`: 99,612 (19.51%); `11`: 88,615 (17.36%); `12`: 36,944 (7.24%); `07`: 16,208 (3.17%); `06`: 11,958 (2.34%); `05`: 7,234 (1.42%); _(+5 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `10`: 53,314 (26.02%); `09`: 49,858 (24.33%); `11`: 38,070 (18.58%); `08`: 35,954 (17.55%); `12`: 14,901 (7.27%); `07`: 4,678 (2.28%); `06`: 3,137 (1.53%); `05`: 1,716 (0.84%); _(+5 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `10`: 81,224 (27.70%); `09`: 70,099 (23.90%); `11`: 59,356 (20.24%); `08`: 45,511 (15.52%); `12`: 21,876 (7.46%); `07`: 5,514 (1.88%); `06`: 3,779 (1.29%); `13`: 2,188 (0.75%); _(+5 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`01`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`14`} _(codes ≥0.05% of an era)_

### `maternal_age_recode9` <a id="c820-fetal_death-maternal_age_recode9"></a>

_Schema note:_ 1-9 — 9-category recode. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `5`: 25,309 (23.48%); `4`: 23,866 (22.14%); `3`: 21,452 (19.90%); `6`: 18,704 (17.35%); `2`: 9,774 (9.07%); `7`: 7,732 (7.17%); `8`: 649 (0.60%); `1`: 273 (0.25%); _(+1 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `4`: 120,192 (23.54%); `5`: 118,956 (23.30%); `3`: 99,612 (19.51%); `6`: 88,615 (17.36%); `2`: 41,352 (8.10%); `7`: 36,944 (7.24%); `8`: 3,625 (0.71%); `1`: 1,065 (0.21%); _(+1 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `5`: 53,314 (26.02%); `4`: 49,858 (24.33%); `6`: 38,070 (18.58%); `3`: 35,954 (17.55%); `7`: 14,901 (7.27%); `2`: 10,947 (5.34%); `8`: 1,577 (0.77%); `1`: 183 (0.09%); _(+1 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `5`: 81,224 (27.70%); `4`: 70,099 (23.90%); `6`: 59,356 (20.24%); `3`: 45,511 (15.52%); `7`: 21,876 (7.46%); `2`: 12,583 (4.29%); `8`: 2,188 (0.75%); `1`: 213 (0.07%); _(+1 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `9` | 23 | 0.02% |
| `2005-2013` | `9` | 167 | 0.03% |
| `2014-2017` | `9` | 119 | 0.06% |
| `2018-2024` | `9` | 212 | 0.07% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`9`} _(codes ≥0.05% of an era)_

### `maternal_race_multi` <a id="c820-fetal_death-maternal_race_multi"></a>

_Schema note:_ 1-30 — 31-category multi-race recode. Not in 2006 public-use file. Available 2014+ (version A only).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `01`: 51,556 (25.16%); `02`: 26,283 (12.83%); `04`: 5,817 (2.84%); `05`: 662 (0.32%); `03`: 584 (0.28%); `12`: 375 (0.18%); `13`: 332 (0.16%); `15`: 169 (0.08%); _(+1 more codes)_ | 58.12% |
| `2018-2024` | 293,262 | `01`: 151,693 (51.73%); `02`: 72,351 (24.67%); `04`: 14,153 (4.83%); `05`: 2,043 (0.70%); `03`: 1,897 (0.65%); `06`: 1,563 (0.53%); `13`: 581 (0.20%); `10`: 439 (0.15%); _(+22 more codes)_ | 16.26% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | _null/blank_ | 119,093 | 58.12% |
| `2018-2024` | _null/blank_ | 47,676 | 16.26% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`01`, `02`, `03`, `04`, `05`, `12`, `13`, `15`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`06`, `10`, `14`}; dropped {`12`, `15`} _(codes ≥0.05% of an era)_

### `maternal_race_recode6` <a id="c820-fetal_death-maternal_race_recode6"></a>

_Schema note:_ 1-6 — 6-category multi-race recode. Not in 2006. Available 2014+ (version A only).

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `1`: 107,586 (52.50%); `2`: 54,737 (26.71%); `4`: 11,974 (5.84%); `6`: 1,956 (0.95%); `3`: 1,228 (0.60%); `5`: 1,219 (0.59%); `9`: 5 (0.00%) | 12.79% |
| `2018-2024` | 293,262 | `1`: 181,109 (61.76%); `2`: 86,383 (29.46%); `4`: 17,175 (5.86%); `6`: 4,015 (1.37%); `5`: 2,401 (0.82%); `3`: 2,179 (0.74%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `9` | 5 | 0.00% |
| `2014-2017` | _null/blank_ | 26,218 | 12.79% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`, `4`, `5`, `6`} _(codes ≥0.05% of an era)_

### `maternal_race_bridged` <a id="c820-fetal_death-maternal_race_bridged"></a>

_Schema note:_ 1-4 — 4-category bridged race (1=White 2=Black 3=AIAN 4=API). V2 sources from raw MRACE (79-80) and harmonize.py recodes 01->1, 02->2, 03->3, 04-78->4, 99->blank (unknown). Available in 2006 (A+S) and 2014 (A+S). Not present as data fiel…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 294,082 (69.83%); `2`: 92,321 (21.92%); `4`: 11,639 (2.76%); `3`: 2,426 (0.58%) | 4.91% |
| `1989-1991` | 188,909 | `1`: 132,946 (70.38%); `2`: 48,714 (25.79%); `4`: 5,989 (3.17%); `3`: 1,095 (0.58%) | 0.09% |
| `1992-2002` | 700,704 | `1`: 475,007 (67.79%); `2`: 193,381 (27.60%); `4`: 28,478 (4.06%); `3`: 3,836 (0.55%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 73,656 (68.34%); `2`: 27,029 (25.08%); `4`: 6,408 (5.95%); `3`: 689 (0.64%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 333,783 (65.38%); `2`: 140,271 (27.48%); `4`: 33,326 (6.53%); `3`: 3,148 (0.62%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 129,534 (63.21%); `2`: 59,516 (29.04%); `4`: 14,465 (7.06%); `3`: 1,408 (0.69%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 20,657 | 4.91% |
| `1989-1991` | _null/blank_ | 165 | 0.09% |
| `1992-2002` | _null/blank_ | 2 | 0.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `3`, `4`} _(codes ≥0.05% of an era)_

### `maternal_race_bridged_detail` <a id="c820-fetal_death-maternal_race_bridged_detail"></a>

_Schema note:_ 01-14;18;21-24;28;38;48;58;68;78;99 — WARNING: V2 vs V1 use INCOMPATIBLE codings in this column. V2 1989-rev MRACE: 01-07 single race + 18/28/38/48/58/68/78 Asian/PI subcodes + 99=Unknown. V1 2006 MBRACE: 01-14 single race + 21-24 bridge…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 294,082 (69.83%); `2`: 92,321 (21.92%); `9`: 20,568 (4.88%); `0`: 5,062 (1.20%); `3`: 2,426 (0.58%); `8`: 2,306 (0.55%); `6`: 1,858 (0.44%); `5`: 1,584 (0.38%); _(+2 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `01`: 132,946 (70.38%); `02`: 48,714 (25.79%); `08`: 2,791 (1.48%); `07`: 1,180 (0.62%); `03`: 1,095 (0.58%); `06`: 762 (0.40%); `05`: 749 (0.40%); `04`: 507 (0.27%); _(+1 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `01`: 475,007 (67.79%); `02`: 193,381 (27.60%); `68`: 6,536 (0.93%); `78`: 5,352 (0.76%); `07`: 4,899 (0.70%); `04`: 3,852 (0.55%); `03`: 3,836 (0.55%); `06`: 2,416 (0.34%); _(+7 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `01`: 2,474 (2.30%); `02`: 556 (0.52%); `10`: 59 (0.05%); `03`: 58 (0.05%); `04`: 37 (0.03%); `15`: 17 (0.02%); `06`: 16 (0.01%); `08`: 16 (0.01%); _(+12 more codes)_ | 96.92% |
| `2005-2013` | 510,528 | `01`: 11,511 (2.25%); `02`: 3,685 (0.72%); `03`: 239 (0.05%); `10`: 175 (0.03%); `04`: 150 (0.03%); `06`: 138 (0.03%); `09`: 102 (0.02%); `05`: 74 (0.01%); _(+10 more codes)_ | 96.80% |
| `2014-2017` | 204,923 | — | 100.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `9` | 20,568 | 4.88% |
| `1992-2002` | `99` | 2 | 0.00% |
| `2003-2004` | `99` | 3 | 0.00% |
| `2003-2004` | _null/blank_ | 104,460 | 96.92% |
| `2005-2013` | _null/blank_ | 494,166 | 96.80% |
| `2014-2017` | _null/blank_ | 204,923 | 100.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`}; dropped {`0`, `1`, `2`, `3`, `4`, `5`, `6`, `8`, `9`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: added {`18`, `28`, `48`, `68`, `78`}; dropped {`08`, `09`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`10`}; dropped {`04`, `05`, `06`, `07`, `18`, `28`, `48`, `68`, `78`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: dropped {`03`, `10`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: dropped {`01`, `02`} _(codes ≥0.05% of an era)_

### `hispanic_origin` <a id="c820-fetal_death-hispanic_origin"></a>

_Schema note:_ 0-9 — 0=Non-Hispanic; 1=Mexican; 2=PR; 3=Cuban; 4=Central/South American; 5=Other Hispanic; 9=Unknown. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `0`: 134,293 (71.09%); `9`: 39,234 (20.77%); `1`: 7,553 (4.00%); `5`: 2,998 (1.59%); `4`: 2,264 (1.20%); `2`: 2,259 (1.20%); `3`: 308 (0.16%) | 0.00% |
| `1992-2002` | 700,704 | `0`: 503,528 (71.86%); `9`: 108,674 (15.51%); `1`: 37,654 (5.37%); `5`: 18,876 (2.69%); `2`: 15,406 (2.20%); `4`: 15,371 (2.19%); `3`: 1,195 (0.17%) | 0.00% |
| `2003-2004` | 107,782 | `0`: 76,148 (70.65%); `9`: 12,816 (11.89%); `1`: 8,195 (7.60%); `5`: 4,704 (4.36%); `4`: 3,481 (3.23%); `2`: 2,234 (2.07%); `3`: 204 (0.19%) | 0.00% |
| `2005-2013` | 510,528 | `0`: 360,449 (70.60%); `9`: 61,249 (12.00%); `1`: 37,829 (7.41%); `5`: 25,660 (5.03%); `4`: 14,923 (2.92%); `2`: 9,474 (1.86%); `3`: 944 (0.18%) | 0.00% |
| `2014-2017` | 204,923 | `0`: 144,389 (70.46%); `9`: 27,213 (13.28%); `1`: 14,892 (7.27%); `5`: 8,995 (4.39%); `4`: 5,685 (2.77%); `2`: 3,246 (1.58%); `3`: 503 (0.25%) | 0.00% |
| `2018-2024` | 293,262 | `0`: 211,540 (72.13%); `9`: 31,305 (10.67%); `1`: 21,327 (7.27%); `5`: 13,840 (4.72%); `4`: 10,074 (3.44%); `2`: 4,151 (1.42%); `3`: 1,025 (0.35%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 39,234 | 20.77% |
| `1992-2002` | `9` | 108,674 | 15.51% |
| `2003-2004` | `9` | 12,816 | 11.89% |
| `2005-2013` | `9` | 61,249 | 12.00% |
| `2014-2017` | `9` | 27,213 | 13.28% |
| `2018-2024` | `9` | 31,305 | 10.67% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`0`, `1`, `2`, `3`, `4`, `5`, `9`} _(codes ≥0.05% of an era)_

### `race_hispanic_combined` <a id="c820-fetal_death-race_hispanic_combined"></a>

_Schema note:_ 1-9 — Combined bridged-race/Hispanic recode. Present in 2006 (A+S) and 2014 (A+S). Not in 2022 layout.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `6`: 89,578 (47.42%); `9`: 39,234 (20.77%); `7`: 39,141 (20.72%); `1`: 7,553 (4.00%); `8`: 5,574 (2.95%); `5`: 2,998 (1.59%); `4`: 2,264 (1.20%); `2`: 2,259 (1.20%); _(+1 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `6`: 317,241 (45.27%); `7`: 159,732 (22.80%); `9`: 108,674 (15.51%); `1`: 37,654 (5.37%); `8`: 26,555 (3.79%); `5`: 18,876 (2.69%); `2`: 15,406 (2.20%); `4`: 15,371 (2.19%); _(+1 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `6`: 47,585 (44.15%); `7`: 22,801 (21.15%); `9`: 12,816 (11.89%); `1`: 8,195 (7.60%); `8`: 5,762 (5.35%); `5`: 4,704 (4.36%); `4`: 3,481 (3.23%); `2`: 2,234 (2.07%); _(+1 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `6`: 214,027 (41.92%); `7`: 117,468 (23.01%); `9`: 61,249 (12.00%); `1`: 37,829 (7.41%); `8`: 28,954 (5.67%); `5`: 25,660 (5.03%); `4`: 14,923 (2.92%); `2`: 9,474 (1.86%); _(+1 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `6`: 84,784 (41.37%); `7`: 48,158 (23.50%); `9`: 27,213 (13.28%); `1`: 14,892 (7.27%); `8`: 11,447 (5.59%); `5`: 8,995 (4.39%); `4`: 5,685 (2.77%); `2`: 3,246 (1.58%); _(+1 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 39,234 | 20.77% |
| `1992-2002` | `9` | 108,674 | 15.51% |
| `2003-2004` | `9` | 12,816 | 11.89% |
| `2005-2013` | `9` | 61,249 | 12.00% |
| `2014-2017` | `9` | 27,213 | 13.28% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`} _(codes ≥0.05% of an era)_

### `race_hispanic_revised` <a id="c820-fetal_death-race_hispanic_revised"></a>

_Schema note:_ 1-8 — 8-category multi-race/Hispanic recode. Version A only. Not in 2006. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `1`: 67,143 (32.76%); `2`: 43,951 (21.45%); `7`: 30,386 (14.83%); `8`: 25,413 (12.40%); `4`: 8,720 (4.26%); `6`: 1,561 (0.76%); `3`: 1,005 (0.49%); `5`: 521 (0.25%) | 12.80% |
| `2018-2024` | 293,262 | `1`: 118,846 (40.53%); `2`: 73,565 (25.09%); `7`: 50,417 (17.19%); `8`: 31,305 (10.67%); `4`: 13,322 (4.54%); `6`: 3,228 (1.10%); `3`: 1,595 (0.54%); `5`: 984 (0.34%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`} _(codes ≥0.05% of an era)_

### `maternal_education` <a id="c820-fetal_death-maternal_education"></a>

_Schema note:_ 1-9 — Revised 2003 coding (1-9). Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `9`: 660 (0.61%); `3`: 630 (0.58%); `4`: 468 (0.43%); `2`: 442 (0.41%); `6`: 331 (0.31%); `5`: 169 (0.16%); `7`: 117 (0.11%); `1`: 109 (0.10%); _(+1 more codes)_ | 97.26% |
| `2005-2013` | 510,528 | `3`: 3,908 (0.77%); `2`: 2,917 (0.57%); `4`: 2,496 (0.49%); `9`: 1,868 (0.37%); `6`: 1,828 (0.36%); `1`: 1,114 (0.22%); `5`: 817 (0.16%); `7`: 537 (0.11%); _(+1 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `9`: 62,892 (30.69%); `3`: 42,905 (20.94%); `4`: 20,499 (10.00%); `6`: 16,705 (8.15%); `2`: 13,728 (6.70%); `5`: 7,986 (3.90%); `7`: 7,225 (3.53%); `1`: 4,885 (2.38%); _(+1 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `9`: 103,329 (35.23%); `3`: 72,035 (24.56%); `6`: 31,252 (10.66%); `4`: 30,172 (10.29%); `2`: 16,777 (5.72%); `7`: 14,638 (4.99%); `5`: 13,735 (4.68%); `1`: 7,439 (2.54%); _(+1 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `9` | 660 | 0.61% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `9` | 1,868 | 0.37% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `9` | 62,892 | 30.69% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 103,329 | 35.23% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`1`, `2`, `3`, `4`, `5`, `6`, `7`, `9`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`8`} _(codes ≥0.05% of an era)_

### `maternal_education_unrevised` <a id="c820-fetal_death-maternal_education_unrevised"></a>

_Schema note:_ 0-99 — Unrevised years-of-school coding (00-17; 99). V2 1992-2002 sources from DMEDUC (82-83); V1 2005-2006 sources from UMEDUC (S-version only). Blank for 2007-2013 (NCHS did not include UMEDUC in those V1 public-use years). Not in 2014…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `99`: 174,802 (41.51%); `12`: 114,988 (27.30%); `16`: 24,431 (5.80%); `14`: 20,784 (4.94%); `11`: 17,868 (4.24%); `13`: 16,021 (3.80%); `10`: 15,362 (3.65%); `17`: 11,540 (2.74%); _(+11 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `99`: 79,791 (42.24%); `12`: 47,357 (25.07%); `16`: 11,240 (5.95%); `14`: 10,360 (5.48%); `11`: 8,154 (4.32%); `13`: 6,820 (3.61%); `10`: 6,449 (3.41%); `17`: 4,903 (2.60%); _(+11 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `99`: 267,642 (38.20%); `12`: 176,407 (25.18%); `16`: 55,303 (7.89%); `14`: 42,391 (6.05%); `11`: 29,828 (4.26%); `17`: 27,274 (3.89%); `13`: 26,050 (3.72%); `10`: 23,637 (3.37%); _(+11 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `99`: 38,465 (35.69%); `12`: 25,691 (23.84%); `16`: 9,391 (8.71%); `14`: 6,600 (6.12%); `17`: 5,395 (5.01%); `11`: 4,202 (3.90%); `13`: 3,857 (3.58%); `10`: 2,984 (2.77%); _(+11 more codes)_ | 2.74% |
| `2005-2013` | 510,528 | `99`: 35,796 (7.01%); `12`: 21,536 (4.22%); `16`: 7,886 (1.54%); `14`: 5,246 (1.03%); `17`: 4,975 (0.97%); `11`: 3,261 (0.64%); `13`: 3,195 (0.63%); `10`: 2,214 (0.43%); _(+11 more codes)_ | 82.29% |
| `2014-2017` | 204,923 | — | 100.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `99` | 174,802 | 41.51% |
| `1989-1991` | `99` | 79,791 | 42.24% |
| `1992-2002` | `99` | 267,642 | 38.20% |
| `2003-2004` | `99` | 38,465 | 35.69% |
| `2003-2004` | _null/blank_ | 2,958 | 2.74% |
| `2005-2013` | `99` | 35,796 | 7.01% |
| `2005-2013` | _null/blank_ | 420,131 | 82.29% |
| `2014-2017` | _null/blank_ | 204,923 | 100.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`00`, `02`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: dropped {`00`, `02`, `03`, `04`, `05`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: dropped {`06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `99`} _(codes ≥0.05% of an era)_

### `marital_status` <a id="c820-fetal_death-marital_status"></a>

_Schema note:_ 1-9 — 1=Married; 2=Unmarried; 9=Unknown. V2 1992-2002 sources from DMAR (86); V1 2005-2013 sources from MAR (A+S). Not in 2014 or 2022 public-use fetal death layouts.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `9`: 173,654 (41.24%); `1`: 171,515 (40.73%); `2`: 75,956 (18.04%) | 0.00% |
| `1989-1991` | 188,909 | `9`: 79,332 (41.99%); `1`: 68,436 (36.23%); `2`: 41,141 (21.78%) | 0.00% |
| `1992-2002` | 700,704 | `9`: 332,411 (47.44%); `1`: 217,360 (31.02%); `2`: 150,933 (21.54%) | 0.00% |
| `2003-2004` | 107,782 | `9`: 54,428 (50.50%); `1`: 30,227 (28.04%); `2`: 23,127 (21.46%) | 0.00% |
| `2005-2013` | 510,528 | `9`: 195,094 (38.21%); `1`: 161,307 (31.60%); `2`: 154,127 (30.19%) | 0.00% |
| `2014-2017` | 204,923 | — | 100.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `9` | 173,654 | 41.24% |
| `1989-1991` | `9` | 79,332 | 41.99% |
| `1992-2002` | `9` | 332,411 | 47.44% |
| `2003-2004` | `9` | 54,428 | 50.50% |
| `2005-2013` | `9` | 195,094 | 38.21% |
| `2014-2017` | _null/blank_ | 204,923 | 100.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `maternal_nativity` <a id="c820-fetal_death-maternal_nativity"></a>

_Schema note:_ 1-3 — 1=Native born; 2=Foreign born; 3=Unknown. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `1`: 129,637 (63.26%); `3`: 45,797 (22.35%); `2`: 29,489 (14.39%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 228,707 (77.99%); `2`: 43,751 (14.92%); `3`: 20,804 (7.09%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`} _(codes ≥0.05% of an era)_

### `paternal_age_combined` <a id="c820-fetal_death-paternal_age_combined"></a>

_Schema note:_ 10-99 — 10-98 single year; 99=Unknown. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `99`: 196,250 (46.60%); `28`: 14,004 (3.33%); `30`: 14,003 (3.33%); `27`: 13,461 (3.20%); `29`: 13,386 (3.18%); `26`: 13,022 (3.09%); `25`: 12,547 (2.98%); `31`: 11,933 (2.83%); _(+69 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `99`: 100,868 (53.40%); `30`: 5,289 (2.80%); `29`: 5,143 (2.72%); `31`: 5,106 (2.70%); `28`: 4,998 (2.65%); `27`: 4,936 (2.61%); `32`: 4,725 (2.50%); `26`: 4,644 (2.46%); _(+57 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `99`: 409,868 (58.49%); `30`: 15,916 (2.27%); `31`: 15,528 (2.22%); `32`: 15,324 (2.19%); `29`: 15,273 (2.18%); `33`: 14,754 (2.11%); `34`: 13,927 (1.99%); `28`: 13,858 (1.98%); _(+76 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `99`: 2,695 (0.53%); `26`: 691 (0.14%); `30`: 643 (0.13%); `29`: 642 (0.13%); `28`: 625 (0.12%); `27`: 621 (0.12%); `25`: 583 (0.11%); `33`: 583 (0.11%); _(+50 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `99`: 118,450 (57.80%); `32`: 4,748 (2.32%); `31`: 4,665 (2.28%); `33`: 4,580 (2.23%); `30`: 4,555 (2.22%); `34`: 4,458 (2.18%); `29`: 4,310 (2.10%); `28`: 4,163 (2.03%); _(+61 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `99`: 163,376 (55.71%); `33`: 7,353 (2.51%); `32`: 7,214 (2.46%); `31`: 7,071 (2.41%); `30`: 7,052 (2.40%); `34`: 6,947 (2.37%); `35`: 6,632 (2.26%); `29`: 6,413 (2.19%); _(+66 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `99` | 196,250 | 46.60% |
| `1989-1991` | `99` | 100,868 | 53.40% |
| `1992-2002` | `98` | 2 | 0.00% |
| `1992-2002` | `99` | 409,868 | 58.49% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `99` | 2,695 | 0.53% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `99` | 118,450 | 57.80% |
| `2018-2024` | `98` | 1 | 0.00% |
| `2018-2024` | `99` | 163,376 | 55.71% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: dropped {`53`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: added {`15`, `53`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: dropped {`15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `49`, `50`, `51`, `52`, `53`, `99`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `99`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`16`, `17`, `18`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `49`, `50`, `51`, `52`, `53`, `54`, `55`} _(codes ≥0.05% of an era)_

### `paternal_age_recode11` <a id="c820-fetal_death-paternal_age_recode11"></a>

_Schema note:_ 01-11 — 11-category recode. V2 1989-rev FAGE11 is 12-cat (10=55-59, 11=60-98, 12=Unknown); harmonize.py collapses to V1 11-cat (V2 10/11 -> 10 [55+]; V2 12 -> 11 [Unknown]). Full 12-cat detail preserved in yearly raw parquets. Position d…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `11`: 196,250 (46.60%); `04`: 66,420 (15.77%); `05`: 57,633 (13.69%); `03`: 42,765 (10.15%); `06`: 31,825 (7.56%); `07`: 12,268 (2.91%); `02`: 7,593 (1.80%); `08`: 4,073 (0.97%); _(+3 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `11`: 100,868 (53.40%); `04`: 23,919 (12.66%); `05`: 23,452 (12.41%); `03`: 14,595 (7.73%); `06`: 14,141 (7.49%); `07`: 5,824 (3.08%); `02`: 3,393 (1.80%); `08`: 1,805 (0.96%); _(+3 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `11`: 409,858 (58.49%); `05`: 75,449 (10.77%); `04`: 66,510 (9.49%); `06`: 53,496 (7.63%); `03`: 45,931 (6.55%); `07`: 24,595 (3.51%); `02`: 12,788 (1.83%); `08`: 8,170 (1.17%); _(+3 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `11`: 60,086 (55.75%); `05`: 11,697 (10.85%); `04`: 10,272 (9.53%); `06`: 8,823 (8.19%); `03`: 7,664 (7.11%); `07`: 4,785 (4.44%); `02`: 2,021 (1.88%); `08`: 1,688 (1.57%); _(+3 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `11`: 297,782 (58.33%); `05`: 51,822 (10.15%); `04`: 47,748 (9.35%); `06`: 39,832 (7.80%); `03`: 32,189 (6.31%); `07`: 20,651 (4.05%); `02`: 8,485 (1.66%); `08`: 8,055 (1.58%); _(+3 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `11`: 118,450 (57.80%); `05`: 23,006 (11.23%); `04`: 19,269 (9.40%); `06`: 16,940 (8.27%); `03`: 11,369 (5.55%); `07`: 8,354 (4.08%); `08`: 3,303 (1.61%); `02`: 2,393 (1.17%); _(+3 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `11`: 163,376 (55.71%); `05`: 35,637 (12.15%); `06`: 27,711 (9.45%); `04`: 27,557 (9.40%); `03`: 14,860 (5.07%); `07`: 13,777 (4.70%); `08`: 4,823 (1.64%); `02`: 2,785 (0.95%); _(+3 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `live_birth_order` <a id="c820-fetal_death-live_birth_order"></a>

_Schema note:_ 0-9 — 0-8 or 9=Unknown. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `0`: 172,395 (40.94%); `1`: 109,881 (26.09%); `2`: 59,901 (14.22%); `9`: 34,859 (8.28%); `3`: 24,652 (5.85%); `4`: 9,988 (2.37%); `5`: 4,420 (1.05%); `6`: 2,240 (0.53%); _(+2 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `0`: 73,065 (38.68%); `1`: 49,149 (26.02%); `2`: 29,071 (15.39%); `9`: 14,855 (7.86%); `3`: 12,666 (6.70%); `4`: 5,206 (2.76%); `5`: 2,305 (1.22%); `6`: 1,169 (0.62%); _(+2 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `0`: 265,274 (37.86%); `1`: 176,732 (25.22%); `2`: 109,370 (15.61%); `9`: 55,905 (7.98%); `3`: 49,892 (7.12%); `4`: 21,727 (3.10%); `5`: 10,037 (1.43%); `6`: 5,044 (0.72%); _(+2 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `0`: 37,164 (34.48%); `1`: 24,987 (23.18%); `2`: 16,226 (15.05%); `9`: 14,066 (13.05%); `3`: 7,939 (7.37%); `4`: 3,659 (3.39%); `5`: 1,716 (1.59%); `6`: 920 (0.85%); _(+2 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `0`: 176,051 (34.48%); `1`: 103,139 (20.20%); `9`: 95,929 (18.79%); `2`: 68,538 (13.42%); `3`: 34,546 (6.77%); `4`: 16,116 (3.16%); `5`: 7,565 (1.48%); `6`: 3,788 (0.74%); _(+2 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `9`: 61,183 (29.86%); `0`: 58,360 (28.48%); `1`: 35,877 (17.51%); `2`: 24,390 (11.90%); `3`: 12,748 (6.22%); `4`: 6,306 (3.08%); `5`: 2,798 (1.37%); `6`: 1,497 (0.73%); _(+2 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `0`: 90,604 (30.90%); `9`: 80,629 (27.49%); `1`: 50,096 (17.08%); `2`: 33,777 (11.52%); `3`: 18,793 (6.41%); `4`: 9,400 (3.21%); `5`: 4,636 (1.58%); `6`: 2,391 (0.82%); _(+2 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `9` | 34,859 | 8.28% |
| `1989-1991` | `9` | 14,855 | 7.86% |
| `1992-2002` | `9` | 55,905 | 7.98% |
| `2003-2004` | `9` | 14,066 | 13.05% |
| `2005-2013` | `9` | 95,929 | 18.79% |
| `2014-2017` | `9` | 61,183 | 29.86% |
| `2018-2024` | `9` | 80,629 | 27.49% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `plurality` <a id="c820-fetal_death-plurality"></a>

_Schema note:_ 1-9 — 1=Single through 5=Quintuplet+. Same concept; 2022 max is 4=Quadruplet or higher vs 2006/2014 have 5=Quintuplet+. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 403,127 (95.73%); `2`: 17,272 (4.10%); `3`: 726 (0.17%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 178,979 (94.74%); `2`: 7,660 (4.05%); `9`: 1,851 (0.98%); `3`: 373 (0.20%); `4`: 37 (0.02%); `5`: 9 (0.00%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 667,430 (95.25%); `2`: 29,058 (4.15%); `3`: 2,141 (0.31%); `9`: 1,713 (0.24%); `4`: 264 (0.04%); `5`: 98 (0.01%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 102,123 (94.75%); `2`: 5,125 (4.75%); `3`: 463 (0.43%); `4`: 54 (0.05%); `5`: 17 (0.02%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 435,087 (85.22%); `9`: 40,089 (7.85%); `2`: 23,226 (4.55%); `5`: 10,207 (2.00%); `3`: 1,793 (0.35%); `4`: 126 (0.02%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 186,211 (90.87%); `2`: 9,394 (4.58%); `9`: 7,977 (3.89%); `5`: 666 (0.33%); `3`: 638 (0.31%); `4`: 37 (0.02%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 267,576 (91.24%); `2`: 13,247 (4.52%); `9`: 11,670 (3.98%); `3`: 696 (0.24%); `4`: 73 (0.02%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1989-1991` | `9` | 1,851 | 0.98% |
| `1992-2002` | `9` | 1,713 | 0.24% |
| `2005-2013` | `9` | 40,089 | 7.85% |
| `2014-2017` | `9` | 7,977 | 3.89% |
| `2018-2024` | `9` | 11,670 | 3.98% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`9`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`4`}; dropped {`9`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`5`, `9`}; dropped {`4`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`5`} _(codes ≥0.05% of an era)_

### `prenatal_care_month` <a id="c820-fetal_death-prenatal_care_month"></a>

_Schema note:_ 0-99 — 00=No care; 01-10=Month; 99=Unknown. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `02`: 722 (0.67%); `99`: 707 (0.66%); `03`: 690 (0.64%); `01`: 274 (0.25%); `04`: 242 (0.22%); `00`: 105 (0.10%); `05`: 95 (0.09%); `06`: 64 (0.06%); _(+4 more codes)_ | 97.26% |
| `2005-2013` | 510,528 | `99`: 5,198 (1.02%); `03`: 3,044 (0.60%); `02`: 2,880 (0.56%); `04`: 1,210 (0.24%); `00`: 1,156 (0.23%); `01`: 869 (0.17%); `05`: 659 (0.13%); `06`: 353 (0.07%); _(+4 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `99`: 76,432 (37.30%); `02`: 34,406 (16.79%); `03`: 22,331 (10.90%); `00`: 19,084 (9.31%); `01`: 10,840 (5.29%); `04`: 8,003 (3.91%); `05`: 4,118 (2.01%); `06`: 1,851 (0.90%); _(+4 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `99`: 123,219 (42.02%); `02`: 58,112 (19.82%); `03`: 40,247 (13.72%); `00`: 30,432 (10.38%); `01`: 16,597 (5.66%); `04`: 12,654 (4.31%); `05`: 6,661 (2.27%); `06`: 2,900 (0.99%); _(+4 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `99` | 707 | 0.66% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `99` | 5,198 | 1.02% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `99` | 76,432 | 37.30% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `99` | 123,219 | 42.02% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`00`, `01`, `02`, `03`, `04`, `05`, `06`, `99`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`07`, `08`, `09`} _(codes ≥0.05% of an era)_

### `prenatal_care_month_unrevised` <a id="c820-fetal_death-prenatal_care_month_unrevised"></a>

_Schema note:_ 0-99 — Unrevised prenatal care month. V2 1992-2002 sources from MONPRE (113-114); V1 2005-2006 sources from MPCB (S-version only). Blank for 2007-2013. Not in 2014/2022.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `99`: 131,680 (31.27%); `02`: 91,777 (21.79%); `00`: 66,104 (15.70%); `01`: 47,419 (11.26%); `03`: 42,860 (10.18%); `04`: 18,658 (4.43%); `05`: 10,569 (2.51%); `06`: 5,665 (1.35%); _(+3 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `99`: 57,825 (30.61%); `02`: 40,348 (21.36%); `00`: 29,327 (15.52%); `01`: 25,871 (13.69%); `03`: 17,928 (9.49%); `04`: 8,159 (4.32%); `05`: 4,560 (2.41%); `06`: 2,311 (1.22%); _(+3 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `99`: 326,919 (46.66%); `02`: 129,552 (18.49%); `01`: 84,601 (12.07%); `00`: 59,442 (8.48%); `03`: 55,110 (7.86%); `04`: 21,965 (3.13%); `05`: 11,520 (1.64%); `06`: 5,339 (0.76%); _(+3 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `99`: 54,306 (50.39%); `02`: 18,504 (17.17%); `01`: 12,969 (12.03%); `03`: 7,993 (7.42%); `00`: 4,728 (4.39%); `04`: 3,027 (2.81%); `05`: 1,646 (1.53%); `06`: 744 (0.69%); _(+3 more codes)_ | 2.74% |
| `2005-2013` | 510,528 | `99`: 50,771 (9.94%); `02`: 14,163 (2.77%); `01`: 10,220 (2.00%); `03`: 6,160 (1.21%); `00`: 3,957 (0.78%); `04`: 2,375 (0.47%); `05`: 1,362 (0.27%); `06`: 603 (0.12%); _(+3 more codes)_ | 82.29% |
| `2014-2017` | 204,923 | — | 100.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `99` | 131,680 | 31.27% |
| `1989-1991` | `99` | 57,825 | 30.61% |
| `1992-2002` | `99` | 326,919 | 46.66% |
| `2003-2004` | `99` | 54,306 | 50.39% |
| `2003-2004` | _null/blank_ | 2,958 | 2.74% |
| `2005-2013` | `99` | 50,771 | 9.94% |
| `2005-2013` | _null/blank_ | 420,131 | 82.29% |
| `2014-2017` | _null/blank_ | 204,923 | 100.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: dropped {`08`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: dropped {`00`, `01`, `02`, `03`, `04`, `05`, `06`, `07`, `09`, `99`} _(codes ≥0.05% of an era)_

### `prenatal_care_recode` <a id="c820-fetal_death-prenatal_care_recode"></a>

_Schema note:_ 1-5 — 5-category recode. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `1`: 1,686 (1.56%); `5`: 707 (0.66%); `2`: 401 (0.37%); `4`: 105 (0.10%); `3`: 59 (0.05%) | 97.26% |
| `2005-2013` | 510,528 | `1`: 6,793 (1.33%); `5`: 5,198 (1.02%); `2`: 2,222 (0.44%); `4`: 1,156 (0.23%); `3`: 281 (0.06%) | 96.93% |
| `2014-2017` | 204,923 | `5`: 76,432 (37.30%); `1`: 67,577 (32.98%); `4`: 19,084 (9.31%); `2`: 13,972 (6.82%); `3`: 1,635 (0.80%) | 12.80% |
| `2018-2024` | 293,262 | `5`: 123,219 (42.02%); `1`: 114,956 (39.20%); `4`: 30,432 (10.38%); `2`: 22,215 (7.58%); `3`: 2,440 (0.83%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`1`, `2`, `3`, `4`, `5`} _(codes ≥0.05% of an era)_

### `delivery_method_recode` <a id="c820-fetal_death-delivery_method_recode"></a>

_Schema note:_ 1-9 — 1=Vaginal; 2=C-section; 9=Not stated. Available A+S all years. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `1`: 99,070 (52.44%); `9`: 81,877 (43.34%); `2`: 7,962 (4.21%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 394,624 (56.32%); `9`: 276,559 (39.47%); `2`: 29,521 (4.21%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 57,598 (53.44%); `6`: 43,163 (40.05%); `3`: 3,904 (3.62%); `4`: 2,445 (2.27%); `5`: 555 (0.51%); `2`: 117 (0.11%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 265,105 (51.93%); `9`: 211,165 (41.36%); `2`: 31,705 (6.21%); `3`: 2,553 (0.50%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 121,373 (59.23%); `9`: 68,674 (33.51%); `2`: 14,876 (7.26%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 169,253 (57.71%); `9`: 100,422 (34.24%); `2`: 23,587 (8.04%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 81,877 | 43.34% |
| `1992-2002` | `9` | 276,559 | 39.47% |
| `2005-2013` | `9` | 211,165 | 41.36% |
| `2014-2017` | `9` | 68,674 | 33.51% |
| `2018-2024` | `9` | 100,422 | 34.24% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`3`, `4`, `5`, `6`}; dropped {`9`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`9`}; dropped {`4`, `5`, `6`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: dropped {`3`} _(codes ≥0.05% of an era)_

### `delivery_method_revised` <a id="c820-fetal_death-delivery_method_revised"></a>

_Schema note:_ 1-9 — 6-category revised recode (vaginal/VBAC/primary C-sec/repeat C-sec/etc). Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `1`: 90,226 (44.03%); `9`: 57,462 (28.04%); `2`: 8,737 (4.26%); `3`: 8,367 (4.08%); `5`: 8,293 (4.05%); `4`: 5,207 (2.54%); `6`: 408 (0.20%) | 12.80% |
| `2018-2024` | 293,262 | `1`: 137,980 (47.05%); `9`: 100,422 (34.24%); `5`: 16,739 (5.71%); `2`: 14,534 (4.96%); `3`: 13,881 (4.73%); `4`: 8,887 (3.03%); `6`: 819 (0.28%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `9` | 57,462 | 28.04% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 100,422 | 34.24% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`, `4`, `5`, `6`, `9`} _(codes ≥0.05% of an era)_

### `delivery_route` <a id="c820-fetal_death-delivery_route"></a>

_Schema note:_ 1-9 — 1=Spontaneous; 2=Forceps; 3=Vacuum; 4=Cesarean; 9=Unknown. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `1`: 12,492 (2.45%); `4`: 2,081 (0.41%); `9`: 760 (0.15%); `2`: 172 (0.03%); `3`: 145 (0.03%) | 96.93% |
| `2014-2017` | 204,923 | `1`: 96,615 (47.15%); `9`: 57,462 (28.04%); `4`: 13,982 (6.82%); `3`: 9,691 (4.73%); `2`: 950 (0.46%) | 12.80% |
| `2018-2024` | 293,262 | `1`: 155,260 (52.94%); `9`: 100,422 (34.24%); `4`: 23,587 (8.04%); `3`: 12,121 (4.13%); `2`: 1,872 (0.64%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `9` | 760 | 0.15% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `9` | 57,462 | 28.04% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 100,422 | 34.24% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`1`, `4`, `9`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`2`, `3`} _(codes ≥0.05% of an era)_

### `prior_cesarean` <a id="c820-fetal_death-prior_cesarean"></a>

_Schema note:_ N, U, Y — Y/N/U. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 13,184 (2.58%); `Y`: 1,573 (0.31%); `U`: 893 (0.17%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 109,714 (53.54%); `U`: 54,274 (26.49%); `Y`: 14,712 (7.18%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 200,811 (68.47%); `U`: 66,401 (22.64%); `Y`: 26,050 (8.88%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 893 | 0.17% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,274 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,401 | 22.64% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `prior_cesarean_number` <a id="c820-fetal_death-prior_cesarean_number"></a>

_Schema note:_ 0-99 — 00-30; 99=Unknown. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `00`: 13,245 (2.59%); `01`: 1,011 (0.20%); `99`: 909 (0.18%); `02`: 340 (0.07%); `03`: 117 (0.02%); `04`: 19 (0.00%); `05`: 4 (0.00%); `06`: 4 (0.00%); _(+1 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `00`: 109,714 (53.54%); `99`: 54,571 (26.63%); `01`: 9,132 (4.46%); `02`: 3,664 (1.79%); `03`: 1,222 (0.60%); `04`: 300 (0.15%); `05`: 72 (0.04%); `06`: 9 (0.00%); _(+5 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `00`: 200,811 (68.47%); `99`: 67,078 (22.87%); `01`: 15,711 (5.36%); `02`: 6,519 (2.22%); `03`: 2,256 (0.77%); `04`: 651 (0.22%); `05`: 149 (0.05%); `06`: 45 (0.02%); _(+5 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `99` | 909 | 0.18% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `99` | 54,571 | 26.63% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `99` | 67,078 | 22.87% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`00`, `01`, `02`, `99`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`03`, `04`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`05`} _(codes ≥0.05% of an era)_

### `fetal_sex` <a id="c820-fetal_death-fetal_sex"></a>

_Schema note:_ F, M, U — M=Male; F=Female. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `U`: 204,751 (48.62%); `M`: 116,048 (27.56%); `F`: 100,326 (23.82%) | 0.00% |
| `1989-1991` | 188,909 | `U`: 89,362 (47.30%); `M`: 54,044 (28.61%); `F`: 45,503 (24.09%) | 0.00% |
| `1992-2002` | 700,704 | `U`: 370,073 (52.81%); `M`: 180,117 (25.71%); `F`: 150,514 (21.48%) | 0.00% |
| `2003-2004` | 107,782 | `M`: 60,170 (55.83%); `F`: 47,612 (44.17%) | 0.00% |
| `2005-2013` | 510,528 | `U`: 256,507 (50.24%); `M`: 137,320 (26.90%); `F`: 116,701 (22.86%) | 0.00% |
| `2014-2017` | 204,923 | `U`: 98,104 (47.87%); `M`: 56,108 (27.38%); `F`: 50,711 (24.75%) | 0.00% |
| `2018-2024` | 293,262 | `U`: 129,726 (44.24%); `M`: 86,711 (29.57%); `F`: 76,825 (26.20%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `U` | 204,751 | 48.62% |
| `1989-1991` | `U` | 89,362 | 47.30% |
| `1992-2002` | `U` | 370,073 | 52.81% |
| `2005-2013` | `U` | 256,507 | 50.24% |
| `2014-2017` | `U` | 98,104 | 47.87% |
| `2018-2024` | `U` | 129,726 | 44.24% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: dropped {`U`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`U`} _(codes ≥0.05% of an era)_

### `gestational_age_clinical` <a id="c820-fetal_death-gestational_age_clinical"></a>

_Schema note:_ 0-99 — Unedited OE gestation in weeks. In 2006 field is ESTGEST (pos 446-447); in 2014/2022 it is OEGest_Unedt (pos 336-337). For version A = obstetric estimate (0-98); for S = clinical estimate (02-47). Field name and position changed.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `99`: 138,445 (32.88%); `08`: 33,987 (8.07%); `06`: 24,291 (5.77%); `10`: 22,252 (5.28%); `12`: 17,140 (4.07%); `40`: 11,409 (2.71%); `20`: 9,641 (2.29%); `07`: 9,283 (2.20%); _(+42 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `99`: 34,088 (18.04%); `08`: 16,811 (8.90%); `06`: 11,536 (6.11%); `10`: 10,461 (5.54%); `12`: 7,652 (4.05%); `20`: 6,313 (3.34%); `22`: 6,056 (3.21%); `07`: 5,935 (3.14%); _(+39 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `99`: 88,381 (12.61%); `08`: 74,168 (10.58%); `10`: 44,298 (6.32%); `06`: 43,465 (6.20%); `07`: 32,657 (4.66%); `09`: 32,022 (4.57%); `12`: 29,152 (4.16%); `20`: 26,527 (3.79%); _(+42 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `99`: 12,891 (11.96%); `08`: 10,625 (9.86%); `06`: 5,861 (5.44%); `07`: 5,417 (5.03%); `10`: 5,249 (4.87%); `09`: 5,213 (4.84%); `20`: 5,155 (4.78%); `21`: 5,073 (4.71%); _(+38 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `08`: 49,098 (9.62%); `99`: 40,696 (7.97%); `06`: 32,621 (6.39%); `07`: 28,898 (5.66%); `09`: 26,422 (5.18%); `20`: 25,038 (4.90%); `10`: 24,556 (4.81%); `21`: 23,899 (4.68%); _(+53 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `08`: 18,594 (9.07%); `06`: 13,897 (6.78%); `07`: 11,284 (5.51%); `99`: 11,084 (5.41%); `20`: 11,055 (5.39%); `09`: 10,483 (5.12%); `21`: 9,690 (4.73%); `22`: 8,774 (4.28%); _(+41 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `08`: 22,324 (7.61%); `06`: 19,253 (6.57%); `20`: 17,696 (6.03%); `99`: 15,327 (5.23%); `21`: 14,958 (5.10%); `07`: 14,759 (5.03%); `09`: 12,909 (4.40%); `22`: 11,962 (4.08%); _(+46 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `99` | 138,445 | 32.88% |
| `1989-1991` | `99` | 34,088 | 18.04% |
| `1992-2002` | `99` | 88,381 | 12.61% |
| `2003-2004` | `99` | 12,891 | 11.96% |
| `2005-2013` | `99` | 40,696 | 7.97% |
| `2005-2013` | _null/blank_ | 2 | 0.00% |
| `2014-2017` | `99` | 11,084 | 5.41% |
| `2018-2024` | `99` | 15,327 | 5.23% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1989-1991`→`1992-2002`: dropped {`43`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`01`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`01`} _(codes ≥0.05% of an era)_

### `gestational_age_oe_edited` <a id="c820-fetal_death-gestational_age_oe_edited"></a>

_Schema note:_ 2-99 — Edited OE in weeks (02-47; 99). Not in 2006 layout. Available 2014+. This is the NCHS standard tabulation item.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `08`: 18,973 (9.26%); `06`: 14,117 (6.89%); `07`: 11,552 (5.64%); `20`: 11,095 (5.41%); `09`: 10,946 (5.34%); `21`: 9,728 (4.75%); `10`: 9,199 (4.49%); `22`: 8,813 (4.30%); _(+38 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `08`: 22,819 (7.78%); `06`: 19,568 (6.67%); `20`: 17,762 (6.06%); `07`: 15,114 (5.15%); `21`: 15,029 (5.12%); `09`: 13,547 (4.62%); `22`: 12,016 (4.10%); `10`: 11,465 (3.91%); _(+39 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `99` | 7,314 | 3.57% |
| `2018-2024` | `99` | 10,001 | 3.41% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `42`, `99`} _(codes ≥0.05% of an era)_

### `gestational_age_combined` <a id="c820-fetal_death-gestational_age_combined"></a>

_Schema note:_ 2-99 — 02-47 weeks; 99=Unknown. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `99`: 41,040 (9.75%); `10`: 22,684 (5.39%); `11`: 21,163 (5.03%); `08`: 20,674 (4.91%); `12`: 20,543 (4.88%); `09`: 16,853 (4.00%); `06`: 14,896 (3.54%); `07`: 14,099 (3.35%); _(+45 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `99`: 12,125 (6.42%); `10`: 10,797 (5.72%); `08`: 10,242 (5.42%); `11`: 9,399 (4.98%); `12`: 8,691 (4.60%); `09`: 8,269 (4.38%); `06`: 7,415 (3.93%); `07`: 6,866 (3.63%); _(+39 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `10`: 46,221 (6.60%); `08`: 45,230 (6.45%); `09`: 42,011 (6.00%); `11`: 39,504 (5.64%); `99`: 34,430 (4.91%); `12`: 32,711 (4.67%); `07`: 30,091 (4.29%); `06`: 26,600 (3.80%); _(+42 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `08`: 6,566 (6.09%); `09`: 6,558 (6.08%); `10`: 6,184 (5.74%); `99`: 5,951 (5.52%); `21`: 5,126 (4.76%); `11`: 5,049 (4.68%); `22`: 4,576 (4.25%); `20`: 4,418 (4.10%); _(+39 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `08`: 33,478 (6.56%); `09`: 33,134 (6.49%); `10`: 31,568 (6.18%); `99`: 25,315 (4.96%); `11`: 24,140 (4.73%); `21`: 21,956 (4.30%); `07`: 21,820 (4.27%); `20`: 20,599 (4.03%); _(+40 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `08`: 13,163 (6.42%); `09`: 12,365 (6.03%); `10`: 11,868 (5.79%); `11`: 8,980 (4.38%); `20`: 8,924 (4.35%); `21`: 8,833 (4.31%); `06`: 8,487 (4.14%); `07`: 8,471 (4.13%); _(+39 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `08`: 16,244 (5.54%); `09`: 15,480 (5.28%); `10`: 14,645 (4.99%); `20`: 14,135 (4.82%); `21`: 13,341 (4.55%); `06`: 12,192 (4.16%); `11`: 11,179 (3.81%); `07`: 11,127 (3.79%); _(+39 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `99` | 41,040 | 9.75% |
| `1989-1991` | `99` | 12,125 | 6.42% |
| `1992-2002` | `99` | 34,430 | 4.91% |
| `2003-2004` | `99` | 5,951 | 5.52% |
| `2005-2013` | `99` | 25,315 | 4.96% |
| `2014-2017` | `99` | 7,323 | 3.57% |
| `2018-2024` | `99` | 10,007 | 3.41% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: dropped {`01`, `47`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: dropped {`46`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`46`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: dropped {`46`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`46`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`46`} _(codes ≥0.05% of an era)_

### `gestational_age_recode12` <a id="c820-fetal_death-gestational_age_recode12"></a>

_Schema note:_ 1-12 — 12-category recode. 2006 bins differ slightly (06=32-35; 07=36; 08=37-39; 09=40) vs 2014/2022 (06=32-33; 07=34-36; 08=37-38; 09=39-40). All years A+S.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `01`: 173,161 (41.12%); `12`: 41,040 (9.75%); `03`: 39,699 (9.43%); `08`: 28,368 (6.74%); `04`: 28,204 (6.70%); `06`: 27,533 (6.54%); `02`: 24,373 (5.79%); `05`: 23,487 (5.58%); _(+4 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `01`: 79,632 (42.15%); `03`: 22,466 (11.89%); `04`: 13,890 (7.35%); `06`: 12,836 (6.79%); `08`: 12,405 (6.57%); `12`: 12,125 (6.42%); `02`: 11,316 (5.99%); `05`: 11,164 (5.91%); _(+4 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `01`: 331,917 (47.37%); `03`: 93,133 (13.29%); `02`: 46,179 (6.59%); `04`: 46,164 (6.59%); `06`: 40,546 (5.79%); `08`: 38,307 (5.47%); `05`: 35,271 (5.03%); `12`: 34,432 (4.91%); _(+4 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `01`: 44,568 (41.35%); `03`: 17,570 (16.30%); `04`: 8,133 (7.55%); `06`: 7,018 (6.51%); `02`: 6,664 (6.18%); `08`: 6,528 (6.06%); `05`: 6,207 (5.76%); `12`: 5,951 (5.52%); _(+4 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `01`: 227,625 (44.59%); `03`: 77,470 (15.17%); `04`: 36,910 (7.23%); `02`: 34,084 (6.68%); `06`: 30,242 (5.92%); `08`: 28,906 (5.66%); `05`: 28,150 (5.51%); `12`: 25,315 (4.96%); _(+4 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `01`: 89,160 (43.51%); `03`: 31,318 (15.28%); `04`: 15,350 (7.49%); `02`: 14,032 (6.85%); `05`: 11,884 (5.80%); `07`: 11,387 (5.56%); `08`: 8,792 (4.29%); `12`: 7,323 (3.57%); _(+4 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `01`: 115,969 (39.54%); `03`: 46,975 (16.02%); `04`: 24,417 (8.33%); `02`: 21,059 (7.18%); `05`: 19,402 (6.62%); `07`: 17,934 (6.12%); `08`: 13,345 (4.55%); `06`: 10,433 (3.56%); _(+4 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `gestational_age_recode5` <a id="c820-fetal_death-gestational_age_recode5"></a>

_Schema note:_ 1-5 — 5-category recode. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 197,534 (46.91%); `4`: 114,648 (27.22%); `5`: 41,040 (9.75%); `2`: 39,699 (9.43%); `3`: 28,204 (6.70%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 90,948 (48.14%); `4`: 49,480 (26.19%); `2`: 22,466 (11.89%); `3`: 13,890 (7.35%); `5`: 12,125 (6.42%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 378,097 (53.96%); `4`: 148,880 (21.25%); `2`: 93,133 (13.29%); `3`: 46,164 (6.59%); `5`: 34,430 (4.91%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 51,232 (47.53%); `4`: 24,896 (23.10%); `2`: 17,570 (16.30%); `3`: 8,133 (7.55%); `5`: 5,951 (5.52%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 261,709 (51.26%); `4`: 109,124 (21.37%); `2`: 77,470 (15.17%); `3`: 36,910 (7.23%); `5`: 25,315 (4.96%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 103,192 (50.36%); `4`: 47,740 (23.30%); `2`: 31,318 (15.28%); `3`: 15,350 (7.49%); `5`: 7,323 (3.57%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 137,028 (46.73%); `4`: 74,835 (25.52%); `2`: 46,975 (16.02%); `3`: 24,417 (8.33%); `5`: 10,007 (3.41%) | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `oe_gest_recode12` <a id="c820-fetal_death-oe_gest_recode12"></a>

_Schema note:_ 1-12 — 12-category OE recode. Not in 2006. Available 2014+ (A+S). NCHS standard tabulation item.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `01`: 91,079 (44.45%); `03`: 35,248 (17.20%); `04`: 13,967 (6.82%); `02`: 12,407 (6.05%); `07`: 11,449 (5.59%); `05`: 11,208 (5.47%); `08`: 9,015 (4.40%); `12`: 7,314 (3.57%); _(+4 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `01`: 118,542 (40.42%); `03`: 52,955 (18.06%); `04`: 22,723 (7.75%); `02`: 19,024 (6.49%); `05`: 18,289 (6.24%); `07`: 18,100 (6.17%); `08`: 13,443 (4.58%); `06`: 10,235 (3.49%); _(+4 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, `12`} _(codes ≥0.05% of an era)_

### `oe_gest_recode5` <a id="c820-fetal_death-oe_gest_recode5"></a>

_Schema note:_ 1-5 — 5-category OE recode. Not in 2006. Available 2014+ (A+S). NCHS standard tabulation item.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `1`: 103,486 (50.50%); `4`: 44,908 (21.91%); `2`: 35,248 (17.20%); `3`: 13,967 (6.82%); `5`: 7,314 (3.57%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 137,566 (46.91%); `4`: 70,017 (23.88%); `2`: 52,955 (18.06%); `3`: 22,723 (7.75%); `5`: 10,001 (3.41%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`, `4`, `5`} _(codes ≥0.05% of an era)_

### `birthweight` <a id="c820-fetal_death-birthweight"></a>

_Schema note:_ 1-9999 — 0001-8165 grams; 9999=Not stated. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `9999`: 220,861 (52.45%); `0510`: 2,877 (0.68%); `0453`: 2,560 (0.61%); `0567`: 2,472 (0.59%); `0680`: 2,457 (0.58%); `0340`: 2,293 (0.54%); `0425`: 2,093 (0.50%); `0595`: 2,000 (0.47%); _(+3306 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `9999`: 96,799 (51.24%); `0500`: 1,640 (0.87%); `0454`: 1,335 (0.71%); `0510`: 1,211 (0.64%); `0340`: 1,184 (0.63%); `0482`: 1,037 (0.55%); `0567`: 982 (0.52%); `0425`: 973 (0.52%); _(+3264 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `9999`: 397,397 (56.71%); `0500`: 4,234 (0.60%); `0340`: 4,122 (0.59%); `0454`: 4,031 (0.58%); `0510`: 3,888 (0.55%); `0425`: 3,489 (0.50%); `0482`: 3,227 (0.46%); `0397`: 3,215 (0.46%); _(+4750 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `9999`: 56,359 (52.29%); `0454`: 746 (0.69%); `0340`: 744 (0.69%); `0510`: 647 (0.60%); `0369`: 640 (0.59%); `0425`: 615 (0.57%); `0397`: 597 (0.55%); `0312`: 565 (0.52%); _(+3475 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `9999`: 283,637 (55.56%); `0340`: 2,855 (0.56%); `0500`: 2,401 (0.47%); `0454`: 2,278 (0.45%); `0425`: 2,258 (0.44%); `0510`: 2,186 (0.43%); `0397`: 2,081 (0.41%); `0312`: 1,985 (0.39%); _(+4787 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `9999`: 101,595 (49.58%); `0001`: 3,140 (1.53%); `0340`: 854 (0.42%); `0454`: 777 (0.38%); `0425`: 692 (0.34%); `0028`: 670 (0.33%); `0510`: 613 (0.30%); `0300`: 523 (0.26%); _(+4316 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `9999`: 130,632 (44.54%); `0001`: 4,497 (1.53%); `0028`: 2,164 (0.74%); `0340`: 1,122 (0.38%); `0300`: 1,011 (0.34%); `0454`: 887 (0.30%); `0510`: 840 (0.29%); `0400`: 813 (0.28%); _(+4462 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `9999` | 220,861 | 52.45% |
| `1989-1991` | `9999` | 96,799 | 51.24% |
| `1992-2002` | `9999` | 397,397 | 56.71% |
| `2003-2004` | `9999` | 56,359 | 52.29% |
| `2005-2013` | `9999` | 283,637 | 55.56% |
| `2014-2017` | `9999` | 101,595 | 49.58% |
| `2018-2024` | `9999` | 130,632 | 44.54% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`0001`, `0002`, `0003`, `0004`, `0005`, `0006`, `0010`, `0012`, `0015`, `0020`, `0025`, `0057`, `0110`, `0120`, `0142`, `0190`, `0227`, `0230`, `0284`, `0290`, `0325`, `0851`, `0879`, `0936`, `0964`, `1021`, `1049`, `1106`, `1191`, `1276`, `1400`, `1418`, `1446`, `1503`, `1531`, `1588`, `1616`, `1673`, `1758`, `1843`, `1928`, `1985`, `2013`, `2070`, `2098`, `2155`, `2183`, `2240`, `2325`, `2410`, `2495`, `2552`, `2580`, `2637`, `2665`, `2750`, `2807`, `2892`, `2977`, `3062`, `3119`, `3147`, `3204`, `3232`, `3289`, `3317`, `3374`, `3459`, `3544`, `3629`, `3686`, `3714`, `3771`, `3799`, `3856`, `3884`}; dropped {`0040`, `0056`, `0141`, `0226`, `0283`, `0311`, `0368`, `0396`, `0453`, `0481`, `0538`, `0623`, `0708`, `0793`, `0878`, `0935`, `0963`, `1020`, `1048`, `1105`, `1190`, `1275`, `1300`, `1360`, `1417`, `1445`, `1502`, `1530`, `1587`, `1615`, `1672`, `1757`, `1842`, `1927`, `1984`, `2012`, `2069`, `2097`, `2154`, `2182`, `2239`, `2324`, `2409`, `2494`, `2551`, `2579`, `2636`, `2664`, `2721`, `2749`, `2806`, `2891`, `2976`, `3061`, `3118`, `3146`, `3203`, `3231`, `3288`, `3316`, `3373`, `3458`, `3543`, `3628`, `3685`, `3713`, `3770`, `3798`, `3855`, `3883`, `3912`, `3940`, `3997`, `4139`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: added {`0013`, `0014`, `0283`, `0355`, `0365`, `0375`, `0385`, `0395`, `0405`, `0475`}; dropped {`0001`, `0003`, `0004`, `0006`, `0025`, `0590`, `0610`, `0630`, `0660`, `0720`, `0750`, `0900`, `1000`, `1100`, `1200`, `1400`, `1500`, `3771`, `3799`, `3827`, `3856`, `3884`, `3969`, `4082`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: added {`0285`, `0295`, `0305`, `0315`, `0335`, `0345`, `0368`, `0396`, `0415`, `0435`, `0445`, `0453`, `0465`, `0495`, `0535`, `0610`, `0750`, `3799`}; dropped {`0002`, `0005`, `0010`, `0012`, `0013`, `0014`, `0015`, `0020`, `0050`, `0110`, `0160`, `0190`, `0620`, `0640`, `0800`, `3657`, `3686`, `3742`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`0110`, `0130`, `0160`, `0190`, `0265`, `0275`, `0311`, `0455`, `0485`, `0525`}; dropped {`0030`, `0120`, `0140`, `0535`, `0610`, `0650`, `0700`, `0750`, `3374`, `3459`, `3487`, `3515`, `3544`, `3572`, `3600`, `3714`, `3799`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`0001`, `0002`, `0003`, `0004`, `0005`, `0006`, `0007`, `0010`, `0012`, `0014`, `0015`, `0020`, `0023`, `0025`, `0030`, `0035`, `0040`, `0043`, `0045`, `0050`, `0060`, `0070`, `0080`, `0090`, `0099`, `0120`, `0125`, `0140`, `0145`, `0175`, `0185`, `0195`, `0215`, `0225`, `0226`, `0235`, `0245`, `0481`, `0505`, `0590`, `0610`, `0620`, `0630`, `0650`, `0660`, `0700`, `0800`, `0999`, `1360`, `1984`, `3118`}; dropped {`0851`, `1418`, `1673`, `1758`, `1985`, `2183`, `2552`, `2637`, `3062`, `3119`, `3147`, `3204`, `3232`, `3317`, `3402`, `3430`, `3629`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`0055`, `0065`, `0075`, `0095`, `0105`, `0115`, `0135`, `0155`, `0165`, `0205`, `0640`, `0670`, `0690`, `0710`, `0720`, `0730`, `0740`, `0750`, `0760`, `0780`, `1000`, `1020`, `1673`, `2183`}; dropped {`0012`, `0195`, `0481`, `0495`, `0505`, `0525`, `1191`, `1701`, `2013`, `2098`, `3118`, `3289`, `3345`} _(codes ≥0.05% of an era)_

### `birthweight_recode14` <a id="c820-fetal_death-birthweight_recode14"></a>

_Schema note:_ 1-14 — 14-category gram-range recode. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `14`: 220,861 (52.45%); `04`: 45,534 (10.81%); `03`: 21,705 (5.15%); `05`: 20,837 (4.95%); `06`: 18,661 (4.43%); `07`: 18,420 (4.37%); `08`: 17,848 (4.24%); `09`: 16,359 (3.88%); _(+6 more codes)_ | 0.00% |
| `1989-1991` | 188,909 | `14`: 96,799 (51.24%); `04`: 20,632 (10.92%); `03`: 11,639 (6.16%); `01`: 10,655 (5.64%); `05`: 8,755 (4.63%); `06`: 7,680 (4.07%); `07`: 7,335 (3.88%); `08`: 7,271 (3.85%); _(+6 more codes)_ | 0.00% |
| `1992-2002` | 700,704 | `14`: 397,397 (56.71%); `04`: 64,225 (9.17%); `03`: 45,930 (6.55%); `01`: 40,376 (5.76%); `02`: 26,927 (3.84%); `05`: 25,453 (3.63%); `06`: 23,071 (3.29%); `07`: 22,256 (3.18%); _(+6 more codes)_ | 0.00% |
| `2003-2004` | 107,782 | `14`: 56,359 (52.29%); `04`: 10,449 (9.69%); `03`: 8,701 (8.07%); `01`: 6,288 (5.83%); `02`: 5,428 (5.04%); `05`: 4,206 (3.90%); `06`: 3,861 (3.58%); `07`: 3,838 (3.56%); _(+6 more codes)_ | 0.00% |
| `2005-2013` | 510,528 | `14`: 279,434 (54.73%); `04`: 44,992 (8.81%); `03`: 37,689 (7.38%); `01`: 34,709 (6.80%); `02`: 24,588 (4.82%); `05`: 18,790 (3.68%); `06`: 16,881 (3.31%); `07`: 16,231 (3.18%); _(+6 more codes)_ | 0.00% |
| `2014-2017` | 204,923 | `14`: 101,595 (49.58%); `01`: 21,669 (10.57%); `04`: 17,128 (8.36%); `03`: 15,152 (7.39%); `02`: 10,324 (5.04%); `05`: 8,260 (4.03%); `06`: 7,373 (3.60%); `07`: 7,033 (3.43%); _(+6 more codes)_ | 0.00% |
| `2018-2024` | 293,262 | `14`: 130,632 (44.54%); `01`: 37,564 (12.81%); `04`: 25,707 (8.77%); `03`: 21,696 (7.40%); `02`: 15,700 (5.35%); `05`: 13,421 (4.58%); `06`: 12,004 (4.09%); `07`: 11,362 (3.87%); _(+6 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

_No documented sentinel candidate or null/blank observed in any era._

**(iii) Era-by-era coding-scheme diff**

- Stable code frame across all populated eras (no add/drop ≥0.05% of an era).

### `birthweight_recode4` <a id="c820-fetal_death-birthweight_recode4"></a>

_Schema note:_ 1-4 — 4-category recode. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `4`: 96,799 (51.24%); `1`: 58,127 (30.77%); `3`: 18,968 (10.04%); `2`: 15,015 (7.95%) | 0.00% |
| `1992-2002` | 700,704 | `4`: 397,397 (56.71%); `1`: 202,911 (28.96%); `3`: 55,069 (7.86%); `2`: 45,327 (6.47%) | 0.00% |
| `2003-2004` | 107,782 | `4`: 56,359 (52.29%); `1`: 35,072 (32.54%); `3`: 8,652 (8.03%); `2`: 7,699 (7.14%) | 0.00% |
| `2005-2013` | 510,528 | `4`: 279,434 (54.73%); `1`: 160,768 (31.49%); `3`: 37,214 (7.29%); `2`: 33,112 (6.49%) | 0.00% |
| `2014-2017` | 204,923 | `4`: 101,595 (49.58%); `1`: 72,533 (35.40%); `3`: 16,389 (8.00%); `2`: 14,406 (7.03%) | 0.00% |
| `2018-2024` | 293,262 | `4`: 130,632 (44.54%); `1`: 114,088 (38.90%); `3`: 25,176 (8.58%); `2`: 23,366 (7.97%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `3`, `4`} _(codes ≥0.05% of an era)_

### `fetal_presentation` <a id="c820-fetal_death-fetal_presentation"></a>

_Schema note:_ 1-9 — 1=Cephalic; 2=Breech; 3=Other; 9=Unknown. Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `1`: 7,904 (1.55%); `2`: 3,374 (0.66%); `9`: 3,301 (0.65%); `3`: 1,071 (0.21%) | 96.93% |
| `2014-2017` | 204,923 | `9`: 86,508 (42.21%); `1`: 61,022 (29.78%); `2`: 21,648 (10.56%); `3`: 9,522 (4.65%) | 12.80% |
| `2018-2024` | 293,262 | `9`: 140,061 (47.76%); `1`: 102,696 (35.02%); `2`: 36,489 (12.44%); `3`: 14,016 (4.78%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `9` | 3,301 | 0.65% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `9` | 86,508 | 42.21% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 140,061 | 47.76% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`1`, `2`, `3`, `9`} _(codes ≥0.05% of an era)_

### `prepregnancy_diabetes` <a id="c820-fetal_death-prepregnancy_diabetes"></a>

_Schema note:_ N, U, Y — Y/N/U (2006 also has X=Not on certificate). Version A only. Same concept; 2006 includes X code. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 14,148 (2.77%); `U`: 1,085 (0.21%); `Y`: 417 (0.08%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 120,763 (58.93%); `U`: 54,279 (26.49%); `Y`: 3,658 (1.79%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 220,135 (75.06%); `U`: 66,413 (22.65%); `Y`: 6,714 (2.29%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 1,085 | 0.21% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,279 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,413 | 22.65% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `gestational_diabetes` <a id="c820-fetal_death-gestational_diabetes"></a>

_Schema note:_ N, U, Y — Y/N/U (2006 also has X). Version A only. Same concept; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 14,107 (2.76%); `U`: 1,085 (0.21%); `Y`: 458 (0.09%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 120,350 (58.73%); `U`: 54,279 (26.49%); `Y`: 4,071 (1.99%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 219,834 (74.96%); `U`: 66,413 (22.65%); `Y`: 7,015 (2.39%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 1,085 | 0.21% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,279 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,413 | 22.65% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `diabetes_unrevised` <a id="c820-fetal_death-diabetes_unrevised"></a>

_Schema note:_ 1-9 — Unrevised combined diabetes flag (1=Yes; 2=No; 9=Unknown). Available in 2006 (A+S) and 2014 (A+S). Not in 2022 layout. 2006 also has 8=Not on certificate.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `2`: 127,678 (67.59%); `9`: 58,623 (31.03%); `1`: 2,608 (1.38%) | 0.00% |
| `1992-2002` | 700,704 | `2`: 424,643 (60.60%); `9`: 264,794 (37.79%); `1`: 11,267 (1.61%) | 0.00% |
| `2003-2004` | 107,782 | `2`: 56,171 (52.12%); `9`: 49,177 (45.63%); `1`: 2,434 (2.26%) | 0.00% |
| `2005-2013` | 510,528 | `2`: 274,301 (53.73%); `9`: 220,883 (43.27%); `1`: 15,344 (3.01%) | 0.00% |
| `2014-2017` | 204,923 | `2`: 128,183 (62.55%); `9`: 68,477 (33.42%); `1`: 8,263 (4.03%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 58,623 | 31.03% |
| `1992-2002` | `9` | 264,794 | 37.79% |
| `2003-2004` | `9` | 49,177 | 45.63% |
| `2005-2013` | `9` | 220,883 | 43.27% |
| `2014-2017` | `9` | 68,477 | 33.42% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `prepregnancy_hypertension` <a id="c820-fetal_death-prepregnancy_hypertension"></a>

_Schema note:_ N, U, Y — Y/N/U (2006 also has X). Version A only. Same concept; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 14,008 (2.74%); `U`: 1,085 (0.21%); `Y`: 557 (0.11%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 119,164 (58.15%); `U`: 54,279 (26.49%); `Y`: 5,257 (2.57%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 216,039 (73.67%); `U`: 66,413 (22.65%); `Y`: 10,810 (3.69%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 1,085 | 0.21% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,279 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,413 | 22.65% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `gestational_hypertension` <a id="c820-fetal_death-gestational_hypertension"></a>

_Schema note:_ N, U, Y — Y/N/U (2006 also has X). Version A only. Same concept; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 13,901 (2.72%); `U`: 1,085 (0.21%); `Y`: 664 (0.13%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 119,274 (58.20%); `U`: 54,279 (26.49%); `Y`: 5,147 (2.51%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 216,022 (73.66%); `U`: 66,413 (22.65%); `Y`: 10,827 (3.69%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 1,085 | 0.21% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,279 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,413 | 22.65% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `chronic_hypertension_unrevised` <a id="c820-fetal_death-chronic_hypertension_unrevised"></a>

_Schema note:_ 1-9 — Unrevised chronic hypertension (1=Yes; 2=No; 9=Unknown). 2006 (A+S) and 2014 (A+S). Not in 2022. 2006 also has 8=Not on certificate.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `2`: 128,228 (67.88%); `9`: 58,623 (31.03%); `1`: 2,058 (1.09%) | 0.00% |
| `1992-2002` | 700,704 | `2`: 427,476 (61.01%); `9`: 264,794 (37.79%); `1`: 8,434 (1.20%) | 0.00% |
| `2003-2004` | 107,782 | `2`: 56,870 (52.76%); `9`: 49,177 (45.63%); `1`: 1,735 (1.61%) | 0.00% |
| `2005-2013` | 510,528 | `2`: 278,607 (54.57%); `9`: 220,883 (43.27%); `1`: 11,038 (2.16%) | 0.00% |
| `2014-2017` | 204,923 | `2`: 130,745 (63.80%); `9`: 68,477 (33.42%); `1`: 5,701 (2.78%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 58,623 | 31.03% |
| `1992-2002` | `9` | 264,794 | 37.79% |
| `2003-2004` | `9` | 49,177 | 45.63% |
| `2005-2013` | `9` | 220,883 | 43.27% |
| `2014-2017` | `9` | 68,477 | 33.42% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `pregnancy_hypertension_unrevised` <a id="c820-fetal_death-pregnancy_hypertension_unrevised"></a>

_Schema note:_ 1-9 — Unrevised pregnancy hypertension (1=Yes; 2=No; 9=Unknown). 2006 (A+S) and 2014 (A+S). Not in 2022. 2006 also has 8.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `2`: 127,133 (67.30%); `9`: 58,623 (31.03%); `1`: 3,153 (1.67%) | 0.00% |
| `1992-2002` | 700,704 | `2`: 423,123 (60.39%); `9`: 264,794 (37.79%); `1`: 12,787 (1.82%) | 0.00% |
| `2003-2004` | 107,782 | `2`: 56,160 (52.11%); `9`: 49,177 (45.63%); `1`: 2,445 (2.27%) | 0.00% |
| `2005-2013` | 510,528 | `2`: 279,205 (54.69%); `9`: 220,883 (43.27%); `1`: 10,440 (2.04%) | 0.00% |
| `2014-2017` | 204,923 | `2`: 131,057 (63.95%); `9`: 68,477 (33.42%); `1`: 5,389 (2.63%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 58,623 | 31.03% |
| `1992-2002` | `9` | 264,794 | 37.79% |
| `2003-2004` | `9` | 49,177 | 45.63% |
| `2005-2013` | `9` | 220,883 | 43.27% |
| `2014-2017` | `9` | 68,477 | 33.42% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `eclampsia` <a id="c820-fetal_death-eclampsia"></a>

_Schema note:_ N, U, Y — Y/N/U (2006 also has X). Version A only. Same concept; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `N`: 14,510 (2.84%); `U`: 1,085 (0.21%); `Y`: 55 (0.01%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 123,850 (60.44%); `U`: 54,279 (26.49%); `Y`: 571 (0.28%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 225,820 (77.00%); `U`: 66,413 (22.65%); `Y`: 1,029 (0.35%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `U` | 1,085 | 0.21% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 54,279 | 26.49% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 66,413 | 22.65% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`N`, `U`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`Y`} _(codes ≥0.05% of an era)_

### `eclampsia_unrevised` <a id="c820-fetal_death-eclampsia_unrevised"></a>

_Schema note:_ 1-9 — Unrevised eclampsia (1=Yes; 2=No; 9=Unknown). 2006 (A+S) and 2014 (A+S). Not in 2022. 2006 also has 8.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `2`: 129,741 (68.68%); `9`: 58,623 (31.03%); `1`: 545 (0.29%) | 0.00% |
| `1992-2002` | 700,704 | `2`: 434,074 (61.95%); `9`: 264,794 (37.79%); `1`: 1,836 (0.26%) | 0.00% |
| `2003-2004` | 107,782 | `2`: 58,291 (54.08%); `9`: 49,177 (45.63%); `1`: 314 (0.29%) | 0.00% |
| `2005-2013` | 510,528 | `2`: 288,243 (56.46%); `9`: 220,883 (43.27%); `1`: 1,402 (0.27%) | 0.00% |
| `2014-2017` | 204,923 | `2`: 135,834 (66.29%); `9`: 68,477 (33.42%); `1`: 612 (0.30%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 58,623 | 31.03% |
| `1992-2002` | `9` | 264,794 | 37.79% |
| `2003-2004` | `9` | 49,177 | 45.63% |
| `2005-2013` | `9` | 220,883 | 43.27% |
| `2014-2017` | `9` | 68,477 | 33.42% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `tobacco_use_revised` <a id="c820-fetal_death-tobacco_use_revised"></a>

_Schema note:_ N, U, Y — Y=Yes; N=No; U=Unknown. Version A only. 2006 also has X=Not on certificate. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `U`: 1,401 (1.30%); `N`: 1,342 (1.25%); `Y`: 215 (0.20%) | 97.26% |
| `2005-2013` | 510,528 | `U`: 7,325 (1.43%); `N`: 7,102 (1.39%); `Y`: 1,223 (0.24%) | 96.93% |
| `2014-2017` | 204,923 | `N`: 110,313 (53.83%); `U`: 56,950 (27.79%); `Y`: 11,437 (5.58%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 199,800 (68.13%); `U`: 79,952 (27.26%); `Y`: 13,510 (4.61%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `U` | 1,401 | 1.30% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `U` | 7,325 | 1.43% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `U` | 56,950 | 27.79% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 79,952 | 27.26% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `tobacco_cig_1st_tri` <a id="c820-fetal_death-tobacco_cig_1st_tri"></a>

_Schema note:_ 0-99 — 00-98 daily; 99=Unknown. Version A only. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `99`: 1,401 (1.30%); `00`: 1,356 (1.26%); `10`: 76 (0.07%); `20`: 41 (0.04%); `03`: 19 (0.02%); `01`: 11 (0.01%); `05`: 11 (0.01%); `04`: 10 (0.01%); _(+9 more codes)_ | 97.26% |
| `2005-2013` | 510,528 | `99`: 7,332 (1.44%); `00`: 7,133 (1.40%); `10`: 385 (0.08%); `20`: 282 (0.06%); `05`: 134 (0.03%); `03`: 68 (0.01%); `02`: 56 (0.01%); `01`: 40 (0.01%); _(+17 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `00`: 110,557 (53.95%); `99`: 56,991 (27.81%); `10`: 3,651 (1.78%); `20`: 2,130 (1.04%); `05`: 1,495 (0.73%); `03`: 709 (0.35%); `02`: 673 (0.33%); `01`: 576 (0.28%); _(+33 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `00`: 200,073 (68.22%); `99`: 79,934 (27.26%); `10`: 4,131 (1.41%); `20`: 2,641 (0.90%); `05`: 1,917 (0.65%); `01`: 910 (0.31%); `03`: 794 (0.27%); `02`: 734 (0.25%); _(+38 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `99` | 1,401 | 1.30% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `98` | 39 | 0.01% |
| `2005-2013` | `99` | 7,332 | 1.44% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `98` | 113 | 0.06% |
| `2014-2017` | `99` | 56,991 | 27.81% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `98` | 61 | 0.02% |
| `2018-2024` | `99` | 79,934 | 27.26% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`00`, `10`, `99`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`20`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `15`, `98`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`40`}; dropped {`98`} _(codes ≥0.05% of an era)_

### `tobacco_cig_2nd_tri` <a id="c820-fetal_death-tobacco_cig_2nd_tri"></a>

_Schema note:_ 0-99 — 00-98 daily; 99=Unknown. Version A only. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `99`: 1,409 (1.31%); `00`: 1,387 (1.29%); `10`: 65 (0.06%); `20`: 32 (0.03%); `03`: 14 (0.01%); `05`: 11 (0.01%); `02`: 10 (0.01%); `01`: 8 (0.01%); _(+6 more codes)_ | 97.26% |
| `2005-2013` | 510,528 | `99`: 7,390 (1.45%); `00`: 7,278 (1.43%); `10`: 332 (0.07%); `20`: 209 (0.04%); `05`: 108 (0.02%); `03`: 67 (0.01%); `02`: 42 (0.01%); `98`: 41 (0.01%); _(+16 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `00`: 112,898 (55.09%); `99`: 57,326 (27.97%); `10`: 2,753 (1.34%); `20`: 1,402 (0.68%); `05`: 1,256 (0.61%); `03`: 577 (0.28%); `02`: 530 (0.26%); `01`: 484 (0.24%); _(+28 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `00`: 202,813 (69.16%); `99`: 80,113 (27.32%); `10`: 3,163 (1.08%); `20`: 1,959 (0.67%); `05`: 1,601 (0.55%); `01`: 685 (0.23%); `03`: 656 (0.22%); `02`: 611 (0.21%); _(+35 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `99` | 1,409 | 1.31% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `98` | 41 | 0.01% |
| `2005-2013` | `99` | 7,390 | 1.45% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `98` | 118 | 0.06% |
| `2014-2017` | `99` | 57,326 | 27.97% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `98` | 53 | 0.02% |
| `2018-2024` | `99` | 80,113 | 27.32% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`00`, `10`, `99`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `15`, `20`, `98`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`15`, `98`} _(codes ≥0.05% of an era)_

### `tobacco_cig_3rd_tri` <a id="c820-fetal_death-tobacco_cig_3rd_tri"></a>

_Schema note:_ 0-99 — 00-98 daily; 99=Unknown. Version A only. Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `99`: 1,420 (1.32%); `00`: 1,403 (1.30%); `10`: 53 (0.05%); `20`: 28 (0.03%); `03`: 13 (0.01%); `05`: 12 (0.01%); `04`: 7 (0.01%); `02`: 5 (0.00%); _(+6 more codes)_ | 97.26% |
| `2005-2013` | 510,528 | `99`: 7,514 (1.47%); `00`: 7,398 (1.45%); `10`: 247 (0.05%); `20`: 169 (0.03%); `05`: 75 (0.01%); `98`: 45 (0.01%); `03`: 41 (0.01%); `02`: 33 (0.01%); _(+15 more codes)_ | 96.93% |
| `2014-2017` | 204,923 | `00`: 114,393 (55.82%); `99`: 57,663 (28.14%); `10`: 2,122 (1.04%); `20`: 1,109 (0.54%); `05`: 1,007 (0.49%); `03`: 458 (0.22%); `02`: 419 (0.20%); `01`: 390 (0.19%); _(+27 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `99`: 219,508 (74.85%); `00`: 68,632 (23.40%); `10`: 1,541 (0.53%); `20`: 981 (0.33%); `05`: 783 (0.27%); `03`: 366 (0.12%); `01`: 336 (0.11%); `02`: 322 (0.11%); _(+27 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | `99` | 1,420 | 1.32% |
| `2003-2004` | _null/blank_ | 104,824 | 97.26% |
| `2005-2013` | `98` | 45 | 0.01% |
| `2005-2013` | `99` | 7,514 | 1.47% |
| `2005-2013` | _null/blank_ | 494,878 | 96.93% |
| `2014-2017` | `98` | 142 | 0.07% |
| `2014-2017` | `99` | 57,663 | 28.14% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `98` | 26 | 0.01% |
| `2018-2024` | `99` | 219,508 | 74.85% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`00`, `99`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`01`, `02`, `03`, `04`, `05`, `06`, `07`, `10`, `20`, `98`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`06`, `07`, `98`} _(codes ≥0.05% of an era)_

### `tobacco_cig_prepreg` <a id="c820-fetal_death-tobacco_cig_prepreg"></a>

_Schema note:_ 0-99 — 00-98 daily; 99=Unknown. Version A only. Not in 2006 layout. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `00`: 108,439 (52.92%); `99`: 56,475 (27.56%); `10`: 4,192 (2.05%); `20`: 3,542 (1.73%); `05`: 1,527 (0.75%); `03`: 726 (0.35%); `02`: 702 (0.34%); `01`: 604 (0.29%); _(+35 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `00`: 197,210 (67.25%); `99`: 79,854 (27.23%); `10`: 4,644 (1.58%); `20`: 4,092 (1.40%); `05`: 1,983 (0.68%); `01`: 1,032 (0.35%); `03`: 855 (0.29%); `02`: 820 (0.28%); _(+41 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `98` | 133 | 0.06% |
| `2014-2017` | `99` | 56,475 | 27.56% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `98` | 85 | 0.03% |
| `2018-2024` | `99` | 79,854 | 27.23% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`00`, `01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `10`, `15`, `20`, `30`, `40`, `98`, `99`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`98`} _(codes ≥0.05% of an era)_

### `tobacco_use_unrevised` <a id="c820-fetal_death-tobacco_use_unrevised"></a>

_Schema note:_ 1-9 — 1=Yes; 2=No; 9=Unknown. V2 1992-2002 sources from TOBACCO (245); V1 2005-2006 sources from TOBUSE (S-version only). Blank for 2007-2013.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `9`: 112,815 (59.72%); `2`: 59,498 (31.50%); `1`: 16,596 (8.79%) | 0.00% |
| `1992-2002` | 700,704 | `9`: 404,721 (57.76%); `2`: 247,489 (35.32%); `1`: 48,494 (6.92%) | 0.00% |
| `2003-2004` | 107,782 | `9`: 62,950 (58.40%); `2`: 38,560 (35.78%); `1`: 6,272 (5.82%) | 0.00% |
| `2005-2013` | 510,528 | `9`: 56,145 (11.00%); `2`: 32,493 (6.36%); `1`: 5,256 (1.03%) | 81.61% |
| `2014-2017` | 204,923 | — | 100.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 112,815 | 59.72% |
| `1992-2002` | `9` | 404,721 | 57.76% |
| `2003-2004` | `9` | 62,950 | 58.40% |
| `2005-2013` | `9` | 56,145 | 11.00% |
| `2005-2013` | _null/blank_ | 416,634 | 81.61% |
| `2014-2017` | _null/blank_ | 204,923 | 100.00% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `9`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `prepregnancy_bmi` <a id="c820-fetal_death-prepregnancy_bmi"></a>

_Schema note:_ 13.0-69.9;99.9 — Valid range 13.0-69.9; 99.9=Unknown. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `99.9`: 73,878 (36.05%); `26.6`: 1,760 (0.86%); `28.3`: 1,618 (0.79%); `23.0`: 1,181 (0.58%); `25.8`: 1,158 (0.57%); `22.3`: 1,119 (0.55%); `27.4`: 1,104 (0.54%); `25.7`: 1,069 (0.52%); _(+513 more codes)_ | 12.80% |
| `2018-2024` | 293,262 | `99.9`: 100,939 (34.42%); `26.6`: 3,227 (1.10%); `28.3`: 3,023 (1.03%); `27.4`: 2,077 (0.71%); `23.0`: 2,059 (0.70%); `25.8`: 2,022 (0.69%); `22.3`: 1,872 (0.64%); `27.5`: 1,869 (0.64%); _(+538 more codes)_ | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `99.9` | 73,878 | 36.05% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `99.9` | 100,939 | 34.42% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`16.6`, `17.2`, `17.4`, `17.5`, `17.6`, `17.7`, `17.8`, `17.9`, `18.0`, `18.1`, `18.2`, `18.3`, `18.4`, `18.5`, `18.6`, `18.7`, `18.8`, `18.9`, `19.0`, `19.1`, `19.2`, `19.3`, `19.4`, `19.5`, `19.6`, `19.7`, `19.8`, `19.9`, `20.0`, `20.1`, `20.2`, `20.3`, `20.4`, `20.5`, `20.6`, `20.7`, `20.8`, `20.9`, `21.0`, `21.1`, `21.2`, `21.3`, `21.4`, `21.5`, `21.6`, `21.7`, `21.8`, `21.9`, `22.0`, `22.1`, `22.2`, `22.3`, `22.4`, `22.5`, `22.6`, `22.7`, `22.8`, `22.9`, `23.0`, `23.1`, `23.2`, `23.3`, `23.4`, `23.5`, `23.6`, `23.7`, `23.8`, `23.9`, `24.0`, `24.1`, `24.2`, `24.3`, `24.4`, `24.5`, `24.6`, `24.7`, `24.8`, `24.9`, `25.0`, `25.1`, `25.2`, `25.3`, `25.4`, `25.5`, `25.6`, `25.7`, `25.8`, `25.9`, `26.0`, `26.1`, `26.2`, `26.3`, `26.4`, `26.5`, `26.6`, `26.7`, `26.8`, `26.9`, `27.0`, `27.1`, `27.2`, `27.3`, `27.4`, `27.5`, `27.6`, `27.7`, `27.8`, `27.9`, `28.0`, `28.1`, `28.2`, `28.3`, `28.4`, `28.5`, `28.6`, `28.7`, `28.8`, `28.9`, `29.0`, `29.1`, `29.2`, `29.3`, `29.4`, `29.5`, `29.6`, `29.7`, `29.8`, `29.9`, `30.0`, `30.1`, `30.2`, `30.3`, `30.4`, `30.5`, `30.6`, `30.7`, `30.8`, `30.9`, `31.0`, `31.1`, `31.2`, `31.3`, `31.4`, `31.5`, `31.6`, `31.7`, `31.8`, `31.9`, `32.0`, `32.1`, `32.2`, `32.3`, `32.4`, `32.5`, `32.6`, `32.7`, `32.8`, `32.9`, `33.0`, `33.1`, `33.2`, `33.3`, `33.4`, `33.5`, `33.6`, `33.7`, `33.8`, `33.9`, `34.0`, `34.1`, `34.2`, `34.3`, `34.4`, `34.5`, `34.6`, `34.7`, `34.8`, `34.9`, `35.0`, `35.1`, `35.2`, `35.3`, `35.4`, `35.5`, `35.7`, `35.8`, `35.9`, `36.0`, `36.1`, `36.2`, `36.3`, `36.4`, `36.5`, `36.6`, `36.7`, `36.8`, `36.9`, `37.0`, `37.1`, `37.2`, `37.3`, `37.4`, `37.6`, `37.7`, `37.8`, `37.9`, `38.0`, `38.1`, `38.2`, `38.3`, `38.4`, `38.6`, `38.7`, `38.8`, `39.0`, `39.1`, `39.2`, `39.3`, `39.5`, `39.7`, `39.9`, `40.2`, `40.3`, `40.4`, `40.6`, `40.7`, `40.8`, `41.0`, `41.2`, `41.6`, `42.0`, `42.1`, `42.3`, `42.6`, `42.9`, `43.3`, `43.9`, `44.3`, `44.6`, `99.9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`16.8`, `17.0`, `35.6`, `37.5`, `38.9`, `39.4`, `39.6`, `39.8`, `40.0`, `41.3`, `41.4`, `41.5`, `41.8`, `41.9`, `42.2`, `42.4`, `42.5`, `42.8`, `43.0`, `43.1`, `43.4`, `43.5`, `43.6`, `43.8`, `44.1`, `44.8`, `44.9`, `45.2`, `45.3`, `45.7`, `46.3`} _(codes ≥0.05% of an era)_

### `prepregnancy_bmi_recode` <a id="c820-fetal_death-prepregnancy_bmi_recode"></a>

_Schema note:_ 1-9 — 6-category BMI recode. Version A only. Not in 2006. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `9`: 73,878 (36.05%); `2`: 37,815 (18.45%); `3`: 27,540 (13.44%); `4`: 17,837 (8.70%); `5`: 10,091 (4.92%); `6`: 8,281 (4.04%); `1`: 3,258 (1.59%) | 12.80% |
| `2018-2024` | 293,262 | `9`: 100,939 (34.42%); `2`: 61,708 (21.04%); `3`: 51,541 (17.58%); `4`: 36,024 (12.28%); `5`: 20,653 (7.04%); `6`: 17,358 (5.92%); `1`: 5,039 (1.72%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `9` | 73,878 | 36.05% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 100,939 | 34.42% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`1`, `2`, `3`, `4`, `5`, `6`, `9`} _(codes ≥0.05% of an era)_

### `uterine_rupture` <a id="c820-fetal_death-uterine_rupture"></a>

_Schema note:_ N, U, Y — Y/N/U. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `N`: 125,662 (61.32%); `U`: 52,571 (25.65%); `Y`: 467 (0.23%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 240,607 (82.05%); `U`: 51,601 (17.60%); `Y`: 1,054 (0.36%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `U` | 52,571 | 25.65% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 51,601 | 17.60% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `icu_admission` <a id="c820-fetal_death-icu_admission"></a>

_Schema note:_ N, U, Y — Y/N/U. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `N`: 124,369 (60.69%); `U`: 52,571 (25.65%); `Y`: 1,760 (0.86%) | 12.80% |
| `2018-2024` | 293,262 | `N`: 238,262 (81.25%); `U`: 51,601 (17.60%); `Y`: 3,399 (1.16%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `U` | 52,571 | 25.65% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 51,601 | 17.60% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`N`, `U`, `Y`} _(codes ≥0.05% of an era)_

### `cause_icd10` <a id="c820-fetal_death-cause_icd10"></a>

_Schema note:_ 277 unique values — 5-character ICD-10 code; blank=none reported. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `P95`: 63,195 (30.84%); `P018`: 11,846 (5.78%); `P011`: 8,206 (4.00%); `P021`: 6,957 (3.39%); `P025`: 4,734 (2.31%); `P022`: 4,457 (2.17%); `P000`: 3,712 (1.81%); `P027`: 2,752 (1.34%); _(+464 more codes)_ | 32.66% |
| `2018-2024` | 293,262 | `P95`: 57,041 (19.45%); `P011`: 11,997 (4.09%); `P021`: 11,589 (3.95%); `P025`: 7,447 (2.54%); `P000`: 7,366 (2.51%); `P022`: 6,497 (2.22%); `P027`: 3,783 (1.29%); `P008`: 3,494 (1.19%); _(+529 more codes)_ | 47.60% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | _null/blank_ | 66,938 | 32.66% |
| `2018-2024` | _null/blank_ | 139,590 | 47.60% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`D181`, `P000`, `P001`, `P002`, `P003`, `P005`, `P008`, `P010`, `P011`, `P012`, `P013`, `P014`, `P015`, `P018`, `P020`, `P021`, `P022`, `P023`, `P024`, `P025`, `P026`, `P027`, `P038`, `P044`, `P059`, `P072`, `P073`, `P209`, `P298`, `P700`, `P701`, `P832`, `P95`, `Q000`, `Q039`, `Q042`, `Q249`, `Q270`, `Q602`, `Q789`, `Q792`, `Q793`, `Q897`, `Q899`, `Q909`, `Q913`, `Q917`, `Q927`, `Q969`, `Q999`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`P049`, `Q038`, `Q234`, `Q248`, `Q601`, `Q798`}; dropped {`P014`, `P209`} _(codes ≥0.05% of an era)_

### `cause_recode124` <a id="c820-fetal_death-cause_recode124"></a>

_Schema note:_ 2-143 — 3-digit recode (001-124). Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `104`: 63,195 (30.84%); `039`: 11,847 (5.78%); `032`: 8,206 (4.00%); `042`: 6,957 (3.39%); `046`: 4,734 (2.31%); `043`: 4,457 (2.17%); `021`: 3,712 (1.81%); `048`: 2,752 (1.34%); _(+103 more codes)_ | 32.67% |
| `2018-2024` | 293,262 | `104`: 57,041 (19.45%); `032`: 11,997 (4.09%); `042`: 11,589 (3.95%); `046`: 7,447 (2.54%); `021`: 7,366 (2.51%); `043`: 6,497 (2.22%); `048`: 3,783 (1.29%); `028`: 3,528 (1.20%); _(+101 more codes)_ | 47.60% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | _null/blank_ | 66,939 | 32.67% |
| `2018-2024` | _null/blank_ | 139,590 | 47.60% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`007`, `021`, `022`, `023`, `024`, `026`, `028`, `031`, `032`, `033`, `034`, `035`, `036`, `039`, `041`, `042`, `043`, `044`, `045`, `046`, `047`, `048`, `058`, `059`, `060`, `062`, `063`, `073`, `090`, `099`, `102`, `103`, `104`, `108`, `112`, `115`, `116`, `121`, `122`, `125`, `128`, `129`, `130`, `131`, `134`, `135`, `137`, `138`, `139`, `140`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`117`, `118`}; dropped {`035`, `073`, `102`} _(codes ≥0.05% of an era)_

### `cause_reporting_flag` <a id="c820-fetal_death-cause_reporting_flag"></a>

_Schema note:_ 0-1 — 0=Not reporting; 1=Reporting. Version A only. Not in 2006. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `0`: 113,319 (55.30%); `1`: 91,263 (44.54%); `*`: 92 (0.04%) | 0.12% |
| `2018-2024` | 293,262 | `1`: 162,753 (55.50%); `0`: 129,658 (44.21%) | 0.29% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | _null/blank_ | 249 | 0.12% |
| `2018-2024` | _null/blank_ | 851 | 0.29% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`0`, `1`} _(codes ≥0.05% of an era)_

### `attendant` <a id="c820-fetal_death-attendant"></a>

_Schema note:_ 1-9 — 1=MD; 2=DO; 3=CNM; 4=Other Midwife; 5=Other; 9=Unknown. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `1`: 174,198 (92.21%); `9`: 8,159 (4.32%); `2`: 3,166 (1.68%); `5`: 2,575 (1.36%); `3`: 715 (0.38%); `4`: 96 (0.05%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 655,605 (93.56%); `9`: 19,585 (2.80%); `2`: 12,474 (1.78%); `5`: 8,286 (1.18%); `3`: 4,070 (0.58%); `4`: 684 (0.10%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 98,765 (91.63%); `9`: 3,553 (3.30%); `2`: 2,958 (2.74%); `5`: 1,392 (1.29%); `3`: 992 (0.92%); `4`: 122 (0.11%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 466,643 (91.40%); `2`: 18,272 (3.58%); `9`: 12,118 (2.37%); `5`: 7,870 (1.54%); `3`: 5,056 (0.99%); `4`: 569 (0.11%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 181,104 (88.38%); `2`: 10,557 (5.15%); `9`: 5,391 (2.63%); `5`: 4,505 (2.20%); `3`: 3,125 (1.52%); `4`: 241 (0.12%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 255,564 (87.15%); `2`: 20,116 (6.86%); `5`: 8,313 (2.83%); `3`: 6,298 (2.15%); `9`: 2,643 (0.90%); `4`: 328 (0.11%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 8,159 | 4.32% |
| `1992-2002` | `9` | 19,585 | 2.80% |
| `2003-2004` | `9` | 3,553 | 3.30% |
| `2005-2013` | `9` | 12,118 | 2.37% |
| `2014-2017` | `9` | 5,391 | 2.63% |
| `2018-2024` | `9` | 2,643 | 0.90% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `3`, `4`, `5`, `9`} _(codes ≥0.05% of an era)_

### `delivery_place_revised` <a id="c820-fetal_death-delivery_place_revised"></a>

_Schema note:_ 1-9 — 7-category revised place (Hospital/Birth Center/Home intended/etc). Version A only. Same coding all years; position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | `1`: 11,864 (2.32%); `4`: 82 (0.02%); `7`: 51 (0.01%); `5`: 46 (0.01%); `6`: 40 (0.01%); `2`: 33 (0.01%); `9`: 21 (0.00%); `3`: 16 (0.00%) | 97.62% |
| `2014-2017` | 204,923 | `1`: 172,993 (84.42%); `6`: 1,974 (0.96%); `4`: 1,532 (0.75%); `7`: 953 (0.47%); `5`: 826 (0.40%); `3`: 192 (0.09%); `9`: 141 (0.07%); `2`: 89 (0.04%) | 12.80% |
| `2018-2024` | 293,262 | `1`: 284,082 (96.87%); `4`: 3,839 (1.31%); `6`: 2,149 (0.73%); `7`: 1,083 (0.37%); `5`: 913 (0.31%); `3`: 488 (0.17%); `9`: 485 (0.17%); `2`: 223 (0.08%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | `9` | 21 | 0.00% |
| `2005-2013` | _null/blank_ | 498,375 | 97.62% |
| `2014-2017` | `9` | 141 | 0.07% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `9` | 485 | 0.17% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2003-2004`→`2005-2013`: added {`1`} _(codes ≥0.05% of an era)_
- `2005-2013`→`2014-2017`: added {`3`, `4`, `5`, `6`, `7`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: added {`2`} _(codes ≥0.05% of an era)_

### `delivery_place_unrevised` <a id="c820-fetal_death-delivery_place_unrevised"></a>

_Schema note:_ 1-9 — WARNING: V2 vs V1 use INCOMPATIBLE place taxonomies. V2 PLDEL: 1=Hospital, 2=Doctor/home/public collapsed, 3=En route, 9=Unknown. V1 UBFACIL: 1=Hospital, 2=Birth Center, 3=Home (intended), 4=Home (unintended), 5=Other, 9=Unknown. C…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 413,155 (98.11%); `2`: 5,815 (1.38%); `9`: 1,815 (0.43%); `3`: 340 (0.08%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 186,482 (98.72%); `2`: 2,225 (1.18%); `9`: 124 (0.07%); `3`: 78 (0.04%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 686,870 (98.03%); `2`: 12,986 (1.85%); `9`: 603 (0.09%); `3`: 245 (0.03%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 105,811 (98.17%); `2`: 1,840 (1.71%); `9`: 49 (0.05%); `4`: 45 (0.04%); `3`: 30 (0.03%); `5`: 7 (0.01%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 494,436 (96.85%); `2`: 8,586 (1.68%); `5`: 3,367 (0.66%); `4`: 2,067 (0.40%); `3`: 1,528 (0.30%); `9`: 544 (0.11%) | 0.00% |
| `2014-2017` | 204,923 | `1`: 198,251 (96.74%); `4`: 2,550 (1.24%); `3`: 1,992 (0.97%); `5`: 953 (0.47%); `2`: 694 (0.34%); `9`: 483 (0.24%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | `9` | 1,815 | 0.43% |
| `1989-1991` | `9` | 124 | 0.07% |
| `1992-2002` | `9` | 603 | 0.09% |
| `2003-2004` | `9` | 49 | 0.05% |
| `2005-2013` | `9` | 544 | 0.11% |
| `2014-2017` | `9` | 483 | 0.24% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: dropped {`3`} _(codes ≥0.05% of an era)_
- `1992-2002`→`2003-2004`: dropped {`9`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`3`, `4`, `5`, `9`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `3`, `4`, `5`, `9`} _(codes ≥0.05% of an era)_

### `delivery_place_recode` <a id="c820-fetal_death-delivery_place_recode"></a>

_Schema note:_ 1-3 — 1=In Hospital; 2=Not in Hospital; 3=Unknown. V2 sources from raw PLDEL (8-8) — harmonize.py recodes PLDEL=1->1, PLDEL=3->1, PLDEL=2->2, PLDEL=9->3 — to recover V1's 3-bucket scheme that V2's PLDEL2 (which folds Unknown into 2) lacks.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | `1`: 413,495 (98.19%); `2`: 5,815 (1.38%); `3`: 1,815 (0.43%) | 0.00% |
| `1989-1991` | 188,909 | `1`: 186,560 (98.76%); `2`: 2,225 (1.18%); `3`: 124 (0.07%) | 0.00% |
| `1992-2002` | 700,704 | `1`: 687,115 (98.06%); `2`: 12,986 (1.85%); `3`: 603 (0.09%) | 0.00% |
| `2003-2004` | 107,782 | `1`: 105,811 (98.17%); `2`: 1,971 (1.83%) | 0.00% |
| `2005-2013` | 510,528 | `1`: 442,256 (86.63%); `2`: 14,493 (2.84%); `3`: 446 (0.09%) | 10.45% |
| `2014-2017` | 204,923 | `1`: 198,251 (96.74%); `2`: 6,189 (3.02%); `3`: 483 (0.24%) | 0.00% |
| `2018-2024` | 293,262 | `1`: 284,082 (96.87%); `2`: 8,695 (2.96%); `3`: 485 (0.17%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `2005-2013` | _null/blank_ | 53,333 | 10.45% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: dropped {`3`} _(codes ≥0.05% of an era)_
- `2003-2004`→`2005-2013`: added {`3`} _(codes ≥0.05% of an era)_

### `breech_unrevised` <a id="c820-fetal_death-breech_unrevised"></a>

_Schema note:_ 1-9 — WARNING: V2 vs V1 measure DIFFERENT CONCEPTS in this column. V2 BREECH = 'Breech/Malpresentation' (broader: includes any malpresentation — breech, transverse, brow, face). V1 ULD_BREECH = 'Breech Delivery' (narrower: only breech-po…

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `2`: 115,168 (60.96%); `9`: 64,074 (33.92%); `1`: 9,235 (4.89%); `8`: 432 (0.23%) | 0.00% |
| `1992-2002` | 700,704 | `2`: 394,823 (56.35%); `9`: 269,998 (38.53%); `1`: 35,883 (5.12%) | 0.00% |
| `2003-2004` | 107,782 | `2`: 51,361 (47.65%); `9`: 47,270 (43.86%); `1`: 6,193 (5.75%) | 2.74% |
| `2005-2013` | 510,528 | `9`: 254,367 (49.82%); `2`: 202,533 (39.67%); `1`: 50,131 (9.82%) | 0.68% |
| `2014-2017` | 204,923 | `9`: 99,162 (48.39%); `2`: 73,919 (36.07%); `1`: 31,842 (15.54%) | 0.00% |
| `2018-2024` | 293,262 | — | 100.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | `9` | 64,074 | 33.92% |
| `1992-2002` | `9` | 269,998 | 38.53% |
| `2003-2004` | `9` | 47,270 | 43.86% |
| `2003-2004` | _null/blank_ | 2,958 | 2.74% |
| `2005-2013` | `9` | 254,367 | 49.82% |
| `2005-2013` | _null/blank_ | 3,497 | 0.68% |
| `2014-2017` | `9` | 99,162 | 48.39% |
| `2018-2024` | _null/blank_ | 293,262 | 100.00% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`, `2`, `8`, `9`} _(codes ≥0.05% of an era)_
- `1989-1991`→`1992-2002`: dropped {`8`} _(codes ≥0.05% of an era)_
- `2014-2017`→`2018-2024`: dropped {`1`, `2`, `9`} _(codes ≥0.05% of an era)_

### `estimated_time_fetal_death` <a id="c820-fetal_death-estimated_time_fetal_death"></a>

_Schema note:_ A, L, N, U — N=At assessment no labor; L=At assessment labor; A=Labor no assessment; U=Unknown. Version A only. Not in 2006 public-use file. Available 2014+.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | — | 100.00% |
| `2005-2013` | 510,528 | — | 100.00% |
| `2014-2017` | 204,923 | `U`: 111,776 (54.55%); `N`: 50,865 (24.82%); `L`: 8,200 (4.00%); `A`: 7,859 (3.84%) | 12.80% |
| `2018-2024` | 293,262 | `U`: 176,417 (60.16%); `N`: 91,708 (31.27%); `L`: 13,667 (4.66%); `A`: 11,470 (3.91%) | 0.00% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 107,782 | 100.00% |
| `2005-2013` | _null/blank_ | 510,528 | 100.00% |
| `2014-2017` | `U` | 111,776 | 54.55% |
| `2014-2017` | _null/blank_ | 26,223 | 12.80% |
| `2018-2024` | `U` | 176,417 | 60.16% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `2005-2013`→`2014-2017`: added {`A`, `L`, `N`, `U`} _(codes ≥0.05% of an era)_

### `gestation_imputed_flag` <a id="c820-fetal_death-gestation_imputed_flag"></a>

_Schema note:_ 1-1 — Blank=Not imputed; 1=Imputed. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | `1`: 8,986 (4.76%) | 95.24% |
| `1992-2002` | 700,704 | `1`: 22,050 (3.15%) | 96.85% |
| `2003-2004` | 107,782 | `1`: 3,081 (2.86%) | 97.14% |
| `2005-2013` | 510,528 | `1`: 9,426 (1.85%) | 98.15% |
| `2014-2017` | 204,923 | `1`: 2,198 (1.07%) | 98.93% |
| `2018-2024` | 293,262 | `1`: 2,380 (0.81%) | 99.19% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 179,923 | 95.24% |
| `1992-2002` | _null/blank_ | 678,654 | 96.85% |
| `2003-2004` | _null/blank_ | 104,701 | 97.14% |
| `2005-2013` | _null/blank_ | 501,102 | 98.15% |
| `2014-2017` | _null/blank_ | 202,725 | 98.93% |
| `2018-2024` | _null/blank_ | 290,882 | 99.19% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1982-1988`→`1989-1991`: added {`1`} _(codes ≥0.05% of an era)_

### `obgest_used_flag` <a id="c820-fetal_death-obgest_used_flag"></a>

_Schema note:_ 1-1 — Blank=Not used; 1=Used. Same coding all years (A+S). Position differs in 2006.

**(i) Historical-value distribution (per era)**

| Era | n | Top values (`code`: count, %) | null/blank |
|---|--:|---|--:|
| `1982-1988` | 421,125 | — | 100.00% |
| `1989-1991` | 188,909 | — | 100.00% |
| `1992-2002` | 700,704 | — | 100.00% |
| `2003-2004` | 107,782 | `1`: 14,191 (13.17%) | 86.83% |
| `2005-2013` | 510,528 | `1`: 81,471 (15.96%) | 84.04% |
| `2014-2017` | 204,923 | `1`: 40,287 (19.66%) | 80.34% |
| `2018-2024` | 293,262 | `1`: 54,751 (18.67%) | 81.33% |

**(ii) Sentinel-code disambiguation**

| Era | sentinel | count | % of era |
|---|---|--:|--:|
| `1982-1988` | _null/blank_ | 421,125 | 100.00% |
| `1989-1991` | _null/blank_ | 188,909 | 100.00% |
| `1992-2002` | _null/blank_ | 700,704 | 100.00% |
| `2003-2004` | _null/blank_ | 93,591 | 86.83% |
| `2005-2013` | _null/blank_ | 429,057 | 84.04% |
| `2014-2017` | _null/blank_ | 164,636 | 80.34% |
| `2018-2024` | _null/blank_ | 238,511 | 81.33% |

_Documented meaning: see the schema note above (`harmonized_schema.csv` `notes`/`allowed_values`)._

**(iii) Era-by-era coding-scheme diff**

- `1992-2002`→`2003-2004`: added {`1`} _(codes ≥0.05% of an era)_

<!-- C8.20-GENERATED:END -->
