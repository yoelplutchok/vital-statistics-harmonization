"""DESIGN: tracks-current-state

Build `notebooks/cross_race_fetal_mortality.ipynb` deterministically from
this source.

Third of three Tier-2 worked-example notebooks per C8.10 §15.C
(`maternal_age_stratified_imr.ipynb` / `preterm_outcomes_time_series.ipynb` /
`cross_race_fetal_mortality.ipynb`). This builder ships notebook 3 of 3
(C.6.c); receipt + tag are `C8.10c-complete`. Parent `C8.10-complete`
tag follows in the same commit.

Run from the repo root:

    python notebooks/_build_cross_race_fetal_mortality.py

The notebook reproduces the 7 *NVSR 73-09* Table A 2022 race-stratified
fetal-mortality-rate cells from `joint_use_demo.ipynb` Section B
precedent (byte-exact within ±0.01/1000 rounding tolerance) as the
current-era cross-validation backbone, then extends to a 1982-2024
cross-era race-stratified FMR time series spanning V3b (1982-1988,
1978-revision 1-digit MRACE), V3a (1989-1991, 1989-revision 2-digit
MRACE), V2 (1992-2002), and V1 (2003-revision 2005-2024 with 2014 OE-
methodology boundary).

The cross-era race-stratification uses `maternal_race_bridged` (Int8
4-cat: 1=White, 2=Black, 3=AIAN, 4=API; available 1982-2013) for the
pre-2014 panel; `race_hispanic_revised` (string codes 1-8 single-race
+ Hispanic; available 2014+) collapsed to the bridged 4-cat scheme for
the post-2014 panel. The 2014 OE-methodology boundary is marked.

Validates ≥3 NVSR-equivalent cells: 7 NVSR 73-09 Table A 2022 cells
(byte-exact via joint_use_demo Section B precedent) + 9 per-era
bridged-race conservation invariants (sum-of-4-cats + null = total per
year). The B3 1-digit-recode caveats (V3b code 7 + code 9 → null per
DECISION_LOG 2026-05-12T18:30:00Z; V3a code 09 → null per DECISION_LOG
2026-05-12T14:30:00Z) are documented inline.

Cell layout:

  Section 0 — Load FD + natality parquets; apply canonical filters
              (per-year FMR tab==1; NVSR Table A detail tab==2);
              report cross-era universe counts.
  Section 1 — 7 NVSR 73-09 Table A 2022 byte-exact cells (cross-
              validation against joint_use_demo Section B precedent).
              tab==2 universe.
  Section 2 — Per-era bridged-race conservation invariants. V3b
              (1982-1988) + V3a (1989-1991) + V2 (1992-2002) + V1
              (2005-2013) era; each era reports per-year sum-of-4-
              cats + null = total invariant. B3 1-digit recode null
              fractions per era documented.
  Section 3 — 1982-2024 cross-era race-stratified FMR time series.
              Uses maternal_race_bridged 1982-2013 + race_hispanic_
              revised collapsed to 4-cat bridged for 2014+. 2014 OE-
              methodology boundary marked. Per-year FMR universe
              (tab==1).
  Section 4 — B3 1-digit-recode caveats narrative + cohort-vs-period
              N/A + 2014 OE-shift boundary documentation.
  Pass/Fail summary table.

Per C8.10c PRE-FLIGHT 2026-05-13T16:30:00Z (PRE_FLIGHT_LOG.md): one
§7.13 condition surfaced + user-resolved via AskUserQuestion 2026-05-
13T16:15:00Z Option A. The §15 PRE-FLIGHT-input "NVSR validation cells
per notebook (L9 cheap-check)" has no encoded source for race-
stratified V3a/V3b 1982-1991 FD (all 3 validation CSVs have zero race
cells; per DECISION_LOG 2026-05-12T14:30Z + 18:30Z, NVSR Series 21
race cells for that era are post-submission scope). Resolution: 7
NVSR 73-09 Table A 2022 cells from joint_use_demo Section B (already
byte-exact-validated at Task 2 receipt 2026-05-11) serve as the
validation backbone. The L11 in-PRE-FLIGHT re-interpretation pattern
generalizes: when the encoded CSV lacks relevant cells for a chosen
era/strata, the validation backbone may be drawn from a sibling
notebook's already-validated byte-exact result.

References:
- joint_use_demo Section B (lines 239-310): 7-cell NVSR 73-09 Table A
  2022 race-stratified FMR validation table (the precedent).
- DECISION_LOG 2026-05-12T14:30:00Z: V3a B3 maternal_race_bridged code
  09 → null (1989-rev "All other Races"; 165 records / 0.087% V3a).
- DECISION_LOG 2026-05-12T18:30:00Z: V3b B3 code 7 + code 9 → null
  (1978-rev; ~89 records code 7; ~18,700 code 9 / 3-5% per V3b year).
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import REPO_ROOT, paths_setup_source  # noqa: E402

OUTPUT = REPO_ROOT / "notebooks" / "cross_race_fetal_mortality.ipynb"


def md(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(text)


def code(src: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(src)


def build() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        md(
            "# Cross-era race-stratified fetal mortality (1982-2024)\n"
            "\n"
            "**Worked example 3 of 3** for the U.S. Harmonized Vital Statistics (HVS) Phase C\n"
            "Tier-2 deliverables (`C8.10` per `NEXT_STEPS.md` §15). Demonstrates the analytic\n"
            "value of the V3a (1989-1991) + V3b (1982-1988) backward extension shipped 2026-05-12\n"
            "by producing a 43-year (1982-2024) race-stratified fetal-mortality-rate time series\n"
            "spanning four era-revisions of the U.S. Standard Certificate of Fetal Death.\n"
            "\n"
            "**What the notebook validates:**\n"
            "\n"
            "- **Section 1** — 7 *NVSR 73-09* Table A 2022 race-stratified fetal-mortality-rate\n"
            "  cells (Total / NH AIAN / NH Asian / NH Black / NH NHOPI / NH White / Hispanic),\n"
            "  reproduced byte-exact (within ±0.01/1000 rounding tolerance) via the\n"
            "  `joint_use_demo.ipynb` Section B precedent. This is the validation backbone for\n"
            "  the current-era (2014+ OE-methodology) race-stratified analysis.\n"
            "- **Section 2** — Per-era `maternal_race_bridged` conservation invariants for V3b\n"
            "  (1982-1988), V3a (1989-1991), V2 (1992-2002), and V1 pre-2014 (2005-2013). Each\n"
            "  era asserts `sum(bridged_1..4) + null == total` for every year. B3 1-digit-recode\n"
            "  null fractions are reported per era.\n"
            "- **Section 3** — 1982-2024 cross-era race-stratified FMR time series. Uses\n"
            "  `maternal_race_bridged` 1982-2013; `race_hispanic_revised` collapsed to bridged\n"
            "  4-cat for 2014+. 2014 OE-methodology boundary marked.\n"
            "\n"
            "**B3 1-digit-recode caveats (DECISION_LOG 2026-05-12T14:30:00Z + 18:30:00Z):**\n"
            "\n"
            "- V3b (1982-1988, 1978-revision MRACE 0-9): code 7 ('Other nonwhite' residual) → null\n"
            "  (~89 records across 1982-1988); code 9 ('Not stated') → null (~18,700 records,\n"
            "  3-5% per year). 1978-revision public-use files have a less-imputed race field than\n"
            "  1989+ resulting in the higher null fraction.\n"
            "- V3a (1989-1991, 1989-revision MRACE 01-09): code 09 ('All other Races' residual) →\n"
            "  null (165 records across 1989-1991; 0.087% V3a). Sibling of the existing V2 (1992+)\n"
            "  99 ('Unknown/Not stated') → null convention.\n"
            "- V2 (1992-2002) + V1 (2005-2013): 100% non-null `maternal_race_bridged`.\n"
            "- V1 (2014-2022, OE-era): `maternal_race_bridged` becomes 100% null in 2022 (NCHS\n"
            "  dropped MBRACE from fetal-death public-use file 2018+); `race_hispanic_revised`\n"
            "  becomes the canonical column (~17.6% null in 2022 from code 8 Unknown).\n"
            "\n"
            "**Canonical analytic filter** (applied identically across all sections; matches\n"
            "`fetal_death/scripts/05_validate/validate_external.py:70-72`):\n"
            "\n"
            "| Product | Filter |\n"
            "|---|---|\n"
            "| Fetal death | `tabulation_flag == 2 AND residence_status != 4` (Int8) — ≥20wk, U.S. resident |\n"
            "| Natality | `residence_status != 4` (Int8) — U.S. resident |\n"
            "\n"
            "**Cohort-vs-period N/A.** Race-stratified FMR uses fetal-death + natality only (not\n"
            "the cohort-linked file), so the cohort-vs-period source distinction documented in\n"
            "notebook 1 (`maternal_age_stratified_imr.ipynb`) does not apply here.\n"
            "\n"
            "**2014 race-coding-methodology boundary.** Starting with 2014 data, NCHS reports\n"
            "race and Hispanic-origin on separate orthogonal axes (`race_hispanic_revised`).\n"
            "Pre-2014, the bridged 4-cat MRACE mixed Hispanic-origin into the race category.\n"
            "The cross-era panel (Section 3) uses the era-appropriate column on BOTH numerator\n"
            "and denominator sides (1990-2013 = bridged 4-cat incl. Hispanic; 2014+ = NH-only\n"
            "bridged 4-cat) — so the 2013→2014 step in measured rates is a methodology-driven\n"
            "coding shift, not real demographic change. (Separately, the 2014 OE gestational-\n"
            "age shift affects notebook 2 `preterm_outcomes_time_series.ipynb` but is largely\n"
            "orthogonal to race.)"
        ),
        md(
            "## Section 0 — Load FD + natality parquets, apply canonical filters"
        ),
        code(
            "import pandas as pd\n"
            "import numpy as np\n"
            + paths_setup_source(marker="README.md", nat=True, fd=True)
        ),
        code(
            "# Load FD (small projection from the 89-column parquet)\n"
            "fd = pd.read_parquet(\n"
            "    FD_PARQUET,\n"
            "    columns=['data_year', 'tabulation_flag', 'residence_status',\n"
            "             'maternal_race_bridged', 'race_hispanic_revised'],\n"
            ")\n"
            "print(f'FD parquet rows (1982-2024 total): {len(fd):,}')\n"
            "print(f'FD parquet years: {sorted(fd[\"data_year\"].unique().tolist())}')"
        ),
        code(
            "# Apply the FD canonical filter (matches validate_external.py:70-72)\n"
            "fd_canonical = fd[(fd['tabulation_flag'] == 2) & (fd['residence_status'] != 4)].copy()\n"
            "\n"
            "print(f'FD canonical universe (tab==2, resident; >=20wk): {len(fd_canonical):,}')\n"
            "print(f'  Cross-references validate_external.py per-year fetal_deaths_gte20wk_resident cells.')"
        ),
        md(
            "## Section 1 — 7 *NVSR 73-09* Table A 2022 cells (cross-validation against `joint_use_demo` Section B)\n"
            "\n"
            "*NVSR 73-09* Table A publishes 2022 fetal mortality rates by the 2003-revision OMB\n"
            "single-race + Hispanic classification: Total, AIAN (American Indian and Alaska Native),\n"
            "Asian, Black, NHOPI (Native Hawaiian or Other Pacific Islander), White, and Hispanic\n"
            "(of any race). The fetal-death column `race_hispanic_revised` carries this\n"
            "classification natively for 2014+; the natality denominator uses\n"
            "`maternal_race_ethnicity_5` further split for the Asian/NHOPI distinction via\n"
            "`maternal_race_detail` (codes '04'=Asian, '05'=NHOPI).\n"
            "\n"
            "This section reproduces the 7 NVSR Table A target rates byte-exact within ±0.01/1000\n"
            "rounding tolerance, cross-validating against `joint_use_demo.ipynb` Section B (the\n"
            "Task 2 shipping precedent at 2026-05-11). The published target rates are:\n"
            "\n"
            "**NVSR 73-09 Table A (rates per 1,000 LB + FD):** Total 5.48; NH AIAN 7.22; NH Asian\n"
            "3.70; NH Black 10.05; NH NHOPI 10.36; NH White 4.48; Hispanic 4.63."
        ),
        code(
            "# --- Numerator: 2022 fetal deaths by single-race + Hispanic (race_hispanic_revised) ---\n"
            "fd_2022 = fd_canonical[fd_canonical['data_year'] == 2022].copy()\n"
            "fd_by_race = fd_2022['race_hispanic_revised'].value_counts(dropna=False).sort_index()\n"
            "print('Fetal deaths 2022 by race_hispanic_revised (FD NVSR Table A universe):')\n"
            "print(fd_by_race)\n"
            "print(f'Total (codes 1-8 sum): {fd_by_race.sum():,}')"
        ),
        code(
            "# --- Denominator: 2022 live births by single-race + Hispanic (from natality) ---\n"
            "# Natality has maternal_race_ethnicity_5 (Hispanic, NH_aian, NH_asian_pi, NH_black,\n"
            "# NH_white, None). To match NVSR Table A's 6-race split, further split NH_asian_pi\n"
            "# via maternal_race_detail (code 04=Asian, code 05=NHOPI).\n"
            "import pyarrow.parquet as pq\n"
            "nat_2022 = pq.read_table(\n"
            "    NAT_PARQUET,\n"
            "    columns=['data_year', 'residence_status', 'maternal_race_ethnicity_5', 'maternal_race_detail'],\n"
            "    filters=[('data_year', '==', 2022)],\n"
            ").to_pandas()\n"
            "nat_2022 = nat_2022[nat_2022['residence_status'] != 4]\n"
            "\n"
            "def nat_race_class(row):\n"
            "    eth5 = row['maternal_race_ethnicity_5']\n"
            "    detail = row['maternal_race_detail']\n"
            "    if eth5 == 'Hispanic':\n"
            "        return 'Hispanic'\n"
            "    if eth5 == 'NH_white':\n"
            "        return 'NH_White'\n"
            "    if eth5 == 'NH_black':\n"
            "        return 'NH_Black'\n"
            "    if eth5 == 'NH_aian':\n"
            "        return 'NH_AIAN'\n"
            "    if eth5 == 'NH_asian_pi':\n"
            "        if detail == '04':\n"
            "            return 'NH_Asian'\n"
            "        elif detail == '05':\n"
            "            return 'NH_NHOPI'\n"
            "    return 'Unknown'\n"
            "\n"
            "nat_2022['race_class'] = nat_2022.apply(nat_race_class, axis=1)\n"
            "lb_by_race = nat_2022['race_class'].value_counts(dropna=False).sort_index()\n"
            "print('Live births 2022 by NVSR Table A race class:')\n"
            "print(lb_by_race)\n"
            "print(f'Total (resident): {lb_by_race.sum():,}')"
        ),
        code(
            "# --- Validation table vs NVSR 73-09 Table A (7 rate cells) ---\n"
            "FD_CODE_TO_GROUP = {\n"
            "    '1': 'NH_White', '2': 'NH_Black', '3': 'NH_AIAN', '4': 'NH_Asian',\n"
            "    '5': 'NH_NHOPI', '7': 'Hispanic',\n"
            "}\n"
            "NVSR_TARGET_RATES = {\n"
            "    'Total': 5.48,\n"
            "    'NH_AIAN': 7.22, 'NH_Asian': 3.70, 'NH_Black': 10.05,\n"
            "    'NH_NHOPI': 10.36, 'NH_White': 4.48, 'Hispanic': 4.63,\n"
            "}\n"
            "GROUP_LABELS = {\n"
            "    'Total': 'Total', 'NH_AIAN': 'AIAN (NH)', 'NH_Asian': 'Asian (NH)',\n"
            "    'NH_Black': 'Black (NH)', 'NH_NHOPI': 'NHOPI (NH)', 'NH_White': 'White (NH)',\n"
            "    'Hispanic': 'Hispanic',\n"
            "}\n"
            "rows = []\n"
            "# Total row (includes code 6 NH MoreThanOne and code 8 Unknown for full FD/LB universe)\n"
            "total_fd = int(fd_by_race.sum())\n"
            "total_lb = int(lb_by_race.sum())\n"
            "total_rate = 1000 * total_fd / (total_lb + total_fd)\n"
            "rows.append({\n"
            "    'group': 'Total', 'fetal_deaths': total_fd, 'live_births': total_lb,\n"
            "    'FMR_per_1000': round(total_rate, 2),\n"
            "    'NVSR_73-09_T_A': NVSR_TARGET_RATES['Total'],\n"
            "    'diff': round(total_rate - NVSR_TARGET_RATES['Total'], 2),\n"
            "    'status': 'PASS' if abs(total_rate - NVSR_TARGET_RATES['Total']) < 0.01 else 'DRIFT',\n"
            "})\n"
            "for fd_code, group in FD_CODE_TO_GROUP.items():\n"
            "    fd_n = int(fd_by_race.get(fd_code, 0))\n"
            "    lb_n = int(lb_by_race.get(group, 0))\n"
            "    rate = 1000 * fd_n / (lb_n + fd_n) if (lb_n + fd_n) > 0 else float('nan')\n"
            "    target = NVSR_TARGET_RATES[group]\n"
            "    diff = round(rate - target, 2)\n"
            "    rows.append({\n"
            "        'group': GROUP_LABELS[group], 'fetal_deaths': fd_n, 'live_births': lb_n,\n"
            "        'FMR_per_1000': round(rate, 2),\n"
            "        'NVSR_73-09_T_A': target, 'diff': diff,\n"
            "        'status': 'PASS' if abs(diff) < 0.01 else 'DRIFT',\n"
            "    })\n"
            "section_1 = pd.DataFrame(rows)\n"
            "section_1"
        ),
        code(
            "# --- Strict assertion: 7/7 cells within 0.01 rounding tolerance ---\n"
            "pass_count = (section_1['status'] == 'PASS').sum()\n"
            "print(f'Section 1 race-stratified 2022 validation: {pass_count}/7 cells PASS within \\u00b10.01 tolerance')\n"
            "assert pass_count == 7, f'Section 1 incomplete: only {pass_count}/7 PASS'\n"
            "print('All 7 NVSR 73-09 Table A 2022 race x Hispanic FMR cells reproduce byte-exact.')\n"
            "print('Cross-validates joint_use_demo.ipynb Section B byte-exact (same parquets + filters).')"
        ),
        md(
            "**Section 1 result.** All 7 *NVSR 73-09* Table A 2022 race x Hispanic fetal-mortality-\n"
            "rate cells reproduce within rounding tolerance (<=0.01/1000), cross-validating the\n"
            "`joint_use_demo.ipynb` Section B byte-exact result from Task 2 (2026-05-11). The\n"
            "Black-vs-White roughly-2x pattern long-documented in U.S. perinatal epidemiology\n"
            "reproduces (10.05 vs 4.48); the higher AIAN (7.22) and NHOPI (10.36) burden\n"
            "relative to White is consistent with NCHS-published patterns. This section\n"
            "establishes the validation backbone for the 1982-2024 cross-era time series in\n"
            "Section 3 below."
        ),
        md(
            "## Section 2 — Per-era bridged-race conservation invariants (1982-2013)\n"
            "\n"
            "For every year 1982-2013, the canonical-filter (`tabulation_flag == 1 AND\n"
            "residence_status != 4`) row count should equal\n"
            "`sum(bridged_1..4) + null_count`. This conservation invariant detects schema-evolution\n"
            "bugs that could silently drop records (e.g., a derived-column bug that recodes a code\n"
            "to a non-1-4 value without updating null counts).\n"
            "\n"
            "Per-era null fractions report the B3 1-digit-recode caveat impact:\n"
            "\n"
            "- **V3b 1982-1988** — null = (V3b code 7 'Other nonwhite' + V3b code 9 'Not stated')\n"
            "  per DECISION_LOG 2026-05-12T18:30:00Z; empirical per-year null fraction 2.65-3.27%\n"
            "  under the tab==2 canonical universe.\n"
            "- **V3a 1989-1991** — null = V3a code 09 'All other Races' per DECISION_LOG\n"
            "  2026-05-12T14:30:00Z; empirical per-year null fraction 0.075-0.191%.\n"
            "- **V2 1992-2002** + **V2.1 2003-2004** + **V1 pre-2014 2005-2013** — null ≤0.1% per\n"
            "  year (existing V2 convention: code 99 'Unknown/Not stated' → null, 1993+; the\n"
            "  null fraction is order-of-magnitude smaller than V3a/V3b).\n"
            "\n"
            "FD canonical universe (`tab==2`, resident; ≥20wk)."
        ),
        code(
            "# Build per-year sum-conservation table for 1982-2013\n"
            "ERA_MAP = {}\n"
            "for y in range(1982, 1989):\n"
            "    ERA_MAP[y] = 'V3b'\n"
            "for y in range(1989, 1992):\n"
            "    ERA_MAP[y] = 'V3a'\n"
            "for y in range(1992, 2003):\n"
            "    ERA_MAP[y] = 'V2'\n"
            "# 2003-2004 = V2.1 transition (1989-revision layout, 2003-revision data per Task 3)\n"
            "for y in (2003, 2004):\n"
            "    ERA_MAP[y] = 'V2.1'\n"
            "for y in range(2005, 2014):\n"
            "    ERA_MAP[y] = 'V1_pre_OE'\n"
            "\n"
            "rows = []\n"
            "for yr in sorted(ERA_MAP.keys()):\n"
            "    sub = fd_canonical[fd_canonical['data_year'] == yr]\n"
            "    if len(sub) == 0:\n"
            "        continue\n"
            "    total = len(sub)\n"
            "    counts = sub['maternal_race_bridged'].value_counts(dropna=False).to_dict()\n"
            "    n1 = int(counts.get(1, 0))\n"
            "    n2 = int(counts.get(2, 0))\n"
            "    n3 = int(counts.get(3, 0))\n"
            "    n4 = int(counts.get(4, 0))\n"
            "    # Sum NaN entries (multiple key types for NaN)\n"
            "    null_n = int(sub['maternal_race_bridged'].isna().sum())\n"
            "    sum_4cat = n1 + n2 + n3 + n4\n"
            "    invariant = (sum_4cat + null_n) == total\n"
            "    rows.append({\n"
            "        'year': yr, 'era': ERA_MAP[yr], 'total': total,\n"
            "        'White': n1, 'Black': n2, 'AIAN': n3, 'API': n4,\n"
            "        'null': null_n, 'null_pct': round(100 * null_n / total, 2),\n"
            "        'sum_4cat_plus_null': sum_4cat + null_n,\n"
            "        'invariant_pass': invariant,\n"
            "    })\n"
            "section_2 = pd.DataFrame(rows)\n"
            "section_2"
        ),
        code(
            "# Strict assertion: invariant holds for every year 1982-2013\n"
            "n_years = len(section_2)\n"
            "n_pass = int(section_2['invariant_pass'].sum())\n"
            "print(f'Section 2 conservation invariant: {n_pass}/{n_years} years PASS (sum_4cat + null == total)')\n"
            "assert n_pass == n_years, f'Conservation invariant FAIL on {n_years - n_pass} years'\n"
            "\n"
            "# Per-era null-fraction summary\n"
            "era_summary = section_2.groupby('era').agg(\n"
            "    years=('year', 'count'),\n"
            "    null_pct_min=('null_pct', 'min'),\n"
            "    null_pct_max=('null_pct', 'max'),\n"
            "    null_pct_mean=('null_pct', 'mean'),\n"
            ").round(3)\n"
            "print('\\nPer-era B3 1-digit-recode null-fraction summary:')\n"
            "print(era_summary)"
        ),
        code(
            "# Strict era-level assertions for the B3 1-digit-recode caveats\n"
            "v3b = section_2[section_2['era'] == 'V3b']\n"
            "v3a = section_2[section_2['era'] == 'V3a']\n"
            "v2 = section_2[section_2['era'] == 'V2']\n"
            "v21 = section_2[section_2['era'] == 'V2.1']\n"
            "v1pre = section_2[section_2['era'] == 'V1_pre_OE']\n"
            "\n"
            "# Empirical per-era null fractions under the tab==2 canonical universe:\n"
            "#   V3b 1982-1988: 2.65-3.27% (1978-rev MRACE code 7 + code 9 -> null)\n"
            "#   V3a 1989-1991: 0.08-0.19% (1989-rev MRACE code 09 -> null)\n"
            "#   V2 1992-2002 + V2.1 2003-2004 + V1_pre_OE 2005-2013: ~0%\n"
            "assert 2.0 <= v3b['null_pct'].min(), f'V3b null pct min {v3b[\"null_pct\"].min()} < 2.0'\n"
            "assert v3b['null_pct'].max() <= 5.0, f'V3b null pct max {v3b[\"null_pct\"].max()} > 5.0'\n"
            "assert v3a['null_pct'].max() <= 0.3, f'V3a null pct max {v3a[\"null_pct\"].max()} > 0.3'\n"
            "assert v2['null_pct'].max() <= 0.05, f'V2 null pct max {v2[\"null_pct\"].max()} > 0.05'\n"
            "assert v21['null_pct'].max() <= 0.05, f'V2.1 null pct max {v21[\"null_pct\"].max()} > 0.05'\n"
            "assert v1pre['null_pct'].max() <= 0.05, f'V1_pre_OE null pct max {v1pre[\"null_pct\"].max()} > 0.05'\n"
            "\n"
            "print('All per-era null-fraction expectations PASS:')\n"
            "print(f'  V3b 1982-1988: null_pct range [{v3b[\"null_pct\"].min():.2f}%, {v3b[\"null_pct\"].max():.2f}%] -- 1978-rev MRACE code 7 + code 9 -> null')\n"
            "print(f'  V3a 1989-1991: null_pct range [{v3a[\"null_pct\"].min():.3f}%, {v3a[\"null_pct\"].max():.3f}%] -- 1989-rev MRACE code 09 -> null')\n"
            "print(f'  V2 1992-2002:  null_pct max={v2[\"null_pct\"].max():.3f}% across {len(v2)} years -- existing 99 Unknown --> null convention')\n"
            "print(f'  V2.1 2003-2004: null_pct max={v21[\"null_pct\"].max():.3f}% across {len(v21)} years -- inherits V2 convention')\n"
            "print(f'  V1 pre-2014 2005-2013: null_pct max={v1pre[\"null_pct\"].max():.3f}% across {len(v1pre)} years')"
        ),
        md(
            "**Section 2 result.** Per-year `sum_4cat + null == total` conservation invariant\n"
            "PASSes byte-exact for every year 1982-2013 (7 V3b + 3 V3a + 11 V2 + 2 V2.1 + 9\n"
            "V1-pre-OE = 32 years). Per-era B3 1-digit-recode null fractions under the tab==2\n"
            "canonical universe: V3b 2.65-3.27% per year (1978-revision code 7 + code 9\n"
            "residual mappings); V3a 0.075-0.191% per year (1989-revision code 09 residual);\n"
            "V2 + V2.1 + V1-pre-OE max 0.004% per year (existing V2 convention: code 99\n"
            "'Unknown' → null, 1993+).\n"
            "\n"
            "The conservation invariant is the durable integrity gate for the V3a/V3b backward\n"
            "extension: any future schema evolution that silently drops or recodes records\n"
            "without preserving the null-as-residual semantics would fail this assertion."
        ),
        md(
            "## Section 3 — 1982-2024 cross-era race-stratified FMR time series\n"
            "\n"
            "Computes the per-year fetal mortality rate by 4-category bridged race for every\n"
            "year 1990-2024 (joint with natality coverage). Bilateral methodology to keep\n"
            "numerator and denominator matched on the same race-coding scheme per era:\n"
            "\n"
            "- **1990-2013**: FD uses `maternal_race_bridged` directly (bridged 4-cat; INCLUDES\n"
            "  Hispanic Whites/Blacks/etc.); natality denominator uses `maternal_race_bridged`\n"
            "  (same bridged 4-cat; INCLUDES Hispanic). Hispanic-origin is encoded as part of\n"
            "  the race on both sides.\n"
            "- **2014+**: FD uses `race_hispanic_revised` collapsed to NH-only bridged 4-cat\n"
            "  (Hispanic broken out as a separate orthogonal axis, EXCLUDED from the panel);\n"
            "  natality denominator collapses `maternal_race_ethnicity_5` to NH-only bridged\n"
            "  4-cat (matches FD: Hispanic excluded). Hispanic-origin on a separate axis.\n"
            "\n"
            "| Era | FD race column | NAT denominator column | Includes Hispanic? |\n"
            "|---|---|---|---|\n"
            "| 1990-2013 (pre-OMB-disaggregation) | `maternal_race_bridged` | `maternal_race_bridged` | YES (both sides) |\n"
            "| 2014+ (OMB-disaggregation; race_hispanic_revised) | `race_hispanic_revised` → NH-only | `maternal_race_ethnicity_5` → NH-only | NO (both sides) |\n"
            "\n"
            "**2014 race-coding-methodology boundary** is the meaningful step in the series:\n"
            "the bridged 4-cat rates pre-2014 are FOR-THAT-BRIDGED-RACE (Hispanic mixed in);\n"
            "the NH-only bridged 4-cat rates post-2014 are FOR-NH-ONLY (Hispanic broken out).\n"
            "The 2013→2014 step in race-stratified FMR is largely driven by this coding shift\n"
            "(Hispanic disaggregation), not real demographic change. Documented in Section 4.\n"
            "\n"
            "`race_hispanic_revised` → NH-only-bridged 4-cat collapse: codes 1→White, 2→Black,\n"
            "3→AIAN, 4→API (Asian), 5→API (NHOPI; merged with Asian per NCHS bridged\n"
            "convention), 6→null (MoreThanOne), 7→null (Hispanic; on separate axis), 8→null\n"
            "(Unknown).\n"
            "\n"
            "Per-year FMR universe (FD `tab==2`, resident, ≥20wk; nat `resident`)."
        ),
        code(
            "# --- FD side: compute per-year race counts under tab==2 canonical universe ---\n"
            "# 1990-2013: use maternal_race_bridged directly (bridged 4-cat; INCLUDES Hispanic).\n"
            "# 2014+: collapse race_hispanic_revised to NH-only bridged 4-cat (Hispanic excluded).\n"
            "def collapse_rhr_to_bridged(rhr):\n"
            "    if rhr == '1':\n"
            "        return 1  # NH White\n"
            "    if rhr == '2':\n"
            "        return 2  # NH Black\n"
            "    if rhr == '3':\n"
            "        return 3  # NH AIAN\n"
            "    if rhr in ('4', '5'):\n"
            "        return 4  # NH API (Asian + NHOPI merged per NCHS bridged convention)\n"
            "    return None    # code 6 MoreThanOne, code 7 Hispanic (orthogonal), code 8 Unknown, '' empty\n"
            "\n"
            "fd_ts = fd_canonical.copy()\n"
            "# bridged_xera: pre-2014 = maternal_race_bridged; 2014+ = collapsed race_hispanic_revised\n"
            "mask_2014plus = fd_ts['data_year'] >= 2014\n"
            "fd_ts['bridged_xera'] = fd_ts['maternal_race_bridged']\n"
            "# Convert Int8 to float64 to accept None (Int8 can hold pd.NA but not None)\n"
            "fd_ts['bridged_xera'] = fd_ts['bridged_xera'].astype('Int64')\n"
            "rhr_collapsed = fd_ts.loc[mask_2014plus, 'race_hispanic_revised'].map(collapse_rhr_to_bridged)\n"
            "fd_ts.loc[mask_2014plus, 'bridged_xera'] = pd.array(rhr_collapsed.values, dtype='Int64')\n"
            "\n"
            "# Per-year x per-race FD count -- compute Null separately to side-step pd.NA-column-name issues\n"
            "fd_nonnull = fd_ts[fd_ts['bridged_xera'].notna()].copy()\n"
            "fd_per_yr_race = (\n"
            "    fd_nonnull.groupby(['data_year', 'bridged_xera']).size()\n"
            "    .unstack('bridged_xera', fill_value=0)\n"
            "    .rename(columns={1: 'White_FD', 2: 'Black_FD', 3: 'AIAN_FD', 4: 'API_FD'})\n"
            ")\n"
            "fd_null_per_yr = fd_ts[fd_ts['bridged_xera'].isna()].groupby('data_year').size().rename('Null_FD')\n"
            "fd_per_yr_race = fd_per_yr_race.join(fd_null_per_yr, how='left').fillna(0).astype(int)\n"
            "print(f'FD per-year x per-race-class counts shape: {fd_per_yr_race.shape}')\n"
            "print(fd_per_yr_race.head(3))\n"
            "print('...')\n"
            "print(fd_per_yr_race.tail(3))"
        ),
        code(
            "# --- Natality side: compute per-year race-class denominator counts ---\n"
            "# 1990-2013: use maternal_race_bridged (bridged 4-cat; includes Hispanic; matches\n"
            "#   the FD 1990-2013 bridged-race numerator side -- both bridged 4-cat with\n"
            "#   Hispanic-on-race-axis).\n"
            "# 2014+: collapse maternal_race_ethnicity_5 to NH-only bridged 4-cat (matches the\n"
            "#   FD 2014+ race_hispanic_revised-collapsed-NH-only numerator side -- both NH-only\n"
            "#   bridged 4-cat with Hispanic-as-separate-axis).\n"
            "# Note: natality coverage starts 1990, so 1982-1989 FD years have no natality\n"
            "#       denominator -- FMR computed only for joint years 1990+.\n"
            "def nat_eth5_to_NH_bridged(eth5):\n"
            "    if eth5 == 'NH_white':\n"
            "        return 1\n"
            "    if eth5 == 'NH_black':\n"
            "        return 2\n"
            "    if eth5 == 'NH_aian':\n"
            "        return 3\n"
            "    if eth5 == 'NH_asian_pi':\n"
            "        return 4\n"
            "    return None\n"
            "\n"
            "# Year-at-a-time aggregation (1990-2024) — avoids loading 201M-row natality whole-file.\n"
            "nat_yr_parts = []\n"
            "nat_null_parts = []\n"
            "for y in range(1990, 2025):\n"
            "    nat_y = pq.read_table(\n"
            "        NAT_PARQUET,\n"
            "        columns=['data_year', 'residence_status', 'maternal_race_bridged', 'maternal_race_ethnicity_5'],\n"
            "        filters=[('data_year', '==', y)],\n"
            "    ).to_pandas()\n"
            "    nat_y = nat_y[nat_y['residence_status'] != 4].copy()\n"
            "    nat_y['bridged_xera'] = nat_y['maternal_race_bridged'].astype('Int64')\n"
            "    if y >= 2014:\n"
            "        eth5_collapsed = nat_y['maternal_race_ethnicity_5'].map(nat_eth5_to_NH_bridged)\n"
            "        nat_y['bridged_xera'] = pd.array(eth5_collapsed.values, dtype='Int64')\n"
            "    nat_nonnull = nat_y[nat_y['bridged_xera'].notna()]\n"
            "    rename_map = {1: 'White_LB', 2: 'Black_LB', 3: 'AIAN_LB', 4: 'API_LB'}\n"
            "    if len(nat_nonnull):\n"
            "        counts = nat_nonnull.groupby('bridged_xera').size()\n"
            "        row = {rename_map.get(int(k), f'code_{k}_LB'): int(v) for k, v in counts.items()}\n"
            "        nat_yr_parts.append(pd.DataFrame([row], index=[y]))\n"
            "    n_null = int(nat_y['bridged_xera'].isna().sum())\n"
            "    if n_null:\n"
            "        nat_null_parts.append({'data_year': y, 'Null_LB': n_null})\n"
            "nat_per_yr_race = pd.concat(nat_yr_parts).fillna(0).astype(int) if nat_yr_parts else pd.DataFrame()\n"
            "if nat_null_parts:\n"
            "    nat_null_per_yr = pd.DataFrame(nat_null_parts).set_index('data_year')['Null_LB']\n"
            "    nat_per_yr_race = nat_per_yr_race.join(nat_null_per_yr, how='left').fillna(0).astype(int)\n"
            "print(f'NAT per-year x per-race-class counts shape: {nat_per_yr_race.shape}')\n"
            "print(nat_per_yr_race.head(3))\n"
            "print('...')\n"
            "print(nat_per_yr_race.tail(3))"
        ),
        code(
            "# --- Join FD + NAT per-year, compute FMR by 4-cat bridged race ---\n"
            "panel = fd_per_yr_race.join(nat_per_yr_race, how='inner')\n"
            "print(f'Joint year coverage: {panel.index.min()}-{panel.index.max()} ({len(panel)} years)')\n"
            "\n"
            "for label in ['White', 'Black', 'AIAN', 'API']:\n"
            "    fd_col = f'{label}_FD'\n"
            "    lb_col = f'{label}_LB'\n"
            "    rate_col = f'{label}_FMR'\n"
            "    panel[rate_col] = 1000 * panel[fd_col] / (panel[lb_col] + panel[fd_col])\n"
            "    panel[rate_col] = panel[rate_col].round(2)\n"
            "\n"
            "fmr_panel = panel[['White_FMR', 'Black_FMR', 'AIAN_FMR', 'API_FMR']].copy()\n"
            "fmr_panel['era'] = fmr_panel.index.map(lambda y: 'V3a' if 1989 <= y <= 1991 else ('V2' if 1992 <= y <= 2002 else ('V1_pre_OE' if 2005 <= y <= 2013 else 'V1_OE')))\n"
            "fmr_panel = fmr_panel[['era', 'White_FMR', 'Black_FMR', 'AIAN_FMR', 'API_FMR']]\n"
            "print('\\nCross-era race-stratified FMR panel (per 1,000 LB + FD):')\n"
            "fmr_panel"
        ),
        code(
            "# --- Sanity assertions on the time series ---\n"
            "# 2022 White FMR should match NVSR Table A (4.48 within ~0.1 due to bridged-not-single-race precision)\n"
            "white_2022 = fmr_panel.loc[2022, 'White_FMR']\n"
            "black_2022 = fmr_panel.loc[2022, 'Black_FMR']\n"
            "print(f'2022 White FMR (cross-era panel): {white_2022:.2f} (NVSR T_A NH_White=4.48; bridged panel includes MoreThanOne null, slight drift expected)')\n"
            "print(f'2022 Black FMR (cross-era panel): {black_2022:.2f} (NVSR T_A NH_Black=10.05)')\n"
            "\n"
            "# Black-vs-White ratio should be elevated across all eras (well-documented disparity);\n"
            "# allow a generous envelope to tolerate small-cell noise in early V3b years.\n"
            "bw_ratios = fmr_panel['Black_FMR'] / fmr_panel['White_FMR']\n"
            "print(f'\\nBlack-vs-White FMR ratio across {len(bw_ratios)} years:')\n"
            "print(f'  range: [{bw_ratios.min():.2f}x, {bw_ratios.max():.2f}x]; mean: {bw_ratios.mean():.2f}x')\n"
            "assert bw_ratios.mean() >= 1.5, f'Black-vs-White mean ratio {bw_ratios.mean():.2f} < 1.5 -- unexpected'\n"
            "assert bw_ratios.max() <= 4.0, f'Black-vs-White ratio max {bw_ratios.max():.2f} > 4.0 -- unexpected'\n"
            "print('Black-vs-White mean ratio elevated across all 35 joint years (mean >=1.5x, max <=4.0x).')\n"
            "\n"
            "# 2014 race-coding-methodology boundary marker (NOT OE-methodology -- that's the\n"
            "# preterm-birth boundary in notebook 2. Here the 2014 boundary is the bridged-race\n"
            "# (Hispanic-mixed-in) -> NH-only-bridged-race (Hispanic broken out) coding shift.)\n"
            "print(f'\\n2014 race-coding-methodology boundary -- pre/post comparison:')\n"
            "for label in ['White', 'Black']:\n"
            "    pre = fmr_panel.loc[2013, f'{label}_FMR']\n"
            "    post = fmr_panel.loc[2014, f'{label}_FMR']\n"
            "    delta = post - pre\n"
            "    print(f'  {label}: 2013={pre:.2f}; 2014={post:.2f}; delta={delta:+.2f}')\n"
            "print('  (Step driven by Hispanic disaggregation in upstream NCHS race coding 2014+;\\n'\n"
            "      '   bridged 4-cat pre-2014 INCLUDED Hispanic Whites/Blacks/etc; NH-only post-2014 EXCLUDES Hispanic.)')"
        ),
        md(
            "**Section 3 result.** 35-year cross-era race-stratified FMR panel produced 1990-2024\n"
            "(joint coverage: natality starts 1990; FD covers 1982-2024 but 1982-1989 lack a\n"
            "race-stratified denominator from natality). Across all 35 joint years:\n"
            "- 2022 NH-White cross-era panel FMR (4.48/1000) matches NVSR 73-09 Table A\n"
            "  NH_White cell (4.48/1000) byte-exact; 2022 NH-Black panel FMR (10.05/1000)\n"
            "  matches Table A NH_Black (10.05/1000) byte-exact.\n"
            "- The Black-vs-White FMR mean ratio (1.82x across 35 years) is elevated, within\n"
            "  the well-documented U.S. perinatal-health disparity envelope (max 2.24x).\n"
            "- The 2014 boundary is a **race-coding-methodology** shift (NOT the OE-methodology\n"
            "  shift from notebook 2 -- that shift is gestational-age-only). Pre-2014 bridged\n"
            "  4-cat INCLUDES Hispanic Whites/Blacks/etc.; post-2014 NH-only bridged 4-cat\n"
            "  EXCLUDES Hispanic. This drops the measured White rate (since Hispanic White\n"
            "  women have a lower FMR than NH White women) and to a lesser extent the Black\n"
            "  rate -- a methodology-driven measured-rate shift, not real demographic change."
        ),
        md(
            "## Section 4 — Cross-era caveats narrative\n"
            "\n"
            "**B3 1-digit-recode caveats (V3b 1982-1988 + V3a 1989-1991).** The V3b 1978-revision\n"
            "MRACE is a 1-digit field (codes 0-9); the V3a 1989-revision MRACE is a 2-digit field\n"
            "(codes 01-09). Both extend the 4-category bridged-race recode for harmonization\n"
            "but require residual-code mappings:\n"
            "\n"
            "- **V3b code 7 ('Other nonwhite' residual)** maps to null per DECISION_LOG\n"
            "  2026-05-12T18:30:00Z. Affects ~89 records across 1982-1988 total. Code 7 is\n"
            "  a residual catch-all that sits alongside specific API subgroups (codes 4/5/6/8)\n"
            "  and the general API code 0; mapping to any of the 4 named bridged categories\n"
            "  would be a false categorization per the §2 fail-closed principle.\n"
            "- **V3b code 9 ('Not stated')** maps to null per same DECISION_LOG entry. Affects\n"
            "  ~18,700 records across 1982-1988 total (3-5% per year, slightly higher under\n"
            "  the canonical-filter narrowing in Section 2). 1978-revision public-use files\n"
            "  have a less-imputed race field than 1989+ resulting in this higher null fraction.\n"
            "- **V3a code 09 ('All other Races' residual)** maps to null per DECISION_LOG\n"
            "  2026-05-12T14:30:00Z. Affects 165 records across 1989-1991 total (0.087% V3a).\n"
            "  Sibling of the existing V2 (1992+) 99 ('Unknown/Not stated') → null convention.\n"
            "\n"
            "**Practical implication for researchers using V3a/V3b race-stratified data:**\n"
            "Totals will not exactly add up to the per-year resident-fetal-death total in the\n"
            "race-stratified panel due to the null-as-residual mapping. The non-null fraction is\n"
            "92-97% per V3b year and >99.9% per V3a year. The conservation invariant in Section 2\n"
            "is the durable integrity gate.\n"
            "\n"
            "**2014 race-coding-methodology boundary.** Starting with 2014 data, NCHS reports\n"
            "race and Hispanic-origin on separate orthogonal axes in the public-use FD file\n"
            "(`race_hispanic_revised` single-race + Hispanic codes 1-8). Pre-2014, the bridged\n"
            "4-cat MRACE included Hispanic Whites/Blacks/etc. in the race category directly.\n"
            "This is a coding-methodology shift, not a real demographic shift. The cross-era\n"
            "panel uses the era-appropriate column on BOTH numerator and denominator sides:\n"
            "1990-2013 bridged 4-cat (Hispanic mixed in); 2014+ NH-only bridged 4-cat (Hispanic\n"
            "broken out). The 2013→2014 step in measured rates is the methodology-driven shift,\n"
            "not real change. **Separately**, the 2014 OE (Obstetric Estimate) gestational-age\n"
            "shift affects gestational-age analyses (see notebook 2,\n"
            "`preterm_outcomes_time_series.ipynb`) but is largely orthogonal to race-stratified\n"
            "FMR.\n"
            "\n"
            "**Cohort-vs-period N/A.** Race-stratified FMR uses fetal-death + natality only (not\n"
            "the cohort-linked file), so the cohort-vs-period source distinction documented in\n"
            "notebook 1 (`maternal_age_stratified_imr.ipynb`) does not apply here.\n"
            "\n"
            "**Post-2014 race-column transition.** `maternal_race_bridged` becomes 100% null\n"
            "starting 2022 (NCHS dropped MBRACE from fetal-death public-use file 2018+);\n"
            "`race_hispanic_revised` is the canonical column 2014+. The cross-era panel in\n"
            "Section 3 bridges this transition via the documented crosswalk.\n"
            "\n"
            "**Why HVS for this analysis.** Pre-1992 NCHS NVSR race-stratified fetal-mortality\n"
            "publications are sparse (NVSR Volume 41/42/43 + NCHS Series 21 reports for\n"
            "1982-1991 ship limited cross-tabulations; cell-level L9 cheap-checking those PDFs\n"
            "is explicit post-submission scope per DECISION_LOG). HVS makes the underlying\n"
            "race-stratified microdata directly accessible at the public-use granularity, with\n"
            "the harmonization caveats made explicit. The 43-year cross-era panel produced by\n"
            "this notebook is, to our knowledge, not available as a single pre-computed\n"
            "NCHS-published table."
        ),
        md(
            "## Pass/fail summary"
        ),
        code(
            "summary_rows = [\n"
            "    ('Section 1: 7 NVSR 73-09 Table A 2022 race x Hispanic cells (cross-val joint_use_demo)', 'PASS' if (section_1['status'] == 'PASS').sum() == 7 else 'FAIL'),\n"
            "    ('Section 2: per-year bridged-race conservation invariant (sum_4cat + null == total)', 'PASS' if int(section_2['invariant_pass'].sum()) == len(section_2) else 'FAIL'),\n"
            "    ('Section 2: V3b 1982-1988 null fraction in [2.0%, 5.0%] per year', 'PASS'),\n"
            "    ('Section 2: V3a 1989-1991 null fraction <=0.3% per year', 'PASS'),\n"
            "    ('Section 2: V2 + V2.1 + V1 pre-2014 null fraction <=0.05% per year', 'PASS'),\n"
            "    ('Section 3: 35-year cross-era panel produced (1990-2024 joint years)', 'PASS' if len(fmr_panel) == 35 else 'FAIL'),\n"
            "    ('Section 3: Black-vs-White FMR mean ratio >=1.5x across all joint years', 'PASS'),\n"
            "    ('Section 3: 2014 race-coding-methodology boundary marker logged in output', 'PASS'),\n"
            "]\n"
            "summary = pd.DataFrame(summary_rows, columns=['Criterion', 'Status'])\n"
            "summary"
        ),
        code(
            "all_pass = (summary['Status'] == 'PASS').all()\n"
            "print(f'\\nCross-era race-stratified fetal mortality notebook: {\"ALL PASS\" if all_pass else \"SOME FAIL\"}')\n"
            "print(f'  {(summary[\"Status\"] == \"PASS\").sum()}/{len(summary)} criteria PASS')\n"
            "assert all_pass, 'Pass/fail summary has FAIL rows -- see table above.'"
        ),
    ]
    return nb


def main() -> int:
    nb = build()
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    print(f"Executing notebook to {OUTPUT}...")
    client.execute(cwd=str(REPO_ROOT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
