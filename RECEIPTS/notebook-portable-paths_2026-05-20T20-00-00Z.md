# Receipt: notebook-portable-paths (D-prep.9 / PZ-NB)

## 2026-05-20T20:00:00Z

### What was done

- Added `notebooks/_paths.py` (env → monorepo `*/output/harmonized/` → build-host fallback).
- Wired all `notebooks/_build_*.py` builders to `_paths`.
- Re-executed `joint_use_demo.ipynb`, `paper_companion.ipynb`, `matched_multiples_demo.ipynb` on build host.
- Fixed `natality/notebooks/quickstart.ipynb`: ~201M row copy + `data_year` vs `year` guidance (audit A4-004).

### Verify results

- Three kickoff notebooks rebuilt and executed without error (PASS).
- `matched_multiples_demo` uses monorepo-relative MM parquet when present (PASS).
- Natality/fetal/linked cells resolve to build-host fallbacks when monorepo parquets gitignored (expected on this clone).

### Self-check

Emitted notebook cells still contain absolute resolved paths (not inline `_gate()` helper); portable for this machine, not path-agnostic in git. A future pass could inject `_paths` setup snippet into notebook source cells.

### Forward-looking HALTs for next session

1. Optional post-fix audit session before Phase D.1.
2. Phase D.1–D.4 each need explicit human go-ahead.
