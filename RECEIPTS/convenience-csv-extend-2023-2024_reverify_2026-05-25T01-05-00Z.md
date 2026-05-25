# Receipt: convenience-csv-extend-2023-2024 (D-prep.8 re-verify)

## 2026-05-25T01:05:00Z

### What was done

Idempotent re-verification session: D-prep.8 shipped 2026-05-20 (`RECEIPTS/convenience-csv-extend-2023-2024_2026-05-20T19-30-00Z.md`). No CSV rebuild required. One doc fix: `build_stratified_denominators.py` module docstring bridged-race null window 2018-2022 → 2020-2024 (aligns with JOINT_USE_GUIDE + shipped CSV).

### Field-value snapshot (Convention 3)

| Artifact | Assumed | Observed |
|---|---|---|
| `live_births_by_year.csv` max year | 2024 | 2024 (`3,628,934` 2024; `3,596,017` 2023) |
| `stratified_denominators.csv` years | 1992-2002 + 2005-2024 | 31 years; 4,990 data rows |
| 2022-2024 strat sum = LBY | byte-exact | 2022/2023/2024 OK |
| Gate SHAs | anchors in PROVENANCE | all four byte-exact on build host |

### Five-phase trace

- **PRE-FLIGHT:** PROCEED — artifacts already at target state.
- **SMOKE:** `pytest` `test_stratified_denominators_*` — 2 passed.
- **DO:** docstring only (no canonical mutation).
- **VERIFY:** gate SHAs; per-year parity 2022-2024; pytest PASS.
- **RECEIPT:** this file.

### Verify results

- Four gate parquet SHAs: `38e2cecb…`, `185c071e…`, `acb5c48a…`, `f630d8cf…` — PASS.
- Stratified SHA `37e250ac…` (differs from 2026-05-20 receipt `ad2cfc2e…` — content still valid; parity tests pass).
- `live_births_by_year.csv` SHA `69db6c2c…`.

### Self-check

Could have assumed KICKOFF “needs build host” meant CSVs still end at 2022; PRE-FLIGHT field snapshot caught shipped state immediately. Rebuild not run — if natality parquet drifted, pytest parity would FAIL (it passed).

### Forward-looking HALTs for next session

1. When NVSR 2024 final publishes, update `live_births_by_year.csv` 2024 `source` + reconcile count if ≠ `3,628,934`.
2. **D-prep.9** next in §15.F queue (notebook paths / re-execute).
3. Gate SHAs must remain byte-exact before any Zenodo patch.

### Git

Tag not applied (re-verify only; original `D-prep.8` receipt at 2026-05-20).
