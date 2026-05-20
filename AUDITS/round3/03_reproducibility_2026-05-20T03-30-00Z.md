# Audit #3 — Reproducibility surface (D-prep.4 round 3)

- **Timestamp:** 2026-05-20T03:30:00Z
- **Verdict:** **CONDITIONAL PASS**

## Findings

| ID | Sev | Location | Class | Summary |
|---|---|---|---|---|
| A3-001 | high | `fetal_death/file_inventory.csv` | L13 | All 43 rows `imported=no` despite shipped 1982–2024 parquets |
| A3-002 | med | `matched_multiples/file_inventory.csv` | L13 | All 3 windows `imported=no` vs shipped harmonized parquet |
| A3-003 | high | `*/REPRODUCING.md`, `PROVENANCE.md` | H10 | Claims `file_inventory` lists SHA-256 — no sha256 column |
| A3-004 | high | `natality/REPRODUCING.md` | H10 | Standalone GitHub URL; ~50 zips; linked 1983–2015; stale shapes |
| A3-005 | med | `NCHS_SOURCE_MANIFEST.md` §2 | H10 | Intro still says pre-1990 `imported=false` — contradicts inventory |
| A3-006 | med | `natality/metadata/harmonized_schema.csv` | L13 | `#ENVELOPE_NOTE` 1968–2024 but `data_year` still `1990-2024` |
| A3-007 | med | `natality/README.md` vs inventory | path | Linked download pattern vs single `LinkCO{YY}US.zip` keys |

## Verified OK

- Manifest §5 gate SHAs = all three `PROVENANCE.md` files (7 rows)
- 141 zip count; C8.18 cohort 38 rows `imported=true`; 1992–1994 gap in schema notes
- `fetal_death/scripts/run_pipeline.py` monorepo paths
