# PROVENANCE

SHA-256 checksums for every **shipped harmonized artifact** in the fetal-death product, plus the monorepo git commit that produced the current in-repo build.

## Pipeline version (in-repo state: v2.4.0)

| Field | Value |
|---|---|
| **Monorepo commit** | `3926e19be4330edd67804dbd8801682357a14494` (`3926e19`) |
| **Repository** | https://github.com/yoelplutchok/vital-statistics-harmonization |
| **Subproject path** | `fetal_death/` |
| **Product version** | v2.4.0 (43 years, 1982–2024; 2,427,233 records; 7-era envelope) |
| **Prior Zenodo deposit** | v2.0.0 concept DOI [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) — immutable; this file documents the **current** monorepo build, not that deposit byte-for-byte |
| **Canonical build tree** | `~/Desktop/fetal-death-harmonization-build/` (monorepo scripts; output under `output/harmonized/`) |

Re-running the fetal-death pipeline from the NCHS public-use zips listed in [`file_inventory.csv`](file_inventory.csv) and cross-checked in [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 1 reproduces these parquets bit-for-bit.

## Primary harmonized parquets (gate artifacts)

These are the **authoritative shipped files** for analyses and cross-product joins.

| File | Rows × cols | Size | SHA-256 |
|---|---|---|---|
| `fetal_death_harmonized.parquet` | 2,427,233 × 73 | 27.3 MB | `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` |
| `fetal_death_derived.parquet` | 2,427,233 × 89 | 34.1 MB | `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` |

**Preferred entry point:** `fetal_death_derived.parquet` (harmonized columns + 16 derived analytic indicators).

Verify on your copy:

```bash
shasum -a 256 fetal_death_harmonized.parquet fetal_death_derived.parquet
```

## Regression baselines (optional; not gate artifacts)

Frozen snapshots for diff/regression checks across major version bumps. **Do not** use for production analyses.

| File | Purpose | SHA-256 |
|---|---|---|
| `fetal_death_harmonized.V1_baseline.parquet` | V1.x (2005–2013 slice) | `cbcc91d24f2982d74bef0ba87a64495fb5cbd27928f720ee63d4006581bea2c0` |
| `fetal_death_derived.V1_baseline.parquet` | V1.x derived | `2795f099380461581a59908b7653f536bb5f1cdbfd78f101097f0495c0232a8d` |
| `fetal_death_harmonized.V3b_baseline.parquet` | Pre–full-43-yr V3b harmonized | `e3d6c64abcb7762df54762b9dbb1e5b0f105a0511eb4b19004d11ca1f5bc111e` |
| `fetal_death_derived.V3b_baseline.parquet` | Pre–full-43-yr V3b derived | `4d1b37cc3a214eea3ec502f08ecc0d53c65c6195de19de3e4383a3573fcdc729` |

## Per-year raw parquets

The monorepo build emits **43** files: `output/yearly_clean/fetal_death_{YEAR}_raw.parquet` for **YEAR = 1982–2024**. A bundled zip for Zenodo deposit is named at upload time (the v2.0.0 deposit shipped `fetal_death_yearly_raw_1992-2022.zip`; the current build spans 1982–2024). Re-hash the bundle after packaging; per-year SHAs are reproducible from `scripts/01_import/` + `file_inventory.csv`.

## Raw NCHS source zips

**43** fetal-death public-use zips (1982–2024). Full SHA-256 table: [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 1, mirrored row-for-row in [`file_inventory.csv`](file_inventory.csv).

## Legacy `PROVENANCE.sha256`

`PROVENANCE.sha256` in this directory targets the **v2.0.0 Zenodo deposit** file bundle (1992–2022 envelope). It is **not** auto-regenerated for v2.4.0; use the table above (or re-run `shasum` on your build outputs) until the unified HVS Zenodo deposit (Phase D.2) ships an updated checksum manifest.

---

*Refreshed 2026-05-24 at D-prep.2 (`provenance-refresh-current-envelope`). Gate SHAs independently re-hashed at PRE-FLIGHT; zero parquet mutation.*
