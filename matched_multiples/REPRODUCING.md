# Reproducing this dataset

This file is bundled with the Zenodo deposit so that someone with only the Zenodo download (no GitHub clone) can understand how the data was produced and verify it.

## What you have downloaded

The matched-multiples product (the 4th HVS product) covers NCHS's three published matched-multiples linkage files: birth + fetal-death + infant-death records of twins / triplets / quadruplets linked into multiple-delivery sets, for three publication windows (1995–1997, 1995–2000, 2016–2020).

- **Primary harmonized Parquet (gate artifact):**
  - `matched_multiples_harmonized.parquet` (**1,665,568 × 24**) — harmonized cross-window schema.
- **Optional derived Parquet:**
  - `matched_multiples_derived.parquet` (**1,665,568 × 27**) — same rows plus `cause_of_death_icd10_derived` and provenance flags, via the CMS 2018 ICD-9→ICD-10 GEM. The canonical `cause_of_death_icd` column is unchanged.
- **Per-window raw Parquets** (`output/yearly_clean/`) — parsed fixed-width NCHS members before harmonization:
  - `matched_multiples_1995-1997_raw.parquet` (324,490 records)
  - `matched_multiples_1995-2000_raw.parquet` (699,144 records)
  - `matched_multiples_2016-2020_raw.parquet` (641,934 records)
- **Documentation** (`README.md`, `ABOUT_SOURCE_DATA.md`, layout decision logs).
- **Metadata CSVs** (`harmonized_schema.csv`, `record_layout_1995_1997.csv`, `record_layout_1995_2000.csv`, `record_layout_2016_2020.csv`, `external_validation_targets.csv`, `file_inventory.csv`, `validation_results.{csv,md}`).
- **`PROVENANCE.md`** — SHA-256 checksums and the monorepo git commit that produced the build.

## To load and explore the data (no reproduction needed)

```python
import pyarrow.parquet as pq
df = pq.read_table('matched_multiples_harmonized.parquet').to_pandas()
print(df.shape)        # (1_665_568, 24)

# US-resident multiple-delivery records, matched sets only:
# (1995-X windows ship residence_status; 2016-2020 suppresses it)
mm = df[
    df['residence_status'].fillna(1).ne(4)   # exclude foreign residents where available
    & df['set_complete'].isin([1, 2])        # complete or incomplete sets (exclude unmatched)
]
print(f"{len(mm):,} matched-set records")
```

Read `README.md` for the schema and the canonical filter, then `ABOUT_SOURCE_DATA.md` for the methodology differences between the three source windows.

## To verify integrity

```bash
shasum -a 256 matched_multiples_harmonized.parquet
shasum -a 256 matched_multiples_derived.parquet
```

Compare against `PROVENANCE.md`. Gate SHAs for the current in-repo build:

- `matched_multiples_harmonized.parquet`: `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549`
- `matched_multiples_derived.parquet`: `682302e3413cdcebadd4bab2a6cf9ae3d52f505cd2611c44df6591f6995cea00`

Per-window raw-parquet SHAs are listed in `PROVENANCE.md`.

## To validate against the NCHS published tables

The harmonized parquet is checked cell-by-cell against the tables NCHS publishes in each source file's documentation. The validation script recomputes the targets and prints pass/fail:

```bash
uv run python matched_multiples/scripts/05_validate/validate_matched_multiples.py
```

Targets are listed in `external_validation_targets.csv`; the current build passes **143/143** committed targets (33 Table 1-class cells, 102 Table 2a twin-set cells, and 8 row-count and structural invariants), recorded in `validation_results.{csv,md}`.

## To reproduce from raw NCHS source files

The full pipeline is open-source in the **U.S. Harmonized Vital Statistics** monorepo:

**https://github.com/yoelplutchok/vital-statistics-harmonization**

(`matched_multiples/scripts/` — parse → harmonize → derive → validate.)

Raw NCHS public-use files (3 fixed-width zips):

- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/1995-1997.zip`
- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/1995-2000.zip`
- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/2016-2020.zip`

Each zip ships with a companion documentation PDF at the same path. `file_inventory.csv` lists every source zip and PDF with notes; SHA-256 anchors for the raw zips are in [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 4.

End-to-end reproduction from a fresh clone:

```bash
# Place the 3 NCHS source zips in raw_data/matched_multiples/ then, from the monorepo root:
python matched_multiples/scripts/01_import/parse_matched_multiples.py      # 3 layouts -> 3 yearly_clean parquets
python matched_multiples/scripts/03_harmonize/harmonize_matched_multiples.py  # -> matched_multiples_harmonized.parquet
python matched_multiples/scripts/04_derive/derive_matched_multiples.py      # optional: + ICD-10 derived columns
python matched_multiples/scripts/05_validate/validate_matched_multiples.py  # 143/143 targets
```

The three windows are small (~1.67 M records total), so reproduction runs in approximately a minute on a standard laptop.

## Companion products

Matched-multiples records span natality, fetal death, and linked birth–infant death. For demographic-stratified live-birth denominators and the other vital-statistics products, see the natality and fetal-death subprojects in the same monorepo.

## Citation

- **NCHS** — underlying public-use matched-multiples microdata (documentation PDF for each window).
- **This harmonization** — shipped as the matched-multiples product of the unified U.S. Harmonized Vital Statistics Zenodo deposit (version-of-record DOI [10.5281/zenodo.20326150](https://doi.org/10.5281/zenodo.20326150); concept DOI resolves to the latest version).

## Questions or issues

Monorepo: https://github.com/yoelplutchok/vital-statistics-harmonization/issues
