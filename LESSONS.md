# LESSONS

> **Append-only.** When a new mistake class — one not in `NEXT_STEPS.md` §8 — is encountered, document it here. Then propose a new row for the §8 matrix via the §11 plan-update process.
>
> A "new mistake class" is a failure mode that was not anticipated by the existing matrix and is likely to recur. A one-off typo is not a new class. A pattern that the matrix should have predicted but didn't is a new class.
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <proposed class ID> — <one-line title>
> **What failed:** <the actual incident>
> **Why the existing matrix didn't catch it:** <which row of §8 should have caught it but didn't, and why>
> **What worked:** <how the failure was eventually surfaced>
> **Proposed new matrix row:** <draft row for §8>
> **Backport scope:** <which already-completed tasks should be re-verified now that this class is known>
> ```

---

## 2026-05-12T04:30:00Z — task7_v3b_doc_hunt — L1/L12 — External-resource filename-variant probes should be sibling-derived, NOT hallucinated; prior session's V3b-not-found conclusion was an L1+L12 cascade

**What happened:** The 2026-05-12T03:50:00Z agent probed for 1982-1991 NCHS fetal-death user guides at the NCHS canonical FTP path and reported (STATUS section): "probed `{1982-1991}FetalUserGuide.pdf` at the same FTP path — all returned HTTP 404. Probed alternate doc paths (`fetal_death_inst.pdf`, `Fetal82UG.pdf`, NCHS series_04 paths, `InstructionsManual/InstrFetalDeath.pdf`, etc.) — all HTTP 404. User guides for 1982-1991 are NOT available at the standard NCHS FTP location." That conclusion drove the 2026-05-12T04:00:00Z session to declare V3b "skipped pre-submission per integrity principle."

The conclusion was wrong. This session (2026-05-12T04:30Z, KICKOFF Step 0 retry) probed `<YYYY>FetalUserGuide.pdf` at the canonical FTP path and got HTTP 200 for all 10 years 1982-1991. The naming convention `<YYYY>FetalUserGuide.pdf` is IDENTICAL to the 2003-2022 user guides already on disk in this monorepo (`raw_docs/fetal_death/2003FetalUserGuide.pdf` etc.) — a sibling-derived extrapolation would have tried this exact form first. The prior agent did not.

The prior session's STATUS section labels its probe as `{1982-1991}FetalUserGuide.pdf` (curly-brace expansion in shell). If that was a literal `bash`/`zsh` brace expansion `{1982-1991}` instead of the integer-range syntax `{1982..1991}`, no real probes happened (curly-brace ranges in bash use `..` not `-`). The 404 "result" might have been a typo-mangled probe, not a real test. In any case, the result was reported as authoritative and propagated downstream.

**Why the existing matrix didn't catch it:** Two existing rows are close:
- **L1** (LLM hallucinated file path): the prior agent's `Fetal82UG.pdf`, `fetal_death_inst.pdf` variants were hallucinated filename forms with no sibling-file basis.
- **L12** (LLM trusts its own grep / probe results without verification): the prior agent's 404 result was trusted enough to drive a session-end "V3b skipped" decision; no follow-up cheap-check (e.g., "try the same naming convention as the 2003-2022 files already on disk").

Neither row explicitly names the *sibling-derivation* fix: when probing for analogous files in a known-pattern series, the FIRST candidate filename should be a direct sibling-extrapolation from a file in the series that is known to exist, NOT a fresh guess.

**What worked (within this session):** WebFetch on `cdc.gov/nchs/data_access/vitalstatsonline.htm` — the authoritative NCHS data-access page — surfaced the per-year link list directly, with filename `<YYYY>FetalUserGuide.pdf` matching the sibling convention. Verification via `curl -sI -k` for all 10 years 1982-1991 returned HTTP 200 with valid content-length and last-modified.

**Proposed matrix row addition (L1/L12-extension, or just a sharpening of L1):**

> **L1-extension** — Filename-variant probes for analogous files in a known series MUST begin with sibling-extrapolation, NOT hallucinated guesses. If file `A.pdf` exists at `path/2003<NAME>.pdf` and the question is "does an analogous file for 1985 exist at the same path?", the FIRST probe is `path/1985<NAME>.pdf` — the exact sibling form. Hallucinated variants (`<YEAR>UG.pdf`, `<NAME>_inst.pdf`, etc.) are only tried if the sibling-form probe returns 404. A 404 on the sibling form is a strong signal; a 404 on a hallucinated form is a weak signal that proves nothing.
>
> **Caught at:** PRE-FLIGHT, before any session-end "X is not available" conclusion. Specific catch: every "X is not available externally" claim must be preceded by an explicit sibling-extrapolation probe, logged with the exact URL tried and the HTTP status code. If only hallucinated-variant probes were tried, the claim is "X is not available **via the variants I tried**," not "X is not available."

**Backport scope:**

- The 2026-05-12T03:30:00Z session's "Task 7 input availability" PRE-FLIGHT and the 2026-05-12T03:50:00Z session's user-guide search both surfaced this class of error. Both sessions' artifacts are not corrupted (no harmonization was done on V3b — V3b was correctly deferred, just for the wrong reason). The fix is to revisit the V3b scope decision (DECISION_LOG 2026-05-12T04:30Z proposes the expansion); no parquet rebuild is needed.
- Generalizable to future sessions: when probing for "is X available externally," start with sibling-derived URLs from this monorepo's existing on-disk inventory. The monorepo already has 1992-2022 user guides; the naming convention is uniform; sibling extrapolation backward to 1982 was the obvious first probe.

**Upstream lesson?** Yes. The upstream NHANES protocol's L1 row could be sharpened to add the sibling-extrapolation discipline. Same shape applies to NHANES-internal probing for analogous NHANES public-use documentation in adjacent cycles.

---

## 2026-05-12T01:40:00Z — task3_v21_fetal_death — L13-extension — Layout CSV "anchor-field spot-check" round verifies byte POSITIONS but not field SEMANTICS; semantic mismatch (MAGER vs MAGER41) at identical byte position 89-90 went undetected until value-distribution inspection of harmonized output

**What was discovered:** Task 3 DO step 1 (record_layout_2003.csv + record_layout_2004.csv reconstruction at commit `bb01eaa`, 2026-05-11) inherited bytes 1-797 from `record_layout_2006.csv` and verified anchor fields via "byte-position spot-checks against 2003 user guide pp 13-22 — VERSION, TABFLG, DOD_YY, OSTATE, MAGER, MRACEREC, F_HYSTERu all aligned." The "all aligned" claim verified that the field NAMES present in record_layout_2006.csv appeared at the same byte positions in the 2003 user guide. It did NOT verify that the field SEMANTICS at those positions match. The 2003 file at bytes 89-90 has `MAGER41` (41-category age recode); record_layout_2006.csv at bytes 89-90 has `MAGER` (single-year age). The byte position is identical; the field semantics differ. Because the anchor-spot-check matched on the string prefix `MAGER` (or didn't notice the `41` suffix), the mismatch persisted.

This is **one notch beyond L13** (L13 covers "inventory CSV records file roles before column-content verification"). The semantic-vs-position distinction is the new wrinkle: a layout CSV can be byte-position-aligned with a similar layout AND still be semantically wrong at every position where the underlying field has a different definition.

**Why the existing matrix didn't catch it:** L13 is the closest class. L13 names "inventory CSV's role/description names columns without a sibling column-name list is a soft-flag for downstream consumers to re-verify." The extension: an inventory CSV that names the SAME field-name as a sibling layout but at a position where the source PDF documents a DIFFERENT field-name — even one with a similar prefix — needs to be value-verified, not just position-verified. The value verification means: compute distributions on the parsed yearly_clean parquet and compare them to the user guide's documented value range / sentinel codes for that field name.

**What worked (within the same Task 3 session):** Running harmonize.py on 2003 data and inspecting the `maternal_age` column's distribution. The min=1, max=41, median=16 distribution was obviously wrong for maternal age (mothers under 10 years of age impossible; max=41 too low for the V1 boundary-coded MAGER range 12-50). The cheap-check moved from "look at byte positions in the user guide" to "look at the value distribution in the parsed parquet" — only the latter would have caught the MAGER vs MAGER41 semantic shift.

**Proposed new matrix row (L13-extension):**

> **L13-extension** — Layout-CSV anchor-field check verifies byte position but not field semantics; same field-name appearing at the same byte position in two siblings layouts can hide a semantic re-purposing.
>
> **Caught at:** PRE-FLIGHT (value-distribution check on parsed yearly_clean parquet, not user-guide cross-reference of byte positions). Or downstream: harmonized-output value-distribution sanity check.
>
> **Specific catch:** When inheriting a layout CSV from a sibling year, do not stop at byte-position verification. For each field that is non-trivial (i.e., not BLANK/FILLER), compute the parsed value distribution and verify it matches the user guide's documented value range / sentinel codes. If the distribution is implausible (e.g., maternal age max=41 instead of expected 12-50 range), the field's byte position holds different semantics than the inherited label suggests. Mutation-test: pick one field per layout-inheritance act and verify its distribution against the user guide's documented coding before claiming "all aligned."

**Backport scope:** Within Task 3: 56 harmonizer-read fields cross-checked against 2003 user guide via systematic byte-position match (42 OK, 14 missing-in-2003-guide). Of the 14 missing-in-guide: 11 are blank-OK (R-prefix risk-factor fields don't exist in 2003 layout at those positions; parser reads blank bytes correctly), 3 are real semantic-mismatch (MAGER vs MAGER41 at 89-90 — fixed via harmonize-time omission; URF_ECLAMP vs URF_ECLAM at 337 — same field, naming typo; ESTGEST vs OBGEST at 446-447 — same semantics, naming change). Only MAGER needed harmonize.py intervention; the other two are documentation-only.

Post-submission, the broader backport scope is: rebuild `record_layout_2003.csv` and `record_layout_2004.csv` from the user guides directly (not by inheritance), and similarly value-distribution-verify the `record_layout_2006.csv` claims for V1 era to confirm none of those fields have a similar semantic re-purposing not caught by byte-position checking.

**Upstream lesson?** Possibly. The upstream NHANES protocol's L13 row could be re-worded to add the byte-position-vs-semantics distinction: inventory CSV verification at layout-reconstruction time should always include a value-distribution sanity check, not just byte-position cross-reference.

---

## 2026-05-11T21:50:00Z — task3_v21_fetal_death — L13 — `record_layout_2006.csv` likely incomplete: declares bytes 802-3351 as a single "BLANK" filler block, but 2003/2004 user guides document race fields at bytes 833-847 and 1088-1111 within that range

**What was discovered (not a failure within Task 3 — surfaced as adjacent risk):** Task 3 DO step 1 (record_layout_2003/2004 reconstruction) read the 2003 user guide pages 48-49 and found:
- Bytes 833-847: Mother's Race checkboxes (MRACE1-15), 2003-revision (A) records only.
- Bytes 1088-1111: Mother's Race Edited codes (MRACE1E-8E), declared in layout but empirically empty in 2003/2004 public-use file.

The existing monorepo file `record_layout_2006.csv` (255 data rows) declares bytes 802-3351 as one single row: `BLANK Blank filler to end of record`. If the 2006 user guide also documents the MRACE1-15 + MRACE1E-8E fields at those positions (which is highly likely, since the 2006 layout is the 2003 layout's natural successor in the V1 era), then the 2006 monorepo CSV omits them. This means:
- A reader cross-referencing `record_layout_2006.csv` against the 2006 user guide would find missing race-detail rows.
- The v2.0.0 harmonization may have undercounted multi-race signal for the 2005-2013 V1 era (the bridged race recode at MRACEREC@byte-143 was still used, so per-NVSR-validated outputs are unaffected, but multi-race detail isn't in the shipped parquet).

**Why the existing matrix didn't catch it:** L13 (inventory CSV records file roles before column-content verification) is the closest existing class. L13 names CSV-level role-vs-column mismatches; the 2006 layout case is FILE-INTERNAL — the CSV correctly enumerates many fields but truncates the documentation past a certain byte boundary into a single BLANK row. This is one notch removed from L13 but it's the same shape (a declarative record about a file's structure being incomplete relative to the file's source documentation).

**What worked (within Task 3):** Reading the 2003 user guide pages 48-49 and cross-referencing against `record_layout_2006.csv` at PRE-FLIGHT. The L9 cheap-check on the user guide spent the time to actually look up named fields in the PDF and discovered the mismatch.

**Proposed new matrix row:** L13 already covers this in principle (extended sense). No new row proposed; the upstream NHANES L13 already names "row's role/description names columns without a sibling column-name list is a soft-flag for downstream consumers to re-verify." The HVS variant: when an inventory CSV summarises a byte range as "blank/unused" without enumerating the documented fields the source PDF places in that range, downstream consumers must re-verify before assuming the CSV is complete.

**Backport scope:** Out-of-scope for Task 3 (Task 3 ships V2.1 fetal-death; does not re-derive 2005-2013 V1 era). Post-submission audit pass should:
1. Read 2006 Fetal Death User Guide PDF pages parallel to 2003 user guide pages 48-49 + 13-49 generally.
2. If 2006 user guide documents race detail at the same byte positions, add the missing rows to `record_layout_2006.csv` (with a schema-version comment row referencing this entry).
3. Decide whether to re-derive the V1-era yearly_clean parquets with the additional race fields surfaced. If yes, a separate FIX_LOG entry tracks the parquet-rebuild scope. If no (because the bridged race at MRACEREC@byte-143 is sufficient for harmonization), document the deliberate omission in a fetal_death/COMPARABILITY.md note.

**Related (this same task):** the V2.1 layout (`record_layout_2003.csv` + `record_layout_2004.csv`, shipped this task at sha `a88e1fa3…85635` and `f4ad74ca…77630`) includes a placeholder `MRACE_LEGACY_S` row at bytes 833-836 for S-revision (1989) records. Empirical sampling found digit patterns (e.g. `9009`, `0001`) but the field's NCHS-canonical semantics were not identified during Task 3 (since the V2.1 harmonization uses MRACEREC@byte-143 for race and does not consume MRACE_LEGACY_S). The semantics question is filed alongside the 2006-CSV-completeness audit above for the post-submission pass.

**Upstream lesson?** Possibly. The upstream NHANES protocol's L13 row could be re-worded to explicitly include the file-internal-completeness case (where a CSV declares a byte range as filler/unused but the source PDF documents fields there).

---

## 2026-05-11T16:32:34Z — protocol-sync — n/a (sync, not a new bug class) — Port generalizable conventions from upstream NHANES protocol

**What happened (not a failure — a proactive sync):** The HVS operating protocol in `NEXT_STEPS.md` §1-§13 and `KICKOFF.md` was originally modeled on the NHANES Assay-Bridging `EXECUTION_PROTOCOL.md`. The NHANES protocol has since accumulated five generalizable conventions (dated 2026-05-11 in NHANES `KICKOFF.md`) plus three new mistake-class matrix rows (L13, L14, L17) that are HVS-applicable and not already in our discipline.

**Why this matters now:** Each of the five conventions and three mistake-class rows prevented a real cascade in NHANES work. Carrying them over before HVS hits a similar issue is the cheap option. The protocol-update process in §11 expects this kind of upstream-distillation backport.

**What was applied (single `[plan-update]` commit):**
- `KICKOFF.md`: added "Conventions in effect" block listing Conventions 1-5 (SHAPE-not-VALUE; FROZEN-AT-TASK docstring tag; Field-value snapshot in PRE-FLIGHT; Forward-looking HALTs in RECEIPT; commit-message brevity); refined audit-session framing to point findings at `AUDITS/` and added L17 to the audit's "look for these specifically" list.
- `NEXT_STEPS.md` §4.2.1: SHAPE-not-VALUE rule + DESIGN docstring tag for new SMOKE harnesses.
- `NEXT_STEPS.md` §4.5: commit-message brevity (~5-line summary; full narrative in receipt).
- `NEXT_STEPS.md` §5: Field-value snapshot subsection in PRE-FLIGHT template.
- `NEXT_STEPS.md` §6: Forward-looking HALTs subsection in RECEIPT template.
- `NEXT_STEPS.md` §8: new mistake-class matrix rows L13 (inventory file roles vs columns), L14 (per-row failures not propagated to script exit code), L17 (SMOKE pins stale annotation values).

**What was NOT ported (NHANES-specific, not HVS-applicable):** Cross-family dual-key transcription relaxation (NHANES bridges.csv `transcribed_by_a/b` is not an HVS concept); `halt_c_reprobe.sh` (NHANES-specific named script enumerating its SMOKE harness set); schema `$schema_version` field on `BRIDGES/bridges_schema.json` (HVS uses per-product `harmonized_schema.csv` with a different versioning convention); the V1.9-folate.c.9 series planned-task block (NHANES-specific in-flight work).

**Backport scope:** None — bootstrap is the only prior HVS session, no canonical-state mutations have happened yet. The conventions take effect for Task 1 onwards (joint-use convenience layer; first task to actually mutate a canonical artifact).

**Upstream lesson?** No — this entry is HVS-internal record-keeping of an upstream-to-downstream sync. The upstream lessons are already documented in NHANES `EXECUTION_PROTOCOL.md`.

---

## How this file relates to the natality `HARMONIZATION_LESSONS.md`

The natality project's `natality/HARMONIZATION_LESSONS.md` (when it exists) and the NHANES Assay-Bridging project's `HARMONIZATION_LESSONS.md` are upstream sources of distilled lessons from prior harmonization work. This file is for **HVS-specific** new lessons that emerge as we work on the cross-product joint-use layer, V2.1 transition years, V3 backward extension, manuscript work, and unified Zenodo deposit.

Lessons that turn out to be general-harmonization lessons (not HVS-specific) should also be reported upward — flag them in the entry, and the human can decide whether to propose them as updates to the upstream lessons documents.
