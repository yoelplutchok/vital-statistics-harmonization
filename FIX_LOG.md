# FIX_LOG

> **Append-only.** Every bug found during HVS work is logged here as a dated row. Bugs include parsing errors, harmonization mistakes, validator self-blindness, doc-data drift, and cross-product join errors.
>
> Use the bug class IDs from `NEXT_STEPS.md` §8 (mistake-class matrix): H1-H10 (harmonization), F1-F5 (HVS-specific cross-product), L1-L12 (LLM-execution).
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <bug class> — <one-line title>
> **Symptom:** <what was observed>
> **Root cause:** <what was actually wrong>
> **Fix:** <what was changed>
> **Files touched:** <paths>
> **Regression scope:** <which adjacent cycles, products, or tasks were re-verified after the fix>
> **Verified by:** <which validator or test confirms the fix>
> **Could the §8 matrix have caught this earlier?** yes/no + how
> ```

---

## 2026-05-24T00:45:00Z — audit-fix-r1r2-bundle — L6/H8/L7/L11 (cosmetic / labelling / stale-doc-string; ALL already in the §8 matrix, NOT new classes) — 8 doc/CSV-only remediations surfaced by 2 independent fresh-eyes adversarial-audit rounds (R1 + R2; 12 audits total), shipped as ONE remediation task per the C8.20-auditfix precedent

**Symptom:** The 2 independent fresh-eyes adversarial-audit rounds against the 5-task Pre-D cleanup block (R1 6 agents at `AUDITS/*.md`, R2 6 agents at `AUDITS/round2/*.md`) returned PASS / 0 blockers / 0 §7 / 0 gate-SHA drift in BOTH rounds (cf. `AUDITS/CONSOLIDATED_R1_vs_R2_2026-05-19T20-30-00Z.md`), but surfaced an 8-item non-blocking remediation bundle worth shipping pre-Phase-D, mirroring the C8.20-auditfix precedent: **C1** (L7 cosmetic, both rounds convergent) — 19/19 `(perLinkCO<YY>Guide.pdf)` missing-space typo in `natality/metadata/file_inventory.csv` col5; **C2** (H8/L7, both rounds convergent) — `fetal_death/CODEBOOK.md` L12 V2-rebroadening gloss redefines legacy "V2" as 1982-2002, but 3 per-variable Notes (plurality / birthweight / singleton) still use "V2" with 1992-2002-only counts (1,713 / 397,397 / 1,713) → reader risk of mis-scoping; **R1a** (L11-adj) — NEXT_STEPS §15.D C8.18 model-clar block enumerates step 3/5/6 sub-decompositions but omits step 4 → 4a/4b/4c (the entries exist in DECISION_LOG 2026-05-18T14:30/20:30/05:00); **R1b** (cosmetic) — V3b "~200 bytes" tilde-prefix breaks sibling-parity with V2 row's "360 bytes (362 with CRLF)" in `fetal_death/COMPARABILITY.md` L13; **R1c** (soft) — `fetal_death/CODEBOOK.md` L60 `data_year` row dropped the pre-v2.4.0 "verified 1,634,195/1,634,195 in V2.0" clause without v2.4.0 replacement during the `fetal-death-codebook-comparability-v240` re-paragraph; **R2a** (L11/H8 NEW) — `docs/NCHS_SOURCE_MANIFEST.md` L153 + L205 still describe the `imported`-flag refresh as a "tracked Phase-D metadata-sync follow-up — deliberately NOT flipped" — stale since the `file-inventory-imported-flag-v4` task at `84a9af3` (2026-05-23) shipped the flip; **R2b** (L11 NEW) — `docs/PIPELINE_TIMING_BENCHMARK.md` L8 attribution implies the C8.13 fetal-death PROPOSE-EDIT body routes both fetal-death AND natality+linked v4 to D.4, but the PROPOSE-EDIT body at L92-106 is fetal-death-only (the natality clause at L146 is "no edit recommended"); **R2c** (H8 NEW) — `docs/PIPELINE_TIMING_BENCHMARK.md` L5 H10 callout flags the linked-H10-row SHA `9b828a4d…` as superseded but not the natality H10 row (`e16ad532…` is the pre-v3.0.0 anchor; post-C8.17 v3.0.0 derived = `acb5c48a…`).

**Root cause:** Each item is a known §8 class — L6 family / H8 family (doc-data drift) / L7 (cosmetic) / L11 (stale roadmap/doc claim) — surfaced by adversarial audit, not by the runtime / pipeline / test surfaces (which is exactly the audit's job per the C8.20-auditfix precedent: fresh-eyes catch what SHAPE-not-VALUE smokes don't bite). NOT a new class (the audit-consolidated report explicitly classed this verdict; aligns with the C8.20-auditfix LESSONS-skip precedent — "an erroneous LESSONS row would imply the protocol failed; the fresh-eyes audit catching minor representation issues IS the protocol working"). The Pre-D cleanup block itself remains substantively sound: 12/12 audits PASS / 0 §7 / 0 gate-SHA drift / `paper/draft_v2_hmd_styled.md` untouched / append-only state-files intact / Task 4 verify+discharge genuine (both rounds independently re-ran the v3-linked validator + got byte-identical re-renders + confirmed the mutation guard live).

**Fix (root cause, §9-#7 — fix the doc/CSV, not the parquet):** 10 Edit operations across 6 git-tracked files (1 replace_all + 9 single-shot), all doc/CSV-only, zero canonical-state mutation: **Item 1** `replace_all` `(perLinkCO` → `(per LinkCO` in `natality/metadata/file_inventory.csv` (×19; L55-73 col5); **Item 2** apply `tabulation_flag`-style scoping (the audit-recommended approach (2); confirmed at PRE-FLIGHT to be preferred over approach (1) drop-the-gloss because the L12 gloss is load-bearing for the 7-era envelope narrative) — scope each of the 3 affected per-variable Notes (L97 plurality, L116 birthweight, L217 singleton) to "V2 1992-2002 slice" + add an Appendix C8.20 pointer; **Item 3** prepend `**DO step 4 → 4a/4b/4c** (4a 1995-2002 cohort 1989-rev; 4b 2003 cohort 2003-rev DEFLATE64; 4c 2004 cohort 2003-rev dual-cert DEFLATE; DECISION_LOG 2026-05-18T14:30:00Z → 2026-05-18T23:00:00Z).` between the step-3 and step-5 clauses in NEXT_STEPS §15.D C8.18 model-clar block L1403; **Item 4** edit only the 1 doc where `~200 bytes` text actually exists (COMPARABILITY.md L13; CODEBOOK.md does NOT have this text — the audit-spec "×2 docs" over-counted, resolved per Convention 3 cheap-check by not fabricating text where it doesn't exist, L6-safe); `~200 bytes (1978-rev)` → `200 bytes (202 with CRLF)`; **Item 5** append `(verified 2,427,233/2,427,233 in v2.4.0; see Appendix C8.20)` to `data_year` Notes in `fetal_death/CODEBOOK.md` L60 (the audit-spec "L77" → actual L60 line-number resolved per Convention 3 cheap-check — `data_year` per-variable row is at L60; the appendix `data_year` at L357 is C3 OOS/generator-side); **Item 6** at NCHS_SOURCE_MANIFEST.md L153 + L205, replace "is a tracked Phase-D metadata-sync follow-up — deliberately NOT flipped at C8.18 DO step 7" with "**was shipped at the `file-inventory-imported-flag-v4` task** (2026-05-23, commit `84a9af3`); `imported` is now uniformly `true` (95/95) across the natality inventory" + supporting parenthetical; **Item 7** at PIPELINE_TIMING_BENCHMARK.md L8, separate the C8.13-PROPOSE-EDIT-body routing (fetal-death-only, per the body at L92-106) from the scope-note routing (v4 natality+linked re-measure routed by *this scope note*, NOT by the PROPOSE-EDIT body); **Item 8** at PIPELINE_TIMING_BENCHMARK.md L5, extend the H10 callout to flag BOTH the natality (`e16ad532…`, pre-v3.0.0 anchor) AND linked (`9b828a4d…`, pre-v4 anchor) H10 rows as superseded point-in-time figures (with current v4 envelope SHAs `acb5c48a…` + `f630d8cf…`). R2d (other `fetal_death/*.md` V2.0-envelope-staleness — GETTING_STARTED, FAQ, etc.) **explicitly NOT in this bundle** per the audit's recommendation + the user's task-message scoping ("R2d ... too big for a remediation bundle and defers it to a separate doc-sync task"); soft-flagged for a separate Phase-D-adjacent doc-sync pass.

**Files touched:** `natality/metadata/file_inventory.csv` (Item 1), `fetal_death/CODEBOOK.md` (Items 2a/2b/2c/5), `fetal_death/COMPARABILITY.md` (Item 4), `NEXT_STEPS.md` (Item 3), `docs/NCHS_SOURCE_MANIFEST.md` (Item 6 ×2 sites), `docs/PIPELINE_TIMING_BENCHMARK.md` (Items 7+8), + state files (PRE_FLIGHT_LOG / RECEIPT / DECISION_LOG / STATUS). **Zero canonical-state mutation** (4 gate SHAs byte-exact `38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`; no parquet/`harmonized_schema.csv`/validation-target/test/script touched).

**Regression scope:** `git diff --name-only` confined to the 6 expected target files + PRE_FLIGHT_LOG; `git diff --stat` 89 ins / 29 del / 7 files — proportionate to 8 doc edits + a ~60-line append-only PRE-FLIGHT entry. PRE_FLIGHT_LOG append-only invariant preserved (0 deletion lines). Manuscript `paper/draft_v2_hmd_styled.md` untouched (`git diff` empty). No code/test mutation ⇒ no pytest re-run owed; the 355P+1S+1XF baseline from C8.20-auditfix is implicitly preserved (doc-only DO cannot affect test outcomes). The C8.20 generated CODEBOOK appendix block is byte-identical (this task only touched the hand-authored body of CODEBOOK.md outside the marker-delimited appendix; verified by `git diff` line numbers all < L260 except for the L217 singleton row in the Derived-Variables hand-table). 4 gate parquet SHAs byte-exact pre/post (the strongest single-zero-mutation signal).

**Verified by:** per-edit `grep -c` (Item 7 fixed-string re-verify via `grep -Fc` after an initial regex-escape artifact); independent re-hash of 4 gate parquets matching the PRE-FLIGHT baseline byte-exact; `git diff --name-only` scope check; `git diff PRE_FLIGHT_LOG.md \| grep -c '^-[^-]'` = 0 (append-only); numerics derivability check (2,427,233 / 1,713 / 397,397 all parquet-derived from CODEBOOK Appendix C8.20 — L6-safe). RECEIPT `RECEIPTS/audit-fix-r1r2-bundle_2026-05-24T00-45-00Z.md`.

**Could the §8 matrix have caught this earlier?** Mostly yes — the relevant rows (L6/H8/L7/L11) DID hold, and the C8.20-auditfix LESSONS-skip precedent applies verbatim: the fresh-eyes adversarial audit IS the designed defense-in-depth for the subtle non-count/representation/labelling residues a SHAPE-not-VALUE smoke won't bite. The 2 independent rounds working together (R1 found 3 items R2 missed; R2 found 4 items R1 missed; convergent on 2) is the matrix's intended belt-and-suspenders behavior. No new mistake class; no LESSONS.md entry owed. (The 2 Convention-3 cheap-check resolutions — Item 4 ×2→1 doc, Item 5 L77→L60 — are themselves the L17/L13-extension matrix family working: PRE-FLIGHT caught spec-vs-actual divergence before any DO mutation.)

---

## 2026-05-23T15:00:00Z — C8.20-auditfix — L6/H8 (precision/representation loss; in the §8 matrix, NOT a new class) — `_build_codebook_extensions.py` `_fmt_val` `f"{v:g}"` (6 sig-fig) collapsed distinct float64 `record_weight` values into shared frequency-table keys in the linked CODEBOOK sub-appendix (i)/(iii)

**Symptom:** The user-run fresh-eyes adversarial audit `AUDITS/C8.20_20260519T152156Z.md` (Check 4) found **72 formatted keys in the linked sub-appendix `record_weight` (i) value-distribution panel + (iii) code-frame diff each merge 2–3 distinct source float64 weights** (e.g. raw `1.027777`+`1.027778`→`1.02778`; `1.029095`/`1.0291`/`1.029103`→`1.0291`). Verdict: 1 FINDING, minor, non-blocking, no HALT (the other 7 audit checks PASS; no count corruption — per-era `n` still conserves; deterministic). Visible artifacts: an undercounted long-tail `_(+510/397/262 more codes)_` and a meaningless continuous "code frame" diff (`dropped {2}`) for a sampling weight.

**Root cause:** `_fmt_val`'s `isinstance(v, float)` branch returns `f"{v:g}"` (6 significant digits) and is used as the **frequency-table key** for *every* column including continuous floating-point ones. Two compounding design issues: (1) 6-sig-fig formatting is lossy for a genuinely continuous float64 (finely-divided inflation/adjustment weights differ past the 6th digit); (2) more fundamentally, a top-N **frequency table is the wrong representation for a continuous variable** regardless of precision — even a lossless `%.17g` would produce hundreds of count≈1 rows. Class **L6/H8 family (precision/format loss)** — already in the §8 matrix; the audit explicitly classed it NOT a new mistake class ⇒ no LESSONS.md entry (an erroneous LESSONS row would imply the protocol failed; the fresh-eyes audit catching a minor representation issue IS the protocol working).

**Fix (root cause, §9-#7 — fixed the builder, not hand-patched the generated doc):** the builder now detects floating-point columns by pyarrow dtype (`pa.types.is_floating`) and, for those columns only, renders subsection **(i)** as a per-era **exact summary-statistics** table (`n`, non-null, null/blank %, distinct, min, p25, median, mean, p75, max — `_float_summary`, deterministic nearest-rank quantile on the weighted ECDF, `%.6g` scalar format with the method disclosed inline) and **(iii)** as a "continuous numeric — no discrete code frame" line. Subsection **(ii)** (sentinel disambiguation) is unchanged (still the `_fmt_val` Counter ⇒ byte-identical; `99.9` BMI sentinel still flagged). Stats are over raw non-null values (no §7-#7 sentinel-as-data presumption; sentinels stay in (ii), pointer note added). Blast radius: exactly 2 variable blocks, both in `natality/docs/CODEBOOK.md` — `bmi_prepregnancy` (f32) + `record_weight` (f64); `fetal_death/CODEBOOK.md` has 0 float cols ⇒ byte-identical. A SHAPE-not-VALUE float Tier-0 fixture was authored + run red **before** the builder edit (§9-#9). Decision rationale (root-cause vs the audit's accept-as-doc / widen-format options): DECISION_LOG 2026-05-23T15:00:00Z.

**Files touched:** `scripts/_build_codebook_extensions.py` (`import math`; new `_float_summary` + `_fmt_stat`; `render_appendix` float branch for (i)/(iii) + 2 new kwargs; `scan_product` float-col detect + raw multiset + 4-tuple return; 3 `main()` call sites), `tests/test_codebook_extensions_smoke.py` (2 new float Tier-0 tests), `natality/docs/CODEBOOK.md` (regenerated marker block — 2 var blocks changed). **Zero canonical-state mutation** (no parquet/`harmonized_schema.csv`/validation-target/metadata-CSV; 3 gate SHAs byte-exact `185c071ec76a`/`acb5c48a9abf`/`f630d8cf20db`).

**Regression scope:** full memory-safe per-file pytest split (34 files) = **355P + 1S + 1XF** = the STATUS C8.20 baseline 353P+1S+1XF **+2** (exactly the 2 new intended float Tier-0 tests); zero failures/errors. Determinism `--check ×2` over the full ~350M-row envelope → both `WOULD-CHANGE: (none)` (§15.D criterion + audit Check 5 preserved). `fetal_death/CODEBOOK.md` + both `FAQ.md` byte-identical. n-conservation invariant (audit Check 2) preserved (per-era `n` = era rowcount). No adjacent product/year affected (fetal appendix byte-unchanged; non-float natality/linked vars byte-identical).

**Verified by:** `tests/test_codebook_extensions_smoke.py` (8P incl. exact hand-fixture `_float_summary` + SHAPE float-render asserts); independent recompute VERIFY-H (DuckDB + independent numpy nearest-rank, NOT importing the builder) byte-matched 3 eras' rendered `record_weight` cells incl. n/distinct/min/p25/median/mean/p75/max; `git diff --name-only C8.20-auditfix-pre-do` scope; `--check ×2` determinism; gate-SHA byte-exactness. RECEIPT `RECEIPTS/C8.20-auditfix_2026-05-23T15-00-00Z.md`.

**Could the §8 matrix have caught this earlier?** Partly. L6/H8 is the right class and the matrix's "Caught at: RECEIPT (auto-generate every numeric…)" did hold — every number WAS parquet-derived; the gap was *representation* (frequency table for a continuous var) + *display precision*, which the C8.20 SMOKE (SHAPE-not-VALUE by design) intentionally does not pin. The fresh-eyes adversarial audit is the designed defense-in-depth for exactly this (a subtle, non-count, representation issue a SHAPE smoke won't bite) and it worked. No matrix sharpening owed (the audit + this entry + the DECISION_LOG fully capture it; it is not a recurring new class).

## 2026-05-23T02:00:00Z — C8.18 DO step 6b — L17 — `test_parquet_column_snapshot.py` `EXPECTED_TOTAL=340` / `EXPECTED_COLUMN_COUNTS[linked]=94` stale count-pins: the PRE-FLIGHT L17 grep-scope enumerated the named release-state pins but missed the snapshot test's own derived-shape count constants

**Symptom:** At the C8.18 DO step 6b VERIFY-E, the FIRST authoritative consolidated 4-dir re-baseline (`/tmp/c8_18_s6/pytest_FINAL_6b.log`) reported `test_parquet_column_snapshot.py :: 2 failed, 4 passed`. `test_baseline_anchor_row_count` (`assert len(rows) == EXPECTED_TOTAL` → 343 vs 340) + `test_baseline_per_parquet_column_counts` (`natality_v3_linked_harmonized_derived` 97 vs the pinned 94) failed; all 4 `test_per_column_sha_matches_baseline[*]` sub-checks PASSED (no content drift / no hash non-determinism — the v3 baseline correctly captures the v4 parquet). Compounding process miss: an earlier memory-safe per-file run's (`bk0mhj9cs`) terse summary format printed only `P=4` for that file (the failed count not surfaced) and the run's single ANYFAIL flag was attributed solely to the (separately-fixed) `test_cross_product_join_parity.py`, so the receipt was briefly drafted with VERIFY-E=345 / snapshot=4/4 before the authoritative consolidated run + the §4.4 commit-gate corrected it.

**Root cause:** The C8.18 DO step 6b PRE-FLIGHT L17 grep-scope (forward-HALT #9 / the §4.2.1-Convention-2-L17 same-commit re-pin discipline) enumerated the *named release-state pins* — `test_row_count_conservation.py`'s `LINKED_EXPECTED_TOTAL`/`LINKED_EXPECTED_YEARS` + the B.12 snapshot CSV regeneration — but did NOT enumerate `test_parquet_column_snapshot.py`'s OWN derived-shape count constants `EXPECTED_TOTAL` (340 = 73+89+84+94) and `EXPECTED_COLUMN_COUNTS["natality_v3_linked_harmonized_derived"]` (94). These are sibling L17 `tracks-current-state` pins in the same test-infra family: the authorized v3→v4 re-harmonize adds 3 linked columns (link_segment + underlying_cause_icd9 + cause_recode_61: 94→97; total 340→343), which the per-column-SHA re-snap correctly reflects but the two hardcoded count constants did not. Not a data/harmonize defect (per-column SHA sub-checks PASS; the harmonize is proven correct by every §15.D gate).

**Fix:** Re-pinned, SAME commit as the v4 canonical mutation (the L17 prescribed response): `EXPECTED_COLUMN_COUNTS["natality_v3_linked_harmonized_derived"]` 94→97; `EXPECTED_TOTAL` comment 340→343; `test_baseline_anchor_row_count` docstring + f-string `73+89+84+94`→`73+89+84+97`; the module docstring "340 ... 73 + 89 + 84 + 94"→"343 ... 73 + 89 + 84 + 97"; added a `tracks-current-state` (Convention 2 / L17) provenance comment naming the v3→v4 cause + the FIX_LOG ref. Re-ran `test_parquet_column_snapshot.py` → 6/6. The authoritative artifact moved to `/tmp/c8_18_s6/pytest_FINAL2_6b.log` (snapshot + cross_product both green) → **347 passed, 1 skipped, 1 xfailed, 0 FAILED**.

**Files touched:** `tests/test_parquet_column_snapshot.py` (the 2 count constants + 3 docstring/f-string strings + a provenance comment). No data/parquet/schema/harmonize change.

**Regression scope:** `test_parquet_column_snapshot.py` 6/6 post-fix; the full 4-dir consolidated re-baseline 347P+1S+1XF/0-FAILED (`pytest_FINAL2_6b.log`). Sibling L17 re-pin to the `test_row_count_conservation.py` LINKED re-pin (same commit). No adjacent products/years affected (FD + natality_v2 per-column SHAs byte-identical; only the linked-derived block grew by 3 columns by design).

**Verified by:** `uv run pytest tests/test_parquet_column_snapshot.py -q` → 6 passed; the consolidated `pytest_FINAL2_6b.log` 0-FAILED; the per-column SHA sub-checks confirm the v3 baseline ↔ v4 parquet consistency (no content drift).

**Could the §8 matrix have caught this earlier?** Yes — this IS **L17**, and the L17 matrix's "Caught at: VERIFY (focused defense-in-depth re-probe at the cheap-check moment)" worked: the authoritative consolidated VERIFY-E surfaced it and the §4.2.1-Convention-2-L17 "bundle the minimal Edit into the same commit as the canonical mutation" prescribed the fix. The gap was upstream — the PRE-FLIGHT L17 grep-scope under-enumerated (named release-state pins only, not the snapshot test's derived-shape count constants). A §11 L17 sharpening is owed: "the L17 PRE-FLIGHT grep-scope MUST enumerate test-infra `EXPECTED_*`/`*_TOTAL`/`*_COUNT` literals that derive from a mutated parquet's shape, not only the named release-state pins; and the per-file kill/fail-detection harness MUST print each file's full summary incl. the failed count (never hand-summate a split run into a VERIFY-E pass)." Carried to the pending LESSONS §11 human-merge (alongside the L13-extension-shared-CSV sharpening).

## 2026-05-23T02:00:00Z — C8.18 DO step 6b — L13-extension — `compare_external_targets_v3_linked.py` ValueError'd on the cohort_* metric_ids + would mis-compute the pre-2005 cohort `resident_births`/`imr_per_1000`: DO step 6a added 95 pre-2005 cohort + cohort-only rows to the SHARED targets CSV this v3-NVSR validator reads, without scoping the validator to its 2005-2023 owned surface

**Symptom:** At the C8.18 DO step 6b VERIFY ("existing 33/35 + 2 docs preserved" §15.D criterion), running the canonical v3 validator `compare_external_targets_v3_linked.py` against the v4 parquet (a) **crashed** — `ValueError: Unsupported metric_id='cohort_den_file_records'` (the FIRST cohort_* row it hit; `load_targets` `raise`d on any metric_id ∉ SUPPORTED_METRICS); and after a skip-unknown-metric patch, (b) reported **61 pass / 12 fail** where all 12 fails were the pre-2005 keyless 1983-1988 `resident_births`/`imr_per_1000` rows (e.g., 1983 resident_births actual 3,377,387 vs expected 3,639,113; 1985 +39,145 == exactly the 1985 num count) — the v3-NVSR validator's resident-count logic has no `link_segment` (keyless den+num two-segment) / RECWT-weighting (1983-1984) logic, so it over/mis-counts the pre-2005 cohort cells.

**Root cause:** A 6a integration gap (latent in completed 6a work; surfaced at the 6b end-to-end VERIFY). DO step 6a (2026-05-21) added 95 additive rows — `cohort_den/num_file_records`, `resident_infant_deaths`, and the pre-2005 years of `resident_births`/`imr_per_1000` (1983-2004) — to `external_validation_targets_v3_linked.csv`. That CSV is a **SHARED** targets file: it carries BOTH this v3-NVSR validator's 2005-2023 shipped-product surface AND the C8.18 cohort backward-extension gates (the cohort guide control totals + published-comparability, verified by the C8.18 DO-step VERIFY — the 6a bespoke H6 verify / 6b `verify_6b_peryear.py`, NOT this script). 6a did not scope the v3 validator to its owned surface (it `raise`d on unknown metric_ids and had no year-bound), so once the v4 parquet (1983-2023) + the shared CSV (1983-2004 rows) met at 6b, the validator both crashed and mis-applied its 2005-era logic to the keyless pre-2005 cohort. NOT a harmonize/data defect — the harmonize is proven correct (cohort_den byte-exact 19/19; resident_births byte-exact 19/19 incl. weighted 1983-1984; published IMR within ±0.02 all 19; 2005-2023 byte-clean vs `.v3_baseline`; the DO-step VERIFY `verify_6b_peryear.py` PASS).

**Fix:** Scoped `load_targets` in `compare_external_targets_v3_linked.py` to this validator's **owned surface = the 2005-2023 shipped-product NVSR cells**: skip-with-disclosure (not crash, not mis-compute) any row whose `metric_id ∉ SUPPORTED_METRICS` OR whose `data_year < 2005` (the entire C8.18 pre-2005 cohort backward-extension surface — the keyless 1983-1988 link_segment era + the 1983-1984 RECWT-weighted den + the 1989-2004 denominator-plus — is verified by the C8.18 DO-step VERIFY, the 6a-established bespoke per-year cohort verification pattern). An explicit `[load_targets] SKIPPED <n> rows of <k> non-owned metric_id(s) [...]` disclosure line prints the skipped set (split `metric:` vs `pre2005-cohort:`). L14-safe: the validator still exits non-zero on any per-row FAIL within its OWNED 2005-2023 surface; the skipped pre-2005 cohort surface is fully verified by the DO-step VERIFY (not silently passed here). Post-fix: **35 pass, 0 fail, 0 missing** (== the canonical shipped-product "33/35 byte-exact + 2 cells within documented tolerance" state, unchanged by the v4 re-harmonize). No harmonize/data/schema change.

**Files touched:** `natality/scripts/05_validate/compare_external_targets_v3_linked.py` — TWO owned-surface scopings: (1) `load_targets`: the `raise`→skip-with-disclosure + the `data_year < 2005` scope + the disclosure print (the targets-comparison table); (2) `main()`: the MD "IMR trend" table `all_years` scoped to `>= 2005` + the section-header + a Notes pointer (a naive unweighted den+num trend row for the keyless 1983-1988 in this shipped MD would misstate the published-comparable cohort figures — §9-#2/L6; the pre-2005 cohort per-year figures are the DO-step VERIFY's domain). The regenerated `natality/output/validation/external_validation_v3_linked_comparison.md` now has BOTH tables scoped to 2005-2023 (35 pass, 0 fail) + the pre-2005 pointer note. No data/parquet/schema/harmonize change.

**Regression scope:** The 2005-2023 owned surface re-verified post-fix = 35 pass / 0 fail (the canonical 33/35+2-docs state preserved on v4; consistent with the independent 2005-2023 byte-clean-vs-`.v3_baseline` regression check, all 10 anchor columns byte-identical, 74,943,824==74,943,824 rows). The pre-2005 cohort surface (1983-2004; 19 years) is fully covered by the DO-step VERIFY `verify_6b_peryear.py` (PASS — den+num byte-exact with the documented numerator-residual tolerance, resident_births byte-exact, IMR within ±0.02, weighted 1983-1984 byte-exact). The `tests/mutations/test_compare_external_targets_v3_linked_mutation.py` adversarial mutation test re-run in the 6b full pytest re-baseline (mutates an owned 2005-2023 cell — unaffected by the pre-2005 skip scope).

**Verified by:** `uv run python natality/scripts/05_validate/compare_external_targets_v3_linked.py --in ~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` → exit 0, "Results: 35 pass, 0 fail, 0 missing", the `[load_targets] SKIPPED 95 ... [metric:cohort_den_file_records=19, metric:cohort_num_file_records=19, metric:resident_infant_deaths=19, pre2005-cohort:imr_per_1000=19, pre2005-cohort:resident_births=19]` disclosure line; + the 6b full 4-dir pytest re-baseline; + the DO-step `verify_6b_peryear.py` covering the skipped pre-2005 surface.

**Could the §8 matrix have caught this earlier?** Partially — **L13-extension** (a SHARED inventory/targets CSV extended at task N with rows a downstream consumer at task M doesn't own; the sibling of FIX_LOG 2026-05-12T01:30Z / 2026-05-12T22:00Z / 2026-05-13T08:30Z monorepo-path-drift fix-on-contact entries). 6a's PRE-FLIGHT/receipt added the 95 rows + used a bespoke H6 verify but did not enumerate the downstream consumers of the shared `external_validation_targets_v3_linked.csv` (the v3 validator + its mutation test) and confirm they tolerate non-owned rows — the L13 "enumerate downstream consumers of a shared declarative file at write time" discipline. Fixed on contact here (the documented fix-on-contact class; no §7 halt — not a harmonize/data/validity defect; the harmonize is proven correct). A §11 sharpening of L13-extension to explicitly name "shared targets/inventory CSV — at write time, verify every downstream reader skips-or-supports non-owned rows" is owed (carried to the LESSONS §11 human-merge already pending).

**Symptom:** C8.17 DO step 5a parser run on `Nat1968.zip` wrote 1,750,782 rows to `natality_1968_raw.parquet`, NOT 1,772,133 as `natality/metadata/file_inventory.csv` row 1968 claimed (DO step 2 entry 2026-05-14T08:30:00Z). Difference = −21,351 records (−1.2%). Cross-check via direct line-iter probe of `NATL1968.PUB` (uncompressed 145,314,906 bytes) confirms the file contains exactly 1,750,782 lines, ALL 81 bytes long, ZERO empty lines, ZERO length-mismatch lines. Per-record block size on disk = 83 bytes (81 data + 0x0d 0x0a terminator), not 82 as DO step 2 arithmetic assumed (verified via hex-dump at file positions 81-82 = `0d 0a`).

Verification across all 22 pre-1990 years (`file_size // block_size` for each year, where block_size = data_len + 2 for the CR/LF terminator):

| Year | Block | file_size / block | Inventory claim | Delta |
|---|---|---|---|---|
| 1968 | 83 (81+2) | 1,750,782 | 1,772,133 | **−21,351** |
| 1969 | 217 (215+2) | 1,800,103 | 1,800,103 | 0 |
| 1970 | 217 | 1,868,900 | 1,868,900 | 0 |
| 1971 | 217 | 1,781,774 | 1,781,774 | 0 |
| 1972 | 217 | 1,749,402 | 1,749,402 | 0 |
| 1973-1979 | 217/215 | matches | matches | 0 |
| 1980 | 217 | 3,310,301 | 3,310,301 | 0 |
| 1981 | mixed | n/a (verified separately) | 3,319,054 | 0 |
| 1982-1988 | 217 | matches | matches | 0 |
| 1989 | 352 (350+2) | 4,045,693 | 4,045,693 | 0 |

Only the 1968 row drifts. All 21 other years' claims are byte-exact.

**Root cause:** C8.17 DO step 2 DECISION_LOG choice 5 (2026-05-14T08:30:00Z, DECISION_LOG.md:129) wrote: *"1968 (NATL1968.PUB = 145,314,906 bytes ÷ 82 = 1,772,133 records — 81 data + \\r\\n terminator)"*. The divisor 82 treats `\\r\\n` as a 1-byte terminator (LF only) while still naming it `\\r\\n`. The 1969-1971 arithmetic in the same choice correctly used divisor 217 (= 215+2) — so the inconsistency was within a single DECISION_LOG bullet. For 1968 specifically the off-by-one math (`/82` instead of `/83`) inflates the record count by ~1.2% (which is exactly 1 in 83 records, or equivalently 1 byte / 83-byte block treated as 1 record's worth of mass).

This is a textbook L13-class error: the inventory CSV recorded a file claim that was never column-content-verified against the actual data. The DO step 2 session's L13-extension probe verified value-distributions on 5,000-record samples (CSEX / DMAGE / DBIRWT / DPLURAL / MRACE / BIRATTND distributions all PASS) but did NOT line-count the file. C8.17 DO step 5a is the first session to actually iterate every record from `NATL1968.PUB` end-to-end, which is when the discrepancy surfaced.

**Fix:** Updated 2 references to the wrong 1968 count:

1. `natality/metadata/file_inventory.csv` row 2 (1968): `1,772,133 records` → `1,750,782 records` in the `file_format` column + added a `notes`-column inline correction pointing to this FIX_LOG entry.
2. `natality/scripts/01_import/field_specs.py:100` (1968 docstring): `(1,772,133 records; ~50% US sample)` → `(1,750,782 records; ~50% US sample)`.

The append-only DECISION_LOG.md:117/129/148 (DO step 2 entry) and STATUS.md:223/233/286/331 (DO step 2 section) sections are NOT edited — per §3 append-only discipline, corrections go in new sections. This FIX_LOG entry + the next STATUS section (DO step 5a close) document the correction; future readers can trace the wrong-count narrative in the historical sections back to this fix.

**Files touched (this fix):**
- `natality/metadata/file_inventory.csv` — 1968 row file_format + notes columns updated
- `natality/scripts/01_import/field_specs.py` — 1968 docstring comment updated

**Regression scope:** None for the canonical parquets (no fetal-death / natality v2.8.0 / linked v3 / matched-multiples row touches the 1968 inventory figure). The 1968 row count was an INVENTORY-DOCUMENTATION value, not a value that gates any pipeline step or test assertion. The C8.17 DO step 6 re-harmonize will use the empirical parser output (1,750,782) regardless of the inventory claim. Cumulative envelope 1968-1989 = 62,363,152 records (corrects the STATUS DO step 4 narrative claim of 50,343,996 which was a separate arithmetic slip — soft-flag (x) for narrative-cleanup at next [plan-update]).

**Verified by:**
- `python -c "from zipfile import ZipFile; ..." → 1,750,782 lines, all 81 bytes` (this entry's diagnostic).
- `145,314,906 / 83 = 1,750,781.999...` (arithmetic identity).
- Empirical parser output `natality_1968_raw.parquet` row count = 1,750,782 (DO step 5a primary action).
- Cross-check across all 22 years: only 1968 drifts; all other claims byte-exact (see table above).

**Could the §8 matrix have caught this earlier?** Yes — **L13** ("any inventory row whose role/description names columns without a sibling column-name list is a soft-flag for downstream consumers to re-verify") is the matching matrix row. The defense (line-count the file at inventory write time, not just byte-position-probe + value-distribution-probe) was not applied because the inventory CSV was treated as informational-only at DO step 2. The DO step 2 entry's choice 5 says "These figures land in `natality/metadata/file_inventory.csv` `file_format` column per row and will be cross-checked at DO step 5 + Tier 2 (NCHS Vital Statistics of the United States annual-volume control counts)" — the "cross-checked at DO step 5" framing is exactly what surfaced this. So DO step 2 anticipated the verification, and DO step 5a is the first session to apply it. The fix-on-contact L11 + L13 discipline closes the loop.

**Forward-looking follow-up:**
- The same arithmetic-class error could affect other files where data_len + terminator_len divisors are mixed. The 22-year cross-check above proves no other pre-1990 natality year has the issue. The fetal_death + natality 1990+ + linked + matched-multiples inventory rows were authored from different processes (parser writes "rows= N" directly) so this class of error is bounded to the manual-arithmetic DO step 2 entry.
- The STATUS DO step 4 narrative claim "envelope total 1968-1989 = 50,343,996" is a separate narrative-arithmetic slip — the file_inventory.csv per-row figures sum to 62,363,152 (corrected for 1968: 62,363,152). Soft-flag (x) for narrative-cleanup at next [plan-update].
- DO step 5a's empirical full-file parser is the durable L13 defense for pre-1990 natality going forward: any future record-count regression at C8.17 DO step 6 or later will surface as a parser-vs-inventory delta, exactly like this one did.

---

**Symptom:** C8.12 B.7 L13 audit (PRE_FLIGHT_LOG 2026-05-13T19:30Z Table 2; static probe of `record_length` claim vs actual zip first-record byte length via `zipfile.ZipFile(...).open(name).readline().rstrip(b'\r\n')`) surfaced 19 of 43 rows with documented `record_length` inconsistent with on-disk reality:

| Rows | Status | Claimed → Actual |
|---|---|---|
| 1982-2004 (V3b + V3a + V2 + V2.1; 23 rows) | EXACT | claim matches actual byte-exact (200 / 360 / 1350 / 1500) |
| 2014 (V1 COD; 1 row) | EXACT | 3050 → 3050 |
| 2005, 2007-2013, 2015-2017, 2018-2024 (17 rows) | EMPTY | claim absent; actual probed at 3350 (2005-2006), 801 (2007), 3338 (2008-2013), 3050 (2014-2017), 2651 (2018-2024) |
| 2006 (1 row) | MISMATCH | 3351 → 3350 (off-by-1; with-terminator convention) |
| 2022 (1 row) | MISMATCH | 2652 → 2651 (off-by-1; with-terminator convention) |

The 2007 outlier (801 bytes vs neighboring 3338/3350) is genuine — `Fetal2007US.zip` ships a single 801-byte-record file (`VS07Fetal.PublicUS`, 48.9 MB) with no trailing filler. `field_specs.py:28` already documents `RECORD_LEN_2007 = 801` so the parser correctly handles it; the inventory was just missing the documentation. The 2008-2013 records are 3338 bytes (different from 2005-2006's 3350; another year-specific layout shift the parser handles via `field_specs.py:get_record_layout(year)`). The 2006 + 2022 with-terminator claims (3351, 2652) diverge from the parser's no-terminator convention (`RECORD_LEN_2006 = 3350`, `RECORD_LEN_2018+ = 2651`).

**Root cause:** The `fetal_death/file_inventory.csv` was authored incrementally across multiple sessions (v2.0 = 1992-2022 baseline at 2026-05-04 build; v2.1 = 2003+2004 at 2026-05-11 task3; V3a = 1989-1991 at 2026-05-12 task7_v3a; V3b = 1982-1988 at 2026-05-12 task7_v3b; latest-year = 2023+2024 at 2026-05-13 C8.2). The `record_length` column was populated for the V3b + V3a + V2.1 rows (which were authored from explicit byte-position probes during layout reconstruction) and for select V1 anchor years (2014); empty for the bulk-imported V1 years (2005, 2007-2013, 2015-2024). The 2006 + 2022 +1 discrepancy was authored from NCHS user guides which document logical-record-length-including-CR-LF, while the parser + the other inventory rows use no-terminator. The asymmetric population is a textbook L13 case: the inventory CSV records file roles (year + raw_filename + doc_filename + format + record_length) but column-content verification (does `record_length` match the actual data file's first-record byte length?) was never run as a downstream check until C8.12 B.7.

**Fix:** Patched all 19 affected rows of `fetal_death/file_inventory.csv` to the no-terminator convention matching `field_specs.py` + the existing 24 EXACT rows. Per-year corrected values: 2005=3350, 2006=3350 (was 3351), 2007=801, 2008-2013=3338, 2015-2017=3050, 2018-2024=2651 (2022 was 2652). Single Python-script edit operating row-by-row with `csv.DictReader` + `csv.DictWriter`; column-order + quoting preserved. Post-fix audit: 0 EMPTY, 0 MISMATCH across all 43 rows.

Additionally, authored `tests/test_inventory_invariants.py` (3 tests; `DESIGN: tracks-current-state` first-docstring tag per Convention 2) as the durable defense:

1. `test_fetal_death_inventory_years_match_schema_years_available` — encodes the soft-flag (j) invariant from C8.11 PRE-FLIGHT: every `file_inventory.csv` year ⊆ `harmonized_schema.csv` years_available union, and vice versa. Defends against any future repeat of the C8.11 9-row gap.
2. `test_natality_inventory_years_match_schema_years_available` — sibling invariant for natality + linked-cohort (skips `<YYYY>_linked` keys + parses `2005-2023 (linked)`-style annotation syntax).
3. `test_fetal_death_inventory_record_length_populated_for_all_rows` — defends against any future inventory row shipping with an EMPTY `record_length` cell (the specific bug class fixed by this entry).

**Files touched (this fix):**
- `fetal_death/file_inventory.csv` — 19-row `record_length` patch; new sha=`2f2ba2c942f14296…` (was `38dc035eeccb8b80…` at C8.11 close)
- `tests/test_inventory_invariants.py` (NEW) — 3 L13 invariant tests

**Regression scope:** None. The `record_length` column in `file_inventory.csv` is INFORMATIONAL — it documents per-year byte width for human readers + future-audit reference. The harmonization pipeline reads byte widths from `field_specs.py` (single source of truth at the parser); the inventory column is documentation-only. Patching it brings the documentation into agreement with the parser + the on-disk reality; no data, no validation, no test outcome changes.

Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns **59 passed + 1 xfailed in 77.00s** post-patch (was 56 + 1 pre-C8.12; +3 from the new inventory-invariants tests).

**Verified by:**
- Post-patch audit script re-run: `for row in <43 rows>; do verify claim == actual; done` returns 0 EMPTY + 0 MISMATCH (down from 17 + 2).
- `pytest tests/test_inventory_invariants.py -v` returns 3 PASS in 0.01s.
- `pytest fetal_death/tests/ natality/tests/ tests/` returns 59 PASS + 1 XFAIL byte-exact baseline preserved (the existing 56 + new 3).
- `field_specs.py:21-31` RECORD_LEN_* constants and inventory `record_length` column now agree row-by-row for the 43-year envelope.

**Could the §8 matrix have caught this earlier?** Yes — L13's "any inventory row whose role/description names columns without a sibling column-name list is a soft-flag for downstream consumers to re-verify" is the matching matrix row. The defense (verify column-content matches at inventory write time) was not applied because the inventory CSV is informational-only and never gated a build or test. C8.12 B.7's audit + the new `tests/test_inventory_invariants.py` are the durable defense: any future inventory regression (e.g., a new year row landing with EMPTY `record_length`, or a year-set drift relative to schema) now fails CI immediately.

**Forward-looking follow-up:**
- **The `record_length` invariant test currently checks population only, NOT vs-actual-zip parity** because the raw zips live outside the monorepo at `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/...` (C8.7a soft-flag). A future C8.X (or the C8.7b orchestrator authoring) could promote the zip-presence-aware audit-script (in this entry's audit logic) into a skip-if-missing test that runs from CI when raw zips become available (e.g., via a CI artifact download from the GitHub Release shipped at C8.13).
- **The natality `metadata/file_inventory.csv` does NOT have a `record_length` column** (8 columns vs fetal-death's 9). For symmetry, a future C8.X (Phase D step 2 candidate) could extend natality's inventory schema with `record_length` + populate from the parsers' per-year byte widths.
- **Convention 5 commit-message brevity**: the L13 + L14 patches both land in this commit per the C8.7a "consolidate by script-class" precedent (each FIX_LOG entry is one class; commit message names the cascade depth = 2 classes × 3+19 fixed rows).

---

## 2026-05-13T20:00:00Z — C8.12 (DO step 1, B.8 L14 audit) — L14 (consolidated by script-class per C8.7a precedent) — 3 validators silently returned exit-code 0 on per-row FAILs: `validate_2022.py` + `validate_external.py` + `validate_linked_parquets.py`

**Symptom:** C8.12 B.8 L14 audit (PRE_FLIGHT_LOG 2026-05-13T19:30Z Table 1; static `grep` for `sys.exit`/`raise SystemExit` patterns vs `FAIL`/`failures` surfaces) surfaced 3 of 11 validators that detect per-row FAILs but do NOT propagate to a non-zero process exit code:

| Validator | Per-row FAIL surface | Exit-code behavior pre-patch |
|---|---|---|
| `fetal_death/scripts/05_validate/validate_2022.py` | 19 `"PASS" if ... else "FAIL"` strings inline (one per `check()` call + 12 internal-consistency string assertions) baked into a markdown report at lines 36-37, 91, 303, 314, 322, 327, 334, 339, 344, 351, 356; report written to `output/validation/validation_2022.md` | main() falls through; exit code = 0 even when report contains 19 FAIL lines |
| `fetal_death/scripts/05_validate/validate_external.py` | `failures = [r for r in all_results if not r["pass"]]` collected from `validate_gte20wk_counts` + `validate_mortality_rates` + `validate_2022_detail` + `validate_2022_cod` + `validate_2014_early_late`; printed to stdout via `for f in failures: print(...)` | main() prints failures but does NOT exit non-zero; exit code = 0 even when `failures` non-empty |
| `natality/scripts/05_validate/validate_linked_parquets.py` | `failures = []` populated by 2 stop-ship checks (row-count MISMATCH for any year; IMR out of 3.0-10.0 plausible range); printed under `"## STOP-SHIP CHECKS"` header with `"*** DO NOT PROCEED until resolved ***"` admonition | main() prints + admonishes but does NOT exit non-zero; CI / `run_pipeline.py` orchestrator could not gate downstream on this validator's verdict |

Each case is textbook L14 per §8 matrix row L14: "a reproduction / validation script's per-row CSV has FAIL / `exceeds_tolerance` / `bridge_applicable=False` rows, but `main()` returns 0 (Python: implicit None); CI / PRE-FLIGHT reads exit code only and reports PASS." All three scripts already had per-row truthy-string aggregation (the per-row classifier output is non-empty, e.g., `"FAIL"` literal in the markdown table cell, or `r["pass"] == False` in the `failures` list) — the missing piece was the `sys.exit(1 if n_fail > 0 else 0)` at end of main().

**Root cause:** All three validators were authored as "write a report to disk + print summary to stdout" style scripts where the human reader was the intended audience. Exit-code propagation was never added because the authoring sessions did not anticipate CI / orchestrator integration. The L14 row of §8 matrix (added 2026-05-11T16:32:34Z via the upstream NHANES protocol-sync) named this exact failure mode but no audit had run across the existing validator inventory. C8.12's B.8 audit is that audit.

`validate_external_v2.py` (fetal-death) + `compare_external_targets_v1.py` (natality) + `compare_external_targets_v3_linked.py` (natality) + `validate_v1_invariants.py` (natality) all DO propagate exit codes correctly — they were authored later under awareness of CI gating. The 4 REPORT-ONLY validators (`harmonized_missingness.py`, `key_rates_from_derived_core.py`, `qa_yearly_core_parquet.py`, `validate_row_counts_vs_nchs.py`) have no FAIL surface and correctly skip L14 propagation.

**Fix (consolidated per C8.7a "FIX_LOG entries consolidated by script-class" precedent; 3 single-block edits in this single entry):**

1. **`fetal_death/scripts/05_validate/validate_2022.py`** (end of main(), post-`OUT.write_text`): added 4-line block computing `n_fail = sum(1 for line in lines if "FAIL" in line)`; if `n_fail > 0`, prints `f"*** {n_fail} FAIL line(s) detected — see {OUT} ***"` to stderr + `sys.exit(1)`. The string-aggregation approach is robust because "FAIL" has no common substring with "PASS"; no false positives possible from the report's own PASS strings.

2. **`fetal_death/scripts/05_validate/validate_external.py`** (inside the existing `if failures:` block at end of main()): added `sys.exit(1)` after the per-failure print loop. Reuses the existing `failures` list as the per-row failure indicator; no new aggregation needed.

3. **`natality/scripts/05_validate/validate_linked_parquets.py`** (inside the existing `if failures:` block in the "STOP-SHIP CHECKS" section): added `sys.exit(1)` after the `"*** DO NOT PROCEED until resolved ***"` admonition print. Reuses the existing `failures` list.

All three validators already imported `sys` (used for `file=sys.stderr` etc.) — no new imports needed.

**Files touched (this fix):**
- `fetal_death/scripts/05_validate/validate_2022.py` (+4 lines at main() tail)
- `fetal_death/scripts/05_validate/validate_external.py` (+1 line inside existing `if failures:`)
- `natality/scripts/05_validate/validate_linked_parquets.py` (+1 line inside existing `if failures:`)

**Regression scope:** None. The patched exit-code behavior is a STRENGTHENING of the validator contract: previously the scripts ran clean (exit code 0) regardless of FAIL state; now they exit 1 when FAILs are detected. Downstream consumers reading the exit code (none currently — the validators are typically invoked interactively, not gated in CI) gain a correct signal. The test suite is unaffected: 56 PASS + 1 XFAIL preserved (cache-cleared run, 81.67s).

**Verified by:**
- Visual diff of each patch matches the §8 matrix L14 row's recommended remedy (`sys.exit(1 if FAIL_COUNT > 0 else 0)`).
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns **56 passed + 1 xfailed in 81.67s** post-patch (matches C8.11/C8.12 PRE-FLIGHT baseline 83.55s within run-to-run variance).
- Static re-scan: `for f in <3 validators>; do grep -cE 'sys\.exit\(1\)|SystemExit\(1\)' "$f"; done` → 1, 1, 1 (each validator now has exactly one `sys.exit(1)` propagation point on the FAIL branch).

**Could the §8 matrix have caught this earlier?** Yes — the L14 row was added 2026-05-11T16:32:34Z via the NHANES protocol-sync `[plan-update]`, but the audit (this C8.12 B.8 step) is the first systematic application of the row to the validator inventory. Pre-existing validators that pre-dated the L14 row addition (these 3 are all v2.0-era authoring) carried the bug silently. Defense going forward: C8.6 (CI wiring; SHIPPED) plus a B.6 mutation-test scaffold around each validator (next C8.12 sub-step) gates regressions; CI now runs cache-cleared pytest on every push so any future L14 regression in a NEW validator surfaces immediately. C8.12 B.6 will pair each of the 7 FAIL-surface validators with a `tests/mutations/test_<validator>_mutation.py` that injects a known violation and asserts exit-code 1.

**Forward-looking follow-up:**
- **C8.12 B.6 (next DO step 2-3)**: mutation-test scaffolding for the 7 FAIL-surface validators. Each test injects a known violation (e.g., temporarily edit a copy of `external_validation_targets.csv` to claim an impossible expected count); spawns the validator via `subprocess.run`; asserts `returncode == 1`. The 3 L14-patched validators above are PREREQUISITES for the mutation-test runner because pre-patch they would all return 0 regardless of injection (false-PASS).
- **The `validate_linked_parquets.py` FAIL surface is small** (2 stop-ship checks: row-count MISMATCH + IMR out-of-plausible-range). A future scope expansion could add per-year frequency-sanity checks (FLGND, AGER5, SEX, DPLURAL distributions; IMR trend monotonicity) as separate stop-ship conditions; deferred to a follow-up task.
- **The `validate_2022.py` string-aggregation pattern** (`"FAIL" in line`) is robust for this script but does not generalize to scripts where report text might legitimately mention the word "FAIL" outside per-row classifier output. For C8.12 B.6 mutation-test pairing, the alternative aggregation (refactor `check()` to append to a module-level `_FAILURES: list[str]`) is cleaner; deferred to a future refactor if the script's report content evolves to legitimately mention "FAIL" outside classifier output (e.g., a header section discussing the FAIL concept).

---

## 2026-05-13T08:30:00Z — C8.7a — L13-extension — Two remaining `fetal_death/scripts/` path-constants resolved to non-existent `fetal_death/output/...` paths from monorepo cwd; sibling of FIX_LOG 2026-05-12T01:30Z (harmonize.py + validate_external*.py paths) and FIX_LOG 2026-05-12T22:00Z (test-harness paths)

**Symptom:** C8.7a Tier-0 static path-constant audit (AST-extract + isolated-exec under monorepo cwd; 31 scripts total across `fetal_death/scripts/` + `natality/scripts/`) surfaced **5 broken path-constants across 2 fetal-death scripts** that should have been part of the original 2026-05-12T01:30Z monorepo-migration path-fix pass but were overlooked because no end-to-end audit had been attempted from the monorepo root.

| Script | Path constant | Old resolution (from monorepo cwd) | Status |
|---|---|---|---|
| `fetal_death/scripts/05_validate/validate_2022.py:19` | `PARQUET = Path(__file__).resolve().parents[2] / "output/yearly_clean/fetal_death_2022_raw.parquet"` | `<MONOREPO>/fetal_death/output/yearly_clean/fetal_death_2022_raw.parquet` — does NOT exist (monorepo `output/` is symlinked at root, not at `fetal_death/output/`) | BROKEN ✗ |
| `fetal_death/scripts/05_validate/validate_2022.py:20` | `OUT = Path(__file__).resolve().parents[2] / "output/validation/validation_2022.md"` | `<MONOREPO>/fetal_death/output/validation/...` — same class | BROKEN ✗ |
| `fetal_death/scripts/run_pipeline.py:32` | `REPO_ROOT = Path(__file__).resolve().parent.parent` | `<MONOREPO>/fetal_death/` — resolves, but downstream constants build broken paths from it | MISLEADING (works but misleading name; downstream paths break) |
| `fetal_death/scripts/run_pipeline.py:33` | `RAW_DIR = REPO_ROOT / "raw_data/fetal_death"` | `<MONOREPO>/fetal_death/raw_data/fetal_death/` — does NOT exist; raw zips live at monorepo-root `raw_data/fetal_death/` (symlinked to standalone build-dir) | BROKEN ✗ |
| `fetal_death/scripts/run_pipeline.py:34` | `YEARLY_DIR = REPO_ROOT / "output/yearly_clean"` | `<MONOREPO>/fetal_death/output/yearly_clean/` — does NOT exist | BROKEN ✗ |
| `fetal_death/scripts/run_pipeline.py:35` | `HARMONIZED_DIR = REPO_ROOT / "output/harmonized"` | `<MONOREPO>/fetal_death/output/harmonized/` — does NOT exist | BROKEN ✗ |

If `validate_2022.py` had been invoked from monorepo cwd (e.g., `python fetal_death/scripts/05_validate/validate_2022.py`), it would `FileNotFoundError` on the missing `output/yearly_clean/fetal_death_2022_raw.parquet`. If `fetal_death/scripts/run_pipeline.py` had been invoked from monorepo cwd, it would fail at the first `parse_year(2020)` invocation with a missing-zip error (RAW_DIR points to non-existent `fetal_death/raw_data/fetal_death/`). Neither failure had surfaced to date because (i) both scripts are typically invoked from the standalone fetal-death build-dir (where the path constants DO resolve), and (ii) C8.7a's audit was the first systematic from-monorepo-cwd path probe.

**Root cause:** Both scripts compute their `REPO_ROOT` (or `parents[2]`) anchor as `fetal_death/scripts/<step>/../../...` = `fetal_death/`, then build output paths as `REPO_ROOT / output/...` = `fetal_death/output/...`. In the standalone-build-dir layout this is correct (`fetal_death-harmonization-build/scripts/` + `fetal_death-harmonization-build/output/` are siblings). In the monorepo migration (2026-05-09), the canonical fetal-death subproject became `fetal_death/`, but its `output/` is now symlinked at `<MONOREPO>/output/` (NOT at `<MONOREPO>/fetal_death/output/`). The path anchors weren't updated for this layout shift.

This is the SAME class as FIX_LOG 2026-05-12T01:30Z (harmonize.py + validate_external.py + validate_external_v2.py path-anchor updates) and FIX_LOG 2026-05-12T22:00Z (test-harness conftest + `_regenerate_schema_years.py`). Those prior fixes introduced a `_PROJECT.parent / 'output' / ...` (= MONOREPO_ROOT) anchor convention. The C8.7a audit catches `validate_2022.py` + `run_pipeline.py` as remaining sibling scripts that weren't covered.

**Fix (consolidated per C8.7a's "FIX_LOG entries consolidated by script-class" plan-update decision; both fixes in this single entry):**

1. **`fetal_death/scripts/05_validate/validate_2022.py` lines 19-20**: changed `Path(__file__).resolve().parents[2]` to `Path(__file__).resolve().parents[3]` (bumping the anchor from `fetal_death/` to MONOREPO_ROOT). Both `PARQUET` and `OUT` now resolve to `<MONOREPO>/output/yearly_clean/fetal_death_2022_raw.parquet` and `<MONOREPO>/output/validation/validation_2022.md` respectively — both reachable via the existing symlinks.

2. **`fetal_death/scripts/run_pipeline.py` lines 32-35 + 55**: renamed `REPO_ROOT` to `SUBPROJECT_ROOT` (clarifying its semantic: it points at the `fetal_death/` subproject, not the monorepo); introduced `MONOREPO_ROOT = SUBPROJECT_ROOT.parent`; re-anchored `RAW_DIR`, `YEARLY_DIR`, `HARMONIZED_DIR` to `MONOREPO_ROOT / ...`; updated line 55 `subprocess.run(cmd, check=True, cwd=REPO_ROOT)` to `cwd=SUBPROJECT_ROOT` (preserving the relative `scripts/01_import/parse_fetal_year.py` cmd-path semantics). Added a 3-line comment below `ALL_YEARS` documenting that the 29-year coverage is stale relative to the v2.4.0 43-year envelope (V3a + V3b extension shipped 2026-05-12); ALL_YEARS extension is C8.7b scope (orchestrator authoring), not C8.7a (path audit).

**Files touched (this fix):**
- `fetal_death/scripts/05_validate/validate_2022.py` (post-fix sha=`67a4dfcbfc345c07…`; 1-char × 2 edits)
- `fetal_death/scripts/run_pipeline.py` (post-fix sha=`959ccac48347d2f3…`; ~7 lines edited)

**Regression scope:** None — these were latent bugs surfaced by C8.7a's audit; both scripts are typically invoked from the standalone build-dir where the old anchors are correct. The patched anchors continue to work in the standalone-build-dir context (`SUBPROJECT_ROOT.parent` resolves to whatever the parent dir of `fetal_death/` is, which in the standalone case is the build dir itself, NOT a "monorepo root" — but the `output/`, `raw_data/`, etc. paths are at the build-dir root in that layout too, so the resolution still resolves correctly). The patches are forward-compatible with both standalone-build and monorepo invocation patterns.

**Verified by:**
- C8.7a audit script (`/tmp/c87a_audit_v2.py`) re-run post-fix: 5 path-constant FAILs reduced to 0 (the 1 remaining FAIL is a confirmed false positive — `OUT_SCHEMA = pa.schema([...])` in `natality/scripts/03_harmonize/harmonize_linked_v3.py` is an Arrow schema definition, not a Path).
- 4 parquet SHAs unchanged: fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`.
- 5 C8.5a/C8.6 file SHAs unchanged: pyproject.toml=`c8826a61…`, uv.lock=`ab627034…`, .python-version=`02e735b3…`, README.md=`694fdd35…`, ci.yml=`c248cf51…`.
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns **56 passed + 1 xfailed in 111.83s** (no test-suite regression from the path-constant edits).

**Could the §8 matrix have caught this earlier?** Yes — this is squarely **L13-extension (monorepo migration path drift)**, the same class as the prior 2026-05-12 L13 fixes. The matrix's L13 row + the existing FIX_LOG entries already named the failure mode. The defense gap: no systematic audit had been run from monorepo cwd. C8.7a's static-AST audit is now that defense; it should run as part of CI gating (C8.13 follow-up) so future scripts can't ship with mis-anchored paths.

**Forward-looking follow-up:**
- **C8.7b (DEFERRED)** authors the monorepo-root orchestrator that wires per-step scripts together with correct paths; this entry's audit table (in `RECEIPTS/C8.7a_<UTC>.md`) is C8.7b's PRE-FLIGHT input.
- **C8.7a's audit script (`/tmp/c87a_audit_v2.py`)** is not currently committed (one-shot probe). A future C8.X may promote it to `tests/test_script_path_resolution.py` as a permanent invariant test (probe every entry-point script's path-constants from monorepo cwd at every CI run). Filed as a recommended C8.12 candidate (mutation-tests + L13/L14 audits).
- **Natality scripts `validate_linked_parquets.py` line 26 + `generate_paper_figures.py` lines 21-22 (REPO = parents[2] = `natality/`)** resolve OK in monorepo (the `natality/` directory exists) but their downstream `REPO / output / ...` paths target `natality/output/yearly_clean/`, `natality/output/validation/`, etc., which do NOT exist in the monorepo. These are CLI-driven scripts (`validate_linked_parquets.py` uses `--linked-dir`/`--raw-dir`/`--out-dir` argparse defaults that are broken; the script works when invoked with explicit overrides). C8.7a documents these as DEFERRED-TO-C8.7b (the orchestrator decides whether to (i) add monorepo-root output symlinks for natality + linked, OR (ii) re-anchor natality scripts to MONOREPO_ROOT). Not patched in C8.7a per "fix-on-contact" + "no orchestrator authoring" scope.
- **`fetal_death/scripts/run_pipeline.py` ALL_YEARS=29 is stale** relative to v2.4.0's 43-year envelope (V3a + V3b shipped 2026-05-12). DOCUMENTED in this fix's run_pipeline.py inline comment; ALL_YEARS extension is C8.7b (orchestrator authoring) scope.

---

## 2026-05-12T22:30:00Z — C8.1 (followup) — L17-extension — Test-infra basename collision: `pytest fetal_death/tests/ natality/tests/` errors at collection under default import mode because both subprojects ship `test_schema_dtype_parity.py` and neither directory had `__init__.py`

**Symptom:** C8.2 PRE-FLIGHT (2026-05-12T22:30:00Z) verification of STATUS 22:00Z forward-looking HALT #7 ("16 tests across both subprojects") reproduced an `ImportPathMismatchError` / "import file mismatch" collection error:

```
ERROR collecting natality/tests/test_schema_dtype_parity.py
import file mismatch:
imported module 'test_schema_dtype_parity' has this __file__ attribute:
  .../fetal_death/tests/test_schema_dtype_parity.py
which is not the same as the test file we want to collect:
  .../natality/tests/test_schema_dtype_parity.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename
```

Reproducible after `find . -name __pycache__ -delete`. Each subproject's test directory could be run in isolation (`pytest fetal_death/tests/` → 12 passed, 1 xfailed; `pytest natality/tests/` → 3 passed), but the documented combined run failed at collection. The STATUS 22:00Z claim "VERIFY: full pytest run `pytest fetal_death/tests/ natality/tests/` returns **15 PASSED + 1 XFAIL**" was reproducible **only** with `--import-mode=importlib`, an undocumented flag not part of the recorded command.

**Root cause:** Pytest's default import mode (`prepend`) inserts each test directory at the head of `sys.path` and imports the test module by its bare filename (e.g., `test_schema_dtype_parity`). When two test directories without `__init__.py` files contain modules with the same basename, the second import collides with the first under the same fully-qualified name. C8.1 DO-3 authored `fetal_death/tests/test_schema_dtype_parity.py` and `natality/tests/test_schema_dtype_parity.py` simultaneously without adding the `__init__.py` files that would make them namespace-distinct (`fetal_death.tests.test_…` vs `natality.tests.test_…`). The C8.1 VERIFY step ran `pytest fetal_death/tests/ natality/tests/` in a session where pytest happened to silently succeed (likely via a cached __pycache__ or with a different invocation than what was recorded) but the recorded command does not reproduce that result on a clean run.

This is a class L17 cousin — not a stale-pin per se, but a similar pattern: a test-infrastructure assertion (STATUS's "16 tests across both subprojects") was authored at a moment when it held, then became invalid as soon as the test-discovery environment was reset (clean `__pycache__`).

**Fix:** Added four empty `__init__.py` files to make the test suites proper namespace packages:

- `fetal_death/__init__.py` (NEW; empty)
- `fetal_death/tests/__init__.py` (NEW; empty)
- `natality/__init__.py` (NEW; empty)
- `natality/tests/__init__.py` (NEW; empty)

Under this layout, pytest's prepend mode generates the fully-qualified names `fetal_death.tests.test_schema_dtype_parity` and `natality.tests.test_schema_dtype_parity`, which are distinct.

**Files touched (this fix):**
- `fetal_death/__init__.py` (NEW)
- `fetal_death/tests/__init__.py` (NEW)
- `natality/__init__.py` (NEW)
- `natality/tests/__init__.py` (NEW)

**Regression scope:**
- Searched `git ls-files | xargs grep -lE "^(from|import) (fetal_death|natality)\b"` → zero matches. No existing Python code imports either subproject as a top-level package, so the new `__init__.py` files are inert outside of pytest's test-discovery machinery.
- Dry-imported `fetal_death/scripts/03_harmonize/harmonize.py` via `importlib.util.spec_from_file_location` → loads OK (no breakage from the new `__init__.py`).
- All four __init__.py files are empty; no module-level side effects.

**Verified by:**
- `find . -name __pycache__ -path "*tests*" -type d | xargs rm -rf ; pytest fetal_death/tests/ natality/tests/` → `15 passed, 1 xfailed in 38.77s`. Documented STATUS 22:00Z claim now reproducible under default import mode.

**Could the §8 matrix have caught this earlier?** Yes — this is L17-adjacent. The matrix's L17 row names "SMOKE / test asset hard-codes a mutable annotation value pinned at authoring time; canonical state evolves; pin becomes stale; SMOKE FAILs on a CORRECT subsequent mutation." The bug here is the dual: the test infrastructure's *collectability* (not the asserted values) was pinned at a moment when an environmental side-effect (cached `__pycache__`?) hid the basename collision, and the bug surfaced on a clean re-run. Sharpening L17 to cover test-infra-collectability claims, or adding a defense-in-depth invariant ("every documented `pytest <dirs>` command must reproduce its claimed pass count after `find . -name __pycache__ -delete`"), would have caught this at the C8.1 VERIFY moment. Filed as L17-extension; promotion to a §8 row pending C8.6 CI authoring (where automated cache-cleared runs become the durable defense).

**Forward-looking follow-up:** C8.6 (GitHub Actions wiring) runs in clean checkouts where __pycache__ never exists; the cache-cleared discipline becomes free. No additional `pyproject.toml` config needed (the four `__init__.py` are sufficient).

---

## 2026-05-12T22:00:00Z — C8.1 — H8 (latent surface broader than v2.0 incident) — ~50 fetal-death raw harmonized columns ship as pyarrow `string` while schema declares `type=int`; documented via xfail(strict=True) test pending full reconciliation

**Symptom:** C8.1's new `fetal_death/tests/test_schema_dtype_parity.py::test_full_schema_type_matches_parquet_dtype` test FAILed on first run with **49 mismatches**: harmonized_schema.csv declares `type=int` (or `type=float` for `prepregnancy_bmi`) for ~50 columns; the actual parquet ships them as pyarrow `string`. Affected columns include: `delivery_year`, `maternal_age_recode14/9`, `maternal_race_multi`, `maternal_race_recode6`, `maternal_race_bridged_detail`, `race_hispanic_combined`, `race_hispanic_revised`, `maternal_education(_unrevised)`, `marital_status`, `maternal_nativity`, `paternal_age_combined`, `paternal_age_recode11`, `live_birth_order`, `plurality`, `prenatal_care_*`, `delivery_method_*`, `delivery_route`, `prior_cesarean_number`, `gestational_age_clinical/oe_edited/combined`, `gestational_age_recode12/5`, `oe_gest_recode12/5`, `birthweight`, `birthweight_recode14/4`, `fetal_presentation`, `diabetes_unrevised`, `chronic_hypertension_unrevised`, `pregnancy_hypertension_unrevised`, `eclampsia_unrevised`, `tobacco_*`, `prepregnancy_bmi(_recode)`, `cause_recode124`, `cause_reporting_flag`, `attendant`, `delivery_place_*`, `breech_unrevised`, `gestation_imputed_flag`, `obgest_used_flag`.

**Root cause:** The fetal-death v2.0 release shipped these columns as `object`/string because the parser (`parse_fetal_year.py`) extracts each raw field as a fixed-width string slice and `harmonize.py` passes the values through without per-column dtype enforcement. The v2.0 H8 incident (FIX_LOG 2026-05-11T18:50Z) named 5 demographic/filter columns; the v2.1 closure (FIX_LOG 2026-05-12T01:30Z) cast those 5 (tabulation_flag, residence_status, maternal_age, maternal_race_bridged, hispanic_origin) but did not extend the cast to the remaining ~50. The `harmonized_schema.csv` `type=int` declaration was therefore correct as a *conceptual* statement ("this column holds integer-coded values") but inaccurate as a pyarrow-dtype statement.

**Fix (partial; latent state documented):** C8.1 documents this via `test_full_schema_type_matches_parquet_dtype` decorated with `@pytest.mark.xfail(strict=True, reason=...)`. The marker:
- Lets the test live in the suite without blocking PASS.
- Documents the latent state in the test docstring + the xfail reason.
- Will flip to XPASS=FAIL when a future task closes the issue, forcing removal of the marker (and re-evaluation of whether the closure is intentional).

The **strict regression gate** for the original H8 incident is preserved as `test_v21_h8_fixed_columns_remain_int`: the 5 V2.1-cast columns MUST remain int; revert is caught immediately.

**Files touched (this fix):**
- `fetal_death/tests/test_schema_dtype_parity.py` (NEW; 4 tests including the xfail-marked full-parity test)

**Regression scope:** None — this is documentation of a pre-existing latent state surfaced by the new test. No canonical data state mutated. The xfail discipline prevents the latent state from being silently "fixed" by an unrelated future change without explicit reconciliation.

**Verified by:**
- `pytest fetal_death/tests/test_schema_dtype_parity.py::test_full_schema_type_matches_parquet_dtype` returns XFAIL (expected).
- `pytest fetal_death/tests/test_schema_dtype_parity.py::test_v21_h8_fixed_columns_remain_int` returns PASS — the 5 V2.1-fixed columns are still int.
- Manual probe of natality's harmonized_schema.csv: natality uses pyarrow physical type names directly ('int8'/'int16'/'bool'/'string'/...); the natality parity test passes 3/3 strict matches. fetal-death's generic-name convention is the divergence.

**Could the §8 matrix have caught this earlier?** Yes — this is squarely H8 (docs vs data drift) at broader surface than the original v2.0 incident named. The existing matrix recommends "auto-generate every numeric in every doc from the validation CSVs; if a doc number is hand-edited, accompany it with the inline computation it came from" — the analog for schema CSVs is: every schema `type` value must be auto-derived from the parquet's pyarrow schema (or asserted by a test). C8.1's dtype parity test IS this defense, and would have caught the v2.0 incident at build time if it had existed.

**Forward-looking follow-up:** A future Phase C task (TBD; not in current Tier 1+2 plan) reconciles by either:
- **Option A (canonical recommend)**: cast the ~50 columns to appropriate pyarrow integer widths in `harmonize.py` (extending the existing `_apply_h8_int_cast()`); re-derive the parquet; bump fetal-death version v2.x → v2.x+1; SHA update propagates to PROVENANCE.md and the smoke's EXPECTED state.
- **Option B**: rephrase the schema CSV's `type` column to declare 'str' for the string-shipping columns (lower-cost; preserves shipped parquet SHA; arguably more honest since the values are coded-string anyway like "01" maternal_education). Anti-Pattern #6 schema-version bump still applies.

Recommendation: Option A — restores user expectation that 'int' means int filterable. Probably 1 session.

---

## 2026-05-12T22:00:00Z — C8.1 — L13-extension — Monorepo path drift surfaced in `fetal_death/tests/` (sibling of FIX_LOG 2026-05-12T01:30Z); test harness pointed at `fetal_death/output/...` non-existent path + `_regenerate_schema_years.py` missing in monorepo

**Symptom:** During C8.1 input verification, discovered:
1. `fetal_death/tests/conftest.py` parquet/schema constants pointed at `REPO_ROOT/output/harmonized/...` where `REPO_ROOT = fetal_death/`. The monorepo has no `fetal_death/output/` directory; only `output/` at top level (symlinks to standalone-build dir). All smoke tests would `pytest.skip` cleanly (per `_require()` skip-if-missing protocol) — silently failing.
2. `fetal_death/tests/test_release_smoke.py` line 48 imports `from _regenerate_schema_years import compute_years_available`, with sys.path insert pointing at `fetal_death/scripts/`. That file did not exist in the monorepo — only in the standalone build dir's `scripts/`. Test discovery would `ImportError` before any test could run.

Both bugs latent since the 2026-05-09 monorepo migration commit `7fd9cdf`. Same class as FIX_LOG 2026-05-12T01:30Z (harmonize.py + validate_external*.py paths drift) — that fix surfaced 3 cases; C8.1 surfaces 2 more in the test harness.

**Root cause:** Same as the prior L13-extension entry: the monorepo migration treated `fetal_death/` as a static archive (data + docs) rather than a fully-runnable subproject; path-constant updates were applied to runtime scripts (harmonize/validate/derive) but not to the test harness.

**Fix:**
1. Copied `_regenerate_schema_years.py` from `~/Desktop/fetal-death-harmonization-build/scripts/` into `fetal_death/scripts/` with monorepo-adapted paths (`_SUBPROJECT_ROOT.parent / "output/harmonized/..."` instead of `REPO_ROOT / "output/harmonized/..."`; `_SUBPROJECT_ROOT / "harmonized_schema.csv"` instead of `REPO_ROOT / "metadata/harmonized_schema.csv"`).
2. Updated `fetal_death/tests/conftest.py` constants: introduced `SUBPROJECT_ROOT` + `MONOREPO_ROOT` distinction; `HARMONIZED_PARQUET = MONOREPO_ROOT / "output/harmonized/..."`; `SCHEMA_CSV = SUBPROJECT_ROOT / "harmonized_schema.csv"`. Updated `_require()` error-path `relative_to` to use `MONOREPO_ROOT` with graceful fallback.

**Files touched (this fix):**
- `fetal_death/scripts/_regenerate_schema_years.py` (NEW)
- `fetal_death/tests/conftest.py` (path-constants edit)

**Regression scope:** Test suite was effectively non-runnable in the monorepo before this fix. No prior canonical state was affected (the parquets, schemas, validators all ran from their own correct paths). All 9 existing release-smoke tests now run cleanly (12 PASSED + 1 XFAIL after smoke retag).

**Verified by:**
- `pytest fetal_death/tests/` collects and runs 13 tests (no ImportError); 12 PASS + 1 XFAIL.
- `python3 fetal_death/scripts/_regenerate_schema_years.py --check` returns "OK: schema years_available matches data for all 73 columns" (post-regen).

**Could the §8 matrix have caught this earlier?** Yes — L13-extension (path-drift across monorepo migration) is exactly this class. The prior fix (FIX_LOG 2026-05-12T01:30Z) recommended `scripts/run_pipeline.py` end-to-end smoke from monorepo root as the durable defense — that work is scheduled as **C8.7** in the Phase C plan and will surface any remaining path-drift cases. Authoring a `pytest fetal_death/tests/` run at monorepo-migration acceptance time would have caught these two cases.

**Forward-looking follow-up:** C8.7 (end-to-end pipeline smoke from monorepo root) is the authoritative defense against further path-drift surfaces. CI wiring (C8.6) will gate every PR on a clean test run going forward, preventing new path-drift bugs from landing.

---

## 2026-05-12T13:35:02Z — natality_v28_rename — H8 — 3 doc references to `restatus` survived the v2.8 build-dir rename pass

**Symptom:** Post-sync grep of monorepo `natality/` for `\brestatus\b` returned 3 hits: `natality/README.md:38` (`Residents-only subsets (exclude foreign residents; \`restatus != 4\`)` in a docs file-table cell) and `natality/docs/GETTING_STARTED.md:41 + :50` ("Full file with foreign residents + restatus columns" in V2 and V3 file-table descriptors). All three describe the v2.8-renamed column, but the build-dir rename pass overlooked them.

**Root cause:** The build-dir v2.8 rename pass (DECISION_LOG 2026-05-12T03:25Z 14-step plan) targeted `metadata/harmonized_schema.csv`, scripts (string-literal column-name references), and 6 documented docs (`CODEBOOK`, `COMPARABILITY`, `ABOUT_THIS_RELEASE`, `VALIDATION`, `FAQ`, `GETTING_STARTED`). The pass caught the schema rows + the script string literals + most doc backtick references. It missed:
1. `README.md` was NOT in the 6-docs list (the natality build-dir README was treated as a top-level README, not a "doc"); the `restatus != 4` filter expression on line 38 escaped.
2. `GETTING_STARTED.md` was in the list, but the rename caught backtick `\`restatus\`` patterns and missed two bare-word "restatus columns" instances in narrative-text file-table cells.

**Fix:** Edited the 3 lines in both repos (monorepo `natality/README.md` + `natality/docs/GETTING_STARTED.md`; build-dir `README.md` + `docs/GETTING_STARTED.md`). The grep `\brestatus\b` for monorepo now returns zero hits in `natality/` user-facing docs. (3 other occurrences exist in state files — FIX_LOG entries, STATUS sections, PRE_FLIGHT_LOG — which are append-only historical records and intentionally retain the old name where they describe pre-rename state.)

**Files touched (this fix):**
- `natality/README.md` (monorepo + build-dir)
- `natality/docs/GETTING_STARTED.md` (monorepo + build-dir) — `replace_all=true` caught both lines 41 + 50.

**Regression scope:** None — these are user-facing doc strings; the rename does not affect data, validation, or notebook execution. Caught during the routine post-sync `\brestatus\b` grep that runs as part of the v2.8 close-out's verification gate.

**Verified by:**
- `grep -rn '\brestatus\b' natality/ --include='*.md'` returns no hits.
- Build-dir `grep -rn '\brestatus\b' README.md docs/*.md` returns no hits.
- (Scripts still contain `restatus` as a LOCAL PYTHON VARIABLE — `restatus = _to_int_or_null(_get_col(batch, "RESTATUS"), ...)` — which is intentional per the raw-field-name convention. Output column is `residence_status`. Documented in the natality_v28_rename receipt Self-check item 3.)

**Could the §8 matrix have caught this earlier?** Yes — this is squarely **L4 (LLM forgets to propagate fix to sibling)** + **H8 (docs vs data drift)** in combination. The 14-step plan's doc-edit list was incomplete: it should have included `README.md` as a top-level user-facing doc. The cheap-check that would have caught it before this point: at PRE-FLIGHT time, the Field-value snapshot's "edit surface" enumeration could have used a stronger filter than the targeted-sed patterns — specifically a word-boundary grep `\brestatus\b` across ALL markdown in the build dir, not just the 6 listed docs. Proposed plan-update for future schema-rename tasks: the PRE-FLIGHT edit-surface table must specify the regex/grep that enumerates the surface, NOT a curated file list, so that no files are silently omitted from the rename pass. Filed as a residual L4-class catch; documented for future schema renames.

---

## 2026-05-11T18:50:00Z — task2_joint_use_demo — H8 — fetal-death schema documents `int` dtype for five columns shipped as `object`/string in v2.0.0 parquet

**Symptom:** Task 2 SMOKE Tier 1 produced 0 rows when the filter `(fd["tabulation_flag"] == 2) & (fd["residence_status"] != 4)` was applied to the shipped `fetal_death_derived.parquet`. `JOINT_USE_GUIDE.md` documented the filter with int literals, matching `fetal_death/harmonized_schema.csv`'s `type=int` column for `tabulation_flag` (allowed_values `1-2`) and `residence_status` (allowed_values `1-4`). A naive user copy-pasting the worked example would silently filter out 100% of records.

**Root cause:** The shipped v2.0.0 parquet stores **five** demographic/filter columns as pyarrow `object` (Python `str`) dtype, not `int`:

| Column | harmonized_schema.csv `type` | parquet dtype (verified) |
|---|---|---|
| `tabulation_flag` | `int` | `object` (string `'1'`, `'2'`) |
| `residence_status` | `int` | `object` (string `'1'`, `'2'`, `'3'`, `'4'`) |
| `maternal_age` | `int` | `object` (string `'10'`-`'54'`, `'99'`) |
| `maternal_race_bridged` | `int` | `object` (string `'1'`-`'4'`) |
| `hispanic_origin` | `int` | `object` (string `'0'`-`'9'`) |

Natality v2.7.0 columns covering the same concepts ARE int (`year` int16, `restatus` int8, `maternal_age` int16, `maternal_race_bridged4` int8) — confirmed at PRE-FLIGHT. The drift is fetal-death-only.

**Fix:**
- `docs/JOINT_USE_GUIDE.md` line 51 filter table updated to specify string-literal syntax for fetal-death and int-literal syntax for natality, plus a dtype-caveat paragraph immediately below the table.
- `docs/JOINT_USE_GUIDE.md` worked-example code (lines 92-95) updated to use `tabulation_flag == "2"` and `residence_status != "4"` (string literals).
- `notebooks/joint_use_demo.ipynb` (new in Task 2) uses string literals on the fetal-death side and int literals on the natality side throughout; the dtype caveat is documented in the notebook's intro markdown cell.
- `fetal_death/harmonized_schema.csv` was NOT edited (anti-pattern #6: schema edits require a schema-version bump). A future task will reconcile the schema doc to match shipped state.

**Files touched (this fix):**
- `docs/JOINT_USE_GUIDE.md`
- `notebooks/joint_use_demo.ipynb` (new)
- `notebooks/_build_joint_use_demo.py` (new — deterministic notebook builder)
- `notebooks/README.md`
- This `FIX_LOG.md` entry

**Regression scope:** None — Task 2 surfaced this; no prior task touched these filter columns directly. The natality-side derivation in Task 1 (`build_stratified_denominators.py`) is unaffected (natality columns are int, not object). The fetal-death validation pipeline (`fetal_death/scripts/05_validate/`) is unaffected — it presumably already accommodates the actual shipped dtype since the existing per-year validation passes 29/29 byte-exact.

**Verified by:**
- Section A in `notebooks/joint_use_demo.ipynb` reproduces NVSR 73-09 Table 4 8/8 age cells byte-exact for 2022 using the string-literal filter.
- Section B reproduces 2017 race-stratified joint-use counts cell-by-cell across both denominator paths.
- SMOKE Tier 0 mutation tests verify the corrected string-comparison filter excludes the correct records on a 10-row hand-constructed fixture.

**Could the §8 matrix have caught this earlier?** Yes — this is squarely an **H8 (docs vs data drift)** instance. The schema-doc claim `type=int` was not auto-checked against the parquet's pyarrow schema at validation time. The mistake-class matrix recommends "Auto-generate every numeric in every doc from the validation CSVs; if a doc number is hand-edited, accompany it with the inline computation it came from" — analogously, every shipped harmonized_schema.csv `type` value should be auto-derived from the parquet's pyarrow schema (or asserted by a `tests/` smoke that loads the parquet and compares column dtypes to the schema CSV). Proposed follow-up:

1. Add a `tests/test_schema_dtype_parity.py` smoke harness in `fetal_death/tests/` that reads the parquet, reads `harmonized_schema.csv`, and asserts dtype parity for every row.
2. When the schema-doc reconciliation task lands (schema-version bump), make the parity test the gate that prevents recurrence.

This follow-up is recommended for a future task; not bundled into Task 2 to keep scope tight.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — H8 closure — fetal-death v2.1.0 parquet reconciles 5 demographic/filter dtypes to nullable Int matching the schema CSV

**Symptom (closed):** v2.0.0 `fetal_death_derived.parquet` stored 5 columns (`tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`) as `object`/string despite `fetal_death/harmonized_schema.csv` declaring them as `int`. Open since 2026-05-11T18:50:00Z (Task 2 surface).

**Root cause:** No dtype-parity assertion existed in the parse → harmonize → derive pipeline; the schema CSV's `type=int` claim was unenforced.

**Fix:** Bundled into Task 3 V2.1 build per DECISION_LOG 2026-05-11T20:50Z's data-first sequencing choice. `fetal_death/scripts/03_harmonize/harmonize.py` now applies `_apply_h8_int_cast()` after the per-year concat:
- `tabulation_flag` → Int8
- `residence_status` → Int8
- `maternal_age` → Int16 (matches natality v2.7.0 dtype)
- `maternal_race_bridged` → Int8
- `hispanic_origin` → Int8

Empty strings become `pd.NA`; sentinel ints (e.g., `maternal_age=99`) are preserved. `pd.to_numeric(errors='raise')` fail-loud catches any non-numeric drift.

**Files touched (this fix):**
- `fetal_death/scripts/03_harmonize/harmonize.py` (cast function + module-level dtype map)
- `fetal_death/scripts/05_validate/validate_external.py` (int-literal filter)
- `fetal_death/scripts/05_validate/validate_external_v2.py` (int-literal filter)
- `fetal_death/quickstart.py` (int-literal filter)
- `docs/JOINT_USE_GUIDE.md` (int-literal filter + dtype reconciliation note)
- `notebooks/_build_joint_use_demo.py` (int-literal filter + dtype note)
- `notebooks/_build_paper_companion.py` (int-literal filter)
- `notebooks/joint_use_demo.ipynb` (rebuilt; 9 PASS)
- `notebooks/paper_companion.ipynb` (rebuilt; 34 PASS, 0 FAIL)
- New v2.1.0 parquet: `fetal_death_harmonized.parquet` sha=`333e1e66…d9e0`; `fetal_death_derived.parquet` sha=`55d3d310…c447`.

**Regression scope:** V1-era 2005-2022 byte-clean: 55/55 external validation passes still (validate_external.py); V2-era 1992-2002 13 counts + 8 rates pass (validate_external_v2.py); 2003-2004 NEW 2 counts + 2 rates pass byte-exact against fetaldeath0304problems.pdf Table 1. **Total: 78/78 checks pass** (was 13 counts + 8 rates + 55 V1 = 76 before V2.1; now 13+10+55 = 78). Joint-use demo's 8/8 NVSR Table-4 age-band cells still byte-exact.

**Verified by:**
- `validate_external_v2.py` 23/23 (1992–2004 counts + 1995–2004 rates).
- `validate_external.py` 55/55 (V1 era unchanged).
- `_build_joint_use_demo.py` and `_build_paper_companion.py` re-run; no FAILs.

**Could the §8 matrix have caught this earlier?** It DID (H8 itself was the catch, at Task 2). The follow-up `tests/test_schema_dtype_parity.py` proposed in the 2026-05-11 entry remains valuable but not yet implemented; added to the post-submission queue.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — pre-existing-bug — `data_year` int32 init silently overwritten by crosswalk's `derived` field loop

**Symptom:** After re-deriving the V2.1 parquet, `validate_external_v2.py` returned 0/23 PASS. Root cause: `data_year` column was `object` (empty string) dtype in the harmonized parquet, breaking the int comparison `harm["data_year"] == year`.

**Root cause:** `harmonize_year()` initialized `data_year` as `int32` via `harmonized: dict[str, pd.Series] = {"data_year": pd.Series([year] * len(raw), dtype="int32")}`. The subsequent `for hname, era_map in field_map.items()` loop iterated over every crosswalk row, including the `data_year` row whose `field_2006` (etc.) is the literal string `"derived"`. The loop's else-branch fired (since `"derived"` is not a real raw column), overwriting the int32 series with `[""] * len(raw)` (object empty-string).

**Fix:** Added `if raw_field == "derived": continue` inside `harmonize_year()`'s field-map loop. The int32 initialization is preserved.

**Files touched:** `fetal_death/scripts/03_harmonize/harmonize.py`.

**Regression scope:** This bug presumably existed in v2.0.0 too. v2.0.0 derived parquet's `data_year` dtype: `int32` (verified at `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`, sha `90af89b9…`). So either v2.0.0 ran a different harmonize.py path or `_apply_sentinels` (which v2.0.0 may have used) was repairing the dtype. The latent-bug commit history is not traced; the fix here is forward-compatible and produces int32 in v2.1.0 matching v2.0.0.

**Verified by:** Post-fix harmonize → derive → validate_external_v2.py: 23/23 PASS.

**Could the §8 matrix have caught this earlier?** L7 (LLM accepts plausible-looking output) is closest — the bug went unnoticed because the v2.0.0 validator might have passed even with the wrong dtype, or v2.0.0 used a different path. Adding `tests/test_schema_dtype_parity.py` (per the H8 closure follow-up) would catch this class of bug at build time.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — pre-existing-monorepo-path-drift — `harmonize.py` + `validate_external*.py` paths pointed at non-existent `fetal_death/metadata/` subdirectory

**Symptom:** `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 2003 …` failed with `FileNotFoundError: fetal_death/metadata/variable_crosswalk_working.csv`. Same issue for `validate_external.py` and `validate_external_v2.py`.

**Root cause:** Pre-existing from the monorepo migration commit `7fd9cdf` (2026-05-09). The standalone `yoelplutchok/fetal-death-harmonization` repo had a `metadata/` subdirectory; the monorepo flattened it to `fetal_death/` per PROJECT_STRUCTURE.md but did not update the path constants in the scripts. The bug was latent because the harmonize step had not been re-run from the monorepo yet — the existing v2.0.0 parquet predated the monorepo migration.

**Fix:** Updated `_CROSSWALK_CSV`, `_SCHEMA_CSV`, `_HARM_PATH`, `_DERIVED_PATH`, `_TARGETS_PATH`, `_OUT_PATH`, `_YEARLY_DIR` in:
- `fetal_death/scripts/03_harmonize/harmonize.py`
- `fetal_death/scripts/05_validate/validate_external.py`
- `fetal_death/scripts/05_validate/validate_external_v2.py`

`_PROJECT.parent` (the monorepo root) now resolves to the symlinked `output/` and `raw_data/`; `_PROJECT` (the `fetal_death/` subdir) resolves to the flat metadata layout.

**Regression scope:** None. The scripts had never been runnable from the monorepo state.

**Verified by:** Successful harmonize → derive → validate runs this session.

**Could the §8 matrix have caught this earlier?** Yes — running ANY of the 3 scripts as part of monorepo-migration acceptance testing (`scripts/run_pipeline.py` end-to-end smoke from the monorepo root) would have surfaced this. The original monorepo migration treated `fetal_death/` as a static archive (parquets-and-docs) rather than a runnable pipeline.

**Forward-looking follow-up:** Other scripts in `fetal_death/scripts/` (`parse_fetal_year.py`, `derive.py`, `run_pipeline.py`, `tests/conftest.py`) may have similar path-drift bugs not yet surfaced. Recommended: post-submission, do an end-to-end `scripts/run_pipeline.py` smoke from the monorepo root and fix any path-drift findings as L13-style "fix on contact" patches.
