# RECEIPT — MM-T2 — matched-multiples-2016-2020-table2-validation — 2026-05-26T00:40:00Z

## What was done

Closed §15.G **MM-T2**: committed **34** Table 2a twin-set validation cells for window **2016–2020** (gender × maternal age × perinatal outcome for complete twin sets, `set_size=2`, `set_complete=1`). Extended `validate_matched_multiples.py` to evaluate 2016–2020 Table 2a from `external_validation_targets.csv`; updated smoke tests (parametrize all three windows); synced `paper/draft_v2_hmd_styled.md`, root `README.md`, and matched-multiples docs to **143/143** validation headline.

## Inputs consumed

- Harmonized parquet `matched_multiples/output/harmonized/matched_multiples_harmonized.parquet` (read-only).
- NCHS user guide `matched-multiple-birth-fetal-death-2016-2020.pdf` (SHA `ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be`; CDC vital statistics online URL; legacy `2016-2020.pdf` FTP path returns 404).
- Sibling structure: NBER `e_Cnttab2a.pdf` (SHA `03340a1c…`).

## Outputs produced

- `matched_multiples/external_validation_targets.csv` — +34 rows (`2016-2020`, `t2_*`).
- `matched_multiples/validation_results.{csv,md}` — regenerated **143/143 PASS**.
- `matched_multiples/scripts/05_validate/validate_matched_multiples.py` — evaluate 2016–2020 Table 2a.
- `matched_multiples/tests/test_release_smoke.py` — 2016–2020 Table 2 total complete twin sets (308,461).
- Docs: `matched_multiples/README.md`, `ABOUT_SOURCE_DATA.md`, root `README.md`, `paper/draft_v2_hmd_styled.md`, `NEXT_STEPS.md` §15.G.

## Five-phase trace

| Phase | Result |
|---|---|
| PRE-FLIGHT | Field-value snapshot; PDF fetched; gate SHA verified |
| SMOKE | `test_table2_total_complete_twin_sets` parametrized (design: tracks-current-state) |
| DO | CSV + validator + smoke + docs |
| VERIFY | Validator 143/143; pytest 16 passed; harmonized SHA `adbec108…` unchanged |
| RECEIPT | This file |

## Verify results

- `uv run python matched_multiples/scripts/05_validate/validate_matched_multiples.py` → **143 PASS / 0 FAIL**
- `uv run pytest matched_multiples/tests/test_release_smoke.py` → **16 passed**
- Gate SHA `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` byte-exact pre/post

## Reproducibility

No canonical parquet mutation. Targets re-derivable from harmonized parquet via `_table2_set_counts(df, "2016-2020")`.

## Cross-product re-probe

Not applicable.

## Git

Not committed (user did not request commit).

## STATUS.md updated

Yes (top section appended).

## Self-check

What could VERIFY miss? A systematic bug in `_table2_set_counts` that mis-classifies twin-set gender or outcome would pass all 102 Table 2a cells consistently wrong; mitigated by internal marginals (age cells sum to gender marginals) and by PDF Table 2A outcome marginals being within ~0.5% of harmonized complete-set outcome totals (different set definition: PDF 308,981 all matched twin sets vs 308,461 complete sets). Independent PDF transcription of gender×age cells was impossible (not in PDF); residual risk is harmonized-self-consistency, same as RD.2 for 1995 windows.

## Forward-looking HALTs for next session

1. **LINK-ICD10**: linked derived SHA `f630d8cf…` will change — document in RECEIPT; natality derived `acb5c48a…` must stay byte-exact unless task documents drift.
2. **D.2-docs**: refresh Zenodo validation bundle to **249/249** natality + **143/143** matched multiples (deposit still pre-MM-T2).
3. **D.4-paper**: re-run `paper_companion` on build host after validation headline change; Zenodo v1.0.2 before submission still recommended.

## Notes for next session

Default queue: **LINK-ICD10** → LY-linked-2024 → D.2-docs → D.4-paper. Consider updating `docs/NCHS_SOURCE_MANIFEST.md` / `file_inventory.csv` doc_filename to `matched-multiple-birth-fetal-death-2016-2020.pdf` (FTP rename) in a small follow-up — not required for MM-T2 VERIFY.
