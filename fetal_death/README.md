# U.S. Fetal Death Harmonization Project

A modern, researcher-ready release of harmonized U.S. fetal death microdata for cross-year stillbirth research.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20031571.svg)](https://doi.org/10.5281/zenodo.20031571)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Release Summary (v2.4.0)

| Metric | Value |
|--------|-------|
| Years covered | **1982-2024** (43 contiguous years; seven NCHS layout eras) |
| Total records | **2,427,233** |
| Harmonized variables | 73 |
| Derived variables | 16 (89 total columns) |
| Annual files processed | 43 |
| External validation | **90/90** per-year control-count targets byte-exact under the canonical filter (`tabulation_flag == 2` & `residence_status != 4`; see `external_validation_targets.csv`) |
| NVSR-comparable subset | **1,121,986** records (1,123,940 with `tabulation_flag == 2`; 1,954 foreign-resident exclusions) |
| Cross-era code-system fixes | 5 V2→V1 value-level normalizations (B1, B2, B3, B4, B6) + 3 `within_era` relabels (B5 `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) + 1 partial relabel (`maternal_age`); extended to V3a/V3b per `COMPARABILITY.md` §10 |

Per-era record counts (parquet-derived; sum to 2,427,233): **1982-1988** 421,125 · **1989-1991** 188,909 · **1992-2002** 700,704 · **2003-2004** 107,782 · **2005-2013** 510,528 · **2014-2017** 204,923 · **2018-2024** 293,262. See `CODEBOOK.md` Appendix C8.20 for the authoritative breakdown.

The v2.0.0 Zenodo deposit at [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) covered 1992-2022 (29 years; 2003-2004 deferred). In-repo **v2.4.0** adds V2.1 (2003-2004), V3a (1989-1991), V3b (1982-1988), and 2023-2024. Migration notes: [`migrations/v2.0.0-to-v2.4.0-fetal-death.md`](../migrations/v2.0.0-to-v2.4.0-fetal-death.md).

## About

The fetal death files are produced by NCHS from the National Vital Statistics System. They cover every reported fetal death in the United States — approximately 25,000 to 30,000 per year at >=20 weeks gestation, with total file sizes of 40,000 to 70,000 records including earlier gestational age deaths.

Despite the importance of this data for stillbirth surveillance and perinatal epidemiology, cross-year use has been prohibitively difficult: three revisions of the Standard Report of Fetal Death (1978, 1989, 2003), staggered state adoption, variables that are added/dropped/recoded across revisions, and records in the same annual file following different schemas during transition periods.

**No harmonized longitudinal product previously existed.** This project fills that gap with **43 consecutive years (1982-2024)** in a single Parquet file with one stable schema.

## Quick Start

When downloaded from Zenodo, all files unpack to a single flat directory; the snippets below assume you `cd` into that directory.

```python
import pandas as pd

# Load the derived dataset (includes all harmonized + derived variables)
df = pd.read_parquet("fetal_death_derived.parquet")

# Standard analytic subset: tab_flag=2 (NVSR-tabulated) AND U.S. residents
nvsr = df[(df["tabulation_flag"] == 2) & (df["residence_status"] != 4)]
print(f"{len(nvsr):,} NVSR-comparable fetal deaths across {nvsr['data_year'].nunique()} years")
# 1,121,986 NVSR-comparable fetal deaths across 43 years (1982-2024)
```

See [Getting Started](GETTING_STARTED.md) for more examples.

## Repository Structure (GitHub source layout)

The Zenodo deposit is **flat** — every file lives at the deposit root. The tree below is the layout of the GitHub source repository (https://github.com/yoelplutchok/vital-statistics-harmonization), shown here so users who clone the monorepo can navigate the pipeline. None of these `output/`, `metadata/`, or `docs/` paths exist in a Zenodo download.

```
vital-statistics-harmonization/
├── README.md
├── fetal_death/
│   ├── raw_data/fetal_death/       # NCHS fetal death zips (not committed) — 43 years
│   ├── raw_docs/fetal_death/       # NCHS documentation PDFs + NVSR validation refs
│   ├── harmonized_schema.csv
│   ├── variable_crosswalk_working.csv
│   ├── record_layout_*.csv         # Per-era layouts (1982-2024)
│   ├── scripts/
│   │   ├── run_pipeline.py         # End-to-end orchestrator
│   │   ├── 01_import/              # Parse fixed-width -> per-year Parquet
│   │   ├── 03_harmonize/           # Map era-specific fields -> common schema
│   │   ├── 04_derive/              # Compute 16 derived variables
│   │   └── 05_validate/            # Validation scripts (V1 + V2 + V3a/V3b + latest-year)
│   └── output/ (monorepo root)
│       ├── yearly_clean/           # 43 raw per-year Parquet files (1982-2024)
│       └── harmonized/
│           ├── fetal_death_harmonized.parquet  # 2,427,233 × 73
│           └── fetal_death_derived.parquet     # 2,427,233 × 89
```

## Documentation

All documentation files are at the deposit root in the Zenodo download (under `fetal_death/` in the monorepo).

| Document | Description |
|----------|-------------|
| [About Source Data](ABOUT_SOURCE_DATA.md) | What the NCHS fetal death files are |
| [About This Release](ABOUT_THIS_RELEASE.md) | V2.1 / V3a / V3b / v2.4.0 increments over the v2.0.0 base |
| [Codebook](CODEBOOK.md) | Every variable defined (+ Appendix C8.20 per-era evidence) |
| [Comparability](COMPARABILITY.md) | Cross-year comparability decisions, seven-era structure |
| [Reporting Thresholds](REPORTING_THRESHOLDS.md) | The threshold problem |
| [Getting Started](GETTING_STARTED.md) | How to load and use the data |
| [FAQ](FAQ.md) | Common questions |
| [Reproducing](REPRODUCING.md) | How the data was produced and how to verify it |

## Validation

The shipped parquet has been validated against every per-year fetal death figure NCHS has published under the standard `tabulation_flag==2 & residence_status!=4'` filter, plus detail-cell samples from NVSR 73-09 where applicable.

| Source | Years | Checks | Result |
|--------|-------|--------|--------|
| NVSR 73-09 (Fetal Mortality: United States) | 2005-2024 | Per-year counts + rates | Byte-exact under canonical filter |
| NVSR 57-08 (Fetal & Perinatal Mortality, US 2005) | 1995-2002 | Per-year counts + rates | Byte-exact |
| NCHS Fetal Death User Guides | 1982-2024 (per-year control blocks) | **90/90** control-count cells | All byte-exact |
| NVSR 73-09 detail-cell tables (Tables A, 4, 8, early/late GA) | 2014, 2022 | 19 detail cells | 13 match exactly + 6 documented methodological differences (see below) |

Per-target source citations are in `external_validation_targets.csv`; the per-target pass/fail table is in `validation_results.csv`. The three known stale-guide V2 years (1996, 2001, 2002) are resolved in favor of NVSR 57-08. The V1 era (2005-2022) slice was held byte-identical to its V1.x baseline through all backward extensions.

### Verifying it yourself

Three levels of independent verification, each strictly stronger than the one above:

**Level 1 — confirm what you downloaded matches what was released (10 seconds):**
```bash
shasum -a 256 -c PROVENANCE.sha256
```

**Level 2 — confirm the parquet reproduces published NCHS statistics (1 minute):**
```bash
pip install -r requirements.txt
python scripts/05_validate/validate_external_v2.py    # 1982-2004 + 1992-2002 V2-era paths
python scripts/05_validate/validate_external.py       # 2005-2024 NVSR 73-09 comparison
```
Both scripts load the shipped parquet, recompute counts and rates with the standard NVSR-comparable filter, and print a pass/fail table against the published figures cited in `external_validation_targets.csv`.

**Level 3 — re-derive the parquet from raw NCHS source files (~6 minutes for 43 years on a standard laptop):**
Download the 43 raw zips listed in `file_inventory.csv` (SHA-256s provided) from `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/` (and the 2023+2024 documentation path documented in `file_inventory.csv` notes), place them in `raw_data/fetal_death/`, then run `python scripts/run_pipeline.py`. The output parquet should be byte-identical to the shipped file; compare with `shasum -a 256`.

A regression-protection pytest suite (`tests/`) covers the schema, row-count, and derivation invariants.

## Key Data Quality Issues

1. **Reporting thresholds.** States differ in what they report (20wk, 350g, various combinations). Use `tabulation_flag == 2` for the standard NVSR-tabulated subset. See [Reporting Thresholds](REPORTING_THRESHOLDS.md).

2. **2003 revision transition.** V1 records (2005-2017) follow either the 2003 (A) or 1989 (S) revision; pre-2003-revision eras (1982-2002 plus 2003-2004 transition) are documented in [Comparability](COMPARABILITY.md). Many fields are A-version only and blank for S-version records. All states are A-version by 2018.

3. **Education gap (V1).** `maternal_education` (revised 1-9 categorical) is blank for 2007-2013 (NCHS data limitation). `maternal_education_unrevised` is also blank for 2007-2013. Pre-2003-revision eras use `maternal_education_unrevised` (years-of-school) instead of the revised scale.

4. **Cause of death.** Available 2014+ only, ~50% missing for 2018+. Not in the public-use file for 1982-2013 (RDC restricted-use only).

5. **Plurality coding anomaly (V1 2005-2013).** See [Comparability §7](COMPARABILITY.md).

6. **V2 cross-era code-system fixes.** Five harmonized columns receive value-level normalizations in `harmonize.py` (B1-B4, B6); three are `within_era` (B5, `delivery_place_unrevised`, `maternal_race_bridged_detail`); `maternal_age` is `partial`. Extended to V3a/V3b with documented caveats. See [Comparability §10](COMPARABILITY.md).

7. **V2 state-specific Hispanic non-reporting.** Oklahoma, Maryland, Massachusetts patterns for 1992-2002 — see [Comparability §11](COMPARABILITY.md).

8. **V2 Louisiana plurality non-reporting (1992-1994).** See [Comparability §11](COMPARABILITY.md).

## Version Roadmap

| Version | Scope | Years |
|---------|-------|-------|
| V1 | Core harmonization + cause of death + reporting thresholds | 2005-2022 |
| V2 | Backward extension to 1992; 1989-revision era | 1992-2002 (base deposit) |
| V2.1 | 2003-2004 transition years | +2 years |
| V3a | 1989-1991 backward extension | +3 years |
| V3b | 1982-1988 backward extension (1978-revision) | +7 years |
| **v2.4.0 (current in-repo)** | Latest-year refresh 2023+2024 | **1982-2024 (43 years; 90/90 validation byte-exact)** |

**Migration guide (v2.0.0 → v2.4.0):** [`migrations/v2.0.0-to-v2.4.0-fetal-death.md`](../migrations/v2.0.0-to-v2.4.0-fetal-death.md).

**Joint-use convenience layer:** `stratified_denominators.csv` and [`shared/helpers/canonical_join_keys.py`](../shared/helpers/canonical_join_keys.py) — see [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md).

## Principles

Reproducibility, transparency, limited claims, explicit comparability documentation, automated regression checks, and usability for researchers who did not build the pipeline.

## Companion Project

This project leverages methodology from the **U.S. Natality Harmonization Project** ([GitHub](https://github.com/yoelplutchok/natality-harmonization) · [Zenodo concept DOI 10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074)). For demographic-stratified live-birth denominators needed to compute fetal mortality rates, see [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md) and `stratified_denominators.csv`.

## Citation

Plutchok, Y. (2026). *Harmonized U.S. Fetal Death Microdata, 1982-2024* (v2.4.0 in-repo; v2.0.0 Zenodo deposit) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.20031571
