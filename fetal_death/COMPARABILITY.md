# Comparability Notes: U.S. Fetal Death Harmonized Dataset (V2.0, 1992-2022)

This document describes cross-year comparability issues that researchers must consider when analyzing trends across the 29-year dataset.

---

## Era Structure

The dataset spans **four** file-format eras, each based on a different NCHS record layout:

| Era | Years | Layout Source | Record Length | Revision |
|-----|-------|---------------|---------------|---------|
| **1992 era** | 1992-2002 | `FETAL_1992_2002_FIELDS` | 360 bytes (362 with CRLF) | 1989 only (synthesized `version_flag = 'S'`) |
| 2006 era | 2005-2013 | `FETAL_2005_2006_FIELDS` | 3,351 / 801 / 3,338 bytes | mixed 1989 (S) and 2003 (A) |
| 2014 era | 2014-2017 | `FETAL_2014_2017_FIELDS` | 3,050 bytes | mostly 2003 (A) with stragglers (S) |
| 2022 era | 2018-2022 | `FETAL_2018_2022_FIELDS` | 2,652 bytes | 2003 (A) only |

Record lengths shown are the full layout including end-of-record FILLER. For the 2022 era the last named field (`F_ICOD`) ends at position 2651; the record extends to position 2652 with a 1-byte trailing FILLER. The same convention applies to the 2006-era 3,351-byte layout (last named field at position 801; trailing FILLER to 3,351). See `record_layout_*.csv` for byte-exact field positions.

**Years 2003 and 2004 are deferred to V2.1** because of distinct, non-uniform transition layouts (1351-byte and 1501-byte records respectively); see NCHS's `fetaldeath0304problems.pdf` (downloadable from the CDC FTP server) for documentation of their idiosyncrasies.

Field positions differ across eras, but harmonized variable names are stable. The `data_year` column always identifies the source year.

---

## 1. The 2003 Revision Transition

The single most important comparability issue is the staggered adoption of the 2003 revision of the Standard Report of Fetal Death.

| Year | % A-version | % S-version | Implication |
|------|-------------|-------------|-------------|
| 1992-2002 | 0% | 100% (synthesized) | All V2 records are uniformly 1989-revision; the source files have no native VERSION field, so harmonize.py synthesizes `version_flag = 'S'` for all 700,704 rows |
| 2005 | 6.6% | 93.4% | Almost all records on 1989 revision |
| 2006 | 23.1% | 76.9% | 16 states on 2003 revision |
| 2008 | 36.5% | 63.5% | More states adopting |
| 2011 | 64.4% | 35.6% | Majority on 2003 revision |
| 2014 | 77.1% | 22.9% | 41 states + DC + NYC |
| 2017 | 96.2% | 3.8% | Nearly universal |
| 2018+ | 100.0% | 0.0% | All states on 2003 revision |

**Impact**: Variables marked "Version A only" in the codebook (revised education, revised tobacco, revised risk factors, BMI, cause of death, revised prenatal care) are only available for A-version records — i.e., for V1 only, and within V1 only for the subset of states already on the 2003 revision in a given year. The proportion of A-version records should be reported in any analysis that uses A-only fields.

**Recommendation**: For trend analysis of A-only variables, either restrict to 2018+ (100% A) or explicitly model the changing composition. For V2 (1992-2002), use the unrevised counterparts (`maternal_education_unrevised`, `tobacco_use_unrevised`, `diabetes_unrevised`, etc.) where available.

---

## 2. Race and Ethnicity

Race coding underwent multiple major changes across the 29-year span:

| Period | Race Classification | Available Variables |
|--------|--------------------|--------------------|
| 1992-2002 | 1989-revision: bridged single-race with 1992+ Asian/PI subcode expansion (codes 18-78) | `maternal_race_bridged` (recoded by harmonize); `maternal_race_bridged_detail` (raw 2-digit MRACE — within_era only) |
| 2005-2017 | Bridged single-race | `maternal_race_bridged` (1=White, 2=Black, 3=AIAN, 4=API) |
| 2014-2022 | OMB 1997 multi-race | `maternal_race_multi` (31 categories), `maternal_race_recode6` |
| 1992-2017 | Combined race/Hispanic | `race_hispanic_combined` (9 categories) |
| 2014-2022 | Revised race/Hispanic | `race_hispanic_revised` (8 categories) |

**Key V2 normalization (B3)**: The 1989-revision `MRACE` (positions 79-80) is a 2-digit code (`01` = White, `02` = Black, `03` = AIAN, `04-07` = Asian/PI single subgroups, `18-78` = expanded API subgroups, `99` = Unknown). harmonize.py recodes this to V1's 4-category bridged scheme: `01→1`, `02→2`, `03→3`, `04-78→4`, `99→blank`. The earlier 3-category `MRACE3` (position 81) was rejected because it collapses AIAN and API together, losing the distinction the V1 4-cat scheme preserves. The B3 normalization is byte-equivalent to using MRACE3 plus the AIAN/API split — a clean bijection on documented codes, with 2 V2 records (raw MRACE='99' Unknown) mapped to blank.

**Key break at 2018**: Starting in 2018, all states reported using the 1997 OMB multi-race standards. Before 2018, multi-race data are only available from states on the 2003 revision. The bridged-race variable (`maternal_race_bridged`) was discontinued in the 2022-era layout, leaving 218,040 V1 records with `maternal_race_bridged=''` for 2018-2022.

**Recommendation**: For race trend analysis spanning the full 1992-2022 period, use `hispanic_origin` (available and consistently coded all years; subject to V2 state-level non-reporting documented in §11) combined with `maternal_race_bridged` for 1992-2017 and `maternal_race_recode6` for 2014+. Be aware that 1992-2002 + 2005-2013 use bridged-race (collapsing multi-race into single categories) while 2018+ uses OMB multi-race directly. Do NOT cross-era groupby on `maternal_race_bridged_detail` (V2 carries 1989-rev MRACE codes; V1 2006 carries MBRACE codes — the same numerics 04-07 mean different subgroups in each era).

---

## 3. Maternal Education

| Period | Source | Coding |
|--------|--------|--------|
| 1992-2002 | `maternal_education_unrevised` (DMEDUC) | 00-17 years of school; 99=Unknown |
| 2005-2006 | `maternal_education` (A-version) | 1-9 revised coding |
| 2005-2006 | `maternal_education_unrevised` (UMEDUC, S-version) | 00-17 years of school |
| 2007-2013 | `maternal_education` | **Blank for all records** (NCHS data limitation) |
| 2014-2022 | `maternal_education` (A-version) | 1-9 revised coding |

**V2 limitation**: V2 (1992-2002) populates ONLY `maternal_education_unrevised`. The revised `maternal_education` field is blank for all V2 records because the revised 1-9 categorical scale was added in the 2003 revision. Consequently the derived `education_cat4` is also blank for all V2 records.

**V1 critical gap**: MEDUC is not available in the 2007-2013 V1 public-use files even for A-version records. This was confirmed at the raw byte level. The unrevised education field (UMEDUC) is also blank for 2007-2013.

**Recommendation**: 
- For 1992-2006 + 2014+, education analysis is possible but requires choosing a column. Years-of-school (`maternal_education_unrevised`) is available for 1992-2002 + 2005-2006 only (blank for 2007-2013, not in 2014+ layouts); revised 4-level categories (`education_cat4`) are available for 2005-2006 + 2014+ but not for 1992-2004 or 2007-2013.
- A 1989→2003 binning bridge (mapping years-of-school 00-17 into the revised <HS / HS / Some college / BA+ buckets) is **not provided by V2.0**: the year-of-schooling and degree-level concepts are not 1:1 mappable, and any bridge would impose modeling choices best left to the analyst. Researchers needing cross-era education trends must build their own bridge.

---

## 4. Cause of Death

| Period | Availability | Notes |
|--------|-------------|-------|
| 1992-2013 | Not available in public-use file | ICD-9 cause data exists in NCHS internal files but is restricted-use only (NCHS Research Data Center); NOT in any public-use fetal death file pre-2014 |
| 2014-2017 | Available (COD variant) | ICD-10 codes for A-version records with cause reported |
| 2018-2022 | Available (COD-only) | All records are A-version; ~47-51% have cause reported |

**Key break at 2014**: Cause-of-death data begins with the 2014 data year. There is no ICD-10 cause data in the public-use file before 2014. The 2006 user guide states this directly on p. 54: *"Cause-of-fetal-death data are also not currently available."* This is a structural limitation of the source data, not a pipeline gap.

**V2 implication**: `cause_icd10`, `cause_recode124`, `cause_reporting_flag`, and the derived `cause_group` are blank for all 700,704 V2 records.

**Missingness in V1 2018+**: Not all jurisdictions report cause of death to the national file. In 2022, NVSR Table 8 excluded 7 jurisdictions where >=50% of deaths had unspecified cause (P95), plus California. Cause completeness varies substantially by state and year.

**Recommendation**: Cause-of-death analysis is limited to 2014+. Always report the proportion of records with known cause. Consider excluding or flagging jurisdictions with high P95 rates.

---

## 5. Gestational Age Measurement

| Period | Primary GA Measure | Notes |
|--------|-------------------|-------|
| 1992-2002 | `gestational_age_combined` (DGESTAT) | 1989-revision edited gestation in weeks |
| 2005-2013 | `gestational_age_combined` (COMBGEST) | Based on last menstrual period (LMP) or clinical estimate |
| 2014-2022 | `gestational_age_combined` (COMBGEST) | Based on obstetric estimate (OE) starting 2014 |

**Key change at 2014**: NCHS switched from LMP-based to OE-based gestational age as the standard starting with the 2014 data year. The `gestational_age_combined` variable exists in all years but the underlying estimation method changed.

**V2 specifics**: V2's DGESTAT is the edited gestation used in NCHS publications for 1992-2002 — same concept as V1's COMBGEST but pre-2014 LMP-based. 34,430 V2 records (~4.9%) have `gestational_age_combined='99'` (Unknown). 3 V2 records (1992, raw rows 29061/30971/32652) have non-canonical single-digit values (`'2'`/`'3'`/`'4'`) due to upstream NCHS data-quality issue (raw bytes were `'2 '`/`'3 '`/`'4 '` — digit followed by space — which the harmonize step strips); all three rows have `birthweight=9999`.

**Recommendation**: `gestational_age_combined` is the primary GA variable and is available all years. Be aware of the LMP-to-OE transition at 2014 when interpreting small shifts in GA distributions. The broad categories (preterm vs. term) are minimally affected. For any analysis that filters to known GA, pre-filter `gestational_age_combined != '99'` (and optionally exclude the 3 V2 single-digit rows if they matter).

---

## 6. Gestational Age Recode Bins

The 12-category gestational age recode (`gestational_age_recode12`) has slightly different bin boundaries:

| Category | 2005-2013 | 2014-2022 |
|----------|-----------|-----------|
| 06 | 32-35 weeks | 32-33 weeks |
| 07 | 36 weeks | 34-36 weeks |
| 08 | 37-39 weeks | 37-38 weeks |
| 09 | 40 weeks | 39-40 weeks |

V2 (1989-revision GESTAT12) bin boundaries also differ slightly from the 2003-revision; verify against the 1992 user guide if relying on this recode for V2-specific analysis. This is why the field is labeled `comparability_class='partial'`.

**Recommendation**: Use `gestational_age_combined` (continuous weeks) rather than the 12-category recode for cross-era analysis. The 5-category recode (`gestational_age_recode5`) is consistent across eras.

---

## 7. Plurality — Data Quality Caveats

**NCHS documented coding** (1992 / 2006 / 2014 User Guides, DPLURAL field):

| Code | Meaning |
|------|---------|
| 1 | Single |
| 2 | Twin |
| 3 | Triplet |
| 4 | Quadruplet |
| 5 | Quintuplet or higher |
| 9 | Unknown / Louisiana non-reporter (V2 only) |

**Observed data pattern** (harmonized `plurality` column):

| Year range | Typical singleton % | Distinctive codes present | Notes |
|------------|---------------------|---------------------------|-------|
| 1992-1994 | ~95% (excl LA non-reporters) | `9` for ~99% of Louisiana resident records | LA explicit non-reporter; see §11 |
| 1995-2002 | ~95% | `9` near-zero | normal coding |
| 2005-2013 | ~85% | `5` present in large volumes (especially A-version records); `9` appears in S-version records only | See V1 anomaly below |
| 2014-2022 | ~92% | `9` appears across all records (typical of current NCHS convention); `5` near-zero | Consistent with NCHS spec |

### V1 2005-2013 DPLURAL="5" anomaly

The 2005-2013 A-version records contain an epidemiologically implausible concentration of `plurality == "5"` codes. For example, 2010 A-version records include 1,828 records coded "5" out of roughly 20,000 — i.e., roughly 9% of A-version fetal deaths nominally classified as quintuplet-or-higher. Real U.S. quintuplet-or-higher fetal death incidence is ~0-1 per year. Aggregate 2005-2013 A-version records contain ~10,200 records coded "5" under this pattern. The pattern ends abruptly in 2014 (2 records) as the 2003-revision layout matured; starting in 2014, missing plurality uses "9" instead.

Neither the 2006 nor the 2014 NCHS User Guide documents this anomaly. The most plausible explanation is state-level miscoding during the 2003-revision transition, where some states coded unknown plurality as "5" rather than blank. Because the pipeline faithfully reproduces the NCHS-published codes, the harmonized data preserves these records as-is — no silent remapping is performed.

**Impact on derived variables.** The `singleton` derived variable treats `plurality == "9"` and `""` as unknown (sets `singleton = ""`) and treats all other non-"1" values, including "5", as `singleton = "0"`. For 2005-2013, this means approximately 10,200 records are classified as multiple-birth when their true plurality is likely unknown. Trend analyses of singleton vs. multiple-birth fetal deaths across 2005-2022 will therefore show a spurious apparent decline in multiples between 2005-2013 and 2014+ that is driven by this coding artifact, not real epidemiology.

**Recommendation for researchers.** For analyses that depend on multiple-pregnancy classification in 2005-2013, treat `plurality == "5"` records as unknown: e.g., filter them out, or recode them to blank before using `singleton`. A conservative one-liner:

```python
df.loc[(df['data_year'] <= 2013) & (df['data_year'] >= 2005) & (df['plurality'] == '5'), 'plurality'] = ''
df.loc[(df['data_year'] <= 2013) & (df['data_year'] >= 2005) & (df['plurality'] == '5'), 'singleton'] = ''
```

Or simply exclude 2005-2013 from cross-year multiple-birth analyses.

---

## 7-bis. Delivery method (simple) — V1 2006-2013 code-`3` anomaly

The 2003-revision DMETH_REC is documented as a 3-code recode (`1`=Vaginal, `2`=C-section, `9`=Not stated). However, V1 2006-2013 records contain a residual code `3` on **2,553** rows:

| Year | A-version code-3 | S-version code-3 | Total |
|---|---:|---:|---:|
| 2005 | 0 | 0 | 0 |
| 2006 | 195 | 63 | 258 |
| 2007 | 184 | 83 | 267 |
| 2008 | 213 | 51 | 264 |
| 2009 | 248 | 39 | 287 |
| 2010 | 221 | 22 | 243 |
| 2011 | 276 | 47 | 323 |
| 2012 | 306 | 32 | 338 |
| 2013 | 545 | 28 | 573 |
| 2014+ | 0 | 0 | 0 |

The pattern appears in both A-version and S-version records, and disappears entirely from 2014 onward. The most plausible explanation is residual 1989-revision coding leaking into the 2003-revision DMETH_REC field during the multi-state transition window — under the 1989-rev scheme, code `3` meant "Primary C-section" — followed by full coding cleanup in the 2014 layout migration. Neither the 2006 nor the 2014 NCHS User Guide documents this anomaly. Because the pipeline faithfully reproduces the NCHS-published codes, the harmonized data preserves these records as-is — no silent remapping is performed.

**Impact.** A researcher filtering `delivery_method_recode == '2'` to count C-sections will undercount by ~258-573 rows per year in 2006-2013. The undercounted rows are most likely true C-sections (under 1989-rev semantics for code `3`), so simple C-section rate calculations on the full 1992-2022 file are slightly biased low for those eight years.

**Recommendation for researchers.** For C-section analyses spanning 2006-2013, treat code `3` as C-section:

```python
mask = (df['data_year'].between(2006, 2013)) & (df['delivery_method_recode'] == '3')
df.loc[mask, 'delivery_method_recode'] = '2'
```

Or, more conservatively, exclude these 2,553 rows from C-section analysis. The V2 (1992-2002) and V1 2014+ slices are not affected.

---

## 8. Unrevised Fields Discontinued

Several "unrevised" fields that provided backward-compatible data for 1989-revision states were discontinued in the 2018+ era:

- `diabetes_unrevised`, `chronic_hypertension_unrevised`, `pregnancy_hypertension_unrevised`, `eclampsia_unrevised` (available 1992-2017, blank 2018+)
- `delivery_place_unrevised`, `breech_unrevised` (available 1992-2017, blank 2018+; **see §10 — these are within_era due to incompatible cross-era semantics**)
- `tobacco_use_unrevised` (available 1992-2002 + 2005-2006 only; blank 2007-2013; not in 2018+)

These fields were removed because all states adopted the 2003 revision by 2018, making unrevised variants unnecessary.

**V2 specifics**: `diabetes_unrevised`, `chronic_hypertension_unrevised`, `pregnancy_hypertension_unrevised`, and `eclampsia_unrevised` use slightly different unknown semantics across eras: V2 1989-rev coding uses `1=Reported, 2=Not reported, 8=Not on cert, 9=Not classifiable`; V1 2006+ uses `1=Yes, 2=No, 8=Not on cert, 9=Unknown/Not stated`. Codes 1 and 2 are functionally equivalent in tabulation (1=present, 2=absent), but the `9` bucket has a slightly different meaning (Not classifiable vs Unknown/Not stated). These are labeled `comparability_class='partial'` and should be used with care.

---

## 9. BMI and Morbidity Fields

Pre-pregnancy BMI (`prepregnancy_bmi`), uterine rupture (`uterine_rupture`), and ICU admission (`icu_admission`) are only available from 2014 onward (2003 revision, COD variant). They are not present in the 1992 era or the 2006 era layouts.

NB: The 1992 layout has a `RUPTURE` field at position 265 — but it is *Premature Rupture of Membrane* (a labor complication), NOT the same item as the V1 2014+ `MM_RUPT` (intrapartum uterine rupture as a maternal morbidity outcome). The V2 RUPTURE field is preserved in the yearly raw parquet but is not mapped into the harmonized `uterine_rupture` column for this reason.

---

## 10. V2 Cross-Era Code Normalizations (B1-B6) and `within_era` Footguns

The 1989-revision (V2) and 2003-revision (V1) coding systems differ for a number of fields. V2.0 normalizes the V2 values inside `harmonize.py` (era=='1992' branch) for five fields so that cross-era `groupby` on those columns produces correct results. Three additional fields could not be safely normalized because the underlying concepts/categories are fundamentally incompatible — they are explicitly marked `within_era` with WARNINGs.

### Normalized columns (safe for cross-era analysis after V2 fix)

| Fix | Column | V2 raw | V1 raw | Normalization (V2 era only) |
|---|---|---|---|---|
| **B1** | `fetal_sex` | FSEX = `1`/`2`/`9` | SEX = `M`/`F`/`U` | `1→M, 2→F, 9→U` |
| **B2** | `delivery_method_recode` | DELMETH6 = `1`/`2`/`3`/`4`/`5`/`6` (6 cats: Vag-excl-VBAC, VBAC, PrimC, RepC, Hyst, NS) | DMETH_REC = `1`/`2`/`9` (Vaginal, C-section, NS) | `{1,2}→1, {3,4,5}→2, 6→9`. Full 6-cat detail preserved in yearly raw `DELMETH6`. |
| **B3** | `maternal_race_bridged` | MRACE 2-digit (01-07 single + 18-78 API + 99 Unk) | MRACEREC = `1`/`2`/`3`/`4` (W, B, AIAN, API) | `01→1, 02→2, 03→3, 04-78→4, 99→blank`. Crosswalk rejected MRACE3 (3-cat) which would collapse AIAN+API. |
| **B4** | `paternal_age_recode11` | FAGE11 = 12-cat (`10`=55-59, `11`=60-98, `12`=Unknown) | FAGEREC11 = 11-cat (`10`=55+, `11`=Unknown) | `01-09→01-09, {10,11}→10, 12→11`. Full 12-cat detail preserved in yearly raw `FAGE11`. |
| **B6** | `delivery_place_recode` | PLDEL2 = `1`/`2` only (2 conflates Unknowns) | BFACIL3 = `1`/`2`/`3` (Hospital, Not, Unknown) | re-derive from raw PLDEL: `{1,3}→1, 2→2, 9→3`. Recovers V1's 3-bucket scheme. |

### `within_era`-tagged columns (do NOT cross-era groupby)

| Column | V2 (1992-2002) | V1 (2005+) | Why incompatible |
|---|---|---|---|
| `maternal_race_bridged_detail` | Raw 1989-rev MRACE: `01`-`07` single race + `18`/`28`/`38`/`48`/`58`/`68`/`78` Asian/PI subcodes + `99` Unknown | Raw 2006 MBRACE: `01`-`14` single race + `21`-`24` bridged race subcategories | Codes `04`-`07` mean different ethnic subgroups in each era (V2 `04`=Chinese; V1 `04`=AIAN-Aleut; etc.). Numeric overlap with semantic divergence. |
| `delivery_place_unrevised` | Raw PLDEL: `1`=Hospital, `2`=Doctor/home/public collapsed, `3`=En route, `9`=Unknown | Raw UBFACIL: `1`=Hospital, `2`=Birth Center, `3`=Home (intended), `4`=Home (unintended), `5`=Other, `9`=Unknown | Codes `2` and `3` mean entirely different things across eras. V2 has 4-cat scheme; V1 has 5-cat scheme. |
| `breech_unrevised` | BREECH = "**Breech/Malpresentation**" (broader: includes any malpresentation — breech, transverse, brow, face) | ULD_BREECH = "**Breech Delivery**" (narrower: actual breech-position deliveries only) | Different clinical concepts in the same column. Verified in 1998 user guide p.57 + 2006 user guide p.28. |

For users who need V2-specific detail beyond the harmonized normalization, the yearly raw parquets — bundled in this Zenodo deposit as `fetal_death_yearly_raw_1992-2022.zip` (29 files inside; in the GitHub source repo they live under `output/yearly_clean/`) — preserve every documented field at its source coding.

---

## 11. V2-Specific State-Level Reporting Quirks (1992-2002)

The 1992-era public-use files carry state codes (STATEFET, STATERES, STOCCFIP, etc.) in the raw yearly parquets. Several state-level reporting incompletenesses are documented in NVSR 57-08 footnotes and reproduced faithfully in the data:

### Hispanic-origin non-reporting (`hispanic_origin == '9'` for all records)

| State | NCHS code | FIPS | Years 100% unknown |
|---|---|---|---|
| Oklahoma | 37 | 40 | **All 11 V2 years (1992-2002)** |
| Maryland | 21 | 24 | 1992-1998 (partial reporting starts 1999) |
| Massachusetts | 22 | 25 | 1992-1997 (partial reporting starts 1998 at 22.3%) |

A user computing Hispanic-origin distributions for V2 should either exclude these state-years or document the bias.

### Louisiana plurality non-reporting (1992-1994)

Louisiana (NCHS code 19, FIPS 22) reports `DPLURAL=9` (Unknown/Louisiana-non-reporter) for essentially all in-state fetal deaths in 1992-1994. By **state of occurrence** (STATEFET=19, the NCHS tabulation convention), 1,686 of 1,714 LA-occurrence records have `plurality=9` (≈98.4%); the 28 exceptions are all interstate nonresidents (`residence_status=3`), and 100% of LA-resident records (RESTATUS≠3) are coded 9. By **state of residence** (STATERES=19), 1,684 of 1,684 LA-resident records excluding interstate nonresidents are coded `plurality=9` (100%); the residence-side count is 1,732 total / 1,689 coded 9 (the 48 RESTATUS=3 LA-residents had their death recorded by other states and are not subject to LA's reporting practice). Reporting resumed normally in 1995. The `singleton` derived variable correctly returns `''` (unknown) for all these records.

### NYC-vs-NY-state coding

In V2 the `STFETEXP` field (positions 15-16) separates NYC from NY state at code `34`/`33`, while `STATEFET` (17-18) folds NYC into NY state (NCHS code `33`). 51 distinct STATEFET values appear in every V2 year (50 states + DC; NYC is part of NY state in STATEFET). NCHS state code `02` is Alaska, NOT NYC. State codes are alphabetical (e.g., OH=36, OK=37 — not the FIPS ordering).

---

## 12. V2 stale-guide years (1996, 2001, 2002)

Three NCHS Fetal Death User Guides (1996, 2001, 2002) have a "U.S. DATA SET → Record count" block that was copy-pasted from an adjacent year. The parsed counts from the raw bytes are:

| Year | Stale guide figure | NVSR 57-08 (authoritative) | Our parse | Resolution |
|---|---|---|---|---|
| 1996 | 27,323 (= 1995's figure) | 27,069 | 27,069 | NVSR matches our parse — guide is stale |
| 2001 | 27,046 (= 2000's figure) | 26,373 | 26,373 | NVSR matches our parse |
| 2002 | 27,046 (= 2000's figure) | 25,943 | 25,943 | NVSR matches our parse |

The pipeline's parse is byte-correct; the guide figures for those three years are documentation errors.

---

## Summary: Variable Availability Matrix (V2 + V1 eras)

| Variable Group | 1992-2002 | 2005-2006 | 2007-2013 | 2014-2017 | 2018-2022 |
|----------------|-----------|-----------|-----------|-----------|-----------|
| Core demographics (age, sex, GA, BW) | All | All | All | All | All |
| Hispanic origin | All (subject to OK/MD/MA non-reporting) | All | All | All | All |
| Bridged race | All (recoded by harmonize from 1989-rev MRACE) | All | All | All | -- |
| Multi-race | -- | -- | -- | A-only | All |
| Education (revised, 4-cat) | -- (V2 uses `*_unrevised` only) | A-only | **Blank** | A-only | All |
| Education (unrevised, years-of-school) | All | All (S-version) | All (S-version) | -- | -- |
| Tobacco (revised) | -- | A-only | A-only | A-only | All |
| Tobacco (unrevised) | All | All | All | -- | -- |
| Risk factors (revised) | -- | A-only | A-only | A-only | All |
| Risk factors (unrevised) | All | All | All | All | -- |
| Cause of death (ICD-10) | -- | -- | -- | A-only | All (~50%) |
| BMI | -- | -- | -- | A-only | All |
| Morbidity (ICU, rupture) | -- | -- | -- | A-only | All |
| Marital status | All | All | All | -- | -- |
| Father's age (single-year) | All | A-only | **Blank** | A-only | All |
| Father's age recode 11 | All (recoded by harmonize from 12-cat) | All | All | All | All |
| Delivery method recode (3-cat) | All (collapsed by harmonize from 6-cat) | All | All | All | All |
| Delivery place recode (3-bucket) | All (re-derived by harmonize from raw PLDEL) | All | All | All | All |
| Breech_unrevised, delivery_place_unrevised, maternal_race_bridged_detail | within_era warnings | within_era warnings | within_era warnings | within_era warnings | -- |
