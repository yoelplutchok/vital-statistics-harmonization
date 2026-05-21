# Data Resource Profile: U.S. Harmonized Vital Statistics microdata, 1968–2024

The U.S. Harmonized Vital Statistics (HVS) microdata resource integrates and disseminates harmonized natality, linked birth–infant death, fetal death, and matched-multiples public-use microdata released by the U.S. National Center for Health Statistics (NCHS), as four companion parquet files with one stable column schema per product. Coverage extends from 1968 forward and comprises 201,161,456 birth records (1968–2024), 149,386,620 linked birth–infant death records (1983–2023, with a permanent 1992–1994 NCHS-linkage gap), 2,427,233 fetal death records (1982–2024), and 1,665,568 matched-multiples records of twins, triplets, and quadruplets across three NCHS publication windows (1995–2020). The harmonization integrates source files spanning four U.S. Standard Certificate of Live Birth and Report of Fetal Death revisions (1968, 1978, 1989, and 2003), several within-revision NCHS layout reformats, and a state-by-state staggered adoption window in which a single annual file contains records following different schemas. Variable coding schemes are standardized across eras, without loss of detail, into one stable parquet column schema per product, and per-year raw parquets preserving every documented source field are also disseminated. Each product is validated against the per-year aggregates NCHS publishes — the *National Vital Statistics Reports* (*NVSR*) series for natality, linked birth–infant death, and fetal death, and the published documentation tables for matched multiples — reproduced byte-exact under a documented analytic filter. The resource is released under Creative Commons Attribution 4.0 on Zenodo, with deterministic open-source pipelines re-runnable end-to-end from the public NCHS source files on a laptop, and with no application or data-use agreement required.

## Data resource basics

The U.S. National Vital Statistics System counts every birth, fetal death, and infant death registered nationally — roughly 3.5–4 million live births, 20,000–30,000 fetal deaths, and 20,000 infant deaths a year.[^nvsr_births] NCHS has compiled these events since 1933 and released them as annual fixed-width public-use microdata since 1968 (natality) and the early 1980s (fetal death). The microdata underlie most U.S. perinatal-mortality and stillbirth trend studies, individual-level state disparity analyses, and age-period-cohort decompositions.

These microdata are difficult to use across years because the source layouts change. Field positions, code values, and variable inventories shift at three kinds of boundary: (i) certificate-revision transitions — principally the staggered 1989-to-2003 transition (phased over 2003–2014 for natality and 2005–2017 for the V1 fetal-death window, reaching 100% revised reporting in 2018), plus the earlier 1968-to-1989 (natality) and 1978-to-1989 (fetal death) boundaries within the backward-extended coverage; (ii) within-revision NCHS reformats (e.g., the natality record compresses 1500→775 bytes in 2006, with unrevised-only fields blanked from 2009, then reformats to 1345 bytes in 2014); and (iii) state-by-state staggered adoption of the 2003 revision, so that a single annual file carries records on different schemas by state of registration. The same conceptual variable can occupy different byte positions, use different codes, or be absent entirely depending on year and state.

The field has adapted by restricting analyses to single-revision windows: Salihu and colleagues used 1995–1998 for 1989-revision uniformity;[^salihu2004] Willinger and colleagues used 2001–2002, the last uniform years before the 2003 rollout;[^willinger2009] Hogue and Silver, surveying disparities through 2005, were forced onto aggregate published rates rather than microdata;[^hogue2011] and Ananth and colleagues' 1980–2020 stillbirth analysis excluded Hispanic ethnicity because the variable "was only made available in the revised 2003 birth certificates".[^ananth2022] These restrictions reflect the source files, not investigator preference.

NCHS itself publishes harmonized cross-revision tabulations (the *Births: Final Data* and *Fetal and Perinatal Mortality* *NVSR* series), but those are aggregate tables produced inside the agency on a fixed tabulation grid; only the published cells survive, so investigators needing microdata-level cross-revision analyses have had to repeat the harmonization privately for each study. To our knowledge, no openly published, reproducible, validated harmonized longitudinal microdata product has previously been available for U.S. natality, linked birth–infant death, or fetal death; HVS provides one — in the spirit of IPUMS-International[^ipums] and the Human Mortality Database[^hmd] — performing the harmonization once, in the open, with deterministic re-runnable pipelines.

The U.S. Harmonized Vital Statistics (HVS) microdata resource fills this gap. First released in 2026 and maintained by a single author, it is versioned on Zenodo (a concept DOI resolves to the latest version; version-specific DOIs let analyses pin to an exact release), with open-source pipelines on GitHub that are included verbatim in the deposit and run end-to-end from the public NCHS files on a laptop.

## Data resource area and coverage

The HVS resource covers the United States from 1968 forward. The natality file holds 201,161,456 records (1968–2024; 84 columns); the linked birth–infant death file 149,386,620 records (1983–2023; 97 columns; a permanent 1992–1994 NCHS-linkage gap; keyless two-file cohort format 1983–1988, denominator-plus 1989–2015, period-cohort merged 2016–2023); the harmonized fetal death file 2,427,233 records (1982–2024; 89 columns); and the matched-multiples file 1,665,568 records of twins, triplets, and quadruplets in multiple-delivery sets across three publication windows (1995–1997, 1995–2000, 2016–2020; 24 columns). Each product carries one stable schema across the years it covers, and per-year raw parquets preserving every documented source field are also disseminated.

The fetal-death years 2003–2004 (distinct 1351/1501-byte transition layouts) and 1982–1991 (1978-revision 1982–1988; early 1989-revision 1989–1991) are all harmonized into the stable schema in the current release, though Hispanic origin is unavailable for 1982–1988 (the 1978-revision Report of Fetal Death did not collect it). The fetal-death 1989-revision era was verified by byte-level comparison (98,500 raw-byte-to-cell comparisons, zero mismatches; 1989–1991 confirmed byte-position-identical to the 1992 benchmark).

The natality file spans six era segments (five transitions); the linked file five segments (four transitions, plus the permanent 1992–1994 gap); the fetal-death file five segments (four transitions); and matched multiples three discrete publication windows (Table 1). Within each segment the layout is uniform; at the transitions record length, certificate revision, or both can change.

**Table 1.** Source-data era boundaries by product.

| Product | Era | Years | Record length | Certificate / revision |
|---|---|---|---|---|
| Natality | 1968-revision era (sub-layouts 1968 / 1969–1971 / 1972–1988 / 1989) | 1968–1989 | varies† | 1968 |
| Natality | Unrevised-only | 1990–2002 | 350 bytes | 1989 |
| Natality | Dual-certificate transition (long format) | 2003 | 1350 bytes | Dual |
| Natality | Dual-certificate transition (long format) | 2004–2005 | 1500 bytes | Dual |
| Natality | Dual-certificate transition (short format) | 2006–2013 | 775 bytes | Dual; unrevised-only fields blanked from 2009 |
| Natality | Revised-only | 2014–2024 | 1345 bytes | 2003 |
| Linked birth–infant death | Cohort, keyless two-file (denominator/numerator) | 1983–1988 | varies† | 1968 |
| Linked birth–infant death | Cohort, denominator-plus | 1989–2004 | varies† | 1989 (dual at 2003–2004; permanent 1992–1994 linkage gap) |
| Linked birth–infant death | Cohort, denominator-plus | 2005–2013 | 900 bytes | Dual |
| Linked birth–infant death | Cohort, denominator-plus | 2014–2015 | 1384 bytes | 2003 |
| Linked birth–infant death | Period-cohort merged (CO_SEQNUM × CO_YOD) | 2016–2023 | varies | 2003 |
| Fetal death | 1978-revision uniform | 1982–1988 | 200 bytes | 1978 |
| Fetal death | 1989-revision uniform | 1989–2002 | 360 bytes | 1989 |
| Fetal death | Dual-certificate transition | 2003–2004 | 1351 / 1501 bytes | Dual |
| Fetal death | 2003-revision transition | 2005–2017 | varies | Mixed (2003-revision A or 1989-revision S per state-year) |
| Fetal death | Revised-only | 2018–2024 | varies (2652 bytes) | 2003 |
| Matched multiples | 1995–1997 publication window | 1995–1997 | 502 bytes | 1989 |
| Matched multiples | 1995–2000 publication window | 1995–2000 | 754 bytes | 1989 |
| Matched multiples | 2016–2020 publication window | 2016–2020 | 155–157 bytes (variable) | 2003 |

† Record length varies by year within the era; the per-year byte-position layouts are documented in each product's `record_layout_*.csv`. The pre-1990 natality and pre-2005 linked layouts are reconstructed from the corresponding NCHS Natality and Cohort Linked File User Guides.

Geographic coverage is the United States as a whole. State-level identifiers are present in the per-year raw parquets for natality 1968–2024, linked birth–infant death 1983–2023, and fetal death 1982–2004. State identifiers are suppressed by NCHS in the 2003-revision (V1-era) fetal-death public-use files (2005 onward) and in the matched-multiples 2016–2020 window, and are therefore absent from the harmonized files in those years.

## Measures

Each product ships one stable harmonized schema mapping per-era raw fields to a common dtype, name, and code space. The natality file has 71 harmonized columns plus 13 derived indicators (84 total); the linked file adds death-side harmonized and derived columns plus three within-era cohort columns from the 1983–2004 extension — `link_segment`, `underlying_cause_icd9`, and `cause_recode_61` (ICD-9 cause of death for the 1983–1998 cohorts) — for 97 total; the fetal-death file has 73 harmonized plus 16 derived (89 total); and the matched-multiples file has 24 columns (set identifiers, record type, demographics, clinical fields, and ICD-9/ICD-10 cause of death for infant deaths). Each `harmonized_schema.csv` lists dtype, allowed values, coverage, comparability class, and source field per era; the full per-era mapping ships as `variable_crosswalk_working.csv` (Supplementary Table S1).

Harmonized measures span maternal and paternal demographics (age, bridged race, Hispanic origin, marital status, education, residence status); pregnancy (gestational age — obstetric estimate plus LMP derivation where available — plurality, birth and fetal-death history, prenatal care, tobacco use); delivery (birth weight, delivery method, breech presentation, place, attendant); linked-file infant outcomes (age and place of death, ICD-10 cause of death, NCHS record weight); fetal-death-specific fields (ICD-10 cause groupings from 2014, autopsy status, the NVSR tabulation flag); and constructed indicators (low birth weight, preterm birth, neonatal vs post-neonatal death, cause groupings) computed deterministically from the harmonized columns.

Sentinel values (`gestational_age_combined=99`, `birthweight=9999`, etc.) are converted to NaN in the derivation step before threshold comparisons, so constructed indicators return missing for sentinel-coded records while the harmonized parent retains the raw sentinel.

### Comparability classification

Every harmonized column is tagged with one of four comparability classes, recorded in the schema CSV: **full** (consistent across all years covered), **partial** (consistent within era; minor cross-era differences documented), **within_era** (incompatible content across eras; cross-era aggregation should not be performed), or **not_available** (era does not collect the field). A few fetal-death columns are irreducibly `within_era` — `breech_unrevised`, `delivery_place_unrevised`, and `maternal_race_bridged_detail` carry concepts the 1989 and 2003 revisions code incompatibly — and are flagged with explicit warnings; users are referred to the per-year raw parquets when within-era detail is required.

## Methods

The HVS resource is produced for each of the four products by deterministic open-source pipelines committed to GitHub and re-runnable end-to-end from the public NCHS source files:

1. **Acquisition.** Annual fixed-width zips, User Guide PDFs, and *NVSR* reports are obtained from the NCHS FTP server, with per-file SHA-256 checksums in each deposit's `file_inventory.csv`.
2. **Parsing.** Each file is parsed using era-specific `record_layout_*.csv` byte-position-to-field-name mappings derived from the NCHS User Guides.
3. **Type casting and renaming.** Per-era raw fields are renamed to harmonized columns and cast to a common dtype — one harmonized parquet per source year.
4. **Value-level normalization.** A minority of variables are recoded across the revision boundary because the eras code the same concept differently — for fetal death, five normalizations (`fetal_sex`, `delivery_method_recode`, `maternal_race_bridged`, `paternal_age_recode11`, `delivery_place_recode`), with the original detail preserved in the raw parquets; the natality and linked products receive analogous normalizations across the 2014 reformat.
5. **Derivation.** Low birth weight, preterm birth, gestational-age recodes, neonatal vs post-neonatal death, and ICD-10 cause groupings are computed deterministically from the harmonized columns.
6. **Validation.** Per-year counts and rates are computed under the canonical filter and compared cell-by-cell to the NCHS-published aggregates; each product's validation script prints a pass/fail table against the targets in `external_validation_targets.csv`.

Without such normalization, naïve concatenation produces columns matching neither era — for example, the fetal-death `DELMETH6` (six categories) and `DMETH_REC` (three) would yield nine spurious categories; the harmonization collapses the six to the three, preserving the full detail in the raw parquets.

Re-deriving from a fresh download of the NCHS zips produces a byte-identical file, with SHA-256 checksums for every artifact in `PROVENANCE.md`. The fetal-death pipeline runs end-to-end in ~5 minutes on a 2024-vintage laptop; the natality pipeline (which also builds the linked file) is parse-dominated and runs in a couple of hours for the full 1968–2024 build.

## Data resource use

The resource supports research in epidemiology, perinatal medicine, demography, public health, biostatistics, and policy that requires U.S. natality, fetal-death, linked, or matched-multiples microdata across periods, revisions, or product boundaries. Each file is a single Apache Parquet readable in Python, R, Stata, SAS, and most modern tools. Worked examples ship as `quickstart.py`/`quickstart.R` per product, with DuckDB views (`views.sql`) and a Stata/SAS bridge at the repository root; cross-product examples are in `notebooks/`.

A canonical analytic filter reproduces the population on which NCHS computes its published rates: for fetal death, `tabulation_flag == '2'` and `residence_status != '4'` (the NVSR-comparable subset of resident fetal deaths meeting NCHS's gestational-age and birth-weight rule); for natality, `residence_status != '4'` (U.S. residents). Applying it is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

The natality, fetal-death, and linked files are designed for joint use: fetal mortality rates need live-birth denominators on the same stratification as the fetal-death numerator, and perinatal mortality rates additionally need early neonatal death counts from the linked file. Because these products share aligned column names for shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status`), joins on `data_year` and demographic strata produce numerator and denominator with consistent semantics. A `live_births_by_year.csv` reference (1995–2002 and 2005–2024, from the *NVSR* *Fetal and Perinatal Mortality* and *Births: Final Data* series) and a stratified-denominator companion ship with the fetal-death product for users who want denominators without loading the full natality file.

Three levels of independent verification are supported: Level 1 (~10 s) checks downloaded files against the SHA-256 checksums in `PROVENANCE.md`; Level 2 (~1 min) runs each product's validation script against its *NVSR* targets in `external_validation_targets.csv`; Level 3 (~1–2 h) re-downloads the raw NCHS zips and re-runs the pipelines to a byte-identical parquet.

Supported analyses include cross-revision stillbirth disparity trends by maternal race, age, and Hispanic origin (the case Ananth and colleagues had to drop Hispanic ethnicity from);[^ananth2022] secular low-birth-weight, preterm, and gestational-age trends back to 1968 (natality) and 1982 (fetal death); period and cohort decompositions of perinatal and infant mortality (the linked cohort denominators reach back to 1983); multiple-gestation analyses; cause-specific neonatal-mortality trends from 2014; and policy natural-experiment studies spanning the 2003 rollout.

## Strengths and weaknesses

Five strengths shape the resource. **Comparability** of the harmonized series across certificate revisions and NCHS reformats through one stable column schema per product, every column tagged with a comparability class and prominent warnings on the subset that cannot be reconciled. **Validation** against the per-year aggregates NCHS publishes, byte-exact under the canonical filter: natality 183/183 *Births: Final Data* targets (1990–2024; pre-1990 benchmarking planned); the linked file 33/35 for 2005–2023 (two cells differ by one record, from NCHS survivor records with null weights), plus byte-exact cohort denominators and resident births and published infant mortality within ±0.02 for all 19 pre-2005 cohort years; fetal death all 29 per-year counts and 26 fetal-mortality rates for the validated years, with 1982–1991 and 2023–2024 control counts matched to the NCHS User Guides and 13 of 19 *NVSR 73-09* detail cells exact (six documented methodological differences); and matched multiples 13/13 checks (five documentation-table totals byte-exact, plus row-count and structural invariants). **Reproducibility** through deterministic open-source pipelines, SHA-256 checksums for every shipped artifact, and per-year raw parquets: a sceptical user is asked not to trust the author but to re-build and diff. **Accessibility** through CC BY 4.0 licensing, no application, agreement, or credentialing, and single-file parquet outputs. **Joint-use design**: shared column names, aligned comparability classes, and consistent demographic codings let fetal, perinatal, and infant mortality rates be computed with matched numerator and denominator strata.

Weaknesses are of two kinds: NCHS public-use suppression that the harmonization passes through, and genuine cross-revision incomparability that it documents rather than imputes. Fetal-death cause-of-death coding is absent before 2014 and missing for ~50% of records from 2018 onward (pre-2014 codes are RDC-only). State identifiers are suppressed in the V1-era fetal-death files (2005 onward) and the matched-multiples 2016–2020 window, remaining only in the pre-2005 raw parquets. In the V1 fetal-death era, `maternal_education` and `paternal_age_combined` (2007–2013) and `maternal_education_unrevised` (2007 onward) are blank because NCHS dropped those fields; all gaps are enumerated in `COMPARABILITY.md`. No 1989/2003 maternal-education bridge is provided — years-of-schooling (UMEDUC, 00–17) and the 9-category degree recode (MEDUC) are not 1:1 mappable — so both are kept as separate columns. The backward extensions carry documented limits: natality 1968–1989 is harmonized but not yet NVSR-benchmarked (planned); the 1983–1988 linked cohort is keyless (infant mortality is a denominator/numerator count ratio, not a per-birth flag), the 1983–1984 denominators are a 50%-non-registration-area weighted sample (a record weight reproduces the published figures), 1992–1994 is a permanent linkage gap, and 1983–1998 ICD-9 cause of death lacks an ICD-9-to-ICD-10 crosswalk. Matched multiples is validated against the published documentation tables rather than the per-year *NVSR* series, with the 1995–1997 and 1995–2000 tables not yet transcribed for cell-level validation. State-specific reporting quirks during the 1992–2002 fetal-death era are preserved rather than imputed.[^state_quirks]

## Future developments

Earlier roadmaps listed the fetal-death 2003–2004 transition years and the 1982–1991 backward extension as planned; both have now shipped (see *Data resource area and coverage*). The roadmap now commits the project to:

- **Annual extension.** Each product is extended forward as NCHS publishes new source files; no retroactive schema changes are required, since the harmonization is forward-extensible by adding entries to the era-specific record-layout CSVs.
- **Pre-1990 natality benchmarking.** The 1968–1989 natality years are harmonized; per-year NVSR benchmarking for those years is a planned incremental addition.
- **Matched-multiples cell-level validation.** The 1995–1997 and 1995–2000 documentation tables will be transcribed to extend matched-multiples validation beyond the 2016–2020 window.
- **Cohort cause-of-death harmonization.** An ICD-9-to-ICD-10 crosswalk for the 1983–1998 linked-cohort causes of death is a deferred derivation.
- **Restricted-use products.** Census record linkage and NCHS Research Data Center geographic-identifier files are out of scope for the public-use resource; users who need these layers are referred to the corresponding NCHS programs.

## Data resource access

The HVS resource is deposited on Zenodo under CC BY 4.0 for the harmonization layer; the underlying NCHS source data are U.S. Government works not subject to copyright (17 U.S.C. § 105). No data-use agreement, application, or credentialing is required. It is deposited as a single multi-product record: the version-of-record DOI is 10.5281/zenodo.20326150 (v1.0.1) and the concept DOI resolves to the latest version, while version-specific DOIs let analyses pin to an exact release. The superseded single-product deposits remain immutable for provenance (natality and linked: 10.5281/zenodo.19363074; fetal death v2.0.0: 10.5281/zenodo.20031571). Pipeline source code is openly developed on GitHub at https://github.com/yoelplutchok/vital-statistics-harmonization and included verbatim in the deposit, which therefore remains re-buildable even if the repository becomes unavailable. Cross-product worked examples — a joint-use fetal-mortality demonstration validated against *NVSR 73-09* Table 4, a matched-multiples demonstration, and a paper-companion notebook recomputing this manuscript's numeric claims from the parquets — ship under `notebooks/`.

## HVS in a nutshell

- The HVS resource integrates and disseminates harmonized U.S. natality, linked birth–infant death, fetal death, and matched-multiples public-use microdata as four companion parquet files with one stable column schema per product.
- Coverage: 201.2 million birth records (1968–2024), 149.4 million linked birth–infant death records (1983–2023, with a permanent 1992–1994 linkage gap), 2.4 million fetal death records (1982–2024), and 1.7 million matched-multiples records (1995–2020).
- The resource is, to our knowledge, the first openly published, reproducible, validated harmonization of U.S. fetal-death microdata across the 1978-, 1989-, and 2003-revision Standard Report boundaries, and the first to package these four vital-statistics products as one reproducible artifact.
- Each product is validated against the per-year aggregates NCHS publishes (the *NVSR* series for natality, linked birth–infant death, and fetal death; the published documentation tables for matched multiples), reproduced byte-exact under a documented analytic filter.
- The first release, in 2026, was made under Creative Commons Attribution 4.0 on Zenodo, with deterministic open-source pipelines on GitHub and a three-level user-runnable verification ladder.
- Future releases will extend each product forward as NCHS publishes new years, add per-year NVSR benchmarking for pre-1990 natality, and transcribe the matched-multiples documentation tables for cell-level validation.

## Ethics approval

Not required. The HVS resource is built exclusively from de-identified public-use microdata released by NCHS under U.S. federal law, with no identifying or restricted-use fields and no human-subjects contact.

## Author contributions

YP is the sole author. YP conceived and designed the resource, built and validated the harmonization pipelines, drafted and revised the manuscript, and is responsible for the final content. <!-- YP: confirm or revise -->

## Use of artificial intelligence (AI) tools

Anthropic's Claude (Opus-class models) was used as a coding-and-writing agent throughout the project: pipeline development, validation scripting, internal documentation, and manuscript drafting and revision. Every numeric claim in this manuscript is derived from the harmonized parquets and the committed per-product validation tables (`validation_results.csv` / `external_validation_*` and each product's `PROVENANCE.md`); a companion notebook (`notebooks/paper_companion.ipynb`) recomputes the cross-product claims directly from the shipped parquets. The author reviewed all AI-suggested content and retains responsibility for the final manuscript. <!-- YP: confirm wording in line with IJE policy and edit tool/model versions as needed. Note for submission: re-run notebooks/paper_companion.ipynb against the current v3.0.0 / v4.0.0 / v2.4.0 + matched-multiples parquets to refresh the per-claim synthesis before submitting. -->

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

[^ipums]: Sobek M, Cleveland L, Flood S, et al. Data Resource Profile: IPUMS-International. *Int J Epidemiol* 2017;46(2):390. https://doi.org/10.1093/ije/dyx012

[^hmd]: Barbieri M, Wilmoth JR, Shkolnikov VM, et al. Data Resource Profile: The Human Mortality Database. *Int J Epidemiol* 2015;44(5):1549–1556. https://doi.org/10.1093/ije/dyv105
