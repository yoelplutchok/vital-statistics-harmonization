# PROVENANCE

SHA-256 checksums for every **shipped harmonized artifact** in the natality + linked birth–infant death products, plus the monorepo git commit that produced the current in-repo build.

## Pipeline version (in-repo state)

| Product | Version | Years | Records (derived) |
|---|---|---|---|
| **Natality** | v3.0.0 | 1968–2024 (57 years) | 201,161,456 |
| **Linked birth–infant death** | v4.0.0 | 1983–2023 (38 cohort years; **permanent 1992–1994 NCHS-linkage gap**) | 149,386,620 |

| Field | Value |
|---|---|
| **Monorepo commit** | `3926e19be4330edd67804dbd8801682357a14494` (`3926e19`) |
| **Repository** | https://github.com/yoelplutchok/vital-statistics-harmonization |
| **Subproject path** | `natality/` |
| **Prior Zenodo deposit** | v2.7.0 concept DOI [10.5281/zenodo.19363074](https://doi.org/10.5281/zenodo.19363074) — immutable; this file documents the **current** monorepo build |
| **Canonical build tree** | `~/Desktop/natality-harmonization/` (`output/harmonized/`) |

**Filename convention:** harmonized natality parquets retain the historical `natality_v2_*` prefix (schema-family tag from the v2.x lineage); in-repo version is **v3.0.0**. Linked parquets use the `natality_v3_linked_*` prefix; in-repo version is **v4.0.0**.

Raw NCHS zips: [`metadata/file_inventory.csv`](metadata/file_inventory.csv) (95 rows) cross-checked in [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Sections 2–3.

## Natality — primary parquets (gate: derived)

| File | Rows × cols | Size | SHA-256 |
|---|---|---|---|
| `natality_v2_harmonized.parquet` | 201,161,456 × 71 | 2.0 GB | `c8a740eb48d4f3de66759da27eef94143c315846885bf905a88cbc0fa6237153` |
| `natality_v2_harmonized_derived.parquet` | 201,161,456 × 84 | 2.7 GB | `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` |

**Gate artifact for cross-product checks:** `natality_v2_harmonized_derived.parquet` (`acb5c48a…`).

## Linked birth–infant death — primary parquets (gate: derived)

| File | Rows × cols | Size | SHA-256 |
|---|---|---|---|
| `natality_v3_linked_harmonized.parquet` | 149,386,620 × 81 | 1.5 GB | `ea89ab3c009de00cddb88aad84aa50fde376a47f96b6865113a600fb5a0907c7` |
| `natality_v3_linked_harmonized_derived.parquet` | 149,386,620 × 100 | 2.0 GB | `22a4523d6e62e018acd1c8648275a9f98d86ee711f61c017f885df6952b73b5e` |

**Gate artifact for cross-product checks:** `natality_v3_linked_harmonized_derived.parquet` (`22a4523d…`). Prior gate (pre–LINK-ICD10, 97 cols): `f630d8cf…`.

**LINK-ICD10 (2026-05-26):** Re-ran `derive_linked_v3.py` only (harmonized `ea89ab3c…` unchanged). Adds `underlying_cause_icd10_derived` + provenance columns via CMS `2018_I9gem.txt` (same GEM as matched multiples RD.4).

Verify on your copy:

```bash
shasum -a 256 \
  natality_v2_harmonized.parquet \
  natality_v2_harmonized_derived.parquet \
  natality_v3_linked_harmonized.parquet \
  natality_v3_linked_harmonized_derived.parquet
```

## Regression baselines (optional; not gate artifacts)

| File | Purpose | SHA-256 |
|---|---|---|
| `natality_v2_harmonized.v28_baseline.parquet` | Pre–v3.0.0 natality (1990–2024 slice) | `230efed2ac34c794638aceaa777a31e62abffb6e8e6af94ed215970933ccebac` |
| `natality_v2_harmonized_derived.v28_baseline.parquet` | Pre–v3.0.0 derived | `e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` |
| `natality_v3_linked_harmonized.v3_baseline.parquet` | Pre–v4.0.0 linked harmonized (2005–2023) | `e1795ac615a6ee40b0d5813ac6f6c072692bc30808b746b3c3efb06cf5f357e7` |
| `natality_v3_linked_harmonized_derived.v3_baseline.parquet` | Pre–v4.0.0 linked derived | `9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` |

> **Note:** Baseline files support regression diffs only; cite the primary derived parquet SHAs above for reproducibility claims.

## Convenience / residents-only variants

Residents-only and other convenience parquets (when present under `output/convenience/`) are **derived subsets** of the primary files above. Their SHAs change when convenience scripts re-run; cite the primary derived parquet SHA for reproducibility claims.

## Reproducibility

End-to-end pipeline: `scripts/01_import/` → `03_harmonize/` → `04_derive/` → `05_validate/`. See [`REPRODUCING.md`](REPRODUCING.md).

---

*Refreshed 2026-05-26 at LY-linked-2024 (verify-only) and auditfix (full linked-derived SHA corrected post–LINK-ICD10). Natality derived gate `acb5c48a…` unchanged.*
