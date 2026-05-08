# External validation comparison (V3 linked birth-infant death)

Computed from `natality_v3_linked_harmonized_derived.parquet` (resident-only: `is_foreign_resident == false`).

- Targets: `/Users/yoelplutchok/Desktop/natality-harmonization/metadata/external_validation_targets_v3_linked.csv`
- Output CSV: `external_validation_v3_linked_comparison.csv`

## Summary

- **Pass**: 35
- **Fail**: 0
- **Missing**: 0

## Target comparison

| Metric | Year | Expected | Actual | Diff | Status |
|--------|------|----------|--------|------|--------|
| resident_births | 2005 | 4138577 | 4138577 | 0 | pass |
| weighted_infant_deaths | 2005 | 28255 | 28255 | 0 | pass |
| resident_births | 2010 | 3999386 | 3999386 | 0 | pass |
| weighted_infant_deaths | 2010 | 24441 | 24441 | 0 | pass |
| resident_births | 2015 | 3978497 | 3978497 | 0 | pass |
| unweighted_infant_deaths | 2015 | 23326 | 23327 | 1 | pass |
| imr_per_1000 | 2015 | 5.86 | 5.86 | 0.00 | pass |
| neonatal_deaths | 2015 | 15554 | 15554 | 0 | pass |
| postneonatal_deaths | 2015 | 7772 | 7773 | 1 | pass |
| resident_births | 2020 | 3613647 | 3613647 | 0 | pass |
| unweighted_infant_deaths | 2020 | 19346 | 19346 | 0 | pass |
| imr_per_1000 | 2020 | 5.35 | 5.35 | 0.00 | pass |
| neonatal_deaths | 2020 | 12755 | 12755 | 0 | pass |
| postneonatal_deaths | 2020 | 6591 | 6591 | 0 | pass |
| resident_births | 2021 | 3664292 | 3664292 | 0 | pass |
| unweighted_infant_deaths | 2021 | 19965 | 19965 | 0 | pass |
| imr_per_1000 | 2021 | 5.45 | 5.45 | 0.00 | pass |
| resident_births | 2022 | 3667758 | 3667758 | 0 | pass |
| unweighted_infant_deaths | 2022 | 20268 | 20268 | 0 | pass |
| imr_per_1000 | 2022 | 5.53 | 5.53 | 0.00 | pass |
| neonatal_deaths | 2022 | 12948 | 12948 | 0 | pass |
| postneonatal_deaths | 2022 | 7320 | 7320 | 0 | pass |
| resident_births | 2023 | 3596017 | 3596017 | 0 | pass |
| unweighted_infant_deaths | 2023 | 19743 | 19743 | 0 | pass |
| imr_per_1000 | 2023 | 5.49 | 5.49 | 0.00 | pass |
| neonatal_deaths | 2023 | 12892 | 12892 | 0 | pass |
| postneonatal_deaths | 2023 | 6851 | 6851 | 0 | pass |
| neonatal_imr_per_1000 | 2015 | 3.91 | 3.91 | 0.00 | pass |
| postneonatal_imr_per_1000 | 2015 | 1.95 | 1.95 | 0.00 | pass |
| neonatal_imr_per_1000 | 2020 | 3.53 | 3.53 | 0.00 | pass |
| postneonatal_imr_per_1000 | 2020 | 1.82 | 1.82 | 0.00 | pass |
| neonatal_imr_per_1000 | 2022 | 3.53 | 3.53 | 0.00 | pass |
| postneonatal_imr_per_1000 | 2022 | 2.00 | 2.00 | 0.00 | pass |
| neonatal_imr_per_1000 | 2023 | 3.59 | 3.59 | 0.00 | pass |
| postneonatal_imr_per_1000 | 2023 | 1.91 | 1.91 | 0.00 | pass |

## IMR trend (all years, residents only)

| Year | Births | Deaths (unw) | Deaths (w) | IMR (unw) | IMR (w) | Neonatal | Postneonatal |
|------|--------|-------------|------------|-----------|---------|----------|--------------|
| 2005 | 4,138,577 | 27,893 | 28,255 | 6.74 | 6.83 | 18,492 | 9,401 |
| 2006 | 4,265,593 | 28,278 | 28,647 | 6.63 | 6.72 | 18,764 | 9,514 |
| 2007 | 4,316,233 | 28,725 | 29,181 | 6.66 | 6.76 | 18,709 | 10,016 |
| 2008 | 4,247,726 | 27,492 | 27,863 | 6.47 | 6.56 | 17,962 | 9,530 |
| 2009 | 4,130,665 | 25,793 | 26,145 | 6.24 | 6.33 | 16,983 | 8,810 |
| 2010 | 3,999,386 | 24,156 | 24,441 | 6.04 | 6.11 | 15,964 | 8,192 |
| 2011 | 3,953,591 | 23,547 | 23,841 | 5.96 | 6.03 | 15,831 | 7,716 |
| 2012 | 3,952,842 | 23,378 | 23,595 | 5.91 | 5.97 | 15,723 | 7,655 |
| 2013 | 3,932,181 | 23,142 | 23,361 | 5.89 | 5.94 | 15,700 | 7,442 |
| 2014 | 3,988,076 | 23,256 | 23,413 | 5.83 | 5.87 | 15,591 | 7,665 |
| 2015 | 3,978,497 | 23,327 | 23,463 | 5.86 | 5.90 | 15,554 | 7,773 |
| 2016 | 3,945,875 | 22,893 | 23,003 | 5.80 | 5.83 | 15,185 | 7,708 |
| 2017 | 3,855,500 | 22,167 | 22,260 | 5.75 | 5.77 | 14,789 | 7,378 |
| 2018 | 3,791,712 | 21,346 | 21,487 | 5.63 | 5.67 | 14,205 | 7,141 |
| 2019 | 3,747,540 | 20,639 | 20,796 | 5.51 | 5.55 | 13,690 | 6,949 |
| 2020 | 3,613,647 | 19,346 | 19,481 | 5.35 | 5.39 | 12,755 | 6,591 |
| 2021 | 3,664,292 | 19,965 | 20,183 | 5.45 | 5.51 | 12,489 | 7,476 |
| 2022 | 3,667,758 | 20,268 | 20,544 | 5.53 | 5.60 | 12,948 | 7,320 |
| 2023 | 3,596,017 | 19,743 | 19,982 | 5.49 | 5.56 | 12,892 | 6,851 |

## Notes

- 2005 and 2010 user guides report **weighted** infant death counts in documentation tables.
- 2015 user guide reports **unweighted** counts (explicitly labeled).
- 2015 and 2020 guides: 'For cohort file use: do not apply the weight.'
- Small differences (1-2 records) expected due to LATEREC (late-filed births) edge cases.

