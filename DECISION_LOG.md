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
