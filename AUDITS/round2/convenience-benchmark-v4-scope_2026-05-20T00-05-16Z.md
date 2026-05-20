# Round 2 — convenience-benchmark-v4-scope adversarial audit

## Scope

- **Commit:** `17814d2` (tag `convenience-benchmark-v4-scope-complete`)
- **In scope (substantive):** 7-line prepended blockquote in `docs/PIPELINE_TIMING_BENCHMARK.md` (+7 / −0 on that file only)
- **Agent claims under test:** (a) no fabricated v4 wall-clock numbers (L6); (b) every envelope fact in the note is sourced; (c) convenience CSVs + `write_residents_only.py` are not linked-v4-dependent and correctly scoped OUT; (d) Phase D step 4 routing is faithful to C8.13’s PROPOSE-EDIT
- **Out of scope (substantive):** `STATUS.md`, `DECISION_LOG.md`, `RECEIPTS/` body in the same commit (five-phase envelope; not audited for factual content)
- **Forbidden reads honored:** No round-1 `AUDITS/*` except this file; no `RECEIPTS/convenience-benchmark-v4-scope_2026-05-23T23-45-00Z.md`; no `STATUS.md` / `DECISION_LOG.md` / `PRE_FLIGHT_LOG.md` entries ≥ 2026-05-23T23:30:00Z

## Checks performed (each: command + result + interpretation)

### Check 1 — SOURCED FACTS (envelope numbers in scope note)

**Commands:** `git show 17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md`; `read README.md` four-products table; `grep` `STATUS.md` for `2026-05-13T23:00:00Z`, `2026-05-23T02:00:00Z`; `grep` `RECEIPTS/C8.13_2026-05-13T23-00-00Z.md`, `RECEIPTS/C8.17_step6_2026-05-16T08-00-00Z.md`, `RECEIPTS/C8.20_2026-05-23T13-00-00Z.md` for gate SHAs

| Fact in scope note | Permitted source | Match |
|-------------------|------------------|-------|
| Natality **201,161,456** / **57 yr** / **1968-2024** / v3.0.0 (C8.17) | `README.md` L16; `RECEIPTS/C8.17_step6` (201,161,456 rows, 57 years) | ✓ |
| Linked v4 **149,386,620** / **1983-2023** / **97 cols** / SHA **`f630d8cf…`** (C8.18) | `README.md` L17; `STATUS.md` `2026-05-23T02:00:00Z` (6b: 149,386,620 rows); `RECEIPTS/C8.20` (`f630d8cf20db72ea…`, 149,386,620 rows) | ✓ |
| Linked v3 **74.9M** / **94 cols** / SHA **`9b828a4d…`** (now `.v3_baseline`) | `STATUS.md` `2026-05-13T23:00:00Z` (74.9M, derive_linked_v3 94 cols); `RECEIPTS/C8.13` full SHA `9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777`, 74,943,824 rows; `STATUS.md` `2026-05-23T02:00:00Z` (`.v3_baseline` == `9b828a4d…`) | ✓ (74.9M = rounded 74,943,824) |
| Natality benchmark envelope **1990-2024 / 138.8M** (pre-C8.17) | `STATUS.md` `2026-05-13T23:00:00Z` L3733–3734; doc body L115–121 | ✓ |

**Interpretation:** No L6 invented envelope figures. Abbreviated SHAs match documented gate prefixes.

---

### Check 2 — NO FABRICATED WALL-CLOCK (L6)

**Command:**
```bash
git diff 09bf813..17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md
grep '^+' … | grep -E '[0-9]+\.[0-9]+ (s|min)|[0-9]+ min'
```

**Result:** Diff is exactly +7 lines (blockquote). No `NN.NN s|min` or `N min` wall-clock literals in added lines. Added text uses rounded record counts (`201M`, `149M`) and envelope metadata only.

**Interpretation:** Claim (a) holds — no fabricated v4 timing numbers in the edit.

---

### Check 3 — CONVENIENCE-CSV / RESIDENTS-ONLY NON-DEPENDENCE

**Commands:** `read fetal_death/live_births_by_year.csv`; `read fetal_death/stratified_denominators.csv` (header); `read shared/helpers/build_stratified_denominators.py`; `read natality/scripts/06_convenience/write_residents_only.py`

| Artifact | Claim | Evidence | Linked-v4-stale risk? |
|----------|-------|----------|----------------------|
| `live_births_by_year.csv` | NVSR-transcribed static | Every row `Source` = NVSR 57-08 / 73-09; no parquet path in file | **No** — not parquet-derived |
| `stratified_denominators.csv` | Natality-derived, not linked-v4 | Builder default input = `natality_v2_harmonized_derived.parquet` (natality core product); groups natality columns only; no linked parquet read | **No** for linked-v4 staleness. **Caveat:** module docstring still says “v2.7.0” (L5) while canonical derived gate is `acb5c48a…` v3.0.0 — documentation lag in a different file, not evidence the committed CSV is linked-v4-stale |
| `write_residents_only.py` | Gitignored reproducible output; `v3_linked` naming retained | Writes under `output/convenience/`; reads shipped parquets at run time; not git-tracked benchmark substrate | **No** for soft-flag (ee) on the *benchmark doc*: script is run-time reproducible, not a stale committed timing artifact. Running it today would pick up v4 linked parquet by path — that is correct behavior, not benchmark-doc drift |

**Interpretation:** Scoping convenience artifacts OUT of (ee) is defensible. None are linked-v4-dependent in a way that invalidates the benchmark scope note.

---

### Check 4 — C8.13 D.4 ROUTING FAITHFULNESS (claim d)

**Command:** `read docs/PIPELINE_TIMING_BENCHMARK.md` — scope note L7–8; preamble L20–22; `### PROPOSE-EDIT to Phase D step 4` L92–113; natality reconciliation L138–146

**Result:**

- **Explicit in C8.13 doc:** Fetal-death manuscript timing PROPOSE-EDIT is routed to Phase D step 4 (L92–113). Preamble L20–22 states ±10% VERIFY failures trigger PROPOSE-EDIT at D.4 (C8.12 precedent).
- **Natality+linked at C8.13:** VERIFY **PASS** (L144–146) — **no** PROPOSE-EDIT block for natality; manuscript “~90 min” clause unchanged.
- **Scope note wording:** Bundles “manuscript timing-claim reconciliation” with “the C8.13 fetal-death PROPOSE-EDIT” (accurate for fetal-death) and assigns “v4 natality+linked re-measure” to “that same Phase-D post-final-rebuild pass” (project/process routing, **not** text inside the PROPOSE-EDIT section).
- **Permitted STATUS** `2026-05-23T02:00:00Z` carried-forward: “C8.13 PROPOSE-EDIT manuscript-timing; … linked v4 …” at D.4 — supports D.4 for v4 timing, but source is STATUS/process, not C8.13 PROPOSE-EDIT body.

**Interpretation:** Claim (d) is **partially faithful**. Fetal-death D.4 routing matches C8.13 PROPOSE-EDIT verbatim. Attributing the **v4 natality+linked re-measure** to “C8.13’s own PROPOSE-EDIT” overstates what that section contains (L11 / looks-right). Correct disposition: D.4 + STATUS carried-forward, not the PROPOSE-EDIT block alone.

---

### Check 5 — C8.13 NATALITY+LINKED MEASUREMENT WAS PRE-C8.17

**Commands:** `read` doc § “Natality + linked pipeline (1990-2024 natality, 2005-2023 linked)” L115–127; `STATUS.md` `2026-05-13T23:00:00Z` L3731–3738

**Result:** Section heading and parse row: “Parse natality 1990-2024 (35 years, **138.8M records**)”. C8.13 driver used `parse_all_v1_years` 1990-2024 + linked 2005-2023. C8.17 extended natality to 1968-2024 / 201.1M **after** 2026-05-13.

**Interpretation:** Staleness claim (pre-C8.17 / pre-C8.18 for linked) is **correct**. No false supersession narrative.

---

### Check 6 — POST-NOTE INTERNAL CONSISTENCY

**Command:** Full read of `docs/PIPELINE_TIMING_BENCHMARK.md` after prepend

**Result:**

| Body region | Tension with scope note | Disposition |
|-------------|-------------------------|-------------|
| Intro L10–12 (“captured at C8.13 … 2026-05-13”) | Historical framing; note says envelope grew | **OK** — note is explicit supersession banner |
| Natality+linked tables L115–127 (88.45 min, 138.8M, 74.9M, 94 cols) | Superseded per note | **OK** — intentional retained measurement |
| H10 linked row L159 (`9b828a4d…`) | Superseded; note calls out “§H10 linked row” | **OK** |
| H10 natality row L158 (`e16ad532…`) | Post-C8.17 gate is `acb5c48a…` (`.v28_baseline` = `e16ad532…`) | **Minor H8** — natality H10 anchor is also pre-v3.0.0; note names linked row explicitly but not natality H10 row (wall-clock section covers natality timing) |
| Fetal-death + methodology + caveats | Note says still valid | **OK** — fetal v2.4.0 unchanged at C8.13 |
| How-to-reproduce L195–201 (`harmonize_linked_v3`, v3 paths) | v4 rebuild would need different drivers | **OK** — note says methodology reproduces v4 when Phase-D rebuild runs; not claiming current commands are v4 |

**Interpretation:** No silent contradiction that defeats the note. Residual doc-data drift is **documented partial staleness**, not an accidental lie.

---

### Ancillary — commit envelope vs “doc-only +7/-0”

**Command:** `git show 17814d2 --stat`

**Result:** 4 files: `docs/PIPELINE_TIMING_BENCHMARK.md` (+7), plus `STATUS.md`, `DECISION_LOG.md`, `RECEIPTS/` (expected five-phase commit). **Zero** `.parquet` / pipeline script / canonical CSV mutation in diff.

**Interpretation:** “Doc-only +7/-0” correctly describes the **benchmark deliverable**; whole commit is not single-file. Aligns with §7-#17 (no canonical rebuild), not scope creep into data plane.

## Findings

| §8 class | Severity | Evidence |
|----------|----------|----------|
| L11 | **minor** | Scope note ties v4 natality+linked re-measure to “C8.13’s own PROPOSE-EDIT”; C8.13 PROPOSE-EDIT body is fetal-death-only. D.4 routing for v4 timing is supported by STATUS `2026-05-23T02:00:00Z` carried-forward, not by the PROPOSE-EDIT section. |
| H8 | **minor** | H10 natality derived SHA row (`e16ad532…`) is pre-C8.17 v3.0.0 gate; scope note explicitly flags linked H10 row but not natality H10 row (timing section covers natality wall-clock). |
| *(none)* | — | L6 invented numbers; fabricated v4 wall-clocks; linked-v4-dependent convenience CSV staleness; false pre-C8.17 measurement claim. |

## Halt

**None.** No §7 gate (reproducibility regression, canonical mutation, new mistake class in scoped benchmark note). Findings are documentation-precision / attribution issues, not blockers to the scoped doc edit.

## Anti-cheerleading

The blockquote does real work: it surfaces superseded C8.13 natality+linked timings and the v3 linked H10 row without inventing replacement numbers. That is the right trade for pre-Zenodo cleanup. The weaknesses are narrow: D.4 attribution over-credits the PROPOSE-EDIT section for work that lives in Phase-D process text, and the H10 table still shows a pre-v3.0.0 natality SHA without a one-line callout. Neither invalidates scoping convenience artifacts OUT or the refusal to fabricate v4 wall-clocks.

## Verdict: **PASS**

Commit `17814d2` scope note is substantively sound: envelope facts are sourced, no L6 timing fabrication, convenience paths are correctly excluded from linked-v4 staleness, and pre-C8.17/C8.18 measurement claims match C8.13 evidence. **Minor** L11/H8 items only; no HALT.
