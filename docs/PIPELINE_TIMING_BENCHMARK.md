# Pipeline timing benchmark — C8.13 F.5

This document records the real end-to-end wall-clock measurements of the
fetal-death and natality+linked pipelines, captured at C8.13 F.5 DO
(2026-05-13). It reconciles measurements against the manuscript timing claim
at `paper/draft_v2_hmd_styled.md:68`:

> *"The fetal-death pipeline runs end-to-end in approximately six minutes on
> a 2024-vintage laptop; the natality pipeline (which also produces the
> linked file) takes approximately ninety minutes, dominated by the
> fixed-width parse stage."*

The §15 C8.13 VERIFY tolerance is **±10% per pipeline**; outside that band
triggers a PROPOSE-EDIT routed to Phase D step 4 per the C8.12 RECEIPT
manuscript-edit-bundles-at-Phase-D-step-4 precedent.

## Measurement methodology

- Driver scripts: `scripts/_drive_fetal_death_benchmark.py` (43-year per-step
  enumeration; routes around stale `fetal_death/scripts/run_pipeline.py`
  `ALL_YEARS=29` per soft-flag (d) / C8.7b deferred) and
  `scripts/_drive_natality_benchmark.py` (6-script chain;
  `parse_all_v1_years` + `parse_all_linked_years` + `harmonize_v1_core` +
  `harmonize_linked_v3` + `derive_v1_core` + `derive_linked_v3`).
- Per-stage wall-clock via `time.monotonic()` wrapped by
  `scripts/_time_pipeline.py::run_stages`; raw per-stage CSV at
  `docs/PIPELINE_TIMING_BENCHMARK_{fetal,natality}_raw.csv`.
- Pipelines run **serial** (fetal-death first, then natality+linked); each
  measurement isolated from the other's CPU/IO load.
- Validate stages excluded from the timing claim per the manuscript's
  "pipeline runs end-to-end" framing interpreted as parse → derive primary
  chain (validate is the Level-2 verification framing).
- H10 reproducibility gate: post-re-derive parquet SHAs MUST match the
  documented anchors byte-exact. **All 4 verified byte-exact** (see §H10
  below).

## Environment

| Item | Value |
|---|---|
| Hostname | `Yoels-MacBook-Air.local` |
| OS | Darwin 21.6.0 (macOS Monterey) |
| Python | 3.13.9 |
| pyarrow | 18.1.0 (pinned via `uv.lock`) |
| pandas | 2.3.2 |
| Disk | local SSD |
| Date | 2026-05-13 |

Note: the manuscript-cited "2024-vintage laptop" is the reference anchor;
the build machine here may differ (the measurement is the measurement, not
a claim of equivalent hardware). The +/-10% tolerance accommodates a
moderate hardware spread.

## Fetal-death pipeline (1982-2024, 43 years, 2,427,233 records)

### Stages

| Stage | Wall-clock (s) | Wall-clock (min) |
|---|---|---|
| Parse 43 yearly zips → yearly_clean parquets | 193.34 | 3.22 |
| Harmonize (concat + B1-B7 normalizations) | 80.72 | 1.35 |
| Derive (16 indicators) | 38.85 | 0.65 |
| **Total** | **312.91** | **5.22** |

### Parse breakdown by era

| Era | Years | n | Sum (s) | Mean s/yr | Note |
|---|---|---|---|---|---|
| V3b 1985-revision | 1982-1988 | 7 | 17.31 | 2.47 | Shortest record (200-360 B); fastest parse |
| V3a 1989-revision (early) | 1989-1991 | 3 | 16.55 | 5.52 | V2-comparable |
| V2 1989-revision (uniform) | 1992-2002 | 11 | 60.39 | 5.49 | Reference era |
| V2.1 2003-2004 transition | 2003-2004 | 2 | 9.15 | 4.57 | Two-byte-mapping era |
| V1 PRE-COD | 2005-2013 | 9 | 48.33 | 5.37 | 3338-3350 B records |
| V1 COD | 2014-2022 | 9 | 35.53 | 3.95 | 3050 B records (post-2018 → 2651 B) |
| Latest | 2023-2024 | 2 | 6.08 | 3.04 | 2651 B records |

### Reconciliation vs manuscript claim

- Manuscript claim: **~6 min**
- Measured: **5.22 min**
- Drift: **-13.1%** (faster than claim)
- ±10% PASS band: 5.4 - 6.6 min
- **VERIFY result: PROPOSE-EDIT** (outside ±10%; faster side)

### PROPOSE-EDIT to Phase D step 4

Per the C8.12 RECEIPT precedent, the actual manuscript line edit bundles to
Phase D step 4 (manuscript re-pass). This RECEIPT documents the proposal;
no in-session manuscript mutation.

Recommended Phase D step 4 edit at `paper/draft_v2_hmd_styled.md:68`:

> *"The fetal-death pipeline runs end-to-end in **approximately five
> minutes** on a 2024-vintage laptop; the natality pipeline (which also
> produces the linked file) takes approximately ninety minutes, dominated
> by the fixed-width parse stage."*

(Change: "**approximately six minutes**" → "**approximately five minutes**".
The natality clause is unchanged per §below.)

Alternative phrasing: keep "approximately six minutes" but document the
measured 5.22 min in the companion notebook + PROVENANCE.md refresh. The
"approximately" qualifier is technically defensible at 6 min for a 5.22
min measurement (within ~0.78 min of 6); the strict ±10% rule is for VERIFY
gating, not editorial wording. Phase D step 4 decides which framing fits
the manuscript voice.

## Natality + linked pipeline (1990-2024 natality, 2005-2023 linked)

### Stages

| Stage | Wall-clock (s) | Wall-clock (min) |
|---|---|---|
| Parse natality 1990-2024 (35 years, 138.8M records) | 3009.79 | 50.16 |
| Parse linked 2005-2023 (19 cohort years, 74.9M records) | 1281.22 | 21.35 |
| Harmonize natality V1 core | 368.53 | 6.14 |
| Harmonize linked V3 | 247.33 | 4.12 |
| Derive natality V1 core (84 cols) | 234.75 | 3.91 |
| Derive linked V3 (94 cols) | 165.62 | 2.76 |
| **Total** | **5307.24** | **88.45** |

### Stage distribution

- Parse stages (natality + linked): 4291.01s = 71.52 min = **80.9% of total**
- Harmonize stages: 615.86s = 10.26 min = **11.6% of total**
- Derive stages: 400.37s = 6.67 min = **7.5% of total**

This confirms the manuscript's "dominated by the fixed-width parse stage"
characterization quantitatively.

### Reconciliation vs manuscript claim

- Manuscript claim: **~90 min**
- Measured: **88.45 min**
- Drift: **-1.72%** (very close to claim; within 1.55 min)
- ±10% PASS band: 81 - 99 min
- **VERIFY result: PASS** (well within ±10%)

No edit recommended for the natality clause of `paper/draft_v2_hmd_styled.md:68`.

## H10 reproducibility gate

Per §7.18 — re-running the pipelines must produce byte-identical output
to the currently-shipped parquets. Verified byte-exact across all 4
shipped artifacts after the F.5 re-derive:

| Parquet | Pre-F.5 SHA-256 (documented anchor) | Post-F.5 SHA-256 | Match |
|---|---|---|---|
| `output/harmonized/fetal_death_harmonized.parquet` | `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` | `38e2cecb03ff4947…` | ✓ |
| `output/harmonized/fetal_death_derived.parquet` | `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` | `185c071ec76ab8aa…` | ✓ |
| `…/natality_v2_harmonized_derived.parquet` | `e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` | `e16ad5323d68e28d…` | ✓ |
| `…/natality_v3_linked_harmonized_derived.parquet` | `9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` | `9b828a4de4e59b17…` | ✓ |

H10 reproducibility holds end-to-end. Re-running the canonical pipelines on
the canonical raw inputs produces bit-identical parquets — the manuscript's
*"byte-identical file"* claim at line 67 is empirically validated.

## Caveats

1. **Build-machine vs reference machine.** The manuscript's "2024-vintage
   laptop" anchor is editorial framing, not a precise hardware spec. A
   factor-of-2 hardware spread can move measured wall-clock by ±50% per
   stage. The ±10% VERIFY tolerance assumes comparable-hardware.
2. **Disk cache effects.** Both pipelines were re-run on a machine where
   the prior shipped parquets already existed in OS page cache; the parse
   stage reads raw zips (uncacheable at scale; ~3.6 GB combined) but
   harmonize + derive may benefit from cached intermediate parquets. A
   cold-cache run would likely add 0-5% to harmonize + derive stages.
3. **Validate stage excluded.** Per the manuscript's "pipeline runs
   end-to-end" framing interpreted as parse → derive primary chain. The
   validate stages add ~30s (fetal-death `validate_external_v2.py` +
   `validate_2022.py`) + ~few minutes (natality validators) but were not
   timed because they are Level-2 verification framing, not
   pipeline-runtime claim substrate.
4. **No parallel execution.** Both pipelines were run serial to isolate
   per-pipeline measurements. A user with a multi-core machine could run
   them concurrently and reduce wall-clock by ~min(fetal, natality) =
   5.22 min savings; the manuscript's serial wording implies serial
   timing.
5. **Soft-flag (d) preserved.** `fetal_death/scripts/run_pipeline.py`
   `ALL_YEARS=29` was NOT extended to 43 this session (C8.7b scope); the
   F.5 measurement uses the explicit 43-year driver
   `scripts/_drive_fetal_death_benchmark.py` instead. Reproduction by
   future readers uses the driver, not the stale orchestrator.

## How to reproduce

```bash
# From monorepo root, with the C8.5a uv.lock environment active:
uv run python scripts/_drive_fetal_death_benchmark.py
uv run python scripts/_drive_natality_benchmark.py
shasum -a 256 output/harmonized/fetal_death_{harmonized,derived}.parquet
shasum -a 256 ~/Desktop/natality-harmonization/output/harmonized/natality_v{2_harmonized_derived,3_linked_harmonized_derived}.parquet
```

Re-derive should produce byte-identical parquets matching the documented
anchors. Total wall-clock will scale with hardware.

## Cross-references

- `RECEIPTS/C8.13_<UTC>.md` — the C8.13 task receipt
- `paper/draft_v2_hmd_styled.md:68` — manuscript timing claim cite
- `DECISION_LOG.md` 2026-05-13T22:30:00Z — F.1 falsified-premise plan-update
- `scripts/_time_pipeline.py` — timer wrapper utility
- `scripts/_drive_fetal_death_benchmark.py` — fetal-death driver
- `scripts/_drive_natality_benchmark.py` — natality+linked driver
- `docs/PIPELINE_TIMING_BENCHMARK_fetal_raw.csv` — per-stage CSV
- `docs/PIPELINE_TIMING_BENCHMARK_natality_raw.csv` — per-stage CSV
