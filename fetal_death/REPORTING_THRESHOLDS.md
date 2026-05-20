# Reporting Thresholds for Fetal Death Data

## The Problem

There is no uniform national definition of a "reportable" fetal death in the United States. Each state sets its own legal threshold for which fetal deaths must be filed with the vital statistics office. Some states require reporting only at 20 completed weeks of gestation; others require reporting of all products of human conception regardless of gestational age. This inconsistency means the denominator of reported fetal deaths is not comparable across states or, for states that changed their laws, across time. Any analysis that ignores these threshold differences risks conflating policy variation with epidemiological variation.

## Threshold Types Found in the Data

The `reporting_thresholds.csv` file classifies each state-year into one of six threshold types:

- **weeks_only (20 weeks)** -- The most common standard. Approximately 25 states require reporting at 20 or more completed weeks of gestation. Examples: Alabama, California, Illinois, Ohio, Texas.

- **weeks_or_grams (20 weeks OR 350g)** -- Approximately 12 states use a disjunctive criterion: a fetal death is reportable if gestational age reaches 20 weeks OR birth weight reaches 350 grams, whichever is met first. This captures some deaths below 20 weeks if the fetus is sufficiently large. Examples: Arizona, Idaho, Kentucky, Massachusetts, Wisconsin. Note that Michigan and Vermont use 400g rather than 350g, and the District of Columbia historically used 500g before switching to 350g.

- **grams_only (350g or 500g)** -- A small number of states define reportability solely by birth weight. Delaware and Montana use 350g (with 20-week fallback when weight is unknown). New Mexico used 500g prior to 2014, and Tennessee used 500g (with a 22-week fallback) prior to 2014.

- **weeks_16 (16 weeks)** -- Pennsylvania requires reporting at 16 or more completed weeks of gestation, capturing deaths between 16 and 19 weeks that most other states exclude.

- **weeks_12 (12 weeks)** -- Arkansas (post-2020) and Oklahoma (post-2020) require reporting at 12 or more completed weeks of gestation.

- **all_periods (all gestational ages)** -- Colorado, Georgia, Hawaii, New York, Rhode Island, and Virginia require reporting of all products of human conception, with no gestational age or weight floor. These states typically send only deaths at 20 or more weeks to NCHS for national tabulation.

## Impact on Analysis

These threshold differences have direct consequences for research:

1. **Inflated counts in low-threshold states.** States reporting at all gestational ages will record substantially more early fetal deaths, inflating their total counts relative to states that report only at 20 weeks.

2. **Weight-based vs. age-based capture.** A 350g threshold captures a different population than a 20-week threshold. A fetus at 18 weeks weighing 360g would be reportable in a weight-based state but not in a weeks-only state.

3. **Cross-state rate comparisons are invalid without adjustment.** Raw fetal death rates cannot be compared across states with different thresholds. A state with a lower threshold will appear to have a higher rate even if the underlying risk is identical.

4. **NCHS standard tabulations partially address this.** NCHS uses a tabulation flag (`tabulation_flag == 2`) to define the published-tabulation subset. The compound criterion is typically "GA >= 20 weeks OR birthweight >= 350g when GA is unknown", with state-specific reporting rules overlaid. A small share of flag-2 rows (almost all in 2014+) have GA < 20; a non-trivial share of flag-1 rows have GA >= 20. For the full **v2.4.0 (1982-2024)** per-era `tabulation_flag` and GA cross-tabs, see `CODEBOOK.md` Appendix C8.20 (parquet-derived). This removes most but not all threshold-driven heterogeneity.

## States That Changed Thresholds (1997-2023)

Several states changed their reporting requirements during the study period, creating within-state discontinuities:

- **Arkansas**: all_periods (through 2006) to 20 weeks/350g (by 2014) to 12 weeks (by 2022)
- **New Mexico**: 500g only (through 2006) to 20 weeks/350g (by 2014)
- **District of Columbia**: 20 weeks/500g (through 2006) to 20 weeks/350g (by 2014) to 20 weeks only (by 2022)
- **Maryland**: 20 weeks only (1997) to 20 weeks/500g (by 2006) to 20 weeks/350g (by 2022)
- **Kansas**: 350g only (1997) to 20 weeks/350g (by 2006)
- **Tennessee**: 500g only (through 2006) to 20 weeks/350g (by 2014)
- **Oklahoma**: 20 weeks only (through 2014) to 12 weeks (by 2022)

Trend analyses for these states must account for the threshold change, which can introduce apparent step-changes in fetal death counts that reflect reporting policy rather than population risk.

## Recommendations for Researchers

1. **Use `tabulation_flag == '2'` for the standard NCHS-published subset.** This is the closest approximation to a nationally uniform definition that NCHS itself maintains; it is the criterion behind every NVSR fetal-mortality count this dataset reproduces. It is *not* identical to "GA >= 20 weeks" — see the §4 footnote above — so when you need a strict GA filter, use `gestational_age_combined` directly or the derived `ga_gte20wks`.

2. **Use derived gestational age flags for common thresholds.** The harmonized dataset includes `ga_gte20wks`, `ga_gte28wks`, and `meets_who_stillbirth` for convenient subsetting at standard cutpoints.

3. **Consult `reporting_thresholds.csv` for state-level detail at era-boundary years.** The file documents threshold type, week cutoff, gram cutoff, and logical operator (AND/OR) for each U.S. state at the five reference years 1997, 2006, 2014, 2022, and 2023 — i.e., at each NCHS user-guide-publication boundary, not for every data year. To infer a state's threshold for an intermediate year, use the most recent prior reference row (e.g., a 2008 reading takes the 2006 row).

4. **Do not compare raw total counts across states.** Differences in total fetal death counts between states may reflect reporting policy, not true differences in risk.

5. **Consider higher gestational age thresholds for robust comparisons.** Restricting to 24 or 28 or more weeks of gestation reduces sensitivity to threshold variation, since virtually all states capture deaths at these later gestational ages regardless of their legal reporting floor.

## Metadata Reference

The file `reporting_thresholds.csv` contains one row per state at each of five reference years (1997, 2006, 2014, 2022, 2023 — the user-guide-publication boundaries). It is **not** a complete state-by-year matrix. Columns:

| Column | Description |
|---|---|
| `state_fips` | Two-digit FIPS code |
| `state_name` | Full state name |
| `year` | Reference year for the threshold |
| `threshold_type` | Category: `weeks_only`, `weeks_or_grams`, `grams_only`, `weeks_16`, `weeks_12`, `all_periods` |
| `threshold_weeks` | Minimum gestational age in completed weeks (blank if weight-only) |
| `threshold_grams` | Minimum birth weight in grams (blank if weeks-only) |
| `logic` | `OR` for disjunctive thresholds, `NA` for single-criterion thresholds |
| `source_document` | Citation for the threshold determination |
| `notes` | Additional context on state-specific rules or changes |
