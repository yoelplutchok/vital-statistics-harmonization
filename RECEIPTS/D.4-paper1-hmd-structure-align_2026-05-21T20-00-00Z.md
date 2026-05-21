# RECEIPT — D.4-paper1-hmd-structure-align — 2026-05-21T20:00:00Z

**Task.** Tighten `paper/draft_v2_hmd_styled.md` to follow the **HMD IJE-2015 Data Resource Profile structure** more closely (user-directed). Four moves; HMD's *organization*, original prose + our own content/figure (no HMD wording reproduced). Builds on `D.4-paper1-ije-finalize-complete` (`39c6ecd`).

## Five-phase trace

- **PRE-FLIGHT** (`PRE_FLIGHT_LOG.md` 2026-05-21T19:30:00Z; commit `0cc2843`; tag `D.4-paper1-hmd-structure-align-pre-do`): HMD skeleton fetched (PMC4707194); figure confirmed stale; figure-regen + word-budget plan; accuracy guards carried. No §7 halt.
- **DO:**
  1. **Dropped the abstract paragraph** — HMD opens directly at "Data resource basics"; the summary survives in the "HVS in a nutshell" box (HMD-faithful; word-count-neutral, abstract excluded from the 2,500).
  2. **Added a "Related resources" section** (before the nutshell, mirroring HMD's "Related Databases"): superseded single-product deposits (DOIs `19363074`, `20031571`) + adjacent harmonized resources (IPUMS-International, HMD, NBER, ICPSR) positioning the gap HVS fills. Original prose; content from `docs/PRIOR_ART.md`.
  3. **Added Figure 1 = cross-product coverage timeline** (mirrors HMD's Figure 1). **Regenerated the stale asset**: edited `shared/helpers/build_timeline_figure.py` — relaxed `verify_band_coverage` (no-overlap; documented internal gaps allowed), added the natality 1968–1989 band, the linked 1983–2004 cohort bands with the **visible 1992–1994 gap**, and a 4th row for matched multiples (two non-overlapping blocks 1995–2000 / 2016–2020), extended the x-axis to 1966 and added the 4th y-row; moved the legend below the x-label. Re-ran → `figures/fig1_coverage_timeline.{pdf,png}` now depict all four products at the current envelope (visually verified). Added the in-text "(Table 1, Figure 1)" callout + a caption (caption notes the linked gap, the MM inter-window gap, and the 1995–1997⊂1995–2000 collapse).
  4. **Expanded references 8 → 12** (toward HMD's ~16): added `gregory2024`, `nichd2024` (cited in Basics for the persistent-gap point) and `nber`, `icpsr` (cited in Related resources).
  - **Offset trim** to honor the 2,500 limit (Related resources + the citation clause added ~110 words → 2,586): ~12 prose-condensation edits across Use / S&W / Basics / Measures / Methods / Future / Related resources, no number/DOI/citation changed. Final body **2,499** (Word-like, footnote refs + Table 1 + Figure 1 caption excluded).
- **VERIFY:** body **2,499 ≤ 2,500**; abstract removed (the abstract's opening clause greps 0); `## Related resources` present (before the nutshell); every headline number/DOI present (201,161,456 / 149,386,620 / 2,427,233 / 1,665,568 / `20326150` / 183/183 / 33/35 / 13/13 / 97 total ×1 each); "Figure 1" referenced (callout + caption); **12 footnote definitions**, all four new refs cited + defined (×2 each); the regenerated figure shows 4 products + correct ranges + the linked gap. `git status` = `paper/draft_v2_hmd_styled.md` + `shared/helpers/build_timeline_figure.py` + `figures/fig1_coverage_timeline.{pdf,png}`. **No gate parquet / schema / validation-CSV / pipeline script touched → 4 gate SHAs byte-exact.**
- **RECEIPT:** this file + DECISION_LOG + STATUS; commit + tag `…-complete`.

## HMD structural fidelity (after this pass)

| HMD (IJE 2015) | Draft now |
|---|---|
| opens at Data Resource Basics (no abstract) | ✅ abstract dropped |
| Basics → Coverage → Measures → Methods → Use → S&W → Future → Access → **Related Databases** → Nutshell | ✅ same order incl. **Related resources** |
| Figure 1 = coverage-by-year timeline; 0 tables | Figure 1 = coverage timeline (+ 1 era-boundary table — a permitted addition; HMD allows up to 5 tables/figures) |
| ~16 references | 12 (expanded from 8) |
| Strengths = guiding principles; "in a nutshell" box near end | ✅ both present |

## §10 self-check — what could be wrong that VERIFY wouldn't catch?

- **Word margin is 1.** 2,499 is a whitespace/Word-like proxy; the journal system may count slightly higher. If it reads >2,500, trim S&W (still the longest body section). For a personal-experiment HMD-mimic this is immaterial; for submission, confirm in-system.
- **Figure determinism.** The generator is COMPARABILITY-sourced and deterministic; I edited band specs + plot extents and re-ran. The PNG was visually verified to show 4 products + the linked 1992–94 gap + MM two-block coverage. Risk: a band year-boundary typo would mis-draw a transition — mitigated by `verify_band_coverage` (passed) and the visual check.
- **Dropping the abstract diverges from the *current* IJE template** (which wants a Key-Features box, not "no abstract"). This was deliberate to follow HMD (2015) per the user; for an actual IJE submission, convert the nutshell box → a ≤200-word Key Features block at the top (one move, noted in forward-HALTs).
- **New references are data-archive/report citations** (NBER, ICPSR, NICHD) without DOIs/PMIDs in some cases — appropriate for those resources but a submission copy-editor may want URLs/access dates; `gregory2024` has a PMID (38143212) available in `docs/PRIOR_ART.md` if a fuller citation is wanted.
- **Figure asset is now current but un-validated against a regenerated paper_companion.** The figure depicts era *boundaries* (from COMPARABILITY), not parquet-derived counts, so it's independent of the still-owed companion-notebook regen.

## Forward-looking HALTs for next session

1. **Key Features box for IJE submission**: if targeting the current IJE template (not the 2015 HMD layout), convert "HVS in a nutshell" → a top-of-paper ≤200-word **Key Features** bullet box; the HMD-faithful no-abstract opening is otherwise submission-incompatible with the current author instructions.
2. **Carried:** companion-notebook regen on the build host; confirm Word count in-system (thin margin); author `<!-- YP -->` markers + cover-letter header.
3. **Figure generator** now models documented gaps; if a future product/year changes coverage, edit the band specs in `build_timeline_figure.py` and re-run (deterministic).

## Build artifacts current

- `paper/draft_v2_hmd_styled.md`: HMD-structure-aligned (no abstract; +Related resources; +Figure 1 callout/caption; 12 refs); body 2,499 words.
- `shared/helpers/build_timeline_figure.py`: 4-product / 1968–2024 envelope; gap-aware band check.
- `figures/fig1_coverage_timeline.{pdf,png}`: regenerated (4 products, linked 1992–94 gap, MM two-block).
- **Zero canonical-state mutation**: 4 gate parquet SHAs (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`) byte-exact (no parquet/schema/validation-CSV/pipeline touched).
