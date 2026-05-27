# Session kickoff prompt

Copy and paste the block below as your **first message** to the LLM at the start of any session in this repo. This is the canonical handshake — it loads the operating discipline before any work starts.

For **build sessions**, paste it as-is.

For **audit sessions** (when you want a fresh-eyes review of a completed task), paste it and add a second message saying: *"This is an audit session. Refuse to read prior `RECEIPTS/`, `FIX_LOG.md`, `LESSONS.md`, and `DECISION_LOG.md`. Use the adversarial framing in `NEXT_STEPS.md` §8 (the mistake-class matrix) and look for L3, L7, L11, L17 specifically. Write findings to `AUDITS/<AUDIT_ID>_<UTC_timestamp>.md` (create the directory if it does not yet exist)."*

---

## Conventions in effect (2026-05-11 protocol-sync from upstream NHANES)

These conventions are binding for every session going forward. They were ported from the NHANES Assay-Bridging operating protocol via the `NEXT_STEPS.md` §11 plan-update process at the timestamp above. Each one prevented a real cascade in the upstream project; carrying them over before HVS hits a similar issue is the cheap option. The next session reads them on first paste of this kickoff prompt and applies them in PRE-FLIGHT / SMOKE / DO / VERIFY / RECEIPT.

### Convention 1 — SHAPE-not-VALUE for new SMOKE harnesses

Every new SMOKE harness asserts **structural invariants that survive authorized canonical-state mutation**, not mutable annotation values pinned at the harness's authoring moment. DO assert: column count, row count, dtype, presence-of-key, monotonic invariants, schema enums, row-count conservation across joins. DO NOT pin: row counts that will grow under V2.1 / V3, sha256s that will change when a script is correctly edited, docs strings that will be reworded. See `NEXT_STEPS.md` §4.2.1 + §8 row L17.

### Convention 2 — FROZEN-AT-TASK vs tracks-current-state SMOKE docstring tag

Every new SMOKE harness declares its design intent on the **first docstring line**: `DESIGN: tracks-current-state` (asserts post-DO canonical state for the task that authored it; updated under authorized canonical drift) OR `DESIGN: frozen-at-<task_id>` (asserts historical schema state by design; remains FAIL under later renames — this IS the test). See `NEXT_STEPS.md` §4.2.1.

### Convention 3 — PRE-FLIGHT includes a Field-value snapshot subsection

For every canonical artifact (CSV row, parquet column, doc number) this task will mutate, snapshot the **current values of the fields being touched** and verify against the task plan's assumed state. Catches surprises at the cheap-check moment instead of mid-DO. Cost: ~1 minute per task. See `NEXT_STEPS.md` §5 template.

### Convention 4 — RECEIPT includes a Forward-looking HALTs subsection

Every receipt declares, in a `Forward-looking HALTs for next session` subsection, the assertions the next session's PRE-FLIGHT must verify (e.g., "if the linked-file validation CSV sha256 doesn't change in the expected direction after Task 6, halt — the reconciliation edit did not take"). Saves the next session from re-deriving "what would trigger a halt." See `NEXT_STEPS.md` §6 template.

### Convention 5 — Commit-message brevity

Commits ship a ~5-line summary; the full narrative lives in the receipt (`RECEIPTS/<task_id>_<UTC_timestamp>.md`). `[plan-update]` commits (protocol or schema changes) use the same shape with `[plan-update]` as the leading bracket-tag. See `NEXT_STEPS.md` §4.5.

### What to do if a convention conflicts with a task's plan

Raise it as a §7 halt condition (BEFORE the first DO mutation) and ask the human. Do NOT silently deviate from a convention; do NOT silently follow a deprecated convention against the new state.

---

## Current planned sequence (as of 2026-05-26, §15.G OPEN — pre-submission enhancements)

**Latest plan-update (2026-05-26).** **§15.F CLOSED**. **§15.G OPEN** — default queue closes gaps in `paper/draft_v2_hmd_styled.md` §Future developments + finishes D.4 submission prep. Full task specs: **`NEXT_STEPS.md` §15.G**.

| Order | Task ID | What it is | Status |
|---|---|---|---|
| **1** | **MM-T2** | Matched multiples 2016–2020 **Table 2** validation (PDF + targets) | ✅ |
| **2** | **LINK-ICD10** | Linked cohort 1983–1998 ICD-9→ICD-10 **derived** (CMS GEM) | ✅ |
| **3** | **LY-linked-2024** | Linked **2024 period / 2023 cohort** ingest (CDC lists file) | ✅ |
| **4** | **D.2-docs** | Zenodo **docs-only v1.0.2** validation-table sync | ✅ |
| **5** | **D.4-paper** | Paper 1 finish: companion notebook, FLAGS, commit draft | ⏳ |
| — | **LY-natality-2025** | Natality 2025 when CDC posts zip | ⏳ trigger |
| — | **RD.1b / §15.F** | Robustness roadmap | ✅ 249/249 (2026-05-25) |

**Paper voice.** Manuscript describes the resource **as it exists now** (present tense). Do not write “earlier roadmaps,” “planned,” or “have now shipped” in `paper/` — update §Future developments after §15.G tasks land.

**Explicitly OUT OF SCOPE (unless user re-authorizes):**

- **RDC / Census restricted-use linkage** (paper lists under Future developments but not executable on public-use data)
- **D.1** — old-repo redirects
- **D.2 legacy patches** — old Zenodo DOI description-only updates

**After §15.G + D.4-paper → human IJE submission → Phase E** (companion paper via `NEXT_STEPS.md` §19.2).

**Build-host note:** Gate parquets are **not** in a typical git clone (gitignored). Paths: `~/Desktop/fetal-death-harmonization-build/output/harmonized/` and `~/Desktop/natality-harmonization/output/harmonized/`. See per-product `PROVENANCE.md`.

**Gate SHA re-hash:** Run **once immediately before** you zip files for Zenodo upload (~1 min). A prior PASS (D-prep.6 or 2026-05-21) proves the build was correct **at that time**; the pre-upload re-hash proves **these are the bytes you publish** (Zenodo is immutable per §9-#15). If you never re-ran pipelines between checks, the hash will match and the step is trivial.

**Historical context (the 2026-05-12 directive that drove Phases B + C):**

Phase A (data-first pre-submission scope) is **COMPLETE**. The user (chat 2026-05-12, post-commit `b0c8b4a` `task7_v3b-complete`) has issued a **§11 plan-update directive** expanding pre-submission scope further: *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo."* Manuscript submission, Zenodo deposits, and the public-repo v1.1 sync are all paused until Phases B + C complete.

### Phase A — data-first pre-submission scope (COMPLETE)

- ✅ Task 1 (joint-use stratified denominators, 2026-05-11)
- ✅ Task 2 (joint-use demo notebook, 2026-05-11)
- ✅ Task 3 V2.1 (fetal-death 2003-2004 + H8 + data_year + monorepo path-drift bundle, 2026-05-12 `task3-complete` @ `8ca5bf9`)
- ✅ Task 4 (paper companion notebook, 2026-05-11)
- ✅ Task 5 (manuscript trim, 2026-05-11)
- ✅ Task 6 (linked-validation framing reconcile, 2026-05-11)
- ✅ Natality v2.8.0 column rename (2026-05-12)
- ✅ Task 7 V3a (fetal-death 1989-1991 backward extension, 2026-05-12 `task7_v3a-complete`)
- ✅ Task 7 V3b (fetal-death 1982-1988 backward extension, 2026-05-12 `task7_v3b-complete` @ `b0c8b4a`)
- ✅ Public v1.0 GitHub repo push 2026-05-12 (commit `a18ca3a` at https://github.com/yoelplutchok/vital-statistics-harmonization; will be superseded by v1.x at Phase D)

Current data envelope: 41-yr fetal death (1982-2022, 2.35M records, 88/88 NVSR validation byte-exact) + 35-yr natality (1990-2024, 138.8M records, 183/183 byte-exact) + 19-yr linked birth-infant death (2005-2023, 74.9M records, 33/35 + 2 docs).

### Phase B — EXPLORATION SESSION (NEXT SESSION'S WORK; READ-ONLY)

**MANDATORY: the next LLM session is a READ-ONLY investigative / exploration session.** Per the 2026-05-12 user directive (logged in DECISION_LOG at commit time of this `[plan-update]`), Phase B EXPANDS pre-submission scope by investigating what additional work would make the project maximally robust and useful BEFORE Phase D (paper + Zenodo + public repo). The exploration session is mandated to:

1. **Brainstorm + research the full frontier of pre-submission additions** across the six dimensions below. Open-ended exploration; do not narrow prematurely. The user wants "everything possible" — the session's job is to enumerate everything plausible, score it, and propose an executable order.

2. **Six exploration dimensions** (each becomes a section in the exploration report):

   **B.a. Data extensions (additional years / additional NCHS files)**
   - **Natality 1968-1989 backward extension** — symmetric sibling of the V3b fetal-death work just shipped. NCHS public-use natality files exist 1968+; 1968-revision (1968-1971 50% sample + 1972-1977 100%) and 1978-revision (1978-1988 100%) covered. Probe URLs at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/` and `Dataset_Documentation/DVS/natality/`. Verify per-year layout availability + user-guide existence via sibling-derived URL probing (per LESSONS L1-extension 2026-05-12T04:30:00Z).
   - **Linked birth-infant death pre-2005 backward extension** — NCHS cohort-linked files exist back to 1983; period-linked starts 1995 (with the well-known 1995-1998 gap that ended NCHS's prior series). Verify which years are public-use and which layouts apply. Probe `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/linked/`.
   - **Latest-year refreshes**: 2023+ fetal death, 2025+ natality, 2024+ linked. Verify NCHS public-use release status via WebFetch on `https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm`.
   - **Pre-1982 fetal death** — almost certainly RDC-only (NCHS public-use FD canonical series begins 1982); confirm by WebFetch + sibling-URL probing.
   - **Other NCHS public-use vital-events files** worth considering: marriage/divorce series, multiple-cause-of-death (all-age mortality — out of HVS scope unless user redirects), abortion surveillance summaries.
   - **IPUMS-International + IPUMS-USA**: are there pre-harmonized versions worth cross-referencing for validation?
   - For each candidate: NCHS URL probe result; raw-zip estimated size + record count; user-guide availability; era-layout count; estimated harmonization effort.

   **B.b. Robustness / testing / validation infrastructure**
   - `tests/test_schema_dtype_parity.py` (durable H8 defense; recommended in FIX_LOG 2026-05-11T18:50:00Z) — asserts every harmonized_schema.csv `type` matches the parquet's pyarrow dtype.
   - `tests/test_canonical_filter_invariants.py` — sum-across-strata = unstratified-total for every canonical filter, every product, every year.
   - `tests/test_row_count_conservation.py` — input = output + documented_drops at every parse/harmonize/derive boundary.
   - `tests/test_cross_product_join_parity.py` — natality joined to fetal-death + linked has the expected demographic-stratum row counts (per JOINT_USE_GUIDE).
   - **Mutation-test scaffolding** for every validator (L3 defense in §8): inject a known violation; assert the validator catches it.
   - **L13 file-inventory completeness audit** — for every CSV in `metadata/`, verify role/description names columns that actually exist with claimed dtypes.
   - **L14 exit-code-vs-per-row aggregation defense** — every validator's `main()` must exit non-zero on any per-row FAIL.
   - **CI integration** — GitHub Actions workflow running smoke + invariant tests on every push (currently no automated test runs).
   - **`scripts/run_pipeline.py` end-to-end smoke from monorepo root** — confirms no latent path-drift bugs (per FIX_LOG 2026-05-12T01:30Z forward-looking follow-up).
   - **PROVENANCE.md refresh + sha-stability test** — automated check that every shipped artifact's documented SHA matches its on-disk SHA.
   - **Snapshot regression test** — every release tags a per-column SHA manifest; subsequent release CI fails if any "stable" column drifts.

   **B.c. Usability / convenience layers / multi-language quickstarts**
   - **Additional pre-computed denominator tables**: state-stratified live births × year; race × age × Hispanic × state; period vs cohort linked-file denominators.
   - **R quickstart**: `quickstart.R` mirroring `quickstart.py`; verifies `arrow::read_parquet()` round-trip; documents R package dependencies.
   - **Stata + SAS quickstarts**: `quickstart.do` + `quickstart.sas`; document `import delimited` or `use` syntax for Stata; PROC IMPORT for SAS. Even a pointer file telling these users "load via pyarrow then export to CSV" would be a usability win.
   - **DuckDB views / pre-built SQL queries**: a `views.sql` file with the canonical filter + common joins as DuckDB-compatible views over the parquets.
   - **Pre-computed cross-tab CSVs** for users who don't want to load the parquet: per-year × per-state × per-race counts for the top 10 most-cited NVSR-equivalent tabulations.
   - **Worked-example notebooks beyond the current 2**:
     - `maternal_age_stratified_imr.ipynb` (using linked file)
     - `preterm_outcomes_time_series.ipynb` (fetal+natality+linked)
     - `cross_race_fetal_mortality.ipynb` (V3a/V3b race-stratified analysis demo, with V3b's code-7+9 null caveat documented)
     - `education_gradient.ipynb` (within-era only, with the 1989/2003 boundary explicit)
     - `state_reporting_quirks.ipynb` (Oklahoma Hispanic, Maryland/Massachusetts 1992-1998, Louisiana plurality)
   - **CLI tool**: `hvs` command-line tool wrapping `quickstart.py` use cases (e.g., `hvs count fetal_deaths --year 2020 --race AIAN`).
   - **Validated "perinatal record" pre-joined parquet**: one row per linked-file infant with fetal-death sibling records flagged (where infant + sibling fetal death share maternal identifiers — limited by suppressed identifiers, but partial joins are possible).

   **B.d. Cross-product / joint-use enhancements**
   - **Three-product perinatal mortality joint computation**: rate = (fetal deaths 28+wk + infant deaths <7d) / (live births + fetal deaths 28+wk) × 1000, computed by year × race using all three products. Currently only fetal mortality (single product) is demoed.
   - **Section B 2017 race-stratified NVSR validation** (the deferred Task 4 fragment).
   - **Task 8 — cross-product timeline figure** (from NEXT_STEPS.md §15; not yet shipped). Era-boundary visualization, all 3 products on one timeline with revision-boundary bands.
   - **Cross-product reproducibility figure** — fetal-mortality rate + IMR + preterm rate + LBW rate on one panel, with documented sources for each.

   **B.e. Documentation / discoverability**
   - **CHANGELOG.md** at the monorepo root with one section per version (v1.0 → v1.1 → … delta).
   - **Migration guides**:
     - v2.7.0 → v2.8.0 natality (column renames; sample sed/awk recipes for legacy code).
     - v2.0.0 → v2.3.0 fetal death (V2.1 transition years added, V3a/V3b backward extension; sample query updates).
   - **Worked-example FAQ** ("how do I compute the perinatal mortality rate?" "how do I get state-level data?" "what's the right canonical filter for my analysis?").
   - **Cross-product COMPARABILITY.md** at monorepo root — synthesizes the within_era/cross_era caveats from both subprojects' COMPARABILITY docs.
   - **PROJECT_STRUCTURE.md upgrade** — add notebook deps + build-order DAG + which-file-to-read-first-by-use-case.
   - **CODEBOOK extensions** — per-variable historical-value-distribution panels, sentinel-code disambiguation tables, era-by-era coding scheme diff.
   - **PRIOR_ART.md update** — does the literature gap argument still hold given recent harmonization efforts (e.g., NBER's IPUMS-Health Surveys, RWJF's 500 Cities)?
   - **NCHS-source-data SHA manifest at sub-project level** — confirms a downstream user replicating from scratch gets bit-identical inputs.

   **B.f. Performance / distribution / reproducibility tooling**
   - **Parquet column dictionary tuning** — set `use_dictionary=True` per low-cardinality column (e.g., race, sex, version_flag); measure size reduction.
   - **Smaller derived parquet** — drop redundant intermediates if any (e.g., string sibling of a numeric column).
   - **Reproducibility container** — `Dockerfile` pinning python+pandas+pyarrow versions; one `docker run` rebuilds every parquet end-to-end.
   - **`uv` / `poetry` lockfile** for deterministic Python environment.
   - **GitHub release artifacts** — attach the parquets to a GitHub Release alongside the Zenodo deposit.
   - **`scripts/run_pipeline.py` from-scratch smoke** — verify clean rebuild from raw zips in <30 min on a standard laptop.
   - **Mirror parquet on a CDN** (CloudFront / S3 / GitHub LFS) for users behind Zenodo-blocking firewalls.

3. **For each candidate, produce a structured writeup** with:
   - **Name** + 1-line description
   - **Why this matters** (use case, who benefits)
   - **Effort estimate** (sessions, with per-session breakdown)
   - **Source / data dependencies** (NCHS user-guide URLs verified via WebFetch + sibling probing; SHA recordable; OCR-needed flag)
   - **Risks / blockers** (RDC-only? requires direct NCHS contact? schema-version-bump-triggering? cross-era incompatible?)
   - **Manuscript impact** (changes a published number? adds a new validation cell? requires re-paragraph?)
   - **Priority recommendation**: must-have / nice-to-have / defer
   - **Execution dependency** (does X need to happen before Y?)

4. **Produce a §11 plan-update proposal** at the end of the session:
   - Diff for `NEXT_STEPS.md` §15 (new task entries with full PRE-FLIGHT/SMOKE/DO/VERIFY/RECEIPT framing per §4)
   - Diff for `KICKOFF.md` (replace this Phase B/C/D placeholder with a concrete ordered task list)
   - **Total effort estimate** (cumulative sessions; surface the trade-off explicitly so the user can decide whether to trim before authorizing)
   - **Suggested execution order** within Phase C (group tasks by data-product-touched; minimize parquet rebuilds; place high-risk early)

5. **HALT and write findings to**:
   - `EXPLORATION_REPORT.md` at monorepo root (NEW file, append-only thereafter)
   - New STATUS.md section appending the proposal pointer + "Open questions for human"
   - DECISION_LOG entry recording the plan-update proposal (status: PENDING USER REVIEW)
   - Do **NOT** execute any of the investigated items. Do **NOT** advance to Phase C without explicit user authorization.

**Investigation methods allowed in Phase B**:
- `WebFetch` on NCHS canonical URLs (`https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm` + sibling-derived `ftp.cdc.gov` paths).
- `WebSearch` for academic / IPUMS / NBER / ICPSR / GitHub references.
- `WebFetch` on `https://web.archive.org/web/*/` for older NCHS pages.
- `Read` on existing repo files (any path).
- `Bash` for read-only repo inspection: `git log`, `git diff`, `grep`, `find`, `ls`, `wc`. **Forbidden**: any tool invocation that mutates state (no `git commit`, no `mv`, no `cp` of canonical files, no script execution that writes to canonical paths).

**Forbidden in Phase B**:
- Any canonical-state mutation (scripts, parquets, schema, metadata CSVs, RECEIPTS/, manuscript drafts).
- Any DO-phase work on any candidate.
- Skipping the halt-and-ask step at session end.
- Hallucinating data sources without sibling-derivation evidence (per LESSONS L1-extension).
- Asserting "PDF X needs OCR" without an explicit `page.get_text()` probe (per LESSONS L12-extension 2026-05-12T15:00Z).
- Inflating effort estimates to discourage user expansion, or deflating them to encourage it. Report honestly.

**Time budget**: 1 session (estimated 60-120 min of agent time). If the exploration is incomplete at session end, deliver a partial proposal + flag the unfinished dimensions; do NOT defer the halt.

### Phase C — EXECUTE PHASE B-AUTHORIZED ADDITIONS (Tier 1 + Tier 2, ~29-35 sessions)

Per Phase B `EXPLORATION_REPORT.md` §G.4 (drafted 2026-05-12T20:30Z) and user authorization 2026-05-12 (Q35 = Tier 1 + Tier 2; logged in `DECISION_LOG.md` 2026-05-12T21:00:00Z; Q32-Q42 self-resolutions in same entry). Each task below uses the full `NEXT_STEPS.md` §4 five-phase discipline (PRE-FLIGHT, SMOKE, DO, VERIFY, RECEIPT) per the `§15` entries C8.1-C8.15 appended at the same `[plan-update]` commit.

#### Tier 1 — pre-Phase-D must-haves (~13-15 sessions)

- **C8.1** — SMOKE retag + dtype parity (B.1 + B.2)               [1.5 sessions]
- **C8.2** — Latest-year refresh: fetal 2023+2024 (fetal-only)    [1 session]
- **C8.3** — Cross-product Tier-1: timeline + perinatal joint + 2022 race [2 sessions]
- **C8.4** — Invariant tests: filter + row-count + join           [3 sessions]
- **C8.5a** — Distribution: pyproject.toml + uv.lock              [0.5-1 session]
- **C8.5b** — Distribution: Dockerfile (DEFERRED; needs docker)   [1-2 sessions]
- **C8.6** — CI: GitHub Actions wiring                            [1 session]
- **C8.7a** — Path-drift static audit across per-step scripts    [1 session]
- **C8.7b** — Orchestrator + Tier-1/2 re-derive (DEFERRED)        [1.5-5 sessions]
- **C8.8** — CHANGELOG + PRIOR_ART update                         [1 session]

#### Tier 2 — high-value additions (~16-20 sessions)

- **C8.9** — Usability: R quickstart + DuckDB views (C.1 DROPPED)  [1-1.5 sessions]
- **C8.10** — Worked-example notebooks (3 of 5)                   [3-4 sessions]
- **C8.11** — Migration guides + cross-product COMPARABILITY      [3-4 sessions]
- **C8.12** — Mutation tests + L13/L14 audits + SHA stability     [3-4 sessions]
- **C8.13** — Pipeline timing benchmark (F.5 only; F.1+F.4 plan-updated 2026-05-13T22:30Z) [~1 session]
- **C8.14** — Worked-example FAQ + PROJECT_STRUCTURE upgrade      [1 session]
- **C8.15** — Notebooks 4-5 (education, state quirks)             [2 sessions]

#### Tier 3 + Tier 5 — ACTIVE (authorized 2026-05-14 per `[plan-update] scope_expansion_tier3_tier5`; ~21-34.5 sessions)

Authorized 2026-05-14 in response to user directive *"i want to do everything possible before uploading to zenodo"* restating the 2026-05-12 mandate with explicit data-extension emphasis. Q35 = Tier 1+2 authorization (2026-05-12T21:00:00Z) is superseded for Tier 3+5 work; Q41 + Q40 + Q36 defaults overridden. Sequence: matched-multiples first as cheap independent early win; then big data extensions in user-chosen order (natality 1968-1989 then linked 1983-2004); then perinatal-record; then docs/usability ancillaries. Manuscript Coverage paragraph re-paragraphed ONCE at D.4 after all data lands.

- **C8.16** — A.5 Matched-multiples ancillary release (4th HVS product)  [1-2 sessions]
- **C8.17** — A.2 Natality 1968-1989 backward extension (22 new years; 4 layouts) [6-10 sessions]
- **C8.18** — A.3 Linked 1983-2004 backward extension (19 new years; 1992-94 gap) [8-14 sessions]
- **C8.19** — C.8 Perinatal-record feasibility + methodology note (record-level public-use join proven infeasible at Tier-0; re-scoped 2026-05-23 per §11 — see §15.D block) [~1 session]
- **C8.20** — E.7 CODEBOOK extensions (per-variable historical distributions)  [2-4 sessions]
- **C8.21** — C.3 Stata/SAS quickstart pointer files                          [0.5 sessions]
- **C8.22** — C.5 Pre-computed cross-tab CSVs (`csv/published_tabulations/`) [1 session]

**Cumulative Phase C estimate revised**: Tier 1+2 done at ~17.5 sessions; Tier 3+5 adds ~21-34.5 sessions; total ~51-71 sessions (was 29-35). **Effort-ceiling cap (Q33) raised 42 → 86 sessions** (+20% of 71 high estimate). Re-ask triggers if cumulative drift exceeds 86.

**Tier 3 candidates not in scope**: C.7 CLI tool (replaced by C.4 DuckDB views shipped at C8.9; re-authorization needed if reconsidered).

#### Sequencing notes within Phase C

- **C8.1 first** (Q37): cheapest item, pure-metadata, fixes the known stale L17 smoke case (forward-looking HALT #10 in STATUS 20:30Z). Unblocks any subsequent task that touches fetal-death state.
- **C8.2 second** (Q37): latest-year refresh extends the data envelope before downstream test/CI scaffolding so subsequent CI runs gate on the full extended envelope (no rework when 2023-2024 land).
- **C8.5a + C8.6 paired**: CI (B.9) depends on a pinned env (F.3 lockfile = C8.5a); ship lockfile first. C8.5b Dockerfile deferred to after `docker` is available on build machine OR after C8.7b lands the monorepo-root pipeline orchestrator (whichever comes first). Note: C8.7a (path-drift audit, this session's narrowed C8.7 scope) does NOT land the orchestrator; that work is in C8.7b (DEFERRED).
- **C8.4 before C8.6**: CI gates on real invariant tests, not bare structural smokes.
- **C8.8 last in Tier 1**: PRIOR_ART updates + CHANGELOG land after Tier 1 work supplies the evidence to cite.
- **C8.9-C8.11 ordering within Tier 2**: usability (C8.9, C8.10) ships before docs (C8.11) so migration guides can reference live R/DuckDB examples.
- **C8.12 mutation tests last in Tier 2**: defends every prior validator; surfaces FIX_LOG cascades if any validator rubber-stamps.
- **C8.16 first in Tier 3+5** (2026-05-14 plan-update sequence Option 1): matched-multiples is a cheap independent early win (1-2 sessions; 4th HVS product); tests post-Tier-2 plumbing on a small new product before tackling the big 6-10 + 8-14 session backward extensions.
- **C8.17 before C8.18** within Tier 5 (EXPLORATION_REPORT Q36 default; user-confirmed 2026-05-14): natality 1968-1989 is shorter (6-10 vs 8-14 sessions), simpler revision-boundary story (sibling of just-shipped V3b fetal-death), and its 1978-cert layout work modestly benefits the cohort-linked 1983-1991 phase in C8.18.
- **C8.19 after C8.17 + C8.18**: perinatal-record pre-joined parquet depends on the final natality + linked envelopes.
- **C8.20-C8.22 last in Tier 3+5**: docs/usability ancillaries (CODEBOOK + Stata/SAS + cross-tabs) run AFTER data work for one-pass authoring against the final envelope; minimizes re-paragraph friction.

#### Always-on Phase C discipline

- Each task: full five-phase (`NEXT_STEPS.md` §4). PRE-FLIGHT writes Field-value snapshot (Convention 3). RECEIPT writes Forward-looking HALTs (Convention 4). Every new SMOKE asserts SHAPE-not-VALUE (Convention 1) + carries `DESIGN:` first-docstring tag (Convention 2).
- Each shipped task tagged `<task_id>-pre-do` (before DO) + `<task_id>-complete` (after RECEIPT). Receipt at `RECEIPTS/<task_id>_<UTC_timestamp>.md`.
- Halt-and-ask on any §7 condition. Do not silently work around. Do not patch downstream artifacts to match buggy upstream.
- Effort-ceiling cap (Q33 self-resolution): if cumulative Phase C effort drifts beyond +20% of the 29-35 session estimate (i.e., >42 sessions), halt at the next clean checkpoint and re-ask the user.
- Phase B-2 trigger (Q42 self-resolution): any new candidate >1 session triggers a `[plan-update]` per §11; silent in-Phase-C scope-creep forbidden.

### Phase D-prep — pre-Zenodo prep + audit pass (agent-executable; reversible; no external action; standing authorization)

Authorized 2026-05-24 by user directive (above). Each task below uses the full `NEXT_STEPS.md` §4 five-phase discipline (PRE-FLIGHT, SMOKE, DO, VERIFY, RECEIPT) per the new `§15.E` entries D-prep.1 — D-prep.5. **All tasks doc/CSV-only; zero canonical-state mutation expected; 4 gate parquet SHAs must remain byte-exact** (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…` — the strongest invariant). Sessions proceed under **standing authorization** (no per-task explicit go required; agent halts only on §7 conditions). Halt-and-ask on any genuine §7 trip.

- **D-prep.1** — `fetal-death-other-docs-v240-sync` (the R2d defer from the 2-round adversarial audit + `data_year` L60 stale `Years` column fix bundled) [~1-2 sessions]
  - Files: `fetal_death/ABOUT_THIS_RELEASE.md`, `fetal_death/ABOUT_SOURCE_DATA.md`, `fetal_death/FAQ.md`, `fetal_death/GETTING_STARTED.md`, `fetal_death/REPRODUCING.md`, `fetal_death/REPORTING_THRESHOLDS.md`, `fetal_death/README.md`, plus `fetal_death/CODEBOOK.md` L60 `data_year` row's `Years` column (V2.0 / 29-yr / 1992-2022 → v2.4.0 / 43-yr / 1982-2024 / 7-era envelope; same Option-A depth as the 2026-05-23 `fetal-death-codebook-comparability-v240` task; every number parquet-derived from Appendix C8.20 — L6-safe).
- **D-prep.2** — `provenance-refresh-current-envelope` (per-product `PROVENANCE.md` reflecting the v2.4.0 / v3.0.0 / v4.0.0 / matched-multiples envelope; SHA cross-reference with `docs/NCHS_SOURCE_MANIFEST.md`) [~0.5 session]
- **D-prep.3** — `schema-years-available-gap-notation` (per-product `harmonized_schema.csv` retroactive `years_available` cells annotating V3a/V3b/V2.1 fetal-death + the linked 1992-1994 permanent NCHS gap) [~0.5 session]
- **D-prep.4** — `pre-zenodo-audit-pass` (broad fresh-eyes adversarial audit of the substantive Phase C deliverables C8.16-C8.22 + the cross-product joint-use surface + user-facing docs + reproducibility surface + the existing `paper/draft_v2_hmd_styled.md` draft as D.4 input) [user-triggered for `/ultrareview` — billed; agent-launched 5-agent fresh-eyes round as fallback; ~1 session in either case]
  - **Recommended**: user runs `/ultrareview` from this repo (KICKOFF's prescribed mechanism for pre-Zenodo broader-audit surfaces; covers canonical pipelines + cross-product surface + manuscript). User-triggered + billed.
  - **Fallback**: agent launches a 5-agent fresh-eyes adversarial round paralleling the prior 2-round Pre-D cleanup audit pattern, covering: (1) data integrity (parquet schema + NVSR cells + 4 gate SHAs); (2) user-facing docs (post-D-prep.1); (3) reproducibility surface (`file_inventory.csv` + `NCHS_SOURCE_MANIFEST.md` + per-product `REPRODUCING.md`); (4) notebooks (`joint_use_demo.ipynb` + `paper_companion.ipynb` + `matched_multiples_demo.ipynb` run end-to-end against shipped parquets); (5) manuscript-readiness D.4 input (`paper/draft_v2_hmd_styled.md` numerics + word-count + references).
  - User may request additional audit rounds (2nd round paralleling the R1/R2 cross-round pattern).
- **D-prep.5** — `pre-zenodo-audit-fix-bundle` [**conditional** on D-prep.4 findings; same shape as the 2026-05-24 `audit-fix-r1r2-bundle` + C8.20-auditfix precedents; doc/CSV-only remediation; ONE single task under full five-phase discipline] — **COMPLETE** (`0a5d122`)

#### Phase D-prep follow-ups (D-prep.6–9) — user-authorized before Phase D; standing authorization

**Requires a build machine with gate parquets on disk** (paths in per-product `PROVENANCE.md` or `fetal_death/output/harmonized/`, `natality/output/harmonized/`). A typical git clone without a local build **cannot** complete D-prep.6–8; D-prep.9 path fixes can start in Cursor without parquets, but re-execution VERIFY needs parquets.

- **D-prep.6** — `build-host-gate-sha-verify` [**do this first**; ~5 min human or agent] Independently `shasum -a 256` the four gate parquets and confirm they match `STATUS` / `PROVENANCE.md` prefixes: fetal harmonized `38e2cecb…`, fetal derived `185c071e…`, natality derived `acb5c48a…`, linked derived `f630d8cf…`. **Halt on any mismatch** (§7-#18) before D-prep.7–8 or Zenodo upload. No file edits unless SHAs are wrong (then halt — do not patch docs to match wrong bytes).

- **D-prep.7** — `codebook-c820-appendix-regen` [~0.25–0.5 session; **needs parquets**] Run `uv run python scripts/_build_codebook_extensions.py` on the build host (env vars `HVS_FETAL_DERIVED`, `HVS_NATAL_DERIVED`, `HVS_LINKED_DERIVED` if paths differ). VERIFY: C8.20 marker block byte-change is expected; hand-authored CODEBOOK body outside markers unchanged; grep no stale `1,634,195` / `1992-2022` in generated `_Schema note_` lines for `data_year`/`delivery_year`. **4 gate parquet SHAs must remain byte-exact post-run** (script is read-only on parquets).

- **D-prep.8** — `convenience-csv-extend-2023-2024` [~0.25–0.5 session; **needs natality + fetal parquets on build host**] Extend `fetal_death/live_births_by_year.csv` and `fetal_death/stratified_denominators.csv` through **2023–2024** (currently end at 2022; documented workaround until this ships). Re-run `shared/helpers/build_stratified_denominators.py` + update `live_births_by_year` rows from NVSR or natality canonical counts; update `docs/JOINT_USE_GUIDE.md` convenience-year tables if counts change. **Optional to defer** if you accept “recompute from natality parquet” for 2023–2024; **recommended** before Zenodo if the fetal-death deposit will ship these CSVs.

- **D-prep.9** — `notebook-portable-paths` (PZ-NB) [~0.5–1 session] Regenerate or patch `notebooks/joint_use_demo.ipynb`, `notebooks/paper_companion.ipynb`, `notebooks/matched_multiples_demo.ipynb`, and `notebooks/_build_*.py` to use `REPO_ROOT`-relative paths (`natality/output/harmonized/`, `fetal_death/output/harmonized/`, `matched_multiples/output/harmonized/`). Fix `natality/notebooks/quickstart.ipynb` `data_year` + 201M copy. Re-execute notebooks on build host for VERIFY if parquets present. **Does not require parquet mutation.**

**Sequencing:** D-prep.1–9 + post-fix audits + `pre-zenodo-audit-fix-bundle-r4` (**done**) → **Phase D: D.2 → D.3 → D.4** (D.1 + old-Zenodo patches **deferred**). Paper 1 work may start in parallel with D.2 prep but should cite the **new** Zenodo DOI only after D.2 publishes.

**Sequencing within Phase D-prep (historical):** D-prep.1 → (D-prep.2 + D-prep.3 may parallelize) → D-prep.4 → D-prep.5 (conditional). D-prep.4 must run AFTER D-prep.1.

### Phase D — ZENODO + PUBLIC GITHUB + PAPER 1 (after Phase D-prep complete; user-trimmed scope 2026-05-21)

**Externally irreversible:** D.2 (Zenodo publish) and D.3 (public GitHub push). **Default sequence: D.2 → D.3 → D.4 (Paper 1).** Each step still needs explicit human go-ahead at session start (§7); standing D-prep authorization does **not** auto-run Phase D.

- **D.1. Task 9 — DEFERRED** (user 2026-05-21). Redirect/archive/delete on old repos `yoelplutchok/natality-harmonization` and `yoelplutchok/fetal-death-harmonization`. Optional later; not blocking Zenodo or Paper 1.

- **D.2. Task 10 — Unified Zenodo deposit (NEXT).** Publish a **new** unified HVS concept DOI covering all four in-repo products (natality v3.0.0, linked v4.0.0, fetal death v2.4.0, matched multiples). Agent: `.zenodo.json`, upload bundle list from `PROVENANCE.md`, post-publish `CITATION.cff` / `README.md` DOI lines. **Human:** zenodo.org upload. **Legacy patches (ii–iv)** to old concept DOIs — **DEFERRED** per user 2026-05-21. PRE-FLIGHT: re-hash 4 gate parquets on the **exact files** going into the zip (see “Gate SHA re-hash” in Current planned sequence).

- **D.3. KICKOFF step 5 — Refresh existing public GitHub (not “create repo”).** Repo already exists: https://github.com/yoelplutchok/vital-statistics-harmonization (v1.0 snapshot 2026-05-12 is stale). Re-rsync `~/Desktop/vital-statistics-harmonization-public/`, re-scrub, push v1.x to **overwrite** v1.0.

  **Scrub principle (user directive 2026-05-21):** publish ONLY what an external user needs to *understand and use* the resource. Exclude every execution-process artifact (audits, plans, pre-flights, receipts, decision/fix/lessons logs) AND the manuscripts. Parquets are NOT in git — README points to the Zenodo DOI from D.2.

  **Exclude (do NOT publish):**
  - Process/state files: `STATUS.md`, `DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `NEXT_STEPS.md`, `KICKOFF.md`, `PRE_FLIGHT_LOG.md`, `EXPLORATION_REPORT.md`, `VERSION_ROADMAP.md`
  - Process dirs: `RECEIPTS/`, `AUDITS/`, `.claude/`
  - Manuscripts: `paper/` (all drafts incl. `PAPER2_*`)
  - Internal / Phase-E code: `notebooks/_build_*.py`, `notebooks/ananth2022_*.py`
  - Internal benchmark: `docs/PIPELINE_TIMING_BENCHMARK.md`
  - Local-only (already gitignored, never in tree): the copyrighted Ananth PDF + `RECEIPTS/ananth2022_*outputs*/`

  **Include (the understand-and-use surface):** root `README.md`, `PROJECT_STRUCTURE.md`, `LICENSE`, `CITATION.cff`, `views.sql`, `STATA_SAS_QUICKSTART.md`, `pyproject.toml`, `uv.lock`, `requirements.txt`, `migrations/`; user-facing `docs/` (`JOINT_USE_GUIDE`, `COMPARABILITY`, `PRIOR_ART`, `NCHS_SOURCE_MANIFEST`, `WORKED_EXAMPLE_FAQ`, `PERINATAL_RECORD_FEASIBILITY`); each product's `README` + user docs (`CODEBOOK` / `COMPARABILITY` / `FAQ` / `GETTING_STARTED` / `REPRODUCING` / `ABOUT_*` / `VALIDATION` / `PROVENANCE`) + `scripts/` + `metadata/` + `output/validation/` + layout/threshold CSVs; `notebooks/*.ipynb` (executed worked examples only — NOT the builders); `csv/published_tabulations/`; `tests/`.

  **Borderline — confirm at D.3 run:** `VERSION_ROADMAP.md` + `docs/PIPELINE_TIMING_BENCHMARK.md` (excluded above as process docs; re-include if you decide they help users) and `tests/` (included above; drop if you'd rather keep the public tree minimal).

- **D.4. Paper 1 — Data Resource Profile** (`paper/draft_v2_hmd_styled.md`). Numeric + envelope sync; IJE trim; admin markers; cite new Zenodo + GitHub from D.2–D.3. Fresh-chat helper: `NEXT_STEPS.md` §19.1. Submit to IJE when human says go.

**Always-on guardrails for Phase C / D execution**:

- §7 halt conditions are binding. Every task PRE-FLIGHT runs the Field-value snapshot (Convention 3) + every RECEIPT writes Forward-looking HALTs (Convention 4) + every new SMOKE harness asserts SHAPE-not-VALUE (Convention 1) + carries a `DESIGN:` docstring tag (Convention 2).
- L9 cheap-checks on every cited external document; L13 column-content verification on every inventory CSV; L17 SMOKE stale-pinning awareness.
- Halt-and-ask on any §7 condition. Do not silently work around. Do not patch downstream artifacts to match buggy upstream.
- §2 four-core-principle: cheap-before-expensive, fail-closed, state-on-disk-never-only-in-memory, re-running-must-be-free.

**When Phase B / C / D may legitimately deviate**:

- If Phase B reveals that a candidate has a RDC-only blocker (or any other immovable obstacle): defer it to post-submission, document the deferral with the specific blocker.
- If Phase C reveals a cumulative effort exceeding what the user is willing to absorb: halt at the next clean checkpoint and re-ask.
- If a Phase B/C/D task surfaces a new mistake class (per §11): log to LESSONS.md, propose §8 matrix row, halt for human approval before continuing.

### Phase E — companion empirical paper drafting (after Phase D.4 ships; executed via fresh LLM chats OUTSIDE Claude Code)

**User-driven, not agent-executable in this Claude Code project.** Authorized 2026-05-24 by user directive (above): *"then generate apapers after sumbiting prompts etc."* After Paper 1 (the Data Descriptor at `paper/draft_v2_hmd_styled.md`, targeting IJE Data Resource Profile) is submitted to IJE at Phase D.4, the companion empirical paper is drafted via fresh LLM chats (claude.ai web or similar) using the self-contained prompt templates in `NEXT_STEPS.md` §19.

Two paper drafting prompts are stored in `NEXT_STEPS.md` §19 (self-contained for fresh-chat use; the chat does NOT need this monorepo's context — the user attaches the relevant files):
- **§19.1** — Paper 1 (Data Descriptor) **finalization** prompt — used at Phase D.4 to polish + IJE-prep the existing `paper/draft_v2_hmd_styled.md` draft (fresh chat: paste prompt + attach the draft + the four products' README + `docs/JOINT_USE_GUIDE.md` + `docs/COMPARABILITY.md`).
- **§19.2** — Paper 2 (Companion empirical) **drafting** prompt — used at Phase E to draft the companion paper from scratch (fresh chat: paste prompt + attach descriptor draft + `fetal_death/COMPARABILITY.md` + `fetal_death/CODEBOOK.md` + `csv/published_tabulations/`).

**If a Claude Code session is opened during Phase E:** the agent's (a)-(d) kickoff handshake should **surface this fact and halt** — Phase E substantive drafting is NOT in scope for the executing agent. The agent's allowed role during Phase E is narrowly: (a) answer questions about HVS data structures when the user pastes them in, (b) help generate small analysis scripts the companion paper needs (e.g., a stratified-trend computation script), (c) help with companion-paper-specific tooling. The substantive paper drafting happens in the fresh LLM chat outside Claude Code, per the §19 prompts.

---

**Source for this sequence:** 2026-05-12 chat sessions — DECISION_LOG entries 2026-05-11T20:50Z, 2026-05-12T01:35Z, 2026-05-12T03:30Z, 2026-05-12T18:30:00Z (B3 1-digit recode + DATAYEAR Option A for V3b), and the 2026-05-12 post-V3b-complete chat directive *"i would like do do everything possible with this project … before we do the paper or the zenodo"* (logged in DECISION_LOG 2026-05-12). 2026-05-23 "Pre-D cleanup first" + 2026-05-24 audit-fix-r1r2-bundle plan-updates (DECISION_LOG 2026-05-23T20:00:00Z + 2026-05-24T00:45:00Z). **2026-05-24 Phase-D-sequencing + Phase E plan-update** (DECISION_LOG 2026-05-24T01:30:00Z; this `[plan-update]` commit). STATUS.md's newest section is the canonical current-state file; this kickoff is the canonical sequencing pointer.

---

```
You are working on the U.S. Harmonized Vital Statistics (HVS) project
as the executing LLM agent.

BEFORE doing ANY work, read these files in this exact order:

1. STATUS.md  — current project state, current task, in-progress, blocks,
   open questions for human.

2. NEXT_STEPS.md  — operating protocol (§1-§13) and full task list (§14-§15;
   after §15.F closure the default queue is §15.G).
   §1 session-start, §2 four core principles, §4 five-phase structure
   (incl. §4.2.1 SHAPE-not-VALUE smoke + DESIGN docstring tag, §4.5
   commit-message brevity), §5 PRE-FLIGHT template (incl. Field-value
   snapshot), §6 RECEIPT template (incl. Forward-looking HALTs),
   §7 halt conditions, §8 mistake-class matrix (incl. L13/L14/L17),
   §9 anti-patterns, §10 self-check question. THIS IS THE BINDING
   OPERATIONAL CONTRACT.

3. README.md and PROJECT_STRUCTURE.md  — what the resource is, where
   things live.

4. The last 10 entries each of DECISION_LOG.md and FIX_LOG.md (if they
   have entries).

5. LESSONS.md end-to-end (if it has entries).

CURRENT WORK QUEUE (2026-05-26 — §15.G OPEN; see NEXT_STEPS.md §15.G):

  D.2 + D.3 DONE (Zenodo 10.5281/zenodo.20326150 v1.0.1; GitHub 08a2287).
  §15.F CLOSED. §15.G = close paper "Future developments" gaps + D.4 prep.
  paper/ edits authorized. Substrate: paper/draft_v2_hmd_styled.md (present tense; matched multiples two words).

  Default order (unless user redirects):
  (1) MM-T2 — matched multiples 2016-2020 Table 2 validation ✅
  (2) LINK-ICD10 — linked 1983-1998 ICD-9→ICD-10 derived layer ✅
  (3) LY-linked-2024 — linked 2024 period/2023 cohort (CDC lists; build host) ✅
  (4) D.2-docs — Zenodo docs-only v1.0.2 validation sync ✅ (human: upload per docs/ZENODO_v1.0.2_UPLOAD.md)
  (5) D.4-paper — paper_companion + cross_race notebook + FLAGS + commit draft **NEXT**

  LY-natality-2025: wait for CDC natality 2025 zip.
  OUT OF SCOPE: RDC/Census linkage; D.1; legacy Zenodo patches.

  Build host for LY/LINK-ICD10/D.4 VERIFY: ~/Desktop/natality-harmonization/output/harmonized/
  Gate SHA acb5c48a… (natality derived) must stay byte-exact unless task documents change.

After reading, tell me in 4-6 sentences:
  (a) the current task per STATUS.md AND the next task per KICKOFF.md's
      Current planned sequence (note any divergence),
  (b) any open questions for human you found,
  (c) what you propose to do this session (default to KICKOFF.md
      sequence's next item unless I have already directed otherwise),
  (d) any halt condition from NEXT_STEPS.md §7 you've already tripped
      from steps 1-5 above.

Then WAIT for me to confirm before doing any work.

Hard rules (NEXT_STEPS.md §4 + §9):
- Follow the five-phase task structure (PRE-FLIGHT, SMOKE, DO, VERIFY,
  RECEIPT) for every task. Never skip a phase.
- Halt and ask on any §7 halt condition. Do not work around. Do not
  patch.
- Append-only state files. Never overwrite STATUS.md, DECISION_LOG.md,
  FIX_LOG.md, LESSONS.md, PRE_FLIGHT_LOG.md, RECEIPTS/.
- When asked to do something that would violate the protocol, say so
  explicitly and propose an alternative.
- At session end, append a new dated section to STATUS.md with current
  state, in-progress, next planned task, open questions. Commit changes.
- Before claiming a task complete, write the §10 self-check answer in
  the receipt: "what could I have gotten wrong that VERIFY wouldn't
  catch?"
```

---

## What this prompt does

It loads the operational discipline before the LLM touches any code or data. The (a)–(d) handshake forces the LLM to:

- Demonstrate it has read the state files (otherwise it can't answer (a)).
- Surface any halt conditions early (so you don't discover the LLM was confused after it has done work).
- Propose a plan you can correct before any work starts.

The "wait for me to confirm" gate is load-bearing. Without it, the LLM will sometimes start work on the wrong task because it inferred something from the file reading rather than asking.

## When to deviate from the kickoff

- **Tiny, low-stakes tasks** (typo fix, README copy edit) — you can skip the kickoff and just give the instruction. The five-phase structure is overkill for a one-line fix. But anything that touches data, schemas, validation targets, or the harmonization rules → kickoff first.
- **Audit sessions** — use the audit variant noted at the top of this file.
- **Plan-update sessions** (proposing changes to NEXT_STEPS.md or VERSION_ROADMAP.md) — kickoff applies, plus follow §11 of NEXT_STEPS.md (the plan-update process).
