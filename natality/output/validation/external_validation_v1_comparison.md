# External validation comparison (V1)

Computed from `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` (resident-only universes use `is_foreign_resident == false`; 1968-1988 `resident_births` use SAMPWT-weighted totals from `/Users/yoelplutchok/Desktop/natality-harmonization/output/yearly_clean`).

- Targets: `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/natality/metadata/external_validation_targets_v1.csv`
- Output CSV: `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/natality/output/validation/external_validation_v1_comparison.csv`

## Summary

- pass: 249
- fail: 0
- missing expected or actual: 0

Notes:
- For many V1 variables (e.g., education/smoking in 2009–2013), the recommended comparison universe is `resident_revised`.

