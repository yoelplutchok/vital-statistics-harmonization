# Receipt: fetal-death-codebook-comparability-v240
## 2026-05-23T21:30:00Z

### What was done

TaskList #2 of the user-authorized 2026-05-23 "Pre-D cleanup first" block. Re-paragraphed the hand-authored bodies of `fetal_death/CODEBOOK.md` (lines 1-258, the body above the C8.20 generated appendix) + `fetal_death/COMPARABILITY.md` (whole file) from the stale **V2.0 / 1992-2022 / 29-year / 1,634,195-record** envelope to the canonical **v2.4.0 / 1982-2024 / 43-year / 2,427,233-record / 7-era** envelope, at the user-confirmed **Option A depth** (AskUserQuestion 2026-05-23): envelope + cross-era narrative re-paragraphed; the per-variable V2/V1 within-era statements (still accurate for those eras) preserved; V3b (1982-1988, 1978-rev) / V3a (1989-1991, early-1989-rev) / V2.1 (2003-2004, transition) era behaviour added as a concise cross-era narrative; **every introduced number parquet-derived** from the committed C8.20 generated appendix (no hand-invented counts — L6/§9-#2); the exhaustive per-variable per-era evidence is pointed at the C8.20 appendix (not duplicated, not hand-edited). The C8.20 generated block is **byte-identical** (the key non-mutation invariant). Doc-only; zero canonical-state mutation.

### Inputs consumed
- `fetal_death/CODEBOOK.md` hand-body (lines 1-258) + `fetal_death/COMPARABILITY.md` — pre-edit state @ `fetal-death-codebook-comparability-v240-pre-do`@`560c754`
- Authoritative L6-safe per-era facts: C8.20 generated appendix `version_flag`/`tabulation_flag` (i)-panels — fetal-death derived parquet sha256[:12]=`185c071ec76a`, 2,427,233 rows, deterministic
- Era nomenclature/behaviour: STATUS/DECISION_LOG V3b (2026-05-12T18:45Z) / V3a (2026-05-12T14:30Z) / V2.1 Task 3 (2026-05-12T02:45Z) / C8.2 (2026-05-12T23:30Z) receipts; `README.md` v2.4.0 row; PROJECT_STRUCTURE record_layout map

### Outputs produced
- `fetal_death/CODEBOOK.md` — hand-body re-paragraphed (title; file row counts 1,634,195→2,427,233; year-coverage para → 7-era; the C8.20 scope note → "re-paragraphed"; the era-summary matrix → 7-era parquet-derived table + cross-era V3b/V3a/V2.1 narrative + appendix pointer; stale-envelope per-variable asides scope-corrected, not recomputed; Data Quality + Source Crosswalk envelope phrasing). +26/-18. **C8.20 appendix (now lines 267-2779) byte-identical.**
- `fetal_death/COMPARABILITY.md` — title; intro "29-year"→"43-year"; Era Structure "four"→"seven" + 7-era table + V3b/V3a/V2.1 narrative; §1 +1982-1991 A/S row (610,034 = 421,125+188,909); §2 race span + bridged-race-discontinued count (293,262, 2018-2024) + recommendation 1982-2024; §3 "V2.0"→"this resource"; §4 `2018-2022`→`2018-2024`; §7-bis envelope label; §10 raw-archive phrasing; Summary-matrix caption + `2018-2022`→`2018-2024` + V3b/V3a/V2.1 + appendix pointer. +25/-19.
- This receipt + `STATUS.md` + `DECISION_LOG.md` appends

### Five-phase trace
- PRE-FLIGHT: ✓ `PRE_FLIGHT_LOG.md` 2026-05-23T21:00:00Z — PROCEED; committed + tagged `fetal-death-codebook-comparability-v240-pre-do`@`560c754` before DO (no L10 back-fill); Option-A depth user-confirmed via AskUserQuestion
- SMOKE: ✓ SHAPE invariants for a doc-only task — C8.20 appendix pre-DO sha snapshot `b27640eeb6eda142`; no test/script reads these docs (Task-1 SMOKE established; unchanged)
- DO: ✓ commits `560c754` (PRE-FLIGHT) .. `<this commit>`
- VERIFY: ✓ criteria below (incl. the §4.4/L7 correction of a measurement artifact)
- RECEIPT: ✓ this file

### Verify results
- V1 (CRITICAL) C8.20 appendix byte-identical: **PASS** — marker-extracted (`<!-- C8.20-GENERATED:BEGIN -->`→EOF) sha `b27640eeb6eda142` pre-DO == post-DO. The first line-range check (`sed 259,$`) FALSELY alarmed because the hand-body length changed and the BEGIN marker moved 259→267; re-checked by marker (line-number-independent) per §4.4/L7 — invariant HELD. Marker integrity: exactly 1 BEGIN (L267) + 1 END (L2779), ordered.
- V2 scope: PASS — `git diff --name-only fetal-death-codebook-comparability-v240-pre-do` = exactly the 2 hand-docs (+ state files this commit)
- V2b zero canonical mutation: PASS — no `.parquet`/`harmonized_schema`/`external_validation`/`file_inventory`/`.py`/`tests/` in the diff
- V3 residual stale-envelope sweep: PASS — both docs clean after fixing the §4 `2018-2022`→`2018-2024` residual (the legitimate within-era `1992-2002` statements + the correct §11/§12 "V2-Specific (1992-2002)" / "V2 stale-guide years (1996,2001,2002)" section titles are preserved, not over-edited)
- V4 numbers parquet-derived + sum-check: PASS — 421,125+188,909+700,704+107,782+510,528+204,923+293,262 = 2,427,233 ✓; 1982-1991 = 421,125+188,909 = 610,034 ✓; all from the C8.20 appendix (no hand-invention)
- V5 markdown well-formed: PASS — pipe-table column counts consistent in both docs (CODEBOOK hand-body + COMPARABILITY)

### Reproducibility
- No build step (doc-only). C8.20 appendix regenerable byte-identically via `scripts/_build_codebook_extensions.py` (unchanged; not run — invariant proven by marker-sha). `git revert <commit>` restores prior doc text; `fetal-death-codebook-comparability-v240-pre-do`@`560c754` is the anchor.

### Cross-product re-probe
- N/A — no canonical artifact; no test/script consumes these docs (Task-1 SMOKE).

### Git
- Pre-DO tag: `fetal-death-codebook-comparability-v240-pre-do`, commit=`560c754`
- Post-RECEIPT tag: `fetal-death-codebook-comparability-v240-complete`, commit=`<this commit>`

### STATUS.md updated
- New section dated 2026-05-23T21:30:00Z prepended; title "last updated" → 2026-05-23T21:30:00Z

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?
1. **A genuine envelope-stale string my regex sweep didn't pattern.** Mitigation: swept multiple patterns (`V2.0,`/`1,634,195`/`933,491`/`29-year`/`29 years`/`1992-2022 file|period|envelope|span`/`spans **four**`/`2018-2022`) on both docs to clean; but a paraphrase ("the 29 year span", "1992 through 2022") could survive. Residual risk logged; the C8.20 line-14 note explicitly scopes the body as V2/V1-detail + points to the appendix, so any survivor is bounded to a V2/V1 narrative aside, not a headline claim.
2. **An over-edit: a `1992-2002` I "corrected" that was a legitimate within-era statement.** Mitigation: Option A explicitly preserves within-era statements; I only retargeted *envelope* claims (counts, year-span, "V2.0", "spans four eras", "2018-2022" era label). The §11/§12 V2-scoped section titles + the §3/§5/§8 within-era `1992-2002` source rows were deliberately NOT touched. Diff is small (+26/-18, +25/-19) — consistent with envelope-only, not a wholesale rewrite (a wholesale rewrite would be Option C, rejected).
3. **A new per-era number transcribed wrong.** Mitigation: every count copied from the committed C8.20 appendix (i)-panels and sum-checked to 2,427,233 + the 610,034 sub-sum; the appendix is itself parquet-derived + deterministic.
4. **V3b/V3a/V2.1 narrative claims (1978-rev predates A/S; V3a follows V2; V2.1 dual-cert 1351/1501-byte; B3 1-digit recode) could be imprecise.** Mitigation: each is sourced to the appendix `version_flag` schema-note + the V3b/V3a/V2.1/Task-3 receipts; stated qualitatively (no invented per-variable per-era counts) and the appendix is named as the authoritative detail — a reader is routed to parquet-derived evidence, not to a hand claim.
5. **Record-length bytes for V3b (~200) / V2.1 (1351/1501).** ~200 is from STATUS 2026-05-12T16:45Z ("record_layout_1982_1988.csv … 200 bytes covered"); 1351/1501 from the original COMPARABILITY §Era line + Task-3 receipt. V3a byte count deliberately left as "(see record_layout_*.csv)" — not invented. Low residual.

### Forward-looking HALTs for next session (Convention 4)
1. `fetal-death-codebook-comparability-v240-pre-do`@`560c754` + `-complete` set ⇒ this task CLOSED. The carried "fetal-death CODEBOOK/COMPARABILITY full-body v2.4.0 re-paragraph" Phase-D deferral is **discharged** — STATUS Phase-D-deferrals should drop it.
2. **C8.20 generated-appendix invariant**: any future edit to `fetal_death/CODEBOOK.md` must keep the `<!-- C8.20-GENERATED:BEGIN -->`…`END` block byte-identical (verify by **marker extraction**, NOT a hardcoded line range — the marker moved 259→267 this task; a line-range check will false-alarm whenever the hand-body length changes). Regenerate only via `scripts/_build_codebook_extensions.py`.
3. 3 gate parquet SHAs unchanged (`185c071e…`/`acb5c48a…`/`f630d8cf…`); doc-only; zero build-side change.
4. Remaining Pre-D cleanup: TaskList #3 (`file_inventory.csv` `imported`-flag), #4 (`external_validation_v3_linked_comparison.{md,csv}` v4), #5 (convenience/benchmark v4). Manuscript Coverage re-paragraph remains D.4 (untouched).
5. Date convention: 2026-05-23T21:30:00Z (monotonic-after the 21:00:00Z PRE-FLIGHT / 20:00:00Z plan-merge; repo append-only clock runs ahead of harness `currentDate` 2026-05-19).

### Notes for next session
- The fetal-death CODEBOOK/COMPARABILITY hand-bodies now describe the v2.4.0 1982-2024 7-era envelope; the C8.20 appendix remains the single source of truth for per-variable per-era distributions and was not touched.
- §2/§4.4/§9-#2/L6/L7 honored: cheap PRE-FLIGHT fact-extraction from the committed parquet-derived appendix before any edit; every number derived not invented; the false "APPENDIX CHANGED" alarm investigated (not rubber-stamped) and shown to be a line-range artifact via a marker-based re-check.
- Option A (not C) preserved the C8.20 generated-appendix architecture (no H8 hand-edit-drift surface re-introduced).
