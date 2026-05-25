# Receipt: RD.1b-phase-b-c-audit-remediation

**Completed:** 2026-05-25T03:05:07Z

## What was done

Fresh-eyes adversarial audit of RD.1b Phase B + C (`AUDITS/RD.1b-phase-b-c-audit_2026-05-25T02-42-45Z.md`) cleared **PASS-WITH-NOTES** (0 critical / 0 high / 3 med / 3 low). Human authorized fix sessions for F1, F2, F3, F5; F4/F6 accepted as-is. Applied:

- **F1 — 1971 LBW re-sourced (target value change).** `lbw_rate_pct,1971` in `natality/metadata/external_validation_targets_v1.csv`: `7.6 / tol 0.06` (IOM 1985 Table B.1 secondary, 7.64%) → **`7.7 / tol 0.05`**, sourced to MVSR `mv23_08sacc.pdf` ("During 1972, 7.7 percent … the same percent as in 1971"); IOM retained as corroboration. DECISION_LOG entry `2026-05-25T02:47:41Z` (supersedes the 1971 portion of the `02:05:00Z` 0.06-tol entry; **1973 LBW unchanged at 7.6/0.06** — direct `mv23_11sacc` cite, microdata 7.55% genuinely needs 0.06).
- **F2 — pre-1990 comparability documented.** Added §"Pre-1990 (1968–1989) external-validation comparability" to `natality/docs/COMPARABILITY.md`: preterm known-gestation / LMP-reporting-area denominator (GESTREC3/GESTAT3 code 3 = not-stated, excluded; excluded fraction ~40% 1972 → ~20% 1980 → ~4% 1985–88 → ~1.4% 1989); 1968 GESTREC vs 1972+ recode; 1989 raw `GESTAT3` vs 1990+ derived `preterm_lt37`; LBW comparability + sourcing. v3.0.0 scope note updated to point to it; broader pre-1990 narrative still routed to C8.20 / soft-flag (aa).
- **F3 — 1968 cells flagged indirect/definitional.** CSV `notes` for `lbw_rate_pct,1968` (INDIRECT CITE — no direct 1968 MVSR headline) and `preterm_rate_pct,1968` (PUF-DEFINITIONAL — GESTREC 0–4 per Nat1968doc, not a published headline) + documented in the new COMPARABILITY section. **Manuscript NOT touched** (`paper/` gated until §15.F closes); manuscript footnote action queued for the future paper session, now backed by artifact caveats.
- **F5 — README composition corrected.** `README.md` + `natality/README.md`: "205 resident-births 1968–2024" → true composition **56 resident-births + 44 LBW/preterm 1968–1989 + 149 1990+ rate/indicator cells = 249**. `205/205` milestone counts in KICKOFF/STATUS/NEXT_STEPS left as-is (accurate cumulative totals, not composition labels).

## VERIFY

- Build-host compare after all edits: **249/249 PASS / 0 fail / 0 missing** (`/tmp/rd1b-f2f3f5-final/external_validation_v1_comparison.csv`).
- `lbw_rate_pct,1971`: actual 7.6553 vs expected 7.7, |diff| 0.045 ≤ 0.05 → pass at standard tolerance.
- CSV integrity: all 249 data rows parse with intact metric/year/expected/tolerance; the 41 split-`notes` rows (unquoted "1,000"/"2,500"/etc.) are pre-existing and harmless (notes is passthrough; comma falls after all computed fields).
- Gate derived SHA unchanged: `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974`.
- F1+F3 touched only target value/tolerance/notes; F2+F5 are docs-only. No validator, parquet, or schema mutation.

## Forward-looking HALTs for next session

1. Re-run compare after any target/validator edit; expect **249/249** PASS.
2. **§15.F is now clear of audit blockers** (F1/F2/F3/F5 applied; F4/F6 accepted). May close → default queue **D.4**.
3. Manuscript footnote for the 1968 LBW (indirect) + 1968 preterm (PUF-definitional) cells remains owed at the next `paper/` session (gated until §15.F closes); artifact caveats are in place to support it.
4. No git tag added for this remediation (doc + single-target follow-up to the already-tagged Phase B/C work).

## §10 self-check

F1 changes a published-comparison target value (7.6→7.7): justified by a primary MVSR back-reference that outranks the prior IOM secondary, and the cell now passes at standard 0.05 tol — but anyone re-deriving must note the DECISION_LOG supersession so the 02:05Z 0.06-tol entry is not read as still governing 1971. F2's pre-1990 comparability section is scoped to the *validation targets*; it deliberately does not claim to be the full pre-1990 narrative (still C8.20) — a reader wanting certificate-era / race-recode / sample-fraction detail must wait for C8.20. F3's manuscript footnote is documented but not yet executed (paper gated); the 1968 cells remain in the 249/249 headline, so a casual reader could still over-read them as direct external transcriptions until the manuscript footnote lands.
