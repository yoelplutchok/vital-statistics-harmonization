# Version roadmap

The unified U.S. Harmonized Vital Statistics (HVS) resource versions each subproject independently. This roadmap consolidates planned work across both.

## Currently shipped

| Subproject | Version (repo) | Coverage | Records | In unified HVS Zenodo |
|---|---|---|---|---|
| Natality | **v3.0.0** (1968–2024; v2.8.0 column rename) | 1968–2024 | 201,161,456 | v1.0.1 parquets; **249/249** validation in v1.0.2 docs |
| Linked birth–infant death | **v4.0.0** (1983–2023 cohort; permanent 1992–1994 gap; parquet prefix `natality_v3_linked_*`; LINK-ICD10 derived 100 cols) | 1983–2023 | 149,386,620 | v1.0.1 parquets; **100** cols / gate `22a4523d…` in v1.0.2 docs |
| Fetal death | **v2.4.0** (V2.1 + V3a + V3b + 2023–2024) | 1982–2024 | 2,427,233 | yes (unchanged v1.0.1) |
| Matched multiples | **C8.16** (3 NCHS windows; MM-T2 **143/143** validation) | 1995–1997 + 1995–2000 + 2016–2020 | 1,665,568 | v1.0.1 parquets; **143/143** targets in v1.0.2 docs |

**Unified deposit (version-of-record):** [10.5281/zenodo.20326150](https://doi.org/10.5281/zenodo.20326150). **v1.0.1** published 2026-05-21 (seven harmonized/derived parquets + docs/metadata zip + `SHA256SUMS.txt`). **v1.0.2** (docs-only; staged in-repo 2026-05-26): refresh validation comparison tables and deposit metadata to **249/249** natality, linked **100** columns (`22a4523d…`), matched multiples **143/143** — **parquets unchanged** from v1.0.1. **Public GitHub:** [yoelplutchok/vital-statistics-harmonization](https://github.com/yoelplutchok/vital-statistics-harmonization) at commit `08a2287` (v1.0.1; parquets on Zenodo, not in git).

**Superseded single-product Zenodo deposits (immutable):** natality + linked [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074); fetal death v2.0.0 (1992–2022) [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571). Legacy description-only patches on those concept DOIs are deferred per user 2026-05-21.

## Shipped in-repo (also on Zenodo v1.0.1)

- **Fetal death V2.1** (2003–2004) + **V3a** (1989–1991) + **V3b** (1982–1988) + **v2.4.0** latest-year refresh (2023–2024) → **1982–2024**, 2,427,233 records. See [`fetal_death/ABOUT_THIS_RELEASE.md`](fetal_death/ABOUT_THIS_RELEASE.md).
- **Joint-use convenience layer** (2026-05-11; CSV years extended 2026-05-20 D-prep.8): [`fetal_death/stratified_denominators.csv`](fetal_death/stratified_denominators.csv) (4,990 strata × **31 years: 1992–2002 + 2005–2024**), [`fetal_death/live_births_by_year.csv`](fetal_death/live_births_by_year.csv) (28 years: 1995–2002 + 2005–2024), [`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md), [`shared/helpers/canonical_join_keys.py`](shared/helpers/canonical_join_keys.py).
- **Cross-product demos**: [`notebooks/joint_use_demo.ipynb`](notebooks/joint_use_demo.ipynb) plus the Tier-2 worked examples under [`notebooks/`](notebooks/).
- **Matched multiples** (C8.16): fourth HVS product — [`matched_multiples/`](matched_multiples/).

## Planned

### Natality forward extension

As NCHS publishes the natality, linked, and fetal-death source files for 2025+, those years will be added to the harmonized files. The harmonization scheme is forward-extensible by adding entries to the era-specific record-layout CSVs; no retroactive schema changes are needed.

**Status:** mechanical. Triggered by NCHS release.

### Manuscript

A Data Resource Profile manuscript covering all four products as a unified HVS resource, modeled on the Human Mortality Database paper (IJE 2015), is in active drafting. The Zenodo DOI and GitHub URL cite v1.0.1 / `08a2287`.

**Status:** draft submission readiness (author markers, companion-notebook regen on build host, optional IJE Key Features template conversion).

## Out of scope (no planned work)

- **Fetal-death cause-of-death codes pre-2014.** Structurally absent from the public-use file. Available only via the NCHS Research Data Center (restricted-use application).
- **State-level identifiers in the V1-era fetal-death public-use files (2005+).** Suppressed by NCHS at source.
- **1989/2003 maternal-education bridge.** Years-of-schooling and degree-level concepts are not 1:1 mappable; bridging would impose modeling choices best left to the analyst. Both fields are preserved in the harmonized schema.
- **Census record linkage and the NCHS RDC geographic-identifier files.** Restricted-use; outside the public-use HVS scope.

## How to propose a roadmap change

Open an issue against this repository describing the proposed change, the impact on existing released versions, and any reproducibility implications.
