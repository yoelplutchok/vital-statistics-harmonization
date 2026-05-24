# ICD-9-CM → ICD-10-CM GEM (RD.4)

Official CMS General Equivalence Mapping used for the optional derived
`cause_of_death_icd10_derived` column on matched-multiples infant-death rows.

| File | Source | SHA-256 |
|---|---|---|
| `2018_I9gem.txt` | [CMS 2018 ICD-10-CM GEMs (diagnosis)](https://www.cms.gov/medicare/coding/icd10/downloads/2018-icd-10-cm-general-equivalence-mappings.zip) | see `file_inventory.csv` row `icd_gem_2018_I9` |

The derive script (`scripts/04_derive/derive_matched_multiples.py`) maps NCHS
4-position underlying-cause codes (no decimal; external causes omit the `E`
prefix per NCHS layout) to GEM 5-character ICD-9 keys, then picks a single
ICD-10 target per code (prefer non-approximate, non-combination rows when
multiple GEM rows exist).

This is a **derived-only** bridge. The canonical `cause_of_death_icd` and
`cause_of_death_icd_revision` columns in `matched_multiples_harmonized.parquet`
are unchanged.
