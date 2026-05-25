# Receipt: RD.1b-pre-1990-natality-rate-benchmarking-phase-b

**Completed:** 2026-05-24T18:00:00Z

## What was done

- **RD.1b Phase B:** Added 10 `preterm_rate_pct` cells (1980–1989) to `natality/metadata/external_validation_targets_v1.csv` from MVSR Advance Reports (one cite per year; tolerance 0.05).
- **Compare path:** Extended `natality/scripts/05_validate/compare_external_targets_v1.py` with `_weighted_preterm_rate_from_raw` (1980–1988, GESTREC3 codes 1|2 denominator + SAMPWT) and `_unweighted_preterm_rate_from_raw_1989` (GESTAT3).
- **SMOKE:** `natality/tests/test_pre1990_preterm_rate_smoke.py` (anchors 1980, 1984, 1985, 1989).
- **Docs:** `README.md` + `natality/README.md` → **225/225** validation headline.

## VERIFY

- Build-host compare: **225/225 PASS** (`/tmp/hvs-rd1b-phase-b-validation/external_validation_v1_comparison.csv`).
- Preterm 1980–1989 actuals vs MVSR (max |diff| 0.04 pct-pt; all within 0.05 tolerance).
- Gate derived SHA unchanged: `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974`.
- `pytest natality/tests/test_pre1990_*.py` → **13 passed**.

## Forward-looking HALTs for next session

1. Re-run compare after any target/validator edit; expect **225/225** PASS.
2. Phase C must not regress resident-births (205) or 1980–1989 LBW/preterm (20) cells.
3. Gate SHA re-hash before next Zenodo upload.

## §10 self-check

The preterm denominator excludes GESTREC3 code 3 (not stated); MVSR narrative uses “prior to 37 weeks” among reported gestations — if NCHS used all births as denominator for some years, targets could be wrong despite passing our aligned path. VERIFY only checked tolerance, not alternate denominator definitions. 1989 uses raw GESTAT3 while 1990+ uses derived `preterm_lt37` — cross-era joint-use notebooks should not assume identical measurement for 1989 vs 1990 without reading COMPARABILITY notes.
