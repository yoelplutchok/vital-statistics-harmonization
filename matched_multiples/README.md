# Matched Multiples — Harmonized Subproject

A 4th HVS data product covering NCHS's three published matched-multiples linkage files: birth + fetal-death + infant-death records of twins / triplets / quadruplets linked into multiple-delivery sets via the `set_id` field. Currently NCHS-released for three publication windows:

| Window | Source file (raw) | Records | Plurality | Cause-of-death coding | Cert revision |
|---|---|---|---|---|---|
| **1995-1997** | `sets9597.public` (502-byte fixed-width) | 324,490 | Twins + triplets | ICD-9 | 1989 |
| **1995-2000** | `Sets9500.public` (754-byte fixed-width) | 699,144 | Twins + triplets + quadruplets | ICD-9 (1995-1998) + ICD-10 (1999-2000) | 1989 |
| **2016-2020** | `MULTIPLES.TXT` (variable 155-157-byte) | 641,934 | Twins + triplets + quadruplets | ICD-10 | 2003 |

Total: ~1.67 M raw records across the three windows.

## Why this subproject is a separate HVS product

Matched-multiples records span natality + fetal-death + linked-birth-infant-death; they don't fit naturally under any single existing HVS product. NCHS publishes them as standalone files. We ship them as a 4th `matched_multiples/` subproject parallel to `natality/` and `fetal_death/`:

- **Clean schema separation** — no force-fit of cross-product linkage into within-product schemas.
- **H10 reproducibility-gate preserved** — the three other HVS gate parquets (`38e2cecb…` fetal harmonized / `185c071e…` fetal derived / `acb5c48a…` natality derived / `f630d8cf…` linked derived) are unchanged when this product is built; see [`PROVENANCE.md`](PROVENANCE.md).
- **Easy for non-multiple-gestation users to ignore.**

Architecture decision recorded in `DECISION_LOG.md` entry 2026-05-14T02:30:00Z (C8.16 PRE-FLIGHT, Option A standalone subproject) + the C8.16 DO sub-step 1 entry adding `applies_to` column to the layout CSVs.

## Relationship between the 1995-1997 and 1995-2000 windows

Both files ship as distinct generations, **not as supersession**. The 1995-2000 file is a methodology-extension of the 1995-1997 file (different author lists; quadruplets added per-confidentiality re-evaluation; ICD-10 cause data added for 1999-2000 records). For analyses limited to 1995-1997, both files can serve — but their methodology and inclusion criteria differ slightly (see `ABOUT_SOURCE_DATA.md`).

## Pipeline (shipped at C8.16)

```
raw_data/matched_multiples/                  raw NCHS zips (3 total; SHA in docs/NCHS_SOURCE_MANIFEST.md §4)
       │
       ▼
scripts/01_import/parse_matched_multiples.py   parse 3 layouts -> 3 yearly_clean parquets
       │
       ▼
scripts/03_harmonize/harmonize.py              -> matched_multiples_harmonized.parquet (1,665,568 x 24)
       │
       ▼
scripts/05_validate/                           Table 1 validation (all 3 windows; 41 targets)
```

See [`PROVENANCE.md`](PROVENANCE.md) for gate SHA and [`REPRODUCING.md`](REPRODUCING.md) for rerun steps.

## Canonical filter

For analyses of US-resident multiple-delivery deaths or births:

```python
# 1995-X windows ship residence_status (RESTATUS@26); 2016-2020 suppresses it
# Within-set analyses (e.g., gender combinations) should also filter by set_complete
df_us_resident = df[
    df['residence_status'].fillna(1).ne(4)  # exclude foreign residents where available
    & df['set_complete'].isin([1, 2])       # complete or incomplete (exclude unmatched)
]
```


## Documentation files

- [`ABOUT_SOURCE_DATA.md`](ABOUT_SOURCE_DATA.md) — NCHS source files: SHA-anchored zips + PDFs, methodology generation differences, record format details.
- [`record_layout_1995_1997.csv`](record_layout_1995_1997.csv) — Field-by-field byte positions for `sets9597.public` (212 rows / 502 bytes / ICD-9).
- [`record_layout_1995_2000.csv`](record_layout_1995_2000.csv) — Field-by-field byte positions for `Sets9500.public` (256 rows / 754 bytes / ICD-9 + ICD-10).
- [`record_layout_2016_2020.csv`](record_layout_2016_2020.csv) — Field-by-field byte positions for `MULTIPLES.TXT` (125 rows / variable 155-157 bytes / ICD-10).
- [`harmonized_schema.csv`](harmonized_schema.csv) — 24-column harmonized schema (C8.16-complete).
- [`file_inventory.csv`](file_inventory.csv) — Source-file inventory + per-window record counts; SHA-256 anchors in [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 4.

## NVSR / NCHS validation targets

Each PDF includes one or more published tables that the harmonized parquet should reproduce byte-exact:

- **1995-1997 Table 1** — 14/14 byte-exact (5 BIRTHID outcome totals + 9 set_complete×outcome cells; layout PDF omits printable counts — see `external_validation_targets.csv`).
- **1995-2000 Table 1** — 14/14 byte-exact (same structure; validate against this window only, not 1995-1997).
- **2016-2020 PDF Table 1** — 5/5 *Total* column cells byte-exact (see `validation_results.md`).
- **Table 2 (gender × maternal age)** — deferred; set-level tables not yet transcribed.

## Status (C8.16-complete; in-repo)

C8.16 shipped in 3 sub-steps: scaffold + 3 record_layout CSVs (sub-step 1), parser + 3 yearly_clean parquets (sub-step 2), harmonize + validate + worked-example notebook + monorepo docs (sub-step 3). RD.2 (2026-05-24) extended validation to all three windows: 14 Table 1 cells byte-exact per 1995-1997 and 1995-2000 window + 5 for 2016-2020 (41 targets total incl. structural invariants). The harmonized parquet (1,665,568 rows × 24 cols) passes all committed targets in `validation_results.csv`.

Pipeline artifacts:

- `output/yearly_clean/matched_multiples_<window>_raw.parquet` (3 files; gitignored; reproducible). Row counts: 324,490 / 699,144 / 641,934.
- `output/harmonized/matched_multiples_harmonized.parquet` (1 file; gitignored; reproducible). 1,665,568 rows × 24 cols.
- `validation_results.{csv,md}` at subproject root (tracked).
- `tests/test_release_smoke.py` (11 tests; SHAPE-not-VALUE per Convention 1).

Cross-window comparability: `within_era` for race / education / delivery-method (different revision-era field semantics); `full` for set-level identifiers + record-type + sex_infant + age-at-death.
