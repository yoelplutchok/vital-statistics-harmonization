# Receipt: schema-years-available-gap-notation (D-prep.3)
## 2026-05-20T02:55:00Z

### What was done

Retroactive schema envelope notation: fixed fetal `delivery_year` / `data_year` stale `allowed_values` + v2.4.0 notes; added `#ENVELOPE_NOTE` comment rows to fetal + natality `harmonized_schema.csv`; added `1992-1994 gap` to linked `manner_of_death` `years_available`; filtered `#` rows in fetal/natality test `schema_df` fixtures + `_regenerate_schema_years.py`. Empirical `years_available` already matched parquet (`--check` OK). Zero parquet mutation.

### Verify results

- `fetal_death/scripts/_regenerate_schema_years.py --check`: **PASS**
- `pytest` spot-checks (fetal schema match + natality phantom-row): **PASS**
- 4 gate parquet SHAs: **PASS** — unchanged
- Schema data row counts: fetal 73 + natality 97 (excluding `#ENVELOPE_NOTE`)

### Self-check

1. Other linked rows without explicit gap suffix but with non-crossing spans (e.g. `1983-1998`) — intentional; gap is implicit in the span.
2. `matched_multiples/harmonized_schema.csv` unchanged (no multi-year gap product).
3. Regenerate script message says "74 columns" (includes comment row) — cosmetic only.

### Forward-looking HALTs for next session

1. **D-prep.3 CLOSED** — D-prep.4 audit may proceed (user `/ultrareview` or agent fallback).
2. Optional: align `fetal_death/quickstart.py` before audit.
3. 4 gate SHAs invariant unchanged.
