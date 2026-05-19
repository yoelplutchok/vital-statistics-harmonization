# Receipt: convenience-benchmark-v4-scope
## 2026-05-23T23:45:00Z

### What was done

TaskList #5 (final) of the user-authorized 2026-05-23 "Pre-D cleanup first" block. Discharged the carried Phase-D deferral "convenience/benchmark v4 refresh (soft-flag (ee))" by precisely scoping it and converting the one genuinely-stale, in-scope, git-tracked artifact from an undocumented latent staleness into a **documented, scoped limitation**: added a prominent dated post-C8.13 scope note to `docs/PIPELINE_TIMING_BENCHMARK.md` stating it is the C8.13 (2026-05-13) point-in-time measurement, that the natality+linked section + the H10 linked-SHA row are superseded pre-C8.17/pre-C8.18 figures (natality 1990-2024/138.8M → v3.0.0 1968-2024/201,161,456; linked v3 2005-2023/74.9M/94/`9b828a4d…` → v4.0.0 1983-2023/149,386,620/97/`f630d8cf…`), that the fetal-death section + methodology + how-to-reproduce remain valid, and that a v4 re-measure is a Phase-D post-final-rebuild item (the manuscript timing reconciliation is already routed to Phase D step 4 by C8.13's own PROPOSE-EDIT). **No fabricated v4 wall-clock numbers (L6); no canonical pipeline rebuild triggered (§7-#17 / C8.7b-orchestrator-DEFERRED class); doc-only; zero canonical mutation.** The convenience CSVs were precisely scoped OUT of (ee) (not linked-v4-dependent).

### Inputs consumed
- `docs/PIPELINE_TIMING_BENCHMARK.md` (committed @ `0155a6f` = C8.13) + `_fetal_raw.csv`/`_natality_raw.csv`
- `fetal_death/live_births_by_year.csv`, `fetal_death/stratified_denominators.csv`, `natality/scripts/06_convenience/write_residents_only.py` (scoping inspection)
- Envelope facts (sourced, not invented): README four-products row (natality 201,161,456); STATUS/C8.18 (linked v4 149,386,620 / 1983-2023 / 97 cols); the gate-SHA list (`f630d8cf…` v4, `9b828a4d…` = `.v3_baseline`)

### Outputs produced
- `docs/PIPELINE_TIMING_BENCHMARK.md` — +7 insertions / 0 deletions (one 6-line blockquote scope note after the title; body untouched) + this receipt + STATUS/DECISION_LOG/PRE_FLIGHT_LOG appends

### Five-phase trace
- PRE-FLIGHT: ✓ `PRE_FLIGHT_LOG.md` 2026-05-23T23:30:00Z — PROCEED; tag `convenience-benchmark-v4-scope-pre-do`@`09bf813` before DO (no L10 back-fill). Per-artifact v4-dependence enumerated.
- SMOKE: ✓ doc-only SHAPE — confirmed no test/validator reads `PIPELINE_TIMING_BENCHMARK.md` (driver scripts only reference the path)
- DO: ✓ one additive blockquote note, commits `09bf813`..`<this commit>`
- VERIFY: ✓ criteria below
- RECEIPT: ✓ this file

### Verify results
- V1 note present + sourced + no fabricated numbers: PASS — note dated 2026-05-23; uses only documented envelope facts (201,161,456 / 149,386,620 / the two SHAs / "Phase D step 4"); a targeted grep for newly-added wall-clock figures = none (no invented v4 times — L6)
- V2 scope: PASS — `git diff --name-only convenience-benchmark-v4-scope-pre-do` = exactly `docs/PIPELINE_TIMING_BENCHMARK.md` (+ state files this commit); zero canonical/test/script/CSV mutation
- V3 convenience CSVs untouched: PASS — `live_births_by_year.csv` (NVSR-transcribed static, not parquet-derived), `stratified_denominators.csv` (natality v3.0.0-derived, gate SHAs unchanged), `write_residents_only.py` (gitignored/reproducible output, retained schema-family-tag name) correctly NOT modified — they are not linked-v4-dependent (out of (ee) scope per PRE-FLIGHT)
- V4 markdown well-formed: PASS — title intact; 6-line balanced blockquote; Measurement methodology + H10 sections intact; +7/-0 additive

### Reproducibility
- Doc-only; `git revert <commit>` removes the note. `convenience-benchmark-v4-scope-pre-do`@`09bf813` is the anchor. The driver scripts + methodology in the doc reproduce a v4 measurement whenever a Phase-D canonical rebuild is run.

### Cross-product re-probe
- N/A — no canonical artifact; no test/validator reads the benchmark doc (SMOKE).

### Git
- Pre-DO tag: `convenience-benchmark-v4-scope-pre-do`, commit=`09bf813`
- Post-RECEIPT tag: `convenience-benchmark-v4-scope-complete`, commit=`<this commit>`

### STATUS.md updated
- New section dated 2026-05-23T23:45:00Z prepended; title "last updated" → 2026-05-23T23:45:00Z; **the entire internal Pre-D cleanup block (TaskList #1-#5) marked COMPLETE**

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?
1. **A convenience artifact that IS linked-v4-dependent and I wrongly scoped out.** Mitigation: enumerated each — `live_births_by_year.csv` has `source` = NVSR (transcribed static, not parquet-derived); `stratified_denominators.csv` derives from natality (gate SHAs `c8a740eb…`/`acb5c48a…` UNCHANGED this whole session); `write_residents_only.py` writes gitignored/reproducible build-side output with the retained `natality_v3_linked_*` schema-family-tag name (the C8.17/C8.18 convention). None is linked-v4-derived-and-git-tracked-and-stale. soft-flag (ee)'s "v4" refers to the C8.18 linked v3→v4 — the benchmark is the only git-tracked artifact carrying that staleness.
2. **The scope note's envelope numbers could be wrong.** Mitigation: 201,161,456 (README four-products row), 149,386,620 (STATUS 2026-05-23 / C8.18 6b), the SHAs (the gate-SHA list / STATUS Build-artifacts) — all sourced, none computed by me; the note adds NO wall-clock figure.
3. **"Document the staleness" under-delivers vs "refresh".** Mitigation: a true measured refresh = a multi-hour canonical natality(201M)+linked-v4(149M) rebuild, which is the C8.7b-orchestrator-DEFERRED class + out of a pre-Zenodo doc-cleanup's scope (§7-#17), and fabricating the numbers violates L6. The honest, scope-correct outcome is exactly to convert an undocumented latent staleness into a documented, scoped, reproducible-on-Phase-D-rebuild limitation — consistent with C8.13's own routing of the manuscript timing reconciliation to Phase D step 4. The natality+linked re-measure naturally belongs to the same Phase-D post-final-rebuild pass.

### Forward-looking HALTs for next session (Convention 4)
1. `convenience-benchmark-v4-scope-pre-do`@`09bf813` + `-complete` set ⇒ task CLOSED; soft-flag (ee) is **documented + scoped** (no longer a latent undocumented staleness). **The entire internal Pre-D cleanup block (TaskList #1-#5) is COMPLETE.**
2. **The natality+linked v4 timing re-measure is a Phase-D post-final-rebuild item** (do it in the same pass as the D.4 manuscript timing-claim reconciliation, using the driver scripts + methodology in `PIPELINE_TIMING_BENCHMARK.md`). The fetal-death section is already v2.4.0-correct.
3. The convenience CSVs (`live_births_by_year.csv` 1995-2022 NVSR-static; `stratified_denominators.csv` natality-derived) are NOT (ee)-stale; any year-coverage extension for the fetal-v2.4.0 / natality-1968 envelopes is a separate, non-blocking, non-(ee) convenience question (soft-flag-able, not owed by this cleanup).
4. 3 gate parquet SHAs unchanged (doc-only). Repo append-only clock ahead of harness `currentDate` — keep timestamps monotonic-after.

### Notes for next session
- **Internal Pre-D cleanup COMPLETE (5/5).** The only remaining work is the externally-irreversible, human-authorization-gated **Phase D** (D.1 GitHub redirects → D.2 unified Zenodo deposit → D.3 public-repo v1.x sync → D.4 manuscript re-pass + submit). Do NOT begin Phase D autonomously.
- §2/§4.4/§9-#2/§9-#3/§10/L6/L11 honored: cheap PRE-FLIGHT per-artifact dependence analysis; honest scope (precisely what (ee) covers — not over-claiming); documented-not-fabricated; no canonical rebuild triggered.
