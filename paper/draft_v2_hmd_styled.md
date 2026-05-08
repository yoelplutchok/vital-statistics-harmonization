# Data Resource Profile: U.S. Harmonized Vital Statistics microdata, 1990–2024

The U.S. Harmonized Vital Statistics (HVS) microdata resource integrates and disseminates harmonized natality, linked birth–infant death, and fetal death public-use microdata released by the U.S. National Center for Health Statistics (NCHS), as three companion parquet files with one stable column schema per product. Coverage extends from 1990 forward and comprises 138,819,655 birth records (1990–2024), 74,943,824 linked birth–infant death records (2005–2023), and 1,634,195 fetal death records (1992–2022). The harmonization integrates source files spanning two U.S. Standard Certificate revisions (1989 and 2003), three within-revision NCHS layout reformats, and a state-by-state staggered adoption window in which a single annual file contains records following different schemas. Variable coding schemes are standardized across eras, without loss of detail, into one stable parquet column schema per product, and per-year raw parquets preserving every documented source field are also disseminated. The harmonized parquet reproduces every per-year aggregate published by NCHS in the relevant *National Vital Statistics Reports* (*NVSR*) series byte-exactly under a documented analytic filter. The resource is released under Creative Commons Attribution 4.0 on Zenodo, with deterministic open-source pipelines re-runnable end-to-end from the public NCHS source files in tens of minutes on a laptop, and with no application or data-use agreement required.

## Data resource basics

Over the past century, the U.S. National Vital Statistics System has counted every birth, fetal death, and infant death registered in the country—approximately 3.5 million live births, 20,000–30,000 fetal deaths, and 20,000 infant deaths each year.[^nvsr_births] Since 1933, these events have been compiled by the U.S. National Center for Health Statistics (NCHS), and since the early 1980s NCHS has released them as annual fixed-width public-use microdata files containing one record per event. The microdata underlie most U.S. perinatal-mortality and stillbirth trend studies, state-level disparity analyses with individual-level covariates, and age-period-cohort decompositions in the field.

Although these microdata are individually informative within a release year, they are difficult to use across years because the source layouts change. Field positions, code values, and variable inventories shift at three kinds of boundary: (i) the transition from the 1989 to the 2003 U.S. Standard Certificate, phased over 2003–2014 for natality and over 2005–2017 for the public-use V1 fetal-death window, with 100% A-version reporting reached in 2018; (ii) within-revision NCHS reformats, including a 2006 compression of the natality record length from 1500 to 775 bytes (with unrevised-only fields blanked from 2009 onward) and a 2014 reformat to a revised-only 1345-byte layout; and (iii) state-by-state staggered adoption of the 2003 revision, so that an annual file during the transition window contains records following different schemas depending on the state of registration. The same conceptual variable can occupy different byte positions, use different code values, or be absent entirely depending on year and state.

The field has adapted to these discontinuities by restricting analyses to single-revision windows. Salihu and colleagues studied racial disparities in stillbirth using 1995–1998 data, the four-year span chosen for 1989-revision uniformity.[^salihu2004] Willinger and colleagues used 2001–2002, the last two years of 1989-revision uniformity before the staggered 2003-revision rollout began.[^willinger2009] Hogue and Silver, surveying stillbirth disparities through 2005, were forced to operate on aggregate published rates rather than microdata.[^hogue2011] Ananth and colleagues' age-period-cohort analysis of stillbirth trends from 1980 to 2020 explicitly excluded Hispanic ethnicity because the variable "was only made available in the revised 2003 birth certificates".[^ananth2022] These restrictions reflect the state of the source files, not investigator preference.

Although NCHS itself publishes harmonized cross-revision tabulations in the *Births: Final Data* and *Fetal and Perinatal Mortality* *NVSR* series, those are aggregate tables. The microdata-level harmonization is performed by NCHS analysts inside the agency on a fixed tabulation grid, and only the published cells survive. To our knowledge, no public harmonized longitudinal microdata product has previously existed for U.S. natality, linked birth–infant death, or fetal death.

The U.S. Harmonized Vital Statistics (HVS) microdata resource fills this gap. The first release was in 2026. The resource is maintained by a single author, with releases versioned on Zenodo: concept DOIs always resolve to the latest version, and version-specific DOIs let analyses pin to an exact release. The pipelines are open-source on GitHub, included verbatim in each Zenodo deposit, and run end-to-end from the public NCHS source files in tens of minutes on a laptop.

## Data resource area and coverage

The HVS resource covers the United States from 1990 forward. The natality file contains 138,819,655 records covering 1990–2024 (84 columns), the linked birth–infant death file contains 74,943,824 records covering 2005–2023 (94 columns; denominator-plus cohort format 2005–2015, period-cohort merged format 2016–2023), and the harmonized fetal death file contains 1,634,195 records covering 1992–2022 (89 columns). Each product carries one stable column schema across all years it covers. Per-year raw parquets preserving every documented source field are also disseminated for users who need detail outside the harmonized schema.

The fetal-death years 2003 and 2004 use distinct transition layouts (1351 and 1501 bytes respectively, with mixed-revision content) and are deferred to a future release. Fetal-death years 1982–1991, spanning the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts, are deferred to a planned V3 release. The "1992–2002 uniform" framing for the fetal-death V2 era reflects empirical verification: byte-level comparison of 50 records by 197 fields by 10 years (98,500 raw-byte to parquet-cell comparisons) returned zero mismatches across 1993–2002, with 1992 verified separately.

The harmonization bridges five distinct era boundaries within the natality product, three within linked birth–infant death, and two within fetal death (Table 1). Within each era the source layout is uniform; at era boundaries record length, certificate revision, or both can change.

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

Each product ships one stable harmonized column schema, with per-era raw fields mapped to a common dtype, name, and code space. The natality file has 71 harmonized columns plus 13 derived analytic indicators (84 total); the linked birth–infant death file extends this with 7 additional death-side harmonized columns and 3 derived death-side indicators (94 total); the fetal death file has 73 harmonized columns plus 16 derived indicators (89 total). The full schema is shipped per product as a machine-readable CSV (`harmonized_schema.csv`) listing dtype, allowed values, coverage, comparability class, and source raw field for each era. The full per-era raw-field-to-harmonized-column mapping is shipped as `variable_crosswalk_working.csv` (Supplementary Table S1).

Harmonized measures are organized as follows:

- **Demographic measures.** Maternal age, paternal age, maternal and paternal race (bridged to four-category Census categories), Hispanic origin, marital status, educational attainment, and residence status (resident vs non-resident on the NVSR analytic filter).
- **Pregnancy measures.** Gestational age (best obstetric estimate plus last-menstrual-period derivation where available), plurality, prior live births, prior fetal deaths, prenatal-care utilization, and tobacco use during pregnancy.
- **Delivery measures.** Birth weight, delivery method, breech presentation, place of delivery, and birth attendant.
- **Infant outcome measures (linked file only).** Age at death, place of death, ICD-10 cause-of-death codes, and the NCHS-assigned record weight.
- **Fetal-death-specific measures.** Cause of fetal death (ICD-10 prefix groupings, fetal death 2014 onward only), autopsy status, and the NVSR tabulation flag indicating whether a record meets NCHS's gestational-age and birth-weight criteria for inclusion in published fetal-mortality counts.
- **Constructed analytic indicators.** Low birth weight, preterm birth, neonatal vs post-neonatal death (linked file), and ICD-10 cause groupings, computed deterministically from the harmonized columns.

Sentinel values (`gestational_age_combined=99`, `birthweight=9999`, `plurality=9`, etc.) are converted to NaN inside the derivation step before threshold comparisons, so constructed indicators correctly return missing for sentinel-coded records. The harmonized parent file retains raw sentinels.

### Comparability classification

Every harmonized column is tagged with one of four comparability classes: **full** (consistent across all years covered), **partial** (consistent within era; minor cross-era differences explicitly documented), **within_era** (incompatible content across eras; cross-era aggregation should not be performed), or **not_available** (era does not collect the field). The class is recorded in the schema CSV. Three fetal-death columns are tagged within_era because the underlying clinical concepts or code spaces differ across the revision boundary in ways that cannot be reconciled by value-level normalization: `breech_unrevised` (V2 "Breech/Malpresentation" is broader than V1 "Breech Delivery"); `delivery_place_unrevised` (V2 4-category PLDEL vs V1 5-category UBFACIL with non-overlapping codes 2 and 3); and `maternal_race_bridged_detail` (V2 1989-revision MRACE codes and V1 2003-revision MBRACE codes overlap numerically but encode different ethnic subgroups). All three are flagged with explicit warnings in the schema and codebook; users are referred to the per-year raw parquets when within-era detail is required.

## Methods

The HVS resource is produced through the following sequence of steps, executed for each of the three products by deterministic open-source pipelines committed to GitHub and re-runnable end-to-end from the public NCHS source files:

1. **Acquisition.** Annual fixed-width zips, User Guide PDFs, and *NVSR* reference reports are obtained from the NCHS public FTP server (`ftp.cdc.gov/pub/Health_Statistics/NCHS/`). Per-file SHA-256 checksums are recorded in each deposit's `file_inventory.csv`.
2. **Parsing.** Each annual file is parsed using era-specific record-layout CSVs (`record_layout_*.csv`) that encode byte-position-to-field-name mappings derived from the corresponding NCHS User Guide PDFs.
3. **Type casting and renaming.** Per-era raw fields are renamed to harmonized column names and cast to a common dtype, producing one harmonized parquet per source year.
4. **Value-level normalization.** A minority of variables require value-level normalization across the revision boundary because the eras coded the same concept differently. For fetal death, five such normalizations are applied: `fetal_sex` (V2 numeric 1/2/9 to V1 alphabetic M/F/U); `delivery_method_recode` (V2 6-category collapsed to V1 3-category); `maternal_race_bridged` (recoded from a 2-digit detail field to V1 4-category); `paternal_age_recode11` (V2 12-category collapsed to V1 11-category); and `delivery_place_recode` (re-derived from raw PLDEL to V1's 3-bucket Hospital, Not-in-hospital, Unknown scheme). The natality and linked products receive analogous within-revision normalizations across the 2014 reformat boundary.
5. **Derivation of constructed indicators.** Low birth weight, preterm birth, gestational-age categorical recodes, neonatal vs post-neonatal death, and ICD-10 cause groupings are computed deterministically from the harmonized columns.
6. **Validation.** Per-year counts and rates are computed from the harmonized parquet under the canonical analytic filter and compared cell-by-cell to the corresponding aggregates published by NCHS in the relevant *NVSR* series. Each product's validation script (`validate_external.py` for natality and linked birth–infant death; the V2 equivalent for fetal death) prints a pass/fail table against every NVSR figure cited in `external_validation_targets.csv`.

A naïve concatenation of source files across the revision boundary, without value-level normalization, would produce columns whose distributions match neither era. The fetal-death `delivery_method_recode` is illustrative: the 1989-revision raw field DELMETH6 carries six categories (vaginal-no-prior-Csection, vaginal-prior-Csection, primary-Csection, repeat-Csection, vaginal-unspecified, route-not-stated) while the 2003-revision raw field DMETH_REC carries three (vaginal, Csection, unknown). A naïve concatenation produces an output column with nine apparent categories, none of which match either era's published distributions. The harmonization collapses the V2 6-category coding to the V1 3-category coding at the harmonization step; the original 6-category detail is preserved in the per-year raw parquets for users who need it.

The pipeline is deterministic. Re-deriving the parquet from a fresh download of the NCHS source zips produces a byte-identical file, and SHA-256 checksums for every shipped artifact are committed in `PROVENANCE.md`. The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes on the same hardware, dominated by the fixed-width parse stage.

## Data resource use

The HVS resource is intended to support research in epidemiology, perinatal medicine, demography, public health, biostatistics, social science, and policy that requires U.S. natality, fetal-death, or linked birth–infant death microdata across periods, certificate revisions, or product boundaries. Each harmonized file is a single Apache Parquet file readable in Python (pandas, pyarrow, polars, DuckDB), R (`arrow`, `duckdb`), Stata (`haven` or recent native versions), and most modern data tools. Worked examples are shipped as `quickstart.py` in each deposit; analogous R examples are in the GitHub repositories' `notebooks/` directory.

A canonical analytic filter reproduces the population on which NCHS computes its published rates. For fetal death this is `tabulation_flag == '2'` and `residence_status != '4'`, the NVSR-comparable subset of resident fetal deaths whose gestational-age and birth-weight criteria meet NCHS's tabulation rule. For natality, the corresponding filter is `restatus != '4'` (U.S. residents). Convenience subsets matching these filters are pre-computed and shipped under `output/convenience/` in the natality deposit. Applying the canonical filter is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

The three files are designed for joint use. Fetal mortality rates require live-birth denominators on the same demographic stratification as the fetal-death numerator; perinatal mortality rates additionally require early neonatal death counts from the linked file. Because all three products share aligned column names for shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status`), joins on `data_year` and demographic strata produce numerator and denominator with consistent semantics. A `live_births_by_year.csv` reference file is shipped with the fetal-death deposit, sourced from *NVSR 57-08* (1995–2002) and *NVSR 73-09* (2005–2022), for users who want unstratified denominators without loading the full natality file.

Three levels of independent verification are supported. Level 1, in approximately ten seconds, confirms that downloaded files match what was released using the SHA-256 checksums in `PROVENANCE.md`. Level 2, in approximately one minute, runs the validation script, which loads the shipped parquet, recomputes per-year counts and rates with the canonical analytic filter, and prints a pass/fail table against every *NVSR* figure cited in `external_validation_targets.csv`. Level 3, in approximately one to two hours for all three products combined, downloads the raw NCHS zips listed in `file_inventory.csv` and re-runs each product's pipeline; the resulting parquet should be byte-identical to the shipped file.

Among the analyses the resource is designed to support are cross-revision stillbirth disparity trends by maternal race, age, and Hispanic origin (the case Ananth and colleagues had to drop Hispanic ethnicity from);[^ananth2022] secular trends in low birth weight, preterm birth, and gestational-age distributions back to 1990; period and cohort decompositions of perinatal mortality using the joint numerator–denominator structure; cause-specific neonatal-mortality trend analyses from 2014 onward, when fetal-death cause coding becomes available; and policy natural-experiment studies that need pre/post observation windows spanning the 2003 revision rollout.

## Strengths and weaknesses

The main strengths of the HVS resource result from its four guiding principles:

- **Comparability** of the harmonized series across certificate revisions and NCHS layout reformats through one stable column schema per product, with explicit comparability classification of every harmonized column and prominent warnings on the small subset that cannot be reconciled across the revision boundary.
- **Validation** against every per-year aggregate NCHS publishes in the relevant *NVSR* series. The harmonized parquet reproduces these aggregates byte-exactly under the canonical analytic filter for natality (183 of 183 targets, 1990–2024, against *Births: Final Data*); for the linked birth–infant death file (33 of 35 targets, 2005–2023, against the NCHS Linked User Guides; two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights, documented in `COMPARABILITY.md` and not a parsing artifact); and for fetal death (74 targets, 1992–2022, against *NVSR 73-09* for 2005–2022, *NVSR 57-08* Tables A and B for 1995–2002, and the NCHS Fetal Death User Guide control counts for 1992–1994; all 29 per-year counts and all 26 per-year fetal mortality rates match exactly).
- **Reproducibility** through deterministic open-source pipelines, SHA-256 checksums for every shipped artifact, and provision of original raw input data as per-year parquets. A sceptical user is not asked to trust the author but to re-build the artifact from the public NCHS source files and diff it against the shipped file.
- **Accessibility** through Creative Commons Attribution 4.0 licensing, no application or data-use agreement, no institutional credentialing requirement, and single-file parquet outputs readable in any modern data-analysis tool.

A fifth strength follows from these four. The three companion products are designed for joint use: column names, comparability classes, and demographic codings align across natality, linked birth–infant death, and fetal death, so that fetal mortality, perinatal mortality, and infant mortality rates can be computed with consistent demographic stratification on numerator and denominator.

One of the main weaknesses of the HVS resource is a consequence of NCHS's own public-use suppression policies, which the harmonization passes through faithfully rather than imputing. Cause-of-death coding for fetal deaths is not present in the public-use file before 2014, and approximately 50% of records lack cause data for 2018 onward; pre-2014 ICD codes are only available through the NCHS Research Data Center under restricted-use application. State-level geographic identifiers are suppressed in V1-era fetal-death public-use files (2005 onward); state codes (`STATEFET`, `STATERES`, `STOCCFIP`) remain in the per-year raw parquets for 1992–2002 only. Note that for the V1 fetal-death era (2005 onward), state-stratified analyses are not supported by the public-use file at all, regardless of harmonization.

A second weakness is harmonization-internal. Three fetal-death columns carry incompatible content across the 1989/2003 revision boundary: `breech_unrevised`, `delivery_place_unrevised`, and `maternal_race_bridged_detail` store semantically different content across eras and are tagged within_era in the schema. No 1989/2003 maternal-education bridge is provided, because the 1989-revision raw field captures years of completed schooling (UMEDUC, 00–17) while the 2003-revision raw field captures a 9-category degree-level recode (MEDUC); the two concepts are not 1:1 mappable, and both are preserved in the harmonized schema as `maternal_education_unrevised` and `maternal_education` respectively, leaving analysts to apply their own modelling choices.

A third weakness is NCHS public-use field-availability gaps within the V1 era, which the harmonization passes through faithfully. The revised 9-category `maternal_education` recode is blank for V1 years 2007–2013, even for records following the revised certificate; `paternal_age_combined` is similarly blank for 2007–2013; and `maternal_education_unrevised` is blank for V1 2007 onward because NCHS dropped the unrevised field from the public-use file from that year. Every gap is enumerated in `COMPARABILITY.md` with the NCHS source confirming the limitation; the gaps are not parsing artifacts and cannot be filled from the public-use files.

Finally, state-specific reporting quirks during the 1992–2002 fetal-death era are preserved rather than imputed. Oklahoma did not report Hispanic origin during this period; Maryland (1992–1998) and Massachusetts (1992–1997) did not report Hispanic origin in early years; Louisiana under-reported plurality 1992–1994. These quirks reproduce the corresponding *NVSR 57-08* footnotes; users analysing Hispanic-origin fetal mortality in the V2 era should restrict to states with complete reporting.

## Future developments

A published version roadmap commits the project to the following extensions:

- **V2.1 release.** Adds the two fetal-death transition years 2003 and 2004 to the harmonized fetal-death file, which is currently 1992–2022 with these two years deferred.
- **V3 release.** Extends the harmonized fetal-death file backward to 1982, spanning the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts.
- **Annual extension.** Each product is extended forward as NCHS publishes the corresponding source files. No retroactive schema changes are required for newly added years; the harmonization scheme is forward-extensible by adding entries to the era-specific record-layout CSVs.
- **Linked file extension.** As NCHS releases period and cohort linked birth–infant death files for 2024 forward, those years will be added to the harmonized linked file.
- **Restricted-use products.** Census record linkage and the NCHS Research Data Center geographic-identifier files are out of scope for the public-use HVS resource. Users who need these layers are referred to the corresponding NCHS programs.

## Data resource access

The HVS resource is deposited on Zenodo under a Creative Commons Attribution 4.0 International (CC BY 4.0) licence for the harmonization layer. The underlying NCHS source data are works of the U.S. Government and are not subject to U.S. copyright (17 U.S.C. § 105). No data-use agreement, application, or institutional credentialing is required. Concept DOIs always resolve to the latest version; version-specific DOIs let analyses pin to an exact release. The natality concept DOI is 10.5281/zenodo.19363074 and the fetal-death v2.0.0 release DOI is 10.5281/zenodo.20031571. The latest version numbers and individual file SHA-256 checksums are recorded in each deposit's `PROVENANCE.md`. Pipeline source code is mirrored on GitHub under a permissive open-source licence and is included verbatim in each Zenodo deposit, so deposits remain re-buildable even if the GitHub mirror becomes unavailable.

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

[To be completed.]

## Use of artificial intelligence (AI) tools

[To be completed in line with IJE policy: disclose any AI-tool use in pipeline development, documentation drafting, or manuscript preparation.]

## Conflict of interest

None declared.

## Funding

[To be completed.]

## References

[^nvsr_births]: Osterman MJK, Hamilton BE, Martin JA, Driscoll AK, Valenzuela CP. Births: Final Data for 2023. *Natl Vital Stat Rep* 2024;73(11). Gregory ECW, Valenzuela CP. Fetal Mortality: United States, 2022. *Natl Vital Stat Rep* 2024;73(09).

[^salihu2004]: Salihu HM, Aliyu MH, Pierre-Louis BJ, Alexander GR. Racial disparity in stillbirth among singleton, twin, and triplet gestations in the United States. *Obstet Gynecol* 2004;104(4):734–740.

[^willinger2009]: Willinger M, Ko CW, Reddy UM. Racial disparities in stillbirth risk across gestation in the United States. *Am J Obstet Gynecol* 2009;201(5):469.e1–8.

[^hogue2011]: Hogue CJR, Silver RM. Racial and ethnic disparities in United States: stillbirth rates, trends, risk factors, and research needs. *Semin Perinatol* 2011;35(4):221–233.

[^ananth2022]: Ananth CV, Fields JC, Brandt JS, Graham HL, Keyes KM, Zeitlin J. Evolving stillbirth rates among Black and White women in the United States, 1980–2020: a population-based study. *Lancet Reg Health Am* 2022;16:100380.
