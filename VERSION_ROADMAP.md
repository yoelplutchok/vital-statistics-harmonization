# Version roadmap

The unified U.S. Harmonized Vital Statistics (HVS) resource versions each subproject independently. This roadmap consolidates planned work across both.

## Currently shipped

| Subproject | Version (repo) | Latest Zenodo | Coverage | Records | Zenodo (latest deposited) |
|---|---|---|---|---|---|
| Natality | **v3.0.0** (1968–2024 backward extension; built on the v2.8.0 column-name rename; not yet deposited) | v2.7.0 | 1968–2024 | 201,161,456 | [10.5281/zenodo.19868835](https://doi.org/10.5281/zenodo.19868835) (v2.7.0) |
| Linked birth–infant death | **v4.0.0** (1983–2023 cohort backward extension; permanent 1992–1994 NCHS-linkage gap; bundled with natality v3.0.0; canonical parquet filename `natality_v3_linked_*` retained per the schema-family convention; not yet deposited) | v2.7.0 | 1983–2023 | 149,386,620 | (same deposit as natality) |
| Fetal death | **v2.4.0** (V2.1 2003+2004 + V3a 1989-1991 + V3b 1982-1988 + latest-year refresh 2023+2024; H8 dtype reconciliation) | v2.0.0 | 1982–2024 | 2,427,233 | [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) (v2.0.0) |

The natality v3.0.0 and fetal-death v2.4.0 in-repo states are pending Zenodo deposit. A new unified Zenodo deposit covering all three products under the HVS umbrella is planned; the per-subproject deposits will be updated alongside.

## Shipped in-repo (pending Zenodo deposit)

- **Fetal death V2.1** (2003–2004) + **V3a** (1989–1991) + **V3b** (1982–1988) + **v2.4.0** latest-year refresh (2023–2024) → **1982–2024**, 2,427,233 records. See [`fetal_death/ABOUT_THIS_RELEASE.md`](fetal_death/ABOUT_THIS_RELEASE.md).
- **Joint-use convenience layer** (2026-05-11): [`fetal_death/stratified_denominators.csv`](fetal_death/stratified_denominators.csv) (4,906 strata × **29 years: 1992–2002 + 2005–2022**; CSV not yet extended to 2023–2024), [`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md), [`shared/helpers/canonical_join_keys.py`](shared/helpers/canonical_join_keys.py).
- **Cross-product demos**: [`notebooks/joint_use_demo.ipynb`](notebooks/joint_use_demo.ipynb), [`notebooks/paper_companion.ipynb`](notebooks/paper_companion.ipynb), Tier-2 worked examples under [`notebooks/`](notebooks/).
- **Matched multiples** (C8.16): fourth HVS product — [`matched_multiples/`](matched_multiples/).

## Planned

### Convenience CSV year extension

Extend `live_births_by_year.csv` and `stratified_denominators.csv` through 2023–2024 (optional; users can recompute from natality parquets today).

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
