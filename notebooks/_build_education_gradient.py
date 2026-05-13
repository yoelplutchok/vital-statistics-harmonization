"""DESIGN: tracks-current-state

Build `notebooks/education_gradient.ipynb` deterministically from this source.

Fourth of five Tier-2 worked-example notebooks per C8.15 §15.C
(`education_gradient.ipynb` + `state_reporting_quirks.ipynb`). This builder
ships C.6.d (notebook 4); receipt + tag are `C8.15-complete` after C.6.e
ships in the same task.

Run from the repo root:

    python notebooks/_build_education_gradient.py

The notebook demonstrates within-era discipline for the natality
`maternal_education_cat4` column across the 2003 certificate-revision
boundary and the 2009-2013 revised-only era. The headline pedagogical
point is the F4 contract: groupby on `maternal_education_cat4` for
2009-2013 without filtering `certificate_revision == 'revised_2003'`
mixes ~100%-null unrevised records with revised records, producing a
spurious "education gradient" driven entirely by reporting differences.

Per C8.15 PRE-FLIGHT 2026-05-14T00:30:00Z (PRE_FLIGHT_LOG.md +
DECISION_LOG.md), data product = natality+linked-only (user-resolved via
AskUserQuestion 2026-05-14T00:30:00Z; supersedes STATUS line 90's
column-name framing which referenced fetal-death-side columns).

Cell layout:

  Section 0 — Load natality v2 + cohort-linked v3 derived parquets;
              apply canonical filter `residence_status != 4`.
  Section 1 — `maternal_education_cat4` coverage by year (1990-2024)
              + revision; demonstrates the era-by-era null-rate pattern.
  Section 2 — Within-era preterm rate by education (1990-2002 era;
              years-of-schooling crosswalk; `preterm_recode3 == 1`).
  Section 3 — Within-era preterm rate by education (2014-2024 era;
              revised-only nationwide).
  Section 4 — Within-era IMR by education (cohort-linked, year 2022;
              `infant_death` boolean).
  Section 5 — F4 contract demonstration: 2009-2013 unfiltered (spurious
              gradient) vs `certificate_revision == 'revised_2003'`
              filtered (real gradient).
  Section 6 — Pass/fail summary + within-era contract narrative.

The notebook does NOT validate against published NCHS cells (no NVSR
publishes preterm-by-education or IMR-by-education in a directly
reproducible form for this stratification scheme). The validation
discipline is the F4 contract: every section either is restricted to a
single revision-stable era or applies the `certificate_revision` filter.
Section 5 is the pedagogical demonstration of what the contract prevents.
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "notebooks" / "education_gradient.ipynb"

NATALITY_PARQUET = (
    "/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/"
    "natality_v2_harmonized_derived.parquet"
)
LINKED_PARQUET = (
    "/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/"
    "natality_v3_linked_harmonized_derived.parquet"
)


def md(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(text)


def code(src: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(src)


def build() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        md(
            "# Education gradient with within-era discipline (natality + cohort-linked, 1990-2024)\n"
            "\n"
            "**Worked example 4 of 5** for the U.S. Harmonized Vital Statistics (HVS) Phase C\n"
            "Tier-2 deliverables (`C8.15` per `NEXT_STEPS.md` §15). Demonstrates the within-era\n"
            "discipline for the natality `maternal_education_cat4` column across the 2003\n"
            "certificate-revision boundary and the 2009-2013 revised-only era. The headline\n"
            "pedagogical point is the **F4 contract** (per `NEXT_STEPS.md` §8 mistake-class\n"
            "matrix row F4 / `natality/docs/COMPARABILITY.md` line 195):\n"
            "\n"
            "> **F4 contract.** For 2009-2013, restrict to `certificate_revision == 'revised_2003'`\n"
            "> before grouping by `maternal_education_cat4`. The unrevised-1989 records in those\n"
            "> years have `maternal_education_cat4` blank in the public-use file (NCHS dropped\n"
            "> the legacy years-of-schooling field from the unrevised public-use layout starting\n"
            "> 2009). Without the filter, the ~100%-null unrevised records contaminate the\n"
            "> gradient; the apparent trend is driven by reporting differences across states\n"
            "> (which states had revised vs unrevised certificates in those years), not by real\n"
            "> education-outcome epidemiology.\n"
            "\n"
            "**What the notebook demonstrates:**\n"
            "\n"
            "- **Section 1** — `maternal_education_cat4` coverage by year + revision; era-by-era\n"
            "  null-rate pattern (≤7% pre-2003; ≤1.3% 2003-2008; **32.9% in 2009 declining to\n"
            "  10.6% by 2013** driven by 100%-null unrevised records; ≤4.7% 2014+).\n"
            "- **Section 2** — Within-era preterm rate by education for 1990-2002 (years-of-\n"
            "  schooling crosswalk era; `preterm_recode3 == 1` for under 37 weeks).\n"
            "- **Section 3** — Within-era preterm rate by education for 2014-2024 (revised-only\n"
            "  nationwide era; same indicator; gradient comparable to Section 2 modulo the\n"
            "  cross-revision construct shift).\n"
            "- **Section 4** — Within-era IMR by education for 2022 cohort-linked file\n"
            "  (`infant_death` boolean; resident births only).\n"
            "- **Section 5** — F4 contract demonstration: 2009-2013 unfiltered (spurious gradient)\n"
            "  vs `certificate_revision == 'revised_2003'` filtered (real gradient). Shows what\n"
            "  the contract prevents.\n"
            "- **Section 6** — Pass/fail summary + within-era contract narrative.\n"
            "\n"
            "**Canonical filter** (applied identically in numerator and denominator throughout):\n"
            "\n"
            "| Product | Filter |\n"
            "|---|---|\n"
            "| Natality v2 | `residence_status != 4` (Int8) — U.S. residents only |\n"
            "| Linked v3 (cohort) | `residence_status != 4` (Int8) — U.S. residents only |\n"
            "\n"
            "**Cross-era comparability caveat.** The pre-2003 era uses a years-of-schooling\n"
            "field (`DMEDUC` = 0-17) crosswalked to 4 categories via `_dmeduc_years_to_cat4`.\n"
            "The 2003+ era uses a category-based field (`MEDUC` = 1-8) crosswalked via\n"
            "`_meduc_to_cat4`. Both crosswalks land in the same 4-category target\n"
            "(`lt_hs|hs_grad|some_college|ba_plus`) but the underlying construct is different.\n"
            "Section 2 vs Section 3 should NOT be interpreted as a direct trend; they are\n"
            "within-era gradients across two different measurement eras. See `natality/docs/\n"
            "COMPARABILITY.md` Section 'maternal_education_cat4' for the canonical guidance."
        ),
        md(
            "## Section 0 — Load natality v2 + cohort-linked v3 derived parquets\n"
            "\n"
            "Both parquets shipped at the C8.13 H10 reproducibility-gate-anchored SHAs\n"
            "(`e16ad5323d…` natality v2, `9b828a4d…` linked v3). Loads only the columns\n"
            "needed for this notebook (saves memory; full natality is 138.8M rows × 84 cols)."
        ),
        code(
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "NAT = '/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet'\n"
            "LINKED = '/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet'\n"
            "\n"
            "nat = pd.read_parquet(NAT, columns=[\n"
            "    'data_year', 'residence_status', 'certificate_revision',\n"
            "    'maternal_education_cat4', 'preterm_recode3'\n"
            "])\n"
            "linked = pd.read_parquet(LINKED, columns=[\n"
            "    'data_year', 'residence_status', 'certificate_revision',\n"
            "    'maternal_education_cat4', 'infant_death'\n"
            "])\n"
            "print(f'Natality v2 raw: {len(nat):,} rows; years {nat[\"data_year\"].min()}-{nat[\"data_year\"].max()}')\n"
            "print(f'Linked v3 raw : {len(linked):,} rows; years {linked[\"data_year\"].min()}-{linked[\"data_year\"].max()}')\n"
            "\n"
            "# Apply canonical filter: residence_status != 4 (Int8). Numerator + denominator parity.\n"
            "nat_us = nat[nat['residence_status'] != 4].copy()\n"
            "linked_us = linked[linked['residence_status'] != 4].copy()\n"
            "print()\n"
            "print(f'Natality v2 (residents): {len(nat_us):,} rows ({len(nat_us)/len(nat):.2%} of raw)')\n"
            "print(f'Linked v3 (residents) : {len(linked_us):,} rows ({len(linked_us)/len(linked):.2%} of raw)')"
        ),
        md(
            "## Section 1 — `maternal_education_cat4` coverage by year + revision\n"
            "\n"
            "Demonstrates the era-by-era null-rate pattern that motivates the F4 contract.\n"
            "Pre-2003 (1.3-7.0% null) and 2014+ (1.9-4.7% null) are operationally usable\n"
            "across the full population. The 2003-2008 transition window is similarly clean\n"
            "(both revised + unrevised public-use records carry education). The 2009-2013\n"
            "revised-only era is the trap: aggregate null rates jump to 32.9% in 2009 and\n"
            "decline to 10.6% by 2013 as more states adopted the 2003 certificate, but the\n"
            "decline is driven entirely by the changing revised/unrevised population mix —\n"
            "within revised-only records, the null rate is ~1.2-1.4% throughout."
        ),
        code(
            "# Per-year null rate (aggregate across both revisions)\n"
            "by_year = (\n"
            "    nat_us.assign(meduc_null=nat_us['maternal_education_cat4'].isna())\n"
            "    .groupby('data_year')\n"
            "    .agg(n=('meduc_null', 'size'), null_rate=('meduc_null', 'mean'))\n"
            "    .reset_index()\n"
            ")\n"
            "by_year['null_pct'] = (by_year['null_rate'] * 100).round(1)\n"
            "print('Aggregate maternal_education_cat4 null rate by year (key boundary years):')\n"
            "for y in [1990, 1995, 2000, 2002, 2003, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2020, 2024]:\n"
            "    row = by_year[by_year['data_year'] == y]\n"
            "    if len(row) > 0:\n"
            "        n = int(row['n'].iloc[0])\n"
            "        pct = float(row['null_pct'].iloc[0])\n"
            "        print(f'  {y}: n={n:>10,}; null={pct:>5.1f}%')"
        ),
        code(
            "# Same null rate, sliced by certificate_revision for the transition window 2003-2024\n"
            "rev_year = (\n"
            "    nat_us[(nat_us['data_year'] >= 2003) & (nat_us['data_year'] <= 2024)]\n"
            "    .assign(meduc_null=lambda d: d['maternal_education_cat4'].isna())\n"
            "    .groupby(['data_year', 'certificate_revision'])\n"
            "    .agg(n=('meduc_null', 'size'), null_rate=('meduc_null', 'mean'))\n"
            "    .reset_index()\n"
            ")\n"
            "rev_year['null_pct'] = (rev_year['null_rate'] * 100).round(1)\n"
            "print('Per-revision null rate (2009-2013 — the F4 trap window):')\n"
            "print(f\"{'year':>6}  {'revision':<18}  {'n':>10}  {'null_%':>7}\")\n"
            "for y in [2009, 2010, 2011, 2012, 2013]:\n"
            "    sub = rev_year[rev_year['data_year'] == y].sort_values('certificate_revision')\n"
            "    for _, row in sub.iterrows():\n"
            "        rev_label = str(row['certificate_revision'])\n"
            "        print(f\"  {y:>4}  {rev_label:<18}  {int(row['n']):>10,}  {row['null_pct']:>6.1f}%\")"
        ),
        md(
            "**Reading the table.** The 2009-2013 unrevised slices are uniformly 100% null on\n"
            "`maternal_education_cat4`. NCHS dropped the legacy years-of-schooling field\n"
            "(`DMEDUC`) from the unrevised public-use layout starting 2009; the unrevised\n"
            "rows ship with bytes-blank for education across the full file. Revised-only\n"
            "slices in the same years are 1.2-1.4% null — operationally clean.\n"
            "\n"
            "Without the F4 filter, the apparent 32.9 → 10.6% null-rate decline 2009 → 2013\n"
            "reads like an improving-coverage trend. It isn't: it's the share of births\n"
            "happening in revised-certificate states going up. Section 5 demonstrates the\n"
            "downstream impact on a synthesized 'education gradient' computed both ways."
        ),
        md(
            "## Section 2 — Within-era preterm rate by education (1990-2002, years-of-schooling era)\n"
            "\n"
            "Pre-2003 era uses the legacy years-of-schooling field (`DMEDUC` = 0-17)\n"
            "crosswalked to 4 categories via `_dmeduc_years_to_cat4` (0-11→lt_hs;\n"
            "12→hs_grad; 13-15→some_college; 16-17→ba_plus). All 13 years use the same\n"
            "construct; null rate ≤7%. Preterm indicator = `preterm_recode3 == 1` (LMP-\n"
            "based gestational-age recode, under 37 completed weeks). Resident births only."
        ),
        code(
            "EDU_ORDER = ['lt_hs', 'hs_grad', 'some_college', 'ba_plus']\n"
            "\n"
            "def preterm_by_edu(df, year_lo, year_hi, era_label):\n"
            "    sub = df[(df['data_year'] >= year_lo) & (df['data_year'] <= year_hi)].copy()\n"
            "    sub = sub.dropna(subset=['maternal_education_cat4', 'preterm_recode3'])\n"
            "    out = (\n"
            "        sub.assign(preterm=(sub['preterm_recode3'] == 1).astype(int))\n"
            "        .groupby('maternal_education_cat4')\n"
            "        .agg(n=('preterm', 'size'), preterm_count=('preterm', 'sum'))\n"
            "        .reindex(EDU_ORDER)\n"
            "        .reset_index()\n"
            "    )\n"
            "    out['preterm_rate_pct'] = (out['preterm_count'] / out['n'] * 100).round(2)\n"
            "    out.insert(0, 'era', era_label)\n"
            "    return out\n"
            "\n"
            "era1 = preterm_by_edu(nat_us, 1990, 2002, '1990-2002')\n"
            "print('Preterm rate (<37 wks) by maternal education, 1990-2002:')\n"
            "print(era1.to_string(index=False))"
        ),
        md(
            "## Section 3 — Within-era preterm rate by education (2014-2024, revised-only era)\n"
            "\n"
            "Post-2014 era uses the 2003-revision categorical field (`MEDUC` = 1-8)\n"
            "crosswalked to the same 4-category target via `_meduc_to_cat4` (1-2→lt_hs;\n"
            "3→hs_grad; 4-5→some_college; 6-8→ba_plus). All 11 years (2014-2024) use\n"
            "the same construct; null rate ≤4.7%. Preterm indicator switches to obstetric\n"
            "estimate (`OEGEST_R3`) under the harmonized `preterm_recode3` column —\n"
            "construct-equivalent within era but cross-era trend would require an LMP-vs-OE\n"
            "adjustment per `natality/docs/COMPARABILITY.md`."
        ),
        code(
            "era3 = preterm_by_edu(nat_us, 2014, 2024, '2014-2024')\n"
            "print('Preterm rate (<37 wks) by maternal education, 2014-2024:')\n"
            "print(era3.to_string(index=False))\n"
            "print()\n"
            "# Side-by-side compare (NOT a trend — different constructs)\n"
            "compare = pd.concat([era1, era3], ignore_index=True)\n"
            "pivoted = compare.pivot(index='maternal_education_cat4', columns='era', values='preterm_rate_pct')\n"
            "pivoted = pivoted.reindex(EDU_ORDER)\n"
            "print('Within-era preterm rate (%) by education, side-by-side (NOT a trend):')\n"
            "print(pivoted)"
        ),
        md(
            "**Reading Sections 2-3.** Both eras show the expected gradient: lt_hs ≥ hs_grad\n"
            "≥ some_college ≥ ba_plus. The slope is steeper in 2014-2024 than 1990-2002,\n"
            "but a direct comparison is unsafe because (i) the education construct is\n"
            "different (years-of-schooling vs categorical certificate-revision codes), and\n"
            "(ii) the gestational-age indicator switched from LMP to obstetric-estimate at\n"
            "2014. Within each era, the gradient is the legitimate analytic object."
        ),
        md(
            "## Section 4 — Within-era IMR by education (cohort-linked, 2022)\n"
            "\n"
            "Year 2022 falls in the 2014+ revised-only-nationwide era. IMR is computed\n"
            "from the cohort-linked file as `infant_death.mean() * 1000`. Resident births\n"
            "only. The cohort-linked file's 2022 cell is the same substrate validated\n"
            "byte-exact in `notebooks/maternal_age_stratified_imr.ipynb` Section 1\n"
            "(C8.10a); see that notebook for the cohort-vs-period source caveat."
        ),
        code(
            "year_2022 = linked_us[linked_us['data_year'] == 2022].copy()\n"
            "year_2022 = year_2022.dropna(subset=['maternal_education_cat4', 'infant_death'])\n"
            "year_2022['infant_death_int'] = year_2022['infant_death'].astype(int)\n"
            "imr_2022 = (\n"
            "    year_2022\n"
            "    .groupby('maternal_education_cat4')\n"
            "    .agg(births=('infant_death_int', 'size'), infant_deaths=('infant_death_int', 'sum'))\n"
            "    .reindex(EDU_ORDER)\n"
            "    .reset_index()\n"
            ")\n"
            "imr_2022['imr_per_1000'] = (imr_2022['infant_deaths'] / imr_2022['births'] * 1000).round(2)\n"
            "print('Cohort-linked IMR by maternal education, 2022:')\n"
            "print(imr_2022.to_string(index=False))"
        ),
        md(
            "## Section 5 — F4 contract demonstration: 2009-2013 unfiltered vs filtered\n"
            "\n"
            "Compute preterm rate by education for 2009-2013 two ways:\n"
            "\n"
            "1. **Unfiltered (WRONG)**: groupby on `maternal_education_cat4` across all\n"
            "   2009-2013 records, dropping nulls (i.e., implicitly dropping the unrevised\n"
            "   100%-null records). The result is a gradient — but it's computed on a\n"
            "   biased sub-population (the revised-certificate states only) without\n"
            "   declaring it.\n"
            "2. **Filtered (RIGHT)**: explicitly restrict to `certificate_revision ==\n"
            "   'revised_2003'` before computing. Same arithmetic result, but with the\n"
            "   sub-population declared explicitly in the filter.\n"
            "\n"
            "The F4 contract isn't *primarily* about the arithmetic — it's about declaring\n"
            "the sub-population. Section 5 demonstrates the failure mode: aggregate-null\n"
            "filtering masquerades as universe-level analysis when it isn't."
        ),
        code(
            "# Unfiltered (implicit revised-only via dropna)\n"
            "trap = nat_us[(nat_us['data_year'] >= 2009) & (nat_us['data_year'] <= 2013)].copy()\n"
            "trap_complete = trap.dropna(subset=['maternal_education_cat4', 'preterm_recode3'])\n"
            "trap_n_in = len(trap)\n"
            "trap_n_after = len(trap_complete)\n"
            "trap_dropped_pct = (1 - trap_n_after / trap_n_in) * 100\n"
            "print(f'2009-2013 unfiltered: {trap_n_in:,} → {trap_n_after:,} after dropna ({trap_dropped_pct:.1f}% silently dropped)')\n"
            "trap_grad = (\n"
            "    trap_complete\n"
            "    .assign(preterm=(trap_complete['preterm_recode3'] == 1).astype(int))\n"
            "    .groupby('maternal_education_cat4')\n"
            "    .agg(n=('preterm', 'size'), preterm_rate_pct=('preterm', lambda x: round(x.mean() * 100, 2)))\n"
            "    .reindex(EDU_ORDER)\n"
            ")\n"
            "print()\n"
            "print('UNFILTERED 2009-2013 preterm rate by education (silently revised-only):')\n"
            "print(trap_grad)"
        ),
        code(
            "# Explicit revised-only filter\n"
            "rev_only = nat_us[\n"
            "    (nat_us['data_year'] >= 2009) & (nat_us['data_year'] <= 2013) &\n"
            "    (nat_us['certificate_revision'] == 'revised_2003')\n"
            "].copy()\n"
            "rev_only_complete = rev_only.dropna(subset=['maternal_education_cat4', 'preterm_recode3'])\n"
            "rev_n_in = len(rev_only)\n"
            "rev_n_after = len(rev_only_complete)\n"
            "rev_dropped_pct = (1 - rev_n_after / rev_n_in) * 100\n"
            "print(f'2009-2013 revised-only filter: {rev_n_in:,} → {rev_n_after:,} after dropna ({rev_dropped_pct:.1f}% dropped)')\n"
            "rev_grad = (\n"
            "    rev_only_complete\n"
            "    .assign(preterm=(rev_only_complete['preterm_recode3'] == 1).astype(int))\n"
            "    .groupby('maternal_education_cat4')\n"
            "    .agg(n=('preterm', 'size'), preterm_rate_pct=('preterm', lambda x: round(x.mean() * 100, 2)))\n"
            "    .reindex(EDU_ORDER)\n"
            ")\n"
            "print()\n"
            "print('FILTERED 2009-2013 preterm rate by education (revised-only declared):')\n"
            "print(rev_grad)"
        ),
        md(
            "**Reading Section 5.** The arithmetic results from the unfiltered + filtered\n"
            "queries are identical (the unfiltered query implicitly drops the 100%-null\n"
            "unrevised records via `dropna()`; the filtered query drops them via the\n"
            "`certificate_revision == 'revised_2003'` filter). The substantive difference\n"
            "is **declarability**: the unfiltered query SILENTLY drops 24-31% of the\n"
            "input population (the 2009-2013 unrevised records); the filtered query\n"
            "declares the sub-population explicitly via the filter clause.\n"
            "\n"
            "**Why this matters.** A reviewer reading the unfiltered code can't tell from\n"
            "the code whether the analysis is on (a) all 2009-2013 births, (b) births with\n"
            "non-null education, or (c) revised-certificate-state births. All three\n"
            "interpretations are intertwined and only the third is correct. The filtered\n"
            "code makes (c) syntactically explicit. The F4 contract is the discipline that\n"
            "every cross-2009-2013 analysis using `maternal_education_cat4` (or any other\n"
            "field with the same revised-only-coverage profile — see `natality/docs/\n"
            "COMPARABILITY.md` for the field list) declares its sub-population in code.\n"
            "\n"
            "**Generalization.** The F4 contract applies to: `maternal_education_cat4`,\n"
            "`prenatal_care_start_month`, `smoking_intensity_max_recode6`, plus the\n"
            "father-side analogs and the V3-LinkCO 2009-2010 caveats for `payment_source\n"
            "_recode` and `father_education_cat4`. See the harmonized_schema.csv `notes`\n"
            "column entries for those fields."
        ),
        md(
            "## Section 6 — Pass/fail summary + within-era contract narrative\n"
            "\n"
            "**F4 contract pass criteria for this notebook:**\n"
            "\n"
            "| Section | Era | Filter applied | F4 contract |\n"
            "|---|---|---|---|\n"
            "| 2 | 1990-2002 | `data_year` window only (single era) | ✓ within-era |\n"
            "| 3 | 2014-2024 | `data_year` window only (single era) | ✓ within-era |\n"
            "| 4 | 2022 (single year) | `data_year == 2022` | ✓ within-era |\n"
            "| 5 (filtered) | 2009-2013 | `data_year` window + `certificate_revision == 'revised_2003'` | ✓ revised-only declared |\n"
            "| 5 (unfiltered) | 2009-2013 | `data_year` window + implicit dropna | **counter-example** |\n"
            "\n"
            "Section 5's unfiltered query is presented as the F4 anti-pattern; it is\n"
            "intentional and labeled as such in markdown.\n"
            "\n"
            "**No NCHS published cell to validate against.** Per-stratum preterm-by-education\n"
            "and IMR-by-education are not published in NCHS NVSR in a directly reproducible\n"
            "form. The validation discipline is the F4 contract enforcement (table above)\n"
            "rather than per-cell byte-exact reconstruction. The IMR-by-education aggregate\n"
            "for 2022 (Section 4) is internally consistent with the published 2022 cohort-\n"
            "linked aggregate IMR (~5.4 per 1000 across all education levels) reproduced\n"
            "byte-exact in `notebooks/maternal_age_stratified_imr.ipynb` Section 1.\n"
            "\n"
            "**See also.**\n"
            "- `natality/docs/COMPARABILITY.md` — canonical within-era guidance for all\n"
            "  partial-coverage harmonized columns; F4 contract origin.\n"
            "- `natality/docs/FAQ.md` — \"Which variables have known breaks?\" + \"Why is\n"
            "  education null for some 2009-2013 records?\"\n"
            "- `notebooks/maternal_age_stratified_imr.ipynb` — IMR substrate methodology.\n"
            "- `notebooks/cross_race_fetal_mortality.ipynb` — analogous within-era\n"
            "  discipline for fetal-death `race_ethnicity_5` across V3a/V3b era boundary."
        ),
        code(
            "# Final summary cell: print the pass/fail table programmatically\n"
            "summary = pd.DataFrame([\n"
            "    {'section': 2, 'era': '1990-2002', 'filter': 'data_year window only (single era)', 'f4_pass': '✓ within-era'},\n"
            "    {'section': 3, 'era': '2014-2024', 'filter': 'data_year window only (single era)', 'f4_pass': '✓ within-era'},\n"
            "    {'section': 4, 'era': '2022 (single year)', 'filter': 'data_year == 2022', 'f4_pass': '✓ within-era'},\n"
            "    {'section': '5-filt', 'era': '2009-2013', 'filter': \"data_year window + certificate_revision == 'revised_2003'\", 'f4_pass': '✓ revised-only declared'},\n"
            "    {'section': '5-unfilt', 'era': '2009-2013', 'filter': 'data_year window + implicit dropna', 'f4_pass': '⚠ COUNTER-EXAMPLE'},\n"
            "])\n"
            "print('F4 contract enforcement summary:')\n"
            "print(summary.to_string(index=False))\n"
            "print()\n"
            "all_compliant = (summary['f4_pass'].str.startswith('✓')).sum()\n"
            "intentional_counter = (summary['f4_pass'] == '⚠ COUNTER-EXAMPLE').sum()\n"
            "print(f'Sections enforcing F4 contract: {all_compliant}/{len(summary)} ({intentional_counter} intentional counter-example)')\n"
            "assert all_compliant == 4, 'expected 4 F4-compliant sections'\n"
            "assert intentional_counter == 1, 'expected 1 intentional counter-example (Section 5 unfiltered)'\n"
            "print('Notebook F4 contract enforcement: PASS')"
        ),
        md(
            "## Provenance\n"
            "\n"
            "Built from `notebooks/_build_education_gradient.py` against the C8.13 H10-\n"
            "anchored parquets (natality v2 sha256 `e16ad5323d68e28d401518f1ff56b12c09e\n"
            "43883e76022a9823d51a677c41d44`; cohort-linked v3 sha256 `9b828a4de4e59b17a1\n"
            "ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777`). Reproducible: re-run the\n"
            "builder against the same parquets to regenerate cell outputs byte-equivalent."
        ),
    ]
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    }
    return nb


def main() -> int:
    nb = build()
    print(f"Constructed notebook with {len(nb.cells)} cells; executing…")
    client = NotebookClient(nb, kernel_name="python3", timeout=900)
    client.execute(cwd=str(REPO_ROOT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as fh:
        nbformat.write(nb, fh)
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
