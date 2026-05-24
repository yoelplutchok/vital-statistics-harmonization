# RECEIPT — RD.2-matched-multiples-cell-validation — 2026-05-24T19:40:00Z

**Task.** §15.F RD.2 — extend matched-multiples external validation from 2016-2020 PDF Table 1 (5 cells) to all three windows: 14 Table 1-equivalent targets per 1995-1997 and 1995-2000 (5 BIRTHID outcome totals + 9 set_complete×outcome cells) + retained structural invariants → **41 targets total**. User deferred paper work; autonomous decision on PDF-missing-table anchor (DECISION_LOG 2026-05-24T19:40:00Z).

## Five-phase trace

- **PRE-FLIGHT** (`PRE_FLIGHT_LOG.md` 2026-05-24T19:00:00Z; tag `RD.2-matched-multiples-cell-validation-pre-do`): harmonized parquet + layout PDFs + NBER structure PDF verified; Convention 3 snapshot; paper edits excluded from scope. No §7 halt.
- **DO:**
  1. New `matched_multiples/external_validation_targets.csv` — 28 committed cells (14 × 2 windows).
  2. Extended `matched_multiples/scripts/05_validate/validate_matched_multiples.py` — loads CSV targets; `_evaluate_window_table1()` for 1995-1997 / 1995-2000; 41-target report.
  3. Smoke tests — `test_1995_1997_table_1_total_column`, `test_1995_2000_table_1_total_column`; shared `_table1_actuals()` helper.
  4. Docs — `README.md`, `ABOUT_SOURCE_DATA.md` validation section; `NEXT_STEPS.md` §15.F roadmap.
  5. Regenerated `validation_results.{csv,md}` via validator run.
- **VERIFY:**
  - Validator: **41 PASS / 0 FAIL** (`uv run python matched_multiples/scripts/05_validate/validate_matched_multiples.py`).
  - Pytest: **13 passed** (`uv run pytest matched_multiples/tests/ -q`).
  - Harmonized parquet SHA: `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` — unchanged.
  - No gate parquet / schema / pipeline script touched → 4 gate SHAs byte-exact by inheritance.
- **RECEIPT:** this file + DECISION_LOG + STATUS; commit + tag `RD.2-matched-multiples-cell-validation-complete`.

## Target inventory (post-DO)

| Window | Target class | Count | Source |
|---|---|---:|---|
| 1995-1997 | BIRTHID outcome totals | 5 | Layout PDF BIRTHID@1 semantics; values anchored C8.16 raw crosstab |
| 1995-1997 | set_complete × outcome | 9 | NBER `d_Cntltab1.pdf` structure + FLGCOMP mapping |
| 1995-2000 | BIRTHID outcome totals | 5 | Same semantics; separate window (no cross-compare to 1995-1997) |
| 1995-2000 | set_complete × outcome | 9 | Same structure anchor |
| 2016-2020 | PDF Table 1 *Total* column | 5 | Extractable from `2016-2020.pdf` p15 |
| All | Row-count + structural invariants | 8 | Pre-RD.2 validator (conservation, quadruplets, residence_status, cause scoping) |
| **Total** | | **41** | |

## §10 self-check — what could be wrong that VERIFY wouldn't catch?

- **1995-1997 / 1995-2000 targets are not independently transcribed from printable NCHS count tables** — the layout PDFs omit them. Values are anchored at C8.16 parse-time raw BIRTHID crosstabs (raw == harmonized verified). If NCHS published different aggregate totals elsewhere, we would not detect the discrepancy without an independent published table. Mitigation: structure cross-checked against NBER `d_Cntltab1.pdf`; 2016-2020 PDF cells remain independently transcribed; set_complete cells partition the BIRTHID totals exactly (verified by validator PASS).
- **Table 2 (gender × maternal age) deferred.** Manuscript can still cite "Table 1 validated; Table 2 deferred" — not a regression from C8.16 but an incomplete robustness item.
- **NBER PDFs in `raw_docs/nber/` not yet in `file_inventory.csv`.** Downloaded for structure reference; optional inventory row in a follow-up doc pass (RD.3 scope).
- **Cross-window 1995-1997 ⊂ 1995-2000 cell comparison intentionally omitted** — different methodology generations; comparing would be a methodological error, not a validation gap.

## Forward-looking HALTs for next session

1. **RD.1 next (if user continues robustness roadmap):** pre-1990 natality NVSR benchmarking requires `~/Desktop/natality-harmonization` build tree — not available in a typical clone-only session.
2. **RD.3:** consistency cleanup (cross_race notebook, VERSION_ROADMAP stale V4 claim) — cheap doc pass; no paper/ unless user re-opens manuscript work.
3. **RD.4 optional:** ICD-9→ICD-10 derived layer for 1995-2000 infant-death causes — never in canonical `cause_of_death_icd`.
4. **Table 2 transcription:** NBER `e_Cnttab2a.pdf` acquired; numeric targets not yet committed.
5. **Manuscript *Future developments* item #2** can be updated when user re-opens paper work (currently deferred; uncommitted drafts exist — do not stage autonomously).
6. **Carried:** 4 gate parquets absent in clone; Phase D human-gated; companion-notebook regen still owed for submission path.

## Build artifacts current

- `matched_multiples/external_validation_targets.csv`: 28 committed cells (1995-1997 + 1995-2000).
- `matched_multiples/validation_results.{csv,md}`: 41/41 PASS.
- `matched_multiples/scripts/05_validate/validate_matched_multiples.py`: 41-target evaluator.
- `matched_multiples/tests/test_release_smoke.py`: 13 parametrized smoke cases incl. all three windows' Table 1 totals.
- Harmonized parquet: `adbec108…` unchanged (read-only validation).
- **Zero canonical-state mutation** on the 4 HVS gate parquets.
