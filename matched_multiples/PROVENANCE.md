# PROVENANCE

SHA-256 checksums for every **shipped harmonized artifact** in the matched-multiples product (4th HVS product), plus the monorepo git commit that produced the current in-repo build.

## Pipeline version (in-repo state: C8.16 release)

| Field | Value |
|---|---|
| **Monorepo commit** | `3926e19be4330edd67804dbd8801682357a14494` (`3926e19`) |
| **Repository** | https://github.com/yoelplutchok/vital-statistics-harmonization |
| **Subproject path** | `matched_multiples/` |
| **Coverage** | 3 NCHS publication windows (1995–1997, 1995–2000, 2016–2020) |
| **Harmonized records** | 1,665,568 × 24 columns |

Raw NCHS zips and companion PDFs: [`file_inventory.csv`](file_inventory.csv) cross-checked in [`docs/NCHS_SOURCE_MANIFEST.md`](../docs/NCHS_SOURCE_MANIFEST.md) Section 4.

## Primary harmonized parquet (gate artifact)

| File | Rows × cols | Size | SHA-256 |
|---|---|---|---|
| `matched_multiples_harmonized.parquet` | 1,665,568 × 24 | 12.4 MB | `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` |

Verify:

```bash
shasum -a 256 matched_multiples_harmonized.parquet
```

## Derived parquet (optional RD.4 layer)

| File | Rows × cols | Size | SHA-256 |
|---|---|---|---|
| `matched_multiples_derived.parquet` | 1,665,568 × 27 | ~13 MB | `682302e3413cdcebadd4bab2a6cf9ae3d52f505cd2611c44df6591f6995cea00` |

Adds `cause_of_death_icd10_derived`, `cause_of_death_icd10_derived_source`, and
`cause_of_death_icd10_gem_approximate` via CMS 2018 ICD-9→ICD-10 GEM
(`metadata/icd_gem/2018_I9gem.txt`). The harmonized gate SHA above is unchanged.

```bash
uv run python matched_multiples/scripts/04_derive/derive_matched_multiples.py
shasum -a 256 matched_multiples_derived.parquet
```

## Per-window raw parquets (`output/yearly_clean/`)

Parsed fixed-width NCHS source members before harmonization. Row counts match NCHS documentation Table 1 totals (validated at C8.16).

| File | Records | Size | SHA-256 |
|---|---|---|---|
| `matched_multiples_1995-1997_raw.parquet` | 324,490 | 7.6 MB | `5c22308bed2883b9be8e244e763c3603f700b5ba5274f3ef30388a28d39205d1` |
| `matched_multiples_1995-2000_raw.parquet` | 699,144 | 15.7 MB | `7c682668006f3fab556b79422d34f5d84eed0bd0e1ae44702908f9f5edd61f5d` |
| `matched_multiples_2016-2020_raw.parquet` | 641,934 | 13.5 MB | `d98b42965573530d26d72368d968c395487b2c4e4dd3bfc4ad426e966a543261` |

## Cross-product H10 note

Matched-multiples is an ancillary product. The four **cross-product gate** parquets (fetal-death + natality + linked derived) are documented in their respective `PROVENANCE.md` files; this product does not mutate those SHAs.

## Reproducibility

Pipeline: `scripts/01_import/parse_matched_multiples.py` → `scripts/03_harmonize/harmonize.py` → `scripts/05_validate/`. See [`README.md`](README.md) and [`ABOUT_SOURCE_DATA.md`](ABOUT_SOURCE_DATA.md).

---

*Refreshed 2026-05-24 at D-prep.2 (`provenance-refresh-current-envelope`). All SHAs independently re-hashed at PRE-FLIGHT; zero parquet mutation.*
