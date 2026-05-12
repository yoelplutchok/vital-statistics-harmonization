# DECISION_LOG

> **Append-only.** Every non-trivial choice the LLM (or human) makes during HVS work is logged here as a dated row. Each entry includes the alternatives considered and the reason for the choice.
>
> A "non-trivial choice" is anything that:
> - Affects the harmonized schema, the analytic filters, or the validation targets
> - Resolves an ambiguity in the source documentation
> - Trades off two reasonable approaches with different downstream costs
> - Documents a residual risk surfaced by the §10 self-check in NEXT_STEPS.md
> - Defers a deferral or scope change
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <one-line title>
> **Choice:** <what was chosen>
> **Alternatives:** <what else was considered>
> **Reason:** <why; cite source documents with page/section if relevant>
> **Source:** <PMID, PDF SHA-256, or repo path>
> **Verifiable by:** <how a future reviewer can check the choice was right>
> **Reversible:** yes / no — <if yes, how>
> ```

---

## 2026-05-12T04:30:00Z — task7_v3b_doc_hunt — KICKOFF Step 0 V3b doc retry succeeded; proposing Task 7 scope expansion to 1982-2022 (41 years)

**Choice (proposal pending user confirmation):** Expand Task 7 scope from the prior session's "V3a only (1989-1991, 34 years total)" framing back to "V3a + V3b (1982-2022, 41 years total)" per KICKOFF.md Step 0 contingency ("If V3b authoritative docs found → expand Task 7 scope to 1982-2022 and proceed with V3a + V3b"). Step 0 found all 10 fetal-death user guides 1982-1991 obtainable from NCHS canonical FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (all HTTP 200; sizes/last-modified per STATUS 2026-05-12T04:30Z). The proposal is NOT yet authorized — it requires explicit user yes before Task 7 PRE-FLIGHT begins downloading the PDFs to the build dir.

**Alternatives considered:**

1. **Keep prior session's V3a-only scope** (1989-1991, 34 years; V3b deferred post-submission). Pro: shorter Task 7 budget (~1 session, not ~4-5); ships a strict superset of the current 31-year coverage; preserves integrity-principle simplicity. Con: leaves 7 years on the table that authoritative sources now confirm are accessible; the manuscript would cite 34 years with a post-submission v1.2 promise to extend, instead of citing the final 41-year extent.

2. **Expand to V3a + V3b (1982-2022, 41 years) — proposed.** Pro: maximum-extent paper coverage from first submission; cited DOI is final not incremental; the integrity principle is SATisfied because authoritative NCHS PDFs anchor V3b layout reconstruction (NOT reverse engineering). Con: +3-4 sessions of effort vs V3a-only; OCR pass required on bitmap-scanned 1980s PDFs (NCHS-published but image-scanned); L13-extension value-distribution discipline must be applied per-field on the new V3b layouts.

3. **Hybrid: V3a + V3b 1988 only.** The Damian Clarke `fetl1988.dct` artifact (88 fields, 200-byte layout) plus the NCHS 1988 user guide is a single-year addition that minimizes OCR risk (1 PDF instead of 7). Adds +4 years total (1988-1991). Rejected as a stopping point — once OCR machinery exists for one year, the marginal cost of 6 more years is small; arbitrary cutoff at 1988 is unjustified.

**Reason:** Step 0 reversed the prior session's empirical assumption ("V3b docs not at NCHS"). Wrong-filename probes by the 2026-05-12T03:50Z agent (used `Fetal82UG.pdf`, `fetal_death_inst.pdf`, NCHS series_04 paths, etc.; did NOT try `<YYYY>FetalUserGuide.pdf` despite that being the exact convention used by 2003-2022 files already on disk in this monorepo). This session's WebFetch on `cdc.gov/nchs/data_access/vitalstatsonline.htm` surfaced the canonical NCHS link list including all 7 V3b years and verified by HEAD probe. Sanity download of 1985 confirmed valid PDF + SHA recorded. The integrity-principle objection in 2026-05-12T04:00Z STATUS ("can't claim 100% correct without authoritative codebook") no longer applies: authoritative codebooks exist and are obtainable.

**Source:**
- WebFetch result for `https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm` showing per-year fetal-death documentation links 1982-1988.
- `curl -sI -k <YYYY>FetalUserGuide.pdf` returning HTTP 200 with valid content-length for all 10 years 1982-1991.
- `/tmp/v3b_hunt/1985FetalUserGuide.pdf` SHA-256 `f7342480302017caf622243510c7e32ea03b6083b9797768b59fa50954eb1ed5`; `file(1)` reports valid PDF v1.4.
- GitHub `damiancclarke/nchs-fetaldata` `process/dicts/fetl1988.dct` 7,412 bytes (cross-check artifact, not authoritative; Damian Clarke 2014-07-02 Version 0.0.0 empty README).
- KICKOFF.md Step 0 contingency clause (lines 47-55 of KICKOFF.md).

**Verifiable by:**
- This entry's HEAD probe results are repeatable via `curl -sI -k https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` for any year 1982-1991.
- The 1985 PDF SHA can be reproduced by `curl -s -k -o /tmp/check.pdf <url> && shasum -a 256 /tmp/check.pdf`.
- STATUS.md 2026-05-12T04:30Z section is the canonical current-state record.

**Reversible:** yes — if Task 7 V3b OCR proves intractable (e.g., the 1980s NCHS scan quality is too low for reliable layout-table OCR, or value-distribution verification surfaces unresolvable per-field semantics ambiguity), the user can direct a fall-back to V3a-only scope at Task 7 PRE-FLIGHT halt-and-ask moment. The proposal does not commit V3b irreversibly; it commits to *attempting* V3b with halt-condition discipline.

**Residual risks:**
- (a) **OCR quality on 2009-vintage NCHS bitmap scans is unknown.** Quality varies year-to-year (NCHS rescanned old paper docs in 2009-01-08 batch; some scans may be cleaner than others). Mitigation: a 20-min proof-of-concept OCR run on a few `1985FetalUserGuide.pdf` pages before committing to all 7 V3b years (was option 4 of this session's 4-option ask; user chose option 1 "update state files first").
- (b) **L13-extension discipline overhead per year**: 7 V3b years × (per-field value-distribution verification + layout-CSV reconstruction from OCR'd text) may grow Task 7 V3b beyond the 3-4 session estimate if multiple fields surface semantic mismatches like the MAGER vs MAGER41 incident in V2.1.
- (c) **Damian Clarke 1988.dct provenance gap**: the Clarke artifact's "Version 0.0.0" + empty README means it MAY itself be reverse-engineered or partially-incorrect. Treating it as a cross-check (not authority) preserves integrity; treating it as authority would be the L13-extension shape we explicitly avoid.
- (d) **Manuscript timing**: pre-submission scope was already expanded once (2026-05-11T20:50Z) and again (2026-05-12T03:30Z); this is the third expansion in 3 days. User has accepted the trade-off pattern of "more sessions for final manuscript state" — but the absolute session count keeps growing. If V3b OCR surfaces a multi-session blocker, the user has the option to fall back without re-litigating the data-first-vs-submit-now choice from scratch.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts "authoritative NCHS PDFs are obtainable" based on (i) HEAD probes returning HTTP 200, (ii) one sanity download verifying valid PDF + matching content-length. It does NOT verify the PDF's *content* is a usable codebook with readable byte-layout tables. The 1985 PDF is bitmap-scanned; if those scans are illegible or missing the layout-table appendix entirely (e.g., the PDF body is some unrelated NCHS report, not a public-use file codebook), this proposal's premise is wrong. Mitigation: Task 7 PRE-FLIGHT MUST include an L9 cheap-check (open one PDF, locate the byte-layout table by page) before downloading all 10 to the build dir and committing harmonization effort.
- The 200-byte record length for 1982-1988 is verified by the prior session's `unzip` + byte-inspection (STATUS 2026-05-12T03:50Z); the layout table in the user guide MUST sum to 200 bytes to be consistent with the actual public-use file. Bond verification at Task 7 PRE-FLIGHT L9 step.

---

## 2026-05-12T03:30:00Z — sequencing — Pull Task 7 (V3 1982-1991) and natality v2.8 rename INTO pre-submission scope

**Choice:** Override the prior "out of pre-submission scope" status (KICKOFF.md, DECISION_LOG 2026-05-11T20:50Z) for both Task 7 fetal-death V3 backward extension AND natality v2.8 column rename. Both will be completed before manuscript submission. New pre-submission sequence:

1. ~~Task 3 V2.1 fetal-death~~ DONE 2026-05-12 (`task3-complete` at `8ca5bf9`).
2. ~~Push monorepo to GitHub at v1.0~~ DONE 2026-05-12 (public repo at https://github.com/yoelplutchok/vital-statistics-harmonization, commit `a18ca3a`).
3. **Natality v2.8 column rename** (start NEXT session per parallel-paths choice; user downloads Task 7 inputs concurrently). ~2 sessions.
4. **Task 7 V3 fetal-death** (1982-1991, +10 years). 2-4 sessions; OCR risk on older user guides.
5. **Task 9 — redirect notices on the two old GitHub repos** (~15-30 min, human-driven).
6. **Task 10 — Unified Zenodo deposit** + v2.1.0 patch to old fetal-death deposit (1 session + upload time).
7. **Push v1.1 to GitHub** (replaces current v1.0 contents; cleanly amended single-commit history not preserved — incremental release).
8. **Manuscript re-pass + submit** (~½ session).

**Alternatives considered:**

1. **Keep prior sequence (Task 7 + natality v2.8 post-submission).** Original NEXT_STEPS.md §17 + KICKOFF.md "out of scope" framing. Pro: shortest path to submission. Con: per the human's preference, the manuscript would cite a 31-year fetal-death series + v2.7.0 natality, then require v3-extended fetal-death + v2.8-renamed natality in a follow-up correction. Pre-emptively doing them before submission means the paper goes out at the latest data state.

2. **Pull Task 7 + natality v2.8 + extend further (chosen).** Pre-submission scope grows by 3-5 sessions. Pro: manuscript ships at maximum-coverage state (41 years fetal-death; aligned natality column names). Con: 3-5 more sessions of work before submission.

**Reason:** Same as DECISION_LOG 2026-05-11T20:50Z (data-first sequencing) but with maximum-extent target instead of minimum-viable. The marginal session-cost of Task 7 + v2.8 (3-5 sessions) is justified by the manuscript-once-and-final outcome. User explicitly authorized.

**Source:** Chat 2026-05-12 between commits `8ca5bf9` (Task 3 V2.1 complete) and `a18ca3a` (public repo push) and this entry. User explicit confirmation of override + parallel-paths sequencing.

**Verifiable by:**
- This DECISION_LOG entry timestamp 2026-05-12T03:30:00Z supersedes 2026-05-11T20:50Z's pre-submission scope listing.
- Future sessions reading STATUS.md + this DECISION_LOG see natality v2.8 as next task; Task 7 follows once 1982-1991 NCHS inputs are downloaded.

**Reversible:** yes — if Task 7 hits a multi-session blocker (e.g., NCHS 1982-1991 user guides only available as scanned/OCR-resistant PDFs), the human can direct a fall-back to submitting at the post-V3-attempt state with Task 7 explicitly deferred again.

**Residual risks:**
- (a) **Task 7 input availability**: PRE-FLIGHT this session showed ZERO 1982-1991 zips or user guides on disk. User has been asked to download from NCHS FTP path `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetal-deaths/`. Some older-year files may not be in the standard public-use FTP path — verification required.
- (b) **Natality v2.8 scope larger than initial estimate**: PRE-FLIGHT shows 61 string-literal column-name references across natality scripts + 4 schema rows + 6 docs + 2 parquets to re-derive + 183 NVSR validation targets to re-gate. Estimated 2 sessions, not 1.
- (c) **Cross-product effects of natality v2.8 rename**: monorepo's `shared/helpers/canonical_join_keys.py` aliasing helper becomes a no-op after v2.8. monorepo's `notebooks/joint_use_demo.ipynb` and `paper_companion.ipynb` use the aliasing helper; they should continue to work (helper still imports, just renames are no-ops). Re-run both notebooks after v2.8 to verify.
- (d) **v1.0 public repo is now slightly stale**: pushed at Task 3 V2.1 state, will be superseded by v1.1 (post-Task-7 + post-v2.8). No external pulls expected in the brief window; acceptable.

---

## 2026-05-12T03:25:00Z — natality_v28_rename — PRE-FLIGHT findings: 61-string-literal rename surface (Field-value snapshot per Convention 3)

**Pre-flight result:** PROCEED to next session DO. No halt conditions. Inputs all available (natality build dir intact at v2.7.0; aliasing helper documents exact renames).

**Field-value snapshot — current state of canonical artifacts that v2.8 will mutate:**

| Artifact | Current (v2.7.0) | Target (v2.8) |
|---|---|---|
| `metadata/harmonized_schema.csv` row 1 | `year,Birth year,int16,...` | `data_year,Data year,int16,...` |
| `metadata/harmonized_schema.csv` row 2 | `restatus,Resident status (NCHS),int8,...` | `residence_status,Residence status,int8,...` |
| `metadata/harmonized_schema.csv` row N | `maternal_hispanic_origin,...` | `hispanic_origin,...` |
| `metadata/harmonized_schema.csv` row M | `maternal_race_bridged4,...` | `maternal_race_bridged,...` |
| natality parquets | columns named `year`, `restatus`, `maternal_hispanic_origin`, `maternal_race_bridged4` | renamed to canonical names |
| `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` dict | 4 explicit renames at read time | EITHER no-op (empty dict) OR full removal with helper deprecation notice |

**String-literal reference counts (the edit surface, scoped to natality build dir scripts/metadata/docs):**

- `"year"` / `'year'`: 48 references (most string-literal column-name uses; some may be `df.groupby("year")` style; many are validation filter expressions like `mask = subset["year"] == y`)
- `"restatus"` / `'restatus'`: 3 references
- `"maternal_race_bridged4"` / `'maternal_race_bridged4'`: 6 references
- `"maternal_hispanic_origin"` / `'maternal_hispanic_origin'`: 4 references
- Total: **61 string-literal references**

**Files touching these columns (per `grep -rln`):**

| Layer | Files |
|---|---|
| Schema | `metadata/harmonized_schema.csv`, `metadata/external_validation_targets_v1.csv` |
| Harmonize | `scripts/03_harmonize/harmonize_v1_core.py`, `scripts/03_harmonize/harmonize_linked_v3.py` |
| Validate | `scripts/05_validate/qa_yearly_core_parquet.py`, `validate_row_counts_vs_nchs.py`, `harmonized_missingness.py`, `key_rates_from_derived_core.py`, `compare_external_targets_v3_linked.py`, `compare_external_targets_v1.py`, `validate_linked_parquets.py`, `validate_v1_invariants.py` |
| Convenience | `scripts/06_convenience/write_residents_only.py` |
| Figures | `scripts/07_figures/generate_paper_figures.py` |
| Docs | `docs/CODEBOOK.md`, `docs/COMPARABILITY.md`, `docs/FAQ.md`, `docs/ABOUT_THIS_RELEASE.md`, `docs/GETTING_STARTED.md`, `docs/VALIDATION.md` |
| Import (linked) | `scripts/01_import/parse_linked_cohort_year.py`, `scripts/01_import/README.md` |

**DO-phase plan:**

1. Edit `metadata/harmonized_schema.csv`: rename 4 rows. Verify schema-version bump (v2.7.0 → v2.8.0) annotated.
2. Edit `scripts/03_harmonize/harmonize_v1_core.py`: rename column-write string literals.
3. Edit `scripts/03_harmonize/harmonize_linked_v3.py`: same.
4. Re-derive `natality_v2_harmonized_derived.parquet` + `natality_v3_linked_harmonized_derived.parquet`.
5. Verify column names in resulting parquets (should be `data_year`, `residence_status`, `maternal_race_bridged`, `hispanic_origin`).
6. Edit 5 validate scripts + 2 misc scripts + 1 import script: rename column-read string literals.
7. Run 183 NVSR validation targets; gate 183/183 byte-exact.
8. Run linked-file validation; gate 33/35 + 2 differ-by-1.
9. Edit 6 docs (CODEBOOK, COMPARABILITY, FAQ, ABOUT_THIS_RELEASE, GETTING_STARTED, VALIDATION) to use new column names.
10. Update `shared/helpers/canonical_join_keys.py` in the monorepo: `NATALITY_TO_CANONICAL` becomes empty dict + deprecation note; the helper continues to import for backward compatibility but is a no-op for natality v2.8.
11. Re-run `notebooks/joint_use_demo.ipynb` + `notebooks/paper_companion.ipynb` against the v2.8 natality parquet to verify cross-product joins still work.
12. Sync renamed files to monorepo's `natality/` subdirectory.
13. Bump version: `CITATION.cff` 2.7.0 → 2.8.0; new Zenodo deposit (since v2.8 is a breaking change; v2.7.0 stays at its DOI for backward compatibility).
14. Write RECEIPT + FIX_LOG + DECISION_LOG entries.

**Forward-looking HALTs for the DO session:**

1. Some "year" references in scripts may be LOCAL VARIABLES, not column-name string literals. The rename must distinguish `df["year"]` (rename target) from `for year in range(...)` (untouched). Use targeted sed patterns like `s|"year"|"data_year"|g` and `s|'year'|'data_year'|g` only — not bare-word replacement.

2. `external_validation_targets_v1.csv` may have "year" as a column header. Inspect before editing; the V1 validation target CSV is canonical state.

3. The downstream user's local projects (multiple-gestation-linked-imr, lbw-imr-divergence per DECISION_LOG 2026-05-11T18:06:12Z) will break on v2.8 — they hard-code `df["year"]` etc. A separate compatibility task to update those projects is OUT OF SCOPE for natality v2.8 itself; flag for the user.

4. The aliasing helper currently maps 4 names. After v2.8, natality natively has the canonical names. The helper's `NATALITY_TO_CANONICAL` dict should be empty `{}` (so `to_canonical_natality(df)` becomes a passthrough). Verify nothing breaks at the call sites.

5. Re-deriving natality parquet takes ~5-10 minutes on the v2.7.0 build laptop. Budget accordingly.

---

## 2026-05-12T01:35:00Z — task3_v21_fetal_death — Bundle 4 fixes into Task 3 V2.1 build (B7 + H8 + data_year + monorepo path drift)

**Choice:** Land the following four orthogonal fixes inside a single Task 3 V2.1 build, producing one new shipped artifact pair (`fetal_death_harmonized.parquet` sha=`333e1e66…d9e0`, `fetal_death_derived.parquet` sha=`55d3d310…c447`) and one set of canonical-state log entries:

1. **B7 TABFLG normalization** for 2003/2004 — NCHS-errata correction per `fetaldeath0304problems.pdf` (records with COMBGEST=99 and OSTATE in 43-state list set TABFLG=2; raises per-year resident totals from 25,653/25,655 originally-reported to 26,004/26,001 corrected, byte-exact against the errata's Table 1).
2. **H8 schema-vs-data dtype reconciliation** — five demographic/filter columns cast from `object` to nullable Int (`tabulation_flag` Int8, `residence_status` Int8, `maternal_age` Int16, `maternal_race_bridged` Int8, `hispanic_origin` Int8), matching the schema CSV and the natality v2.7.0 dtype convention; closes FIX_LOG 2026-05-11T18:50:00Z.
3. **`data_year` derived-column fix** — surfaced when the V2 validator returned 0/23 after H8: the harmonize loop's field-map iteration was overwriting the int32 `data_year` initialization with empty-string `object` because the crosswalk row for `data_year` has `field_2006="derived"` which falls through to the loop's else-branch. Added `if raw_field == "derived": continue` to skip derived-marker rows.
4. **Monorepo path drift in `harmonize.py` + `validate_external*.py`** — pre-existing from monorepo migration `7fd9cdf`; scripts assumed `fetal_death/metadata/` subdir but the monorepo flattened the layout. Re-pointed `_CROSSWALK_CSV`/`_SCHEMA_CSV`/`_HARM_PATH`/etc. to the actual paths.

**Alternatives considered:**

1. **Land each fix as a separate task** (B7 → task3a, H8 → task3b, data_year → task3c, paths → task3d). Cleaner per-task scope; one parquet rebuild per fix. Cost: 4 parquet rebuilds, 4 separate receipts, 4 separate Zenodo deposit considerations. Rejected — H8/data_year/paths are LATENT bugs surfaced as a consequence of running Task 3's re-derive; treating them as separate tasks is artificial, and re-deriving the parquet four times burns reproducibility-budget for no extra information.
2. **Land B7 only; defer H8/data_year/paths to post-submission** (chosen-not). Pro: keeps Task 3 scope tight. Con: V2.1 ships with a known H8 dtype defect AND a latent data_year bug that would re-surface when downstream code starts using the int-comparison path; manuscript references the v2.1.0 parquet with two known issues that would need a v2.1.1 correction. Rejected.
3. **Land all four fixes bundled into one V2.1 build (chosen).** Pro: one parquet, one receipt, one deposit-version, transparent V2.1 release notes covering everything that changed. Con: receipt is denser; Task 3 effort exceeded the 1–2 session estimate. The receipt names all four orthogonally; downstream readers can trace each.

**Reason:** All four fixes converge on the same parquet rebuild. B7 requires harmonize.py edit and re-derive. H8 requires harmonize.py edit and re-derive. data_year bug surfaces during H8 re-derive (the validator failure exposes it). Path drift blocks all of the above from running at all. Bundling is the natural unit. Convention 1 (SHAPE-not-VALUE) is preserved — no SMOKE harnesses pin v2.0.0-specific values that V2.1 changes.

**Source:**
- `FIX_LOG.md` entries 2026-05-12T01:30:00Z (three new entries: H8 closure, data_year, monorepo path drift).
- `fetal_death/V2_1_2003_2004_LAYOUT_DECISIONS.md` (new).
- `raw_docs/fetal_death/fetaldeath0304problems.pdf` page 1 + Tables 2–3 (for B7).
- `raw_docs/fetal_death/2003FetalUserGuide.pdf` pages 17–19 (for the MAGER41-vs-MAGER discovery).

**Verifiable by:**
- `validate_external.py` 55/55 + `validate_external_v2.py` 23/23 = 78/78 byte-exact pass.
- joint_use_demo: 8/8 NVSR Table-4 age-band cells byte-exact for 2022.
- paper_companion: 34/34 PASS, 0 FAIL.

**Reversible:** yes — `git reset --hard task3-pre-do` reverts; v2.0.0 parquet preserved at `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet` (sha `90af89b9…`) for byte-clean baseline comparison.

**Residual risks (Self-check feed):**
- (a) **`record_layout_2003/2004.csv` documentation imprecisions** (inherited from 2006 with anchor-field spot-checks; surfaced semantic mismatch at MAGER vs MAGER41 plus several BLANK-vs-actual-field documentation errors). The harmonized parquet is correct (because parser-read positions for fields the harmonizer reads ARE correct, or read-all-blank which is correct behavior); only the layout CSVs need a post-submission audit-rebuild. Documented in `V2_1_2003_2004_LAYOUT_DECISIONS.md`.
- (b) **V1-era byte-clean column-level regression not exhaustively verified.** The V1 validator passed 55/55 (functional verification), but a column-by-column SHA comparison of the 2005–2022 slice of the new derived parquet vs v2.0.0's `90af89b9…` derived parquet was NOT performed this session. The 5 H8 columns are expected to change (string→int); all other 84 columns should be byte-identical. Forward-looking HALT in receipt.
- (c) **maternal_age=null for 2003+2004 may surprise downstream users** unaware that the 2003+2004 public-use files don't ship single-year-of-age. Documented in V2_1_DECISIONS doc and in the JOINT_USE_GUIDE dtype note.
- (d) **Other monorepo scripts may have latent path drift** (parse_fetal_year.py, derive.py, run_pipeline.py, tests/conftest.py). Not touched this session; flagged in FIX_LOG 2026-05-12T01:30:00Z forward-looking follow-up.

---

## 2026-05-11T20:50:00Z — sequencing — Data-first before manuscript submission (Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit)

**Choice:** Run the remaining data-side work (Task 3 V2.1 fetal-death with bundled H8 reconciliation) and the cross-product publication tasks (push GitHub, Task 9 redirect notices, Task 10 unified Zenodo) BEFORE manuscript submission, so the manuscript cites the latest fetal-death coverage and the unified Zenodo concept DOI from the first submitted version rather than the two old subproject DOIs.

**Alternatives considered:**
1. **Submit now, do data work later (submit-first).** Three pre-submission process tasks: YP admin review, GitHub push + URL injection, IJE reference reformat. Then submit at v2.0 fetal-death (29 years, with 2003–2004 gap) citing concept DOIs 10.5281/zenodo.19363074 + 10.5281/zenodo.20031571. Pros: fastest path to submission; ½ session. Cons: the paper goes out reporting a 2-year gap and the two old DOIs; a follow-up correction or v2.1 release update would be needed within weeks; the manuscript's headline numbers (1,634,195 fetal deaths; Table 1 fetal-death row count = 3; validation counts 29/29 + 26/26) become stale on a planned schedule.
2. **Data-first sequence: Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit (chosen).** Run Task 3 (V2.1 fetal-death; bundles H8 schema-doc reconciliation), push the monorepo to GitHub, do Task 9 redirect notices, set up the unified Zenodo deposit with DOI pre-reservation, then a half-session manuscript re-pass to update affected numbers (fetal-death record count ~1.6M → ~1.7M; Table 1 rows; validation counts 31/31 + 28/28), inject the unified DOI and GitHub URL, resolve the three `<!-- YP: review -->` admin-section markers, and reformat references. Pros: paper is published at the latest data state; cites the unified DOI from day one; H8 dtype fix-up rides for free in the Task 3 parquet re-derivation. Cons: 4–6 session delay before submission; Task 3 has known unknowns (2003 + 2004 transition-layout reconstruction from NCHS user guides — `fetaldeath0304problems.pdf` is the documented source for the known ambiguities).
3. **Maximum-extent: also do Task 7 V3 backward extension to 1982 pre-submission.** Adds 1982–1991 fetal-death (1978-revision + early 1989-revision). Pros: longest paper coverage. Cons: explicitly post-submission per `NEXT_STEPS.md` §17; 2–4 sessions; OCR risk on older user-guide PDFs; the marginal scientific value over the V2.1 state is incremental. Rejected as scope creep.
4. **Maximum-extent: also do natality v2.8 column rename pre-submission.** Renames `year` → `data_year`, `restatus` → `residence_status`, etc., so the aliasing helper becomes a no-op deprecation. Pros: cleaner namespace alignment. Cons: breaking change for downstream natality-only users (the `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the human's Desktop); requires re-running 183 NVSR validation targets + new natality Zenodo deposit; the paper's Methods section already documents the cross-product alignment via the aligned shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status` per the manuscript), so deferring the rename does not cost the paper a claim. Rejected as scope creep + breaking-change risk.

**Reason:** The Data Resource Profile genre rewards "publish at the latest data state" and the IJE editorial expectation is that a Data Resource Profile cites the unified resource DOI in the manuscript. Submitting at v2.0 fetal-death (29-year coverage) and v2.1-correcting weeks later costs more author and editor time than a 4–6 session pre-submission data push. Task 3 is rated "ideally pre-submission, not blocking" by `NEXT_STEPS.md` §17 — the §17 framing was conservative; the human's preference to upgrade it to "do before submission" is consistent with the underlying intent. Task 7 and natality v2.8 are explicitly post-submission and remain so.

**Source:** Chat transcript 2026-05-11 between Task 5 commit `9aaa702` (20:30Z) and this DECISION_LOG entry (20:50Z); human's explicit confirmation of the sequence after LLM presented the trade-off summary. `KICKOFF.md` "Current planned sequence" block; STATUS.md 2026-05-11T20:50:00Z section.

**Verifiable by:**
- `KICKOFF.md` contains the "Current planned sequence" section listing the 5-step order (Task 3 → push → Task 9 → Task 10 → re-pass + submit).
- `STATUS.md` most-recent section is dated 2026-05-11T20:50:00Z and supersedes the Task 5 entry's "Next planned task: Pre-submission process pass by default" line.
- Future sessions reading KICKOFF.md and STATUS.md will propose Task 3 as the next task by default; the (a)-(d) handshake's (c) "what you propose to do this session" should name Task 3 PRE-FLIGHT unless the human directs otherwise.

**Reversible:** yes. If Task 3 hits a multi-session blocker (e.g., a 2003-revision layout ambiguity that NCHS docs don't resolve), the human can direct a fall-back to the submit-first sequence (alternative 1 above) without needing a new DECISION_LOG entry — just halt Task 3 at the blocked PRE-FLIGHT and pivot.

**Residual risks:**
- (a) Task 3 effort estimate (1–2 sessions) could grow if the 2003 + 2004 transition-layout reconstruction hits ambiguities. The human has implicit budget tolerance for this per the data-first choice; explicit budget reset would be a halt-and-ask moment.
- (b) The manuscript re-pass in step 5 is a paper-side ripple effect; if the journal's IJE author guidelines change in the intervening 4–6 sessions, the re-pass scope grows. Mitigation: low-probability over a multi-week window.
- (c) Cross-pollination between Task 3 (data-side change) and the manuscript edits (Task 5's body) is unavoidable. Task 4's HALT 5 already documents this: any manuscript edit re-runs `_build_paper_companion.py` to detect new/changed claims; Task 3's effect on the manuscript means the synthesis CSV WILL change (currently bit-stable at `7891809c...`).

---

## 2026-05-11T20:30:00Z — task5_manuscript_trim — Override Task 4's C47/C48/C49 L11 recommendation (Task 4 misdiagnosis)

**Choice:** Do NOT apply Task 4's recommended precision edit for C47/C48/C49 (line 104 of `paper/draft_v2_hmd_styled.md`). Keep the manuscript wording for `maternal_education`, `paternal_age_combined`, and `maternal_education_unrevised` exactly as-is.

**Alternatives considered:**
1. **Apply Task 4's recommended edit** — rewrite line 104 to clarify that the italicised names are "raw NCHS field names" rather than harmonized columns. Task 4's PRE-FLIGHT and receipt explicitly recommended this as a Task 5 input.
2. **Override and keep manuscript as-is (chosen).** Direct verification at Task 5 PRE-FLIGHT shows that the italicised names ARE fetal-death harmonized column names per `fetal_death/harmonized_schema.csv` lines 17 (`maternal_education`, years_available `2005-2006, 2014-2022`), 18 (`maternal_education_unrevised`, years_available `1992-2002, 2005-2006`), and 21 (`paternal_age_combined`, years_available `1992-2002, 2005-2006, 2014-2022`). Direct null-rate verification on `fetal_death_derived.parquet` (sha=`90af89b9...`) shows 100% blank for all three columns in 2007–2013 — matching the manuscript's claim byte-exact. The italicization convention is consistent with line 60's `breech_unrevised` / `delivery_place_unrevised` / `maternal_race_bridged_detail` (italics = harmonized column names throughout the manuscript). The manuscript wording at line 104 is correct and self-consistent; no edit is warranted.
3. **Hybrid: keep wording but add a clarifying footnote naming the underlying raw NCHS fields (MEDUC, FAGECOMB, MEDUC).** Considered; rejected as scope creep — the harmonized column / raw-field correspondence is documented in `fetal_death/harmonized_schema.csv` already, and adding a manuscript-level footnote duplicates the schema CSV without adding clarity.

**Reason:** Task 4's PRE-FLIGHT and DO phase checked the NATALITY parquet (`natality_v2_harmonized_derived.parquet`) for these three column names. The natality parquet has different harmonized column names for the same conceptual fields: `maternal_education_cat4` (a 4-category derivation) rather than `maternal_education`; `father_age` (single-year) rather than `paternal_age_combined`; and no equivalent of `maternal_education_unrevised`. Task 4 received "columns not found" from the natality parquet and interpreted the manuscript's italicised names as raw NCHS field names. The fetal-death parquet was not checked. Task 5 PRE-FLIGHT re-verification reads the fetal-death schema CSV and parquet directly and finds the manuscript wording byte-exact correct. This is a Task 4 receipt Self-check item 4 outcome: the receipt explicitly flagged "if the manuscript actually means harmonized columns, then C47–C49 are DIFFs… the latter scenario is plausible — recommend Task 5 author verify which framing was intended" — Task 5 carried out that verification and found the harmonized-columns framing is the correct one.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-11T20:05:00Z (Field-value snapshot, "5 precision-edit candidates from Task 4 — PRE-FLIGHT re-verification" table, C47/C48/C49 row).
- `fetal_death/harmonized_schema.csv` lines 17, 18, 21 (authoritative declaration of harmonized column names + years_available).
- Direct fetal-death parquet null-rate verification (PRE-FLIGHT bash output 2026-05-11T20:00Z): `maternal_education` 100% blank 2007-2013; `paternal_age_combined` 100% blank 2007-2013; `maternal_education_unrevised` 100% blank from V1 2007 onward.
- `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` Self-check item 4 (Task 4's own flag that this could be a misdiagnosis).

**Verifiable by:**
- `grep -n "^maternal_education,\|^maternal_education_unrevised,\|^paternal_age_combined," fetal_death/harmonized_schema.csv` returns three rows matching the years_available pattern above.
- A re-run of `python notebooks/_build_paper_companion.py` against an unchanged fetal-death parquet emits 100.00% blank rates for 2007-2013 in C47/C48/C49 cells, matching the manuscript.

**Reversible:** yes — if the IJE author or peer reviewer requests the clarification anyway, the Hybrid alternative (a footnote naming the underlying raw fields) is a one-line addition.

**Residual risks:**
- (a) A reader who is unfamiliar with the harmonization may parse line 104's `maternal_education` as the natality harmonized column (which has a different name) and conclude there is a manuscript-data mismatch. Mitigation: the schema CSV (shipped) is the canonical disambiguation; a future precision pass could add an explicit `(fetal-death harmonized columns)` parenthetical, but this is sub-precision-edit not L6 risk.
- (b) The Task 4 receipt's Forward-looking HALT 1 names C47/C48/C49 as a Task 5 input; future receipt-readers tracing the HALT chain should consult this entry to see the override rationale.
- (c) The C47/C48/C49 rows in `notebooks/paper_companion_results.csv` continue to show `status=L11` because the builder is data-driven (it doesn't read the manuscript line text); the L11 flag is informational not regression. A future refactor of `_build_paper_companion.py` could either fix the C47-C49 check logic to look at the fetal-death parquet rather than expect a hardcoded comparison, or update the synthesis-row status to reflect the Task 5 override. Not done in Task 5 to keep scope tight.

---

## 2026-05-11T19:26:28Z — task4_paper_companion — Re-defer Section B 2017 race-stratified NVSR validation (originally Task 2 → Task 4 absorption)

**Choice:** Re-defer the Section B 2017 race-stratified NVSR cell-level validation that §15 Task 4 (current state at `89ddc77`) names as an absorption from Task 2. Task 4 produces no race-stratified 2017 NVSR cells. The absorption becomes a separate small future task with explicit NVSR-2017 fetal-mortality PDF input.

**Alternatives considered:**
1. **Absorb Section B into Task 4 as §15 currently directs.** Would require: (a) locating the 2017-vintage NVSR fetal-mortality report PDF (likely NVSR 67-?); (b) transcribing 4 race-stratified rows into `fetal_death/external_validation_targets.csv`; (c) adding a verification cell to either `joint_use_demo.ipynb` or `paper_companion.ipynb` that reproduces each cell against the parquet. Cost: one short session if PDF is at hand; L9 risk on table/page citation.
2. **Re-defer with explicit reasoning (chosen).** The original Task 2 deferral cited the same L9 risk. The manuscript itself makes no race-stratified-2017 NVSR claim (line 94's validation claims are aggregate-level), so `paper_companion.ipynb`'s "reproduce every numeric claim in the manuscript" scope is complete without it.
3. **Hybrid: defer the NVSR validation but add a structural sanity check in the notebook** (e.g., assert race-stratified counts sum to the unstratified 2017 = 22,827 from external_validation_targets.csv). Task 2's notebook already does this cross-check (Section B's CSV-vs-direct-natality-recompute consistency check); duplicating it in `paper_companion.ipynb` would be redundant.

**Reason:** Convention 3 second bullet directs the PRE-FLIGHT to surface divergence between §15 spec and the task's available source-of-truth state, and to resolve at the cheap-check moment rather than silently proceeding. `fetal_death/external_validation_targets.csv` ships NO 2017 race-stratified targets (verified at PRE-FLIGHT by metric enumeration: 26 distinct metrics, none race-keyed). The L9 cheap-check therefore concludes that absorbing Section B would require fresh PDF transcription with the same risk profile that motivated Task 2's deferral. Re-deferring keeps Task 4 focused on its primary scope (reproduce manuscript numeric claims, which does not require race-stratified-2017 NVSR cells) and isolates the PDF-transcription work into a separate task where the L9 cheap-check can be done explicitly with the PDF in hand.

**Source:** `PRE_FLIGHT_LOG.md` 2026-05-11T19:15:00Z (Field-value snapshot, "Plan assumption amended at PRE-FLIGHT" section, item 1). `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` (Forward-looking HALT 3).

**Verifiable by:**
- `grep -i "race\|maternal_race" fetal_death/external_validation_targets.csv` returns zero hits (no race-stratified targets pre-encoded).
- Task 4's `paper_companion.ipynb` synthesis CSV contains no rows whose `claim` mentions "2017 race"; the 50 claim tags cover only manuscript-stated numeric claims.
- The manuscript's line 94 NVSR-validation claims are aggregate-level (183/183, 33/35+2, 29/29 counts + 26/26 rates); none are race-stratified-2017.

**Reversible:** yes — adding the absorption is additive (new rows in `external_validation_targets.csv` + new notebook cells). The original Task 2 deferral and this re-deferral can both be reversed in a single future session if the PDF is located.

**Residual risks:**
- (a) A reader of `NEXT_STEPS.md` §15 Task 4 may expect the absorption to be present in `paper_companion.ipynb` and be surprised by its absence. Mitigation: the receipt's Forward-looking HALT 3 and Self-check item 6 both flag this; the notebook's intro markdown cell explicitly names the deferral as out-of-scope.
- (b) The manuscript might later be edited (Task 5) to ADD a race-stratified-2017 validation claim, at which point Task 4's "reproduce every numeric claim" status would become stale. Mitigation: receipt Forward-looking HALT 5 says any future edit to `paper/draft_v2_hmd_styled.md` should re-run `python notebooks/_build_paper_companion.py` to surface new claims; the CSV `notebooks/paper_companion_results.csv` is the bit-stable check.
- (c) §15 Task 4's description currently names the absorption as in-scope. A `[plan-update]` could reword §15 Task 4 to mention the re-deferral; not done as part of Task 4 itself to avoid scope creep (similar to Task 2's stale-§15-wording handling).

---

## 2026-05-11T18:06:12Z — task1_joint_use_denominators — Aliasing-helper vs source-schema-rename for cross-product join keys

**Choice:** Reconcile cross-product join-key column-name divergence (`year`↔`data_year`, `restatus`↔`residence_status`, `maternal_race_bridged4`↔`maternal_race_bridged`, `maternal_hispanic_origin`↔`hispanic_origin`) via a read-time aliasing helper at `shared/helpers/canonical_join_keys.py`. The natality v2.7.0 Zenodo deposit's shipped schema is NOT mutated; the helper renames at the joint-use code boundary. Output `fetal_death/stratified_denominators.csv` uses the canonical (fetal_death-style) names.

**Alternatives considered:**
1. **Rename columns in the natality schema** (bump to v2.8 with `year` → `data_year`, etc.) and re-derive the parquet. Cleaner long-term, but: (a) requires re-running 183 NVSR validation targets; (b) breaks downstream user code that imports natality by its current names (e.g., `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the user's Desktop); (c) requires a new Zenodo deposit (v2.7.0 stays immutable at its DOI); (d) needs a coordinated bump of `paper/draft_v2_hmd_styled.md` references.
2. **Use the aliasing helper as a stopgap, keep both shipped schemas as-is** (chosen). Pros: ships the joint-use convenience layer today; preserves Zenodo deposit immutability; no breaking change to natality users; isolates the cross-product reconciliation in one auditable place. Cons: future joint-use code must import the helper; the docs must document the divergence (now done in `docs/JOINT_USE_GUIDE.md`).
3. **Build Task 1 against natality-native names; ship the output with fetal_death-style names; defer documentation/helper to later**. Functionally similar to choice 2 but loses the unified-namespace clarity at the helper boundary — joint-use code would each need to know the rename rules locally.

**Reason:** Task 1's purpose is to enable the manuscript's "designed for joint use" claim by producing a stratified denominator file. Choice 1 is the long-term right answer but is a multi-session task with a meaningful breaking-change surface. Choice 2 ships the deliverable today and isolates the cross-product reconciliation behind a single helper, keeping the breaking-change decision for natality v2.8 (or v3.0) as an independent future task. The Forward-looking HALTs in the Task 1 receipt explicitly propose this rename as a §11 plan-update candidate.

**Source:** PRE_FLIGHT_LOG.md 2026-05-11T17:50:48Z (Field-value snapshot of cross-product schema divergence). `shared/helpers/canonical_join_keys.py` (the helper); `docs/JOINT_USE_GUIDE.md` (user-facing docs explaining the choice and the namespace).

**Verifiable by:**
- `python -c "from shared.helpers.canonical_join_keys import NATALITY_TO_CANONICAL; print(NATALITY_TO_CANONICAL)"` should print exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}`.
- `shasum -a 256 fetal_death/stratified_denominators.csv` should produce `6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` as long as natality v2.7.0 is the upstream input.
- Per-year sums in `stratified_denominators.csv` should match `external_validation_v1_comparison.csv` `resident_births` for all 29 years in 1992–2002 + 2005–2022.

**Reversible:** yes — `git reset --hard task1-pre-do` reverts the helper and the convenience file; the natality v2.7.0 deposit was never touched.

**Residual risks (Self-check feed from RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md):**
- (a) The 1992–2002 era's `maternal_race_bridged4` in natality uses "approximate_pre2003" crosswalk per natality schema notes; fetal-death uses a different `harmonize.py` recode. Unverified whether they produce identical 4-category outputs on the same source MRACE codes. Joint stratified-by-race rates for 1992–2002 should be cross-checked as a Task 2 PRE-FLIGHT smoke.
- (b) Hispanic code 9 (Unknown) is preserved as a stratum, not dropped. JOINT_USE_GUIDE.md flags this but does not enforce; downstream code that misaggregates would silently bias rates.
- (c) The full natality `natality_v2_harmonized_derived.parquet` is not listed in any shipped PROVENANCE.md (only the residents-only convenience parquet is). Upstream documentation gap. Locally computed sha=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` is recorded in the receipt and the build script's `--natality-parquet` arg requires the user to provide the path explicitly.

---

## 2026-05-11T17:30:00Z — task6_linked_validation_reconcile — Canonical framing for V3 linked external-target validation count

**Choice:** Adopt "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance" as the canonical framing across the repo, matching the manuscript drafts and monorepo top-level README. Updated `natality/README.md` (lines 19, 27, 146), `natality/docs/ABOUT_THIS_RELEASE.md` (line 80), `natality/docs/COMPARABILITY.md` (line 367), `natality/docs/VALIDATION.md` (line 206), `paper/README.md` (line 18), `NEXT_STEPS.md` (§14 Table 1 line 440, §17 checklist line 791) to match.

**Alternatives considered:**
1. Keep "35/35 pass" as the headline everywhere and treat the 2-cell differences as a tolerance-aware caveat only in detailed validation tables. Cleaner headline; loses precision.
2. Adopt "33/35 byte-exact + 2 differ by 1" as the headline everywhere. More informative; honest about what "pass" means at the byte level. (Chosen.)
3. Carry both framings in parallel ("35/35 pass under documented tolerance; 33/35 byte-exact"). Most explicit; verbose.

**Reason:** The authoritative source `natality/output/validation/external_validation_v3_linked_comparison.md` shows 35 PASS / 0 FAIL / 0 MISSING under tolerance, AND shows 33 rows at Diff=0 with 2 rows (both 2015) at Diff=1. Both framings are factually correct, but they describe different metrics. The manuscript drafts already use option 2 (33/35 byte-exact + 2 cells differ by 1), as does the monorepo top-level `README.md`. The natality subproject's README and three of its docs were the outliers using only the headline "35/35 pass" framing. Option 2 is more honest about what the validation "pass" status means at the byte level, and aligning the natality subproject docs to it removes the cross-doc inconsistency the prior STATUS section flagged as Open Question #3.

**Source:**
- `natality/output/validation/external_validation_v3_linked_comparison.md` (authoritative validation comparison; 2015 rows `unweighted_infant_deaths` 23326→23327 and `postneonatal_deaths` 7772→7773 each show Diff=1, marked `pass`).
- `paper/draft_v2_hmd_styled.md` line 94 (manuscript canonical framing, retained).
- `README.md` (monorepo top-level) line 17 (already canonical, retained).

**Verifiable by:** `git ls-files | xargs grep -n -E '35/35|33/35' 2>/dev/null` should now show consistent canonical framing across all post-edit shipping docs; residual "35/35" mentions should only appear in (a) historical state-file entries (PRE_FLIGHT_LOG, STATUS open questions), (b) NEXT_STEPS.md §15 Task 6 spec which describes the problem being resolved.

**Reversible:** yes — `git reset --hard task6-pre-do` rolls back the seven file edits; the manuscript drafts and monorepo README would remain canonical (they were unchanged in this task).

**Residual risk (Self-check feed):**
- (a) `natality/README.md` line 146 mechanism-attribution phrase ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism-attribution phrase ("LATEREC edge cases") differ from the manuscript canonical mechanism phrase ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are intentionally preserved because the task scope is HEADLINE-count reconciliation, not mechanism-attribution reconciliation. Each may describe the same underlying NCHS phenomenon under different terminology (LATEREC = late-filed records that lacked record_weight at file-build time; "survivor" likely refers to the surviving-cohort linkage). Disambiguating these three framings into one is a downstream task if pursued.
- (b) `natality/README.md` line 146 retains "2014/2015" for the underlying survivor rows although both validation diffs manifest in 2015 cells. The two need not contradict (e.g., a 2014-birth-cohort record manifesting in 2015 linked-file death counts), so the original wording is preserved without speculation.
- (c) Headline framing carries forward through future LinkedFile re-validation: if a later release re-derives different per-year counts that change the byte-exact vs differ-by-1 split, every file touched in this task needs a paired update.

---

## 2026-05-09T00:00:00Z — bootstrap — Operating protocol adopted from NHANES Assay-Bridging template

**Choice:** Adopt the NHANES Assay-Bridging Harmonization Project's `EXECUTION_PROTOCOL.md` discipline (five-phase task structure, append-only state files, mistake-class matrix, halt conditions, anti-patterns, self-check) for HVS work. Folded into `NEXT_STEPS.md` §1-§13.

**Alternatives:** (a) lighter-weight ad-hoc protocol with just task list and review hook; (b) full NHANES protocol replicated verbatim; (c) hybrid (this choice).

**Reason:** HVS data is already shipped and validated, so the heaviest NHANES patterns (multi-LLM dual-key transcription, mutation fixtures, NIST SRM checks) don't apply directly. But the patterns that matter most for any harmonization with public-validation-target gold standards — five-phase structure, halt conditions, mistake-class prevention, append-only state — apply equally to HVS. Adopting them now (before Tasks 1-10 ship) means the discipline guards the manuscript-supporting work, not just future maintenance.

**Source:** `/Users/yoelplutchok/Desktop/nhanes-assay-bridging/EXECUTION_PROTOCOL.md` (read 2026-05-09); `NEXT_STEPS.md` §1-§13 (this commit).

**Verifiable by:** A future LLM session, kicked off via `KICKOFF.md`, should be unable to do work without first running the §1 session-start sequence and waiting for human confirmation. The discipline is enforced by the prompt, not by code.

**Reversible:** yes — if the protocol proves too heavy for the actual work pattern, simplify by §11 plan-update process.
