# Receipt: pre-zenodo-audit-fix-bundle (D-prep.5)

- **Task ID:** `pre-zenodo-audit-fix-bundle`
- **Timestamp:** 2026-05-20T12:00:00Z
- **Trigger:** D-prep.4 round-3 findings (Tier A PZ-01–PZ-11)
- **Scope:** Doc/CSV-only; zero canonical parquet mutation

## What was done

Single commit remediating pre-Zenodo audit round-3 doc/CSV drift:

| ID | Fix |
|---|---|
| PZ-01 | `docs/JOINT_USE_GUIDE.md` — v3.0.0/v2.4.0 envelope, joint years 1992–2024, convenience CSV 2022 cap |
| PZ-02 | `fetal_death/quickstart.py` — v2.4.0 / 1982–2024 |
| PZ-03 | Root `README.md` heritage + citation footnote |
| PZ-04 | `fetal_death/CODEBOOK.md` L63 + C8.20 appendix schema notes (delivery_year, data_year) |
| PZ-05 | `matched_multiples/README.md` — shipped state + gate SHA pointer |
| PZ-06 | `fetal_death/REPRODUCING.md`, `natality/REPRODUCING.md` — monorepo paths, manifest SHA routing |
| PZ-07 | `file_inventory.csv` imported flags (fetal 43, MM 3); `NCHS_SOURCE_MANIFEST.md` §2 intro |
| PZ-08 | `natality/metadata/harmonized_schema.csv` `data_year` → 1968–2024 |
| PZ-09 | `docs/COMPARABILITY.md` denominator year policy |
| PZ-10 | `VERSION_ROADMAP.md`, `CHANGELOG.md` (2,427,233) |
| PZ-11 | `conftest.py` comment, `STATA_SAS_QUICKSTART.md`, `test_inventory_invariants.py` docstring |

**Deferred (explicit):** PZ-NB notebooks; PZ-MS manuscript (D.4); convenience CSV extension to 2023–2024.

## VERIFY

- Grep: no `1992-2022` / `29-year` / V2.0 quickstart docstring in JOINT_USE, quickstart.py
- `pytest tests/ -k inventory` — 3 passed
- No edits under `output/` parquets or harmonize scripts
- C8.20 appendix marker block not regenerated (manual schema-note patch only; full regen requires build-host parquet)

## §10 self-check

VERIFY would not catch: a missed stale string in `docs/WORKED_EXAMPLE_FAQ.md` or natality README; C8.20 per-variable panels still internally consistent but other appendix variables might retain historical V2.0 slice notes in `_Schema note_` lines not grep-targeted. Mitigation: optional post-fix grep `1992-2022` across `docs/` + `fetal_death/*.md` before Zenodo.

## Forward-looking HALTs

1. D-prep.5 Tier A CLOSED — optional `/ultrareview` after fixes; notebook paths (PZ-NB) still open.
2. Manuscript + `paper_companion` → Phase D.4.
3. Build-host `shasum` on 4 gate parquets before D.2.
4. Phase D per-step human go-ahead unchanged.
