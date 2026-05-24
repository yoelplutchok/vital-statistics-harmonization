# Receipt: RD.1 — pre-1990 natality NVSR benchmarking (resident births 1968–1989)

## 2026-05-24T20:20:42Z

### What was done

Extended natality external validation backward to **1968–1989** for **`resident_births`** (22 new committed targets), matching the byte-exact discipline used for 1990–2024.

**Key design finding (PRE-FLIGHT):** Pre-1990 public-use files are not always 100% microdata row counts. NCHS publishes **residence-tabulated weighted totals** in each year's User Guide ("By residence") that match CDC `e6fc-ccez`. Unweighted `is_foreign_resident == false` row counts match CDC only from **1985** onward. For **1968–1988**, validation applies **SAMPWT weighting** on `natality_{year}_raw.parquet` (`RESTATUS != 4`; weight 2 when `SAMPWT == 2`; uniform 2× for 1968–1971 50% sample years).

**Shipped artifacts:**

| Artifact | Change |
|---|---|
| `natality/metadata/external_validation_targets_v1.csv` | +22 `resident_births` rows (1968–1989) |
| `natality/scripts/05_validate/compare_external_targets_v1.py` | `--yearly-parquet-dir`; `_weighted_resident_births_from_raw()` |
| `natality/tests/test_pre1990_resident_births_smoke.py` | NEW (DESIGN: tracks-current-state) |
| `natality/output/validation/external_validation_v1_comparison.{csv,md}` | Regenerated: **205/205 PASS** |
| `README.md`, `natality/README.md` | Validation headline |

**Build-host paths used:**

- Derived: `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`
- Raw yearly: `~/Desktop/natality-harmonization/output/yearly_clean/natality_{year}_raw.parquet`
- NVSR PDFs: `~/Desktop/natality-harmonization/raw_docs/Nat{year}doc.pdf` (for PRE-FLIGHT source verification; not committed)

### Five-phase trace

- **PRE-FLIGHT:** Build host present; 57-year derived envelope confirmed; CDC `e6fc-ccez` fetched for 1968–1989; weighted formula verified all 22 years before CSV commit (L6-safe).
- **SMOKE:** `test_pre1990_resident_births_smoke.py` (anchor years 1968, 1972, 1978, 1984, 1988 + 1989 derived).
- **DO:** CSV + validator + tests + doc lines.
- **VERIFY:** Full compare run **205/205 PASS**; pytest 6/6; natality derived gate SHA unchanged.
- **RECEIPT:** This file.

### Verify results

- `compare_external_targets_v1.py`: **205 pass / 0 fail / 0 missing** (183 prior + 22 new resident-birth years).
- `shasum -a 256` natality derived: `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` (unchanged).
- No edits under `output/harmonized/` in monorepo.

### Self-check (§10) — what could I have gotten wrong that VERIFY wouldn't catch?

1. **CDC `e6fc-ccez` vs NVSR PDF "By residence" drift for a year** — VERIFY used CDC as the committed source (same as 1990–2024 `resident_births`). A PDF transcription mismatch would not surface unless we dual-source a year. Mitigation: spot-checked 1984/1985/1988 User Guide page-8 weighted totals against CDC during PRE-FLIGHT.
2. **SAMPWT semantics wrong for a rare state-year** — formula matches CDC for all 22 years empirically; a corner-case state could still differ if NCHS revised a table post-publication. Low risk given byte-exact pass on full grid.
3. **Rate metrics still 1990+ only** — README now says 205/205 resident + 183/183 rates; a reader conflating "205 targets" with "all NVSR cells" would overstate coverage. Mitigation: explicit "rate/indicator targets (1990–2024)" wording.
4. **CI clone without raw parquets** — smoke tests skip cleanly; full 205-cell gate requires build host. Documented in HALTs.

### Forward-looking HALTs for next session

1. If `external_validation_targets_v1.csv` row count for `resident_births` drops below 57 contiguous years 1968–2024, halt — regression or partial target file.
2. Any natality re-derive must re-run compare with `--yearly-parquet-dir` on the build host; expect **205/205** resident-birth PASS.
3. Pre-1990 **rate** targets (LBW, preterm, twin, cesarean, …) need NVSR/*Vital Statistics* table transcription — separate session; not blocking RD.1 close.

### Reproducibility

Deterministic: targets CSV + weighted raw-parquet formula + derived parquet scan. Re-run:

```bash
python natality/scripts/05_validate/compare_external_targets_v1.py \
  --in ~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet \
  --yearly-parquet-dir ~/Desktop/natality-harmonization/output/yearly_clean \
  --targets natality/metadata/external_validation_targets_v1.csv \
  --out-dir natality/output/validation
```
