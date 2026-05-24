# Receipt: RD.1b-phase-b-preterm-deferral — 2026-05-24T23:16:00Z

**Task.** §15.F RD.1b Phase B — `preterm_rate_pct` 1980–1989.

## Outcome

**DEFERRED** (doc-only). No canonical mutation.

## Decision

childstats **HEALTH1.A** publishes U.S. preterm percentages from **1990** onward only (table title: "1990–2022"; WebSearch confirmed). Unlike LBW (HEALTH1.B from 1980), there is no citable national series for 1980–1989 preterm at the childstats tier. Per L6, no invented NVSR/childstats cells.

**1989 LBW tolerance 0.06** (Phase A): **accepted** — childstats one-decimal 7.1 vs microdata 7.05%; widening all years rejected.

## Verify

- Natality compare on build host: **215/215 PASS** (unchanged).
- Gate derived SHA `acb5c48a…` byte-exact.
- `pytest natality/tests/test_pre1990_*.py`: 9 passed.

## Forward-looking HALTs for next session

1. Phase C (1968–1979 rates) requires NVSR/MVSR transcription — not childstats.
2. After any natality re-derive: expect 215/215 with `--yearly-parquet-dir`.

## §10 self-check

Could have missed a non-childstats published preterm series (e.g., archived NVSR narrative). Mitigation: explicit deferral + Phase C scoped to MVSR transcription; no false PASS introduced.
