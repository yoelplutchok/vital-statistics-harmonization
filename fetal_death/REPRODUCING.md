# Reproducing this dataset

This file is bundled with the Zenodo deposit so that someone with only the Zenodo download (no GitHub clone) can understand how the data was produced and verify it.

## What you have downloaded

The Zenodo deposit contains:

- **2 primary Parquet files** with the harmonized data:
  - `fetal_death_harmonized.parquet` (1,634,195 × 73) — harmonized cross-era schema
  - `fetal_death_derived.parquet` (1,634,195 × 89) — same rows + 16 derived analytic indicators (preferred starting point)
- **`fetal_death_yearly_raw_1992-2022.zip`** — bundle of 29 per-year raw Parquet files (`fetal_death_{year}_raw.parquet`) preserving every NCHS source field, for users who need fields outside the harmonized 73-column schema. Unzip to obtain the per-year files.
- **2 V1-baseline diff targets** (`fetal_death_harmonized.V1_baseline.parquet`, `fetal_death_derived.V1_baseline.parquet`) — the V1.x release snapshot used to verify V1 byte content is unchanged across V2 development.
- **9 documentation files** (`README.md`, `ABOUT_SOURCE_DATA.md`, `ABOUT_THIS_RELEASE.md`, `CODEBOOK.md`, `COMPARABILITY.md`, `FAQ.md`, `GETTING_STARTED.md`, `REPORTING_THRESHOLDS.md`, `V2_1992_LAYOUT_DECISIONS.md`) explaining the schema, how to load the data, comparability rules, and validation results.
- **Metadata CSVs** (`harmonized_schema.csv`, `variable_crosswalk_working.csv`, `record_layout_{1992,2006,2014,2022}.csv`, `reporting_thresholds.csv`, `live_births_by_year.csv`, `external_validation_targets.csv`, `file_inventory.csv`, `validation_tracking.csv`, `validation_results.csv`).
- **`PROVENANCE.md`** and **`PROVENANCE.sha256`** with SHA-256 checksums and the pipeline git hash that produced these files.
- **`quickstart.py`** — a Python script with worked examples.
- **`requirements.txt`** — pinned Python dependencies.
- **`LICENSE`** — CC-BY-4.0 for the harmonization work (harmonized + derived parquets, crosswalks, schema, scripts, validation reports, and documentation contributed by this project). NCHS source data are works of the United States Government and are not subject to U.S. copyright (17 U.S.C. § 105); see `LICENSE` §1 for the two-part wording.
- **`CITATION.cff`** — machine-readable citation metadata.

## To load and explore the data (no reproduction needed)

```bash
pip install -r requirements.txt
python quickstart.py
```

Or in Python:

```python
import pyarrow.parquet as pq
df = pq.read_table('fetal_death_derived.parquet').to_pandas()
print(df.shape)        # (1_634_195, 89)
print(df.columns.tolist()[:10])

# Standard NVSR-comparable subset (>=20 weeks, U.S. residents)
nvsr = df[(df['tabulation_flag'] == '2') & (df['residence_status'] != '4')]
print(f"{len(nvsr):,} NVSR-comparable fetal deaths across 1992-2022")
```

For column definitions, read `CODEBOOK.md` first, then `COMPARABILITY.md` for cross-era analysis caveats.

## To verify integrity

```bash
shasum -a 256 *.parquet
```

Compare against the SHA-256s in `PROVENANCE.md`. If they match, your copy is byte-identical to the deposit.

## To reproduce from raw NCHS source files

The full pipeline (parsing fixed-width raw zips → harmonized Parquet) is open-source on GitHub:

**https://github.com/yoelplutchok/fetal-death-harmonization**

That repository contains all the code (`scripts/01_import/` through `scripts/05_validate/`), field-position specifications (`metadata/record_layout_*.csv`), the regression-protection pytest suite (`tests/`), and a top-level orchestrator (`scripts/run_pipeline.py`). The raw NCHS source files are public-use products from the CDC FTP server:

- Fetal death data: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/`
- Fetal death User Guide PDFs: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeathus/`

Filename patterns:
- 1992–2013: `Fetal{YYYY}US.zip` + `{YYYY}FetalUserGuide.pdf`
- 2014–2022: `Fetal{YYYY}US_COD.zip` + `{YYYY}FetalUserGuide.pdf` (cause-of-death-inclusive variant)

`file_inventory.csv` (in this Zenodo bundle) lists every required raw source zip and user-guide PDF for the 29 V2.0 years (1992-2002 + 2005-2022). The 2003 and 2004 transition years are deferred to V2.1.

End-to-end reproduction from a fresh clone:

```bash
# Place 29 NCHS source zips in raw_data/fetal_death/ then:
python scripts/run_pipeline.py
```

Approximate run time: ~6 minutes on a 2024-vintage laptop.

## Companion product

For demographic-stratified live-birth denominators (race-, age-, or ethnicity-specific) needed to compute fetal mortality rates, see the **U.S. Natality Harmonization Project**:

- GitHub: https://github.com/yoelplutchok/natality-harmonization
- Zenodo concept DOI: [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074) (resolves to latest)

Together the two harmonizations cover both the fetal-death numerator and the live-birth denominator on consistent schemas.

## Citation

When using this dataset, please cite:

- **NCHS** as the source of the underlying public-use fetal death microdata (the NCHS Fetal Death User Guide for the year(s) you analyze; see `external_validation_targets.csv` for relevant NVSR / user-guide reports).
- **This harmonization** (v2.0.0): [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571).

A concept DOI that always resolves to the latest version may also be available on the Zenodo deposit page.

## Questions or issues

Open an issue on GitHub: https://github.com/yoelplutchok/fetal-death-harmonization/issues
