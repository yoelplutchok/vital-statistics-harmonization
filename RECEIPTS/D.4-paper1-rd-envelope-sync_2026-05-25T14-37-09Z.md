# RECEIPT — D.4-paper1-rd-envelope-sync — 2026-05-25T14:37:09Z

**Task.** Post–RD.1b manuscript sync + IJE trim on `paper/draft_v2_hmd_styled.md`. Doc-only; zero canonical-state mutation.

## PRE-FLIGHT

`PRE_FLIGHT_LOG.md` 2026-05-25T14:37:09Z — PROCEED. User "go" = `paper/` authorized.

## SMOKE

Word-count proxy (Basics→Access, excl. table/figure lines, footnote defs stripped): **~2,275 words** ≤ 2,500. Key Features: **~181 words** ≤ 200.

## DO

- Validation headlines: **249/249** natality, **109/109** matched multiples, linked 33/35 + pre-2005 cohort checks unchanged.
- Footnotes: `[^zenodo_validation]`, `[^mm_validation]`, `[^pre1990_1968]` (1968 indirect LBW + PUF-definitional preterm; LMP denominator).
- Deposit wording: four products / harmonized+derived pair (Key Features, Data resource use, S&W).
- Future developments: removed shipped pre-1990 benchmarking bullet.
- Condensed S&W, case studies, coverage, basics, methods for word budget.

## VERIFY

- `grep -c "249/249" paper/draft_v2_hmd_styled.md` → 1 (S&W).
- `grep -c "109/109" paper/draft_v2_hmd_styled.md` → 2 (case study 2 + S&W).
- No edits to `natality/metadata/external_validation_targets_v1.csv` or parquets.
- **Not run this session:** `paper_companion` (build host); gate SHA re-hash.

## Forward-looking HALTs for next session

1. Build host: re-run `notebooks/_build_paper_companion.py` → all PASS.
2. Execute `cross_race_fetal_mortality.ipynb` (case study 3 FLAG).
3. Publish Zenodo docs-only v1.0.2 before submission.
4. Human: resolve `<!-- YP -->` admin markers + abstract word-limit check.

## §10 self-check

Word-count proxy may differ from IJE submission system by a few percent — margin ~225 words. paper_companion not re-run — a stale claim could survive if trim accidentally dropped a guarded number; mitigated by grep of headline counts (201,161,456; 249/249; 109/109; DOI lines preserved).
