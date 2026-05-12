# U.S. Fetal Death Harmonization Project

A modern, researcher-ready release of harmonized U.S. fetal death microdata for cross-year stillbirth research.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20031571.svg)](https://doi.org/10.5281/zenodo.20031571)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Release Summary (V2.0)

| Metric | Value |
|--------|-------|
| Years covered | 1992-2022 (29 years; 2003 and 2004 deferred to V2.1) |
| Total records | 1,634,195 |
| Harmonized variables | 73 |
| Derived variables | 16 (89 total columns) |
| Annual files processed | 29 |
| Validation checks passed | 74 checks against published NCHS/NVSR statistics (55 V1 + 19 V2): **68 byte-exact matches** plus 6 documented differences in V1 detail-cell tabulations (4 early/late GA cells where NVSR proportionally redistributes records with unknown gestational age; 2 cause-of-death cells where NVSR Table 8 restricts to a 43-state reporting area while the harmonization includes all states). All per-year counts (29/29) and per-year rates (26/26) match exactly. |
| Fetal mortality rates verified | 18/18 V1 (NVSR 73-09) + 8/8 V2 1995-2002 (NVSR 57-08) |
| Cross-era V2 code-system fixes | 5 V2→V1 value-level normalizations (B1, B2, B3, B4, B6) + 3 `within_era` relabels (B5 `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) + 1 partial relabel (`maternal_age`) |

## About

The fetal death files are produced by NCHS from the National Vital Statistics System. They cover every reported fetal death in the United States — approximately 25,000 to 30,000 per year at >=20 weeks gestation, with total file sizes of 40,000 to 70,000 records including earlier gestational age deaths.

Despite the importance of this data for stillbirth surveillance and perinatal epidemiology, cross-year use has been prohibitively difficult: three revisions of the Standard Report of Fetal Death (1978, 1989, 2003), staggered state adoption, variables that are added/dropped/recoded across revisions, and records in the same annual file following different schemas during transition periods.

**No harmonized longitudinal product previously existed.** This project fills that gap, now spanning 29 years from 1992 to 2022 in a single Parquet file with one stable schema.

## Quick Start

When downloaded from Zenodo, all files unpack to a single flat directory; the snippets below assume you `cd` into that directory.

```python
import pandas as pd

# Load the derived dataset (includes all harmonized + derived variables)
df = pd.read_parquet("fetal_death_derived.parquet")

# Standard analytic subset: tab_flag='2' (NVSR-tabulated) AND U.S. residents
nvsr = df[(df["tabulation_flag"] == "2") & (df["residence_status"] != "4")]
print(f"{len(nvsr):,} NVSR-comparable fetal deaths across {nvsr['data_year'].nunique()} years")
# 727,155 NVSR-comparable fetal deaths across 29 years
```

See [Getting Started](GETTING_STARTED.md) for more examples.

## Repository Structure (GitHub source layout)

The Zenodo deposit is **flat** — every file lives at the deposit root. The tree below is the layout of the GitHub source repository (https://github.com/yoelplutchok/fetal-death-harmonization), shown here so users who clone the repo can navigate the pipeline. None of these `output/`, `metadata/`, or `docs/` paths exist in a Zenodo download.

```
fetal-death-harmonization/
├── README.md
├── raw_data/fetal_death/       # NCHS fetal death zips (not committed) — 29 years
├── raw_docs/fetal_death/       # NCHS documentation PDFs + NVSR validation refs
├── metadata/
│   ├── harmonized_schema.csv           # Variable definitions
│   ├── variable_crosswalk_working.csv  # Raw-to-harmonized mapping (4 eras)
│   ├── record_layout_1992.csv          # 1992-2002 1989-revision layout
│   ├── reporting_thresholds.csv        # State thresholds at era-boundary years (1997, 2006, 2014, 2022, 2023); see file header
│   ├── live_births_by_year.csv         # Live-birth denominators 1995-2022 (NVSR 57-08 + NVSR 73-09)
│   ├── external_validation_targets.csv # Published validation targets
│   └── validation_tracking.csv         # Year-by-year validation status
├── scripts/
│   ├── run_pipeline.py         # End-to-end orchestrator: parse all 29 years -> harmonize -> derive -> validate
│   ├── 01_import/              # Parse fixed-width -> per-year Parquet
│   ├── 03_harmonize/           # Map era-specific fields -> common schema (incl B1-B4+B6 V2 recodes)
│   ├── 04_derive/              # Compute 16 derived variables
│   └── 05_validate/            # Validation scripts (V1 + V2)
├── output/
│   ├── yearly_clean/           # 29 raw per-year Parquet files (bundled in Zenodo as fetal_death_yearly_raw_1992-2022.zip)
│   ├── harmonized/
│   │   ├── fetal_death_harmonized.parquet  # 1,634,195 x 73
│   │   └── fetal_death_derived.parquet     # 1,634,195 x 89
│   └── validation/             # External-validation outputs (NVSR / user-guide comparisons)
├── notebooks/                  # Quickstart examples
└── docs/                       # Documentation
```

## Documentation

All documentation files are at the deposit root in the Zenodo download.

| Document | Description |
|----------|-------------|
| [About Source Data](ABOUT_SOURCE_DATA.md) | What the NCHS fetal death files are |
| [About This Release](ABOUT_THIS_RELEASE.md) | What V2 adds over V1 |
| [Codebook](CODEBOOK.md) | Every variable defined |
| [Comparability](COMPARABILITY.md) | Cross-year comparability decisions, including 1989-revision/2003-revision bridge |
| [Reporting Thresholds](REPORTING_THRESHOLDS.md) | The threshold problem |
| [Getting Started](GETTING_STARTED.md) | How to load and use the data |
| [FAQ](FAQ.md) | Common questions |
| [Reproducing](REPRODUCING.md) | How the data was produced and how to verify it |

## Validation

The shipped parquet has been validated against every per-year fetal death figure NCHS has published, plus a 55-cell detail-cell sample from NVSR 73-09. All checks are computed under the standard `tabulation_flag=='2' & residence_status!='4'` filter.

| Source | Years | Checks | Result |
|--------|-------|--------|--------|
| NVSR 73-09 (Fetal Mortality: United States, 2022) | 2005-2022 | 18 counts + 18 rates | All 36 match exactly |
| NVSR 57-08 (Fetal & Perinatal Mortality, US 2005) | 1995-2002 | 8 counts + 8 rates | All 16 match exactly |
| NCHS Fetal Death User Guides | 1992-1994 | 3 control counts | All 3 match exactly |
| NVSR 73-09 detail-cell tables (Tables A, 4, 8, plus early/late GA from Table 1) | 2014, 2022 | 19 detail cells | 13 match exactly + 6 documented differences: 4 early/late gestational-age cells where NVSR proportionally redistributes records with unknown GA, and 2 cause-of-death cells where NVSR Table 8 restricts to a 43-state reporting area while the harmonization includes all states. None are byte-level mismatches in the harmonized data. |

Per-target source citations are in `external_validation_targets.csv`; the per-target pass/fail table is in `validation_results.csv`. The three known stale-guide V2 years (1996, 2001, 2002) — where the user-guide control-count blocks were copy-pasted from adjacent years — are resolved in favor of NVSR 57-08, which the parsed counts match exactly. The V1 era (2005-2022) was held byte-identical to its V1.x baseline through the V2 backward-extension to 1992 (0 of 73 harmonized + 0 of 89 derived columns drifted), so V2 did not perturb existing V1-era analyses. Byte-level parse verification of the 1992-2002 layout: 98,500 raw-byte-to-parquet field comparisons across 10 years × 50 records × 197 fields, with 0 mismatches.

### Verifying it yourself

Three levels of independent verification, each strictly stronger than the one above:

**Level 1 — confirm what you downloaded matches what was released (10 seconds):**
```bash
shasum -a 256 -c PROVENANCE.sha256
```

**Level 2 — confirm the parquet reproduces published NCHS statistics (1 minute):**
```bash
pip install -r requirements.txt
python scripts/05_validate/validate_external_v2.py    # NVSR 57-08 + user-guide comparison, 1992-2002
python scripts/05_validate/validate_external.py       # NVSR 73-09 comparison, 2005-2022
```
Both scripts load the shipped parquet, recompute counts and rates with the standard NVSR-comparable filter, and print a pass/fail table against the published figures cited in `external_validation_targets.csv`. Reference NVSR PDFs are downloadable from CDC; you can pull them and check the targets independently.

**Level 3 — re-derive the parquet from raw NCHS source files (~6 minutes):**
Download the 29 raw zips listed in `file_inventory.csv` (SHA-256s provided) from `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/`, place them in `raw_data/fetal_death/`, then run `python scripts/run_pipeline.py`. The output parquet should be byte-identical to the shipped file; compare with `shasum -a 256`. If the diff is empty, the harmonization is fully reproducible from public sources without trusting the project's own outputs.

A regression-protection pytest suite (`tests/`) covers the schema, row-count, and derivation invariants and runs in under a second.

## Key Data Quality Issues

1. **Reporting thresholds.** States differ in what they report (20wk, 350g, various combinations). Use `tabulation_flag == '2'` for the standard NVSR-tabulated subset. See [Reporting Thresholds](REPORTING_THRESHOLDS.md).

2. **2003 revision transition.** V1 records (2005-2017) follow either the 2003 (A) or 1989 (S) revision; V2 records (1992-2002) are uniformly 1989-revision (synthesized `version_flag = 'S'` since the source files have no native VERSION field). Many fields are A-version only and so are blank for V2 and partially blank for V1 2005-2017. All states are A-version by 2018. See [Comparability](COMPARABILITY.md).

3. **Education gap (V1).** `maternal_education` (revised 1-9 categorical) is blank for 2007-2013 (NCHS data limitation). `maternal_education_unrevised` (years-of-school 00-17) is *also* blank for 2007-2013 (NCHS did not include UMEDUC in those V1 public-use years). `maternal_education` is also blank for all V2 records, since V2 populates `maternal_education_unrevised` instead.

4. **Cause of death.** Available 2014+ only, ~50% missing for 2018+. Not in the public-use file for 1992-2013 (RDC restricted-use only).

5. **Plurality coding anomaly (V1 2005-2013).** The harmonized `plurality == "5"` code is epidemiologically implausible at observed volumes in 2005-2013 A-version records and likely reflects state-level miscoding of unknown plurality. See [Comparability §7](COMPARABILITY.md) for details and the recommended researcher workaround.

6. **V2 cross-era code-system fixes.** V2 1989-revision records use different code systems than V1 2003-revision records. Five harmonized columns receive **value-level normalizations** in `harmonize.py` so `groupby` across all 29 years works correctly: B1 `fetal_sex`, B2 `delivery_method_recode`, B3 `maternal_race_bridged`, B4 `paternal_age_recode11`, B6 `delivery_place_recode`. Three additional columns where the underlying concepts/categories are fundamentally incompatible across eras are **relabeled to `within_era`** (no value normalization possible) with explicit WARNINGs in both crosswalk and schema: B5 `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`. One column (`maternal_age`) is relabeled `full → partial` because V2 1989-rev DMAGE is exact single-year while V1 MAGER top/bottom-codes 50+/12-. See [Comparability §10](COMPARABILITY.md) for the full rules.

7. **V2 state-specific Hispanic non-reporting.** Oklahoma (100% unknown all 11 V2 years), Maryland (100% unknown 1992-1998), and Massachusetts (100% unknown 1992-1997) did not report Hispanic origin in the indicated years. Faithfully preserved in the data; documented in NVSR 57-08 footnotes.

8. **V2 Louisiana plurality non-reporting (1992-1994).** Louisiana (NCHS state code 19) reports `DPLURAL=9` for ~99% of resident-occurrence fetal deaths in 1992-1994. Reporting resumed in 1995. Pipeline preserves the source bytes.

## Version Roadmap

| Version | Scope | Years |
|---------|-------|-------|
| V1 | Core harmonization + cause of death + reporting thresholds | 2005-2022 |
| **V2 (current)** | Backward extension to 1992; 1989-revision era; full cross-era validation | 1992-2022 (29 years; 2003-2004 deferred) |
| V2.1 | Add 2003 and 2004 transition years (distinct layouts) | 1992-2022 (31 years complete) |
| V3 | Full historical depth | 1982-2022 |
| **v2.4.0 (current)** | Latest-year refresh: 2023+2024 fetal-death | 1982-2024 (43 years complete; 90/90 NVSR validation byte-exact) |

**Joint-use convenience layer (shipped 2026-05-11):** `stratified_denominators.csv` and the cross-product helper at [`shared/helpers/canonical_join_keys.py`](../shared/helpers/canonical_join_keys.py) provide demographic-stratified live-birth denominators for joint fetal-mortality-rate computation; see the *Companion Project* section above. Replaces the prior roadmap "V4: Natality companion product" entry.

## Principles

Reproducibility, transparency, limited claims, explicit comparability documentation, automated regression checks, and usability for researchers who did not build the pipeline.

## Companion Project

This project leverages methodology and infrastructure from the **U.S. Natality Harmonization Project** ([GitHub](https://github.com/yoelplutchok/natality-harmonization) · [Zenodo concept DOI 10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074)). For demographic-stratified live-birth denominators (race-, age-, or ethnicity-specific) needed to compute fetal mortality rates, two paths:

- **Pre-built convenience file** — `stratified_denominators.csv` ships at the root of this deposit, with one row per (`data_year`, `maternal_age_band`, `maternal_race_bridged`, `hispanic_origin`) cell across the 29 joint-coverage years (1992–2002 + 2005–2022). See [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md) in the monorepo for column semantics, the 2018+ bridged-race gap, and worked examples. Built by [`shared/helpers/build_stratified_denominators.py`](../shared/helpers/build_stratified_denominators.py).
- **Direct join** — load the natality v2.7.0 parquet and join on `data_year` × demographics. The [`shared/helpers/canonical_join_keys.py`](../shared/helpers/canonical_join_keys.py) helper handles the cross-product column-name reconciliation.

## Citation

Plutchok, Y. (2026). *Harmonized U.S. Fetal Death Microdata, 1992-2022* (v2.0.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.20031571
