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

## Status

- `joint_use_demo.ipynb` — **shipped 2026-05-11** (Task 2 in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `paper_companion.ipynb` — **shipped 2026-05-11** (Task 4 in `NEXT_STEPS.md` §15; see receipt under `RECEIPTS/`).
- `era_boundary_walkthrough.ipynb` — stub.
