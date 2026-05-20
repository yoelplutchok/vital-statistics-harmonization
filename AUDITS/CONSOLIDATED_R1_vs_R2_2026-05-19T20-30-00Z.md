# CONSOLIDATED R1 vs R2 — Independent two-round audit comparison

- **Consolidator timestamp:** 2026-05-19T20:30:00Z
- **Subject:** Pre-D cleanup block + session integrity, 5 tasks + 10 commits + 10 tags between `d913b91` and `17814d2`
- **Method:** 6 round-1 fresh-eyes agents (results at `AUDITS/*.md`) + 6 round-2 fresh-eyes agents (results at `AUDITS/round2/*.md`), each refused to read the matching RECEIPT and the other round's outputs
- **Consolidator role:** synthesis only; not itself an audit

---

## 1. Top-line: both rounds say PASS; zero blockers

| Task | R1 verdict | R2 verdict | Aligned? |
|---|---|---|---|
| #1 plan-merge | PASS-WITH-NOTES | **PASS** | Yes (both non-blocking; finding-count differs — see §3) |
| #2 CODEBOOK+COMPARABILITY | PASS-WITH-NOTES | **PASS** (advisory only) | Yes (different severity grading on the convergent finding) |
| #3 file_inventory | 1 FINDING (cosmetic) | **PASS** (with minor findings) | Yes (converged on the typo; R2 added 2 new minor findings) |
| #4 v3-linked-comparison | NO FINDINGS | **PASS** (ACCEPT) | **Perfect convergence** — both note only the pre-existing absolute-path smell |
| #5 benchmark scope note | NO L-CLASS FINDINGS | **PASS** (2 minor findings) | Mostly aligned; R2 found 2 NEW minor items R1 missed |
| #6 Session-integrity | PASS | **PASS** | **Perfect convergence** — both flag only the clock-offset & receipt-not-read caveats |

**Zero HALT in either round. Zero §7 conditions. Zero gate-SHA drift.** The independently-re-hashed 4 gate parquets (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`) match both rounds. Session-integrity audit returned PASS in both rounds (the strongest single signal — same conclusion from two independent agents on the cross-cutting invariants).

---

## 2. Per-task convergence map

### Task #1 — plan-merge-owed-backlog

| | R1 (Task1-plan-merge_…22-15-00Z) | R2 (round2/Task1-plan-merge_…00-01-55Z) |
|---|---|---|
| Verdict | PASS-WITH-NOTES | PASS |
| Findings | **1 minor (L11-adj):** C8.18 model-clar block omits `DO step 4 → 4a/4b/4c` decomposition | None binding; 2 informational notes: (i) two `L13-ext` rows share prefix with disambiguating suffixes only (naming overlap); (ii) one extra blank line after each prepended `>` block header (cosmetic) |
| Convergence | — | — |
| **R1 unique** | **R2 missed R1's DO-step-4 finding.** R2's Check 5 verified the sub-steps the block *did* cite (3, 5, 5c, 6, 7) but did not check whether DO step 4 should have been cited and was omitted. R1 caught it by querying DECISION_LOG for step 4 entries and finding 4a/4b/4c at 2026-05-18T05:00:00Z → 23:00:00Z. | |
| **R2 unique** | | The "L13-ext naming overlap" observation is new (low-value but factually correct — two distinct `L13-ext` rows differ only by suffix `(year-axis)` vs `(shared CSV)`). The blank-line note is cosmetic. |

### Task #2 — fetal-death CODEBOOK + COMPARABILITY v2.4.0

| | R1 (fetal-death-codebook-comparability-v240_…22-45-00Z) | R2 (round2/…00-04-28Z) |
|---|---|---|
| Verdict | PASS-WITH-NOTES | PASS (no HALT) |
| Findings | **#1 SIGNIFICANT (H8/L7):** L35 V2-rebroadening gloss vs per-variable Notes carrying 1992-2002-only counts (plurality 1,713; birthweight 397,397; singleton 1,713 — wrong under new gloss). **#2 cosmetic:** V3b "~200 bytes" tilde. **Soft #3:** L77 lost the "verified 1,634,195/1,634,195" V2.0 count without v2.4.0 replacement. **Out-of-scope obs:** appendix `data_year` Schema note still V2.0. | **Advisory (L7/H8 — label-not-arithmetic):** "Line 12 redefines legacy 'V2' as 1982-2002, but per-variable Notes still use 'V2' with 1992-2002-era counts. Reader applying new glossary could mis-scope. Mitigation already partial: appendix + era matrix disambiguate; residual doc UX risk only." **Residual #4 (NEW):** other `fetal_death/*.md` (GETTING_STARTED, FAQ, etc.) still carry V2.0 envelope. |
| **Convergence (strong)** | R1 Finding #1 ↔ R2 Advisory: **same defect** (L35 gloss vs per-variable Notes). **R2 explicitly classes it lower severity** ("residual doc UX risk only") vs R1's "significant." | |
| Convergence (also strong) | R1 out-of-scope obs (appendix `data_year` stale) ↔ R2 Check 4 appendix residue — same finding, both correctly out-of-scope. | |
| **R1 unique** | **Finding #2 (V3b ~200 tilde cosmetic)** — R2 verified the source ("87 rows, 200 bytes covered, 202 with CRLF") but did not object to the formatting tilde. **Soft #3 (L77 lost verification count)** — R2 classed the removal as envelope-correction; did not flag as a regression. | |
| **R2 unique** | | **Residual #4 (NEW):** other fetal_death docs (GETTING_STARTED, FAQ, etc.) still describe the V2.0 envelope. This is a real **project-wide doc-sync gap** — out of this commit's scope but real (a future-D deferral, or fold into the remediation bundle). |

### Task #3 — file-inventory imported-flag

| | R1 (file-inventory-imported-flag-v4_…23-00-00Z) | R2 (round2/…00-05-04Z) |
|---|---|---|
| Verdict | 1 FINDING (cosmetic) | PASS (with minor findings) |
| Findings | **Finding #1 (L7 cosmetic):** 19/19 col5 rewrite dropped the space → `(perLinkCO83Guide.pdf)` instead of `(per LinkCO83Guide.pdf)`. | **L7 minor:** same `(perLinkCO…)` missing space, 19/19 — **identical finding to R1**. **L11/H8 minor (NEW):** `docs/NCHS_SOURCE_MANIFEST.md` still describes the `imported`-flag refresh as a "tracked Phase-D follow-up" / "deliberately not flipped at C8.18 step 7" — that narrative is stale now that Task 3 shipped the flip. **L11 minor (NEW, informational):** `test_inventory_invariants.py` docstring still describes 1968-1989 as `imported=false` (data is now `true`; pre-existing, not introduced by Task 3). |
| **Convergence (perfect, the strongest cross-round signal)** | **Both rounds found the EXACT same typo** — 19/19 `(perLinkCO…)` missing space — independently, with the same grep evidence. **High-confidence real defect.** | |
| **R2 unique** | | **NEW H8 finding:** `docs/NCHS_SOURCE_MANIFEST.md` lines ~153 / ~205 still say the `imported`-flag refresh is deferred. This is real H8 doc-data drift that Task 3 *should* have propagated to that doc (the C8.17/C8.18-step7 honest-propagation pattern). R1 missed it. Trivially fixable. |

### Task #4 — v3-linked-comparison-v4-verify

| | R1 (v3-linked-comparison-v4-verify_516b621_…22-45-00Z) | R2 (round2/…00-04-58Z) |
|---|---|---|
| Verdict | NO FINDINGS | PASS (ACCEPT) |
| Findings | None blocking. Pre-existing portability smell (absolute path in `.md` line 4) flagged as out of audit scope. | None blocking. **O1 cosmetic pre-existing:** absolute targets path in generated `.md`, predates `516b621`. |
| **Convergence (perfect)** | **Both rounds independently re-ran the validator, confirmed H10 byte-identical re-render, confirmed mutation guard non-tautological, confirmed parquet SHA `f630d8cf20db72ea…`, confirmed 35 pass / 0 fail / 0 missing on the 2005-2023 owned surface.** Both noted *only* the pre-existing absolute-path cosmetic. **Strongest cross-round agreement on the most dangerous audit shape (claim of zero work).** | |

### Task #5 — convenience-benchmark-v4-scope

| | R1 (convenience-benchmark-v4-scope_…22-45-00Z) | R2 (round2/…00-05-16Z) |
|---|---|---|
| Verdict | NO L-CLASS FINDINGS | PASS (2 minor findings) |
| Findings | 2 minor non-L observations: (i) L146 verdict implicitness — the scope note's "superseded" framing transitively covers the doc's L146 "no edit recommended for natality clause" verdict but doesn't explicitly call it out; (ii) `build_stratified_denominators.py` docstring still says v2.7.0 (out of scope; different file). | **L11 minor (NEW):** the scope note attributes "v4 natality+linked re-measure routing" to "C8.13's own PROPOSE-EDIT" — but C8.13's PROPOSE-EDIT body is fetal-death-only. D.4 routing for v4 natality+linked timing is supported by STATUS 2026-05-23T02:00:00Z carried-forward, **not by the PROPOSE-EDIT section itself**. **H8 minor (NEW):** the scope note explicitly flags the H10 *linked* row as superseded but not the H10 *natality* row, which is also pre-C8.17 (`e16ad532…` is the pre-v3.0.0 gate; post-C8.17 is `acb5c48a…`). |
| **Convergence** | R1 obs (ii) ↔ R2 Check 3 caveat on `build_stratified_denominators.py` v2.7.0 docstring — same item, same out-of-scope classification. | |
| **R1 unique** | R1 obs (i) (L146 verdict implicitness) — R2's Check 6 walked internal consistency and explicitly classed the L146 retention as "OK — intentional retained measurement" under the note's blanket "superseded" framing. **R2 disagrees with R1 here.** | |
| **R2 unique** | | **Two new findings R1 missed:** (i) the PROPOSE-EDIT attribution overstatement (real L11 — the scope note implies C8.13 already routed v4 natality+linked to D.4, but C8.13's PROPOSE-EDIT covers only fetal-death); (ii) the natality H10 row is also pre-C8.17 and was not called out. Both are real, both trivially fixable. |

### Prompt #6 — Session-integrity

| | R1 (Session-integrity_…22-30-00Z) | R2 (round2/…00-06-55Z) |
|---|---|---|
| Verdict | PASS | PASS |
| Findings | None. PASS-with-notes-deferred-to-per-task-prompts on (i) clock offset and (ii) receipts-not-read. | None HALT. Same two PASS-WITH-NOTES informational items (clock offset; receipt fidelity not verified by design). |
| **Convergence (perfect)** | **Both rounds independently re-hashed the 4 gate parquets and got identical SHAs**, both verified L10 ordering, both verified tag/receipt completeness, both verified append-only integrity, both verified discharge-delta, both verified cumulative numstats. **Most independent verification this session got.** | |

---

## 3. Convergent findings (high confidence — both rounds caught these)

These are the **highest-credibility findings** — two independent fresh-LLM agents reached the same conclusion without seeing each other's work:

| ID | Task | Class | What | Severity (averaged) |
|---|---|---|---|---|
| **C1** | #3 | L7 | 19/19 `(perLinkCO…Guide.pdf)` missing-space typo in col5 of every flipped row | Cosmetic |
| **C2** | #2 | H8/L7 | L35 V2-rebroadening gloss conflicts with per-variable Notes carrying 1992-2002-only counts | R1=Significant / R2=Advisory; effective = **Significant-but-non-blocking** |
| **C3** | #2 | (out-of-scope) | C8.20 appendix `data_year` Schema note still V2.0; upstream generator-input issue | OOS — future regenerator-side fix |
| **C4** | #5 | (out-of-scope) | `build_stratified_denominators.py` module docstring still v2.7.0 | OOS — different file |
| **C5** | #4 | (cosmetic, pre-existing) | Absolute targets path in generated `.md` line 4 | Pre-existing, out of scope |
| **C6** | #6 | (caveat) | Repo append-only clock vs harness `currentDate` (documented offset) | Not a finding |

---

## 4. R2-unique findings (R1 missed — but R2 caught real things)

R2 surfaced **4 substantive findings R1 missed** — all real, all trivially fixable:

| ID | Task | Class | What | Recommended action |
|---|---|---|---|---|
| **R2a** | #3 | L11/H8 | `docs/NCHS_SOURCE_MANIFEST.md` still describes the `imported`-flag refresh as a tracked Phase-D follow-up; Task 3 shipped the flip but didn't propagate to that doc | **Add to remediation bundle:** one targeted reword (turn "deferred to Phase D" → "shipped at task `file-inventory-imported-flag-v4`@`84a9af3`") |
| **R2b** | #5 | L11 | Scope note overstates what C8.13's PROPOSE-EDIT section contains (it covers fetal-death only; v4 natality+linked routing is from STATUS-carried-forward, not the PROPOSE-EDIT body) | **Add to remediation bundle:** one-sentence rework of the attribution in the scope note |
| **R2c** | #5 | H8 | Scope note flags H10 linked row as superseded but not H10 natality row (also pre-C8.17, `e16ad532…` is the pre-v3.0.0 gate) | **Add to remediation bundle:** extend the scope note to flag the natality H10 row too |
| **R2d** | #2 | (project-wide gap) | Other `fetal_death/*.md` (GETTING_STARTED, FAQ, etc.) still describe the V2.0 envelope | Out of this session's scope; flag as a separate Phase-D doc-sync task |

---

## 5. R1-unique findings (R2 missed — likely real, lower-priority)

R1 surfaced **3 substantive findings R2 missed**. Triage:

| ID | Task | Class | What | Status |
|---|---|---|---|---|
| **R1a** | #1 | L11-adj | C8.18 model-clar block omits `DO step 4 → 4a/4b/4c` decomposition (4a 1995-2002; 4b 2003 DEFLATE64; 4c 2004 dual-cert; all witnessed in DECISION_LOG 2026-05-18T05–23) | **Real** — R2's Check 5 only verified the sub-steps the block did cite, didn't probe for omitted ones. Add to remediation bundle. |
| **R1b** | #2 | Cosmetic | V3b "~200 bytes" tilde vs V2's "360 bytes (362 with CRLF)" parity | **Real** but truly cosmetic. R2 verified the source value (200) but didn't flag formatting parity. Optional. |
| **R1c** | #2 | Soft | L77 `data_year` Notes dropped the pre-edit "verified 1,634,195/1,634,195 in V2.0" without v2.4.0 replacement | **Subjective.** R2 classed the removal as legitimate envelope-correction; R1 flagged the loss of evidentiary backing. **Reasonable disagreement.** Optional. |
| (Task 5 L146 verdict implicitness — R1 only) | #5 | — | R1 noted the scope note doesn't explicitly cover the L146 "no edit recommended" verdict transitively superseded | **R2 explicitly disagrees** — R2 Check 6 classed it as "OK — intentional retained measurement" covered by the blanket framing. **Defer; R2's read is defensible.** |

---

## 6. Expanded remediation bundle (rolling C1 + C2 + R2a + R2b + R2c + R1a + R1b + R1c)

Pre-Phase-D one-task remediation bundle (mirrors the C8.20-auditfix precedent), now expanded to incorporate round-2 findings:

| # | Source | Edit | Files |
|---|---|---|---|
| 1 | C1 (R1+R2 converged) | `replace_all` `(perLinkCO` → `(per LinkCO` (19 rows) | `natality/metadata/file_inventory.csv` |
| 2 | C2 (R1+R2 converged) | Apply `tabulation_flag`-style scoping (explicit "V2.0 1992-2002 slice" + appendix pointer) to the 3 affected per-variable Notes — OR drop the L35 V2-rebroadening gloss | `fetal_death/CODEBOOK.md` |
| 3 | R1a | Prepend `DO step 4 → 4a/4b/4c` clause to C8.18 model-clar block | `NEXT_STEPS.md` §15.D |
| 4 | R1b | Replace V3b `"~200 bytes (1978-rev)"` → `"200 bytes (202 with CRLF)"` (×2 docs) | `fetal_death/COMPARABILITY.md`, `fetal_death/CODEBOOK.md` |
| 5 | R1c | Add `(verified 2,427,233/2,427,233 in v2.4.0; see Appendix C8.20)` to CODEBOOK L77 | `fetal_death/CODEBOOK.md` |
| 6 | **R2a (NEW)** | Update `docs/NCHS_SOURCE_MANIFEST.md` paragraphs that say the `imported`-flag refresh is deferred → shipped | `docs/NCHS_SOURCE_MANIFEST.md` |
| 7 | **R2b (NEW)** | Reword the scope-note attribution: separate "C8.13's PROPOSE-EDIT routes the fetal-death edit to D.4" from "the v4 natality+linked re-measure is routed to D.4 via STATUS carried-forward" | `docs/PIPELINE_TIMING_BENCHMARK.md` |
| 8 | **R2c (NEW)** | Extend the scope note to flag the H10 natality row (`e16ad532…`) as also pre-C8.17, not only the linked H10 row | `docs/PIPELINE_TIMING_BENCHMARK.md` |

**Estimated effort:** 1 short task under full five-phase discipline. All doc/metadata-only; fully reversible; zero canonical mutation. Deliverable count: 8 edits across 5 files (1 metadata-CSV, 4 docs).

**R2d (Task 2 other fetal_death/*.md V2.0 envelope)** is a *separate* project-wide doc-sync question — not part of this bundle; either fold into the same bundle (widens it significantly) or defer to a dedicated D.3-adjacent doc-sync pass. **Recommend defer** — it's a >1-task surface and triggering it pre-D would balloon scope. Soft-flag it for Phase D.3 or post-submission.

---

## 7. Phase-D-entry readiness assessment

### What two independent rounds prove with very high confidence
- **Zero canonical data mutation.** 4 gate parquet SHAs byte-exact (re-hashed independently by both Session-integrity audits). The strongest single Phase-D-readiness signal.
- **Append-only state-file integrity intact** (both Session-integrity audits verified — both spot-checked the LESSONS 2026-05-20 entry and STATUS C8.22 section byte-identical pre/post).
- **No L10 back-fills, no scope creep, no §7 conditions, no halts.** Both rounds independently.
- **All 5 Phase-D deferrals discharged faithfully, manuscript untouched** (`git diff -- paper/draft_v2_hmd_styled.md` empty — both rounds confirmed).
- **Task 4 (verify-current) discharge is genuine** — both rounds independently re-ran the validator, both got byte-identical re-renders, both confirmed mutation guard live. This was the most dangerous audit shape and got the cleanest cross-round convergence.

### What the two rounds disagree about (worth noting)
- **Severity of Task 2 Finding C2.** R1: "significant" (could mislead a careful reader into 80-100% wrong counts). R2: "advisory — residual doc UX risk only." Effective severity = **significant-but-non-blocking** (real, fixable, not a release blocker).
- **Task 5 L146 verdict implicitness.** R1 flagged; R2 explicitly disagreed. Defensible either way; defer.
- **R1 found 3 finds R2 missed; R2 found 4 finds R1 missed.** Net: both rounds individually had ~50% recall on the union of findings. Together they form a ~stronger picture than either alone — exactly why the two-round design is worth the effort.

### Recommendation

**Phase D entry: not blocked.** Both rounds independently say PASS / no blockers / no HALT. The convergent findings (C1, C2) plus the union of R1-unique and R2-unique findings constitute a known, scoped, trivially-fixable remediation bundle (8 edits, 5 files, ~1 short task).

**Ship the expanded remediation bundle now**, then Phase D. The bundle is:
- Strictly larger than what R1 alone proposed (R2 added 3 real items R1 missed; the dual-round audit was worth it).
- Strictly doc/metadata-only; zero canonical mutation; fully reversible.
- Mirrors the established C8.20-auditfix precedent (a fresh-eyes audit catches non-blocking improvements; remediate before submission).

The R2d "other fetal_death docs still V2.0 envelope" item is the only thing flagged for **defer** — it's a project-wide doc-sync surface bigger than a remediation bundle should swallow.

### What this two-round audit does NOT cover

Same as the single-round report:
- Pre-Zenodo Phase-C scope itself (C8.16–C8.22 deliverables, excluding the previously-audited C8.20)
- Canonical pipelines (natality v3.0.0, linked v4.0.0, fetal v2.4.0, matched-multiples) — the gate-SHA invariants attest to no-mutation this session, but full pipeline audit is out of scope
- Phase D itself (externally irreversible; human-authorization-gated by design)

For those surfaces, `/ultrareview` is the right mechanism pre-Phase-D.

---

## 8. Bottom line

**12 independent adversarial audits across 2 rounds. 0 blockers in either round. 0 §7 halts. 0 gate-SHA drift.** Both rounds reached the same overall verdict (Pre-D cleanup is substantively sound), with high cross-round convergence on the most-confidence-warranting findings (Task 3 typo, Task 4 zero-work-discharge, Task 6 session integrity) and meaningful complementary coverage on smaller items.

The R2 pass **earned its keep** — it caught 4 real items R1 missed (the manifest staleness on Task 3, the attribution overstatement and natality-H10-row gap on Task 5, the project-wide doc-sync gap on Task 2). It also independently confirmed the most-load-bearing claim (zero canonical mutation; H10 reproducibility) — a cross-validation that single-round audits cannot offer.

**Recommendation: ship the 8-item remediation bundle, then Phase D.**
