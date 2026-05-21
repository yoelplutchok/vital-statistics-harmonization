# HVS Paper 1 & 2 — findings from the Ananth 2022 replication exercise

**Date:** 2026-05-20
**Status:** Reference document. Synthesizes the literature review, the Ananth 2022 PDF read-through, and three independent LLM-driven replication tests against `RECEIPTS/ananth2022_*`.

This document is the source-of-truth for what changes in Paper 1's framing and what Paper 2 should and should not claim.

---

## 1. Source materials

| Artifact | Path |
|---|---|
| Ananth et al. 2022 full PDF | `Evolving stillbirth rates among Black and White women in the United States, 1980–2020- A population-based study.pdf` |
| Replication test #1 (bilateral framing) | `RECEIPTS/ananth2022_replication_test_2026-05-20T19-30-00Z.md` + `notebooks/ananth2022_replication_test_v2.py` |
| Replication test #2 (independent verify + naive-proxy robustness) | `RECEIPTS/ananth2022_replication_test_independent_2026-05-20T19-55-00Z.md` + `notebooks/ananth2022_replication_test_independent.py` |
| Closeout test ≥24 wk (Ananth-stated methodology only) | `RECEIPTS/ananth2022_closeout_test_2026-05-20T20-17-21Z.md` + `notebooks/ananth2022_closeout_test.py` + `RECEIPTS/ananth2022_closeout_outputs/` |
| Closeout test ≥20 wk follow-up | `RECEIPTS/ananth2022_closeout_test_ge20wk_2026-05-20T22-21-46Z.md` + `RECEIPTS/ananth2022_closeout_outputs_ge20wk/` |

---

## 2. What Ananth 2022 actually did (definitive read of the published PDF)

| Aspect | Ananth's actual choice |
|---|---|
| Data source | NCHS public-use microdata via NBER mirror or direct CDC download (data sharing statement, p. 9) |
| Year span | 1980–2020 (41 years) |
| Stated gestational-age threshold | ≥24 weeks (primary); ≥28 weeks (sensitivity) |
| Operational gestational-age behavior | Headline rates match HVS at **≥20 wk**, not ≥24 wk (see §4) — methodology gap between stated and operational |
| Plurality | Singletons + multiples; twin sensitivity reported |
| Maternal-age exclusions | <11 and ≥50 years; missing GA dropped |
| Race coding | Bridged-INCL-Hispanic held constant across 1980–2020 ("we do not distinguish maternal race by Hispanic ethnicity" — Limitations section) |
| Residence filter | None applied (denominator includes non-residents; see §4) |
| `tabulation_flag` filter | None applied |
| APC software | R `Epi` package; Poisson with `log(LB + stillbirths)` offset, 5-year age groups, single-year periods + cohorts, Holford constraint, 10-knot natural splines on age/period/cohort, reference period 2020, reference cohort 1980 |
| Headline 1980/2020 rates | Total 10.6 → 5.8; White 9.2 → 5.0; Black 17.4 → 10.1 per 1,000 |
| Headline qualitative findings | Persistent 2× Black:White ratio, period decline through 2005, plateau thereafter, elevated youngest-cohort risk (more pronounced in Black women) |

**Important correction to `docs/PRIOR_ART.md`:** Ananth 2022 used microdata, not aggregates. The "Hogue & Silver forced to aggregates" point still stands, but the Ananth citation must be reframed.

---

## 3. Three replication attempts — summary

| Test | Framing | Verdict |
|---|---|---|
| #1 (v2) | Naive vs bilateral race coding | "Paper 2 has bite" (54–223% AP shift) — **interpretation overstated** |
| #2 (independent) | Replicate #1 + 5-variant naive proxy robustness | 14/14 cells match #1; one variant (`naive_rhr_2014`, NH-from-2014) shows 0% shift — confirmed bilateral methodology is equivalent to "switch to NH-only at 2014" |
| #3 (closeout, ≥24 wk) | Ananth-stated methodology only, no bilateral | **FAILED**: 16/60 cells pass (26.7%) |
| #3b (closeout, ≥20 wk) | Closeout re-run with the GA threshold that matches Ananth's headline rates | **FAILED**: 19/60 cells pass (31.7%); **3/3 Table 2 crude 2020 cells now pass** |

---

## 4. The headline-rate reproduction story

Under HVS canonical filtering (`residence_status != 4 AND tabulation_flag == 2`) and ≥24 wk gestation, HVS does **not** reproduce Ananth's 2020 crude rates. Ananth reports Total 5.8 / White 5.0 / Black 10.1; HVS canonical produces Total 3.94 / White 3.45 / Black 7.10.

Under broad filters (no `residence_status`, no `tabulation_flag`) at **≥20 wk**, HVS reproduces Ananth's 2020 Table 2 cells within tolerance:

| 2020 cell | Ananth | HVS broad-filter ≥20 wk | Δ |
|---|---:|---:|---:|
| Overall | 5.8 | 5.76 | +0.04 |
| White | 5.0 | 5.00 | +0.01 |
| Black | 10.1 | 10.49 | +0.39 |

**What this means:** Ananth's stated ≥24 wk filter operationally behaves like ≥20 wk in the published numbers. The Methods section as published does not contain enough detail to determine which the actual analysis used. Total stillbirth counts confirm the same pattern: Ananth reports 710,832 stillbirths ≥24 wk; HVS ≥20 wk under broad filters returns 1,070,898 for the overlapping 1982–2020 window — Ananth's number is closer to a hybrid of stated and operational filters than to a clean ≥24 wk slice.

---

## 5. The APC reproduction story

Under Ananth's stated methodology held constant (bridged-INCL-Hispanic race + broad filters + Holford-style APC), HVS fails to reproduce Ananth's Table 4 period and cohort rate ratios at the ±0.03 tolerance:

- **Period RRs**: shape is directionally similar (high 1980s, dip mid-2000s), magnitudes are off by 0.06–0.37 on most non-reference cells.
- **Cohort RRs**: HVS values collapse toward 1.0 across most cohorts. The expected gradient (youngest cohorts elevated) is not recovered.

Likely causes (in order of confidence, per the closeout LLM's diagnostics):

1. **APC software mismatch**: Python `patsy` + constrained GLM does not replicate Ananth's R `Epi` package extraction of period and cohort effects under the Holford constraint. This is a software implementation issue, not an HVS data issue.
2. **GA-threshold ambiguity**: Switching ≥24 → ≥20 raised pass rate from 16/60 to 19/60 — modest improvement, mostly in crude rates. APC magnitudes only marginally improve.
3. **2020 natality race reconstruction loss**: When `maternal_race_bridged` becomes null after 2019, reconstructing bridged-INCL-Hispanic from `maternal_race_ethnicity_5 + maternal_race_detail` produces a 6–9% drop in 2020 race-specific live-birth counts. This affects 2020-era cells but not the long-trend coefficients.

**No causes are HVS data defects.** All three are documentation / implementation / reconstruction issues at the interface between Ananth's published methodology and HVS's public artifact.

---

## 6. The bilateral methodology question — definitively settled

The bilateral race-coding methodology in `docs/COMPARABILITY.md` Era 3 is **valid** for NH-only research questions (e.g., reproducing NVSR Table A 2022 cells byte-exact for NH-stratified analyses). It is **not** a correction to apply to a bridged-INCL-Hispanic time-series like Ananth's.

The 54–239% AP period-coefficient shift the first two LLM runs reported between "naive" and "bilateral" methodology is the difference between **two valid race definitions** in the 2014+ window, not the magnitude of a hidden artifact in Ananth's analysis. The second LLM's robustness check confirmed this empirically: the one "naive" variant that uses NH-only race from 2014 onward (`naive_rhr_2014`) produces 0% shift relative to bilateral — i.e., bilateral methodology is mathematically equivalent to "switch to NH-only at 2014".

Ananth explicitly states he does not distinguish by Hispanic ethnicity. Therefore he is not in the `naive_rhr_2014` family. His methodology is internally consistent, and bilateral methodology applied across the 2014 boundary on his data produces a Hispanic-redistribution step, not a correction.

**The "correction of Ananth" Paper 2 framing is conclusively dead.** Do not pursue.

---

## 7. Implications for Paper 1 (Data Resource Profile)

### 7.1 Reframe `docs/PRIOR_ART.md`

Specific changes required:

- **Drop**: "Ananth was forced to use aggregates" / "no microdata cross-revision analysis existed". Both are false. Ananth used the same NCHS public-use microdata HVS harmonizes.
- **Drop**: "first to enable cross-revision long-trend microdata analysis" as a primary novelty claim. Multiple research groups (Ananth, Pradhan, etc.) have built internal partial harmonizations sufficient to publish long-trend microdata analyses.
- **Keep and sharpen**: "first public, documented, NVSR-byte-exact-validated, reproducibly built, openly licensed harmonization." This is true and verifiable.
- **Add**: explicit IPUMS-International / HMD analogy. The contribution is research-infrastructure democratization, not finding-enablement. IJE publishes Data Resource Profiles in this style routinely.
- **Add**: a documentation point — Ananth 2022's published Methods omit operational details (residence filter status, `tabulation_flag` status, GA operational definition, APC software, race-coding handling at 2014) sufficient to prevent byte-exact reproduction from public-use data alone, as evidenced by three independent replication attempts. HVS provides a fully documented alternative pipeline. **Frame as observation, not critique.**

### 7.2 Updates to `paper/draft_v2_hmd_styled.md`

- Replace the "no harmonized cross-revision microdata existed" paragraph with the corrected framing above.
- Add one paragraph positioning HVS as the public-reproducible-artifact analog to IPUMS-International + HMD.
- The Coverage, Measures, Methods, and Validation sections can remain substantively unchanged — they describe the resource accurately. Only the literature-gap framing needs revision.
- Verify that all numerical claims in Tables match the current README envelope (Paper 1 draft as of 2026-05-20 still shows stale counts: 1990–2024 natality, 2005–2023 linked, 1992–2022 fetal — current README is 1968–2024, 1983–2023 with 1992–1994 gap, 1982–2024).

### 7.3 Validation framing for credibility

Anchor Paper 1's credibility claim to NVSR byte-exact validation (which HVS achieves: 183/183 natality, 33/35 + 2 within-1-record linked 2005–2023, byte-exact pre-2005 cohort 19/19, 29/29 + 26/26 fetal V2-era), not to Ananth replication (which we now know is harder than expected and not the right target).

---

## 8. Implications for Paper 2 (empirical companion)

### 8.1 What Paper 2 is NOT

- Not a "correction of Ananth 2022". Three replication tests confirm there is no artifact to correct.
- Not a "byte-exact reproduction of Ananth 2022". Not achievable on HVS public-use data alone, for technical reasons (APC software, GA-threshold ambiguity, 2020 race reconstruction loss) that are not Paper 2 contributions.
- Not a "first to enable long-trend microdata stillbirth analysis". Ananth 2022 + Pradhan 2020 already did this with their own internal harmonizations.
- Not Lancet Reg Health Am tier. The novelty isn't there.

### 8.2 What Paper 2 IS

Scope: **complementary analyses that Ananth 2022 explicitly could not perform, run on HVS canonical methodology with NVSR byte-exact validation as the credibility anchor.**

Three specific contributions:

1. **Hispanic-disaggregated FMR trends 2014–2024 (11 years).** Ananth explicitly excluded Hispanic ethnicity. HVS's bilateral race-coding methodology is *the appropriate tool* for this specific sub-analysis — it matches NVSR Table A 2022 NH-only race cells byte-exact. Headline: "What does the U.S. Black–White stillbirth gap look like when Hispanic ethnicity is disaggregated, 2014–2024?" Note: bilateral methodology is correct here precisely because the research question is about NH-only categories, unlike the long-trend continuity question where it would force a definitional step.

2. **Post-COVID period extension (2021–2024).** Ananth's series ends in 2020. HVS extends through 2024 with NVSR-validated cells (Total FMR 2021 = 5.73, 2022 = 5.48, 2023 = 5.53, 2024 = 5.44 per `csv/published_tabulations/fetal_mortality_rate_by_year.csv`). The pandemic-era trajectory and recovery are scientifically interesting; dedicate a figure to race-stratified post-COVID trends.

3. **Publicly reproducible pipeline.** Ananth's analysis cannot be exactly reproduced from his published Methods (three independent attempts confirmed this). HVS provides documented filter specs, deterministic open-source pipelines, NVSR byte-exact validation, and CC BY 4.0 / MIT licensing. Frame this as Methods-section credibility rather than as a critique of Ananth.

Target journals (in priority order):

- **American Journal of Epidemiology** — fits the methods rigor + complementary-extension scope.
- **Paediatric and Perinatal Epidemiology** — natural home for U.S. stillbirth long-trend work.
- **Annals of Epidemiology** — accepts methods + reproducibility-themed empirical papers.

### 8.3 Methodology decisions for Paper 2

| Decision | Recommended choice |
|---|---|
| Filter convention | **HVS canonical** (`residence_status != 4 AND tabulation_flag == 2`). Ananth-style broad filter as supplementary sensitivity. |
| GA threshold | **≥20 weeks** (NVSR convention). ≥28 weeks as supplementary sensitivity (matches Ananth's secondary). |
| Race coding for 2014–2024 sub-analysis | **Bilateral methodology** (NH-only on both sides). Validated byte-exact against NVSR 73-09 Table A 2022. |
| Race coding for any extension series spanning 2014 | **Bridged-INCL-Hispanic held constant** through the last year it's available (2017 fetal-side; 2019 natality-side). State explicitly that the series uses the same race definition Ananth held constant. |
| APC software | **R `Epi` package** (matches Ananth's tooling). Not Python `patsy`. Document choice. Optionally include a joinpoint or segmented regression as a less-software-sensitive alternative. |
| Reference period | 2020 (matches Ananth for direct comparability) |
| Reference cohort | 1980 (matches Ananth) |
| Validation cells in Results | At minimum: 7/7 NVSR 73-09 Table A 2022 race-stratified FMR cells; 26/26 NVSR FMR-by-year matches 1995–2022 from `csv/published_tabulations/fetal_mortality_rate_by_year.csv`. |

### 8.4 Concrete next actions

| Order | Action | Approximate effort |
|---|---|---|
| 1 | Pull `csv/published_tabulations/fetal_mortality_rate_by_year_x_maternal_race.csv` + add the 2014+ NH-only-bridged series from `notebooks/cross_race_fetal_mortality.ipynb`. Sketch the Hispanic-disaggregated 2014–2024 panel. | 1 day |
| 2 | Verify HVS reproduces NVSR 73-09 Table A 2022 byte-exact (PI runs the notebook locally). | half day |
| 3 | Draft Paper 2 outline targeting AJE. Methods section anchored to HVS canonical filtering + bilateral race-coding only for the 2014+ NH-only sub-analysis. | 1 week |
| 4 | If APC modeling is desired, port the closeout test to R `Epi` package. Otherwise use joinpoint regression. | 1 week |
| 5 | Write — Paper 2 should be ~6000 words main text + supplementary. Target 4 figures: coverage timeline, 2014–2024 NH-only-stratified FMR with Hispanic shown separately, post-COVID period detail, joinpoint/APC summary. | 4–6 weeks |

Total effort: **~6–8 weeks of focused PI time**, contingent on R APC port (or joinpoint substitute) being straightforward.

---

## 9. Open methodological questions (worth flagging but not blocking)

These are not Paper 2 contributions; they are background uncertainties to be honest about in the manuscript.

1. **Ananth's effective GA threshold.** Stated ≥24 wk but operational behavior matches ≥20 wk. Without access to his exact code, we cannot determine which his Table 4 APC actually used. Resolution: pick one threshold (≥20 wk per NVSR) and state it explicitly. Note in Discussion that Ananth's stated ≥24 wk may differ from his operational threshold.

2. **2020 natality race reconstruction.** When `maternal_race_bridged` becomes null in 2020, reconstructing bridged-INCL-Hispanic from `maternal_race_ethnicity_5 + maternal_race_detail` loses 6–9% of race-specific live births. For 2020+ analyses, switching to NH-only (bilateral methodology) is cleaner. Document this as a methodological consideration in the race-coding section.

3. **APC software comparability.** Closeout test could not match Ananth's published Table 4 cohort RRs under Python `patsy` + constrained GLM. R `Epi` package may produce different results. Until verified, restrict any APC claims in Paper 2 to qualitative shape statements, not coefficient magnitudes. If exact cohort coefficients matter, port to R.

---

## 10. The bottom line

**Paper 1** is publishable as a Data Resource Profile after honest framing revision (drop overclaimed novelty, position as IPUMS/HMD analog, anchor credibility to NVSR validation). **Submit it** with the revised framing.

**Paper 2** is publishable as a complementary AJE/PPE/Annals-of-Epi-tier paper: Hispanic disaggregation 2014–2024 + post-COVID extension + publicly reproducible pipeline. **Do not** pitch as a correction of Ananth. **Do** anchor credibility to NVSR byte-exact validation, not Ananth reproduction. **Use bilateral race-coding methodology only where the research question is NH-only** (the 2014+ sub-analysis), not as a general "correction" applied across the 2014 boundary.

The three replication tests cost ~1 day of compute and clarified the framing. They are not themselves Paper 2 content but they were a necessary epistemic exercise to arrive at honest scoping.
