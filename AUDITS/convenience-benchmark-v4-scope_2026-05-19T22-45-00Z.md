# Adversarial audit — `convenience-benchmark-v4-scope` (commit `17814d2`)

- **Auditor**: fresh-eyes adversarial pass, no agent self-review
- **Scope**: commit `17814d2` only (tag `convenience-benchmark-v4-scope-complete`); 1 doc edit + 3 state-file appends
- **Agent claims under test**:
  - (a) the prepended blockquote note adds **no fabricated v4 wall-clock numbers** (L6-clean)
  - (b) every envelope fact in the note is **sourced**, not invented
  - (c) the convenience CSVs and the residents-only generator are **not linked-v4-dependent** and were correctly scoped OUT
  - (d) "Phase D step 4 routing" is **faithful** to C8.13's own PROPOSE-EDIT
- **High-risk classes**: L6 (invented number), L11 (stale roadmap claim), L7 (looks-right rubber-stamp), H8 (doc-data drift), §7-#17 (scope creep)

---

## Audit setup

**Commit footprint** (`git show 17814d2 --stat`):

```
 DECISION_LOG.md                                    | 18 +++++++
 ...ence-benchmark-v4-scope_2026-05-23T23-45-00Z.md | 55 +++++++++++++++++++
 STATUS.md                                          | 62 +++++++++++++++++++-
 docs/PIPELINE_TIMING_BENCHMARK.md                  |  7 +++
 4 files changed, 141 insertions(+), 1 deletion(-)
```

Exactly the four expected categories: one doc edit + three state files (DECISION_LOG / RECEIPT / STATUS). **Zero canonical-state mutation** (no parquet / schema / test-target / metadata-CSV / test / script touched). **§7-#17 scope-creep: clean.**

**The doc edit**: 7-line additive blockquote prepended at line 3 of `docs/PIPELINE_TIMING_BENCHMARK.md`. Doc-only `+7/-0`.

**Forbidden reads** (per audit charter, not consulted): the session RECEIPT; STATUS / DECISION_LOG / PRE_FLIGHT_LOG entries dated 2026-05-23T23:30:00Z or later (the `2026-05-23T23:45:00Z` STATUS section did appear incidentally in one grep result — not read substantively).

---

## CHECK 1 — Sourced facts (every envelope number must trace to a permitted source)

Every numerical / SHA claim in the note traced to the README "Four products at a glance" row and the permitted pre-session STATUS sections (C8.17 / C8.18):

| Note claim | Source | Match |
|---|---|---|
| Natality 201,161,456 / 57 yr / 1968-2024 | README L16 | ✓ |
| Linked v4 149,386,620 / 1983-2023 / 97 cols | README L17; STATUS L579 (2026-05-23T05:00:00Z C8.18 step 7); STATUS L595 | ✓ |
| Linked v4 SHA `f630d8cf…` | STATUS L656 (2026-05-23T02:00:00Z C8.18 DO step 6b) | ✓ |
| `.v3_baseline` SHA `9b828a4d…` | STATUS L656 ".v3_baseline preserved == `9b828a4d…`"; doc L159 H10 row | ✓ |
| Natality 1990-2024 / 138.8M (the C8.13-time historic figures) | doc L121 itself (the section the note marks as superseded) | ✓ |
| v3 linked 74.9M / 94 cols / 2005-2023 (historic) | doc L122 / L126 itself | ✓ |
| Fetal-death 1982-2024 / 2,427,233 / v2.4.0 | README L18 | ✓ |
| C8.17 envelope-grow date 2026-05-14 | STATUS L2351 (2026-05-14T10:30:00Z C8.17 DO step 4) | ✓ |
| C8.18 envelope-grow date 2026-05-23 | STATUS L656 (2026-05-23T02:00:00Z 6b) + L595 (T05:00:00Z step 7) | ✓ |

**Result: every envelope fact in the scope note is sourced. Nothing invented.**

---

## CHECK 2 — No fabricated wall-clock (L6 gate)

The agent claims the note adds no new times.

```
$ git diff 09bf813..17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md \
    | grep '^+' | grep -oE '[0-9]+\.[0-9]+ (s|min)|[0-9]+ min'
8.13 s
```

One apparent hit. Investigation: the `"8.13 s"` match is a **false positive on the token `"C8.13 scope"`** — the regex caught `8.13` + space + `s` (from "scope"). A second, stricter sweep with a unit-boundary anchor:

```
$ git diff 09bf813..17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md \
    | grep '^+' | grep -oE '[0-9][0-9.,]* ?(s|min|sec|hour|hr)\b'
(no output)
```

**Result: no fabricated wall-clock numbers were added.** The note's only quantitative content is row counts / column counts / SHAs / years — all sourced per CHECK 1. **L6 clean.**

The note's prose phrase "a multi-hour end-to-end re-run" is qualitative, not a measurement claim.

---

## CHECK 3 — Convenience CSV non-dependence (scope-out correctness)

The agent's scope-out classification:

### `fetal_death/live_births_by_year.csv`

```
year,live_births,source
1995,3899589,NVSR 57-08 Table B
1996,3891494,NVSR 57-08 Table B
...
2005,4138573,NVSR 73-09 / NCHS Vital Statistics
```

Each row carries an explicit NVSR source citation. **NVSR-transcribed static, not parquet-derived.** **Cannot be linked-v4-stale.** ✓

### `fetal_death/stratified_denominators.csv`

Schema: `data_year,maternal_age_band,maternal_race_bridged,hispanic_origin,live_births`.

Build script `shared/helpers/build_stratified_denominators.py`:
- L51: `JOINT_COVERAGE_YEARS: list[int] = list(range(1992, 2003)) + list(range(2005, 2023))`
- L86-93: reads from `natality_v2_harmonized_derived.parquet`, applies `residence_status != 4`, groups by age/race/hispanic
- **Reads the natality (non-linked) parquet only. Does not touch the linked parquet at all.**

C8.18 mutated **only** the linked-derived parquet (STATUS L656: *"the linked-derived gate SHA `9b828a4d…` → the v4 SHA, **the only canonical mutation in C8.18**"*). The natality parquet was untouched by C8.18. **Not linked-v4-dependent.** ✓

*Minor imprecision noted (not L-class)*: the CSV was originally built at Task 1 (2026-05-11T18:06:12Z) against natality **v2.7.0** sha `9f917a43…` (STATUS L7966 / L8696), not v3.0.0. The scope note's "natality-v3.0.0-derived" phrasing is loose. However, C8.17 step 6 preserved the entire 1990-2024 natality slice byte-exact post-cutover (STATUS L2065: *"1990-2024 slice BYTE-CLEAN — all 35 years content-EQUAL vs `.v28_baseline`"* via `pyarrow.Table.equals`). Since the CSV's input year-range (1992-2002 + 2005-2022) lies entirely within the byte-stable 1990-2024 slice, the CSV is **byte-reproducible** against the current v3.0.0 natality. The scope-out claim ("not linked-v4-derived") is correct as written; the "natality-v3.0.0-derived" framing is loose but defensible.

### `natality/scripts/06_convenience/write_residents_only.py`

L114, L123-124: outputs `natality_v3_linked_residents_only.parquet` to `output/convenience/` (and `natality/output/convenience/`).

```
$ git check-ignore -v natality/output/convenience/natality_v3_linked_residents_only.parquet \
    output/convenience/natality_v3_linked_residents_only.parquet
.gitignore:17:output/   natality/output/convenience/natality_v3_linked_residents_only.parquet
.gitignore:17:output/   output/convenience/natality_v3_linked_residents_only.parquet

$ git ls-files natality/output/convenience/ output/convenience/
(no output)
```

**Both output paths are gitignored; no `*_residents_only.parquet` is tracked.** ✓

The `v3_linked` filename token is a **schema-family tag**, not a version claim — the script adapts to whatever input parquet sits at the `--v3-in` path. Running it today against the current linked-v4 derived parquet would produce a (gitignored) reproducible v4-content output with the historic filename. **No stale linked-v3 data is committed.** ✓

**CHECK 3 conclusion**: all three convenience artifacts are correctly scoped OUT of the linked-v4 staleness flag. None depend on the linked-v4 parquet in a way that survives in committed state.

---

## CHECK 4 — Phase D step 4 routing faithfulness

The agent claims: *"the manuscript timing-claim reconciliation is already routed to Phase D step 4 (the C8.13 fetal-death PROPOSE-EDIT, §below); the v4 natality+linked re-measure belongs to that same Phase-D post-final-rebuild pass."*

The pre-existing C8.13 "## PROPOSE-EDIT to Phase D step 4" section (`docs/PIPELINE_TIMING_BENCHMARK.md` L92-113) was read in full. Its content:

- L94-96: *"Per the C8.12 RECEIPT precedent, the actual manuscript line edit bundles to Phase D step 4 (manuscript re-pass). This RECEIPT documents the proposal; no in-session manuscript mutation."*
- L100-103: recommends the fetal-death `"approximately six minutes"` → `"approximately five minutes"` edit
- L106: *"The natality clause is unchanged per §below."*
- L146 (downstream Reconciliation): *"No edit recommended for the natality clause of `paper/draft_v2_hmd_styled.md:68`."* (because at C8.13 measurement-time, natality+linked measured 88.45 min vs ~90 min claim = -1.72% drift = PASS).

**Routing-faithfulness verdict**: the scope note correctly attributes only the **fetal-death** PROPOSE-EDIT to C8.13's existing D.4 routing ("the C8.13 fetal-death PROPOSE-EDIT, §below"). It then makes a separate, new claim — that the v4 natality+linked re-measure *belongs to that same Phase-D pass* — without falsely claiming C8.13 already routed it. **Honest framing, not overstated.** ✓

---

## CHECK 5 — C8.13 natality+linked measurement was pre-C8.17 / pre-C8.18

The note's staleness claim depends on C8.13's measurement having pre-dated both envelope changes.

- doc L11-12: *"captured at C8.13 F.5 DO (2026-05-13)"*
- doc L54 environment table: *"Date | 2026-05-13"*
- doc L115 section header: *"Natality + linked pipeline (1990-2024 natality, 2005-2023 linked)"*
- doc L121: *"Parse natality 1990-2024 (35 years, 138.8M records)"*
- doc L122: *"Parse linked 2005-2023 (19 cohort years, 74.9M records)"*

Envelope-change dates:

- C8.17 DO step 4 = 2026-05-14T10:30:00Z (STATUS L2351) — *next day after C8.13 measurement*
- C8.17 DO step 6 (full v3.0.0 cutover; 138.8M → 201M) = 2026-05-16T08:00:00Z (STATUS L2065)
- C8.18 DO step 6b (linked v4 cutover; 74.9M → 149M) = 2026-05-23T02:00:00Z (STATUS L656)

**C8.13's measurement (2026-05-13, against 138.8M natality + 74.9M linked) is genuinely pre-C8.17 and pre-C8.18.** The note's staleness framing is empirically correct. ✓

---

## CHECK 6 — Post-note internal contradictions

Walked the doc post-edit for self-consistency between the prepended note and the remaining content:

- L40-42 *"All 4 verified byte-exact (see §H10 below)"* — true at the C8.13 point-in-time; the note's "**point-in-time C8.13 measurement**" framing covers this.
- L142-146 *"Measured: 88.45 min ... PASS (well within ±10%) ... No edit recommended for the natality clause"* — this verdict is **downstream of the now-superseded wall-clock numbers**. A v4 re-measure on the 350M-record envelope (201M natality + 149M linked, vs the historic 138.8M + 74.9M = 213.7M) could plausibly push the natality+linked total over the ±10% band and flip the verdict.
- L154-159 H10 table row 4 (linked v3 SHA `9b828a4d…`) — explicitly marked superseded by the note.

**Minor observation (not L-class)**: the note marks "the natality+linked **wall-clock numbers** + the §H10 linked row" as superseded — by transitivity this also covers the L146 PASS verdict (since the verdict is derived from the now-superseded measurement), but the note does **not separately call out** that the "no edit recommended for the natality clause" verdict is itself contingent and may flip in the Phase-D re-measure. A careful reader gets there by inference; a casual one might not.

**This is an under-spelled-out implication, not a contradiction.** The note's blanket "superseded point-in-time figures" framing applies to the entire natality+linked section including its verdict.

---

## Verdict

**No L-class findings.**

| Check | Class | Status |
|---|---|---|
| 1 — Sourced facts | L6 / L11 | ✓ all envelope facts trace to README + permitted STATUS |
| 2 — No fabricated wall-clock | L6 | ✓ zero new time numbers; one regex false-positive on "C8.13 scope" |
| 3 — Convenience-CSV scope-out | L11 / H8 | ✓ none of the three artifacts depend on linked-v4 in committed state |
| 4 — D.4 routing faithfulness | L7 / L11 | ✓ note correctly attributes only fetal-death edit to C8.13's routing; v4 natality re-measure framed as a new D.4-class claim, not an overstated C8.13 claim |
| 5 — C8.13 measurement was pre-envelope-grow | L11 | ✓ 2026-05-13 measurement genuinely pre-dates 2026-05-14 (C8.17) and 2026-05-23 (C8.18) |
| 6 — Internal consistency | H8 | ✓ no contradictions the note's "superseded" framing doesn't already cover |
| §7-#17 scope creep | §7-#17 | ✓ exactly 1 doc + 3 state files; zero canonical-state mutation |

### Two minor non-L observations (for any future tightening pass)

1. **L146 verdict implicitness.** The doc retains *"No edit recommended for the natality clause"* (L146). The scope note's blanket "natality+linked wall-clock numbers + §H10 linked row are superseded" framing transitively covers this verdict, but does not call it out separately. A more explicit sentence in the note — e.g., *"the L146 'no edit recommended' verdict for the natality clause is downstream of the superseded numbers and may flip in the Phase-D v4 re-measure"* — would close the implication gap.
2. **build_stratified_denominators.py docstring lag.** The helper's module docstring (L5) still references *"natality v2.7.0 full harmonized parquet"*, while the canonical natality is now v3.0.0. This is a separate documentation staleness in a different file; **not in scope** for the convenience-benchmark-v4-scope commit under audit and not a finding against the commit. Flagged here only for situational awareness.

### What was actually verified (anti-cheerleading record)

Every check above rests on a command actually run or a file actually read:

- `git show 17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md` (full diff)
- `git show 17814d2 --stat` (footprint)
- `git diff 09bf813..17814d2 -- docs/PIPELINE_TIMING_BENCHMARK.md | grep '^+' | grep -oE ...` (two regexes for time patterns)
- `git check-ignore -v` for both convenience-output paths
- `git ls-files natality/output/convenience/ output/convenience/`
- `git log --oneline -5 -- ...` for the four scoped files
- Read: full post-edit `docs/PIPELINE_TIMING_BENCHMARK.md` (216 lines), `README.md` (111 lines), `fetal_death/live_births_by_year.csv` (head), `fetal_death/stratified_denominators.csv` (head), `natality/scripts/06_convenience/write_residents_only.py` (full), `shared/helpers/build_stratified_denominators.py` (full)
- `grep -n` over STATUS.md for permitted-section anchors: 2026-05-23T02:00:00Z (C8.18 6b), 2026-05-14T (C8.17), 2026-05-13T23:00:00Z (C8.13), and the C8.17 step 6 v3.0.0 cutover entry at 2026-05-16T08:00:00Z

The commit's four agent-claimed properties (no fabricated wall-clock; every envelope fact sourced; convenience artifacts correctly scoped OUT; D.4 routing faithful to C8.13) all hold under independent verification.
