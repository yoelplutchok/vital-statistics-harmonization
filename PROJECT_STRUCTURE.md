# Project Structure

This document is the canonical map of the repository — written for both human readers (skim the headings) and LLM agents (every important location is named, with the purpose of each file/directory in one line).

## Top-level layout

```
vital-statistics-harmonization/
├── README.md                 Unified overview (start here for new readers)
├── PROJECT_STRUCTURE.md      This file (canonical map)
├── VERSION_ROADMAP.md        V2.1, V3, joint-use, etc.
├── CITATION.cff              Citation metadata
├── LICENSE                   CC BY 4.0 (data) + MIT (code)
├── .gitignore                Excludes parquets, zips, raw NCHS data
├── requirements.txt          Combined Python dependencies
├── docs/                     Cross-product documentation
├── natality/                 Natality + linked birth–infant death subproject
├── fetal_death/              Fetal death subproject
├── notebooks/                Cross-product worked examples
├── paper/                    Data Resource Profile manuscript drafts
├── figures/                  Cross-product figures
└── shared/helpers/           Python utilities used across products
```

## docs/

Documentation that spans both subprojects. Each file should answer a question that doesn't fit neatly inside one product.

| File | Purpose |
|---|---|
| `JOINT_USE_GUIDE.md` | How to compute rates that need both numerator and denominator (fetal mortality rate, perinatal mortality rate, infant mortality rate). Specifies the canonical join keys and aligned strata. |
| `PRIOR_ART.md` | The literature gap that motivates the harmonization. Cited from the Data Resource Profile manuscript. |

Subproject-specific docs (codebooks, FAQs, comparability notes) live inside `natality/docs/` and `fetal_death/` respectively.

## natality/

Natality 1990–2024 plus linked birth–infant death 2005–2023, mirrored from the [yoelplutchok/natality-harmonization](https://github.com/yoelplutchok/natality-harmonization) repo (v2.8.0 in-repo state, last Zenodo deposit v2.7.0).

| Path | Purpose |
|---|---|
| `natality/README.md` | Subproject overview |
| `natality/REPRODUCING.md` | End-to-end pipeline rerun instructions |
| `natality/docs/ABOUT_THIS_RELEASE.md` | What's in the current release, validation summary |
| `natality/docs/CODEBOOK.md` | Variable-by-variable definitions |
| `natality/docs/COMPARABILITY.md` | Cross-era comparability notes |
| `natality/docs/FAQ.md` | Common questions |
| `natality/docs/GETTING_STARTED.md` | First-load tutorial |
| `natality/docs/VALIDATION.md` | Validation methodology |
| `natality/scripts/01_import/` | Parsing fixed-width NCHS zips into yearly parquets |
| `natality/scripts/03_harmonize/` | Mapping per-era raw fields to the harmonized schema |
| `natality/scripts/04_derive/` | Computing derived analytic indicators |
| `natality/scripts/05_validate/` | Per-target NVSR validation scripts |
| `natality/scripts/06_convenience/` | Pre-computed convenience subsets |
| `natality/scripts/07_figures/` | Paper figure generation |
| `natality/metadata/harmonized_schema.csv` | Authoritative column schema |
| `natality/metadata/external_validation_targets_v1.csv` | Natality NVSR targets |
| `natality/metadata/external_validation_targets_v3_linked.csv` | Linked-file NVSR targets |
| `natality/metadata/file_inventory.csv` | Source-zip SHA-256 checksums |
| `natality/output/validation/` | Per-target pass/fail tables (CSV + Markdown) |
| `natality/notebooks/quickstart.ipynb` | First-load demo |
| `natality/figures/` | fig1_pipeline, fig2_timeline, fig3_availability, fig4_validation |

## fetal_death/

Fetal death 1992–2022 (with 2003–2004 deferred to V2.1), mirrored from the [yoelplutchok/fetal-death-harmonization](https://github.com/yoelplutchok/fetal-death-harmonization) repo (v2.0.1 import). Top-level docs live at the subproject root rather than under `docs/` because the existing deposit shipped them flat.

| Path | Purpose |
|---|---|
| `fetal_death/README.md` | Subproject overview, version roadmap |
| `fetal_death/ABOUT_THIS_RELEASE.md` | V2.0 release notes, B1–B6 cross-era fixes |
| `fetal_death/ABOUT_SOURCE_DATA.md` | Description of NCHS source files |
| `fetal_death/CODEBOOK.md` | Variable-by-variable definitions |
| `fetal_death/COMPARABILITY.md` | Cross-era comparability classification |
| `fetal_death/FAQ.md` | Common questions |
| `fetal_death/GETTING_STARTED.md` | First-load tutorial |
| `fetal_death/REPRODUCING.md` | End-to-end pipeline rerun |
| `fetal_death/REPORTING_THRESHOLDS.md` | State-by-year reporting threshold notes |
| `fetal_death/V2_1992_LAYOUT_DECISIONS.md` | 1989-revision layout reconstruction notes |
| `fetal_death/PROVENANCE.md` | SHA-256 checksums for shipped artifacts |
| `fetal_death/scripts/01_import/` | Parsing 1992–2022 fixed-width zips |
| `fetal_death/scripts/03_harmonize/` | Cross-era harmonization (B1–B6 normalizations) |
| `fetal_death/scripts/04_derive/` | Derived analytic indicators |
| `fetal_death/scripts/05_validate/` | NVSR validation scripts (v2.0 covers V2 era) |
| `fetal_death/scripts/run_pipeline.py` | End-to-end orchestrator |
| `fetal_death/tests/` | Smoke tests for shipped parquets |
| `fetal_death/harmonized_schema.csv` | Authoritative column schema |
| `fetal_death/external_validation_targets.csv` | NVSR validation targets |
| `fetal_death/validation_results.csv` | Per-target pass/fail table |
| `fetal_death/file_inventory.csv` | Source-zip SHA-256 checksums |
| `fetal_death/record_layout_*.csv` | Per-era byte-position mappings |
| `fetal_death/reporting_thresholds.csv` | State-by-year reporting thresholds |
| `fetal_death/variable_crosswalk_working.csv` | Per-era raw-to-harmonized mapping |
| `fetal_death/live_births_by_year.csv` | Convenience denominator file |
| `fetal_death/quickstart.py` | First-load demo |
| `fetal_death/figures/` | fig1_nvsr_counts, fig2_fmr_trend, fig3_within_era_demo, companion figs |

## paper/

Data Resource Profile manuscript drafts.

| File | Status |
|---|---|
| `draft_v1_ipums_styled.md` | First draft, modeled on IPUMS-International (IJE 2017). Superseded. |
| `draft_v2_hmd_styled.md` | Current preferred draft, modeled on the Human Mortality Database (IJE 2015). HMD is a much closer template because it harmonizes one class of vital-statistics data across versions. |

Style and structural decisions are noted in commit messages and the agent transcript.

## notebooks/

Cross-product worked examples. Each notebook should be runnable end-to-end against the shipped parquets.

| Notebook | Status | Purpose |
|---|---|---|
| `joint_use_demo.ipynb` | Stub | Compute fetal mortality rate by maternal race using all three products jointly. To be filled in. |
| `paper_companion.ipynb` | Stub | Reproduce every numeric claim in the paper from the parquets. To be filled in. |

## shared/helpers/

Python utilities used by both subprojects (e.g., common parsing helpers, schema validators). Empty until cross-cutting code accumulates.

## Naming conventions

- **V1** in the fetal-death subproject refers to the *2005–2022 era* (2003-revision transition window). In the natality subproject, era boundaries use different names; see each subproject's COMPARABILITY for the era nomenclature there.
- **V2** in the fetal-death subproject refers to the *1992–2002 era* (1989-revision uniform window).
- **HVS** = U.S. Harmonized Vital Statistics; the umbrella name for the unified resource described in the manuscript.
- **NVSR** = National Vital Statistics Reports (the NCHS publication series whose figures are the validation gold standard).
- **NCHS** = National Center for Health Statistics.

## Where to start

- **A new researcher** should read this file then `README.md` then `docs/JOINT_USE_GUIDE.md`, then load a single product following its `GETTING_STARTED.md`. For cross-product use cases, also read [`docs/WORKED_EXAMPLE_FAQ.md`](docs/WORKED_EXAMPLE_FAQ.md).
- **An LLM agent** asked to add a feature, fix a bug, or extend coverage should grep this file for the relevant product subdirectory, read the target product's `README.md` and `scripts/` layout, then proceed.
- **A reader of the manuscript** should map paper claims to artifacts via the validation tables in each `metadata/` directory.

## Build-order DAG

Each subproject is a five-stage pipeline that consumes raw NCHS zips and produces parquet artifacts. The stages run in order; later stages depend on earlier stages' outputs. Cross-product analyses consume the three derived parquets jointly via notebooks in `notebooks/`.

```
   raw_data/                               raw NCHS zips (97 total; SHA-pinned in docs/NCHS_SOURCE_MANIFEST.md)
       │
       ▼
   01_import/        parse_*               yearly fixed-width → per-year Parquet
       │                                  outputs: output/yearly_clean/<product>_<year>_*.parquet
       │
       ▼
   03_harmonize/     harmonize_*           per-year Parquet → unified harmonized Parquet
       │                                  outputs: output/harmonized/<product>_harmonized.parquet
       │
       ▼
   04_derive/        derive_*              harmonized → harmonized + derived indicators
       │                                  outputs: output/harmonized/<product>_harmonized_derived.parquet (SHIPPED)
       │
       ▼
   05_validate/      validate_*            harmonized_derived → per-target PASS/FAIL tables
                                          outputs: <product>/output/validation/*.{csv,md}
```

Cross-product joint analyses (`notebooks/joint_use_demo.ipynb`, `notebooks/maternal_age_stratified_imr.ipynb`, etc.) consume the three `*_harmonized_derived.parquet` files and the shared helpers in `shared/helpers/`. They are independent of the per-product validate stage; failure of a validator does not affect notebook execution but should be investigated before publication.

The 02_clean_yearly (natality only) stage is empty in the current pipeline — natality's `parse_all_v1_years.py` writes the yearly clean parquets directly. The slot is preserved in the layout for symmetry with potential future per-year cleaning logic.

**Reproducing end-to-end.** Drivers exist at [`scripts/_drive_fetal_death_benchmark.py`](scripts/_drive_fetal_death_benchmark.py) (43-year fetal-death chain) and [`scripts/_drive_natality_benchmark.py`](scripts/_drive_natality_benchmark.py) (natality + linked 6-stage chain). Both consume the SHA-pinned `uv.lock` environment. The C8.13 F.5 benchmark documents wall-clock per stage at [`docs/PIPELINE_TIMING_BENCHMARK.md`](docs/PIPELINE_TIMING_BENCHMARK.md). Re-running the pipelines produces byte-identical parquets (H10 reproducibility gate; validated empirically at C8.13).

## Notebook-deps graph

Each notebook lists its parquet inputs and helper-module imports. All notebooks read from the three shipped `*_harmonized_derived.parquet` files; some additionally consume the convenience denominator file.

| Notebook | Fetal-death derived | Natality derived | Linked derived | `shared/helpers/` | NVSR validation |
|---|---|---|---|---|---|
| `joint_use_demo.ipynb` | ✓ (Sections A, B, C) | ✓ (Section A denom, Section C denom) | ✓ (Section C ENN) | `canonical_join_keys` | A: 8/8 cells *NVSR 73-09* Table 4; B: 7/7 *NVSR 73-09* Table A; C: sub-components |
| `paper_companion.ipynb` | ✓ | ✓ | ✓ | (built post-Task 4) | Reproduces every manuscript numeric |
| `maternal_age_stratified_imr.ipynb` (C.6.a) | — | — | ✓ | (linked-only) | Per-stratum cells vs *NVSR* IMR table |
| `preterm_outcomes_time_series.ipynb` (C.6.b) | ✓ | ✓ | ✓ | `canonical_join_keys` | Per-year preterm cells |
| `cross_race_fetal_mortality.ipynb` (C.6.c) | ✓ | — | — | (fetal-only) | 2017 bridged-race + 2022 single-race |
| `education_gradient.ipynb` (C.6.d, future) | — | ✓ | — | — | TBD (C8.15) |
| `state_reporting_quirks.ipynb` (C.6.e, future) | ✓ | ✓ | — | — | Documentary; no NVSR cells (geography suppressed) |

Builder scripts at `notebooks/_build_*.py` produce the executed `.ipynb` deterministically. Re-running the builder against the current parquets reproduces the notebook cell-by-cell.

The `shared/helpers/` directory contains the cross-product Python utilities used by multiple notebooks and pipelines:

- `canonical_join_keys.py` — maps each product's residence-status column to a canonical name; provides `to_canonical_natality()` / `to_canonical_fetal_death()`
- `build_stratified_denominators.py` — produces `fetal_death/stratified_denominators.csv` (the 4,906-cell long-format file used by joint-use rate computations)
- `build_timeline_figure.py` — produces `figures/fig1_coverage_timeline.{pdf,png}` (manuscript Figure 1 candidate)

## Which-file-by-use-case matrix

Given an analytic question, this matrix points at the right starting file.

| If you want to… | Start with | Filter to apply | Cross-link |
|---|---|---|---|
| Compute fetal mortality rate (unstratified) | `fetal_death/fetal_death_derived.parquet` + `fetal_death/live_births_by_year.csv` | `tabulation_flag == 2 AND residence_status != 4` (numerator) | `docs/JOINT_USE_GUIDE.md` §90 |
| Compute fetal mortality rate by demographic stratum | `fetal_death/fetal_death_derived.parquet` + `fetal_death/stratified_denominators.csv` | as above + groupby stratum | `notebooks/joint_use_demo.ipynb` Section B |
| Compute infant mortality rate (overall or by maternal stratum) | linked `natality_v3_linked_harmonized_derived.parquet` | `residence_status != 4` | `notebooks/maternal_age_stratified_imr.ipynb` |
| Compute perinatal mortality rate | All three derived parquets | per-product canonical filter | `docs/JOINT_USE_GUIDE.md` §128 + `notebooks/joint_use_demo.ipynb` Section C |
| Compute preterm-birth rate (any product, any era) | natality `_derived` (use `preterm_lt37`) | `residence_status != 4` + filter to relevant gestational-age era | `notebooks/preterm_outcomes_time_series.ipynb` |
| Reproduce a specific *NVSR* cell | Per-product `external_validation_targets*.csv` + the corresponding `05_validate/*.py` script | per-product canonical filter | each subproject's `metadata/external_validation_targets*.csv` |
| Understand era boundaries / which years are comparable | `docs/COMPARABILITY.md` (cross-product) + per-product `COMPARABILITY.md` | — | `docs/COMPARABILITY.md` |
| Load the data in R / Stata / SAS | per-product `quickstart.R` / `quickstart.py` | (loader code includes the filter) | `docs/JOINT_USE_GUIDE.md` §174 |
| Query via SQL without Python | `views.sql` at monorepo root (DuckDB views over the parquets) | (views include the filter) | `docs/JOINT_USE_GUIDE.md` §194 |
| Check per-year totals against published *NVSR* figures | per-product `validation_results.csv` + each subproject's `output/validation/*.md` | — | per-subproject `VALIDATION.md` |
| Add a new harmonized column | Per-product `harmonized_schema.csv` (then propagate through 03_harmonize/04_derive scripts) | — | per-subproject `REPRODUCING.md` |
| Investigate a per-year discrepancy from *NVSR* | `<product>/output/validation/<target>_<year>.csv` (PASS/FAIL per cell) | — | per-product `05_validate/` source |
| Cite this resource | `CITATION.cff` + Zenodo concept DOIs | — | `docs/WORKED_EXAMPLE_FAQ.md` |
| Get state-level data | (not available from public-use NCHS files) | — | `docs/WORKED_EXAMPLE_FAQ.md` "How do I get state-level data?" |
