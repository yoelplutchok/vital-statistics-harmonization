# Manuscript drafts

Data Resource Profile manuscript covering the three products as a unified resource.

## Drafts

| File | Status | Modeled on |
|---|---|---|
| `draft_v1_ipums_styled.md` | Superseded | Sobek et al., *Data Resource Profile: IPUMS-International*, IJE 2017 |
| `draft_v2_hmd_styled.md` | **Current preferred** | Barbieri et al., *Data Resource Profile: The Human Mortality Database*, IJE 2015 |

The HMD-styled draft is closer because the HMD paper harmonizes a single class of vital-statistics data across version boundaries, validates against published rates, and ships derived files alongside raw inputs — exactly the structural problem this resource solves.

## Outstanding manuscript work

- **Word count.** The HMD-styled draft is ~3,500 words; IJE main-text limit is 2,500 words excluding abstract, key features, references, and tables. Trim Strengths and Weaknesses (longest section).
- **Admin sections.** Author contributions, AI-tool disclosure, Funding are placeholders.
- ~~**Linked-file validation framing.**~~ **RESOLVED 2026-05-11 (Task 6, see `DECISION_LOG.md` and `RECEIPTS/task6_*.md`).** Canonical framing across the repo is "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance." Both manuscript drafts already use this framing; `natality/README.md`, `natality/docs/{ABOUT_THIS_RELEASE,COMPARABILITY,VALIDATION}.md`, and `NEXT_STEPS.md` §14 Table 1 were updated to match. Authoritative source: `natality/output/validation/external_validation_v3_linked_comparison.md`.
- **Table 1 row count check.** Make sure record-length figures and era boundaries in Table 1 match each subproject's `record_layout_*.csv` and the relevant NCHS user guides.
- **Figures.** Decide which of the existing figures (`natality/figures/fig{1-4}_*.{pdf,png}`, `fetal_death/figures/figure{1-3}_*.{pdf,png}`) appear in the manuscript, and whether a cross-product figure is needed (e.g., a single timeline showing all three products' coverage with era boundaries).
- **References.** Add the IPUMS, HMD, and IPUMS-NHIS Data Resource Profiles as adjacent-resource citations (sourced from `docs/PRIOR_ART.md`).
- **Companion notebook.** Build `notebooks/paper_companion.ipynb` that reproduces every numeric claim in the manuscript directly from the parquets.
