# Zenodo v1.0.2 upload — docs-only validation sync

**Concept DOI:** [10.5281/zenodo.20326150](https://doi.org/10.5281/zenodo.20326150)  
**Prior version:** v1.0.1 (2026-05-21) — seven harmonized/derived parquets + `HVS-docs-and-metadata-1.0.1.zip`  
**This version:** v1.0.2 — **parquets unchanged**; replace the docs/metadata zip and refresh `SHA256SUMS.txt` for doc files only.

## What changed vs v1.0.1

| Surface | v1.0.1 (stale in deposit) | v1.0.2 (in-repo) |
|---|---|---|
| Natality external validation | 183/183 (1990–2024 only) in `.zenodo.json` / comparison summary | **249/249** (`external_validation_v1_comparison.{csv,md}`) |
| Linked derived | 97 columns; gate `f630d8cf…` in v1.0.1 upload notes | **100** columns; gate **`22a4523d6e62e018acd1c8648275a9f98d86ee711f61c017f885df6952b73b5e`** |
| Matched multiples validation | 41/41 or 109/109 era in some docs | **143/143** (`matched_multiples/validation_results.{csv,md}`) |
| Root metadata | `.zenodo.json` description | Updated counts + v1.0.2 |

## Four gate parquet SHAs (must match v1.0.1 bytes — do not re-upload parquets)

Re-hash on the build host before publishing:

```bash
shasum -a 256 \
  ~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet \
  ~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet \
  ~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet \
  ~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet
```

Expected prefixes: `38e2cecb` · `185c071e` · `acb5c48a` · **`22a4523d`**

**Halt (§7-#18)** if any gate SHA differs from v1.0.1 — do not publish a docs-only version on wrong parquets.

## Build the docs zip (from monorepo root)

Model on v1.0.1 (`RECEIPTS/D.2-zenodo-deposit-bundle-r2_2026-05-21T14-30-00Z.md`): lean user-facing tree only — no `scripts/`, `tests/`, `paper/`, process logs.

**Must include (updated paths for v1.0.2):**

- Root: `README.md`, `PROJECT_STRUCTURE.md`, `LICENSE`, `CITATION.cff`, `.zenodo.json` (v1.0.2)
- Cross-product: `docs/JOINT_USE_GUIDE.md`, `docs/COMPARABILITY.md`, `docs/NCHS_SOURCE_MANIFEST.md`, `docs/WORKED_EXAMPLE_FAQ.md`, `docs/PERINATAL_RECORD_FEASIBILITY.md`, `docs/PRIOR_ART.md`
- `natality/metadata/external_validation_targets_v1.csv`
- `natality/output/validation/external_validation_v1_comparison.{csv,md}` ← **249/249**
- `natality/output/validation/external_validation_v3_linked_comparison.{csv,md}` ← **35/35**, 100-col parquet
- `natality/PROVENANCE.md`, `natality/docs/*`, `natality/metadata/*` (schemas, linked targets)
- `matched_multiples/external_validation_targets.csv`
- `matched_multiples/validation_results.{csv,md}` ← **143/143**
- `matched_multiples/PROVENANCE.md`, README, schemas, layouts
- `fetal_death/PROVENANCE.md` + user docs (unchanged validation envelope)
- `csv/published_tabulations/`, quickstarts, `views.sql`, `STATA_SAS_QUICKSTART.md`, `migrations/`

Suggested output name: `HVS-docs-and-metadata-1.0.2.zip`

## Zenodo UI steps

1. Open the record → **New version**.
2. Set version **1.0.2**.
3. **Keep** the seven v1.0.1 parquet files (do not remove or replace).
4. **Remove** `HVS-docs-and-metadata-1.0.1.zip` (and any v1.0.0 docs zip).
5. **Upload** `HVS-docs-and-metadata-1.0.2.zip` + refreshed `SHA256SUMS.txt` (doc files only, or full manifest if you prefer one file).
6. Paste `.zenodo.json` description from repo (or edit in UI).
7. Publish → note the version-specific DOI for the manuscript `[^zenodo_validation]` footnote (D.4).

## Post-publish (agent or human)

- Confirm concept DOI still resolves to latest.
- Optional: update `paper/draft_v2_hmd_styled.md` footnote from “v1.0.2 will align…” to “deposited v1.0.2” (D.4-paper scope).
