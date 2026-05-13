# Cross-product notebooks

Worked examples that span more than one of the three products. Each notebook should be runnable end-to-end against the shipped parquets (or a downloaded subset for partial demos).

## Planned

### `joint_use_demo.ipynb` — fetal mortality rate, two stratifications

Built by [`_build_joint_use_demo.py`](_build_joint_use_demo.py); loads all three parquets (natality, linked, fetal-death), applies each product's canonical analytic filter, and computes fetal mortality rates in two demonstrations:

- **Section A.** 2022 fetal mortality rate by maternal age band (8 NVSR-standard bands `<15 / 15-19 / 20-24 / 25-29 / 30-34 / 35-39 / 40-44 / 45+`), validated byte-exact against *NVSR 73-09* Table 4 (8 cells; all PASS). Aggregate FMR 5.4778 per 1,000 matches the NVSR-published 5.48 within rounding.
- **Section B.** 2017 fetal mortality rate by maternal race (last year `maternal_race_bridged` is non-null in both products — NCHS dropped MBRACE from 2018+ public-use files). Joint-use machinery demonstration; *NVSR* cell-level validation deferred to the paper companion notebook.

The pseudocode template is in [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md). The notebook is regenerable deterministically from the builder script against new parquet versions.

### `paper_companion.ipynb` — reproduce every numeric claim in the manuscript

Built by [`_build_paper_companion.py`](_build_paper_companion.py); enumerates the 55 numeric claims in `paper/draft_v2_hmd_styled.md` (cataloged C01–C55), recomputes each from the harmonized parquets, schema CSVs, and validation CSVs, and ships a pass/fail synthesis to `paper_companion_results.csv`. Section coverage: top-line record + column counts; annual averages; Table 1 era boundaries; harmonized vs derived split; `within_era` columns; value-level normalizations; NVSR validation pass counts (183/183 + 33/35-byte-exact-plus-2-by-1 + 29/29 counts + 26/26 rates); byte-level parse verification; cause-of-death missingness 2018+; citation-only and out-of-monorepo claims. Findings drive Task 5 (manuscript trim) precision-edits.

### `era_boundary_walkthrough.ipynb` — what changes at each NCHS layout boundary

A pedagogical notebook that loads the same demographic stratum across each of the era boundaries described in Table 1 of the manuscript, and shows where the harmonization made decisions (renames, value-level normalizations, comparability classifications). Useful for new users and reviewers who want to verify the harmonization choices.

## Worked examples (Phase C Tier-2, C8.10)

### `maternal_age_stratified_imr.ipynb` — IMR by maternal age, cohort-linked 2005-2023

Built by [`_build_maternal_age_stratified_imr.py`](_build_maternal_age_stratified_imr.py); reproduces the cohort-linked file's published 2022 infant mortality cells byte-exact (7 cells from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4) and the 19-year unweighted-IMR time series 2005-2023 (5 byte-exact cells for the years the user-guide reports unweighted counts: 2015 + 2020 + 2021 + 2022 + 2023). Section 3 extends to a maternal-age stratification (6 NCHS bands: `<20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+`) as a machinery demo; NCHS publishes IMR-by-maternal-age only for the period-linked file (NVSR 73-05 Ely+Driscoll 2024), so the cohort-linked numbers in Section 3 are not directly comparable to a published NVSR cell — Section 4 documents the cohort-vs-period source distinction explicitly. Total of 12 NCHS-published cells reproduced byte-exact; maternal-age U-shape (minimum at 30-34) confirmed with row-count + death-count conservation across age bands.

### `preterm_outcomes_time_series.ipynb` — preterm-birth secular trends 1990-2024 (cross-product)

Built by [`_build_preterm_outcomes_time_series.py`](_build_preterm_outcomes_time_series.py); loads natality + linked + fetal-death parquets and reproduces the natality preterm-birth rate time series 1990-2023 byte-exact against **34 NVSR-cited cells** in `external_validation_targets_v1.csv` (every year 1990-2023; 19 cells at tight tolerance ≤0.05 for the 2014+ OE-based era; 15 cells at wider tolerance 0.15 for the 1990-2004 LMP-based era — the 2014 OE-based methodology shift drops the measured preterm rate from 11.39% to 9.57% by methodology change, not by real incidence drop). Section 2 cross-checks 19 joint-year natality-vs-linked preterm rates within the C8.4-documented 0.01 pct-pt drift bound. Section 3 reproduces 4 FD gestation-stratified cells (2014 + 2022, early 20-27wk + late 28+wk) against NVSR 73-09 Table 1 under the validator-documented expected-diff (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown). The 43-year FD early/late gestation time series 1982-2024 is produced end-to-end; conservation invariant `under_20wk + early + late + unknown = NVSR-universe total` PASSes byte-exact for 2022. Section 4 documents the 2014 OE-shift, cohort-vs-period file distinction, FD `preterm` column semantics vs natality `preterm_lt37`, and the FD canonical-filter choice (`tabulation_flag == 2`).

### `cross_race_fetal_mortality.ipynb` — V3a/V3b race-stratified FD (planned)

Will demonstrate the V3a (1989-1991) and V3b (1982-1988) backward extensions with B3 1-digit MRACE recode caveats documented. Pending C8.10c PRE-FLIGHT.

## Status

- `joint_use_demo.ipynb` — **shipped 2026-05-11** (Task 2 in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `paper_companion.ipynb` — **shipped 2026-05-11** (Task 4 in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `maternal_age_stratified_imr.ipynb` — **shipped 2026-05-13** (C8.10a in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `preterm_outcomes_time_series.ipynb` — **shipped 2026-05-13** (C8.10b in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `cross_race_fetal_mortality.ipynb` — pending C8.10c.
- `era_boundary_walkthrough.ipynb` — stub.
