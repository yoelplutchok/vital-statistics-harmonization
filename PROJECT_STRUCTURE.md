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

- **A new researcher** should read this file then `README.md` then `docs/JOINT_USE_GUIDE.md`, then load a single product following its `GETTING_STARTED.md`.
- **An LLM agent** asked to add a feature, fix a bug, or extend coverage should grep this file for the relevant product subdirectory, read the target product's `README.md` and `scripts/` layout, then proceed.
- **A reader of the manuscript** should map paper claims to artifacts via the validation tables in each `metadata/` directory.
