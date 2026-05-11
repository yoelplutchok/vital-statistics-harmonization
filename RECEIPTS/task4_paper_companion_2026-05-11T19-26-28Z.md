# Receipt: task4_paper_companion
## 2026-05-11T19:26:28Z

### What was done

Shipped `notebooks/paper_companion.ipynb` (NEXT_STEPS.md §15 Task 4, §17 readiness item 7). The notebook is built deterministically by `notebooks/_build_paper_companion.py` and walks through 55 numeric claims enumerated in `paper/draft_v2_hmd_styled.md` (cataloged C01–C55 in `PRE_FLIGHT_LOG.md` 2026-05-11T19:15:00Z Field-value snapshot). Each claim is mapped to a manuscript line number and a source-of-truth artifact (parquet, schema CSV, validation CSV, or release-notes document); each is recomputed where the artifact supports it, and a pass/fail synthesis is emitted to `notebooks/paper_companion_results.csv` (and printed at the bottom of the notebook).

The synthesis: **25 PASS, 20 CITE-ONLY (citations / benchmarks not parquet-derivable), 4 L11 (wording-precision findings), 1 DIFF.** The four L11 and one DIFF are real manuscript-side precision-edit candidates for Task 5 (manuscript trim):

- **C04 (line 7) DIFF**: manuscript says "approximately 3.5 million live births ... each year"; natality 1990–2024 mean is 3,966,275 (range 3,605,081–4,324,008). Both readings are defensible (3.5M is the multi-decade rough historical context; 3.97M is the 1990–2024 mean), but the value is below the actual mean over the resource's coverage period.
- **C29 (line 23) wording**: "two within fetal death" boundary count is the era-to-era transition count (Table 1 ships three fetal-death eras → two transitions). Both readings consistent IFF reader does arithmetic; an explicit "three eras with two era-to-era transitions" wording would be clearer.
- **C33 (line 60) L11**: "Three fetal-death columns are tagged within_era" is scope-restrictive (the three irreducibly-incompatible-clinical-concept columns); the schema actually tags 24 columns within_era. Suggested edit: "Three of the within_era fetal-death columns carry irreducibly incompatible clinical concepts ..."
- **C47, C48, C49 (line 104) L11**: italicized `maternal_education`, `paternal_age_combined`, `maternal_education_unrevised` are raw NCHS field names (MEDUC, FAGECOMB, MEDUC_REC), not harmonized column names — italics imply harmonized columns but the referent is raw. Clarify the wording.

§15 Task 4's secondary scope ("absorbs Section B NVSR cell-level validation deferred from Task 2") was re-deferred at PRE-FLIGHT per Convention 3 second bullet: the L9 cheap-check confirmed `fetal_death/external_validation_targets.csv` ships no 2017 race-stratified targets, so the absorption would require fresh PDF transcription with the same L9 risk that motivated Task 2's original deferral. The Section B absorption becomes a separate small future task with explicit NVSR-2017 PDF input.

### Inputs consumed

- `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (unchanged from Task 1/2; carries forward the PROVENANCE-gap finding).
- `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (unchanged).
- `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` (matches `fetal_death/PROVENANCE.md` v2.0.0).
- `paper/draft_v2_hmd_styled.md`: sha256=`5e86c923d581936ce517740fadb6b247bbac4f6297a1cd517ed36b9f3c3967fb` (read-only; not edited by this task).
- `fetal_death/harmonized_schema.csv`: sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab`.
- `natality/metadata/harmonized_schema.csv`: sha256=`2e95488fd910f60cbf5965bd9f0d3503f59111e38180c20e4e51e29af2983577`.
- `natality/output/validation/external_validation_v1_comparison.csv`: sha256=`c82a412ca16dc0f8b3c8a6a6b842b8a4cac43c19015a388bba1f4608f123e68a`.
- `natality/output/validation/external_validation_v3_linked_comparison.csv`: sha256=`868dc5c99e7c7e7bc3cd7674dee6a2abf7062af15ea01e83b4bd14d23763dcbe`.
- `fetal_death/validation_results.csv`: sha256=`8041586dc99f450faf4a3b91505a98652410a31d6caa5da14dfa39c75da7de0e`.
- `fetal_death/external_validation_targets.csv`: sha256=`0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f`.
- `fetal_death/ABOUT_THIS_RELEASE.md`: read-only; supplies the canonical 5-normalizations Summary line and the 98,500-byte-comparison phrasing.
- `fetal_death/validation_tracking.csv`: read-only; supplies the per-year `external_validation_done=yes` flag.
- `fetal_death/live_births_by_year.csv`: read-only; supplies the NVSR 57-08 / 73-09 source attribution for C37.

### Outputs produced

- `notebooks/_build_paper_companion.py`: new, sha256=`055c3aff0b12ec0bef029aa2da761e36e89a8134d9a4fa4918a11283e2517abe`. ~370 lines. `DESIGN: tracks-current-state` per Convention 2. Deterministic builder; canonical source for the notebook.
- `notebooks/paper_companion.ipynb`: new, sha256=`dde922d17f961adde86f7c026cc425f1f8598c3c294830cb61940fbecba7deba`. 38 cells (15 markdown, 23 code), all code cells executed cleanly with 0 errors. **Per L17 / Task 2 HALT 3 the binary `.ipynb` sha is NOT bit-reproducible across re-executions** (Jupyter metadata); data-content reproducibility is via re-running the builder.
- `notebooks/paper_companion_results.csv`: new, sha256=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce`. 50 unique-tag rows × 7 columns. The pass/fail synthesis output; deterministic byte-by-byte across re-runs (verified during DO).
- `notebooks/README.md`: edited (`paper_companion.ipynb` description rewritten with scope; status table updated). Post-edit sha=`1e3878dee0382f347b68e3e9178f910bb49469830da6948691ecc772d248532f`.
- `paper/README.md`: edited (Companion notebook outstanding-work item marked RESOLVED with the four manuscript precision-edit candidates inlined for Task 5 readers). Post-edit sha=`d87a4a4012b20933e75fea16bbe75db480cdb2c2d739ab3659243dec34d9b226`.
- `NEXT_STEPS.md`: §17 readiness item 7 ⏳ → ✅. Post-edit sha=`b2be0f19a1b05df7f9eb2f84a83b0528d103116431e6b59e98c925e63cfafa65`.
- This receipt.
- New STATUS.md section dated 2026-05-11T19:26:28Z (pending at receipt write).
- New DECISION_LOG entry recording the Section B re-deferral choice (pending).

### Five-phase trace

- **PRE-FLIGHT**: ✓ at `PRE_FLIGHT_LOG.md` timestamp 2026-05-11T19:15:00Z. Field-value snapshot enumerated all 55 manuscript numeric claims (C01–C55) with source-of-truth artifacts; three plan amendments resolved at PRE-FLIGHT per Convention 3 (Section B 2017 race-NVSR absorption re-deferred; C29 eras-vs-boundaries framing; C33 line-60 scope-restrictive reading). All six Task 2 Forward-looking HALTs verified pre-DO; the first (joint_use_demo 8-cell NVSR validation) re-verified by re-running Task 2's builder during VERIFY (data-content green; binary sha changed per L17 and was reverted to keep Task 2's artifact unmodified).
- **SMOKE**:
  - **Tier 0/1** (parquet record counts + validation-CSV row counts): PASS. 138,819,655 / 74,943,824 / 1,634,195 byte-exact; 183 / 35 / 29 CSV row counts byte-exact. Total wall-clock < 1 second (`pq.read_metadata`).
  - **Tier 2 / Tier 3 / Tier 4**: not separately staged. Task 4's nature is reproduction-and-comparison rather than incremental scale; the DO phase IS the full-scale execution against all three parquets, and Task 2's existing 8-cell NVSR validation serves as the Tier-4-equivalent cross-product sanity check (re-verified during VERIFY, passed).
- **DO**:
  - Built `_build_paper_companion.py` (~370 lines, 14 section headers + 23 code cells), executed via `nbclient.NotebookClient` against the three parquets in ~3 minutes wall-clock.
  - Two mid-DO author-side bugs discovered and corrected:
    - **C44/C45 detection logic**: initial null-rate check used `.isna()` but `cause_icd10` stores empty STRING `""` not pandas NA. Corrected to `.astype(str).str.strip().eq("")` and re-executed; both now PASS (pre-2014 100% blank; 2018+ ~50% blank).
    - **C34 detection logic**: initial regex `^### B[0-9]+` matched zero headers because B-blocks live in a markdown table, not as section headers. Corrected to parse the explicit `**Summary**: 5 V2 value-level normalizations (B1, B2, B3, B4, B6) + 3 comparability relabels` line; now PASS (5 normalizations match manuscript's 5).
    - **C47/C48/C49 interpretation**: initial check loaded the natality parquet with the column names from the manuscript; columns NOT FOUND in the parquet. Re-interpreted as L11 wording-precision (manuscript italicises raw NCHS field names MEDUC / FAGECOMB / MEDUC_REC); recorded as L11 with a precision-edit recommendation, not as a parquet-side error.
  - Tagged `task4-pre-do` at `61090fc` (the PRE-FLIGHT commit). Edits to `notebooks/README.md`, `paper/README.md`, `NEXT_STEPS.md` §17 item 7 done as part of DO.
- **VERIFY**: ✓ three criteria pass (see below).
- **RECEIPT**: ✓ this file.

### Verify results

- **Criterion A — notebook runs end-to-end without manual intervention** (§15): PASS. `nbclient.NotebookClient(...).execute(cwd=REPO_ROOT)` returns cleanly; 23 code cells, 0 with `output_type=error`, every code cell carries an `execution_count`. Re-running `python notebooks/_build_paper_companion.py` regenerates a notebook with identical data-content (the binary sha changes per L17).
- **Criterion B — every cell matches the paper; if not, fix the paper** (§15): PASS-with-findings. 50 unique-tag synthesis rows; 25 PASS (parquet/schema/validation-CSV-derivable claims byte-exact); 20 CITE-ONLY (citations / benchmarks not parquet-derivable — listed in §11 of the notebook); 4 L11 (wording-precision-edit recommendations for Task 5: C29, C33, C47, C48, C49 — all recorded with suggested edits); 1 DIFF (C04 line 7 "approximately 3.5 million live births / year" — actual 1990–2024 mean is 3,966,275). The "fix the paper" half of the criterion is out of scope for Task 4 (manuscript edits are Task 5); Task 4 produces the findings + suggested edits in `paper/README.md` for Task 5 to act on.
- **Criterion C — task 2 Forward-looking HALT 1 regression check** (Task 2 receipt; defense-in-depth): PASS. Re-ran `python notebooks/_build_joint_use_demo.py` during VERIFY; all 8/8 NVSR 73-09 Table 4 cells still byte-exact; aggregate FMR 5.4778 unchanged; binary `.ipynb` sha changed (Jupyter metadata per L17) — reverted to keep Task 2's canonical artifact unmodified. Data-content reproducibility green.

### Reproducibility

**Data-content reproducibility (deterministic):** Re-running `python notebooks/_build_paper_companion.py` produces identical computed values in every code cell. The synthesis CSV `notebooks/paper_companion_results.csv` is byte-identical across re-runs (verified during DO: two consecutive builds produced sha=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` both times).

**Binary `.ipynb` reproducibility (NOT deterministic):** The notebook JSON file's sha changes across re-executions due to Jupyter's per-execution metadata. Same caveat as Task 2 receipt's HALT 3. Use the synthesis CSV (`paper_companion_results.csv`) as the bit-stable artifact; the .ipynb is the user-facing rendered view.

**Builder script reproducibility:** `notebooks/_build_paper_companion.py` sha=`055c3aff...` is deterministic. If the script's sha changes, the notebook is no longer canonical for this receipt.

No regression noted; no FIX_LOG entry needed.

### Cross-product re-probe (if applicable)

Tasks that depend on this output: Task 5 (manuscript trim) consumes the four L11 + one DIFF findings as precision-edit candidates; the recommendations are inlined in `paper/README.md` for the Task 5 author. No retroactive re-verification of prior tasks needed — Task 4 produces new artifacts only and does not mutate any prior validated output.

### Git

- Pre-DO tag: `task4-pre-do`, commit=`61090fc` (the PRE-FLIGHT commit).
- Post-RECEIPT tag (to be set after the task commit): `task4-complete`.

### STATUS.md updated

New section dated 2026-05-11T19:26:28Z marking Task 4 complete and §17 item 7 → ✅ (pending at this receipt write).

### Self-check (§10): what could I have gotten wrong that VERIFY wouldn't catch?

1. **The Field-value snapshot may have missed a manuscript numeric claim.** I enumerated C01–C55 from a section-by-section walk through `draft_v2_hmd_styled.md`, but the manuscript also contains numeric content in footnotes, table cells (Table 1 record-length / certificate-revision values are NOT enumerated as C01–C55; they live under T1 in the snapshot), and references (year ranges in citations). A future audit could check: did I miss any number? Mitigation: §11 of the notebook explicitly groups cite-only / out-of-monorepo claims (20 rows) which include citation year ranges; the Table 1 row-count count (3 era-row predicates) is implicitly verified by C27/C28/C29.
2. **My C04 framing decision** ("approximately 3.5 million" vs 1990–2024 mean of 3.97M) is judgment-laden. If the manuscript's intent at line 7 is "historical multi-decade rough characterization," then 3.5M may be defensible; if the intent is "current 1990–2024 mean," then 3.97M is the correct value. The DIFF flag surfaces this as a Task 5 decision rather than a hard error.
3. **My C29 framing decision** (eras vs boundaries) — I marked all three eras-vs-boundaries rows as PASS-with-note because the arithmetic is consistent under "N eras = N-1 transitions." A stricter reading would mark them DIFF. Task 5 can decide; the note is in the synthesis CSV.
4. **My C47/C48/C49 interpretation** — the manuscript italicises raw NCHS field names but the wording implies harmonized columns. I marked them L11 (wording-precision) rather than DIFF (data-side error). If the manuscript truly intends the raw NCHS field availability claim, then L11 is correct; if the manuscript actually means harmonized columns, then C47–C49 are DIFFs because the harmonized columns are NOT 100% blank in 2007–2013 (they have populated values from non-revised states in that period). The latter scenario is plausible — recommend Task 5 author verify which framing was intended.
5. **C44/C45 detection logic was wrong in the first build** — I used `.isna()` but the parquet uses empty-string sentinel. I caught this within DO and corrected; documented in the DO trace. A future audit might check whether other claims in the synthesis use the same wrong null-detection pattern (e.g., does C46 state-ID claim use the right null check? — it's CITE-ONLY in this notebook, so the question doesn't apply).
6. **The Task 4 scope did not absorb Section B NVSR 2017 race-stratified validation** (per PRE-FLIGHT Convention 3 second bullet). §15 Task 4 description names this absorption; the L9 cheap-check found no pre-encoded targets. If the human disagrees with the re-deferral and wants Section B NVSR-pinned, that's a one-session add-on (input: NVSR-2017 fetal-mortality PDF; output: 4 new race-stratified rows in `external_validation_targets.csv`). Flagged in Forward-looking HALTs.
7. **The "55 enumerated claims" count is one I created at PRE-FLIGHT.** A different reader of the manuscript might enumerate a different set (e.g., counting each row of Table 1 as a separate claim → 11 more rows in the snapshot). The synthesis records 50 unique tags; the 5-missing are tag-collapses on three groups of three for the record-count claims (C01/C16/C53 etc.). If the human wants finer granularity (one row per Table 1 cell), that's an extension of Task 4 not a regression.

### Forward-looking HALTs for next session

Per Convention 4. If the next session is Task 5 (manuscript trim), Task 3 (V2.1 fetal-death), or any other:

1. **Five Task-5 precision-edit candidates from this task** are inlined in `paper/README.md` (resolution of "Companion notebook" outstanding-work item). If Task 5 runs, it should consume these as input. They are: (C04) "approximately 3.5 million" wording; (C29) "two within fetal death" boundary framing; (C33) line-60 "three within_era" scope-restrictive wording; (C47/C48/C49) line-104 raw-vs-harmonized italicization. The synthesis CSV `notebooks/paper_companion_results.csv` carries the per-claim details.
2. **`notebooks/paper_companion.ipynb` binary sha = `dde922d1...` is NOT bit-stable across re-executions** (Jupyter execution metadata per L17). Receipt records as snapshot, not contract. Use `paper_companion_results.csv` (sha=`7891809c...`) as the bit-stable verification artifact. The Task 2 HALT 3 carries forward to Task 4's notebook.
3. **§15 Task 4 description names Section B 2017 race-stratified NVSR cell-level validation as an absorption** from Task 2's deferral. PRE-FLIGHT re-deferred per Convention 3 with explicit L9 reasoning (no pre-encoded targets; PDF transcription required; identical L9 risk to Task 2's original deferral). If the human disagrees, the absorption becomes a separate small future task: input is the 2017-vintage NVSR fetal-mortality PDF; output is ~4 new race-stratified rows in `fetal_death/external_validation_targets.csv` + a Section-B-style validation in either `joint_use_demo.ipynb` or `paper_companion.ipynb`.
4. **`fetal_death/harmonized_schema.csv` H8 dtype drift remains NOT YET RECONCILED** (Task 2 HALT 2 carried forward). Task 4's notebook uses string literals on `tabulation_flag` and `residence_status` (verified in §3 C05 cell). All future fetal-death joint-use code must follow the same pattern until the schema-version bump task lands.
5. **If a future task touches `paper/draft_v2_hmd_styled.md`** (any edit, not just Task 5), the manuscript's sha changes from `5e86c923...`. The next session's PRE-FLIGHT should re-run `python notebooks/_build_paper_companion.py` to confirm whether the edit added or removed numeric claims; if a new claim is added, the C01–C55 enumeration becomes stale and the notebook needs a Field-value-snapshot extension. A bit-stable check: `diff` the CSV sha against `7891809c...`; if changed, inspect the synthesis table for new tags.
6. **Task 1 HALT 6 (natality v2.8 rename plan-update)** remains open. No closing action in Task 4. Carried forward.

### Notes for next session

- Task 4 commit ships a ~5-line summary per Convention 5; full narrative in this receipt + the four precision-edit candidates inlined in `paper/README.md` + new STATUS.md section.
- `task4-pre-do` is at `61090fc`; `task4-complete` to be set after the task commit lands.
- §17 readiness checklist now has **1 ⏳ item remaining for manuscript submission** (was 2 at end of Task 2): Task 5 (manuscript trim). Tasks 3, 7, 8, 9, 10 also remain but only Task 3 is "ideally pre-submission, not blocking."
- Task 5 is the natural next move and is unblocked by this task's findings.
- Field-value snapshot (Convention 3) caught FOUR divergences this task (two pre-DO: Section B deferral + C29 framing; one in-DO: C44/C45 detection logic discovered and corrected during execution; one in-DO: C47/C48/C49 framing). Two of the in-DO corrections were author-side bugs in the notebook code that the snapshot helped surface quickly; one was a manuscript-side wording-precision finding.
