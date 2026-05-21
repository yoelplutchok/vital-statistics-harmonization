# Cross-product comparability (HVS)

> **Scope.** Synthesis of era boundaries that affect cross-product analyses (joint use of natality + linked + fetal-death). Aggregates the caveats relevant across products from each subproject's COMPARABILITY file + adds cross-product-specific caveats discovered during the worked-example notebook authoring (C8.10a/b/c).
>
> **When to read this doc vs. per-product COMPARABILITY:**
> - **This doc**: when you are computing rates / proportions / regressions that join across products (fetal mortality rate, perinatal mortality rate, infant mortality rate by demographic strata, cross-product trend analyses).
> - [`natality/docs/COMPARABILITY.md`](../natality/docs/COMPARABILITY.md): for natality-only analyses (16 KB, 11 top-level sections; covers MRACE bridging, certificate revisions, gestation source breaks, California marital-status non-reporting 2017+, etc.).
> - [`fetal_death/COMPARABILITY.md`](../fetal_death/COMPARABILITY.md): for fetal-death-only analyses (26 KB, 12 numbered sections + availability matrix; covers V2 state-level reporting quirks, V1 era plurality coding, V2.1 transition layouts, V3a/V3b backward extension caveats, etc.).

## Era-boundary timeline (cross-product)

```text
NATALITY    1968 ──── 1990 ──────────────────────────────────────────────── 2024 [57 yr]
            1968-rev (1968–1989: 1968/1969-71/1972-88/1989 layouts)──────
                       2003-rev────────                              2014 OE────
                                  MEDUC unbridged
                                                                          California marital → null 2017+
                                                                                    bridged-race → null 2020+

LINKED      1983 ──── ││││ ──────────────────────────────────────────── 2023 [38 cohort yr]
COHORT      1983-1988 keyless  1989-2004 denom-plus  2005-2015 denom-plus  2016-2023 period-cohort
            (v4)      1992-1994 permanent gap (││││)         2014 OE────
                      1983-1984 = 50%-non-VSCP RECWT-weighted sample
                                  (self-contained birth-side + death-side; natality-joint only 1990+)

FETAL_      1982 ─────────────────────────────────────────────────────── 2024 [43 yr]
DEATH       V3b (1978-rev)──── V3a (1989-rev)── V2 (1989-rev)── V2.1 (mixed)── V1 (2003-rev mixed)──── V1 OE (2003-rev)──── COD-only (2003-rev)
            1982-1988          1989-1991        1992-2002       2003-2004      2005-2013                2014-2017             2018-2024
            200-byte           360-byte         360-byte        1350/1500-byte 3351-byte                3050-byte             2652-byte
                                                                                                                    bridged-race → null 2018+
                                                                                                                   COD only (no education) 2018+
```

**Joint-coverage envelope**: cross-product analyses joining fetal-death numerator + natality denominator can use **33 years (1992-2024)** in the V2+V1+v2.4 envelope; if including V3a/V3b backward years for fetal-death, the natality denominator is not available (natality covers 1990+, fetal-death V3a/V3b covers 1982-1991 — only 1990+1991 are joint-coverage for V3a). The linked-cohort product itself now spans **38 cohort years (1983-2023; permanent 1992-1994 gap)** as a self-contained birth-side + death-side file (linked v4, C8.18). Linked + natality *joint* analyses (using the natality file as an external denominator) span **1990-2023** (natality starts 1990; less the 1992-1994 linked gap); pre-1990 linked years are linked-only (the linked file carries its own cohort denominator).

---

## Era boundary 1: 2003 revision transition (cross-product)

The **2003 revision of the Standard Certificate of Live Birth + Standard Report of Fetal Death** changed field names, coding frames, and measurement methods for both natality and fetal-death. Adoption was staggered across states. Both products document the transition at the same calendar boundary but with different consequences:

- **Natality** ([`natality/docs/COMPARABILITY.md` §"certificate_revision values"](../natality/docs/COMPARABILITY.md)): 2003-2013 records have a heuristic `certificate_revision` column (`"unrevised_1989"` / `"revised_2003"` / `"unknown"`) based on `MEDUC` + `MRACEREC` populated patterns. ~101K records in 2009 still `"unknown"` (2.45% of births).
- **Fetal-death** ([`fetal_death/COMPARABILITY.md` §1 "2003 Revision Transition"](../fetal_death/COMPARABILITY.md)): a native `VERSION` byte indicates 'A' (2003-revision) vs 'S' (1989-revision) per record from 2005 onward. % A-version grows from 6.6% in 2005 to 100% by 2018. V2 (1992-2002) is synthesized as `version_flag = 'S'` uniformly.

**Cross-product implication**: a cross-product joint analysis using 2003-revision-only fields (e.g., maternal BMI, revised education categories) needs to either restrict to **2018+ (both products universally 2003-rev)** OR carefully filter on the per-product revision flag. Mixing 2003-revision-only natality fields with all-records fetal-death will silently include 1989-revision fetal-death records that have those fields blank.

---

## Era boundary 2: 2014 OE-based gestational-age methodology shift (natality + linked)

In 2014, NCHS switched the canonical gestational-age field from `combined gestation` (LMP-based; available 2003-2013) to `obstetric estimate` (`OEGEST_COMB`; available 2014+). **The numerical preterm rate drops by approximately 1.5-2 percentage points across the 2014 boundary** — this is a methodology shift, NOT a demographic shift in preterm-birth incidence. See [`notebooks/preterm_outcomes_time_series.ipynb`](../notebooks/preterm_outcomes_time_series.ipynb) (C8.10b) for the empirical demonstration: natality preterm rate 2013 = 11.39%, 2014 = 9.57% (Δ = -1.82 pct-pt of which essentially all is methodology).

**Cross-product implication**:
- **Natality + linked**: both products use OEGEST_COMB starting 2014, so cross-product joins are consistent within the 2014+ window. Pre-2014 natality + linked both use combined gestation.
- **Fetal-death**: V1 era 2005-2013 uses 1989-revision LMP-based gestation; 2014+ uses 2003-revision OE-based gestation. Same methodology shift applies but is documented under the fetal-death V1 era boundary (V1-pre-OE → V1-OE).
- **Recommendation for cross-product preterm analyses**: avoid spanning the 2014 boundary without explicitly stratifying on `gestational_age_weeks_source` (natality) + `gestational_age_combined`/`oe_gest_recode12` (fetal-death). The C8.10b notebook narrative documents the recommended approach.

---

## Era boundary 3: 2014 race-coding methodology boundary (cross-product) — **NEW from C8.10c**

**Distinct from the 2014 OE-gestational-age shift even though it falls at the same calendar year.** In 2014, NCHS introduced Hispanic-disaggregated race classifications (`race_hispanic_revised` on the fetal-death side; `maternal_race_ethnicity_5` on the natality side). The pre-2014 bridged-race classification mixes Hispanic White/Black/etc. into the single-race-group categories; the 2014+ NH-only-bridged classification separates Hispanic into its own category.

**Empirical demonstration** ([`notebooks/cross_race_fetal_mortality.ipynb`](../notebooks/cross_race_fetal_mortality.ipynb) Section 3, C8.10c): on a cross-era race-stratified panel 1990-2024, the 2013→2014 transition shows a methodology-driven step of -0.87/1000 for White fetal mortality + -1.09/1000 for Black fetal mortality. These are NOT real demographic changes; they are an artifact of switching from bridged-incl-Hispanic to NH-only-bridged classifications.

### Bilateral race-coding methodology for cross-era panels (cross-product)

For race-stratified cross-product analyses spanning the 2014 boundary, **numerator and denominator must use MATCHED race-coding semantics**:

| Era window | Fetal-death race column | Natality race column | Result |
|---|---|---|---|
| 1990-2013 (cross-era pre-OE/race-coding shift) | `maternal_race_bridged` (4-cat bridged INCL. Hispanic) | `maternal_race_bridged` (4-cat bridged INCL. Hispanic; natality v2.8.0 column name) | Internally consistent panel; matches NVSR pre-2014 bridged-race tables |
| 2014-2024 (post-shift) | `race_hispanic_revised` collapsed to NH-only 4-cat | `maternal_race_ethnicity_5` collapsed to NH-only 4-cat | Internally consistent panel; matches NVSR Table A 2022 race-stratified FMR cells byte-exact |
| Mixed (1990-2013 bridged + 2014+ NH-only on the same series) | — | — | **AVOID**: produces artificial 2014 step (~-2.91/1000 White FMR; ~-2 for Black) due to Hispanic-population redistribution |

The C8.10c notebook's Section 3 reproduces NVSR 73-09 Table A 2022 race-stratified FMR cells byte-exact (Total 5.48 / NH AIAN 7.22 / NH Asian 3.70 / NH Black 10.05 / NH NHOPI 10.36 / NH White 4.48 / Hispanic 4.63 per 1,000) using the bilateral methodology + extends to a 35-year cross-era panel 1990-2024 with documented methodology-shift markers at the 2014 boundary.

**Recommendation for joint-use code**: any race-stratified cross-product analysis must declare its race-classification basis explicitly per era; the bilateral pattern above is the durable cross-era pattern. Mixing semantics yields biased trend estimates.

---

## Era boundary 4: Bridged-race null timing (asymmetric across products)

The bridged-race column ends at different years on each product because NCHS discontinued the bridged-race public-use field at different times:

| Product | Last year with `maternal_race_bridged` populated | First year null |
|---|---|---|
| **Natality** (v3.0.0) | 2019 | 2020 |
| **Linked** (v3) | 2019 | 2020 (matches natality numerator side) |
| **Fetal-death** (v2.4.0) | 2017 | 2018 |

**Cross-product implication**: a stratified-by-bridged-race cross-product analysis (e.g., fetal mortality rate × race × year) has different "race available" windows depending on product:
- **Joint-coverage with bridged race**: 1992-2017 (joint between natality 1990-2019 + fetal-death 1992-2017). V3a 1989-1991 + V3b 1982-1988 add 10 more years on the fetal-death side, but natality starts in 1990, so 1990-1991 are joint (V3a only).
- **Joint-coverage WITHOUT bridged race** (2018+ requires reconstruction from MRACE detail codes): both products provide reconstructed `maternal_race_ethnicity_5` (natality) / `race_hispanic_revised` (fetal-death) starting at the respective bridged-race end year. The reconstruction is approximate for multi-race births (~3% of 2018+ natality records map to null because they cannot be bridged to a single race group).

**Recommendation**: if you need consistent bridged-race coverage across both products, restrict to 1990-2017 (or 1989-2017 if you include V3a 1989); for 2018+ analyses, switch to the reconstructed columns + document the multi-race null fraction.

---

## Era boundary 5: V3a + V3b backward extension caveats (fetal-death only)

The fetal-death backward extension to V3a (1989-1991) and V3b (1982-1988) is an asymmetric coverage extension — these years exist for fetal-death but **NOT for natality** (natality starts 1990; **NOT for linked**, which starts 2005-cohort).

**V3a 1989-1991 (1989-revision uniform)** ([`DECISION_LOG.md` 2026-05-12T14:30Z](../DECISION_LOG.md)): MRACE 1-digit codes 1-9; B3 recode `1→1, 2→2, 3→3, 4-8→4, 9→null`. ~165 records null from code 9 across 1989-1991 (~0.087% per year).

**V3b 1982-1988 (1978-revision uniform)** ([`DECISION_LOG.md` 2026-05-12T18:30Z](../DECISION_LOG.md)): MRACE 1-digit codes 0-9; B3 recode `1→1, 2→2, 3→3, 4-6,8→4, 7→null, 9→null`. Code 7 ("Other nonwhite") + code 9 ("Not stated") each → null; total ~89 (code 7) + ~18,700 (code 9) = ~18,800 null records across 1982-1988 (~3-5% per year). The 1978-revision public-use file has a less-imputed race field than 1989+. **Hispanic origin is null for all V3b years** (1978-revision did not collect Hispanic origin systematically; first introduced in 1989-revision).

**Cross-product implication**: V3a + V3b years cannot be joint-analyzed with natality + linked (those products don't extend back). Use the fetal-death-only series for 1982-1989 (single-product fetal-mortality counts, not rates — there is no denominator for those years in this resource).

---

## Per-product-only caveats (pointers)

The following caveats are PRODUCT-SPECIFIC and do NOT affect cross-product analyses unless the cross-product analysis depends on the affected column. Pointers to authoritative documentation:

### Natality-only (consult [`natality/docs/COMPARABILITY.md`](../natality/docs/COMPARABILITY.md))

- 2003 maternal age recode (MAGER41 1-41 → single-year approximate; codes 37-41 → ages 50-54 distinct)
- 1990-2002 smoking: independent source fields (TOBACCO + CIGAR6); ~429K records have smoker status with unknown intensity
- 2009-2013 "U-only" fields blank in public-use files (education, prenatal-care, smoking measures revised-only)
- California marital-status non-reporting 2017+: `marital_status` null for ~11-12% of births starting 2017
- Smoking missingness 2003-2008 = ~7-20% (item-level nonresponse); 2009-2013 = ~14-44% (unrevised structural missingness); 2014+ = <5% declining to <0.5%

### Linked-cohort-only (consult [`natality/docs/COMPARABILITY.md` §"V3 Linked"](../natality/docs/COMPARABILITY.md))

- Cohort year vs publication year naming convention changes at cohort 2015 / publication 2016 (`LinkCO15US.zip` → `2017PE2016CO.zip`)
- **Linked v4 spans 1983-2023** (C8.18; the pre-2005 cohort files ARE now harmonized — the prior "not processed" note is superseded). Four pre-2005 cohort caveats, all linked-cohort-only (natality + fetal-death do not extend below 1990/1982 respectively, so these years have no cross-product joint partner — single-product linked IMR only):
  - **Keyless 1983-1988 within-era structural difference.** The 1983-1988 cohort files are a two-file den/num pair with no per-record link key. The cohort IMR there is `count(link_segment='num') / count(link_segment='den')` per stratum — **NOT** a per-birth `infant_death` filter (denominator rows: `infant_death` NULL; numerator rows: True). `age_at_death_days` is NULL for 1983-1988 (keyless numerator carries only AGER5 — use `age_at_death_recode5`). This is the documented within-era structural difference (schema `link_segment` notes + the manuscript Coverage paragraph).
  - **1983-1984 50%-non-VSCP weighted sample.** The 1983/1984 cohort denominators are a documented 50%-of-births-in-5-non-VSCP-areas weighted sample; `record_weight` (= NCHS RECWT) is populated so weighted counts reproduce published cohort figures byte-exact (1983 weighted resident births 3,639,113 / IMR 10.90; 1984 3,669,268 / 10.44). 1985-2004 are full files.
  - **1992-1994 permanent gap.** NCHS suspended ALL birth-infant-death linkage for the 1992, 1993, 1994 cohorts (no cohort and no period file published). Permanent; surfaced in `harmonized_schema.csv` `years_available`, CODEBOOK, ABOUT_THIS_RELEASE.md, and (at Phase D) the manuscript Coverage paragraph.
  - **Documented numerator-file residual (3 of 19 cohort years).** For 1989, 1998, 2002 the cohort numerator-file record count differs from the denominator-linked infant-death subset by Δ +1 / +40 / −8 (≤0.15%, deterministic, bidirectional) — the SAME NCHS cohort-linked numerator-file-vs-denominator-linkage class as the 2005-2023 "2 cells differ by exactly one record from NCHS upstream null-record-weight survivors". Pinned as a per-year `tolerance_abs` + sourced notes in `external_validation_targets_v3_linked.csv`; denominator / resident-births / published IMR remain byte-exact / within ±0.02 for all 19 cohort years.
- 2014/2015 each have 1 record with null `record_weight` (NCHS upstream survivor records); validation framing per [`paper/draft_v2_hmd_styled.md`](../paper/draft_v2_hmd_styled.md) records this as "33/35 byte-exact + 2 cells differ by exactly one record" (the manuscript Coverage re-paragraph carrying the linked v4 1983-2023 envelope + these four caveats is a Phase-D / D.4 deliverable, deferred so the manuscript Coverage paragraph is re-written once after the full data envelope settles)

### Fetal-death-only (consult [`fetal_death/COMPARABILITY.md`](../fetal_death/COMPARABILITY.md))

- V1 era plurality coding anomaly (2005-2013): `plurality == "5"` is implausible at observed volumes; likely state-level miscoding of unknown plurality. fd COMPARABILITY §7
- V2 (1992-2002) state-level reporting quirks: Oklahoma Hispanic non-reporting; Maryland/Massachusetts pattern; Louisiana plurality non-reporting 1992-1994 (DPLURAL=9 for ~99% of records)
- V2 stale-guide years (1996, 2001, 2002): NCHS user guide control counts copy-pasted from prior years; validation cell `external_validation_targets.csv` notes flag these
- V2 → V1 transition skip (2003-2004 deferred until V2.1, shipped 2026-05-12); the 2003 + 2004 raw files use distinct mixed 1989/2003-revision layouts (1350-byte / 1500-byte records); see fd COMPARABILITY §"Era Structure" + companion `fetaldeath0304problems.pdf`

---

## Joint-use cross-product checklist

Before computing any cross-product rate or stratified statistic, verify:

1. **Canonical filter applied on BOTH sides.** Numerator filter: `tabulation_flag == 2 AND residence_status != 4` (fetal-death); denominator filter: `residence_status != 4` (natality); see [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md) for the full filter spec.
2. **Era-boundary intersection.** Your analysis year-window is JOINT-COVERAGE on every product you join (e.g., fetal-death + natality joint = 1992-2024 less V3a/V3b which are FD-only).
3. **Race-classification semantics MATCH on both sides** of any race-stratified panel. Pre-2014: bridged-on-both. 2014+: NH-only-on-both. See [Era boundary 3](#era-boundary-3-2014-race-coding-methodology-boundary-cross-product--new-from-c810c) above.
4. **Gestation-source consistency**: pre-2014 panels use LMP-based (or "combined" 2003-2013 natality); 2014+ panels use OE-based. Mixing yields methodology-driven step. See [Era boundary 2](#era-boundary-2-2014-oe-based-gestational-age-methodology-shift-natality--linked).
5. **Bridged-race null window awareness**: fetal-death bridged ends 2017; natality + linked bridged end 2019. If your race stratum requires bridged-race AND your year-window crosses these ends, your sample size in the post-end years uses reconstructed columns + drops multi-race records (~3% of natality 2018+).
6. **2017+ California marital-status caveat**: if your stratifier or covariate includes `marital_status` AND your year-window crosses 2017, use `marital_reporting_flag` to scope to reporting states OR restrict to 2003-2016 window.
7. **V3a/V3b cannot be denominator-joined**: 1982-1991 fetal-death years have no natality denominator in this resource. Use the single-product fetal-death count series for those years.
8. **Compute denominators with the convenience helper or stratified file**. [`fetal_death/stratified_denominators.csv`](../fetal_death/stratified_denominators.csv) and [`fetal_death/live_births_by_year.csv`](../fetal_death/live_births_by_year.csv) cover **1992-2002 + 2005-2024 (31 strat years; 28 LBY years: 1995-2002 + 2005-2024)**. See [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md) for microdata-vs-NVSR denominators and 2024 LBY sourcing. Fetal-death numerators are available through **2024**.

---

## Worked examples

The three Tier-2 worked-example notebooks at [`notebooks/`](../notebooks/) demonstrate three classes of cross-product analyses + their COMPARABILITY checklists:

- **[`maternal_age_stratified_imr.ipynb`](../notebooks/maternal_age_stratified_imr.ipynb)** (C8.10a): IMR by maternal-age band, linked-file-based; demonstrates cohort-vs-period source divergence + 12 NCHS byte-exact cells.
- **[`preterm_outcomes_time_series.ipynb`](../notebooks/preterm_outcomes_time_series.ipynb)** (C8.10b): 43-year preterm-rate time series across natality + linked + fetal-death; reproduces 34 NCHS preterm cells byte-exact; documents the 2014 OE-methodology shift.
- **[`cross_race_fetal_mortality.ipynb`](../notebooks/cross_race_fetal_mortality.ipynb)** (C8.10c): 35-year race-stratified FMR time series 1990-2024 across V3b + V3a + V2 + V2.1 + V1 fetal-death eras; reproduces NVSR 73-09 Table A 2022 race-stratified FMR cells byte-exact; demonstrates the bilateral race-coding methodology + documents the 2014 race-coding methodology boundary distinct from the 2014 OE gestational-age boundary.

The two existing `joint_use_demo.ipynb` (single-year fetal-mortality rate by maternal-age + by race) and `paper_companion.ipynb` (paper-numeric reproduction) also exemplify cross-product joint-use patterns.

---

## See also

- [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md) — canonical filters, join keys, worked examples
- [`docs/PRIOR_ART.md`](PRIOR_ART.md) — literature gap motivating cross-product harmonization
- [`docs/NCHS_SOURCE_MANIFEST.md`](NCHS_SOURCE_MANIFEST.md) — 97 raw NCHS zips with SHA-256
- [`VERSION_ROADMAP.md`](../VERSION_ROADMAP.md) — version timeline + upcoming work
- [`migrations/`](../migrations/) — per-subproject migration guides
- [`shared/helpers/canonical_join_keys.py`](../shared/helpers/canonical_join_keys.py) — cross-product column-name reconciliation
