# Independent Ananth 2022 replication — verification receipt

**Code:** `notebooks/ananth2022_replication_test_independent.py`  
**Outputs:** `RECEIPTS/ananth2022_outputs_independent/`  
**Compared against:** prior memo headline cells only (not read from prior CSVs).

## TL;DR

**Independent replication confirms the prior memo.** All 14 headline comparison cells match within rounding (largest Δ = 0.3 on White AP % change). **Paper 2 verdict unchanged:** period-coefficient shift at 2014 decisively exceeds 25% under every naive proxy except switching to NH race codes from 2014 onward (which collapses naive ≡ bilateral).

## Cell-by-cell vs prior memo

| Metric | Independent | Prior | Match |
|--------|------------:|------:|:-----:|
| ≥20 wk 2020 Black FMR | 9.94 | 9.94 | ✓ |
| ≥20 wk 2020 White FMR | 4.62 | 4.62 | ✓ |
| ≥24 wk 2020 Black FMR | 6.79 | 6.79 | ✓ |
| ≥24 wk 2020 White FMR | 3.28 | 3.28 | ✓ |
| Crude 2013→14 step Black naive | −0.335 | −0.335 | ✓ |
| Crude step Black bilateral | −1.418 | −1.418 | ✓ |
| Crude step White naive / bilateral | −0.114 / −0.955 | same | ✓ |
| AP RR 2014 Black naive / bilateral | 0.815 / 0.729 | same | ✓ |
| AP RR 2014 White naive / bilateral | 0.921 / 0.766 | same | ✓ |
| AP \|β\| % change Black / White | 54.7% / 223.3% | 54.7% / 223% | ✓ |

Full table: `comparison_to_prior_memo.csv`.

## Naive-proxy robustness (>25% period shift?)

| Naive variant | Black ge20wk | White ge20wk | Meets 25%? |
|---------------|-------------:|-------------:|:----------:|
| `naive_default` (bridged→2017/2019) | 54.7% | 223.3% | Yes |
| `naive_bridged_prefer` | 54.7% | 223.3% | Yes |
| `naive_hisp_impute` | 54.7% | 223.3% | Yes |
| `naive_mrace6` (MRACE6 2014+) | 54.9% | 225.4% | Yes |
| `naive_rhr_2014` (NH from 2014+) | **0%** | **0%** | **No** |

If Ananth applied NH-only race coding from 2014 onward on both numerator and denominator, the naive/bilateral distinction vanishes by construction — but that is not the default “straight bridged” proxy and would still leave pre-2014 bridged-INCL-Hispanic cells inconsistent with post-2014 NH cells in a single series.

## Cohort effects

Post-1985 cohort attenuation remains &lt;5% for Black; White peaks ~4% — well below the 25% decision threshold. Ananth’s youngest-cohort finding is robust.

## Implementation notes

- Natality streamed year-by-year via `pyarrow.dataset` (1982–2024 scan; models/rates on 1982–2020).
- FD loaded once (~2.4M rows); V2.1 ages via `maternal_age_recode14`.
- Six race schemes aggregated in one FD pass; five naive variants + bilateral.
