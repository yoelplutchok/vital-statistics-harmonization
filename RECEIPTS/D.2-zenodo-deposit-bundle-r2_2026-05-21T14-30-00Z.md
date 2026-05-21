# RECEIPT — D.2 Zenodo deposit bundle (r2): self-describing, modeled on prior deposits

**UTC:** 2026-05-21T14:30:00Z
**Supersedes:** the bundle-scope sections (§2 + §6.2) of `RECEIPTS/D.2-zenodo-deposit-prep_2026-05-21T13-30-00Z.md` (r1). r1 retained (append-only); its gate re-hash (§3), upload runbook (§4), and post-publish edits (§5) still apply unchanged.
**Why:** user directive 2026-05-21 — *"all I should deposit are the parquets? how about the rest of the things that are useful — I want to model it after the previous Zenodo uploads."* The prior **fetal v2.0.0** deposit (`fetal_death/PROVENANCE.sha256`) and **natality** deposits were **self-describing data packages** (parquets + every user doc + schema/validation/layout CSVs + quickstart + LICENSE/CITATION/PROVENANCE/.zenodo.json), **not** parquets-only — and they did **not** ship the pipeline `scripts/` (code lives on GitHub). The unified HVS deposit follows that exact model across all four products + a cross-product layer.
**Canonical-state mutation:** none. `.zenodo.json` aligned to prior conventions (added `affiliation`, `subjects`, NCHS `isDerivedFrom`); this receipt added. 4 gate SHAs unchanged.

---

## Deposit bundle — what to upload

> Build-host parquet locations: fetal `~/Desktop/fetal-death-harmonization-build/output/harmonized/`; natality+linked `~/Desktop/natality-harmonization/output/harmonized/`; matched-multiples in-repo `matched_multiples/output/harmonized/`. Per-year raw parquets/zips under each subproject's `output/yearly_clean/`.

### A. Cross-product / top-level (new for the unified deposit)
- `README.md`, `PROJECT_STRUCTURE.md`, `LICENSE`, `CITATION.cff`, `.zenodo.json`
- env: `requirements.txt`, `pyproject.toml`, `uv.lock`
- access helpers: `views.sql`, `STATA_SAS_QUICKSTART.md`
- `docs/`: `JOINT_USE_GUIDE.md`, `COMPARABILITY.md`, `PRIOR_ART.md`, `NCHS_SOURCE_MANIFEST.md`, `WORKED_EXAMPLE_FAQ.md`, `PERINATAL_RECORD_FEASIBILITY.md`
- `migrations/`: `v2.0.0-to-v2.4.0-fetal-death.md`, `v2.7.0-to-v2.8.0-natality.md`
- `csv/published_tabulations/`: `README.md` + the 10 cross-tab CSVs
- `notebooks/*.ipynb` worked examples (executed) — `joint_use_demo`, `paper_companion`, `matched_multiples_demo`, `maternal_age_stratified_imr` (run clean); `preterm_outcomes_time_series`, `cross_race_fetal_mortality`, `education_gradient`, `state_reporting_quirks` **only after a clean re-execution** (STATUS 2026-05-20T21:30 flagged pre-existing execution drift in preterm/cross_race) — else ship those as source-only or omit
- `SHA256SUMS.txt` (generated on build host at upload, step r1-§3)

### B. Fetal death — `fetal_death/` (v2.4.0)
- **Parquets:** `fetal_death_harmonized.parquet` (`38e2cecb…`), `fetal_death_derived.parquet` (`185c071e…`), baselines `fetal_death_harmonized.V1_baseline.parquet` / `fetal_death_derived.V1_baseline.parquet` / `fetal_death_harmonized.V3b_baseline.parquet` / `fetal_death_derived.V3b_baseline.parquet`, raw bundle `fetal_death_yearly_raw_1982-2024.zip` (43 per-year files)
- **Docs:** README, ABOUT_SOURCE_DATA, ABOUT_THIS_RELEASE, CODEBOOK, COMPARABILITY, FAQ, GETTING_STARTED, REPRODUCING, REPORTING_THRESHOLDS, V2_1992 / V2_1_2003_2004 / V3a_1989_1991 / V3b_1982_1988 layout-decisions, PROVENANCE.md, quickstart.py, quickstart.R
- **CSVs:** external_validation_targets, file_inventory, harmonized_schema, live_births_by_year, stratified_denominators, record_layout_{1982_1988,1992,2003,2004,2006,2014,2022}, reporting_thresholds, validation_results, validation_tracking, variable_crosswalk_working

### C. Natality + linked — `natality/` (natality v3.0.0 + linked v4.0.0)
- **Parquets:** `natality_v2_harmonized.parquet` (`c8a740eb…`), `natality_v2_harmonized_derived.parquet` (`acb5c48a…`), `natality_v3_linked_harmonized.parquet` (`ea89ab3c…`), `natality_v3_linked_harmonized_derived.parquet` (`f630d8cf…`), baselines (v28 ×2, v3 ×2), raw per-year bundles (natality 1968–2024; linked 1983–2023, 1992–1994 gap) — **size driver; see note below**
- **Docs:** README, REPRODUCING, docs/{ABOUT_THIS_RELEASE, CODEBOOK, COMPARABILITY, FAQ, GETTING_STARTED, VALIDATION}, PROVENANCE.md, quickstart.R, quickstart_linked.R, notebooks/quickstart.ipynb
- **metadata/:** harmonized_schema, external_validation_targets_v1, external_validation_targets_v3_linked, file_inventory
- **output/validation/:** external_validation_v1_comparison.md, external_validation_v3_linked_comparison.md

### D. Matched multiples — `matched_multiples/`
- **Parquets:** `matched_multiples_harmonized.parquet` (`adbec108…`, verified locally), 3 per-window raw parquets (`5c22308b…`, `7c682668…`, `d98b4296…`)
- **Docs:** README, ABOUT_SOURCE_DATA, PROVENANCE.md
- **CSVs:** harmonized_schema, file_inventory, record_layout_{1995_1997,1995_2000,2016_2020}, validation_results.csv + .md

---

## Excluded (consistent with the prior model + the D.3 scrub principle)
- **Pipeline code** `*/scripts/` and `*/tests/`, `__init__.py`, `requirements-dev.txt` — code lives on **GitHub**; the deposit links to it (`isSupplementedBy`). (Re-include `scripts/` only if you want a single fully-self-contained reproducibility archive — the prior deposits did not.)
- **Process docs / papers:** STATUS, DECISION_LOG, FIX_LOG, LESSONS, NEXT_STEPS, KICKOFF, PRE_FLIGHT_LOG, EXPLORATION_REPORT, VERSION_ROADMAP, `RECEIPTS/`, `AUDITS/`, `.claude/`, `paper/`, `notebooks/_build_*.py`, `notebooks/ananth2022_*.py`, `docs/PIPELINE_TIMING_BENCHMARK*`, the copyrighted Ananth PDF.
- **Figures** `*/figures/` — the prior fetal deposit omitted them; include only if you want them in the archive.
- **Raw NCHS source zips / raw_docs** — reproducible from `file_inventory.csv` + `docs/NCHS_SOURCE_MANIFEST.md` SHAs; the harmonized per-year raw *parquets* (section B/C/D) are the deposited preservation copy.

## Size note
Harmonized + derived parquets ≈ **8.27 GB**. Adding baselines + per-year raw bundles (natality 1968–2024 raw is the dominant driver) can push the record to **~15–30+ GB** — measure on the build host. Zenodo's default per-record quota is 50 GB; request more in-UI if needed, or split raw bundles into a second linked deposit. **Decision for human:** include the raw per-year bundles (full preservation, matches prior fetal deposit) vs. harmonized+derived+baselines only (rely on GitHub-pipeline reproduction for raw). Default if unsure: include raw, to match the prior model.

## Gate re-hash (unchanged from r1 §3) — MANDATORY before upload
Re-hash on the build host and confirm the 4 gate SHAs (`38e2cecb` / `185c071e` / `acb5c48a` / `f630d8cf`); also verify the harmonized + baseline parquet SHAs against each `PROVENANCE.md`; capture all into `SHA256SUMS.txt`. Any mismatch → §7-#18 halt; do not upload.

## §10 self-check — what could be wrong that VERIFY wouldn't catch?
- The exact prior **natality** deposit file list isn't pinned in-repo (no `natality/PROVENANCE.sha256`); section C is modeled by analogy to the fetal v2.0.0 `PROVENANCE.sha256` + the natality user-facing inventory. If you want byte-for-byte parity with the actual natality v2.7.0 deposit, cross-check its Zenodo file list before upload.
- A few worked-example notebooks had execution drift (STATUS 2026-05-20T21:30) — re-execute or omit before depositing so the archive doesn't ship a notebook that errors on Run-All.
- `license: cc-by-4.0` / `subjects` term strings should be confirmed against the Zenodo picker at upload (UI is authoritative for a manual deposit).
