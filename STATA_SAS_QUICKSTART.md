# Loading HVS in Stata and SAS

A short pointer for Stata and SAS users. The U.S. Harmonized Vital Statistics
(HVS) data ship as **Apache Parquet** files. The **recommended, version-proof
path for every Stata and SAS release is to convert Parquet → CSV once, then
load the CSV.** Native/direct Parquet options exist for some builds and are
documented at the end with their exact requirements.

> This is a *pointer* file, not an executable worked example. The build
> machine has no Stata or SAS license, so `.do`/`.sas` scripts cannot be
> run-verified here; per `EXPLORATION_REPORT.md` §C.3 full worked examples are
> deferred. Every command below is quoted from official vendor documentation
> (see **References**) — not invented.

## The data files

| Product | Parquet (unpacked Zenodo-deposit layout) |
|---|---|
| Natality | `natality_v2_harmonized_derived.parquet` |
| Linked birth–infant death | `natality_v3_linked_harmonized_derived.parquet` |
| Fetal death | `fetal_death_derived.parquet` |
| Matched multiples | `matched_multiples_harmonized.parquet` |

The natality (~201M rows) and linked (~149M rows) files are large; a full CSV
export is tens of GB. Prefer exporting a **canonical-filtered or pre-aggregated
subset** — the shipped [`views.sql`](views.sql) already defines the
canonical-filter views, so you can export exactly the rows you need.

## Recommended path — convert Parquet → CSV, then load

### Step 1 — Parquet → CSV (pick one; no Stata/SAS dependency)

**Option A — DuckDB CLI (no Python).** DuckDB is a single self-contained
binary. Using the shipped `views.sql` (applies each product's canonical filter)
or a direct read:

```sql
-- canonical-filtered subset (recommended for the large files)
duckdb hvs.duckdb < views.sql
COPY (SELECT * FROM fetal_death_canonical) TO 'fetal_death.csv' (HEADER, DELIMITER ',');

-- or a whole file directly, no views.sql needed
COPY (SELECT * FROM read_parquet('fetal_death_derived.parquet'))
  TO 'fetal_death.csv' (HEADER, DELIMITER ',');
```

**Option B — Python (uses the shipped quickstart).** Any environment with
`pandas` + `pyarrow` (see [`fetal_death/quickstart.py`](fetal_death/quickstart.py)):

```python
import pandas as pd
df = pd.read_parquet("fetal_death_derived.parquet")
df.to_csv("fetal_death.csv", index=False)
```

### Step 2 — load the CSV

**Stata** (base `import delimited`; every Stata release ≥13):

```stata
import delimited "fetal_death.csv", varnames(1) clear
```

**SAS** (base `PROC IMPORT`; SAS 9.4 and later):

```sas
proc import datafile="fetal_death.csv" out=work.fetal_death dbms=csv replace;
    getnames=yes;
run;
```

Apply the canonical analytic filter if you did not export a pre-filtered view:
`tabulation_flag == 2 AND residence_status != 4` for fetal death;
`residence_status != 4` for natality and linked. See
[`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md) for the per-product filters
and joint-use rate mechanics.

## Direct / native Parquet (build-dependent)

These avoid the CSV step but each has a hard requirement — confirm yours before
relying on them; otherwise use the CSV path above.

- **Stata — native `import parquet`:** available **only in StataNow** (the
  subscription update channel), not in standard Stata 17/18. If you have
  StataNow: `import parquet "fetal_death_derived.parquet", clear`. See the
  official manual entry [`[D] import parquet`](https://www.stata.com/manuals/dimportparquet.pdf).
- **Stata — community package (Unix/Linux only):** the `parquet` package
  (Apache-Arrow plugin) reads/writes Parquet on Stata for Unix. Install and
  exact syntax: <https://github.com/mcaceresb/stata-parquet>.
- **SAS 9.4:** **no native Parquet read** (the Parquet LIBNAME engine is not
  supported in SAS 9). Use the CSV path above.
- **SAS Viya:** reads Parquet through the **ORC/Parquet LIBNAME engine**
  (assign a `LIBNAME` to the Parquet directory — *not* `PROC IMPORT
  DBMS=PARQUET`). See [*SAS Viya LIBNAME Engines for ORC and
  Parquet*](https://documentation.sas.com/doc/en/pgmsascdc/v_046/enghdff/titlepage.htm).

## References (verified official documentation)

- DuckDB — CSV export (`COPY … TO … (HEADER, DELIMITER ',')`):
  <https://duckdb.org/docs/current/guides/file_formats/csv_export.html>
- Stata — `[D] import` (overview; includes `import delimited`):
  <https://www.stata.com/manuals/dimport.pdf>
- Stata — `[D] import parquet` (StataNow):
  <https://www.stata.com/manuals/dimportparquet.pdf> ·
  <https://www.stata.com/statanow/import-data-parquet-files/>
- SAS — PROC IMPORT Statement:
  <https://documentation.sas.com/doc/en/vdmmlcdc/8.1/acpcref/p0jf3o1i67m044n1j0kz51ifhpvs.htm>
- SAS Viya — LIBNAME Engines for ORC and Parquet:
  <https://documentation.sas.com/doc/en/pgmsascdc/v_046/enghdff/titlepage.htm>

See also: [`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md) (cross-language
access: R, DuckDB, Stata, SAS), [`views.sql`](views.sql) (canonical-filter
DuckDB views), and the per-product `quickstart.py` / `quickstart.R`.
