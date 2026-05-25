# Receipt: RD.1b-pre-1990-natality-rate-benchmarking-phase-c

**Completed:** 2026-05-25T02:05:00Z

## What was done

- **RD.1b Phase C:** Added 24 cells (12 years × LBW + preterm, 1968–1979) to `natality/metadata/external_validation_targets_v1.csv` from MVSR Final Natality / Registered Births supplements (plus IOM 1985 Table B.1 for 1971 LBW; Series 21 No. 48 adjacent cite for 1968 LBW).
- **Compare path:** `_weighted_preterm_rate_from_raw_1968` (GESTREC 0–4) in `compare_external_targets_v1.py`; existing LBW/preterm maps cover 1969–1979.
- **SMOKE:** `natality/tests/test_pre1990_rate_phase_c_smoke.py` (anchors 1968, 1972, 1979).
- **Docs:** `README.md`, `natality/README.md`, `KICKOFF.md` → **249/249** validation headline.

## VERIFY

- Build-host compare: **249/249 PASS** (`/tmp/hvs-rd1b-phase-c-validation/external_validation_v1_comparison.csv`).
- Zero regression on prior 225 cells (205 resident-births + 1980–1989 LBW/preterm).
- Gate derived SHA unchanged: `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974`.
- `pytest natality/tests/test_pre1990_*.py` → **19 passed**.

## Forward-looking HALTs for next session

1. Re-run compare after any target/validator edit; expect **249/249** PASS.
2. §15.F may close after human review of Phase C MVSR cites (1968 LBW uses adjacent national series; 1971/1973 LBW use 0.06 tol).
3. **D.4** remains gated until §15.F closed.

## §10 self-check

1968 preterm target (8.9%) is aligned to GESTREC 0–4 PUF semantics, not the LMP-area “premature” definition in later MVSR tables (1972+). Cross-era notebooks must not treat 1968 preterm as identical to 1980+ GESTREC3 code-1 rates without reading COMPARABILITY notes. 1979 rates come from the 1980 Final Natality report (mv31_08) citing 1979 levels — not a standalone 1979-only PDF in this session.
