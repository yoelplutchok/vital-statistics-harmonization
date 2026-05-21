# Receipt: build-host-gate-sha-verify (D-prep.6)

## 2026-05-20T18:00:00Z

### What was done

Independent `shasum -a 256` of the four gate parquets on the Mac build tree; compared to `fetal_death/PROVENANCE.md`, `natality/PROVENANCE.md`, and STATUS anchors.

### Verify results

| Artifact | Expected (prefix) | On-disk | Result |
|---|---|---|---|
| `fetal_death_harmonized.parquet` | `38e2cecb…` | `38e2cecb03ff4947…` | PASS |
| `fetal_death_derived.parquet` | `185c071e…` | `185c071ec76ab8aa…` | PASS |
| `natality_v2_harmonized_derived.parquet` | `acb5c48a…` | `acb5c48a9abf82ac…` | PASS |
| `natality_v3_linked_harmonized_derived.parquet` | `f630d8cf…` | `f630d8cf20db72ea…` | PASS |

Build paths: `~/Desktop/fetal-death-harmonization-build/output/harmonized/`, `~/Desktop/natality-harmonization/output/harmonized/`.

### Self-check

Could have compared wrong filenames (harmonized vs derived) or stale baseline copies; verified against PROVENANCE table names and full 64-char hashes.

### Forward-looking HALTs for next session

1. If any gate SHA drifts after D-prep.7–8, halt before Zenodo — do not patch PROVENANCE to wrong bytes.
2. D-prep.7 script must remain read-only on parquets.
