# RECEIPT — D.2-docs — zenodo-docs-only-v1.0.2-validation-sync — 2026-05-26T14:00:00Z

**Task.** §15.G D.2-docs — prepare Zenodo **v1.0.2** docs-only bundle (validation tables + deposit metadata; parquets unchanged).

## PRE-FLIGHT

- **Targets CSV:** `external_validation_targets_v1.csv` (249 rows with expected values); `external_validation_targets_v3_linked.csv`; `matched_multiples/external_validation_targets.csv` (143 targets).
- **Stale deposit state:** v1.0.1 comparison summary **215 pass** (natality); `.zenodo.json` cited 183/183 + 97 linked cols.
- **Field-value snapshot:** Linked derived gate documented `22a4523d6e62e018acd1c8648275a9f98d86ee711f61c017f885df6952b73b5e` in `natality/PROVENANCE.md`; build-host `shasum` confirmed match.
- **Halt conditions:** none tripped.

## SMOKE

Doc-only task: structural smoke = grep scope for stale `183/183`, `215/215`, `97 columns` in deposit-facing paths before/after DO.

## DO

1. Regenerated `natality/output/validation/external_validation_v1_comparison.{csv,md}` from build-host parquet (`acb5c48a…` path) + yearly_clean for pre-1989 SAMPWT.
2. Regenerated `natality/output/validation/external_validation_v3_linked_comparison.{csv,md}` (35 pass; 100 columns).
3. Synced natality user docs (`VALIDATION.md`, `ABOUT_THIS_RELEASE.md`, `GETTING_STARTED.md`, `FAQ.md`, `COMPARABILITY.md`, `README.md` honest-validation line).
4. Bumped root `.zenodo.json`, `CITATION.cff`, `README.md` citation note, `CHANGELOG.md` [1.0.2], `VERSION_ROADMAP.md`.
5. Added `docs/ZENODO_v1.0.2_UPLOAD.md` human runbook.

## VERIFY

| Check | Result |
|---|---|
| Natality comparison | **249 pass / 0 fail / 0 missing** |
| Linked comparison | **35 pass / 0 fail / 0 missing**; script reports 100 columns |
| Matched multiples | `validation_results.md` already **143/143** (MM-T2; unchanged this session) |
| Linked gate SHA on build host | `22a4523d6e62…` matches PROVENANCE |
| Parquet mutation | **none** (read-only compare scripts) |
| Stale `183/183` in natality/docs | cleared (grep) |

## Git

Doc/CSV/MD only; commit at session end per kickoff.

## Forward-looking HALTs for next session

1. **D.4-paper:** build-host `paper_companion` + `cross_race_fetal_mortality.ipynb`; resolve `<!-- FLAG -->` markers.
2. **Human Zenodo:** publish v1.0.2 per `docs/ZENODO_v1.0.2_UPLOAD.md`; re-hash four gate SHAs before upload; halt on any mismatch.
3. After v1.0.2 publish: optional manuscript footnote update (v1.0.2 deposited vs “will align”).
4. Natality `acb5c48a…` byte-exact unless LY-natality-2025 or other data task documents drift.

## Self-check (§10)

Could have shipped comparison tables built against wrong parquet path — mitigated by explicit build-host `--in` paths and gate SHA verify. Could have missed a stale validation count in a non-grepped doc (e.g. `notebooks/README.md` still mentions 183/183) — deposit zip follows D.2 r2 file list, not every monorepo path; D.4 or a follow-up grep can catch notebook copy.
