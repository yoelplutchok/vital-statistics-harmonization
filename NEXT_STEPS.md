# Next steps — detailed handoff plan

**Purpose:** This document is the canonical plan for everything left to do on the U.S. Harmonized Vital Statistics (HVS) resource before the Data Resource Profile manuscript is ready for submission. It is written for both human readers and LLM agents resuming work in a fresh session, and is deliberately self-contained: a fresh agent should be able to read this file plus `README.md` and `PROJECT_STRUCTURE.md` and have full context.

**Last updated:** 2026-05-08, immediately after the initial monorepo migration commit (`7fd9cdf`).

---

## 0. Onboarding (read these first, in this order)

If you are an LLM agent or new human collaborator picking this up, read in order:

1. **[`README.md`](README.md)** — what the resource is, three products at a glance, where things live.
2. **[`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)** — full file-by-file map. Use this when you need to find something.
3. **[`VERSION_ROADMAP.md`](VERSION_ROADMAP.md)** — what's shipped, what's planned at high level. (This document, NEXT_STEPS.md, is the *detailed* version of what's planned.)
4. **[`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md)** — canonical join keys, analytic filters, worked-example pseudocode. Read before doing anything cross-product.
5. **[`docs/PRIOR_ART.md`](docs/PRIOR_ART.md)** — literature gap motivating the harmonization. Cited from the manuscript.
6. **[`paper/draft_v2_hmd_styled.md`](paper/draft_v2_hmd_styled.md)** — current preferred manuscript draft. Modeled on the IJE Data Resource Profile for the Human Mortality Database (Barbieri et al., 2015). The other draft (`draft_v1_ipums_styled.md`) is superseded.
7. Each subproject's README and ABOUT (in `natality/README.md`, `fetal_death/README.md`, `fetal_death/ABOUT_THIS_RELEASE.md`, `natality/docs/ABOUT_THIS_RELEASE.md`).

You should also confirm orientation with `git log --oneline -10` and `ls -F` at the repo root.

---

## 1. Project context (what this resource is, why it exists)

The U.S. National Center for Health Statistics (NCHS) releases public-use natality, linked birth–infant death, and fetal death microdata as annual fixed-width files whose layouts have changed multiple times. Three boundary types make cross-year analyses difficult: (i) the 1989-to-2003 U.S. Standard Certificate revision; (ii) within-revision NCHS reformats; (iii) state-by-state staggered adoption of the 2003 revision. Researchers have historically been forced into single-revision analytic windows (see `docs/PRIOR_ART.md`).

This resource integrates and disseminates the three NCHS public-use microdata products as three companion harmonized parquet files with one stable column schema per product, validated against every per-year aggregate NCHS publishes in the relevant *National Vital Statistics Reports* (*NVSR*) series.

**Three products (current state, as of 2026-05-08):**

| Product | Coverage | Records | Columns | NVSR validation |
|---|---|---|---|---|
| Natality | 1990–2024 | 138,819,655 | 84 | 183/183 byte-exact |
| Linked birth–infant death | 2005–2023 | 74,943,824 | 94 | 35/35 (or 33/35 + 2 docs diffs — verify; see Task 6) |
| Fetal death | 1992–2022 (excl. 2003–2004) | 1,634,195 | 89 | 29/29 counts + 26/26 rates exact; 13/19 detail-cell + 6 docs diffs |

**Repository state (as of 2026-05-08):**
- Initial monorepo migration committed at `7fd9cdf`.
- `natality/` mirrors v2.7.0 of the natality-harmonization repo.
- `fetal_death/` mirrors v2.0.1 of the fetal-death-harmonization repo (large parquets and the `fetal_death_yearly_raw_1992-2022.zip` are .gitignored; they live in Zenodo).
- The two original repos (yoelplutchok/natality-harmonization, yoelplutchok/fetal-death-harmonization) on GitHub are unchanged and still represent the published Zenodo deposits. The user plans a new unified Zenodo deposit anchored to this monorepo.

---

## 2. Tasks, in priority order

Each task has a fixed format: **Goal** (what done looks like), **Why this matters** (manuscript or roadmap link), **Inputs** (what to read/load), **Approach** (concrete steps), **Output artifacts** (files to create or modify), **Validation** (how to know it's correct), **Estimated effort**, **Dependencies**.

---

### Task 1 — Joint-use convenience layer (stratified live-birth denominators)

**Goal.** Ship a single parquet (or CSV) inside the fetal-death deposit that gives demographically stratified live-birth counts by year, so that users can compute fetal mortality rates by race × age × ethnicity without loading the 138.8M-row natality file.

**Why this matters.** The manuscript's strongest claim is that the three products are "designed for joint use." Currently the only convenience denominator file in the fetal-death deposit is `fetal_death/live_births_by_year.csv`, which is unstratified. Adding stratified denominators is the single highest-leverage addition for the paper's credibility, and is listed as the joint-use convenience layer in `VERSION_ROADMAP.md`.

**Inputs.**
- Natality parquet: produced by `natality/scripts/03_harmonize/harmonize_v1_core.py` and `natality/scripts/04_derive/derive_v1_core.py`. The shipped parquet is in the natality Zenodo deposit (DOI 10.5281/zenodo.19868835), not in this repo.
- Canonical natality filter: `restatus != '4'` (U.S. residents only). See `docs/JOINT_USE_GUIDE.md`.
- Stratification columns to use (must exactly match the fetal-death harmonized schema): `data_year`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`. (Verify these against `fetal_death/harmonized_schema.csv` and `natality/metadata/harmonized_schema.csv` — both products use the same harmonized names per the joint-use guide, but the LLM should confirm before computing.)

**Approach.**
1. Verify the natality parquet is downloadable and accessible. If not on disk, the user must place it under `natality/output/` (path determined by `natality/.gitignore` and `natality/REPRODUCING.md`).
2. Write a script `shared/helpers/build_stratified_denominators.py` that:
   - Loads the natality derived parquet.
   - Applies `restatus != '4'`.
   - Groups by `data_year` × `maternal_age_recode` (or 5-year bands) × `maternal_race_bridged` × `hispanic_origin`.
   - Writes a long-format parquet `fetal_death/stratified_denominators.parquet` with columns `data_year, maternal_age_band, maternal_race_bridged, hispanic_origin, live_births`.
3. Decide between full-detail strata (one row per cell) vs paper-relevant strata only. Recommend full-detail because storage is cheap (a few MB) and downstream users can aggregate.
4. Update `fetal_death/README.md` and `fetal_death/CODEBOOK.md` to document the new file.
5. Update `docs/JOINT_USE_GUIDE.md` to point to the new file in the "Convenience" section.

**Output artifacts.**
- `shared/helpers/build_stratified_denominators.py` (new)
- `fetal_death/stratified_denominators.parquet` (new; .gitignored, lives in Zenodo)
- `fetal_death/stratified_denominators.csv.gz` (optional smaller text variant; .gitignored)
- Diff against `fetal_death/README.md`, `fetal_death/CODEBOOK.md`, `docs/JOINT_USE_GUIDE.md`.

**Validation.**
- Sum across strata for any year matches the unstratified count in `fetal_death/live_births_by_year.csv` (which itself is sourced from *NVSR 57-08* and *NVSR 73-09*).
- Spot-check a small number of cells against published *NVSR* tables (e.g., *NVSR 73(11)* Table 1 for natality by race, 2023).

**Estimated effort.** Half a session if natality parquet is on disk; one session if it has to be downloaded and validated first.

**Dependencies.** None. Can start immediately if natality parquet is accessible.

---

### Task 2 — `notebooks/joint_use_demo.ipynb`

**Goal.** A runnable Jupyter notebook that loads all three parquets, applies each canonical filter, joins on demographic strata, computes the fetal mortality rate per 1,000 (live births + fetal deaths) by maternal race for one representative year (recommend 2022), and matches each cell against *NVSR 73-09* Table A.

**Why this matters.** Demonstrates the manuscript's "designed for joint use" claim from outside the manuscript. Reviewers and skeptical readers can run it themselves.

**Inputs.**
- Pseudocode in `docs/JOINT_USE_GUIDE.md` ("Worked example: fetal mortality rate by maternal race, 2022").
- Both parquets (natality + fetal-death; downloaded from Zenodo or built from source).
- *NVSR 73-09* Table A figures (already encoded in `fetal_death/external_validation_targets.csv` for the unstratified case; stratified targets need to be transcribed from the PDF).

**Approach.**
1. Start from the pseudocode in `docs/JOINT_USE_GUIDE.md`.
2. Add the cross-product analytic-filter check (each product's canonical filter applied at load time).
3. Compute fetal mortality rate per 1,000 (live births + fetal deaths) by `maternal_race_bridged` for 2022.
4. Compare cell-by-cell against *NVSR 73-09* Table A (race-stratified 2022 figures).
5. Print a markdown pass/fail table at the bottom.
6. Save the notebook with executed outputs (so readers don't need to run it to see results).

**Output artifacts.**
- `notebooks/joint_use_demo.ipynb` (replaces stub described in `notebooks/README.md`).

**Validation.**
- Notebook runs end-to-end without manual intervention.
- Every cell matches *NVSR 73-09* Table A within rounding (or the diff is documented as it is for the unstratified case in the fetal-death repo).

**Estimated effort.** Half a session, depending on how much *NVSR 73-09* table transcription is needed.

**Dependencies.** Task 1 is helpful but not required (the notebook can load the full natality parquet directly if the stratified denominator file does not yet exist).

---

### Task 3 — Fetal-death V2.1 (add 2003 and 2004 transition years)

**Goal.** Bring fetal-death coverage to 1992–2022 (31 consecutive years) by parsing and harmonizing the two transition years currently deferred.

**Why this matters.** The manuscript currently has to footnote that 2003 and 2004 are missing. If V2.1 ships before submission, the manuscript can claim 31-year continuous coverage, simplifying the *Strengths and weaknesses* section.

**Inputs.**
- 2003 fetal-death zip from NCHS FTP (1351-byte records, mixed 1989/2003-revision content).
- 2004 fetal-death zip from NCHS FTP (1501-byte records, mixed 1989/2003-revision content).
- `fetaldeath0304problems.pdf` from NCHS FTP (NCHS's own documentation of the transition-year idiosyncrasies).
- Existing parser at `fetal_death/scripts/01_import/parse_fetal_year.py` and field specs at `fetal_death/scripts/01_import/field_specs.py`.
- The existing record-layout CSVs (`fetal_death/record_layout_1992.csv`, `record_layout_2006.csv`) bracket the transition; reconstruct 2003 and 2004 layouts by reading the NCHS transition-year user guides.

**Approach.**
1. Download the 2003 and 2004 zips and the `fetaldeath0304problems.pdf` from `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeath/`.
2. Reconstruct the 2003 and 2004 fixed-width layouts from the corresponding NCHS user guides. Save as `fetal_death/record_layout_2003.csv` and `fetal_death/record_layout_2004.csv`.
3. Extend `field_specs.py` to handle the transition layouts.
4. Per-state, identify which records follow the 1989-revision schema vs the 2003-revision schema (the `version` field at byte 7 in the 2003-revision case carries 'A' for revised, 'S' for unrevised; in 2003 and 2004 the file is mixed by state).
5. Apply the existing harmonization rules — same B1–B6 normalizations from V2.0 — to both halves.
6. Validate per-year counts against:
   - 2003: NCHS user-guide control counts; *NVSR 57-08* Table B (1995–2005, includes 2003 and 2004).
   - 2004: same sources.
7. Re-run `validate_external.py` and `validate_external_v2.py`.
8. Bump fetal-death version to v2.1.0; update `fetal_death/.zenodo.json`, `fetal_death/CITATION.cff`, `fetal_death/ABOUT_THIS_RELEASE.md`, and `fetal_death/README.md`.
9. Verify V1 byte-clean regression (the 2005–2022 slice must remain cell-identical to its V1 baseline; same as V2.0 → V2.1 must not perturb existing era data).

**Output artifacts.**
- `fetal_death/record_layout_2003.csv` (new)
- `fetal_death/record_layout_2004.csv` (new)
- Updated `fetal_death/scripts/01_import/parse_fetal_year.py` (transition-year branch)
- Updated `fetal_death/scripts/01_import/field_specs.py`
- Updated `fetal_death/external_validation_targets.csv` (add 2003, 2004 rows)
- Updated `fetal_death/validation_results.csv`
- Updated parquets (regenerated; .gitignored)
- Updated docs: `fetal_death/ABOUT_THIS_RELEASE.md`, `fetal_death/README.md`, `fetal_death/.zenodo.json`, `fetal_death/CITATION.cff`, `fetal_death/COMPARABILITY.md`, `fetal_death/FAQ.md`.
- Updated top-level `VERSION_ROADMAP.md`, `README.md`.
- Updated manuscript drafts (`paper/draft_v2_hmd_styled.md`).

**Validation.**
- Per-year counts for 2003 and 2004 match *NVSR 57-08* Table B exactly.
- V1 era (2005–2022) byte-clean: 0/73 harmonized + 0/89 derived columns drift after the V2.1 extension.
- Total per-year counts: 31/31 exact (was 29/29 in V2.0).
- Total per-year fetal mortality rates: 28/28 exact (was 26/26).

**Estimated effort.** One to two sessions. Layout reconstruction and per-state version branching is the main work; the harmonization rules are already implemented.

**Dependencies.** None. Can run in parallel with Tasks 1 and 2.

---

### Task 4 — `notebooks/paper_companion.ipynb`

**Goal.** A notebook that reproduces every numeric claim in the manuscript directly from the parquets, with each cell mapped to the paper paragraph it supports.

**Why this matters.** Demonstrates the reproducibility claim from outside the manuscript and makes peer review easier — the reviewer can run one notebook and see every paper number rebuilt from data.

**Inputs.**
- Current preferred manuscript: `paper/draft_v2_hmd_styled.md`.
- All three parquets.

**Approach.**
1. Walk through the manuscript and extract every numeric claim with its paragraph reference. Possible claims include:
   - 138,819,655 natality records
   - 74,943,824 linked records
   - 1,634,195 fetal-death records
   - 183/183 natality NVSR targets exact
   - 33/35 (or 35/35) linked targets exact
   - 29/29 fetal-death per-year counts
   - 26/26 fetal-death per-year rates
   - 13/19 detail-cell matches; 6 documented diffs
   - 700,704 V2-era + 933,491 V1-era fetal-death records
   - 98,500 byte-level comparisons returning 0 mismatches
2. For each claim, write a notebook cell that loads the relevant artifact (parquet, validation CSV, or schema CSV) and prints the value alongside the paper claim.
3. Emit a final markdown pass/fail table at the end.

**Output artifacts.**
- `notebooks/paper_companion.ipynb` (replaces stub described in `notebooks/README.md`).

**Validation.**
- Every cell matches the paper. If any cell does not, fix the paper.

**Estimated effort.** One session.

**Dependencies.** The manuscript should be reasonably stable first (Task 5 should ideally precede or run alongside this).

---

### Task 5 — Manuscript trim and admin sections

**Goal.** Bring `paper/draft_v2_hmd_styled.md` to the IJE Data Resource Profile main-text limit of 2,500 words, fill in admin sections (Author contributions, AI-tool disclosure, Funding), and finalize references.

**Why this matters.** Submission-ready manuscript.

**Inputs.**
- Current draft: `paper/draft_v2_hmd_styled.md` (~3,500 words).
- IJE author guidelines: https://academic.oup.com/ije/pages/Data_Resource_Profile_Series. Limits: 2,500 words main text (excluding abstract, key features, references, tables, supplementary), up to 5 tables/figures, ~30 references. Required sections: Key Features (≤200 words bullets), Data resource basics, Data collected, Data resource use, Strengths and weaknesses, Data resource access, Ethics approval, Acknowledgements, Author contributions, Supplementary data, Conflict of interest, Funding, Use of artificial intelligence (AI) tools.
- HMD model paper: Barbieri et al. 2015, IJE 44(5):1549–1556. https://doi.org/10.1093/ije/dyv105 (PMC: PMC4707194). The current draft is modeled on this.

**Approach.**
1. Word-count the current draft per section. Strengths and Weaknesses is the longest at ~1,000 words; trim to ~600.
2. Compress the validation breakdown in Strengths bullet (ii) by moving the 19-detail-cell breakdown to a supplementary table or omitting and citing the validation CSV.
3. Trim the V2-era reporting-quirk paragraph (Oklahoma/Maryland/Massachusetts/Louisiana) — it can become a footnote or supplementary note.
4. Add a one-paragraph *Companion paper* sentence pointing to this monorepo and the joint-use notebook (see Task 2).
5. Fill in Ethics approval, Author contributions, AI-tool disclosure, Conflict of interest, Funding sections.
6. Verify references are formatted to journal style.
7. Final word count check.

**Output artifacts.**
- Revised `paper/draft_v2_hmd_styled.md`.
- Possibly a `paper/supplementary.md` for trimmed-out detail (V2 reporting quirks, full validation breakdown).

**Validation.**
- Main text ≤ 2,500 words excluding the listed exclusions.
- All required sections present.
- All admin sections filled.

**Estimated effort.** One session.

**Dependencies.** Task 6 (linked-file validation framing) should resolve before final word-count freeze.

---

### Task 6 — Verify and reconcile linked-file validation framing

**Goal.** Resolve a discrepancy between the natality README and the manuscript drafts in how the linked birth–infant death validation is described.

**Why this matters.** One framing is stale. The manuscript cannot ship with an inconsistency.

**Inputs.**
- Natality repo README (mirrored at `natality/README.md`) says "35/35 V3 linked targets pass."
- The manuscript drafts (both `paper/draft_v1_*.md` and `paper/draft_v2_*.md`) say "33 of 35 byte-exact, two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights."
- Authoritative source: `natality/output/validation/external_validation_v3_linked_comparison.md` and `external_validation_v3_linked_comparison.csv`.

**Approach.**
1. Read `natality/output/validation/external_validation_v3_linked_comparison.md` (and the corresponding CSV).
2. Determine the actual current state: 35/35 exact, or 33/35 + 2 documented diffs?
3. If 35/35: update the manuscript drafts to match. The old "33/35 + 2 docs" framing was likely the V3 baseline before some upstream NCHS data fix.
4. If 33/35 + 2: update the natality README to match the manuscript framing, and flag this as a known thing to mention in *Strengths and weaknesses*.
5. Either way, add a note to `paper/README.md` recording which framing is now canonical.

**Output artifacts.**
- Possibly updated `natality/README.md`, `paper/draft_v2_hmd_styled.md`, `README.md` (top-level table).

**Validation.**
- The natality README, the top-level monorepo README, the manuscript draft, and the validation CSV all agree.

**Estimated effort.** 15–30 minutes.

**Dependencies.** None. Should be done early to unblock Task 5.

---

### Task 7 — Fetal-death V3 (extend backward to 1982)

**Goal.** Bring fetal-death coverage to 1982–2022 (41 years) by parsing the 1978-revision (1982–1988) and early 1989-revision (1989–1991) layouts.

**Why this matters.** Closes the historical gap. Several major prior-art studies use 1980-onward data; once V3 ships, those analyses can be replicated and extended on harmonized microdata.

**Inputs.**
- 1982–1991 fetal-death zips from NCHS FTP.
- NCHS user guides for those years (some may only be available as scanned PDFs; OCR may be needed).
- 1978-revision Standard Report of Fetal Death documentation (older, may need to source from NCHS archive).

**Approach.**
1. Audit which years 1982–1988 use the 1978-revision layout vs early 1989-revision (some years may be hybrid).
2. Reconstruct each era's record layout. Save `fetal_death/record_layout_1982.csv` (or per-year if layouts shift within era).
3. Extend `field_specs.py` for the older eras.
4. Define the harmonization rules for fields that exist in 1978-revision but not 1989-revision, and vice versa. Some fields will need new comparability classifications.
5. Validate per-year counts against any available NCHS published source. Note: *NVSR Fetal & Perinatal Mortality* series begins at 1995; 1982–1994 control counts come from the original NCHS user guides.
6. Re-run all validation.
7. Bump fetal-death version to v3.0.0.

**Output artifacts.**
- New `fetal_death/record_layout_*.csv` for 1982–1991.
- Updated parsers, field specs, harmonization rules.
- Expanded validation targets.
- Updated parquets (regenerated; .gitignored).
- Updated docs across the board.

**Validation.**
- Per-year counts match user-guide control counts exactly for years where guides ship clean control counts.
- 1992–2022 slice byte-clean regression.

**Estimated effort.** Two to four sessions. The 1978-revision is older and the documentation may be harder to source.

**Dependencies.** Task 3 (V2.1) should ship first — both for cleaner versioning and because the V2.1 layout work serves as a precedent for the V3 work.

---

### Task 8 — Cross-product timeline figure

**Goal.** A single figure showing all three products' coverage on one timeline, with era boundaries (1989-revision uniform, 2003-revision rollout, post-rollout) marked.

**Why this matters.** A reviewer-friendly visual showing the full scope of the resource. Slot it as Figure 1 in the manuscript.

**Inputs.**
- Existing per-product timelines: `natality/figures/fig2_timeline.{pdf,png}`.
- Era boundary metadata in each subproject's COMPARABILITY.md.

**Approach.**
1. Sketch a horizontal timeline 1980–2025.
2. Three rows: natality (1990–2024), linked (2005–2023), fetal death (1992–2022, with the 2003–2004 gap visible).
3. Vertical bands marking the 1989-revision-only era, the 2003-revision rollout window, and the post-rollout era.
4. Annotate within-revision NCHS reformats (2006 natality compression, 2014 natality reformat, 2014 linked reformat, 2018 fetal-death revised-only).
5. Save as `figures/fig1_coverage_timeline.{pdf,png}`.

**Output artifacts.**
- `figures/fig1_coverage_timeline.pdf` and `.png`.
- A small Python script `shared/helpers/build_timeline_figure.py` (so the figure is regeneratable).

**Validation.**
- Era boundaries match COMPARABILITY documentation in both subprojects.

**Estimated effort.** Half a session.

**Dependencies.** None.

---

### Task 9 — Update old GitHub repos with redirect notices

**Goal.** Update the `natality-harmonization` and `fetal-death-harmonization` repo READMEs on GitHub to add a notice at the top: "Future development of this project happens in [yoelplutchok/vital-statistics-harmonization](https://github.com/yoelplutchok/vital-statistics-harmonization)."

**Why this matters.** Discoverability. A reader who finds the old repo through Zenodo or Google should be pointed at the unified repo.

**Inputs.**
- Existing READMEs in both old repos.

**Approach.**
1. Add a notice block at the very top of each README (above the title), e.g.:
   > **Note.** This project has been unified with the [U.S. Fetal Death Harmonization Project](https://github.com/yoelplutchok/fetal-death-harmonization) into a single monorepo at [yoelplutchok/vital-statistics-harmonization](https://github.com/yoelplutchok/vital-statistics-harmonization). Future development happens there. This repo remains as the published Zenodo deposit's source-code mirror.
2. Commit and push to each old repo.
3. Optionally, archive the old repos on GitHub (Settings → General → Archive). **Do not archive until the new monorepo has been pushed and the user has reviewed.**

**Output artifacts.**
- Updated `README.md` in each old repo.

**Validation.**
- Both old repos render the notice at the top.

**Estimated effort.** 15–30 minutes.

**Dependencies.** This monorepo must be pushed to GitHub first.

---

### Task 10 — Set up unified Zenodo deposit

**Goal.** Publish a new unified Zenodo deposit covering all three products under the U.S. Harmonized Vital Statistics umbrella.

**Why this matters.** The manuscript's central claim is the resource is unified. A unified Zenodo deposit makes that claim concrete.

**Inputs.**
- This monorepo.
- Existing two deposit metadata: `natality/.zenodo.json` and `fetal_death/.zenodo.json`.

**Approach.**
1. Confirm with the user that this is the right time to publish (typically aligned with manuscript submission).
2. Create a top-level `.zenodo.json` describing the unified resource. Include both subproject DOIs as `isPartOf` related identifiers.
3. Generate a tarball or zip of all three products' parquets + this monorepo's source code.
4. Upload to Zenodo. Reserve the DOI in advance and inject it into the manuscript before final submission.
5. Update top-level `CITATION.cff` and `README.md` with the new DOI.
6. Continue maintaining the two existing deposits as legacy DOIs that still resolve. Mark them as superseded in their Zenodo descriptions.

**Output artifacts.**
- New top-level `.zenodo.json`.
- New Zenodo deposit (external).
- Updated `README.md`, `CITATION.cff`, manuscript with new DOI.

**Validation.**
- Zenodo DOI resolves to the deposit page.
- Concept DOI resolves to the latest version.
- Old deposits still resolve and have a notice pointing to the new one.

**Estimated effort.** One session, plus user time for the Zenodo upload and form-filling.

**Dependencies.** Tasks 1–6 should be done first so the deposit reflects the final manuscript-aligned state of the three products. Task 9 (old-repo redirects) should also be done.

---

## 3. Cross-cutting concerns

### What NOT to change without consulting the user

- Era boundaries, harmonization rules, value-level normalizations (B1–B6 for fetal death, the analogous within-revision normalizations for natality and linked). These are the substance of the harmonization. Changing them changes the data.
- The canonical analytic filters (`tabulation_flag == '2' AND residence_status != '4'` for fetal death; `restatus != '4'` for natality and linked). These are what reproduce the NVSR aggregates exactly.
- Existing column names in the harmonized schema. Renames break user code.
- Existing Zenodo DOIs. They are persistent identifiers and must continue to resolve.

### Conventions to preserve

- **Subproject independence.** Each subproject (`natality/`, `fetal_death/`) is a self-contained pipeline. Cross-product code lives in `shared/helpers/` or `notebooks/`, not inside either subproject.
- **One stable schema per product.** The harmonized schema columns do not change across versions. Within a column, values may be added (e.g., new years' codes) but existing codes are not redefined.
- **Per-year raw parquets are sacred.** They preserve every documented source field in its original form and are the audit trail. Do not modify them after release.
- **Validation against published NVSR figures is the gold standard.** Any change to the harmonization that breaks a previously-passing NVSR cell is a regression and must be justified.
- **Bit-reproducibility.** The harmonized parquet should be byte-identical when the pipeline is re-run from a fresh download of the NCHS source files. SHA-256 checksums in `PROVENANCE.md` files are the test.

### Known data caveats (to remember when answering questions)

- **Cause-of-death codes for fetal deaths before 2014.** Not in the public-use file. RDC-only (restricted-use application required). Do not promise to deliver these from public data; it is impossible.
- **State-level identifiers in V1-era fetal-death public-use files (2005+).** Suppressed by NCHS at source. The per-year raw parquets carry state codes for 1992–2002 only.
- **Maternal education across the 1989/2003 boundary.** No bridge is provided. The two fields (`maternal_education_unrevised`, years 00–17; `maternal_education`, 9-category degree levels) are deliberately preserved separately. Building a bridge is a deliberate non-goal.
- **State reporting quirks 1992–2002.** Oklahoma did not report Hispanic origin during this period; Maryland (1992–1998), Massachusetts (1992–1997), Louisiana plurality 1992–1994. These are documented in `fetal_death/COMPARABILITY.md` and reproduce *NVSR 57-08* footnotes.

### Stale items in current docs that need fixing as you work

- The `fetal_death/README.md` Version Roadmap table lists "V4: Natality companion product" as a future item. Natality is already shipped (in the natality subproject and at Zenodo DOI 10.5281/zenodo.19868835). When you next touch this file, reword the V4 row to "Joint-use convenience layer + cross-product validation notebook" or similar (per `VERSION_ROADMAP.md` at the monorepo root).
- The fetal-death `LICENSE` says "U.S. Harmonized Vital Statistics Microdata" at the top (was updated during the migration). The fetal_death/LICENSE in the subproject directory still says "U.S. Fetal Death Harmonization Project" — that's correct because that LICENSE is subproject-scoped. Don't change it.

---

## 4. Definition of "ready to submit"

The manuscript is ready to submit when:

1. ✅ Three products published to Zenodo with persistent DOIs.
2. ✅ Pipelines deterministic and re-runnable end-to-end from public NCHS source files.
3. ⏳ Joint-use convenience layer shipped (Task 1).
4. ⏳ Joint-use demo notebook shipped (Task 2).
5. ⏳ Linked-file validation framing reconciled (Task 6).
6. ⏳ Manuscript at IJE word limit with admin sections filled (Task 5).
7. ⏳ Paper-companion notebook reproducing every numeric claim (Task 4).
8. ⏳ V2.1 fetal-death (2003–2004) ideally shipped (Task 3) so the manuscript can claim continuous 1992–2022 coverage. If not, the manuscript footnotes the deferral as it currently does.
9. ⏳ Cross-product Figure 1 (Task 8).
10. ⏳ Old GitHub repos pointed at the monorepo (Task 9).
11. ⏳ Unified Zenodo deposit reserved (Task 10).

Tasks 7 (V3 1982 extension) is post-submission. Do not block submission on V3.

---

## 5. How to use this document

### As an LLM agent

1. Read sections 0–1 to load context.
2. Pick a task from section 2 in the priority order shown, or follow the user's explicit instruction.
3. Before starting any task, verify the listed inputs are accessible (parquets present, NCHS files reachable). If not, surface that to the user rather than guessing.
4. Follow the task's Approach steps. When you finish, run the listed Validation checks.
5. Commit with a clear message linking back to the task name (e.g., "Task 1: ship stratified denominator file").
6. Update this document if the work uncovers a new sub-task, a stale item, or a fact that other future agents should know.

### As a human collaborator

1. Skim sections 0–2 to see what's planned.
2. Pick what to work on next or hand a task to an agent with the relevant section as context.
3. Update sections 2 and 4 as tasks complete.
4. When the manuscript is submitted, archive this document or move it to `docs/post-submission-followups.md` for V3 and later work.
