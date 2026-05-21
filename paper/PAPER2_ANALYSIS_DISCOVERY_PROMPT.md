# Paste this entire document into a fresh LLM chat (no other context)

You are advising the principal investigator on **Paper 2**: an empirical companion paper to the **U.S. Harmonized Vital Statistics (HVS)** microdata resource. Paper 1 (separate) is an IJE *Data Resource Profile* describing the resource itself. **Your job is not to write the paper yet.** Your job is to **study the attached project materials**, identify what analyses this resource **uniquely enables that prior literature could not do with raw NCHS files**, and recommend the **single best analysis** (with 2–3 strong runners-up).

The investigator will attach files from the monorepo `vital-statistics-harmonization`. Read them in the order below. **Do not invent record counts, rates, or validation results** — every number you cite must come from an attached file or be clearly labeled as a placeholder.

---

## 1. What HVS is (60-second orientation)

The U.S. National Center for Health Statistics (NCHS) releases annual **public-use vital statistics microdata** as fixed-width files. Layouts, field names, and code values change across:

1. **Certificate revisions** (1989 → 2003 Standard Certificate of Live Birth / Fetal Death),
2. **Within-revision NCHS reformats** (e.g., natality record length 1500 → 775 bytes in 2006; 2014 OE-based gestational age),
3. **State-by-state staggered adoption** of the 2003 revision (a single year’s file can mix certificate versions by state).

Researchers historically **restrict analyses to single-revision windows** (e.g., 1995–1998, 2001–2002, or 2005+) because no public harmonized longitudinal microdata product existed. NCHS publishes harmonized **aggregate** tables in *National Vital Statistics Reports* (NVSR), but not harmonized **microdata**.

**HVS** harmonizes four NCHS products into **stable Apache Parquet schemas** per product, with:

- Deterministic open-source pipelines re-runnable from public NCHS zips,
- **Byte-exact validation** against published NVSR cells under documented canonical filters,
- Cross-product join keys and documentation for joint rates (fetal mortality, perinatal mortality, infant mortality),
- Explicit comparability notes for every era boundary.

**License:** CC BY 4.0 (data); MIT (code). No RDC required for the public-use envelope described here.

---

## 2. The four products (current envelope — verify in `README.md`)

| Product | Years (in-repo) | Records (approx.) | What it enables |
|---|---|---|---|
| **Natality** | **1968–2024** (57 yr) | ~201.2M | Live births; LBW, preterm, cesarean, demographics; denominator for fetal/IMR rates |
| **Linked birth–infant death** | **1983–2023** (38 cohort yr; **gap 1992–1994**) | ~149.4M | Infant/neonatal/postneonatal deaths linked to birth cohort; IMR; cause groups |
| **Fetal death** | **1982–2024** (43 yr) | ~2.43M | Stillbirth / fetal death; **V3b (1982–1988)** and **V3a (1989–1991)** backward extensions are HVS’s largest *novel* data contribution vs prior public harmonizations |
| **Matched multiples** | 1995–1997, 1995–2000, 2016–2020 (3 windows) | ~1.67M | Twins/triplets/quads with linked infant + fetal deaths in same multiple set |

Each product: harmonized derived parquet + per-year raw parquets + validation CSVs + user guides.

**Pre-1990 natality** (1968–1989): harmonized and shipped; NVSR byte-exact benchmarking is **planned**, not yet complete for all years — flag if your proposal leans heavily on 1968–1989 natality validation.

---

## 3. What is genuinely novel vs prior work (read `docs/PRIOR_ART.md` first)

Prior studies were forced to:

- Use **short uniform windows** inside one certificate revision (Salihu 1995–1998; Willinger 2001–2002),
- Use **published aggregates only** when revisions overlapped (Hogue & Silver through 2005),
- **Exclude Hispanic ethnicity** across 1980–2020 APC work because 2003-revision fields were unavailable cross-boundary (Ananth et al. 2022),
- Analyze **fetal death only from ~1992 or 2005+** in practice, not a 43-year harmonized series across 1978-rev → 1989-rev → 2003-rev.

**No adjacent resource** (IPUMS-International, HMD, IPUMS-NHIS, NBER, ICPSR, GitHub loaders) provides harmonized U.S. natality + linked + fetal death microdata across these boundaries with NVSR validation.

**HVS novelty axes** (use these to score candidate analyses):

| Axis | Why it matters |
|---|---|
| **Longest harmonized fetal-death series (1982–2024)** | Cross **three certificate eras** in one microdata product (1978-rev 1982–1988, early 1989-rev 1989–1991, 1989-rev/V2/V1 1992+) |
| **Natality 1968–2024** | Decades longer than typical single-revision natality studies |
| **Linked cohort 1983–2004 + 2005–2023** | Pre-2005 cohort extension newly harmonized (v4); IMR trends back to 1983 on linked file’s own denominator |
| **Three-product joint rates** | Fetal mortality rate, **perinatal mortality rate**, IMR with aligned strata — previously required ad hoc harmonization per study |
| **Matched multiples** | Twin/triplet/quadruplet complete-set mortality — separate NCHS product, now in same ecosystem |
| **NVSR validation as credibility** | Every proposed headline rate should be checkable against shipped validation tables |

---

## 4. Hard constraints (violating these = infeasible or misleading)

Read **`docs/COMPARABILITY.md`** and **`docs/JOINT_USE_GUIDE.md`** before proposing methods.

1. **No state-level geography in public-use microdata** — NCHS suppresses residence state in harmonized files for many eras. State analyses require RDC / CDC WONDER, not HVS parquets. Do **not** propose “state disparity maps” from HVS alone.

2. **Bridged-race (`maternal_race_bridged`) has product-specific null windows:**
   - Natality stratified CSV / convenience layer: null **2020–2024** (use `maternal_race_ethnicity_5` for 2020+),
   - Fetal death: `maternal_race_bridged` null **2018–2024** in harmonized parquet; stratified denominator CSV null **2020–2024** (2018–2019 bridged populated in CSV),
   - **Joint bridged-race rates: 1992–2002 + 2005–2017 only (24 years)** unless you use bilateral race coding (see COMPARABILITY § “2014 race-coding methodology boundary”).

3. **2014 boundaries (natality + linked + fetal):**
   - **Gestational age / preterm:** switch from LMP-based to obstetric estimate (~1.5–2 pp preterm drop at 2014 — methodology, not biology). Stratify or restrict windows.
   - **Race coding:** bridged-in-Hispanic (pre-2014) vs NH-only bridged (2014+) — **must not** mix on one trend line without explicit era-specific columns (demonstrated in `notebooks/cross_race_fetal_mortality.ipynb`).

4. **Fetal death canonical filter for NVSR-comparable rates:** `tabulation_flag == 2 AND residence_status != 4` (not “all fetal deaths”). V2 era (1992–2002) also needs `version_flag == 'S'` where applicable.

5. **1982–1991 fetal years without natality denominator in joint layer:** V3b/V3a fetal extension is **fetal-only** for 1982–1991 (natality starts 1968 but joint demographic alignment for fetal-mortality *rates* with natality denominator is **1992+** for the convenience CSV path). Analyses using 1982–1991 must be explicit about denominator source (e.g., fetal-only counts/rates, or linked file, not “joint natality denominator”).

6. **Linked file 1992–1994 gap** — permanent NCHS cohort-linkage gap; no imputation.

7. **Perinatal-record row-level sibling join** — explored and deemed **infeasible** at public-use (documented in `docs/perinatal_record_feasibility.md` if attached; C8.19). Do not propose “link every fetal death to its sibling birth record” at microdata level.

8. **Pre-1982 fetal death** — public-use floor is 1982; earlier years are RDC-only.

---

## 5. Reading order (efficient path through attachments)

Read in this sequence. Skip only if the investigator did not attach a file.

### Tier A — Must read (30–45 min)

| Order | File | Why |
|---|---|---|
| A1 | `README.md` | Current envelope, four products, validation summary |
| A2 | `docs/PRIOR_ART.md` | Literature gap + what prior papers could not do |
| A3 | `docs/COMPARABILITY.md` | Era boundaries, 2014 shifts, joint-coverage years, race methodology |
| A4 | `docs/JOINT_USE_GUIDE.md` | Canonical filters, joint rates, denominator files, bridged-race limits |
| A5 | `fetal_death/COMPARABILITY.md` | V3a/V3b caveats, state reporting quirks (LA plurality, OK Hispanic), tabulation_flag semantics |
| A6 | `csv/published_tabulations/README.md` + skim the CSVs listed there | Pre-computed NVSR-reconciled trends 1968–2024 / 1982–2024 without loading parquets |

### Tier B — Strongly recommended (20–30 min)

| Order | File | Why |
|---|---|---|
| B1 | `paper/draft_v2_hmd_styled.md` | Descriptor paper (Paper 1 draft) — what the resource claims; **numbers may be stale** vs README; trust README + validation CSVs for counts |
| B2 | `EXPLORATION_REPORT.md` — §§ **D.1, D.3, C.8, G.4** (search headings) | Pre-scored ideas: perinatal mortality joint, cross-product timeline, matched multiples, execution priorities |
| B3 | `notebooks/joint_use_demo.ipynb` (or describe from README if not attached) | Byte-exact NVSR cells for FMR, race-stratified FMR, **perinatal mortality** joint computation |
| B4 | `notebooks/cross_race_fetal_mortality.ipynb` | 35-year race-stratified FMR panel + 2014 methodology step |
| B5 | `notebooks/preterm_outcomes_time_series.ipynb` | 2014 OE preterm shift + cross-product preterm caveats |
| B6 | `matched_multiples/README.md` + `ABOUT_SOURCE_DATA.md` | 4th product semantics |

### Tier C — If proposing linked / IMR / cohort methods

| File | Why |
|---|---|
| `natality/docs/COMPARABILITY.md` | Natality-only breaks (CA marital status 2017+, etc.) |
| `natality/metadata/external_validation_targets_v3_linked.csv` | IMR / neonatal targets 2005–2023 + pre-2005 cohort rows |
| `fetal_death/external_validation_targets.csv` | Fetal mortality validation cells |

### Tier D — Optional depth

- `PROJECT_STRUCTURE.md` — file locator
- `docs/WORKED_EXAMPLE_FAQ.md` — common user questions
- `VERSION_ROADMAP.md` — what was deferred

---

## 6. Candidate analysis families already identified (do not treat as final)

The project team already surfaced these **starting points**. Your job is to **improve, combine, or supersede** them with evidence-backed reasoning — not to rubber-stamp the default.

| ID | Candidate | HVS-uniqueness hook | Main caveats |
|---|---|---|---|
| **F1** | **Fetal mortality rate trends 1982–2024** by age, race (era-appropriate coding), certificate revision era | **V3b/V3a** extend pre-1992; 43-year harmonized fetal series unprecedented in public microdata | Bridged race ends 2017 (FD) / 2020 (natality CSV); 2014 race + GA breaks; 1982–1991 denominator story |
| **F2** | **Cross-revision comparison** of stillbirth disparities 1982–2024 (revision-era panels with explicit breaks) | Ananth 1980–2020 excluded Hispanic; HVS enables ethnicity + longer span with documented breaks | Must handle 2014 race + GA explicitly; strong methods section required |
| **F3** | **Perinatal mortality rate** (fetal ≥28wk + early neonatal) trends, joint three-product | `joint_use_demo` Section C demonstrates joint computation; NVSR partial coverage | Early neonatal from linked; denominator alignment; not one NVSR headline cell |
| **F4** | **Infant / neonatal mortality 1983–2023** on extended linked cohort | C8.18 linked v4 back to 1983; 19/19 pre-2005 cohort denominators byte-exact | 1992–1994 gap; pre-2005 IMR weighting (1983–1984 RECWT); period vs cohort break 2016 |
| **F5** | **Natality 1968–2024** macro trends (LBW, preterm, cesarean, plurality) | 57-year harmonized natality vs typical 1990+ studies | Pre-1990 NVSR benchmarking incomplete; 2014 OE break; race 2020+ |
| **F6** | **Matched-multiples mortality** (twin/triplet IMR, complete-set vs incomplete-set) | Only HVS ships this as harmonized alongside other vital products | Sparse years (3 windows only); not a long annual series |
| **F7** | **Education / SES gradient** across certificate revision (within-era panels) | `education_gradient.ipynb` pattern — cross-era education not comparable | Within-era only; manuscript must not over-claim cross-era education trends |
| **F8** | **Methodology paper**: “harmonization enables X” simulation — bias from naive pooling vs HVS bilateral methodology | Strong if quantified (e.g., wrong 2014 step if you ignore race coding shift) | Needs crisp counterfactual; risk of sounding like a stats methods note not epidemiology |

---

## 7. What “best contribution” means (scoring rubric)

Rank every candidate analysis you consider on **1–5** (5 = best) on each dimension, then recommend **one primary** and **two alternates**.

| Dimension | Question |
|---|---|
| **Novelty** | Could a competent team do this with raw NCHS files without multi-year harmonization labor? If yes, score lower. |
| **Credibility** | Can headline findings be anchored to NVSR validation cells or clearly documented tolerances? |
| **Scientific impact** | Would AJE, PPE, Paediatric Perinatal Epidemiology, JAMA Network Open, or Lancet Regional Health care? |
| **Feasibility** | Runnable with shipped parquets + docs in &lt; ~6 months PI time? No RDC? No state geography? |
| **Harmonization story** | Does success **depend** on HVS (cross-product joins, era flags, V3b, linked pre-2005, matched multiples)? |
| **Manuscript clarity** | One clear headline finding + 3–5 figures? |
| **Ethics / data** | Public-use only; no re-identification risk beyond NCHS norms? |

**Disqualify** proposals that:

- Require state-level maps from public-use HVS,
- Ignore canonical filters,
- Treat 2014 preterm or race jumps as real epidemic trends without stratification,
- Claim row-level perinatal sibling linkage across products,
- Invent numbers not in validation tables.

---

## 8. Deliverables (structured output required)

Produce a **planning memo** with these sections:

### 8.1 Executive recommendation (≤ 300 words)

- **Primary analysis** (one sentence headline finding placeholder, e.g., “FMR for NH Black women declined X–Y across certificate eras after accounting for …” — use `X` only if from attached CSVs).
- **Why this beats all alternatives** (3–5 bullets).
- **Target journal tier** (name 2–3 journals with 2-sentence fit each).

### 8.2 Runner-up analyses (2 entries, ≤ 150 words each)

### 8.3 Candidate inventory table

| Rank | Short name | Years | Products | Key columns | NVSR anchor | Novelty (1–5) | Risk |

Include at least **6** candidates (may include F1–F8 above or new ones).

### 8.4 Methods sketch for the primary analysis

- Cohort / cross-sectional / APC / joinpoint?
- Outcome definition (cite canonical filters verbatim from JOINT_USE_GUIDE).
- Stratifications (age bands, race era-split at 2014, revision-era indicators).
- Sensitivity analyses (mandatory: 2014 race break, 2014 GA break, bridged-race window).
- Figure list (3–5 figures, plain-language titles).

### 8.5 Data & reproducibility plan

- Which parquets / CSVs / notebooks the PI should run first.
- What validation cells must appear in Results Table 1.
- What goes in supplementary vs main text.

### 8.6 Explicit “do not do” list (project-specific)

### 8.7 Three concrete next actions for the PI (each ≤ 1 hour of work)

---

## 9. Tone and epistemic rules

- Be **skeptical and specific**. Cite file paths and section names when claiming a fact.
- When uncertain, say **“verify in attached X”** rather than guessing.
- Distinguish **“NVSR publishes this rate”** vs **“HVS enables computing this rate from microdata.”**
- The PI is an applied epidemiologist / data scientist, not a methods tourist — prefer analyses that answer a population-health question, not “we harmonized data.”
- Paper 2 must stand alone empirically but cite Paper 1 (descriptor) as the data source — do not duplicate the descriptor’s pipeline description.

---

## 10. Attachments checklist (investigator: attach these)

Minimum attach set for you to work efficiently:

- [ ] `README.md`
- [ ] `docs/PRIOR_ART.md`
- [ ] `docs/COMPARABILITY.md`
- [ ] `docs/JOINT_USE_GUIDE.md`
- [ ] `fetal_death/COMPARABILITY.md`
- [ ] `csv/published_tabulations/README.md` + all `csv/published_tabulations/*.csv`
- [ ] `paper/draft_v2_hmd_styled.md` (stale counts OK — treat as narrative only)
- [ ] `EXPLORATION_REPORT.md` (long; OK to attach whole file)
- [ ] `matched_multiples/README.md`
- [ ] Optional: `notebooks/joint_use_demo.ipynb`, `cross_race_fetal_mortality.ipynb`, `preterm_outcomes_time_series.ipynb`
- [ ] Optional: `docs/perinatal_record_feasibility.md` if proposing any record-level linkage

If parquets are **not** attached, rely on published_tabulations CSVs + validation target CSVs + notebooks; state explicitly when an idea requires full microdata loads.

---

**Begin by confirming which attachments you received, then follow the reading order in §5, then produce §8.**
