# Frequently Asked Questions

## Q: What years are covered?

**1992 through 2022, with 2003 and 2004 deferred to V2.1.** That's 29 annual files containing 1,634,195 total records — 700,704 in the V2 era (1992-2002, 1989-revision) and 933,491 in the V1 era (2005-2022, 2003-revision transition).

## Q: Why are 2003 and 2004 missing?

Both years have distinct, non-uniform transition layouts (1351-byte and 1501-byte records respectively, with mixed 1989/2003-revision content) that require dedicated handling. NCHS publishes a separate `fetaldeath0304problems.pdf` documenting their idiosyncrasies. They are deferred to V2.1.

## Q: What is a fetal death?

A fetal death is a spontaneous intrauterine death at any gestational age, excluding induced terminations. The standard public-use file focuses on deaths occurring at 20 or more completed weeks of gestation.

## Q: What is the difference between total records and the NVSR-tabulated subset?

The total file includes deaths at all gestational ages reported by each state. The NVSR-tabulated subset (`tabulation_flag == '2'`) is the standard analytic population, yielding roughly 20,000 to 30,000 records per year. Total across all 29 years: 1,634,195 (728,483 of which carry `tabulation_flag == '2'`; **727,155** of those are also U.S. residents and form the NVSR-comparable subset). NB: `tabulation_flag` is NCHS's compound criterion — typically "GA >= 20 weeks **OR** birthweight >= 350g when GA is unknown" — not a pure GA cutoff. About 5,400 V1 records flagged `'2'` have `gestational_age_combined < 20` (almost all in 2014+; NCHS retained them via the BW criterion or state-specific reporting rules), and roughly 63,700 records across all 29 years (~42,200 in V1 alone) flagged `'1'` have GA >= 20 (excluded by NCHS's source flag for other reasons). When you need a pure GA filter, use `gestational_age_combined` directly.

## Q: What is the reporting threshold problem?

States define "reportable" fetal death differently — some use 20 weeks, some use 350 grams, and others use various combinations. This affects total counts but does not affect the >=20 week tabulation subset. See `REPORTING_THRESHOLDS.md` for state-level details.

## Q: What is the VERSION flag?

Records follow either the 2003 revision (`A`) or the 1989 revision (`S`). Some fields — revised education, revised tobacco, revised risk factors, BMI, ICD-10 cause of death — are only available for A-version records. By 2018, all V1 records use version A. **All V2 records (1992-2002) are `version_flag='S'`** (synthesized; the 1989-revision raw files have no native VERSION field), so version-A-only fields are uniformly blank for the V2 slice.

## Q: Why is `maternal_education` blank for 1992-2002 and for 2007-2013?

- **1992-2002**: V2 populates `maternal_education_unrevised` (years-of-school 00-17) instead of the revised 1-9 categorical scale, because the revised scale was added in the 2003 revision.
- **2007-2013**: NCHS did not include this field in the V1 public-use files for those years, even for A-version records. This is a data availability limitation, not a parsing error.

The unrevised education variable (`maternal_education_unrevised`) is available for 1992-2002 (all 11 V2 years) and 2005-2006 (V1 S-version only); the field is blank for 2007-2013 in the V1 public-use files. Cross-era education trends require building a 1989→2003 binning bridge — V2.0 deliberately does not provide this because the year-of-schooling and degree-level concepts are not 1:1 mappable.

## Q: When is cause-of-death data available?

ICD-10 cause codes (`cause_icd10`) appear in the public-use file starting in 2014 (the COD variant). They are not available for 1992-2013. Roughly 50% of records have cause data for 2018 and later. The 2006 user guide states this directly on p. 54: *"Cause-of-fetal-death data are also not currently available."* Pre-2014 ICD codes are only available through the NCHS Research Data Center (restricted-use).

## Q: Which variables are comparable across all years?

Variables with `comparability_class` of "full" in `harmonized_schema.csv` are consistent across the entire 29-year time series (after the V2 era code-normalization fixes B1, B2, B3, B4, and B6). Examples of `full` columns include `fetal_sex`, `birthweight`, `gestational_age_combined`, `delivery_method_recode`, `delivery_place_recode`, `paternal_age_recode11`, `attendant`, `live_birth_order`, `residence_status`. `maternal_age` is `partial` (V2 1989-rev DMAGE is exact single-year while V1 MAGER top/bottom-codes 50+/12-). See `COMPARABILITY.md` §10 for the full split between (a) the five V2→V1 value-level normalizations B1-B4+B6, (b) the three `within_era` relabels (B5 `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) to avoid in cross-era `groupby`, and (c) the `maternal_age` partial relabel.

## Q: What are the `within_era` columns and why?

Three harmonized columns store **incompatible content** across V2 and V1 eras and are explicitly tagged `within_era` in the schema and codebook:

- `maternal_race_bridged_detail` — V2 raw 1989-rev MRACE codes vs V1 2006 raw MBRACE codes (overlap with different meanings).
- `delivery_place_unrevised` — V2 PLDEL 4-cat scheme vs V1 UBFACIL 5-cat scheme (codes 2 and 3 mean different things).
- `breech_unrevised` — V2 BREECH = "Breech/Malpresentation" (broader) vs V1 ULD_BREECH = "Breech Delivery" (narrower) — different clinical concepts.

For these three columns, do NOT cross-era `groupby`. Use the per-year raw parquets bundled in `fetal_death_yearly_raw_1992-2022.zip` if you need V2-specific detail.

## Q: Are these data nationally representative?

The file contains all reported fetal deaths, not a sample. However, completeness varies by state and gestational age, especially at younger gestational ages where reporting practices differ. For 1992-2002 specifically, several states had incomplete Hispanic-origin reporting (Oklahoma all 11 years, Maryland 1992-1998, Massachusetts 1992-1997) and Louisiana did not report plurality 1992-1994. See `COMPARABILITY.md` §11.

## Q: How should I filter for standard analyses?

Use `tabulation_flag == '2'` AND `residence_status != '4'`. This produces the NVSR-comparable subset of resident fetal deaths at 20 or more weeks of gestation, which matches published NVSR per-year figures exactly for every count and rate row in `validation_results.csv` (NVSR 73-09 for 2005+, NVSR 57-08 for 1995-2002, user guides for 1992-1994). Detail-cell tabulations from NVSR 73-09 (Tables A, 4, 8, and early/late GA from Table 1, for 2014 and 2022) yield 6 documented differences out of 19 cells: 4 early/late gestational-age cells where NVSR proportionally redistributes records with unknown gestational age between strata, and 2 cause-of-death cells where NVSR Table 8 restricts to a 43-state reporting area while the harmonization includes all states. None are byte-level mismatches in the harmonized data. See README §Validation for the breakdown.

Note: filtering ONLY on `tabulation_flag == '2'` (without excluding foreign residents) overstates the published NVSR resident counts by 18-166 records per year (mean ~46/year; the inflation grew in 2018-2022 as foreign-resident reporting normalized).

## Q: What file format is the data in?

Apache Parquet. Readable in Python (pandas, pyarrow), R (arrow), Stata (via `haven` or recent versions), and most modern data tools.

## Q: How should I cite this dataset?

Authoritative citation metadata lives in [`CITATION.cff`](CITATION.cff) at the deposit root (machine-readable; GitHub renders a "Cite this repository" button from it).

Suggested form:

> Plutchok, Yoel (2026). *Harmonized U.S. Fetal Death Microdata, 1992-2022*. Version 2.0.0. Zenodo. DOI: [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571)

For demographic-stratified live-birth denominators (needed to compute race-, age-, or ethnicity-specific fetal mortality rates), see the companion U.S. Natality Harmonization Project (Zenodo concept DOI [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074)).

## Q: What is planned for future versions?

- **V2.1**: add the 2003 and 2004 transition years (distinct layouts), bringing coverage to 1992-2022 with 31 years complete.
- **V3**: extend backward to 1982 (earlier 1978-revision layouts).

<!-- C8.20-GENERATED:BEGIN (do not hand-edit; regenerate via scripts/_build_codebook_extensions.py) -->

## Per-variable historical distributions (C8.20)

**Q: How do I see how a variable's codes/sentinels behaved in each era?**

See the auto-generated **Appendix C8.20 — Per-variable historical evidence** at the end of the CODEBOOK. For every harmonized variable it gives, per documented layout era: the value distribution, a sentinel-code disambiguation table, and an era-by-era coding-scheme diff. Every number is derived from the shipped parquet by `scripts/_build_codebook_extensions.py` (deterministic; regenerate to reproduce byte-identically).

<!-- C8.20-GENERATED:END -->
