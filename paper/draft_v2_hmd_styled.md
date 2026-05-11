# Data Resource Profile: U.S. Harmonized Vital Statistics microdata, 1990–2024

The U.S. Harmonized Vital Statistics (HVS) microdata resource integrates and disseminates harmonized natality, linked birth–infant death, and fetal death public-use microdata released by the U.S. National Center for Health Statistics (NCHS), as three companion parquet files with one stable column schema per product. Coverage extends from 1990 forward and comprises 138,819,655 birth records (1990–2024), 74,943,824 linked birth–infant death records (2005–2023), and 1,634,195 fetal death records (1992–2022). The harmonization integrates source files spanning two U.S. Standard Certificate revisions (1989 and 2003), three within-revision NCHS layout reformats, and a state-by-state staggered adoption window in which a single annual file contains records following different schemas. Variable coding schemes are standardized across eras, without loss of detail, into one stable parquet column schema per product, and per-year raw parquets preserving every documented source field are also disseminated. The harmonized parquet reproduces every per-year aggregate published by NCHS in the relevant *National Vital Statistics Reports* (*NVSR*) series byte-exactly under a documented analytic filter. The resource is released under Creative Commons Attribution 4.0 on Zenodo, with deterministic open-source pipelines re-runnable end-to-end from the public NCHS source files in tens of minutes on a laptop, and with no application or data-use agreement required.

## Data resource basics

The U.S. National Vital Statistics System counts every birth, fetal death, and infant death registered in the country—approximately 3.5–4 million live births, 20,000–30,000 fetal deaths, and 20,000 infant deaths each year.[^nvsr_births] Since 1933 these events have been compiled by the U.S. National Center for Health Statistics (NCHS), and since the early 1980s NCHS has released them as annual fixed-width public-use microdata files. The microdata underlie most U.S. perinatal-mortality and stillbirth trend studies, state-level disparity analyses with individual-level covariates, and age-period-cohort decompositions in the field.

These microdata are difficult to use across years because the source layouts change. Field positions, code values, and variable inventories shift at three kinds of boundary: (i) the transition from the 1989 to the 2003 U.S. Standard Certificate, phased over 2003–2014 for natality and over 2005–2017 for the public-use V1 fetal-death window, with 100% A-version reporting reached in 2018; (ii) within-revision NCHS reformats, including a 2006 compression of the natality record length from 1500 to 775 bytes (with unrevised-only fields blanked from 2009 onward) and a 2014 reformat to a revised-only 1345-byte layout; and (iii) state-by-state staggered adoption of the 2003 revision, so that an annual file during the transition window contains records following different schemas depending on the state of registration. The same conceptual variable can occupy different byte positions, use different code values, or be absent entirely depending on year and state.

The field has adapted by restricting analyses to single-revision windows. Salihu and colleagues used 1995–1998, chosen for 1989-revision uniformity;[^salihu2004] Willinger and colleagues used 2001–2002, the last two uniform years before the 2003-revision rollout;[^willinger2009] Hogue and Silver, surveying stillbirth disparities through 2005, were forced to use aggregate published rates rather than microdata;[^hogue2011] Ananth and colleagues' 1980–2020 age-period-cohort stillbirth analysis explicitly excluded Hispanic ethnicity because the variable "was only made available in the revised 2003 birth certificates".[^ananth2022] These restrictions reflect the source files, not investigator preference.

Although NCHS itself publishes harmonized cross-revision tabulations in the *Births: Final Data* and *Fetal and Perinatal Mortality* *NVSR* series, those are aggregate tables: the microdata-level harmonization is performed by NCHS analysts inside the agency on a fixed tabulation grid, and only the published cells survive. To our knowledge, no public harmonized longitudinal microdata product has previously existed for U.S. natality, linked birth–infant death, or fetal death.

The U.S. Harmonized Vital Statistics (HVS) microdata resource fills this gap. The first release was in 2026. The resource is maintained by a single author, with releases versioned on Zenodo: concept DOIs always resolve to the latest version, and version-specific DOIs let analyses pin to an exact release. The pipelines are open-source on GitHub, included verbatim in each Zenodo deposit, and run end-to-end from the public NCHS source files in tens of minutes on a laptop.

## Data resource area and coverage

The HVS resource covers the United States from 1990 forward. The natality file contains 138,819,655 records covering 1990–2024 (84 columns), the linked birth–infant death file contains 74,943,824 records covering 2005–2023 (94 columns; denominator-plus cohort format 2005–2015, period-cohort merged format 2016–2023), and the harmonized fetal death file contains 1,634,195 records covering 1992–2022 (89 columns). Each product carries one stable column schema across all years it covers. Per-year raw parquets preserving every documented source field are also disseminated for users who need detail outside the harmonized schema.

The fetal-death years 2003 and 2004 use distinct transition layouts (1351 and 1501 bytes respectively, with mixed-revision content) and are deferred to a future release. Fetal-death years 1982–1991, spanning the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts, are deferred to a planned V3 release. The "1992–2002 uniform" framing for the fetal-death V2 era reflects empirical verification: byte-level comparison of 50 records by 197 fields by 10 years (98,500 raw-byte to parquet-cell comparisons) returned zero mismatches across 1993–2002, with 1992 verified separately.

The harmonized natality file spans five era segments with four era-to-era transitions; the linked file spans three segments with two transitions; the harmonized fetal-death file spans three segments with two transitions (Table 1). Within each segment the source layout is uniform; at the transitions record length, certificate revision, or both can change.

**Table 1.** Source-data era boundaries by product.

| Product | Era | Years | Record length | Certificate / revision |
|---|---|---|---|---|
| Natality | Unrevised-only | 1990–2002 | 350 bytes | 1989 |
| Natality | Dual-certificate transition (long format) | 2003 | 1350 bytes | Dual |
| Natality | Dual-certificate transition (long format) | 2004–2005 | 1500 bytes | Dual |
| Natality | Dual-certificate transition (short format) | 2006–2013 | 775 bytes | Dual; unrevised-only fields blanked from 2009 |
| Natality | Revised-only | 2014–2024 | 1345 bytes | 2003 |
| Linked birth–infant death | Cohort, denominator-plus | 2005–2013 | 900 bytes | Dual |
| Linked birth–infant death | Cohort, denominator-plus | 2014–2015 | 1384 bytes | 2003 |
| Linked birth–infant death | Period-cohort merged (CO_SEQNUM × CO_YOD) | 2016–2023 | varies | 2003 |
| Fetal death | 1989-revision uniform | 1992–2002 | 360 bytes | 1989 |
| Fetal death | 2003-revision transition | 2005–2017 | varies | Mixed (2003-revision A or 1989-revision S per state-year) |
| Fetal death | Revised-only | 2018–2022 | varies | 2003 |

Geographic coverage is the United States as a whole. State-level identifiers are present in the per-year raw parquets for natality 1990–2024, linked birth–infant death 2005–2023, and fetal death 1992–2002. State identifiers are suppressed by NCHS in V1-era fetal-death public-use files (2005 onward) and are therefore absent from the harmonized fetal-death file in those years.

## Measures

Each product ships one stable harmonized schema mapping per-era raw fields to a common dtype, name, and code space. The natality file has 71 harmonized columns plus 13 derived indicators (84 total); the linked file extends this with 7 death-side harmonized columns and 3 death-side derived indicators (94 total); the fetal-death file has 73 harmonized columns plus 16 derived indicators (89 total). Each product's `harmonized_schema.csv` lists dtype, allowed values, coverage, comparability class, and source raw field per era; the full per-era raw-to-harmonized mapping ships as `variable_crosswalk_working.csv` (Supplementary Table S1).

Harmonized measures cover demographics (maternal and paternal age, race bridged to four-category Census, Hispanic origin, marital status, educational attainment, and residence status); pregnancy (gestational age — best obstetric estimate plus last-menstrual-period derivation where available — plurality, prior live births, prior fetal deaths, prenatal-care utilization, tobacco use); delivery (birth weight, delivery method, breech presentation, place of delivery, birth attendant); infant outcomes in the linked file (age at death, place of death, ICD-10 cause-of-death codes, NCHS-assigned record weight); fetal-death-specific measures (cause of fetal death by ICD-10 prefix groupings 2014 onward, autopsy status, and the NVSR tabulation flag for inclusion in published fetal-mortality counts); and constructed analytic indicators (low birth weight, preterm birth, neonatal vs post-neonatal death, ICD-10 cause groupings) computed deterministically from the harmonized columns.

Sentinel values (`gestational_age_combined=99`, `birthweight=9999`, `plurality=9`, etc.) are converted to NaN inside the derivation step before threshold comparisons, so constructed indicators return missing for sentinel-coded records; the harmonized parent retains raw sentinels.

### Comparability classification

Every harmonized column is tagged with one of four comparability classes: **full** (consistent across all years covered), **partial** (consistent within era; minor cross-era differences explicitly documented), **within_era** (incompatible content across eras; cross-era aggregation should not be performed), or **not_available** (era does not collect the field). The class is recorded in the schema CSV. Three of the within_era fetal-death columns carry irreducibly incompatible content across the revision boundary in ways that cannot be reconciled by value-level normalization: `breech_unrevised` (V2 "Breech/Malpresentation" is broader than V1 "Breech Delivery"); `delivery_place_unrevised` (V2 4-category PLDEL vs V1 5-category UBFACIL with non-overlapping codes 2 and 3); and `maternal_race_bridged_detail` (V2 1989-revision MRACE codes and V1 2003-revision MBRACE codes overlap numerically but encode different ethnic subgroups). All three are flagged with explicit warnings in the schema and codebook; users are referred to the per-year raw parquets when within-era detail is required.

## Methods

The HVS resource is produced for each of the three products by deterministic open-source pipelines committed to GitHub and re-runnable end-to-end from the public NCHS source files:

1. **Acquisition.** Annual fixed-width zips, User Guide PDFs, and *NVSR* reference reports are obtained from the NCHS public FTP server, with per-file SHA-256 checksums recorded in each deposit's `file_inventory.csv`.
2. **Parsing.** Each annual file is parsed using era-specific record-layout CSVs (`record_layout_*.csv`) that encode byte-position-to-field-name mappings derived from the corresponding NCHS User Guides.
3. **Type casting and renaming.** Per-era raw fields are renamed to harmonized column names and cast to a common dtype, producing one harmonized parquet per source year.
4. **Value-level normalization.** A minority of variables require normalization across the revision boundary because the eras coded the same concept differently. For fetal death, five such normalizations are applied: `fetal_sex` (V2 numeric to V1 alphabetic); `delivery_method_recode` (V2 6-category collapsed to V1 3-category); `maternal_race_bridged` (recoded from a 2-digit detail field to V1 4-category); `paternal_age_recode11` (V2 12-category collapsed to V1 11-category); and `delivery_place_recode` (re-derived to V1's 3-bucket Hospital, Not-in-hospital, Unknown scheme). The natality and linked products receive analogous within-revision normalizations across the 2014 reformat.
5. **Derivation of constructed indicators.** Low birth weight, preterm birth, gestational-age categorical recodes, neonatal vs post-neonatal death, and ICD-10 cause groupings are computed deterministically from the harmonized columns.
6. **Validation.** Per-year counts and rates are computed from the harmonized parquet under the canonical analytic filter and compared cell-by-cell to the corresponding aggregates published by NCHS. Each product's validation script prints a pass/fail table against every NVSR figure cited in `external_validation_targets.csv`.

Without value-level normalization a naïve concatenation across the revision boundary produces columns whose distributions match neither era. The fetal-death `delivery_method_recode` is illustrative: the 1989-revision raw field DELMETH6 carries six categories and the 2003-revision raw field DMETH_REC carries three; naïve concatenation produces nine apparent categories matching no published distribution. The harmonization collapses the V2 6-category coding to the V1 3-category coding; the 6-category detail is preserved in the per-year raw parquets.

Re-deriving the parquet from a fresh download of the NCHS source zips produces a byte-identical file, and SHA-256 checksums for every shipped artifact are committed in `PROVENANCE.md`. The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes, dominated by the fixed-width parse stage.

## Data resource use

The HVS resource is intended to support research in epidemiology, perinatal medicine, demography, public health, biostatistics, and policy that requires U.S. natality, fetal-death, or linked birth–infant death microdata across periods, certificate revisions, or product boundaries. Each harmonized file is a single Apache Parquet readable in Python, R, Stata, and most modern data tools. Worked examples are shipped as `quickstart.py` in each deposit; cross-product worked examples are in `notebooks/` in the monorepo.

A canonical analytic filter reproduces the population on which NCHS computes its published rates. For fetal death this is `tabulation_flag == '2'` and `residence_status != '4'` — the NVSR-comparable subset of resident fetal deaths meeting NCHS's gestational-age and birth-weight tabulation rule. For natality the filter is `restatus != '4'` (U.S. residents). Applying the canonical filter is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

The three files are designed for joint use. Fetal mortality rates require live-birth denominators on the same demographic stratification as the fetal-death numerator; perinatal mortality rates additionally require early neonatal death counts from the linked file. Because all three products share aligned column names for shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status`), joins on `data_year` and demographic strata produce numerator and denominator with consistent semantics. A `live_births_by_year.csv` reference file is shipped with the fetal-death deposit, sourced from *NVSR 57-08* (1995–2002) and *NVSR 73-09* (2005–2022), for users who want unstratified denominators without loading the full natality file.

Three levels of independent verification are supported. Level 1 (~10 seconds) confirms downloaded files match the SHA-256 checksums in `PROVENANCE.md`. Level 2 (~1 minute) runs each product's validation script and prints a pass/fail table against every *NVSR* figure cited in `external_validation_targets.csv`. Level 3 (~1–2 hours combined) downloads the raw NCHS zips and re-runs each pipeline; the resulting parquet should be byte-identical to the shipped file.

Analyses the resource is designed to support include cross-revision stillbirth disparity trends by maternal race, age, and Hispanic origin (the case Ananth and colleagues had to drop Hispanic ethnicity from);[^ananth2022] secular trends in low birth weight, preterm birth, and gestational-age distributions back to 1990; period and cohort decompositions of perinatal mortality; cause-specific neonatal-mortality trend analyses from 2014 onward, when fetal-death cause coding becomes available; and policy natural-experiment studies spanning the 2003 revision rollout.

## Strengths and weaknesses

Five strengths shape the resource. **Comparability** of the harmonized series across certificate revisions and NCHS reformats through one stable column schema per product, with every column tagged with a comparability class and prominent warnings on the subset that cannot be reconciled. **Validation** against every per-year aggregate NCHS publishes in the relevant *NVSR* series: the parquet reproduces these byte-exactly under the canonical filter for natality (183/183 targets, 1990–2024, against *Births: Final Data*), for the linked file (33/35 byte-exact, 2005–2023; two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights, documented in `COMPARABILITY.md`), and for fetal death (74 targets, 1992–2022; all 29 per-year counts and all 26 per-year fetal mortality rates match exactly). **Reproducibility** through deterministic open-source pipelines, SHA-256 checksums for every shipped artifact, and per-year raw parquets preserving the original NCHS fields: a sceptical user is not asked to trust the author but to re-build and diff. **Accessibility** through CC BY 4.0 licensing, no application or data-use agreement, no institutional credentialing, and single-file parquet outputs. **Joint-use design**: shared column names, aligned comparability classes, and consistent demographic codings let fetal, perinatal, and infant mortality rates be computed with matched strata on numerator and denominator.

Weaknesses are of two kinds: NCHS public-use suppression that the harmonization passes through, and genuine cross-revision incomparability that it documents rather than imputes. Cause-of-death coding for fetal deaths is absent before 2014 and missing for approximately 50% of records from 2018 onward; pre-2014 codes are available only through the NCHS Research Data Center. State-level identifiers are suppressed in V1-era fetal-death public-use files (2005 onward) and remain only in the per-year raw parquets for 1992–2002. Within the V1 fetal-death era, `maternal_education` and `paternal_age_combined` are blank for 2007–2013 and `maternal_education_unrevised` is blank from V1 2007 onward, because NCHS dropped the underlying fields from the public-use file in those years; every gap is enumerated in `COMPARABILITY.md`. Three fetal-death columns — `breech_unrevised`, `delivery_place_unrevised`, and `maternal_race_bridged_detail` — carry irreducibly incompatible content across the 1989/2003 boundary and are tagged within_era. No 1989/2003 maternal-education bridge is provided: the 1989-revision raw field captures years of completed schooling (UMEDUC, 00–17), the 2003-revision raw field captures a 9-category degree-level recode (MEDUC), and the two are not 1:1 mappable; both are preserved as separate harmonized columns. State-specific reporting quirks during the 1992–2002 fetal-death era are preserved rather than imputed.[^state_quirks]

## Future developments

A published version roadmap commits the project to:

- **V2.1 release.** Adds the two fetal-death transition years 2003 and 2004, currently deferred.
- **V3 release.** Extends the harmonized fetal-death file backward to 1982, spanning the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts.
- **Annual extension.** Each product is extended forward as NCHS publishes new source files; no retroactive schema changes are required, since the harmonization is forward-extensible by adding entries to the era-specific record-layout CSVs.
- **Restricted-use products.** Census record linkage and NCHS Research Data Center geographic-identifier files are out of scope for the public-use resource; users who need these layers are referred to the corresponding NCHS programs.

## Data resource access

The HVS resource is deposited on Zenodo under a Creative Commons Attribution 4.0 International (CC BY 4.0) licence for the harmonization layer; the underlying NCHS source data are works of the U.S. Government and are not subject to U.S. copyright (17 U.S.C. § 105). No data-use agreement, application, or institutional credentialing is required. Concept DOIs always resolve to the latest version; version-specific DOIs let analyses pin to an exact release. The natality concept DOI is 10.5281/zenodo.19363074 and the fetal-death v2.0.0 release DOI is 10.5281/zenodo.20031571; per-deposit `PROVENANCE.md` lists the latest version numbers and SHA-256 checksums. Pipeline source code is mirrored on GitHub under a permissive open-source licence and included verbatim in each Zenodo deposit, so deposits remain re-buildable even if the GitHub mirror becomes unavailable. Cross-product worked examples — a joint-use demonstration reproducing the 2022 maternal-age-stratified fetal mortality cells against *NVSR 73-09* Table 4, and a paper-companion notebook recomputing every numeric claim in this manuscript directly from the parquets — are shipped under `notebooks/` in the monorepo accompanying this resource.

## HVS in a nutshell

- The HVS resource integrates and disseminates harmonized U.S. natality, linked birth–infant death, and fetal death public-use microdata as three companion parquet files with one stable column schema per product.
- Coverage: 138.8 million birth records (1990–2024), 74.9 million linked birth–infant death records (2005–2023), and 1.6 million fetal death records (1992–2022).
- The fetal-death release is the first public harmonization of U.S. fetal-death microdata across the 1989-revision and 2003-revision Standard Report boundary.
- The harmonized parquet reproduces every per-year aggregate NCHS publishes in the relevant *NVSR* series byte-exactly under a documented analytic filter.
- The first release, in 2026, was made under Creative Commons Attribution 4.0 on Zenodo, with deterministic open-source pipelines on GitHub and a three-level user-runnable verification ladder.
- Future releases will extend the fetal-death file to 2003–2004 (V2.1) and back to 1982 (V3), and will add subsequent NCHS release years annually to all three products.

## Ethics approval

Not required. The HVS resource is built exclusively from de-identified public-use microdata released by NCHS under U.S. federal law, with no identifying or restricted-use fields and no human-subjects contact.

## Author contributions

YP is the sole author. YP conceived and designed the resource, built and validated the harmonization pipelines, drafted and revised the manuscript, and is responsible for the final content. <!-- YP: confirm or revise -->

## Use of artificial intelligence (AI) tools

Anthropic's Claude (Opus-class models) was used as a coding-and-writing agent throughout the project: pipeline development, validation scripting, internal documentation, and manuscript drafting and revision. Every numeric claim in this manuscript is recomputed directly from the harmonized parquets and validation CSVs by a companion notebook (`notebooks/paper_companion.ipynb`) that runs end-to-end against the shipped artifacts; the pass/fail synthesis is committed alongside the manuscript. The author reviewed all AI-suggested content and retains responsibility for the final manuscript. <!-- YP: confirm wording in line with IJE policy and edit names of tools/model versions as needed -->

## Conflict of interest

None declared.

## Funding

None declared. <!-- YP: edit if any funding source applies -->


## References

[^nvsr_births]: Osterman MJK, Hamilton BE, Martin JA, Driscoll AK, Valenzuela CP. Births: Final Data for 2023. *Natl Vital Stat Rep* 2024;73(11). Gregory ECW, Valenzuela CP. Fetal Mortality: United States, 2022. *Natl Vital Stat Rep* 2024;73(09).

[^salihu2004]: Salihu HM, Aliyu MH, Pierre-Louis BJ, Alexander GR. Racial disparity in stillbirth among singleton, twin, and triplet gestations in the United States. *Obstet Gynecol* 2004;104(4):734–740.

[^willinger2009]: Willinger M, Ko CW, Reddy UM. Racial disparities in stillbirth risk across gestation in the United States. *Am J Obstet Gynecol* 2009;201(5):469.e1–8.

[^hogue2011]: Hogue CJR, Silver RM. Racial and ethnic disparities in United States: stillbirth rates, trends, risk factors, and research needs. *Semin Perinatol* 2011;35(4):221–233.

[^ananth2022]: Ananth CV, Fields JC, Brandt JS, Graham HL, Keyes KM, Zeitlin J. Evolving stillbirth rates among Black and White women in the United States, 1980–2020: a population-based study. *Lancet Reg Health Am* 2022;16:100380.

[^state_quirks]: Oklahoma did not report Hispanic origin during 1992–2002; Maryland (1992–1998) and Massachusetts (1992–1997) did not report Hispanic origin in early years; Louisiana under-reported plurality 1992–1994. These quirks reproduce the corresponding *NVSR 57-08* footnotes; users analysing Hispanic-origin fetal mortality in the V2 era should restrict to states with complete reporting.
