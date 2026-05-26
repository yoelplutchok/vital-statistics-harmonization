# RECEIPT — LY-linked-2024 — `latest-year-linked-2024-period`

**UTC:** 2026-05-26T13:30:00Z  
**Task ID:** LY-linked-2024  
**Phase:** PRE-FLIGHT → SMOKE → DO → VERIFY → RECEIPT

## Summary

Closed the §15.G “latest linked year” item as **verify-only**. NCHS `2024PE2023CO.zip` is the **2023 cohort** (2024 period) file; that cohort was already in the v4 linked envelope from C8.18. Refreshed committed validation comparison artifacts; **no parquet rebuild**. Cohort **2024** remains deferred until `2025PE2024CO.zip` publishes.

## Gate SHA proof

| Artifact | SHA (prefix) | Changed? |
|---|---|---|
| `natality_v2_harmonized_derived.parquet` | `acb5c48a…` | no |
| `natality_v3_linked_harmonized.parquet` | `ea89ab3c…` | no |
| `natality_v3_linked_harmonized_derived.parquet` | `22a4523d…` (100 cols) | no |

## DO

- **Verify-only** — no parse/harmonize/derive on build host (existing `linked_2023_denomplus.parquet` = 3,605,081 rows; harmonized max `data_year` = 2023; total 149,386,620 rows).
- Refreshed `natality/output/validation/external_validation_v3_linked_comparison.{csv,md}` via validator re-run.
- Docs: `natality/PROVENANCE.md` footer; `docs/NCHS_SOURCE_MANIFEST.md` cohort-2024 deferral note; `NEXT_STEPS.md` §15.G; `KICKOFF.md` sequence table.

## VERIFY

- **CDC:** vital statistics online lists **2024 period / 2023 cohort** (2026-05-26).
- **SMOKE:** `parse_linked_cohort_year.py --zip 2024PE2023CO.zip --year 2023 --max-rows 5000` → 5,000 rows; VS2023/VS2024 numerator members found.
- **NVSR validator:** `compare_external_targets_v3_linked.py` → **35 pass, 0 fail, 0 missing** (includes seven 2023 cells: resident births 3,596,017 byte-exact).
- **Smoke tests:** `test_linked_icd10_derived_smoke.py` + `test_parquet_column_snapshot.py` → **13 passed**.
- **2023 cohort row conservation:** `linked_2023_denomplus` rows = harmonized `data_year==2023` count (3,605,081).

## §10 self-check

What VERIFY might not catch: (1) full-byte identity of the 2023 slice vs a fresh full re-harmonize was not run (assumed stable since C8.18 + LINK-ICD10 derive-only). (2) User-guide PDF `24PE23CO_linkedUG.pdf` not re-OCR’d this session (targets already committed from prior session). (3) Convenience `natality_v3_linked_residents_only.parquet` still reflects 2005–2023 v3 slice (documented pending refresh — out of scope).

## Forward-looking HALTs for next session

1. **D.2-docs:** Zenodo bundle must cite **143/143** MM, linked **100** cols / `22a4523d…`, **35/35** linked 2005–2023.
2. **Cohort 2024:** halt if `2025PE2024CO.zip` layout differs from 2022–2023 period-cohort pattern without plan-update.
3. **D.4-paper:** build-host notebook VERIFY still pending.
4. Natality `acb5c48a…` and linked harmonized `ea89ab3c…` byte-exact unless a task documents expected drift.
