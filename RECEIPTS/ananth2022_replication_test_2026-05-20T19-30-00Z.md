# Ananth et al. 2022 replication test — decision memo

**Receipt:** `RECEIPTS/ananth2022_replication_test_2026-05-20T19-30-00Z.md`
**Code:** `notebooks/ananth2022_replication_test_v2.py`
**Aggregated data:** `RECEIPTS/ananth2022_outputs/*.csv`, `results.json`
**Reference:** Ananth CV, Brandt JS, Hill J, et al. *Lancet Reg Health Am* 2022;16:100380.

---

## RETRACTION + UPDATED VERDICT (added 2026-05-20, post-paper-read)

**The original verdict in this memo is wrong.** When I wrote this memo I had
not read the Ananth paper. After reading the paper (PDF in repo root) a
second-pass review surfaced two errors in my analysis:

1. **The reproduction failure at ≥24 wk was a filter mismatch, not a
   threshold mismatch.** Ananth used GA ≥ 24 wk (per his Methods, page 3),
   exactly as the task spec said. But he did NOT apply HVS's canonical
   `tabulation_flag == 2` filter or the residence filter. His total 2020
   stillbirth count (20,949 at ≥24 wk in 3,635,736 total births) is
   essentially HVS's all-canonical ≥20 wk count (20,854 at ≥20 wk in
   3,613,647 resident live births) — his less-strict inclusion (no NCHS
   tabulation flag, no residence filter) offsets his stricter GA cutoff.
   The right Ananth-replication filter is what he wrote: GA ≥ 24, drop
   missing GA, age 11-49, **no `tabulation_flag` restriction, no residence
   restriction**. I never tried that combination, which is why my pipeline
   gave rates ~half of his.

2. **The "bilateral race-coding correction" is not a correction to apply
   to Ananth's analysis.** Ananth deliberately holds the race definition
   constant as bridged-INCL-Hispanic across 1980-2020 — he says so
   explicitly in the Limitations section: *"we do not distinguish
   maternal race by Hispanic ethnicity since data on Hispanic ethnicity
   was only made available consistently in the revised 2003 birth
   certificates."* HVS's own
   `csv/published_tabulations/fetal_mortality_rate_by_year_x_maternal_race.csv`,
   which uses `maternal_race_bridged` on both sides 1990-2017, shows
   **essentially no step at 2013→2014** (Black 10.56 → 10.63, +0.07;
   White 5.09 → 5.10, +0.01). The −0.7 to −1.4/1,000 step that my
   "bilateral" panel produces is created BY switching column semantics
   at 2014 (from bridged-INCL-Hispanic to NH-only), not by exposing a
   hidden NCHS artifact. The HVS bilateral methodology is a *different
   operational definition* for a *different research question*
   (NH-only consistency 2014+ to match NVSR Table A 2022 cells) — it is
   not a correction for a Black-vs-White-bridged-INCL-Hispanic
   time-series.

The 54.7 % / 223 % period-coefficient changes I reported in the original
TL;DR are arithmetically real but compare (i) a coefficient where the
race definition is held constant across 2014 to (ii) a coefficient where
the race definition is switched at 2014. That's a methodology *change*,
not a methodology *correction*. The percent-change metric is also unfair
on its own terms (naive 2014 RR ≈ 0.92 is near 1, so small absolute
shifts produce large percentage changes).

### Updated TL;DR (replaces original below)

**Paper 2 does NOT have empirical bite as a correction-of-Ananth paper.**
Ananth's methodology is internally consistent and defensible: bridged-
INCL-Hispanic Black vs bridged-INCL-Hispanic White, held constant across
the 2014 boundary, with documented Poisson-regression APC + 10-knot
natural-spline parameterization. There is no hidden 2014 artifact to
correct.

**Paper 2 still exists as a complementary, not corrective, paper** with
three contributions:

1. **Hispanic disaggregation 2014-2024.** Ananth explicitly flags
   Hispanic ethnicity as a documented limitation. HVS can stratify NH
   White / NH Black / NH AIAN / NH Asian-PI / Hispanic for the
   post-2014 window using `race_hispanic_revised` (FD) +
   `maternal_race_ethnicity_5` (natality). Genuinely new analysis.
2. **Post-COVID extension 2021-2024.** Ananth ends at 2020. HVS goes
   through 2024. The four post-COVID years are scientifically
   interesting and outside Ananth's coverage.
3. **Public-reproducibility methodology paper.** Replicate Ananth's
   1980-2020 panel byte-exact using a publicly documented HVS pipeline
   (Ananth's stated data sources — NBER + CDC — don't actually include
   his exact filter spec or code; the published-rate reproduction
   itself is a finding).

**Likely target: AJE / PPE / Annals of Epidemiology** (not *Lancet Reg
Health Am*). Honest novelty: public reproducibility + Hispanic
disaggregation + 4 post-COVID years. Estimated effort: ~2-3 months
careful work for Hispanic + ~2 weeks for COVID extension.

**What NOT to pitch in Paper 2:**
- "Ananth's plateau is materially incorrect" — not supported.
- "Ananth missed a 2014 race-coding artifact" — not supported.
- "HVS bilateral methodology corrects Ananth" — not supported.

### HVS doc-hygiene action item

`docs/COMPARABILITY.md` Era boundary 3 describes the bilateral
methodology and characterizes the 2014 step as "artifact, not biology."
That framing is misleading in the context of long-trend race-stratified
analyses that intentionally use bridged-INCL-Hispanic throughout. The
doc should be updated to clarify that the bilateral methodology is for
NH-only consistency post-2014 (to match NVSR Table A 2022 cells
byte-exact), and is NOT a universal correction to apply to series that
intentionally hold bridged-INCL-Hispanic constant across the 2014
boundary. Tracked separately from Paper 2.

---

## Original memo (preserved below for audit trail; conclusions superseded)

## TL;DR (ORIGINAL, RETRACTED)

~~**Paper 2 has empirical bite.** Under the HVS bilateral race-coding correction
(matched bridged-INCL-Hispanic semantics pre-2014 and NH-only-bridged
semantics 2014+ on BOTH numerator and denominator), the fitted 2014
age-period Poisson period coefficient for Black women shifts from
RR = 0.815 (naive) → 0.729 (bilateral) — a 54.7 % change in |β| at ≥20 wk;
for White women RR shifts from 0.921 → 0.766 (223 %). The 2013→2014 crude
Black FMR step is −0.34/1,000 under Ananth's naive coding but **−1.42/1,000**
under bilateral. Ananth's "increase 2005→mid-2010s, plateau thereafter"
narrative is largely an artifact of an undisclosed 2014 NCHS race-coding
methodology break; the 2× Black:White ratio and the elevated-youngest-cohort
finding survive (cohort effects shift <5 %).
**Pursue Paper 2 as a correction-and-extension paper.**~~

**(Retracted — see "Updated TL;DR" above. The 54.7 % / 223 % shifts and
the −1.42/1,000 bilateral step are arithmetically real but reflect a
definitional switch at 2014, not the exposure of a hidden artifact in
Ananth's analysis. The numbers in the original memo are correct as
counts and rate computations; only the interpretation as a "correction
of Ananth" is wrong.)**

## 0. Pre-flight: Step 1 fails at the task spec's ≥24 wk threshold

**[POST-RETRACTION NOTE: my inference here was wrong. Ananth's paper
Methods page 3 explicitly say "stillbirth as a fetal death at ≥24
weeks' gestation". The Step 1 reproduction failure at ≥24 wk was not a
threshold problem — it was caused by over-filtering: I applied HVS's
canonical `tabulation_flag == 2` AND `residence_status != 4` filters,
neither of which Ananth applied. The right Ananth filter is GA ≥ 24,
drop missing GA, age 11-49, and no canonical / no residence
restriction. The ≥20 wk "match" I found at 2020 was coincidence:
Ananth's looser inclusion + ≥24 wk produced approximately the same
count as HVS canonical + ≥20 wk. The original Section 0 prose below is
preserved for audit but the conclusion that "Ananth used ≥20 wk" is
wrong.]**

The task spec stated ≥24-wk gestation but the Ananth headlines it cited
(Black 17.4 / 10.1 in 1980 / 2020; White 9.2 / 5.0) align with published
NCHS **≥20-wk** fetal-mortality figures. Under ≥24 wk, HVS does NOT reproduce
Ananth's 2020 headlines within ±0.5/1,000 (Black 6.79 vs 10.1, Δ = −3.31;
White 3.28 vs 5.0, Δ = −1.72). Under ≥20 wk, both 2020 cells PASS within
tolerance (Black 9.94 vs 10.1, Δ = −0.16; White 4.62 vs 5.0, Δ = −0.38).
1982-vs-1980 cells fail at both thresholds because HVS PUF starts at 1982
and NCHS Black FMR fell from ~18.6 (1980) to ~14.0 (1982) — a 2-year offset
problem, not a methodology problem.

Per "do not silently tune", I report both thresholds; the verdict is the
same.

## 1. Reproduction (≥20 wk, naive coding)

`step1_reproduction_both_thresholds.csv`:

| Year | Race | HVS ≥20 wk | Ananth target | Δ | ±0.5 pass? |
|---|---|---:|---:|---:|---|
| 1982 (vs 1980) | Black | 12.46 | 17.4 | −4.94 | FAIL† |
| 1982 (vs 1980) | White |  7.35 |  9.2 | −1.85 | FAIL† |
| 1990 | Black | 12.36 | — | — | — |
| 2000 | Black | 12.09 | — | — | — |
| 2010 | Black | 10.67 | — | — | — |
| 2020 | Black |  9.94 | 10.1 | **−0.16** | **PASS** |
| 2020 | White |  4.62 |  5.0 | **−0.38** | **PASS** |

† 2-year offset; HVS 1982 cell matches the NCHS-published 1982 cell.

## 2. APC comparison — naive vs bilateral

### Parameterization

Poisson GLM, log link, `log(LB + FD)` offset. **Age**: 7 bands (Ananth's;
ages 11-49); reference 25-29. V2.1 (2003-2004) FD `maternal_age` is null;
v2 builder falls back to `maternal_age_recode14`. **Period**: annual
1982-2020; reference 2000. **Cohort** (APC only): 5-yr groups from
`period − age-band midpoint`. Holford-style identifiability: first two
non-reference cohorts merged. Both AP and APC reported; AP gives directly
interpretable period RRs at the boundary.

### 2.1 Crude 2013→2014 step (no model) — `boundary_2014_crude_rate_check_both.csv`

| Threshold | Race  | Naive step | Bilateral step | HVS-doc expected |
|---|---|---:|---:|---:|
| ≥20 wk | Black | −0.335 | **−1.418** | −1.09 |
| ≥20 wk | White | −0.114 | **−0.955** | −0.87 |
| ≥24 wk | Black | −0.031 | −0.697 | — |
| ≥24 wk | White | −0.029 | −0.572 | — |

The bilateral panel exposes a 4-30× larger 2014 step than the naive panel.
At ≥20 wk the bilateral step exceeds the C8.10c documented step because
the C8.10c reference panel is all-maternal-ages while this is age 11-49.

### 2.2 Fitted period coefficient at 2014 — `boundary_period_effect_change_both.csv`

| Threshold | Race  | Model | RR naive | RR bilateral | |Δβ|/|β naive| |
|---|---|---|---:|---:|---:|
| ≥20 wk | Black | AP  | 0.815 | 0.729 | **54.7 %** |
| ≥20 wk | Black | APC | (8.25) | (7.36) | 5.4 % |
| ≥20 wk | White | AP  | 0.921 | 0.766 | **223 %** |
| ≥20 wk | White | APC | (3.42) | (2.99) | 10.9 % |
| ≥24 wk | Black | AP  | 0.861 | 0.773 | **71.8 %** |
| ≥24 wk | White | AP  | 0.931 | 0.785 | **236 %** |

APC RRs in parentheses are inflated by the Holford-merged-cohort reference
and are NOT directly interpretable as levels; only the naive-vs-bilateral
*difference* is the meaningful quantity. AP RRs are interpretable directly
as rate-ratio vs the year-2000 reference. **AP threshold (>25 %)
DECISIVELY met for both races at both thresholds.**

### 2.3 Youngest-cohort effects (1985+ cohorts) — `cohort_effects_youngest_both.csv`

Cohort-effect attenuation is <5 % across all post-1985 cohorts examined at
both GA thresholds for both races. **The cohort threshold (>25 %) is NOT
met.** Ananth's "elevated youngest cohort" finding is robust under
bilateral correction.

### 2.4 Sensitivity (`sensitivity_period_effects_both.csv`)

- **Singleton-only** (≥20 wk bilateral): 2014 RR = 0.729 / 0.773 — virtually
  identical to all-plurality.
- **2024 extension**: 2014 RR stays at 0.731 / 0.767. Post-2020 Black RRs
  cluster in [0.720, 0.772]; White in [0.795, 0.867]. No COVID-era spike
  in the fitted period coefficients (raw Black 2021 dipped to 9.45,
  recovered).

## 3. Substantive verdict [RETRACTED — see top of memo]

**[The table below interprets the bilateral panel's 2014 step as a
correction of Ananth's "plateau" finding. Per the retraction at the top
of this memo, that interpretation is wrong. The bilateral panel SWITCHES
race-definition semantics at 2014 (bridged-INCL-Hispanic pre-2014 →
NH-only 2014+), which CREATES the step. Ananth's analysis holds race
definition constant across 2014 (bridged-INCL-Hispanic throughout), and
HVS's own `published_tabulations` CSV — which uses the same column on
both sides 1990-2017 — shows essentially no 2014 step. Ananth's
"plateau" is in the data under his stated methodology; it is not an
artifact to correct. Original table preserved below for audit.]**

| Ananth conclusion | ~~Survives bilateral correction?~~ (RETRACTED) |
|---|---|
| Persistent ~2× Black:White ratio | ~~Yes~~ — trivially yes; not in dispute |
| Strong age effects | ~~Yes~~ — trivially yes; not in dispute |
| Period decline 1982→2005 | ~~Yes~~ — yes under any consistent coding |
| "Plateau after mid-2010s" | ~~**No** — bilateral shows a clear 2014 downward step + continued decline 2014-2024, not a plateau~~ → **In fact yes; the "bilateral correction" introduces a step rather than removing one** |
| Elevated youngest-cohort risk, more so for Black | Yes (<5 % cohort attenuation) — robust under any coding scheme |

~~The naive 2013→2014 step is −0.03 to −0.34/1,000 (Black); the bilateral
step is −0.70 to −1.42/1,000. Spread over the 2014-2020 window, this
boundary artifact is comparable to the year-over-year fluctuations Ananth
interpreted as a trend reversal. **Ananth's "plateau" interpretation is
materially incorrect once bilateral correction is applied.**~~

## 4. Recommendation [RETRACTED — see updated recommendation at top of memo]

**[The original recommendation below — "pursue Paper 2 as a
correction-and-extension paper" with the 2014 race-coding correction as
contribution #1 — is retracted. See "Updated TL;DR" at the top of this
memo for the corrected recommendation: pursue Paper 2 as a complementary
paper (Hispanic disaggregation 2014-2024 + post-COVID extension +
public-reproducibility), not corrective. The 54-236 % period-coefficient
shift cited below is arithmetically real but reflects a definitional
switch at 2014, not a correction of a hidden artifact in Ananth's
analysis. Original recommendation preserved below for audit.]**

~~Per decision rule (>25 % period-coefficient shift OR >25 % youngest-cohort
attenuation → bite):~~

- ~~**Period-coefficient threshold: DECISIVELY met** (AP 54-236 % across
  both races and both thresholds; crude rate boundary step 4-30× larger
  under bilateral).~~
- ~~Cohort threshold: not met (<5 % attenuation) — Ananth's cohort finding
  is robust.~~

~~The OR clause is satisfied by the period side. **Pursue Paper 2 as a
correction-and-extension paper** with two distinguishing contributions:~~

1. ~~**2014 race-coding methodology correction.** Ananth's pre-2014 cells
   use bridged-INCL-Hispanic race; 2014+ cells use NH-only-bridged
   (NCHS shifted the underlying meaning of the bridged-race column at
   2014 without renaming it; Ananth's published Methods do not document
   how this was handled). Bilateral methodology (matched semantics on
   numerator + denominator across the boundary) is the durable
   correction; HVS implements and validates it in
   `notebooks/cross_race_fetal_mortality.ipynb` (`C8.10c`, 2026-05-13).
   Materially changes Ananth's period-effect narrative.~~
2. **2021-2024 extension.** Ananth had data only through 2020. Bilateral
   ≥20 wk extension stabilizes Black RR in [0.72, 0.77] and White in
   [0.80, 0.87], including pandemic-era years. *(This contribution
   survives the retraction; see top of memo for the corrected framing.)*

~~Suggested scope: reproduce Ananth's exact pipeline at ≥20 wk and report
period figures side-by-side under naive vs bilateral; cite HVS Paper 1
data-resource profile + C8.10c as the methodology source (bilateral is
not a Paper-2 invention, it's the application of an HVS-disclosed method
to a previously-published analysis whose methodology was undisclosed).~~

## Notes / fine print

- **AP > APC for the boundary question.** APC period *levels* are
  un-interpretable under the Holford-merged-cohort constraint, but
  *differences* between naive and bilateral at the same year are valid;
  the qualitative pattern matches AP (bilateral β more negative at 2014).
- **V2.1 (2003-2004).** FD `maternal_age` is null; v2 builder uses
  `maternal_age_recode14`. v1 builder did not and produced near-zero RRs
  at those years; v1 results are superseded.
- **"Naive" coding.** `maternal_race_bridged` 1982-2017 + `race_hispanic_revised`
  codes '1'/'2' (NH only) 2018-2020 on FD; symmetric on natality
  (bridged 1982-2019; eth5 collapsed 2020+). Best-effort Ananth proxy;
  his actual coding pipeline is not disclosed.
- **At 2020 naive and bilateral are numerically identical** because both
  use NH-only `race_hispanic_revised`/`maternal_race_ethnicity_5` by then —
  the divergence lives in the 2014-2017 window.

## Files

All in `RECEIPTS/ananth2022_outputs/`:
`fd_aggregated.csv`, `nat_aggregated.csv`,
`step1_reproduction_both_thresholds.csv`,
`boundary_2014_crude_rate_check_both.csv`,
`boundary_period_effect_change_both.csv`,
`period_effects_2013_2014_2015_both.csv`,
`cohort_effects_youngest_both.csv`,
`sensitivity_period_effects_both.csv`,
`extension_2020_2024_bilateral_ge20wk.csv`,
`panel_{naive,bilateral}_{ge20wk,ge24wk}_{all,singleton,all_ext}.csv`,
`annual_rates_*.csv`, `results.json`. Reproducer:
`notebooks/ananth2022_replication_test_v2.py`.
