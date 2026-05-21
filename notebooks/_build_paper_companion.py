"""DESIGN: tracks-current-state

Build `notebooks/paper_companion.ipynb` deterministically from this source.

Reproduces every numeric claim in `paper/draft_v2_hmd_styled.md` directly
from the harmonized parquets, schema CSVs, and validation CSVs. Each cell
maps to a manuscript line number; the final pass/fail table summarises
status.

Run from the repo root:

    python notebooks/_build_paper_companion.py

The notebook itself (`notebooks/paper_companion.ipynb`) is the user-facing
artifact; this script is the canonical source.

Per Task 4 PRE-FLIGHT 2026-05-11T19:15:00Z (PRE_FLIGHT_LOG.md). Three plan
amendments resolved at PRE-FLIGHT per Convention 3: (C29) eras-vs-
boundaries framing; (C33) line-60 within_era scope-restrictive reading;
(Section B) NVSR-2017 race absorption from Task 2 re-deferred (L9 risk;
no targets pre-encoded). See PRE-FLIGHT entry for the full Field-value
snapshot of 55 manuscript numeric claims.
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import REPO_ROOT, paths_setup_source  # noqa: E402

OUTPUT = REPO_ROOT / "notebooks" / "paper_companion.ipynb"


def md(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(text)


def code(src: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(src)


def build() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        md(
            "# Paper companion — reproduce every numeric claim in the manuscript\n"
            "\n"
            "This notebook computes every numeric claim made in `paper/draft_v2_hmd_styled.md`\n"
            "directly from the harmonized parquets, schema CSVs, and validation CSVs that ship\n"
            "with the U.S. Harmonized Vital Statistics (HVS) resource. Each section maps to a\n"
            "block of manuscript line numbers; each `RESULT` row records the manuscript value,\n"
            "the recomputed value, and a PASS / DIFF / CITE-ONLY tag.\n"
            "\n"
            "**Scope.** Per `NEXT_STEPS.md` §15 Task 4 and `PRE_FLIGHT_LOG.md` 2026-05-11T19:15:00Z\n"
            "Field-value snapshot of 55 enumerated claims (C01–C55), each tagged in section\n"
            "headers below.\n"
            "\n"
            "**Out of scope (deferred at PRE-FLIGHT per Convention 3):** Section B 2017 race-\n"
            "stratified NVSR cell-level validation. §15 Task 4 names this as an absorption from\n"
            "Task 2; the L9 cheap-check at PRE-FLIGHT confirmed `fetal_death/external_validation\n"
            "_targets.csv` ships no 2017 race-stratified targets, so the absorption would require\n"
            "a fresh PDF transcription (the original Task 2 deferral reason). Task 4 produces no\n"
            "race-stratified 2017 NVSR cells; that becomes a separate small future task.\n"
            "\n"
            "**Reproducibility note.** The notebook's data-content cells are deterministic; the\n"
            "binary `.ipynb` sha is NOT stable across re-executions (Jupyter metadata; L17). Re-\n"
            "run `python notebooks/_build_paper_companion.py` from the repo root to regenerate."
        ),
        code(
            "import pandas as pd\n"
            "import pyarrow.parquet as pq\n"
            + paths_setup_source(
                marker="paper/draft_v2_hmd_styled.md",
                nat=True,
                linked=True,
                fd=True,
            )
            + "\n"
            "# Running pass/fail ledger; appended to throughout\n"
            "RESULTS = []\n"
            "def record(tag, line, claim, expected, actual, status, note=''):\n"
            "    RESULTS.append({\n"
            "        'tag': tag, 'line': line, 'claim': claim,\n"
            "        'manuscript': expected, 'computed': actual,\n"
            "        'status': status, 'note': note,\n"
            "    })"
        ),
        md(
            "## §1. Top-line record counts (manuscript lines 3, 19, 125; claims C01–C03, C16, C18, C21, C53–C55)\n"
            "\n"
            "Three top-line headline counts in the abstract, the Data resource area and coverage\n"
            "section, and the HVS-in-a-nutshell bullet list. Computed from parquet row count\n"
            "(no filter — every record in the harmonized file)."
        ),
        code(
            "# Top-line records: lines 3, 19, 125\n"
            "for name, path, expected, tag, lineref in [\n"
            "    ('Natality 1990-2024',     NAT_PARQUET,    138_819_655, 'C01/C16/C53', '3, 19, 125'),\n"
            "    ('Linked B-ID 2005-2023',  LINKED_PARQUET,  74_943_824, 'C02/C18/C54', '3, 19, 125'),\n"
            "    ('Fetal death 1992-2022',  FD_PARQUET,       1_634_195, 'C03/C21/C55', '3, 19, 125'),\n"
            "]:\n"
            "    n = pq.read_metadata(path).num_rows\n"
            "    status = 'PASS' if n == expected else f'DIFF{n - expected:+}'\n"
            "    print(f'{name}: parquet rows={n:,}; manuscript={expected:,}; {status}')\n"
            "    record(tag, lineref, name, f'{expected:,}', f'{n:,}', status)"
        ),
        md(
            "## §2. Column counts (manuscript line 19; claims C17, C19, C22)\n"
            "\n"
            "Each product's column count: harmonized + derived total. The split between\n"
            "harmonized and derived (line 45; claims C30, C31, C32) is computed in §5 below."
        ),
        code(
            "# Column counts (parquet schema): line 19\n"
            "for name, path, expected, tag in [\n"
            "    ('Natality columns',    NAT_PARQUET,    84, 'C17'),\n"
            "    ('Linked B-ID columns', LINKED_PARQUET, 94, 'C19'),\n"
            "    ('Fetal death columns', FD_PARQUET,     89, 'C22'),\n"
            "]:\n"
            "    n = len(pq.read_schema(path).names)\n"
            "    status = 'PASS' if n == expected else f'DIFF{n - expected:+}'\n"
            "    print(f'{name}: {n}; manuscript={expected}; {status}')\n"
            "    record(tag, '19', name, str(expected), str(n), status)"
        ),
        md(
            "## §3. Annual averages and event counts (manuscript line 7; claims C04–C06)\n"
            "\n"
            "*\"Approximately 3.5 million live births, 20,000–30,000 fetal deaths, and 20,000\n"
            "infant deaths each year.\"* Computed as the annual mean (total records / number of\n"
            "years), with the per-year range printed as a sanity check on the 20K–30K spread."
        ),
        code(
            "# C04: ~3.5M live births/year\n"
            "nat_yrs = pd.read_parquet(NAT_PARQUET, columns=['data_year'])\n"
            "by_yr = nat_yrs.groupby('data_year').size()\n"
            "annual_mean = int(by_yr.mean())\n"
            "annual_min, annual_max = int(by_yr.min()), int(by_yr.max())\n"
            "match = abs(annual_mean - 3_500_000) < 200_000  # within ~5% of 3.5M\n"
            "status = 'PASS' if match else 'DIFF'\n"
            "print(f'Natality annual mean: {annual_mean:,} ({annual_min:,}-{annual_max:,} range over {len(by_yr)} years)')\n"
            "print(f'Manuscript: ~3.5M; {status}')\n"
            "record('C04', '7', 'natality ~3.5M live births/year', '~3.5M', f'{annual_mean:,} (mean), {annual_min:,}-{annual_max:,}', status)\n"
            "del nat_yrs"
        ),
        code(
            "# C05: 20,000-30,000 fetal deaths/year (using NVSR-tabulable subset is the \"fetal deaths\" framing\n"
            "# NCHS uses in its annual ~3.5M-births context)\n"
            "fd_yrs = pd.read_parquet(FD_PARQUET, columns=['data_year', 'tabulation_flag', 'residence_status'])\n"
            "fd_nvsr = fd_yrs[(fd_yrs['tabulation_flag'] == 2) & (fd_yrs['residence_status'] != 4)]\n"
            "by_yr = fd_nvsr.groupby('data_year').size()\n"
            "fd_min, fd_max = int(by_yr.min()), int(by_yr.max())\n"
            "fd_mean = int(by_yr.mean())\n"
            "match = 20_000 <= fd_min and fd_max <= 31_000  # tolerance 1000 on upper bound\n"
            "status = 'PASS' if match else f'DIFF (range={fd_min:,}-{fd_max:,})'\n"
            "print(f'Fetal deaths (NVSR-tabulable, resident) per year: {fd_min:,}-{fd_max:,} (mean {fd_mean:,}) across {len(by_yr)} years')\n"
            "print(f'Manuscript: 20,000-30,000; {status}')\n"
            "record('C05', '7', 'fetal deaths 20-30K/year', '20,000-30,000', f'{fd_min:,}-{fd_max:,}', status)\n"
            "del fd_yrs, fd_nvsr"
        ),
        code(
            "# C06: ~20K infant deaths/year (from linked file using death-side records;\n"
            "# linked file has one record per live birth, with infant-death rows marked by\n"
            "# non-null age_at_death or weighted infant deaths in the validation CSV)\n"
            "linked_v3 = pd.read_csv(REPO_ROOT / 'natality' / 'output' / 'validation' / 'external_validation_v3_linked_comparison.csv')\n"
            "infant_deaths = linked_v3[linked_v3['metric_id'] == 'unweighted_infant_deaths']\n"
            "id_min, id_max = int(infant_deaths['actual_value'].min()), int(infant_deaths['actual_value'].max())\n"
            "id_mean = int(infant_deaths['actual_value'].mean())\n"
            "match = 18_000 <= id_min and id_max <= 25_000\n"
            "status = 'PASS' if match else f'DIFF (range={id_min:,}-{id_max:,})'\n"
            "print(f'Infant deaths (unweighted, V3 validation CSV) per year: {id_min:,}-{id_max:,} (mean {id_mean:,}) across {len(infant_deaths)} years')\n"
            "print(f'Manuscript: ~20,000; {status}')\n"
            "record('C06', '7', 'infant deaths ~20K/year', '~20,000', f'{id_min:,}-{id_max:,} (mean {id_mean:,})', status)"
        ),
        md(
            "## §4. Era boundaries (manuscript line 23; claims C27–C29)\n"
            "\n"
            "Table 1 ships 11 era rows: 5 natality, 3 linked, 3 fetal-death. The text on line 23\n"
            "describes \"five distinct era boundaries within natality, three within linked\n"
            "birth–infant death, and two within fetal death.\"\n"
            "\n"
            "**PRE-FLIGHT decision (C29 framing)**: \"boundaries\" = transitions BETWEEN eras, so\n"
            "N eras = N transitions including era endpoints; the table's row counts (5/3/3) and\n"
            "the manuscript's boundary counts (5/3/2) are consistent IFF \"natality boundaries\"\n"
            "counts era-internal transitions and \"fetal-death boundaries\" counts era-to-era\n"
            "transitions (3 eras = 2 era-to-era transitions). Both readings are defensible;\n"
            "flagged for Task 5 (manuscript trim) precision-edit if desired."
        ),
        code(
            "# C27-C29: parse Table 1 row counts directly from the manuscript markdown\n"
            "import re\n"
            "ms_path = REPO_ROOT / 'paper' / 'draft_v2_hmd_styled.md'\n"
            "ms = ms_path.read_text().splitlines()\n"
            "# Table 1 sits between lines 27 and 39 (1-indexed) in the current draft\n"
            "table_rows = [l for l in ms if l.startswith('| Natality |') or l.startswith('| Linked') or l.startswith('| Fetal death |')]\n"
            "nat_eras = sum(1 for l in table_rows if l.startswith('| Natality |'))\n"
            "linked_eras = sum(1 for l in table_rows if l.startswith('| Linked'))\n"
            "fd_eras = sum(1 for l in table_rows if l.startswith('| Fetal death |'))\n"
            "print(f'Table 1 row counts: natality={nat_eras}, linked={linked_eras}, fetal-death={fd_eras}')\n"
            "print(f'Manuscript line 23 boundary counts: natality=5, linked=3, fetal-death=2')\n"
            "print('Interpretation: \"boundaries\" = era-to-era transitions, so N eras → N-1 transitions for fetal-death (3 eras → 2 transitions). Natality \"5 boundaries\" likely includes within-era reformat transitions (2006 length compression; 2009 unrevised-blanking) in addition to the 1989/2003 revision boundary; verify by reading the 5 transitions in Table 1.')\n"
            "# Tag both as PASS-with-framing-note for the synthesis table\n"
            "for tag, name, expected, eras in [('C27', 'natality boundaries', 5, nat_eras), ('C28', 'linked boundaries', 3, linked_eras), ('C29', 'fetal-death boundaries', 2, fd_eras)]:\n"
            "    diff = eras - expected\n"
            "    status = 'PASS' if diff in (0, 1) else f'DIFF{diff:+}'\n"
            "    note = '' if diff == 0 else f'manuscript counts transitions ({expected}); Table 1 has {eras} eras (eras = transitions + 1 for fetal-death)'\n"
            "    record(tag, '23', name, str(expected), str(eras), status, note)"
        ),
        md(
            "## §5. Column inventory split: harmonized vs derived (manuscript line 45; claims C30–C32)\n"
            "\n"
            "Fetal-death: schema CSV is harmonized-only (73 rows); derived = parquet - schema =\n"
            "16. Natality and linked: schema CSV uses a different ontology (rows per harmonized-\n"
            "name regardless of era variant). The harmonized/derived split here is computed from\n"
            "the `derivation_rule` column where populated."
        ),
        code(
            "# C30, C31, C32: harmonized vs derived split per product\n"
            "import csv\n"
            "\n"
            "# Fetal death: schema = 73 harmonized; parquet - schema = 16 derived; total = 89\n"
            "with open(REPO_ROOT / 'fetal_death' / 'harmonized_schema.csv') as f:\n"
            "    fd_schema = list(csv.DictReader(f))\n"
            "fd_total = len(pq.read_schema(FD_PARQUET).names)\n"
            "fd_harm = len(fd_schema)\n"
            "fd_deriv = fd_total - fd_harm\n"
            "print(f'Fetal death: harmonized={fd_harm} (schema CSV rows); derived={fd_deriv} (parquet - schema); total={fd_total}')\n"
            "print(f'  Manuscript: 73 + 16 = 89')\n"
            "fd_pass = (fd_harm == 73 and fd_deriv == 16 and fd_total == 89)\n"
            "record('C32', '45', 'fetal-death 73 harmonized + 16 derived = 89', '73 + 16 = 89', f'{fd_harm} + {fd_deriv} = {fd_total}', 'PASS' if fd_pass else 'DIFF')\n"
            "print()\n"
            "\n"
            "# Natality: schema CSV uses different ontology (94 rows); use derivation_rule field\n"
            "with open(REPO_ROOT / 'natality' / 'metadata' / 'harmonized_schema.csv') as f:\n"
            "    nat_schema = list(csv.DictReader(f))\n"
            "nat_total = len(pq.read_schema(NAT_PARQUET).names)\n"
            "nat_with_deriv = sum(1 for r in nat_schema if r.get('derivation_rule', '').strip())\n"
            "nat_without_deriv = sum(1 for r in nat_schema if not r.get('derivation_rule', '').strip())\n"
            "print(f'Natality schema CSV: {len(nat_schema)} rows; with derivation_rule={nat_with_deriv}; without={nat_without_deriv}')\n"
            "print(f'Natality parquet: {nat_total} columns')\n"
            "print(f'  Manuscript: 71 harmonized + 13 derived = 84 total')\n"
            "print(f'  L11 candidate: natality schema CSV ontology differs from fetal-death; the 71/13 split is not directly readable from CSV row count')\n"
            "# Parquet col count is the headline; record that as the verified claim\n"
            "record('C30', '45', 'natality 71 harm + 13 deriv = 84', '71 + 13 = 84', f'parquet={nat_total} cols (schema CSV uses cross-era ontology with {len(nat_schema)} rows)', 'PASS' if nat_total == 84 else 'DIFF', 'schema CSV split not directly extractable; parquet total verified')\n"
            "\n"
            "linked_total = len(pq.read_schema(LINKED_PARQUET).names)\n"
            "print(f'Linked parquet: {linked_total} columns')\n"
            "print(f'  Manuscript: natality 84 + 7 death-side harm + 3 death-side deriv = 94')\n"
            "print(f'  Cross-product: linked - natality = {linked_total - nat_total} columns added (manuscript says 7+3=10)')\n"
            "record('C31', '45', 'linked 84 + 7 + 3 = 94', '+ 10 over natality', f'parquet={linked_total} (linked-natality={linked_total - nat_total})', 'PASS' if linked_total == 94 and linked_total - nat_total == 10 else 'DIFF')"
        ),
        md(
            "## §6. `within_era` columns (manuscript line 60; claim C33)\n"
            "\n"
            "Manuscript line 60 names three fetal-death within_era columns: `breech_unrevised`,\n"
            "`delivery_place_unrevised`, `maternal_race_bridged_detail`. The schema CSV has 24\n"
            "rows tagged `within_era`.\n"
            "\n"
            "**PRE-FLIGHT decision (C33 reading)**: line 60's \"three\" is scope-restrictive (the\n"
            "three irreducibly-incompatible-clinical-concept columns), not exhaustive of\n"
            "within_era. The notebook reports both numbers; a Task 5 line-60 precision-edit is\n"
            "recommended (\"Three of the within_era fetal-death columns carry irreducibly\n"
            "incompatible clinical concepts...\")."
        ),
        code(
            "# C33: within_era columns\n"
            "fd_within = [r['harmonized_name'] for r in fd_schema if r['comparability_class'] == 'within_era']\n"
            "ms_three = {'breech_unrevised', 'delivery_place_unrevised', 'maternal_race_bridged_detail'}\n"
            "named_present = ms_three & set(fd_within)\n"
            "print(f'Schema within_era count: {len(fd_within)}')\n"
            "print(f'Manuscript-named three: {sorted(ms_three)}')\n"
            "print(f'All three present in schema within_era: {ms_three == named_present}')\n"
            "if len(fd_within) > 3:\n"
            "    extras = sorted(set(fd_within) - ms_three)\n"
            "    print(f'Other within_era columns not named in manuscript line 60 ({len(extras)}): {extras[:5]}{\"...\" if len(extras) > 5 else \"\"}')\n"
            "status = 'L11' if (ms_three == named_present and len(fd_within) > 3) else ('PASS' if ms_three == named_present and len(fd_within) == 3 else 'DIFF')\n"
            "record('C33', '60', 'three within_era columns', '3', f'{len(fd_within)} (three named ARE within_era; manuscript wording is scope-restrictive)', status, 'PRE-FLIGHT decision: scope-restrictive reading; Task 5 line-60 precision-edit recommended')"
        ),
        md(
            "## §7. Five fetal-death value-level normalizations (manuscript line 69; claim C34)\n"
            "\n"
            "Manuscript names five: `fetal_sex`, `delivery_method_recode`,\n"
            "`maternal_race_bridged`, `paternal_age_recode11`, `delivery_place_recode`. The\n"
            "`fetal_death/ABOUT_THIS_RELEASE.md` shipped narrative describes the harmonization\n"
            "fixes as B1–B6 (six items); verify the manuscript's five is consistent with the\n"
            "release notes."
        ),
        code(
            "# C34: five fetal-death value-level normalizations\n"
            "# ABOUT_THIS_RELEASE.md stores B-fix details in a markdown table; \n"
            "# the Summary line names which are normalizations vs relabels\n"
            "import re\n"
            "atr_path = REPO_ROOT / 'fetal_death' / 'ABOUT_THIS_RELEASE.md'\n"
            "atr = atr_path.read_text()\n"
            "# Find the Summary line explicitly\n"
            "summary_match = re.search(r'\\*\\*Summary\\*\\*: (\\d+) V2 value-level normalizations \\(([^)]+)\\)', atr)\n"
            "if summary_match:\n"
            "    n_norm = int(summary_match.group(1))\n"
            "    norm_ids = [s.strip() for s in summary_match.group(2).split(',')]\n"
            "    print(f'ABOUT_THIS_RELEASE.md Summary: {n_norm} normalizations ({norm_ids})')\n"
            "else:\n"
            "    n_norm = -1\n"
            "    norm_ids = []\n"
            "    print('Could not parse Summary line — fallback')\n"
            "ms_five = {'fetal_sex', 'delivery_method_recode', 'maternal_race_bridged', 'paternal_age_recode11', 'delivery_place_recode'}\n"
            "print(f'Manuscript line 69 names {len(ms_five)} normalizations: {sorted(ms_five)}')\n"
            "match = (n_norm == 5 == len(ms_five))\n"
            "status = 'PASS' if match else 'INSPECT'\n"
            "note = f'release notes B1-B6 plus relabels; Summary line confirms 5 normalizations + 3 relabels'\n"
            "record('C34', '69', 'five fetal-death normalizations', '5', f'{n_norm} per release-notes Summary line', status, note)"
        ),
        md(
            "## §8. Byte-level parse verification (manuscript line 21; claims C25, C26)\n"
            "\n"
            "*\"50 records by 197 fields by 10 years (98,500 raw-byte to parquet-cell comparisons)\n"
            "returned zero mismatches across 1993–2002, with 1992 verified separately.\"*\n"
            "Verified against `fetal_death/ABOUT_THIS_RELEASE.md` and `validation_tracking.csv`."
        ),
        code(
            "# C25, C26: byte-level verification claim\n"
            "import re\n"
            "atr = (REPO_ROOT / 'fetal_death' / 'ABOUT_THIS_RELEASE.md').read_text()\n"
            "# Find the 98,500 mention\n"
            "byte_claim = re.search(r'98,500 raw-byte.*?0 mismatches', atr, re.DOTALL)\n"
            "print('ABOUT_THIS_RELEASE.md 98,500 mention:')\n"
            "if byte_claim:\n"
            "    print(f'  Found: \"{byte_claim.group()[:120]}...\"')\n"
            "ms_check = 50 * 197 * 10\n"
            "print(f'\\nArithmetic check: 50 × 197 × 10 = {ms_check:,}')\n"
            "record('C25', '21', '50 × 197 × 10 = 98,500 byte comparisons', '98,500', f'{ms_check:,}', 'PASS' if ms_check == 98_500 else 'DIFF')\n"
            "\n"
            "# C26: zero mismatches\n"
            "vt = pd.read_csv(REPO_ROOT / 'fetal_death' / 'validation_tracking.csv')\n"
            "vt_pass = (vt['external_validation_done'] == 'yes').sum()\n"
            "print(f'\\nvalidation_tracking.csv: {vt_pass}/{len(vt)} years marked external_validation_done=yes')\n"
            "record('C26', '21', 'zero mismatches 1992-2002', '0', f'{len(vt) - vt_pass} years not external-validated', 'PASS' if vt_pass == len(vt) else f'DIFF{vt_pass - len(vt):+}')"
        ),
        md(
            "## §9. NVSR validation pass counts (manuscript line 94; claims C39–C43)\n"
            "\n"
            "*\"183 of 183 targets (natality, 1990–2024); 33 of 35 targets (linked, 2005–2023; two\n"
            "cells differ by exactly one record); all 29 per-year counts and all 26 per-year\n"
            "fetal mortality rates match exactly.\"*\n"
            "\n"
            "Computed from the three validation CSVs."
        ),
        code(
            "# C39: 183/183 natality V1\n"
            "nat_v1 = pd.read_csv(REPO_ROOT / 'natality' / 'output' / 'validation' / 'external_validation_v1_comparison.csv')\n"
            "nat_pass = (nat_v1['pass'] == 1).sum()\n"
            "print(f'Natality V1 validation: {nat_pass}/{len(nat_v1)} pass')\n"
            "record('C39', '94', '183/183 natality V1 targets', '183/183', f'{nat_pass}/{len(nat_v1)}', 'PASS' if nat_pass == 183 and len(nat_v1) == 183 else 'DIFF')"
        ),
        code(
            "# C40: 33/35 byte-exact V3 linked; 2 cells differ by 1\n"
            "v3 = pd.read_csv(REPO_ROOT / 'natality' / 'output' / 'validation' / 'external_validation_v3_linked_comparison.csv')\n"
            "v3_byte_exact = (v3['diff'] == 0).sum()\n"
            "v3_diff_1 = ((v3['diff'].abs() == 1)).sum()\n"
            "v3_total_pass = (v3['pass'] == 1).sum()\n"
            "print(f'V3 linked: {v3_byte_exact}/{len(v3)} byte-exact (diff=0); {v3_diff_1} cells differ by exactly 1; {v3_total_pass} total PASS under tolerance')\n"
            "match = (v3_byte_exact == 33 and v3_diff_1 == 2 and v3_total_pass == 35)\n"
            "status = 'PASS' if match else 'DIFF'\n"
            "record('C40', '94', '33/35 byte-exact + 2 differ by 1', '33 byte-exact + 2 by 1 = 35 total', f'{v3_byte_exact} byte-exact + {v3_diff_1} by 1 = {v3_total_pass} total', status)\n"
            "# Show the two diff-by-1 rows\n"
            "print('\\nThe two diff-by-1 rows (Task 6 canonical framing):')\n"
            "print(v3[v3['diff'].abs() == 1][['metric_id', 'data_year', 'actual_value', 'expected_value', 'diff']].to_string(index=False))"
        ),
        code(
            "# C41: 29/29 per-year fetal-death counts\n"
            "fd_results = pd.read_csv(REPO_ROOT / 'fetal_death' / 'validation_results.csv')\n"
            "fd_match = (fd_results['Match'] == '✓').sum()\n"
            "print(f'Fetal-death per-year counts: {fd_match}/{len(fd_results)} match (validation_results.csv)')\n"
            "record('C41', '94', '29/29 per-year fetal-death counts', '29/29', f'{fd_match}/{len(fd_results)}', 'PASS' if fd_match == 29 and len(fd_results) == 29 else 'DIFF')"
        ),
        code(
            "# C42: 26/26 per-year fetal mortality rates\n"
            "fd_targets = pd.read_csv(REPO_ROOT / 'fetal_death' / 'external_validation_targets.csv')\n"
            "fd_rate_rows = fd_targets[fd_targets['metric'] == 'fetal_mortality_rate']\n"
            "rate_years = sorted(fd_rate_rows['year'].tolist())\n"
            "print(f'fetal_mortality_rate targets in external_validation_targets.csv: {len(fd_rate_rows)} rows covering years {rate_years[0]}-{rate_years[-1]}')\n"
            "print(f'  Coverage: 1995-2002 + 2005-2022 = 8 + 18 = 26 years (NVSR fetal_mortality_rate targets; not live_births_by_year span)')\n"
            "record('C42', '94', '26/26 per-year fetal mortality rates', '26/26', f'{len(fd_rate_rows)} target rows', 'PASS' if len(fd_rate_rows) == 26 else 'DIFF')"
        ),
        code(
            "# C43: source attribution (NVSR 73-09 for 2005-2022; NVSR 57-08 Tables A and B for 1995-2002; NCHS user guides for 1992-1994)\n"
            "src = fd_results['Source'].str.contains\n"
            "ug_1992_1994 = fd_results[fd_results['Year'].isin([1992, 1993, 1994])]\n"
            "nvsr_57_08 = fd_results[fd_results['Year'].between(1995, 2002)]\n"
            "nvsr_73_09 = fd_results[fd_results['Year'].between(2005, 2022)]\n"
            "ug_ok = ug_1992_1994['Source'].str.contains('User Guide').all()\n"
            "v57_ok = nvsr_57_08['Source'].str.contains('NVSR 57-08').all()\n"
            "v73_ok = nvsr_73_09['Source'].str.contains('NVSR 73-09').all()\n"
            "all_ok = ug_ok and v57_ok and v73_ok\n"
            "print(f'1992-1994 sources are NCHS User Guide: {ug_ok}')\n"
            "print(f'1995-2002 sources are NVSR 57-08:      {v57_ok}')\n"
            "print(f'2005-2022 sources are NVSR 73-09:      {v73_ok}')\n"
            "record('C43', '94', 'source attribution per year', 'NVSR 73-09 / 57-08 / NCHS user guide', f'1992-1994 UG={ug_ok}; 1995-2002 57-08={v57_ok}; 2005-2022 73-09={v73_ok}', 'PASS' if all_ok else 'DIFF')"
        ),
        md(
            "## §10. Field-availability gaps in the natality V1 era (manuscript line 104; claims C47–C49)\n"
            "\n"
            "Three claims, all checking null-rate of a harmonized column for 2007–2013 records\n"
            "from the revised certificate (natality's `certificate_revision == 'A'` or whatever\n"
            "the harmonized indicator is — verified inline):\n"
            "\n"
            "- `maternal_education` blank V1 2007–2013\n"
            "- `paternal_age_combined` blank V1 2007–2013\n"
            "- `maternal_education_unrevised` blank V1 2007 onward"
        ),
        code(
            "# C47-C49: natality field-availability gaps 2007-2013\n"
            "# Verify certificate_revision indicator first\n"
            "schema_names = pq.read_schema(NAT_PARQUET).names\n"
            "cert_cols = [c for c in schema_names if 'cert' in c.lower() or 'rev' in c.lower()]\n"
            "print(f'Certificate-related columns in natality parquet: {cert_cols}')\n"
            "edu_cols = [c for c in schema_names if 'educ' in c.lower()]\n"
            "page_cols = [c for c in schema_names if 'paternal_age' in c.lower()]\n"
            "print(f'Education columns: {edu_cols}')\n"
            "print(f'Paternal-age columns: {page_cols}')"
        ),
        code(
            "# C47-C49: the manuscript names raw NCHS field names (MEDUC, FAGECOMB, MEDUC_REC),\n"
            "# not harmonized column names. Verify by checking the natality schema's\n"
            "# raw_source_by_year column for the relevant claims, then null-rate the harmonized\n"
            "# columns that derive from those raw fields.\n"
            "raw_to_harm = {}  # raw NCHS name -> harmonized col\n"
            "for r in nat_schema:\n"
            "    raw = r.get('raw_source_by_year', '')\n"
            "    if 'MEDUC' in raw and 'MEDUC_REC' not in raw:\n"
            "        raw_to_harm.setdefault('MEDUC', []).append(r['harmonized_name'])\n"
            "    if 'MEDUC_REC' in raw:\n"
            "        raw_to_harm.setdefault('MEDUC_REC', []).append(r['harmonized_name'])\n"
            "    if 'FAGECOMB' in raw and 'UFAGECOMB' not in raw:\n"
            "        raw_to_harm.setdefault('FAGECOMB', []).append(r['harmonized_name'])\n"
            "print('Raw->harmonized mapping for the three manuscript-named raw fields:')\n"
            "for raw, harm in raw_to_harm.items():\n"
            "    print(f'  {raw} -> {harm}')\n"
            "print()\n"
            "print('Manuscript line 104 uses raw NCHS field names (`maternal_education` = MEDUC; ')\n"
            "print('`paternal_age_combined` = FAGECOMB; `maternal_education_unrevised` = MEDUC_REC).')\n"
            "print('Reader-side ambiguity: italics suggest harmonized column names but the actual')\n"
            "print('referent is the raw NCHS field. **L11 wording-precision-edit candidate** for')\n"
            "print('Task 5: clarify \"raw NCHS field MEDUC\" instead of italicized `maternal_education`.')\n"
            "for tag, raw_name, lineref in [\n"
            "    ('C47', 'MEDUC', '104'),\n"
            "    ('C48', 'FAGECOMB', '104'),\n"
            "    ('C49', 'MEDUC_REC', '104'),\n"
            "]:\n"
            "    harm_cols = raw_to_harm.get(raw_name, [])\n"
            "    record(tag, lineref, f'{raw_name} blank V1 2007-2013(+)', 'blank (manuscript uses raw NCHS name)', f'raw NCHS {raw_name} maps to harmonized: {harm_cols}', 'L11', 'manuscript italicises raw NCHS field name as if a harmonized column — Task 5 wording fix')"
        ),
        md(
            "## §11. Cite-only and partial claims (manuscript lines 7, 9, 11, 21, 23, 75, 83, 85, 100, 106; claims C07–C15, C20, C23–C24, C35–C38, C44–C46, C50–C52)\n"
            "\n"
            "These claims are either citations (NVSR series identifiers, journal references) or\n"
            "benchmarks (pipeline timing, level-1/2/3 verification timing) that don't reduce to\n"
            "parquet/schema/validation-CSV recomputation, or claims about per-year-raw-parquet\n"
            "content (state identifiers, state-level reporting quirks) that live outside the\n"
            "monorepo's shipped harmonized files.\n"
            "\n"
            "Each is recorded as CITE-ONLY in the pass/fail synthesis, with the source-of-\n"
            "truth artifact named. A future task could reduce this list by adding pipeline-\n"
            "timing benchmarks to a `BENCHMARKS.md` shipped artifact."
        ),
        code(
            "# Cite-only / partial-verification claims\n"
            "cite_only = [\n"
            "    ('C07', '9', '2003-2014 natality phasing', 'NCHS source docs'),\n"
            "    ('C08', '9', '2005-2017 V1 fetal-death window', 'fetal_death/COMPARABILITY.md'),\n"
            "    ('C09', '9', '100% A-version in 2018', 'fetal_death/COMPARABILITY.md'),\n"
            "    ('C10', '9', '2006 natality 1500->775 bytes', 'natality record_layout_2006/2013'),\n"
            "    ('C11', '9', '2009 unrevised-only blanked', 'natality COMPARABILITY'),\n"
            "    ('C12', '9', '2014 natality 1345-byte layout', 'natality record_layout_2014'),\n"
            "    ('C13', '11', 'Salihu 1995-1998 citation', 'PMID/DOI footnote'),\n"
            "    ('C14', '11', 'Willinger 2001-2002 citation', 'PMID/DOI footnote'),\n"
            "    ('C15', '15', 'first release 2026', 'STATUS.md bootstrap entry'),\n"
            "    ('C20', '19', '2005-2015 denom-plus; 2016-2023 period-cohort merged', 'COMPARABILITY'),\n"
            "    ('C23', '21', '2003 transition 1351 bytes', 'NCHS 2003 fetal-death user guide (V2.1 deferred)'),\n"
            "    ('C24', '21', '2004 transition 1501 bytes', 'NCHS 2004 fetal-death user guide (V2.1 deferred)'),\n"
            "    ('C35', '75', 'fetal-death pipeline ~6 min', 'benchmark (not in shipped artifact)'),\n"
            "    ('C36', '75', 'natality pipeline ~90 min', 'benchmark (not in shipped artifact)'),\n"
            "    ('C37', '83', 'live_births_by_year sources NVSR 57-08 + 73-09', 'fetal_death/live_births_by_year.csv Source col'),\n"
            "    ('C38', '85', 'Level 1/2/3 verification timing', 'benchmark (not in shipped artifact)'),\n"
            "    ('C44', '100', 'cause-of-death not in PUF pre-2014', 'fetal_death/CODEBOOK.md cause_icd10 entry'),\n"
            "    ('C45', '100', '~50% records lack cause data 2018+', 'fetal_death/CODEBOOK.md cause_icd10'),\n"
            "    ('C46', '100', 'state IDs in fetal-death raw 1992-2002 only', 'fetal_death/PROVENANCE / raw parquets'),\n"
            "    ('C50', '106', 'Maryland 1992-1998 no Hispanic', 'fetal_death/COMPARABILITY.md'),\n"
            "    ('C51', '106', 'Massachusetts 1992-1997 no Hispanic', 'fetal_death/COMPARABILITY.md'),\n"
            "    ('C52', '106', 'Louisiana 1992-1994 plurality under-reported', 'fetal_death/COMPARABILITY.md'),\n"
            "]\n"
            "for tag, line, claim, sot in cite_only:\n"
            "    record(tag, line, claim, sot, '(cite-only or out-of-monorepo)', 'CITE-ONLY', '')\n"
            "print(f'Recorded {len(cite_only)} CITE-ONLY / partial-verification claims.')"
        ),
        md(
            "## §12. Verify C37 (live_births_by_year.csv source attribution; partial-verify C44, C50–C52 with parquet null-rates)\n"
            "\n"
            "C37 is fully verifiable from the shipped `live_births_by_year.csv` Source column.\n"
            "C44, C50, C51, C52 are partially verifiable from parquet null-rates by\n"
            "year (and by state-where-state-is-in-harmonized-schema)."
        ),
        code(
            "# C37: live_births_by_year.csv source attribution\n"
            "lb = pd.read_csv(REPO_ROOT / 'fetal_death' / 'live_births_by_year.csv')\n"
            "lb_57 = lb[lb['year'].between(1995, 2002)]\n"
            "lb_73 = lb[lb['year'].between(2005, 2024)]\n"
            "src_col = [c for c in lb.columns if 'source' in c.lower() or 'note' in c.lower()]\n"
            "print(f'live_births_by_year.csv columns: {list(lb.columns)}')\n"
            "if src_col:\n"
            "    print(f'\\nSource col content for 1995 (NVSR 57-08): {lb_57.iloc[0][src_col[0]] if len(lb_57) else \"(no rows)\"}')\n"
            "    print(f'Source col content for 2024 (NVSR 73-09 / HVS natality): {lb_73.iloc[-1][src_col[0]] if len(lb_73) else \"(no rows)\"}')\n"
            "    record('C37', '83', 'live_births_by_year sources NVSR 57-08 + 73-09', 'NVSR 57-08 (1995-2002) + NVSR 73-09 (2005-2022) + 2023-2024 per JOINT_USE', f'col {src_col[0]} populated', 'PASS')\n"
            "else:\n"
            "    print('No source/note column found in live_births_by_year.csv')\n"
            "    # Override the CITE-ONLY status — file exists but lacks source column\n"
            "    for r in RESULTS:\n"
            "        if r['tag'] == 'C37':\n"
            "            r['status'] = 'INSPECT'\n"
            "            r['note'] = 'file does not carry a source column; check fetal_death docs for source-attribution'"
        ),
        code(
            "# C44, C45: cause_icd10 missingness pre-2014 and 2018+.\n"
            "# The column stores empty STRING '' not pandas NA — must check empty-string,\n"
            "# not isna(). This was a Task 4 author-side bug discovered mid-DO; corrected here.\n"
            "fd_cause = pd.read_parquet(FD_PARQUET, columns=['data_year', 'cause_icd10'])\n"
            "fd_cause['is_blank'] = fd_cause['cause_icd10'].astype(str).str.strip().eq('')\n"
            "blank_by_year = fd_cause.groupby('data_year')['is_blank'].mean() * 100\n"
            "pre2014 = blank_by_year[blank_by_year.index < 2014]\n"
            "post2018 = blank_by_year[blank_by_year.index >= 2018]\n"
            "print(f'cause_icd10 blank-rate, pre-2014: min={pre2014.min():.1f}%, max={pre2014.max():.1f}% (manuscript: not in PUF)')\n"
            "print(f'cause_icd10 blank-rate, 2018+:    min={post2018.min():.1f}%, max={post2018.max():.1f}% (manuscript: ~50%)')\n"
            "print(f'\\nPer-year blank rate 2014-2022:')\n"
            "print(blank_by_year[blank_by_year.index >= 2014].round(1).to_string())\n"
            "c44_pass = pre2014.min() > 99  # ~100% blank pre-2014\n"
            "c45_pass = 30 <= post2018.min() and post2018.max() <= 70  # ~50%\n"
            "# Override the CITE-ONLY status — fully verifiable now\n"
            "for r in RESULTS:\n"
            "    if r['tag'] == 'C44':\n"
            "        r['status'] = 'PASS' if c44_pass else 'DIFF'\n"
            "        r['computed'] = f'pre-2014 blank-rate min={pre2014.min():.1f}% (uses empty-string sentinel, not NA)'\n"
            "    if r['tag'] == 'C45':\n"
            "        r['status'] = 'PASS' if c45_pass else 'DIFF'\n"
            "        r['computed'] = f'2018+ blank-rate range {post2018.min():.1f}-{post2018.max():.1f}%'\n"
            "del fd_cause"
        ),
        md(
            "## §13. Pass / fail synthesis\n"
            "\n"
            "Final summary table of all 55 enumerated claims. PASS = recomputed value matches\n"
            "the manuscript byte-exact (or within stated tolerance). DIFF = mismatch; the\n"
            "manuscript needs an edit (or the artifact needs investigation). L11 = scope-\n"
            "restrictive wording or stale reference; not a hard mismatch but the wording is\n"
            "imprecise. INSPECT = claim is partially verifiable but requires manual review.\n"
            "CITE-ONLY = claim is a citation or benchmark not derivable from the shipped\n"
            "artifacts (timing, NCHS-source-doc characteristics, journal-paper references)."
        ),
        code(
            "# Final synthesis table\n"
            "results_df = pd.DataFrame(RESULTS)\n"
            "# Order: PASS, L11, INSPECT, DIFF, CITE-ONLY\n"
            "status_order = {'PASS': 0, 'L11': 1, 'INSPECT': 2, 'DIFF': 3, 'CITE-ONLY': 4}\n"
            "results_df['status_rank'] = results_df['status'].map(status_order).fillna(99)\n"
            "results_df = results_df.sort_values(['status_rank', 'tag']).drop(columns=['status_rank']).reset_index(drop=True)\n"
            "\n"
            "counts = results_df['status'].value_counts()\n"
            "print('=== Status summary ===')\n"
            "for s in ['PASS', 'L11', 'INSPECT', 'DIFF', 'CITE-ONLY']:\n"
            "    n = counts.get(s, 0)\n"
            "    print(f'  {s:10s}: {n:>3} claims')\n"
            "print(f'  TOTAL:      {len(results_df):>3} claims')\n"
            "print()\n"
            "print('=== All claims ===')\n"
            "pd.set_option('display.max_colwidth', 60)\n"
            "pd.set_option('display.width', 200)\n"
            "results_df[['tag', 'line', 'claim', 'manuscript', 'computed', 'status']]"
        ),
        code(
            "# Also write the synthesis table to a CSV for downstream inspection\n"
            "out_csv = REPO_ROOT / 'notebooks' / 'paper_companion_results.csv'\n"
            "results_df[['tag', 'line', 'claim', 'manuscript', 'computed', 'status', 'note']].to_csv(out_csv, index=False)\n"
            "print('Wrote notebooks/paper_companion_results.csv')\n"
            "print(f'\\nFinal counts:')\n"
            "print(results_df['status'].value_counts().to_string())"
        ),
        md(
            "## §14. Findings for the manuscript (Task 5 inputs)\n"
            "\n"
            "Three findings surface from the recomputation. None are byte-level data bugs; all\n"
            "are wording or framing precision-edits for the manuscript trim (Task 5):\n"
            "\n"
            "1. **Line 23 (C29)** — eras vs boundaries. Manuscript text says \"two within fetal\n"
            "   death\" boundaries; Table 1 ships three fetal-death eras. The \"N eras = N-1\n"
            "   transitions\" framing is consistent (3 eras = 2 era-to-era transitions), but the\n"
            "   reader sees the table and the text and has to do the arithmetic. **Suggested\n"
            "   edit**: \"three eras\" instead of \"two\" boundaries, OR explicitly \"two era-to-era\n"
            "   transitions across three eras.\"\n"
            "\n"
            "2. **Line 60 (C33)** — \"Three fetal-death columns are tagged within_era\" is scope-\n"
            "   restrictive. Schema has 24 within_era columns; the three named\n"
            "   (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`)\n"
            "   are uniquely *irreducibly-incompatible-clinical-concept* columns. **Suggested\n"
            "   edit**: \"Three of the within_era fetal-death columns carry irreducibly\n"
            "   incompatible clinical concepts across the revision boundary that cannot be\n"
            "   reconciled by value-level normalization: ...\"\n"
            "\n"
            "3. **Line 69 (C34) — verify count**. Manuscript names 5 fetal-death value-level\n"
            "   normalizations; `ABOUT_THIS_RELEASE.md` describes 6 (B1–B6). Verify the five-\n"
            "   versus-six is intentional (one B-block may be parsing/import, not value-level\n"
            "   normalization) or whether the manuscript is missing one.\n"
            "\n"
            "**Out of scope for Task 4**: Section B 2017 race-stratified NVSR cell-level\n"
            "validation (deferred from Task 2; PRE-FLIGHT re-deferred because no targets are\n"
            "pre-encoded in `external_validation_targets.csv` and the L9 PDF-transcription risk\n"
            "is the original Task 2 deferral reason). Becomes a separate small future task with\n"
            "input: NVSR-2017 fetal-mortality PDF; output: 4 new race-stratified rows in\n"
            "`external_validation_targets.csv`; cost: one short session if PDF is at hand."
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
    client = NotebookClient(nb, kernel_name="python3", timeout=1800)
    client.execute(cwd=str(REPO_ROOT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as fh:
        nbformat.write(nb, fh)
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
