# Frequently Asked Questions

## Q: What years are covered?

**1982 through 2024 — 43 contiguous years.** Total records: **2,427,233** across seven NCHS layout eras (see `CODEBOOK.md` / `COMPARABILITY.md` era table; per-era counts in Appendix C8.20).

## Q: Why were 2003 and 2004 once deferred?

Both years have distinct, non-uniform transition layouts (1,351-byte and 1,501-byte records with mixed 1989/2003-revision content). NCHS publishes `fetaldeath0304problems.pdf` documenting their idiosyncrasies. They shipped in **V2.1** (2026-05-12); the v2.0.0 Zenodo deposit predates that extension.

## Q: What is a fetal death?

A fetal death is a spontaneous intrauterine death at any gestational age, excluding induced terminations. The standard public-use analytic subset focuses on deaths NCHS flags for tabulation (typically >=20 weeks gestation OR >=350g when GA is unknown).

## Q: What is the difference between total records and the NVSR-tabulated subset?

The total file includes deaths at all gestational ages reported by each state. The NVSR-tabulated subset (`tabulation_flag == 2`) is the standard analytic population. Across **43 years (1982-2024)**: **2,427,233** total records; **1,123,940** with `tabulation_flag == 2`; **1,121,986** of those are U.S. residents (`residence_status != 4`) and form the NVSR-comparable subset (parquet-derived). `tabulation_flag` is NCHS's compound criterion — not a pure GA cutoff. For full per-era `tabulation_flag` / GA cross-tabs see Appendix C8.20 in `CODEBOOK.md`. When you need a pure GA filter, use `gestational_age_combined` directly.

## Q: What is the reporting threshold problem?

States define "reportable" fetal death differently. See `REPORTING_THRESHOLDS.md` for state-level details at era-boundary reference years.

## Q: What is the VERSION flag?

Records follow either the 2003 revision (`A`) or the 1989 revision (`S`). **1982-2002 (incl. V3b/V3a/V2 plus 2003-2004 transition)** are predominantly synthesized or native `S` for pre-2003-revision content; V1-era years (2005+) mix A and S until 2018+, when all records are A. Version-A-only fields are blank for S-version records.

## Q: Why is `maternal_education` blank for many years?

- **1982-2002 (pre-2003-revision eras):** populate `maternal_education_unrevised` (years-of-school), not the revised 1-9 scale.
- **2007-2013 (V1):** NCHS did not include revised education in the public-use files.

Cross-era education trends require an explicit 1989→2003 bridge; this resource does not ship one.

## Q: When is cause-of-death data available?

ICD-10 cause codes (`cause_icd10`) appear starting in 2014. Not available for 1982-2013 in public-use files. Pre-2014 ICD codes are NCHS RDC restricted-use.

## Q: Which variables are comparable across all years?

Variables with `comparability_class` of "full" in `harmonized_schema.csv` are consistent across the full 43-year span (after era-specific code normalizations). `maternal_age` is `partial`. See `COMPARABILITY.md` §10 for B1-B6 rules and `within_era` columns.

## Q: What are the `within_era` columns and why?

Three harmonized columns are tagged `within_era`: `maternal_race_bridged_detail`, `delivery_place_unrevised`, `breech_unrevised`. Do NOT cross-era `groupby` on them. Use per-year raw parquets in `output/yearly_clean/` (`fetal_death_{year}_raw.parquet`, 1982-2024) for era-specific detail.

## Q: Are these data nationally representative?

The file contains all reported fetal deaths, not a sample. Completeness varies by state and gestational age. State-specific quirks (Hispanic non-reporting, Louisiana plurality 1992-1994) are documented in `COMPARABILITY.md` §11.

## Q: How should I filter for standard analyses?

Use `tabulation_flag == 2` AND `residence_status != 4` (integer comparison; see migration guide if upgrading from v2.0.0 string-literal filters). This reproduces published NVSR per-year figures under `external_validation_targets.csv` (**90/90** byte-exact control counts at v2.4.0).

## Q: What file format is the data in?

Apache Parquet. Readable in Python (pandas, pyarrow), R (arrow), Stata, SAS (see monorepo `STATA_SAS_QUICKSTART.md`), and DuckDB (`views.sql` at monorepo root).

## Q: How should I cite this dataset?

Authoritative citation metadata: [`CITATION.cff`](CITATION.cff).

Suggested form:

> Plutchok, Yoel (2026). *Harmonized U.S. Fetal Death Microdata, 1982-2024* (v2.4.0 in-repo). Zenodo concept deposit: [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571)

For live-birth denominators, see the U.S. Natality Harmonization Project ([10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074)).

## Q: What is planned for future versions?

The in-repo envelope is **v2.4.0 (1982-2024)** pending the unified HVS Zenodo deposit (Phase D). Linked birth-infant death 2024-cohort refresh is tracked separately when NCHS releases the cohort file.

<!-- C8.20-GENERATED:BEGIN (do not hand-edit; regenerate via scripts/_build_codebook_extensions.py) -->

## Per-variable historical distributions (C8.20)

**Q: How do I see how a variable's codes/sentinels behaved in each era?**

See the auto-generated **Appendix C8.20 — Per-variable historical evidence** at the end of the CODEBOOK. For every harmonized variable it gives, per documented layout era: the value distribution, a sentinel-code disambiguation table, and an era-by-era coding-scheme diff. Every number is derived from the shipped parquet by `scripts/_build_codebook_extensions.py` (deterministic; regenerate to reproduce byte-identically).

<!-- C8.20-GENERATED:END -->
