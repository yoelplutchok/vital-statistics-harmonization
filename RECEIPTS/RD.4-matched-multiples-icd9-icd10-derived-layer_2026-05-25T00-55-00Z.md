# Receipt: RD.4-matched-multiples-icd9-icd10-derived-layer

**Completed:** 2026-05-25T00:55:00Z  
**Tags:** `RD.4-matched-multiples-icd9-icd10-derived-layer-pre-do`, `RD.4-matched-multiples-icd9-icd10-derived-layer-complete`

## Summary

Shipped optional **derived-only** ICD-10 underlying-cause layer for matched-multiples infant deaths: CMS 2018 ICD-9→ICD-10 GEM mapping for ICD-9 rows; native copy for ICD-10 rows. Canonical `matched_multiples_harmonized.parquet` **unchanged** (gate SHA `adbec108…`).

## Inputs / outputs

| Artifact | SHA-256 (prefix) |
|---|---|
| `matched_multiples_harmonized.parquet` (unchanged) | `adbec108…` |
| `matched_multiples_derived.parquet` (new) | `682302e3…` |
| `metadata/icd_gem/2018_I9gem.txt` | `44f4079c…` |

**Coverage:** 39,806 / 39,882 infant_deaths with `cause_of_death_icd10_derived` populated (76 `gem_unmapped`).

## Verify

- `pytest matched_multiples/tests/`: **23 passed**
- `validate_matched_multiples.py`: **109/109 PASS** (harmonized validator unchanged)
- Harmonized column byte-parity vs derived (first 24 cols)

## §10 self-check

**What could I have gotten wrong that VERIFY wouldn't catch?**

1. **GEM choice vs NCHS mortality-specific crosswalk** — CMS diagnosis GEM may disagree with NCHS mortality recode rules for edge external-cause / perinatal codes; VERIFY only checks structural invariants, not clinical plausibility.
2. **Multi-target GEM rows** — tie-break (prefer non-approximate, lexicographic first) is deterministic but not NCHS-official; rare ICD-9 codes with multiple plausible ICD-10 targets could be wrong for epidemiologic tabulation.
3. **NCHS UCOD→GEM key normalization** — 14 unmapped codes (`888`, `558`, …) may need additional alias rules; VERIFY only asserts ≥95% row-level map rate, not 100%.

## Forward-looking HALTs for next session

1. If `matched_multiples_harmonized.parquet` SHA ≠ `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` after a task claiming doc-only — halt (§7 / gate regression).
2. Re-run `derive_matched_multiples.py` after any harmonized rebuild; expect derived SHA `682302e3413cdcebadd4bab2a6cf9ae3d52f505cd2611c44df6591f6995cea00` if inputs unchanged.
3. §15.F next: D-prep.8 (build host) or explicit deferral entries for remaining queue items before D.4.
