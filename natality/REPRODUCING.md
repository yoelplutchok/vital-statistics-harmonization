# Reproducing this dataset

This file is bundled with the Zenodo deposit so that someone with only the Zenodo download (no GitHub clone) can understand how the data was produced and verify it.

## What you have downloaded

The current **in-repo** build (natality **v3.0.0**, linked **v4.0.0**) ships from the unified monorepo:

**https://github.com/yoelplutchok/vital-statistics-harmonization**

Gate parquets (SHA-256 in [`natality/PROVENANCE.md`](PROVENANCE.md)):

| File | Shape | SHA-256 (prefix) |
|---|---|---|
| `natality_v2_harmonized_derived.parquet` | 201,161,456 × 84 | `acb5c48a…` |
| `natality_v3_linked_harmonized_derived.parquet` | 149,386,620 × 97 | `f630d8cf…` |

The legacy standalone repo [yoelplutchok/natality-harmonization](https://github.com/yoelplutchok/natality-harmonization) mirrors earlier Zenodo deposits (v2.7.0 = 1990–2024 natality slice only).

Documentation: `README.md`, `docs/ABOUT_THIS_RELEASE.md`, `docs/CODEBOOK.md`, `docs/COMPARABILITY.md`, `docs/FAQ.md`, `docs/GETTING_STARTED.md`, `docs/VALIDATION.md`.

Metadata: `metadata/harmonized_schema.csv`, `metadata/external_validation_targets_v1.csv`, `metadata/external_validation_targets_v3_linked.csv`, `metadata/file_inventory.csv` (95 rows: 57 natality + 38 linked-cohort years).

Validation outputs under `output/validation/` (1990–2024 natality NVSR surface; 2005–2023 linked owned surface).

## To load and explore the data (no reproduction needed)

From the monorepo root with `uv sync`:

```bash
uv run python -c "
import pyarrow.parquet as pq
t = pq.read_table('natality/output/harmonized/natality_v2_harmonized_derived.parquet')
print(t.num_rows, len(t.column_names))
"
```

Or `natality/notebooks/quickstart.ipynb` (paths relative to `natality/`).

Column definitions: `docs/CODEBOOK.md`; cross-era rules: `docs/COMPARABILITY.md`.

## To verify integrity

```bash
shasum -a 256 natality/output/harmonized/natality_v2_harmonized_derived.parquet
shasum -a 256 natality/output/harmonized/natality_v3_linked_harmonized_derived.parquet
```

Compare against [`PROVENANCE.md`](PROVENANCE.md) and [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 5.

## To reproduce from raw NCHS source files

Scripts: `natality/scripts/01_import/` through `natality/scripts/05_validate/`.

Raw files (~120 GB total):

- Natality: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/` — **57** zips (1968–2024)
- Linked cohort: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/cohortlinkedus/` — **38** zips (1983–2023; permanent **1992–1994** gap)
- Linked period (2005–2023 slice also in period-cohort tree): see `metadata/file_inventory.csv`

SHA-256 for every raw zip: [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Sections 2–3 (not duplicated in `file_inventory.csv` columns).

Quick reproduce (see also `natality/README.md`):

```bash
# Place zips per file_inventory.csv, then from monorepo root:
python natality/scripts/01_import/parse_all_pre1990_years.py   # if rebuilding 1968-1989
# ... per-era import + harmonize + derive + validate scripts
```

## Citation

- **NCHS** — underlying public-use microdata (*Births: Final Data* / linked user guides for your years).
- **This harmonization** — concept DOI [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074) (resolves to latest deposited version; in-repo v3.0.0 / v4.0.0 pending unified HVS deposit).

## Questions or issues

https://github.com/yoelplutchok/vital-statistics-harmonization/issues
