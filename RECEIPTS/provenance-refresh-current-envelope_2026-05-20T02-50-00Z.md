# Receipt: provenance-refresh-current-envelope (D-prep.2)
## 2026-05-20T02:50:00Z

### What was done

Refreshed per-product `PROVENANCE.md` for the v2.4.0 / v3.0.0 / v4.0.0 / matched-multiples envelope. Created `natality/PROVENANCE.md` and `matched_multiples/PROVENANCE.md` (previously referenced but missing). Rewrote `fetal_death/PROVENANCE.md` from v2.0.0 deposit SHAs to current gate artifacts. Added `docs/NCHS_SOURCE_MANIFEST.md` Section 5 (shipped harmonized parquets cross-reference). Doc-only; zero canonical-state mutation.

### Verify results

- 4 gate parquet SHAs: **PASS** — `38e2cecb…` / `185c071e…` / `acb5c48a…` / `f630d8cf…` byte-exact pre/post
- All documented SHAs re-hashed empirically (L6-safe)
- Scope: **PASS** — PROVENANCE files + NCHS manifest Section 5 only

### Self-check

1. `fetal_death/PROVENANCE.sha256` still targets v2.0.0 bundle (documented; not auto-regenerated).
2. Convenience/residents-only parquets not individually listed (by design; cite primary derived SHAs).
3. Build paths off-repo (`~/Desktop/*-harmonization*`) — documented explicitly.

### Forward-looking HALTs for next session

1. **D-prep.2 CLOSED** — next D-prep.3 then D-prep.4 (after 1–3).
2. Re-hash 4 gate SHAs at every PRE-FLIGHT.
3. Phase D remains per-step human-gated.
