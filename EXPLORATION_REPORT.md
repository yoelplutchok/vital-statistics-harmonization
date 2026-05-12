# EXPLORATION_REPORT — Phase B candidate frontier (PENDING USER REVIEW)

> **Status: drafted 2026-05-12T20:30:00Z; PENDING USER REVIEW.**
>
> This is the deliverable of the Phase B mandate set by KICKOFF.md "Current planned sequence" (commit `306370e` `[plan-update]`, 2026-05-12T19:15Z). Phase B is a **READ-ONLY exploration session**: no canonical-state mutation other than this file, the accompanying `STATUS.md` section, and a `DECISION_LOG.md` entry. Phase C (executing user-authorized candidates) starts only after the user reviews this report and authorizes a specific subset.
>
> **How to use this file**: skim §0 for the executive summary; jump to §A–§F for the per-dimension candidate tables; read §G for cumulative effort + suggested execution order; read §H for open questions for the human. The §11 plan-update proposal (KICKOFF.md + NEXT_STEPS.md §15 diffs) is in `STATUS.md` 2026-05-12T20:30Z and is not duplicated here.
>
> **Append-only after this draft is reviewed.** Future Phase B-2 / Phase C reports append new dated sections at the top; never edit the existing report.

---

## 0. Executive summary

Phase B mapped the candidate frontier across the six dimensions KICKOFF.md mandated. The total surface is **~42 distinct candidates** spanning data extensions, robustness/testing, usability/convenience, cross-product/joint-use, documentation, and performance/distribution. Honest cumulative effort if every candidate were executed is **~32–58 HVS-sessions** (Tier-5 backward extensions are the big swing; without them, ~14–22 sessions).

**External research findings** (Phase B agents, full results in §A and §E):

1. **Latest-year refresh is the obvious cheap pre-submission win.** Fetal Death 2023 + 2024 are now public-use (last-modified 12/5/2024 and 2/4/2026); Linked 2024 (`2024PE2023CO.zip`) was released 1/22/2026 — both **post-date the most recent HVS shipments**. Natality 2025 is NOT yet released as of 2026-05-12. 1–2 sessions total to ship.
2. **Natality 1968–1989 is fully public-use** (no RDC barrier), spanning four distinct pre-1989 layouts (1968 alone; 1969–71 joint doc; 1972–77 joint doc; 1978–88). 6–10 sessions to harmonize. Symmetric sibling of the V3b fetal-death work just shipped.
3. **Linked birth–infant death 1983–2004 is partially public-use**, with a permanent 1992–1994 NCHS-suspension gap and a cohort-vs-period publishing-design question. 8–14 sessions.
4. **Pre-1982 fetal death does NOT exist as public-use microdata** — HVS's current 1982 floor is the public-data floor. Document the boundary in the manuscript; do not attempt.
5. **Literature-gap claim is still defensible as of 2026-05.** No harmonized cross-revision U.S. vital-statistics microdata resource has been published in 2024–2026. Closest candidate (`Mikuana/vitalstatistics` on GitHub) is births-only, no NVSR validation, no Data Resource Profile. Three minor PRIOR_ART.md updates suggested in §E.5.

**Internal repo findings** (this session's introspection, full results in §B–§F):

6. **The existing fetal-death smoke test (`fetal_death/tests/test_release_smoke.py`) is stale post-V3b** — it pins `EXPECTED_ROW_COUNT = 1_634_195` (current is 2,352,011), 29 expected years (current is 41), and similar V2.0-frozen invariants. **Currently runs FAIL on the V3b parquet**. This is a textbook L17 stale-pin case; the existing pins also lack the Convention 2 `DESIGN:` docstring tag. A 0.5-session fix retags it `DESIGN: tracks-current-state` and re-pins to V3b state (preserving structural invariants per Convention 1 SHAPE-not-VALUE).
7. **No automated testing infrastructure.** 1 test file in the entire monorepo; 0 in `natality/`; no `.github/` directory; no CI; no `pyproject.toml`/lockfile; `requirements.txt` uses `>=` not `==`.
8. **`fetal_death/PROVENANCE.md` is 4 versions stale** (still cites v2.0.0 SHAs at commit `bfbcfea7…`, pre-monorepo migration). Already on backlog for Task 10 PRE-FLIGHT.
9. **Manuscript still cites 1,634,195 records / 29 years / 74 targets / "V3 deferred"** — every numeric in the Coverage paragraph + the *Future developments* section is stale post-V2.1/V3a/V3b. Already on backlog for KICKOFF step 6 (manuscript re-pass).
10. **5 worked-example notebooks are listed in KICKOFF.md §B.c but not yet built.** Each adds ~1–2 sessions; their value varies (see §C).

**Headline recommendation for the user**: the executable middle ground that maximizes "robust and useful" per the user's directive without absorbing the largest backward-extension swings is roughly Tiers 1–4 in §G — **about 13–19 sessions of Phase C work** before Phase D (Task 9 / Task 10 / public-repo v1.x sync / manuscript) ships. Tier 5 (natality 1968–1989; linked 1983–2004) adds another 15–26 sessions and is best framed as a *v1.1 → v2.0* follow-up after the initial paper lands, since it would re-trigger every validation grid + re-paragraph the manuscript's Coverage section twice (now and again post-extension).

The user can choose any prefix. §H lists the questions the user should answer before authorizing Phase C.

---

## §A. Data extensions

External-research provenance: agent `aea960a496472bb6b` (2026-05-12T20:15Z). Probed CDC FTP directory listings under `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/{natality,cohortlinkedus,periodlinkedus,period-cohort-linked,fetaldeathus,mortality,matched-multiples}/` and the parallel `Dataset_Documentation/DVS/...` paths. Negative results (HTTP 404) are explicitly listed in §A.9.

### A.1. Latest-year refreshes — fetal death 2023 + 2024, linked 2024

**Description**: extend each product to its current NCHS-public extent.

**Public-use availability (verified URLs)**:
- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2023US_COD.zip` — 2,219,550 B, last-mod 2024-12-05. HTTP 200.
- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2024US_COD.zip` — 1,925,286 B, last-mod 2026-02-04. HTTP 200.
- `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/period-cohort-linked/2024PE2023CO.zip` — 432.5 MB, last-mod 2026-01-22. HTTP 200.
- User guides `2023fetaluserguide.pdf`, `2024fetaluserguide.pdf`, `24PE23CO_linkedUG.pdf` all HTTP 200. Sibling-derived from existing 2022 + 2023 conventions.
- Natality 2025: `Nat2025us.zip` is NOT yet present (probed 2026-05-12). Latest natality is `Nat2024us.zip` already in HVS. NCHS natality typical release lag is ~12–14 months after year-end; Natality 2025 expected ≈ Aug-Oct 2026.

**Layout reconstruction risk**: low. Fetal 2023/2024 continue the 2018–2022 COD-only layout (the user guide for 2022 sibling-derived; expect ≤1-byte-per-column delta if any). Linked 2024 continues the post-2017 combined-period-cohort layout used for 2023.

**Effort estimate**: **1–2 sessions total**.

**Source / data deps**: 3 source zips totaling ~437 MB; 3 user-guide PDFs.

**Risks / blockers**: minor — layout-byte deltas (if any) must be parsed against the new user guide per L13-extension. NCHS occasionally reorders columns mid-revision; sibling-byte-position diff against 2022 is the cheap check.

**Manuscript impact**: pushes "current as of" date. Fetal Death becomes 1982–2024 (43 yrs), Linked becomes 2005–2024 (20 yrs), Natality stays 1990–2024 (35 yrs). Every "through 2022/2023" claim in the Coverage paragraph updates.

**Priority**: **must-have if submission slips past summer 2026**; otherwise nice-to-have at cost of 1 session.

**Execution dependency**: independent. Cheapest pre-submission win on the table.

### A.2. Natality 1968–1989 backward extension

**Description**: parse pre-1990 natality public-use files. Symmetric sibling of V3b fetal-death backward extension.

**Public-use availability**: all 22 yrs present at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/Nat<YYYY>.zip` (note: **no `us` suffix** pre-1994; the `us`/`ps` resident/place-of-occurrence split begins 1994). All last-modified 2007-08-24/28 (single archival batch). Filename casing irregularity: `Nat1968.ZIP` is uppercase; 1969+ is lowercase.

Sizes from FTP listing: 1968 (14.6 MB; 50% sample, smaller); 1969–1971 (35.3 / 38.6 / 35.1 MB; 50% sample); 1972–1977 (35–60 MB each; mixed sample); 1978 (71.1 MB; 100% file); 1979–1981 (88.4 / 90.6 / 97.3 MB); 1982–1988 (≈100–119 MB each); 1989 (141.0 MB). **Total ≈ 1.66 GB raw.**

**Layout / revision boundaries** (four distinct pre-1989 layouts to reconstruct):
- **1968 alone** (50% sample; first year of harmonized public-use file). `Nat1968doc.pdf` singleton documentation.
- **1969–1971** (50% sample, multi-year joint doc `Nat1969-71doc.pdf`).
- **1972–1977** (mixed 50%-some-states / 100%-most-states; multi-year joint doc `Nat1972-77doc.pdf`).
- **1978–1988** (1978-revision birth certificate, 100% file from 1985+; per-year docs `Nat<YYYY>doc.pdf`).
- 1989 alone (1989-revision birth certificate; sibling of 1990–2002 V2 era in current HVS).

**Estimated record count**: ~80 million records across 22 yrs (extrapolating from NCHS-published annual birth totals 3.5–4.0 M; the 50% sample years 1968–1971 hold ~1.7–2.0 M each).

**User-guide availability**: all probed HTTP 200 at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/Nat<YYYY>doc.pdf` plus the two multi-year PDFs. All dated 2007-08-24 (NCHS's 2007 re-OCR batch — analogous to the 2009 batch that gave V3b text-extractable layouts; expect same text-layer embedding per LESSONS L12-extension).

**Layout reconstruction risk**: **medium-to-high**. Four distinct layouts is 4× the V3b cost in layout-CSV reconstruction. The 1968 50%-sample handling, the 1978-rev→1989-rev cert boundary at 1989, and the absence of Hispanic-origin field until 1978-onward-in-subset-of-states all add complexity. The 1972–1977 multi-year joint doc is the highest-risk single artifact (mixed sample fraction varies by state-year; the joint doc may abbreviate). Tier-2 SMOKE gate: per-year canonical-filter aggregate must match published *Vital Statistics of the United States* annual volumes (paper-only, OCR friction).

**Effort estimate**: **6–10 sessions** = 3–5 layout-reconstruction + 2–3 parser/harmonize + 1–2 validation.

**Source / data deps**: 22 source zips (~1.66 GB); ~17 user-guide PDFs (singleton + 2 joint + per-year 1978–1989); 22 yrs of published-aggregate validation targets (paper *Vital Statistics of the United States* volumes; some online via CDC archives, others not).

**Risks / blockers**:
- (a) Pre-1978 records lack Hispanic-origin field → harmonized `hispanic_origin` is `null` for those years (already the V3b convention; cheap to extend).
- (b) **Schema-version bump risk**: adding 4 new eras = ~22 new rows in `harmonized_schema.csv`'s `years_available` cells; verify Convention 1 SHAPE-not-VALUE on existing smokes (the V3b extension showed this is manageable).
- (c) 50%-sample-period weighting: NCHS recommends scaling 1968–1971 counts by ×2 for rate computation; harmonization must surface a `sample_fraction` column or a per-year doc note.
- (d) **Maternal race coding** in 1968-rev (3-cat: White / Black / Other) vs 1978-rev (1-digit 0–9; same as V3b) vs 1989-rev (2-digit 01–99): two new B3-style recodes to author + DECISION_LOG entries.

**Manuscript impact**: extends natality 35 yrs → **57 yrs (1968–2024)**. Pairs with fetal death 1982–2022 to push joint analyses backward to 1982 (limited by FD floor; symmetric earlier extension blocked by RDC per §A.4). Manuscript Coverage paragraph + record-count claim need full re-paragraph. Manuscript *Future developments* section's "Annual extension" framing gains a sibling.

**Priority**: **nice-to-have, defer-to-post-submission** by default. The natality 1968–1989 extension would be a v1.1 or v2.0 release — large enough to warrant a follow-up Data Resource Profile *Update* note in IJE or a v2.0 Zenodo deposit. Re-paragraphing Coverage twice (once for v1.0, once for v1.1) is the friction.

**Execution dependency**: independent of all other backward extensions. Doesn't block; doesn't depend.

### A.3. Linked birth–infant death pre-2005 backward extension

**Description**: parse cohort-linked 1983–1991 (9 yrs) + cohort-linked 1995–2004 (10 yrs) + period-linked 1995–2004 (10 yrs). Bridges to current HVS-linked 2005–2023.

**Public-use availability**:
- Cohort-linked 1983–1991: `LinkCO83.zip` through `LinkCO91.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/cohortlinkedus/`. No `US` suffix in filename pre-1995. Sizes ~49–117 MB each. **Total ≈ 665 MB.**
- **1992–1994 gap**: no files. NCHS suspended linkage. Permanent — document, do not close.
- Cohort-linked 1995–2015: `LinkCO95US.zip` through `LinkCO15US.zip`. Sizes 90–236 MB. **Backward-extension subset 1995–2004 ≈ 1.18 GB.**
- Period-linked 1995–2017: `LinkPE95US.zip` through `LinkPE17US.zip`. Sizes 102–193 MB. **Backward-extension subset 1995–2004 ≈ 1.18 GB.**
- 2016+ migrated to combined period-cohort format (`<YYYY>PE<YY>CO.zip`), already in HVS.

**Total raw size for the pre-2005 backward extension: ≈ 3.0 GB.**

**Layout / revision boundaries**:
- Cohort 1983–1988 (6 yrs): **1978-revision birth cert + ICD-9 cause-of-death**. Most distinct layout.
- Cohort 1989–1991 (3 yrs): 1989-revision birth + ICD-9.
- 1992–1994: GAP.
- Cohort 1995–1998 (4 yrs): 1989-rev birth + ICD-9 (1995–98), then ICD-10 (1999+).
- Cohort 1999–2002 (4 yrs): 1989-rev birth + ICD-10.
- Cohort 2003–2004 (2 yrs): 1989+2003-rev mix, ICD-10. Boundary year for revision-rollout.
- Period 1995–2004: same revision/ICD pattern, different linkage method.

**User-guide availability**: all probed HTTP 200 at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/{cohortlinked,periodlinked}/Link*UserGuide.pdf` (per-year + multi-year docs).

**Layout reconstruction risk**: **high**. Three distinct boundary types (cert-revision 1989→2003, ICD-9→ICD-10 1998→1999, linkage-method cohort-vs-period) intersect. The **cohort/period publishing-design question** is a one-time decision: HVS-linked from 2005 ships period-format only; extending backward forces (a) ship cohort and period both as separate parquets, or (b) reconcile via a derived "period-equivalent" view of cohort data, or (c) stop the backward extension at 1995 and ship period-only. Each choice has manuscript implications.

**Effort estimate**: **8–14 sessions** = 3–5 cohort-linked 1983–1991 + 2–3 period-linked 1995–2004 + 2–3 cohort-linked 1995–2004 + 1–2 validation grid + 1 schema-design.

**Source / data deps**: ~29 source zips (~3 GB); ~25 user-guide PDFs; validation targets from NCHS Linked File reports (mostly online).

**Risks / blockers**:
- (a) **1992–1994 gap is permanent** — must be loud in schema (`years_available` cells include the gap), CODEBOOK, and manuscript.
- (b) **Cohort/period publishing-design** is a one-time decision affecting public-API.
- (c) ICD-9 vs ICD-10 cause-of-death harmonization is non-trivial. Either ship `cause_icd10` null for 1983–1998 (simpler) or build a 9→10 crosswalk (large; many published crosswalks exist; can defer to dedicated derivation task).
- (d) The cohort-linked file's *denominator-plus* format pre-2005 differs from the post-2005 *period-cohort merged* format; schema variant analogous to natality V2 vs V3 boundary.

**Manuscript impact**: extends linked 19 yrs → **41 yrs (1983–2023)** with a documented 3-yr gap. Strong support for the manuscript's "single-revision-window forced" framing.

**Priority**: **nice-to-have, defer-to-post-submission**. Largest session-count of any candidate; cohort/period design decision is methodology-paper territory. Realistic as a v1.1 or v2.0 follow-up.

**Execution dependency**: Cohort 1983–1991 benefits modestly from natality 1968–1989 first (shared 1978-cert layout knowledge). Post-1995 sub-blocks are independent.

### A.4. Pre-1982 fetal death

**Description**: probe whether fetal-death microdata extends backward of HVS's V3b floor.

**Public-use availability**: **NOT public-use available.** Probed (all HTTP 404):
- `Fetal1981US.zip`, `Fetal1980US.zip`, `Fetal1979US.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/`.

The fetal-death FTP directory listing confirms the earliest file is `Fetal1982US.zip` (last-mod 2009-01-08); no earlier zips.

NCHS *Vital Statistics of the United States* paper volumes (Series 21) publish *aggregate* fetal-death tabulations back to the 1950s, but the microdata equivalent is not redistributed.

**Layout reconstruction risk**: not applicable; no source files.

**Effort estimate**: **infeasible without RDC access**. RDC requires institutional approval, on-prem or virtual-enclave compute, and prohibits redistribution — incompatible with HVS's open-redistribution model.

**Source / data deps**: NCHS RDC application process.

**Risks / blockers**: blocker is NCHS data-release policy.

**Manuscript impact**: explicit boundary statement — "pre-1982 fetal-death microdata is RDC-only and not redistributable." Strengthens scope-definition.

**Priority**: **defer indefinitely / document as boundary**. Add one sentence to manuscript Coverage paragraph and `fetal_death/ABOUT_SOURCE_DATA.md`.

**Execution dependency**: blocked by NCHS data-release policy.

### A.5. Matched-multiples (NCHS ancillary linkage)

**Description**: NCHS publishes three special-purpose linkage files matching multiple-birth records to fetal-death siblings.

**Public-use availability**: at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/`:
- `matched-multiple-birth-fetal-death-1995-1997.zip` (9.6 MB)
- `matched-multiple-birth-fetal-death-1995-2000.zip` (21.7 MB)
- `matched-multiple-birth-fetal-death-2016-2020.zip` (11.7 MB)

**Layout reconstruction risk**: medium. Each file is a derived NCHS product with its own layout; sibling-derive from existing HVS linkage may not apply directly.

**Effort estimate**: **1–2 sessions**.

**Source / data deps**: 3 zips (~43 MB); 3 documentation PDFs.

**Manuscript impact**: minor — could ship as a 4th HVS product, but cross-references to multiple-birth analyses would need an extra paragraph in *Methods* or *Data resource use*. Risk: scope creep.

**Priority**: **defer to post-v1 ancillary release**. Useful for the multiple-gestation IMR / fetal-mortality research community but not core HVS.

**Execution dependency**: independent.

### A.6. Other NCHS public-use files (out-of-scope verification)

External agent confirmed presence + scope of:
- **Marriage / Divorce 1968–1995** (NCHS discontinued post-1995; NBER hosts at `nber.org/research/data/marriage-and-divorce-data-1968-1995`). **OUT of HVS scope** (vital events around birth only).
- **Multiple-Cause-of-Death (all-age mortality) 1968–2024** at `ftp.cdc.gov/.../mortality/Mort<YYYY>us.zip` (~5 GB total). **OUT of HVS scope** — adjacent communities (NBER, SSA, IHME, Human Mortality Database) already harmonize.
- **Abortion surveillance**: aggregate-only MMWR summaries; no microdata to harmonize. **OUT of HVS scope.**

**Priority**: list as out-of-scope in manuscript (boundary-defining); add one paragraph to `docs/PRIOR_ART.md` distinguishing HVS lane.

### A.7. IPUMS / NBER / ICPSR competition assessment

External agents confirmed:
- **IPUMS-USA**: Census + ACS only. **No competition.**
- **IPUMS Health Surveys**: NHIS + MEPS only. **No competition.**
- **IPUMS-International**: non-U.S. census only. **No competition.**
- **NBER**: redistributes NCHS raw files; does NOT harmonize across 1989/2003 boundary. **No competition for harmonization.**
- **ICPSR**: year-by-year distribution of NCHS Natality Detail / Cohort-Linked files; "data and documentation … in essentially the same form … received." **No competition.**
- **`Mikuana/vitalstatistics` GitHub** (births-only R package, ~7 stars): partial precursor; no NVSR validation; no DRP publication; no 1989/2003 explicit handling. Mention in PRIOR_ART.md "GitHub precursors" subsection. **Not a competitor.**
- **HL7/fhir-bfdr**: prospective FHIR-based reporting standard for future certificates. Orthogonal to retrospective harmonization. Optional one-sentence mention in PRIOR_ART.md.

**Priority**: documentation-only update. See §E.5.

### A.8. Aggregate priority ranking for Phase B/C data extensions

| Rank | Candidate | Effort | Priority |
|---|---|---|---|
| 1 | A.1 Latest-year refresh (fetal 2023+2024; linked 2024) | 1–2 sessions | **Must-have if submission slips past summer 2026** |
| 2 | A.5 Matched-multiples | 1–2 sessions | Post-v1 ancillary |
| 3 | A.2 Natality 1968–1989 | 6–10 sessions | Nice-to-have; v1.1/v2.0 follow-up |
| 4 | A.3 Linked 1983–2004 | 8–14 sessions | Nice-to-have; v1.1/v2.0 follow-up |
| 5 | A.4 Pre-1982 fetal death | Infeasible | Document as boundary |
| 6 | A.6 M-D / MCD / abortion | N/A | Out-of-scope; document boundary |

### A.9. Negative results (HTTP 404 / not-present)

For audit / sibling-derivation evidence per LESSONS L1-extension:
- `Fetal1981US.zip`, `Fetal1980US.zip`, `Fetal1979US.zip` (and earlier) — 404. Public-use floor for fetal death is 1982.
- `Nat2025us.zip` — not yet present (NCHS release lag).
- `Nat1968us.zip` (wrong probe filename — actual is `Nat1968.ZIP` uppercase, no `us` suffix). Sibling-derivation succeeded once the correct convention was probed.

---

## §B. Robustness / testing / validation infrastructure

Internal-introspection findings: monorepo has **one** test file (`fetal_death/tests/test_release_smoke.py`, 9 tests, currently stale post-V3b), **zero** test files in `natality/`, and **no CI** (no `.github/` directory). Most candidates in this section are 0.5–1.5 sessions each; collectively they're the cheapest "robust and useful" wins.

### B.1. **Retag + repin the existing fetal-death smoke (L17 stale-pin fix)**

**Why**: `fetal_death/tests/test_release_smoke.py` pins `EXPECTED_ROW_COUNT = 1_634_195`, `EXPECTED_YEARS` = 29-yr (1992–2002 + 2005–2022), `EXPECTED_HARMONIZED_COLS = 73`, `EXPECTED_DERIVED_COLS = 89`. After V2.1 (+107K records, +2 years), V3a (+188K, +3 years), V3b (+421K, +7 years), the actual state is **2,352,011 records / 41 years**. The smoke **currently runs FAIL** on the V3b parquet. The col counts ARE preserved (73 + 89), which is the SHAPE-not-VALUE invariant.

**Effort**: **0.5 sessions**. Two-line decision:
- (a) Repin row count + year set to V3b state; add `DESIGN: tracks-current-state` first-docstring tag.
- (b) Or split into two harnesses: keep V2.0 smoke as `DESIGN: frozen-at-task7_v3b` (anchor: expected-FAIL after any future row-count growth IS the test that future growth was authorized) + add new tracks-current-state smoke.

**Source / deps**: existing smoke file; current parquet SHAs (already in STATUS forward-looking HALTs).

**Risks**: none meaningful. Pure metadata update.

**Manuscript impact**: none direct; supports "Reproducibility" Strengths paragraph.

**Priority**: **must-have, pre-Phase D**. Already in `task7_v3b_2026-05-12T18-45-00Z.md` Notes-for-next-session ("Joint-use notebooks not re-run this session. KICKOFF step 5 / Task 10 should rebuild …") but the smoke retag is the cheaper item.

**Execution dependency**: none.

### B.2. `tests/test_schema_dtype_parity.py` (durable H8 defense)

**Why**: FIX_LOG 2026-05-11T18:50:00Z and 2026-05-12T01:30:00Z both recommend this. Assert every `harmonized_schema.csv` row's `type` matches the parquet's pyarrow dtype. Would have caught the v2.0 H8 incident (5 demographic columns shipped as `object` while schema declared `int`).

**Effort**: **0.5–1 session** per product. Build one harness reused for fetal-death + natality.

**Source / deps**: schema CSVs + harmonized + derived parquets.

**Risks**: low. The harness is structurally simple; mutation-test gate (per §B.6) ensures it catches the failure mode it claims.

**Manuscript impact**: indirect — strengthens *Reproducibility* claim.

**Priority**: **must-have, pre-Phase D**.

**Execution dependency**: none.

### B.3. `tests/test_canonical_filter_invariants.py`

**Why**: assert sum-across-strata = unstratified-total for every canonical filter, every product, every year. Catches silent join-stage record loss or duplicate counting.

**Effort**: **1 session**.

**Source / deps**: derived parquets; canonical filter definitions (per `docs/JOINT_USE_GUIDE.md`).

**Risks**: low.

**Manuscript impact**: indirect — supports "Joint-use design" Strengths claim.

**Priority**: high. Closes a class of bugs not currently guarded.

**Execution dependency**: none.

### B.4. `tests/test_row_count_conservation.py`

**Why**: input = output + documented_drops at every parse → harmonize → derive boundary. NEXT_STEPS §8 H6.

**Effort**: **1 session**.

**Source / deps**: yearly_clean parquets + harmonized parquet + derive parquet + documented-drop counts (currently in DECISION_LOG entries; consolidate).

**Risks**: medium. Requires assembling a "documented drops" registry — may surface undocumented drops that need post-hoc explanation.

**Manuscript impact**: indirect.

**Priority**: high.

**Execution dependency**: ideally after B.3 lands (shared invariant infrastructure).

### B.5. `tests/test_cross_product_join_parity.py`

**Why**: natality joined to fetal-death + linked has expected demographic-stratum row counts (per JOINT_USE_GUIDE). Defends F2 (cross-product join without filter on both sides).

**Effort**: **1 session**.

**Source / deps**: all three parquets + `shared/helpers/canonical_join_keys.py`.

**Risks**: low.

**Manuscript impact**: directly supports the manuscript's joint-use claim.

**Priority**: high.

**Execution dependency**: B.3 + B.4.

### B.6. Mutation-test scaffolding for every validator

**Why**: NEXT_STEPS §8 L3 + L14. Inject a known violation; assert validator catches. Currently no validator has a paired mutation test; rubber-stamp risk is unbounded.

**Effort**: **2 sessions** (covers ~13 validators across 5 scripts in both subprojects).

**Source / deps**: existing validators.

**Risks**: medium — may reveal validators that don't catch what they claim to catch. That's the point, but each finding becomes a FIX_LOG entry → cascade.

**Manuscript impact**: supports *Reproducibility* claim; also strengthens the L3/L14 defense the protocol cites.

**Priority**: high.

**Execution dependency**: none.

### B.7. L13 file-inventory completeness audit

**Why**: NEXT_STEPS §8 L13. For every CSV in `metadata/`, verify `role`/`description` names columns that actually exist with claimed dtypes. The V3a/V3b work surfaced two L13-extension cases (record_layout_2006 BLANK truncation; MAGER-vs-MAGER41 byte-position rename).

**Effort**: **1 session**.

**Source / deps**: all CSVs in `metadata/` + `fetal_death/`.

**Risks**: may surface undocumented field rows.

**Manuscript impact**: none direct; supports `Reproducibility`.

**Priority**: medium-high.

**Execution dependency**: none.

### B.8. L14 exit-code-vs-per-row aggregation defense

**Why**: NEXT_STEPS §8 L14. Every validator's `main()` must `sys.exit(1 if FAIL_COUNT > 0 else 0)`; mutation-runner uses AND-of-rows. Audit existing validators.

**Effort**: **0.5–1 session**.

**Source / deps**: 13 validators across 5 scripts.

**Risks**: low.

**Manuscript impact**: none direct.

**Priority**: medium-high.

**Execution dependency**: ideally bundled with B.6.

### B.9. CI integration (GitHub Actions)

**Why**: no automated test runs today; every regression discovered post-hoc. Wire B.1–B.5 to a workflow that runs on every push.

**Effort**: **1 session**.

**Source / deps**: GitHub Actions runner; pinned env (requires B.f.2 or B.f.3 lockfile/Dockerfile).

**Risks**: low. Public-repo CI minutes are free at this scale.

**Manuscript impact**: indirect — supports *Reproducibility* and signals "active maintenance" for reviewers.

**Priority**: **must-have, pre-Phase D**. The cheapest single signal of project health for an external reviewer.

**Execution dependency**: B.1, B.2 (need real tests to run); B.f.2 or B.f.3 (need a pinned env).

### B.10. `scripts/run_pipeline.py` end-to-end smoke from monorepo root

**Why**: FIX_LOG 2026-05-12T01:30Z noted three latent path-drift bugs in `fetal_death/scripts/` that were not caught because no end-to-end run from the monorepo root had been attempted. Confirms no further path-drift bugs exist.

**Effort**: **1 session** (probably catches 1–2 more L13-style path-drift cases; budget for fix-on-contact).

**Source / deps**: existing pipeline scripts; raw zips (already on disk).

**Risks**: medium. May surface multi-session blockers if a script has architectural drift, not just path-drift.

**Manuscript impact**: indirect — `Reproducibility` claim becomes auto-verifiable.

**Priority**: high.

**Execution dependency**: none, but ideally after a clean Tier-1 baseline.

### B.11. PROVENANCE.md refresh + sha-stability test

**Why**: `fetal_death/PROVENANCE.md` is v2.0.0 SHAs (4 versions stale). Already in Task 10 PRE-FLIGHT per STATUS forward-looking HALT 7 / 8. The sha-stability test is the durable extension: every shipped artifact's documented SHA must match its on-disk SHA at CI time.

**Effort**: **0.5 sessions** for the refresh (already-scoped); **0.5 sessions** to author the stability test.

**Source / deps**: derived parquets + PROVENANCE.md + CI (B.9).

**Risks**: low.

**Manuscript impact**: direct — manuscript cites SHAs.

**Priority**: must-have for Phase D (refresh); CI test is high-value pre-Phase-D.

**Execution dependency**: refresh blocked by V3b parquet finalization (done at `b0c8b4a`); test blocked by B.9.

### B.12. Snapshot regression test (per-column SHA manifest)

**Why**: every release tags a per-column SHA manifest; subsequent release CI fails if any "stable" (`comparability_class != within_era`) column drifts. Defends L5 (LLM forgets to re-probe adjacent years) and L11 (stale roadmap claim).

**Effort**: **1 session**.

**Source / deps**: derived parquets; schema CSVs.

**Risks**: low.

**Manuscript impact**: indirect.

**Priority**: medium.

**Execution dependency**: B.9.

### B.13. Aggregate — robustness Tier-1 must-haves

The "robust and useful pre-submission" floor:
- B.1 (smoke retag) — 0.5
- B.2 (dtype parity) — 1
- B.3 (canonical-filter invariants) — 1
- B.4 (row-count conservation) — 1
- B.5 (cross-product join parity) — 1
- B.9 (CI) — 1
- B.10 (end-to-end smoke) — 1

**Subtotal: ~6.5 sessions for the robustness floor.** B.6–B.8, B.11 (test only), B.12 add another ~5 sessions if all included.

---

## §C. Usability / convenience / quickstarts

### C.1. State-stratified live-birth denominator file

**Why**: current `stratified_denominators.csv` covers race × age × Hispanic but NOT state. State-stratified rates are a primary analytic need (state-level disparity studies). Natality has state from 1990–2024 (suppressed only in fetal-death V1 era 2005+); a `stratified_denominators_state.csv` is the natural sibling.

**Effort**: **1 session** (mirror of existing `build_stratified_denominators.py`, additional dimension).

**Source / deps**: natality derived parquet.

**Risks**: low. State × race × age × Hispanic × year grows the CSV from ~4900 rows to maybe ~200K rows — still manageable.

**Manuscript impact**: directly supports "Joint-use design" Strengths.

**Priority**: high.

**Execution dependency**: none.

### C.2. R quickstart (`quickstart.R`)

**Why**: mirror `quickstart.py`. Verify `arrow::read_parquet()` round-trip; document R package dependencies (arrow, dplyr).

**Effort**: **1 session**.

**Source / deps**: existing `fetal_death/quickstart.py` as template; existing R-side parquet reading is well-supported.

**Risks**: low.

**Manuscript impact**: minor — supports *Accessibility* Strengths claim ("readable in Python, R, Stata") which is currently asserted without a worked R example.

**Priority**: high. Concrete win for the R-using epidemiology community.

**Execution dependency**: none.

### C.3. Stata + SAS quickstarts (pointer files)

**Why**: even a 1-page pointer file for Stata/SAS users telling them "Stata 17+ supports `import parquet`; otherwise convert via Python or DuckDB" is a usability win. Hard to ship full quickstarts without Stata/SAS licenses on the build machine.

**Effort**: **0.5 sessions** (each is a short instruction file; full worked examples deferred).

**Source / deps**: published Stata/SAS docs; one DuckDB-based conversion path.

**Risks**: low.

**Manuscript impact**: indirect.

**Priority**: medium.

**Execution dependency**: none.

### C.4. DuckDB views file (`views.sql`)

**Why**: many users prefer SQL. A `views.sql` defining canonical filters + common joins as DuckDB-compatible views over the parquets means zero Python is needed for ad-hoc analyses.

**Effort**: **0.5–1 session**.

**Source / deps**: existing canonical-filter definitions; DuckDB.

**Risks**: low.

**Manuscript impact**: minor — extends `Accessibility`.

**Priority**: medium-high. High value-per-session ratio.

**Execution dependency**: none.

### C.5. Pre-computed cross-tab CSVs for top NVSR cells

**Why**: a `csv/published_tabulations/` folder with the top-10 most-cited NVSR-equivalent tabulations (per-year × per-state × per-race counts, per-year × age-band fertility rates, etc.) means users who don't want to load the parquet can still cite HVS.

**Effort**: **1 session**.

**Source / deps**: derived parquets + canonical filters.

**Risks**: low; pure derivation. But maintenance burden: every parquet bump requires regenerating these.

**Manuscript impact**: minor.

**Priority**: medium. The maintenance tax is the friction.

**Execution dependency**: stable parquet state.

### C.6. Worked-example notebooks (5 listed in KICKOFF §B.c)

Five named in KICKOFF.md §B.c:

| Notebook | Effort | Priority | Reason |
|---|---|---|---|
| C.6.a `maternal_age_stratified_imr.ipynb` (linked file) | 1 session | high | Replicable IMR-by-maternal-age curve; covers the linked file (currently no worked example) |
| C.6.b `preterm_outcomes_time_series.ipynb` (FD + natality + linked) | 1–2 sessions | high | Most-cited HVS use case per literature scan (preterm-birth secular trends) |
| C.6.c `cross_race_fetal_mortality.ipynb` (V3a/V3b demo) | 1 session | medium-high | Demonstrates the V3a/V3b backward extension's analytic value + B3 1-digit-recode caveats |
| C.6.d `education_gradient.ipynb` (within-era only) | 1 session | medium | Documents the 1989/2003 boundary problem the manuscript invokes |
| C.6.e `state_reporting_quirks.ipynb` (OK, MD, MA, LA) | 1 session | medium | Operationalizes COMPARABILITY notes |

**Aggregate effort for all five: 5–6 sessions.** Recommend C.6.a + C.6.b + C.6.c (3–4 sessions) as the "robust and useful" middle ground; C.6.d + C.6.e are nice-to-have.

### C.7. CLI tool (`hvs` command)

**Why**: `hvs count fetal_deaths --year 2020 --race AIAN` style wrapper for common queries.

**Effort**: **1–2 sessions**.

**Source / deps**: existing quickstart.py code + click or argparse.

**Risks**: low.

**Manuscript impact**: minor — supports *Accessibility*.

**Priority**: low-medium. The DuckDB-views path (C.4) covers most of the same use case with less code.

**Execution dependency**: none. Recommend deferring or replacing with C.4.

### C.8. Validated pre-joined "perinatal record" parquet

**Why**: one row per linked-file infant with fetal-death sibling records flagged. Limited by NCHS identifier suppression but partial joins are possible via maternal demographics + state + year.

**Effort**: **2–3 sessions** (research-grade derivation; needs validation grid).

**Source / deps**: all three parquets; maternal-identifier proxy strategy.

**Risks**: high. NCHS identifier suppression in V1-era FD limits join success rate; results may be too sparse to be useful. Methodology-paper territory.

**Manuscript impact**: substantial if it works (would be a manuscript-level contribution); zero if it doesn't.

**Priority**: defer to post-v1. Genuine research extension, not infrastructure.

**Execution dependency**: requires a methodology-paper subproject.

### C.9. Aggregate — usability Tier-1 high-value items

- C.1 (state-stratified denominators) — 1
- C.2 (R quickstart) — 1
- C.4 (DuckDB views) — 0.5–1
- C.6.a + C.6.b + C.6.c (3 notebooks) — 3–4

**Subtotal: ~5.5–7 sessions for the usability floor.**

---

## §D. Cross-product / joint-use enhancements

### D.1. Three-product perinatal mortality joint computation

**Why**: rate = (fetal deaths 28+wk + early neonatal deaths <7d) / (live births + fetal deaths 28+wk) × 1000, computed using all three products. Currently only fetal mortality (single product) is demoed in the existing `joint_use_demo.ipynb`. This is the *unique* analytical capability HVS provides that no single product can deliver.

**Effort**: **1 session** (extends `joint_use_demo.ipynb` Section C or new section).

**Source / deps**: all three parquets + NVSR 73-09 Table A for validation.

**Risks**: low.

**Manuscript impact**: directly supports the "designed for joint use" central claim. Currently the manuscript invokes this without a worked example outside the paper.

**Priority**: high.

**Execution dependency**: none.

### D.2. Section B 2017 race-stratified NVSR validation (deferred Task 4 fragment)

**Why**: Task 4 PRE-FLIGHT (2026-05-11) deferred this fragment. Section B in `joint_use_demo.ipynb` currently shows joint-use machinery but doesn't validate cell-by-cell against NVSR for 2017 by maternal race.

**Effort**: **0.5 sessions**.

**Source / deps**: relevant NVSR fetal-mortality table for 2017 (PDF location to be verified at PRE-FLIGHT per L9).

**Risks**: NVSR PDF cell location must be L9-verified.

**Manuscript impact**: closes a documented loose end; supports `Validation` claim count (currently 88/88).

**Priority**: must-have.

**Execution dependency**: none.

### D.3. Cross-product timeline figure (NEXT_STEPS §15 Task 8)

**Why**: a single figure showing all three products' coverage on one timeline with era boundaries. Already scoped in NEXT_STEPS §15 Task 8 (estimated half a session). Manuscript's Coverage paragraph would reference it.

**Effort**: **0.5–1 session**.

**Source / deps**: era-boundary metadata in each subproject's COMPARABILITY.

**Risks**: low.

**Manuscript impact**: direct — likely becomes Figure 1.

**Priority**: must-have. Already in NEXT_STEPS.

**Execution dependency**: none.

### D.4. Cross-product reproducibility figure

**Why**: fetal-mortality rate + IMR + preterm rate + LBW rate on one panel, documented sources for each. Visual reproducibility cross-check.

**Effort**: **1 session**.

**Source / deps**: all three parquets + NVSR sources.

**Risks**: low.

**Manuscript impact**: medium — potential Figure 2.

**Priority**: medium-high.

**Execution dependency**: D.1.

### D.5. Aggregate — cross-product Tier-1 must-haves

- D.1 (perinatal mortality joint) — 1
- D.2 (Section B race validation) — 0.5
- D.3 (timeline figure / Task 8) — 0.5–1
- D.4 (reproducibility figure) — 1

**Subtotal: ~3–3.5 sessions.**

---

## §E. Documentation / discoverability

### E.1. `CHANGELOG.md` at monorepo root

**Why**: no CHANGELOG exists. One section per version (v1.0 → v1.x → …) consolidates the per-version delta currently scattered across subproject `ABOUT_THIS_RELEASE.md`, DECISION_LOG, FIX_LOG.

**Effort**: **0.5 sessions**.

**Source / deps**: existing receipts + ABOUT_THIS_RELEASE files.

**Risks**: low.

**Manuscript impact**: minor — supports *Reproducibility*.

**Priority**: must-have, pre-Phase D.

**Execution dependency**: none.

### E.2. Migration guides

**Why**: two migrations to document:
- `migrations/v2.7.0-to-v2.8.0-natality.md` (column renames `year → data_year` etc; sample sed/awk recipes for legacy code).
- `migrations/v2.0.0-to-v2.3.0-fetal-death.md` (V2.1 transition years + V3a + V3b backward extension; sample query updates for the new years_available cells).

**Effort**: **0.5–1 session** each (1–2 total).

**Source / deps**: DECISION_LOG entries.

**Risks**: low.

**Manuscript impact**: minor — *Accessibility*.

**Priority**: high.

**Execution dependency**: none.

### E.3. Worked-example FAQ

**Why**: "how do I compute the perinatal mortality rate?", "how do I get state-level data?", "what's the right canonical filter for my analysis?" — natural complement to the existing per-product FAQ files. Sits at `docs/WORKED_EXAMPLE_FAQ.md`.

**Effort**: **0.5 sessions**.

**Source / deps**: existing notebooks + JOINT_USE_GUIDE + COMPARABILITY.

**Risks**: low.

**Manuscript impact**: minor — *Accessibility*.

**Priority**: medium-high.

**Execution dependency**: ideally after D.1 (provides the perinatal-mortality answer).

### E.4. Cross-product `docs/COMPARABILITY.md`

**Why**: synthesizes within_era / cross_era caveats from both subprojects' COMPARABILITY docs. Currently a user must read `natality/docs/COMPARABILITY.md` AND `fetal_death/COMPARABILITY.md` separately to know cross-product comparability rules.

**Effort**: **1 session**.

**Source / deps**: both COMPARABILITY files.

**Risks**: low.

**Manuscript impact**: medium — supports manuscript *Comparability* Strengths.

**Priority**: high.

**Execution dependency**: none.

### E.5. PRIOR_ART.md updates (from §A.7 + literature-gap agent)

**Why**: three concrete additions from the literature-gap re-verification:
1. Add a "GitHub precursors" subsection: `Mikuana/vitalstatistics`, `arebe/cdc-natality`, `damiancclarke/nchs-fetaldata`. Frame as "partial precursors but none harmonize across the 1989/2003 boundary, none cover all three products, none validate against NVSR, none published as DRP." Pre-empts reviewer "this has been done on GitHub" pushback.
2. Add Hoyert et al. 2024 ([PubMed 38143212](https://pubmed.ncbi.nlm.nih.gov/38143212/)) + NICHD Stillbirth WG July 2024 ([report](https://www.nichd.nih.gov/sites/default/files/inline-files/NICHD_Stillbirth_WG_Report_July_2024_508.pdf)) — recent (post-Ananth-2022) evidence the gap persists. Closes the literature thread to 2024.
3. Optional one-sentence mention of `HL7/fhir-bfdr` (prospective FHIR-based reporting; doesn't retro-harmonize). Defuses any "FHIR will solve this" reviewer comment.

**Effort**: **0.5 sessions**.

**Source / deps**: existing PRIOR_ART.md.

**Risks**: low. Don't reword Ananth 2022 framing (it's the load-bearing citation; reinforced not weakened by new searches).

**Manuscript impact**: direct — manuscript's *Data resource basics* paragraph already cites Ananth; one-sentence addition citing Hoyert 2024 lands cheaply.

**Priority**: must-have, pre-Phase D.

**Execution dependency**: none.

### E.6. `PROJECT_STRUCTURE.md` upgrade

**Why**: current file is good but doesn't include (a) the notebook dependencies graph, (b) the build-order DAG (raw zip → yearly_clean → harmonized → derived), (c) the "which file to read first by use case" matrix.

**Effort**: **0.5 sessions**.

**Source / deps**: existing PROJECT_STRUCTURE.md + scripts inventory.

**Risks**: low.

**Manuscript impact**: minor.

**Priority**: medium.

**Execution dependency**: none.

### E.7. CODEBOOK extensions

**Why**: per-variable historical-value-distribution panels; sentinel-code disambiguation tables; era-by-era coding-scheme diff. Currently the codebook has variable definitions but not the per-era code-distribution evidence that would let a researcher choose whether to use a variable across the boundary.

**Effort**: **1–2 sessions** per product (~2–4 sessions total).

**Source / deps**: derived parquets.

**Risks**: low; large surface.

**Manuscript impact**: minor — extends *Comparability classification* claim.

**Priority**: medium. Diminishing returns vs. the existing CODEBOOK.

**Execution dependency**: none.

### E.8. NCHS-source-data SHA manifest at sub-project level

**Why**: confirms a downstream user replicating from scratch gets bit-identical inputs. Currently each subproject has `file_inventory.csv` with source-zip SHAs; cross-product manifest sits at monorepo root.

**Effort**: **0.5 sessions**.

**Source / deps**: existing file_inventory.csv files in both subprojects.

**Risks**: low.

**Manuscript impact**: minor — supports *Reproducibility*.

**Priority**: medium-high.

**Execution dependency**: none.

### E.9. Aggregate — documentation Tier-1 must-haves

- E.1 (CHANGELOG.md) — 0.5
- E.2 (migration guides; 2) — 1–2
- E.4 (cross-product COMPARABILITY) — 1
- E.5 (PRIOR_ART updates) — 0.5
- E.8 (cross-product SHA manifest) — 0.5

**Subtotal: ~3.5–4.5 sessions.** E.3, E.6, E.7 add another ~3 sessions if all included.

---

## §F. Performance / distribution / reproducibility tooling

### F.1. Parquet column-dictionary tuning

**Why**: `use_dictionary=True` per low-cardinality column (race, sex, version_flag, state codes) typically yields 30–50% size reduction with no schema change.

**Effort**: **0.5 sessions**.

**Source / deps**: existing harmonized + derived parquets.

**Risks**: low; but byte-comparison test (B.12) must accommodate a one-time SHA shift.

**Manuscript impact**: minor.

**Priority**: medium.

**Execution dependency**: none, but conflicts with B.12 sha-stability if not done first.

### F.2. Dockerfile (pinned env, full pipeline rebuild)

**Why**: one `docker run` rebuilds every parquet end-to-end. Closes the reproducibility loop the manuscript currently advertises.

**Effort**: **1–2 sessions**.

**Source / deps**: existing requirements.txt; raw zips.

**Risks**: medium. Building a runnable image with the right Python + pandas + pyarrow versions may surface dependency-pinning issues (current requirements.txt uses `>=`).

**Manuscript impact**: direct — supports *Reproducibility* Strengths.

**Priority**: must-have for Phase D / v1.1 release.

**Execution dependency**: ideally with F.3 (lockfile).

### F.3. `uv` / `poetry` lockfile for deterministic Python env

**Why**: `requirements.txt` uses `>=` not `==`. A lockfile pins exact versions so a fresh install always produces the build-time env.

**Effort**: **0.5–1 session**.

**Source / deps**: existing requirements.txt.

**Risks**: low. Choose `uv` over `poetry` for speed + simpler conventions; both work.

**Manuscript impact**: indirect — supports *Reproducibility*.

**Priority**: high.

**Execution dependency**: pairs with F.2; helps B.9 (CI).

### F.4. GitHub release artifacts

**Why**: attach the parquets to a GitHub Release alongside Zenodo. Users behind Zenodo-blocking firewalls have an alternate download path.

**Effort**: **0.5 sessions**.

**Source / deps**: existing parquets.

**Risks**: low. GitHub LFS quotas; cost minimal at this size.

**Manuscript impact**: minor — supports *Accessibility*.

**Priority**: medium.

**Execution dependency**: Phase D Task 10 / public-repo v1.x sync.

### F.5. `scripts/run_pipeline.py` from-scratch smoke (timing benchmark)

**Why**: verify clean rebuild from raw zips in <30 min on a standard laptop (current advertised: "tens of minutes" / "approximately ninety minutes" depending on product). Time and document.

**Effort**: **0.5–1 session** (overlaps with B.10).

**Source / deps**: existing pipeline; raw zips.

**Risks**: low.

**Manuscript impact**: direct — current manuscript cites "approximately six minutes" (FD) and "approximately ninety minutes" (natality); these need re-verification post-V3b.

**Priority**: must-have, pre-Phase D.

**Execution dependency**: B.10.

### F.6. CDN mirror (CloudFront / S3 / GitHub LFS)

**Why**: users behind Zenodo-blocking firewalls have alternate. Overkill at v1.0 scale; relevant if downloads scale up.

**Effort**: **1–2 sessions** depending on infra choice.

**Source / deps**: AWS / GitHub LFS / Cloudflare R2 — out-of-pocket cost.

**Risks**: medium (recurring cost).

**Manuscript impact**: minor — extends *Accessibility*.

**Priority**: defer. F.4 (GitHub release) is a cheap subset.

**Execution dependency**: none.

### F.7. Aggregate — performance Tier-1 must-haves

- F.2 (Dockerfile) — 1–2
- F.3 (lockfile) — 0.5–1
- F.5 (timing benchmark) — 0.5–1

**Subtotal: ~2–4 sessions.** F.1 + F.4 add another ~1 session if included.

---

## §G. Cumulative effort + suggested execution order

### G.1. Per-dimension subtotals (Tier-1 must-haves + Tier-2 high-value, EXCLUDING Tier-5 backward extensions)

| Dimension | Tier-1 floor | Tier-2 add'l |
|---|---|---|
| §A. Data extensions | 1–2 (latest-year refresh A.1 only) | 1–2 (matched-multiples A.5) |
| §B. Robustness / testing | 6.5 (B.1–B.5 + B.9 + B.10) | 5 (B.6, B.7, B.8, B.11, B.12) |
| §C. Usability / convenience | 5.5–7 (C.1, C.2, C.4, C.6.a-c) | 2–3 (C.3, C.5, C.6.d-e) |
| §D. Cross-product / joint-use | 3–3.5 (D.1–D.4) | 0 (none, all are Tier-1) |
| §E. Documentation | 3.5–4.5 (E.1, E.2, E.4, E.5, E.8) | 3 (E.3, E.6, E.7) |
| §F. Performance / distribution | 2–4 (F.2, F.3, F.5) | 1 (F.1, F.4) |
| **Subtotal** | **~22–27 sessions** | **+12–14 sessions** |

### G.2. Tier-5 backward extensions (excluded from above)

| Candidate | Effort |
|---|---|
| A.2 Natality 1968–1989 | 6–10 |
| A.3 Linked 1983–2004 | 8–14 |
| C.8 Perinatal record parquet | 2–3 (methodology research) |
| **Subtotal** | **~16–27 sessions** |

### G.3. Total honest cumulative-effort range

- **Conservative (Tier-1 must-haves only)**: ~22–27 sessions of Phase C
- **Middle ground (Tier-1 + Tier-2; "robust and useful" without big backward extensions)**: ~34–41 sessions
- **Maximalist (everything including A.2 + A.3 + C.8)**: ~50–68 sessions

Plus Phase D (Task 9 + Task 10 + public-repo v1.x sync + manuscript re-pass): ~3 sessions on top of any prefix above.

**Phase B's own forecast for this dimension**: the maximalist interpretation of the user's directive expands pre-submission scope by **~30–60 additional sessions**, which significantly delays manuscript submission. The user should explicitly choose a prefix in answering Q33 (effort ceiling) below.

### G.4. Suggested execution order (Phase C task entries)

Grouped to minimize parquet rebuilds and maximize CI gate per session.

**Tier 1 — pre-Phase-D must-haves (~7–9 sessions):**

1. **C8.1** [robustness] B.1 retag fetal-death smoke + B.2 dtype parity test (both products) [0.5 + 1 = 1.5]
2. **C8.2** [data] A.1 latest-year refresh (fetal 2023+2024 + linked 2024) [1–2]
3. **C8.3** [cross-product] D.3 cross-product timeline figure (Task 8) + D.1 perinatal mortality joint demo + D.2 Section B 2017 race validation [0.5 + 1 + 0.5 = 2]
4. **C8.4** [robustness] B.3 canonical-filter invariants + B.4 row-count conservation + B.5 cross-product join parity [3]
5. **C8.5** [distribution] F.3 lockfile + F.2 Dockerfile [1.5–3]
6. **C8.6** [robustness] B.9 GitHub Actions CI wiring (runs B.1–B.5 on every push) [1]
7. **C8.7** [robustness] B.10 end-to-end smoke from monorepo root [1]
8. **C8.8** [docs] E.1 CHANGELOG.md + E.5 PRIOR_ART.md update [1]

**Tier 1 subtotal: ~13–15 sessions.** This is the recommended "robust and useful" floor before Phase D.

**Tier 2 — high-value additions (~10–13 sessions, decide per item):**

9. **C8.9** [usability] C.1 state-stratified denominators + C.2 R quickstart + C.4 DuckDB views [2.5–3]
10. **C8.10** [usability] C.6.a maternal_age_stratified IMR + C.6.b preterm time-series + C.6.c cross-race FD demo [3–4]
11. **C8.11** [docs] E.2 v2.7→v2.8 + v2.0→v2.3 migration guides + E.4 cross-product COMPARABILITY.md + E.8 SHA manifest [3–4]
12. **C8.12** [robustness] B.6 mutation-test scaffolding + B.7 L13 audit + B.8 L14 audit + B.11 SHA-stability test + B.12 snapshot regression [3–4]
13. **C8.13** [distribution] F.1 dict tuning + F.4 GitHub release + F.5 timing benchmark [1.5–2]
14. **C8.14** [docs] E.3 worked-example FAQ + E.6 PROJECT_STRUCTURE upgrade [1]
15. **C8.15** [usability] C.6.d education-gradient + C.6.e state-quirks notebooks [2]

**Tier 2 subtotal: ~16–20 sessions.** Cumulative Tier-1+2: **~29–35 sessions.**

**Tier 3 — defer-or-skip (decide per item):**

16. **C8.16** [data] A.5 matched-multiples ancillary release [1–2]
17. **C8.17** [docs] E.7 CODEBOOK extensions [2–4]
18. **C8.18** [usability] C.3 Stata/SAS quickstart pointer files [0.5]
19. **C8.19** [usability] C.5 pre-computed cross-tab CSVs [1]
20. **C8.20** [usability] C.7 CLI tool (likely deferred in favor of C.4 DuckDB views) [1–2 if pursued]

**Tier 3 subtotal: ~5–9 sessions.**

**Tier 5 — backward extensions (big swings, separate Zenodo deposits):**

21. **C8.21** [data] A.2 natality 1968–1989 — multi-session subproject [6–10]
22. **C8.22** [data] A.3 linked 1983–2004 — multi-session subproject [8–14]
23. **C8.23** [research] C.8 perinatal-record pre-joined parquet (methodology research) [2–3]

**Tier 5 subtotal: ~16–27 sessions.**

### G.5. Recommendation

The user said "everything possible to make it as robust and useful as possible before paper or zenodo." The honest tradeoff:

- **Tier 1 only (~13–15 sessions)**: ships a substantially more robust HVS than today; CI + tests + Docker + latest-year refresh + perinatal-mortality joint demo + cross-product figure. Submit manuscript with current 1990-2024 natality + 1982-2024 (post-refresh) fetal-death + 2005-2024 (post-refresh) linked envelope. **Recommended prefix if the user weights "ship sooner" highly.**
- **Tier 1 + Tier 2 (~29–35 sessions)**: ships a maximally polished v1.0 HVS including R quickstart, 3 worked-example notebooks, migration guides, mutation tests. **Recommended prefix if the user weights "ship robust" highly and is willing to absorb ~6 weeks of additional pre-submission work.**
- **Tier 1 + Tier 2 + Tier 5 (~45–62 sessions)**: ships v1.1 with natality 1968–1989 + linked 1983–2004 backward extensions, doubling natality coverage. **Substantial timeline extension** (~3–4 months of additional pre-submission work at one session per ~half-day). Re-paragraphs manuscript twice (or once at v1.0 with v1.1 noted as imminent). **Recommended only if the user explicitly wants the manuscript to launch with maximum-extent coverage.**

The middle option is my recommended prefix unless the user signals otherwise in Q33.

---

## §H. Open questions for the human

In addition to Q32, Q33, Q34 from STATUS 2026-05-12T19:15Z (Phase B scope inclusivity; Phase C effort ceiling; in-scope-vs-out-of-HVS-mission boundary):

**Q35. Tier prefix authorization.** Which prefix authorizes Phase C? Options:
- (a) Tier 1 only (~13–15 sessions); ship after.
- (b) Tier 1 + Tier 2 (~29–35 sessions); ship after. **Recommended unless effort budget is tight.**
- (c) Tier 1 + Tier 2 + Tier 5 (~45–62 sessions); ship after the backward extensions.
- (d) Custom — user lists which §A–§F candidates to include.

**Q36. Backward-extension scope decision.** If Tier 5 is in scope: which of A.2 (natality 1968–1989) and A.3 (linked 1983–2004) goes first? My default is **A.2 first** (shorter; simpler revision-boundary story; cleaner sibling of V3b just shipped); A.3 follows because it benefits from A.2's 1978-cert layout work.

**Q37. Latest-year refresh sequencing (A.1).** Recommend executing A.1 **first** in Phase C (1 session, cheapest win, defers no decision). Confirm.

**Q38. R-quickstart-only vs full Stata/SAS/R coverage.** Default: ship R (C.2, full quickstart) + Stata/SAS pointer-files (C.3, half-page each). Confirm or override.

**Q39. CLI tool (C.7) vs DuckDB views (C.4).** Both target ad-hoc query convenience. C.4 is cheaper and DuckDB's SQL surface covers most use cases. Default: ship C.4, defer C.7. Confirm.

**Q40. Manuscript re-paragraph cadence.** If Tier 5 is in scope, do we re-paragraph the manuscript Coverage section twice (once for v1.0 at end of Tier 2; once for v1.1 at end of Tier 5) or hold the manuscript until Tier 5 completes? Default: **single submission after Tier 2; Tier 5 ships as v1.1 with an *Update* note in IJE or a v2.0 Zenodo deposit later**.

**Q41. Tier-3 items**: which are worth pulling into Phase C, if any? Default: defer all to post-v1 ancillary releases.

**Q42. Phase B-2 trigger conditions.** If Phase C surfaces a candidate not in this report (e.g., a reviewer comment on the manuscript draft suggests a new convenience layer), is it a §11 plan-update or do we treat it as in-Phase-C scope creep? Default: §11 plan-update for any candidate adding >1 session.

---

## §I. Phase B forbidden-actions audit (per KICKOFF.md)

Verifying Phase B did NOT cross any forbidden boundary:

- ✅ No canonical-state mutation (only `EXPLORATION_REPORT.md` + `STATUS.md` section + `DECISION_LOG.md` entry).
- ✅ No DO-phase work on any candidate.
- ✅ Halt-and-ask step preserved (this report + Q35–Q42 + DECISION_LOG status PENDING USER REVIEW).
- ✅ No hallucinated data sources — all 8 §A candidate-availability claims sibling-derived from the existing `<YYYY>FetalUserGuide.pdf` / `Nat<YYYY>.zip` conventions and verified via WebFetch (full URL list in §A.9 negative results + dispatched agent log).
- ✅ No "PDF X needs OCR" assertion (only fetal-death V3b PDFs were assessed for OCR previously; this session did not probe new PDFs at content level).
- ✅ No inflated / deflated effort estimates. All estimates anchored on V3b's empirical 2–3 session unit (`b763e5c → c598ce7 → b0c8b4a`) and surfaced as honest ranges.

## §K. Plan-update proposal (PENDING USER REVIEW)

This proposal would amend KICKOFF.md "Current planned sequence" and NEXT_STEPS.md §15 to embed the user-authorized Phase C prefix. The actual amendment is a future commit; this section documents the structure so the user can confirm shape before content.

### K.1. KICKOFF.md Phase C population (diff sketch)

Current KICKOFF.md (commit `306370e`):

```
### Phase C — EXECUTE PHASE B-PROPOSED ADDITIONS (subsequent sessions)

To be populated by Phase B's plan-update proposal. Estimated 5-20 sessions
depending on Phase B-recommended scope.
```

Proposed replacement, parameterized by user choice in Q35 (this draft assumes **Tier 1 + Tier 2 = ~29–35 sessions**; trim for Tier-1-only or extend for Tier-5):

```
### Phase C — EXECUTE PHASE B-PROPOSED ADDITIONS

Per Phase B EXPLORATION_REPORT.md §G.4 (drafted 2026-05-12T20:30Z) and user
authorization 2026-05-12T<AUTHORIZED-TIMESTAMP> (Q35: Tier 1 + Tier 2; see
DECISION_LOG <AUTHORIZED-TIMESTAMP>). Each task below uses the full §4
five-phase discipline (PRE-FLIGHT, SMOKE, DO, VERIFY, RECEIPT) per
NEXT_STEPS.md §15 entries.

#### Tier 1 — pre-Phase-D must-haves
- C8.1 SMOKE retag + dtype parity (B.1 + B.2)              [1.5 sessions]
- C8.2 Latest-year refresh: fetal 2023+2024, linked 2024   [1-2 sessions]
- C8.3 Cross-product Tier-1: timeline + perinatal joint    [2 sessions]
- C8.4 Invariant tests: filter + row-count + join          [3 sessions]
- C8.5 Distribution: lockfile + Dockerfile                 [1.5-3 sessions]
- C8.6 CI: GitHub Actions wiring                           [1 session]
- C8.7 End-to-end pipeline smoke                           [1 session]
- C8.8 CHANGELOG + PRIOR_ART update                        [1 session]

#### Tier 2 — high-value additions
- C8.9 Usability: state denominators + R + DuckDB views    [2.5-3 sessions]
- C8.10 Worked-example notebooks (3 of 5)                  [3-4 sessions]
- C8.11 Migration guides + cross-product COMPARABILITY      [3-4 sessions]
- C8.12 Mutation tests + L13/L14 audits + SHA stability    [3-4 sessions]
- C8.13 Performance + GitHub release artifacts             [1.5-2 sessions]
- C8.14 Worked-example FAQ + PROJECT_STRUCTURE upgrade     [1 session]
- C8.15 Notebooks 4-5 (education, state quirks)            [2 sessions]

Cumulative effort: ~29-35 sessions. Subject to per-task PRE-FLIGHT halt
discipline and DECISION_LOG entries for any scope changes.

### Phase D — PRE-PAPER POLISH + ZENODO + SUBMIT (after Phase C completes)
[unchanged from 2026-05-12T19:15Z]
```

If the user chooses Q35 (a) Tier 1 only, drop the Tier 2 block and reduce to ~13–15 sessions. If (c) including Tier 5, append a Phase C-3 block:

```
#### Tier 5 — backward extensions (separate Zenodo deposits)
- C8.21 Natality 1968-1989 backward extension              [6-10 sessions]
- C8.22 Linked 1983-2004 backward extension                [8-14 sessions]
- C8.23 Perinatal-record pre-joined parquet (research)     [2-3 sessions]

Cumulative effort: +16-27 sessions. Manuscript timing decision: re-paragraph
twice (v1.0 at end of Tier 2 + v1.1 at end of Tier 5) OR hold submission
until Tier 5 completes. See Q40.
```

### K.2. NEXT_STEPS.md §15 task-entry template

Each Phase C task gets one §15 entry. Template (one fully-worked example follows for **C8.2 Latest-year refresh** since it's the recommended first Phase C task per Q37):

```markdown
### Task C8.2 — Latest-year refresh (fetal death 2023+2024, linked 2024)

**Goal.** Extend fetal-death from 1982-2022 (41 yrs) to 1982-2024 (43 yrs) and
linked from 2005-2023 (19 yrs) to 2005-2024 (20 yrs) by parsing the
newly-released NCHS public-use files. Natality stays at 1990-2024 since 2025
is not yet released.

**Why this matters.** The cheapest single pre-submission win identified by
Phase B (EXPLORATION_REPORT.md §A.1). Three NCHS source files were released
between the most recent HVS shipment and this task:
- `Fetal2023US_COD.zip` (NCHS released 2024-12-05)
- `Fetal2024US_COD.zip` (NCHS released 2026-02-04)
- `2024PE2023CO.zip` (NCHS released 2026-01-22)
All three are sibling-layout extensions of the V1 era already parsed.

**PRE-FLIGHT inputs.**
- 3 NCHS source zips (URLs in EXPLORATION_REPORT.md §A.1).
- 3 user-guide PDFs (sibling-derived URLs in §A.1).
- Existing parser `fetal_death/scripts/01_import/parse_fetal_year.py` +
  `field_specs.py` (post-V3b SHAs in STATUS 2026-05-12T18:45Z FL-HALTs).
- Existing natality-linked import code under `natality/scripts/01_import/`.
- Field-value snapshot per Convention 3 of:
  - `fetal_death/external_validation_targets.csv` (need to extend with 2023+2024 NVSR targets or user-guide control counts)
  - `fetal_death/file_inventory.csv` (need to extend with 2023+2024 zip + PDF SHAs)
  - `fetal_death/harmonized_schema.csv` `years_available` cells
  - All forward-looking HALTs from `task7_v3b-complete` receipt.

**SMOKE plan.**
- Tier 0: byte-position diff between 2024 user guide and 2022 (sibling-derive).
- Tier 1: 100-record parse of 2024 fetal-death; assert plausible distribution.
- Tier 2: full-year 2024 parse + per-year control-count match.
- Tier 3: 1982-2024 re-harmonize + V3b-era byte-clean regression.

**DO scope.**
- Add 3 rows to fetal-death `file_inventory.csv`; 1 row per year to
  `external_validation_targets.csv`; extend `harmonized_schema.csv`
  `years_available`.
- If layout-byte deltas surface vs 2022, extend `field_specs.py` with a new
  era_tag (probably re-using 2022 era_tag if no deltas).
- Re-harmonize + re-derive fetal-death parquet (now 1982-2024).
- Re-harmonize + re-derive linked parquet (now 2005-2024).
- Bump fetal-death version v2.3.0 → v2.4.0; bump natality+linked v2.8.0 → v2.9.0.
- Update CITATION.cff + .zenodo.json + ABOUT_THIS_RELEASE.md + README.md.

**VERIFY criteria.**
- Per-year counts 2023+2024 match user-guide control counts byte-exact.
- V3b baseline byte-clean regression: 0/162 columns drift on 1982-2022 slice.
- Linked 2024 per-year count matches NCHS Linked File 2024 report control.
- Manuscript Coverage paragraph numerics updated where applicable.

**RECEIPT requirement.** Standard template. Self-check: did I run V3b
baseline byte-clean comparison? Did I update the manuscript's
"approximately X minutes" pipeline timing if it materially changed?

**Estimated effort.** 1-2 sessions.

**Dependencies.** None.

**Halt-condition flags.** H1, L13 (if layout-byte delta to 2022), L17 (if
SMOKE pins shift). Convention 1 SHAPE-not-VALUE on every new SMOKE.

**Forward-looking HALTs to write in receipt.**
- 2023+2024 zip + PDF SHAs unchanged (record in this receipt's outputs).
- Post-refresh fetal-death + linked parquet SHAs.
- `field_specs.py` SHA unchanged if no era_tag added; new SHA otherwise.
```

The same template applies to every C8.X task; ~30 entries to author. Phase C
PRE-FLIGHT for each is the §5 standard checklist + field-value snapshot
(Convention 3) + the forward-looking HALTs from the prior receipt.

### K.3. KICKOFF.md "Conventions in effect" — no changes proposed

Conventions 1–5 carry forward unchanged. No new conventions surfaced from
Phase B; the existing ones (SHAPE-not-VALUE, DESIGN docstring tag,
Field-value snapshot, Forward-looking HALTs, commit-message brevity) cover
the Phase C surface adequately.

### K.4. Backport scope (per §11.4)

None. Phase B is read-only; no prior receipts are invalidated. The Phase C
work that lands after authorization may surface backports (e.g., L13 audit
in B.7 may find an existing CSV with stale role/description claims), at
which point §11.4 fires per-task.

---

## §J. Receipts pointer

This file's authoring trace:

- **PRE-FLIGHT**: this is a read-only exploration session per KICKOFF Phase B mandate; no separate PRE-FLIGHT entry required (KICKOFF Phase B brief is the PRE-FLIGHT analog).
- **DO**: this file + accompanying STATUS section + DECISION_LOG entry, all created in a single LLM session 2026-05-12T20:00–20:30Z.
- **VERIFY**: forward-looking — user reviews and either authorizes a Phase C prefix (Q35) or requests amendments.
- **RECEIPT**: STATUS.md 2026-05-12T20:30Z section is the canonical session-end record.

External-research agents that contributed to this report:
- Agent `aea960a496472bb6b` (B.a data-extension URL verification, 50 tool uses, ~5min wall clock).
- Agent `a3e650be058a65976` (literature-gap re-verification, 50 tool uses, ~4min wall clock).

Phase B work is now complete; HALT for user authorization before Phase C DO work.
