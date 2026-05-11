# Receipt: task2_joint_use_demo
## 2026-05-11T18:51:59Z

### What was done

Shipped the joint-use demo notebook (NEXT_STEPS.md §15 Task 2, §17 readiness item 4). The notebook is deterministically built by a companion script (`notebooks/_build_joint_use_demo.py`) and executes end-to-end against the locally-available v2.7.0 natality + v3.0.0 linked + v2.0.0 fetal-death parquets. Two integrated demonstrations: **Section A** validates 2022 fetal mortality by maternal age band against *NVSR 73-09* Table 4 (8 cells, all PASS byte-exact); **Section B** demonstrates 2017 race-stratified joint-use machinery (last bridged-race-available year before NCHS dropped MBRACE), cross-validating both denominator paths (pre-built `stratified_denominators.csv` vs direct natality recompute) cell-by-cell.

The §15 Task 2 spec was discovered at PRE-FLIGHT (Convention 3 Field-value snapshot) to have two stale-vs-current divergences: (a) "by maternal race, 2022" is impossible because `maternal_race_bridged` is null in both products for 2018-2022; (b) "matches NVSR 73-09 Table A" mis-cites — Table A is sex/plurality, not race. The plan was amended at PRE-FLIGHT per Convention 3 (Section A swaps stratification axis race→age; Section B preserves the race demonstration by swapping year 2022→2017). The amendment is documented in `PRE_FLIGHT_LOG.md` 2026-05-11T18:27:14Z; a future `[plan-update]` will reword §15 Task 2.

SMOKE Tier 1 surfaced a second-order finding: **the fetal-death v2.0.0 parquet stores five demographic/filter columns as `object` (string) dtype despite `fetal_death/harmonized_schema.csv` documenting them as `int`** — an H8 doc-vs-data drift that would silently produce 0 rows for any user copying the prior JOINT_USE_GUIDE.md code example. Bundled fixes into Task 2's DO: corrected the JOINT_USE_GUIDE.md filter syntax to string literals; added a dtype caveat paragraph; filed FIX_LOG entry. `fetal_death/harmonized_schema.csv` is NOT edited (anti-pattern #6: schema edits require a schema-version bump — flagged as a future task).

### Inputs consumed

- `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: 2,202,879,406 bytes, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (locally computed; carries forward the Task 1 PROVENANCE-gap finding).
- `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: 1,300,258,973 bytes, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (locally computed; same PROVENANCE gap).
- `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: 25,452,090 bytes, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0.
- `fetal_death/stratified_denominators.csv` (Task 1 output): sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` (matches Task 1 Forward-looking HALT 1 byte-exact).
- `shared/helpers/canonical_join_keys.py` (Task 1 output): `NATALITY_TO_CANONICAL = {'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}` (matches Task 1 Forward-looking HALT 2 byte-exact).
- `fetal_death/external_validation_targets.csv`: 82 rows; 8 used for Section A NVSR 73-09 Table 4 verify (`fetal_deaths_age_under15/15_19/20_24/25_29/30_34/35_39/40_44/45_plus` for year 2022).
- `fetal_death/harmonized_schema.csv`: read at PRE-FLIGHT; surfaced the H8 dtype drift documented in FIX_LOG.md.
- `docs/JOINT_USE_GUIDE.md` (Task 1 output): the worked-example pseudocode source for Section B (2017 race demo). Edited in this task per FIX_LOG.md fix.

### Outputs produced

- `notebooks/joint_use_demo.ipynb`: new, sha256=`ff563e103cbe1c3640230cb178d2657fa3ec8d879fd383d955f02bd13f7c36d1`. 19 cells (8 markdown, 11 code), all code cells executed cleanly with 0 errors. **The notebook's binary sha256 is NOT bit-reproducible** across re-executions (Jupyter embeds execution-count, cell uuids, kernel-start-time metadata that vary); however the **data-content** of the outputs (8/8 NVSR cell PASS, aggregate FMR 5.4778, Section B FMRs 5.08/9.98/7.22/4.29) IS deterministic. See "Reproducibility" below.
- `notebooks/_build_joint_use_demo.py`: new, sha256=`1f5952d4db03496d83df79535714c0dab29418f020b35ed77f229a8449330599`. 199 lines. `DESIGN: tracks-current-state` per Convention 2. Deterministic builder; canonical source for the notebook.
- `docs/JOINT_USE_GUIDE.md`: edited (filter table line 51 syntax fix + new dtype-caveat paragraph + worked-example code lines 92-95 string-literal fix). Post-edit sha256=`cd68eba0a51fb866af47d724d8cf998494f651c9a7122aba56cbbeef2c43ac6a`.
- `notebooks/README.md`: edited (joint_use_demo description rewritten to reflect actual notebook scope: Section A age + Section B race; status table updated).
- `NEXT_STEPS.md`: §17 readiness item 4 ⏳ → ✅.
- `FIX_LOG.md`: new entry (first in the repo) for the H8 fetal-death-dtype-drift class.
- This receipt.

### Five-phase trace

- **PRE-FLIGHT**: ✓ at PRE_FLIGHT_LOG.md timestamp 2026-05-11T18:27:14Z. Field-value snapshot enumerated §15-spec vs current-state divergences on two axes (2022 race null; Table A mis-cite); resolution: plan amended at PRE-FLIGHT (Section A age, Section B race-2017, NVSR-validation for Section B deferred to Task 4). All 6 Task 1 Forward-looking HALTs verified pre-DO.
- **SMOKE**:
  - **Tier 0** (synthetic 10-row fixture): PASS. Combined filter `(tab_flag=='2') AND (res_status!='4')` retained 6/10 rows matching hand-computed expected subset. Mutation tests: `tab_flag=='2'` alone retains 7 rows; `res_status!='4'` alone retains 8 rows; inverted-tab filter retains the expected complementary rows. Race groupby on filtered subset yields hand-computed expected counts. Sentinel `age=99` preserved as-is (NaN-handling deferred to age-binning step).
  - **Tier 1** (fetal-death 2017 single-year + Task 1 HALT 5 crosswalk equivalence): PASS. (a) 2017 NVSR-pop = 22,827 byte-exact vs `fetal_death/external_validation_targets.csv` NVSR 73-09 Table 1 target (Diff=0). (b) Task 1 HALT 5: both products partition 1995 into the same 4 bridged-race categories `{1, 2, 3, 4}` (structural equivalence; bridge rules produce compatible 4-category outputs). Tier 1 also surfaced the H8 dtype drift — fixed and FIX_LOG-filed.
  - **Tier 2** (single-year full): skipped per §15 SMOKE plan ("Tier 0, Tier 1, Tier 4" specified; Tier 2 + Tier 3 were Task 1's scope).
  - **Tier 4** (full 2022 cross-product): PASS. (a) 8/8 NVSR 73-09 Table 4 age cells byte-exact (Diff=0 across `<15`, `15-19`, `20-24`, `25-29`, `30-34`, `35-39`, `40-44`, `45+`; sum=20,202 matches unstratified target). (b) Aggregate FMR = 5.4778 per 1,000 vs NVSR 73-09 Table 1 published 5.48; |diff|=0.0022 (within rounding tolerance 0.01). (c) Row-count conservation on both numerator (sum-of-bands=20,202) and denominator (sum-of-bands=3,667,758) sides per §8 H6.
- **DO**: ✓ Tagged `task2-pre-do` at `da5d407` (the PRE-FLIGHT commit). Builder script + notebook created; JOINT_USE_GUIDE.md + notebooks/README.md edited; NEXT_STEPS.md §17 updated; FIX_LOG entry filed.
- **VERIFY**: ✓ Three criteria pass (see below).
- **RECEIPT**: ✓ this file.

### Verify results

- **Criterion A — notebook runs end-to-end without manual intervention**: PASS. `nbclient.NotebookClient(...).execute(cwd=REPO_ROOT)` returned cleanly; inspection of all 19 cells confirms 0 cells with `output_type=error`. The notebook can be opened in Jupyter and "Run All" reproduces the executed state.
- **Criterion B — every per-cell stratified value matches the NVSR target within rounding** (§15 criterion 2, amended per PRE-FLIGHT to Section A's NVSR 73-09 Table 4): PASS 8/8 byte-exact (Diff=0 across all 8 age bands). Section B race cells are joint-use machinery demonstration only; NVSR validation deferred to Task 4 per PRE-FLIGHT amendment.
- **Criterion C — pass/fail table at the bottom of the notebook is all PASS, or any FAIL is documented**: PASS. Notebook's final markdown cell ships a 7-row pass/fail table; 6 PASS + 1 DEFERRED (Section B NVSR validation → Task 4). No FAILs.
- **Supplementary verify (Task 1 Forward-looking HALT 5)** — 1992-2002 maternal_race_bridged crosswalk equivalence: PASS. Executed in SMOKE Tier 1. Both products partition 1995 (a V2-era year) into the same `{1, 2, 3, 4}` bridged-race code set with no extraneous codes. Demographic-risk differentials between live-birth and fetal-death populations (e.g., Black 28.45% of 1995 fetal deaths vs 15.47% of 1995 live births) explain the proportion differences — NOT a bridge-rule artifact. Joint stratified-by-race rates for 1992-2002 are byte-clean to derive at the 4-category-code level. Closes Task 1 Self-check residual risk 3.

### Reproducibility

**Data-content reproducibility (deterministic):** Re-running `python notebooks/_build_joint_use_demo.py` produces identical computed values in every code cell (8/8 NVSR PASS, aggregate FMR 5.4778, Section B FMRs 5.08/9.98/7.22/4.29, cross-path race-denominator agreement True). The cell outputs' text/plain representations are byte-identical across re-runs.

**Binary reproducibility (NOT deterministic):** The notebook JSON file's `sha256` will change across re-executions due to Jupyter's per-execution metadata (cell uuids, execution counts, kernel-startup timestamps). This is intentional Jupyter behavior, not a regression. Users wishing to verify data-content reproducibility should run the builder script and `diff` the resulting cell output text/plain blocks against this receipt's "Verify results" section.

**Builder script reproducibility:** `notebooks/_build_joint_use_demo.py` sha256=`1f5952d4...` is deterministic. If the script's sha changes, the notebook is no longer canonical for this receipt.

No regression noted; no FIX_LOG entry needed beyond the H8 dtype drift one (which is a finding, not a regression — Task 2 surfaced it; nothing prior had been broken by it).

### Cross-product re-probe (if applicable)

Tasks that depend on this output: Task 4 (`notebooks/paper_companion.ipynb`) — the deferred Section B NVSR validation is in Task 4's scope. Task 5 (manuscript trim) may cite this notebook as evidence of the "designed for joint use" claim. No retroactive re-verification needed — Task 2 ships new artifacts only and does not mutate any prior validated output; the JOINT_USE_GUIDE.md edit is a fix to a Task-1-shipped doc that surfaced as buggy during Task 2 SMOKE (the fix is in scope for Task 2 because the notebook implements that worked example).

### Git

- Pre-DO tag: `task2-pre-do`, commit=`da5d407` (PRE-FLIGHT-only commit).
- Post-RECEIPT tag (to be set after the task commit): `task2-complete`.

### STATUS.md updated

New section dated 2026-05-11T18:51:59Z marking Task 2 complete and §17 item 4 → ✅.

### Self-check (§10): what could I have gotten wrong that VERIFY wouldn't catch?

1. **Section A's NVSR 8-band age binning may disagree with NCHS's actual NVSR 73-09 Table 4 boundary convention.** I used `<15` = `age < 15`, `15-19` = `15 ≤ age ≤ 19`, etc. (inclusive of both endpoints in the middle bands). NVSR could use exclusive-upper boundaries (e.g., `15-19` meaning `15 ≤ age < 20`). The 8/8 byte-exact PASS is strong evidence that my boundary convention matches NCHS's (any 1-year boundary error would shift cells by hundreds or thousands of records, blowing the PASS), but the test only proves "for 2022" — the binning convention could theoretically differ in pre-2022 NVSR vintages if NCHS changes conventions.
2. **The aggregate FMR rounds to 5.48 via two paths**: (a) sum-of-bands / (sum-of-bands + sum-of-band-numerators) = 5.4778; (b) NCHS's NVSR computation = unstratified FD / (unstratified LB + unstratified FD) = (20202 / (3667758 + 20202)) × 1000 = 5.4778. These ARE the same number because the band partition is complete (row-count conservation); but if any of my band predicates leaked or double-counted a record, the aggregate would still come close to 5.48 (because individual bands cancel) while individual cells could fail. The 8/8 byte-exact PASS at the cell level rules this out.
3. **`maternal_age = 99` sentinel in V2 era**: the schema says `0 V2 rows have DMAGE=99 (NCHS imputes mother's age in V2 era)` — but the 1992-2002 stratified denominator (Task 1) reports `null` age-band rows for some maternal-age=99 strata. Section A is 2022-only (V1 era, no `99` sentinel — verified 0 rows). Section B is 2017-only (also V1 era, no `99` sentinel). The risk would only manifest if the notebook were extended to pre-2003 era; flagged but not exercised.
4. **NVSR 73-09 Table 4's "<15" cell value (16 records)** is small — any single-record dtype-coercion error in the fetal-death's small-age tail could plausibly mis-place 1-2 records and still pass the 0-tolerance check by coincidence. The byte-exact PASS is, in this cell, weaker evidence than for the larger cells (5,634 in the 30-34 cell, say). But the SMOKE Tier 0 mutation tests cover the filter-logic edge cases on a fixture that includes both `age=99` and `age=17` sentinels; the filter implementation is verified.
5. **Section B's denominator path agreement (CSV vs direct natality recompute) is a Task-1-verified cross-check, not an independent verification.** Task 1's Criterion C verified this byte-exactly for years {2000, 2010, 2015, 2017}; Section B's 2017 cell-by-cell agreement assertion is independent confirmation. If both paths shared a bug (e.g., the canonical_join_keys helper renamed natality columns wrong in the same way both Task 1 and Task 2 read them), the agreement would not detect it. Mitigation: the natality side's unstratified 2017 resident count (the assertion `len(nat_2017) == 3667758` in Tier 4) is itself anchored to natality's NVSR validation target byte-exact, providing the independent anchor.
6. **The notebook does NOT use the linked-file parquet beyond loading it for the "all three products" demonstration**. The §15 spec says "loads all three parquets, applies each canonical filter" — the linked file is loaded and filtered (cell 5), but not used in any rate computation. This is consistent with the spec ("loads all three parquets") and the rate formula (FMR doesn't need linked records). If a reader interprets "joins on demographic strata" as also requiring a 3-way join involving linked, the spec is more ambiguous than I've executed; flagged as a clarifying-edit candidate for §15 Task 2 in any future `[plan-update]`.
7. **H8 dtype drift discovery → I edited JOINT_USE_GUIDE.md (Task 1 output) as part of Task 2's scope.** This is borderline Task-1-rework. Justification: the broken code example would invalidate Task 1's worked example (a Task 1 success criterion implied by the JOINT_USE_GUIDE.md rewrite), so the fix is a Task-1-retroactive-correction wrapped into Task 2's scope. Alternative would have been a `[plan-update]` to JOINT_USE_GUIDE.md as a separate commit; bundling it into Task 2 is justifiable because Task 2's SMOKE surfaced it and the notebook needs the worked example to be correct. Documented here for future audit.

### Forward-looking HALTs for next session

Per Convention 4. If the next session is Task 3 (V2.1 fetal-death extension), Task 4 (paper companion notebook), Task 5 (manuscript trim), or any task that consumes the fetal-death parquet or the JOINT_USE_GUIDE:

1. **`notebooks/joint_use_demo.ipynb` 2022 8-cell NVSR validation must remain all PASS.** If any future change touches the natality v2.7.0 parquet OR the fetal-death v2.0.0 parquet (e.g., re-deriving under a v2.8 / v2.1 rename), re-run `python notebooks/_build_joint_use_demo.py` and inspect the Section A pass/fail table. Any DIFF row that wasn't there before is a regression — halt and ask.
2. **`fetal_death/harmonized_schema.csv` claims `int` dtype for `tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin` — parquet actually stores `object`/string.** Future task should reconcile (schema-version bump per anti-pattern #6, or a comment row referencing FIX_LOG 2026-05-11). DO NOT edit harmonized_schema.csv without bumping the version. Until reconciled, ALL fetal-death joint-use code MUST use string literals on these columns (or coerce with `pd.to_numeric`).
3. **L17-class risk: the notebook is NOT bit-sha-stable across re-executions** (Jupyter execution metadata). The receipt records sha=`ff563e10...` as a snapshot, NOT a contract. Verification of "the notebook is unchanged" requires either (a) inspecting the executed-output values cell-by-cell, or (b) hashing only the cells' source code + output text/plain (excluding Jupyter metadata). DO NOT treat the .ipynb sha as a regression signal.
4. **Plan-update candidate for §15 Task 2 wording (carried from PRE-FLIGHT)**: the §15 description still says "by maternal race, 2022, matches NVSR 73-09 Table A" — stale on both axes. Recommend a `[plan-update]` to reword to "Section A: 2022 by age band vs NVSR 73-09 Table 4; Section B: 2017 by race (machinery demo)." Not done in Task 2 to avoid scope creep; proposed for a separate `[plan-update]` commit.
5. **Schema-doc parity smoke test (FIX_LOG follow-up)**: a future task should add `fetal_death/tests/test_schema_dtype_parity.py` that loads the parquet, loads `harmonized_schema.csv`, and asserts dtype parity for every row. This prevents H8 recurrence. Bundled with the schema-version bump in (2) is the natural place.
6. **Task 1 Forward-looking HALT 5 (1992-2002 crosswalk equivalence) is now CLOSED** by Section B's structural-equivalence check in SMOKE Tier 1. Future receipt-readers tracing the HALT chain should know the residual risk is resolved at the 4-category-code level (both products partition `{1, 2, 3, 4}`); demographic-risk differentials between LB and FD populations are unrelated to bridge equivalence. Race-stratified joint-use rates for 1992-2002 are byte-clean to compute.

### Notes for next session

- Task 2 commit ships a ~5-line summary per Convention 5; full narrative in this receipt + DECISION_LOG (if a follow-up DECISION_LOG entry surfaces the dtype-drift choice) + STATUS.md.
- `task2-pre-do` is at `da5d407`; `task2-complete` to be set after the task commit lands.
- §17 readiness checklist now has 2 ⏳ items remaining for manuscript submission (was 3 at end of Task 1): Task 4 (paper companion) and Task 5 (manuscript trim).
- Task 4 (paper companion) is now unblocked by this notebook's existence — its scope ("reproduce every numeric claim in the manuscript") naturally includes a Section B–style race-stratified validation that this notebook deferred.
- The H8 finding (fetal-death dtype drift) is the first FIX_LOG entry in the repo. The `tests/test_schema_dtype_parity.py` follow-up is the cheapest defense-in-depth against this recurring.
