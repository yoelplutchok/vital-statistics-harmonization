# Receipt: fetal-death-other-docs-v240-sync
## 2026-05-24T12:00:00Z

### What was done

**D-prep.1** — R2d defer discharged. Synced the seven remaining `fetal_death/*.md` hand-docs from the stale **V2.0 / 29-yr / 1,634,195-record** envelope to **v2.4.0 / 43-yr / 1982-2024 / 2,427,233-record / 7-era**, at Option-A depth (matching the 2026-05-23 `fetal-death-codebook-comparability-v240` precedent). Bundled fix: `CODEBOOK.md` L60 `data_year` **Years** column `1992-2022` → `1982-2024`. Every introduced aggregate number parquet-derived (total 2,427,233; NVSR subset 1,121,986; per-era counts from CODEBOOK header / Appendix C8.20). **C8.20 appendix byte-identical** (marker `BEGIN`→EOF sha `b27640eeb6eda142`). Doc-only; zero canonical-state mutation.

### Inputs consumed

- Seven target docs + `CODEBOOK.md` L60 @ `fetal-death-other-docs-v240-sync-pre-do`
- Parquet probe: `fetal_death_derived.parquet` sha256[:12]=`185c071ec76a` — total 2,427,233; NVSR 1,121,986; years 1982-2024 (43)
- Era counts: CODEBOOK.md lines 12-36 + Appendix C8.20 (sum-checked 2,427,233)
- PRE-FLIGHT gate SHAs: `38e2cecb…` / `185c071e…` (fetal only locally present; natality/linked anchors unchanged per prior STATUS)

### Outputs produced

- `fetal_death/README.md` — full v2.4.0 release summary + validation + structure
- `fetal_death/ABOUT_SOURCE_DATA.md` — seven-era source table + v2.4.0 coverage totals
- `fetal_death/ABOUT_THIS_RELEASE.md` — Key Output Files + Validation Summary + limitations (historical V2.0/V2.1/V3a/V3b sections preserved)
- `fetal_death/FAQ.md`, `GETTING_STARTED.md`, `REPRODUCING.md` — envelope + int-filter quickstart alignment
- `fetal_death/REPORTING_THRESHOLDS.md` — tab_flag footnote → Appendix C8.20 pointer
- `fetal_death/CODEBOOK.md` — L60 only (`data_year` Years → 1982-2024)
- This receipt + `PRE_FLIGHT_LOG.md` + `STATUS.md` + `DECISION_LOG.md`

### Five-phase trace

- PRE-FLIGHT: ✓ Field-value snapshot; gate SHAs; C8.20 baseline `b27640eeb6eda142`; tagged `fetal-death-other-docs-v240-sync-pre-do`
- SMOKE: ✓ Doc-only Tier-0 — gate SHAs + appendix marker pre-DO recorded
- DO: ✓ 8 files (7 docs + CODEBOOK L60); 204 ins / 246 del
- VERIFY: ✓ below
- RECEIPT: ✓ this file

### Verify results

- V1 gate parquet SHAs: **PASS** — `38e2cecb03ff4947` / `185c071ec76ab8aa` unchanged pre/post
- V2 C8.20 appendix: **PASS** — `b27640eeb6eda142` pre == post (BEGIN→EOF marker extraction)
- V3 scope: **PASS** — `git diff --name-only` ⊆ 8 target paths + state files
- V4 stale-envelope sweep: **PASS** — no current-envelope claims at 1,634,195 / 29 years / “deferred to V2.1” as headline; legitimate historical v2.0.0 deposit / V2.0 changelog sections retained in `ABOUT_THIS_RELEASE.md` and README migration note
- V5 `data_year` L60: **PASS** — Years column `1982-2024`; Notes still cite 2,427,233/2,427,233 v2.4.0
- V6 sum-check: **PASS** — 421,125+188,909+700,704+107,782+510,528+204,923+293,262 = 2,427,233

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?

1. A paraphrased stale envelope string outside the grep patterns (e.g. “twenty-nine annual files” spelled out).
2. `quickstart.py` still says V2.0 / 1992-2022 — **out of D-prep.1 scope** (not in §15.E file list); D-prep.4 audit or a follow-up micro-task should align it.
3. `PROVENANCE.md` / zip bundle name still v2.0.0 — **scheduled D-prep.2**.
4. NVSR subset 1,121,986 not duplicated in every doc — intentional; pointed to parquet-derived FAQ/README.
5. Historical “V2.0” section titles in `ABOUT_THIS_RELEASE.md` could be misread as current envelope — mitigated by file title “in-repo state: v2.4.0” and overview paragraph.

### Forward-looking HALTs for next session (Convention 4)

1. **D-prep.1 CLOSED** — R2d + `data_year` L60 discharged. Next: **D-prep.2** (PROVENANCE) + **D-prep.3** (`years_available`) may parallelize.
2. **4 gate parquet SHAs** — re-hash at D-prep.2/3 PRE-FLIGHT; any drift = §7 halt.
3. **D-prep.4 audit AFTER D-prep.1-3** — audit should see post-R2d docs; optional align `quickstart.py` before audit or flag as finding.
4. **Phase D (D.1-D.4)** remains per-step human-authorization-gated.
5. **C8.20 appendix** — marker-based verify only (never hardcoded line range).

### Git

- Pre-DO tag: `fetal-death-other-docs-v240-sync-pre-do`
- Post-RECEIPT tag: `fetal-death-other-docs-v240-sync-complete` (this commit)
