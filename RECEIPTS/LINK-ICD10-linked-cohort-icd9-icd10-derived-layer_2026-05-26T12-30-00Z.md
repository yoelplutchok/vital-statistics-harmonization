# RECEIPT — LINK-ICD10 — `linked-cohort-icd9-icd10-derived-layer`

**UTC:** 2026-05-26T12:30:00Z  
**Task ID:** LINK-ICD10  
**Phase:** PRE-FLIGHT → SMOKE → DO → VERIFY → RECEIPT

## Summary

Added three derived columns on the linked derived parquet via CMS 2018 ICD-9→ICD-10 diagnosis GEM (`matched_multiples/metadata/icd_gem/2018_I9gem.txt`), mirroring RD.4 on matched multiples. Harmonized gate unchanged; linked derived gate SHA changed by design.

## Gate SHA proof

| Artifact | Pre-DO | Post-DO |
|---|---|---|
| `natality_v3_linked_harmonized.parquet` | `ea89ab3c009de00cddb88aad84aa50fde376a47f96b6865113a600fb5a0907c7` | unchanged ✓ |
| `natality_v2_harmonized_derived.parquet` | `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` | unchanged ✓ |
| `natality_v3_linked_harmonized_derived.parquet` | `f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073` (97 cols) | `22a4523d6e62eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073` (100 cols) |

## DO

- `natality/scripts/04_derive/icd9_to_icd10_gem.py` (GEM loader; monorepo GEM path)
- `natality/scripts/04_derive/derive_linked_v3.py` (+3 derived columns per batch)
- `natality/metadata/harmonized_schema.csv` (+3 rows)
- `natality/tests/test_linked_icd10_derived_smoke.py`
- `tests/test_parquet_column_snapshot.py` (97→100; 343→346)
- `tests/snapshots/v3_2026-05-23T02-00-00Z_columns.csv` (re-snap 346 rows)
- Docs: `natality/docs/COMPARABILITY.md`, `CODEBOOK.md`, `README.md`, `PROVENANCE.md`, `REPRODUCING.md`; root `README.md`; `paper/draft_v2_hmd_styled.md`

Re-derive command:

```bash
uv run python natality/scripts/04_derive/derive_linked_v3.py \
  --in ~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized.parquet \
  --out ~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet
```

## VERIFY

- **2005–2023 regression:** seven anchor columns (`data_year`, `infant_death`, `underlying_cause_icd10`, `cause_group`, `neonatal_death`, `low_birthweight`, `record_weight`) byte-identical vs pre-DO backup on `data_year >= 2005` slice.
- **Linked NVSR validator:** `compare_external_targets_v3_linked.py` → **35 pass, 0 fail, 0 missing** (2005–2023 owned surface).
- **Smoke:** `pytest natality/tests/test_linked_icd10_derived_smoke.py` → **7 passed**.
- **Snapshot:** `pytest tests/test_parquet_column_snapshot.py` → **6 passed**.
- **ICD-9 era GEM (1983–1998 deaths with ICD-9 UCOD):** 452,638 rows; `gem_from_icd9` 448,661 (99.12%); `gem_unmapped` 3,977 (0.88%); **37** distinct unmapped UCOD codes (top: `7468` n=2245, `558` n=743).

## Unmapped ICD-9 codes (documented)

GEM leaves `underlying_cause_icd10_derived` null and `underlying_cause_icd10_derived_source=gem_unmapped` for 3,977 death rows (37 distinct UCOD). Users must not treat null derived codes as “no death”; use `underlying_cause_icd9` for ICD-9-era analyses.

## §10 self-check

What VERIFY might not catch: (1) full 97-column byte identity on 2005–2023 was not hashed column-by-column (only seven anchors — derive path unchanged for existing columns, so risk is low). (2) GEM picks lexicographically first target when multiple GEM rows tie — same RD.4 rule, not re-audited per-code. (3) `cause_group` still null 1983–1998 by design; cross-era cause grouping from `underlying_cause_icd10_derived` is user responsibility.

## Forward-looking HALTs for next session

1. **LY-linked-2024:** linked derived SHA will change again when a new year lands — document in RECEIPT.
2. **D.2-docs:** Zenodo validation bundle must cite linked **100** cols and gate `22a4523d…` (not `f630d8cf…`).
3. **D.4-paper:** if manuscript cites linked column count or gate SHA, sync to 100 / `22a4523d…`.
4. Halt if `ea89ab3c…` or `acb5c48a…` drift during a docs-only task (unexpected parquet rebuild).
