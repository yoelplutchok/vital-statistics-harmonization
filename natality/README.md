# U.S. Natality Harmonization Project

A researcher-ready release of harmonized U.S. natality microdata for cross-year analysis (1968–2024) plus linked birth-infant death records (1983–2023; permanent 1992–1994 NCHS-linkage gap).

## What this is

NCHS publishes annual natality public-use microdata as fixed-width ASCII records inside zips, with the field layout changing multiple times across 1968–2024:

| Era | Years | Record length | Certificate |
|-----|-------|---------------|-------------|
| Unrevised-only | 1990–2002 | 350 bytes | 1989 certificate |
| Dual-certificate transition | 2003 | 1350 bytes | Dual |
| Dual-certificate transition | 2004–2005 | 1500 bytes | Dual |
| Dual-certificate transition | 2006–2013 | 775 bytes | Dual (unrevised-only fields get blanked from 2009 on) |
| Revised-only | 2014–2024 | 1345 bytes | 2003 revised certificate |

The table above shows the 1990–2024 layouts. Natality coverage also extends back to **1968–1989** (added in v3.0.0, C8.17) across four earlier NCHS layouts under the 1968-revision certificate — 1968 (81-byte), 1969–1971 (215-byte), 1972–1988, and 1989 (a sibling of the 1990 layout). Exact per-era byte positions and record lengths are in `scripts/01_import/field_specs.py`; per-variable pre-1990 comparability is tracked at task C8.20.

Plus the linked birth-infant death cohort formats: 1983–1988 keyless two-file den/num, 1989–2004 denominator-plus, 2005–2013 denominator-plus 900 bytes, 2014–2015 denominator-plus 1384 bytes, 2016–2023 period-cohort merged by CO_SEQNUM+CO_YOD (permanent 1992–1994 NCHS-linkage gap).

This project parses all of them, maps the era-specific raw fields to a **single stable schema of 71 harmonized columns + 13 derived indicators** (V2 natality) and 81 + 16 (v4 linked: the 78 v3 columns + 3 within-era cohort columns), documents every era boundary and comparability constraint, and validates the output against NCHS "Births: Final Data" NVSR reports + the NCHS cohort linked-file user guides (225/225 V2 external validation targets pass (205 resident-births 1968–2024; 203 rate/indicator 1980–2024 including LBW from childstats HEALTH1.B and preterm from MVSR Advance Reports 1980–1989); linked 35/35 for 2005–2023 plus per-year byte-exact / within-tolerance for the pre-2005 cohort 1983–2004).

## Headline metrics

- **Years covered**: 1968–2024 (57 years natality); 1983–2023 linked birth-infant death (38 years; permanent 1992–1994 NCHS-linkage gap)
- **Birth records**: 201,161,456 total (natality V2); 149,386,620 (linked v4)
- **Residents-only subsets**: 138.58M V2 *(1990–2024 v2.8 slice; v3.0.0 1968–2024 convenience refresh pending)*; 74.79M linked *(v3 2005–2023 slice; v4 1983–2023 convenience refresh pending)*
- **Columns**: V2 = 71 harmonized + 13 derived = 84; v4 linked = 81 harmonized + 16 derived = 97 (the v3 78+94 plus 3 within-era cohort columns: `underlying_cause_icd9`, `cause_recode_61`, `link_segment`)
- **Validation**: all 41 internal invariants pass with 0 violations against the V2 natality parquet (V3 linked: 38 pass clean + 1 with 2 documented NCHS-upstream survivor exceptions; 3 V2-only coverage invariants are skipped in V3 mode — see `docs/COMPARABILITY.md` §"V3 linked vs V2 natality: 2009–2010 unrevised-cert field retention"); V2 external targets **225/225** pass (205 resident-birth cells 1968–2024 with SAMPWT-weighted raw totals; 203 rate/indicator cells 1980–2024 including pre-1990 LBW + preterm with SAMPWT-weighted raw GESTREC3 for 1980–1988 and unweighted GESTAT3 for 1989); linked external targets 35/35 pass for 2005–2023 (from NCHS linked user guides) plus per-year byte-exact / within-±0.02 for the pre-2005 cohort 1983–2004 (denominator + resident-births + IMR; weighted 1983–1984; a documented numerator-file residual for 3 of 19 cohort years — same NCHS class as the 2 differ-by-1 cells)
- **Zenodo (cite the unified HVS deposit):** [10.5281/zenodo.20326150](https://doi.org/10.5281/zenodo.20326150) (v1.0.1) ships **natality v3.0.0** (1968–2024; 201,161,456 records; `certificate_revision` includes `unrevised_1968`; v2.8.0 column renames: `year → data_year`, `restatus → residence_status`, `maternal_race_bridged4 → maternal_race_bridged`, `maternal_hispanic_origin → hispanic_origin`) and **linked v4.0.0** (1983–2023 cohort; 149,386,620 records; permanent 1992–1994 gap; +3 within-era cohort columns; parquet prefix `natality_v3_linked_*`). **Superseded natality-only deposit:** concept [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074), latest version v2.7.0 [10.5281/zenodo.19868835](https://doi.org/10.5281/zenodo.19868835) (1990–2024 only). **Migration:** v3.0.0 is schema-additive over v2.8.0 — the 1990–2024 slice is byte-identical (C8.17); linked v4 is schema-additive over v3 2005–2023. See [`migrations/v2.7.0-to-v2.8.0-natality.md`](../migrations/v2.7.0-to-v2.8.0-natality.md) for the v2.7→v2.8 rename surface.

## Output files

All outputs live under `output/`. The three files a researcher will actually use:

| File | Rows | Columns | What it is |
|------|-----:|--------:|-----------|
| `output/harmonized/natality_v2_harmonized_derived.parquet` | 201,161,456 | 84 | All U.S. births 1968–2024, one row per birth, with all derived indicators. **Start here for most analyses.** |
| `output/harmonized/natality_v3_linked_harmonized_derived.parquet` | 149,386,620 | 97 | Linked birth-infant death 1983–2023 (permanent 1992–1994 gap), one row per birth (1989+); for the keyless 1983–1988 era den/num rows are tagged by `link_segment`. |
| `output/convenience/*.parquet` | ~138.58M / ~74.79M | — | Residents-only subsets (exclude foreign residents; `residence_status != 4`) for matching NCHS residence-based published rates. *(V2 reflects the 1990–2024 v2.8 slice; linked reflects the v3 2005–2023 slice; the v3.0.0 / v4 1968–2024 / 1983–2023 convenience refreshes are pending follow-ups.)* |

## Reading order

1. **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** — how to load the parquet, required filters, example queries.
2. **[docs/CODEBOOK.md](docs/CODEBOOK.md)** — every harmonized and derived column: definition, dtype, year coverage, raw-field provenance, and known caveats.
3. **[docs/COMPARABILITY.md](docs/COMPARABILITY.md)** — cross-year comparability rules. This is the single most important doc for anyone doing multi-year trend analysis. Read it before filtering or decomposing.
4. **[docs/VALIDATION.md](docs/VALIDATION.md)** — what was validated, against what, and the residual coverage gaps.
5. **[docs/ABOUT_THIS_RELEASE.md](docs/ABOUT_THIS_RELEASE.md)** — what this project adds over working directly with the raw NCHS zips.
6. **[docs/FAQ.md](docs/FAQ.md)** — common questions and gotchas.

Supporting reference:
- **[metadata/harmonized_schema.csv](metadata/harmonized_schema.csv)** — the canonical machine-readable schema (columns, dtypes, raw-field provenance per era).
- **[metadata/file_inventory.csv](metadata/file_inventory.csv)** — per-year inventory of source NCHS zips (filename, size, SHA-256).

## Repository layout

```
natality-harmonization/
├── README.md                          ← you are here
├── requirements.txt                   ← Python deps (pyarrow, pandas)
├── raw_data/                          ← NCHS natality + linked zips (not committed; download per "Quick reproduce" below)
│   └── linked/                        ← linked birth-infant death zips
├── raw_docs/                          ← NCHS User Guide PDFs (committed for reproducibility)
│   ├── Nat{year}doc.pdf               ← 1990–2004 layout docs
│   ├── UserGuide{year}.pdf            ← 2005–2024 layout docs (authoritative for field positions)
│   ├── linked/                        ← LinkCO{05,10,15}Guide.pdf and {Y+1}PE{Y}CO_linkedUG.pdf
│   └── nvsr/                          ← NCHS "Births: Final Data" reports (external validation targets)
├── metadata/
│   ├── harmonized_schema.csv          ← canonical column-level schema
│   ├── external_validation_targets_v1.csv  ← 183 target rows for V2 validation
│   ├── external_validation_targets_v3_linked.csv  ← 35 target rows for V3 linked
│   └── file_inventory.csv             ← per-year zip inventory
├── scripts/
│   ├── 01_import/                     ← parse fixed-width → per-year Parquet
│   ├── 03_harmonize/                  ← map era-specific fields → common schema
│   ├── 04_derive/                     ← compute LBW, preterm, age categories, neonatal_death, etc.
│   ├── 05_validate/                   ← invariants, external targets, missingness diagnostics
│   ├── 06_convenience/                ← residents-only subsets + provenance
│   └── 07_figures/                    ← paper figures
├── output/
│   ├── yearly_clean/                  ← raw per-year Parquet extracts (one per year, pre-harmonization)
│   ├── linked/                        ← raw per-year linked Parquet extracts
│   ├── harmonized/                    ← stacked harmonized + derived Parquet files (the end product)
│   ├── convenience/                   ← residents-only subsets + PROVENANCE.md
│   └── validation/                    ← external-target reports, invariants reports, missingness diagnostics
├── notebooks/                         ← quickstart examples
├── figures/                           ← publication-ready figures (PDF + PNG)
└── docs/                              ← codebook, comparability, FAQ, validation, etc.
```

## Quick reproduce (full pipeline)

### 0. Download raw NCHS files

The raw zips and User Guide PDFs are public-use NCHS products. Download from the CDC FTP:

- Natality data: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/` → `raw_data/`
- Natality docs: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/` → `raw_docs/`
- Linked 2005–2015: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/cohortlinkedus/` → `raw_data/linked/`
- Linked 2016–2023: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/period-cohort-linked/` → `raw_data/linked/`

Filename patterns:
- 1990–1993: `Nat{YYYY}.zip` + `Nat{YYYY}doc.pdf`
- 1994–2024: `Nat{YYYY}us.zip` + `UserGuide{YYYY}.pdf`
- Linked 2005–2015: `LinkCO{YY}USnum.zip` / `LinkCO{YY}USden.zip` + `LinkCO{YY}Guide.pdf`
- Linked 2016–2023: `{Y+1}PE{Y}CO.zip` + `{Y+1}PE{Y}CO_linkedUG.pdf`

`metadata/file_inventory.csv` lists every required file with its expected size and SHA-256.

Years 2009–2013 and 2015 use non-standard zip compression (deflate64 / PPMd); install the `7z` CLI utility (`brew install p7zip` on macOS).

### 1+. Run the pipeline

```bash
# 1. Parse raw zips → per-year parquet (run once)
python scripts/01_import/parse_all_pre1990_years.py --years 1968-1989   # pre-1990 (C8.17 DO 5a)
python scripts/01_import/parse_all_v1_years.py --years 1990-2024
python scripts/01_import/parse_all_linked_years.py --years 1983-1991        # pre-2005 cohort: keyless two-file den/num
python scripts/01_import/parse_all_linked_years.py --years 1995-2004        # pre-2005 cohort: denominator-plus  (1992-1994 = permanent NCHS gap)
python scripts/01_import/parse_all_linked_years.py --years 2005-2015        # denom-plus
for y in 2016 2017 2018 2019 2020 2021 2022 2023; do
  python scripts/01_import/parse_linked_cohort_year.py \
    --zip raw_data/linked/$((y+1))PE${y}CO.zip --year $y \
    --out output/linked/linked_${y}_denomplus.parquet
done

# 2. Harmonize era-specific fields → common schema
python scripts/03_harmonize/harmonize_v1_core.py --years 1968-2024
python scripts/03_harmonize/harmonize_linked_v3.py --years 1983-2023        # default; auto-skips the 1992-1994 gap

# 3. Derive analysis-ready indicators (LBW, preterm, age-cat, neonatal_death, cause_group)
python scripts/04_derive/derive_v1_core.py
python scripts/04_derive/derive_linked_v3.py

# 4. Validate
python scripts/05_validate/validate_v1_invariants.py --years 1990-2024    # internal invariants
python scripts/05_validate/compare_external_targets_v1.py                  # 183 NVSR targets
python scripts/05_validate/compare_external_targets_v3_linked.py           # 35 linked targets
python scripts/05_validate/validate_linked_parquets.py --years 2005-2023   # V3 stop-ship checks
python scripts/05_validate/harmonized_missingness.py                       # per-variable null rates
python scripts/05_validate/validate_row_counts_vs_nchs.py --years 1994-2024
```

End-to-end runtime on a single modern laptop: ~1 hour wall clock for parse, ~15 min for harmonize+derive, ~10 min for validate.

## Principles

- **Reproducibility**: every output can be regenerated from `raw_data/` + committed scripts + committed `metadata/*.csv`.
- **Transparency**: the raw-field-to-harmonized-column mapping is in `scripts/01_import/field_specs.py` with inline comments per era, and mirrored in `metadata/harmonized_schema.csv` for machine consumption.
- **Explicit comparability documentation**: every column that's not fully comparable across 1990–2024 is flagged in the CODEBOOK and has a corresponding entry in COMPARABILITY.md's pitfall tables.
- **Honest validation**: 183/183 and 35/35 are headline numbers, but individual transcription failures, single-year coverage gaps, and known quirks (e.g., two null-`record_weight` survivor rows in 2014/2015; the documented pre-2005 cohort numerator-file residual for 1989/1998/2002 — the same NCHS class as those 2 cells) are documented rather than papered over.

## Citation

- Cite **NCHS** as the source of the underlying public-use natality and linked birth-infant death microdata. The relevant NVSR "Births: Final Data" report for the year(s) you analyze is the standard citation; see `metadata/external_validation_targets_v1.csv` `value_source` column for the exact NVSR volume/issue/date per year.
- Cite this harmonization (concept DOI — always resolves to latest version):
  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19363074.svg)](https://doi.org/10.5281/zenodo.19363074)
- Or pin to a specific version:
  - v2.7.0 (latest deposited; in-repo state is v3.0.0, pending the unified-HVS deposit): [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19868835.svg)](https://doi.org/10.5281/zenodo.19868835)
  - v2.5.0 (initial): [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19363075.svg)](https://doi.org/10.5281/zenodo.19363075)
