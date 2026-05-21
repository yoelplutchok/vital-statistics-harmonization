# RECEIPT — D.4-paper1-ije-finalize — 2026-05-21T19:00:00Z

**Task.** D.4 / Paper 1 IJE finalization in-session (`NEXT_STEPS.md` §19.1, per user "continue in the session"): trim the main-text body to the IJE 2,500-word limit, confirm Vancouver/Index-Medicus reference conformance, and draft a cover letter. Builds on `D.4-paper1-envelope-sync-complete` (`1db47d3`). Doc-only; **zero canonical-state mutation** (4 gate SHAs byte-exact); git-reversible.

## Five-phase trace

- **PRE-FLIGHT** (`PRE_FLIGHT_LOG.md` 2026-05-21T18:30:00Z; commit `3670690`; tag `D.4-paper1-ije-finalize-pre-do`): per-section word counts (body 3,145); cut plan = redundancy/verbosity only; invariants to preserve = the envelope-sync accuracy guards. No §7 halt.
- **SMOKE** (word-count instrumentation): a whitespace/Word-like counter (strips markdown, excludes footnote refs, treats `tabulation_flag` as one word) used as the proxy for the journal's count, re-run after each batch.
- **DO** — ~30 trim edits across six batches, prose-only:
  - **Batch 1–2** (3,145→2,900): Measures domain list + within-era detail (the per-column reasons were duplicated in S&W → kept once, pointed to schema); Methods normalization illustration; boundary paragraph; fetal-coverage verification sentence; S&W strengths validation sentence (all numbers kept) + weaknesses; Use 3-level verification + joint-use.
  - **Batch 3–4** (2,900→2,626): Coverage enumeration; Methods step 4 (normalization list) + steps 1–3/5/6; Basics opener + reframe connective (reframe + IPUMS/HMD refs kept); Use intro + analyses; Access paragraph; segment-count line; S&W strengths tail; **canonical-filter fix** `restatus`→`residence_status` (the harmonized natality column per the v2.8.0 rename — corrects a pre-existing raw-vs-harmonized name slip).
  - **Batch 5–6** (2,626→**body 2,469 Word-like / 2,541 token**): boundary (ii) clause; sentinel + education-bridge + V1-gap + backward-extension sentences; Future lead-in; fetal-coverage + timing sentences.
  - **Cover letter**: new `paper/cover_letter.md` (≤1 page) leading with the gap → resource → byte-exact validation evidence → public availability (Zenodo DOI + GitHub), per §19.1(g).
- **VERIFY**: (1) **body = 2,469 words** (whitespace/Word-like, footnote refs excluded) ≤ 2,500 IJE limit — PASS. (2) every headline number/DOI/URL still present (201,161,456 / 149,386,620 / 2,427,233 / 1,665,568 ×2 each; DOI; GitHub; 183/183; 33/35; 13 of 19; 13/13; 97 total; reframe; 1968–2024 ×6) — PASS. (3) secondary numbers survived (98,500; ±0.02; 1992–1994; 1351/1501; 29 counts; 26 rates; ~5 min) — PASS. (4) stale-token grep still 0 (incl. `restatus` now 0) — PASS. (5) footnotes: 8 definitions, `[^ipums]`/`[^hmd]` cited + defined — PASS. (6) cover-letter numbers match the manuscript (each ×1) — PASS. (7) `git status` = only `paper/draft_v2_hmd_styled.md` + new `paper/cover_letter.md`. **Zero canonical mutation; 4 gate SHAs byte-exact.**
- **RECEIPT**: this file + DECISION_LOG + STATUS; commit + tag `D.4-paper1-ije-finalize-complete`.

## §19.1 coverage map

- **(b) S&W trim / (c) word audit** → DONE: body 3,145 → 2,469 (≤2,500); S&W condensed (validation evidence kept verbatim). Section spread now Basics 463 / Coverage 280 / Measures 356 / Methods 316 / Use 373 / S&W 454 / Future 153 / Access 146 (token-counter figures).
- **(d) numeric audit** → discharged in the envelope-sync pass + re-verified here (every number traceable to a committed artifact; companion-notebook regen still owed — forward-HALT 1).
- **(f) references** → Vancouver/Index-Medicus conformant: abbreviated journal names (*Obstet Gynecol*, *Am J Obstet Gynecol*, *Semin Perinatol*, *Lancet Reg Health Am*, *Natl Vital Stat Rep*, *Int J Epidemiol*), `authors. title. journal year;vol(issue):pages` form, ≤6-authors-then-*et al.* rule honored; markdown footnotes render as numbered endnotes in citation order.
- **(g) cover letter** → `paper/cover_letter.md`.
- **(a) structure / (e) admin** → no change needed: the draft already mirrors the HMD IJE-2015 template (Abstract → Basics → Coverage → Measures+Comparability → Methods → Use → S&W → Future → Access → "in a nutshell" box → admin) and all admin sections (Ethics / Author contributions / AI disclosure / COI / Funding) are present with `<!-- YP -->` review markers.

## §10 self-check — what could be wrong that VERIFY wouldn't catch?

- **Word-count proxy.** 2,469 is a whitespace/Word-like estimate; the journal's submission system may count a few percent differently. If it reports >2,500, a small further trim (S&W is still the longest at ~454 tokens) closes it. Margin is ~30 words — thin.
- **A non-grepped number altered in a reword.** I grepped all headline + several secondary numbers (all present); a number I did not enumerate could in principle have been touched. Mitigation: the trims were prose-condensation, not number edits; the coherence of the validation sentence (which I kept near-verbatim) is the highest-risk spot and was preserved.
- **`restatus`→`residence_status` correctness.** I changed the natality canonical-filter field name on the basis that the v2.8.0 rename made `residence_status` the harmonized column (CITATION.cff + the manuscript's own joint-use column list both use `residence_status`). If a reader runs the filter against a *raw* (pre-rename) parquet, `restatus` would be the column there — but the manuscript describes the harmonized product, so `residence_status` is correct.
- **Meaning loss from condensation.** Some illustrative detail (e.g., the per-within-era-column reasons) now lives only in the schema/COMPARABILITY, not the manuscript body — by design (those docs are the authoritative home), but a reviewer wanting that detail in-text could ask for it back; it is one git-revert away.

## Forward-looking HALTs for next session

1. **Confirm the Word count in the submission system** before submitting; if >2,500, trim S&W further (it is the longest section and the most condensable without losing numbers).
2. **Companion-notebook regen still owed** (carried from envelope-sync forward-HALT 1): re-run `notebooks/_build_paper_companion.py` on the build host against the v3.0.0/v4.0.0/v2.4.0 + MM parquets to re-discharge the per-claim numeric synthesis.
3. **Author to complete `<!-- YP -->` markers** (affiliation, contact, funding, AI-policy wording) and the cover-letter header (date, address, editor) before submission.
4. **Natality+linked v4 pipeline wall-clock** is still qualitative ("a couple of hours"); replace with a measured figure if a build-host re-run is done.

## Build artifacts current

- `paper/draft_v2_hmd_styled.md`: trimmed to ≤2,500-word body (2,469 Word-like), all envelope-sync numbers/guards/reframe intact, `restatus`→`residence_status` fixed.
- `paper/cover_letter.md`: NEW (≤1 page IJE cover letter).
- **Zero canonical-state mutation**; 4 gate parquet SHAs (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`) byte-exact (manuscript/doc-only).
