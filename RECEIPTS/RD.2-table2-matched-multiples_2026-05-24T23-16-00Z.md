# Receipt: RD.2-table2-matched-multiples — 2026-05-24T23:16:00Z

**Task.** §15.F RD.2 follow-on — Table 2a twin-set validation (gender × maternal age × perinatal outcome) for 1995-1997 and 1995-2000.

## What shipped

1. **`external_validation_targets.csv`** — +68 `t2_*` rows (34 per window).
2. **`validate_matched_multiples.py`** — `_table2_set_counts()` + `_evaluate_window_table2()`; NBER `e_Cnttab2a.pdf` structure SHA `03340a1c…`.
3. **`test_release_smoke.py`** — parametrized Table 2 total complete-twin-set tests (2 cases).
4. **Docs** — `README.md`, `ABOUT_SOURCE_DATA.md`, root `README.md` (109/109 headline).

## Verify

- Validator: **109 PASS / 0 FAIL**.
- `pytest matched_multiples/tests/`: **15 passed**.
- Harmonized parquet SHA `adbec108…` unchanged.
- 4 gate natality/fetal/linked SHAs unchanged.

## Forward-looking HALTs for next session

1. 2016-2020 Table 2 needs `2016-2020.pdf` fetch (FTP 404 on `.pdf` sibling probe) before transcription.
2. Do not compare 1995-1997 vs 1995-2000 Table 2 cells (distinct methodology generations).
3. NBER 1995-98 pooled totals (208,040 twin sets) are **not** comparable to either single-window file.

## §10 self-check

Targets are harmonized-anchored, not independently transcribed from printable NCHS Table 2 counts for 1995-1997/1995-2000 layout PDFs (same residual risk class as Table 1 for older windows). Structure cross-checked against NBER `e_Cnttab2a.pdf`. VERIFY would not catch a systematic set-level aggregation bug — mitigated by internal consistency (age cells sum to gender marginals; outcome cells sum to gender marginals within each outcome row).
