# Receipt: audit-fix-r1r2-bundle
## 2026-05-24T00:45:00Z

### What was done

The 8-item R1+R2 cross-round adversarial-audit remediation bundle (canonical task spec: `AUDITS/CONSOLIDATED_R1_vs_R2_2026-05-19T20-30-00Z.md` §6) was shipped as ONE single task under full five-phase discipline (PRE-FLIGHT → SMOKE → DO → VERIFY → RECEIPT), mirroring the established C8.20-auditfix precedent. Doc/CSV-only edits across 6 git-tracked files; **zero canonical-state mutation** (all 4 gate parquet SHAs byte-exact before/after). C2 approach (2) — apply `tabulation_flag`-style scoping to the 3 affected per-variable CODEBOOK Notes — was confirmed at PRE-FLIGHT (no §7 reason to prefer approach (1) drop-the-gloss; the L12 gloss is load-bearing for the 7-era envelope narrative). The 2 cheap-check spec-vs-actual divergences (Item 4 "×2 docs"→actual 1 doc; Item 5 "L77"→actual L60) were resolved at PRE-FLIGHT per Convention 3 by editing the actually-existing sites, not by fabricating text (L6-safe). Manuscript not touched (D.4 by KICKOFF mandate). R2d (other `fetal_death/*.md` V2.0-envelope-staleness) explicitly out of scope per the user's task framing — soft-flagged for a separate Phase-D-adjacent doc-sync task.

### Inputs consumed

- `AUDITS/CONSOLIDATED_R1_vs_R2_2026-05-19T20-30-00Z.md` — canonical task spec (§6 = the 8-item bundle table; §7 + §8 = readiness/recommendation)
- `AUDITS/round2/*.md` (6 files) — R2-unique findings (R2a/R2b/R2c surfaced here, R1 missed)
- `AUDITS/*.md` (6 files) — R1 findings (R1a/R1b/R1c surfaced here, R2 missed)

### Outputs produced (7 git-tracked files modified; 0 created; 0 deleted)

- `natality/metadata/file_inventory.csv` — Item 1 (replace_all `(perLinkCO` → `(per LinkCO` ×19 across L55-73)
- `fetal_death/CODEBOOK.md` — Item 2a (L97 plurality V2 1992-2002-slice scoping), 2b (L116 birthweight V2 1992-2002-slice scoping), 2c (L217 singleton V2 1992-2002 slice scoping), 5 (L60 data_year v2.4.0 verification clause)
- `NEXT_STEPS.md` — Item 3 (§15.D C8.18 model-clar block: insert `DO step 4 → 4a/4b/4c` clause between step 3 and step 5)
- `fetal_death/COMPARABILITY.md` — Item 4 (L13 V3b row: `~200 bytes (1978-rev)` → `200 bytes (202 with CRLF)` — sibling-parity with the L15 V2 row)
- `docs/NCHS_SOURCE_MANIFEST.md` — Item 6 (L153 + L205: imported-flag clauses → "shipped at `file-inventory-imported-flag-v4` task 2026-05-23 commit `84a9af3`")
- `docs/PIPELINE_TIMING_BENCHMARK.md` — Item 7 (L8 attribution rework: separate the fetal-death PROPOSE-EDIT-body routing from the natality+linked scope-note routing), Item 8 (L5 H10 callout extension: flag BOTH natality `e16ad532…` AND linked `9b828a4d…` rows as superseded)
- `PRE_FLIGHT_LOG.md` — new PRE-FLIGHT entry (append-only, +60/-0 lines)

Plus this RECEIPT (`RECEIPTS/audit-fix-r1r2-bundle_2026-05-24T00-45-00Z.md`) + state-file updates to follow (FIX_LOG, DECISION_LOG, STATUS).

### Five-phase trace

- **PRE-FLIGHT**: ✓ `PRE_FLIGHT_LOG.md` 2026-05-24T00:30:00Z. Field-value snapshot for all 8 sites; 4 gate parquet SHAs baseline-recorded byte-exact (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`); 2 Convention-3 cheap-check resolutions logged (Item 4 ×2→1 docs, Item 5 L77→L60). PROCEED.
- **SMOKE**: ✓ Tier-0/1 equivalent for doc-only DO: per-edit anchor-string uniqueness/findability dry-run via `grep -c`. All 10 anchor-strings verified unique-or-replace_all-safe (Item 3 disambiguated via longer "DECISION_LOG 2026-05-17T20:00:00Z). **DO step 5 → 5a/5b/5c**" anchor; Item 6 done as 2 distinct Edits with different surrounding context).
- **DO**: ✓ 10 Edit operations applied across 6 files (1 replace_all + 9 single-shot edits). HEAD pre-DO `17814d2` tagged `audit-fix-r1r2-bundle-pre-do`.
- **VERIFY**: ✓ All 8 items per-edit grep-verified (Item 7 false-fail from regex-escape artifact in initial grep, re-verified PASS with `grep -Fc` fixed-string). 4 gate parquet SHAs byte-exact unchanged. `git diff --name-only` confined to the 6 expected target files + PRE_FLIGHT_LOG (no scope creep). `git diff --stat` 89 ins / 29 del / 7 files — reasonable, no surprise mass-edit. Append-only invariant on PRE_FLIGHT_LOG: 0 deletion lines (purely additive). All cited numerics (2,427,233 / 1,713 / 397,397) parquet-derivable from CODEBOOK Appendix C8.20 (L6-safe).
- **RECEIPT**: ✓ This file. DECISION_LOG + FIX_LOG + STATUS updates to follow before commit.

### Verify results

| # | Criterion | PASS/FAIL | Evidence |
|---|---|---|---|
| 1 | Item 1: 19 `(per LinkCO` post-edit, 0 `(perLinkCO` | PASS | `grep -c` = 19 / 0 |
| 2a | Item 2a: plurality V2 1992-2002-slice clause present; old phrasing gone | PASS | `grep -c` = 1 / 0 |
| 2b | Item 2b: birthweight V2 1992-2002-slice clause present; old phrasing gone | PASS | `grep -c` = 1 / 0 |
| 2c | Item 2c: singleton V2 1992-2002 slice clause present; old phrasing gone | PASS | `grep -c` = 1 / 0 |
| 3 | Item 3: NEXT_STEPS §15.D `DO step 4 → 4a/4b/4c` clause present; sibling step 3/5/6 clauses preserved | PASS | `grep -c` = 1 / 2 / 1 / 1 |
| 4 | Item 4: COMPARABILITY V3b row reads `200 bytes (202 with CRLF)`; old `~200 bytes (1978-rev)` gone | PASS | `grep -c` = 1 / 0 |
| 5 | Item 5: data_year row carries `verified 2,427,233/2,427,233 in v2.4.0; see Appendix C8.20` | PASS | `grep -c` = 1 |
| 6 | Item 6: NCHS_SOURCE_MANIFEST imported-flag-shipped language present ×2 (L153 + L205); old "tracked Phase-D metadata-sync follow-up" gone | PASS | `grep -c` = 2 / 0 |
| 7 | Item 7: PIPELINE_TIMING_BENCHMARK attribution rework present; old conflated language gone | PASS | `grep -Fc` = 1 / 0 |
| 8 | Item 8: PIPELINE_TIMING_BENCHMARK BOTH-H10-rows callout present (`natality e16ad532… AND linked 9b828a4d…`); old single-linked-row phrasing gone | PASS | `grep -c` = 1 / 1 / 0 |
| **INV1** | **Gate parquet SHA invariant: all 4 byte-exact pre/post** | **PASS** | `shasum -a 256`: `38e2cecb03ff4947` / `185c071ec76ab8aa` / `acb5c48a9abf82ac` / `f630d8cf20db72ea` — all unchanged |
| INV2 | `git diff --name-only` ⊆ 6 expected target files + PRE_FLIGHT_LOG | PASS | 7 files modified, all expected |
| INV3 | Append-only on state files (PRE_FLIGHT_LOG): 0 deletion lines | PASS | `git diff PRE_FLIGHT_LOG.md \| grep -c '^-[^-]'` = 0 |
| INV4 | All cited numerics derivable from Appendix C8.20 (L6-safe) | PASS | 2,427,233 (envelope; CODEBOOK L12); 1,713 (plurality=9 1992-2002; appendix L1009); 397,397 (BW=9999 1992-2002; appendix L1591) |

### Reproducibility

- Re-running the same 10 Edit operations against HEAD `17814d2` produces identical post-edit file states (Edit operations are deterministic; old/new strings exact-match). ✓
- The 4 gate parquet SHAs are independent of this task's edits (parquets live in untracked build dirs; doc-only DO cannot mutate them). ✓
- No FIX_LOG regression noted; the task is itself a remediation, so the FIX_LOG entry (to be written) is a forward-cause record, not a fix-of-a-regression.

### Cross-product re-probe (if applicable)

- **Manuscript untouched** (D.4 by KICKOFF mandate; `git diff -- paper/draft_v2_hmd_styled.md` empty — verified post-DO).
- **No script/test mutations** ⇒ no test re-runs owed.
- **No `harmonized_schema.csv` mutations** ⇒ no schema-parity re-probe.
- **No NVSR target CSV mutations** ⇒ no validation re-run.
- **No FIX_LOG-class data/code regression**; doc-only remediation.

### Git

- **Pre-DO tag**: `audit-fix-r1r2-bundle-pre-do` at commit `17814d2` (HEAD before DO).
- **Post-RECEIPT tag**: `audit-fix-r1r2-bundle-complete` (to be set after the DO commit lands).
- **DO commit**: ONE commit ships all 7 file modifications + this RECEIPT + the 3 state-file updates (FIX_LOG, DECISION_LOG, STATUS).

### STATUS.md updated

New section dated `2026-05-24T00:45:00Z` will be prepended (append-only) before the commit, recording task completion + Phase-D-authorization-still-gating.

### Self-check (§10 — what could I have gotten wrong that VERIFY wouldn't catch?)

1. **`data_year` row's stale `Years` column ("1992-2022")**. The L60 row's 4th column still reads `1992-2022`, but the v2.4.0 envelope is 1982-2024. I did NOT fix this (out of audit-bundle scope per §9-#8 "never compress two tasks into one because they go together"; the user explicitly framed R2d-class envelope-sync as a separate task). **Residual risk:** a careful reader reading L60 in isolation could think `data_year` only spans 1992-2022. **Mitigation:** the new verification clause I added explicitly cites "v2.4.0" and "Appendix C8.20", and the appendix's era partition is 1982-2024 (per L275 in CODEBOOK). The CODEBOOK head paragraph L12 already establishes the v2.4.0 1982-2024 envelope. Not a §7 condition. Recommend folding this column-staleness into the future R2d Phase-D doc-sync task.

2. **The Item 4 spec divergence ("×2 docs" → 1 doc) interpretation could have been wrong.** I edited only COMPARABILITY.md. If the audit author actually meant "add a `200 bytes (202 with CRLF)` line to CODEBOOK.md's V3b context too", my fix is incomplete. **Mitigation:** CODEBOOK's variability-matrix table at L36-44 doesn't have a "Record Length" column at all (only "Era / Years / Revision / Records / version_flag" — see L36-44 schema). Adding byte-length to a row that lacks the column would corrupt the table. The natural place for byte-length is COMPARABILITY's Era Structure table (which has it). The audit's "×2 docs" was likely an over-count from the audit author's quick scan; my Convention-3-cheap-check resolution preserved table integrity over completionism. Not §7.

3. **Item 5 spec divergence ("L77" → L60) interpretation.** I edited L60 (the `data_year` row in the Record Identification section). If "L77" referred to a different `data_year` mention elsewhere (e.g., in COMPARABILITY or a different CODEBOOK section), my fix is in the wrong place. **Mitigation:** `data_year` appears only in (a) CODEBOOK L60 (harmonized variable row), (b) CODEBOOK L277 (variable index), (c) CODEBOOK L357 (appendix data_year section, with the pre-existing "verified 1,634,195/1,634,195 in V2.0" the audit explicitly C3-classed as generator-side OOS), and (d) COMPARABILITY L25 / L60 (cross-reference text). L60 is the only place a v2.4.0 verification clause belongs (it's the per-variable row in the harmonized-table; the appendix is auto-generated; COMPARABILITY's mentions are pointers, not Notes). Not §7.

4. **The 19-row replace_all on `file_inventory.csv`** could have over-matched. **Mitigation:** PRE-FLIGHT confirmed `(perLinkCO` appears in 0 other contexts (only the 19 col5 rows); VERIFY confirmed 0 post-replace residue. The 19→19 substitution is exactly bijective per the audit's "19 rows" count. Not §7.

5. **The new "shipped at `file-inventory-imported-flag-v4` task (2026-05-23, commit `84a9af3`)" language** in Item 6 references a commit hash. **Mitigation:** `git log` shows `84a9af3 file-inventory-imported-flag-v4 COMPLETE: flip 19 pre-2005 cohort rows imported=true` — verified the hash + task name are accurate. Tag `file-inventory-imported-flag-v4-complete` exists.

6. **Item 8 H10 callout claims about `e16ad532…` being "the pre-v3.0.0 anchor".** **Mitigation:** the on-disk `.v28_baseline.parquet` sidecar IS `e16ad5323d68e28d…` (verified by `shasum`); STATUS 2026-05-23T22:15:00Z confirms `Natality v3.0.0 c8a740eb…/acb5c48a…; .v28_baseline 230efed2…/e16ad532…`. So `e16ad532…` is the v2.8.0 derived = pre-C8.17/pre-v3.0.0. Current shipped main file at the same path is `acb5c48a9abf82ac…` = v3.0.0 derived. My new bullet correctly identifies both. Not §7.

7. **Numerics derivability (L6 defense).** The 2,427,233 v2.4.0 envelope total is parquet-derived (Appendix C8.20 header L273 cites the parquet `185c071ec76a` and rowcount 2,427,233); 1,713 and 397,397 are parquet-derived from Appendix C8.20 L1009 + L1591 respectively. No invented numbers.

### Forward-looking HALTs for next session (Convention 4)

These are the assertions the next session's PRE-FLIGHT must verify. If any fails, halt and re-derive.

1. **Phase D is now the sole gating question; do NOT enter it autonomously.** The user's authorization for this audit-fix bundle was scoped to *this remediation* only — explicit phrasing in the task message: *"After the audit-fix bundle ships and you append the STATUS section, halt and surface for my explicit Phase D authorization decision."* The next-session entry point is the (a)–(d) handshake → halt-for-Phase-D-go-ahead, NOT "since Pre-D cleanup is complete, begin D.1." Honor this.
2. **4 gate parquet SHAs byte-exact across all 6 Pre-D cleanup tasks + this auditfix.** `38e2cecb03ff4947` / `185c071ec76ab8aa` / `acb5c48a9abf82ac` / `f630d8cf20db72ea`. Independently re-hashed at next PRE-FLIGHT to confirm zero canonical mutation continued; if any drift, that's a §7-#18 reproducibility regression — halt.
3. **R2d (other `fetal_death/*.md` V2.0-envelope-staleness) is a documented carry-forward soft-flag**, NOT discharged by this bundle. The audit explicitly recommended defer; this bundle honored that. If next session is Phase D D.3 (public-repo sync), R2d should land in the D.3-adjacent doc-sync pass per the audit's recommendation, NOT silently fold into D.3 without scoping. Surface it.
4. **The `data_year` L60 row's stale `Years` column ("1992-2022")** is a known out-of-bundle-scope artifact (Self-check #1 above). If a future doc-sync task touches CODEBOOK.md narrative tables, fold this column-staleness fix in (consistent with the v2.4.0 envelope = 1982-2024). Not §7.
5. **The audit-spec line-number divergences (Item 4 "×2 docs"→1 doc, Item 5 "L77"→L60) are Convention-3 cheap-check resolutions** — preserved here for next session's awareness if the audit is re-run or audited-of-audit. Both are correctness-preserving; not §7.
6. **Repo append-only clock runs ahead of harness `currentDate` (2026-05-19)** — this RECEIPT is dated 2026-05-24T00:45:00Z to keep the monotonic-after invariant (carried-forward Convention-4 HALT #4 from `convenience-benchmark-v4-scope`). Per next session's PRE-FLIGHT: timestamps must be monotonic-after the newest STATUS section.

### Notes for next session

- **Internal Pre-D cleanup + audit-fix-r1r2-bundle BOTH COMPLETE.** The 2 independent fresh-eyes audit rounds (12 audits total, 0 blockers) recommended this remediation pre-Phase-D, mirroring the C8.20-auditfix precedent; now shipped. Only the externally-irreversible, human-authorization-gated **Phase D** remains.
- **Phase D entry surface for next session**: D.1 (Task 9, redirect notices on the 2 old GitHub repos) → D.2 (Task 10, unified Zenodo deposit) → D.3 (public-repo v1.x sync, with R2d folded into the D.3-adjacent doc-sync) → D.4 (manuscript re-pass + submit, with the C8.13/C8.18 timing reconciliation + the Coverage re-paragraph). Each is its own five-phase task; halt-and-ask before each externally-irreversible step.
- **Tag**: `audit-fix-r1r2-bundle-pre-do` at `17814d2`; `audit-fix-r1r2-bundle-complete` to be set after the commit lands.
- **§2/§4.4/§9-#2/L6** honored throughout: cheap PRE-FLIGHT caught the 2 spec divergences before any DO mutation; numerics derived not invented; §9-#8 (non-compression) honored by deferring R2d + the data_year `Years` column staleness as separate items; §9-#2 (no fabricated numerics) honored by refusing to invent a `~200 bytes` line in CODEBOOK where the column doesn't exist.
- **C2 approach choice (2 = scope-the-3-Notes; recommended-default; not approach 1 drop-the-gloss)**: confirmed at PRE-FLIGHT; logged in DECISION_LOG with reasoning.
