# Data Resource Profile: U.S. Harmonized Vital Statistics microdata, 1990–2024

The U.S. Harmonized Vital Statistics (HVS) microdata resource integrates and disseminates harmonized natality, linked birth–infant death, and fetal death public-use microdata released by the U.S. National Center for Health Statistics (NCHS). Since the first release in 2026, HVS has assembled the largest publicly available cross-revision harmonized U.S. perinatal microdata collection: 138,819,655 birth records (1990–2024), 74,943,824 linked birth–infant death records (2005–2023), and 1,634,195 fetal death records (1992–2022). The harmonization integrates source files spanning two U.S. Standard Certificate revisions (1989 and 2003), three within-revision NCHS layout reformats, and a state-by-state staggered adoption window in which a single annual file contains records following different schemas. Variable coding schemes are standardized across eras, without loss of detail, into one stable parquet column schema per product. Per-year raw parquets preserving every documented source field are also disseminated. The harmonized parquet reproduces every per-year aggregate published by NCHS in the relevant *National Vital Statistics Reports* series byte-exactly under a documented analytic filter. Pipelines are deterministic, open-source, and re-runnable end-to-end from the public NCHS source files in tens of minutes on a laptop. The data are released under Creative Commons Attribution 4.0 on Zenodo with no application or data-use agreement required.

## Data resource basics

The U.S. Harmonized Vital Statistics (HVS) microdata resource integrates and disseminates harmonized natality, linked birth–infant death, and fetal death public-use microdata released by NCHS, packaged as one stable parquet schema per product. Since the first release in 2026, HVS has assembled the largest publicly available cross-revision harmonized U.S. perinatal microdata collection. As of the v2.0 release, the natality file contains 138,819,655 records covering 1990–2024 (84 columns), the linked birth–infant death file contains 74,943,824 records covering 2005–2023 (94 columns), and the fetal death file contains 1,634,195 records covering 1992–2022 (89 columns; 2003 and 2004 are deferred to a future release because of distinct transition-year layouts). Each product carries one stable column schema across all years it covers, and per-year raw parquets preserving every documented source field are also disseminated for users who need detail outside the harmonized schema.

Approximately three and a half million live births, twenty thousand to thirty thousand fetal deaths, and twenty thousand infant deaths are registered each year in the United States.[^nvsr_births] These events have been counted in the National Vital Statistics System since 1933 and are released by NCHS as annual public-use microdata files containing one record per event. The microdata underlie most U.S. perinatal-mortality and stillbirth trend studies, state-level disparity analyses with individual-level covariates, and age-period-cohort decompositions in the field.

The files are difficult to use across years. NCHS releases them as fixed-width ASCII inside annual zips, with field positions, code values, and variable inventories that change at three kinds of boundary: (i) the transition from the 1989 to the 2003 U.S. Standard Certificate, phased over 2003–2014 for natality and over 2005–2017 for the public-use V1 fetal-death window, with 100% A-version reporting reached in 2018; (ii) within-revision NCHS reformats, including a 2006 compression of the natality record length from 1500 to 775 bytes (with unrevised-only fields blanked from 2009 onward) and a 2014 reformat to a revised-only 1345-byte layout; and (iii) state-by-state staggered adoption of the 2003 revision, so that a given annual file during the transition window contains records following different schemas depending on the state of registration. The same conceptual variable can occupy different byte positions, use different code values, or be absent entirely depending on year and state.

The field has adapted to these discontinuities by restricting analyses to single-revision windows. Salihu and colleagues studied racial disparities in stillbirth using 1995–1998 data, the four-year span chosen for 1989-revision uniformity.[^salihu2004] Willinger and colleagues used 2001–2002, the last two years of 1989-revision uniformity before the staggered 2003-revision rollout began.[^willinger2009] Hogue and Silver, surveying stillbirth disparities through 2005, were forced to operate on aggregate published rates rather than microdata.[^hogue2011] Ananth and colleagues' age-period-cohort analysis of stillbirth trends from 1980 to 2020 explicitly excluded Hispanic ethnicity because the variable "was only made available in the revised 2003 birth certificates".[^ananth2022] These restrictions reflect the state of the source files, not investigator preference.

NCHS itself publishes harmonized cross-revision tabulations in the *Births: Final Data* and *Fetal and Perinatal Mortality* NVSR series, but those are aggregate tables, not microdata. Harmonization is performed by NCHS analysts inside the agency on a fixed tabulation grid, and the published cells are what survives. To our knowledge, no public harmonized longitudinal microdata product has previously existed for U.S. natality, linked birth–infant death, or fetal death. The HVS resource fills this gap.

The resource is maintained by a single author. Releases are versioned on Zenodo: concept DOIs resolve to the latest version, and version-specific DOIs let analyses pin to an exact release. The pipelines are open-source on GitHub, included verbatim in each Zenodo deposit, and run end-to-end from the public NCHS source files in tens of minutes on a laptop.

## Data collected

As of the v2.0 release (2026), the harmonized natality file contains 138,819,655 records covering 1990 through 2024, the harmonized linked birth–infant death file contains 74,943,824 records covering 2005 through 2023 (denominator-plus cohort format 2005–2015; period-cohort merged format 2016–2023), and the harmonized fetal death file contains 1,634,195 records covering 1992 through 2022, excluding the two transition years 2003 and 2004. All source files were obtained from the NCHS public FTP server (`ftp.cdc.gov/pub/Health_Statistics/NCHS/`); the corresponding User Guide PDFs and *NVSR* reference reports came from the same server and are committed as project-internal documentation. Per-file inventories with SHA-256 checksums are shipped in each deposit's `file_inventory.csv`. Future annual releases will extend each product as NCHS publishes the corresponding source files.

### Era boundaries

The harmonization bridges five distinct era boundaries within the natality product, three within linked birth–infant death, and two within fetal death (Table 1). Within each era the source layout is uniform; at era boundaries record length, certificate revision, or both can change. The fetal-death "1992–2002 uniform" framing reflects empirical verification: byte-level comparison of 50 records by 197 fields by 10 years (98,500 raw-byte to parquet-cell comparisons) returned zero mismatches across 1993–2002, with 1992 verified separately.

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

### Variable harmonization

Each product maps its era-specific raw fields to one stable column schema. The natality file has 71 harmonized columns plus 13 derived analytic indicators (84 total); the linked birth–infant death file extends this with 7 additional death-side harmonized columns and 3 derived death-side indicators (94 total); the fetal death file has 73 harmonized columns plus 16 derived indicators (89 total). The full schema is shipped per product as a machine-readable CSV (`harmonized_schema.csv`) with one row per column listing dtype, allowed values, coverage, and the source raw field for each era. The full per-era raw-field-to-harmonized-column mapping is shipped as `variable_crosswalk_working.csv` (Supplementary Table S1).

For most variables, era-specific raw fields use compatible code values and harmonization reduces to renaming and type-casting. A minority of variables require value-level normalization because the eras coded the same concept differently. The fetal-death `delivery_method_recode` is illustrative. The 1989-revision raw field DELMETH6 carries six categories (vaginal-no-prior-Csection, vaginal-prior-Csection, primary-Csection, repeat-Csection, vaginal-unspecified, route-not-stated). The 2003-revision raw field DMETH_REC carries three (vaginal, Csection, unknown). A naïve concatenation across the revision boundary produces an output column with nine apparent categories, none of which match either era's published distributions. The harmonization collapses the V2 6-category coding to the V1 3-category coding inside the harmonization step; the original 6-category detail is preserved in the per-year raw parquets for users who need it.

The fetal-death release applies five such value-level normalizations across the revision boundary: `fetal_sex` (V2 numeric 1/2/9 to V1 alphabetic M/F/U); `delivery_method_recode` (as above); `maternal_race_bridged` (crosswalk switched from a 3-category to a 2-digit detail field, then recoded to V1 4-category); `paternal_age_recode11` (V2 12-category collapsed to V1 11-category); and `delivery_place_recode` (re-derived from raw PLDEL to recover V1's 3-bucket Hospital, Not-in-hospital, Unknown scheme). The natality and linked products receive analogous within-revision normalizations across the 2014 reformat boundary; these are documented in COMPARABILITY.md and the schema's `comparability_class` column.

### Comparability classification

Every harmonized column is tagged with one of four comparability classes: full (consistent across all years covered), partial (consistent within era; minor cross-era differences explicitly documented), within_era (incompatible content across eras; cross-era aggregation should not be performed), or not_available (era does not collect the field). The class is recorded in the schema CSV. Three fetal-death columns are tagged within_era because the underlying clinical concepts or code spaces differ across the revision boundary in ways that cannot be reconciled by value-level normalization: `breech_unrevised` (V2 "Breech/Malpresentation", broader, vs V1 "Breech Delivery", narrower); `delivery_place_unrevised` (V2 4-category PLDEL vs V1 5-category UBFACIL with non-overlapping codes 2 and 3); and `maternal_race_bridged_detail` (V2 1989-revision MRACE codes and V1 2003-revision MBRACE codes overlap numerically but encode different ethnic subgroups). Two of the three carry an `_unrevised` suffix in the column name; all three are flagged with explicit warnings in the schema and codebook. Cross-era groupby operations on these columns will execute, but the result is not interpretable; users are referred to the per-year raw parquets when within-era detail is required.

### Constructed variables

Each product ships a small derived layer of analytic indicators that almost every consumer recomputes anyway: low birth weight, preterm birth, maternal-age and gestational-age categorical recodes, neonatal versus post-neonatal death (linked file), and ICD-10-prefix cause groupings (fetal death 2014 onward). Constructed variables are computed deterministically from the harmonized columns; users are free to recompute from primitives. Sentinel values (`gestational_age_combined=99`, `birthweight=9999`, `plurality=9`, etc.) are converted to NaN inside the derivation step before threshold comparisons, so constructed variables correctly return missing for sentinel-coded records. The harmonized parent file retains raw sentinels.

### Out of scope

The following are outside the current release. Cause-of-death coding for fetal deaths is not present in the public-use file before 2014, and approximately 50% of records lack cause data for 2018 onward; pre-2014 ICD codes are only available through the NCHS Research Data Center under restricted-use application. State-level geographic identifiers are suppressed in V1-era fetal-death public-use files (2005 onward) and are absent from the harmonized fetal-death file in those years; for 1992–2002 they remain in the per-year raw parquets. The 2003 and 2004 fetal-death transition years are deferred to a planned V2.1 release. Fetal-death years 1982–1991, spanning the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts, are deferred to a planned V3 release. Restricted-use products (Census record linkage; the NCHS Research Data Center geographic-identifier files) are out of scope.

## Data resource use

The HVS resource is designed to serve researchers in epidemiology, perinatal medicine, demography, public health, biostatistics, social science, and policy who work with U.S. natality, fetal-death, or linked birth–infant death microdata across periods, certificate revisions, or product boundaries. Each harmonized file is a single Apache Parquet file readable in Python (pandas, pyarrow, polars, DuckDB), R (`arrow`, `duckdb`), Stata (`haven` or recent native versions), and most modern data tools. Worked examples in Python are shipped as `quickstart.py` in each deposit; analogous R examples are in the GitHub repositories' `notebooks/` directory. A harmonized file can be loaded in two lines of Python:

```python
import pandas as pd
df = pd.read_parquet("fetal_death_derived.parquet")
nvsr = df[(df["tabulation_flag"] == "2") & (df["residence_status"] != "4")]
```

### Standard analytic filters

Each product has one canonical analytic filter that reproduces the population on which NCHS computes its published rates. For fetal death this is `tabulation_flag == '2'` and `residence_status != '4'`, the NVSR-comparable subset of resident fetal deaths whose gestational age and birth-weight criteria meet NCHS's tabulation rule. For natality, the corresponding filter is `restatus != '4'` (U.S. residents). Convenience subsets matching these filters are pre-computed and shipped under `output/convenience/` in the natality deposit; the fetal-death deposit applies the filter on demand inside the validation scripts. Applying the canonical filter is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

### Joining the three products

The three files are designed to be used jointly. Fetal mortality rates require live-birth denominators on the same demographic stratification as the fetal-death numerator; perinatal mortality rates additionally require early neonatal death counts from the linked file. Because all three products share aligned column names for shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status`), joins on `data_year` and demographic strata produce numerator and denominator with consistent semantics. A `live_births_by_year.csv` reference file is also shipped with the fetal-death deposit, sourced from NVSR 57-08 (1995–2002) and NVSR 73-09 (2005–2022), for users who want unstratified denominators without loading the full natality file. Denominators for fetal-death years 1992–1994 and 2003–2004 are not included in the convenience CSV; both can be derived from the natality file directly.

### Reader-runnable verification

Three levels of independent verification are supported. Level 1, in approximately ten seconds, confirms that downloaded files match what was released using the SHA-256 checksums in `PROVENANCE.md`. Level 2, in approximately one minute, runs the validation script (`validate_external.py`, and its V2 equivalent for fetal death), which loads the shipped parquet, recomputes per-year counts and rates with the canonical analytic filter, and prints a pass/fail table against every NVSR figure cited in `external_validation_targets.csv`. Level 3, in approximately one to two hours for all three products combined, downloads the raw NCHS zips listed in `file_inventory.csv` and re-runs each product's pipeline; the resulting parquet should be byte-identical to the shipped file. The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes on the same hardware, dominated by the fixed-width parse stage.

### Example research applications

Among the analyses the resource supports are cross-revision stillbirth disparity trends by maternal race, age, and Hispanic origin (the case Ananth and colleagues had to drop Hispanic ethnicity from)[^ananth2022]; secular trends in low birth weight, preterm birth, and gestational-age distributions back to 1990; period and cohort decompositions of perinatal mortality using the joint numerator–denominator structure; cause-specific neonatal-mortality trend analyses from 2014 onward, when fetal-death cause coding becomes available; and policy natural-experiment studies that need pre/post observation windows spanning the 2003 revision rollout.

## Strengths and weaknesses

The principal contributions of the HVS resource are: (i) freely distributing harmonized longitudinal microdata for U.S. natality, linked birth–infant death, and fetal death across periods and certificate revisions that have previously forced researchers into single-revision windows; (ii) consistently naming and coding variables across eras, without loss of detail, to facilitate analyses across time and across the three products; and (iii) reproducing every per-year aggregate published by NCHS in the relevant *NVSR* series byte-exactly under a documented analytic filter.

Validation rests on the *NVSR* series, which NCHS produces by harmonizing the same source files internally on a fixed tabulation grid and publishing aggregate rates. The harmonized parquet reproduces these aggregates byte-exactly under the canonical analytic filter for natality (183 of 183 targets, 1990–2024, against *Births: Final Data*); for the linked birth–infant death file (33 of 35 targets, 2005–2023, against the NCHS Linked User Guides; two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights, documented in COMPARABILITY.md and not a parsing artifact); and for fetal death (74 targets, 1992–2022, against *NVSR 73-09* for 2005–2022, *NVSR 57-08* Tables A and B for 1995–2002, and the NCHS Fetal Death User Guide control counts for 1992–1994; all 29 per-year counts and all 26 per-year fetal mortality rates match the published figures exactly). The 19 detail-cell tabulations checked against *NVSR 73-09* Tables A, 4, 1, and 8 include 13 byte-exact matches and six documented differences: four early/late gestational-age cells where NVSR redistributes records with unknown gestational age proportionally between strata while the harmonization preserves them in a separate unknown bin, and two cause-of-death cells that compare a 43-state NVSR reporting area against the harmonization's all-states totals. None of the documented differences are byte-level mismatches in the harmonized data.

A second strength is bit-reproducibility from public sources. The pipeline is deterministic; re-deriving the parquet from a fresh download of the NCHS source zips produces a byte-identical file, and SHA-256 checksums for every shipped artifact are committed in `PROVENANCE.md`. This distinguishes the HVS resource from products released without re-buildable pipelines: a sceptical user is not asked to trust the author but to re-build the artifact and diff it against the shipped file. A third strength is joint-use design: column names, comparability classes, and demographic codings align across natality, linked birth–infant death, and fetal death, so fetal mortality, perinatal mortality, and infant mortality rates can be computed with consistent demographic stratification on numerator and denominator. The pipeline source is committed to GitHub under a permissive licence; every era-specific field mapping is in `field_specs.py` and the corresponding raw-field-position CSVs (`record_layout_*.csv`); a researcher who wants to audit a specific variable's harmonization can trace it from raw byte positions through to the harmonized column without running anything, and forward-extension to subsequent NCHS release years is mechanical.

From the perinatal researcher's point of view, the primary shortcoming of the HVS resource is the absence of cause-of-death coding for fetal deaths in the public-use file before 2014. The 2006 NCHS Fetal Death User Guide states this directly (p. 54): "Cause-of-fetal-death data are also not currently available." For 2018 and later, approximately 50% of records are missing cause data. The pathway through the NCHS Research Data Center (restricted-use) is referenced in the codebook for users who need the codes; cause-specific work prior to 2014 is not represented as supported. State-level geographic identifiers are similarly suppressed in V1-era fetal-death public-use files (2005 onward); state codes (`STATEFET`, `STATERES`, `STOCCFIP`) remain in the per-year raw parquets for 1992–2002, and that subset of years can support state-stratified analyses.

A second category of limitation is harmonization-internal. Three fetal-death columns carry incompatible content across the 1989/2003 revision boundary: `breech_unrevised`, `delivery_place_unrevised`, and `maternal_race_bridged_detail` store semantically different content across eras. Each is tagged within_era in the schema, surfaced in the column name suffix where applicable, and accompanied by a warning in CODEBOOK.md. No 1989/2003 maternal-education bridge is provided, because the 1989-revision raw field captures years of completed schooling (UMEDUC, 00–17) while the 2003-revision raw field captures a 9-category degree-level recode (MEDUC); the two concepts are not 1:1 mappable, and both are preserved in the harmonized schema as `maternal_education_unrevised` and `maternal_education` respectively, leaving analysts to apply their own modelling choices.

A third category is NCHS public-use field-availability gaps within the V1 era, which the harmonization passes through faithfully. The revised 9-category `maternal_education` recode is blank for V1 years 2007–2013, even for records following the revised certificate, and `paternal_age_combined` is similarly blank for 2007–2013. The years-of-completed-schooling field `maternal_education_unrevised` is populated for V2 1992–2002 and V1 2005–2006 only, and is blank for V1 2007 onward because NCHS dropped the unrevised field from the public-use file from that year. Every gap is enumerated in COMPARABILITY.md with the NCHS source confirming the limitation; the gaps are not parsing artifacts and cannot be filled from the public-use files.

Finally, state-specific reporting quirks during the 1992–2002 fetal-death era are preserved rather than imputed. Oklahoma did not report Hispanic origin during this period; Maryland (1992–1998) and Massachusetts (1992–1997) did not report Hispanic origin in early years; Louisiana under-reported plurality 1992–1994. These quirks are documented in COMPARABILITY.md and reproduce the corresponding *NVSR 57-08* footnotes; users analysing Hispanic-origin fetal mortality in the V2 era should restrict to states with complete reporting. The 2003 and 2004 fetal-death transition years and pre-1992 fetal-death years are not in the current release. A published version roadmap commits to V2.1 (adding 2003–2004) and V3 (extending to 1982); the shipped 1992–2022 span already covers every year for which NCHS publishes fetal-mortality rates in the *NVSR Fetal & Perinatal Mortality* series.

## Data resource access

The HVS resource is deposited on Zenodo under a Creative Commons Attribution 4.0 International (CC BY 4.0) licence for the harmonization layer. The underlying NCHS source data are works of the U.S. Government and are not subject to U.S. copyright (17 U.S.C. § 105). No data-use agreement, application, or institutional credentialing is required. Concept DOIs resolve to the latest version; version-specific DOIs let analyses pin to an exact release. The natality concept DOI is 10.5281/zenodo.19363074 and the fetal-death v2.0.0 release DOI is 10.5281/zenodo.20031571. The latest version numbers and individual file SHA-256 checksums are recorded in each deposit's `PROVENANCE.md`. Pipeline source code is mirrored on GitHub under a permissive open-source licence and is included verbatim in each Zenodo deposit, so deposits remain re-buildable even if the GitHub mirror becomes unavailable.

## HVS in a nutshell

- Three companion harmonized parquet files: natality (1990–2024, 138.8 million records), linked birth–infant death (2005–2023, 74.9 million records), and fetal death (1992–2022, 1.6 million records), each with one stable column schema across all years covered.
- First public harmonization of U.S. fetal death microdata across the 1989-revision and 2003-revision Standard Report boundary.
- Validated against every per-year figure NCHS has published in the relevant *National Vital Statistics Reports* series.
- Released CC BY 4.0 on Zenodo with concept DOIs that resolve to the latest version.
- Deterministic open-source pipelines and a three-level user-runnable verification ladder allow the harmonization to be re-built from public NCHS sources without trusting the author's outputs.

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
