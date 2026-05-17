# Changelog

All notable changes to the U.S. Harmonized Vital Statistics (HVS) resource are documented here. The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Versioning operates at two layers:

- **Monorepo version (v1.x)** — this changelog's primary axis. Tracks the unified resource as published at https://github.com/yoelplutchok/vital-statistics-harmonization.
- **Per-product version** — natality `v2.x`, fetal-death `v2.x`, linked `v3.x` — tracked in each sub-product's `ABOUT_THIS_RELEASE.md` and reflected in Zenodo concept-DOI version patches at each release. Per-product versions cadence independently; the monorepo version increments capture cross-product additions and protocol-level changes.

Each section below cites the per-task receipts (in `RECEIPTS/` of the development monorepo; not shipped in public releases) so that readers can trace every claim to a five-phase PRE-FLIGHT / SMOKE / DO / VERIFY / RECEIPT audit trail.

---

## [Unreleased / v1.1-WIP] — Tier 1 + Tier 2 work (Phase C of pre-submission scope expansion)

Work in progress as of 2026-05-13. Will tag as `v1.1` at the next public-repo sync once Phase C completes (or sooner if Tier 1 completes and Tier 2 is split into `v1.2`). Task identifiers (`C8.1`, `C8.4`, …) reference `NEXT_STEPS.md` §15.C entries.

### Data extensions

(Tier-1 had none new beyond the latest-year refresh below; major data extensions shipped in `v1.0`. Tier-3+5 backward extensions begin with **C8.17 natality v3.0.0** below.)

- **C8.17** — **Natality 1968–1989 backward extension → v3.0.0.** Natality coverage extended from 1990–2024 (35 years) to **1968–2024 (57 years)**: 22 pre-1990 NCHS public-use natality files parsed across four earlier layouts (1968 81-byte; 1969–1971 215-byte; 1972–1988; 1989 = 1990-layout sibling) and re-harmonized into the existing 71-column schema (84 with derived). Canonical parquet is now **201,161,456 records** (= 138,819,655 v2.8 1990–2024 + 62,341,801 1968–1989, exactly). The 1990–2024 slice is byte-clean (0/35-year content drift vs the preserved v2.8 baseline; verified at DO step 6 via `pyarrow.Table.equals`). `certificate_revision` gains a fourth value `unrevised_1968` (1968–1988 = 1968-revision certificate); `harmonized_schema.csv` `years_available` widened to 1968–2024. Existing 183/183 NVSR benchmarks (1990–2024) preserved byte-exact; pre-1990 NVSR benchmarking is a planned incremental addition. Major version bump (v2.8.0 → v3.0.0) per the H10 reproducibility-gate cascade: universal row-count/SHA change + a new certificate-revision era boundary. Schema-additive over v2.8.0 — existing 1990–2024 analyses run unchanged. The 7 non-natality-v2 canonical parquet SHAs (fetal-death ×2, linked ×1, matched-multiples ×4) are byte-exact (only natality changed). (Receipts: `RECEIPTS/C8.17_step1…step7_*.md`.)

- **C8.2** — Latest-year fetal-death refresh: NCHS public-use 2023 + 2024 files harmonized into the existing v2.0 + V2.1 + V3a + V3b envelope. Fetal-death coverage now spans **1982–2024 (43 years, 2,352,011 records)**. NVSR per-year validation cells re-extended through 2024. (Receipt: `RECEIPTS/C8.2_2026-05-12T23-30-00Z.md`.)

### Robustness / testing / infrastructure

- **C8.1** — `fetal_death/tests/test_release_smoke.py` retagged to the v2.4.0 envelope (43-yr / 2.35M records) with a `DESIGN: tracks-current-state` first-docstring tag per Convention 2. New `fetal_death/tests/test_schema_dtype_parity.py` adds a durable H8-class defense: every row in `harmonized_schema.csv`'s `type` column must match the parquet's pyarrow dtype. An `xfail(strict=True)` documents the 49 known `string`-declared-as-`int` columns pending a future v3.x schema reconciliation. (Receipt: `RECEIPTS/C8.1_2026-05-12T22-00-00Z.md`.)
- **C8.4** — Three monorepo-root invariant-test harnesses authored at `tests/`:
  - `tests/test_canonical_filter_invariants.py` — sum-across-strata equals unstratified-total for every canonical filter, every product, every year.
  - `tests/test_row_count_conservation.py` — input rows equal output rows plus documented drops at every pipeline boundary.
  - `tests/test_cross_product_join_parity.py` — natality joined to fetal-death and linked produces the expected demographic-stratum row counts.
  - 41 invariant tests + 12 paired mutation tests (Tier-0 L3 defense; each mutation test injects a known violation and asserts the harness catches it). (Receipt: `RECEIPTS/C8.4_2026-05-13T03-00-00Z.md`.)
- **C8.7a** — Static path-constant audit across 31 per-step pipeline scripts (10 fetal-death + 21 natality) caught 5 L13-extension path-drift bugs in 2 fetal-death scripts (`fetal_death/scripts/05_validate/validate_2022.py` and `fetal_death/scripts/run_pipeline.py`); both patched on contact. Documents 2 additional natality scripts with broken default output paths as deferred to the orchestrator-authoring task `C8.7b`. (Receipt: `RECEIPTS/C8.7a_2026-05-13T08-30-00Z.md`.)
- **Test-infra namespace fix** — Four new `__init__.py` files added at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/` to make the dual `test_schema_dtype_parity.py` modules namespace-distinct under pytest's default `prepend` import mode. Fixes a basename-collision (L17-extension) surfaced on clean `__pycache__` runs. (FIX_LOG 2026-05-12T22:30:00Z.)

### Distribution / reproducibility infrastructure

- **C8.5a** — Pinned Python 3.13 environment via `uv` lockfile:
  - New `pyproject.toml` at monorepo root (PEP 621 metadata, `requires-python = ">=3.13,<3.14"`, 6 runtime + 2 dev dependencies, `[tool.uv] package = false`).
  - New `uv.lock` (38 packages resolved deterministically; reruns produce bit-identical output).
  - New `.python-version` (single line `3.13`).
  - `README.md` gains a "Pinned environment via `uv` lockfile" subsection under "## Reproducibility".
  - `uv sync` on a fresh machine reproduces the canonical build environment exactly; cache-cleared `uv run pytest fetal_death/tests/ natality/tests/ tests/` returns **56 passed + 1 xfailed** in approximately 110 seconds. (Receipt: `RECEIPTS/C8.5a_2026-05-13T05-00-00Z.md`.)
- **C8.6** — GitHub Actions continuous integration:
  - New `.github/workflows/ci.yml` (single-job `ubuntu-latest`, Python 3.13 sourced via `astral-sh/setup-uv@v6` pinned to `0.11.x`).
  - Steps: `actions/checkout@v5` → `setup-uv@v6` → `uv lock --check` → `uv sync --frozen` → `uv run pytest fetal_death/tests/ natality/tests/ tests/`.
  - Triggers: push on `main` + pull_request on `main` + manual `workflow_dispatch`. Concurrency control cancels in-flight runs on rapid pushes.
  - Locally-emulated workflow reproduces the C8.5a baseline (56 passed + 1 xfailed in 108.81s); live-CI green-check VERIFY closes at the next public-repo sync. (Receipt: `RECEIPTS/C8.6_2026-05-13T06-30-00Z.md`.)

### Cross-product / joint-use enhancements

- **C8.3** — Cross-product Tier-1 work:
  - `notebooks/cross_product_timeline.ipynb` — era-boundary visualization with all three products on one timeline (revision-boundary bands; coverage-gap shading).
  - Perinatal-mortality joint computation: rate = (fetal deaths ≥28 weeks + infant deaths <7 days) ÷ (live births + fetal deaths ≥28 weeks) × 1000, computed by year and by race using all three products.
  - 2017 race-stratified NVSR validation (the Section B 2017 fragment originally deferred from Task 2). (Receipt: `RECEIPTS/C8.3_2026-05-13T00-30-00Z.md`.)

### Docs

- **C8.8 (this release)** — `CHANGELOG.md` authored at monorepo root (this file). `docs/PRIOR_ART.md` extended with:
  - A post-Ananth-2022 citation pair (Gregory ECW, Barfield WD 2024 *Semin Perinatol* [PMID 38143212](https://pubmed.ncbi.nlm.nih.gov/38143212/); NICHD Stillbirth Working Group Report, July 2024).
  - A new "GitHub precursors" subsection covering `Mikuana/vitalstatistics`, `arebe/cdc-natality`, and `damiancclarke/nchs-fetaldata` — partial precursors that do not harmonize across the 1989/2003 boundary, do not cover all three products, and do not validate against NVSR.
  - A one-sentence note on HL7's [fhir-bfdr](http://hl7.org/fhir/us/bfdr/) prospective FHIR-based reporting standard.
  - A new "Out-of-scope vital-events series" subsection naming marriage/divorce, multiple-cause-of-death (all-age mortality), and abortion surveillance as deliberately excluded from HVS's vital-events-around-birth scope. (Receipt: `RECEIPTS/C8.8_2026-05-13T<UTC>.md`.)

### Breaking / deprecations

(none new in `v1.1`; the natality v2.7.0 → v2.8.0 column rename shipped in `v1.0` — see below.)

### Deferred to a later `v1.x`

- **C8.5b** — `Dockerfile` providing a one-command full-pipeline rebuild. Deferred at C8.5 PRE-FLIGHT pending `docker` runtime availability AND a monorepo-root pipeline orchestrator from `C8.7b`. (DECISION_LOG 2026-05-13T04:30:00Z.)
- **C8.7b** — Monorepo-root pipeline orchestrator + Tier-1 single-year per-product re-build + Tier-2 full byte-identical re-derive of all four parquets. Deferred at C8.7 PRE-FLIGHT pending an explicit multi-session compute window (estimated 6–12+ hours of compute). (DECISION_LOG 2026-05-13T07:40:00Z.)
- **C8.9 – C8.15** — Tier-2 task block: usability layers (state-stratified denominators, R quickstart, DuckDB views), worked-example notebooks (maternal-age-stratified IMR, preterm time series, cross-race fetal mortality, education gradient, state reporting quirks), migration guides (v2.7.0→v2.8.0 natality, v2.0.0→v2.3.0 fetal death), cross-product `COMPARABILITY.md`, mutation-test scaffolding for every validator, sub-project SHA manifest, parquet column-dictionary tuning, GitHub release artifacts, worked-example FAQ, `PROJECT_STRUCTURE.md` upgrade. Authorized in `EXPLORATION_REPORT.md` §G.4 + DECISION_LOG 2026-05-12T21:00:00Z; queued post-C8.8.

---

## [v1.0] — 2026-05-12

First public release of the unified U.S. Harmonized Vital Statistics monorepo at https://github.com/yoelplutchok/vital-statistics-harmonization (commit `a18ca3a`). Built by rsync of the development monorepo with the protocol-state files excluded (`STATUS.md`, `DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `NEXT_STEPS.md`, `KICKOFF.md`, `PRE_FLIGHT_LOG.md`, `RECEIPTS/`, `.claude/`, `paper/` manuscript drafts, `EXPLORATION_REPORT.md`, internal `_build_*.py` notebook builders).

### Three products

- **Natality v2.8.0** — 35 years (1990–2024); 138,819,655 records; 84 columns (71 harmonized + 13 derived). NVSR *Births: Final Data* targets 183/183 byte-exact. Column rename from v2.7.0: `year` → `data_year`, `restatus` → `residence_status`, `maternal_race_bridged4` → `maternal_race_bridged`, `maternal_hispanic_origin` → `hispanic_origin`. (Receipt: `RECEIPTS/natality_v28_rename_2026-05-12T13-35-02Z.md`.)
- **Linked birth–infant death v3** — 19 years (2005–2023); 74,943,824 records; 94 columns (87 harmonized + 7 derived death-side). 33/35 NVSR targets byte-exact; 2 cells differ by exactly 1 record (null-record-weight survivors documented upstream in NCHS). See `natality/output/validation/external_validation_v3_linked_comparison.md`.
- **Fetal death v2.0 + V2.1 + V3a + V3b** — combined coverage 1982–2022; 1,634,195 → 2,352,011 records across the four extensions; 89 columns (73 harmonized + 16 derived). NVSR *Fetal Mortality* 29/29 per-year counts + 26/26 per-year fetal mortality rates byte-exact; 13/19 detail cells byte-exact + 6 documented diffs.

### Tasks completed in Phase A (2026-05-11 → 2026-05-12)

(Task IDs reference `NEXT_STEPS.md` §15 pre-Phase-C entries; receipts at `RECEIPTS/` in the development monorepo.)

- **Task 1** — Joint-use convenience layer: `shared/helpers/canonical_join_keys.py` + `shared/helpers/build_stratified_denominators.py` + `fetal_death/stratified_denominators.csv` (29 joint-coverage years, 114.9M records; 29/29 per-year sums byte-exact against the natality NVSR target).
- **Task 2** — `notebooks/joint_use_demo.ipynb`: Section A 2022 age-stratified fetal mortality (8/8 NVSR cells byte-exact); Section B 2017 race-stratified fetal mortality (joint-use demonstration). First `FIX_LOG.md` entry filed (H8 fetal-death dtype drift on five demographic columns).
- **Task 3 V2.1** — Fetal-death 2003–2004 transition years added (+107K records; 1.63M → 1.74M); H8 dtype reconciliation alongside.
- **Task 4** — `notebooks/paper_companion.ipynb` — 55 manuscript numeric claims mapped to source-of-truth artifacts (25 PASS / 20 CITE-ONLY / 4 L11 / 1 DIFF). Five author-side precision-edit candidates inlined for Task 5.
- **Task 5** — Manuscript trim + admin sections; integrated Task 4's findings.
- **Task 6** — Linked-file validation framing canonicalized as "33/35 byte-exact + 2 cells differ by 1 record."
- **Task 7 V3a** — Fetal-death 1989–1991 backward extension (+188K records; 3 years).
- **Task 7 V3b** — Fetal-death 1982–1988 backward extension (+421K records; 7 years; with B3 1-digit-recode caveats documented for code-7 and code-9 race null handling).
- **Natality v2.7.0 → v2.8.0 column rename** — bundled with Tasks 3/4/5 follow-through.
- **Public repo first push** — 2026-05-12 to https://github.com/yoelplutchok/vital-statistics-harmonization (commit `a18ca3a`).

### Validation

All three products validated end-to-end against every per-year figure NCHS publishes in NVSR series under each product's canonical analytic filter. Verification scripts at `<product>/scripts/05_validate/`; per-target pass/fail tables at `<product>/output/validation/`.

### Reproducibility

Per-subproject pipelines are deterministic; re-deriving the parquets from a fresh download of the NCHS source zips produces byte-identical files. SHA-256 checksums for every shipped artifact in each product's `PROVENANCE.md` (where applicable) and `metadata/file_inventory.csv`.

### License

CC BY 4.0 (harmonized data) + MIT (source code).

---

## Notes for the public-repo reader

The development monorepo operates under a five-phase task discipline (PRE-FLIGHT → SMOKE → DO → VERIFY → RECEIPT) with a 17-class mistake-class matrix defense. Internal state files (`STATUS.md`, `DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `NEXT_STEPS.md`, `KICKOFF.md`, `PRE_FLIGHT_LOG.md`, `RECEIPTS/`) live in the development monorepo only and are excluded from public releases via the rsync scrub list. References to receipts above are anchored against the development monorepo's commit history; tagged commits (`task7_v3b-complete`, `C8.7a-complete`, etc.) provide the verifiable trail for each shipped change.
