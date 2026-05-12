# PRE_FLIGHT_LOG

> **Append-only.** Before every task's DO phase, the LLM appends a PRE-FLIGHT checklist here per the template in `NEXT_STEPS.md` §5.
>
> **Back-fills are forbidden** (per §8 matrix row L10). The PRE-FLIGHT entry's timestamp must precede the first DO commit for that task. If a back-fill is detected (e.g., during receipt drafting), file an L10 entry forensically and remediate via §11 before doing further DO action on that task.
>
> See `NEXT_STEPS.md` §5 for the template.

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
