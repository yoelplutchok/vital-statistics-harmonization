# Receipt: codebook-c820-appendix-regen (D-prep.7)

## 2026-05-20T18:15:00Z

### What was done

Ran `uv run python scripts/_build_codebook_extensions.py` on build host (default env paths to `-build` / `natality-harmonization` trees). Regenerated C8.20 marker blocks in `fetal_death/CODEBOOK.md`, `natality/docs/CODEBOOK.md`, and FAQ pointers.

### Verify results

- Post-run gate SHAs: all four byte-identical vs D-prep.6 (PASS).
- `data_year` appendix `_Schema note_` reads `1982-2024` / `2,427,233/2,427,233` (PASS).
- No stale `1,634,195` in generated `_Schema note_` lines for `data_year` (PASS).
- Hand-authored CODEBOOK body outside markers unchanged except marker splice (PASS).

### Self-check

Could have edited outside markers if regex splice mis-anchored; spot-checked `data_year` block and git diff scope.

### Forward-looking HALTs for next session

1. Re-run gate SHA verify if any script touching parquets runs before Zenodo.
2. C8.20 appendix is deterministic — re-run should be byte-identical unless parquets drift.
