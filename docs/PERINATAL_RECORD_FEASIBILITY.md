# Perinatal-record pre-join: feasibility and methodology

**Status:** C8.19 deliverable, re-scoped 2026-05-23 (`NEXT_STEPS.md` §15.D `[plan-update]` block; 2026-05-23T08:00:00Z). The original C8.19 plan proposed a fifth, record-level "perinatal record" parquet. The §15.D-designed Tier-0 cheap-check proved that artifact is not constructible from public-use data. This note documents the finding, points to the two perinatal analyses that *are* supported, and records what a true perinatal record-linkage would require.

All numbers below are produced by [`scripts/perinatal_feasibility_analysis.py`](../scripts/perinatal_feasibility_analysis.py) and reproduce byte-identically on re-run. No data, schema, or validation artifact is modified by this task.

## Bottom line

A *record-level* perinatal record — one row per linked-file infant with its fetal-death **sibling** (a fetal death to the same mother) flagged — **cannot be built from NCHS public-use microdata**, by construction, in any year. The expected rate at which a fetal death can be uniquely matched to its sibling birth is **at most 0.00118% across all tested years and key variants** <!-- computed by scripts/perinatal_feasibility_analysis.py; see RECEIPTS/C8.19_2026-05-23T09-00-00Z.md -->, against the §15.D Tier-0 decision threshold of 5% — a shortfall of more than three orders of magnitude. The cause is permanent NCHS disclosure protection, not an engineering gap.

This does not reduce the resource. The two perinatal analyses that public-use data genuinely supports are already shipped (see [What is supported](#what-is-supported)).

## Two different things called "perinatal"

| | Perinatal mortality **rate** (aggregate) | Perinatal **record** (record-level) |
|---|---|---|
| Definition | (fetal deaths ≥28 wk + early-neonatal deaths) / (live births + fetal deaths ≥28 wk) × 1000 | one infant row with its same-mother fetal-death sibling joined on |
| Needs record linkage? | **No** — stratum-level counts from the three products | **Yes** — a key connecting two pregnancies of one woman |
| Supported by HVS? | **Yes** — shipped (`joint_use_demo.ipynb` §C; `JOINT_USE_GUIDE.md` §128) | **No** — infeasible on public-use data (this note) |

The analytically important perinatal quantity — the rate — is already delivered. Only the record-level join is blocked, and only because the linking key was deliberately removed from the source files.

## Why the record-level sibling join is impossible

Four independent, permanent blockers, each sufficient on its own:

1. **No maternal / household / pregnancy identifier.** NCHS strips every direct and household identifier from public-use natality, fetal-death, and linked birth–infant-death files specifically to prevent re-identification. A "sibling" relation requires knowing two records share a mother; that key is not in the data and never was.
2. **No sub-national geography.** Full column enumeration of both shipped derived parquets shows zero state/county/region field — only a resident/non-resident `residence_status` recode. (Consistent with `PROJECT_STRUCTURE.md`'s which-file matrix: "Get state-level data → not available from public-use NCHS files.") The §15.D-proposed proxy key "maternal demographics + **state** + year" loses its highest-entropy non-demographic component entirely.
3. **Different pregnancies.** A stillbirth and the same mother's live birth are *different pregnancies*, generally in different years, with different gestational age, plurality, and infant sex. Pregnancy-specific attributes therefore cannot serve as a sibling key; only stable maternal attributes (race/ethnicity, nativity) could — and those alone partition millions of births into a handful of cells.
4. **Post-2018 bridged race is fully absent.** `maternal_race_bridged` is 100% NULL in both products from 2018 on (the documented NCHS bridged-race discontinuation; `JOINT_USE_GUIDE.md` bridged-race-gap caveat), removing one of the few stable maternal proxies for recent years. The two products also share no value-level cross-product record key (the existing `shared/helpers/canonical_join_keys.py` aliases column *names* for aggregate denominators, not record joins; education label vocabularies differ outright).

NCHS itself distributes the fetal-death file and the (period and cohort) linked files as separate products with no integrated perinatal dataset and no published record-level linkage (WebFetch of `cdc.gov/nchs/data_access/vitalstatsonline.htm`, 2026-05-23) — so there is also no external validation target for such an artifact.

## Quantitative evidence

The only join substrate left is coarse demographic strata. [`scripts/perinatal_feasibility_analysis.py`](../scripts/perinatal_feasibility_analysis.py) builds the most generous value-harmonized maternal key available — maternal age (exact single year, an upper bound on specificity), Hispanic origin, harmonized 4-category education, infant/fetal sex, plus bridged race where it exists — and measures, per year, how uniquely a fetal death (≥20 wk, canonical fetal-death filter) can be matched to a linked-file birth (canonical `residence_status != 4`). Years span every linked-product era and the bridged-race boundary.

<!-- The following table is verbatim deterministic output of scripts/perinatal_feasibility_analysis.py; see RECEIPTS/C8.19_2026-05-23T09-00-00Z.md. Do not hand-edit; regenerate. -->

| Year | Births | Infant deaths | Fetal deaths ≥20wk | Key | Effective strata | Candidate births / fetal death (mean) | (max) | "Unique" cells | Expected match rate | Stratum-flag TRUE |
|---|---|---|---|---|---|---|---|---|---|---|
| 2000 | 4,058,903 | 27,690 | 26,026 | age/hisp/edu/sex | 121 | 599 | 977 | 18 | 0.00044% | 1.5% |
| 2000 | 4,058,903 | 27,690 | 26,026 | + race | 246 | 292 | 606 | 41 | 0.00101% | 1.5% |
| 2007 | 4,316,233 | 28,725 | 26,296 | age/hisp/edu/sex | 138 | 424 | 686 | 17 | 0.00039% | 1.2% |
| 2007 | 4,316,233 | 28,725 | 26,296 | + race | 282 | 206 | 408 | 51 | 0.00118% | 1.2% |
| 2015 | 3,978,497 | 23,327 | 23,012 | age/hisp/edu/sex | 487 | 14,555 | 50,883 | 1 | 0.00003% | 98.3% |
| 2015 | 3,978,497 | 23,327 | 23,012 | + race | 984 | 7,805 | 39,986 | 11 | 0.00028% | 96.3% |
| 2020 | 3,613,647 | 19,346 | 20,216 | age/hisp/edu/sex | 486 | 13,934 | 50,891 | 1 | 0.00003% | 98.4% |

**Maximum expected unique-sibling match rate across all years and key variants: 0.00118%** <!-- computed by scripts/perinatal_feasibility_analysis.py --> — versus the 5% Tier-0 threshold. The result is uniform and year-invariant; it has two distinct failure modes:

- **Modern era (2015, 2020):** the maternal key is well populated, but each occupied stratum holds a *mean of ~14,000 candidate births* (max ~51,000). A fetal death "matches" thousands of births, none verifiably its sibling. The trivial "does this stratum contain ≥1 stillbirth" flag is true for ~98% of all births — it carries essentially zero sibling information (it only says stillbirths occur in nearly every demographic cell).
- **Pre-2015 era (2000, 2007):** the two products do not even share a value-level key (different source revisions / encodings; era-sparse harmonized education), so demographic cells barely coincide across files at all — pairs cannot be formed.

The handful of "unique" cells (1–51 per year) are **not real siblings**: they are demographic-cell singletons — coincidental one-birth/one-stillbirth cells with no maternal-identity verification. They are reported only as a generous upper bound, and even that upper bound is ~4,000× below the threshold at its most favorable. A naive cartesian proxy join would instead fabricate hundreds of millions of false pairings (e.g., ~280M for 2020) — the canonical example of plausible-looking but information-free output the project's discipline forbids.

### Reproduce

```bash
uv run python scripts/perinatal_feasibility_analysis.py
# deterministic; re-running yields byte-identical output.
# override input paths with HVS_LINKED_DERIVED / HVS_FETAL_DERIVED if your
# build tree differs.
```

## What is supported

Two legitimate perinatal analyses are already part of HVS:

1. **Perinatal mortality rate (aggregate, any stratum).** No linkage needed — counts from the three products jointly. Code and caveats: [`docs/JOINT_USE_GUIDE.md` §128](JOINT_USE_GUIDE.md#worked-example-perinatal-mortality-rate-2022-three-product-joint); cell-by-cell: [`notebooks/joint_use_demo.ipynb`](../notebooks/joint_use_demo.ipynb) Section C; FAQ: [`docs/WORKED_EXAMPLE_FAQ.md`](WORKED_EXAMPLE_FAQ.md#q-how-do-i-compute-the-perinatal-mortality-rate).
2. **Stillborn ↔ liveborn co-multiple linkage.** The one perinatal record-linkage public-use data genuinely supports — a multiple-gestation set where one fetus is stillborn and a co-twin/triplet is liveborn (with the infant-death and fetal-death outcomes linked *within the set* by NCHS itself) — is already a shipped HVS product: [`matched_multiples/`](../matched_multiples/) (C8.16). This is the genuinely linkable perinatal data, and it is in the resource.

## Future work — restricted-data linkage (out of public-use scope)

A true singleton, cross-pregnancy maternal-sibling perinatal record would require restricted access and is outside the scope of a *public-use* harmonization resource:

- **NCHS Research Data Center (RDC).** The RDC provides restricted-use data with indirect identifiers and geographic detail (`cdc.gov/rdc`, 2026-05-23). However, the public RDC documentation does not describe a maternal record-linkage key spanning the fetal-death and natality/linked data systems; fetal deaths and live births are separate NCHS data systems and NCHS does not publish a mother-level longitudinal link between a woman's stillbirth and her later live birth. Restricted geography alone does not produce a sibling key. Specifics would have to be confirmed with NCHS directly (rdca@cdc.gov).
- **State vital-records linkage.** Maternally-linked perinatal records exist in some state vital-statistics systems via state-held identifiers, under state IRB and data-use agreements — a separate, restricted, state-by-state research project.

Either path is a dedicated restricted-data study, not an extension of this public-use resource. Recording it here gives future researchers the map so they do not repeat the public-use dead end.

## Provenance and cross-references

- Decision + rationale: 2026-05-23T08:00:00Z.
- Reproducible analysis: [`scripts/perinatal_feasibility_analysis.py`](../scripts/perinatal_feasibility_analysis.py).
