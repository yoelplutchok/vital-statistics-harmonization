# Reproducing this dataset

This file is bundled with the Zenodo deposit so that someone with only the Zenodo download (no GitHub clone) can understand how the data was produced and verify it.

## What you have downloaded

The Zenodo deposit contains:

- **6 Parquet files** with the harmonized data (V2 natality 1990-2024 and V3 linked birth-infant death 2005-2023, in three variants each: full, derived, residents-only).
- **6 documentation files** (`README.md`, `ABOUT_THIS_RELEASE.md`, `CODEBOOK.md`, `COMPARABILITY.md`, `FAQ.md`, `GETTING_STARTED.md`, `VALIDATION.md`) explaining the schema, how to load the data, comparability rules, and validation results.
- **4 metadata CSVs** (`harmonized_schema.csv`, `external_validation_targets_v1.csv`, `external_validation_targets_v3_linked.csv`, `file_inventory.csv`).
- **4 validation outputs** (`external_validation_v1_comparison.{csv,md}`, `external_validation_v3_linked_comparison.{csv,md}`, `harmonized_missingness_breaks.csv`, `harmonized_missingness_by_year.csv`) showing what was validated and the results.
- **`PROVENANCE.md`** with SHA-256 checksums and the pipeline git hash that produced these files.
- **`quickstart.ipynb`** — a Jupyter notebook with worked examples.
- **`requirements.txt`** — pinned Python dependencies.
- **`LICENSE`** — MIT (code) + CC-BY-4.0 (data).

## To load and explore the data (no reproduction needed)

```bash
pip install -r requirements.txt
jupyter notebook quickstart.ipynb
```

Or in Python:

```python
import pyarrow.parquet as pq
df = pq.read_table('natality_v2_residents_only.parquet').to_pandas()
print(df.shape)        # (138_582_904, 82)
print(df.columns.tolist()[:10])
```

For column definitions, read `CODEBOOK.md` first, then `COMPARABILITY.md` for trend-safe analysis subsets.

## To verify integrity

```bash
shasum -a 256 *.parquet
```

Compare against the SHA-256s in `PROVENANCE.md`. If they match, your copy is byte-identical to the deposit.

## To reproduce from raw NCHS source files

The full pipeline (parsing fixed-width raw zips → harmonized Parquet) is open-source on GitHub:

**https://github.com/yoelplutchok/natality-harmonization**

That repository contains all the code (`scripts/01_import/` through `scripts/07_figures/`), field-position specifications (`scripts/01_import/field_specs.py`), and a step-by-step "Quick reproduce" section in its README.md. The raw NCHS source files (~120 GB, ~50 zips) are public-use products from the CDC FTP server:

- Natality data: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`
- Linked birth-infant death (2005–2015): `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/cohortlinkedus/`
- Linked birth-infant death (2016–2023): `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/period-cohort-linked/`

`metadata/file_inventory.csv` (in this Zenodo bundle) lists every required raw file with its expected size and SHA-256.

## Citation

When using this dataset, please cite:

- **NCHS** as the source of the underlying public-use natality and linked birth-infant death microdata (the relevant NVSR "Births: Final Data" reports for the year(s) you analyze; see `value_source` column in `external_validation_targets_v1.csv`).
- **This harmonization**: concept DOI [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074) (resolves to latest version). For pinned-version citation, use the version-specific DOI shown on the Zenodo page (e.g., v2.7.0 = [10.5281/zenodo.19868835](https://doi.org/10.5281/zenodo.19868835)).

## Questions or issues

Open an issue on GitHub: https://github.com/yoelplutchok/natality-harmonization/issues
