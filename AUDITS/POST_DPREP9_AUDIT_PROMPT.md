# Post–D-prep.9 fresh-eyes audit — paste into a fresh LLM chat

Copy **everything inside the fenced block below** as your first message. Attach or open this repo in the chat. Do **not** paste `KICKOFF.md` build-session block unless you want the agent to also run PRE-FLIGHT/DO work — this prompt is **read-only audit only**.

---

```
You are conducting a **fresh-eyes adversarial audit** of the U.S. Harmonized Vital Statistics (HVS) monorepo **after Phase D-prep.6–9 and the ultrareview-fix-bundle** (2026-05-20). Your job is to find defects, stale claims, and §7-class risks **before Phase D** (Zenodo + public repo + manuscript). You are **not** authorized to mutate canonical state (parquets, schemas, validation targets, pipeline code) unless the human explicitly asks you to fix findings in a follow-up session.

## Audit session rules (binding)

1. **This is an audit session.** Refuse to read or rely on:
   - `RECEIPTS/`
   - `FIX_LOG.md`
   - `LESSONS.md`
   - `DECISION_LOG.md`
   Treat prior audit narratives as **untrusted** until you re-verify from primary artifacts.

2. **You MAY read:** `STATUS.md` (newest section only for sequencing context), `README.md`, `PROJECT_STRUCTURE.md`, `NEXT_STEPS.md` (especially §7 halt conditions and §8 mistake-class matrix), `KICKOFF.md` (current planned sequence only), all product docs/codebooks, `docs/*`, `metadata/*`, `tests/*`, `notebooks/*`, `paper/draft_v2_hmd_styled.md`, prior `AUDITS/*.md` (for deduplication only — do not rubber-stamp “already fixed” without re-checking).

3. **Adversarial framing:** Use `NEXT_STEPS.md` §8 (mistake-class matrix). **Prioritize hunting for:**
   - **L3** — tests that pass but do not test the claim; validators without mutation coverage
   - **L7** — “looks right” without numeric threshold; grep-only verification
   - **L11** — stale roadmap/README/JOINT_USE claims vs shipped envelope
   - **L17** — SMOKE/tests pinning mutable values (row counts, sha256s, doc strings) that should be SHAPE-not-VALUE

   Also sample **H8** (docs vs data), **L6** (hand-invented numbers), **L13/L14** (inventory vs columns; validator exit codes), **F1/F2** (canonical filter / cross-product join).

4. **Output:** Write findings under `AUDITS/` (create if missing):
   - Per-lane reports: `AUDITS/round4/01_data-integrity_<UTC>.md` … `05_manuscript_<UTC>.md`
   - Consolidated: `AUDITS/CONSOLIDATED_POST_DPREP9_<UTC>.md`
   Use UTC timestamps in filenames. **Do not** edit `STATUS.md`, `RECEIPTS/`, or state logs unless the human asks.

5. **Verdict taxonomy per finding:** `PASS` | `FINDING` (with severity: critical / high / med / low) | `HALT` (§7 — requires canonical rebuild or blocks Zenodo). Every FINDING needs: ID, location (file:line or path), evidence (grep output, computed check, or explicit “could not verify because …”), suggested remediation tier.

6. **No rubber-stamping:** Round 3 (`AUDITS/CONSOLIDATED_PRE_ZENODO_2026-05-20T03-30-00Z.md`) flagged PZ-01–PZ-11 and PZ-NB. D-prep.5, D-prep.6–9, and ultrareview-fix-bundle **claim** those are closed. **Your job is to verify closure**, not assume it.

---

## What shipped since round 3 (verify from disk, not from receipts)

Per `STATUS.md` newest sections (2026-05-20):

| Work unit | Claimed outcome | Your verify focus |
|---|---|---|
| **D-prep.6** | 4/4 gate parquet SHAs byte-exact vs PROVENANCE | Re-hash if parquets on disk; else document “cannot verify” |
| **D-prep.7** | C8.20 appendix regen; gate SHAs unchanged | Marker block in CODEBOOKs; no stale `1,634,195` / `1992-2022` in generated `_Schema note_` lines |
| **D-prep.8** | `live_births_by_year.csv` + `stratified_denominators.csv` through **2024** | Row years, dtypes (Int8 not float `0.0`), JOINT_USE_GUIDE tables |
| **D-prep.9** | `notebooks/_paths.py` + portable paths; 3 kickoff notebooks re-executed | No `/Users/...` literals in `.ipynb` sources; `_gate_parquet()` pattern |
| **ultrareview-fix** | Bugs 001, 004, 011, 012, 016 remediated | See STATUS table; re-grep each |

**Known residual (do not treat as regression if still present):** `preterm_outcomes_time_series` and `cross_race_fetal_mortality` notebooks — source regenerated but execute may fail on **pre-existing** assertion drift (STATUS 21:30Z). Report as FINDING only if **new** vs round 3.

**Gate SHA anchors** (full hashes in `fetal_death/PROVENANCE.md`, `natality/PROVENANCE.md`):

| Artifact | SHA-256 prefix |
|---|---|
| `fetal_death_harmonized.parquet` | `38e2cecb…` |
| `fetal_death_derived.parquet` | `185c071e…` |
| `natality_v2_harmonized_derived.parquet` | `acb5c48a…` |
| `natality_v3_linked_harmonized_derived.parquet` | `f630d8cf…` |

If parquets are gitignored/absent: say so; run all other lanes; flag **PZ-OP** (mandatory build-host re-hash before Zenodo) as operational FINDING, not data defect.

**Current envelope (sanity):** Natality 1968–2024 ~201.2M; linked 1983–2023 (gap 1992–1994) ~149.4M; fetal death 1982–2024 ~2.43M; matched multiples ~1.67M.

---

## Five parallel audit lanes

Run all five. Each lane ends with **Verdict:** PASS | PASS-WITH-NOTES | FAIL | HALT.

### Lane 1 — Data integrity (`01_data-integrity`)

- Re-hash gate parquets if present; compare to PROVENANCE + `docs/NCHS_SOURCE_MANIFEST.md` §5.
- Spot-check `harmonized_schema.csv` dtypes vs a parquet column sample (pyarrow) for each product — H7/L13.
- Read committed validation summaries under `*/output/validation/` — any FAIL rows or exit-code-0 with failures (L14)?
- `tests/test_parquet_column_snapshot.py`, `test_row_count_conservation.py`, `test_schema_dtype_parity.py` — DESIGN tags, L17 pins.
- **Do not** re-run full pipeline unless human authorizes (§7-#17).

### Lane 2 — User-facing docs (`02_user-facing-docs`)

Re-verify round 3 Tier A closure **and** D-prep.1/8 doc surfaces:

- `docs/JOINT_USE_GUIDE.md`, `docs/COMPARABILITY.md`, root `README.md`
- Per-product: `*/README.md`, `CODEBOOK.md`, `COMPARABILITY.md`, `GETTING_STARTED.md`, `REPRODUCING.md`, `FAQ.md`, `ABOUT_*`
- Cross-check four-product table vs PROVENANCE record counts (L6/H8).
- Grep stale envelope strings: `1,634,195`, `29-year`, `1992-2022` as **current** envelope (not historical changelog), `V2.0` as headline where v2.4.0/v3.0.0 shipped.
- `fetal_death/live_births_by_year.csv`, `stratified_denominators.csv` — years through 2024, bridged-race null window **2020–2024** per JOINT_USE (bug 016 fix).

### Lane 3 — Reproducibility (`03_reproducibility`)

- `file_inventory.csv` (both products): `imported` flags, `(per LinkCO` spacing, record_length populated (fetal).
- `docs/NCHS_SOURCE_MANIFEST.md` vs on-disk zip SHAs if zips available.
- `REPRODUCING.md` paths monorepo-relative; zip counts match inventory.
- `docs/PIPELINE_TIMING_BENCHMARK.md` — post-C8.13 scope note still honest?
- CI: `.github/workflows/*` — what runs on push? Any gap vs claimed test suite?

### Lane 4 — Notebooks (`04_notebooks`)

- `notebooks/_paths.py` exists and is imported by all `notebooks/_build_*.py`.
- Source cells: no hardcoded `/Users/yoelplutchok/...`; `_gate_parquet()` env → repo-relative → fallback pattern.
- Kickoff trio: `joint_use_demo.ipynb`, `paper_companion.ipynb`, `matched_multiples_demo.ipynb` — execute **if** parquets available; else static source audit only.
- Extended set: `preterm_outcomes_time_series`, `cross_race_fetal_mortality`, `education_gradient`, `maternal_age_stratified_imr` — path portability + assertion drift status.
- `natality/notebooks/quickstart.ipynb` — `data_year`, 201M vs 201.2M copy, title years.
- `tests/test_stratified_denominators_per_year_matches_natality.py` — still meaningful (L3)?

### Lane 5 — Manuscript + Phase D readiness (`05_manuscript`)

- `paper/draft_v2_hmd_styled.md` — numerics vs README four-product table; validation counts; year spans; linked 1992–1994 gap; matched multiples.
- Word-count vs IJE Data Resource Profile limit (~2,500 main text excl. abstract/refs/tables).
- Admin `<!-- YP: review -->` markers — list for D.4.
- **Tier:** findings here are **D.4 scope** unless they block data deposit truth (cross-product README lies).

---

## Consolidated report template

In `AUDITS/CONSOLIDATED_POST_DPREP9_<UTC>.md` include:

1. **Per-lane verdict table** (blockers count).
2. **Round-3 regression check** — table: PZ-01 … PZ-11, PZ-NB → CLOSED / STILL OPEN / NEW.
3. **D-prep.6–9 regression check** — same for gate SHAs, C8.20, CSV 2024, notebooks.
4. **Ranked findings** — Tier A (doc/CSV fix before Zenodo), Tier B (notebook execute/fix), Tier C (D.4 manuscript), Tier D (§7 HALT / canonical rebuild).
5. **Recommendation:** Proceed to Phase D.1? Run another fix bundle? Mandatory build-host `shasum` before D.2?
6. **Explicit non-findings** — do not re-flag items D-prep.1–5 already closed unless evidence regressed.

---

## Anti-patterns (refuse)

- Reading `RECEIPTS/` to justify PASS.
- Hand-editing findings into PASS because “probably fine.”
- Proposing canonical parquet rebuilds in a doc-only fix bundle (→ HALT + ask human).
- Inventing record counts — cite README, PROVENANCE, or parquet probe only.

---

## Deliverable checklist

- [ ] `AUDITS/round4/01_data-integrity_<UTC>.md`
- [ ] `AUDITS/round4/02_user-facing-docs_<UTC>.md`
- [ ] `AUDITS/round4/03_reproducibility_<UTC>.md`
- [ ] `AUDITS/round4/04_notebooks_<UTC>.md`
- [ ] `AUDITS/round4/05_manuscript_<UTC>.md`
- [ ] `AUDITS/CONSOLIDATED_POST_DPREP9_<UTC>.md`

Begin by reading `STATUS.md` (top section only), `README.md`, and `NEXT_STEPS.md` §7–§9. Then execute the five lanes. **Halt and report** if you discover gate SHA mismatch, NVSR validation FAIL in committed artifacts, or schema/parquet inconsistency — do not patch silently.
```

---

## Optional second message (if the agent tries to read forbidden files)

> Reminder: audit session — do not open `RECEIPTS/`, `FIX_LOG.md`, `LESSONS.md`, or `DECISION_LOG.md`. Re-verify from primary repo artifacts only.

## After the audit

If Tier A findings exist, run a **build session** (paste `KICKOFF.md` + authorize `post-dprep9-audit-fix-bundle` doc/CSV-only remediation per `audit-fix-r1r2-bundle` precedent). If PASS / notes only, human may authorize **Phase D.1** redirect notices.
