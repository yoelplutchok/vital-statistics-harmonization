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
- **H10 reproducibility-gate preserved** — existing 4 canonical parquet SHAs (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) untouched.
- **Easy for non-multiple-gestation users to ignore.**

Architecture decision recorded in `DECISION_LOG.md` entry 2026-05-14T02:30:00Z (C8.16 PRE-FLIGHT, Option A standalone subproject) + the C8.16 DO sub-step 1 entry adding `applies_to` column to the layout CSVs.

## Relationship between the 1995-1997 and 1995-2000 windows

Both files ship as distinct generations, **not as supersession**. The 1995-2000 file is a methodology-extension of the 1995-1997 file (different author lists; quadruplets added per-confidentiality re-evaluation; ICD-10 cause data added for 1999-2000 records). For analyses limited to 1995-1997, both files can serve — but their methodology and inclusion criteria differ slightly (see `ABOUT_SOURCE_DATA.md`).

## Pipeline (planned, per C8.16 DO sub-steps 2-3)

```
raw_data/matched_multiples/                  raw NCHS zips (3 total; SHA-pinned)
       │
       ▼
scripts/01_import/parse_matched_multiples.py   parse 3 layouts -> 3 yearly_clean parquets
       │                                       outputs: output/yearly_clean/matched_multiples_<window>_raw.parquet
       │
       ▼
scripts/03_harmonize/harmonize.py              per-window raw -> harmonized canonical
       │                                       outputs: output/harmonized/matched_multiples_harmonized.parquet
       │
       ▼
scripts/04_derive/                             derived analytic indicators (TBD)
       │                                       outputs: output/harmonized/matched_multiples_derived.parquet (SHIPPED)
       │
       ▼
scripts/05_validate/                           validate against PDF documentation tables (Table 1 of each PDF)
                                               outputs: validation_results.{csv,md} at subproject root
```

## Canonical filter (preliminary; subject to validation refinement)

For analyses of US-resident multiple-delivery deaths or births:

```python
# 1995-X windows ship residence_status (RESTATUS@26); 2016-2020 suppresses it
# Within-set analyses (e.g., gender combinations) should also filter by set_complete
df_us_resident = df[
    df['residence_status'].fillna(1).ne(4)  # exclude foreign residents where available
    & df['set_complete'].isin([1, 2])       # complete or incomplete (exclude unmatched)
]
```

The cross-window canonical filter is finalized at C8.16 DO sub-step 3 (validation against PDF Table 1 cell-by-cell).

## Documentation files

- [`ABOUT_SOURCE_DATA.md`](ABOUT_SOURCE_DATA.md) — NCHS source files: SHA-anchored zips + PDFs, methodology generation differences, record format details.
- [`record_layout_1995_1997.csv`](record_layout_1995_1997.csv) — Field-by-field byte positions for `sets9597.public` (212 rows / 502 bytes / ICD-9).
- [`record_layout_1995_2000.csv`](record_layout_1995_2000.csv) — Field-by-field byte positions for `Sets9500.public` (256 rows / 754 bytes / ICD-9 + ICD-10).
- [`record_layout_2016_2020.csv`](record_layout_2016_2020.csv) — Field-by-field byte positions for `MULTIPLES.TXT` (125 rows / variable 155-157 bytes / ICD-10).
- [`harmonized_schema.csv`](harmonized_schema.csv) — Preliminary 25-column harmonized schema (skeleton authored at C8.16 DO sub-step 1; refined at sub-step 2 once parser surfaces value-distribution surprises per L13-extension).
- [`file_inventory.csv`](file_inventory.csv) — Source-file SHA-256 anchors + per-window record counts.

## NVSR / NCHS validation targets

Each PDF includes one or more published tables that the harmonized parquet should reproduce byte-exact:

- **1995-1997 PDF Tables 1-2** — not yet transcribed; record-level counts of matched/unmatched and gender combinations.
- **1995-2000 PDF Tables 1-2** — not yet transcribed.
- **2016-2020 PDF Table 1** — total = 641,934 records (633,734 birth + 8,200 fetal death) ✓ MATCHES empirical row count; Tables 2A-2C give per-plurality matched-set perinatal outcome counts.

Cell-by-cell validation lands at C8.16 DO sub-step 3.

## Status (as of C8.16-complete; 2026-05-14)

C8.16 shipped in 3 sub-steps: scaffold + 3 record_layout CSVs (sub-step 1), parser + 3 yearly_clean parquets (sub-step 2), harmonize + validate + worked-example notebook + monorepo docs (sub-step 3). The harmonized parquet (1,665,568 rows × 24 cols) reproduces 5 of 5 PDF Table 1 *Total* cells byte-exact for the 2016-2020 window plus 8 structural invariants (cause-of-death scoping; quadruplet exclusion; residence_status suppression; row-count conservation; cross-window plurality coverage).

Pipeline artifacts:

- `output/yearly_clean/matched_multiples_<window>_raw.parquet` (3 files; gitignored; reproducible). Row counts: 324,490 / 699,144 / 641,934.
- `output/harmonized/matched_multiples_harmonized.parquet` (1 file; gitignored; reproducible). 1,665,568 rows × 24 cols.
- `validation_results.{csv,md}` at subproject root (tracked).
- `tests/test_release_smoke.py` (11 tests; SHAPE-not-VALUE per Convention 1).

Cross-window comparability: `within_era` for race / education / delivery-method (different revision-era field semantics); `full` for set-level identifiers + record-type + sex_infant + age-at-death.
