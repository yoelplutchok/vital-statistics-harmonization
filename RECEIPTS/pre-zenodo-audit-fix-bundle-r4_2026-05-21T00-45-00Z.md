# Receipt: pre-zenodo-audit-fix-bundle-r4

- **Task ID:** `pre-zenodo-audit-fix-bundle-r4`
- **UTC:** 2026-05-21T00:45:00Z
- **Authority:** `AUDITS/CONSOLIDATED_POST_DPREP9_2026-05-21T00-21-08Z.md` Tier A + task spec `AUDITS/pre-zenodo-audit-fix-bundle-r4_TASK_SPEC.md`
- **Halt status:** none

## What was done

Doc/CSV/notebook-builder-only remediation closing round-4 audit propagation gaps (D-prep.8 convenience CSV years not reflected in cross-product docs).

| ID | File | Change |
|---|---|---|
| A1-001 | `VERSION_ROADMAP.md` | 4,990 × 31 years shipped; removed Planned convenience-CSV block |
| A1-002 | `docs/COMPARABILITY.md` | L154 → 31 strat years / 28 LBY years through 2024 |
| A1-003 | `docs/JOINT_USE_GUIDE.md` | L22 fetal bridged null → 2018–2024 (harmonized parquet) |
| A1-004 | `fetal_death/quickstart.py` | LBY comment through 2024; dropped 2023–2024 recompute clause |
| A1-005 | `PROJECT_STRUCTURE.md` | fetal_death § → v2.4.0 / 1982–2024 + layout doc rows |
| A1-006 | `notebooks/_build_paper_companion.py` + `paper_companion.ipynb` | C37 LBY window 2005–2024; C42 print clarifies 26 = rate targets |
| A1-007 | `tests/test_cross_product_join_parity.py` | docstrings 29 → 31 years |
| A1-008 | `paper/PAPER2_ANALYSIS_DISCOVERY_PROMPT.md` | bridged-null windows aligned |
| A1-009 | `fetal_death/scripts/run_pipeline.py` | comment clarifies 29-yr orchestrator vs v2.4.0 envelope |

**A1-006 note:** Consolidated audit suggested changing C42 “26 years” to 28; **rejected at DO** — 26 remains correct for `external_validation_targets.csv` `fetal_mortality_rate` rows (through 2022). Only C37 / LBY attribution updated.

## Verify

- `uv run pytest tests/test_cross_product_join_parity.py -q` → **13 passed**
- `uv run python notebooks/_build_paper_companion.py` → exit 0; notebook regenerated + executed
- Residual grep on target docs: no `not yet extended` / `not extended to 2023` / `null 2018–2022` in JOINT_USE L22
- Strat CSV unchanged: 4990 rows, 31 years (1992–2024)
- Gate parquets: not re-hashed this session (no parquet DO); **re-hash required before Zenodo D.2**

## Self-check (§10)

1. **Wrong year count in COMPARABILITY L154** — mitigated: matches JOINT_USE L59–61 (31 strat / 28 LBY).
2. **C42 mislabeled as LBY span in future edits** — mitigated: explicit parenthetical in builder print.
3. **Notebook execute drift in validation cells** — mitigated: full builder re-run on build host succeeded this session; preterm/cross_race still out of scope.

## Forward-looking HALTs (Convention 4)

1. Re-hash 4 gate SHAs on build host immediately before Zenodo D.2.
2. Phase D.1–D.4 each need explicit human go-ahead.
3. Manuscript `paper/draft_v2_hmd_styled.md` — D.4 only.
4. Optional: notebook execute pass for `preterm_outcomes_time_series` / `cross_race_fetal_mortality` (Tier B).
