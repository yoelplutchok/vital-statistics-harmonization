# Receipt: RD.1b-pre-1990-natality-rate-benchmarking-phase-a

**Completed:** 2026-05-24T22:57:47Z

## What was done

- **KICKOFF `[plan-update]`** — default queue is §15.F robustness roadmap until CLOSED; D.4 gated.
- **RD.1b Phase A:** 10 `lbw_rate_pct` targets (1980–1989) from childstats HEALTH1.B; extended `compare_external_targets_v1.py` with SAMPWT-weighted LBW% from raw yearly parquets (1980–1988); 1989 uses derived stream with 0.06 tolerance (one-decimal publication).
- **Validation:** 215/215 PASS on build host (`acb5c48a…` unchanged).
- **Tests:** `test_pre1990_lbw_rate_smoke.py` (3 anchor years).
- **Docs:** root `README.md` + `natality/README.md` validation headlines.

## Deferred (Phase B–C)

- Preterm 1980–1989 (HEALTH1.A starts 1990).
- 1968–1979 rates (no childstats floor; NVSR/MVSR transcription).

## Forward-looking HALTs for next session

1. Re-run compare after any natality re-derive; expect **215/215** PASS.
2. §15.F next item: RD.1b Phase B or RD.2 Table 2 (per KICKOFF order).
3. Do not open `paper/` until §15.F CLOSED unless user re-authorizes D.4.

## §10 self-check

Weighted LBW uses `DBIRWT` on raw parquets; harmonized `birthweight_grams` could diverge on edge sentinels — VERIFY used raw path for 1980–1988. 1989 tolerance widened to 0.06; a future year-specific NVSR cell could narrow it. Pre-1990 preterm not probed this session.
