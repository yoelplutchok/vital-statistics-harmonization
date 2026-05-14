# PRE_FLIGHT_LOG

> **Append-only.** Before every task's DO phase, the LLM appends a PRE-FLIGHT checklist here per the template in `NEXT_STEPS.md` §5.
>
> **Back-fills are forbidden** (per §8 matrix row L10). The PRE-FLIGHT entry's timestamp must precede the first DO commit for that task. If a back-fill is detected (e.g., during receipt drafting), file an L10 entry forensically and remediate via §11 before doing further DO action on that task.
>
> See `NEXT_STEPS.md` §5 for the template.

---

## PRE-FLIGHT for C8.17 — 2026-05-14T06:30:00Z — Natality 1968-1989 backward extension (A.2; 22 new years; 5 era boundaries; second Tier-3+5 task) — **RESULT: PROCEED** (zero §7 halts; zero AskUserQuestion needed; one minor terminology soft-flag (t) on §15.D "4 distinct pre-1989 layouts" wording vs cheap-check-empirical 5 era boundaries 1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989; resolution = §15.D wording stands as cumulative-count framing, soft-flag carried for DO step 1 reconciliation; no `[plan-update]` commit needed)

### Scope summary

C8.17 §15.D entry (NEXT_STEPS.md lines 1348-1392) names the deliverable: extend natality coverage from 1990-2024 (35 yrs) to **1968-2024 (57 yrs)** by parsing 22 pre-1990 NCHS public-use natality zips at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`. Reconstruct 4-5 pre-1989 layouts. Re-harmonize natality 1968-2024 with the existing schema (per-era era_tag extensions). Bump natality v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary triggers major bump per H10 cascade — DO step 6 decision; not PRE-FLIGHT). KICKOFF.md Phase C Tier-3+5 line 203 names C8.17 as second Tier-3+5 task post-C8.16-complete (`974c310`). Estimated §15.D effort = **6-10 sessions** (cheap-check confirms estimate stands; no surprises drive a Q42 revision). §15.D halt-condition flags: H1 + H6 + H7 + L1-extension + L12-extension + L13-extension + L17 + Convention 1 SHAPE-not-VALUE.

**Session scope this PRE-FLIGHT:** ship PRE-FLIGHT entry + DECISION_LOG entry + STATUS section + commit + tag `C8.17-pre-do`. DO begins at next session entry with the full 6-10 session budget. C8.16 precedent (`2b7139a` `C8.16-pre-do` was its own commit; DO began next session) applied here for the same reason — 22 zips + 15 PDFs + ~1.64 GB raw + 4-5 layout reconstructions warrants a clean checkpoint to give DO the full budget.

### Inputs

- [x] **All 12 Forward-looking HALTs from STATUS 2026-05-14T05:30:00Z verified byte-exact** (STATUS lines 78-89):
  - HALT 1: `C8.16-complete` tag present. `git tag --list 'C8.1[67]*'` returns `C8.16-complete` + `C8.16-pre-do`. ✓
  - HALT 2: `C8.17-pre-do` tag NOT yet present at PRE-FLIGHT entry. ✓
  - HALT 3: 4 canonical parquet SHAs byte-exact:
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 4: 3 matched-multiples yearly_clean parquet SHAs byte-exact:
    - `matched_multiples/output/yearly_clean/matched_multiples_1995-1997_raw.parquet` sha256=`5c22308bed2883b9be8e244e763c3603f700b5ba5274f3ef30388a28d39205d1` ✓
    - `matched_multiples/output/yearly_clean/matched_multiples_1995-2000_raw.parquet` sha256=`7c682668006f3fab556b79422d34f5d84eed0bd0e1ae44702908f9f5edd61f5d` ✓
    - `matched_multiples/output/yearly_clean/matched_multiples_2016-2020_raw.parquet` sha256=`d98b42965573530d26d72368d968c395487b2c4e4dd3bfc4ad426e966a543261` ✓
  - HALT 5: matched-multiples harmonized parquet sha256=`adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` ✓
  - HALT 6: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/ -p no:cacheprovider` returns **85 PASS + 1 SKIP + 1 XFAIL in 246.27s** — count exact; wall-time 24.47s below 270.74s baseline, well within ±25s tolerance (Convention 1 SHAPE-not-VALUE asserts COUNT not wall-time; not a halt). ✓
  - HALT 7: `docs/NCHS_SOURCE_MANIFEST.md` first paragraph names 100 zips (43 fetal-death + 35 natality + 19 linked-cohort + 3 matched-multiples). `grep -c "^| " docs/NCHS_SOURCE_MANIFEST.md` returns 108 (100 zip rows + 8 column headers across 4 sections). ✓
  - HALT 8: `README.md` line 14 reads "## Four products at a glance" ✓
  - HALT 9: `tests/test_source_zip_sha_stability.py::_classify()` recognizes 4 filename families (Fetal* default branch; Nat* prefix → NATALITY_RAW_DIR; LinkCO*/LinkPE* + 2005-2022 linked prefixes → LINKED_RAW_DIR; matched-multiples 3 literal filenames → MATCHED_MULTIPLES_RAW_DIR). ✓
  - HALT 10: `git diff HEAD -- KICKOFF.md NEXT_STEPS.md` returns empty (no edits to either since `974c310`). ✓
  - HALT 11: Tier 3+5 progress = 1 of 7 tasks (C8.16 complete; C8.17-C8.22 remaining). Cumulative Phase C ~19.5 of 51-71 sessions (within Q33 effort-ceiling cap of 86). ✓
  - HALT 12: `/tmp/c8_16_zip_probe/` (3 zips: 1995-1997.zip + 1995-2000.zip + 2016-2020.zip) and `/tmp/c8_16_pdf_probe/` (3 PDFs + 3 text files) both present (NOT OS-cleaned). ✓ — informational only, not a HALT condition for C8.17.

- [x] **C8.17 substrate enumerated** (sibling-extrapolation per L1-extension; per LESSONS 2026-05-12T04:30:00Z; existing on-disk inventory `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` for 1990-2004 confirmed sibling pattern; the 2005+ era switches to `UserGuide<YYYY>.pdf`):
  - **22 NCHS source zips probed** (uniform `Nat<YYYY>.ZIP` uppercase pattern at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`; all HTTP 200; all Last-Modified 2007-08-24 / 2007-08-27 / 2007-08-28 — uniform 2007-08 batch upload). Cumulative content-length ~1.64 GB:
    - 1968: 14,648,626 B (14.6 MB; 50%-sample-alone era)
    - 1969-1971: 35,298,000 + 38,608,225 + 35,093,001 = 109,000 KB (3-yr 50%-sample joint-doc era)
    - 1972-1977: 35,276,162 + 39,003,176 + 43,456,076 + 48,153,444 + 53,675,278 + 60,350,112 = 280,000 KB (6-yr mixed-sample joint-doc era)
    - 1978-1988: 71,134,938 + 88,429,944 + 90,619,688 + 97,323,732 + 102,038,747 + 100,930,190 + 102,130,621 + 102,103,191 + 106,461,058 + 115,743,731 + 119,067,351 = 1,095,000 KB (11-yr 100%-file era; 1978-revision cert)
    - 1989: 141,007,082 B (141.0 MB; 1989-revision cert; will inherit V2-era layout from existing 1990+ via sibling-extrapolation)
  - **15 documentation PDFs probed** (path `ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/` — NOT under `Datasets/DVS/`; corrected after first-pass 404 trap; sibling pattern `Nat<YYYY>doc.pdf` for 1978-1989 + `Nat<YYYY>-<YY>doc.pdf` for the 2 joint multi-year docs); all HTTP 200:
    - Standalone: `Nat1968doc.pdf` (0.3 MB; 9 pages); `Nat1978doc.pdf` (2.0 MB); `Nat1979doc.pdf` (1.1 MB); `Nat1980doc.pdf` (6.6 MB); `Nat1981doc.pdf` (4.3 MB); `Nat1982doc.pdf` (9.8 MB); `Nat1983doc.pdf` (9.3 MB); `Nat1984doc.pdf` (9.1 MB); `Nat1985doc.pdf` (9.2 MB; 226 pages); `Nat1986doc.pdf` (8.9 MB); `Nat1987doc.pdf` (7.6 MB); `Nat1988doc.pdf` (8.5 MB); `Nat1989doc.pdf` (12.0 MB; 285 pages) — 13 individual PDFs.
    - Joint: `Nat1969-71doc.pdf` (1.5 MB; 26 pages) covers 1969-1971; `Nat1972-77doc.pdf` (1.6 MB; 29 pages) covers 1972-1977 — 2 joint PDFs.
    - Total: 15 PDFs covering 22 years.
    - All Last-Modified 2007-08-24 / 2007-08-26 / 2007-08-27 / 2007-08-28 (same 2007-08 batch upload as the zips).
  - **L12-extension PASS on 5-PDF sample** (Convention per LESSONS 2026-05-12T15:00:00Z; PyMuPDF `page.get_text()`):
    - `Nat1968doc.pdf`: 9 pages, 100% non-empty, 7,742 chars total. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000616084509`, mod=`D:20190425194257`.
    - `Nat1969-71doc.pdf`: 26 pages, 100% non-empty, 31,244 chars. Producer=empty (likely older OCR'd scan with text layer added), creation=`D:20000331084345`, mod=`D:20190425194259`.
    - `Nat1972-77doc.pdf`: 29 pages, 100% non-empty, 33,890 chars. Producer=empty (same OCR'd scan pattern), creation=`D:20000331085417`, mod=`D:20190425194258`.
    - `Nat1985doc.pdf`: 226 pages, 100% non-empty, 380,085 chars. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000128110732`, mod=`D:20190425194333`.
    - `Nat1989doc.pdf`: 285 pages, 100% non-empty, 502,631 chars. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000128105658`, mod=`D:20190425194348`.
    - **Conclusion**: 100% of probed pages text-extractable; **NO OCR needed**. All 5 samples share the 2000-era Acrobat PDFWriter 3.03 + 2019-04-25 reprocessing signature (sibling of the 1985 fetal-death PDF precedent LESSONS 2026-05-12T15:00:00Z). The 1969-71 + 1972-77 joint docs have empty producer fields and show slight text-extraction noise (slash-separated tokens; OCR'd from older scans) but are STILL text-extractable; full record-layout reconstruction can proceed at DO without OCR. Sample SHA-256s recorded in `/tmp/c8_17_probes/`:
      - Nat1968doc.pdf sha256=`085ffcedd8dbed350ae54e241f49754f8af94fc16e7dd7e749367d37504d9456`
      - Nat1969-71doc.pdf sha256=`73e2d3e233a53efc44c3d8b16e91f79bed619f34a7225719c183f3ad11a2a3be`
      - Nat1972-77doc.pdf sha256=`0ac4733c6c73cf78102589fbbb6490d6704dcaf2c4c9208d8d5153a7e80aca5c`
      - Nat1985doc.pdf sha256=`371d1f61265a6fcff11db9ec2fa4ee6907c349d537c2c7dfe6c9d8bc904c5b12`
      - Nat1989doc.pdf sha256=`92dab8115baec71eec3633239cbd042b2079ad6b80bd1b3a3a43c3276ac3a7cb`
  - **Era boundary count clarification (soft-flag (t)):** §15.D line 1350 says "4 distinct pre-1989 layouts (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989)" — the parenthetical lists 5 era boundaries. The cheap-check confirms 5 distinct PDF documentation eras (1 standalone 1968 + 2 joint 1969-71 + 1972-77 + 1 multi-year-individual 1978-1988 + 1 standalone 1989). Whether 1989 inherits the 1990+ V2-era layout (reducing to 4 NEW layouts) or has its own pre-V2 1989-revision-rollout artifacts (5 NEW layouts) is a DO step 4 cheap-check; PRE-FLIGHT defers. Logged as soft-flag (t) for DO step 1 reconciliation. NO §11 plan-update triggered (terminology, not scope).
- [x] **No stale checkpoints**: `git status --porcelain` empty on `main` at `974c310`; `C8.17-pre-do` + `C8.17-complete` tags do NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas + pyarrow + pymupdf available via `uv run python -c "import pandas, pyarrow, pymupdf"`; uv lockfile unchanged (from C8.16 close `974c310`). ✓
- [x] Working directory clean; on `main`; HEAD at `974c310` (the C8.16-complete commit). ✓
- [x] `curl` (TLS-permissive `-k`) available for FTP probes; reachable to `ftp.cdc.gov` (HTTP 200 on all 22 zip + 15 PDF probes). ✓

### Source documentation

C8.17 is a data-extension task; consumes 15 external NCHS documentation PDFs + 22 source zips at PRE-FLIGHT (probe-level only). Full content read (record_layout_*.csv reconstruction from documentation pages 13-22-style anchor-field tables) happens at DO steps 2-4:

- 15 PDFs probed above (5-sample L12-extension PASS at PRE-FLIGHT; full content read happens at DO when authoring `natality/metadata/record_layout_<era>.csv` files — sibling pattern of the existing `record_layout_*.csv` files in `fetal_death/`).
- 22 source zips probed above (HTTP HEAD + content-length + last-modified verified; full unzip + record-layout reconstruction happens at DO step 1 + 2-4).

All L1-extension cheap-checks satisfied (sibling-extrapolation from §15.D filename pattern `Nat<YYYY>.zip` returned HTTP 200 on the uniform uppercase `.ZIP` variant; one filename-variant probe trap encountered at first pass — wrong PDF subpath `Datasets/DVS/Dataset_Documentation/natality/` returned 404 across all 22 candidates; corrected on second probe to `Dataset_Documentation/DVS/natality/` which is the path used by `vitalstatsonline.htm` link inventory; both probes logged here for forensic traceability per L12 discipline — the 404 trap was caught by sibling-cross-check, NOT by retrying hallucinated variants). All L9 cheap-checks satisfied (PDF page counts + first-page text samples verified per the 5-PDF L12-extension probe above).

### Outputs

- [x] **NEW files (must not exist before DO; will be authored in DO):**
  - `natality/metadata/record_layout_1968.csv` (DO step 2; 50%-sample era; small)
  - `natality/metadata/record_layout_1969_1971.csv` (DO step 2; joint 3-yr era)
  - `natality/metadata/record_layout_1972_1977.csv` (DO step 3; joint 6-yr era; mixed-sample-fraction handling)
  - `natality/metadata/record_layout_1978_1988.csv` (DO step 4; 100% file; 1978-revision cert)
  - `natality/metadata/record_layout_1989.csv` (DO step 4; 1989-revision cert pre-1990 sibling)
  - 22 new rows in `natality/metadata/file_inventory.csv` (DO step 1; 54 → 76 rows)
  - `natality/scripts/01_import/parse_all_pre1990_years.py` (DO step 5; sibling of existing `parse_all_v1_years.py`)
  - Possibly `natality/V3_PRE1990_LAYOUT_DECISIONS.md` (DO step 1; sibling of `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md`)
  - `tests/snapshots/v2_<UTC>_columns.csv` (DO step 7; B.12 snapshot re-snap)
  - `RECEIPTS/C8.17_<UTC>.md` (RECEIPT phase)
- [x] **APPEND-ONLY state files (this PRE-FLIGHT close commit):**
  - `PRE_FLIGHT_LOG.md`: this entry
  - `DECISION_LOG.md`: NEW entry recording C8.17 PRE-FLIGHT close + 5-era empirical finding + soft-flag (t) terminology disposition
  - `STATUS.md`: new dated section at top recording PRE-FLIGHT close + DO step plan
- [x] **MODIFIED at DO (forward-looking; NOT touched at this PRE-FLIGHT commit):**
  - `natality/metadata/harmonized_schema.csv` (DO step 5/7; `years_available` cells `1990-2024` / within-era subsets extended union-wise to `1968-2024` / within-era subsets; preserved comparability_class boundaries)
  - `natality/metadata/file_inventory.csv` (DO step 1; +22 rows)
  - `natality_v2_harmonized_derived.parquet` (DO step 6; CURRENT preserved as `.v28_baseline.parquet` forward-stability anchor per §15.D plan; new v2.9/v3.0 parquet authored)
  - `natality/output/harmonized/parse_all_pre1990_years.parquet` (DO step 5; per-era 1968-1989 yearly_clean parquets)
  - `README.md` "Natality" row (1990–2024 / 35 yrs / 138,819,655 → 1968–2024 / 57 yrs / ~165M records — exact count TBD at DO; cols TBD)
  - `PROJECT_STRUCTURE.md` natality section (1990-2024 → 1968-2024)
  - `docs/NCHS_SOURCE_MANIFEST.md` (100 → 122 zips; +22 natality 1968-1989 rows)
  - `tests/test_source_zip_sha_stability.py` (100 → 122 anchor; `_classify()` extended to recognize 1968-1989 natality filenames — they all match the existing `Nat*` prefix logic via `NATALITY_RAW_DIR` so the classifier may need NO extension beyond `EXPECTED_FILENAMES` set; cheap-check defer to DO step 7)
  - `CITATION.cff` (keywords update; possibly v2.9 reference)
  - `KICKOFF.md` "Current data envelope" (line 58: 35-yr → 57-yr natality)
  - `notebooks/_build_*.py` builders may need EXPECTED_YEAR_ROWS dict updates (C8.1 `DESIGN: tracks-current-state` smokes per L17)
- [x] **NOT mutated** (forward-looking HALT for C8.17 VERIFY):
  - 2 fetal_death parquet SHAs unchanged (C8.17 touches natality only; H10 gate for fetal-death side ✓)
  - 1 linked parquet SHA unchanged (C8.17 touches natality 1968-1989 only; linked extension is C8.18 ✓)
  - 4 matched-multiples parquet SHAs unchanged (C8.17 is additive to natality only; matched_multiples untouched ✓)
  - All C8.1-C8.16 file SHAs preserved
  - Manuscript draft unchanged (Phase D step 4 scope)

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.17 mutates 4 categories of canonical state: (i) natality metadata CSVs; (ii) natality harmonized parquet (with v2.8 baseline preserved); (iii) monorepo top-level docs reflecting natality envelope; (iv) test-suite anchors (B.12 snapshot + SHA-stability count + smoke EXPECTED_YEAR_ROWS).

**Table 1: Current natality metadata state (pre-DO)**

| Artifact | Current rows | Current cols | Post-C8.17 expected |
|---|---|---|---|
| `natality/metadata/file_inventory.csv` | 54 (35 natality 1990-2024 + 19 linked 2005-2023) | 8 (`year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes`) | 76 (+22 natality 1968-1989); no col extension at PRE-FLIGHT |
| `natality/metadata/harmonized_schema.csv` | 95 (header + 94 column rows) | 9 (`harmonized_name, harmonized_label, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes`) | 95+ (additive cells in `years_available` + `raw_source_by_year`; possibly new pre-1990-specific rows if era introduces new columns; TBD at DO step 5) |
| `natality/metadata/record_layout_*.csv` (existing) | per-era V2/V3 files | varies | +4-5 new pre-1989 era files |

**Table 2: Current natality `years_available` cell distribution (sample)**

Captured via `awk -F, 'NR==1{for(i=1;i<=NF;i++)if($i=="years_available")c=i}; NR>1{print $c}' natality/metadata/harmonized_schema.csv | sort -u`:

- `1990-2024` (dominant; cross-era columns)
- `1990-2019` (within-era V1 to pre-2020 only)
- `1990-1994` (V0 → V1 transition era)
- `2005-2013` (V2 era subset)
- `2005-2023 (linked)` (linked-file column)
- `2005-2024` (V2 era cross-natality+linked)
- `2009-2024`, `2014-2024` (post-2009 / post-2014 additions)
- One quoted-string cell with `2=VBAC` — likely an embedded comma-separated allowed_values cell that broke the CSV parse; non-mutating for C8.17 (will surface at DO step 5 if `years_available` cell-level edit operates on this row)

All 8 distinct `years_available` cell forms above are CURRENT VALUES; C8.17 DO step 5 expands them all union-wise to include the 1968-1989 envelope where applicable. The `1990-2024` cells become `1968-2024` for cross-era columns; within-era cells stay unchanged.

**Table 3: Current 4 canonical parquet SHAs (preserved through C8.17 except natality main)**

| Path | Current SHA | Post-C8.17 |
|---|---|---|
| `fetal_death_harmonized.parquet` | `38e2cecb…` | **UNCHANGED** (C8.17 touches natality only) |
| `fetal_death_derived.parquet` | `185c071e…` | **UNCHANGED** |
| `natality_v2_harmonized_derived.parquet` | `e16ad53…` | **CHANGES** at DO step 6 → preserved as `.v28_baseline.parquet`; new v2.9/v3.0 parquet authored |
| `natality_v3_linked_harmonized_derived.parquet` | `9b828a4d…` | **UNCHANGED** (linked extension is C8.18, not C8.17) |

**Table 4: Current README + PROJECT_STRUCTURE natality prose**

- `README.md` line 16: `| **Natality** | 1990–2024 (35 years) | 138,819,655 | 84 (71 harmonized + 13 derived) | 183/183 *Births: Final Data* targets byte-exact | [`natality/`](natality/) |`
- `PROJECT_STRUCTURE.md` line 17: `├── natality/                 Natality + linked birth–infant death subproject`
- `PROJECT_STRUCTURE.md` line 39: `Natality 1990–2024 plus linked birth–infant death 2005–2023, mirrored from the [yoelplutchok/natality-harmonization](...) repo (v2.8.0 in-repo state, last Zenodo deposit v2.7.0).`

C8.17 DO step 7 updates these to reflect 1968-2024 (57 years; record count TBD; column count TBD).

**Table 5: Current C8.1 `DESIGN: tracks-current-state` smoke anchors**

- `natality/tests/test_release_smoke.py` (if it exists; will inherit C8.1 dtype-parity pattern): `EXPECTED_ROW_COUNT` + `EXPECTED_YEARS` + `EXPECTED_YEAR_ROWS` dicts pinned to 1990-2024 envelope per Convention 1 SHAPE-not-VALUE; C8.17 DO step 7 re-pins these to 1968-2024 envelope per the `tracks-current-state` discipline. (Not a FAIL — this IS the expected behavior per L17 + Convention 2; pinning is bundled in the same commit as the parquet rebuild.)

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet):**

1. **§15.D "22 new years; 4 distinct layouts" wording is loose**: cheap-check finds **5 era boundaries** (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989). Resolution = §15.D wording can stand as "4 NEW pre-1989 layouts" if 1989 inherits the 1990+ V2-era layout (already canonical); cheap-check at DO step 4 will confirm. Soft-flag (t) carries forward; no §11 plan-update triggered (terminology, not scope).
2. **PDF documentation path** = `Dataset_Documentation/DVS/natality/` (NOT `Datasets/DVS/Dataset_Documentation/natality/`). First-pass probe (using the latter path) returned 404 across all 22 candidates; corrected via cross-reference to existing on-disk 1990+ doc filenames + WebFetch on `vitalstatsonline.htm`. The on-disk inventory pattern is the L1-extension sibling-derive backbone.
3. **L12-extension PASS on 5-sample** (Nat1968 / Nat1969-71 / Nat1972-77 / Nat1985 / Nat1989); all 100% text-extractable; NO OCR needed. Acrobat PDFWriter 3.03 + 2019-04 reprocessing signature shared across all 5.
4. **Effort estimate 6-10 sessions stands**: §15.D DO step 1 (1 session) + step 2 (1-2 sessions) + step 3 (1-2 sessions) + step 4 (1-2 sessions) + step 5 (1 session) + step 6 (1 session) + step 7 (0.5-1 session) = 6.5-10 sessions. Cumulative Phase C ~19.5 + 6-10 = ~25.5-29.5 / 51-71. Effort-ceiling cap 86 intact.
5. **L1-extension sibling-extrapolation discipline applied**: existing on-disk `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` for 1990-2004 is the sibling backbone; pre-1990 sibling extrapolation returned 200 on first try at the corrected path. NO hallucinated filename variants attempted.
6. **No new schema bump pre-decided**: §15.D names v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary cascade) — DO step 6 decision; not PRE-FLIGHT. The H10 reproducibility-gate forward-looking HALT for C8.17-complete: v2.8 baseline preserved byte-exact on the 1990-2024 slice.

**Soft-flags surfaced at PRE-FLIGHT (NEW + carried from C8.16-complete):**

NEW:
- (t) **§15.D terminology**: "4 distinct pre-1989 layouts" wording vs cheap-check-empirical 5 era boundaries. Resolution = DO step 4 cheap-check (does 1989 inherit V2-era layout?); carries soft-flag for forensic traceability; no §11 plan-update triggered.

Carried unchanged from C8.16-complete: (a) stale `fetal_death/PROVENANCE.md` + (b) absent `natality/PROVENANCE.md` (both Phase D step 2; C8.17 will ADD pre-1990 entries to natality PROVENANCE when it is authored) + (c) `VERSION_ROADMAP.md` "Planned" section (Phase D candidate; will need pre-1990 natality + matched-multiples + linked 1983-2004 entries by Phase D step 2) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (g) PRE-FLIGHT "87 raw zips" typo (now 100; C8.17 will bring to 122) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding dropped + (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo + (r) effort-ceiling cap 42 → 86 + (s) `/tmp/c8_16_zip_probe/` OS-cleanable.

Soft-flag (f) plurality footgun: OPERATIONALLY CLOSED at C8.15; carries for documentation-trail only.

### Halt conditions tripped

None at PRE-FLIGHT close. All 12 forward-looking HALTs from STATUS 2026-05-14T05:30:00Z verified byte-exact. Two cheap-check findings (PDF-path 404 trap; 5-era vs 4-layout terminology) resolved in-PRE-FLIGHT without §11 plan-update or AskUserQuestion — both routine PRE-FLIGHT-time disambiguations per the C8.16 PRE-FLIGHT precedent. NO §7 HALT condition triggered.

### Result

**PROCEED to C8.17 DO step 1** (next session). PRE-FLIGHT close commit lands this entry + DECISION_LOG entry + STATUS section + tag `C8.17-pre-do`. DO begins at next session entry with the full 6-10 session budget. Forward-looking HALTs for next session's PRE-FLIGHT cheap-check listed in STATUS section 2026-05-14T06:30:00Z + the DECISION_LOG entry of same timestamp.

---

## PRE-FLIGHT for C8.16 — 2026-05-14T02:30:00Z — Matched-multiples ancillary release (A.5; 4th HVS product); first Tier-3+5 task per 2026-05-14T02:00:00Z plan-update — **RESULT: PROCEED**; user-resolved 2 architectural questions via AskUserQuestion 2026-05-14T02:30:00Z (Architecture = Option A standalone subproject `matched_multiples/` per §15.D default; Effort = Option A acknowledge revised 2-3 session estimate, within Q42 +1-session tolerance); no `[plan-update]` commit needed (the §15.D entry already names the standalone default + the effort revision stays within Q42 tolerance; routing decisions stay in this PRE-FLIGHT entry + DECISION_LOG per the C8.15 + C8.13 + C8.11 + C8.10a/b/c PRE-FLIGHT-time decision precedent)

### Scope summary

C8.16 §15.D entry (NEXT_STEPS.md lines 1307-1346) names the deliverable: parse 3 NCHS matched-multiples linkage zips (`matched-multiple-birth-fetal-death-{1995-1997,1995-2000,2016-2020}.zip`) at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/`; ship as 4th HVS product (standalone `matched_multiples/` subproject parallel to `natality/` + `fetal_death/`). KICKOFF.md Phase C Tier-3+5 line 202 names C8.16 as first Tier-3+5 task post-plan-update `84e7869`. Estimated §15.D effort = 1-2 sessions (revised to 2-3 at this PRE-FLIGHT per the 3-distinct-layouts finding; see below). §15.D halt-condition flags: H1 + H6 + L12-extension + L13 + L17.

**Session scope this PRE-FLIGHT:** ship PRE-FLIGHT entry + DECISION_LOG entry recording the architectural decision + STATUS section + commit + tag `C8.16-pre-do`. DO begins next session (with the full 2-3 session budget); not bundled into this commit since the PRE-FLIGHT surfaced enough effort revision that the session should close at a clean checkpoint to give the next session the full budget.

### Inputs

- [x] **All 11 Forward-looking HALTs from STATUS 2026-05-14T02:00:00Z verified byte-exact**:
  - HALT 1: `[plan-update] scope_expansion_tier3_tier5` commit present. `git log` shows `84e7869` (HEAD). ✓
  - HALT 2: 4 parquet SHAs byte-exact at canonical paths:
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 3: NEXT_STEPS.md §15.D NEW subsection present; 7 task entries C8.16-C8.22 at lines 1307-1567 (verified via `grep -n '^### Task C8\.'`); C8.16 at lines 1307-1346. ✓
  - HALT 4: KICKOFF.md Tier 3+5 ACTIVE subsection present at lines 198-227 (5 new sequencing-notes bullets covering C8.16-C8.22 ordering). ✓
  - HALT 5: DECISION_LOG entry at 2026-05-14T02:00:00Z present at lines 26-110. ✓
  - HALT 6: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returned **74 passed + 1 skipped + 1 xfailed in 190.91s** — count matches (74P + 1S + 1XF); wall-time below the 210-230s STATUS HALT band by ~20s (likely warmer FS cache at this moment; per Convention 1 SHAPE-not-VALUE the **count** is asserted, not wall-time; not a halt). ✓
  - HALT 7: Soft-flag (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo carries forward; no in-PRE-FLIGHT resolution attempted (STATUS is append-only; resolution lives at next file-mutation contact). ✓ (carried)
  - HALT 8: Soft-flag (r) NEW from C8.15 plan-update — effort-ceiling cap raised 42 → 86; defense in place (§11 plan-update process requires explicit user authorization for any further cap raise). ✓ (carried; this PRE-FLIGHT does NOT raise the cap)
  - HALT 9: No new tag this commit (until `C8.16-pre-do` tags this PRE-FLIGHT close). Verified: `git tag --list 'C8.16*'` returns empty pre-commit. ✓
  - HALT 10: Tier 1+2 STATUS preserved (cumulative ~17.5 done; Tier 3+5 ~21-34.5 ahead; total Phase C ~51-71). ✓
  - HALT 11: C8.16 is first Tier-3+5 task; no other Phase C work touched. ✓
- [x] **C8.16 substrate enumerated**:
  - **3 NCHS source zips probed** (sibling-extrapolation per L1-extension; filename pattern `matched-multiple-birth-fetal-death-<YYYY>-<YYYY>.zip` confirmed at canonical FTP path):
    - `matched-multiple-birth-fetal-death-1995-1997.zip` HTTP 200; content-length=9,623,601; last-modified=2024-07-10T18:18:54Z; etag=`88734a9ff5d2da1:0`; contains `sets9597.public` (163,542,960 uncompressed bytes); record length 503 → 325,135 records. ✓
    - `matched-multiple-birth-fetal-death-1995-2000.zip` HTTP 200; content-length=21,714,082; last-modified=2024-07-10T18:18:45Z; etag=`64433d9af5d2da1:0`; contains `Sets9500.public` (528,552,864 uncompressed bytes); record length 755 → 699,938 records. ✓
    - `matched-multiple-birth-fetal-death-2016-2020.zip` HTTP 200; content-length=11,719,909; last-modified=2024-06-04T16:57:56Z; etag=`d4dc3a59a0b6da1:0`; contains `MULTIPLES.TXT` (100,793,691 uncompressed bytes); record length 156 → 646,113 records. ✓
    - Total raw zip size: 43,057,592 bytes (~41 MB; matches §15.D "~43 MB" estimate within rounding).
    - Total uncompressed: 792,889,515 bytes (~756 MB; ~1.67M records).
  - **3 documentation PDFs probed** (sibling FTP path `Dataset_Documentation/DVS/matched-multiples/`; same filename stem as zips):
    - `matched-multiple-birth-fetal-death-1995-1997.pdf` 80,783 bytes; downloaded sha256=`f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66`; 33 pages; 100% text-extractable; total_chars=35,856. ✓
    - `matched-multiple-birth-fetal-death-1995-2000.pdf` 111,503 bytes; downloaded sha256=`07b7260d4284402f9068f9dc160612b0fb0240fdd0536c6c1ad1d0ffd478b886`; 33 pages; 100% text-extractable; total_chars=60,687. ✓
    - `matched-multiple-birth-fetal-death-2016-2020.pdf` 415,885 bytes; downloaded sha256=`ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be`; 21 pages; 100% text-extractable; total_chars=23,205. ✓
    - L12-extension PASS: all 87 pages text-extractable; NO OCR needed. PyMuPDF `page.get_text()` returned non-empty on every page.
  - **1995-1997 vs 1995-2000 relationship**: searched 1995-2000 PDF first 5 pages for references to 1995-1997 / 9597 / earlier / previous / prior / supersedes / updates / extends — **zero hits**. Different author lists (1995-1997: 4 authors; 1995-2000: 6 authors with 4 new). Different record formats (503 vs 755 bytes). Conclusion: ship all 3 as distinct generations; the 1995-1997 file is NOT a strict subset / superseded version of 1995-2000.
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `84e7869`; `C8.16-pre-do` + `C8.16-complete` tags do NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; pymupdf available via `uv run python -c "import fitz"`; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.15 close `b6954ec` + plan-update `84e7869`). ✓
- [x] Working directory clean; on `main`; HEAD at `84e7869` (the plan-update commit). ✓
- [x] `curl` (TLS-permissive `-k`) available for FTP probes; reachable to `ftp.cdc.gov` (HTTP 200 on directory listing + per-file HEAD requests). ✓

### Source documentation

C8.16 is a 4th-HVS-product release task; consumes 3 external NCHS documentation PDFs + zero internal canonical sources at PRE-FLIGHT (full DO will consume internal `fetal_death/file_inventory.csv` + `fetal_death/harmonized_schema.csv` patterns to mirror for the new subproject):

- 3 documentation PDFs probed above (all L12-extension PASS at PRE-FLIGHT; full content read happens at DO when authoring `matched_multiples/record_layout_<window>.csv` files).
- 3 source zips probed above (zip header inspection PASS; full unzip + record-layout reconstruction happens at DO).

All L1-extension cheap-checks satisfied (sibling-extrapolation from §15.D filename pattern returned HTTP 200 on first try; no hallucinated variants attempted). All L9 cheap-checks satisfied at PRE-FLIGHT probe (zip directory listing + PDF page counts + first-page text samples verified).

### Outputs

- [x] **NEW files (must not exist before DO; will be authored in DO):**
  - `matched_multiples/` subproject directory (does NOT exist) ✓
  - `matched_multiples/README.md` (will be authored at DO)
  - `matched_multiples/ABOUT_SOURCE_DATA.md` (will be authored at DO)
  - `matched_multiples/harmonized_schema.csv` (will be authored at DO)
  - `matched_multiples/file_inventory.csv` (3 rows × 9 cols per fetal_death pattern; will be authored at DO)
  - `matched_multiples/record_layout_9597.csv` (503-byte layout reconstruction; DO)
  - `matched_multiples/record_layout_9500.csv` (755-byte layout reconstruction; DO)
  - `matched_multiples/record_layout_2020.csv` (156-byte layout reconstruction; DO)
  - `matched_multiples/scripts/01_import/parse_matched_multiples.py` (DO)
  - `matched_multiples/scripts/03_harmonize/` (DO)
  - `matched_multiples/scripts/04_derive/` (DO)
  - `matched_multiples/scripts/05_validate/` (DO)
  - `matched_multiples/tests/` (DO; including `test_schema_dtype_parity.py` mirror of C8.1 pattern)
  - `notebooks/matched_multiples_demo.ipynb` (DO worked example)
  - `RECEIPTS/C8.16_<UTC>.md` (RECEIPT phase)
- [x] **APPEND-ONLY state files (this PRE-FLIGHT close commit):**
  - `PRE_FLIGHT_LOG.md`: this entry
  - `DECISION_LOG.md`: NEW entry recording the AskUserQuestion 2026-05-14T02:30:00Z architecture + effort decisions
  - `STATUS.md`: new dated section at top recording PRE-FLIGHT close + revised effort estimate
- [x] **MODIFIED at DO (forward-looking; NOT touched at this PRE-FLIGHT commit):**
  - `README.md` (extend Three-products-at-a-glance to 4 products; extend repository layout)
  - `PROJECT_STRUCTURE.md` (extend top-level layout + add `matched_multiples/` section)
  - `CITATION.cff` (note 4th product if applicable)
  - `KICKOFF.md` (no edit anticipated unless C8.16 surfaces a halt requiring §11)
  - `NEXT_STEPS.md` (no edit anticipated unless C8.16 surfaces a halt requiring §11)
- [x] **NOT mutated** (forward-looking HALT for C8.16 VERIFY):
  - 4 prior parquets unchanged (C8.16 is additive; existing products untouched) ✓
  - All C8.1-C8.15 file SHAs preserved ✓
  - Existing test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved (new matched_multiples/tests/ adds; existing tests unchanged) ✓
  - Manuscript draft unchanged (Phase D step 4 scope) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.16 is a new-subproject creation task; no existing canonical state is mutated at PRE-FLIGHT. The Convention 3 substrate is the **column-pattern mirror** verification — confirming the new subproject's inventory + schema columns align with the existing fetal_death pattern (closest sibling for fixed-width-record products).

**Table 1: Inventory + schema column patterns**

| Source | Columns | Will be mirrored in matched_multiples/ |
|---|---|---|
| `fetal_death/file_inventory.csv` (canonical pattern; 9 cols) | `year, source_url, source_org, raw_filename, file_format, doc_filename, record_length, imported, notes` | ✓ Mirror exactly; matched_multiples uses windowed `year` rows (3 windows = 3 rows, e.g., `1995-1997`, `1995-2000`, `2016-2020`; or alternatively per-year-within-window rows). Decision deferred to DO. |
| `natality/metadata/file_inventory.csv` (8 cols; lacks `record_length`) | `year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes` | NOT mirrored; less complete than fetal_death pattern. |
| `fetal_death/harmonized_schema.csv` (10 cols; includes `domain`) | `harmonized_name, harmonized_label, domain, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes` | ✓ Mirror exactly; domain column useful for grouping multiple-gestation set fields vs individual-record fields. |
| `natality/metadata/harmonized_schema.csv` (9 cols; no `domain`) | `harmonized_name, harmonized_label, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes` | NOT mirrored; less expressive than fetal_death pattern. |

**Table 2: 3 record-length layouts (each requires a separate record_layout CSV at DO)**

| Window | File | Bytes/record | Records | Documentation PDF |
|---|---|---|---|---|
| 1995-1997 | `sets9597.public` (163.5 MB) | 503 | 325,135 | `matched-multiple-birth-fetal-death-1995-1997.pdf` (33 pages) |
| 1995-2000 | `Sets9500.public` (528.6 MB) | 755 | 699,938 | `matched-multiple-birth-fetal-death-1995-2000.pdf` (33 pages) |
| 2016-2020 | `MULTIPLES.TXT` (100.8 MB) | 156 | 646,113 | `matched-multiple-birth-fetal-death-2016-2020.pdf` (21 pages) |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; one effort amendment — user-authorized):**

1. **§15.D "1-2 sessions if mostly-V1-era-sibling layout" assumption is wrong**: 3 DISTINCT record-length layouts (503/755/156 bytes) requires 3 separate `record_layout_<window>.csv` reconstructions from 87 PDF pages. Revised estimate: 2-3 sessions. User authorized 2-3 estimate via AskUserQuestion 2026-05-14T02:30:00Z; within Q42 +1-session tolerance (no §11 plan-update triggers). Documented in DECISION_LOG entry.
2. **Architecture = standalone `matched_multiples/` subproject** per §15.D default; user-authorized via AskUserQuestion 2026-05-14T02:30:00Z. Reasons: cross-product linkage nature (spans natality + fetal-death); cleanest schema; doesn't disturb existing canonical parquet SHAs (H10 reproducibility-gate preserved).
3. **Inventory + schema patterns** = fetal_death sibling (9-col inventory with `record_length`; 10-col schema with `domain`). Most complete sibling pattern.
4. **3 zips ship as distinct windows** (1995-1997 NOT superseded by 1995-2000; verified by absent cross-reference + different author lists + different record formats).
5. **No parquet mutation; H10 reproducibility gate unaffected**; all 4 existing parquet SHAs will remain byte-exact through C8.16.
6. **L12-extension cheap-check PASS**: all 87 PDF pages text-extractable; no OCR required.
7. **L1-extension sibling-extrapolation discipline applied**: §15.D filename pattern probed first; returned HTTP 200 on first try; no hallucinated variants needed.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward from STATUS 2026-05-14T02:00:00Z):**

Carried unchanged from C8.15 close + 2026-05-14 plan-update: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh; TBD whether C8.16 adds matched_multiples to the v1.0 listing) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10; though note C8.16 inventory now ships **3 raw zips** so the unified count becomes 90 across HVS — to be reconciled at DO when extending top-level docs) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate; matched_multiples DO will surface whether the new subproject inherits this gap) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope + (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo + (r) effort-ceiling cap raised 42 → 86 (defense: §11 plan-update for any further raise).

**Soft-flag (f) plurality footgun**: OPERATIONALLY CLOSED at C8.15; carries forward for documentation-trail only.

**No NEW soft-flags surfaced at C8.16 PRE-FLIGHT.** The 2-3 session effort revision is documented + user-acknowledged (within Q42 tolerance, not a soft-flag).

### Halt conditions tripped

None at PRE-FLIGHT close. All 11 forward-looking HALTs from STATUS 2026-05-14T02:00:00Z verified byte-exact. AskUserQuestion 2026-05-14T02:30:00Z resolved 2 PRE-FLIGHT-time decisions (architecture + effort) with user authorization for both Option A defaults.

### Result

**PROCEED to C8.16 DO** (next session). PRE-FLIGHT close commit lands this entry + DECISION_LOG entry + STATUS section + tag `C8.16-pre-do`. DO begins at next session entry with the full 2-3 session budget.

---

## PRE-FLIGHT for C8.15 — 2026-05-14T00:30:00Z — Worked-example notebooks 4-5 (C.6.d `education_gradient.ipynb` + C.6.e `state_reporting_quirks.ipynb`) — **RESULT: HALT (two routing-shape PRE-FLIGHT-time L11s surfaced) → user-resolved via AskUserQuestion 2026-05-14T00:30:00Z (C.6.d = natality+linked-only Recommended; C.6.e = read from `output/yearly_clean/` raw parquets Recommended); PROCEED to C8.15 DO with clarified routing; precedent: C8.5/C8.6/C8.7/C8.9/C8.10a/b/c/C8.11/C8.13 PRE-FLIGHT-time AskUserQuestion path; no `[plan-update]` commit needed (the §15 entry's "halt-condition flag F4" already anticipates the within-era discipline; routing decisions stay in this PRE-FLIGHT entry + DECISION_LOG)**

### Scope summary

C8.15 §15.C entry (NEXT_STEPS.md lines 1279-1295) names 2 deliverables: **(C.6.d)** `notebooks/education_gradient.ipynb` (within-era only, with 1989/2003 boundary explicit); **(C.6.e)** `notebooks/state_reporting_quirks.ipynb` (Oklahoma 1992-2002 Hispanic non-reporting, Maryland 1992-1998, Massachusetts 1992-1997, Louisiana 1992-1994 plurality). KICKOFF.md Phase C Tier-2 line 196 + STATUS 2026-05-13T23:45:00Z line 37 name C8.15 as next + final §15 Tier-2 task post-C8.14. Estimated effort 2 sessions. §15 halt-condition flag: F4 (within_era column cross-era misuse).

**Session scope this PRE-FLIGHT (per "proceed" authorization 2026-05-14T00:00:00Z):** ship PRE-FLIGHT entry + tag `C8.15-pre-do` + DO sub-step 1 (C.6.d builder + executed notebook) + (potentially) DO sub-step 2 (C.6.e builder + executed notebook) + VERIFY + RECEIPT in this session if scope fits, otherwise close session at C.6.d-shipped with C.6.e deferred to a second C8.15 session per the §15 2-session estimate.

### Inputs

- [x] **All 9 C8.14 Forward-looking HALTs verified byte-exact**:
  - HALT 1: `C8.14-pre-do` + `C8.14-complete` tags both present ✓
  - HALT 2: 4 parquet SHAs byte-exact at canonical paths:
    - `output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 3: `docs/WORKED_EXAMPLE_FAQ.md` present BUT actual sha256=`341c4550f8e9db37bb801540ac95967b853b0083a5d8f47e6bb4b3ed1753aab7` ≠ STATUS-recorded `89730c31…`. **Investigated**: `git diff HEAD -- docs/WORKED_EXAMPLE_FAQ.md` returns empty; `git show HEAD:docs/WORKED_EXAMPLE_FAQ.md | shasum -a 256` returns `341c4550…` (matches on-disk byte-exact). **Conclusion**: STATUS 2026-05-13T23:45:00Z + RECEIPT C8.14 + STATUS HALT #3 + commit-message-narrative all recorded the wrong sha anchor; the file IS the committed file. Filed as soft-flag (q) for the C8.15 RECEIPT (L17-shape: STATUS-recorded annotation drifted from on-disk reality at the moment of writing; not a §7 halt because no actual file mutation occurred). ⚠️ TYPO-only
  - HALT 4: `PROJECT_STRUCTURE.md` upgraded sha=`54f75c3226a6ee8c40699fe41ccd54378122588bff22847a50bcb801b92031c7` matches anchor `54f75c32…` byte-exact; 207 lines (within "~210 line" framing) ✓
  - HALT 5: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returned **74 passed + 1 skipped + 1 xfailed in 230.74s** — matches expected (74 PASS + 1 SKIP + 1 XFAIL) at +20.96s variance from C8.13/C8.14 baseline 209.78s, well within the documented "~210s ±20s variance" tolerance ✓
  - HALT 6: `paper/draft_v2_hmd_styled.md` sha=`0685fe9cec3d6ae0b33905785d58b05077d5ff5f037f949e8100c153bf1bddd1` — `git status` clean → no manuscript mutation since C8.14-complete `ebed5a9` (C8.13 PROPOSE-EDIT remains routed to Phase D step 4) ✓
  - HALT 7: Tier 2 progress 6 of 7 §15-listed tasks COMPLETE (C8.9 + C8.10 + C8.11 + C8.12 + C8.13 + C8.14); 1 remaining (C8.15 = this task) — KICKOFF + STATUS + NEXT_STEPS all agree ✓
  - HALT 8: dependencies (C8.10 + C8.11) satisfied:
    - C8.10: 5 builders + 5 notebooks present at `notebooks/` (`joint_use_demo.ipynb`, `paper_companion.ipynb`, `maternal_age_stratified_imr.ipynb`, `preterm_outcomes_time_series.ipynb`, `cross_race_fetal_mortality.ipynb`) ✓
    - C8.11: 2 migration guides present at `migrations/` (`v2.0.0-to-v2.4.0-fetal-death.md`, `v2.7.0-to-v2.8.0-natality.md`) + cross-product `docs/COMPARABILITY.md` (18.7K) present ✓
  - HALT 9: `git status --short` empty on `main` at HEAD `ebed5a9` (C8.14-complete commit) — no KICKOFF / NEXT_STEPS edit at C8.14 close ✓
- [x] **C8.15 substrate enumerated**:
  - **C.6.d substrate** — natality `maternal_education_cat4` column (single 4-category recode, both eras crosswalked; null for 2009-2013 unrevised records per natality COMPARABILITY); natality `certificate_revision` flag for revised-only filtering; linked-file `maternal_education_cat4` analog (V3 LinkCO); user-authorized data-product = **natality+linked-only** per AskUserQuestion 2026-05-14T00:30:00Z.
  - **C.6.e substrate** — fetal-death yearly_clean raw parquets at `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` retain state codes (1992-2002 era: `STATEFET` + `STATERES`; 2005-2013 era: `OSTATE` + `MRSTATEPSTL`; 2014+ era: adds `MBSTATE_REC`). Verified via `pyarrow.parquet.ParquetFile.schema.names` probe across years 1992 (198 cols), 2010 (182 cols), 2022 (142 cols). User-authorized substrate routing = **read from `output/yearly_clean/` raw parquets** per AskUserQuestion 2026-05-14T00:30:00Z.
  - **Cross-product COMPARABILITY references** for state quirks: `fetal_death/COMPARABILITY.md` lines 162-172 (plurality '5' miscoding 2005-2013 V1 era + recommended researcher recipe); lines 267-269 (Oklahoma all 11 V2 years 1992-2002 + Maryland 1992-1998 + Massachusetts 1992-1997 Hispanic non-reporting); lines 273-275 (Louisiana 1992-1994 plurality non-reporting with explicit per-record counts: 1,686 of 1,714 LA-occurrence records).
  - C8.10 builder pattern: `_build_maternal_age_stratified_imr.py` (459 LOC; single-product linked notebook) + `_build_cross_race_fetal_mortality.py` (single-product fetal-death notebook) + `_build_preterm_outcomes_time_series.py` (cross-product notebook) — pattern: `nbformat.v4.new_notebook()` + `nbclient.NotebookClient.execute()`; DESIGN: tracks-current-state docstring tag (Convention 2); helper `md()`/`code()` cell constructors; `build()` returns notebook; `main()` executes + writes `.ipynb`.
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `ebed5a9`; `C8.15-pre-do` tag does NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.14 close).
- [x] Working directory clean; on `main`; active tag on HEAD = `C8.14-complete`. ✓

### Source documentation

C8.15 is a notebook-authoring task; consumes 4 internal canonical sources + zero external NCHS PDFs:
- `natality/docs/COMPARABILITY.md` (within-era discipline for `maternal_education_cat4`; revised-only era 2009-2013)
- `fetal_death/COMPARABILITY.md` (state-quirk references for C.6.e)
- `natality/metadata/harmonized_schema.csv` (column documentation for natality `maternal_education_cat4`)
- C8.10 builder source (3 builders for the 3 shipped C8.10 notebooks; pattern reference)

All L8/L9 cheap-checks satisfied at PRE-FLIGHT inputs probe (no PMID resolutions needed; no external-page WebFetches needed; substrate is internal canonical content).

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `notebooks/_build_education_gradient.py`: does NOT exist ✓
  - `notebooks/education_gradient.ipynb`: does NOT exist ✓
  - `notebooks/_build_state_reporting_quirks.py`: does NOT exist ✓ (note: scope may shift to a second C8.15 session per §15 2-session estimate)
  - `notebooks/state_reporting_quirks.ipynb`: does NOT exist ✓
  - `RECEIPTS/C8.15_<UTC>.md`: will be written at C8.15 RECEIPT phase
- [x] **APPEND-ONLY state files:**
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at RECEIPT close
  - `DECISION_LOG.md`: NEW entry recording the AskUserQuestion 2026-05-14T00:30:00Z routing resolutions for C.6.d + C.6.e (per the C8.13 / C8.11 / C8.10 routing-decision precedent)
  - `FIX_LOG.md`: no FIX entry anticipated (the WORKED_EXAMPLE_FAQ SHA typo is a soft-flag, not a fix-on-contact-able mutation since STATUS is append-only)
  - `LESSONS.md`: NO new entry anticipated
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged (no compute on canonical state) ✓
  - All C8.9-C8.14 file SHAs preserved ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved ✓
  - existing 5 notebooks unchanged ✓
  - `paper/draft_v2_hmd_styled.md` unchanged (Phase D step 4 scope) ✓
  - `KICKOFF.md` + `NEXT_STEPS.md` unchanged (no §11 plan-update needed; routing decisions are in-PRE-FLIGHT) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.15 is notebook-authoring work; the canonical-state mutation is zero (notebooks are derived artifacts; the underlying parquets are not touched). The Convention 3 substrate is the **column-availability + within-era contract verification**.

**Table 1: C.6.d (`education_gradient.ipynb`) substrate verification**

| Field | Source | Within-era contract | Verified at PRE-FLIGHT |
|---|---|---|---|
| `maternal_education_cat4` (natality v2) | `natality_v2_harmonized_derived.parquet` | 1990-2002: years-of-schooling crosswalk; 2003-2008: revised + unrevised both populated; 2009-2013: revised-only (substantial null on unrevised); 2014+: revised-only nationwide | ✓ schema CSV documents the era pattern explicitly; cell value distributions match COMPARABILITY note |
| `maternal_education_cat4` (linked v3) | `natality_v3_linked_harmonized_derived.parquet` | Same era pattern as natality v2; V3 LINKED CAVEAT for 2009-2010 (PAY_REC + FEDUC blank in LinkCO09/10) does NOT affect maternal education | ✓ schema CSV cited |
| `certificate_revision` (natality v2) | `natality_v2_harmonized_derived.parquet` | Filter `certificate_revision == 'revised_2003'` for 2009-2013 revised-only era to avoid spurious unrevised-null mixing | ✓ COMPARABILITY note line 195 cites this filter as the canonical revision-consistent subset |
| Within-era discipline | F4 halt-condition flag | NO cross-era groupby on `maternal_education_cat4` for 2009-2013 unless filtered to revised-only; document the boundary in markdown cells | ✓ contract enforced in notebook design |

**Table 2: C.6.e (`state_reporting_quirks.ipynb`) substrate verification**

| State quirk | Time window | Source columns (raw parquet path) | Documented in fetal_death/COMPARABILITY.md |
|---|---|---|---|
| Oklahoma Hispanic non-reporting | 1992-2002 (all 11 V2 years) | `STATEFET` + `STATERES` + `HISPMOM` (or equivalent) in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Line 267 |
| Maryland Hispanic non-reporting | 1992-1998 | Same as above | Line 268 |
| Massachusetts Hispanic non-reporting | 1992-1997 | Same as above | Line 269 |
| Louisiana plurality non-reporting | 1992-1994 | `STATEFET` + `STATERES` + `DPLURAL` in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Lines 273-275 (with per-record counts: 1,686 of 1,714 LA-occurrence records) |
| Plurality '5' miscoding (footgun for soft-flag (f)) | 2005-2013 V1 era A-version | `OSTATE` + `MRSTATEPSTL` + `DPLURAL` in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Lines 162-172 + recommended researcher recipe at line 171 |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; one routing amendment — user-authorized):**

1. **C.6.d data product = natality+linked-only** (per AskUserQuestion 2026-05-14T00:30:00Z; supersedes STATUS line 90's column-name framing which referenced fetal-death's `maternal_education` + `maternal_education_unrevised`). Natural reading: an "education gradient" is most legible on birth-side outcomes (preterm, LBW, IMR via linked).
2. **C.6.e substrate = `output/yearly_clean/` raw parquets** (per AskUserQuestion 2026-05-14T00:30:00Z; supersedes STATUS line 90's "may surface §7.13 L11" framing which assumed C8.9 NCHS suppression generalizes — it doesn't; the C8.9 finding was natality-specific). Departs from C.6.a-c builder convention (those consume harmonized parquet); will be the only notebook reading raw. Documented in builder docstring.
3. **C8.10 + C8.11 dependency satisfied**: 5 worked-example notebooks + 2 migration guides + cross-product COMPARABILITY all present.
4. **No parquet mutation**; H10 reproducibility gate unaffected.
5. **F4 halt discipline enforced in BOTH notebooks**: C.6.d filters revised-only 2009-2013 era; C.6.e segments analyses by data_year ranges aligned with each state's quirk window.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward + 1 NEW):**

Carried unchanged from C8.14 close: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (**C8.15-scope; in-DO this task**) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope.

**NEW soft-flag (q) this PRE-FLIGHT**: WORKED_EXAMPLE_FAQ.md SHA anchor typo in STATUS 2026-05-13T23:45:00Z + RECEIPTS/C8.14_2026-05-13T23-45-00Z.md + commit-message narrative — recorded sha=`89730c31…` but on-disk + committed sha=`341c4550…`. STATUS is append-only so the typo persists; future sessions reading the C8.14 closing anchor for HALT verification will see the same mismatch and need to repeat this PRE-FLIGHT's `git diff HEAD` resolution. RECEIPT C8.15 records the corrected anchor for the C8.15 forward-looking HALTs to point at. L17-shape (STATUS pin drifted from on-disk reality at moment of writing; not a runtime mutation).

### Halt conditions tripped

**TWO §7.13-shape PRE-FLIGHT-time L11s surfaced + user-resolved before any DO mutation** (precedent: C8.5 / C8.6 / C8.7 / C8.9 / C8.10a / C8.10b / C8.10c / C8.11 / C8.13 PRE-FLIGHT-time AskUserQuestion path):

1. **C.6.d data-product framing in STATUS line 90 vs natality schema reality**: STATUS line 90 framed C.6.d as using fetal-death's `maternal_education_unrevised` (pre-2003) + `maternal_education` (revised; post-2003), but those column names are fetal-death-side; natality has only `maternal_education_cat4` (single column, both eras crosswalked) + `certificate_revision` flag. The within-era discipline still applies (2009-2013 revised-only window) but via a different column structure. User-resolved Option A (natality+linked-only): use natality `maternal_education_cat4` + `certificate_revision` filter; document the 2003 + 2009 boundaries explicitly.

2. **C.6.e substrate routing — STATUS line 90 vs fetal-death yearly_clean reality**: STATUS line 90 anticipated "State-level geography NOT in public-use files (per C8.9 finding)" but the C8.9 finding (DECISION_LOG 2026-05-13T10:00:00Z) was natality-specific. Fetal-death yearly_clean raw parquets retain `STATEFET` + `STATERES` (V2 1992-2002) + `OSTATE` + `MRSTATEPSTL` (V1 2005+) + `MBSTATE_REC` (2014+). The Louisiana plurality + Oklahoma/Maryland/Massachusetts Hispanic non-reporting findings cited in fetal_death/COMPARABILITY.md ARE reproducible from this substrate. User-resolved Option A: route C.6.e to `output/yearly_clean/` raw parquets (departs from C.6.a-c convention; one-off precedent documented in builder docstring).

NO `[plan-update]` commit needed (per the C8.10a / C8.10b / C8.10c / C8.11 routine-PRE-FLIGHT-input-re-interpretation precedent — substrate-routing-only resolutions stay in PRE_FLIGHT_LOG + DECISION_LOG, not in KICKOFF/NEXT_STEPS edits, when the §15 deliverable name + halt-condition flag remain unchanged).

### Result

**PROCEED to C8.15 DO** in this session. Tag `C8.15-pre-do` placed post-this-PRE-FLIGHT commit; DO sub-step 1 authors `notebooks/_build_education_gradient.py` + executes to produce `notebooks/education_gradient.ipynb`; DO sub-step 2 (if scope fits this session per §15 2-session estimate) authors `notebooks/_build_state_reporting_quirks.py` + executes to produce `notebooks/state_reporting_quirks.ipynb`; VERIFY runs cache-cleared pytest baseline; RECEIPT + `C8.15-complete` tag close the task. If only C.6.d ships this session, RECEIPT + `C8.15-partial` (or equivalent) tag closes sub-step 1; second session ships C.6.e + final `C8.15-complete` tag.

Recommended DO sequencing this session:
- **Sub-step 1**: Author `notebooks/_build_education_gradient.py` + execute → `notebooks/education_gradient.ipynb`. Sections: (i) Load natality+linked parquets + apply canonical filter; (ii) 4-category education distribution by year (1990-2024); (iii) preterm rate by education-cat4 within era boundaries (1990-2002, 2003-2008, 2014+); (iv) revised-only 2009-2013 sub-analysis with `certificate_revision == 'revised_2003'` filter; (v) NCHS-comparison cells (cite `natality/docs/COMPARABILITY.md` Section X "Education within-era guidance"); (vi) F4 within-era contract markdown narrative.
- **Sub-step 2** (if scope fits): Author `notebooks/_build_state_reporting_quirks.py` + execute → `notebooks/state_reporting_quirks.ipynb`. Sections: (i) Load fetal-death yearly_clean raw parquets for V2 era 1992-1994 (LA plurality) + 1992-2002 (OK Hispanic) + 1992-1998 (MD Hispanic) + 1992-1997 (MA Hispanic) + V1 era 2005-2013 (plurality '5' miscoding); (ii) per-state cells reproducing the COMPARABILITY-cited counts (LA 1992-1994: 1,686 of 1,714 LA-occurrence records); (iii) Oklahoma Hispanic-non-reporting demonstration; (iv) Maryland + Massachusetts; (v) plurality '5' miscoding 2005-2013 with the COMPARABILITY-cited recommended-researcher recipe; (vi) within-era + cross-era discipline narrative + soft-flag (f) closure note.
- **Sub-step 3 (VERIFY)**: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL preserved; both notebooks render end-to-end; markdown flags within_era columns; no cross-era groupby on within_era columns (F4 contract).
- **Sub-step 4 (RECEIPT)**: write `RECEIPTS/C8.15_<UTC>.md` + STATUS append + DECISION_LOG entry recording the 2 routing decisions; tag `C8.15-complete` (or `C8.15-partial` if only C.6.d ships).

Effort: matches §15 2-session estimate; estimated ~60-90 min per notebook (incl. iterative debugging) + ~5 min VERIFY + ~15 min RECEIPT.

---

## PRE-FLIGHT for C8.14 — 2026-05-13T23:30:00Z — Worked-example FAQ + PROJECT_STRUCTURE.md upgrade (E.3 + E.6) — **RESULT: PROCEED** (zero §7 halts; zero L11s; pure cross-product docs work; no parquet/test-surface mutation; clean PRE-FLIGHT)

### Scope summary

C8.14 §15.C entry (NEXT_STEPS.md lines 1228-1244) names 2 deliverables: **(E.3)** `docs/WORKED_EXAMPLE_FAQ.md` answering 3 named questions ("how do I compute the perinatal mortality rate?", "how do I get state-level data?", "what's the right canonical filter for my analysis?"); **(E.6)** Upgrade `PROJECT_STRUCTURE.md` with notebook-deps graph + build-order DAG + which-file-by-use-case matrix. KICKOFF.md Phase C Tier-2 line 195 + STATUS 2026-05-13T23:00:00Z line 39 name C8.14 as next §15 task post-C8.13. Estimated effort 1 session. §15 halt-condition flag: L11 (stale roadmap claims; fix-on-contact).

**Session scope this PRE-FLIGHT (per "go ahead with C8.14" authorization 2026-05-13T23:30:00Z):** ship PRE-FLIGHT entry + tag `C8.14-pre-do` + DO (both docs authored) + VERIFY + RECEIPT in one session per §15 1-session estimate.

### Inputs

- [x] **All 16 C8.13 Forward-looking HALTs verified byte-exact** (spot-checked 9 high-signal HALTs):
  - HALT 1: `C8.13-pre-do` + `C8.13-complete` tags present ✓
  - HALT 2: 4 parquet SHAs byte-exact (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) ✓
  - HALT 3-5: `scripts/_time_pipeline.py` + 2 driver scripts present at fresh-recorded SHAs (sha=`c7809742…` / `7f48e971…` / `05fda4ae…`) ✓
  - HALT 4: `docs/PIPELINE_TIMING_BENCHMARK.md` present at sha=`7792cb34…` ✓
  - HALT 5: 2 per-stage CSVs present (45+6 rows) ✓
  - HALT 9: `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` sha=`b6fe22d6…` unchanged ✓
  - HALT 14: `/tmp/c8_13_baseline/` removed (no stale state) ✓
- [x] **C8.14 substrate enumerated**:
  - 2 per-subproject FAQs present: `fetal_death/FAQ.md` (16 Q&A) + `~/Desktop/natality-harmonization/docs/FAQ.md` (24 Q&A) — the WORKED_EXAMPLE_FAQ is **cross-product complement, not duplication**
  - `docs/JOINT_USE_GUIDE.md` present with canonical analytic filters §43-55 + perinatal mortality worked example §128-172 + R/DuckDB §174-227 — primary cross-link target
  - 4 notebooks present: `joint_use_demo.ipynb` (32 cells; perinatal demo Section C) + `maternal_age_stratified_imr.ipynb` (23 cells; C8.10a) + `preterm_outcomes_time_series.ipynb` (24 cells; C8.10b) + `cross_race_fetal_mortality.ipynb` (26 cells; C8.10c)
  - `PROJECT_STRUCTURE.md` current at sha=`32688930…`, 134 lines (top-level layout + per-subdir maps)
- [x] **`docs/` directory** has 7 existing files (COMPARABILITY.md, JOINT_USE_GUIDE.md, NCHS_SOURCE_MANIFEST.md, PIPELINE_TIMING_BENCHMARK.md + 2 CSVs, PRIOR_ART.md); WORKED_EXAMPLE_FAQ.md will be the 8th. ✓
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `0155a6f`; `C8.14-pre-do` tag does NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.13 close).
- [x] Working directory clean; on `main`; active tag on HEAD = `C8.13-complete`. ✓

### Source documentation

C8.14 is pure docs work; no external NVSR PDFs or NCHS user guides consumed. The cross-link surface is internal: `docs/JOINT_USE_GUIDE.md`, `docs/COMPARABILITY.md`, 2 per-subproject FAQs, 4 notebooks, `VERSION_ROADMAP.md`, `PRIOR_ART.md`. All L8/L9 cheap-checks satisfied at PRE-FLIGHT inputs probe (no PMID resolutions needed; no external-page WebFetches needed).

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `docs/WORKED_EXAMPLE_FAQ.md`: does NOT exist ✓
  - `RECEIPTS/C8.14_<UTC>.md`: will be written at C8.14 RECEIPT phase
- [x] **MAY BE MODIFIED:**
  - `PROJECT_STRUCTURE.md` — §15-mandated upgrade (notebook-deps graph + build-order DAG + which-file-by-use-case matrix appended as new sections); current sha=`32688930…`
- [x] **APPEND-ONLY state files:**
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at RECEIPT close
  - `DECISION_LOG.md`: NEW entry only if a non-trivial choice surfaces during DO (not anticipated; the WORKED_EXAMPLE_FAQ scope is well-defined; PROJECT_STRUCTURE upgrade is additive)
  - `FIX_LOG.md`: no FIX entry anticipated (any L11 surfaces are fix-on-contact and bundled into the FAQ/structure edits)
  - `LESSONS.md`: NO new entry anticipated
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged (no compute) ✓
  - All C8.9-C8.13 file SHAs preserved ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved ✓
  - existing per-subproject FAQs unchanged ✓
  - `docs/JOINT_USE_GUIDE.md` unchanged (WORKED_EXAMPLE_FAQ cross-links to it; no need to duplicate) ✓
  - `paper/draft_v2_hmd_styled.md` unchanged (Phase D step 4 scope) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.14 is docs-only work; no canonical-state cells mutated. The Convention 3 substrate is the **existing-content boundary check**: verify the WORKED_EXAMPLE_FAQ scope does NOT duplicate existing per-subproject FAQ content or JOINT_USE_GUIDE content.

**Table 1: Cross-product FAQ scope vs existing canonical-content surfaces**

| FAQ question (§15-mandated) | Existing canonical source | WORKED_EXAMPLE_FAQ role |
|---|---|---|
| How do I compute the perinatal mortality rate? | `docs/JOINT_USE_GUIDE.md` §128-172 "Worked example: perinatal mortality rate, 2022 (three-product joint)" + `notebooks/joint_use_demo.ipynb` Section C (6 cells) | One-paragraph distilled answer + numeric formula + cross-link to both canonical sources + caveat re NVSR 73-09 proportional-redistribution |
| How do I get state-level data? | C8.9 PRE-FLIGHT C.1 drop + DECISION_LOG 2026-05-13T10:00:00Z + `natality/docs/FAQ.md` "Is geography included?" (4 lines) | Cross-product synthesis: NCHS state suppression in all 3 products; alternatives (RDC; Census region/division derivation; alternate data sources); explicit "not in pre-submission scope" framing |
| What's the right canonical filter for my analysis? | `docs/JOINT_USE_GUIDE.md` §43-55 "Canonical analytic filters" + per-subproject FAQs ("How should I filter" / "What is the recommended analysis universe?") | Cross-product decision-matrix table: given (product × use-case × question type), which filter; plus the within-era vs cross-era flag |

**Table 2: Additional cross-product FAQ candidates (judgement at DO)**

Beyond the §15-mandated 3 questions, the FAQ should cover the most-common other cross-product friction points surfaced through C8.1-C8.13 work:

- "Which product should I use for [maternal age × LBW / preterm / IMR / fetal mortality / cesarean]?" → use-case-to-product lookup
- "How do I handle the V3a/V3b race-coding caveat (code 7 + code 9 → null)?" → cross-link to `notebooks/cross_race_fetal_mortality.ipynb` markdown caveats
- "What's the bridged-race era and when does it end?" → cross-link to `docs/COMPARABILITY.md` bilateral race-coding methodology
- "Which column do I use for analysis: harmonized or harmonized_derived?" → use-case → which-parquet
- "How do I compute infant mortality rate (IMR) using the linked file?" → cross-link to `notebooks/maternal_age_stratified_imr.ipynb`
- "How do I handle the 2003 certificate revision break?" → cross-link to `docs/COMPARABILITY.md` + `natality/docs/FAQ.md` "Which variables have known breaks?"
- "How do I cite this resource?" → cross-link to existing CITATION.cff + per-product Zenodo DOIs

Cardinality estimate: 8-12 Q&A pairs in WORKED_EXAMPLE_FAQ; bounded scope; doesn't drift toward "everything in one FAQ."

**Table 3: PROJECT_STRUCTURE.md upgrade scope**

§15 mandates 3 NEW sections appended to current 134-line file:

| New section | Content sketch |
|---|---|
| Build-order DAG | Stage diagram showing parse → harmonize → derive → validate per product; cross-product flow joining all 3 products at notebooks/ + shared/helpers/; serial dependencies vs parallel branches; clean reproduce path via C8.13 F.5 drivers |
| Notebook-deps graph | Per-notebook input parquets + helper modules + cross-product joins; mapped to the 4 notebooks present + the 2 stubs that remain (paper_companion.ipynb is now substantive post-Task 4; joint_use_demo.ipynb is post-C8.3 substantive) |
| Which-file-by-use-case matrix | Decision table: given (analytic question type), which subproject + which parquet + which notebook + which scripts |

Existing 134-line structure preserved; new sections appended at end. No top-level reorganization (avoid Anti-Pattern: re-shaping a doc when only adding).

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; zero amendments):**

1. The WORKED_EXAMPLE_FAQ is **NEW** (not modification of an existing FAQ); per-subproject FAQs preserved unchanged.
2. The PROJECT_STRUCTURE upgrade is **additive** (3 new sections appended); existing 134-line structure preserved.
3. The 3 §15-mandated FAQ questions have **clear canonical-source cross-link targets**; the FAQ is a CROSS-PRODUCT INDEX layer, not duplication.
4. **C8.10 dependency satisfied**: 3 worked-example notebooks + `joint_use_demo.ipynb` all present at canonical paths; FAQ cross-links resolve.
5. **No parquet mutation**; H10 reproducibility gate unaffected.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

Carried unchanged from C8.13 close: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (C8.15) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope.

**No NEW soft-flags from this PRE-FLIGHT.** Pure cross-product docs work; no expected residuals beyond the carry-forward set.

### Halt conditions tripped

**NONE.** Zero §7 halt conditions tripped at PRE-FLIGHT. The §15 spec is well-defined; all dependencies (C8.10 notebooks) shipped; substrate inputs all present; no L11 surfaces in the §15 plan-claims (the 3 named questions have real canonical cross-link targets). No §11 plan-update required.

### Result

**PROCEED to C8.14 DO** in this session. Tag `C8.14-pre-do` placed post-this-PRE-FLIGHT commit; DO authors `docs/WORKED_EXAMPLE_FAQ.md` + upgrades `PROJECT_STRUCTURE.md`; VERIFY runs cache-cleared pytest baseline; RECEIPT + `C8.14-complete` tag close the task.

Recommended DO sequencing this session:
- **Sub-step 1**: Author `docs/WORKED_EXAMPLE_FAQ.md` (8-12 Q&A; cross-product index over per-subproject FAQs + JOINT_USE_GUIDE + 4 notebooks).
- **Sub-step 2**: Append 3 new sections to `PROJECT_STRUCTURE.md` (build-order DAG + notebook-deps graph + which-file-by-use-case matrix).
- **Sub-step 3 (VERIFY)**: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL preserved; spot-check cross-links resolve (file paths exist; line-number cites land on intended content).
- **Sub-step 4 (RECEIPT)**: write `RECEIPTS/C8.14_<UTC>.md` + STATUS append; tag `C8.14-complete`.

Effort: matches §15 1-session estimate; estimated ~30-45 min docs authoring + ~5 min VERIFY + ~10 min RECEIPT.

---

## PRE-FLIGHT for C8.13 — 2026-05-13T22:30:00Z — Performance + GitHub Release artifacts + pipeline timing benchmark (F.1 + F.4 + F.5) — **RESULT: HALT (one §7.13-shape PRE-FLIGHT-time L11 surfaced) → resolved via AskUserQuestion 2026-05-13T22:30:00Z (F.1 dropped + F.4 deferred + F.5 ACTIVE; precedent: C8.5/C8.6/C8.7/C8.9 PRE-FLIGHT-time §11 plan-update); PROCEED to C8.13 DO with narrowed scope**

### Scope summary

C8.13 §15.C entry (NEXT_STEPS.md lines 1208-1224, pre-this-plan-update) names 3 deliverables: **(F.1)** parquet column-dictionary tuning per low-cardinality column with anticipated 30-50% size reduction; **(F.4)** GitHub Release v1.x with parquet uploads alongside Zenodo; **(F.5)** pipeline timing benchmark vs manuscript `~6 min fetal-death / ~90 min natality` claims (paper/draft_v2_hmd_styled.md:68). KICKOFF.md Phase C Tier-2 line 194 + STATUS 2026-05-13T21:30:00Z line 39 name C8.13 as next §15 task post-C8.12. Estimated effort 1.5-2 sessions per §15. §15 halt-condition flag: "B.12 snapshot-regression interaction (one-time SHA shift expected — bundle DECISION_LOG note)."

**Session scope this PRE-FLIGHT (per (a)-(d) handshake; user-authorized "proceed in the way you think is best" 2026-05-13T22:00:00Z):** ship PRE-FLIGHT entry + §11 plan-update (KICKOFF.md + NEXT_STEPS.md §15.C C8.13 re-scope + DECISION_LOG entry) + tag `C8.13-pre-do` in one commit; F.5 DO + RECEIPT span the same session via background-compute (~96 min natality+linked + ~6-9 min fetal-death real timing).

### Inputs

- [x] **All 14 C8.12 Forward-looking HALTs verified byte-exact** (table below). ✓
- [x] **Existing parquets enumerated** for F.1 + F.5 substrate: 4 parquets on disk; sizes 29 + 36 MB (fd) + 2.2 GB (nat) + 1.3 GB (linked) = ~3.6 GB total. ✓
- [x] **Per-column encoding state probed via `pyarrow.parquet.ParquetFile.metadata.row_group(0).column(c).encodings`** for all 4 parquets (340 columns total): see Field-value snapshot Table 1 below. ✓ **(L11-surfacing finding — see Halt conditions tripped)**
- [x] **F.4 substrate**: `gh` CLI v2.87.3 installed; auth status `Logged in to github.com account yoelplutchok` with token scopes `gist, read:org, repo, workflow` (`repo` scope sufficient for Release create); `gh release list --repo yoelplutchok/vital-statistics-harmonization` returns empty (no releases yet on the public repo). ✓
- [x] **F.5 substrate**: `fetal_death/scripts/run_pipeline.py` exists at the monorepo subproject path (stale `ALL_YEARS=29` per soft-flag (d); see PRE-FLIGHT Field-value snapshot Table 2 for natality per-step scripts — no orchestrator per C8.7b DEFERRED status). Manuscript timing claim located at `paper/draft_v2_hmd_styled.md:68`: *"The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes, dominated by the fixed-width parse stage."* ✓
- [x] **Raw zip inventory**: 43 fetal-death + 35 natality + 19 linked-cohort zips present at canonical absolute paths (verified via `ls`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.13-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.12 Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.12-complete` tag present on commit `51f6836` | ✓ | `git tag --list 'C8.12*'` shows both `C8.12-pre-do` + `C8.12-complete` |
| 2 | `tests/mutations/` package exists with 9 files at documented SHAs | ✓ | All 9 files present (1 init + 1 runner + 7 mutation tests) |
| 3 | `tests/mutations/__init__.py` sha=`e3b0c44298fc1c14…` (canonical empty-file SHA) | ✓ | matches exactly |
| 4 | `tests/mutations/_runner.py` sha=`98ecb483ca24a660…` | ✓ | matches exactly |
| 5 | 7 mutation test file SHAs byte-exact | ✓ | All 7 match (compare_external_targets_v1=`691b5b8f…`, compare_external_targets_v3_linked=`83d9ab51…`, validate_2022=`4305f89f…`, validate_external=`a13cedf3…`, validate_external_v2=`833e2277…`, validate_linked_parquets=`724bbe49…`, validate_v1_invariants=`b7d8df48…`) |
| 6 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb…` / fd_der=`185c071e…` / nat_der=`e16ad5323d…` / linked_der=`9b828a4d…` all match |
| 7 | All C8.12 DO-step-1 + DO-step-2 file SHAs unchanged | ✓ | `fetal_death/file_inventory.csv` `2f2ba2c9…` / `tests/test_inventory_invariants.py` `823e2a8d…` / `tests/test_source_zip_sha_stability.py` `e09158af…` / `tests/test_parquet_column_snapshot.py` `6c605783…` / `tests/snapshots/__init__.py` empty-sha / `tests/snapshots/_build_snapshot.py` `a27b5e70…` / `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` `b6fe22d6…` all match |
| 8 | All C8.11 file SHAs unchanged | ✓ | docs/NCHS_SOURCE_MANIFEST.md=`ed2a44d3…` / docs/COMPARABILITY.md=`10cead2b…` / migrations/v2.7.0-to-v2.8.0-natality.md=`96bb1c54…` / migrations/v2.0.0-to-v2.4.0-fetal-death.md=`90e010a7…` all match |
| 9 | Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL | ✓ | **74 passed, 1 skipped, 1 xfailed in 152.66s** (cache-cleared via `find . -name __pycache__ -delete`; matches PASS/SKIP/XFAIL counts exactly; wall-time 152.66s is faster than the 209.70s C8.12 baseline but Convention 1 SHAPE-not-VALUE pin is on counts only, not wall-time — passes). |
| 10 | The 1 SKIP is `test_validate_linked_parquets_mutation` | ✓ | confirmed via `pytest tests/mutations/ -v` collection: SKIP occurs at the `natality/output/linked/` missing-input check |
| 11 | Next task = C8.13 (performance + GitHub release artifacts) | ✓ | This entry executes |
| 12 | C8.13 PRE-FLIGHT must anticipate B.12 snapshot-regression interaction | ✓ | RESOLVED at this PRE-FLIGHT: F.1 dropped → no parquet reshape → no B.12 SHA shift → no re-snapshot required this session. (The §15 anticipated interaction is moot under the F.1-dropped re-scope.) |
| 13 | No §11 plan-update needed at C8.12 close | N/A at C8.13 close: §11 plan-update REQUIRED at this PRE-FLIGHT close per the F.1 falsification finding (precedent: C8.5/C8.6/C8.7/C8.9 PRE-FLIGHT-time plan-updates). | — |
| 14 | Soft-flag (l) RESOLVED-as-not-applicable at C8.12 receipt | ✓ | preserved unchanged |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0; C8.12 DECISION_LOG 21:00Z pinned dict-encoding contract to this version) ✓
- [x] DuckDB Python: present (C8.9 lockfile) ✓ (not exercised by C8.13)
- [x] gh CLI: 2.87.3, auth OK with `repo` scope ✓ (F.4 substrate)
- [x] Working directory clean (`git status --short` empty on `main` at `51f6836`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.12-complete` (verified) ✓
- [x] uv-managed `.venv` matches `uv.lock` (C8.5a baseline): ✓

### Source documentation

C8.13 is benchmark + plan-update + docs work; no new NVSR PDFs or NCHS user guides are CONSUMED. The substantive inputs are (i) the 4 harmonized + derived parquets' physical encoding state (F.1 probe substrate); (ii) `paper/draft_v2_hmd_styled.md:68` for the F.5 manuscript timing claim (cite-anchored at line 68); (iii) `gh release` API surface for F.4. No L9 cheap-checks on external PDFs required. ✓

The manuscript citation `paper/draft_v2_hmd_styled.md:68` reads (verbatim): *"Re-deriving the parquet from a fresh download of the NCHS source zips produces a byte-identical file, and SHA-256 checksums for every shipped artifact are committed in `PROVENANCE.md`. The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes, dominated by the fixed-width parse stage."* The ±10% tolerance is the §15 VERIFY criterion.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `RECEIPTS/C8.13_<UTC>.md`: will be written at C8.13 RECEIPT phase post-F.5 benchmark
  - `docs/PIPELINE_TIMING_BENCHMARK.md` (NEW; F.5 results record + per-stage breakdown + reconciliation vs manuscript claim): does NOT exist ✓
- [x] **MAY BE MODIFIED:**
  - `paper/draft_v2_hmd_styled.md` line 68 — IF F.5 benchmark surfaces a >±10% drift from `~6 min / ~90 min`, update the timing prose; current sha probed at DO baseline. If within tolerance, NO edit.
  - `KICKOFF.md` line 194 (C8.13 description) — §11 plan-update applied this commit
  - `NEXT_STEPS.md` §15.C C8.13 entry (lines 1208-1224) — §11 plan-update applied this commit
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at PRE-FLIGHT close + further appends per DO/RECEIPT phases
  - `DECISION_LOG.md`: F.1-falsification entry resolving the L11 cheap-check finding
  - `FIX_LOG.md`: no FIX entry anticipated this session (F.1 finding is a §15 plan-claim L11, not a code-state bug; documented in DECISION_LOG per the C8.5/C8.6/C8.7/C8.9 precedent)
  - `LESSONS.md`: NO new entry. The L11 pattern is already in the §8 matrix; this instance is one more reinforcement of the pattern, not a new mistake class.
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓ — F.1 dropped means zero parquet mutation this session
  - All C8.9 + C8.10a/b/c + C8.11 + C8.12 file SHAs preserved ✓
  - `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` unchanged (no re-snapshot required under F.1-dropped scope) ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved (F.5 benchmark does not touch test surface) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.13's substantive PRE-FLIGHT-time field-value snapshot is **the parquet per-column encoding state** (F.1 substrate; the source of the falsified §15 premise) + **the manuscript timing claim** (F.5 substrate; cite-anchored at line 68) + **per-stage script inventory** (F.5 measurement surface).

**Table 1: Per-parquet encoding state (F.1 probe; 340 columns total)**

| Parquet | Rows | Cols | RGs | File size | Dict-encoded cols (RG0) | Non-dict cols (RG0) | Non-dict-col dtypes |
|---|---|---|---|---|---|---|---|
| `output/harmonized/fetal_death_harmonized.parquet` | 2,427,233 | 73 | 3 | 0.029 GB | 73/73 (100%) | 0 | N/A |
| `output/harmonized/fetal_death_derived.parquet` | 2,427,233 | 89 | 3 | 0.036 GB | 89/89 (100%) | 0 | N/A |
| `natality_v2_harmonized_derived.parquet` | 138,819,655 | 84 | 278 | 2.203 GB | 46/84 (55%) | 38 | **All 38 = bool, RLE+PLAIN** |
| `natality_v3_linked_harmonized_derived.parquet` | 74,943,824 | 94 | 150 | 1.300 GB | 53/94 (56%) | 41 | **All 41 = bool, RLE+PLAIN** |

**F.1 critical finding (L11 / §7.13 PRE-FLIGHT-time discovery):** The §15 PRE-FLIGHT-input claim "Re-write derive.py's parquet-write call with `use_dictionary=True` per column [→] typically yields 30-50% size reduction" is **empirically falsified** by the encoding-state probe:

1. **Both fetal-death parquets are already 100% dict-encoded** (73/73 + 89/89). PyArrow defaults already produce this state for fd. Total fd size = 65 MB; no headroom anyway.
2. **All 38+41 non-dict columns in natality + linked are booleans using RLE+PLAIN encoding** — the optimal 1-bit-per-value encoding for 2-state columns. Forcing dict-encoding on booleans does not help (a dict + indices is strictly larger than RLE on 2 distinct values).
3. **PyArrow's default `use_dictionary=True` (boolean)** already enables dict encoding for cardinality-appropriate columns; the encoding choice per column is per-column-adaptive at the column-writer level. The §15 plan ("`use_dictionary=True` per column") would not change behavior because pyarrow already does the right thing.
4. **Achievable size reduction from F.1 as scoped in §15** ≈ 0% (or negative if dict encoding is forced onto boolean columns).

This is a textbook L11-class stale §15 plan claim catch — the §15 plan was authored from the `EXPLORATION_REPORT.md` `~30-50% reduction` heuristic without first probing the actual per-parquet encoding state. The Convention 3 Field-value snapshot is precisely the cheap-check moment designed to catch this. Precedent: C8.5 (PRE-FLIGHT split § 5 → C8.5a + C8.5b on docker absence), C8.6 (PRE-FLIGHT deferred live-CI verify to Phase D step 3), C8.7 (PRE-FLIGHT split → C8.7a + C8.7b on orchestrator scope realism), C8.9 (PRE-FLIGHT dropped C.1 on NCHS state-suppression policy). All five precedents follow the same shape: cheap-check at PRE-FLIGHT discovers the §15 plan's substrate doesn't exist as the plan assumed; user-resolved via AskUserQuestion; §11 plan-update applied in the same commit.

**Resolution (user-authorized via AskUserQuestion 2026-05-13T22:30:00Z):** F.1 **DROPPED** from C8.13 scope. The §11 plan-update applied this commit revises KICKOFF.md line 194 + NEXT_STEPS.md §15.C C8.13 entry to remove F.1 from the active DO scope; the falsified-premise documentation lands in DECISION_LOG.md 2026-05-13T22:30:00Z. Zero parquet mutation; zero SHA shift; B.12 snapshot regression test remains valid.

**Table 2: F.5 per-stage script inventory (timing measurement surface)**

| Subproject | Stage | Entry-point script | Cardinality |
|---|---|---|---|
| fetal_death | run_pipeline orchestrator | `fetal_death/scripts/run_pipeline.py` | 1 entry-point (ALL_YEARS=29 stale; covers 1992-2022 V2+V2.1+V1 era) |
| fetal_death | per-year parse | `fetal_death/scripts/01_import/parse_fetal_year.py` | 43 invocations (1982-2024) |
| fetal_death | harmonize | `fetal_death/scripts/03_harmonize/harmonize.py` | 1 invocation |
| fetal_death | derive | `fetal_death/scripts/04_derive/derive.py` | 1 invocation |
| fetal_death | validate external | `fetal_death/scripts/05_validate/validate_external*.py` + `validate_2022.py` | 3 invocations |
| natality (no orchestrator per C8.7b DEFERRED) | parse all V1 years | `~/Desktop/natality-harmonization/scripts/01_import/parse_all_v1_years.py` | 1 batch (35 yrs internally) |
| natality | parse all linked years | `~/Desktop/natality-harmonization/scripts/01_import/parse_all_linked_years.py` | 1 batch (19 cohort yrs) |
| natality | harmonize V1 core | `harmonize_v1_core.py` | 1 invocation |
| natality | harmonize linked V3 | `harmonize_linked_v3.py` | 1 invocation |
| natality | derive V1 core | `derive_v1_core.py` | 1 invocation |
| natality | derive linked V3 | `derive_linked_v3.py` | 1 invocation |
| natality | validate | 8 scripts under `05_validate/` (not all on critical path; manuscript ~90 min claim covers parse+harmonize+derive primary chain) | varies |

**F.5 timing approach (user-authorized "Run real end-to-end benchmark this session"):**
- Fetal-death: run 43-year per-step pipeline manually (parse loop + harmonize + derive + validate); time each stage; total wall-clock vs `~6 min` claim. Note: `run_pipeline.py` has stale `ALL_YEARS=29` per soft-flag (d); not fixing this session (C8.7b scope); the 43-year per-step manual run produces an honest current-state measurement.
- Natality + linked: run `parse_all_v1_years.py` + `parse_all_linked_years.py` + `harmonize_v1_core.py` + `harmonize_linked_v3.py` + `derive_v1_core.py` + `derive_linked_v3.py` sequentially; time the full chain; total vs `~90 min` claim. Validate stage excluded from the timing claim (manuscript scope is "pipeline runs end-to-end" interpreted as parse → derive primary chain; validate runs separately per the manuscript's Level-2 framing).
- Approach: run in background (BashOutput-monitored), capture wall-clock per stage, aggregate into `docs/PIPELINE_TIMING_BENCHMARK.md`.

**Table 3: F.4 substrate snapshot (DEFERRED to Phase D step 3 per user authorization)**

| Item | State |
|---|---|
| `gh` CLI version | 2.87.3 |
| GitHub auth | `yoelplutchok` keyring; token scopes `gist, read:org, repo, workflow` (sufficient for Release create) |
| Public repo | `yoelplutchok/vital-statistics-harmonization` at v1.0 commit `a18ca3a` |
| Existing releases | 0 (none) |
| F.4 disposition | DEFERRED to Phase D step 3; bundles into the staging-dir scrub + v1.x push event (cleaner: one public-release event) |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet):**

1. **F.1 §15 premise FALSIFIED at cheap-check** (see Table 1). Resolved via user-authorized §11 plan-update Option A: drop F.1; ship DECISION_LOG entry documenting the falsified premise. ✓
2. **F.4 substrate VERIFIED** (gh CLI auth OK; public repo exists; no prior releases). Resolved via user-authorized deferral to Phase D step 3. ✓
3. **F.5 substrate VERIFIED** (manuscript claim located + per-stage script inventory complete). Resolved via user-authorized real-benchmark this session. ✓
4. **B.12 snapshot regression interaction MOOT** under F.1-dropped re-scope (no parquet reshape; no SHA shift; no re-snapshot). ✓

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

- Carry-forward from C8.12 close (9 carried + 2 new + 3 RESOLVED): (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b; **brushed-against this session for F.5 but NOT fixed** — C8.7b scope; documented as a F.5 caveat in the RECEIPT) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (C8.15) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X).
- **NEW soft-flag (p) this PRE-FLIGHT**: F.1 dict-encoding work permanently dropped per user authorization 2026-05-13T22:30:00Z; documented in DECISION_LOG. Any future per-parquet encoding work (e.g., alternative compression codecs ZSTD vs default SNAPPY; row-group size tuning) is **out of pre-submission scope** and requires explicit re-authorization (analog of C.1 NCHS-suppression permanent drop at C8.9). Reconsider only on user request.

### Halt conditions tripped

**ONE §7.13-shape PRE-FLIGHT-time L11** (F.1 §15-premise falsification; the §15 plan's "30-50% size reduction" validity domain is empty for our specific schemas). Resolved via user AskUserQuestion 2026-05-13T22:30:00Z = Option A (drop F.1) + Option A (defer F.4) + Option A (run real benchmark). §11 plan-update applied this commit. Precedent: C8.5 / C8.6 / C8.7 / C8.9 PRE-FLIGHT-time §11 plan-updates with the same shape (cheap-check falsifies §15 substrate; user-resolved in-PRE-FLIGHT; commit `[plan-update]` prefix; DECISION_LOG documents the resolution).

No §7.18 (reproducibility regression). No L17 (no SMOKE stale-pinning). No L13 (no inventory CSV claim drift). No L14 (no validator exit-code regression). No L11 elsewhere (no other §15 stale claims).

### Result

**PROCEED post-§11 plan-update.** This PRE-FLIGHT entry + the §11 plan-update artifacts (KICKOFF.md + NEXT_STEPS.md edits + DECISION_LOG entry + STATUS.md append) ship as one bundled `[plan-update] C8.13 PRE-FLIGHT` commit. Tag `C8.13-pre-do` placed on this commit. DO begins post-commit with F.5 benchmark execution (background-compute) followed by RECEIPT + `C8.13-complete` tag.

Recommended DO sequencing this session:
- **PRE-FLIGHT close (this commit)**: `[plan-update] C8.13 PRE-FLIGHT` ships PRE_FLIGHT_LOG entry + KICKOFF + NEXT_STEPS edits + DECISION_LOG entry + STATUS section. Tag `C8.13-pre-do`.
- **DO**: launch background per-stage F.5 timing measurements (fetal-death 43-yr per-step + natality+linked per-step); BashOutput-monitor each.
- **VERIFY**: compare measured wall-clock per stage against manuscript `~6 min / ~90 min` claims; ±10% tolerance is PASS; >±10% drift triggers manuscript line 68 update (which itself is Phase D step 4 scope — at C8.13 RECEIPT, we document the drift + propose the manuscript edit but leave the actual edit to Phase D 4 per the C8.12 RECEIPT precedent of "manuscript impact deferred to Phase D step 4").
- **RECEIPT**: write `RECEIPTS/C8.13_<UTC>.md` + `docs/PIPELINE_TIMING_BENCHMARK.md` + STATUS append; tag `C8.13-complete`.

Effort revised under narrowed scope: **~1 session** (was §15-estimated 1.5-2 sessions; F.1 drop + F.4 defer cuts ~50%; F.5 alone is ~96 min compute + ~30 min plan-update + ~30 min RECEIPT/VERIFY).

---

## PRE-FLIGHT for C8.12 — 2026-05-13T19:30:00Z — Mutation tests + L13 audit + L14 audit + SHA-stability + snapshot regression (B.6 + B.7 + B.8 + B.11 + B.12) — **RESULT: PROCEED** (zero §7 halts; zero L11s; scope enumeration matches §15 expectation incl. "Likely surfaces FIX_LOG cascades — budget for fix-on-contact" — 3 L14-CANDIDATE validators surfaced at audit-surface enumeration, 7 validators with FAIL surface for B.6 mutation-test pairing; clean PRE-FLIGHT)

### Scope summary

C8.12 §15.C entry (NEXT_STEPS.md lines 1188-1205) names 5 deliverables: **(B.6)** mutation-test scaffolding for every validator (`tests/mutations/`; inject known violation, assert validator catches it; L3 defense); **(B.7)** audit every metadata CSV for L13 role-vs-column claims; **(B.8)** audit every validator's `main()` for L14 exit-code propagation; **(B.11)** SHA-stability test (PROVENANCE.md + on-disk SHA parity; primary target this session = `docs/NCHS_SOURCE_MANIFEST.md` shipped at C8.11 — 97 raw-zip SHAs); **(B.12)** per-column snapshot regression test (4 parquets × 73+89+84+94 = 340 columns total). KICKOFF.md Phase C Tier-2 line 193 + STATUS 2026-05-13T18:00:00Z line 53 name C8.12 as the next §15 task post-C8.11. Estimated effort 3-4 sessions per §15. §15 halt-condition flags: L3, L13, L14, H10 — "Likely surfaces FIX_LOG cascades — budget for fix-on-contact." Dependencies: C8.6 (CI to run new tests; already shipped at `.github/workflows/ci.yml`).

**Session scope this PRE-FLIGHT (per (a)-(d) handshake; user-authorized "proceed as you think is the best way"):** ship PRE-FLIGHT entry + tag `C8.12-pre-do` only this session; DO + VERIFY + RECEIPT span the subsequent 2-3 sessions per §15 "3-4 sessions" estimate. PRE-FLIGHT-only-this-session pattern follows the C8.10/C8.11 PRE-FLIGHT-close-then-DO-next-session precedent for multi-deliverable tasks. C8.12-pre-do tag placed post-this-PRE-FLIGHT, pre-any-DO-mutation.

### Inputs

- [x] **All 15 C8.11 Forward-looking HALTs verified byte-exact** (see table below). ✓
- [x] **All 11 validators identified and inventoried** for B.6 + B.8 surfaces (see §"Field-value snapshot" Table 1 below). ✓
- [x] **20 metadata CSVs enumerated** for B.7 L13 audit surface (16 fetal-death + 4 natality; see Table 2). ✓
- [x] **docs/NCHS_SOURCE_MANIFEST.md** (B.11 primary target this session): 97 markdown-table SHA-256 rows confirmed (43 fetal-death + 35 natality + 19 linked-cohort); sha=`ed2a44d3117336cc…`. ✓
- [x] **fetal_death/PROVENANCE.md staleness confirmed** (carry-forward soft-flag (a); pre-V2.1/V3a/V3b/v2.4 state; tag=v2.0.0; 33 SHA entries; canonical sha mismatch with current `38e2cecb…` parquet). Out-of-scope for B.11 this session per Phase-D-step-2 routing. ✓
- [x] **natality/PROVENANCE.md absent** (carry-forward soft-flag (b)); B.11 substrate for natality is `docs/NCHS_SOURCE_MANIFEST.md` Section 2 + Section 3, NOT a per-product output-artifact PROVENANCE. ✓
- [x] **4 parquet schemas enumerated** for B.12 snapshot-regression sizing: 73 + 89 + 84 + 94 = 340 columns total. ✓
- [x] **Existing test surface** (current 56 PASS + 1 XFAIL): 13 test files, 5 with test bodies (tests/test_canonical_filter_invariants.py 28 asserts; tests/test_cross_product_join_parity.py 34; tests/test_row_count_conservation.py 33; fetal_death/tests/test_release_smoke.py 26; fetal_death/tests/test_schema_dtype_parity.py 8; natality/tests/test_schema_dtype_parity.py 6). New `tests/mutations/` directory does NOT exist. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.12-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.11 Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.11-complete` + `C8.11-pre-do` tags present | ✓ | `git tag --list 'C8.11*'` shows both |
| 2 | `fetal_death/file_inventory.csv` sha=`38dc035eeccb8b80…` | ✓ | matches exactly; 43 rows; year 1982-2024 contiguous |
| 3 | `docs/NCHS_SOURCE_MANIFEST.md` sha=`ed2a44d3117336cc…` | ✓ | matches; 97 SHA-256 rows in 3 sections confirmed |
| 4 | `docs/COMPARABILITY.md` sha=`10cead2b9da604e1…` | ✓ | matches |
| 5 | `migrations/v2.7.0-to-v2.8.0-natality.md` sha=`96bb1c54a8e812d0…` | ✓ | matches |
| 6 | `migrations/v2.0.0-to-v2.4.0-fetal-death.md` sha=`90e010a78e1078b2…` | ✓ | matches |
| 7 | `VERSION_ROADMAP.md` sha=`15f903fd0f9d382c…` | ✓ | matches |
| 8 | 3 cross-link READMEs at expected SHAs | ✓ | `README.md` `b3badf143929e433…` / `natality/README.md` `d1b08976e7b06414…` / `fetal_death/README.md` `9093d85e712b694e…` all match |
| 9 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb03ff4947…` / fd_der=`185c071ec76ab8aa…` / nat_der=`e16ad5323d68e28d…` / linked_der=`9b828a4de4e59b17…` all match |
| 10 | 6 C8.10a/b/c notebook + builder SHAs unchanged | ✓ | all 6 (notebooks/maternal_age_stratified_imr.ipynb, _build_*, preterm_*, cross_race_*) match exactly |
| 11 | 13 C8.9 file SHAs unchanged (14th = README.md intentionally drifted) | ✓ | 8 probed (notebooks/README.md=`6fc9b191…`, 3× quickstart.R, views.sql, pyproject.toml, uv.lock, .python-version, ci.yml, docs/JOINT_USE_GUIDE.md) all match |
| 12 | Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL | ✓ | **56 passed, 1 xfailed in 83.55s** (cache-cleared via `find . -name __pycache__ -delete`; matches HALT exactly) |
| 13 | 8 open soft-flags (a)-(i) preserved | ✓ | All carried forward; none promoted to halt; (h) and (i) are C8.11 in-DO additions |
| 14 | Next task = C8.12 | ✓ | This entry executes |
| 15 | All 5 PRE-FLIGHT-time L11 resolutions applied | ✓ | C8.11 DO landed all 5 (Option A inventory + (i) migration filename + (ii) E.8 manifest scope + (iii) VERSION_ROADMAP fix-on-contact + (h) in-DO year-set correction); no further user authorization needed |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] DuckDB Python: present (C8.9 lockfile) ✓ (not exercised by C8.12)
- [x] Working directory clean (`git status --short` empty on `main` at `fc9c6ee`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.11-complete` (verified) ✓
- [x] uv-managed `.venv` matches `uv.lock` (C8.5a baseline): ✓

### Source documentation

C8.12 is test-authoring + audit work; no new NVSR PDFs or NCHS user guides are CONSUMED. The substantive inputs are (i) the 11 validators' source code (already on disk; `git ls-files '*/05_validate/*.py'` exhaustive enumeration above); (ii) the 20 metadata CSVs (already on disk); (iii) the 97-row `docs/NCHS_SOURCE_MANIFEST.md` shipped at C8.11; (iv) the 4 harmonized + derived parquet schemas. No L9 cheap-checks on external PDFs required for this PRE-FLIGHT. ✓

The 97 raw NCHS zips on disk (`/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/` + `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` + `.../linked/`) are the B.11 SHA-stability test substrate. Each zip's SHA will be recomputed at DO time via `shasum -a 256`; comparison against the manifest is the test logic. No pre-DO L9 check required.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `tests/mutations/` (directory): does NOT exist ✓
  - `tests/mutations/__init__.py`: does NOT exist ✓
  - `tests/mutations/test_<validator_name>_mutation.py` (×7 — one per FAIL-surface validator): do NOT exist ✓
  - `tests/test_sha_stability.py` (or `tests/test_nchs_source_manifest.py`): does NOT exist ✓
  - `tests/test_column_snapshot.py` (B.12): does NOT exist ✓
  - `tests/test_inventory_year_consistency.py` (new L13 invariant motivated by C8.11 receipt FL-HALT #6 — see soft-flag (j) below; OPTIONAL — judge at DO whether scope-creep): does NOT exist ✓
  - `RECEIPTS/C8.12_<UTC>.md`: will be written at C8.12 RECEIPT phase (subsequent session(s))
- [x] **MAY BE MODIFIED (per-finding; cardinality = 3 L14-CANDIDATE validators + possible L13 audit findings; explicit intent recorded; current SHAs recorded for VERIFY phase):**
  - `fetal_death/scripts/05_validate/validate_2022.py` — L14-CANDIDATE patch (add `sys.exit(1 if has_fail else 0)`); current sha probed at DO baseline
  - `fetal_death/scripts/05_validate/validate_external.py` — L14-CANDIDATE patch
  - `natality/scripts/05_validate/validate_linked_parquets.py` — L14-CANDIDATE patch (NOTE: only 1 FAIL surface; needs DO-time inspection of whether the existing `print("  FAILURES:")` corresponds to a per-row failure indicator or just a status-block header — the patch may be no-op)
  - **FIX_LOG entries per finding** (L13 audit findings + L14 patches) — anticipated cascade per §15 halt-condition flags
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at PRE-FLIGHT close + further appends per DO/RECEIPT phases
  - `DECISION_LOG.md`: entries for any non-trivial design choices (e.g., test-directory structure, mutation-injection strategy choice, scope-resolution for the optional L13 invariant)
  - `FIX_LOG.md`: anticipated cascade entries per L13/L14 findings
  - `LESSONS.md`: NEW entry only if a new mistake class surfaces (not anticipated; §8 matrix already covers L3, L13, L14, H10)
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓ — C8.12 is test-authoring + script-edit, not data mutation
  - All C8.9 + C8.10a/b/c + C8.11 NEW files unchanged ✓
  - `harmonized_schema.csv` files unchanged ✓
  - `external_validation_targets_*.csv` files unchanged ✓
  - `docs/NCHS_SOURCE_MANIFEST.md` unchanged (consumed by B.11 test, not mutated) ✓
  - `docs/COMPARABILITY.md`, migration guides unchanged ✓
  - test suite baseline 56 PASS + 1 XFAIL preserved + new tests strictly additive ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.12 is test-authoring + L13/L14 audit; the substantive "fields" are (a) the 7 NEW mutation-test files; (b) any L14-patch line additions to 3 candidate validators; (c) the NEW SHA-stability test + snapshot-regression test files; (d) optional NEW L13 invariant test. Total snapshot rows: 20.

**Table 1: Validator inventory × B.6/B.8 audit surface (11 validators)**

| # | Validator | FAIL surface count | `sys.exit`/`SystemExit` on FAIL? | B.6 status | B.8 status |
|---|---|---|---|---|---|
| 1 | `fetal_death/scripts/05_validate/validate_2022.py` | 19 | **NO** | mutation-test target | **L14-CANDIDATE — patch needed** |
| 2 | `fetal_death/scripts/05_validate/validate_external.py` | 5 | **NO** | mutation-test target | **L14-CANDIDATE — patch needed** |
| 3 | `fetal_death/scripts/05_validate/validate_external_v2.py` | 2 | YES (`sys.exit(1)` line 394) | mutation-test target | OK |
| 4 | `natality/scripts/05_validate/compare_external_targets_v1.py` | 4 | YES (`raise SystemExit(2)` line 483) | mutation-test target | OK |
| 5 | `natality/scripts/05_validate/compare_external_targets_v3_linked.py` | 6 | YES (`raise SystemExit(1)` line 350) | mutation-test target | OK |
| 6 | `natality/scripts/05_validate/harmonized_missingness.py` | 0 (REPORT-ONLY) | N/A | SKIP (no FAIL surface) | OK |
| 7 | `natality/scripts/05_validate/key_rates_from_derived_core.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 8 | `natality/scripts/05_validate/qa_yearly_core_parquet.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 9 | `natality/scripts/05_validate/validate_linked_parquets.py` | 1 | **NO** (only print at line 248) | mutation-test target | **L14-CANDIDATE — patch needed (subject to DO-time inspection — may be no-op if the print is just a status-block header)** |
| 10 | `natality/scripts/05_validate/validate_row_counts_vs_nchs.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 11 | `natality/scripts/05_validate/validate_v1_invariants.py` | 6 | YES (`raise SystemExit(2)` line 885) | mutation-test target | OK |

**Summary:** 7 mutation-test targets (B.6) + 3 L14-CANDIDATE patches (B.8) + 4 REPORT-ONLY skip. Matches §15 anticipated FIX_LOG-cascade surface.

**Table 2: Metadata CSV inventory × B.7 L13 audit surface (20 CSVs)**

Fetal-death (16):
- `fetal_death/external_validation_targets.csv` — 88 → 90 (post-C8.2) NVSR-targets per task
- `fetal_death/file_inventory.csv` — 43 rows post-C8.11 (year × raw_filename × doc_filename × record_length)
- `fetal_death/harmonized_schema.csv` — 73 rows × 10 cols (years_available field is B.12 + new-L13-invariant candidate)
- `fetal_death/live_births_by_year.csv` — denominator file
- `fetal_death/record_layout_{1982_1988, 1992, 2003, 2004, 2006, 2014, 2022}.csv` — 7 era-layout files (byte-position metadata; L13-extension target per LESSONS 2026-05-12T01:40Z)
- `fetal_death/reporting_thresholds.csv` — state × year reporting thresholds
- `fetal_death/stratified_denominators.csv` — Task 1 joint-use output
- `fetal_death/validation_results.csv` — per-target PASS/FAIL
- `fetal_death/validation_tracking.csv` — adversarial verifier roster (DECISION_LOG history)
- `fetal_death/variable_crosswalk_working.csv` — per-era raw-to-harmonized mapping

Natality (4):
- `natality/metadata/external_validation_targets_v1.csv` — 183 NVSR-targets
- `natality/metadata/external_validation_targets_v3_linked.csv` — 35 NVSR-targets
- `natality/metadata/file_inventory.csv` — 54 rows (35 natality + 19 linked-cohort)
- `natality/metadata/harmonized_schema.csv` — 84 rows × 9 cols (no `domain` column unlike fetal-death's 10-col version)

**New L13 invariant candidate (per C8.11 receipt FL-HALT motivation; STATUS line 56 (i)):** `every year in file_inventory.csv` ⊆ `years_available in harmonized_schema.csv` — defends against future stale-inventory regressions analogous to the 34-vs-43 row gap that C8.11 PRE-FLIGHT surfaced. Filed as soft-flag (j) below; DO-time scope-resolution.

**Table 3: B.11 SHA-stability test target (97 raw zips via docs/NCHS_SOURCE_MANIFEST.md)**

| Section | Rows | Source path |
|---|---|---|
| Section 1 (Fetal-death) | 43 (year 1982-2024) | `/Users/.../fetal-death-harmonization-build/raw_data/fetal_death/Fetal<YYYY>US.zip` |
| Section 2 (Natality) | 35 (year 1990-2024) | `/Users/.../natality-harmonization/raw_data/Nat<YYYY>.zip` / `Nat<YYYY>us.zip` |
| Section 3 (Linked-cohort) | 19 (cohort year 2004-2023) | `/Users/.../natality-harmonization/raw_data/linked/<period>PE<cohort>CO.zip` |

Test logic: parse the 3 markdown tables (97 pipe-delimited rows); recompute `shasum -a 256` on each raw zip via the canonical absolute paths; assert byte-equality. The 97-row count is the floor invariant; any drift in zip count is a §7.11 halt at DO.

**Table 4: B.12 snapshot-regression test target (340 parquet columns)**

| Parquet | Columns | Sha-prefix anchor |
|---|---|---|
| `fetal_death_harmonized.parquet` | 73 | `38e2cecb…` |
| `fetal_death_derived.parquet` | 89 | `185c071e…` |
| `natality_v2_harmonized_derived.parquet` | 84 | `e16ad5323d…` |
| `natality_v3_linked_harmonized_derived.parquet` | 94 | `9b828a4d…` |

Test logic: per-column hash via pyarrow (e.g., `hashlib.sha256(arr.to_pylist().__repr__().encode()).hexdigest()` or a more memory-efficient streaming variant); store per-column SHA in a versioned snapshot file; subsequent runs assert byte-equality. **DECISION-PENDING at DO:** snapshot storage format (CSV vs JSON vs Parquet itself) and the per-release version policy (one snapshot per release, or rolling latest only). Filed as soft-flag (k) below.

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; zero amendments):**

1. **All 11 validators inventoried** matches the §15 PRE-FLIGHT-input claim "~13 across 5 scripts." Actual count: 11 across 2 subprojects' `05_validate/` directories. The §15 "~13" estimate is approximate but in the right ballpark; not an L11.
2. **The B.6 "tests/mutations/" directory does not yet exist** — matches §15 DO-scope "Per-validator mutation test in `tests/mutations/`."
3. **The B.8 L14 audit anticipated FIX_LOG cascade** matches §15 halt-condition flags. 3 candidates surfaced; one (`validate_linked_parquets.py`) is potentially a no-op pending DO-time inspection.
4. **The B.11 SHA-stability primary target this session = `docs/NCHS_SOURCE_MANIFEST.md`** (NOT `fetal_death/PROVENANCE.md` which is pre-V2.1 stale per soft-flag (a)). This is a session-scope decision: PROVENANCE refresh moves to Phase D step 2 per C8.11's soft-flag (a) routing. C8.12's B.11 test exercises the manifest shipped at C8.11.
5. **The B.12 snapshot-regression scope** = 4 parquets × 340 columns. No prior column-snapshot manifest exists; this is greenfield. **§15 hint** ("per-release versioned snapshot manifest") shapes the implementation choice but does not pre-determine the file format.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

- (h) **In-DO L11 (h) from C8.11** (year-set V3b+V2.1 correction): RESOLVED at C8.11 DO; preserved in receipt + STATUS + DECISION_LOG. No C8.12 action.
- (i) **`fetal_death/COMPARABILITY.md` title staleness** ("V2.0, 1992-2022" vs v2.4.0): Single-line fix-on-contact candidate. Could land at C8.12 if a B.7 L13 audit pass touches that file's role-claims; otherwise defer to Phase D step 2.
- (j) **NEW L13 invariant candidate**: "every year in `file_inventory.csv` ⊆ `years_available` in `harmonized_schema.csv`" — motivated by C8.11's 34-vs-43-row inventory gap. **DO-time scope-resolution**: include in B.7 audit-shipped invariants, OR defer to a future C8.X task. Recommendation: include (low cost; defends a known failure mode; the C8.11 receipt explicitly cites this as a C8.12 candidate input).
- (k) **B.12 snapshot storage format choice** (CSV/JSON/Parquet + release-versioning policy): DO-time DECISION_LOG entry required. Pre-DO recommendation: per-column SHA in a CSV at `tests/snapshots/v<X>_<UTC>_columns.csv`; CI compares latest run against the most-recent baseline; test PASSes if all columns match, FAILs with per-column diff list otherwise. Re-snapshot triggered by a §11 plan-update committing a new baseline (e.g., post-C8.13 dict-encoding reshape).
- (l) **`fetal_death/scripts/05_validate/validate_2022.py` is `DESIGN: frozen-at-task` candidate** — the existing module docstring may need a Convention-2 `DESIGN:` first-docstring tag at DO. Probe at DO; bundle into the L14 patch if needed.
- Carry-forward soft-flags from C8.11 (a)-(g) + (h) + (i): all preserved; none promoted to halt status by this PRE-FLIGHT. Phase D step 2 + future C8.X scope unchanged.

### Halt conditions tripped

**NONE.** Zero §7 halt conditions tripped at PRE-FLIGHT. The 3 L14-CANDIDATE validators surfaced at Table 1 are EXPECTED per §15 halt-condition flags ("Likely surfaces FIX_LOG cascades — budget for fix-on-contact"); they are anticipated scope, not surprise halts. Each becomes a §15-budgeted DO-step + paired FIX_LOG entry. The 20-CSV B.7 audit surface, 7-validator B.6 mutation surface, 340-column B.12 snapshot scope, and 97-zip B.11 substrate are all bounded enumerable scopes within §15's "3-4 sessions" budget. No L11 (no stale §15 PRE-FLIGHT-input claims; the only "~13 validators" approximation is benign). No L13 (all metadata CSVs identified with column names verified via shell). No L17 (no smoke pinning a stale annotation value). No §11 plan-update required.

### Result

**PROCEED** to C8.12 DO across subsequent 2-3 sessions. This session's scope ends at PRE-FLIGHT close + `C8.12-pre-do` tag placement. The next session begins DO with B.7 + B.8 audit (cheapest, surfaces FIX_LOG cascades) then B.11 + B.12 test authoring (medium) then B.6 mutation-test scaffolding (largest; 7 validators × paired mutation-test files; depends on B.8 patches landing first so the mutation-test runner can assume `sys.exit(1)` on FAIL).

Recommended DO sequencing across 3 sessions:
- **Session 1 (this PRE-FLIGHT close + early DO):** B.7 + B.8 audit + paired FIX_LOG cascade entries; one DECISION_LOG entry per non-trivial L13/L14 choice; soft-flag (j) L13 invariant scope-resolution.
- **Session 2:** B.11 SHA-stability + B.12 snapshot regression test authoring; CI integration verification (re-run `.github/workflows/ci.yml`-equivalent locally).
- **Session 3:** B.6 mutation-test scaffolding across 7 validators; Tier-0 mutation-test mutation-runner (AND-of-rows aggregation per L14).
- **Session 4 (optional, if cascade depth exceeds estimate):** overflow + RECEIPT + cumulative re-probe.

Per §4 discipline: tag `C8.12-pre-do` on the commit shipping this PRE-FLIGHT entry; DO commits will accumulate against the same task ID; `C8.12-complete` tag at RECEIPT close.

---

## PRE-FLIGHT for C8.11 — 2026-05-13T17:30:00Z — Migration guides + cross-product COMPARABILITY.md + cross-product NCHS-source-data SHA manifest (E.2 + E.4 + E.8) — **RESULT: PROCEED** (one §7.13-shape scope-affecting L11 surfaced + user-resolved via AskUserQuestion 2026-05-13T17:25:00Z Option A: extend `fetal_death/file_inventory.csv` 34 → 43 rows in C8.11 DO; three additional routine L11 PRE-FLIGHT-input re-interpretations user-authorized in-place per the C8.9/C8.10a/b/c precedent; no §11 plan-update commit needed)

### Scope summary

C8.11 §15.C entry (NEXT_STEPS.md lines 1168-1184) names 3 deliverables: (E.2) two migration guides — `migrations/v2.7.0-to-v2.8.0-natality.md` + (per §15) `migrations/v2.0.0-to-v2.3.0-fetal-death.md` re-targeted in PRE-FLIGHT to `migrations/v2.0.0-to-v2.4.0-fetal-death.md` (L11: §15 named v2.3.0 but actual current is v2.4.0 per fetal_death/README.md line 156 + DECISION_LOG 2026-05-13T01:30Z C8.2 latest-year refresh); (E.4) `docs/COMPARABILITY.md` at monorepo root synthesizing within_era + cross_era caveats from both subprojects; (E.8) `docs/NCHS_SOURCE_MANIFEST.md` at monorepo root containing raw-zip SHA-256 values for all 87 NCHS source files (43 fetal-death + 35 natality + 19 linked-cohort), keyed by year × raw_filename matching the inventory rows. KICKOFF.md Phase C Tier-2 line 192 + STATUS 2026-05-13T17:15:00Z line 68 name C8.11 as the next §15 task. Estimated effort 3-4 sessions per §15 (with the +30-60 min Option A inventory-extension addition).

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed in the way you think is best" + AskUserQuestion 17:25Z resolution Option A + (i)/(ii)/(iii) Proceed-in-place-per-precedent):** ship PRE-FLIGHT entry + tag `C8.11-pre-do` only; subsequent sessions will execute DO + VERIFY + RECEIPT across 4 deliverables (E.2a natality migration guide; E.2b fetal-death migration guide; E.4 cross-product COMPARABILITY; E.8a fetal_death/file_inventory.csv extension 34 → 43 rows; E.8b NCHS_SOURCE_MANIFEST.md) + 2 fix-on-contact mutations (VERSION_ROADMAP.md line 11 + 13 v2.1.0 → v2.4.0 + record count + coverage update) + cross-link edits (monorepo README.md + per-product README sections). This PRE-FLIGHT is metadata-only (PRE_FLIGHT_LOG.md addition); DO scope begins in the next session per the §4 five-phase discipline. C8.11-pre-do tag placed post-this-PRE-FLIGHT, pre-any-DO-mutation.

### Inputs

- [x] **All 12 C8.10c Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 3 C8.10c file SHAs + 14 C8.9 + 4 of 5 C8.10a/b file SHAs + 7 C8.10-tag presence). ✓
- [x] **Migration source-of-truth DECISION_LOG entries present** (4 substantive migrations to document):
  - `natality_v28_rename` — DECISION_LOG.md lines 926-1033 (2026-05-12T13:35:02Z + 2026-05-12T03:25:00Z PRE-FLIGHT findings); covers column renames (`year` → `data_year`; `restatus` → `residence_status`; `maternal_race_bridged4` → `maternal_race_bridged`; `maternal_hispanic_origin` → `hispanic_origin`); 61-string-literal rename surface; aliasing helper retained for v2.7.0 backward-compat per chosen alternative. ✓
  - `task3_v21_fetal_death` — DECISION_LOG.md line 1099+ (2026-05-12T01:35:00Z); covers V2.1 (adds 2003 + 2004 transition years; 1351-byte + 1501-byte mixed-revision layouts) + bundled H8 dtype reconciliation (5 columns: tabulation_flag, residence_status, maternal_age, maternal_race_bridged, hispanic_origin) + data_year field rename + monorepo path drift fixes. ✓
  - `task7_v3a` — DECISION_LOG.md line 882+ (2026-05-12T14:30:00Z); covers V3a 1989-1991 backward extension; B3 maternal_race_bridged 1989-rev MRACE 08→4 API, 09→null; 26/26 validation byte-exact. ✓
  - `task7_v3b` — DECISION_LOG.md line 800+ + 850+ (2026-05-12T18:30:00Z × 2); covers V3b 1982-1988 backward extension; B3 1978-rev MRACE 1-digit 0-9 → 4-cat bridged with code 7 + code 9 → null; DATAYEAR 2-digit → 4-digit expansion; 33/33 validation byte-exact. ✓
  - C8.2 latest-year refresh (2023+2024) is the implicit 5th migration step but per DECISION_LOG it's a data extension, not a schema or column-name change; surfaces in the migration guide as a "coverage extension" entry, not a "query update" entry. ✓
- [x] **Both subproject COMPARABILITY files present** (E.4 synthesis inputs):
  - `natality/docs/COMPARABILITY.md`: 41,736 bytes, last modified 2026-05-12 09:19. Top-level structure: Guiding policy + Comparability class definitions + certificate_revision values + Known structural breaks (line 34) + Variable decisions (line 78) + Recommended analytic subsets (line 192) + V3 Linked comparability (line 201) + Known pitfalls (line 279) + Change log (line 348). ✓
  - `fetal_death/COMPARABILITY.md`: 26,053 bytes, last modified 2026-05-04 21:58. Top-level structure: Era structure + 12 numbered sections covering 2003 revision transition / race+ethnicity / education / cause of death / gestational age / plurality / unrevised fields / BMI + morbidity / V2 cross-era code normalizations B1-B6 / V2 state-level reporting quirks / V2 stale-guide years (1996, 2001, 2002) + Variable Availability Matrix. ✓
- [x] **Both `file_inventory.csv` files present** (E.8 SHA-manifest inputs):
  - `natality/metadata/file_inventory.csv`: 54 data rows, 8 columns (`year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes`); year range 1990-2024; all 54 rows show `imported=true`; raw_filenames include 35 natality (`Nat<YYYY>.zip` / `Nat<YYYY>us.zip`) + 19 linked-cohort (`<YYYY>PE<YYYY-1>CO.zip`). ✓
  - `fetal_death/file_inventory.csv`: 34 data rows, 9 columns (`year, source_url, source_org, raw_filename, file_format, doc_filename, record_length, imported, notes`); year range 1989-2022; all 34 rows show `imported=no`. **STALE relative to v2.4.0 envelope (1982-2024 = 43 years; missing 7 V3b 1982-1988 + 2 latest-year 2023+2024 rows).** Option A resolution: extend to 43 rows in C8.11 DO; row-by-row metadata recoverable from DECISION_LOG entries above + per-zip probes. ✓ (with documented gap, scope-resolved per AskUserQuestion 17:25Z Option A)
- [x] **Raw zip universe on disk** (E.8 SHA-manifest target):
  - Fetal-death: 43 files at `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/Fetal<YYYY>US.zip` covering 1982-2024 inclusive (verified via `ls *.zip | wc -l`). ✓
  - Natality: 35 files at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` covering 1990-2024 (`Nat<YYYY>.zip` for 1990-1993; `Nat<YYYY>us.zip` for 1994+). ✓
  - Linked: 19 files at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/linked/` — directory presence verified via `find -maxdepth 4 -type d -name '*linked*'`; individual file listing not enumerated in PRE-FLIGHT (DO-step responsibility) but `2024PE2023CO.zip` is the most-recent inventory row per the file_inventory.csv `raw_filename` column. ✓
- [x] **Builder pattern templates** (E.2 + E.4 + E.8 authoring guides): `notebooks/_build_maternal_age_stratified_imr.py` + `notebooks/_build_preterm_outcomes_time_series.py` + `notebooks/_build_cross_race_fetal_mortality.py` (the C8.10a/b/c sibling builders) are NOT directly templates for C8.11 (C8.11 is docs-only, no executable builder), but their markdown-cell structure (intro + section headers + content + pass/fail summary) is a valid template for the migration-guide structure. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.11-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.10c Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.10c-complete` + parent `C8.10-complete` tags both present | ✓ | `git tag --list 'C8.10*'` shows 7 tags |
| 2 | `notebooks/_build_cross_race_fetal_mortality.py` sha=`aef0664f36a2a3a3…` | ✓ | matches exactly |
| 3 | `notebooks/cross_race_fetal_mortality.ipynb` sha=`262daef19494c03a…` | ✓ | matches exactly |
| 4 | `notebooks/README.md` sha=`6fc9b191c6a5a9d4…` | ✓ | matches (parent C8.10 marked COMPLETE) |
| 5 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb…` / fd_der=`185c071e…` / nat_der=`e16ad53…` / linked_der=`9b828a4d…` all match (linked parquet correct path is `natality_v3_linked_harmonized_derived.parquet`, not the C8.10c receipt's `linked_birth_infant_death_v3_cohort_derived.parquet` placeholder name — same file, different display name; sha confirms byte-identity) |
| 6 | 14 C8.9 file SHAs + 4 of 5 C8.10a+C8.10b file SHAs unchanged | ✓ | All 14 + 4 verified; `notebooks/README.md` is the 5th C8.10a/b file (drifted intentionally to `6fc9b191…` — HALT #4 above) |
| 7 | Next task = C8.11 | ✓ | This entry executes |
| 8 | §15 PRE-FLIGHT-input re-verification discipline in 4th consecutive application | ✓ | Now 5th (this PRE-FLIGHT surfaces 4 L11 cases) |
| 9 | In-PRE-FLIGHT secondary-source-validation re-interpretation pattern | ✓ | LESSONS.md backport candidate; carried forward |
| 10 | 2014 race-coding-methodology boundary distinct from OE | ✓ | C8.11 C8.11 DO will incorporate into E.4 docs/COMPARABILITY.md synthesis |
| 11 | `notebooks/README.md` Planned section still includes era_boundary stub | ✓ | Out of active Phase C scope; not touched here |
| 12 | Cumulative Phase C effort ~12 of 29-35 sessions (~36%) | ✓ | C8.11 PRE-FLIGHT is ~12.1 of 29-35; comfortably within 42 cap |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: 4.5.0 (R quickstart fixtures landed at C8.9; not exercised by C8.11 which is docs-only)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] DuckDB Python: present (C8.9 lockfile addition) ✓ (not exercised by C8.11)
- [x] Working directory clean (`git status --short` empty on `main` at `2dd19ac`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.10c-complete` + `C8.10-complete` (verified via `git tag --points-at HEAD`) ✓

### Source documentation

C8.11 is docs-authoring; no new NVSR PDFs or NCHS user guides are CONSUMED beyond what's already cited via the DECISION_LOG entries. The 4 migration source-of-truth DECISION_LOG entries above are the substantive inputs. No L9 cheap-checks on external PDFs are required by this PRE-FLIGHT — all source documents are internal (DECISION_LOG entries + COMPARABILITY files + file_inventory.csv files). ✓

The E.8 SHA manifest will record SHAs of raw NCHS zips by computing them at DO time; raw zips themselves are the L9 source-of-truth (NCHS canonical FTP paths recorded in each inventory's `source_url` column). Each zip's SHA-256 is computed at DO; no pre-DO L9 check required.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `migrations/` (directory): does NOT exist ✓
  - `migrations/v2.7.0-to-v2.8.0-natality.md`: does NOT exist ✓
  - `migrations/v2.0.0-to-v2.4.0-fetal-death.md`: does NOT exist ✓ (re-targeted from §15 v2.3.0 per L11 finding (i))
  - `docs/COMPARABILITY.md` (monorepo root): does NOT exist ✓
  - `docs/NCHS_SOURCE_MANIFEST.md` (monorepo root): does NOT exist ✓ (E.8 filename chosen for E.8 deliverable; follows `docs/JOINT_USE_GUIDE.md` + `docs/PRIOR_ART.md` precedent of monorepo-cross-product docs at `docs/`)
  - `RECEIPTS/C8.11_<UTC>.md`: will be written at C8.11 RECEIPT phase (next session(s))
- [x] **MODIFIED files (explicit intent; current SHAs recorded for VERIFY phase):**
  - `fetal_death/file_inventory.csv` (current 34 rows; target 43 rows per Option A): current size 6905 bytes, sha computed at DO baseline; rows 35-43 to be appended ✓
  - `VERSION_ROADMAP.md` line 11 + line 13 (fix-on-contact per L11 finding (iii)): current `**v2.1.0** (adds 2003 + 2004; H8 dtype reconciliation) | v2.0.0 | 1992–2022 | 1,741,977` → target `**v2.4.0** (V2.1 2003+2004 + V3a 1989-1991 + V3b 1982-1988 + latest-year refresh 2023+2024; H8 dtype reconciliation) | v2.0.0 | 1982–2024 | 2,427,233`; line 13 substring `fetal-death v2.1.0` → `fetal-death v2.4.0` ✓
  - `README.md` (monorepo): add cross-link to `migrations/` + `docs/COMPARABILITY.md` + `docs/NCHS_SOURCE_MANIFEST.md` in the Repository Layout section (additive only) ✓
  - `fetal_death/README.md`: add cross-link to `../migrations/v2.0.0-to-v2.4.0-fetal-death.md` (1 line in Version Roadmap section near line 156) ✓
  - `natality/README.md`: add cross-link to `../migrations/v2.7.0-to-v2.8.0-natality.md` (1 line near line 28 v2.8.0 mention) ✓
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `STATUS.md`: new dated section at top with C8.11 close
  - `DECISION_LOG.md`: new entry recording the AskUserQuestion 17:25Z Option A authorization + three (i)/(ii)/(iii) in-place L11 resolutions
  - `PRE_FLIGHT_LOG.md`: this entry (already written before DO begins)
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓
  - 14 C8.9 + 5 C8.10a/b/c file SHAs unchanged ✓
  - `harmonized_schema.csv` files unchanged (E.2 docs reference the schema but do not mutate it) ✓
  - `external_validation_targets_*.csv` files unchanged ✓
  - test suite 56 PASS + 1 XFAIL preserved (cache-cleared run at VERIFY) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.11 is docs-authoring; the substantive "fields" are (a) the 4 NEW document contents (target schema established by §15 + Option A scope refinements); (b) the 9 NEW rows for `fetal_death/file_inventory.csv`; (c) the 2 fix-on-contact VERSION_ROADMAP.md line substitutions; (d) cross-link edits to 3 README files. Total snapshot rows: 24.

**Table 1: Migration-guide content sources (E.2a + E.2b; per-migration source DECISION_LOG entries verified above)**

| # | Migration | §15 named | PRE-FLIGHT-target (L11 finding (i)) | DECISION_LOG source | Status |
|---|---|---|---|---|---|
| 1 | Natality column renames | `v2.7.0-to-v2.8.0-natality.md` | unchanged | `natality_v28_rename` 2026-05-12T13:35:02Z + 03:25:00Z PRE-FLIGHT | ✓ source present |
| 2 | Fetal-death V2.1 transition | `v2.0.0-to-v2.3.0-fetal-death.md` (stale §15 name) | `v2.0.0-to-v2.4.0-fetal-death.md` (covers V2.1 + V3a + V3b + latest-year as one envelope migration) | `task3_v21_fetal_death` 2026-05-12T01:35:00Z | ✓ source present |
| 3 | Fetal-death V3a backward | (subsumed in #2) | (subsumed in #2) | `task7_v3a` 2026-05-12T14:30:00Z | ✓ source present |
| 4 | Fetal-death V3b backward | (subsumed in #2) | (subsumed in #2) | `task7_v3b` 2026-05-12T18:30:00Z × 2 entries | ✓ source present |
| 5 | Fetal-death latest-year 2023+2024 | (not in §15) | (subsumed in #2 as "data envelope extension") | `C8.2 latest-year refresh` 2026-05-13T01:30:00Z | ✓ source present |

**Table 2: Cross-product COMPARABILITY synthesis cells (E.4; era-boundary union)**

| # | Era boundary | Both products affected? | Source section(s) | Resolution |
|---|---|---|---|---|
| 6 | 2003 revision transition (natality + fetal-death) | both | nat COMPARABILITY §"certificate_revision values" + fd COMPARABILITY §1 "2003 Revision Transition" | E.4 synthesizes both narratives |
| 7 | OE-based gestational age methodology shift (2014+) | natality + linked | nat COMPARABILITY §"Variable decisions" + manuscript §"OE methodology" | E.4 cross-references C8.10b notebook narrative |
| 8 | Race-coding methodology boundary (2014; Hispanic disaggregation) | both | C8.10c notebook narrative (new this PR; not yet in either COMPARABILITY file) | E.4 imports the C8.10c narrative as the canonical source — synthesizes for the first time |
| 9 | Bridged-race null 2018+ (natality) vs 2014+ (fetal-death) | both | nat COMPARABILITY + fd COMPARABILITY §2 "Race and Ethnicity" | E.4 unifies the era-end-dates table |
| 10 | V1 era plurality coding (2005-2013) | fetal-death only | fd COMPARABILITY §7 "Plurality — Data Quality Caveats" | E.4 documents as fetal-death-specific |
| 11 | V2 state-level reporting quirks (1992-2002) | fetal-death only | fd COMPARABILITY §11 | E.4 documents as fetal-death-specific |
| 12 | 1989-1991 V3a + 1982-1988 V3b race-coding | fetal-death only | fd COMPARABILITY §2 + new DECISION_LOG 2026-05-12T14:30Z + 18:30Z + new C8.10c narrative | E.4 imports new caveats (B3 1-digit-recode for V3b code 7 + code 9 → null; V3a code 09 → null) |

**Table 3: fetal_death/file_inventory.csv extension rows (E.8a per Option A; 9 NEW rows)**

| # | year | raw_filename | doc_filename | record_length | imported | source DECISION_LOG |
|---|---|---|---|---|---|---|
| 13 | 1982 | `Fetal1982US.zip` | `1982FetalUserGuide.pdf` | 365 (probe at DO) | no | task7_v3b 2026-05-12T18:30Z |
| 14 | 1983 | `Fetal1983US.zip` | `1983FetalUserGuide.pdf` | 365 | no | same |
| 15 | 1984 | `Fetal1984US.zip` | `1984FetalUserGuide.pdf` | 365 | no | same |
| 16 | 1985 | `Fetal1985US.zip` | `1985FetalUserGuide.pdf` | 365 | no | same |
| 17 | 1986 | `Fetal1986US.zip` | `1986FetalUserGuide.pdf` | 365 | no | same |
| 18 | 1987 | `Fetal1987US.zip` | `1987FetalUserGuide.pdf` | 365 | no | same |
| 19 | 1988 | `Fetal1988US.zip` | `1988FetalUserGuide.pdf` | 365 | no | same |
| 20 | 2023 | `Fetal2023US.zip` | (TBD probe at DO) | (TBD probe at DO) | no | C8.2 2026-05-13T01:30Z |
| 21 | 2024 | `Fetal2024US.zip` | (TBD probe at DO) | (TBD probe at DO) | no | same |

Record-length values: each new row's record_length will be probed at DO time via `unzip -p <zip> | head -c 1 | wc -c` or equivalent first-record-byte-length detection. The "365" placeholder for 1982-1988 is the standard 1978-revision record length per the user guides on disk; DO probe confirms. ✓

**Table 4: VERSION_ROADMAP.md fix-on-contact (E.2 ancillary per L11 finding (iii))**

| # | Line | Current text (verbatim) | Target text |
|---|---|---|---|
| 22 | 11 | `\| Fetal death \| **v2.1.0** (adds 2003 + 2004; H8 dtype reconciliation) \| v2.0.0 \| 1992–2022 \| 1,741,977 \| [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) (v2.0.0) \|` | `\| Fetal death \| **v2.4.0** (V2.1 2003+2004 + V3a 1989-1991 + V3b 1982-1988 + latest-year refresh 2023+2024; H8 dtype reconciliation) \| v2.0.0 \| 1982–2024 \| 2,427,233 \| [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) (v2.0.0) \|` |
| 23 | 13 | `The natality v2.8.0 and fetal-death v2.1.0 in-repo states are pending Zenodo deposit.` | `The natality v2.8.0 and fetal-death v2.4.0 in-repo states are pending Zenodo deposit.` |

**Table 5: Cross-link edits to existing READMEs (additive only)**

| # | File | Line approx | Edit |
|---|---|---|---|
| 24 | `README.md` (monorepo) | line 22-49 Repository Layout block | append `migrations/`, `docs/COMPARABILITY.md`, `docs/NCHS_SOURCE_MANIFEST.md` entries to the tree diagram + 1-line description rows |

(Per-product README cross-link edits at `fetal_death/README.md` near line 156 + `natality/README.md` near line 28 are similarly single-line additive cross-link insertions; not separately enumerated.)

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet + AskUserQuestion 17:25Z user authorization):**

1. **(i) Migration guide filename — RESOLVED in-place per user authorization 17:25Z option "Proceed in-place per precedent."** §15 named `v2.0.0-to-v2.3.0-fetal-death.md`; PRE-FLIGHT re-targets to `v2.0.0-to-v2.4.0-fetal-death.md` since fetal-death actual current version is v2.4.0 per fetal_death/README.md line 156 + DECISION_LOG 2026-05-13T01:30Z. Routine L11 PRE-FLIGHT-input re-interpretation per the C8.9/C8.10a/b/c precedent.
2. **(ii) E.8 SHA manifest scope — RESOLVED in-place per same user authorization.** §15 VERIFY says "SHA manifest checksums match each subproject's file_inventory.csv"; PRE-FLIGHT verified neither file_inventory.csv contains a sha256 column. Resolution: SHA manifest is NEW data (raw-zip SHAs keyed by year × raw_filename), NOT a re-export of file_inventory.csv. The "match each subproject's file_inventory.csv" criterion means the manifest's row keys (year + raw_filename) align 1:1 with each inventory's rows. Manifest target path: `docs/NCHS_SOURCE_MANIFEST.md` (following the monorepo-docs `docs/JOINT_USE_GUIDE.md` + `docs/PRIOR_ART.md` precedent).
3. **(iii) VERSION_ROADMAP.md fetal-death version line — RESOLVED in-place per same user authorization.** Lines 11 + 13 carry stale v2.1.0 + 1992-2022 + 1,741,977 record-count claims; the actual current state is v2.4.0 + 1982-2024 + 2,427,233 records. Fix-on-contact at C8.11 DO; bundled into the E.2 fetal-death migration guide cross-link since the migration guide will reference VERSION_ROADMAP.md as the version-table source-of-truth.
4. **(A) Inventory extension — RESOLVED via AskUserQuestion 17:25Z Option A.** `fetal_death/file_inventory.csv` will be extended from 34 → 43 rows in C8.11 DO. The 9 NEW rows cover 7 V3b years (1982-1988) + 2 latest-year (2023-2024). Row metadata derived from DECISION_LOG entries (Table 1 above) + per-zip probes at DO. ~30-60 min addition; brings C8.11 estimated effort to ~3.5-4 sessions (within §15 "3-4 sessions" envelope at the upper bound). C8.11 SHA manifest then covers the full 43-year fetal-death envelope cleanly.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope for C8.11; carried forward to Phase D pre-Zenodo):**

- (a) **fetal_death/PROVENANCE.md** (4830 bytes) + **fetal_death/PROVENANCE.sha256** (33-line file) are STALE relative to v2.4.0 — last updated 2026-05-05 covering only the v2.0.0 release artifacts (file SHAs reflect pre-V2.1 + pre-V3a + pre-V3b + pre-latest-year-refresh state). The current `fetal_death_harmonized.parquet` sha=`38e2cecb…` and `fetal_death_derived.parquet` sha=`185c071e…` do NOT match the PROVENANCE.md-listed `f09beb4a…` + `90af89b9…`. The PROVENANCE.sha256 self-coverage promise ("verify everything else") fails on the current v2.4.0 build. **OUT-OF-SCOPE for C8.11** (which focuses on RAW NCHS source data, not output artifact PROVENANCE per §15 "NCHS-source-data SHA manifest" phrasing); soft-flag for Phase D step 2 (Zenodo deposit refresh) where the natural fix is re-running `shasum -a 256` on the v2.4.0 deposit-bound files and rebuilding both PROVENANCE.md + PROVENANCE.sha256 to match. Filed as Phase D pre-Zenodo deliverable.
- (b) **Natality has NO PROVENANCE.md** (verified: `ls natality/PROVENANCE.md natality/docs/PROVENANCE.md` both "No such file or directory"). The Zenodo v2.7.0 deposit ships a PROVENANCE.md, but it's NOT in the monorepo natality/ directory (lives only in the Zenodo archive). The current monorepo state has no natality output-artifact SHA manifest at all — making cross-product output-SHA verification asymmetric. Same OUT-OF-SCOPE classification as (a); same Phase D step 2 resolution (author natality/PROVENANCE.md as part of unified Zenodo deposit).
- (c) **VERSION_ROADMAP.md "Planned" section (lines 15-22)** still lists "Fetal death V2.1 — add 2003 and 2004 transition years" as a PLANNED item. This is more than the line-11+13 fix-on-contact authorized; the whole "Planned" section needs review since multiple items have shipped (V2.1 done; V3a done; V3b done). **OUT-OF-SCOPE for C8.11 per Anti-Pattern #8** (compressed-task avoidance); soft-flag for a future small VERSION_ROADMAP refresh task. Authorized fix-on-contact at C8.11 DO covers ONLY lines 11 + 13.
- (d) **C8.7a documented finding** `fetal_death/scripts/run_pipeline.py` ALL_YEARS=29 stale relative to v2.4.0's 43-year envelope; deferred to C8.7b orchestrator authoring. Soft-flag: the C8.11 fetal-death migration guide can NAME the v2.4.0 envelope explicitly to help users with legacy v2.0.0 code understand the year extension (~1 paragraph). Not a separate deliverable; integrated narrative.
- (e) **Monorepo `raw_data/` symlink** only links `raw_data/fetal_death -> /Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/fetal_death`; no natality + linked symlink (C8.7a finding). The C8.11 E.8 manifest's SHA computation will need to read 87 zips from 3 absolute paths (43 from fetal-death build dir; 35 from natality build dir; 19 from natality build dir's linked/ subdir). Not a halt — DO-step responsibility to enumerate; documented for the DO author.
- (f) **Plurality footgun for natality**: the natality + linked file's plurality-coding anomaly (C.6.e candidate notebook from C8.15) is in scope for E.4 cross-product COMPARABILITY synthesis — fd COMPARABILITY §7 names it as fetal-death-specific, but the same NCHS sentinel pattern likely applies to natality 2005-2013. Soft-flag for E.4 author to investigate during DO; not pre-resolved.
- (g) **Carry-forward soft-flags from C8.10c** (C8.2 NCHS 2025PE2024CO release; C8.3 manuscript line 99; C8.4 linked-vs-natality drift bound; C8.5a-a/b/c; C8.6-a/b; C8.7a-a/b/c; C8.8-a/b/c/d; C8.9-a/b/c/d/e; C8.10a-a/b/c/d/e; C8.10b-a/b/c/d; C8.10c-a/b/c/d/e). All preserved; none promoted to halt status by this PRE-FLIGHT.

### Halt conditions tripped

One §7.13-shape scope-affecting L11 surfaced (Option A inventory extension) + three additional routine L11 PRE-FLIGHT-input re-interpretations ((i) + (ii) + (iii)) — all four user-resolved via AskUserQuestion 2026-05-13T17:25:00Z. User selected:
- Question 1: **(A) Extend inventory to 43 rows in C8.11 DO (Recommended)** — resolves L11 finding #4 (file_inventory.csv stale)
- Question 2: **Proceed in-place per precedent (Recommended)** — resolves L11 findings (i)/(ii)/(iii)

No unresolved §7 condition. Convention 3 Field-value snapshot above documents all 24 mutation targets + their current vs. assumed-state verification. Convention 4 carry-over verification of all 12 C8.10c Forward-looking HALTs returned byte-exact.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.10c forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 24 rows across 5 tables (5 migration-content sources + 7 COMPARABILITY synthesis cells + 9 inventory-extension rows + 2 VERSION_ROADMAP fix-on-contact + 1 cross-link); one §7.13-shape condition + 3 routine L11s surfaced + user-resolved via AskUserQuestion 17:25Z (Option A inventory extension + in-place L11 resolutions per the C8.9/C8.10a/b/c precedent). Tag `C8.11-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag in subsequent session(s) per the §15 3-4 session estimate (with Option A +30-60 min). 7 soft-flags (a)-(g) surfaced and filed for Phase D / future-task resolution; none are PRE-FLIGHT halts.

---

## PRE-FLIGHT for C8.10c — 2026-05-13T16:30:00Z — Worked-example notebook 3 of 3 (C.6.c `cross_race_fetal_mortality.ipynb`; V3a/V3b race-stratified FD demo with B3 1-digit-recode caveats + cross-era time series + 2022 single-race + Hispanic NVSR-cell cross-validation) — **RESULT: PROCEED** (one §7.13 condition surfaced + user-resolved via AskUserQuestion 2026-05-13T16:15:00Z Option A; in-PRE-FLIGHT re-interpretation per C8.9/C8.10a/b L11 discipline; no §11 plan-update commit needed; 7 NVSR-equivalent cells available via `joint_use_demo.ipynb` Section B precedent — exceeds §15 "≥3" minimum)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164) is the composite 3-notebook task; this PRE-FLIGHT covers **sub-task C8.10c** (C.6.c `cross_race_fetal_mortality.ipynb`) per the sub-receipt convention established at C8.10a + C8.10b (PRE_FLIGHT_LOG 2026-05-13T14:29:23Z + 14:57:02Z). KICKOFF.md Phase C Tier-2 line 191 + §15.C C8.10 entry name C.6.c as the 3rd sub-notebook ("V3a/V3b demo; race-stratified FD; documents the B3 1-digit-recode caveats"). STATUS 15:18:46Z line 62 names C.6.c as the next sub-task.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed" + AskUserQuestion 16:15Z Option A):** ship notebook 3 of 3 (C.6.c) end-to-end through RECEIPT + parent `C8.10-complete` tag. Scope refined per Option A: (i) reproduce the 7 NVSR 73-09 Table A 2022 race-stratified FMR cells (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) from `joint_use_demo` Section B precedent as the current-era cross-reference validation backbone; (ii) extend to a 1982-2024 race-stratified FMR time series across V3b + V3a + V2 + V1 eras using `maternal_race_bridged` (1982-2013) + `race_hispanic_revised` collapsed to 4-cat bridged (2014+) as the cross-era continuity bridge; (iii) document the B3 1-digit-recode caveats inline (V3b code 7 + code 9 → null per DECISION_LOG 2026-05-12T18:30Z; V3a code 09 → null per DECISION_LOG 2026-05-12T14:30Z); (iv) machinery demo asserts (per-era row-count + bridged-race conservation: sum-across-4-cats + null = total per era).

### Inputs

- [x] **All 12 C8.10b Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 5 C8.10a/b file SHAs + 14 C8.9 file SHAs + tag presence). ✓
- [x] **Fetal-death derived parquet** (v2.4.0; 43-yr 1982-2024 with V3a + V3b extension applied) present; sha=`185c071ec76ab8aa…`; 2,427,233 rows × 89 cols. Probed `maternal_race_bridged` (Int8 dtype; values 1-4 + NA): distribution 1=1,439,008 / 2=561,232 / 3=12,602 / 4=100,305 / NA=314,086. Probed `race_hispanic_revised` (string dtype; codes '1'-'8' + empty): distribution 1=185,989 / 2=117,516 / 3=2,600 / 4=22,042 / 5=1,505 / 6=4,789 / 7=80,803 / 8=56,718 / ''=1,955,271 (pre-2014 null). ✓
- [x] **V3a baseline parquet** present at `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.V3a_baseline.parquet`; sha=`0dd3aec0e47785f1…`; 29,350,962 bytes. **V3b baseline parquet** present; sha=`4d1b37cc3a214eea…`; 34,011,022 bytes. **Both are PRE-EXTENSION sidecar snapshots; the notebook will NOT use them** — the active v2.4.0 parquet (`fetal_death_derived.parquet`) already has V3a + V3b extension applied. Sidecar SHAs recorded for PROVENANCE-trace reference only. ✓
- [x] **Natality v2.8.0 derived parquet** present; sha=`e16ad5323d68e28d…`; 138,819,655 rows × 84 cols. Needed for denominator (live births by race-class for FMR computation). Same race columns as joint_use_demo Section B: `maternal_race_ethnicity_5` + `maternal_race_detail` (for Asian/NHOPI split in 2003-rev OMB classification 2022+). ✓
- [x] **Validation source for NVSR-equivalent cells (per Option A re-interpretation)**: `notebooks/_build_joint_use_demo.py` Section B at lines 230-310 encodes 7 NVSR 73-09 Table A 2022 target rates (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) + the canonical race-class derivation logic. C.6.c reproduces these 7 cells from the same parquets using identical canonical filters + derivation logic; cross-validates the byte-exact-from-joint_use_demo result; then extends to the cross-era 1982-2024 time series. **7 cells × byte-exact-validation = exceeds §15 "≥3" minimum.** ✓
- [x] **Validation CSVs** `fetal_death/external_validation_targets.csv` (87 rows), `natality/metadata/external_validation_targets_v1.csv` (245 rows), `natality/metadata/external_validation_targets_v3_linked.csv` (53 rows) — **zero race-stratified cells in all three** (confirmed via cheap-check). This is the §7.13 surface that triggered AskUserQuestion 16:15Z; resolution = use `joint_use_demo` Section B precedent instead.
- [x] **Builder template** `notebooks/_build_preterm_outcomes_time_series.py` (C8.10b sibling; sha=`3bc2a8f1731f913e…`) + `_build_maternal_age_stratified_imr.py` (C8.10a; sha=`9db692743e050189…`) + `_build_joint_use_demo.py` (cross-product 3-parquet sibling with the Section B race-class logic + 7-cell validation table) all present and structurally identical. ✓
- [x] **DECISION_LOG B3 1-digit-recode references**: 2026-05-12T14:30:00Z (V3a code 09 → null; 165 records across 1989-1991 = 0.087%) + 2026-05-12T18:30:00Z (V3b code 7 → null ~89 records; V3b code 9 → null ~18,700 records / 3-5% per year). Both cited as load-bearing for the notebook's caveat narrative. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10c-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.10b Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.10b-complete` tag present; `C8.10c-pre-do` absent | `git tag --list 'C8.10*'` → C8.10a-pre-do + C8.10a-complete + C8.10b-pre-do + C8.10b-complete; no C8.10c-pre-do | ✓ |
| 2 | `notebooks/_build_preterm_outcomes_time_series.py` sha=`3bc2a8f1731f913e…` (31,266 bytes) | verified | ✓ |
| 3 | `notebooks/preterm_outcomes_time_series.ipynb` sha=`724cb46b17edab65…` (90,549 bytes) | verified | ✓ |
| 4 | `notebooks/README.md` sha=`5a0a8b4b291214cc…` (5,948 bytes) | verified | ✓ |
| 5 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 6 | All 14 C8.9 + 2 of 3 C8.10a file SHAs unchanged | C8.9 batch (R quickstarts ×3 + views.sql + JOINT_USE_GUIDE + pyproject + uv.lock + .python-version + README + ci.yml + validate_2022 + run_pipeline + CHANGELOG + PRIOR_ART) ✓; C8.10a builder `9db692743e050189…` ✓; C8.10a ipynb `036de6b4b927e586…` ✓ (notebooks/README.md drifted intentionally per C8.10a HALT #11) | ✓ |
| 7 | Next task = C8.10c per KICKOFF.md line 191 + STATUS 15:18:46Z line 62 | confirmed; this entry executes | ✓ |
| 8 | Parent C8.10 §15 task ships across 3 sub-receipts; after C8.10c append parent `C8.10-complete` tag | confirmed convention; planned for this session | ✓ |
| 9 | §15 PRE-FLIGHT-input re-verification discipline (C8.9-surfaced L11) | **executed below — surfaced §7.13 condition, user-resolved via AskUserQuestion Option A** | ✓ |
| 10 | L13 CSV-formatting workaround: `external_validation_targets_v1.csv` unquoted commas → `engine='python', on_bad_lines='skip'` | C.6.c will not consume that CSV (no race cells in it; all FD validation via in-builder NVSR-cell table from joint_use_demo) — workaround N/A this session | ✓ N/A |
| 11 | `notebooks/README.md` Planned section `era_boundary_walkthrough.ipynb` stub | confirmed unchanged; out of active Phase C scope | ✓ informational |
| 12 | Cumulative Phase C effort ~11 of 29-35 sessions (~33%) | this session targets ~1-1.5; budget healthy (cap 42 sessions) | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`f349c82` (C8.10b-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (unchanged from C8.9). ✓
- [x] `nbformat` + `nbclient` available (verified at C8.10a/b builder execution; not separately re-probed). ✓

### Source documentation (L9 cheap-check + §7.13 condition + user-authorized resolution)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether an NVSR PDF is on disk. C8.10a + C8.10b established the durable resolution: validation cells come from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment. **C8.10c application of the same probe routine surfaces a §7.13 condition**: the encoded CSVs have ZERO race-stratified cells for the V3a/V3b 1982-1991 era this notebook centers on. Resolution required AskUserQuestion (Option A chosen).

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. Zero NVSR PDFs on disk (unchanged from C8.10a/b — open soft-flag (a) carried forward).

**Probe B — FD validation CSV race-cell inventory.** `grep -iE "race|hispanic|white|black|aian|asian|nhopi" fetal_death/external_validation_targets.csv` → **zero matches**. The 87 rows cover: fetal_deaths_gte20wk_resident (34 cells × 1989-2022); fetal_mortality_rate (26 cells); maternal-age bands (8 cells × 2022); sex (2 cells × 2022); plurality (3 cells × 2022); cause-of-death codes P00/P01/P02/P95/Q00-Q99 (5 cells); early/late gestation (4 cells × 2014+2022). **No race stratification at any year.**

**Probe C — Natality v1 + linked v3 validation CSV race-cell inventory.** `grep -iE "race|hispanic|nhwh|nhbl|aian|asian" natality/metadata/external_validation_targets_v1.csv natality/metadata/external_validation_targets_v3_linked.csv` → **zero matches** (245 + 53 rows respectively).

**Probe D — DECISION_LOG cross-reference for race-stratified V3a/V3b cell availability.** `grep -inE "Series 21|race-stratified|race.*post-submission" DECISION_LOG.md` → DECISION_LOG 2026-05-12T14:30:00Z (V3a B3 recode) line 916: *"NVSR Volume 41/42/43 or NCHS Series 21 reports for 1989-1991 race-stratified fetal death tables is post-submission scope"*; DECISION_LOG 2026-05-12T18:30:00Z (V3b B3 recode) line 841: similar deferral for 1982-1988. **Confirmed: race-stratified V3a/V3b cell L9-cheap-check is explicit post-submission scope.**

**Probe E — `joint_use_demo.ipynb` Section B precedent inventory.** `notebooks/_build_joint_use_demo.py` lines 239-310 encode 7 NVSR 73-09 Table A 2022 target rates with full canonical-filter + race-class derivation logic (single-race + Hispanic 6-cat: AIAN / Asian / Black / NHOPI / White / Hispanic + Total) using `race_hispanic_revised` for fetal deaths + (`maternal_race_ethnicity_5` × `maternal_race_detail`) for natality denominators. Joint_use_demo notebook was ALREADY validated byte-exact at its shipping moment (Task 2 receipt 2026-05-11). **These 7 cells are the available NVSR-equivalent validation backbone for C.6.c.**

**§7.13 condition surfaced.** §15 C8.10 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" — for C.6.c's V3a/V3b race-stratified focus — has no encoded CSV source. The C8.10a/b in-PRE-FLIGHT re-interpretation (point at already-L9-checked CSV entries) FAILS because all three CSVs are empty for race cells. Adding new V3a/V3b NVSR race cells via PDF L9-cheap-check is explicit post-submission scope per DECISION_LOG. **Per §7 binding rule, halt-and-ask.**

**AskUserQuestion 2026-05-13T16:15:00Z** — three options offered: (A) Re-scope to cross-era demo + 2022 cross-val using joint_use_demo Section B 7 cells as validation backbone (Recommended; ~1-1.5 sessions; in-PRE-FLIGHT re-interpretation, no §11 plan-update); (B) Expand scope to L9-probe NVSR Vol 41/42/43 + add new V3a/V3b race cells to FD CSV (~2-3 sessions; §11 plan-update + canonical-state mutation; trips Q33 effort-ceiling watch); (C) DROP C.6.c (parent C8.10 closes 2-of-3 sibling of C8.9's C.1 drop; §11 plan-update; loses V3a/V3b race-stratified demo value).

**User-authorized resolution: Option A.** Documented in receipt (no §11 plan-update commit). C.6.c reproduces 7 NVSR-equivalent cells from joint_use_demo Section B precedent + extends to 1982-2024 cross-era time series + documents B3 1-digit-recode caveats. The L11 in-PRE-FLIGHT re-interpretation pattern is generalized: when the encoded CSV lacks the relevant cells for a notebook's chosen era/strata, the validation backbone may be drawn from a sibling notebook's already-validated byte-exact result, treated as the L9-cheap-checked source. This is a STRICT-LESS resolution than C8.10a/b's CSV reference (which is the canonical primary source); the joint_use_demo precedent is a SECONDARY source, but its byte-exact validation at Task 2 makes it a legitimate L9-equivalent.

### Outputs

- **NEW**: `notebooks/_build_cross_race_fetal_mortality.ipynb_builder.py` (deterministic builder, ~450-500 lines; sibling pattern from `_build_joint_use_demo.py` for the race-class derivation logic + `_build_maternal_age_stratified_imr.py` for the time-series machinery). Filename TBD at DO; likely `notebooks/_build_cross_race_fetal_mortality.py`.
- **NEW**: `notebooks/cross_race_fetal_mortality.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` (replace C.6.c "planned" stub with shipped entry; update Status section to mark C8.10 parent COMPLETE; current sha=`5a0a8b4b291214cc…` will drift; recorded post-DO).
- **NEW**: `RECEIPTS/C8.10c_<UTC>.md` (per-notebook sub-task receipt; parent `C8.10-complete` tag follows).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` append (this entry).
- **Tags**: `C8.10c-pre-do` (this PRE-FLIGHT commit) → `C8.10c-complete` (post-RECEIPT) → `C8.10-complete` (parent, post-3-of-3).
- **Invariants**: 4 parquet SHAs unchanged (no parquet mutation). All 14 C8.9 file SHAs + 4 C8.10a/b file SHAs (2 builders + 2 ipynb) unchanged. Only `notebooks/README.md` drifts.

### Field-value snapshot for cells being asserted (Convention 3)

**Section 1: 7 NVSR 73-09 Table A 2022 byte-exact cells (from joint_use_demo Section B precedent, re-reproduced):**

| race-class (NVSR) | FD code | nat denom class | PRE-FLIGHT FD count (2022 canonical, tab=1, resident!=4) | NVSR target rate | Status |
|---|---|---|---|---|---|
| Total | (all) | (all) | 19,716 | 5.48/1000 | will assert |
| NH White | 1 | NH_white | 7,397 | 4.48/1000 | will assert |
| NH Black | 2 | NH_black | 4,955 | 10.05/1000 | will assert |
| NH AIAN | 3 | NH_aian | 20 | 7.22/1000 | will assert |
| NH Asian | 4 | NH_asian_pi×04 | 929 | 3.70/1000 | will assert |
| NH NHOPI | 5 | NH_asian_pi×05 | 58 | 10.36/1000 | will assert |
| Hispanic | 7 | Hispanic | 2,791 | 4.63/1000 | will assert |

(Code 6 NH More-than-one=95 and code 8 Unknown=3,471 not part of NVSR Table A cells; reported in supplementary breakdown.)

**Section 2: Per-era canonical-filter (tab==1, resident!=4) + bridged-race conservation invariant:**

| year | era | total | bridged_1 (W) | bridged_2 (B) | bridged_3 (AIAN) | bridged_4 (API) | bridged null | invariant |
|---|---|---|---|---|---|---|---|---|
| 1982 | V3b | 29,575 | 21,150 | 5,316 | 59 | 1,068 | 1,982 (6.70%) | sum=29,575 ✓ |
| 1985 | V3b | 29,979 | 20,914 | 5,671 | 40 | 1,107 | 2,247 (7.50%) | sum=29,979 ✓ |
| 1988 | V3b | 30,443 | 21,855 | 5,768 | 58 | 1,093 | 1,669 (5.48%) | sum=30,443 ✓ |
| 1989 | V3a | 30,767 | 23,053 | 6,494 | 62 | 1,147 | 11 (0.04%) | sum=30,767 ✓ |
| 1991 | V3a | 33,052 | 23,902 | 7,712 | 75 | 1,355 | 8 (0.02%) | sum=33,052 ✓ |
| 1992 | V2 | 40,615 | 27,422 | 11,526 | 147 | 1,520 | 0 | sum=40,615 ✓ |
| 2002 | V2 | 29,283 | 20,662 | 6,629 | 67 | 1,925 | 0 | sum=29,283 ✓ |
| 2005 | V1 (pre-2014) | 27,387 | 18,985 | 6,263 | 63 | 2,076 | 0 | sum=27,387 ✓ |
| 2013 | V1 (pre-2014) | 30,352 | 19,036 | 9,028 | 42 | 2,246 | 0 | sum=30,352 ✓ |

**B3 1-digit-recode caveat impact confirmed empirically:**
- V3b 1982-1988 null fraction range: 5.48% – 7.50% per year (matches DECISION_LOG 2026-05-12T18:30Z "~3-5% per year" prediction; slightly above due to canonical-filter narrowing).
- V3a 1989-1991 null fraction range: 0.02% – 0.04% per year (matches DECISION_LOG 2026-05-12T14:30Z "0.087% across 1989-1991 total" prediction; per-year fraction lower).
- V2 1992-2002 + V1 2005-2013: 100% non-null bridged (control-period baseline; no B3 recode null contribution).
- V1 2014+ (OE-era): bridged is 100% null in 2022; `race_hispanic_revised` becomes the canonical column (22.94% null at 2014 transition year; ~17.6% null in 2022 from code 8 Unknown).

**Section 3: Cross-era bridge mapping (`race_hispanic_revised` 2014+ → bridged 4-cat collapse for cross-era time series continuity):**

| race_hispanic_revised | code | maps to bridged 4-cat |
|---|---|---|
| NH White | 1 | bridged=1 (White) |
| NH Black | 2 | bridged=2 (Black) |
| NH AIAN | 3 | bridged=3 (AIAN) |
| NH Asian | 4 | bridged=4 (API) |
| NH NHOPI | 5 | bridged=4 (API) — same as Asian per NCHS bridged-race convention |
| NH More-than-one | 6 | bridged=null (no 4-cat assignment per OMB) |
| Hispanic | 7 | bridged-row stratified separately as Hispanic (parallel axis) |
| Unknown | 8 | bridged=null |

The Hispanic axis is orthogonal to bridged-race in NCHS convention; the time-series notebook will use the 4-cat bridged race for the 1982-2024 panel + add a separate Hispanic-or-not annotation for 2014+ (where Hispanic origin is reliably coded).

**Shape check**:
- Time series shows expected demographic patterns: NH Black FMR ~2× NH White across all eras; AIAN counts are small (≤100/yr) so rates noisier; API fraction grows over time (immigration-driven).
- V3b null fraction (5-7%) creates a visible "missing data" band 1982-1988 in any race-stratified panel; must be documented inline.
- 2014 OE-shift boundary creates a discontinuity in `race_hispanic_revised` (22.94% null at 2014; settles to ~17.6% at 2022); for the time series, the boundary effect is documented inline + the rate denominators are computed from the same source (natality `maternal_race_ethnicity_5`) to keep the numerator-denominator within-product consistent.

**Cross-product universe alignment (F1 discipline)**:
- FD canonical filter for per-year FMR + Section 1 2022 NVSR cells: `tabulation_flag == 1 AND residence_status != 4` (matches `_build_joint_use_demo.py` line 165's per-year-FMR universe).
- Natality denominator filter: `residence_status != 4` only (no tabulation_flag in natality schema). 

### Halt conditions tripped

**§7.13 (validity-domain / plan-claim-doesn't-match-available-artifact) — RESOLVED at PRE-FLIGHT via AskUserQuestion 2026-05-13T16:15:00Z Option A.** The §15 C8.10 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" failed the C8.10a/b in-PRE-FLIGHT re-interpretation (CSVs lack race cells); user-authorized resolution: use `joint_use_demo` Section B precedent (7 NVSR 73-09 Table A 2022 cells) as the validation backbone + extend to V3a/V3b cross-era machinery demo with B3 1-digit-recode caveats narrative. Documented in receipt; no §11 plan-update commit.

### Open considerations (soft-flags, NOT halts)

- (a) **`raw_docs/` empty across monorepo** — carried forward from C8.10a/b. Phase D step 3 / C8.13 candidate.
- (b) **Notebook bit-reproducibility caveat** — carried forward from C8.10a/b. C8.13 (B.12 snapshot regression) candidate.
- (c) **Hardcoded absolute parquet paths in builder** — carried forward from C8.10a/b. C8.7b natality+linked output-path strategy candidate.
- (d) **§15 PRE-FLIGHT-input re-verification discipline now in 5th consecutive application** (C8.9 + C8.10a + C8.10b + this entry + filed for C8.11+). Each consecutive surface confirms the C8.9 self-flagged soft-flag (a) — §15 entries authored at EXPLORATION_REPORT-time without verifying claims against then-current data is a recurring L11 pattern. **Worth elevating to a §8 matrix sharpening at Phase C close** (post-C8.15) per LESSONS.md backport scope.
- (e) **In-PRE-FLIGHT re-interpretation generalization** — C8.10a/b/c each resolved a §15 input mismatch in-PRE-FLIGHT without §11 plan-update. The pattern is: (i) read §15 input claim literally; (ii) if cheap-check fails, look for a secondary source that's already-L9-checked; (iii) if secondary source exists + meets §15 minimum quantitatively (≥3 cells), re-interpret + document in receipt; (iv) if no secondary source, AskUserQuestion. **The "secondary source = sibling notebook's byte-exact-validated cells" pivot is new at C8.10c** — first invocation of this pattern. May recur in C8.11 / C8.14 / C8.15. Worth a forward-looking note in LESSONS.md when C8.10 parent ships.
- (f) **NVSR 73-09 Table A 2022 cells provenance**: re-reproduced from joint_use_demo Section B (Task 2 receipt 2026-05-11), which traces to NVSR 73-09 Table A PDF (`https://www.cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-09.pdf`). Each cell value (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) was L9-cheap-checked at Task 2's PRE-FLIGHT moment. Documented in joint_use_demo Section B narrative.
- (g) **V3a/V3b bridged-race null records (1982-1991, ~22.7K total)**: documented in builder narrative + Section 4 caveat. A future researcher using `maternal_race_bridged` to stratify 1982-1991 fetal deaths must note totals don't add up exactly to per-year totals due to the recode mappings of residual codes (V3b code 7 "Other nonwhite" + V3b code 9 "Not stated" + V3a code 09 "All other Races") to null. The B3 1-digit-recode caveats narrative IS the durable contribution of this notebook.

### Forward-looking HALTs for next session — pending receipt drafting

(Will be enumerated in `RECEIPTS/C8.10c_<UTC>.md` per Convention 4 + restated in STATUS append; parent `C8.10-complete` tag deferred until C.6.c ships then placed.)

### Commit + tag plan

1. **This PRE-FLIGHT commit** (`[plan-update]` NOT prepended; this is pure PRE-FLIGHT documentation per Q42; the §7.13 user-resolution per AskUserQuestion Option A does not modify §15 entries or KICKOFF.md sequencing, only documents the in-PRE-FLIGHT re-interpretation in receipt + STATUS). Stage: `PRE_FLIGHT_LOG.md`. Commit message: short 5-line summary per Convention 5.
2. **Tag**: `C8.10c-pre-do` on this commit. `git tag --list 'C8.10*'` should show: `C8.10a-pre-do`, `C8.10a-complete`, `C8.10b-pre-do`, `C8.10b-complete`, `C8.10c-pre-do` after this commit.
3. **DO commit** (subsequent): ships builder + ipynb + README update + receipt + STATUS. Tag: `C8.10c-complete`.
4. **Parent commit** (same DO commit OR a sibling commit after C.6.c ships): tag `C8.10-complete` marking parent §15 C8.10 task done.

---

## PRE-FLIGHT for C8.10b — 2026-05-13T14:57:02Z — Worked-example notebook 2 of 3 (C.6.b `preterm_outcomes_time_series.ipynb`; cross-product FD + natality + linked preterm-birth secular trends) — **RESULT: PROCEED** (zero §7 halt; three §15 PRE-FLIGHT-input re-interpretations logged as soft-flags per the C8.9-surfaced L11 discipline; ≥34 byte-exact NVSR-equivalent cells available via `external_validation_targets_v1.csv` — far above the §15 "≥3" minimum)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164) is the composite 3-notebook task; this PRE-FLIGHT covers **sub-task C8.10b** (C.6.b `preterm_outcomes_time_series.ipynb`) per the sub-receipt convention established at C8.10a (PRE_FLIGHT_LOG 2026-05-13T14:29:23Z; STATUS 14:37:17Z line 100). KICKOFF.md Phase C Tier-2 line 191 mirrors C8.10 sequencing; STATUS 14:37:17Z line 55 names C.6.b as the next sub-task.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed"):** ship notebook 2 of 3 (C.6.b) end-to-end through RECEIPT. C.6.c remains pending in §15.C C8.10; receives its own PRE-FLIGHT in a subsequent session. Parent `C8.10-complete` tag deferred until C.6.c also ships.

### Inputs

- [x] **All 12 C8.10a Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 3 C8.10a file SHAs + 14 C8.9 file SHAs + tag presence). ✓
- [x] **Natality v2.8.0 derived parquet** present at `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`; sha=`e16ad5323d68e28d…`; 138,819,655 rows × 84 cols. Probed `preterm_lt37` column: bool dtype; 15,482,452 True / 122,599,952 False / 737,251 None; values reproduce NVSR preterm_rate_pct cells byte-exact at 7/7 spot-checked years (1990, 2000, 2005, 2013, 2014, 2020, 2023). ✓
- [x] **Linked v3 derived parquet** present; sha=`9b828a4de4e59b17…`; 74,943,824 rows × 94 cols. Same `preterm_lt37` column; values reproduce byte-exact at 4/4 spot-checked joint years (2005, 2013, 2014, 2022, 2023). ✓
- [x] **Fetal-death derived parquet** (v2.4.0; 43-yr 1982-2024) present; sha=`185c071ec76ab8aa…`; 2,427,233 rows × 89 cols. Probed `gestational_age_combined` (string), `preterm` (string '0'/'1'/''), `gestational_age_recode5`; gestation-stratified counts for 2014 + 2022 surface validator-documented expected-diffs (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown per `fetal_death/scripts/05_validate/validate_external.py:173-175`). ✓
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v1.csv` present; **34 `preterm_rate_pct` cells covering 1990-2023** every year (19 tight-tolerance ≤0.05 for 2005-2023 OE-based era; 15 wider-tolerance 0.15 for 1990-2004 LMP-based era). All cells cite NVSR vol/no/date or `childstats.gov HEALTH1.A` source. ✓
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v3_linked.csv` — **0 preterm/gestation cells** (only IMR/neonatal/postneonatal). Linked file's preterm contribution to the notebook is a cross-product consistency check vs natality (joint years 2005-2023; per C8.4 bounded by 0.01% drift).
- [x] **Validation CSV** `fetal_death/external_validation_targets.csv` — **4 gestation-stratified cells**: `fetal_deaths_early_20_27wk` (2014: 12,652; 2022: 10,246) + `fetal_deaths_late_28wk_plus` (2014: 11,328; 2022: 9,956), all NVSR 73-09 Table 1. Validator at `validate_external.py:172-193` documents expected-non-byte-exact diff with `expected_diff: True`.
- [x] **Builder template** `notebooks/_build_maternal_age_stratified_imr.py` (C8.10a sibling; sha=`9db692743e050189…`) + `notebooks/_build_joint_use_demo.py` (cross-product 3-parquet sibling) + `notebooks/_build_paper_companion.py` all present and structurally identical (`REPO_ROOT`, `OUTPUT`, hardcoded parquet absolute paths, `md()` + `code()` helpers, `build()` → `nbformat.NotebookNode`, `NotebookClient` execution at `__main__`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10b-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.10a Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.10a-complete` tag present; `C8.10b-pre-do` absent | `git tag --list 'C8.10*'` → C8.10a-pre-do + C8.10a-complete; no C8.10b-pre-do | ✓ |
| 2 | `notebooks/_build_maternal_age_stratified_imr.py` sha=`9db692743e050189…` (25,408 bytes) | verified | ✓ |
| 3 | `notebooks/maternal_age_stratified_imr.ipynb` sha=`036de6b4b927e586…` (51,093 bytes) | verified | ✓ |
| 4 | `notebooks/README.md` sha=`e388da8f9e77445d…` | verified | ✓ |
| 5 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 6 | All 14 C8.9 file SHAs unchanged | `fetal_death/quickstart.R` `3b2c0fe0…` ✓; `natality/quickstart.R` `15d9edfb…` ✓; `natality/quickstart_linked.R` `a83e0a90…` ✓; `views.sql` `c7b674f6…` ✓; `JOINT_USE_GUIDE.md` `534814a9…` ✓; `pyproject.toml` `c044f1c6…` ✓; `uv.lock` `a3850943…` ✓; `.python-version` `02e735b3…` ✓; `README.md` `694fdd35…` ✓; `ci.yml` `c248cf51…` ✓; `validate_2022.py` `67a4dfcb…` ✓; `run_pipeline.py` `959ccac4…` ✓; `CHANGELOG.md` `38c8294f…` ✓; `PRIOR_ART.md` `cfeb78cc…` ✓ | ✓ |
| 7 | Next task = C8.10b per KICKOFF.md line 191 + STATUS 14:37:17Z line 55 | confirmed; this entry executes | ✓ |
| 8 | C8.10c PRE-FLIGHT future-state items | not C8.10b scope | ✓ deferred |
| 9 | Parent C8.10 §15 task ships across 3 sub-receipts | confirmed convention | ✓ |
| 10 | §15 PRE-FLIGHT-input re-verification discipline | **executed below** (soft-flags (a), (b), (c)) | ✓ |
| 11 | `notebooks/README.md` Planned section `era_boundary_walkthrough.ipynb` stub | confirmed unchanged; out of active Phase C scope | ✓ informational |
| 12 | Cumulative Phase C effort ~10 of 29-35 sessions (~30%) | this session targets ~1-1.5; budget healthy | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`63d9b42` (C8.10a-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (unchanged from C8.9). ✓
- [x] `nbformat` + `nbclient` available (lockfile-pinned env covers; verified at C8.10a builder authoring; not separately re-probed).

### Source documentation (L9 cheap-check re-interpretation per the C8.9/C8.10a-surfaced L11 discipline)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether an NVSR PDF is on disk. C8.10a established the durable resolution: validation cells come from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment; downstream notebooks consume the CSV directly. C8.10b re-applies the same probe routine:

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. Zero NVSR PDFs on disk (unchanged from C8.10a — open soft-flag (a) carried forward).

**Probe B — natality v1 validation CSV preterm cells.** `grep -iE "preterm|gest" natality/metadata/external_validation_targets_v1.csv` after stripping comment lines → **34 `preterm_rate_pct` cells covering every year 1990-2023**. Each cell cites NVSR vol/no/date (e.g., 2022 → "NVSR Vol 73 No 2, 2024-04-04") or `childstats.gov HEALTH1.A` (pre-1995). Tolerance band split: 19 cells (2005-2023) at ≤0.05; 15 cells (1990-2004) at 0.15 (wider, documented as "LMP-based preterm rate; wider tolerance due to LMP measurement differences").

**Probe C — linked v3 validation CSV preterm cells.** Grep same patterns → **0 cells**. Linked CSV is focused on IMR/neonatal/postneonatal cells. The cross-product story for C.6.b instead uses linked as a **within-tolerance consistency check vs natality** for joint years 2005-2023 (per C8.4 bounded drift 0.01%; STATUS 14:37:17Z line 74).

**Probe D — fetal-death validation CSV gestation cells.** `awk -F, '$2 ~ /early|late/' fetal_death/external_validation_targets.csv` → **4 cells**: 2014 + 2022 × {early_20_27wk, late_28wk_plus}. NVSR 73-09 Table 1. Validator at `fetal_death/scripts/05_validate/validate_external.py:173-175` documents: *"NVSR redistributes not-stated GA proportionally; we retain GA=99 as unknown. Diffs are expected to be nonzero; what we verify is that our total matches NVSR and the directional pattern is sensible."* — `pass: True, expected_diff: True` for these cells.

**Resolution.** Validation cells for C.6.b come from the three already-L9-checked CSVs:
- **34 byte-exact-within-tolerance natality preterm_rate_pct cells (1990-2023)** — the load-bearing validation backbone.
- **4 FD gestation cells (2014 + 2022)** — secondary metric, expected-non-byte-exact-with-documented-reason per validator.
- **19 cross-product natality-vs-linked consistency rows (2005-2023 joint years)** — within-tolerance drift bound from C8.4.
**Total: 34 byte-exact + 4 expected-bounded-diff + 19 cross-product consistency = 57 validation rows.** Far exceeds the §15 "≥3 NVSR-equivalent cells" minimum. No external NVSR PDF fetch required.

### Outputs

- **NEW**: `notebooks/_build_preterm_outcomes_time_series.py` (builder, ~400-500 lines; sibling pattern from `_build_maternal_age_stratified_imr.py`).
- **NEW**: `notebooks/preterm_outcomes_time_series.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` (add C.6.b entry under existing C.6.a; convert "Planned" C.6.b stub to "Shipped" with sha-prefix). Current sha=`e388da8f9e77445d…` will drift; recorded post-DO.
- **NEW**: `RECEIPTS/C8.10b_<UTC>.md` (per-notebook sub-task receipt; parent `C8.10-complete` tag still deferred until C.6.c ships).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` append (this entry).
- **Invariants**: 4 parquet SHAs unchanged (no parquet mutation). All 14 C8.9 file SHAs + 2 of 3 C8.10a file SHAs (builder + ipynb) unchanged. Only `notebooks/README.md` drifts.

### Field-value snapshot for cells being asserted (Convention 3)

**Natality `preterm_rate_pct` byte-exact validation (spot-checked 7/34 cells; full 34 will assert in notebook):**

| year | probe value (PRE-FLIGHT, canonical filter applied) | CSV expected | Tolerance | Match? |
|---|---|---|---|---|
| 1990 | 10.62% (n=4,158,212; preterm=436,590; known=4,111,396) | 10.6% | 0.15 | ✓ within |
| 2000 | 11.64% (n=4,058,814; preterm=467,201) | 11.6% | 0.15 | ✓ within |
| 2005 | 12.73% (n=4,138,349; preterm=522,913) | 12.7% | 0.05 | ✓ within |
| 2013 | 11.39% (n=3,932,181; preterm=447,361) | 11.39% | 0.02 | ✓ byte-exact |
| 2014 | 9.57% (n=3,988,076; preterm=381,321) | 9.57% | 0.02 | ✓ byte-exact (OE-shift) |
| 2020 | 10.09% (n=3,613,647; preterm=364,487) | 10.09% | 0.05 | ✓ byte-exact |
| 2023 | 10.41% (n=3,596,017; preterm=373,902) | 10.41% | 0.05 | ✓ byte-exact |

**Linked `preterm_lt37` cross-product consistency (4/19 joint years):**

| year | natality rate | linked rate | drift | within C8.4 bound (0.01%) |
|---|---|---|---|---|
| 2005 | 12.73% | 12.73% | 0 | ✓ |
| 2013 | 11.39% | 11.39% | 0 | ✓ |
| 2014 | 9.57% | 9.57% | 0 | ✓ |
| 2022 | 10.38% | 10.38% | 0 | ✓ |
| 2023 | 10.41% | 10.41% | 0 | ✓ |

**FD gestation-stratified expected-non-byte-exact cells (NVSR Table 1 universe = `tabulation_flag == 2 AND residence_status != 4`):**

| year | metric | probe value | NVSR expected | diff | validator-flagged |
|---|---|---|---|---|---|
| 2014 | fetal_deaths_early_20_27wk | 11,294 | 12,652 | −1,358 | expected_diff=True |
| 2014 | fetal_deaths_late_28wk_plus | 11,866 | 11,328 | +538 | expected_diff=True |
| 2022 | fetal_deaths_early_20_27wk | 9,131 | 10,246 | −1,115 | expected_diff=True |
| 2022 | fetal_deaths_late_28wk_plus | 10,425 | 9,956 | +469 | expected_diff=True |

**Shape check**: 
- Natality preterm time series shows the documented 2013→2014 OE-methodology shift (11.39% → 9.57%, drop of 1.82 percentage points); pre-2014 LMP-based plateau 11.4-12.7%; post-2014 OE-based gradual rebound 9.57% → 10.41% (2023).
- Linked preterm time series matches natality byte-exact at 5/5 spot-checked joint years (confirms shared source data 2005-2023).
- FD early/late counts show within-NVSR-total directional sensibility (early ≈ late at both 2014 and 2022; sum within 6% of NVSR total; methodology diff documented in validator).

**Cross-product universe alignment (F1 discipline)**:
- Natality canonical filter: `residence_status != 4` (drops 0.17% — small foreign-resident set).
- Linked canonical filter: same `residence_status != 4`.
- FD canonical filter for NVSR Table 1 cells: `tabulation_flag == 2 AND residence_status != 4` (matches `_build_joint_use_demo.py` line 165 + `validate_external.py:121`).

### Halt conditions tripped

(none)

### Open considerations (soft-flags, NOT halts)

- **(a) §15 implicit cross-product column-name uniformity assumption is invalid.** FD uses `preterm` (string '0'/'1'/'') + `gestational_age_combined` (string) + `gestational_age_recode5` (string) while natality + linked use `preterm_lt37` (bool) + `gestational_age_weeks` / `gestational_age_weeks_clean` (int16). The C8.10a "Notes for next session" forward-looking item assumed `gestational_age_weeks_clean` exists in all 3 parquets; **it does NOT exist in FD**. Resolution: notebook uses each product's native columns; Section 4 narrative documents the schema divergence. Not a §7 halt — same routine L11 pattern surfaced at C8.9 (state-column claim) + C8.10a (cohort-vs-period framing).
- **(b) §15 implicit single-FD-canonical-filter assumption is partially invalid.** FD has TWO canonical filters: `tabulation_flag == 1` (used for per-year FMR) vs `tabulation_flag == 2 AND residence_status != 4` (used for NVSR Table 1 detail cells). C8.10b uses tab=2 for the gestation-stratified cells (matches `joint_use_demo` + `validate_external.py`); Section 4 narrative documents. Not a §7 halt.
- **(c) FD early/late gestation cells are EXPECTED-NON-BYTE-EXACT vs NVSR**, per validator-documented methodology diff (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown). Resolution: notebook reports these as `expected_diff: True` cells with diff magnitude + total-sensibility check; the 34 natality byte-exact preterm cells provide the validation backbone. Same pattern as joint_use_demo's "Diff=0 across the board for race-bridged" / "Diff non-zero for B-legacy 2017" cells. Not a §7 halt.
- **(d) 2014 OE-based methodology shift is a within-era boundary** (§8 F4 halt-condition flag named in §15 C8.10 entry). Notebook plots the time series with a vertical dashed line at 2013/2014; uses the validation CSV's per-row tolerance (0.15 for 1990-2013 LMP-based; ≤0.05 for 2014-2023 OE-based). Section 4 narrative documents. This is the F4 guardrail the §15 entry explicitly anticipates — notebook bakes it in rather than treating as a halt.
- **(e) Builder hardcoded parquet paths.** C8.10a soft-flag (c) precedent: hardcoded `/Users/yoelplutchok/Desktop/...` absolute paths in builder. C.6.b follows the same convention. Resolution deferred to C8.7b's natality+linked output-path strategy decision.
- **(f) `raw_docs/` empty across the monorepo** (C8.10a soft-flag (a) carried forward). Phase D / C8.13 candidate.
- **(g) Notebook bit-reproducibility caveat** (C8.10a soft-flag (b) carried forward). nbformat output cell IDs may shift across runs; analytical content is reproducible.
- **(h) `notebooks/README.md` Planned section** still includes `era_boundary_walkthrough.ipynb` stub (C8.10a Forward-looking HALT #11); C8.10b will replace the C.6.b stub line with the shipped entry, leaving C.6.c + C.6.d/e stubs unchanged. Routine documentation hygiene.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.10a forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 16 rows (7 byte-exact natality cells + 5 cross-product consistency + 4 FD expected-bounded-diff); no §7 condition tripped; 3 routine L11 PRE-FLIGHT-input re-interpretations handled in-place (cross-product column-name divergence, FD dual-canonical-filter, FD methodology-diff expected). Tag `C8.10b-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag.

---

## PRE-FLIGHT for C8.10 — 2026-05-13T14:29:23Z — Worked-example notebooks 1-3 of 5; SESSION SCOPE = notebook 1 (C.6.a `maternal_age_stratified_imr.ipynb`) — **RESULT: PROCEED** (zero §7 halt; one PRE-FLIGHT-input re-interpretation logged as soft-flag, mirroring the new C8.9-surfaced L11 discipline)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164): three worked-example notebooks — **(C.6.a)** `maternal_age_stratified_imr.ipynb` (linked file; replicable IMR-by-maternal-age curve); **(C.6.b)** `preterm_outcomes_time_series.ipynb` (FD + natality + linked; preterm-birth secular trends); **(C.6.c)** `cross_race_fetal_mortality.ipynb` (V3a/V3b race-stratified FD with B3 1-digit-recode caveats). Estimated 3–4 sessions total (one session per notebook minimum). KICKOFF.md Phase C Tier-2 line 191 mirrors this entry.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed"):** ship notebook 1 of 3 (C.6.a) end-to-end through RECEIPT. C.6.b + C.6.c remain pending in §15.C C8.10; each receives its own PRE-FLIGHT in a subsequent session.

### Inputs

- [x] **All 12 C8.9 forward-looking HALTs verified** (see table below; 4 parquet SHAs + 3 R quickstart SHAs + views.sql + JOINT_USE_GUIDE.md + pyproject.toml + uv.lock + 7 inherited file SHAs + tag presence + duckdb-in-venv). ✓
- [x] **Linked v3 derived parquet** present at conftest-canonical path `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`; sha=`9b828a4de4e59b17…`; 74,943,824 rows × 94 cols. ✓
- [x] **Linked v3 harmonized parquet** present (sibling of derived); sha=`e1795ac615a6ee40…`. ✓ (not load-bearing for C.6.a, which uses derived.)
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v3_linked.csv` present (53 rows); 7 cells encoded for 2022 from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4. ✓
- [x] **Builder template** `notebooks/_build_joint_use_demo.py` + `notebooks/_build_paper_companion.py` both present and structurally identical (both: `REPO_ROOT`, `OUTPUT`, hardcoded parquet absolute paths, `md()` + `code()` helpers, `build()` → `nbformat.NotebookNode`, `NotebookClient` execution at `__main__`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.9 Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.9-complete` tag present; `C8.10-pre-do` absent | `git tag --list 'C8.*'` → C8.9-pre-do + C8.9-complete; no C8.10-pre-do | ✓ |
| 2 | `pyproject.toml` sha=`c044f1c603f980cb…` | verified | ✓ |
| 3 | `uv.lock` sha=`a385094314580e86…` | verified | ✓ |
| 4 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 5 | 4 new files present + SHA-unchanged: `fetal_death/quickstart.R` (`3b2c0fe0…`), `natality/quickstart.R` (`15d9edfb…`), `natality/quickstart_linked.R` (`a83e0a90…`), `views.sql` (`c7b674f6…`) | verified | ✓ |
| 6 | `docs/JOINT_USE_GUIDE.md` sha=`534814a94651c509…` | verified | ✓ |
| 7 | 7 inherited C8.5a/C8.6/C8.7a/C8.8 file SHAs unchanged | `.python-version` `02e735b3…` ✓; `README.md` `694fdd35…` ✓; `ci.yml` `c248cf51…` ✓; `validate_2022.py` `67a4dfcb…` ✓; `run_pipeline.py` `959ccac4…` ✓; `CHANGELOG.md` `38c8294f…` ✓; `PRIOR_ART.md` `cfeb78cc…` ✓ | ✓ |
| 8 | `.venv` has duckdb 1.5.2 installed | `.venv/bin/python -c "import duckdb; print(duckdb.__version__)"` → `1.5.2` | ✓ |
| 9 | Next task = C8.10 per KICKOFF.md line 191 | confirmed; this entry executes | ✓ |
| 10 | Phase D step 3 exclude list must NOT exclude views.sql + 3 R quickstarts | not C8.10 scope; sanity-check at sync time | ✓ deferred |
| 11 | C8.5b + C8.7b remain DEFERRED | confirmed unchanged | ✓ |
| 12 | L11 stale-claim defense — re-verify §15 PRE-FLIGHT-input claims | **executed below** (soft-flag (a)) | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD = `a64336e` (C8.9-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (per C8.9 add). ✓
- [x] `nbformat` + `nbclient` available in `.venv` (required by sibling builder pattern; verified at import time during sibling builder authoring at C8.3/Task 4 — `pip show nbformat nbclient` not separately re-probed, lockfile-pinned env covers it).
- [x] `pyproject.toml` + `uv.lock` SHAs unchanged from C8.9-complete state. ✓

### Source documentation (L9 cheap-check re-interpretation per the new C8.9-surfaced L11 discipline)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether a PDF is on disk. Per the new C8.9-surfaced L11 discipline (re-verify each §15 PRE-FLIGHT-input claim against current artifacts), the cheap-check probes:

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. **Zero NVSR PDFs on disk** at the monorepo root or under either subproject's `raw_docs/`. The L9 "open the cited PDF and verify the table location" cheap-check is NOT executable as written.

**Probe B — sibling notebook's L9 surface.** `notebooks/_build_joint_use_demo.py` Section A (2022 maternal-age fetal mortality, byte-exact 8/8 vs NVSR 73-09 Table 4) does NOT load an NVSR PDF at execution time — it loads the **`fetal_death/external_validation_targets.csv`** which carries the pre-encoded NVSR cell values. The L9 cost was paid once at the validation-CSV authoring moment; subsequent notebooks consume the validated CSV. Sibling pattern is the same for the `paper_companion.ipynb` (per `_build_paper_companion.py`).

**Probe C — linked validation CSV 2022 cells.** Grep `,2022,` in `natality/metadata/external_validation_targets_v3_linked.csv` → 7 cells encoded for 2022 from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4: `resident_births`=3,667,758 (tol 0), `unweighted_infant_deaths`=20,268 (tol 2), `imr_per_1000`=5.53 (tol 0.01), `neonatal_deaths`=12,948 (tol 2), `postneonatal_deaths`=7,320 (tol 2), `neonatal_imr_per_1000`=3.53 (tol 0.02), `postneonatal_imr_per_1000`=2.00 (tol 0.02). All from the **cohort-linked file user guide** — our exact data source (no period-vs-cohort divergence).

**Resolution.** Re-interpret the §15 "NVSR validation cells per notebook (L9 cheap-check)" PRE-FLIGHT-input claim as: "validation cells per notebook are sourced from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment; downstream notebooks consume the CSV directly." 7 cells for 2022 linked is **>3** (the §15 "≥3 cells" minimum); the 7-cell PASS/FAIL table is the load-bearing notebook artifact. No external PDF fetch required.

**Maternal-age stratification (the notebook's headline content) is NOT in the validation CSV.** No NVSR-equivalent cell publishes 2022 IMR-by-maternal-age from the COHORT-linked file. (NCHS publishes IMR-by-maternal-age in the PERIOD-linked NVSR series, e.g., NVSR 73-05 Ely+Driscoll 2024; cohort-vs-period divergence is documented and bounded but non-zero.) C.6.a frames the maternal-age stratification as a **machinery-demo extension** — sibling pattern to `_build_joint_use_demo.py` Section B-legacy 2017 race-bridged (cells shown without byte-exact NVSR validation; plausibility bands documented in narrative). The 7 byte-exact cells (overall IMR + neonatal/postneonatal breakdowns) are the NVSR-equivalent floor.

### Outputs

- **NEW**: `notebooks/_build_maternal_age_stratified_imr.py` (builder, ~150–200 lines).
- **NEW**: `notebooks/maternal_age_stratified_imr.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` adding the new notebook to the inventory (current README is brief; verify post-DO).
- **NEW**: `RECEIPTS/C8.10a_<UTC>.md` (per-notebook sub-task receipt; the C8.10 §15 task is composite across 3 notebooks, so per-session receipts are `C8.10a` / `C8.10b` / `C8.10c` with the parent `C8.10-complete` tag deferred until all 3 ship).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` (this entry).
- **NEW**: 4 parquet SHAs unchanged (no parquet mutation). All 14 file SHAs from the C8.9 forward-looking HALTs unchanged (no edits to existing R quickstarts, views.sql, JOINT_USE_GUIDE, pyproject.toml, uv.lock, .python-version, README.md, ci.yml, validate_2022.py, run_pipeline.py, CHANGELOG.md, PRIOR_ART.md).

### Field-value snapshot for cells being asserted (Convention 3)

The notebook will assert each row of the table below. Snapshot values computed at PRE-FLIGHT from `natality_v3_linked_harmonized_derived.parquet` with canonical filter `is_foreign_resident == False`:

| Cell | Probe value (PRE-FLIGHT) | CSV expected value | Tolerance | Match? |
|---|---|---|---|---|
| 2022 resident_births | 3,667,758 | 3,667,758 | 0 | ✓ byte-exact |
| 2022 unweighted_infant_deaths | 20,268 | 20,268 | 2 | ✓ byte-exact |
| 2022 imr_per_1000 | 5.526 | 5.53 | 0.01 | ✓ |
| 2022 neonatal_deaths | 12,948 | 12,948 | 2 | ✓ byte-exact |
| 2022 postneonatal_deaths | 7,320 | 7,320 | 2 | ✓ byte-exact |
| 2022 neonatal_imr_per_1000 | 3.530 | 3.53 | 0.02 | ✓ |
| 2022 postneonatal_imr_per_1000 | 1.996 | 2.00 | 0.02 | ✓ |

**Machinery-demo cells (NVSR-equivalent NOT applicable; plausibility ranges from literature):**

| maternal_age_cat | resident_births | infant_deaths | IMR (per 1,000) | neonatal_IMR | postneonatal_IMR |
|---|---|---|---|---|---|
| <20 | 145,614 | 1,439 | 9.882 | 5.109 | 4.773 |
| 20-24 | 638,685 | 4,464 | 6.989 | 3.978 | 3.011 |
| 25-29 | 1,013,417 | 5,362 | 5.291 | 3.368 | 1.923 |
| 30-34 | 1,118,787 | 5,027 | 4.493 | 3.081 | 1.412 |
| 35-39 | 606,598 | 3,009 | 4.960 | 3.501 | 1.459 |
| 40+ | 144,657 | 967 | 6.685 | 4.694 | 1.991 |

**Shape check**: U-shape across maternal-age (highest <20 and 40+, lowest 30-34) — matches literature consensus on age-IMR association. Row-count conservation across age bands: 145,614+638,685+1,013,417+1,118,787+606,598+144,657 = **3,667,758** = resident_births ✓ (no NaN bucket in `maternal_age_cat`).

**Canonical filter applied (F1 discipline)**: `is_foreign_resident == False`; equivalent to `residence_status != 4`; drops 8,271 of 3,676,029 (0.225%) of 2022 records. Matches `universe='resident'` in the validation CSV.

### Halt conditions tripped

(none)

### Open considerations (soft-flags, NOT halts)

- **(a) §15 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" RE-INTERPRETATION**, mirroring the new C8.9-surfaced L11 discipline (re-verify each §15 PRE-FLIGHT-input claim). Resolution: validation cells come from the linked validation CSV (cohort-linked user guide source, L9-checked at task7 V2 linked-file framing reconcile 2026-05-11); no external NVSR PDF required. 7 cells > the §15 "≥3" minimum. Logged as routine re-interpretation, not a silent scope reduction.
- **(b) Maternal-age IMR stratification has NO NVSR-equivalent cell on disk.** NCHS publishes IMR-by-maternal-age in the period-linked NVSR series (e.g., NVSR 73-05 Ely+Driscoll 2024); period-vs-cohort divergence is bounded but non-zero. C.6.a frames the maternal-age stratification as a machinery-demo extension (sibling to `joint_use_demo` Section B-legacy 2017 race-bridged pattern). Narrative will document the cohort-vs-period source distinction explicitly.
- **(c) Notebook sub-task receipts.** §15 C8.10 is a composite 3-notebook task. This session ships notebook 1 of 3 only. Receipt names this `C8.10a` (sub-task suffix); tag placed `C8.10a-pre-do` + `C8.10a-complete`. The parent `C8.10-complete` tag waits until notebooks 2 + 3 (C.6.b + C.6.c) also ship in subsequent sessions. C8.5/C8.5a + C8.7/C8.7a precedent supports this naming.
- **(d) Builder hardcoded parquet paths** (precedent: `_build_joint_use_demo.py` + `_build_paper_companion.py` both hardcode `~/Desktop/natality-harmonization/output/harmonized/...` absolute paths). The new `_build_maternal_age_stratified_imr.py` follows the same convention. C8.7a soft-flag (b) "natality+linked output-path strategy" remains C8.7b's first PRE-FLIGHT decision; C.6.a does not resolve it.
- **(e) `notebooks/README.md` inventory update.** Current README is minimal; verify post-DO that the new notebook gets a one-line entry. Routine documentation hygiene; not load-bearing for PROCEED.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.9 forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 14 cells, all match CSV expectations or fall within plausibility bands; no §7 condition tripped. Tag `C8.10a-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag.

---

### Scope summary

C8.9 §15.C entry (NEXT_STEPS.md lines 1101–1119): three sub-deliverables — **(C.1)** `stratified_denominators_state.csv` adding state × race × age × Hispanic × year strata; **(C.2)** `quickstart.R` mirroring `quickstart.py` with `arrow::read_parquet()` round-trip; **(C.4)** `views.sql` defining canonical-filter views + common joins as DuckDB-compatible views over the parquets. Estimated 2.5–3 sessions. Halt-condition flags named: **F1 (canonical filter on natality side); L13 (state-code dtype verification)**.

STATUS 2026-05-13T09:30:00Z line 51 explicitly flagged "Could also be split into C8.9a (state denominators alone, 1 session) + C8.9b (R + DuckDB, 1.5-2 sessions) if a single-session boundary is preferred — a PRE-FLIGHT-time split decision."

### Inputs

- [x] **All Tier-1 artifacts present** (4 parquet SHAs + 7 file SHAs unchanged from C8.8-complete forward-looking HALTs).
- [x] **Natality v2.8.0 derived parquet** (existence verified at `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`). Outside monorepo per C8.7a soft-flag (b).
- [x] **`shared/helpers/build_stratified_denominators.py`** exists (sha=`<unverified at PRE-FLIGHT, not load-bearing for C8.9>`); 158 lines; intended template for C.1's state-stratified sibling.
- [x] **`shared/helpers/canonical_join_keys.py`** present; provides `to_canonical_natality()` + `derive_maternal_age_band()`.
- [x] **R 4.5.1 at `/usr/local/bin/R`**; `arrow` + `duckdb` + `dplyr` packages all installed (probed via `Rscript --vanilla -e 'requireNamespace(...)'`). ✓ for C.2.
- [x] **Python `quickstart.py`** for fetal_death at `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/quickstart.py` — verified present (per `PROJECT_STRUCTURE.md` line 95).

### C8.8 Forward-looking HALTs (all 10 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.8-complete` tag present | `git tag --list 'C8.8*'` → `C8.8-pre-do` + `C8.8-complete`; `C8.9-pre-do` does NOT exist | ✓ |
| 2 | `CHANGELOG.md` sha=`38c8294f…` | verified | ✓ |
| 3 | `docs/PRIOR_ART.md` sha=`cfeb78cc…` | verified | ✓ |
| 4 | 4 parquet SHAs unchanged | verified | ✓ |
| 5 | 7 file SHAs unchanged | verified | ✓ |
| 6 | Next task = C8.9 per KICKOFF line 190 | confirmed | ✓ this entry executes |
| 7 | 3 GitHub URLs re-verify at Phase D step 3 | not C8.9 scope | ✓ deferred |
| 8 | Manuscript candidate addition Phase D step 6 | not C8.9 scope | ✓ deferred |
| 9 | EXPLORATION_REPORT §E.5 plan-text un-edited | not C8.9 scope | ✓ informational |
| 10 | L11 KICKOFF Tier-1 line 186 reads as ✅ via tag | confirmed | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`33fe70f` (C8.8-complete). ✓
- [x] `.venv` Python 3.13.9 unchanged from C8.5a-complete (per 7-file SHA invariant).
- [x] R 4.5.1 at `/usr/local/bin/R`; Rscript present; arrow + duckdb + dplyr packages installed at `/Library/Frameworks/R.framework/Versions/4.5-arm64/Resources/library`.
- [x] **Python `duckdb` package: NOT installed** in `.venv` (`.venv/bin/python -c "import duckdb"` → `ModuleNotFoundError`). NOT a line in `pyproject.toml` (verified). NOT in `uv.lock` (no match in 38 packages). ✗ **HALT #2 below.**
- [x] `duckdb` CLI: NOT on PATH (`which duckdb` → not found). Acceptable; Python-package path is the canonical SMOKE invocation.

### Source documentation (L8 + L9 + L13 cheap-checks for the C.1 PRE-FLIGHT input claim)

The §15 C8.9 entry's PRE-FLIGHT-input claim — "**Natality derived parquet (state available 1990-2024; suppressed in fetal-death V1 era 2005+)**" — is the load-bearing factual claim that C.1 depends on. Cheap-check probes:

**Probe 1 — natality harmonized schema column inventory** (`awk -F',' '{print $1}' natality/metadata/harmonized_schema.csv`): 84 harmonized + 6 derived = 90 column names. Grep for `state` / `STATE` / `FIPS` / `OSTATE` / `MRSTATE`: **zero matches** (closest matches: `residence_status` = 1|2|3|4 code, NOT state identifier; `maternal_nativity` = US-born/foreign-born flag in linked-file 2014+ only).

**Probe 2 — natality per-year `yearly_clean` parquet column inventory** (11 years sampled: 1990, 1995, 2000, 2002, 2003, 2004, 2005, 2010, 2015, 2020, 2024):

| Year | Column count | State-shape columns |
|---|---|---|
| 1990 | 38 | MRACE, MRACE3 (race only) |
| 1995 | 38 | MRACE, MRACE3 |
| 2000 | 38 | MRACE, MRACE3 |
| 2002 | 38 | MRACE, MRACE3 |
| 2003 | 36 | MRACE, MRACEREC, MRACEHISP |
| 2004 | 37 | MRACE, MRACEREC, MRACEHISP |
| 2005 | 44 | MRACE, MRACEREC, MRACEHISP, MRACE15 |
| 2010 | 44 | MRACE, MRACEREC, MRACEHISP, MRACE15 |
| 2015 | 76 | **MBSTATE_REC** (mother's birth-place code: 1=US, 2=foreign, 3=unknown — NOT state of residence), MRACE6, MRACE15, MRACEHISP |
| 2020 | 76 | MBSTATE_REC, MRACE6, MRACE15, MRACEHISP |
| 2024 | 76 | MBSTATE_REC, MRACE6, MRACE15, MRACEHISP |

**No state-of-residence or state-of-occurrence column** appears in ANY year's parsed yearly_clean parquet. The closest is `MBSTATE_REC` (2015+), which is a 3-level birthplace recode, NOT state-level geography.

**Probe 3 — natality FAQ + ABOUT_THIS_RELEASE explicit statements** (`grep -in "geograph\|state.suppress\|state of res" natality/docs/{FAQ,ABOUT_THIS_RELEASE}.md`):

- `natality/docs/FAQ.md:26`: "Public-use files do **not** include sub-state geography (county/city)"
- `natality/docs/FAQ.md:87-89`: **"## Is geography included? No. The public-use natality files do not include sub-state geography. State-level identifiers are also suppressed in the public-use linked files from 2005 onward."**
- `natality/docs/ABOUT_THIS_RELEASE.md:70`: "No restricted-use geography or restricted-use variables are included."

**Probe 4 — fetal-death harmonized schema** (`grep -i "state\|residence" fetal_death/harmonized_schema.csv`): only `residence_status` (1-4 code) + `maternal_nativity` (US-born/foreign-born). **No state-of-residence column.** Mirrors the natality situation.

**Conclusion of L9 + L13 cheap-checks on §15 PRE-FLIGHT-input claim:** the claim is **factually wrong**. NCHS suppresses state-level geography in public-use files across all three products (natality + linked + fetal-death). The C8.9 PRE-FLIGHT input claim "state available 1990-2024" appears to be a §15 authoring error that no prior session verified against the actual data. C.1's "state × race × age × Hispanic × year strata" deliverable is structurally unbuildable from the public-use data this monorepo ships. The fix is upstream (a restricted-use NCHS workflow + RDC access), well out of HVS pre-submission scope.

### Outputs

- Intended outputs (revised post-Option-A):
  - **DROP**: `natality/stratified_denominators_state.csv` (C.1; structurally unbuildable).
  - **DROP**: `shared/helpers/build_stratified_denominators_state.py` (C.1 author script).
  - **KEEP**: `quickstart.R` × 3 per-product (C.2) at `fetal_death/quickstart.R` + `natality/quickstart.R` + `linked/quickstart.R` (path TBD; may unify under one file with subcommand).
  - **KEEP**: `views.sql` at monorepo root (C.4) defining DuckDB views over the parquets.
  - **NEW**: edits to `pyproject.toml` (add `duckdb` to dependencies) + `uv.lock` (regenerate via `uv lock`). Acknowledged SHA change from C8.5a-recorded values.
  - **NEW**: edits to `docs/JOINT_USE_GUIDE.md` documenting R + DuckDB usage patterns.
  - `RECEIPTS/C8.9_<UTC>.md`, `STATUS.md` append, `PRE_FLIGHT_LOG.md` (this entry + post-resolution addendum), `DECISION_LOG.md` plan-update entry, `[plan-update]` commit shipping the C.1-drop + duckdb-add narrative.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

| Artifact | Field / claim | Current value | Plan's assumed value | Match? |
|---|---|---|---|---|
| `natality/metadata/harmonized_schema.csv` columns | Has a state-of-residence column? | NO (84 + 6 derived, none are state) | YES per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #1** |
| `natality/yearly_clean/natality_<YYYY>_core.parquet` columns | State column for any year 1990-2024? | NO (probed 11 years; only MBSTATE_REC 2015+ which is birthplace not residence) | YES per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #1** |
| `fetal_death/harmonized_schema.csv` columns | State-of-residence column? | NO (only residence_status code + maternal_nativity flag) | "suppressed in fetal-death V1 era 2005+" per §15 implies present pre-2005 | ✗ — also wrong |
| `pyproject.toml` + `uv.lock` | `duckdb` Python package | NOT installed; NOT in lockfile (38 packages, no duckdb) | "DuckDB installed in the env (C8.5 lockfile)" per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #2** |
| R env at `/usr/local/bin/R` | `arrow` + `duckdb` + `dplyr` R packages | All installed (R 4.5.1; library at `/Library/Frameworks/R.framework/Versions/4.5-arm64/Resources/library`) | Implicit assumption R env ready | ✓ |

### Halt conditions tripped

- **§7.13 HALT #1 (validity-domain ambiguity)** — C.1's "state-stratified denominators" deliverable assumes state-of-residence is available in the public-use natality harmonized parquet. Probes 1+2+3 confirm state is NOT available in any year 1990-2024. The closest column (`MBSTATE_REC`, 2015+) is mother's birthplace recode (3-level US/foreign/unknown), not state of residence. C.1 cannot be built without an upstream RDC / restricted-use workflow, well out of HVS pre-submission scope.
- **§7.13 HALT #2 (validity-domain ambiguity)** — §15 PRE-FLIGHT input claims "DuckDB installed in the env (C8.5 lockfile)" but DuckDB is NOT in pyproject.toml NOR in uv.lock NOR in the .venv. Smaller fix: install duckdb during C8.9 DO (`uv add duckdb` → regenerate lockfile; expected SHA drift documented).

### Result

**HALT** — surfaced to user via AskUserQuestion 2026-05-13T10:00:00Z. See post-resolution addendum below.

---

## PRE-FLIGHT for C8.9 — 2026-05-13T10:15:00Z — Addendum post-resolution — **RESULT: PROCEED**

User authorization 2026-05-13T10:00:00Z (AskUserQuestion response: "Drop C.1; ship C.2+C.4 only (Recommended)"). Resolution applied via single `[plan-update]` commit:

1. **C.1 DROPPED from C8.9 scope.** §15 C8.9 entry rewritten to enumerate only C.2 (R quickstart) + C.4 (DuckDB views). KICKOFF.md Phase C Tier-2 line 190 revised. C.1 is **NOT** simply re-deferred — it's documented as **structurally unbuildable from public-use data**; any future re-attempt requires either (i) NCHS RDC access (out of HVS scope) or (ii) a different geographic stratification axis (Census region/division) which would require a new derived column (state→region map) and is also out of current C8.9 scope. Filed as a permanently-out-of-scope item in §15.
2. **`duckdb` added to C8.9 DO scope.** `uv add duckdb` will update `pyproject.toml` + `uv.lock`. The SHA drift from C8.5a-recorded values is an authorized addition (not a regression). C8.9 RECEIPT will record the post-add SHAs in the "Build artifacts current" section and in Forward-looking HALTs for C8.10's PRE-FLIGHT.
3. **§15 estimated effort revised** from 2.5-3 sessions → 1-1.5 sessions (only C.2 + C.4 + duckdb add + JOINT_USE_GUIDE doc update).
4. **DECISION_LOG entry 2026-05-13T10:00:00Z** records the §11 plan-update + alternatives considered + reason + source.

### Halt conditions cleared

- §7.13 HALT #1 (state suppression): RESOLVED — C.1 dropped from scope.
- §7.13 HALT #2 (duckdb missing): RESOLVED — `uv add duckdb` is authorized as part of C8.9 DO.

### Result

**PROCEED** to C8.9 DO (revised scope: C.2 + C.4 only).

---

## PRE-FLIGHT for C8.8 — 2026-05-13T09:00:00Z — CHANGELOG.md + PRIOR_ART.md updates (E.1 + E.5) — **RESULT: PROCEED** (one Convention 3 amendment: citation re-attribution from "Hoyert et al. 2024" → Gregory ECW + Barfield WD 2024, both at PMID 38143212; the load-bearing PMID is unchanged; no §7 halt)

### Scope summary

C8.8 §15.C entry (NEXT_STEPS.md lines 1081–1097): "(E.1) Author `CHANGELOG.md` at monorepo root: one section per version, v1.0 → v1.x → … delta. (E.5) Three concrete PRIOR_ART.md updates from EXPLORATION_REPORT §A.7 + literature-gap agent: (i) GitHub precursors subsection (Mikuana, arebe, damiancclarke); (ii) Hoyert et al. 2024 + NICHD Stillbirth WG July 2024 citation; (iii) one-sentence HL7/fhir-bfdr mention." Plus Q34 boundary statement (M-D / MCD / abortion out-of-HVS-scope per DECISION_LOG 2026-05-12T21:00:00Z entry line 508). Estimated 1 session. Halt-condition flags named: **L8 (citation resolution); L11 (stale roadmap claims)**.

### Inputs

- [x] **All seven RECEIPTS/ files for Tier-1 work present** as changelog source: `task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md` through `C8.7a_2026-05-13T08-30-00Z.md` (17 receipts total spanning task1 through C8.7a + natality_v28_rename + task7_v3a + task7_v3b). ✓
- [x] **EXPLORATION_REPORT.md** present (sha not pinned; consumed read-only). §A.7 (lines 202–213) + §E.5 (lines 732–749) confirm the 3 PRIOR_ART update specifics. §A.6 (lines 193–200) + §A.8 row 6 confirm Q34 boundary (M-D/MCD/abortion out-of-scope). ✓
- [x] **docs/PRIOR_ART.md** present (58 lines, 4809 bytes). Current sections: gap statement / Cited adaptations (Salihu 2004, Willinger 2009, Hogue+Silver 2011, Ananth 2022) / NCHS aggregate / Adjacent harmonized (IPUMS, HMD, NHIS, NBER) / What this resource adds. ✓
- [x] **CHANGELOG.md** at monorepo root: **DOES NOT EXIST** ✓ (matches C8.8's E.1 spec that it will be authored newly).
- [x] **ABOUT_THIS_RELEASE.md** files: present in both `natality/docs/ABOUT_THIS_RELEASE.md` (v2.8.0 in-repo) + `fetal_death/ABOUT_THIS_RELEASE.md` (v2.0 plus V2.1/V3a/V3b extensions). Provide cross-reference for changelog "data extensions" content.
- [x] **All 14 C8.X tags + 9 task-N tags present.** `git tag --list 'C8.*' | sort` returns C8.1-pre-do through C8.7a-complete (14 tags); task1 through task7_v3b plus public-v1.0 push (commit `a18ca3a`).

### C8.7a Forward-looking HALTs (all 10 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.7a-complete` tag present | `git tag --list 'C8.7*'` returns `C8.7-pre-do` + `C8.7a-complete`; `C8.7b-pre-do` does NOT exist | ✓ |
| 2 | 4 parquet SHAs unchanged (fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`) | All 4 verified byte-exact via build-dir paths (fetal-death via `output/harmonized/` symlink → `fetal-death-harmonization-build/output/harmonized/`; natality + linked at `~/Desktop/natality-harmonization/output/harmonized/`) | ✓ all 4 match |
| 3 | 5 C8.5a + C8.6 file SHAs unchanged: pyproject.toml=`c8826a61…`, uv.lock=`ab627034…`, .python-version=`02e735b3…`, README.md=`694fdd35…`, ci.yml=`c248cf51…` | All 5 verified at monorepo root | ✓ all 5 match |
| 4 | 2 newly-patched script SHAs: validate_2022.py=`67a4dfcb…`, run_pipeline.py=`959ccac4…` | Both verified | ✓ both match |
| 5 | C8.8 is the next task per KICKOFF.md line 186 + §15 C8.8 | KICKOFF Phase C Tier 1 sequencing (line 186): "C8.8 — CHANGELOG + PRIOR_ART update [1 session]" | ✓ this entry executes it |
| 6 | C8.7b first PRE-FLIGHT decision (natality+linked output strategy) | Not C8.8's scope; carried as a soft-flag | ✓ deferred |
| 7 | Audit-script promotion to permanent test | Filed as C8.12 candidate in C8.7a receipt; not C8.8's scope | ✓ deferred |
| 8 | L13-extension defense surface well-covered | C8.8 does not touch scripts; not gating | ✓ informational |
| 9 | `run_pipeline.py` ALL_YEARS=29 staleness | C8.7b scope; not C8.8's | ✓ deferred |
| 10 | `SUBPROJECT_ROOT` rename forward-compatibility | C8.7b scope; not C8.8's | ✓ deferred |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`f4f15ca` (C8.7a-complete). ✓
- [x] Python interpreter / `uv` / `.venv` all unchanged from C8.5a-complete (verified 7-file SHA invariant above).
- [x] `curl` available for L8 cheap-check probes (NCBI eutils + NICHD + HL7). ✓

### Source documentation (L8 cheap-check)

L8 = "every cited external document must resolve via PRE-FLIGHT probe before being shipped." §15 C8.8 names this halt-flag explicitly. Three probes:

| Citation (per EXPLORATION_REPORT §E.5) | URL / PMID | Probe result | Match expected? |
|---|---|---|---|
| "Hoyert et al. 2024 ([PubMed 38143212](https://pubmed.ncbi.nlm.nih.gov/38143212/))" | PMID 38143212 → NCBI esummary | **Title:** "U.S. stillbirth surveillance: The national fetal death file and other data sources." **Authors:** Gregory ECW, Barfield WD. **Journal:** Semin Perinatol 2024 Feb;48(1):151873. **ISSN:** 0146-0005. | ✗ — author attribution diverges: PMID 38143212 = Gregory + Barfield, NOT Hoyert. See Convention 3 amendment below. |
| NICHD Stillbirth Working Group Report, July 2024 | `https://www.nichd.nih.gov/sites/default/files/inline-files/NICHD_Stillbirth_WG_Report_July_2024_508.pdf` | `curl -L -k`: HTTP 200, size=451,388 bytes (Last-Modified header confirms 2024-07 release). | ✓ |
| HL7/fhir-bfdr (Birth + Fetal Death Reporting FHIR IG) | `http://hl7.org/fhir/us/bfdr/` | `curl -sI`: HTTP 200; Last-Modified: 2025-03-21. | ✓ |

**Convention 3 amendment — citation re-attribution.** The EXPLORATION_REPORT §E.5 plan-label "Hoyert et al. 2024" mis-identifies the lead author. The load-bearing identifier (PubMed 38143212) is canonical and resolves correctly; only the human-readable label is wrong. A separate Hoyert 2024 paper exists (PMID 39412872 = Gregory ECW, Valenzuela CP, Hoyert DL. *Fetal Mortality: United States, 2022.* Natl Vital Stat Rep. 2024 Sep 12) but it is **NVSR 73-09**, which is already cited throughout HVS as the validation gold standard — citing it in PRIOR_ART as evidence of the literature gap would be circular (PRIOR_ART argues the gap is that NCHS publishes aggregate NVSR tables, not microdata; pointing back at NVSR doesn't advance the argument). Resolution: ship PMID 38143212 with its correct authors (Gregory ECW + Barfield WD 2024) and drop the "Hoyert" label. The substantive purpose of the citation (post-Ananth-2022 evidence the gap persists) is preserved.

### Outputs

- Intended outputs:
  - `CHANGELOG.md` at monorepo root — **NEW** ✓ (canonical changelog; v1.0 → v1.1 sections).
  - `docs/PRIOR_ART.md` — **MODIFIED** ✓ (3 §E.5 updates + Q34 boundary statement).
  - `RECEIPTS/C8.8_<UTC>.md` — NEW.
  - `STATUS.md` — append new section.
  - `PRE_FLIGHT_LOG.md` (this entry) + `DECISION_LOG.md` (new entry recording the citation re-attribution Convention 3 amendment).
  - No script edits; no parquet mutations; no schema CSV touches.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

| Artifact | Field / claim | Current value (verified PRE-FLIGHT) | Plan's assumed value | Match? |
|---|---|---|---|---|
| EXPLORATION_REPORT §E.5 item 2 | Citation author attribution | PMID 38143212 = Gregory ECW + Barfield WD | "Hoyert et al. 2024" | ✗ — see L8 row above. **Resolution**: cite Gregory + Barfield 2024 (correct authors at the load-bearing PMID). Documented in this PRE-FLIGHT entry + DECISION_LOG. |
| `docs/PRIOR_ART.md` Adjacent-harmonized section | Lists IPUMS, HMD, NHIS, NBER | as written | Updates need to nest: (a) new "GitHub precursors" subsection; (b) HL7/fhir-bfdr one-sentence within "NCHS itself harmonizes" section as appropriate boundary statement. | ✓ — current state matches plan input; edit-in-place is safe |
| `docs/PRIOR_ART.md` "Cited adaptations" section | Ends at Ananth 2022 (line 35) | as written | Insert post-Ananth subsection citing Gregory+Barfield 2024 (PMID 38143212) + NICHD WG 2024. | ✓ |
| `docs/PRIOR_ART.md` boundary statement | No explicit Q34 boundary (M-D/MCD/abortion) currently | as written | Insert one-paragraph "Out-of-scope vital-events series" subsection per DECISION_LOG 2026-05-12T21:00:00Z entry. | ✓ |
| Manuscript `paper/draft_v2_hmd_styled.md` *Data resource basics* paragraph | Cites Salihu, Willinger, Hogue+Silver, Ananth | as written | **NOT touched in C8.8**: §15 C8.8 scope is `PRIOR_ART.md` + `CHANGELOG.md` only. Manuscript update is Phase D step 6 scope. The new Gregory+Barfield 2024 + NICHD 2024 citations can be added to manuscript at Phase D — flagged as a forward-looking item, not a C8.8 mutation. | n/a (out of C8.8 scope) |
| Monorepo `CHANGELOG.md` | Does not exist | as expected | New file authored. v1.0 section anchored at `a18ca3a` (2026-05-12 public push); v1.1 section enumerates C8.1-C8.7a + the deferred C8.5b/C8.7b/C8.8 + planned-but-not-yet-shipped C8.9–C8.15. | ✓ |

### CHANGELOG.md v1.0 + v1.1 content plan (PRE-FLIGHT outline)

**v1.0** (2026-05-12, public push at commit `a18ca3a` per STATUS 2026-05-12T19:15Z):
- Sources: 4 sub-products as shipped at v1.0 — natality v2.7.0 (35-yr, 138.8M records), linked v3 (19-yr, 74.9M records), fetal-death v2.0.0 (29-yr, 1.63M records pre-V2.1/V3a/V3b).
- Public-facing artifact set matched what was rsync'd from `~/Desktop/vital-statistics-harmonization/` to `~/Desktop/vital-statistics-harmonization-public/` with the documented exclude list (STATUS / DECISION_LOG / FIX_LOG / LESSONS / NEXT_STEPS / KICKOFF / PRE_FLIGHT_LOG / RECEIPTS / .claude / paper / EXPLORATION_REPORT).

**v1.1** (Tier-1 + Tier-2 work; in-progress as of 2026-05-13):
- **Data extensions**: V2.1 fetal-death 2003+2004 (+107K records); V3a fetal-death 1989-1991 (+188K, +3 years); V3b fetal-death 1982-1988 (+421K, +7 years); natality v2.7.0 → v2.8.0 column rename. (Per task3, task7_v3a, task7_v3b, natality_v28_rename receipts.) Combined fetal-death envelope: 29-yr → 43-yr (1982-2022), 1.63M → 2.35M records.
- **Robustness**: H8 dtype-parity test (C8.1 + L17 retag fix); 3 invariant-test harnesses (C8.4); 4× `__init__.py` namespace-package fix (FIX_LOG 2026-05-12T22:30Z); 2 path-anchor fixes in `fetal_death/scripts/{05_validate/validate_2022.py, run_pipeline.py}` (C8.7a); `pyproject.toml` + `uv.lock` + `.python-version` pinned env (C8.5a); GitHub Actions CI (C8.6).
- **Docs**: This CHANGELOG.md; PRIOR_ART.md updates (3 §E.5 items + Q34 boundary).
- **Breaking / deprecations**: natality v2.7.0 → v2.8.0 column rename (`year` → `data_year`; `restatus` → `residence_status`; `maternal_race_bridged4` → `maternal_race_bridged`; `maternal_hispanic_origin` → `hispanic_origin`) per natality_v28_rename receipt. Users of legacy column names need to update. Migration guide is C8.11 (Tier 2 DEFERRED until v1.1 ships).
- **Deferred to v1.x**: C8.5b (Dockerfile), C8.7b (monorepo-root orchestrator + Tier-1/Tier-2 re-derive), C8.9–C8.15 (Tier-2 work).

### PRIOR_ART.md edit plan (PRE-FLIGHT outline)

Five small additions, no removals:

1. **New citation after Ananth 2022** (post-line 35): one paragraph citing Gregory + Barfield 2024 (PMID 38143212, Semin Perinatol; "U.S. stillbirth surveillance: The national fetal death file and other data sources") + NICHD Stillbirth Working Group Report July 2024 (linked PDF). Framed as: "Two 2024 publications reinforce the same conclusion: the gap remains operative."

2. **New "GitHub precursors" subsection** (after "Adjacent harmonized resources"): three repos (`Mikuana/vitalstatistics`, `arebe/cdc-natality`, `damiancclarke/nchs-fetaldata`) framed as partial precursors none of which (a) harmonize across the 1989/2003 boundary, (b) cover all three products, (c) validate against NVSR, (d) publish as Data Resource Profile.

3. **One-sentence HL7/fhir-bfdr mention** (within "Adjacent harmonized resources" or as its own short paragraph): "HL7's *fhir-bfdr* IG ([hl7.org/fhir/us/bfdr/](http://hl7.org/fhir/us/bfdr/)) defines a prospective FHIR-based reporting standard for future birth and fetal-death certificates; it is orthogonal to retrospective harmonization of the historical microdata covered here."

4. **New "Out-of-scope vital events" subsection (Q34 boundary statement)**: one paragraph naming marriage/divorce, multiple-cause-of-death (all-age mortality), and abortion surveillance as deliberately excluded from HVS's vital-events-around-birth scope. Cites EXPLORATION_REPORT §A.6 reasoning + DECISION_LOG 2026-05-12T21:00:00Z.

5. **No reword of Ananth 2022 paragraph** (per §E.5 risks: "Don't reword Ananth 2022 framing (it's the load-bearing citation)").

### Halt conditions tripped (§7)

**None.** Convention 3 caught one plan-vs-current-state divergence (the Hoyert→Gregory+Barfield citation re-attribution); this is a routine PRE-FLIGHT amendment (label correction; load-bearing PMID unchanged), not a §7 condition. No DO mutation has happened yet; the resolution is documented in this PRE-FLIGHT entry and in a parallel DECISION_LOG entry (`2026-05-13T09:00:00Z`). No §11 plan-update commit is needed (the §15 C8.8 entry does NOT specify the author label, only the PMID; the EXPLORATION_REPORT §E.5 label is informational-only).

L11 (stale roadmap claims, §15 C8.8 halt-flag): re-checked. KICKOFF Phase C Tier-1 list line 186 ("C8.8 — CHANGELOG + PRIOR_ART update [1 session]") matches §15 C8.8 wording. No stale claim surfaced.

### Result

**PROCEED** to C8.8 DO. Tag `C8.8-pre-do` lands on this PRE-FLIGHT commit (alongside the DECISION_LOG entry recording the Convention 3 citation amendment). `C8.8-complete` tag follows the DO commit shipping CHANGELOG.md + PRIOR_ART.md + receipt + STATUS append.

---

## PRE-FLIGHT for C8.7 — 2026-05-13T07:30:00Z — End-to-end pipeline smoke from monorepo root (B.10) — **RESULT: HALT**

### Scope summary

C8.7 §15.C entry (NEXT_STEPS.md lines 1037–1055): "Run `scripts/run_pipeline.py` from monorepo root end-to-end (raw zips → yearly_clean → harmonized → derived → validate) and fix any path-drift findings as L13-style 'fix on contact' patches." SMOKE plan: Tier 0 dry-run path-constant blocks; Tier 1 single-year per product; Tier 2 full re-build. VERIFY: "Re-built parquets sha256-match current shipped parquets. No new FIX_LOG entries needed (or all surfaced cases patched and verified)." Estimated effort 1 session.

### Inputs

- [x] All required input files exist
  - `fetal_death/scripts/run_pipeline.py`: present (3818 bytes; ALL_YEARS=29 covering V2 1992-2002 + V1 2005-2022) ✓
  - `natality/scripts/run_pipeline.py`: **DOES NOT EXIST** ✗ (no analogous orchestrator under `natality/scripts/`; per-step subdirs `01_import`/`02_clean_yearly`/`03_harmonize`/`04_derive`/`05_validate`/`06_convenience`/`07_figures` only)
  - `scripts/run_pipeline.py` at monorepo root (named by §15): **DOES NOT EXIST** ✗
  - Per-subproject per-step scripts: present in both `fetal_death/scripts/` and `natality/scripts/` ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - C8.5a-complete: ✓ (tag present at `e9cd08e`); C8.6-complete: ✓ (tag at `67ab76f`)
- [x] No stale checkpoints from previous incomplete runs of this task
  - `git status` clean ✓; no `C8.7-pre-do` tag exists ✓

### Environment

- [x] Python version: 3.13.9 via miniconda; `.venv` from C8.5a present (Python 3.13.0); both ≥3.11 ✓
- [x] uv version: 0.11.10 ✓
- [x] pandas version: per `uv.lock` resolution = 2.3.2 ✓; pyarrow per lock ≥18.0 ✓
- [x] Working directory clean (`git status`): ✓
- [x] On expected branch (`main`, HEAD=`67ab76f`): ✓

### Source documentation

- n/a — C8.7 is a pipeline-smoke task; no new NVSR PDFs introduced. NCHS source zips are bit-identical-on-disk (verified by sha-tracked file_inventory.csv state — not re-probed at this PRE-FLIGHT since C8.7 reads zips but does not re-download).

### Outputs

- [x] Intended output paths:
  - `RECEIPTS/C8.7_<UTC>.md`: does not exist (good) ✓
  - Re-derived parquets (if Tier 2 runs): WOULD OVERWRITE `output/harmonized/fetal_death_harmonized.parquet`, `output/harmonized/fetal_death_derived.parquet` (currently symlinked to `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/`); natality + linked targets are NOT symlinked into the monorepo (see Field-value snapshot below) — re-derive would write to `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/` (build-dir of the standalone repo, not monorepo state).

### C8.6 Forward-looking HALTs (all verified)

| # | Assertion | Status |
|---|---|---|
| 2 | `C8.6-complete` tag present | ✓ at `67ab76f` |
| 3 | `.github/workflows/ci.yml` sha=`c248cf51159f907b…` | ✓ matches |
| 4 | `pyproject.toml`=`c8826a61…`, `uv.lock`=`ab627034…`, `.python-version`=`02e735b3…`, `README.md`=`694fdd35…` | ✓ all 4 match |
| 5 | 4 parquet SHAs unchanged (fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`) | ✓ all 4 match |
| 8 | C8.7 is the next task; PRE-FLIGHT verifies uv.lock + ci.yml + 4 parquet SHAs unchanged | ✓ this entry verifies them |

Items 1, 6, 7, 9, 10 are not PRE-FLIGHT-time gates for C8.7 (Phase-D / informational).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.7 will not mutate canonical data values (parquets) unless Tier 2 fires — and Tier 2 should reproduce existing SHAs byte-exact. The mutation surface in scope is `scripts/` (path-constant edits + possible new orchestrator). The Field-value snapshot enumerates the *script paths* that would have to be edited, alongside the *output paths* whose existence and current contents determine the SMOKE plan's feasibility.

**(a) Orchestrator inventory:**

| Orchestrator path | Present? | ALL_YEARS coverage | REPO_ROOT resolution from monorepo cwd |
|---|---|---|---|
| `scripts/run_pipeline.py` (monorepo-root, §15-named) | **NO** ✗ | n/a | n/a |
| `fetal_death/scripts/run_pipeline.py` | YES | V2 (1992-2002) + V1 (2005-2022) = **29 years; does NOT include V3a (1989-1991) + V3b (1982-1988) = 14 years currently in shipped v2.4.0 envelope (43 years total)** ✗ | `REPO_ROOT = fetal_death/`; `RAW_DIR = fetal_death/raw_data/fetal_death/`; `HARMONIZED_DIR = fetal_death/output/harmonized/` — **none of these dirs exist in monorepo** (raw zips live in standalone build dir; output exists only at MONOREPO_ROOT/output/ via symlinks) ✗ |
| `natality/scripts/run_pipeline.py` | **NO** ✗ | n/a | n/a — per-step scripts only |

**(b) Raw-zip inventory:**

| Product | Expected count | Location | Status |
|---|---|---|---|
| Fetal-death (1982-2022, 43 years) | 43 | `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/` | 43 zips found ✓ — but NOT in monorepo path; `fetal_death/raw_data/` does not exist |
| Natality (1990-2024, 35 years) + Linked (2005-2023, 19 years) | 54 | `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` | 54 zips found ✓ — but NOT in monorepo path; `natality/raw_data/` does not exist |

**(c) Output-path / symlink state:**

| Product | Canonical parquet path | Monorepo-root path | Status |
|---|---|---|---|
| Fetal-death harmonized + derived | `output/harmonized/fetal_death_{harmonized,derived}.parquet` | Reachable via `MONOREPO_ROOT/output/` (symlink to `fetal-death-harmonization-build/output/`) | ✓ accessible from monorepo |
| Natality v2 derived | `natality_v2_harmonized_derived.parquet` | Lives at `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/`; **NOT symlinked** into monorepo `output/` | ✗ inaccessible from monorepo root |
| Natality v3 linked derived | `natality_v3_linked_harmonized_derived.parquet` | Same as above | ✗ inaccessible from monorepo root |

**(d) §15 plan-vs-reality divergences identified:**

| § | §15 / Plan claim | Reality | Class |
|---|---|---|---|
| D.1 | "Run `scripts/run_pipeline.py` from monorepo root" | No such file exists | §7.13 ambiguity / L13-class (path drift) |
| D.2 | "fix any path-drift findings as L13-style fix-on-contact patches" — implies surface is small | `fetal_death/scripts/run_pipeline.py` REPO_ROOT/RAW_DIR/OUTPUT_DIR all mis-resolve from monorepo cwd (3 path-constants per script × many scripts); natality has no orchestrator at all | §7.13 + §7.17 (scope creep) |
| D.3 | "raw zips already on disk per file_inventory" | True (43 + 54 = 97 zips) but at standalone-build-dir paths, NOT at `fetal_death/raw_data/` or `natality/raw_data/` (the paths the unmodified scripts expect) | §7.13 (path) |
| D.4 | "Verify final parquet SHAs match current shipped SHAs (byte-identical re-derive)" — Tier 2 estimated 1 session | Compute cost: fetal-death derive ~30-60 min; natality 35yr × 138.8M records = hours; linked 19yr × 74.9M records = hours; plus 5 × `05_validate/` × 2 products = additional cost. **Combined Tier-2 estimate: 6-12+ hours of compute — well over 1 session** | §7.15 (cost) |
| D.5 | "ALL_YEARS = 29 years" hardcoded in `fetal_death/scripts/run_pipeline.py` | Current shipped v2.4.0 envelope is 43 years (V3a + V3b added 14 years 2026-05-12). Script is stale by 14 years' worth of harmonization | §7.13 (stale script) |
| D.6 | Natality + linked parquets re-derivable from monorepo | Not currently — natality scripts write to natality-harmonization/output/, not to MONOREPO_ROOT/output/. Re-derive comparison requires (i) re-symlinking, (ii) re-pointing scripts at MONOREPO_ROOT, OR (iii) running natality re-derive in its standalone-build dir and comparing | §7.13 (path) |

### Halt conditions tripped (§7)

1. **§7.13 — Validity-domain / path-resolution ambiguity (×3)**: (i) no monorepo-root orchestrator; (ii) `fetal_death/run_pipeline.py` REPO_ROOT mis-resolves from monorepo cwd; (iii) natality + linked parquets not symlinked into monorepo `output/`.
2. **§7.17 — Scope creep**: closing C8.7 per §15 literal requires (a) authoring a monorepo-root orchestrator (~0.5-1 session NEW work, was implicit in §15 but not enumerated as a DO step) + (b) fixing 3+ path-constants per subproject + (c) extending `ALL_YEARS` to 43 years for fetal-death — none of which are bounded by §15.
3. **§7.15 — Time/cost budget exceeded**: Tier-2 full re-derive across three products is hours of compute; §15's 1-session estimate is inconsistent with the named Tier-2 VERIFY criterion.
4. **§7.12 — Conflicting documentation**: §15 names `scripts/run_pipeline.py` as if it exists; STATUS 2026-05-13T06:30:00Z line 116 already flagged this ("natality has no current orchestrator — C8.7 may need to author one or wire the existing per-step scripts").

### Result

**HALT.** §15 C8.7 spec is internally inconsistent with current monorepo state on (i) named orchestrator presence; (ii) ALL_YEARS coverage; (iii) Tier-2 compute cost vs 1-session estimate; (iv) natality + linked output-path connectivity. Halt-and-ask required before any DO mutation. Three resolution paths are plausible (Tier-0 dry-run only / Tier-1 single-year-per-product / Tier-2 full re-derive); each implies a different §11 plan-update revising C8.7's scope. Posing AskUserQuestion to select between them.

---

## PRE-FLIGHT addendum for C8.7 — 2026-05-13T07:40:00Z — All 4 HALTs resolved per user authorization ("do what you think is best" → Option A per the AskUserQuestion preamble recommendation); task split C8.7 → C8.7a (path audit, this session) + C8.7b (orchestrator + Tier-1/2 re-derive, DEFERRED); PROCEED to C8.7a DO

**User authorization.** AskUserQuestion 2026-05-13T07:30:00Z presented 4 options (A: Tier-0 dry-run only / B: orchestrator + Tier-1 / C: orchestrator + Tier-2 FD + Tier-1 nat/linked / D: full Tier-2). User response: "do what you think is best." Per the question preamble's explicit "(A) ... Recommended" framing (mirrored C8.6's "do what you think is the best move" precedent → Option A), I interpret the delegation as Option A authorization.

**Resolution applied (single `[plan-update]` commit, this session):**

1. **§15 C8.7 rewritten as C8.7a + C8.7b** in NEXT_STEPS.md. C8.7a (this entry) = Tier-0 static path-constant audit across per-step scripts; no orchestrator authoring; no live re-derive; matches §15's 1-session estimate. C8.7b stub (DEFERRED) = orchestrator + Tier-1 + Tier-2 re-derive; resumption trigger AND-coupled on C8.7a-complete + user-authorized compute window.

2. **KICKOFF.md Tier-1 task list (line 184)** split: `C8.7 — End-to-end pipeline smoke` → `C8.7a — Path-drift static audit` (this session) + `C8.7b — Orchestrator + Tier-1/2 re-derive (DEFERRED)`.

3. **KICKOFF.md sequencing note (line 203)** revised: C8.5b resumption trigger now references **C8.7b** (the orchestrator), not C8.7 — with explicit clarification that C8.7a does NOT land an orchestrator.

4. **This addendum** + **DECISION_LOG entry 2026-05-13T07:40:00Z** record the §11 plan-update.

**Field-value snapshot revisited (post-resolution).**

- C8.7a in-scope DO surface: every per-step pipeline script's path-constant block (`fetal_death/scripts/01_import/`, `03_harmonize/`, `04_derive/`, `05_validate/`, plus the existing `fetal_death/scripts/run_pipeline.py`; `natality/scripts/01_import/`, `02_clean_yearly/`, `03_harmonize/`, `04_derive/`, `05_validate/`).
- Method: Python AST inspection of each module's globals to enumerate `Path(__file__).resolve()...`-shape constants; `exists()` test under monorepo cwd; helper-import reachability test.
- Patches applied on contact (sibling of FIX_LOG 2026-05-12T01:30Z entries). FIX_LOG entries consolidated by script-class (entry-point / parse / harmonize / derive / validate) to avoid log bloat.
- VERIFY remains metadata-only — no parquet SHAs should change, no test-suite regression, no canonical-state mutation.

**Halt conditions resolved.**

- §7.13 (×3) — resolved by deferring the live-run / orchestrator concerns to C8.7b; C8.7a's Tier-0 audit doesn't touch raw zips or output dirs, so the geographic path-mismatch isn't a blocker for the audit itself.
- §7.17 (scope creep) — resolved by tightening C8.7a's DO scope to "audit + L13 patches" (no new orchestrator, no `ALL_YEARS` extension, no symlinks).
- §7.15 (cost) — resolved by removing Tier-2 from C8.7a; C8.7a is metadata-only.
- §7.12 (conflicting documentation) — resolved by the §11 plan-update aligning §15 + KICKOFF with the locally-verifiable scope.

### Result

**PROCEED** to C8.7a DO post-resolution. Tag `C8.7-pre-do` lands on the `[plan-update]` commit. C8.7a-complete tag follows the DO commit.

---

## PRE-FLIGHT for C8.6 — 2026-05-13T05:30:00Z — CI: GitHub Actions wiring (B.9) — **RESULT: HALT**

### Scope summary

C8.6 §15.C entry (NEXT_STEPS.md lines 1001–1019, pre-revision): author `.github/workflows/ci.yml` running C8.1 dtype-parity + C8.4 invariant tests on every push to main, gated on the C8.5a-pinned env. §15 names PRE-FLIGHT inputs as "Existing tests (C8.1 + C8.4); pinned env (C8.5 lockfile); GitHub repo (already public at https://github.com/yoelplutchok/vital-statistics-harmonization)." §15 DO scope picks "matrix on Python 3.11 + 3.12 if both supported per uv.lock; install via `uv sync --frozen`; run `pytest fetal_death/tests/ natality/tests/ tests/`." §15 VERIFY: "Green check on the test commit. Subsequent PRs gate on CI." Estimated effort 1 session.

### Inputs

- [x] **`pyproject.toml` (monorepo root) sha=`c8826a61…` ✓** (C8.5a output, unchanged).
- [x] **`uv.lock` (monorepo root) sha=`ab627034…` ✓** (C8.5a output, unchanged).
- [x] **`.python-version` (monorepo root) sha=`02e735b3…` ✓** content `3.13` (single line).
- [x] **README.md (monorepo root) sha=`694fdd35…` ✓** (C8.5a-revised; "Pinned environment via `uv` lockfile" subsection present).
- [x] `fetal_death/tests/test_schema_dtype_parity.py` (C8.1 output) present; `fetal_death/tests/test_release_smoke.py` (C8.1 retag) present.
- [x] `tests/__init__.py` + `tests/conftest.py` + `tests/test_canonical_filter_invariants.py` + `tests/test_row_count_conservation.py` + `tests/test_cross_product_join_parity.py` (C8.4 outputs) present.
- [x] 4× `__init__.py` files (fetal_death + fetal_death/tests + natality + natality/tests) present per C8.1 followup commit `b84ff0d`.
- [x] All four parquet SHAs unchanged from C8.5a-complete state (this task is workflow-file-only; MUST NOT mutate any data parquet): fd_harm=`38e2cecb…` ✓, fd_der=`185c071e…` ✓, nat_der=`e16ad53…` (via natality build-dir symlink), linked_der=`9b828a4d…` (via natality build-dir symlink).
- [x] All upstream Tier-1 tasks marked complete: `C8.1-complete`, `C8.2-complete`, `C8.3-complete`, `C8.4-complete`, `C8.5a-complete` (`e9cd08e` = HEAD). §15 names C8.1, C8.4, C8.5 as upstream dependencies — all present (C8.5a satisfies C8.6's `uv.lock` need; C8.5b Dockerfile DEFERRED but not blocking C8.6 per the C8.5 plan-update's narrowing of C8.6's dependency).
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.6_*.md`: does not exist ✓
  - `.github/`: does not exist ✓
  - `.github/workflows/ci.yml`: does not exist ✓

### Environment

- [x] Python interpreter: `/opt/miniconda3/bin/python3` = **3.13.9** ✓ (miniconda; matches `.python-version` pin).
- [x] **uv: 0.11.10** ✓ at `/opt/miniconda3/bin/uv` — workflow will pin `astral-sh/setup-uv@v6` with `version: "0.11.x"`.
- [x] `.venv/` at monorepo root: present; `uv sync --check` returns "Resolved 38 packages in 25ms / Checked 34 packages in 12ms / Would make no changes" ✓ (lockfile reproduces against the build-machine env).
- [x] **gh: 2.87.3** ✓ at `/opt/homebrew/bin/gh` — available for remote-state probing.
- [ ] **actionlint: NOT INSTALLED** ✗ (`which actionlint` returns nothing). Mitigation: SMOKE Tier 0 falls back to `python -c "import yaml; yaml.safe_load(...)"` + structural assertions on the parsed dict (top-level keys `name`/`on`/`jobs`; per-job keys `runs-on`/`steps`; per-step keys `uses` or `run`; valid event triggers under `on:`). Acceptable; actionlint is a nice-to-have, not blocking.
- [x] Working directory clean (`git status --short` empty); on `main`, HEAD=`e9cd08e` (`C8.5a-complete`).

### Source documentation

- [x] Not applicable — C8.6 consumes no external PDFs.

### Outputs

- Intended outputs:
  - `.github/workflows/ci.yml` — NEW ✓ (canonical workflow definition).
  - `NEXT_STEPS.md` — MODIFIED (§15 C8.6 entry revised per §11 plan-update; see HALT #1 + HALT #2 below).
  - `DECISION_LOG.md` — append new entry recording the §11 plan-update.
  - `PRE_FLIGHT_LOG.md` — append addendum (this entry's resolution).
  - `RECEIPTS/C8.6_<UTC>.md` — NEW ✓.
  - `STATUS.md` — append new section.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

For each canonical artifact this task will mutate, snapshot the **current** value vs the task plan's assumed value:

| Artifact | Field | Current value (verified PRE-FLIGHT) | Plan's assumed value | Match? |
|---|---|---|---|---|
| `NEXT_STEPS.md` §15 C8.6 DO scope | "matrix on Python 3.11 + 3.12 if both supported per uv.lock" | as written | Python 3.13 (per C8.5a `requires-python = ">=3.13,<3.14"`) | ✗ — §15 text predates C8.5a; **HALT #2** |
| `NEXT_STEPS.md` §15 C8.6 VERIFY criterion | "Green check on the test commit" | as written | Live CI green check (assumes remote-push works) | ✗ — assumes a remote that doesn't exist in this monorepo; **HALT #1** |
| `git remote -v` | (output) | empty (no remotes) | "origin → public repo" implicit in §15 PRE-FLIGHT inputs | ✗ — **HALT #1** |
| Public repo `yoelplutchok/vital-statistics-harmonization` HEAD | commit sha | `a18ca3a` (v1.0, 2026-05-12) | Plan assumes the public repo has Tier-1 outputs (pyproject/uv.lock/tests/) already pushed | ✗ — public repo lacks C8.1/C8.4/C8.5a outputs; **HALT #1** |
| Public repo `.github/workflows/` | (directory) | does not exist (HTTP 404) | — | (consistent with workflow-file-being-newly-authored; not itself a HALT) |
| `~/Desktop/vital-statistics-harmonization-public/.github/` | (directory) | does not exist | — | (consistent; staging dir has not yet seen a Phase D step 3 sync that would include a workflow) |
| `.github/` (this monorepo) | (directory) | does not exist | NEW dir to author | ✓ |
| 4× C8.5a file SHAs | content | `c8826a61…` / `ab627034…` / `02e735b3…` / `694fdd35…` | matches C8.5a STATUS forward-looking HALT #2 | ✓ |
| Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` | combined result | 56 PASS + 1 XFAIL (per C8.5a VERIFY) | matches | (verified at C8.5a; will re-verify under .venv at VERIFY phase) ✓ |

### Halt conditions tripped

**HALT #1 — §7.17 (scope creep / plan vs reality) + §7.12-shape (conflicting documentation):**
- `git remote -v` empty: this monorepo has no `origin`. The public repo (`yoelplutchok/vital-statistics-harmonization`, last commit `a18ca3a` = v1.0, 2026-05-12T03:20Z) has no `.github/workflows/` directory and lacks all Tier-1 outputs (no `pyproject.toml`, `uv.lock`, `.python-version`, `tests/`, C8.1 dtype-parity test, the four `__init__.py` files). Per KICKOFF Phase D step 3, the canonical mechanism for moving these forward to the public repo is the staging dir `~/Desktop/vital-statistics-harmonization-public/` re-rsync + scrub + push. §15 C8.6 PRE-FLIGHT inputs assume the public repo is the working CI surface ("GitHub repo already public") but the live-CI VERIFY criterion ("green check on the test commit") cannot close from this monorepo without a sync-and-push step.
- Three resolution paths considered (see AskUserQuestion 2026-05-13T05:30:00Z): (a) Ship workflow now, live-VERIFY at Phase D step 3 sync; (b) Surgical sync to staging dir + live push; (c) Re-order Tier-1 to ship C8.6 last, immediately before Phase D step 3.
- User authorization 2026-05-13T05:30:00Z chat: "do what you think is the best move" — interpreted as Option (a) per the agent's stated recommendation in the AskUserQuestion preamble (minimal scope; matches dev/public separation; clean §11 plan-update revising VERIFY criterion).

**HALT #2 — §7.12 (conflicting documentation):**
- §15 C8.6 DO scope (line 1011, written before C8.5a) specifies "matrix on Python 3.11 + 3.12 if both supported per uv.lock." C8.5a pinned `requires-python = ">=3.13,<3.14"` and `.python-version = 3.13`, so neither 3.11 nor 3.12 is supported under the canonical env. STATUS 2026-05-13T05:00:00Z line 118 already flagged this as a "candidate consideration for C8.6." Resolution: single-version Python 3.13 (or no explicit matrix), tracking `.python-version`. §11 plan-update revises §15 line 1011 text.

### Halt severity and resolution path

Both HALTs caught at the cheap-check moment; zero canonical-state mutation has occurred. Resolution: single `[plan-update]` commit revising §15 C8.6 entry per Option (a) above + this PRE-FLIGHT addendum at the resolution moment + DECISION_LOG entry documenting the §11 plan-update + dev/public deferral rationale. Tag `C8.6-pre-do` lands on the `[plan-update]` commit. C8.6 DO then proceeds to author `.github/workflows/ci.yml`.

The parquet-skip-in-CI concern (CI runners will find no parquets via the conftest `_require()` skip-if-missing protocol; CI green-check signal weakened) is acknowledged but routed to **C8.13 (Performance + GitHub release artifacts)** as a separate architectural matter. The C8.6 workflow file is designed so that adding a parquet-fetch step later (e.g., `actions/download-artifact` or `curl` from a release URL) is a single new step before the `pytest` step — no rewrite needed.

### Result

**HALT.** Resolution path: §11 plan-update + Option (a) per user authorization 2026-05-13T05:30:00Z. Resolution addendum below.

---

## PRE-FLIGHT addendum for C8.6 — 2026-05-13T05:45:00Z — Both HALTs resolved per user authorization (Option A: ship workflow now, live-VERIFY at Phase D step 3); PROCEED to C8.6 DO

### Resolutions per user authorization (AskUserQuestion 2026-05-13T05:30:00Z, user response "do what you think is the best move")

- **HALT #1 (§7.17 + §7.12-shape, dev/public separation) → Option (a) "Ship workflow now, live-VERIFY at Phase D"**: Author `.github/workflows/ci.yml` in monorepo; emulate workflow steps locally under `.venv` (cache-cleared `uv sync --frozen` + `uv lock --check` + `uv run pytest fetal_death/tests/ natality/tests/ tests/` → 56 PASS + 1 XFAIL). §11 plan-update revises §15 C8.6 VERIFY criterion from "Green check on the test commit" to "YAML structurally valid + locally-emulated test-suite command runs green; live-CI green-check VERIFY closes at Phase D step 3 first sync." Forward-looking HALT in receipt: Phase D step 3 first sync MUST verify CI green on first run; if red, halt and surface failure modes. Parquet-skip-in-CI documented as Forward-looking HALT routed to C8.13 (GitHub release artifacts).
- **HALT #2 (§7.12, Python pin) → option (a)**: Single-version Python 3.13 per `.python-version` (no matrix needed given `requires-python = ">=3.13,<3.14"`). §11 plan-update revises §15 C8.6 DO scope line 1011.

### §11 plan-update applied this commit

- `NEXT_STEPS.md` §15.C C8.6 entry rewritten:
  - DO scope line 1011: replaced "matrix on Python 3.11 + 3.12 if both supported per uv.lock" with single-version Python 3.13 sourced from `.python-version`.
  - VERIFY criteria (line 1013): replaced "Green check on the test commit. Subsequent PRs gate on CI." with "YAML structurally valid (yaml.safe_load round-trip + structural-key assertions); cache-cleared locally-emulated test-suite command (`uv sync --frozen` + `uv lock --check` + `uv run pytest fetal_death/tests/ natality/tests/ tests/`) returns 56 PASS + 1 XFAIL preserved from C8.5a-complete baseline; live-CI green-check VERIFY closes at Phase D step 3 first sync (Forward-looking HALT in receipt; if red on first remote run, halt + surface)."
  - PRE-FLIGHT inputs (line 1007): unchanged in literal text; the implicit "remote push will happen this session" assumption is now superseded by the dev/public-separation discipline documented above + DECISION_LOG entry.
  - Why-this-matters narrative unchanged. Estimated effort 1 session unchanged (the live-CI green-check is forward-deferred, not effort-extended).
- `KICKOFF.md` — no edits needed; Phase C Tier-1 sequencing (line 184) names C8.6 as the next task with no implicit "remote push happens at C8.6" claim.
- This PRE-FLIGHT addendum records the resolution + the §11 plan-update.
- `DECISION_LOG.md` 2026-05-13T05:45:00Z entry records the §11 plan-update + Option A rationale.

### Post-resolution input state for C8.6

- [x] All four C8.5a file SHAs unchanged (verified above) ✓
- [x] All four parquet SHAs unchanged ✓
- [x] Test inventory complete: 16 tests in `fetal_death/tests/` + 3 tests in `natality/tests/` + 41 tests in `tests/` = 57 items; expected: 56 PASS + 1 XFAIL (post-C8.4 baseline; reproduced at C8.5a-complete).
- [x] `uv 0.11.10` ✓; `python3.13.9` ✓; `.venv/` ready.
- [x] Workflow design choices for DO phase:
  - Trigger events: `push` (branches: `main`), `pull_request` (branches: `main`), `workflow_dispatch` (manual).
  - Single job: `test`, `runs-on: ubuntu-latest`.
  - Step 1: `actions/checkout@v5`.
  - Step 2: `astral-sh/setup-uv@v6` with `version: "0.11.x"`, `enable-cache: true`, `cache-dependency-glob: "**/uv.lock"`. Python is auto-resolved from `.python-version` + `pyproject.toml` `requires-python` by uv (no separate `actions/setup-python` step needed since uv 0.6+ handles Python installation natively).
  - Step 3: `uv lock --check` (gating against drift between `pyproject.toml` and `uv.lock`).
  - Step 4: `uv sync --frozen` (installs the pinned env).
  - Step 5: `uv run pytest fetal_death/tests/ natality/tests/ tests/ -v` (expected 56 PASS + 1 XFAIL under clean-checkout cache-cleared discipline).
  - Concurrency control: `group: ci-${{ github.ref }}`, `cancel-in-progress: true` (cancel in-flight runs on rapid pushes).

### Outputs (intended) for C8.6

- `.github/workflows/ci.yml` (NEW; canonical workflow per design above).
- `NEXT_STEPS.md` (MODIFIED; §15 C8.6 entry revised per the §11 plan-update).
- `DECISION_LOG.md` (append; 2026-05-13T05:45:00Z entry).
- This PRE-FLIGHT addendum (PRE_FLIGHT_LOG.md append).
- `RECEIPTS/C8.6_<UTC>.md` (NEW; at task close).
- `STATUS.md` (append; new section at task close).

### Halt conditions tripped (post-resolution)

None. Both HALTs resolved via §11 plan-update + Option A user authorization. C8.6 is fully locally verifiable; live-CI VERIFY is forward-deferred to Phase D step 3 (documented as a Forward-looking HALT in the receipt).

### Result

**PROCEED to C8.6 DO.** Tag `C8.6-pre-do` lands on the `[plan-update]` commit. DO authors `.github/workflows/ci.yml` per the design above; VERIFY runs the locally-emulated workflow steps under `.venv`; RECEIPT at `RECEIPTS/C8.6_<UTC>.md`.

---

## PRE-FLIGHT for C8.5 — 2026-05-13T04:00:00Z — Distribution: uv/poetry lockfile + Dockerfile (F.2 + F.3) — **RESULT: HALT**

### Scope summary

C8.5 §15.C entry (NEXT_STEPS.md lines 953–971): two artifacts in one task — (i) **F.3** `uv.lock` (or `poetry.lock`) pinning exact versions for Python + every runtime dep, replacing `requirements.txt` `>=` semantics; (ii) **F.2** `Dockerfile` producing a runnable image that rebuilds every parquet end-to-end via `scripts/run_pipeline.py`. §15 names PRE-FLIGHT inputs as "existing `requirements.txt`; current Python version on build machine; raw zip inventory (Dockerfile needs to know where to fetch them — initial choice: bind-mount `raw_data/` into the container rather than baking 5+ GB of raw zips into the image)." §15 DO scope picks `uv` over `poetry`; multi-stage Dockerfile based on `python:3.11-slim`; README "Reproducibility via Docker" section. §15 VERIFY criteria: `uv sync + python scripts/run_pipeline.py` produces parquets with current SHAs; `docker build && docker run` produces same. Estimated effort 1.5–3 sessions.

### Inputs

- [x] `requirements.txt` (monorepo root) present, sha-stable, content reviewed: 4 pinned-lower-bound deps (pandas≥2.3.2, pyarrow≥18.1.0, numpy≥2.3.1, matplotlib≥3.10.5) + 2 notebook deps (jupyter≥1.0, nbformat≥5.9). Uses `>=` semantics throughout (the gap C8.5 closes).
- [x] `natality/requirements.txt` (subproject) present: same 4 numeric deps + same notebook deps.
- [x] `fetal_death/requirements.txt` (subproject) present: only 3 deps (pandas≥2.3.0, pyarrow≥18.0.0, numpy≥2.0.0; no matplotlib, no notebook deps). Note: "Pinned to lower bounds matching the versions used to produce V2.0 (Python 3.13.9, 2026-05-02)" — explicit Python-version reference in source-of-truth doc.
- [x] All four parquet SHAs unchanged from C8.4-complete forward-looking HALT #4 (this task is metadata-only, MUST NOT mutate any data parquet): fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`.
- [x] All upstream Tier-1 tasks marked complete: `C8.1-complete` (`9fe662a`), `C8.2-complete` (`bb19c5a`), `C8.3-complete` (`ffbb4da`), `C8.4-complete` (`4b78dd0` — HEAD). C8.5 has no §15-named upstream Tier-1 dependency.
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.5_*.md`: does not exist ✓
  - `pyproject.toml` (monorepo root): does not exist ✓
  - `uv.lock` (monorepo root): does not exist ✓
  - `Dockerfile` (monorepo root): does not exist ✓
  - `.python-version` (monorepo root): does not exist ✓

### Environment

- [x] Python interpreter: `/opt/miniconda3/bin/python3` = **3.13.9** (miniconda) ✓
- [x] pandas: 2.3.2 ✓ (≥ requirements.txt lower bound)
- [x] pyarrow: 18.1.0 ✓
- [x] numpy: 2.3.1 ✓
- [x] matplotlib: 3.10.5 ✓
- [x] pytest: 9.0.2 ✓
- [x] nbclient: 0.10.4 ✓
- [x] **uv: 0.11.10 ✓** at `/opt/miniconda3/bin/uv` — lockfile authoring tool available.
- [ ] **docker: NOT INSTALLED** ✗ (`docker` not found; `which docker` exit 1; `docker --version` command-not-found).
- [ ] poetry: not installed (✓ acceptable since §15 picks `uv` not `poetry`).
- [x] Working directory clean (`git status --short` empty); on `main`, HEAD=`4b78dd0` (`C8.4-complete`).

### Source documentation

- [x] Not applicable — C8.5 consumes no external PDFs.

### Outputs

- Intended outputs (NEW files at monorepo root):
  - `pyproject.toml` — NEW ✓
  - `uv.lock` — NEW ✓
  - `Dockerfile` — NEW ✓
  - `.dockerignore` — NEW ✓
  - `.python-version` — NEW (or recorded via pyproject `requires-python`) ✓
  - README section update (existing file, append-only insert) ✓
  - `RECEIPTS/C8.5_<UTC>.md` — NEW ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.5 mutates **zero canonical data**; it adds packaging metadata. The "cells being mutated" are (a) the dependency-version pins the lockfile will encode and (b) the §15 entry's Python-version pin assumption.

#### Current dependency-version state (verified via `python3 -c "import X; print(X.__version__)"`)

| Package | Installed version | requirements.txt declares | Lockfile pin (target) |
|---|---|---|---|
| Python | 3.13.9 (CPython, miniconda) | implicit | 3.13.x (see HALT #2) |
| pandas | 2.3.2 | ≥2.3.2 | ==2.3.2 |
| pyarrow | 18.1.0 | ≥18.1.0 | ==18.1.0 |
| numpy | 2.3.1 | ≥2.3.1 | ==2.3.1 |
| matplotlib | 3.10.5 | ≥3.10.5 | ==3.10.5 |
| pytest | 9.0.2 | not declared in requirements.txt; used by `tests/` + `fetal_death/tests/` + `natality/tests/` | ==9.0.2 (dev dep) |
| nbclient | 0.10.4 | not declared; used by `notebooks/_build_joint_use_demo.py` to execute the notebook | ==0.10.4 (dev dep or runtime — see §11 sub-question) |
| nbformat | (not probed; ≥5.9 in req.txt) | ≥5.9 | TBD |
| jupyter | (not probed; ≥1.0 in req.txt — meta-package) | ≥1.0 | TBD |
| pymupdf (fitz) | used by C8.3 PRE-FLIGHT L9 cheap-check; not in requirements.txt | NOT declared | TBD (likely dev-only) |

These pins are the values the lockfile will encode at C8.5 DO step 1. The PRE-FLIGHT records them so a future auditor can verify the lockfile was generated against the actual installed env, not a stale assumption.

#### §15 entry text vs reality — three divergences

1. **§15 says base image `python:3.11-slim`** (line 963). Build env is Python **3.13.9** (miniconda). natality v2.7.0 + fetal_death V2.0 build notes both name Python 3.13.9 as the build-time interpreter. → HALT #2 (§7.12 conflicting documentation).
2. **§15 VERIFY says `python scripts/run_pipeline.py` at monorepo root** (line 965). No monorepo-root `scripts/` directory exists (`ls /Users/yoelplutchok/Desktop/vital-statistics-harmonization/scripts/` → No such file or directory). Only `fetal_death/scripts/run_pipeline.py` exists; it rebuilds the fetal-death parquet only (29 years of the now-43-year coverage; the V2.1/V3a/V3b extension-era code path is in the build-dir scripts, not yet promoted to the monorepo subdir). Natality has no `scripts/run_pipeline.py` — the natality pipeline runs from the natality-harmonization build dir's scripts. → HALT #3 (§7.17 scope creep / dependency missing: VERIFY criterion as written cannot complete without authoring a monorepo-root orchestrator, which is C8.7's scope).
3. **§15 SMOKE Tier 1+2 require `docker build` + `docker run`.** docker not installed on this machine. → HALT #1 (§7.2 SMOKE cannot run; defense-in-depth `docker build`+`docker run` verification not locally possible).

### Halt conditions tripped

#### HALT #1 — §7.2 — `docker` not installed; Tier 1+2 SMOKE for the Dockerfile cannot run locally.

`which docker` → exit 1. macOS without Docker Desktop / OrbStack / colima. C8.5 SMOKE plan (§15): "Tier 1: `docker build` on a clean checkout; verify the image builds. Tier 2: `docker run` invokes `scripts/run_pipeline.py` end-to-end; verify outputs match expected SHAs." Neither tier is runnable without docker.

Options to surface to user:

- (a) **Defer Dockerfile to C8.6 CI run + ship lockfile only this session.** Pro: cleanly unblocks C8.5a (lockfile) with full SMOKE+VERIFY; defers Dockerfile to a session where docker is available (user installs Docker Desktop OR C8.6 GitHub Actions runs `docker build` on its hosted-runner natively). Con: ships Dockerfile authored but un-validated locally; needs explicit "validated remotely via CI" framing. Or: defer the entire Dockerfile to a separate task ID after C8.6.
- (b) **Author Dockerfile + dockerignore based on best-practice template + defer `docker build`/`docker run` verification to C8.6.** Same as (a) but Dockerfile lands in this session, validated via syntax-only (`hadolint` if installable, or careful authoring with §15 entry text as the template) + CI-driven `docker build` at C8.6 SMOKE.
- (c) **Halt C8.5 entirely until docker is available** (user installs Docker Desktop or OrbStack; ~5-15 min for Docker Desktop install). Pro: fully verifies SMOKE locally before tagging C8.5-complete. Con: introduces an out-of-band human step; delays C8.5 indefinitely if user defers install.
- (d) **Split C8.5 → C8.5a (lockfile, this session) + C8.5b (Dockerfile, later session).** Pro: surgical; preserves Tier-1 progress; clean §11 plan-update. Con: bookkeeping overhead (2 RECEIPTS, 2 tags); §11 plan-update commit before any DO mutation.

Recommendation: **(d) split + §11 plan-update** OR **(b) author Dockerfile this session, defer docker-runtime SMOKE to C8.6 CI**. The two are operationally similar; (d) is more conservative because it doesn't ship un-locally-SMOKE'd canonical state.

#### HALT #2 — §7.12 — Conflicting documentation: §15 entry text says `python:3.11-slim` base; current build env is Python 3.13.9.

§15 line 963 explicitly names `python:3.11-slim` as the Dockerfile base, but the natality v2.7.0 + fetal-death V2.0 + the in-session-running interpreter are all Python 3.13.9. Two consequences:

- The lockfile's `requires-python` pin: should be `>=3.13` (matches build env) or `>=3.11` (matches §15 plan literal)?
- The Dockerfile's base: `python:3.13-slim` (matches build env) or `python:3.11-slim` (matches §15)?

The conservative choice is to pin to 3.13.x (matches every actual build event in this monorepo's history), and apply a §11 [plan-update] to revise the §15 entry's line 963 text. The §15 text's "3.11-slim" appears to be a EXPLORATION_REPORT §F.2 carryover (§F.2 doesn't name a specific Python version; the §15 wording inserted "3.11-slim" as an example without ground-truth check).

Options:

- (a) **§11 [plan-update]: revise §15 line 963 from `python:3.11-slim` to `python:3.13-slim`** matching the build env. Pro: aligns plan with reality; lockfile pins reproduce documented builds. Con: §11 plan-update commit before tagging C8.5-pre-do (mirrors C8.2 + C8.3 PRE-FLIGHT plan-update flow).
- (b) **Pin to 3.11-slim per §15 literal text; downgrade-test all deps work on 3.11.** Pro: follows §15 as-written. Con: lockfile becomes a hypothetical-env pin (no actual 3.11 build event in this repo's history); may surface dep version conflicts (pandas 2.3.2 + numpy 2.3.1 both still support 3.11, but the resolution might prefer different versions on 3.11 vs 3.13); breaks reproducibility of every existing build.
- (c) **Range-pin `requires-python = ">=3.11,<3.14"`** (or similar) — broadest compatibility. Pro: future-flexible. Con: lockfile still resolves against one specific Python version (whichever `uv` picks at lock time); the range doesn't actually give resolver flexibility — it constrains downstream-consumer Python.

Recommendation: **(a) §11 plan-update to revise the §15 entry to `python:3.13-slim`** and pin `requires-python = "==3.13.*"` (or `>=3.13,<3.14`) in `pyproject.toml`. Matches every existing build event.

#### HALT #3 — §7.17 — Scope creep / dependency missing: §15 VERIFY criterion references `scripts/run_pipeline.py` at monorepo root; only `fetal_death/scripts/run_pipeline.py` exists.

§15 line 965 VERIFY: "`uv sync` + `python scripts/run_pipeline.py` produces parquets with current SHAs." Reality:

- `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/scripts/run_pipeline.py` — does not exist.
- `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/scripts/run_pipeline.py` — exists; rebuilds the V2.0 (29 years, 1.6M records) fetal-death parquet only. Does not orchestrate V2.1 / V3a / V3b / 2023-2024 extensions; does not orchestrate the natality or linked pipelines.
- The natality + linked pipelines run from `/Users/yoelplutchok/Desktop/natality-harmonization/` (a separate sibling repo) — their scripts/build-dir code is not in the monorepo.

The §15 VERIFY criterion presupposes a monorepo-root pipeline orchestrator. That orchestrator is **C8.7's scope** ("end-to-end pipeline smoke from monorepo root") per KICKOFF.md Tier 1 sequencing. C8.5 cannot satisfy its §15-named VERIFY without C8.7 first.

Options:

- (a) **§11 [plan-update]: revise §15 C8.5 VERIFY to use `uv sync` env-resolution check only** (no pipeline rebuild). Add a separate verifier: `uv sync && python -c "import pandas, pyarrow, numpy, matplotlib, pytest, nbclient" && pytest fetal_death/tests/ natality/tests/ tests/` (= "the env is sufficient to run the full test suite"). The pipeline-rebuild verification moves to C8.7 (which already plans to do this). Pro: aligns C8.5 scope with what's locally verifiable; C8.7 explicitly takes the pipeline-rebuild VERIFY responsibility. Con: weakens C8.5 VERIFY; relies on C8.7 for end-to-end closure.
- (b) **Author a stub monorepo-root `scripts/run_pipeline.py` that calls per-subproject pipelines** (scope creep into C8.7). Pro: C8.5 VERIFY closes per §15 literal. Con: scope creep (~0.5-1 session of work that belongs in C8.7); duplicates C8.7's intent.
- (c) **Use the per-subproject `fetal_death/scripts/run_pipeline.py` as the VERIFY witness.** Pro: minimal scope. Con: covers fetal-death only; doesn't address natality + linked; partial verification.
- (d) **Defer C8.5 to after C8.7.** Pro: VERIFY criterion fully satisfied per §15. Con: re-orders Tier 1 sequencing (§15/KICKOFF say C8.5 before C8.6; C8.7 is positioned after C8.6).

Recommendation: **(a) §11 [plan-update]: revise §15 VERIFY to "env-resolution check + test suite passes"** + explicitly leave the pipeline-rebuild VERIFY to C8.7. Mirrors the C8.6 entry which already has "CI gates on real invariant tests" as its VERIFY (test-suite-based, not pipeline-rebuild-based).

### Result

**HALT.** Three §7 conditions tripped (§7.2 docker missing; §7.12 Python version conflict; §7.17 VERIFY scope vs missing dependency). All three are PRE-FLIGHT-class — caught at cheap-check before any DO mutation. None are blockers to the eventual completion of C8.5; all are resolvable via user authorization at this PRE-FLIGHT halt-and-ask + a single combined `[plan-update]` commit revising §15 line 963 + line 965 + KICKOFF.md Tier 1 line 181 commentary (if needed). Tag `C8.5-pre-do` is **NOT yet placed** — it lands on the `[plan-update]` commit after user authorization, per the C8.2/C8.3 precedent.

A PRE-FLIGHT addendum will follow once user resolves the three halts; tag `C8.5-pre-do` lands on the `[plan-update]` commit and DO begins.

---

## PRE-FLIGHT addendum for C8.5 — 2026-05-13T04:30:00Z — All 3 HALTs resolved per user authorization; task split C8.5 → C8.5a + C8.5b; PROCEED to C8.5a DO

### Resolutions per user authorization (AskUserQuestion 2026-05-13T04:15:00Z)

- **HALT #1 (§7.2 docker missing) → option (a)**: Split C8.5 → **C8.5a** (lockfile, this session, fully verifiable) + **C8.5b** (Dockerfile, DEFERRED until docker available OR C8.6 CI ships). §11 [plan-update] commit ships the split.
- **HALT #2 (§7.12 Python version conflict) → option (a)**: Pin to **3.13.x** (matches build env). §15 line 963 revised from `python:3.11-slim` to `python:3.13-slim` (C8.5b entry); `pyproject.toml` `requires-python = ">=3.13,<3.14"`.
- **HALT #3 (§7.17 VERIFY scope) → option (a)**: Revise C8.5a VERIFY to **env-resolution + test-suite passes**. Pipeline-rebuild VERIFY moves to C8.7's responsibility. §15 C8.5a entry rewritten.

### §11 plan-update applied this commit

- `NEXT_STEPS.md` §15.C C8.5 entry rewritten into two entries: C8.5a (lockfile, this session) + C8.5b (Dockerfile, DEFERRED with resumption trigger documented).
- `KICKOFF.md` Tier 1 task list (line 181) split: `C8.5a` + `C8.5b` entries replace the single `C8.5`.
- `KICKOFF.md` sequencing note (line 202): `C8.5 + C8.6 paired` revised to `C8.5a + C8.6 paired` (C8.6 depends on lockfile only, not Dockerfile).
- This PRE-FLIGHT addendum records the resolution.
- `DECISION_LOG.md` 2026-05-13T04:30:00Z entry records the §11 plan-update.

### Post-resolution input state for C8.5a

- [x] `uv 0.11.10` ✓ at `/opt/miniconda3/bin/uv` (verified PRE-FLIGHT 04:00Z).
- [x] Python 3.13.9 (CPython, miniconda) — target lockfile pin.
- [x] Installed package versions enumerated at PRE-FLIGHT 04:00Z (pandas 2.3.2, pyarrow 18.1.0, numpy 2.3.1, matplotlib 3.10.5, pytest 9.0.2, nbclient 0.10.4).
- [x] `requirements.txt` (monorepo root + 2 subprojects) all present; will be preserved post-DO as discovery-pointers.
- [x] All four parquet SHAs unchanged from C8.4-complete state (must remain so post-C8.5a; this task is metadata-only).

### Outputs (intended) for C8.5a

- `pyproject.toml` (monorepo root, NEW) — PEP 621 metadata + `requires-python = ">=3.13,<3.14"` + exact-pin dependencies + dev-dependencies.
- `uv.lock` (monorepo root, NEW) — deterministic lock generated by `uv lock`.
- `.python-version` (monorepo root, NEW) — single-line `3.13`.
- `README.md` (existing, edit) — append section "Reproducibility via uv lockfile" describing the `uv sync` workflow.
- `RECEIPTS/C8.5a_<UTC>.md` — receipt at task close.

### Halt conditions tripped (post-resolution)

None. All three HALTs resolved via §11 plan-update + user authorization. C8.5a is fully locally verifiable.

### Result

**PROCEED to C8.5a DO.** Tag `C8.5-pre-do` (preserving the original C8.5 task ID for git-tag continuity with the C8.5 lineage; future C8.5b PRE-FLIGHT will tag `C8.5b-pre-do`) lands on this `[plan-update]` commit. DO step 1 authors `pyproject.toml` + runs `uv lock` to produce `uv.lock`; DO step 2 authors `.python-version` + README section; VERIFY runs the test-suite under the lockfile-defined env; RECEIPT at `RECEIPTS/C8.5a_<UTC>.md`.

---

## PRE-FLIGHT for C8.4 — 2026-05-13T01:30:00Z — Invariant tests: canonical-filter + row-count conservation + cross-product join parity — **RESULT: PROCEED**

### Scope summary

C8.4 §15.C entry (NEXT_STEPS.md lines 931–949): three new invariant test harnesses defending core analytic-correctness invariants per §8 H6 (silent row drops), §8 F2 (cross-product join without filter), §8 H9 (external targets cancel internal bugs), and §8 L3 (validator self-blindness — defended via mutation tests). Files land at monorepo-root `tests/` (NEW directory). Each harness carries a Convention 2 `DESIGN:` first-docstring tag and asserts SHAPE-not-VALUE invariants per Convention 1 (§4.2.1), with Tier-0 mutation tests asserting the harness fails predictably when an invariant is violated.

Three harnesses:
- **B.3** `tests/test_canonical_filter_invariants.py` — `DESIGN: structural-invariant-no-pins`. Sum-across-strata = unstratified-total for every canonical filter, every product, every year.
- **B.4** `tests/test_row_count_conservation.py` — `DESIGN: tracks-current-state`. Carries a documented-drops dict; asserts harmonized↔derived row equality per-product per-year (no drops between these stages); asserts total row counts match documented v2.4.0 / v2.8.0 / v3 envelope.
- **B.5** `tests/test_cross_product_join_parity.py` — `DESIGN: structural-invariant-no-pins`. Joint canonical-filter coverage; canonical join-key column presence; per-stratum natality vs `stratified_denominators.csv` parity.

Estimated effort 3 sessions per §15 (may close faster — Tier-1 tasks have run ~50% of their estimates).

### Inputs

- [x] All required parquets exist + match C8.3-complete (STATUS 2026-05-13T00:30:00Z) SHAs
  - `output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓ (verified by `shasum -a 256`)
  - `output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
  - `…/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
- [x] All four C8.3 FL-HALTs verified: PDF=`dd8b3203…` ✓, PNG=`f32ad101…` ✓, helper=`e3e74264…` ✓, JOINT_USE_GUIDE.md=`4569b0b4…` ✓, joint_use_demo.ipynb=`e0094812…` ✓, 4× `__init__.py` present (0 bytes each) ✓.
- [x] All required upstream tasks marked complete: `C8.1-complete` (`9fe662a`), `C8.2-complete` (`bb19c5a`), `C8.3-complete` (`ffbb4da` — HEAD) ✓.
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.4_*.md`: does not exist ✓
  - `tests/` at monorepo root: does not exist (good — this task creates it) ✓
- [x] `shared/helpers/canonical_join_keys.py` present and importable; `CANONICAL_JOIN_KEYS = [data_year, maternal_age, maternal_race_bridged, hispanic_origin, residence_status]`; `NATALITY_TO_CANONICAL` populated (kept for v2.7.0 backcompat; v2.8.0+ adopts canonical names natively — verified via column-name probe of the v2.8.0 parquet showing `data_year`/`residence_status`/`maternal_race_bridged`/`hispanic_origin` present natively).

### Environment

- [x] Python: 3.13.9 ✓
- [x] pandas: ≥2.3 (verified at runtime) ✓
- [x] pyarrow: ≥18.0 (verified at runtime) ✓
- [x] pytest: 9.0.2 ✓
- [x] Working directory clean (`git status --short` returns empty) ✓
- [x] On expected branch: `main`, HEAD=`ffbb4da` (`C8.3-complete`) ✓
- [x] Cache-cleared `pytest fetal_death/tests/ natality/tests/` reproduces 15 passed + 1 xfailed in 41.14s ✓ (C8.3 FL-HALT #5)

### Source documentation

- [x] Not applicable — C8.4 consumes no external PDFs; it only consumes already-validated parquets + the canonical-filter definitions documented in `docs/JOINT_USE_GUIDE.md` (sha `4569b0b4…`).

### Outputs

- [x] Intended output paths do not exist OR are explicitly marked for new
  - `tests/` (monorepo root): NEW directory ✓
  - `tests/__init__.py`: NEW (empty, namespace package per Convention from FIX_LOG 2026-05-12T22:30:00Z L17-extension) ✓
  - `tests/conftest.py`: NEW ✓
  - `tests/test_canonical_filter_invariants.py`: NEW ✓
  - `tests/test_row_count_conservation.py`: NEW ✓
  - `tests/test_cross_product_join_parity.py`: NEW ✓
  - `RECEIPTS/C8.4_2026-05-13T<ts>.md`: NEW ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.4 does not mutate any canonical parquet, schema CSV, or doc number. It authors NEW test files. The "cells being mutated" are the test-asset *assertions* themselves; the Field-value snapshot enumerates the **current parquet-derived invariants the new tests will assert**, so a future audit can verify the test was authored against the actual v2.4.0 / v2.8.0 / v3 state, not a stale assumption.

#### Parquet envelope (verified by `pyarrow.parquet.read_table` 2026-05-13T01:25:00Z)

| Product | Path | Rows | Years | residence_status uniques | tabulation_flag uniques |
|---|---|---|---|---|---|
| fetal_death harmonized | `output/harmonized/fetal_death_harmonized.parquet` | 2,427,233 | 1982–2024 (43 contiguous) | {1, 2, 3, 4} | {1, 2} |
| fetal_death derived | `…/fetal_death_derived.parquet` | 2,427,233 (= harmonized) | 1982–2024 | {1, 2, 3, 4} | {1, 2} |
| natality derived | `…/natality_v2_harmonized_derived.parquet` | 138,819,655 | 1990–2024 (35 contiguous) | {1, 2, 3, 4} | n/a (no tabulation_flag) |
| linked derived | `…/natality_v3_linked_harmonized_derived.parquet` | 74,943,824 | 2005–2023 (19 contiguous) | {1, 2, 3, 4} | n/a |

#### Canonical filters (from `docs/JOINT_USE_GUIDE.md` §"Canonical analytic filters")

| Product | Filter | Dtype literal |
|---|---|---|
| Natality | `residence_status != 4` | int8 |
| Linked | `residence_status != 4` | int8 |
| Fetal-death | `tabulation_flag == 2 AND residence_status != 4` | Int8 (both, post-v2.1.0 H8 cast) |

#### Canonical join keys (from `shared/helpers/canonical_join_keys.py`)

`CANONICAL_JOIN_KEYS = [data_year, maternal_age, maternal_race_bridged, hispanic_origin, residence_status]`. All five present in both fetal-death derived parquet (verified) and natality v2.8.0 derived parquet (verified).

#### Documented row-conservation invariants (the B.4 documented-drops registry)

- **harmonized ↔ derived (all three products):** **NO drops.** `derive.py` adds columns; row count must be conserved. Test asserts `len(harmonized) == len(derived)` per-product. Per-year row count also conserved.
- **No documented per-year drops at any pipeline stage** in any product's `DECISION_LOG` after the v2.4.0 / v2.8.0 / v3 releases — verified by `grep` against DECISION_LOG.md for "documented_drop" / "drop" / "exclude" → matches refer to filter exclusions (`residence_status == 4`, `tabulation_flag == 1`), not to silent row drops at parse/harmonize/derive boundaries.
- **The 2003–2004 fetal-death "deferred years" were not dropped; they are present in v2.1.0+.** Verified by `data_year` uniques showing {1982–2024} contiguous.

#### Canonical-filter invariant (the B.3 SHAPE check)

For each (product, year):
- `total_filtered = len(df[canonical_filter])`
- For every demographic stratum column S in {residence_status, tabulation_flag (FD only), maternal_race_bridged, hispanic_origin}:
  - `sum_across_S = df[canonical_filter].groupby(S, dropna=False).size().sum()`
  - assert `sum_across_S == total_filtered` (the grouping with `dropna=False` preserves null cells; sum across all strata including null must equal the unstratified total).

This is a SHAPE-not-VALUE invariant: it holds regardless of the specific count values; survives V2.x → V2.x+1 row-count growth; survives bridged-race-null era boundaries.

#### Cross-product join parity invariant (the B.5 SHAPE check)

For each year Y in the joint-coverage intersection {2005…2023} (where all three products are present):
- canonical-filter applied on all three sides
- After `to_canonical_natality()` rename, all three products expose `{data_year, residence_status, maternal_race_bridged, hispanic_origin, maternal_age}` columns
- For natality + linked: linked rows for year Y is a subset of natality rows for year Y (every linked birth is a natality birth); test asserts `len(linked_Y) <= len(natality_Y)` after canonical filter on both.
- For natality + fetal-death: independent populations (live births vs fetal deaths); the join-key columns must be present + compatible-dtype.
- For natality_per_year vs stratified_denominators.csv: per-year sum from CSV matches direct natality groupby on residence_status != 4 byte-exact (29 years — already verified at Task 1; this is the durable test).

- [x] Current values match task plan's assumed state ✓

### Halt conditions tripped

None. All §15-named inputs verified present; no §7 condition surfaced. The "documented drops" registry is empty (no documented drops at parse/harmonize/derive boundaries in any product's release notes), which means B.4's `tracks-current-state` design starts with an empty drops dict — clean.

### Result

**PROCEED.** Tag `C8.4-pre-do` lands on the commit that ships this PRE-FLIGHT entry. The DO phase authors three test files + an empty `tests/__init__.py` + a `tests/conftest.py` (shared fixtures for cross-product parquet loading at session scope) + runs Tier 0 mutation tests as part of each harness's authoring, then a cache-cleared combined-pytest VERIFY pass before tagging `C8.4-complete`.

---

## PRE-FLIGHT for C8.3 — 2026-05-12T22:30:00Z — Cross-product Tier-1: timeline + perinatal joint + Section B race validation — **RESULT: HALT**

### Scope summary

C8.3 §15.C entry (NEXT_STEPS.md lines 881–903): land three cross-product items in one task — (i) cross-product timeline figure (`shared/helpers/build_timeline_figure.py` + `figures/fig1_coverage_timeline.{pdf,png}`); (ii) three-product perinatal-mortality joint computation in `notebooks/joint_use_demo.ipynb` as a new Section C; (iii) Section B 2017 race-stratified NVSR validation, the deferred Task 4 fragment. §15 names PRE-FLIGHT inputs as "All three parquets (post-C8.2 refresh state); **NVSR 73-09 Table A for 2022 perinatal validation; NVSR fetal-mortality table for 2017 by maternal race** (PDF location verified at PRE-FLIGHT per L9); era-boundary metadata in each subproject's COMPARABILITY." Estimated effort 2 sessions.

This PRE-FLIGHT enumerates the §15 inputs read-only (no DO mutation), runs the Convention 3 Field-value snapshot for every cell/row/column the task would mutate, and runs the L9 cheap-checks on the two NVSR sources named in the §15 plan. **One HALT condition surfaced (§7.12 + planning error): two of the four NVSR source-location assumptions in the §15 plan do not match the actual NVSR contents.** Two of the three sub-items proceed cleanly; the third needs a scope clarification. PRE-FLIGHT result is HALT pending user decision on the Section B race-validation source year + race-classification.

### Inputs

- [x] All required parquets exist + match STATUS 2026-05-12T23:30:00Z (C8.2-complete) SHAs
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` (43 yrs 1982–2024, 2,427,233 rows × 73 cols) ✓
  - `…/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` (same row count, 89 cols, post-C8.2) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` (35 yrs 1990–2024, 138,819,655 rows) ✓
  - `…/natality_v3_linked_harmonized_derived.parquet` (19 yrs 2005–2023, 74,943,824 rows) ✓
- [x] Monorepo symlinks at `output/harmonized → /Users/.../fetal-death-harmonization-build/output/harmonized` intact ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - `C8.1-complete` tag at `9fe662a` ✓
  - `C8.2-complete` tag at `bb19c5a` ✓ (current HEAD; verified via `git tag --list 'C8.2*'`)
- [x] No stale checkpoints from previous incomplete runs
  - `RECEIPTS/C8.3_*.md`: does not exist ✓
  - `git tag --list 'C8.3*'`: empty ✓
- [x] Forward-looking HALTs from STATUS 2026-05-12T23:30:00Z (10 items) — verified
  - **#1** `C8.2-complete` + `C8.2-pre-do` tags present ✓
  - **#2** Post-C8.2 parquet SHAs match STATUS-recorded values ✓ (`38e2cecb…` + `185c071e…`)
  - **#3** V3b baseline parquets preserved as `.V3b_baseline.parquet` sidecars at `e3d6c64a…` + `4d1b37cc…` ✓
  - **#4** Smoke EXPECTED state pinned to 43 yrs / 2,427,233 rows ✓ (verified via `pq.read_table(columns=['data_year']).to_pandas()` row count + year set)
  - **#5** `field_specs.py` `layout_for_year` accepts 1982–2024 ✓ (no probe of 2025; not relevant to C8.3)
  - **#6** External validation 88/88 + 2 spot cells unchanged ✓
  - **#7** dtype-parity XFAIL still in place ✓
  - **#8** 4× `__init__.py` files still present ✓ (cache-cleared `pytest fetal_death/tests/ natality/tests/` produces 15 passed + 1 xfailed — confirmed implicitly via STATUS 23:30Z + commit log; not re-run at this PRE-FLIGHT)
  - **#9** Linked-2024-cohort refresh remains future-task — `2025PE2024CO.zip` still HTTP 404, no action this task ✓
  - **#10** Manuscript stale-numerics gap noted (43 yrs / 2.43M records in repo vs 29 yrs / 1.6M in `paper/draft_v2_hmd_styled.md`) — C8.3 does not edit the manuscript; flagged for Phase D step 6.

### Environment

- [x] Python: 3.13.9 (≥3.11) ✓
- [x] pandas + pyarrow 18.1.0 ✓
- [x] PyMuPDF: present (used for L9 PDF text-extraction probes during this PRE-FLIGHT) ✓
- [x] matplotlib: TBD — C8.3 DO needs it for the timeline figure; will verify before SMOKE. (Not a HALT; standard scientific-python install.)
- [x] nbformat + nbclient: present (per `_build_joint_use_demo.py` existing invocation) ✓
- [x] Working directory clean (`git status`): ✓
- [x] On `main` at commit `bb19c5a` (= `C8.2-complete`): ✓

### Source documentation

NVSR PDFs available on disk (in fetal-death build dir's `raw_docs/.../validation/`):

- `nvsr73-09.pdf` (Gregory et al. 2024, *Fetal Mortality: United States, 2022*, 21 pp) sha256=`2590e41719d1be949a2ad0e32c6497a747194020d26c38e4fcbecedced84c8d1` ✓
- `nvsr57_08.pdf` (MacDorman & Kirmeyer 2009, *Fetal and Perinatal Mortality, US 2005*, used for V2-era validation) sha256=`71c0b48ae71555b036952dbde1091e75a410327d240e66562fc9dbdb06b59861` ✓
- `nvsr64_09.pdf` (Mathews & MacDorman 2015, *Infant Mortality Statistics From the 2013 Period Linked Birth/Infant Death Data Set*, 30 pp) sha256=`bef51b1593a6d180abe9230ef05c2d24269f68468d36c6c05eb67fb8cc521304` ✓ — note: INFANT mortality, **not** "Fetal and Perinatal Mortality 2013" as the validation/INDEX.md memo claims (INDEX.md row needs a fix; documented below as a non-HALT finding).
- Other NVSR PDFs on disk for V2-era references: `nvsr55_06`, `nvsr56_03`, `nvsr60_08`; deep-history: `sr20_026`, `db169`.
- Natality NVSR: `Births_Final_Data_2005.pdf` through `Births_Final_Data_2020.pdf` at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_docs/nvsr/`. No 2021–2024 *Births: Final Data* PDFs on disk.

NVSR PDFs **not** on disk that the §15 plan implicitly assumes:

- §15 names **"NVSR fetal-mortality table for 2017 by maternal race"** as a PRE-FLIGHT input. **An NVSR titled "Fetal Mortality: United States, 2017" does not appear to exist.** L9 probe (this PRE-FLIGHT 22:00–22:25Z): probed every NVSR 65/66/67/68/69 PDF at `cdc.gov/nchs/data/nvsr/nvsr{vol}/nvsr{vol}_{nn}{,_-,_508,-508}.pdf` and scanned first-page text via PyMuPDF. Found NCHS "Fetal Mortality" annual reports: NVSR 70-11 (data year **2019**), NVSR 71-04 (**2020**), NVSR 72-08 (**2021**), NVSR 73-09 (**2022**); NVSR 65-07 (**Cause of Fetal Death** 2013); NVSR 69-04 (**Cause-of-Death from Fetal Death File 2015–2017** — note: this IS a cause-of-death focused report on 2015–2017 data, not a race-stratified fetal-mortality-rate report). **No standalone "Fetal Mortality: United States, 2017" exists.** NVSR 73-09 Table 1 publishes year-by-year fetal-death TOTALS 1990–2022 (and 20–27wk / 28+wk breakouts for 2014–2022) but **not race-stratified breakdowns for any year other than 2022**. So the §15 "NVSR fetal-mortality table for 2017 by maternal race" source assumption is incorrect: such a published cell does not exist.

### Outputs (intended)

Per §15 DO scope; targets do not yet exist (good):

- [x] `shared/helpers/build_timeline_figure.py` — does not exist ✓
- [x] `figures/fig1_coverage_timeline.pdf` — does not exist (`figures/` empty) ✓
- [x] `figures/fig1_coverage_timeline.png` — does not exist ✓
- [x] `notebooks/joint_use_demo.ipynb` — exists (will be MUTATED via re-build of `_build_joint_use_demo.py`); current sha=`39d2fb3c70494327…` (Section A 2022 by age + Section B 2017 by race-bridged; **DESIGN: tracks-current-state**)
- [x] `notebooks/_build_joint_use_demo.py` — exists; will be MUTATED; current sha=`7bab184c88dff6f9…`
- [x] `docs/JOINT_USE_GUIDE.md` — exists; **may be MUTATED** with a perinatal-mortality worked example per §15; current sha=`09266eae572bddf7…`
- [x] `RECEIPTS/C8.3_*.md` — does not exist ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

**Files this task will mutate (write or edit):**
- `notebooks/joint_use_demo.ipynb` (existing 2-section notebook → 3-section): adds Section C (three-product perinatal joint computation, 2022); MAY refresh Section B 2017 race-stratified content depending on user-resolution below. Currently asserts: `len(fd_2022) == 20202`, `len(nat_2022) == 3667758`, `len(fd_2017) == 22827`. All three match NVSR 73-09 Table 1 (2022 fetal deaths 20,202; 2022 live births 3,667,758; 2017 fetal deaths 22,827). ✓
- `notebooks/_build_joint_use_demo.py` (existing builder script): adds Section C build cells; minor edits to Section B comments depending on resolution.
- `figures/` (empty directory): new `fig1_coverage_timeline.{pdf,png}` + helper at `shared/helpers/build_timeline_figure.py`.
- `docs/JOINT_USE_GUIDE.md` (existing): the §15 plan calls for a new "perinatal mortality worked example." Current document has only the FMR worked example (lines 86-122).

**Files this task will NOT mutate** (Anti-Pattern #8 — not in scope):
- Any harmonized parquet (no canonical-data mutation).
- Any `harmonized_schema.csv` or `file_inventory.csv` (no schema change).
- Manuscript draft (Phase D step 6 territory).
- `external_validation_targets.csv` for any product (NVSR validation cells live in the notebook + this PRE-FLIGHT-log).

**Field-value snapshot for cells whose existence/values are load-bearing for C8.3 computations:**

| Target | Source | Current value | Used by |
|---|---|---|---|
| `fetal_death_derived[data_year=2022, tab_flag=2, res!=4].shape[0]` | post-C8.2 parquet | 20,202 (existing assert) | NVSR 73-09 Table 1 — total fetal deaths 2022, matches byte-exact |
| Same, gestational_age_*≥28wk | post-C8.2 parquet | **TBD** (DO Tier 0 compute) | Target = 9,956 per NVSR 73-09 Table 1 ("28 weeks or more" 2022 column); proportional-redistribution caveat applies |
| `natality_v2_harmonized_derived[year=2022, restatus!=4].shape[0]` | shipped parquet | 3,667,758 (existing assert) | NVSR 73-09 Table 1 — live births 2022, matches byte-exact |
| `linked_derived[data_year=2022, residence_status!=4, age_at_death_days<7].shape[0]` | shipped parquet | **TBD** (DO Tier 0 compute) | Sub-component for perinatal numerator; would validate against a 2022 linked-file infant-mortality NVSR (NVSR 73-XX series for 2022 cohort, NOT on disk; would need fetch) |
| `fetal_death_derived[data_year=2017, tab_flag=2, res!=4].shape[0]` | post-C8.2 parquet | 22,827 (existing assert) | NVSR 73-09 Table 1 — 2017 total, matches byte-exact. NO race breakdown published for 2017. |
| `fetal_death_derived[data_year=2017, …, maternal_race_bridged=k]` for k∈{1,2,3,4} | post-C8.2 parquet | (computed in joint_use_demo Section B; values not duplicated here) | Existing machinery demo, currently UNVALIDATED externally |
| NVSR 73-09 Table A (2022 race × Hispanic, single-race revised standard) | nvsr73-09.pdf p.6 | 7 rate cells: Total 5.48; AIAN 7.22; Asian 3.70; Black 10.05; NHOPI 10.36; White 4.48; Hispanic 4.63 | Potential alternative validation source — see Halt #1 |
| Era-boundary years for timeline figure | COMPARABILITY docs | Fetal: 1982/1989/1992/2003/2005/2018; Natality: 1990/2003/2014/2020; Linked: 2005/2016/2020 (see era-spec below) | Timeline figure spec |

**Era-band spec for timeline figure (from COMPARABILITY docs):**

| Product | Bands |
|---|---|
| Fetal death (1982–2024) | 1982–1988 V3b (1978-revision); 1989–1991 V3a (early 1989-rev); 1992–2002 V2 (1989-rev uniform); 2003–2004 V2.1 (transition); 2005–2017 V1 (2003-rev transition, 6.6%→96.2% A-version state-by-state); 2018–2024 V1+ uniform 2003-revision |
| Natality (1990–2024) | 1990–2002 1989-rev uniform; 2003–2013 2003-rev transition state-by-state; 2014–2019 2014-reformat (revised-only); 2020–2024 bridged-race-dropped era |
| Linked (2005–2023) | 2005–2015 denominator-plus cohort format; 2016–2023 period-cohort merged format. Sub-band 2020+ for bridged-race-dropped. |

### Halt conditions tripped

#### HALT #1 — §7.12 (Conflicting documentation) + planning error: §15 names two NVSR sources that don't match the actual NVSR contents

**Discovery.** §15 C8.3 entry (line 887) states:

> *"PRE-FLIGHT inputs. … **NVSR 73-09 Table A for 2022 perinatal validation; NVSR fetal-mortality table for 2017 by maternal race** (PDF location verified at PRE-FLIGHT per L9)."*

**Reality** (L9 cheap-check on NVSR 73-09 + NVSR-series probe):

- **(A) "NVSR 73-09 Table A for 2022 perinatal validation."** NVSR 73-09 is titled *"Fetal Mortality: United States, 2022"* — it does **not** publish perinatal-mortality rates. The earlier MacDorman/Gregory *"Fetal and Perinatal Mortality"* combined series ended with NVSR 64-09 era (last edition published was 2013-data-year per NCHS website). For 2022, NCHS publishes fetal mortality and infant mortality as separate annual reports; no single NVSR cell publishes the combined perinatal rate. **Furthermore, NVSR 73-09 Table A is "Fetal mortality rate, by selected characteristics and race and Hispanic origin of mother: United States, 2022"** — a 2022 fetal-mortality-by-race table, NOT a perinatal-mortality table. The §15 phrasing conflated three things: (1) "perinatal mortality rate" as a computed concept, (2) NVSR 73-09 (fetal-mortality-only), and (3) Table A (race-stratified).

- **(B) "NVSR fetal-mortality table for 2017 by maternal race."** No such NVSR exists. The NVSR "Fetal Mortality: United States, YYYY" annual series resumed with NVSR 70-11 (data year **2019**) after a gap; the series gap covers 2014–2018 data years. NVSR 73-09 Table 1 publishes 2014–2022 year-by-year fetal-death TOTALS (no race breakdown for 2014–2021; only 2022 has a race breakdown in Table A). Probe summary (L9 cheap-check at PRE-FLIGHT, ~30 min): probed `nvsr{65,66,67,68,69}_NN.pdf` covers via PyMuPDF text-extraction; found Cause-of-Fetal-Death reports (NVSR 65-07, NVSR 69-04) but no race-stratified fetal-mortality-rate report for 2017. The 2017 fetal-mortality-by-race tabulation is unpublished.

**Consequence.** As written, §15 C8.3's NVSR validation source is unworkable for both (i) the perinatal joint computation and (ii) the 2017 Section B race validation. The two cleanly-validate-able cells from existing on-disk sources are:

- **2022 28+wk fetal deaths = 9,956** per NVSR 73-09 Table 1 ("Fetal deaths 28 weeks or more" column for 2022). Useful for the 28+wk sub-component of the perinatal numerator.
- **2022 race-stratified fetal mortality rates** per NVSR 73-09 Table A (Total 5.48 + 6 race-Hispanic group rates). Useful for a 2022 race-stratified validation **IF** the joint_use_demo's race-stratification switches from `maternal_race_bridged` (null in fetal-death 2018+ and natality 2020+, so unavailable for 2022) to the single-race + Hispanic columns NCHS uses post-2018 (`race_hispanic_revised` in fetal-death, `maternal_race_ethnicity_5` in natality).

**Options for resolution (user decision required)**:

- **(a) RECOMMENDED — Re-scope Section B validation to 2022 single-race + Hispanic; reframe the perinatal joint computation as a demo without a full-rate NVSR cell.** Section B in joint_use_demo.ipynb switches to 2022 fetal-mortality by single-race + Hispanic groups (7 cells), validated against NVSR 73-09 Table A (on disk; no fetch needed). The existing 2017 bridged-race machinery is preserved in the notebook for backward documentation but no longer claimed as NVSR-validated — it remains a "machinery demo" closing the manuscript's joint-use bridge for the last-bridged-race-year. The perinatal joint computation (new Section C) computes the rate as a JOINT-USE DEMO using all three parquets for 2022, with **sub-component validations**: (i) 28+wk fetal-death count = 9,956 (NVSR 73-09 Table 1); (ii) <7-day early neonatal deaths from linked file — validated against any 2022 linked-file infant-mortality NVSR found, OR documented as unvalidated if no such NVSR exists. No claim of "perinatal mortality rate validated byte-exact." Pro: minimal NVSR-fetch friction (1 known PDF for sub-component (ii) — to be located in DO step 1 L9); strongest manuscript-relevant year (2022 = latest post-C8.2); no bridged-race availability issues. Con: drops the "2017 deferred Task 4 fragment" framing in favour of a more defensible 2022 validation.

- **(b) Preserve 2017 bridged-race Section B + drop NVSR validation claim there; do perinatal demo against the 2022 28+wk sub-component only.** Keep joint_use_demo Section B's existing 2017 machinery (machinery demo, no NVSR cell). Perinatal Section C uses 2022 with the 28+wk-only validation per (a). Pro: smallest scope change vs §15 plan. Con: leaves Section B externally unvalidated — defers the deferred-Task-4-fragment ambition again.

- **(c) Defer the 2017 race validation entirely; do a 2022 race validation as a new Section B' addition; drop perinatal entirely from this task.** Splits C8.3 into a smaller item that ships only the timeline figure + 2022 race validation; perinatal joint computation moves to a new C8.X candidate. Reduces this task to ~1 session. Con: a `[plan-update]` adding a new task, and the perinatal-joint demo is the most distinctive cross-product demonstration; moving it out feels like under-shipping.

- **(d) Halt C8.3 entirely, propose a `[plan-update]` that rewrites the §15 entry with explicit NVSR sources matching reality.** Pro: methodologically clean. Con: a session of plan-update overhead before any work.

#### Other findings (NOT HALTs)

- **L13-like INDEX.md soft-flag.** `…/fetal-death-harmonization-build/raw_docs/fetal_death/validation/INDEX.md` describes NVSR 64-09 as *"Fetal and Perinatal Mortality, United States, 2013 (MacDorman & Gregory)"*; the actual PDF cover (page 1, PyMuPDF text-extraction) reads *"Infant Mortality Statistics From the 2013 Period Linked Birth/Infant Death Data Set"* by Mathews/MacDorman/Thoma. Same volume number; different topic. This is one notch beyond LESSONS L13-extension (CSV inventory file-roles drift). No canonical-data impact in C8.3; the file is used for V2-era reference. FIX_LOG entry can be filed by a future audit / Phase D pre-flight that touches the validation/ inventory.
- **2017 fetal-death external_validation_targets.csv** has TWO existing rows: total 22,827 fetal deaths (NVSR 73-09 Table 1) + 2017 fetal-mortality rate 5.89 (NVSR 73-09 Table 1). Both PASS in current validation. The "deferred Task 4 fragment" was specifically the race-stratified cells, which are NOT in external_validation_targets.csv.
- **Manuscript line 99 numerical claim** *"Cross-product worked examples — a joint-use demonstration reproducing the 2022 maternal-age-stratified fetal mortality cells against NVSR 73-09 Table 4"* — verified. Section A in joint_use_demo.ipynb validates against NVSR 73-09 Table 4 (8/8 age cells); the manuscript's claim is accurate. C8.3 may add a sibling claim for the new Section C / Section B' work; manuscript edit is Phase D scope.
- **L9 cheap-check on NVSR 73-09 Table 1 contents:** the 2022 row of Table 1 publishes total 20,202; 20–27wk 10,246; 28+wk 9,956; live births 3,667,758; rates 5.48 / 2.79 / 2.71 per 1,000. Table 1 footnote: "Not stated gestational age proportionally distributed; see Technical Notes" — the 9,956 figure is post-redistribution. **Important downstream issue for Section C verify criterion**: our parquet's `gestational_age_*` columns store observed gestation values without proportional redistribution. The 28+wk count from a naïve filter will be slightly different from 9,956. The H8-class fix (auto-derive every NVSR-comparable cell from the parquet with redistribution if NCHS does redistribution) is C8.4-scope, not C8.3; for C8.3 we document the redistribution caveat in the receipt's Self-check and the notebook's Section C narrative. This is **not** a halt; it's a known tolerance.

### Result

**HALT** — One §7 condition tripped (§7.12 conflicting documentation: NVSR sources named in §15 do not match the actual NVSR series contents for both (i) 2022 perinatal validation and (ii) 2017 by-maternal-race fetal mortality). Do not proceed to C8.3 SMOKE/DO without user authorization on the Section B / Section C scope-and-validation strategy.

Forward-looking once resolved: DO step 1 will probe NCHS for a 2022 period-cohort-linked infant-mortality NVSR (likely under NVSR 73-XX series, e.g. NVSR 73-3 or NVSR 74-X candidates) for the early-neonatal sub-component validation in Section C. If found and fetch-able, the sub-component validation lands; if not, Section C narrative documents the absence and the perinatal-rate computation remains a JOINT-USE DEMO with one sub-component (28+wk fetal deaths) externally validated.

---

## PRE-FLIGHT addendum for C8.3 — 2026-05-12T23:50:00Z — HALT #1 resolved per user authorization; NVSR 73-05 located + PROCEED to SMOKE/DO

**User authorization received 2026-05-12T22:30Z** (single AskUserQuestion round): option **(a) 2022 race + perinatal demo (Recommended)**. §11 plan-update applied via DECISION_LOG entry 2026-05-12T23:50:00Z editing `NEXT_STEPS.md` §15.C C8.3 entry + `KICKOFF.md` line 179.

**Forward-looking follow-up resolved at addendum time:** Probed NVSR 73 + 74 series for a 2022 period-cohort-linked infant-mortality NVSR. **Found: NVSR 73-05** (Ely & Driscoll 2024, *Infant Mortality in the United States, 2022: Data From the Period Linked Birth/Infant Death File*, 19 pp, July 25, 2024) at `https://www.cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-05.pdf`. Fetched to `/tmp/c83_preflight/nvsr73-05.pdf`. sha256=`dccdc895022c3c9d3fbc07ffce18dc3238af797197f3cc6f0b35e463676c95cc`. Table 2 (page 10) verified containing:
- 2022 Total Infant Mortality Rate = 5.61 per 1,000 LB
- 2022 Early neonatal (<7 days) rate = **2.81** per 1,000 LB (headline for Section C sub-component validation)
- Late neonatal (7–27) = 0.78; Total neonatal = 3.59; Postneonatal = 2.02
- Race-stratified breakouts for each cell (AIAN 3.73; Asian 2.01; Black 5.05; NHOPI 3.36; White 2.23; Hispanic 2.65 for early neonatal column).

This closes the §15 C8.3 PRE-FLIGHT-input gap. The early-neonatal sub-component validation in new Section C now has a single on-disk NVSR cell (Total = 2.81/1000); race-stratified ENN validation is OPTIONAL in scope.

### Post-resolution input state (revised)

- NVSR 73-09 (on disk in build-dir; SHA `2590e417…`) ✓
- NVSR 73-05 (fetched to /tmp; sha `dccdc895…`); DO step 1 = move to `raw_docs/natality/nvsr/nvsr73-05.pdf` + add to `natality/metadata/file_inventory.csv` row + SHA-verify after move (per FIX_LOG 2026-05-12T01:30Z monorepo-path discipline).
- All three parquets at C8.2-complete SHAs ✓
- All era-boundary metadata sourced from COMPARABILITY docs ✓

### Halt conditions tripped (post-resolution)

(none — HALT #1 resolved via §11 plan-update; all other PRE-FLIGHT checks PASS)

### Result

**PROCEED** — to C8.3 SMOKE/DO under the revised §15.C scope. Tag `C8.3-pre-do` lands on this `[plan-update]` commit.

---

## PRE-FLIGHT for C8.2 — 2026-05-12T22:30:00Z — Latest-year refresh (fetal 2023+2024, linked 2024) — **RESULT: HALT**

### Scope summary

C8.2 §15.C entry (`NEXT_STEPS.md` lines 817-880) goal: extend fetal-death from 1982-2022 (41 yrs) → 1982-2024 (43 yrs) by parsing `Fetal2023US_COD.zip` + `Fetal2024US_COD.zip`; extend linked from 2005-2023 (19 yrs) → 2005-2024 (20 yrs) by parsing `2024PE2023CO.zip`. Three new source zips (~440 MB), three new user-guide PDFs.

This PRE-FLIGHT enumerates the §15 inputs read-only (no DO mutation), runs the Convention 3 Field-value snapshot for every cell/row/column the task would mutate, and verifies the STATUS 2026-05-12T22:00:00Z forward-looking HALTs. **Two HALT conditions surfaced; PRE-FLIGHT result is HALT pending user decision.**

### Inputs

- [x] All required input files exist (external)
  - `Fetal2023US_COD.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2023US_COD.zip` — HEAD HTTP=200, Content-Length=**2,219,550**, Last-Modified=Thu, 05 Dec 2024 16:18:30 GMT, ETag=`"3599a0523147db1:0"` ✓
  - `Fetal2024US_COD.zip` at same dir — HEAD HTTP=200, Content-Length=**1,925,286**, Last-Modified=Wed, 04 Feb 2026 12:21:08 GMT, ETag=`"52fea1bdd095dc1:0"` ✓
  - `2024PE2023CO.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/period-cohort-linked/2024PE2023CO.zip` — HEAD HTTP=200, Content-Length=**432,493,258**, Last-Modified=Thu, 22 Jan 2026 11:57:31 GMT, ETag=`"e1529449968bdc1:0"` ✓ — **BUT see HALT #1 below: this file represents cohort year 2023, already imported.**
- [x] User-guide PDFs (3 — one of three URL patterns corrected from §15 plan; see Source documentation below)
  - `2023fetaluserguide.pdf` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/2023fetaluserguide.pdf` (**path corrected** — see "L1-extension finding" below): HTTP=200, fetched to `/tmp/c82_preflight/2023fetaluserguide.pdf`, size=1,064,197, sha256=`947042d892ea1cf584392f55dbc833c30b7ff68b7290f5958164fefaf58863aa`, Last-Modified=Mon, 24 Feb 2025 20:20:59 GMT ✓
  - `2024fetaluserguide.pdf` at same corrected dir: HTTP=200, size=906,615, sha256=`63bcc8b1082db135f698ddc194d5ce59e0dfee9558027269e3873be289eecb42`, Last-Modified=Thu, 12 Mar 2026 12:47:24 GMT ✓
  - `24PE23CO_linkedUG.pdf` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/period-cohort-linked/24PE23CO_linkedUG.pdf` (matches §15 plan): HTTP=200, Content-Length=1,079,044, Last-Modified=Thu, 19 Feb 2026 15:52:41 GMT ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - C8.1 (tag `C8.1-complete` at `9fe662a`): ✓
  - `phase-c-authorized` tag at `0ba0279`: ✓
  - task7_v3b-complete at `b0c8b4a`: ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.2_*.md`: does not exist ✓
  - `git tag --list 'C8.2*'`: empty ✓
- [x] Forward-looking HALTs from STATUS 2026-05-12T22:00:00Z (10 items) — verified
  - **#1** `C8.1-complete` tag at `9fe662a` ✓; `C8.1-pre-do` tag at `04e6519` ✓
  - **#2** `fetal_death/harmonized_schema.csv` SHA `337a0ad0ab6d0a6b…` ✓ (will legitimately re-regen in C8.2 DO step 3)
  - **#3** `EXPECTED_YEAR_ROWS` dict has 41 entries (line 70 in `test_release_smoke.py`) ✓
  - **#4** `test_full_schema_type_matches_parquet_dtype` is xfail(strict=True) ✓ (XFAIL on isolated `pytest fetal_death/tests/` run)
  - **#5** `_regenerate_schema_years.py` exists, SHA `4275ed641fb76506…` ✓
  - **#6** `natality/tests/` exists with conftest.py + test_schema_dtype_parity.py ✓
  - **#7** Test count: claim was "16 tests across both subprojects" — **HALT-WORTHY**: see HALT #2 below.
  - **#8** `EXPLORATION_REPORT.md` unchanged (66,259 bytes, present at root) ✓; `KICKOFF.md` Phase C section unchanged ✓
  - **#9** Parquet SHAs: harmonized=`e3d6c64abcb7762d…` ✓; derived=`4d1b37cc3a214eea…` ✓
  - **#10** ~50 string-typed columns latent state still XFAIL ✓; 5 V2.1-fixed columns still int (`test_v21_h8_fixed_columns_remain_int` PASSes) ✓

### Environment

- [x] Python: 3.13.9 (≥3.11) ✓
- [x] pandas: present ✓ ; pyarrow 18.1.0 (≥18.0) ✓
- [x] PyMuPDF: present (needed for L12-extension `page.get_text()` PDF text-layer probes during SMOKE Tier 0) — verified via prior C8.1 work; no separate probe needed.
- [x] Working directory clean (`git status`): ✓
- [x] On `main` at commit `9fe662a`: ✓

### Source documentation

- [x] NVSR / NCHS user guides referenced by this task have current SHA-256s recorded above for the three new PDFs.
- [x] Existing 2022 fetal user guide (sibling-byte-position anchor for SMOKE Tier 0): `raw_docs/fetal_death/2022fetaluserguide.pdf` sha256=`d515813f89765af0ca2804afb7673f03e4efd4737f3de04e6939f9e7f43b20b3` ✓
- **L1-extension finding (URL drift; resolved):** §15 PRE-FLIGHT inputs cite "sibling-derived URLs at `…/Dataset_Documentation/DVS/fetaldeathus/{2023,2024}fetaluserguide.pdf`". Probed BOTH casings of the sibling-derived URL at `fetaldeathus/` → HTTP 404. NCHS reorganized the documentation directory; the canonical NCHS landing page (`cdc.gov/nchs/data_access/vitalstatsonline.htm`) directs to `…/Dataset_Documentation/DVS/fetaldeath/2023fetaluserguide.pdf` (note: `fetaldeath`, not `fetaldeathus`). Both 2023+2024 user guides verified at the corrected location. **Plan amendment**: at C8.2 DO step 3 (`file_inventory.csv` extension), the 2023+2024 rows' `doc_filename` URLs must use the new `Dataset_Documentation/DVS/fetaldeath/` prefix; the 2003-2022 rows' existing URLs in file_inventory.csv (`…/fetaldeathus/`) remain valid for the older user guides and need no change. This is one notch beyond the LESSONS L1-extension class (sibling-derivation correctly tried but the source FTP reorganized between releases).
- [x] All cited Zenodo DOIs resolve — `10.5281/zenodo.20031571` (fetal-death concept) + `10.5281/zenodo.19363074` (natality concept) — no new DOI fetch needed at PRE-FLIGHT.

### Outputs (intended)

Per §15 DO scope items 1-8; targets do not yet exist (good):

- [x] `raw_data/fetal_death/Fetal2023US_COD.zip` — does not exist (good) ✓
- [x] `raw_data/fetal_death/Fetal2024US_COD.zip` — does not exist (good) ✓
- [x] `raw_data/natality/2024PE2023CO.zip` — **already exists or already imported per `natality/metadata/file_inventory.csv` row `2023_linked` `imported=true`** — see HALT #1.
- [x] `raw_docs/fetal_death/2023fetaluserguide.pdf` — does not exist ✓
- [x] `raw_docs/fetal_death/2024fetaluserguide.pdf` — does not exist ✓
- [x] `raw_docs/natality/24PE23CO_linkedUG.pdf` — TBD (not probed; deferred until HALT #1 resolved)
- [x] New parquet outputs (post-rebuild): `output/harmonized/fetal_death_{harmonized,derived}.parquet` (mutate intended); V3b baseline preservation as `*.V3b_baseline.parquet` (new files; do not exist) ✓
- [x] `RECEIPTS/C8.2_*.md` does not exist ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

- **`fetal_death/file_inventory.csv`** (current sha=`c561fd9487e73e73…`, **32 data rows** covering 1989-2022 — verified last row `2022` present). C8.2 plan adds 2 rows (2023, 2024). No row already exists for 2023 or 2024. ✓
- **`fetal_death/external_validation_targets.csv`** (current sha=`83c58d68eca3941e…`, **84 data rows**). C8.2 plan adds 2 rows (one per new year). Last 2022 rows already present. ✓
- **`fetal_death/harmonized_schema.csv`** (current sha=`337a0ad0ab6d0a6b…`, 73 data rows post-C8.1 regen). Sample `years_available` cells:
  - `data_year` → `1992-2022` (plan: add `;2023;2024` per V3a/V3b convention)
  - `version_flag` → starts with `A,S` followed by year-range strings (regen-derived; plan: regenerate)
  - `tabulation_flag` → `1-2` (no change; allowed-values column not a year list)
  - `maternal_age` → `10-54;99` (no change)
- **`natality/metadata/file_inventory.csv`** (current sha=`0e31b92bc05b6011…`, **53 data rows**). Already contains `2023_linked` row pointing at `2024PE2023CO.zip` with `imported=true`. **NO 2024_linked row.** Adding one requires `2025PE2024CO.zip` which does not exist yet (probed → HTTP 404).
- **`natality/metadata/external_validation_targets_v3_linked.csv`** (current sha=`4bbc75072e2dfea1…`, **52 data rows**). Latest validation row covers 2023; no 2024 cells. NVSR Linked-File 2024 report would be source; not yet released (sibling of the data file being unavailable).
- **Linked parquet year coverage (current state on disk)**:
  - `natality_v3_linked_harmonized.parquet`: 74,943,824 rows × data_year ∈ {2005…2023} (19 yrs); sha256=`e1795ac615a6ee40b0d5813ac6f6c072692bc30808b746b3c3efb06cf5f357e7`
  - `natality_v3_linked_harmonized_derived.parquet`: same row count; data_year ∈ {2005…2023}; sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777`
- **Fetal-death parquet (current state)**: harmonized 41 yrs 1982-2022 (sha `e3d6c64abcb7762d…`), derived (sha `4d1b37cc3a214eea…`). Plan: rebuild as 43 yrs 1982-2024 (~110K new rows ≈ 55K × 2 yrs based on 2022's 40K).
- **`fetal_death/scripts/01_import/field_specs.py`** sha=`f67e5924ea7fc73a…`. C8.2 DO step 2: probe layout-byte deltas vs 2022; if no delta, reuse 2022 era_tag; if delta, add new era_tag (would bump SHA).
- **`fetal_death/scripts/01_import/parse_fetal_year.py`** sha=`e73ddb348deff53f…`. Plan: no edit expected; flagged for re-verification if `field_specs.py` mutates.
- **Smoke EXPECTED state** (`fetal_death/tests/test_release_smoke.py` sha=`6abeeb2c67b15165…`): EXPECTED_ROW_COUNT=2,352,011; EXPECTED_YEARS=1982-2022 (41); EXPECTED_YEAR_ROWS dict 41 entries. Plan: re-pin to 43-yr / new row count post-rebuild (tracks-current-state per Convention 2).

### Halt conditions tripped

Two HALT conditions surfaced during PRE-FLIGHT; do not proceed to DO.

#### HALT #1 — §7.12 (Conflicting documentation) + planning error: §15 C8.2 linked-file scope is a no-op at current state

**Discovery.** §15 C8.2 entry (line 819) states: *"Extend fetal-death from 1982-2022 (41 yrs) to **1982-2024 (43 yrs)** … and linked from 2005-2023 (19 yrs) to **2005-2024 (20 yrs)** by parsing the newly-released NCHS public-use files."* Listed source: `2024PE2023CO.zip` (NCHS released 2026-01-22; 432.5 MB).

**Reality (PRE-FLIGHT Field-value snapshot).**
- `natality/metadata/file_inventory.csv` row `2023_linked` points at `2024PE2023CO.zip` with `imported=true` — the file is already imported, NCHS-released 2026-01-22, well before the §15 entry was written 2026-05-12T21:00Z.
- The linked parquet on disk covers data_year ∈ {2005…2023} (19 yrs, 74,943,824 rows; SHAs above) — consistent with the file_inventory.
- NCHS naming pattern (verified across 5 existing rows): `YYYY+1`PE`YYYY`CO.zip` where the first `YYYY+1` is the period/release year and the second `YYYY` is the cohort year. `2024PE2023CO.zip` is the **cohort 2023** file; the **cohort 2024** file would be `2025PE2024CO.zip` (HTTP 404 — not yet released) or `2024PE2024CO.zip` (HTTP 404).
- The §15 entry conflated period year with cohort year.

**Consequence.** As written, C8.2's linked-file scope is unachievable at current world state. The linked parquet is already at maximum-extent for NCHS-public-use data; the next 1-year extension requires `2025PE2024CO.zip` which is not yet released (estimated NCHS cadence: 2027-Q1).

**Options for resolution (user decision required)**:
- **(a) Re-scope C8.2 to fetal-only** (drop linked-file work). Effort drops from 1-2 sessions to ~1 session. Linked-2024-cohort refresh becomes a `[plan-update]` candidate for whenever NCHS releases `2025PE2024CO.zip`. This is the LLM's recommended option.
- **(b) Defer C8.2 entirely** until NCHS releases the 2024-cohort linked file. Phase C reorders to start with C8.3 or C8.4 (which depend on C8.2's refreshed parquets per §15 line 903, 925 — so this option also requires §11 re-sequencing).
- **(c) Confirm the linked file is genuinely current** (no version bump; document the no-op in the receipt). Bump natality v2.8.0 → v2.9.0 anyway to acknowledge the refresh-checkpoint, OR leave natality at v2.8.0 since nothing changed.

#### HALT #2 — §7.18 (Reproducibility regression) + C8.1 test-infra latent bug: `pytest fetal_death/tests/ natality/tests/` errors at collection under default import mode

**Discovery.** STATUS 2026-05-12T22:00:00Z item 5 + forward-looking HALT #7 assert: "VERIFY: full pytest run `pytest fetal_death/tests/ natality/tests/` returns **15 PASSED + 1 XFAIL** in ~35 sec." Re-running the literal documented command at PRE-FLIGHT:

```
ERROR collecting natality/tests/test_schema_dtype_parity.py
import file mismatch:
imported module 'test_schema_dtype_parity' has this __file__ attribute:
  …/fetal_death/tests/test_schema_dtype_parity.py
which is not the same as the test file we want to collect:
  …/natality/tests/test_schema_dtype_parity.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename
```

Reproducible after `find … -name __pycache__ -delete`. Default pytest import mode (`prepend`) fails on duplicate module basenames across test directories that lack `__init__.py`. The C8.1 RECEIPT/STATUS claim is reproducible **only with `--import-mode=importlib`**: `pytest fetal_death/tests/ natality/tests/ --import-mode=importlib` → 15 passed, 1 xfailed.

**Consequence.** C8.6 (CI: GitHub Actions wiring) is scheduled to call `pytest fetal_death/tests/ natality/tests/` in CI; under default mode it will fail at collection. C8.2 itself doesn't gate on this, but C8.2 DO step 8 ("Refresh smoke EXPECTED_ROW_COUNT + EXPECTED_YEARS + EXPECTED_YEAR_ROWS") cannot meaningfully VERIFY via the documented combined-run command.

**Fix options** (cheap; pick one):
- **(a) Add `__init__.py`** to both `fetal_death/tests/` and `natality/tests/` — makes them proper namespace packages; pytest's `prepend` import then produces unique fully-qualified names (`fetal_death.tests.test_schema_dtype_parity` vs `natality.tests.test_schema_dtype_parity`). Trivial; ~30 seconds.
- **(b) Add `pyproject.toml`** with `[tool.pytest.ini_options]\naddopts = "--import-mode=importlib"`. Trivial; ~1 minute.
- **(c) Rename one of the test files** (e.g., `fetal_death/tests/test_fd_schema_dtype_parity.py`). 2 minutes; updates 1 test file, no other references.
- **(d) Defer to C8.6** (where CI wiring will encounter and force-fix). Document HALT here; C8.2 proceeds; the bug ships to C8.6.

The fix is **not part of C8.2 scope**; it's a C8.1 latent bug that should be filed in FIX_LOG (L17-extension or new "test-infra basename collision under default import mode" class). LLM recommends (b) bundled with C8.6 wiring — but a quick (a) right now is also reasonable since it's pure-defensive and unblocks the next runner of the documented combined-pytest command.

#### Other findings (NOT HALTs)

- **L1-extension URL-drift** for 2023+2024 fetal user guides (sibling-derived path `fetaldeathus/` returned 404; NCHS landing page at `cdc.gov/nchs/data_access/vitalstatsonline.htm` directs to `fetaldeath/`). Resolved at PRE-FLIGHT moment; no halt. File `file_inventory.csv` rows for 2023/2024 will use the corrected path at DO step 3.
- **cert-chain TLS warning** when probing NCHS FTP via curl (exit 60 `unable to get local issuer certificate`). Repo precedent (LESSONS L1-extension 2026-05-12T04:30:00Z) is `curl -sI -k` for read-only HEAD probes; that's what this PRE-FLIGHT used. For canonical-data DOWNLOAD at C8.2 DO step 1, integrity will be re-verified via SHA-256 against the values recorded above (`Fetal2023US_COD.zip` Content-Length=2,219,550 byte-exact; etag preserved). Cert-pinning option (`--cacert <path>`) is also available if the user prefers stricter verification at download time.

### Result

**HALT** — Two §7 conditions tripped (#1 §7.12 conflicting documentation; #2 §7.18 reproducibility regression on C8.1 test-infra). Do not proceed to C8.2 SMOKE/DO without user authorization on:

- Resolution of HALT #1 (re-scope C8.2 to fetal-only / defer entirely / something else).
- Resolution of HALT #2 (fix now as a C8.1-followup patch / fold into C8.6 / defer with documented FIX_LOG entry).

---

## PRE-FLIGHT addendum for C8.2 — 2026-05-12T22:45:00Z — both HALTs resolved per user authorization; PROCEED to SMOKE/DO

**User authorization received 2026-05-12T22:30Z** (single AskUserQuestion round):

- **HALT #1 → "Re-scope C8.2 to fetal-only (Recommended)"** — apply §11 plan-update editing `NEXT_STEPS.md` §15.C C8.2 entry + `KICKOFF.md` line 178. Linked-2024-cohort refresh deferred to a future task triggered when NCHS releases `2025PE2024CO.zip`. DECISION_LOG entry 2026-05-12T22:30:00Z files the [plan-update].
- **HALT #2 → "Add __init__.py to both test dirs now (Recommended)"** — shipped as separate `[c8.1-followup]` commit `b84ff0d` (4× `__init__.py` files at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/`); pytest co-collection now reproducible under default import mode (`pytest fetal_death/tests/ natality/tests/` → 15 passed, 1 xfailed in 38.77s on a cache-cleared run). FIX_LOG entry 2026-05-12T22:30:00Z files as L17-extension.

### Post-resolution input state (revised)

- 2 source zips (was 3): `Fetal2023US_COD.zip` + `Fetal2024US_COD.zip`. Linked `2024PE2023CO.zip` removed from scope (already imported as cohort 2023).
- 2 user-guide PDFs (was 3): `2023fetaluserguide.pdf` + `2024fetaluserguide.pdf` at corrected `Dataset_Documentation/DVS/fetaldeath/` URL. Linked `24PE23CO_linkedUG.pdf` removed.
- Field-value snapshot updated: no `natality/metadata/file_inventory.csv` or `external_validation_targets_v3_linked.csv` mutation needed.
- Smoke EXPECTED state still needs re-pin (43 yrs / new row count).
- Version bump now fetal-death-only: v2.3.0 → v2.4.0; natality v2.8.0 unchanged.

### Halt conditions tripped (post-resolution)

None.

### Result

**PROCEED** — Tag `C8.2-pre-do` lands on this `[plan-update]` commit. Subsequent commits execute the revised §15.C DO scope (downloads → layout probe → harmonize → version bump → smoke retag → receipt → tag `C8.2-complete`).

---

## PRE-FLIGHT for C8.1 — 2026-05-12T21:15:00Z

### Scope summary

Three sub-steps under one PRE-FLIGHT umbrella per §4.1 L10 ("multi-sub-step tasks require either (a) one upfront PRE-FLIGHT enumerating every sub-step's inputs, or (b) per-sub-step PRE-FLIGHT before each sub-step's DO. Back-fill is forbidden.").

- **DO-1 (path-drift fix)**: copy `_regenerate_schema_years.py` from standalone-build `scripts/` into monorepo `fetal_death/scripts/`; fix `fetal_death/tests/conftest.py` parquet/schema path constants to monorepo-canonical locations.
- **DO-2 (smoke retag)**: edit `fetal_death/tests/test_release_smoke.py` to add Convention 2 `DESIGN: tracks-current-state` first-docstring tag, repin EXPECTED_ROW_COUNT/YEARS/YEAR_ROWS to V3b state, expand test 5 version_flag='S' assertion from 1992-2002 → 1982-2002 (V3b + V3a + V2 eras all synthesize 'S' per harmonize.py), re-verify NVSR_2010_ANCHOR.
- **DO-3 (dtype parity)**: author `fetal_death/tests/test_schema_dtype_parity.py` + new `natality/tests/test_schema_dtype_parity.py` (natality currently has no test directory) with Convention 2 `DESIGN: tracks-current-state` first-docstring tag.

### Inputs

- [x] All required input files exist
  - `fetal_death/tests/test_release_smoke.py`: present, sha256=`0006dc7934fd9504…` (185 lines; pins V2.0 state)
  - `fetal_death/tests/conftest.py`: present, sha256=`43e699f1b55f58a0…` (93 lines; paths point at `REPO_ROOT/output/...` where REPO_ROOT = `fetal_death/`)
  - Standalone-build `~/Desktop/fetal-death-harmonization-build/scripts/_regenerate_schema_years.py`: present, sha256=`bc457abd907e1649…` (source of DO-1 copy)
  - `fetal_death/harmonized_schema.csv`: present, sha256=`69f92bf775251f1e…` (73 rows; matches STATUS 18:45Z FL-HALT)
  - `natality/metadata/harmonized_schema.csv`: present, sha256=`8a3c1cd347ec22aa…` (94 rows)
  - `output/harmonized/fetal_death_harmonized.parquet`: present, sha256=`e3d6c64abcb7762d…` (matches STATUS 20:30Z FL-HALT 8; 2,352,011 rows × 73 cols)
  - `output/harmonized/fetal_death_derived.parquet`: present, sha256=`4d1b37cc3a214eea…` (matches; 2,352,011 rows × 89 cols)
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`e16ad5323d68e28d…` (138,819,655 rows × 84 cols)
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, sha256=`9b828a4de4e59b17…` (74,943,824 rows × 94 cols)
- [x] All required upstream tasks marked complete in STATUS.md
  - task7_v3b-complete (2026-05-12, commit b0c8b4a): ✓
  - phase-c-authorized (this session's prior commit 0ba0279): ✓
- [x] No stale checkpoints from previous incomplete runs
  - `RECEIPTS/C8.1_*.md`: does not exist (good) ✓
  - `fetal_death/scripts/_regenerate_schema_years.py`: does not exist (good — DO-1 creates it) ✓
  - `fetal_death/tests/test_schema_dtype_parity.py`: does not exist (good — DO-3 creates it) ✓
  - `natality/tests/`: does not exist (good — DO-3 creates the directory + test file) ✓

### Environment

- [x] Python version: 3.13.7 (≥3.11 ✓)
- [x] pandas: 2.2.x (≥2.3 — close enough; existing pipelines run on it ✓)
- [x] pyarrow: 21.0.x (≥18.0 ✓)
- [x] pytest: available (existing fetal_death/tests/ assumes it)
- [x] Working directory clean (`git status` post-plan-update-commit): ✓
- [x] On expected branch (`main`, HEAD=`0ba0279` post-plan-update): ✓

### Source documentation

- [x] No NVSR PDFs / NCHS user guides referenced in this task — C8.1 is test infrastructure work, not data harmonization. SHA verification of source PDFs deferred to per-task PRE-FLIGHTs that consume them.

### Outputs

- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `fetal_death/scripts/_regenerate_schema_years.py`: NEW (DO-1 creates) ✓
  - `fetal_death/tests/conftest.py`: EXPLICIT EDIT (DO-1 path-constant fix) — current SHA `43e699f1b55f58a0…` preserved for receipt diff ✓
  - `fetal_death/tests/test_release_smoke.py`: EXPLICIT EDIT (DO-2 retag + repin) — current SHA `0006dc7934fd9504…` preserved for receipt diff ✓
  - `fetal_death/tests/test_schema_dtype_parity.py`: NEW (DO-3 creates) ✓
  - `natality/tests/__init__.py` + `natality/tests/test_schema_dtype_parity.py`: NEW (DO-3 creates new directory + files) ✓
  - `RECEIPTS/C8.1_<timestamp>.md`: NEW (post-VERIFY) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Target rows / cells enumerated; current values verified against the task plan's assumed state.

**DO-1 (path-drift fix) — target cells in `fetal_death/tests/conftest.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 16 | `REPO_ROOT = Path(__file__).resolve().parent.parent` | unchanged ✓ |
| 18 | `HARMONIZED_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"` | change to monorepo-root-relative: `REPO_ROOT.parent / "output/harmonized/fetal_death_harmonized.parquet"` (monorepo `output/` is at top level via symlinks) |
| 19 | `DERIVED_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_derived.parquet"` | same: `REPO_ROOT.parent / "output/harmonized/fetal_death_derived.parquet"` |
| 20 | `SCHEMA_CSV = REPO_ROOT / "metadata/harmonized_schema.csv"` | change to flat layout: `REPO_ROOT / "harmonized_schema.csv"` (per monorepo `fetal_death/harmonized_schema.csv` — no `metadata/` subdir) |

**DO-1 (path-drift fix) — target lines in `fetal_death/tests/test_release_smoke.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 43-46 | `_REPO_ROOT = Path(__file__).resolve().parent.parent` + `_SCRIPTS_DIR = _REPO_ROOT / "scripts"` + sys.path insert | unchanged ✓ (after DO-1's copy of `_regenerate_schema_years.py` into `fetal_death/scripts/`, the import path resolves correctly) |
| 48 | `from _regenerate_schema_years import compute_years_available  # noqa: E402` | unchanged ✓ |

**DO-2 (smoke retag) — target lines in `fetal_death/tests/test_release_smoke.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 1 | `"""V2.0 release smoke suite.` | prepend `"""DESIGN: tracks-current-state` then `\n` then existing prose; update title `V2.0` → `V2.3.0 (V3b)` |
| 50 | `EXPECTED_ROW_COUNT = 1_634_195` | `EXPECTED_ROW_COUNT = 2_352_011` (post-V3b state) |
| 51 | `EXPECTED_HARMONIZED_COLS = 73` | unchanged ✓ (SHAPE invariant preserved by V3b — verified) |
| 52 | `EXPECTED_DERIVED_COLS = 89` | unchanged ✓ (SHAPE invariant preserved) |
| 53 | `EXPECTED_YEARS = tuple(list(range(1992, 2003)) + list(range(2005, 2023)))` | `EXPECTED_YEARS = tuple(range(1982, 2023))` (41 contiguous years 1982-2022) |
| 56-63 | `EXPECTED_YEAR_ROWS = {1992: 70929, ..., 2022: 40113}` (29 entries) | replace with 41-entry dict per parquet probe results (1982:62352, 1983:60584, ..., 2022:40113) |
| 67 | `NVSR_2010_ANCHOR = 24258` | re-verify (V2.1 B7 TABFLG correction did NOT touch 2010; expect unchanged but verify in DO-2) |
| 94-95 | `assert 2003 not in years; assert 2004 not in years` | REMOVE (V2.1 added these years) |
| 109 | `v2 = df[df["data_year"].between(1992, 2002)]` | `v2 = df[df["data_year"].between(1982, 2002)]` (expand to V3b + V3a + V2 eras, all synthesize 'S' per harmonize.py) |
| Module docstring lines 13-15 | "(1992-2002 + 2005-2022; 2003/2004 deferred to V2.1)" | "(1982-2022 contiguous 41 yrs after V3a + V3b + V2.1 extensions)" |

- Current parquet probe confirms:
  - row count 2,352,011 (matches new pin) ✓
  - year set is 41 contiguous 1982-2022 ✓
  - 1982-2002 (V3b + V3a + V2) all version_flag='S' (421,125 + 188,909 + 700,704 = 1,310,738 rows; zero non-S) ✓
  - 2003-2004 (V2.1) is MIXED 'S' (104,824) + 'A' (2,958) — exclusion correct ✓
  - 2005-2022 (V1) is MIXED 'A' (602,306) + 'S' (331,185) — exclusion correct ✓

**DO-3 (dtype parity test) — new file content spec:**

- `fetal_death/tests/test_schema_dtype_parity.py`: ~80 lines. Reads `fetal_death/harmonized_schema.csv` (73 rows, type column values: 58 'int', 13 'str', 1 'int32', 1 'float'). Reads `fetal_death/output/harmonized/fetal_death_derived.parquet` (89 cols; superset of schema's 73). For each schema row, find the parquet column with matching `harmonized_name` (raise on missing); verify the parquet's pyarrow type maps to schema's `type` value per the canonical type-class table:
  - schema 'int' → pyarrow `int8|int16|int32|int64|uint*` (any integer)
  - schema 'str' → pyarrow `string|large_string|binary|object`
  - schema 'int32' → pyarrow `int32` strictly
  - schema 'float' → pyarrow `float32|float64`
- `natality/tests/test_schema_dtype_parity.py`: ~100 lines. natality's schema uses pyarrow physical type names directly ('int8', 'int16', 'bool', 'string', 'int32', 'float32', 'float64') so the test does strict pyarrow-physical-type matching. Tests both natality parquet (84 cols) and linked parquet (94 cols); schema rows covering 94-col superset; per-row test enforces match against whichever parquet the column appears in (using `years_available` cell to disambiguate).

### Halt conditions tripped

None. All inputs present; SHAs match STATUS 20:30Z FL-HALTs; outputs do not yet exist; parquet probe matches plan-assumed state byte-for-byte (row count, year set, version_flag distribution).

### Result

**PROCEED.** Tag `C8.1-pre-do` on the commit landing this PRE-FLIGHT entry.

---



### Scope summary

Extend fetal-death coverage backward by 7 years from current 1989-2022 (V3a state, 34 years; `task7_v3a-complete` at monorepo `06f1bf4`) to 1982-2022 (41 years), by parsing 7 raw zips for 1982-1988 through a new 1978-revision parser dispatch and re-running harmonize + derive against an extended era set. The 1978-revision layout is **structurally different** from V3a/V2.0's 1989-revision (per STATUS 2026-05-12T15:00Z critical finding 2): 200-byte records (vs 360); different field names (no DATAYEAR/TABFLG/MAGER/MRACE; instead "Data year", "Tabulation inclusion", "Age of Mother", "Race of Mother"); different byte positions (AGE @ 81-82 vs MAGER @ 89-90; RACE @ 86 single-byte vs MRACE @ 79-80). New version: v2.3.0 (additive backward extension; no schema-version-breaking mutation — schema columns unchanged, only `years_available` strings + `raw_source_by_year` cells extend backward).

Page-4/5/6 cheap-check across all 7 V3b user guides (this PRE-FLIGHT, see Source documentation below) confirmed **byte-identical field positions** in the "List of Data Elements" overview for items 1-10 spanning bytes 1-200. Q23 resolved: **shared `record_layout_1982_1988.csv`** is feasible (with per-year sub-field value-distribution verification deferred to L13-extension discipline during DO, per STATUS 15:00Z FL-HALT 4).

Per KICKOFF.md "Current planned sequence" step 2 (already executed for V3a; V3b expands the same step per KICKOFF's "When to deviate" clause: "If STEP 0 finds V3b documentation: ADD V3b to step 2's scope (don't change the sequence order)"). User direction this session ("finish all data extensions before github/zenodo"; STATUS 2026-05-12T15:00Z) is the authorization basis; the explicit DO-start gate is the closing HALT of this PRE-FLIGHT (see Result section).

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build location**: canonical mutation target is the **monorepo** (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/`), per the V3a precedent. `raw_data/fetal_death/`, `raw_docs/fetal_death/`, and `output/` are symlinks to the sibling build dir (`~/Desktop/fetal-death-harmonization-build/`); harmonize.py + parse_fetal_year.py + validate scripts resolve `_PROJECT.parent` correctly per V3a (commit `06f1bf4`).

2. **Input rearrangement (PROPOSED at this PRE-FLIGHT; executed at DO step 1)**: V3b zips currently at `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1982..1988}US.zip` (top-level, NOT in `fetal_death/` subdir; NOT visible to monorepo symlink). V3a precedent: `mv` zips into `raw_data/fetal_death/` subdir for monorepo-symlink visibility. SHAs preserved (pure file-system move). All 7 zips verified present this PRE-FLIGHT with SHAs byte-exact to STATUS 2026-05-12T03:50Z baselines.

3. **User-guide downloads (executed at this PRE-FLIGHT)**: 7 PDFs newly downloaded to `raw_docs/fetal_death/` from canonical NCHS FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (same convention as 1989-2022 user guides already on disk). Content-length byte-exact to HEAD probes for all 7. SHAs recorded below; 1985 + 1988 SHAs match the 2026-05-12T15:00Z PoC baselines byte-exact.

4. **NVSR control source identified for 1982-1988**: per-year user-guide control count from **MACHINE/FILE/DATA CHARACTERISTICS → 12. Data counts → b. With stated or presumed gestation of 20 weeks or more → 2. By residence** (page 7 of each user guide, same structure as V3a's 1989-1991 control-count source). Values extracted via PyMuPDF text-layer this PRE-FLIGHT, with OCR-disambiguation against context (monotonic decline 1982-1988; ~30-60 record diff between by-occurrence and by-residence consistent with adjacent years).

5. **Q23 resolution**: **ONE shared `record_layout_1982_1988.csv`** for all 7 years (not 7 per-year CSVs). Justified by page-4/5/6 byte-identical field-position cheap-check across all 7 years. Per-year sub-field value-distribution verification still required at DO time per L13-extension; the shared CSV reduces edit surface and matches the empirical uniformity of the 1978-revision layout across 1982-1988.

6. **Q22 resolution**: user-guide downloads **folded into PRE-FLIGHT** (executed this session), matching V3a pattern (V3a downloaded 3 user guides during PRE-FLIGHT at 2026-05-12T14:05Z). No separate housekeeping commit.

### Inputs

- [x] All required input files exist (verified by direct check at this PRE-FLIGHT timestamp)
  - **Raw V3b zips** (build-dir top-level; staging-decision 2 will `mv` to `raw_data/fetal_death/` at DO step 1):
    - `Fetal1982US.zip` sha256=`56ddf02376cb17116ea4ac58b65908cb68aaca6b1efcef3a0ea062c1dc74bc2b` (matches STATUS 2026-05-12T03:50Z `56ddf02376cb1711…`) ✓
    - `Fetal1983US.zip` sha256=`c44b65d1aac15d76032b91a591831635dfdba234bf7619506586ebe1d5a67d5a` (matches `c44b65d1aac15d76…`) ✓
    - `Fetal1984US.zip` sha256=`e74c45516a90adcd26c1723b9f593f5c34088c0e2dcc699f00d0e00fb8a6fec8` (matches `e74c45516a90adcd…`) ✓
    - `Fetal1985US.zip` sha256=`cb57279c3bc430ca40154fdf17a489308b542f5cd35522eaf8060513c0ea25e2` (matches `cb57279c3bc430ca…`) ✓
    - `Fetal1986US.zip` sha256=`864d93dd255c33f5f876585ff0c19b8f3ceb504eaa7522f92978d3a1647d0e92` (matches `864d93dd255c33f5…`) ✓
    - `Fetal1987US.zip` sha256=`5bbd2b356ce6ab720873d7b2cf7cd1bbbfdf57d0da43e42d8cb4376e0789cb6a` (matches `5bbd2b356ce6ab72…`) ✓
    - `Fetal1988US.zip` sha256=`e6c733dbda5cd5a5d389cb1400c9b1b5d16082fcf42dbfc137b741a2453b20fd` (matches `e6c733dbda5cd5a5…`) ✓
  - **V3b user guides** (newly downloaded this PRE-FLIGHT to `raw_docs/fetal_death/` via monorepo symlink):
    - `1982FetalUserGuide.pdf` 17,331,782 B (matches HEAD content-length) sha256=`f812d88471502669b9e46953a536ecc6948462e0356fc55a19ca8cf11e934486` ✓
    - `1983FetalUserGuide.pdf` 18,412,560 B (matches) sha256=`959de19f88fa413fa813f913269ce800400a5027794a304e930e08ced4916ebd` ✓
    - `1984FetalUserGuide.pdf` 17,957,381 B (matches) sha256=`a32126a422fcf7fd2ffffc0ab5bc19582c52b951b099597f956e2ad1cd3db722` ✓
    - `1985FetalUserGuide.pdf` 19,114,655 B (matches) sha256=`f7342480302017caf622243510c7e32ea03b6083b9797768b59fa50954eb1ed5` (matches PoC baseline byte-exact) ✓
    - `1986FetalUserGuide.pdf` 19,495,712 B (matches) sha256=`35c3676618e021011a28c78b2e857124d076544e00bef916a1834b3e5db65515` ✓
    - `1987FetalUserGuide.pdf` 17,859,810 B (matches) sha256=`fbb783d978cdc967e9d82187b9b1b46d06a0f1cf501f293057627c754370a7f2` ✓
    - `1988FetalUserGuide.pdf` 18,417,693 B (matches) sha256=`66eb8b2440e63632fe1c081801d7e9a04b3c87d7618263b8dc8ea0be4daae967` (matches PoC baseline byte-exact) ✓
  - **Existing canonical reference files** (V3a/V2 era state at task7_v3a-complete; V3b extends without mutating these):
    - `fetal_death/scripts/01_import/field_specs.py` sha256=`7a99641984eb5e83a78186bdee7a18184cf22296b0d48a431e1a27e96f2eba5c` (post-V3a; current `layout_for_year` covers 1989-2022; V3b adds 1982-1988 branch) — DO step 3 edit target ✓
    - `fetal_death/scripts/03_harmonize/harmonize.py` sha256=`acad3b5bb04f16c00cdb7bb0925009e61f342b85464848811d5cd19526b42e0c` (post-V3a; `_era_tag()` line 84-96 + `_build_field_map()` line 38-81 + B3 maternal_race_bridged recode line 264-298 are DO step 4 edit targets) ✓
    - `fetal_death/variable_crosswalk_working.csv` sha256=`e72190aac63375bd465613ade4b2b14a2af9ca71fb3f5fab8ddb42e9f767043c` (74 rows × 13 cols; current `field_1992`/`field_2006`/`field_2014`/`field_2022` columns; V3b adds `field_1985,pos_1985` columns) — DO step 5 edit target ✓
    - `fetal_death/harmonized_schema.csv` sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (matches Task 3 V2.1 PRE-FLIGHT 2026-05-11T21:30Z baseline byte-exact — schema rows unchanged across V2.1/V3a; V3b extends `years_available` + `raw_source_by_year` cells without breaking the schema) — DO step 6 edit target ✓
    - `fetal_death/external_validation_targets.csv` sha256=`83c58d68eca3941ee5bf589981daa777b22e49e0eb950e05faf7c4326a5df3c1` (post-V3a; +7 V3b rows additive) — DO step 11 edit target ✓
    - `fetal_death/file_inventory.csv` sha256=`c561fd9487e73e73c3dd80a15d631cca4f8344da88b554efe063d7f3cdf306a5` (post-V3a; +14 V3b rows additive) — DO step 11 edit target ✓
  - **V3a output baselines** (Forward-looking HALT 2 from STATUS 2026-05-12T14:30Z verified at session start): all 5 parquet SHAs byte-exact ✓
    - `output/harmonized/fetal_death_harmonized.parquet` sha=`23c56a9d6a0948b4ad985b534bc515f6850d9bea439b1fee8801fa70a5268f69` (V3a baseline)
    - `output/harmonized/fetal_death_derived.parquet` sha=`0dd3aec0e47785f191c17df83ef6af91884ca350c0edca7df657f232374165c4` (V3a baseline)
    - `output/yearly_clean/fetal_death_1989_raw.parquet` sha=`8dc050a3c03906642f51aa75c251e963517445b7749755cb203c266e86a1f87d` (V3a baseline)
    - `output/yearly_clean/fetal_death_1990_raw.parquet` sha=`cc5c840156cc3ab600bffdb595b1b6a3d20b21288e4be659f7b149825d951b27` (V3a baseline)
    - `output/yearly_clean/fetal_death_1991_raw.parquet` sha=`18ac106ac63c8487c1e5362fd05282452ab26a0ed9e7eafbb67388a86bc6040a` (V3a baseline)
- [x] All required upstream tasks marked complete in STATUS.md
  - `task7_v3a` (V3a backward extension to 1989-1991): COMPLETE 2026-05-12 at monorepo `06f1bf4` (`task7_v3a-complete` tag) ✓
  - `task3_v21_fetal_death` (V2.1, 2003+2004 transition): COMPLETE 2026-05-12 (`task3-complete` tag) ✓
  - `natality_v28_rename` (column canonicalization): COMPLETE 2026-05-12 (`natality_v28_rename-complete` tag) ✓
  - V3b OCR feasibility PoC (text-layer extraction works): COMPLETE 2026-05-12T15:00Z (commit `58b59f1`) ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `task7_v3b_*` tags in monorepo (verified: `git tag --list 'task7_v3b*'` empty) ✓
  - No partial V3b edits in canonical work tree — monorepo tree CLEAN at `58b59f1` ✓
  - No `output/yearly_clean/fetal_death_198{2..8}_raw.parquet` files exist (good — DO step 7 will create) ✓
  - No `fetal_death/record_layout_1982_1988.csv` exists (good — DO step 2 will create) ✓
  - Tier-0 byte-length probe confirms zips parse at 200-byte records:
    - `unzip -p Fetal1985US.zip | head -1 | wc -c` = 201 (200 data + LF) per STATUS 2026-05-12T03:50Z probe; re-verifiable at DO step 7 ✓
    - All 7 user guides' page-7 "Record length: 200" entries text-extracted this PRE-FLIGHT — uniform 200-byte record length across 1982-1988 ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] PyMuPDF (fitz) version 1.27.2.2: available for user-guide detail-record layout extraction (no Tesseract needed; V3b OCR PoC STATUS 2026-05-12T15:00Z confirmed text-layer is embedded in NCHS's 2009-rescan batch PDFs uniform across 1982-1988)
- [x] Working directory clean (`git status` in monorepo): CLEAN at `58b59f1` ✓
- [x] On expected branch: monorepo `main` ✓
- [x] Build-dir `~/Desktop/fetal-death-harmonization-build/` is not a git repository (verified V3a PRE-FLIGHT 2026-05-12T14:05Z); data-backing-store only. Canonical version control remains in the monorepo.

### Source documentation

- [x] **Page-4/5/6 cross-year diff** (this PRE-FLIGHT, Q23 cheap-check): all 7 V3b years have byte-identical field byte-positions in the "List of Data Elements and Tape Locations" overview. Uniform field positions confirmed:
  - General: Data year @ 1-2; Reporting area @ 3; Tabulation inclusion @ 10; Record type @ 11; Resident status @ 12
  - Occurrence: NCHS State @ 13-14; NCHS County @ 15-17; FIPS State @ 187-188; FIPS County @ 189-191; Expanded NCHS State @ 21-22
  - Residence: NCHS State @ 23-24; NCHS County @ 25-27; City @ 28-30; Population size @ 31; Met/Nonmet @ 32; FIPS State @ 192-193; FIPS County @ 194-196; FIPS SMSA @ 197-200; NCHS SMSA @ 38-40
  - Dates: LMP @ 47-51; Delivery @ 52-55; Place of delivery @ 56
  - Mother (bytes 81-90 umbrella): Age @ 81-85 (5-byte umbrella; AGE specifically @ 81-82 per STATUS 2026-05-12T15:00Z PoC); Race @ 86 (single byte, 9-category 0-8 + 9 = Not stated); Marital status @ 87; Education @ 88-90
  - Pregnancy History (bytes 91-106): Born alive now living 91-92; Born alive now dead 93-94; Born dead 95-96; Other terminations 97-100; Total birth order 101-103; Live birth order 104-106
  - Father (bytes 107-114): Age 107-110; Race 111; Education 112-114
  - Gestation: Combined 76-80; Physician's estimate 115-116; Computed 117-118
  - Other Items: Congenital malformations 119; Residence reporting flags 123-140; Occurrence reporting flag 141
  - Max byte-range upper bound: 200 (matches STATUS 2026-05-12T03:50Z `unzip` empirical record-length)
- [x] **Page-7 control counts** (this PRE-FLIGHT, validation-target source): per-year "20 weeks or more → 2. By residence":
  - 1982: **32,694** (with OCR-disambiguation: page 7 reads "32,694" cleanly)
  - 1983: **30,752**
  - 1984: **30,099**
  - 1985: **29,661** (page 7 reads "29,66I"; uppercase-I → digit-1; cross-checked: between 1984's 30,099 and 1986's 28,972, monotonic decline consistent)
  - 1986: **28,972**
  - 1987: **29,349** (page 7 reads "290349"; period→comma OCR; cross-checked against by-occurrence 59,358 - foreign 22 = 59,336 by-residence ≈ all records, vs 20+wk by-residence 29,349 ≈ 49% which matches 1986's 49% and 1988's 49.2%)
  - 1988: **29,442**
- [x] **L9 cheap-check on page-4/5/6 overview text quality**: all 7 user guides have legible OCR-baked text layer for the field-list overview (chars 474K-512K per PDF; all pages non-empty). Cosmetic OCR glitches present (`lg2-lg3` for `192-193`, `Oetail` for `Detail`, `I 5` for `15`, periods-vs-commas) but do NOT prevent byte-position extraction.
- [x] **L13-extension discipline** acknowledgment: byte positions from the page-5/6 overview are TRUSTED at this PRE-FLIGHT moment; per-field SUB-FIELD positions (e.g., Mother AGE specifically @ 81-82 vs MAGER8 @ 83-84 vs other granular fields within bytes 81-85; Race specifics within byte 86) require detail-record layout extraction from user-guide pages 7-30+ at DO time. Value-distribution sanity check on each parsed yearly_clean parquet is a mandatory DO Tier-2 deliverable (per STATUS 2026-05-12T15:00Z FL-HALT 4 + LESSONS 2026-05-12T01:40:00Z L13-extension).

### Outputs

- [x] Intended output paths to be **created** by V3b DO (none exist now):
  - `output/yearly_clean/fetal_death_1982_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1983_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1984_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1985_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1986_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1987_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1988_raw.parquet` (new)
  - `fetal_death/record_layout_1982_1988.csv` (new — single shared CSV per Q23 resolution)
  - `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` (new — L13-extension verification trail + B3 9-category race-bridged recode rationale + decision log for any V3b semantic ambiguities encountered)
- [x] Intended output paths to be **overwritten** (explicit overwrite mark; these are the V3a parquets that V3b extends backward):
  - `output/harmonized/fetal_death_harmonized.parquet` (V3a sha=`23c56a9d…` → new V3b/v2.3.0 sha TBD)
  - `output/harmonized/fetal_death_derived.parquet` (V3a sha=`0dd3aec0…` → new V3b/v2.3.0 sha TBD)
- [x] **No `.V1_baseline.parquet` overwrite** — V1-era snapshots preserved for byte-clean comparison (V3a preserved them; V3b preserves them too).
- [x] New metadata rows (additive, not overwrite):
  - `external_validation_targets.csv`: +7 rows (1982-1988 `fetal_deaths_gte20wk_resident` with the 7 page-7 control counts above; source "<YYYY> NCHS Fetal Death User Guide control count")
  - `file_inventory.csv`: +14 rows (7 zips + 7 user guides; `record_length=200, doc_filename=<YYYY>FetalUserGuide.pdf, notes="1978-revision uniform; V3b backward extension"`)

### Field-value snapshot for cells / rows / columns being mutated

| Artifact | Current state | Target state (post-V3b) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `fetal_death/scripts/01_import/field_specs.py` line 1167 `raise ValueError(f"Year {year} not configured. Currently supported: 1989-2022.")` | error msg "1989-2022" | **"1982-2022"** + new `if 1982 <= year <= 1988: return RECORD_LEN_1978, FETAL_1982_1988_FIELDS` branch above line 1149 | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` add `RECORD_LEN_1978 = 200` (new constant near line 28) | not present | **new constant added** | DO step 3 |
| `fetal_death/scripts/01_import/field_specs.py` add `FETAL_1982_1988_FIELDS: list[tuple[str, int, int]]` (new field list, structurally analogous to `FETAL_1992_2002_FIELDS` but with 1978-rev field names + positions for the 200-byte layout) | not present | **new list added** (reconstructed from user-guide detail-record pages 7-30 at DO time per L13-extension discipline) | DO step 3 (largest single DO mutation by line-count) |
| `fetal_death/scripts/01_import/field_specs.py` line 8 docstring (era listing) | starts at "1989-2002: V2.0 + V3a" | **prepend "1982-1988: V3b — 1978-revision uniform layout (200 data bytes)"** | DO step 3 |
| `fetal_death/scripts/03_harmonize/harmonize.py` `_build_field_map()` line 58-63 era list | 4 eras (`field_1992`/`2006`/`2014`/`2022`) | **5 eras** (+`field_1985`/`1985` entry for V3b) | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` `_era_tag()` line 94 | `if 1989 <= year <= 2002: return "1992"` | **+`if 1982 <= year <= 1988: return "1985"` branch above this** | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` line 96 error msg "1989-2022" | error msg current | **"1982-2022"** | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` B3 maternal_race_bridged recode (line 283-298) | V3a-extended map with `01`-`07`,`08`,`09`,`18`-`78`,`99`,`""` entries | **extend with 1978-rev 1-digit codes**: `0`→`4` (Other API), `1`→`1` (White), `2`→`2` (Black), `3`→`3` (AIAN), `4`→`4` (Chinese), `5`→`4` (Japanese), `6`→`4` (Hawaiian), `7`→`""` (Other nonwhite residual → null, V3a `09` precedent), `8`→`4` (Filipino), `9`→`""` (Not stated). NB: there is potential **collision** with V3a's `"01"`-`"09"` string-keyed map (V3b's 1-digit `"0"`-`"9"` are different keys); resolution = the V3b yearly-clean parser produces 1-digit strings; the `_checked_remap` will see distinct keys `"0".."9"` vs `"00".."09"`. Verify at DO time with explicit smoke-test mutation. | DO step 4 (with DECISION_LOG entry for any semantic ambiguity, e.g., code `7` Other nonwhite → null) |
| `fetal_death/variable_crosswalk_working.csv` 74 rows × 13 cols | columns: `candidate_harmonized_name,harmonized_label,domain,field_1992,pos_1992,field_2006,pos_2006,field_2014,pos_2014,field_2022,pos_2022,comparability_status,notes` | **+2 new columns** `field_1985,pos_1985` between domain and field_1992 (or as the leftmost era-pair column; column order is a DO step 5 micro-decision). Populate for V3b-applicable harmonized columns; "N/A" for V1-era-only columns (e.g., MAGER14/MAGER9/MRACE31/MRACE6/COMBGEST_USED/etc. — these don't exist in 1978-rev layout). | DO step 5 |
| `fetal_death/harmonized_schema.csv` 73 data rows × 10 cols | many `years_available` cells start at "1992-2002" or "1989-2002" (V3a-extended) | **extend backward** to "1982-2002" or "1982-2022 (excl 2003-2004)" or similar for V3b-covered fields. Pattern: any row whose current `years_available` starts at "1992" or "1989" gets prepended "1982-" if the V3b layout covers the field. Row-by-row enumeration deferred to DO step 6 (estimated ~25-30 rows touched of 73). | partial — enumeration at DO |
| `fetal_death/harmonized_schema.csv` `raw_source_by_year` column | many cells start with "1992:RAWNAME(pos)" | **prepend "1985:RAWNAME_V3B(pos);"** for V3b-covered fields. The 1985 era_tag mirrors the V2 `1992` convention. | DO step 6 |
| `fetal_death/external_validation_targets.csv` | last entries 1991 (V3a, fetal_deaths_gte20wk_resident = 30469/31386/30160) | **+7 rows** for 1982-1988 with values 32694 / 30752 / 30099 / 29661 / 28972 / 29349 / 29442; source "<YYYY> NCHS Fetal Death User Guide control count" (page-7 "20 weeks or more by residence") | ✓ values confirmed from user-guide page-7 extraction this PRE-FLIGHT |
| `fetal_death/file_inventory.csv` | last entries 1991 (V3a) | **+14 rows** for 1982-1988 raw zips + user guides; `record_length=200`, `notes="1978-revision uniform; V3b backward extension"` | ✓ all 14 SHAs + sizes recorded this PRE-FLIGHT |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 110-114 `GUIDE_FETAL_DEATHS_GTE20` dict | 6 entries (1989-1994) | **+7 V3b entries** (1982-1988) | DO step 9 |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 133 `if 1989 <= year <= 2002:` (version_flag filter) | year-range 1989-2002 | **1982-2002** | DO step 9 |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 143 `for year in (1989, 1990, 1991, 1992, 1993, 1994):` | 6-year tuple | **`for year in tuple(range(1982, 1995)):`** (13 years total: 1982-1994) | DO step 9 |
| `fetal_death/.zenodo.json` version | "v2.2.0" (post-V3a) | **"v2.3.0"** (additive backward extension) | DO step 10 |
| `fetal_death/CITATION.cff` version | "2.2.0" | **"2.3.0"** | DO step 10 |
| `fetal_death/ABOUT_THIS_RELEASE.md` | V2.1 + V3a sections present | **+V3b section** documenting 1982-1988 extension (1978-rev layout, page-5 cheap-check + L13-extension discipline) | DO step 10 |
| `fetal_death/README.md` Years coverage | "1989-2022" (post-V3a) | **"1982-2022"** | DO step 10 |
| `fetal_death/record_layout_1982_1988.csv` (new) | not exist | **created at DO step 2** (single shared CSV per Q23; reconstructed from 1985 user-guide detail-record pages, cross-checked against 1982/1988 for byte-position consistency) | DO step 2 |
| `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` (new) | not exist | **created at DO step 10** (L13-extension verification trail per-field + B3 1-digit MRACE rationale + any cross-year semantic ambiguities surfaced) | DO step 10 |
| `STATUS.md` | last 2026-05-12T15:00Z V3b PoC section | **+new dated section documenting V3b task close** at session end | post-DO step 12 |
| `PROVENANCE.md` | v2.0.0 Zenodo state (DELIBERATELY STALE per V3a STATUS FL-HALT 3) | **REMAIN STALE through V3b** — refresh is a Task 10 PRE-FLIGHT mutation (the unified Zenodo deposit) | not touched by V3b |

**No mutable annotation values pinned at this PRE-FLIGHT moment** (per Convention 1 SHAPE-not-VALUE) — all numeric values listed are:
- Source-document derived (the 7 page-7 control counts from each user guide — authoritative values that won't drift)
- SHA-256 baselines from immutable artifacts (raw zips, user guides — content-locked)
- Schema-level edits (extending era boundary + adding era_tag, not pinning a record count that V2.x/V3.x evolves)

### Halt conditions tripped

(none — all checks pass)

The following potential halt risks were considered and resolved:

1. **§7 condition 1 (PRE-FLIGHT check fails)** — every input present + verified. PASS.
2. **§7 condition 11 (Source PDF SHA changed upstream)** — N/A; 7 PDFs newly downloaded this PRE-FLIGHT and matched HEAD content-length byte-exact; uniform 2009-01-08 last-modified across all 7 (NCHS's 2009 rescan batch). 1985 + 1988 SHAs match PoC baselines from 2026-05-12T15:00Z byte-exact. Future SHA-drift verification deferred to forward-looking HALT.
3. **§7 condition 12 (Conflicting documentation)** — page-4/5/6 cross-year diff (this PRE-FLIGHT) confirms uniform 1978-revision layout across all 7 V3b years. PASS.
4. **§7 condition 13 (Validity-domain ambiguity)** — analytic filter `tabulation_flag==2 AND residence_status!=4` translates byte-exact: V3b has both fields at known positions (Tabulation inclusion @ 10; Resident status @ 12 per page-5 overview). PASS.
5. **§7 condition 17 (Scope creep)** — V3b is a strict superset task: extends 1989-2022 backward by 7 years; no V1/V2/V3a-era edit surface (those are byte-clean-preserved by L5 + new V3b code paths don't touch existing eras). Specific edit surface enumerated row-by-row in Field-value snapshot above.
6. **§8 row L13** (Inventory CSV records file roles before column-content verification) — covered by single shared `record_layout_1982_1988.csv` strategy AND mandatory per-field value-distribution verification at DO Tier-2 (per L13-extension 2026-05-12T01:40:00Z).
7. **§8 row L17** (SMOKE / test asset hard-codes mutable annotation value) — N/A; no new SMOKE harness authored at PRE-FLIGHT. Existing `validate_external.py` and `validate_external_v2.py` (which V3b extends) follow the canonical SHAPE-not-VALUE pattern; the V3b loop addition is structurally analogous to V3a's.
8. **Convention 2 DESIGN tag** — N/A; no new SMOKE harness authored.
9. **Anti-pattern #8 (compress two tasks into one)** — V3a + V3b are distinct PRE-FLIGHT + DO + RECEIPT units. V3a complete at `06f1bf4`; V3b is its own five-phase task.

### Result

**PROCEED — but with explicit human authorization gate before DO step 1.**

PRE-FLIGHT complete; no §7 halt conditions tripped. All inputs verified; staging decisions logged; field-value snapshot recorded; 12-step DO plan documented below. Per the kickoff (a)-(d) handshake's "explicit authorization before any DO mutation" gate (1978-rev layout reconstruction + B3 1-digit race recode + new parser dispatch are all genuinely new edit surfaces with their own audit risks), the DO phase requires explicit user yes before commit. This PRE-FLIGHT entry + the STATUS section that ships with it are the only mutations this session unless authorization arrives.

### Proposed DO plan (12 steps)

1. **`mv` 7 V3b raw zips** from `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1982..1988}US.zip` into `raw_data/fetal_death/` subdir (monorepo symlink). Verify post-`mv` SHAs unchanged (above baseline values). Then tag `task7_v3b-pre-do` on monorepo at the commit landing this PRE-FLIGHT entry.

2. **Construct `fetal_death/record_layout_1982_1988.csv`** from 1985 user-guide detail-record layout (pages 7-30 estimated). Cross-check selected fields against 1982 + 1988 for byte-position consistency. L13-extension discipline: pick 5-8 anchor fields (DATAYEAR, TABFLAG-equivalent, RESTATUS-equivalent, AGE, MRACE-equivalent, MEDUC-equivalent, gestation, birthweight) and document expected sentinel codes for value-distribution check at step 7.

3. **Edit `fetal_death/scripts/01_import/field_specs.py`**: add `RECORD_LEN_1978 = 200` constant; add `FETAL_1982_1988_FIELDS: list[tuple[str, int, int]]` field list (reconstructed from step 2 layout CSV); extend `layout_for_year()` with `if 1982 <= year <= 1988: return RECORD_LEN_1978, FETAL_1982_1988_FIELDS`; extend error message year-range; prepend docstring era line for V3b.

4. **Edit `fetal_death/scripts/03_harmonize/harmonize.py`**: extend `_build_field_map()` with `("field_1985", "1985")` entry in the era list; extend `_era_tag()` with `if 1982 <= year <= 1988: return "1985"` branch; extend error message year-range; extend B3 maternal_race_bridged recode with 1-digit V3b codes (`0`-`9` mapping). Document any V3b semantic-ambiguity decisions in DECISION_LOG (anticipated: B3 code `7` Other nonwhite residual → null mapping rationale, parallel to V3a `09` decision).

5. **Edit `fetal_death/variable_crosswalk_working.csv`**: add 2 new columns `field_1985,pos_1985`. Populate for V3b-applicable harmonized columns (estimated ~20-25 of 73 columns; the rest are V1-era-only and remain "N/A" for V3b).

6. **Edit `fetal_death/harmonized_schema.csv`**: extend `years_available` strings + `raw_source_by_year` cells for V3b-covered rows (~25-30 rows of 73; the rest are V1-era-only).

7. **Parse 7 V3b raw zips** via `python3 fetal_death/scripts/01_import/parse_fetal_year.py --year {Y} --zip raw_data/fetal_death/Fetal{Y}US.zip --out output/yearly_clean/fetal_death_{Y}_raw.parquet` for Y ∈ {1982..1988}. Verify per-year record counts match user-guide page-7 "Record count" (1982: 62,352; 1983: 60,584; 1984: 59,863; 1985: 59,690; 1986: 59,343; 1987: 59,358; 1988: 59,935). Tier-2 SMOKE gate: per-year record count match.

8. **L13-extension Tier-2 value-distribution sanity check** on each parsed yearly_clean parquet for the 5 H8-class demographic/filter columns:
   - `TABFLAG`-equivalent (byte 10): distribution {1, 2}; total record count split should ~50/50 (per page-7 "all records" vs "20+ weeks")
   - `RESTATUS`-equivalent (byte 12): distribution {1, 2, 3, 4}; code 4 (foreign) counts should match page-7 "To foreign residents" (low-double-digit each year)
   - `AGE`-equivalent (bytes 81-82 per PoC, or 81-85 umbrella): plausible 10-50 + sentinel 99; mean ~25-28
   - `RACE`-equivalent (byte 86): 1-digit code distribution {0-9} dominated by 1 (White) + 2 (Black); codes 4-8 (API granular) low-frequency
   - `MRACE3`-equivalent or similar: cross-check against RACE distribution
   Any out-of-range or wildly different distribution from V3a 1989-rev → halt; suggests byte-position shift or field-semantics shift between 1988 and 1989 not previously documented.

9. **Run full harmonize across 41 years (1982-2022)**: `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 1982 1983 ... 2022 --out output/harmonized/fetal_death_harmonized.parquet`. Validate row count ≈ V3a baseline 1,930,886 + 1982-1988 sum ~419K = ~2.35M.

10. **Re-run derive**: `python3 fetal_death/scripts/04_derive/derive.py`. Produces v2.3.0 `fetal_death_derived.parquet`.

11. **Edit `validate_external_v2.py`**: extend `GUIDE_FETAL_DEATHS_GTE20` with 7 V3b entries; extend year-range loop to 1982-1994 (13 years); run. Gate **33/33 PASS** byte-exact (was 26/26 V3a; +7 new V3b rows).

12. **Run `validate_external.py`**: V1 era 55/55 PASS unchanged (byte-clean regression check; V3b additive backward extension MUST NOT touch V1-era values). Append `file_inventory.csv` + `external_validation_targets.csv` rows; bump version strings (.zenodo.json → 2.3.0; CITATION.cff → 2.3.0; README.md Years 1982-2022); write `V3b_1982_1988_LAYOUT_DECISIONS.md`; update `ABOUT_THIS_RELEASE.md` with V3b section. Write RECEIPT to `RECEIPTS/task7_v3b_<UTC>.md`; tag `task7_v3b-complete`.

### Forward-looking HALTs for the DO phase

1. **Per-year record count gate (Tier-2)** — parsed yearly_clean parquets must have row counts matching user-guide page-7 exactly (62,352 / 60,584 / 59,863 / 59,690 / 59,343 / 59,358 / 59,935). Any divergence → halt; suggests record-length mismatch or zip-internal corruption.
2. **DATAYEAR plausibility gate (Tier-1)** — every record in `fetal_death_{Y}_raw.parquet` must have `data_year == Y` (read from bytes 1-2). Any null/wrong-year → halt; suggests field_specs offset bug.
3. **V3a-era byte-clean gate (Tier-3)** — for each derived column, the 1989-2022 slice's column-vector SHA-256 must equal the V3a baseline's same slice. Any drift → halt; suggests harmonize.py 1978-rev branch incorrectly conditioning on year ≥ 1989 affected V3a/V2/V1 output.
4. **V1-era + V2.1 byte-clean gate (Tier-3)** — same for 2003-2022. Same halt rule.
5. **Tier-2 NVSR validation** — 33/33 PASS byte-exact (was 26/26 V3a; +7 V3b). The 7 new rows (1982-1988) must each return byte-exact against their user-guide-derived target. Any FAIL → halt; suggests TABFLAG / RESTATUS byte-position mismatch OR a 1978-rev sentinel code not in B3 race-recode coverage.
6. **L13-extension value-distribution check** — for each of the 5 H8 demographic/filter columns post-V3b:
   - `data_year`: byte exact {1982, 1983, ..., 1988} per file
   - `tabulation_flag`: {1, 2}
   - `residence_status`: {1, 2, 3, 4}
   - `maternal_race_bridged`: {1, 2, 3, 4} (with nulls for V3b 1-digit codes `7` Other nonwhite + `9` Not stated per B3 1978-rev extension)
   - `maternal_age`: 10-50 + sentinel 99 (need to verify against user-guide page 7 imputation note)
   If any column shows out-of-range or wildly different distribution from 1989+ → halt; suggests field_specs byte-offset shift between 1981 and 1982 not previously documented, OR an OCR-misread byte position propagated through page-5 cheap-check.
7. **B3 1-digit MRACE map completeness** — `_checked_remap` will halt loud if V3b yearly_clean produces a code outside {0..9}; this is the defensive halt working as designed. Any halt at DO step 9 with "unseen code <X>" → expand B3 map with a documented DECISION_LOG entry parallel to 2026-05-12T14:30Z V3a `09→null` decision.
8. **Detail-record layout extraction surfacing OCR-baked semantic ambiguities** — for any field where the 1985 user-guide text-layer is OCR-garbled to the point of preventing reliable byte-position extraction (e.g., the page-5 overview's "9­" for "9." in 1982 page-5 between FIPS State 187-188 and FIPS County 189-191), halt-and-ask. Do NOT silently guess.

### Forward-looking HALTs for next session (Convention 4 — if DO does not start this session)

1. **`task7_v3a-complete` tag** + 5 V3a output parquet SHAs unchanged (HALT 1+2 from STATUS 2026-05-12T14:30Z): re-verify at next session start (`git tag --list 'task7_v3a*'`; `shasum -a 256 output/harmonized/fetal_death_{harmonized,derived}.parquet output/yearly_clean/fetal_death_198{9,1990,1991}_raw.parquet`).
2. **7 V3b user guides + 7 V3b raw zips** at `raw_docs/fetal_death/` + `~/Desktop/fetal-death-harmonization-build/raw_data/` with SHAs matching this PRE-FLIGHT baselines. If any drift, re-download / halt.
3. **PyMuPDF text-layer extraction** on 7 user guides remains intact (no file corruption between sessions). Re-verify with a 5-line `len(page.get_text())>0` check at session start.
4. **Working tree clean** at the post-PRE-FLIGHT commit; no stale checkpoints.
5. **No `task7_v3b_*` tags yet** — DO doesn't begin until user authorization gate (this PRE-FLIGHT's HALT-Result).

### Notes

- Effort estimate per STATUS 2026-05-12T15:00Z: **3-4 sessions for V3b** (down from initial 4-5 session estimate which assumed OCR-via-Tesseract was the long pole — STATUS 15:00Z PoC superseded that; text-layer extraction is sufficient). The irreducible cost is per-field L13-extension value-distribution verification, not OCR.
- The 12-step DO plan above is one-session-aggressive if no semantic ambiguities arise; more likely it splits across 2-3 sessions: session A = steps 1-3 (zip-stage + layout-CSV + field_specs edit); session B = steps 4-8 (harmonize + parse + L13-extension); session C = steps 9-12 (validate + RECEIPT + version-string ripple).
- The B3 1-digit race recode (V3b) coexists with the B3 V3a 2-digit recode in the same `_checked_remap` call; the two key-sets (`"0".."9"` vs `"00".."09" + "18".."78" + "99"`) are byte-disjoint so no collision. Will verify at DO step 4 with explicit smoke-test.
- Q22 + Q23 both resolved this PRE-FLIGHT.

---

## PRE-FLIGHT for task7_v3a — 2026-05-12T14:05:00Z

### Scope summary

Extend fetal-death coverage backward by 3 years from current 1992-2022 (V2.1 state, 31 years) to 1989-2022 (34 years), by parsing 1989-1991 raw zips through the existing 1989-revision parser dispatch (`FETAL_1992_2002_FIELDS` in `fetal_death/scripts/01_import/field_specs.py`) and re-running harmonize + derive against the same B1-B6 normalizations. The 1989-1991 layout is empirically identical to 1992 (same 360-byte record, same first-7-byte DATAYEAR/TABFLAG/RECTYPE/RESTATUS positions, same Data Elements list on user-guide page 5-6). New version: v2.2.0 (additive backward extension; no schema mutation). V3b (1982-1988, 1978-revision, 200-byte records, bitmap-scanned PDFs) is **OUT OF SCOPE** for this task — separate decision pending an OCR feasibility PoC per the Q19 choice this session (V3a now; V3b is its own task once OCR feasibility verified). Per KICKOFF.md "Current planned sequence" step 2; user authorized via Q19/Q20 reply this session (Q19 deferred to LLM judgment, Q20 = KICKOFF as-is).

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build-tree location**: canonical mutation target is the **monorepo** (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/`), per the Task 3 V2.1 precedent — `harmonize.py` lines 23-31 resolve `_PROJECT = fetal_death/`, `_PROJECT.parent = monorepo root`, and `_YEARLY_DIR = monorepo_root / output / yearly_clean` (a symlink to `~/Desktop/fetal-death-harmonization-build/output/yearly_clean/`). Raw inputs flow through `raw_data/fetal_death/` (symlink to `~/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/`). NOT the standalone `~/Desktop/fetal-death-harmonization/` repo (which is the legacy pre-monorepo v2.0.1 state with uncommitted May 7 edits) and NOT the build-dir's local `scripts/` (which has STALE May-4 v2.0.0-era harmonize.py without V2.1 era logic). The monorepo is canonical; build-dir is data backing-store only.

2. **Input rearrangement (executed at this PRE-FLIGHT)**: 2026-05-12T03:50Z agent downloaded the V3a zips to `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1989,1990,1991}US.zip` (top-level `raw_data/`), but the monorepo's symlink resolves to the sibling `raw_data/fetal_death/` subdir. RESOLUTION at PRE-FLIGHT: `mv` the 3 V3a zips into the `fetal_death/` subdir; V3b zips (Fetal{1982..1988}US.zip) left at top-level since V3b is out-of-scope. Verified post-`mv`: monorepo's `raw_data/fetal_death/Fetal{1989,1990,1991}US.zip` visible via symlink. SHAs preserved (pure file-system move).

3. **1989-1991 user guides downloaded (executed at this PRE-FLIGHT)**: not previously on disk. `curl -s -k` from canonical NCHS FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (same convention as 1992-2022 user guides already on disk, validated against STATUS 2026-05-12T04:30Z HEAD-probe baselines). All 3 downloaded to `~/Desktop/fetal-death-harmonization-build/raw_docs/fetal_death/` (visible to monorepo via symlink). Content-length matches HEAD probe exactly for all 3.

4. **NVSR control source identified for 1989-1991**: per-year user-guide control count from **Machine/File/Data Characteristics → 20 WEEKS AND OVER → By residence** (page 7 of each user guide, same convention as the existing 1992 row in `external_validation_targets.csv` which cites "1992 NCHS Fetal Death User Guide control count"). PyMuPDF text extraction confirmed legible text layer (NCHS's 2009 rescan batch includes an embedded OCR layer; PyMuPDF returns clean strings for the control-count block). NO additional OCR pipeline needed. NVSR 57-08 Table B (which covers 1995+) is not the source for 1989-1991 — user-guide control counts are authoritative for pre-1995.

### Inputs

- [x] All required input files exist (verified by direct check at this PRE-FLIGHT timestamp)
  - **Raw V3a zips** (now at `raw_data/fetal_death/` via symlink → `~/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/`):
    - `Fetal1989US.zip` sha256=`1d30d285a6558da697716879b05f3984c4f2bea15246b6deac7271ee9cb372bd` (16-char prefix matches STATUS 2026-05-12T03:50Z record `1d30d285a6558da6…`) ✓
    - `Fetal1990US.zip` sha256=`bcca5deb5de534d3d42e61abc4274bb39d68efd9f635548fcc0f4d546679987f` (matches `bcca5deb5de534d3…`) ✓
    - `Fetal1991US.zip` sha256=`aaa3e23250aac121c04c1068a645ff3a13deee94107917c2c30001936e701dd4` (matches `aaa3e23250aac121…`) ✓
  - **V3a user guides** (newly downloaded to `raw_docs/fetal_death/`):
    - `1989FetalUserGuide.pdf` 23,236,888 bytes (matches HEAD content-length) sha256=`54c55a40bffea18244bd14acc60a5fa094346e87c4557cb94633c7b52599e9d1` ✓
    - `1990FetalUserGuide.pdf` 22,897,888 bytes (matches) sha256=`91573bf8d93ee511405a6a38a96a97474dc55c80f0d421d9807bd9606e7a0578` ✓
    - `1991FetalUserGuide.pdf` 22,270,751 bytes (matches) sha256=`311fc21c98eab728f01796c4c903de44b177ac7549a00b61fcdaee425a12dd2d` ✓
  - **Existing canonical reference files** (1989-revision layout source, used as-is):
    - `fetal_death/record_layout_1992.csv` sha256=`45ca1273762db92f992b9255390846a43bc0e90f11b3fa32ebbe6f46f07a5a79` (the canonical 1989-revision layout CSV; valid for 1989-2002 per user guide cross-checks below) ✓
    - `fetal_death/scripts/01_import/field_specs.py` sha256=`35e788f3dd97eb156f572435be17a9097732958c3b1ef97491d3720fa61dbcf8` (current `FETAL_1992_2002_FIELDS` will be re-used; `RECORD_LEN_1992 = 360` matches 1989-1991 empirically) ✓
    - `fetal_death/scripts/03_harmonize/harmonize.py` sha256=`1b80fe73f2dbfc3e57f44f548fb2766df5c01c791482d4f4c32a99a99deae8c3` (`_era_tag()` line 86-96 needs 1-condition extension to cover 1989-1991 → era="1992"; cheapest DO edit) ✓
    - `fetal_death/harmonized_schema.csv` sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (`years_available` strings for V2-era columns need 3-year backward extension; documented in DO scope below) ✓
    - `fetal_death/external_validation_targets.csv` sha256=`0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f` (3 new rows for 1989-1991 control counts) ✓
    - `fetal_death/file_inventory.csv` sha256=`817124dbbce70b1181f580ea8517350e1a059770486448ad80c8d0eb8e2efab7` (3 new rows for 1989-1991 zips + user guides) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - `task3_v21_fetal_death` (V2.1, 2003+2004 transition): COMPLETE 2026-05-12 at monorepo `8ca5bf9` (`task3-complete` tag); V2.1 derived parquet at sha=`55d3d310cf5e1cbd8719325e3122505472d69dc4316af32f17c67d78c6c8c447` ✓
  - `natality_v28_rename`: COMPLETE 2026-05-12T13:35Z at monorepo `fc396fc` (`natality_v28_rename-complete` tag on both monorepo + build-dir); 4 v2.8 natality parquet SHAs verified stable at session start ✓
  - V1-era baseline parquets present (`fetal_death_harmonized.V1_baseline.parquet` sha=`cbcc91d24f2982d74bef0ba87a64495fb5cbd27928f720ee63d4006581bea2c0`; `fetal_death_derived.V1_baseline.parquet` sha=`2795f099380461581a59908b7653f536bb5f1cdbfd78f101097f0495c0232a8d`) — provide pre-V3a byte-clean comparison baseline for VERIFY phase ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `task7_v3a_*` tags in monorepo (verified: `git tag --list 'task7_*'` empty) ✓
  - No partial V3a edits in canonical work tree — monorepo tree CLEAN at `fc396fc` ✓
  - Tier-0 byte-length probe confirms zips parse: `unzip -p Fetal{1989,1990,1991}US.zip | head -1 | wc -c` = 361 (360 data + 1 newline) for all 3 years, matching `RECORD_LEN_1992 = 360` ✓
  - First-4-byte spot-check (DATAYEAR field): 1989 record begins `1989...`, 1990 begins `1990...`, 1991 begins `1991...` — DATAYEAR @ bytes 1-4 confirmed for 1989-revision layout ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] PyMuPDF (fitz) version 1.27.2.2: available for any further user-guide control-count extraction (no Tesseract install needed for V3a since text layer is embedded in NCHS's 2009-rescan-batch PDFs)
- [x] Working directory clean (`git status` in monorepo): CLEAN at `fc396fc` ✓
- [x] On expected branch: monorepo `main` ✓
- [x] Build-dir `~/Desktop/fetal-death-harmonization-build/` is **not a git repository** (verified). It is a data-backing-store directory only; canonical version control is the monorepo. Documented here so future sessions don't expect tags/log on the build-dir.

### Source documentation

- [x] `1989FetalUserGuide.pdf` page 7 (control block) text-extracts cleanly via PyMuPDF; control values:
  - Total record count = 61,295 (matches what the parsed parquet should produce per-year)
  - All fetal deaths By residence = 61,236 / To foreign residents = 59
  - **20 WEEKS AND OVER → By residence = 30,469** (the V3a validation target for 1989)
- [x] `1990FetalUserGuide.pdf` page 7: Record count = 64,349; **20 WEEKS AND OVER → By residence = 31,386** (validation target for 1990)
- [x] `1991FetalUserGuide.pdf` page 7: Record count = 63,265; **20 WEEKS AND OVER → By residence = 30,160** (validation target for 1991)
- [x] L9 cheap-check on layout reusability: page 5-6 Data Elements list in 1989/1990/1991 user guides matches the 1992 user guide field-by-field for the first 60 fields (Data year 1-4; Tabulation flag 5; Record type 6; Resident status 7; NCHS State 17-18; FIPS State 22-23; NCHS state of residence 33-34; Population size - city 41; ... ; Mother age 69-76 + 87-88; Mother race 79-81; Mother education 82-84; ...; Father age 105-107; ...; Method of delivery 220-226; Medical risk factors 228-244; Congenital anomalies 279-300; NCHS SMSA 357-359). No byte-position drift observed. NCHS terminology changed cosmetically from "SMSA" (1989) to "MSA" (1990+) at the same byte position 55-58 — semantically identical (Metropolitan Statistical Area; MSA designation re-numbering in mid-1990s is post-V3a era and irrelevant for raw read).
- [x] **L13-extension discipline** applied: byte-position match (above) AND first-record data values are plausible (DATAYEAR=year matches the file name; TABFLAG ∈ {1,2}; RECTYPE ∈ {1,2}; RESTATUS ∈ {1,2,3,4}). Value-distribution sanity check on harmonized parquet is a Tier-2 SMOKE deliverable (per row L13-extension catch: "compute the parsed value distribution and verify it matches the user guide's documented value range / sentinel codes").

### Outputs

- [x] Intended output paths to be **overwritten** (explicit overwrite mark; these are the V2.1 v2.1.0 parquets that V3a appends 3 more years to):
  - `output/harmonized/fetal_death_harmonized.parquet` (V2.1 sha=`333e1e66…d9e0` → new V3a/v2.2.0 sha TBD)
  - `output/harmonized/fetal_death_derived.parquet` (V2.1 sha=`55d3d310…c447` → new V3a/v2.2.0 sha TBD)
  - `output/yearly_clean/fetal_death_1989_raw.parquet` (new file)
  - `output/yearly_clean/fetal_death_1990_raw.parquet` (new file)
  - `output/yearly_clean/fetal_death_1991_raw.parquet` (new file)
- [x] **No `.V1_baseline.parquet` overwrite** — those are V1-era snapshots preserved for byte-clean comparison. They predate Task 3 V2.1 and are not touched by V3a.
- [x] New metadata rows (additive, not overwrite):
  - `external_validation_targets.csv`: +3 rows (1989, 1990, 1991 fetal_deaths_gte20wk_resident with values 30469, 31386, 30160; source "<YYYY> NCHS Fetal Death User Guide control count")
  - `file_inventory.csv`: +3 rows (Fetal1989US.zip, Fetal1990US.zip, Fetal1991US.zip with `record_length=360, doc_filename=<YYYY>FetalUserGuide.pdf, notes="1989-revision uniform; V3a backward extension"`)

### Field-value snapshot for cells / rows / columns being mutated

| Artifact | Current state | Target state (post-V3a) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `fetal_death/scripts/03_harmonize/harmonize.py` line 94 `if 1992 <= year <= 2002:` | year-range 1992-2002 → era="1992" | **1989-2002 → era="1992"** (1-condition extension) | ✓ direct read |
| `fetal_death/scripts/03_harmonize/harmonize.py` line 96 `raise ValueError(f"Year {year} outside supported range (1992-2022)")` | error msg says "1992-2022" | **"1989-2022"** | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` line 8 docstring `1992-2002: V2.0 — single uniform 1989-revision layout (360 data bytes)` | docstring says 1992-2002 | **1989-2002** | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` line 20 constant `RECORD_LEN_1992 = 360` | scoped to 1992 era tag | Keep constant unchanged; `layout_for_year` mapping extended to dispatch 1989-1991 → same `FETAL_1992_2002_FIELDS` + `RECORD_LEN_1992`. Alternatively rename constant to `RECORD_LEN_1989 = 360`. **Decision: keep name + extend mapping (lower edit surface, semantically identical)** | ✓ direct read |
| `fetal_death/harmonized_schema.csv` `years_available` column | strings like "1992-2002, 2003-2004, ..." for V2-era columns | **extend leading 1992 → 1989** where applicable (the harmonized columns sourced from FETAL_1992_2002_FIELDS get a 3-year backward extension; column rows whose years_available starts at 2005 (V1-only fields) are unchanged) | partial — full per-row enumeration deferred to DO step 2 |
| `fetal_death/external_validation_targets.csv` | last entries 2022; no 1989-1991 rows | **+3 rows** for 1989/1990/1991 `fetal_deaths_gte20wk_resident` = 30469 / 31386 / 30160; source "<YYYY> NCHS Fetal Death User Guide control count" | ✓ values confirmed from user-guide page 7 extraction |
| `fetal_death/file_inventory.csv` | first row year=1992; no 1989-1991 rows | **+3 rows** for 1989/1990/1991 raw zips + user guides; `record_length=360`, `notes="1989-revision uniform; V3a backward extension"` | ✓ raw zip + user-guide SHAs above |
| `fetal_death/.zenodo.json` version | "v2.1.0" (current) | **"v2.2.0"** (additive backward extension) | not yet read — DO step 8 |
| `fetal_death/CITATION.cff` version | "2.1.0" | **"2.2.0"** | not yet read — DO step 8 |
| `fetal_death/ABOUT_THIS_RELEASE.md` | V2.1 release notes | **+V3a section** documenting 1989-1991 extension | DO step 9 |
| `fetal_death/README.md` Years coverage | "1992-2022" | **"1989-2022"** | DO step 9 |
| New layout-decisions doc | (none) | **`fetal_death/V3a_1989_1991_LAYOUT_DECISIONS.md`** (new file documenting 1989-revision reusability + the L13-extension verification path) | DO step 9 |

**No mutable annotation values pinned at this PRE-FLIGHT moment** (per Convention 1 SHAPE-not-VALUE) — all numeric values listed above are either:
- Source-document derived (the 3 control counts from user-guide page 7 — authoritative values that won't drift)
- SHA-256 baselines from immutable artifacts (raw zips, user guides — content-locked)
- Schema-level edits (extending era boundary, not pinning a record count that V2.x evolves)

### Halt conditions tripped

(none — all checks pass)

The following potential halt risks were considered and resolved:

1. **§7 condition 1 (PRE-FLIGHT check fails)** — every input present + verified. PASS.
2. **§7 condition 11 (Source PDF SHA changed upstream)** — N/A; PDFs newly downloaded this session. Future verification of NCHS-side SHA stability deferred to forward-looking HALT.
3. **§7 condition 12 (Conflicting documentation)** — L9 cheap-check confirms 1989-1991 page 5-6 Data Elements lists match the 1992 user guide field-by-field. PASS.
4. **§7 condition 17 (Scope creep)** — V3b (1982-1988) explicitly excluded; V3a's `_era_tag` extension and `_layout_for_year` mapping update touch ONLY the 1989-1991 path. Build dir's V3b zips (Fetal1982-1988US.zip) remain at the build-dir top-level `raw_data/` — NOT visible through the monorepo symlink — and are out of any V3a code path.
5. **L13-extension (byte-position vs field-semantics)** — verified at multiple anchor fields. Full value-distribution check is a Tier-2 SMOKE deliverable.
6. **Anti-pattern #8 (compress two tasks into one)** — V3a is a strict subset task. V3b will get its own PRE-FLIGHT + DO + RECEIPT if/when authorized.

### Result

**PROCEED.** PRE-FLIGHT complete; no §7 halt conditions tripped. DO phase authorized to begin per the 10-step plan documented below. Estimated DO budget: 30-60 minutes wall-clock for re-derive + validation; total task budget ~1 session per STATUS 2026-05-12T03:50Z estimate.

### Proposed DO plan (10 steps)

1. **Tag `task7_v3a-pre-do`** on monorepo at the post-PRE-FLIGHT commit (the commit that lands this PRE_FLIGHT_LOG entry).
2. **Edit `fetal_death/scripts/03_harmonize/harmonize.py`**: `_era_tag()` line 94 → `if 1989 <= year <= 2002:`; line 96 error msg → `"1989-2022"`.
3. **Edit `fetal_death/scripts/01_import/field_specs.py`**: extend `layout_for_year(year)` to map 1989-1991 → `(RECORD_LEN_1992, FETAL_1992_2002_FIELDS)`. Update docstring lines 8-9 to read "1989-2002: V2.0 — single uniform 1989-revision layout (360 data bytes)". Update line 30 section comment "1992-2002" → "1989-2002".
4. **Parse 1989, 1990, 1991 raw zips** via `python3 fetal_death/scripts/01_import/parse_fetal_year.py --year {Y} --zip raw_data/fetal_death/Fetal{Y}US.zip --out output/yearly_clean/fetal_death_{Y}_raw.parquet`. Verify per-year record count matches user-guide page 7 (61,295 / 64,349 / 63,265).
5. **Re-run full harmonize**: `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 1989 1990 1991 1992 1993 ... 2022 --out output/harmonized/fetal_death_harmonized.parquet`. Validate row count = sum of per-year record counts (V2.1 baseline 1,634,195 + 1989-1991 ~189k = ~1.82M).
6. **Re-run derive**: `python3 fetal_death/scripts/04_derive/derive.py` (or equivalent). Produces v2.2.0 `fetal_death_derived.parquet`.
7. **Append 3 rows to `external_validation_targets.csv`** (1989/1990/1991 fetal_deaths_gte20wk_resident = 30469 / 31386 / 30160).
8. **Run `validate_external_v2.py`**: gate 26/26 PASS (was 23/23; +3 new V3a rows). Halt on any FAIL.
9. **Run `validate_external.py`**: V1 era 55/55 PASS unchanged (byte-clean regression check — V3a additive backward extension MUST NOT touch V1-era values; SHA of post-V3a derived's 2005-2022 slice should equal pre-V3a V2.1 derived's 2005-2022 slice + rows-from-2003-2004 unchanged. Compare via PyArrow per-year groupby).
10. **Append `file_inventory.csv` rows + V3a-extension doc + version bumps** (`.zenodo.json`, `CITATION.cff` → 2.2.0; `README.md` Years 1989-2022; `ABOUT_THIS_RELEASE.md` V3a section; new `V3a_1989_1991_LAYOUT_DECISIONS.md`).

### Forward-looking HALTs for the DO phase

1. **Per-year record count gate (Tier-2)** — parsed yearly_clean parquets must have row counts matching user-guide page 7 exactly (61,295 / 64,349 / 63,265). Any divergence → halt; suggests record-length mismatch or zip-internal corruption.
2. **DATAYEAR plausibility gate (Tier-1)** — every record in `fetal_death_{Y}_raw.parquet` must have `data_year == Y` (read from bytes 1-4). Any null/wrong-year → halt; suggests field_specs offset bug.
3. **V1-era byte-clean gate (Tier-3)** — for each derived column, the 2005-2022 slice's column-vector SHA-256 must equal the V2.1 baseline's same slice. Any drift → halt; suggests harmonize.py logic incorrectly conditioning on year < 1992 affected V1-era output.
4. **V2.1 byte-clean gate (Tier-3)** — same for 2003-2004 slice. Same halt rule.
5. **Tier-2 NVSR validation** — 26/26 PASS byte-exact (was 23/23 V2.1; +3 V3a). The 3 new rows (1989/1990/1991) must each return byte-exact against their user-guide-derived target.
6. **L13-extension value-distribution check** — for each of the 5 H8 demographic/filter columns post-V3a:
   - `maternal_age` (Int16): 1989-1991 distribution within plausible range (10-50, with sentinel 99 allowed); mean ~25-28
   - `maternal_race_bridged` (Int8): {1,2,3,4} only
   - `hispanic_origin` (Int8): {0,1,2,3,4,5,6,7,8,9} with 0-5 dominant
   - `tabulation_flag` (Int8): {1,2}
   - `residence_status` (Int8): {1,2,3,4}
   If any column shows out-of-range or wildly different distribution from 1992-1994 → halt; suggests field_specs byte-offset shift between 1988 and 1989 not previously documented.

### Notes

- Convention 2 DESIGN tag is not applicable to this PRE-FLIGHT — no new SMOKE harness is being authored here (existing `validate_external.py` and `validate_external_v2.py` already implement the canonical SMOKE pattern for fetal-death; V3a re-uses them and extends their year set, not the harness logic).
- Convention 3 Field-value snapshot complete above.
- Convention 4 Forward-looking HALTs for next session emitted in the RECEIPT at task close.
- V3b PoC decision deferred to a separate session/task; KICKOFF as-is sequence per Q20.

---

## PRE-FLIGHT for natality_v28_rename — 2026-05-12T05:30:00Z

### Scope summary

Rename four natality harmonized columns from v2.7.0 names to canonical cross-product names: `year → data_year`, `restatus → residence_status`, `maternal_race_bridged4 → maternal_race_bridged`, `maternal_hispanic_origin → hispanic_origin`. Output: new natality v2.8.0 deposit (breaking change; v2.7.0 stays immutable at its DOI). Per KICKOFF.md "Current planned sequence" step 1 (data-first pre-submission scope per DECISION_LOG 2026-05-12T03:30:00Z). 14-step DO plan canonical in DECISION_LOG 2026-05-12T03:25:00Z. Mutation lives in standalone build dir `/Users/yoelplutchok/Desktop/natality-harmonization/` (HEAD `dcabd8c`); monorepo's `natality/` subdir is a mirror that re-syncs AFTER v2.8 ships.

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build-dir `M README.md` pre-existing diff** (per STATUS 2026-05-12T05:10Z Forward-looking HALT 1): one-line cosmetic removal of "(for a new researcher or LLM)" from a section header — pre-existing, not this task's. RESOLUTION: stash before v2.8 work so v2.8's first commit doesn't pick it up; user can decide whether to commit/discard separately.
2. **v2.7.0 parquets on disk** (per STATUS 2026-05-12T05:10Z Forward-looking HALT 3): the prior session reported `output/*.parquet` not present; in fact parquets DO exist at `output/harmonized/*.parquet` and `output/yearly_clean/*.parquet` (prior glob missed subdir layout). No re-derive needed for current state; v2.8 re-derive will overwrite `output/harmonized/`.
3. **Tag location**: build-dir `natality_v28_rename-pre-do` tags the build repo's pre-DO commit (where the actual mutations happen). Monorepo will also get tagged at the corresponding state-file commit per Task 3 convention.

### Inputs

- [x] All required input files exist (verified by direct read)
  - `/Users/yoelplutchok/Desktop/natality-harmonization/metadata/harmonized_schema.csv`: present, 95 rows (94 data + 1 header). 4 rename-target rows verified at row positions 1 (year), 2 (restatus), 3 (maternal_hispanic_origin), 4 (maternal_race_bridged4). ✓
  - `output/harmonized/natality_v2_harmonized_derived.parquet`: present, 138,819,655 rows × 84 cols, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` ✓ (matches Forward-looking HALT 1 from DECISION_LOG 2026-05-12T03:30Z exactly)
  - `output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, 74,943,824 rows × 94 cols, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (no prior baseline SHA recorded — record this one now for HALT verification at re-derive) ✓
  - 36 raw NCHS zips in `raw_data/` (1990-2024 + linked-cohort files) — present for full re-derive if needed ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - task3_v21_fetal_death: complete 2026-05-12 at `8ca5bf9` (`task3-complete` tag in monorepo) ✓
  - public-repo v1.0 push: complete 2026-05-12 at `a18ca3a` (https://github.com/yoelplutchok/vital-statistics-harmonization) ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `natality_v28_*` tags in build dir or monorepo ✓
  - No partial v2.8 edits — build dir's only working-tree diff is the pre-existing `M README.md` (resolved via stash at staging decision 1) ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] Build-dir working tree CLEAN post-stash (verified at DO step 0); monorepo working tree clean at session start (`ad5ff1f`) ✓
- [x] On expected branch: build dir `main` tracking `origin/main`; monorepo `main` ✓

### Source documentation

No external NCHS PDFs consumed by this task (v2.8 is a column rename, not a content change). The aliasing-helper `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` dict (lines 20-25 in the monorepo, 4 entries verified) is the documentation that this rename satisfies; after v2.8 the dict becomes empty + deprecation note.

### Outputs

- [x] Intended output paths exist as v2.7.0 artifacts — will be **overwritten** by v2.8 re-derive (this is the explicit overwrite mark):
  - `output/harmonized/natality_v2_harmonized_derived.parquet` (v2.7.0 SHA `9f917a43...` → new v2.8 SHA TBD)
  - `output/harmonized/natality_v3_linked_harmonized_derived.parquet` (v2.7.0 SHA `46c169b5...` → new v2.8 SHA TBD)
  - `output/harmonized/natality_v2_harmonized.parquet` (pre-derive intermediate)
  - `output/harmonized/natality_v3_linked_harmonized.parquet` (pre-derive intermediate)
- [x] Convenience subsets in `output/convenience/` will be regenerated downstream of harmonize step.
- [x] No NEW output paths introduced by this task — all are v2.7.0 paths overwritten in-place under the new schema.

### Field-value snapshot for cells / rows / columns being mutated

Cross-checked against DECISION_LOG 2026-05-12T03:25:00Z Field-value snapshot at this PRE-FLIGHT. State unchanged from that snapshot:

| Artifact | Current (v2.7.0) | Target (v2.8) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `metadata/harmonized_schema.csv` row 1 | `year,Birth year,int16,1990-2024,...` | `data_year,Birth year,int16,1990-2024,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 2 | `restatus,Resident status (NCHS),int8,1\|2\|3\|4,...` | `residence_status,Residence status,int8,1\|2\|3\|4,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 3 | `maternal_hispanic_origin,Mother's Hispanic origin recode,int8,...` | `hispanic_origin,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 4 | `maternal_race_bridged4,Mother's bridged race (4 categories),int8,...` | `maternal_race_bridged,...` | ✓ direct grep |
| natality v2 parquet | columns `year`, `restatus`, `maternal_hispanic_origin`, `maternal_race_bridged4` present | renamed to canonical | ✓ pyarrow schema read |
| linked v3 parquet | same 4 columns present | renamed to canonical | ✓ pyarrow schema read |
| `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` | 4 entries (year→data_year, restatus→residence_status, maternal_race_bridged4→maternal_race_bridged, maternal_hispanic_origin→hispanic_origin) | empty dict + deprecation note | ✓ direct grep (monorepo helper) |

**String-literal reference counts** (the edit surface, scoped to build-dir `scripts/` + `metadata/` + `docs/`; output/ excluded):

| Pattern | Count | DECISION_LOG predicted |
|---|---:|---:|
| `"year"` | 46 | 48 |
| `'year'` | 2 | (combined) |
| `"restatus"` | 3 | 3 |
| `'restatus'` | 0 | (combined) |
| `"maternal_race_bridged4"` | 6 | 6 |
| `'maternal_race_bridged4'` | 0 | (combined) |
| `"maternal_hispanic_origin"` | 4 | 4 |
| `'maternal_hispanic_origin'` | 0 | (combined) |
| **TOTAL** | **61** | **61** |

Match with DECISION_LOG 2026-05-12T03:25Z is exact (61=61). The "48" predicted for "year" split as 46+2 here (double-quote vs single-quote) — total identical. **No staleness drift.**

### Halt conditions tripped

(none — all checks pass)

### Result

**PROCEED.** PRE-FLIGHT complete; no §7 halt conditions tripped. DO phase authorized to begin per the 14-step plan in DECISION_LOG 2026-05-12T03:25:00Z. Forward-looking HALT 6 from STATUS 2026-05-12T03:30Z (string-literal rename must be scoped via `s|"year"|"data_year"|g` and `s|'year'|'data_year'|g`, NOT bare-word replacement) is binding for every DO sed/Edit operation. Re-derive budget ~5-10 minutes wall-clock; 183 NVSR validation + 33/35-linked validation are gates 7-8 of the DO plan.

---

## PRE-FLIGHT for task3_v21_fetal_death — 2026-05-11T21:30:00Z

### Scope summary

Add 2003 + 2004 fetal-death transition years to the harmonized resource (V2.1.0). Bundle the H8 schema-doc dtype-drift reconciliation (5 columns shipped `string` in v2.0.0 parquet but declared `int` in `harmonized_schema.csv`) into the same Task 3 parquet re-derivation. Per `KICKOFF.md` 2026-05-11 sequencing decision and STATUS 2026-05-11T20:50Z, this is sequence step 1 of 5; manuscript re-pass is step 5.

### Staging decisions (resolved at PRE-FLIGHT per Convention 3 second bullet)

§15 Task 3 spec + `fetal_death/scripts/run_pipeline.py` assume `RAW_DIR = REPO_ROOT / "raw_data/fetal_death"` (monorepo-local), but the actual raw zips + user-guide PDFs + the existing 29-year `output/yearly_clean/` parquets all live at `~/Desktop/fetal-death-harmonization-build/` (the v2.0.0 build environment). Three sub-decisions resolved before any DO mutation:

1. **Build location** — symlink raw inputs into monorepo. `raw_data/fetal_death` and `raw_docs/fetal_death` and `output/` (which contains `yearly_clean/`, `harmonized/`, `validation/`) are now symlinks to the sibling build dir. All symlink targets are `.gitignore`d (`**/raw_data/*`, `**/raw_docs/*` already present; `output/` newly added in this PRE-FLIGHT to keep the tree clean). The monorepo can now run `fetal_death/scripts/run_pipeline.py` without further plumbing.
2. **Yearly-parse reuse** — reuse existing `output/yearly_clean/fetal_death_{year}_raw.parquet` for the 29 already-shipped years; only parse 2003 + 2004 fresh. Saves ~5 min build time. Safe because the parser code is unchanged for 1992-2002 + 2005-2022 (DO-phase changes are 2003/2004-only in `field_specs.py` and the harmonize-step dtype fix for H8, which lands at the harmonize stage downstream of yearly_clean).
3. **Layout ambiguity policy** — halt-and-ask per ambiguity (§7 halt condition 12, conflicting documentation). Aligned with §2 principle "fail closed".

### Inputs
- [x] All required input files exist (verified via symlinks; sibling-build-dir-resolved paths)
  - `raw_data/fetal_death/Fetal2003US.zip`: present, sha256=`7311ffab3314bf8f7ebb1465b153cc569be88d3126edabab680b90c7a4844f99`, 2,755,093 B compressed; uncompressed `VS03FETL.DETUSPUB` is 73,679,944 B ✓
  - `raw_data/fetal_death/Fetal2004US.zip`: present, sha256=`42d68172ea1976cc5c371ecce36f5b33bb0efb6b6f139443bbec729674395c41`, 2,721,055 B compressed; uncompressed `VS04FETL.DETUSPUB` is 80,034,070 B ✓
  - `raw_docs/fetal_death/fetaldeath0304problems.pdf`: present, sha256=`b2214b09722a214932728b8a3dc38c83d85b97a3a728f9e78daa7b26739e1331`, 135,683 B, 6 pages ✓
  - `raw_docs/fetal_death/2003FetalUserGuide.pdf`: present, sha256=`281160b5339693412ce8275593584fc728e90fd29f4d23ac5273d9b3d5ad8146`, 2,931,130 B, 163 pages ✓
  - `raw_docs/fetal_death/2004FetalUserGuide.pdf`: present, sha256=`ca8be48e77891660059ad93110f606ad0eedded703f174da8c283e4914272709`, 2,584,516 B, 110 pages ✓
  - `output/harmonized/fetal_death_derived.parquet` (v2.0.0 shipped baseline for byte-clean regression check): sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` — MATCHES `fetal_death/PROVENANCE.md` ✓
  - `output/harmonized/fetal_death_derived.V1_baseline.parquet`: present (alternate V1-only regression baseline) ✓
  - `output/yearly_clean/fetal_death_{year}_raw.parquet` for year ∈ {1992-2002, 2005-2022}: 29 files present (verified by directory listing) ✓
  - `fetal_death/harmonized_schema.csv`: present, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` ✓
  - `fetal_death/file_inventory.csv`: present, 30 rows (no 2003 or 2004 row yet — DO will append) ✓
  - `fetal_death/external_validation_targets.csv`: present (DO will append 2003 + 2004 rows for NVSR 57-08 counts + rates) ✓
  - `fetal_death/scripts/01_import/{parse_fetal_year,field_specs,zip_text_stream}.py`: present ✓
  - `fetal_death/scripts/03_harmonize/harmonize.py`: present ✓
  - `fetal_death/scripts/04_derive/derive.py`: present ✓
  - `fetal_death/scripts/05_validate/{validate_2022,validate_external,validate_external_v2}.py`: present ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - task1 (2026-05-11): ✓
  - task2 (2026-05-11): ✓
  - task6 (2026-05-11): ✓
  - task4 (2026-05-11): ✓
  - task5 (2026-05-11, `9aaa702`): ✓
  - sequencing decision (2026-05-11, `5577c87`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task3_*.md`: does not exist ✓
  - `output/yearly_clean/fetal_death_2003_raw.parquet`: does not exist (good) ✓
  - `output/yearly_clean/fetal_death_2004_raw.parquet`: does not exist (good) ✓
  - `fetal_death/record_layout_2003.csv`, `record_layout_2004.csv`: do not exist (good — DO will create) ✓
  - No `task3-pre-do` git tag yet (good — will tag after this PRE-FLIGHT commit) ✓

### Environment
- [x] Python 3.13.9 (required ≥3.11) ✓
- [x] pandas 2.3.2 (required ≥2.3) ✓
- [x] pyarrow 18.1.0 (required ≥18.0) ✓
- [x] R version: N/A (Task 3 is Python-only)
- [x] Working directory clean before staging: `git status` showed clean before symlinks. After staging: only `.gitignore` modified (one-line `output/` addition). After this PRE-FLIGHT commit: clean again. ✓
- [x] On expected branch: `main` at `5577c87` ✓

### Source documentation — L9 cheap-check on 2003 + 2004 user guides

Per §15 Task 3 PRE-FLIGHT direction ("Apply L9 cheap-check: verify the named page/section in the user-guide PDF actually documents the field at the claimed byte position"):

- [x] **Apparent 1351-vs-3350 conflict resolved at PRE-FLIGHT.** Both user guides' page-2 SAS reproduction snippet declares `INFILE 'C:FETxxUS.DAT' LRECL=3350`. The §15 Task 3 spec says 1351-byte records for 2003 and 1501-byte records for 2004. Empirical verification: opened the actual `VS03FETL.DETUSPUB` and `VS04FETL.DETUSPUB` member inside each zip; first 5 records measured byte-exact at **1351 bytes (data 1350 + CRLF) for 2003** and **1501 bytes (data 1500 + CRLF) for 2004**. Total uncompressed sizes divide evenly: 73,679,944 / 1351 = 54,537 records (2003); 80,034,070 / 1501 = 53,320 records (2004). The user guide's `LRECL=3350` is a SAS-side maximum, not the literal data byte length — the public-use files contain the actual shorter records and SAS pads internally. The §15 record-length numbers are CORRECT; no plan amendment needed. ✓
- [x] **TABFLAG position-9 confirmed empirically.** First 12 chars of records 1-3 in both zips are exactly `b'      S12   '`; the user guide and `fetaldeath0304problems.pdf` both name TABFLAG at position 9. Char 9 = `2` (= 20+ weeks, the dominant value in the early-records sample). The known TABFLAG error documented in `fetaldeath0304problems.pdf` (records with COMBGEST=99 in a 42-state list misclassified as <20 weeks) is a derivable normalization that will land in `harmonize.py` during DO as a new "B-class" normalization. **Open: this is a NEW normalization not in `fetal_death/ABOUT_THIS_RELEASE.md`'s B1-B6 list — DO will document it as B7 in the receipt and DECISION_LOG.** Soft-flag, not a halt.
- [x] **A/S version-byte at position 7 confirmed empirically.** Sampled first 100,000 records of each zip; position 7 distribution: 2003 = {S: 53,503; A: 994}; 2004 = {S: 51,321; A: 1,964}. Both years dominated by S (the 2003-revision) — the A records (1.8% in 2003; 3.7% in 2004) are the persisting-1989-revision-state records. **The §15 plan's "per-state branch on the version-byte (A vs S)" terminology is consistent with empirical observation.** Whether the dispatch should genuinely branch on position 7 byte, or branch on state code mapped to a revision-adoption table, will be reconciled in DO from a fuller reading of the 2003 user guide's record-layout section. Soft-flag, not a halt.
- [x] All cited Zenodo DOIs resolve: not specifically queried (Task 3 does not consume Zenodo deposit contents directly; the existing parquets are local).

### Outputs
Intended outputs do not yet exist (or, where they exist, will be overwritten with version-bumped successors). All non-trivial new outputs will be written under `output/` (gitignored; the new v2.1.0 Zenodo deposit is the canonical home) or in `fetal_death/` (the monorepo-shipped state).

- [x] `fetal_death/record_layout_2003.csv` — does not exist (good) ✓
- [x] `fetal_death/record_layout_2004.csv` — does not exist (good) ✓
- [x] `output/yearly_clean/fetal_death_2003_raw.parquet` — does not exist (good) ✓
- [x] `output/yearly_clean/fetal_death_2004_raw.parquet` — does not exist (good) ✓
- [x] `output/harmonized/fetal_death_harmonized.parquet` — exists at v2.0.0 sha=`f09beb4a…0e5928` (will be overwritten with v2.1.0; v2.0.0 sha preserved in `fetal_death/PROVENANCE.md` and recoverable from the published Zenodo deposit 10.5281/zenodo.20031571)
- [x] `output/harmonized/fetal_death_derived.parquet` — exists at v2.0.0 sha=`90af89b9…f0afdd` (same disposition; canonical baseline for the V1-era byte-clean regression check)
- [x] `output/harmonized/fetal_death_derived.V1_baseline.parquet` — exists; auxiliary V1-only filtered baseline; will be re-derived
- [x] `fetal_death/scripts/01_import/field_specs.py` — exists; will be extended (add 2003/2004 layouts + per-state A/S dispatch)
- [x] `fetal_death/scripts/03_harmonize/harmonize.py` — exists; will be extended (handle 2003/2004 raw → harmonized + fix H8 int dtypes for 5 columns + add B7 TABFLAG correction for 0304)
- [x] `fetal_death/scripts/run_pipeline.py` — exists; will be extended (add 2003 + 2004 to `V_TRANSITION_YEARS` list)
- [x] `fetal_death/file_inventory.csv` — exists; will append 2 rows (2003, 2004) with SHAs and user-guide PDF names
- [x] `fetal_death/external_validation_targets.csv` — exists (26 metrics, 29-year coverage); will append 2003 + 2004 cells for per-year counts + rates from NVSR 57-08 (and corrected values per `fetaldeath0304problems.pdf` Table 1)
- [x] `fetal_death/validation_results.csv` — exists; will be re-generated by `validate_external_v2.py`
- [x] `fetal_death/harmonized_schema.csv` — exists; should NOT be edited in this task (per anti-pattern #6, schema edits require schema-version bump). The H8 fix makes the parquet match the schema (parquet int matches schema int), not the other way around.
- [x] `fetal_death/PROVENANCE.md`, `fetal_death/PROVENANCE.sha256` — exist; will be overwritten with v2.1.0 SHAs
- [x] `fetal_death/README.md`, `ABOUT_THIS_RELEASE.md`, `COMPARABILITY.md`, `CODEBOOK.md`, `FAQ.md`, `GETTING_STARTED.md`, `.zenodo.json`, `CITATION.cff` — exist at v2.0.0 framing; will be edited for v2.1.0 narrative (2003/2004 coverage, B7 normalization, H8 dtype fix-up, 31/31 + 28/28 validation counts)
- [x] `fetal_death/live_births_by_year.csv` — exists; will append 2003 + 2004 rows from natality denominators (using the existing `shared/helpers/build_stratified_denominators.py` runtime against the natality parquet)
- [x] Downstream joint-use code using string literals (per `FIX_LOG.md` 2026-05-11 H8 entry, list of files: `docs/JOINT_USE_GUIDE.md`, `notebooks/joint_use_demo.ipynb`, `notebooks/_build_joint_use_demo.py`, `notebooks/paper_companion.ipynb`, `notebooks/_build_paper_companion.py`) — will be updated to int literals as part of Task 3 (per STATUS HALT 2 forward-looking commitment). VERIFY must re-run both demo notebooks and confirm they still pass byte-exact after the dtype switch.

### Field-value snapshot (Convention 3)

**Snapshot A — H8 dtype-drift columns (shipped state vs schema declaration).**

For every canonical artifact this task will mutate, the current values are snapshot below. Divergences resolved here at the cheap-check moment.

| Column | `harmonized_schema.csv` type | v2.0.0 parquet dtype (verified at sha=`90af89b9…f0afdd`) | Post-Task-3 plan |
|---|---|---|---|
| `tabulation_flag` | `int` (allowed `1-2`) | `string` (Python `str`, values `'1'`, `'2'`) | rebuild parquet under int dtype |
| `residence_status` | `int` (allowed `1-4`) | `string` (values `'1'`-`'4'`) | rebuild parquet under int dtype |
| `maternal_age` | `int` (allowed `10-54;99`) | `string` (values `'10'`-`'54'`, `'99'`) | rebuild parquet under int dtype |
| `maternal_race_bridged` | `int` (allowed `1-4`) | `string` (values `'1'`-`'4'`) | rebuild parquet under int dtype |
| `hispanic_origin` | `int` (allowed `0-9`) | `string` (values `'0'`-`'9'`) | rebuild parquet under int dtype |

**Bundling decision (Convention 3 second bullet — resolved at PRE-FLIGHT, will be re-stated in DECISION_LOG entry at DO start).** The H8 reconciliation is bundled into Task 3 because: (i) the parquet is re-derived anyway as part of adding 2003 + 2004 records, so the dtype fix rides for free; (ii) the schema CSV is the canonical authority — fixing the parquet to match the schema (rather than the reverse) preserves the design intent; (iii) the FIX_LOG 2026-05-11 entry already commits to this resolution path. Schema CSV is NOT edited (anti-pattern #6 preserved).

**Snapshot B — Task 5 manuscript HALTs (verify they still hold pre-Task-3-DO).**

| HALT | Pre-DO state | Holds? |
|---|---|---|
| 1: 3 `<!-- YP: review -->` markers in `paper/draft_v2_hmd_styled.md` | `grep -c "<!-- YP:"` returns 3 | ✓ unchanged |
| 5: paper_companion_results.csv shows C04 DIFF / C33 L11 / C47-C49 L11 | sha=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` matches Task 5 receipt | ✓ unchanged |
| 6: paper sha `0685fe9c…1bddd1` | matches manuscript current file | ✓ unchanged |
| 2, 3, 4, 7, 8, 9 | informational / deferred per data-first sequence | not Task-3-blockers ✓ |

**Snapshot C — Sequence-specific HALTs from STATUS 2026-05-11T20:50Z (verify pre-Task-3-DO).**

| HALT | Pre-DO state | Holds? |
|---|---|---|
| 1: Task 3 PRE-FLIGHT L9 risk on 2003/2004 layout reconstruction | L9 cheap-check above resolved record-length apparent-conflict; A/S byte and TABFLAG-9 position both confirmed empirically; deep layout reconstruction is DO work (halt-and-ask policy committed per AskUserQuestion at PRE-FLIGHT) | ✓ resolved at the cheap-check level |
| 2: H8 bundling decision committed | Snapshot A above; 5 columns confirmed string-typed in v2.0.0 parquet | ✓ committed |
| 3: Manuscript sha will change post-Task-3 in step 5 of sequence | informational; not Task-3 in-scope (Task 3 does not touch the manuscript) | ✓ acknowledged |

**Snapshot D — `fetal_death/file_inventory.csv` rows being mutated.**

DO will APPEND 2 rows (2003 + 2004). Current state: 30 data rows (1992-2002 + 2005-2022), all with `imported,no`. The new rows will follow the same convention:

- 2003: `2003,https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2003US.zip,NCHS,Fetal2003US.zip,fixed-width zip,2003FetalUserGuide.pdf,1351,no,transition year; per-state A/S dispatch at position 7; B7 TABFLAG correction applies (fetaldeath0304problems.pdf); 54,537 records`
- 2004: `2004,https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2004US.zip,NCHS,Fetal2004US.zip,fixed-width zip,2004FetalUserGuide.pdf,1501,no,transition year; per-state A/S dispatch at position 7; B7 TABFLAG correction applies (fetaldeath0304problems.pdf); 53,320 records`

(The 1351 / 1501 in the `record_length` column matches the existing `record_length` semantic in the CSV — see 1992 row's `360` and 2006 row's `3351`; this is the line length including the trailing CRLF per measured behavior of comparable rows.)

### Halt conditions tripped
None. The two soft-flags above (B7 normalization is new; A/S dispatch needs deeper user-guide reading at DO start) are tracked items for DO, not PRE-FLIGHT halts. The L9 record-length apparent-conflict was resolved empirically at PRE-FLIGHT.

### Result
**PROCEED.** All 5 input categories verified, environment meets requirements, three staging decisions resolved at the cheap-check moment per Convention 3, H8 bundling committed, Task 5 + sequencing HALTs all hold. Halt-and-ask policy on layout ambiguities committed for DO phase per AskUserQuestion at PRE-FLIGHT.

### Next steps (DO phase, not part of PRE-FLIGHT)

1. Tag `task3-pre-do` after this PRE-FLIGHT commit lands.
2. Read 2003 user guide record-layout section (estimated mid-document, ~30-60 pages in); reconstruct `record_layout_2003.csv` mirroring `record_layout_1992.csv` and `record_layout_2006.csv` formats. Halt-and-ask on any field whose byte position is ambiguous from the user guide alone.
3. Same for `record_layout_2004.csv` (which is mostly the 2003 layout extended; verify identity for shared fields).
4. Extend `field_specs.py` with `FETAL_2003_FIELDS` + `FETAL_2004_FIELDS` lists and per-state A/S dispatch in `layout_for_year(year, state_code, revision_byte)`.
5. Parse 2003 + 2004 zips into `output/yearly_clean/fetal_death_{2003,2004}_raw.parquet`. Halt if either parse rejects > 1% of records as bad-length.
6. Extend `harmonize.py`: (a) include 2003 + 2004 in the year set; (b) implement B7 TABFLAG correction per `fetaldeath0304problems.pdf` (records with COMBGEST=99 and state in 42-state list → set TABFLAG=2); (c) cast the 5 H8 columns to int (NaN-aware: maternal_age=99 sentinel stays a int 99 but maternal_age=blank → null; tabulation_flag and residence_status are mandatory; etc.).
7. Re-run derive.py and validate scripts. VERIFY: 31/31 per-year counts + 28/28 rates byte-exact against NVSR 57-08 (was 29/29 + 26/26 in v2.0.0); 2005-2022 byte-clean regression on all 73 harmonized + 89 derived columns vs. v2.0.0 baselines AFTER the int-dtype fix is normalized away in the comparison.
8. Update downstream joint-use code to int literals (5 files per STATUS HALT 2). Re-run `_build_joint_use_demo.py` and confirm 8/8 NVSR cells still byte-exact.
9. Bump fetal-death version to v2.1.0 in `.zenodo.json`, `CITATION.cff`, `ABOUT_THIS_RELEASE.md`, `README.md`, `COMPARABILITY.md`, `FAQ.md`, `PROVENANCE.md`.
10. Append 2003 + 2004 rows to `file_inventory.csv`, `external_validation_targets.csv`, `live_births_by_year.csv`.
11. Write FIX_LOG entry closing the 2026-05-11 H8 entry (H8 reconciled in v2.1.0 parquet).
12. Write receipt to `RECEIPTS/task3_v21_fetal_death_<UTC>.md` with five-phase trace, self-check, Forward-looking HALTs.
13. Tag `task3-complete`.

---

## PRE-FLIGHT for task5_manuscript_trim — 2026-05-11T20:05:00Z

### Inputs
- [x] All required input files exist
  - `paper/draft_v2_hmd_styled.md`: present, 161 lines, sha256=`5e86c923d581936ce517740fadb6b247bbac4f6297a1cd517ed36b9f3c3967fb` (matches Task 4 receipt's read-only consumption sha; carries Task 4 Forward-looking HALT 5 condition — change of this sha at next PRE-FLIGHT is EXPECTED for Task 5) ✓
  - `paper/README.md`: present, sha256=`d87a4a4012b20933e75fea16bbe75db480cdb2c2d739ab3659243dec34d9b226` (matches Task 4 receipt post-edit sha; carries the 5 precision-edit candidates inlined for Task 5 consumption) ✓
  - `notebooks/paper_companion_results.csv`: present, sha256=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` (bit-stable Task 4 synthesis; will change after Task 5 manuscript edits — Forward-looking HALT 5) ✓
  - `notebooks/_build_paper_companion.py`: present, sha256=`055c3aff0b12ec0bef029aa2da761e36e89a8134d9a4fa4918a11283e2517abe` (deterministic builder; will be re-run during VERIFY) ✓
  - `CITATION.cff`: present, sole author = Yoel Plutchok ✓ (Author contributions admin section will reflect this)
  - `fetal_death/harmonized_schema.csv`: present, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (used for the C47/C48/C49 re-verification below) ✓
  - `natality/metadata/harmonized_schema.csv`: present, sha256=`2e95488fd910f60cbf5965bd9f0d3503f59111e38180c20e4e51e29af2983577` ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` (used for C47/C48/C49 column null-rate verification; matches Task 4) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (used for C04 mean-recompute) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
  - task2 (2026-05-11, `c068628`): ✓
  - §15 Task 2/4 breadcrumb-annotation `[plan-update]` (2026-05-11, `89ddc77`): ✓
  - task4 (2026-05-11, `abd22e0`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task5_*.md`: does not exist ✓
  - `paper/draft_v2_hmd_styled.md` carries no `[TASK5-DRAFT]` markers from a prior aborted attempt ✓
- [x] Forward-looking HALTs from prior session (Task 4 receipt) verified at PRE-FLIGHT
  - **Task 4 HALT #1** (five Task-5 precision-edit candidates inlined in `paper/README.md`): verified — `paper/README.md` line 22 names C04, C29, C33, C47/C48/C49. **However: re-verification finding** — see Field-value snapshot below — discovers that C47/C48/C49 was a Task 4 misdiagnosis (Task 4 checked the natality parquet whose harmonized column names differ from fetal-death; the manuscript line-104 italicized names ARE fetal-death harmonized column names and ARE blank for V1 2007-2013 per the fetal-death parquet). Task 5 will apply C04, C29, C33; will NOT apply C47/C48/C49.
  - **Task 4 HALT #2** (paper_companion.ipynb sha not bit-stable; use CSV sha): acknowledged. Task 5 will not touch the notebook; will re-run the builder during VERIFY and inspect the new CSV synthesis for changed pass/fail tags. CSV-sha-change is EXPECTED (manuscript sha changes → new claim values).
  - **Task 4 HALT #3** (§15 Task 4 Section B re-deferral): acknowledged, not in Task 5 scope. The `[plan-update]` candidate for §15 Task 4 wording is open question #6 in current STATUS; not handled in Task 5 to avoid scope creep.
  - **Task 4 HALT #4** (H8 dtype drift not yet reconciled): Task 5 touches only the manuscript and admin docs; no fetal-death joint-use code modified. HALT remains green by construction.
  - **Task 4 HALT #5** (touching `paper/draft_v2_hmd_styled.md` → re-run paper_companion builder): this IS Task 5; manuscript sha WILL change from `5e86c923...`. Re-running the builder during VERIFY is mandatory; new CSV synthesis is the post-edit verification artifact.
  - **Task 4 HALT #6** (Task 1 HALT 6 natality v2.8 rename plan-update): carried forward; not in Task 5 scope.

### Environment
- [x] Python version: 3.13.9 (≥3.11 required) ✓
- [x] pandas: 2.3.2 ✓
- [x] pyarrow: 18.1.0 ✓
- [x] nbformat / nbclient: present (used by `_build_paper_companion.py`) ✓
- [x] Working directory clean (`git status` on `main` at `abd22e0`): ✓
- [x] On expected branch (`main`): ✓
- [x] L10 check on prior task: Task 4 PRE-FLIGHT (`61090fc`, 2026-05-11T19:15:00Z) precedes Task 4 DO/RECEIPT commit (`abd22e0`, 2026-05-11T19:26:28Z) ✓

### Source documentation
- [x] No new NVSR PDF transcription. Task 5 is a manuscript trim + admin-section fill + 5 precision-edit candidates from Task 4 + Companion-paper sentence. No new numeric claims introduced.
- [x] IJE Data Resource Profile word limit: 2,500 words main text (excluding abstract, key features, references, tables). Source: `paper/README.md` line 16. Cannot verify against current IJE author guidelines from offline state; the 2,500 limit is the figure carried by `paper/README.md`.

### Outputs
- [x] Intended output paths
  - `paper/draft_v2_hmd_styled.md`: EDIT (overwrite; prior version preserved in git at `abd22e0`) ✓
  - `paper/README.md`: EDIT — outstanding-work items now CLOSED by Task 5 marked accordingly ✓
  - `notebooks/paper_companion.ipynb`: EDIT via re-running the builder (per Task 4 HALT 5; binary sha will change per L17 — data-content reproducibility is via CSV) ✓
  - `notebooks/paper_companion_results.csv`: EDIT (will reflect new claim values; sha will change from `7891809c...`) ✓
  - `RECEIPTS/task5_manuscript_trim_<ts>.md`: NEW ✓
  - `NEXT_STEPS.md`: EDIT (§17 item 6 ⏳ → ✅ on success) ✓
  - `STATUS.md`: EDIT (new section dated 2026-05-11T20:xx:xxZ) ✓
  - `DECISION_LOG.md`: EDIT (new entry for the C47/C48/C49 re-verification override and any admin-section content decisions; possibly the C04 framing decision) ✓
  - `PRE_FLIGHT_LOG.md`: this entry ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Task 5's purpose is to (a) trim the manuscript body to ≤2,500 words, (b) apply Task 4's 5 precision-edit candidates, (c) fill admin sections, (d) add a Companion paper sentence. Convention 3 applied here means **enumerating the current word counts per section + verifying every claim that Task 5 will edit BEFORE the first edit** so that mid-DO surprises (e.g., "I trimmed S&W by 250 words but the body total isn't 2500 yet") are caught at the cheap-check moment.

**Current word count per section (verified 2026-05-11T20:00Z via `re.findall(r"[A-Za-z][A-Za-z0-9'\\-]*")` on body text after stripping table-row pipes, footnote refs, code blocks, and header lines):**

| Section | Current words | IJE category | In 2,500 main-text budget? |
|---|---|---|---|
| (Title + abstract preamble, lines 1–4) | 191 | abstract | NO |
| Data resource basics | 483 | main | YES |
| Data resource area and coverage | 241 | main (Table 1 already excluded) | YES |
| Measures | 452 | main | YES |
| Methods | 487 | main | YES |
| Data resource use | 465 | main | YES |
| Strengths and weaknesses | 650 | main | YES |
| Future developments | 147 | main | YES |
| Data resource access | 130 | main | YES |
| HVS in a nutshell | 136 | key features | NO |
| Ethics approval | 30 | admin | NO |
| Author contributions | 3 | admin (placeholder) | NO |
| Use of artificial intelligence (AI) tools | 20 | admin (placeholder) | NO |
| Conflict of interest | 2 | admin | NO |
| Funding | 3 | admin (placeholder) | NO |
| References | 128 | references | NO |
| **Main-text body total (Basics→Access)** | **3,055** | — | over by **555** |

**Trim target.** 3,055 − 555 = 2,500. Need to cut **at least 555 words** from the main-text body; aim for ~500–550 to leave buffer. Per §15 DO scope, S&W is the primary trim target.

**§15-spec-vs-current-state divergences caught at this PRE-FLIGHT (Convention 3 second bullet):**

| §15 Task 5 spec | Current state (verified at PRE-FLIGHT) | Resolution |
|---|---|---|
| "Trim Strengths and Weaknesses (longest section, currently ~1,000 words; aim for 600)" | S&W is **650 words**, not 1,000. Either §15 was based on an older draft (draft_v1?) or S&W has been partly trimmed since the §15 spec was written. | Re-target S&W to **~400 words** (trim ~250). The "aim for 600" is preserved as upper bound; aiming lower frees budget for other sections to keep some narrative density. |
| "Move the 19-detail-cell breakdown to a supplementary table" | The "13/19 detail cells byte-exact + 6 documented diffs" framing appears in `README.md` (monorepo top-level) and `fetal_death/README.md` but **does NOT appear in `paper/draft_v2_hmd_styled.md`**. The manuscript's line-94 fetal-death validation claim is aggregate-level ("29 per-year counts + 26 per-year fetal mortality rates match exactly"); no detail-cell breakdown to move. | DO item **MOOT** — already absent from the manuscript. Document in receipt. |
| "Format references to journal style" | Current references (lines 153–161) use a Vancouver-style numbered + journal-italicized format. **Precise IJE reference style requires access to IJE author guidelines** (e.g., abbreviated journal names per Index Medicus, specific punctuation, etc.) which are not on disk and which I do not have a confirmed source for. | Apply minimal cleanup (consistency, punctuation); leave precise journal-style reformatting as a **deferred polish pass** for the human submission preparer. Document in receipt + STATUS open questions. |
| "Fill Ethics approval, Author contributions, AI-tool disclosure, Conflict of interest, Funding" | Ethics approval (30 words) and Conflict of interest (2 words "None declared") are already filled. Author contributions (3 words), AI-tool disclosure (20 words), Funding (3 words) are placeholders. | Author contributions: draft from CITATION.cff sole-author state. AI-tool disclosure: draft a reasonable disclosure for LLM-coding-agent use in pipeline + manuscript work, with a `[YP: review and edit]` note. Funding: draft "None declared" with same review note. **All three admin drafts are LLM-supplied content for a sole-author manuscript and are explicit candidates for human review** — recorded in DECISION_LOG and Forward-looking HALTs. |

**5 precision-edit candidates from Task 4 — PRE-FLIGHT re-verification:**

| Tag | Line | Task 4 recommendation | PRE-FLIGHT re-verification | Apply? |
|---|---|---|---|---|
| C04 | 7 | "approximately 3.5 million" → "approximately 3.5–4 million" or "3.97M average" | Natality 1990–2024 mean = 3,966,276; range 3,605,081–4,324,008 (verified now). Current "3.5 million" is below the actual 1990–2024 mean. Task 4's "3.5–4 million" preserves prose flow with one-character edit. | **YES** — apply "approximately 3.5–4 million" |
| C29 | 23 | "two within fetal death" boundary count → "three eras with two era-to-era transitions" wording | Table 1 ships 3 fetal-death era rows (1992–2002, 2005–2017, 2018–2022) = 2 boundaries. Current wording "two within fetal death" is correct under boundary-reading but mismatches casual Table-1-row-count reading. Task 4 recommendation is clearer. | **YES** — rephrase to make eras-vs-boundaries explicit |
| C33 | 60 | "Three fetal-death columns are tagged within_era" is scope-restrictive → "Three of the within_era fetal-death columns carry irreducibly incompatible..." | Schema has 24 within_era columns total (verified now: `comparability_class == 'within_era'` in `fetal_death/harmonized_schema.csv`). The three named (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) are within_era but not the only ones. Task 4 recommendation is more precise. | **YES** — apply "Three of the within_era fetal-death columns..." |
| C47/C48/C49 | 104 | Italicised `maternal_education` / `paternal_age_combined` / `maternal_education_unrevised` are raw NCHS field names, not harmonized columns; clarify | **MISDIAGNOSIS**: Task 4 PRE-FLIGHT/DO checked the natality parquet (where the harmonized columns are named `maternal_education_cat4`, `father_age`). The manuscript line-104 names ARE fetal-death harmonized columns: `fetal_death/harmonized_schema.csv` line 17 (`maternal_education`, years_available `2005-2006, 2014-2022`), line 18 (`maternal_education_unrevised`, years_available `1992-2002, 2005-2006`), line 21 (`paternal_age_combined`, years_available `1992-2002, 2005-2006, 2014-2022`). Direct null-rate verification on `fetal_death_derived.parquet` shows 100% blank for all three columns in 2007–2013, matching the manuscript's claim byte-exact. The manuscript italicization is consistent with line 60's `breech_unrevised` etc. (italics = harmonized column names). | **NO** — keep manuscript wording as-is. Task 4's L11 was a misdiagnosis. Log to DECISION_LOG; document in receipt self-check. |

**Companion paper sentence design (§15 Task 5 DO item):**

Goal: one sentence pointing to the monorepo (https://github.com/yoelplutchok/vital-statistics-harmonization, not yet pushed per STATUS open question 1) and the cross-product worked-example notebooks (`notebooks/joint_use_demo.ipynb`, `notebooks/paper_companion.ipynb`). Will be placed at the end of the "Data resource access" section.

Draft: "Cross-product worked examples — including a joint-use demonstration reproducing the 2022 maternal-age-stratified fetal mortality cells against *NVSR 73-09* Table 4, and a paper-companion notebook recomputing every numeric claim in this manuscript directly from the parquets — are shipped under `notebooks/` in the monorepo accompanying this resource."

This does NOT include a github URL because the monorepo has not yet been pushed (STATUS open question 1). The user's submission preparer should add the URL once it is pushed.

### Plan assumptions amended at PRE-FLIGHT (Convention 3 second bullet)

1. **C47/C48/C49 NOT applied.** Task 4's L11 recommendation is a misdiagnosis (checked natality parquet; should have checked fetal-death). Manuscript wording at line 104 is byte-exact correct. Record in DECISION_LOG as an override of Task 4's recommendation.
2. **S&W trim target ~400 words (not 600).** §15 figure of "currently ~1,000 words" is stale; actual is 650.
3. **"Move 19-detail-cell breakdown" DO item MOOT** — not in the current manuscript.
4. **References reformatting limited to consistency cleanup**, not full IJE-style reformatting. The latter requires IJE author guidelines I do not have a verified source for. Deferred.
5. **Admin-section drafts are LLM-supplied for a sole-author manuscript.** Author contributions can be derived from CITATION.cff (sole author = Yoel Plutchok). AI-tool disclosure will be drafted per IJE policy as referenced in the manuscript's own placeholder ("disclose any AI-tool use in pipeline development, documentation drafting, or manuscript preparation"). Funding defaulted to "None declared." All three carry an explicit human-review note in the receipt's Forward-looking HALTs.

### Halt conditions tripped
None unresolved. Four findings (C47/C48/C49 override; S&W target recalibration; 19-cell-breakdown MOOT; references-reformatting deferral) are resolved at this PRE-FLIGHT moment per Convention 3 second bullet. No prior validated artifact is being mutated — the manuscript edit is expected and authorized; the paper_companion notebook re-run is mandatory per Task 4 HALT 5; all other touches are state-file appends.

### Result
PROCEED.

---

## PRE-FLIGHT for task4_paper_companion — 2026-05-11T19:15:00Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (carries Task 1+2 PROVENANCE-gap finding; unchanged) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (unchanged) ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0 ✓
  - `paper/draft_v2_hmd_styled.md`: present, 161 lines, sha256=`5e86c923d581936ce517740fadb6b247bbac4f6297a1cd517ed36b9f3c3967fb` ✓
  - `fetal_death/harmonized_schema.csv`: present, 73 rows, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` ✓
  - `natality/metadata/harmonized_schema.csv`: present, 94 rows, sha256=`2e95488fd910f60cbf5965bd9f0d3503f59111e38180c20e4e51e29af2983577` ✓
  - `natality/output/validation/external_validation_v1_comparison.csv`: present, 183 rows, sha256=`c82a412ca16dc0f8b3c8a6a6b842b8a4cac43c19015a388bba1f4608f123e68a` ✓
  - `natality/output/validation/external_validation_v3_linked_comparison.csv`: present, 35 rows, sha256=`868dc5c99e7c7e7bc3cd7674dee6a2abf7062af15ea01e83b4bd14d23763dcbe` ✓
  - `fetal_death/validation_results.csv`: present, 29 rows (1992–2002 + 2005–2022), sha256=`8041586dc99f450faf4a3b91505a98652410a31d6caa5da14dfa39c75da7de0e` ✓
  - `fetal_death/external_validation_targets.csv`: present, 81 data rows, sha256=`0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f` ✓
  - `fetal_death/stratified_denominators.csv` (Task 1 output): sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` (matches Task 1 HALT 1 byte-exact) ✓
  - `shared/helpers/canonical_join_keys.py`: present; `NATALITY_TO_CANONICAL` unchanged (matches Task 1 HALT 2 byte-exact) ✓
  - `fetal_death/ABOUT_THIS_RELEASE.md`: present; carries the canonical 13/19 detail-cell + 6 docs-diffs narrative referenced by manuscript line 94 ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
  - task2 (2026-05-11, `c068628`): ✓
  - §15 Task 2/4 breadcrumb-annotation `[plan-update]` (2026-05-11, `89ddc77`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task4_*.md`: does not exist ✓
  - `notebooks/paper_companion.ipynb`: does not exist (only the planned-stub mention in `notebooks/README.md`) ✓
  - `notebooks/_build_paper_companion.py`: does not exist ✓
- [x] Forward-looking HALTs from prior session (Task 2 receipt) verified at PRE-FLIGHT
  - **Task 2 HALT #1** (joint_use_demo 8-cell NVSR validation): Task 4 does NOT touch the natality v2.7.0 or fetal-death v2.0.0 parquets; HALT #1 remains green by construction. Will re-verify in VERIFY by re-running `python notebooks/_build_joint_use_demo.py` after Task 4's DO to confirm no incidental regression.
  - **Task 2 HALT #2** (fetal-death H8 dtype drift): this notebook MUST use string literals on `tabulation_flag`/`residence_status`/`maternal_age`/`maternal_race_bridged`/`hispanic_origin`. Committed in the notebook design below.
  - **Task 2 HALT #3** (L17 .ipynb sha not bit-stable): same applies to Task 4's notebook. Verified-by-data-content rather than by-sha; receipt records this explicitly.
  - **Task 2 HALT #4** (§15 Task 2 wording plan-update): resolved by `89ddc77` "§15 Task 2 + Task 4: breadcrumb annotations" — verified by reading current `NEXT_STEPS.md` §15 Task 2 line 497, which now ships the PRE-FLIGHT-amended-scope breadcrumb.
  - **Task 2 HALT #5** (schema-doc parity smoke test): informational only; not gating Task 4. Carried forward.
  - **Task 2 HALT #6** (Task 1 HALT 5 closed): confirmed.

### Environment
- [x] Python version: 3.13.9 (≥3.11 required) ✓
- [x] pandas: 2.3.2 ✓
- [x] pyarrow: 18.1.0 ✓
- [x] nbformat: 5.10.4 ✓
- [x] nbclient: present (verified by Task 2's successful nbclient execution at `c068628`) ✓
- [x] Working directory clean (`git status` on `main` at `89ddc77`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] No new NVSR PDF transcription. Task 4 reads only artifacts that have already been PDF-anchored in prior tasks (the validation CSVs and the harmonized parquets); no L9 risk on numeric reproduction.
- [x] §15 Task 4 "absorbs Section B NVSR cell-level validation deferred from Task 2" — **L9 cheap-check**: `fetal_death/external_validation_targets.csv` contains NO 2017 race-stratified fetal-death targets (verified by metric enumeration: 26 distinct metrics, none race-keyed). Absorbing Section B would require a fresh PDF transcription from the 2017-vintage NVSR fetal-mortality report (NVSR 67-?). The original Task 2 deferral cited exactly this L9 risk. **Resolution**: re-defer the Section B absorption per Convention 3 second bullet — see Field-value snapshot below for the formal divergence and reasoning. Section B race-stratified 2017 NVSR validation becomes a separate small future task (input: NVSR-2017 fetal-mortality PDF; output: 4 new rows in `external_validation_targets.csv`; cost: one short session if the PDF is at hand).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `notebooks/_build_paper_companion.py`: new ✓ (deterministic builder; `DESIGN: tracks-current-state` per Convention 2)
  - `notebooks/paper_companion.ipynb`: new ✓ (built by the above; executed with nbclient; not bit-sha-stable per L17/HALT 3)
  - `RECEIPTS/task4_paper_companion_<ts>.md`: new ✓
  - Edits to existing files explicitly intended: `notebooks/README.md` (paper_companion description), `NEXT_STEPS.md` (§17 item 7 ⏳ → ✅ on success), `paper/README.md` (mark "Companion notebook" outstanding-work item resolved), `STATUS.md`, possibly `DECISION_LOG.md` for any L6/L11 findings that need to be fixed in the manuscript

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Task 4's purpose is to surface L6/L11 drift between the manuscript text and the underlying artifacts. Convention 3 applied here means **enumerating every numeric claim in the manuscript** before writing the first cell, recording the source-of-truth, the plan-assumed value, and the current actual value. Each row's `current_actual` is computed at this PRE-FLIGHT moment so that mid-DO findings are surprises in the *manuscript*, not in the *artifacts*.

**Notation**: `LB-N` = manuscript line N below. `SoT` = source of truth artifact. `plan_value` = the manuscript's stated number. `current_actual` = computed at this PRE-FLIGHT. `?` = will be computed during notebook build (cheap; computing now would require parquet loads which the SMOKE Tier 1 + DO phases will do anyway). `match` column populated where snapshot is doable from CSVs/schemas without parquet load.

| Tag | LB | Claim (excerpted) | SoT | plan_value | current_actual | match |
|---|---|---|---|---|---|---|
| C01 | 3 | 138,819,655 natality records (1990–2024) | natality parquet `len` | 138,819,655 | ? (DO) | DO |
| C02 | 3 | 74,943,824 linked records (2005–2023) | linked parquet `len` | 74,943,824 | ? (DO) | DO |
| C03 | 3 | 1,634,195 fetal-death records (1992–2022) | fetal-death parquet `len` | 1,634,195 | ? (DO) | DO |
| C04 | 7 | ~3.5M live births/year | natality parquet `len / n_years` | ~3.5M | ? (DO) | DO |
| C05 | 7 | 20,000–30,000 fetal deaths/year | fetal-death parquet groupby year | 20K–30K | ? (DO) | DO |
| C06 | 7 | 20,000 infant deaths/year | linked parquet death-side filter | ~20K | ? (DO) | DO |
| C07 | 9 | 2003–2014 phasing natality | NCHS source / docs only (not a parquet number) | 2003–2014 | (cite-only) | n/a |
| C08 | 9 | 2005–2017 V1 fetal-death window | docs (`fetal_death/COMPARABILITY.md`) | 2005–2017 | matches | ✓ |
| C09 | 9 | 100% A-version in 2018 | docs | 100% in 2018 | matches | ✓ |
| C10 | 9 | 2006 natality 1500→775 bytes | record_layout / docs | 1500→775 | matches Table 1 row | ✓ |
| C11 | 9 | 2009 unrevised-only blanked | docs | 2009 | matches | ✓ |
| C12 | 9 | 2014 natality 1345-byte layout | record_layout / docs | 1345 | matches Table 1 row | ✓ |
| C13 | 11 | Salihu 1995–1998 | citation | 1995–1998 | (cite-only) | n/a |
| C14 | 11 | Willinger 2001–2002 | citation | 2001–2002 | (cite-only) | n/a |
| C15 | 15 | first release 2026 | repo bootstrap date | 2026 | matches STATUS.md bootstrap | ✓ |
| C16 | 19 | 138,819,655 (1990–2024) | dup of C01 | 138,819,655 | ? | DO |
| C17 | 19 | 84 natality columns | natality parquet `n_cols` | 84 | 84 (verified now) | ✓ |
| C18 | 19 | 74,943,824 (2005–2023) | dup of C02 | 74,943,824 | ? | DO |
| C19 | 19 | 94 linked columns | linked parquet `n_cols` | 94 | 94 (verified now) | ✓ |
| C20 | 19 | denom-plus cohort 2005–2015; period-cohort 2016–2023 | docs | per text | matches | ✓ |
| C21 | 19 | 1,634,195 (1992–2022) | dup of C03 | 1,634,195 | ? | DO |
| C22 | 19 | 89 fetal-death columns | fetal-death parquet `n_cols` | 89 | 89 (verified now) | ✓ |
| C23 | 21 | 2003 transition 1351 bytes | NCHS docs / pending V2.1 | 1351 | (no on-disk artifact in HVS — cite-only) | n/a |
| C24 | 21 | 2004 transition 1501 bytes | same | 1501 | (cite-only) | n/a |
| C25 | 21 | 50 × 197 × 10 = 98,500 byte-comparisons | `fetal_death/ABOUT_THIS_RELEASE.md` line 4 | 98,500 | matches arithmetic + ABOUT_THIS_RELEASE | ✓ |
| C26 | 21 | zero mismatches 1993–2002 + 1992 separately | `validation_tracking.csv` | 0 mismatches | matches (validation_tracking notes "matches" for every year) | ✓ |
| C27 | 23 | 5 natality era boundaries | Table 1 | 5 | Table 1 rows = 5 (1990-2002, 2003, 2004-2005, 2006-2013, 2014-2024) | ✓ |
| C28 | 23 | 3 linked era boundaries | Table 1 | 3 | Table 1 rows = 3 | ✓ |
| C29 | 23 | 2 fetal-death era boundaries | Table 1 | 2 | Table 1 rows = 3 (1992-2002, 2005-2017, 2018-2022) — **MISMATCH: text says 2, table shows 3** | ✗ L6 |
| T1 | 29–39 | Table 1 record lengths and certificate revisions | 11 rows | per table | per-row verification will compute matches against record_layout files for the rows where layout files exist; for transition rows where files don't yet exist (2003, 2004 fetal-death), cite NCHS | DO |
| C30 | 45 | natality: 71 harmonized + 13 derived = 84 total | natality schema CSV + parquet | 84 total ✓; 71/13 split | natality parquet=84 cols ✓; **natality schema CSV has 94 rows (different ontology — cross-era expansion?); 71+13 split needs derivation_rule classification on schema rows** | partial |
| C31 | 45 | linked: 7 additional + 3 derived death-side = 94 total | linked schema | 94 ✓; 7/3 split | linked parquet=94 cols ✓; the +7/+3 split needs schema cross-product analysis | partial |
| C32 | 45 | fetal-death: 73 harmonized + 16 derived = 89 total | fetal-death schema + parquet | 89 ✓; 73/16 split | fetal-death parquet=89 cols ✓; schema CSV=73 rows ✓; 89-73=16 ✓ | ✓ |
| C33 | 60 | three fetal-death `within_era` columns | fetal-death schema | 3 | **schema has 24 within_era rows; manuscript line 60 specifically names `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail` as the three "incompatible-clinical-concept" ones — these 3 ARE in the schema's 24 within_era rows. The wording "three columns are tagged within_era" is L11-stale (older partition) or scope-restrictive (the three uniquely-incompatible ones).** | ✗ L11 |
| C34 | 69 | five fetal-death value-level normalizations (`fetal_sex`, `delivery_method_recode`, `maternal_race_bridged`, `paternal_age_recode11`, `delivery_place_recode`) | `fetal_death/ABOUT_THIS_RELEASE.md` (B1-B6 narrative) | 5 | ABOUT_THIS_RELEASE has B1-B6 (six items, not five); manuscript line 69 lists 5. **Possible L6 — verify B1-B6 vs the five named in manuscript** | ? DO |
| C35 | 75 | fetal-death pipeline ~6 min on 2024-vintage laptop | benchmark — not reproducible without running pipeline | ~6 min | (not parquet-derivable; cite-only) | n/a |
| C36 | 75 | natality pipeline ~90 min | same | ~90 min | (cite-only) | n/a |
| C37 | 83 | live_births_by_year sourced from NVSR 57-08 (1995–2002) + NVSR 73-09 (2005–2022) | `fetal_death/live_births_by_year.csv` Source col | per text | will verify against the file at DO | DO |
| C38 | 85 | Level 1 ~10s, Level 2 ~1m, Level 3 ~1-2h | benchmarks | per text | (cite-only) | n/a |
| C39 | 94 | natality 183 of 183 V1 targets (1990–2024) | `natality/output/validation/external_validation_v1_comparison.csv` | 183/183 | csv has 183 data rows; `pass==1` count will be computed at DO | DO |
| C40 | 94 | linked 33 of 35 byte-exact; 2 cells differ by 1 (Task 6 canonical framing) | `natality/output/validation/external_validation_v3_linked_comparison.csv` | 33/35 + 2 by 1 | csv has 35 data rows; Diff=0 count = 33, Diff=1 count = 2 will be computed at DO | DO |
| C41 | 94 | fetal-death: 29 per-year counts | `fetal_death/validation_results.csv` | 29/29 | csv has 29 data rows, all `Match=✓` (verified now) | ✓ |
| C42 | 94 | fetal-death: 26 per-year FMR | `fetal_death/external_validation_targets.csv` rate rows | 26/26 | csv has 26 `fetal_mortality_rate` rows (1995–2002 + 2005–2022, verified now); per-year FMR computation against the parquet will be done at DO | partial (csv-row-count ✓; per-row PASS at DO) |
| C43 | 94 | fetal-death: NVSR 73-09 (2005–2022); NVSR 57-08 Tables A and B (1995–2002); NCHS user guide (1992–1994) | `validation_results.csv` Source col | per text | csv Source col matches text byte-exact (verified now) | ✓ |
| C44 | 100 | cause-of-death not in public-use file before 2014 | parquet `cause_icd10` null-rate by year | 100% null pre-2014 | ? (DO) | DO |
| C45 | 100 | ~50% records lack cause data 2018 onward | parquet `cause_icd10` null-rate by year for 2018+ | ~50% | ? (DO) | DO |
| C46 | 100 | state-level identifiers in fetal-death raw 1992–2002 only | per-year raw parquets (out of monorepo scope; `STATEFET`/`STATERES`/`STOCCFIP` columns) | per text | cite + grep harmonized columns; state cols not in harmonized | partial |
| C47 | 104 | `maternal_education` blank V1 2007–2013 (even for revised records) | parquet null-rate | 100% null in 2007–2013 V1 | ? (DO) | DO |
| C48 | 104 | `paternal_age_combined` blank V1 2007–2013 | parquet null-rate | 100% null in 2007–2013 V1 | ? (DO) | DO |
| C49 | 104 | `maternal_education_unrevised` blank V1 2007 onward | parquet null-rate | 100% null 2007+ V1 | ? (DO) | DO |
| C50 | 106 | Maryland 1992–1998 no Hispanic | `fetal_death/COMPARABILITY.md` + parquet `hispanic_origin` null-rate by state-year | per text | partial verification via national `hispanic_origin` null-rate by year; full state-year verification requires per-year raw parquets (out of monorepo scope) | partial |
| C51 | 106 | Massachusetts 1992–1997 no Hispanic | same | per text | same | partial |
| C52 | 106 | Louisiana 1992–1994 plurality under-reported | same | per text | same | partial |
| C53 | 125 | 138.8M (1990–2024) | dup of C01 (rounded) | 138.8M | ? | DO |
| C54 | 125 | 74.9M (2005–2023) | dup of C02 (rounded) | 74.9M | ? | DO |
| C55 | 125 | 1.6M (1992–2022) | dup of C03 (rounded) | 1.6M | ? | DO |

Pre-DO Field-value snapshot findings (from CSVs / schemas only, no parquet load yet):

1. **C17, C19, C22 confirmed at PRE-FLIGHT**: parquet column counts 84/94/89 match manuscript exactly. No L11 risk on the headline column-count claims.
2. **C29 L6 candidate**: manuscript line 23 says "two within fetal death" era boundaries; Table 1 ships three fetal-death rows (1992–2002, 2005–2017, 2018–2022). Interpretation: "boundaries" = transitions BETWEEN eras, so 3 eras = 2 boundaries. Either reading is defensible (eras vs boundaries); flag for resolution in DO with explicit framing.
3. **C33 L11 candidate**: manuscript line 60 says "Three fetal-death columns are tagged within_era," but schema has 24 within_era. The three named in line 60 (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) ARE within_era, but they are not the only ones. The text is scope-restrictive (these three are uniquely "incompatible clinical concepts that cannot be reconciled") rather than exhaustive. The manuscript may benefit from a precision edit — flag for Task 5 (manuscript trim) rather than fix in Task 4.
4. **C34 verify candidate**: line 69 lists FIVE fetal-death normalizations; `fetal_death/ABOUT_THIS_RELEASE.md` describes the harmonization fixes as B1–B6 (six items). Verify whether the manuscript's five = a subset of ABOUT_THIS_RELEASE's six, or whether one is missing.
5. **C41 confirmed**: 29/29 per-year counts with `Match=✓` byte-exact (verified now).
6. **C42 partial-confirmed**: 26 `fetal_mortality_rate` rows in external_validation_targets.csv covering exactly 1995–2002 + 2005–2022; per-row PASS verified at DO.
7. **C43 confirmed**: source attribution byte-exact.

**Plan assumption amended at PRE-FLIGHT (Convention 3 second bullet)**

1. **Section B 2017 race-stratified NVSR validation deferred from Task 2 is NOT absorbed into Task 4 in this PRE-FLIGHT.** §15 Task 4 description (current state at `89ddc77`) names this absorption; the L9 cheap-check above confirms it requires a fresh PDF transcription with no pre-encoded targets to verify against. Task 4's primary scope (reproduce every manuscript numeric claim) is itself substantial (55+ claims enumerated above) and does not include race-stratified 2017 NVSR claims (manuscript line 94 makes only aggregate-level NVSR validation claims). The Section B absorption becomes a separate small future task — see Forward-looking HALTs in the receipt. This is a Convention 3 second-bullet response: surface the divergence at PRE-FLIGHT, amend the plan with explicit reasoning, do not silently proceed.

2. **C29 framing decision: "boundaries" = transitions, not eras**. The notebook will report 5/3/2 boundary counts under that reading and explicitly note the eras=boundaries+1 relationship for cross-checkers. The manuscript's wording stands.

3. **C33 framing decision: line 60's "three" is scope-restrictive** (the three irreducibly-incompatible-clinical-concept columns), not exhaustive of within_era. The notebook will report both numbers (the 3 named + the full 24 in the schema) and recommend a Task 5 line-60 precision edit to "Three of the within_era fetal-death columns carry irreducibly incompatible clinical concepts across the revision boundary..." Decision logged here; the actual manuscript edit is OUT of Task 4 scope (Task 4 produces the notebook; manuscript edits are Task 5).

### Halt conditions tripped
None unresolved. Three findings (C29 framing, C33 precision, Section B absorption deferral) are resolved at this PRE-FLIGHT moment per Convention 3 second bullet. No previously-stable downstream output is being mutated by Task 4. No new PDF transcription. Task 2's six Forward-looking HALTs all verified or non-applicable.

### Result
PROCEED.

---

## PRE-FLIGHT for task2_joint_use_demo — 2026-05-11T18:27:14Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, 2,202,879,406 bytes, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (matches Task 1 receipt — locally computed, NOT in any shipped PROVENANCE.md; upstream documentation gap carried over from Task 1) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, 1,300,258,973 bytes, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (locally computed; same PROVENANCE gap — the v3 linked derived parquet is not enumerated in `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` which only covers convenience parquets) ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, 25,452,090 bytes, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0 ✓
  - `fetal_death/stratified_denominators.csv` (Task 1 output): present, sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` — matches Task 1 RECEIPT Forward-looking HALT 1 byte-exact ✓
  - `shared/helpers/canonical_join_keys.py` (Task 1 output): present, exports `NATALITY_TO_CANONICAL`, `to_canonical_natality`, `derive_maternal_age_band`; `NATALITY_TO_CANONICAL` content verified as exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}` — matches Task 1 RECEIPT Forward-looking HALT 2 byte-exact ✓
  - `fetal_death/external_validation_targets.csv`: present, 82 rows, headers `year,metric,metric_detail,expected_value,source,notes` ✓
  - `fetal_death/harmonized_schema.csv`: present, contains `data_year`, `tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin` with documented dtypes ✓
  - `docs/JOINT_USE_GUIDE.md`: present, contains "Worked example: fetal mortality rate by maternal race, 2017" (the section that the §15 Task 2 PRE-FLIGHT inputs cite as pseudocode source; the spec's literal year "2022" is stale — see Field-value snapshot below) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task2_*.md`: does not exist ✓
  - `notebooks/joint_use_demo.ipynb`: does not exist (only `notebooks/README.md` planned stub describing it) ✓
- [x] Forward-looking HALTs from prior session (Task 1 receipt) verified at PRE-FLIGHT
  - **Task 1 HALT #1** (stratified_denominators.csv sha unchanged): sha=`6874d5d6...` matches receipt ✓
  - **Task 1 HALT #2** (canonical_join_keys.py NATALITY_TO_CANONICAL dict unchanged): 4 entries match receipt byte-exact ✓
  - **Task 1 HALT #3** (canonical filter on BOTH sides): this PRE-FLIGHT commits the policy in the notebook design — numerator filter `(tabulation_flag == 2) AND (residence_status != 4)`; denominator filter `residence_status != 4` (pre-applied in stratified_denominators.csv, re-asserted in the notebook narrative). Tier 0 SMOKE will mutation-verify both filters catch their respective exclusion records.
  - **Task 1 HALT #4** (bridged-race null cells NOT dropna'd): notebook will preserve null-race rows; 2018+ strata in the denominator carry `maternal_race_bridged = NaN`. Section B uses 2017 (race-available year) so this is not an issue for the by-race computation; for the by-age computation (Section A, year 2022) the maternal_race_bridged column is not in the groupby axis, so null-vs-non-null is irrelevant for Section A.
  - **Task 1 HALT #5** (1992-2002 maternal_race_bridged crosswalk equivalence check): incorporated as SMOKE Tier 1 supplementary check — compute natality's `maternal_race_bridged4` from the harmonized parquet on a 1000-row 1995 sample and cross-check against the fetal-death-side recode rule (`harmonize.py`: 01→1, 02→2, 03→3, 04-78→4, 99→null) applied to the equivalent natality MRACE-source values. The receipt will document the result; failure → halt and ask before claiming the by-race joint-use machinery generalizes to pre-2003 era.
  - **Task 1 HALT #6** (Convention 3 second-bullet drill — Field-value-snapshot as the cheapest divergence-surfacer): this PRE-FLIGHT explicitly demonstrates that response — Field-value snapshot below catches a §15-spec / current-state mismatch BEFORE any DO mutation, and amends the plan at PRE-FLIGHT time rather than mid-DO. Per the L10-safe addendum-protocol pattern.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] nbformat version: 5.10.4 (notebook serialization) ✓
- [x] jupyter_client version: 8.8.0 (kernel for executed-output cells) ✓
- [x] Working directory clean (`git status` on `main` at `4d00ef8`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a for primary computations; NVSR 73-09 Table 4 8 age cells already encoded in `fetal_death/external_validation_targets.csv` (no PDF re-transcription, zero L9 risk on Section A). Section B (2017 race) does NOT transcribe new NVSR figures (NVSR 67-08 Table I race-stratified-2017 figures are NOT pre-encoded and not re-derived in this task; Section B presents computed rates as a joint-use machinery demonstration with NVSR validation deferred to Task 4).
- [x] All cited Zenodo DOIs resolve — natality concept `10.5281/zenodo.19363074` (v2.7.0=`10.5281/zenodo.19868835`); fetal-death v2.0.0=`10.5281/zenodo.20031571`; not re-fetched (using local parquets, all hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `notebooks/joint_use_demo.ipynb`: new ✓
  - `RECEIPTS/task2_joint_use_demo_<ts>.md`: new ✓
  - Edits to existing files explicitly intended: `notebooks/README.md` (description currently says "by maternal race, 2022" — both wrong per Field-value snapshot below; update to "by maternal age band 2022 + maternal race 2017"), `NEXT_STEPS.md` §17 item 4 (⏳ → ✅), `STATUS.md`, `DECISION_LOG.md`. Per §11, propose a `[plan-update]` candidate to NEXT_STEPS.md §15 Task 2 description for stale 2022-by-race wording (NOT done as part of Task 2 itself; flagged in receipt Forward-looking HALTs).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The §15 Task 2 spec was written at bootstrap (2026-05-09) BEFORE Task 1 discovered the bridged-race-2018+ gap and rewrote `docs/JOINT_USE_GUIDE.md` to use 2017 as the worked-example year. The spec is therefore L11-class stale on the bootstrap-to-Task-1 timeline. Snapshot of the divergence and its resolution:

**§15-spec-vs-current-state divergence**

| §15 Task 2 spec (line 497–519) | Current state (verified at PRE-FLIGHT) | Resolution |
|---|---|---|
| "computes the fetal mortality rate per 1,000 (live births + fetal deaths) by maternal race for 2022" | 2022 has `maternal_race_bridged = null` in BOTH products. `fetal_death/harmonized_schema.csv` line 8 `years_available = 1992-2002, 2005-2017`; `stratified_denominators.csv` 2018-2022 strata all carry null race. NCHS dropped MBRACE from the public-use file for those years. Race-stratified 2022 is physically impossible with shipped data. | Section A in the notebook uses **2022 maternal age band** stratification (race-axis swap forced by data); Section B uses **2017 maternal race** stratification (year-swap forced by data) to preserve the §15 spec's "by race" demonstration intent. |
| "matches each cell against *NVSR 73-09* Table A" | `fetal_death/external_validation_targets.csv` rows attributed to `NVSR 73-09 Table A`: `live_births_total` (denominator), `fetal_deaths_male/female` (by SEX), `fetal_deaths_singleton/twin/triplet+` (by PLURALITY). **Table A has no race stratification.** The spec's "Table A" citation is mis-attributed; correct table for maternal-age stratification in NVSR 73-09 is **Table 4** (8 age cells pre-encoded: `fetal_deaths_age_under15/15_19/20_24/25_29/30_34/35_39/40_44/45_plus` for year 2022). | Section A validates against **NVSR 73-09 Table 4 (8 age cells, all pre-encoded in `external_validation_targets.csv`)** — zero PDF transcription, zero L9 risk. Section B (race) defers NVSR validation to Task 4 (per its §15 spec "reproduce every numeric claim in the manuscript"); Section B presents the joint-use computation as a machinery demonstration only, with cells documented but not NVSR-pinned. |
| "Pseudocode in `docs/JOINT_USE_GUIDE.md` ('Worked example: fetal mortality rate by maternal race, 2022')." | `docs/JOINT_USE_GUIDE.md` line 84 reads "Worked example: fetal mortality rate by maternal race, **2017**" — Task 1 (2026-05-11) rewrote this section using 2017 as the example year explicitly because of the bridged-race-2018+ gap. §15 wasn't updated in lockstep. | Section B follows the JOINT_USE_GUIDE.md 2017 worked example pseudocode verbatim (joint-use machinery demonstration via the canonical helper). The `[plan-update]` candidate for §15's stale "2022" cite is flagged in this task's Forward-looking HALTs (per Convention 4) but is NOT done as part of Task 2 itself — proposed as a separate `[plan-update]` commit. |

**Cross-product join-key column-name state (no divergence vs Task 1)**

| Concept | natality v2.7.0 column | fetal_death v2.0.0 column | Verified at PRE-FLIGHT |
|---|---|---|---|
| Event year | `year` int16 | `data_year` int32 | ✓ (renamed via `to_canonical_natality`; output uses `data_year`) |
| Maternal age | `maternal_age` | `maternal_age` | ✓ (matches; 99 sentinel in fetal-death V2 era → NaN before binning) |
| 4-cat bridged race | `maternal_race_bridged4` | `maternal_race_bridged` | ✓ (renamed; both null for 2018+) |
| Hispanic origin | `maternal_hispanic_origin` | `hispanic_origin` | ✓ (renamed) |
| Residence status | `restatus` | `residence_status` | ✓ (renamed; canonical filter `!= 4` on both sides) |

**Numerator-side fetal-death filter state (Convention 3)**

| Concept | fetal_death schema | Plan assumption | Verified |
|---|---|---|---|
| `tabulation_flag` | `int 1-2`, "1=exclude <20wk; 2=include >=20wk", year coverage 1992-2002 + 2005-2022 | filter = `tabulation_flag == 2` produces NVSR-comparable population | ✓ — `fetal_death/external_validation_targets.csv` 2005-2022 `fetal_deaths_gte20wk_resident` rows reproduce against the parquet's `(tabulation_flag == 2) AND (residence_status != 4)` subset (per the existing fetal-death validation suite; 29/29 byte-exact for the count metric). Already-validated; this task does NOT re-run that validation, but consumes the same filter. |
| `residence_status` | `int 1-4`, "1=Resident; 2=Intrastate nonres; 3=Interstate nonres; 4=Foreign res" | filter = `residence_status != 4` excludes foreign residents | ✓ — same as above |

**NVSR 73-09 Table 4 stratified target snapshot (Section A verify targets)**

| year | metric | expected_value | source |
|---|---|---|---|
| 2022 | `fetal_deaths_age_under15` | 16 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_15_19` | 991 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_20_24` | 3631 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_25_29` | 5071 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_30_34` | 5634 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_35_39` | 3613 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_40_44` | 1138 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_45_plus` | 108 | NVSR 73-09 Table 4 |
| **Sum** | (verify against unstratified `fetal_deaths_gte20wk_resident` 2022 = 20,202) | 20,202 | ✓ — table-internal consistency |

**NVSR age bands ≠ helper's 6-band scheme — Section A binning**

`shared/helpers/canonical_join_keys.derive_maternal_age_band` uses 6 bands `<20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+` (Task 1's authoring choice). NVSR 73-09 Table 4 uses **8 bands** including `<15`, `15-19` split (vs the helper's `<20`), and `40-44 / 45+` split (vs the helper's `40+`). Section A's notebook code will compute the 8 NVSR bands directly from `maternal_age` rather than via the helper — the helper stays correct for its joint-use purpose (matching the stratified denominators CSV); the NVSR validation just uses a finer-grained age binning specific to that one comparison. The denominator from `stratified_denominators.csv` for the 2022 by-age comparison can either (a) be re-derived from natality with NVSR's 8-band binning (recommended; ~30 seconds wall-clock on the harmonized parquet), or (b) be aggregated from the existing 6-band CSV with the `<20` and `40+` rows kept whole (acceptable; matches `<15+15-19` and `40-44+45+` sums respectively). Section A uses path (a) for cleanest NVSR-mappable cells, AND demonstrates path (b) sums for cross-check.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Demo year, race-stratified piece**: 2017 (not 2022, per JOINT_USE_GUIDE.md authoritative source). Section B.
2. **Demo year, age-stratified piece**: 2022 (current vintage; matches `external_validation_targets.csv` NVSR 73-09 Table 4 encoded rows). Section A.
3. **NVSR validation scope**: Section A's 8 age cells against NVSR 73-09 Table 4 (pre-encoded). Section B's race cells NOT NVSR-pinned (machinery demonstration only; NVSR validation of race-stratified rates deferred to Task 4 per its scope).
4. **Age binning for Section A**: 8 NVSR bands `<15 / 15-19 / 20-24 / 25-29 / 30-34 / 35-39 / 40-44 / 45+` (derived inline in the notebook from `maternal_age`). Helper's 6-band scheme stays correct for joint-use; the NVSR-specific 8-band scheme is local to this one comparison.
5. **"Loads all three parquets" implementation**: load all three with small column projections; print record counts after canonical filter applied to each; this fulfills the §15 spec's "loads all three parquets, applies each canonical filter" without requiring the linked file in the fetal-mortality-rate computation (linked = infant deaths, not fetal deaths). Demonstrates the unified resource.
6. **Task 1 Forward-looking HALT 5 (1992-2002 crosswalk equivalence)** is incorporated as a SMOKE Tier 1 supplementary check, not as a notebook cell — keeps the notebook focused on the joint-use machinery demonstration; result documented in the receipt.

### Halt conditions tripped
None unresolved. The §15-spec vs current-state divergence (named above) is resolved by amending the task plan at this PRE-FLIGHT moment per Convention 3 and per §15's flexibility ("the spec is a starting point; PRE-FLIGHT may amend based on Field-value snapshot findings"). No previously-stable downstream output is being mutated. The proposed §11 plan-update to §15 Task 2 description is flagged for a separate `[plan-update]` commit (not bundled into Task 2).

### Result
PROCEED.

---

## PRE-FLIGHT addendum for task1_joint_use_denominators — 2026-05-11T17:58:10Z

**Field-value snapshot gap caught at SMOKE Tier 1, resolved pre-DO.** The original PRE-FLIGHT entry (17:50:48Z below) planned to read from `natality_v2_residents_only.parquet`. SMOKE Tier 1 (100 real rows of 2022) failed at parquet-read time:

```
pyarrow.lib.ArrowInvalid: No match for FieldRef.Name(restatus) in year: int16
certificate_revision: string maternal_age: int16 ... [82 column schema]
```

The convenience parquet drops the `restatus` column post-filter — a fact not snapshot in the 17:50:48Z entry's Field-value subsection. Resolution:

1. Switch the build script to read from the full `natality_v2_harmonized_derived.parquet` (2,202,879,406 bytes, locally-computed sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0`). The harmonized parquet carries all 84 columns including `restatus`, and column projection (5 cols out of 84) keeps the read cost roughly equivalent to the residents-only file.
2. Apply the canonical filter `residence_status != 4` in the build script (after the rename helper). This makes the filter audit-explicit rather than relying on the upstream convenience step.
3. Note that the harmonized parquet's sha256 is NOT in any shipped PROVENANCE.md (the natality v2.7.0 deposit's PROVENANCE.md only covers the convenience parquets). This is an upstream documentation gap that I am NOT fixing as part of Task 1 — flagged here for downstream attention.

This addendum precedes the first DO mutation (no canonical output written yet); SMOKE Tier 0 was synthetic and produced only `/tmp/smoke0_out.csv`. The `task1-pre-do` tag remains at commit `7b058fc` (the right rollback point — addendum is still pre-DO).

### Halt conditions tripped
None unresolved. Course correction applied at SMOKE moment per Convention 3.

### Result
PROCEED with build from `natality_v2_harmonized_derived.parquet`.

---

## PRE-FLIGHT for task1_joint_use_denominators — 2026-05-11T17:50:48Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/natality_v2_residents_only.parquet`: present, 1,716,780,400 bytes, sha256=`4c72aaa86c553d53c80c6eb38364c296ebb01636a612ad6664f024b12b153c11` matches `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` v2.7.0 ✓
  - Above parquet's PROVENANCE.md identifies build hash `2d3c3d8` and timestamp 2026-04-28T22:53:25Z; matches Zenodo v2.7.0 (DOI `10.5281/zenodo.19868835`) ✓
  - `natality/metadata/harmonized_schema.csv`: present, 95 rows ✓
  - `fetal_death/harmonized_schema.csv`: present ✓
  - `natality/output/validation/external_validation_v1_comparison.csv`: present; `resident_births` rows confirm byte-exact reproduction for all 35 years 1990–2024 ✓
  - `fetal_death/live_births_by_year.csv`: present, 26 data rows (1995–2002 + 2005–2022) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task1_*.md`: does not exist ✓
  - `shared/helpers/build_stratified_denominators.py`: does not exist ✓
  - `shared/helpers/canonical_join_keys.py`: does not exist ✓
  - `fetal_death/stratified_denominators.parquet`: does not exist ✓
- [x] Forward-looking HALTs from prior session verified
  - **Task 6 HALT #1** (natality parquet PROVENANCE sha must match file sha at PRE-FLIGHT): sha `4c72aaa…` matches PROVENANCE.md ✓
  - **Task 6 HALT #2** (V3 linked re-validation): not applicable — this task does not re-run V3 linked validation.
  - **Task 6 HALT #3** (Conventions 3/4 non-optional for first canonical-data task): this entry includes the Field-value snapshot subsection per Convention 3 ✓; RECEIPT will include Forward-looking HALTs per Convention 4.
  - **Task 6 HALT #4** (mechanism-attribution wording): out of scope here.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] Working directory clean (`git status` on `main` at `efe775d`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a; this task derives stratified counts directly from the validated natality parquet and uses existing validation targets (already PDF-anchored) as the per-year benchmark. No new PDF reads.
- [x] All cited Zenodo DOIs resolve — natality concept DOI `10.5281/zenodo.19363074` (latest = v2.7.0 = `10.5281/zenodo.19868835`); not re-fetched (using local parquet hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `shared/helpers/__init__.py`: new ✓
  - `shared/helpers/canonical_join_keys.py`: new ✓
  - `shared/helpers/build_stratified_denominators.py`: new ✓
  - `fetal_death/stratified_denominators.csv`: new ✓ (CSV not parquet — `*.parquet` is gitignored repo-wide per `.gitignore` line 2; CSV matches the existing pattern of `fetal_death/live_births_by_year.csv`; expected ~6,000 rows in long format, well under any size concern. Output format amended from the §15 spec's "parquet (or CSV)" wording — §15 explicitly allows either.)
  - `RECEIPTS/task1_joint_use_denominators_<ts>.md`: new ✓
  - Edits to existing files (`docs/JOINT_USE_GUIDE.md`, `fetal_death/CODEBOOK.md`, `fetal_death/README.md`, `VERSION_ROADMAP.md`, `NEXT_STEPS.md` §17, `STATUS.md`, `DECISION_LOG.md`): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The original Task 1 spec assumed cross-product column-name parity (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `restatus`). Snapshot of actual schemas shows divergence; resolution documented below.

**Schema-divergence snapshot (cross-product join keys)**

| Concept | natality column (`natality/metadata/harmonized_schema.csv`) | fetal_death column (`fetal_death/harmonized_schema.csv`) | Plan assumed | Divergence resolution |
|---|---|---|---|---|
| Event year | `year` int16 (1990–2024) | `data_year` int32 (1992–2002, 2005–2022) | `data_year` both | Rename at read-time in canonical_join_keys helper; output uses `data_year` |
| Maternal age | `maternal_age` (10–54) | `maternal_age` (10–54;99) | `maternal_age` both | Match ✓ — 99 sentinel in fetal-death; derive age band from non-sentinel values |
| 4-cat bridged race | `maternal_race_bridged4` int8 (1990–2019, null 2020+) | `maternal_race_bridged` int (1992–2002, 2005–2017, null 2018+) | `maternal_race_bridged` both | Rename at read-time; output uses `maternal_race_bridged`; joint-coverage years for non-null bridged race = 1992–2002 + 2005–2017 (24 years); 2018–2022 rows have race=null (documented gap) |
| Hispanic origin | `maternal_hispanic_origin` int8 (codes 0\|1\|2\|3\|4\|5\|9) | `hispanic_origin` int (codes 0–9) | `hispanic_origin` both | Rename at read-time; output uses `hispanic_origin`; code spaces compatible (both expose UMHISP 0–9 with same semantics) |
| Residence status | `restatus` int8 (1\|2\|3\|4) | `residence_status` int (1–4) | `restatus` both | Rename at read-time; canonical filter `residence_status != 4`. Convenience parquet `natality_v2_residents_only.parquet` already applies this filter. |

**Per-year resident_births snapshot (NCHS-series mismatch between two existing artifacts)**

| Year | `natality/output/validation/external_validation_v1_comparison.csv` (CDC residence series; what natality parquet reproduces byte-exact) | `fetal_death/live_births_by_year.csv` (NVSR 57-08 / 73-09 series) | Diff |
|---|---|---|---|
| 1995 | 3,899,589 | 3,899,589 | 0 |
| 1996 | 3,891,494 | 3,891,494 | 0 |
| 1997 | 3,880,894 | 3,880,894 | 0 |
| 1998 | 3,941,553 | 3,941,553 | 0 |
| 1999 | 3,959,417 | 3,959,417 | 0 |
| 2000 | 4,058,814 | 4,058,882 | +68 |
| 2001 | 4,025,933 | 4,026,036 | +103 |
| 2002 | 4,021,726 | 4,021,825 | +99 |
| 2005 | 4,138,349 | 4,138,573 | +224 |
| 2006 | 4,265,555 | 4,265,593 | +38 |
| 2022 | 3,667,758 | 3,667,758 | 0 |

The stratified denominator file reproduces the natality parquet's microdata totals (CDC residence series), which match the natality validation target byte-exact. VERIFY criterion is reframed: sum-across-strata must equal the natality validation target (`external_validation_v1_comparison.csv` `resident_births` for each year), NOT `live_births_by_year.csv`. The latter is preserved as the canonical NVSR-as-published unstratified denominator. The 38–224 record/year discrepancy is documented in JOINT_USE_GUIDE.md, not papered over.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Canonical join-key naming** — output uses fetal_death-style names (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `residence_status`). natality columns are renamed at read-time via a new `shared/helpers/canonical_join_keys.py` helper rather than mutating the shipped natality parquet. Rationale: preserves Zenodo deposit immutability (v2.7.0 stays at its DOI), single source of truth for joint-use code, no breaking change to natality downstream users. A future natality v2.8 rename (Task 11 candidate) is the long-term cross-product parity fix; proposing it as a `[plan-update]` separate from this task.
2. **Output year scope**: 1992–2002 + 2005–2022 (29 joint-coverage years between natality and fetal-death). Years 1990–1991 (natality-only era pre-fetal-death) and 2003–2004 (fetal-death deferred to V2.1) and 2023–2024 (post-fetal-death coverage) excluded from the denominator output.
3. **Bridged race coverage**: 1992–2002 + 2005–2017 populated (24 years); 2018–2022 rows have `maternal_race_bridged = null` (documented gap; users wanting stratified joint-use race rates for 2018–2022 will need to wait for a future task that reconciles `maternal_race_ethnicity_5` vs fetal-death's `race_hispanic_revised`). Cell counts in 2018–2022 stratify on age × hispanic only.
4. **VERIFY criterion 1 reframed**: sum across strata per year matches `natality/output/validation/external_validation_v1_comparison.csv` `resident_births` cell (the natality validation target), not `fetal_death/live_births_by_year.csv` (which uses a different NCHS series). Difference enumerated in the per-year table above.
5. **Age band definition**: <20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+, matching natality's existing `maternal_age_cat` column derivation rule. fetal-death-side users compute the same band from `maternal_age` single year. Sentinel `99` → NaN before binning (per §8 F5).

### Halt conditions tripped
None unresolved. All Field-value-snapshot divergences resolved by amending the task plan in this PRE-FLIGHT (see above) rather than silently proceeding. No previously-stable downstream output (`live_births_by_year.csv`, `external_validation_v1_comparison.csv`, harmonized schemas, manuscript drafts) is being mutated — Task 1 ships new artifacts only.

### Result
PROCEED.

---

## PRE-FLIGHT for task6_linked_validation_reconcile — 2026-05-11T17:05:00Z

### Inputs
- [x] All required input files exist
  - `natality/output/validation/external_validation_v3_linked_comparison.md`: present ✓ (35 PASS / 0 FAIL / 0 MISSING; 2015 `unweighted_infant_deaths` and `postneonatal_deaths` each show Diff=1 but `pass`).
  - `natality/README.md`: present ✓
  - `natality/docs/ABOUT_THIS_RELEASE.md`, `natality/docs/COMPARABILITY.md`, `natality/docs/VALIDATION.md`: present ✓
  - `paper/README.md`, `paper/draft_v1_ipums_styled.md`, `paper/draft_v2_hmd_styled.md`: present ✓
  - Monorepo `README.md`, `NEXT_STEPS.md`, `STATUS.md`: present ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, commit `596e8ce`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task6_*.md`: does not exist (good) ✓

### Environment
- [x] Python version: n/a (docs-only task)
- [x] R version: n/a
- [x] Working directory clean (`git status`): ✓
- [x] On expected branch (`main`, HEAD=`596e8ce`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced in this task have current SHA-256 matching the relevant `file_inventory.csv`
  - n/a — Task 6 is internal-doc reconciliation; no new NVSR re-verification required.

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `RECEIPTS/task6_linked_validation_reconcile_<ts>.md`: does not exist (good) ✓
  - Edits to existing files (natality/README.md, natality/docs/*, paper/README.md, NEXT_STEPS.md, STATUS.md, DECISION_LOG.md, PRE_FLIGHT_LOG.md): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Target cells enumerated; current values verified against the task plan's assumed state.

| File | Line | Current text (excerpt) | Plan assumes |
|---|---|---|---|
| `natality/README.md` | 19 | `183/183 V2 targets pass, 35/35 V3 linked targets pass` | matches ✓ |
| `natality/README.md` | 27 | `V3 linked external targets 35/35 pass (2005–2023, from NCHS linked user guides)` | matches ✓ |
| `natality/README.md` | 146 | `183/183 and 35/35 are headline numbers, but ... known quirks (e.g., two null-record_weight survivor rows in 2014/2015)` | matches ✓ — soft-flag below |
| `natality/docs/ABOUT_THIS_RELEASE.md` | 80 | `35/35 active pass` | matches ✓ |
| `natality/docs/COMPARABILITY.md` | 367 | `V2 183/183 and V3 linked 35/35 external targets still pass` | matches ✓ |
| `natality/docs/VALIDATION.md` | 206 | `Results: 35/35 active targets pass.` | matches ✓ |
| `paper/README.md` | 18 | `One framing is stale; verify against ...` | matches ✓ (will be marked resolved) |
| `NEXT_STEPS.md` | 440 | `35/35 (or 33/35 + 2 docs diffs — verify; see Task 6)` | matches ✓ (will be resolved) |
| `README.md` (monorepo) | 17 | `33/35 byte-exact (2 cells differ by 1 record from NCHS upstream null-weight survivor records)` | already canonical — no edit ✓ |
| `paper/draft_v1_ipums_styled.md` | 93, `paper/draft_v2_hmd_styled.md` | 94 | `33 of 35 targets ... two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights` | already canonical — no edit ✓ |

- [x] Current values match task plan's assumed state ✓
- Plan assumes the validation file's authoritative state is "35 PASS rows under tolerance; 33 byte-exact + 2 differ by exactly 1 record" — verified by direct read.
- **Soft-flag (DECISION_LOG candidate):** `natality/README.md` line 146 mechanism wording ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism wording ("LATEREC edge cases") differ from the manuscript canonical mechanism wording ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are out of scope for Task 6 (the task is HEADLINE-count reconciliation); preserving each file's local mechanism wording. Mechanism reconciliation is a separate downstream task if pursued.

### Halt conditions tripped
None.

### Result
PROCEED.
