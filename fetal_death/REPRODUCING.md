# Reproducing this dataset

This file is bundled with the Zenodo deposit so that someone with only the Zenodo download (no GitHub clone) can understand how the data was produced and verify it.

## What you have downloaded

The Zenodo deposit contains:

- **2 primary Parquet files** with the harmonized data:
  - `fetal_death_harmonized.parquet` (**2,427,233 × 73**) — harmonized cross-era schema
  - `fetal_death_derived.parquet` (**2,427,233 × 89**) — same rows + 16 derived analytic indicators (preferred starting point)
- **Per-year raw Parquet archive** — in the v2.0.0 deposit this shipped as `fetal_death_yearly_raw_1992-2022.zip` (29 files). The monorepo build produces **43** files (`fetal_death_{year}_raw.parquet`, **1982-2024**) under `output/yearly_clean/`. PROVENANCE refresh at deposit time documents the current bundle name and SHA.
- **2 V1-baseline diff targets** (`fetal_death_harmonized.V1_baseline.parquet`, `fetal_death_derived.V1_baseline.parquet`) — V1.x snapshot for V1-slice regression checks.
- **Documentation** (`README.md`, `ABOUT_SOURCE_DATA.md`, `ABOUT_THIS_RELEASE.md`, `CODEBOOK.md`, `COMPARABILITY.md`, `FAQ.md`, `GETTING_STARTED.md`, `REPORTING_THRESHOLDS.md`, layout decision logs).
- **Metadata CSVs** (`harmonized_schema.csv`, `variable_crosswalk_working.csv`, `record_layout_*.csv`, `reporting_thresholds.csv`, `live_births_by_year.csv`, `external_validation_targets.csv`, `file_inventory.csv`, `validation_tracking.csv`, `validation_results.csv`).
- **`PROVENANCE.md`** and **`PROVENANCE.sha256`** — SHA-256 checksums and pipeline git hash.
- **`quickstart.py`**, **`requirements.txt`**, **`LICENSE`**, **`CITATION.cff`**.

## To load and explore the data (no reproduction needed)

```bash
pip install -r requirements.txt
python quickstart.py
```

Or in Python:

```python
import pyarrow.parquet as pq
df = pq.read_table('fetal_death_derived.parquet').to_pandas()
print(df.shape)        # (2_427_233, 89)

nvsr = df[(df['tabulation_flag'] == 2) & (df['residence_status'] != 4)]
print(f"{len(nvsr):,} NVSR-comparable fetal deaths across 1982-2024")
```

Read `CODEBOOK.md` first, then `COMPARABILITY.md` for cross-era caveats. Appendix C8.20 in `CODEBOOK.md` is the authoritative per-variable per-era evidence (parquet-derived).

## To verify integrity

```bash
shasum -a 256 *.parquet
```

Compare against `PROVENANCE.md`. Gate SHAs for the current in-repo build (v2.4.0):

- `fetal_death_harmonized.parquet`: `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48`
- `fetal_death_derived.parquet`: `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09`

## To reproduce from raw NCHS source files

The full pipeline is open-source in the **U.S. Harmonized Vital Statistics** monorepo:

**https://github.com/yoelplutchok/vital-statistics-harmonization**

(`fetal_death/scripts/` — parse → harmonize → derive → validate.)

Raw NCHS public-use files:

- Fetal death data: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/`
- User Guide PDFs: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeathus/` (2022 and earlier); 2023+ documented in `file_inventory.csv` notes (`…/fetaldeath/` path).

Filename patterns:

- 1992–2013: `Fetal{YYYY}US.zip` + `{YYYY}FetalUserGuide.pdf`
- 2014–2022: `Fetal{YYYY}US_COD.zip` + user guide
- 1982–1991 / 2023–2024: see `file_inventory.csv` (43 zips total at v2.4.0)

`file_inventory.csv` lists every required source zip and user-guide PDF. SHA-256 anchors for raw zips: [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 1 (mirrored by filename in `file_inventory.csv`).

End-to-end reproduction from a fresh clone:

```bash
# Place 43 NCHS source zips in raw_data/fetal_death/ then:
python fetal_death/scripts/run_pipeline.py   # from monorepo root; outputs under fetal_death/output/
```

Approximate run time: ~6–10 minutes on a standard laptop for 43 years.

## Companion product

For demographic-stratified live-birth denominators, see the **U.S. Natality Harmonization Project**:

- GitHub: https://github.com/yoelplutchok/natality-harmonization
- Zenodo: [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074)

Cross-product joint-use: [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md) in the monorepo.

## Citation

- **NCHS** — underlying public-use fetal death microdata (user guides / NVSR for years analyzed).
- **This harmonization** — v2.4.0 in-repo; v2.0.0 Zenodo: [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571).

## Questions or issues

Monorepo: https://github.com/yoelplutchok/vital-statistics-harmonization/issues
