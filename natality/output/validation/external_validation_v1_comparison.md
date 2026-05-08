# External validation comparison (V1)

Computed from `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` (resident-only universes use `is_foreign_resident == false`).

- Targets: `/Users/yoelplutchok/Desktop/natality-harmonization/metadata/external_validation_targets_v1.csv`
- Output CSV: `/Users/yoelplutchok/Desktop/natality-harmonization/output/validation/external_validation_v1_comparison.csv`

## Summary

- pass: 183
- fail: 0
- missing expected or actual: 0

Notes:
- For many V1 variables (e.g., education/smoking in 2009–2013), the recommended comparison universe is `resident_revised`.

