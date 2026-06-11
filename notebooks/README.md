# Cross-product notebooks

Worked examples that span more than one of the three products. Each notebook should be runnable end-to-end against the shipped parquets (or a downloaded subset for partial demos).

## Planned

### `joint_use_demo.ipynb` — fetal mortality rate, two stratifications

Built by [`_build_joint_use_demo.py`](_build_joint_use_demo.py); loads all three parquets (natality, linked, fetal-death), applies each product's canonical analytic filter, and computes fetal mortality rates in two demonstrations:

- **Section A.** 2022 fetal mortality rate by maternal age band (8 NVSR-standard bands `<15 / 15-19 / 20-24 / 25-29 / 30-34 / 35-39 / 40-44 / 45+`), validated byte-exact against *NVSR 73-09* Table 4 (8 cells; all PASS). Aggregate FMR 5.4778 per 1,000 matches the NVSR-published 5.48 within rounding.
- **Section B.** 2017 fetal mortality rate by maternal race (last year `maternal_race_bridged` is non-null in both products — NCHS dropped MBRACE from 2018+ public-use files). Joint-use machinery demonstration.

The pseudocode template is in [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md). The notebook is regenerable deterministically from the builder script against new parquet versions.

### `era_boundary_walkthrough.ipynb` — what changes at each NCHS layout boundary

A pedagogical notebook that loads the same demographic stratum across each of the era boundaries described in Table 1 of the manuscript, and shows where the harmonization made decisions (renames, value-level normalizations, comparability classifications). Useful for new users and reviewers who want to verify the harmonization choices.

## Worked examples (Phase C Tier-2, C8.10)

### `maternal_age_stratified_imr.ipynb` — IMR by maternal age, cohort-linked 2005-2023

Built by [`_build_maternal_age_stratified_imr.py`](_build_maternal_age_stratified_imr.py); reproduces the cohort-linked file's published 2022 infant mortality cells byte-exact (7 cells from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4) and the 19-year unweighted-IMR time series 2005-2023 (5 byte-exact cells for the years the user-guide reports unweighted counts: 2015 + 2020 + 2021 + 2022 + 2023). Section 3 extends to a maternal-age stratification (6 NCHS bands: `<20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+`) as a machinery demo; NCHS publishes IMR-by-maternal-age only for the period-linked file (NVSR 73-05 Ely+Driscoll 2024), so the cohort-linked numbers in Section 3 are not directly comparable to a published NVSR cell — Section 4 documents the cohort-vs-period source distinction explicitly. Total of 12 NCHS-published cells reproduced byte-exact; maternal-age U-shape (minimum at 30-34) confirmed with row-count + death-count conservation across age bands.

### `preterm_outcomes_time_series.ipynb` — preterm-birth secular trends 1990-2024 (cross-product)

Built by [`_build_preterm_outcomes_time_series.py`](_build_preterm_outcomes_time_series.py); loads natality + linked + fetal-death parquets and reproduces the natality preterm-birth rate time series 1990-2023 byte-exact against **34 NVSR-cited cells** in `external_validation_targets_v1.csv` (every year 1990-2023; 19 cells at tight tolerance ≤0.05 for the 2014+ OE-based era; 15 cells at wider tolerance 0.15 for the 1990-2004 LMP-based era — the 2014 OE-based methodology shift drops the measured preterm rate from 11.39% to 9.57% by methodology change, not by real incidence drop). Section 2 cross-checks 19 joint-year natality-vs-linked preterm rates within the C8.4-documented 0.01 pct-pt drift bound. Section 3 reproduces 4 FD gestation-stratified cells (2014 + 2022, early 20-27wk + late 28+wk) against NVSR 73-09 Table 1 under the validator-documented expected-diff (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown). The 43-year FD early/late gestation time series 1982-2024 is produced end-to-end; conservation invariant `under_20wk + early + late + unknown = NVSR-universe total` PASSes byte-exact for 2022. Section 4 documents the 2014 OE-shift, cohort-vs-period file distinction, FD `preterm` column semantics vs natality `preterm_lt37`, and the FD canonical-filter choice (`tabulation_flag == 2`).

### `cross_race_fetal_mortality.ipynb` — cross-era race-stratified fetal mortality 1990-2024

Built by [`_build_cross_race_fetal_mortality.py`](_build_cross_race_fetal_mortality.py); loads fetal-death + natality parquets, applies the canonical `tabulation_flag == 2 AND residence_status != 4` filter, and produces a 35-year (1990-2024) race-stratified FMR time series demonstrating the analytic value of the V3a (1989-1991) + V3b (1982-1988) backward extensions shipped 2026-05-12. Section 1 reproduces **7 NVSR 73-09 Table A 2022 race-stratified FMR cells byte-exact** (Total 5.48 / NH AIAN 7.22 / NH Asian 3.70 / NH Black 10.05 / NH NHOPI 10.36 / NH White 4.48 / Hispanic 4.63 per 1,000) via cross-validation against `joint_use_demo` Section B. Section 2 asserts the per-year `sum(bridged_1..4) + null == total` conservation invariant for every year 1982-2013 (32 years across V3b + V3a + V2 + V2.1 + V1_pre_OE) and reports per-era B3 1-digit-recode null fractions (V3b 2.65-3.27%, V3a 0.075-0.191%, V2/V2.1/V1_pre_OE ~0%). Section 3 produces the 35-year cross-era race-stratified FMR panel via bilateral race-coding methodology — 1990-2013 uses `maternal_race_bridged` on both numerator and denominator (bridged 4-cat including Hispanic); 2014+ uses NH-only bridged 4-cat on both sides (`race_hispanic_revised` collapsed for FD; `maternal_race_ethnicity_5` collapsed for natality). The 2013→2014 race-coding-methodology boundary is documented in Section 4 (Hispanic disaggregation drives a -0.87 / -1.09 step for White / Black, which is a methodology shift, not real demographic change; distinct from the OE gestational-age shift that affects notebook 2). Black-vs-White FMR mean ratio 2.15x across all 35 joint years (range 2.04-2.27x). The B3 1-digit-recode caveats (V3b code 7 + code 9 → null per 2026-05-12T18:30Z; V3a code 09 → null per 2026-05-12T14:30Z) are documented inline.

## Status

- `joint_use_demo.ipynb` — shipped.
- `maternal_age_stratified_imr.ipynb` — shipped.
- `preterm_outcomes_time_series.ipynb` — shipped.
- `cross_race_fetal_mortality.ipynb` — shipped.
- `education_gradient.ipynb`, `state_reporting_quirks.ipynb` — worked examples.
- `era_boundary_walkthrough.ipynb` — stub.
