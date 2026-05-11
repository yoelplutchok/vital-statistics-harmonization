# Version roadmap

The unified U.S. Harmonized Vital Statistics (HVS) resource versions each subproject independently. This roadmap consolidates planned work across both.

## Currently shipped

| Subproject | Version | Coverage | Records | Zenodo |
|---|---|---|---|---|
| Natality | v2.7.0 | 1990–2024 | 138,819,655 | [10.5281/zenodo.19868835](https://doi.org/10.5281/zenodo.19868835) |
| Linked birth–infant death | v2.7.0 (bundled) | 2005–2023 | 74,943,824 | (same deposit as natality) |
| Fetal death | v2.0.0 | 1992–2022 (excl. 2003–2004) | 1,634,195 | [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) |

A new unified Zenodo deposit covering all three products under the HVS umbrella is planned.

## Planned

### Fetal death V2.1 — add 2003 and 2004 transition years

Both years use distinct, non-uniform transition layouts (1351-byte and 1501-byte records respectively, with mixed 1989/2003-revision content). NCHS publishes a separate `fetaldeath0304problems.pdf` documenting their idiosyncrasies. Brings fetal-death coverage to 1992–2022 (31 consecutive years).

**Status:** scoped. Layout reconstruction needed; cross-era harmonization rules already in place from V2.0 should apply.

### Joint-use convenience layer

Ship demographically-stratified live-birth denominators inside the fetal-death deposit so users can compute fetal mortality rates without loading the full 138.8M-row natality file. Stratifications: maternal race × age × Hispanic origin × year. Source: aggregated from the natality-harmonization output.

**Status: ✅ shipped 2026-05-11.** Output: [`fetal_death/stratified_denominators.csv`](fetal_death/stratified_denominators.csv) (4,906 strata × 29 years; per-year sums match natality validation target byte-exact 29/29). Build: [`shared/helpers/build_stratified_denominators.py`](shared/helpers/build_stratified_denominators.py). Cross-product column-name reconciliation: [`shared/helpers/canonical_join_keys.py`](shared/helpers/canonical_join_keys.py). User docs: [`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md). Known gap: 4-category bridged race is null 2018–2022 (NCHS source); joint stratified-by-race rates available for 24 of 29 joint-coverage years.

### Cross-product validation notebook

A single notebook that computes fetal mortality, perinatal mortality, and infant mortality rates by demographic stratum using all three products jointly, and matches each cell against the corresponding *NVSR Fetal & Perinatal Mortality* table. Demonstrates the manuscript's "designed for joint use" claim from outside the manuscript.

**Status:** stub at [`notebooks/joint_use_demo.ipynb`](notebooks/joint_use_demo.ipynb).

### Fetal death V3 — extend backward to 1982

Parse 1982–1991 fetal-death files. Spans the 1978-revision (1982–1988) and the early 1989-revision (1989–1991) layouts. Larger, multi-era undertaking; would bring fetal-death coverage to 1982–2022 (41 years).

**Status:** scoped. No layout reconstruction yet attempted.

### Natality forward extension

As NCHS publishes the natality, linked, and fetal-death source files for 2025+, those years will be added to the harmonized files. The harmonization scheme is forward-extensible by adding entries to the era-specific record-layout CSVs; no retroactive schema changes are needed.

**Status:** mechanical. Triggered by NCHS release.

### Manuscript

A Data Resource Profile manuscript covering all three products as a unified HVS resource, modeled on the Human Mortality Database paper (IJE 2015), is in active drafting. Drafts in [`paper/`](paper/).

**Status:** drafting.

## Out of scope (no planned work)

- **Fetal-death cause-of-death codes pre-2014.** Structurally absent from the public-use file. Available only via the NCHS Research Data Center (restricted-use application).
- **State-level identifiers in the V1-era fetal-death public-use files (2005+).** Suppressed by NCHS at source.
- **1989/2003 maternal-education bridge.** Years-of-schooling and degree-level concepts are not 1:1 mappable; bridging would impose modeling choices best left to the analyst. Both fields are preserved in the harmonized schema.
- **Census record linkage and the NCHS RDC geographic-identifier files.** Restricted-use; outside the public-use HVS scope.

## How to propose a roadmap change

Open an issue against this repository describing the proposed change, the impact on existing released versions, and any reproducibility implications.
