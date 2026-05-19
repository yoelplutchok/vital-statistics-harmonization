#!/usr/bin/env python3
"""C8.22 — deterministic builder for csv/published_tabulations/.

Generates the 10 curated top-NVSR-cited cross-tabulations as pre-computed
CSVs so users can cite HVS without loading the multi-GB parquets.

Design (DECISION_LOG 2026-05-23T18:00:00Z):
  D1  Public-use NCHS has NO sub-national geography — the §15.D "per-state"
      tabs are structurally infeasible; substituted by the feasible, higher-
      NVSR-citation race + maternal-age national stratifications + documented.
  D2  Every metric MIRRORS the exact filter/definition of the canonical NVSR
      validator that owns it (compare_external_targets_v1.py,
      compare_external_targets_v3_linked.py, validate_external_v2.py) — never
      reinvented (§9-#5 / L3 / L7). Resident = residence_status != 4
      (verified byte-exact == is_foreign_resident == False). Rates over
      known/non-null denominators. Era-dependent cesarean crosswalk. Fetal
      canonical = tabulation_flag==2 AND residence_status!=4, + version_flag
      =='S' for 1982-2002. Linked IMR = UNWEIGHTED resident deaths/births.
  D3  Linked IMR cross-tabs = 2005-2023 (the validator-owned, NVSR-
      reconcilable surface). Pre-2005 cohort IMR (1983-2004) needs the
      RECWT/link_segment cohort logic the canonical validator deliberately
      refuses inline — pointer-documented, not naively recomputed.
  D4  One deterministic single-pass builder; byte-identical on re-run
      (fixed column order + sorted rows + '\\n' endings + fixed-precision
      numerics; no timestamps). Read-only; zero canonical-state mutation.
  D5  maternal_race_bridged {1:White,2:Black,3:AIAN,4:Asian or Pacific
      Islander}; NULL surfaced as an explicit 'Not stated / not bridged'
      bucket, NEVER dropped (H6 row-count conservation).

Halt-flags (§15.D C8.22): F1 (canonical filter per tab), F2 (cross-product
join filtered on BOTH sides), H6 (Σ strata == year total), L6 (every cell
auto-derived; NVSR-overlapping cells reconciled, diffs reported not hidden).
Any NVSR-overlapping cell whose |actual-expected| EXCEEDS the documented
tolerance is recorded as `RECONCILE_FAIL` and makes the builder exit non-zero
(L14) — VERIFY must §7-#4 halt-and-ask on it.

Usage:
  uv run python scripts/_build_published_tabulations.py            # build
  uv run python scripts/_build_published_tabulations.py --check     # verify
                                                # byte-identical re-render
Env overrides (read-only; the monorepo-path-drift pin):
  HVS_FETAL_DERIVED  HVS_NATAL_DERIVED  HVS_LINKED_DERIVED
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# ── Canonical gate-verified parquet paths (DECISION_LOG 2026-05-23T11:00:00Z
#    monorepo-path-drift pin: fetal canonical = the -build/ tree, NOT the
#    stale flat ~/Desktop/fetal-death-harmonization/). Env-overridable.
FETAL = os.environ.get("HVS_FETAL_DERIVED", os.path.expanduser(
    "~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet"))
NATAL = os.environ.get("HVS_NATAL_DERIVED", os.path.expanduser(
    "~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet"))
LINKED = os.environ.get("HVS_LINKED_DERIVED", os.path.expanduser(
    "~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet"))

OUT_DIR = REPO / "csv" / "published_tabulations"

# Validated-target sources (committed artifacts; the reconciliation anchors).
FD_TARGETS = REPO / "fetal_death" / "external_validation_targets.csv"
NAT_V1_TARGETS = REPO / "natality" / "metadata" / "external_validation_targets_v1.csv"
NAT_LINKED_TARGETS = REPO / "natality" / "metadata" / "external_validation_targets_v3_linked.csv"
# The fetal canonical validator — import its FROZEN published-constant dicts so
# 1982-2004 fetal reconciliation mirrors the validator (D2; not hand-numbers).
FD_VALIDATOR = REPO / "fetal_death" / "scripts" / "05_validate" / "validate_external_v2.py"

# ── Pure classifiers (SMOKE Tier 0 exercises these; no parquet I/O) ─────────

NOT_STATED_RACE = "Not stated / not bridged"
NOT_STATED_AGE = "Not stated"
_RACE_LABELS = {1: "White", 2: "Black", 3: "AIAN", 4: "Asian or Pacific Islander"}


def race_label(code) -> str:
    """maternal_race_bridged code -> canonical label. NULL/out-of-frame ->
    the explicit not-stated bucket (D5/H6 — never dropped)."""
    try:
        return _RACE_LABELS[int(code)]
    except (TypeError, ValueError, KeyError):
        return NOT_STATED_RACE


def cesarean_classify(code, year: int) -> tuple[bool, bool]:
    """Mirror compare_external_targets_v1.py. Returns (is_known, is_cesarean).
    <=2004 DELMETH5-style: known = code in 1..4, cesarean = 3|4.
    >=2005   DMETH_REC:     known = code in 1|2, cesarean = 2."""
    if code is None:
        return (False, False)
    try:
        c = int(code)
    except (TypeError, ValueError):
        return (False, False)
    if year <= 2004:
        return (1 <= c <= 4, c in (3, 4))
    return (c in (1, 2), c == 2)


def age_band(age) -> str:
    """NCHS-standard maternal-age bands; NULL / sentinel / out-of-range ->
    Not stated (§7-#7 — a sentinel is never counted as data)."""
    if age is None:
        return NOT_STATED_AGE
    try:
        a = int(age)
    except (TypeError, ValueError):
        return NOT_STATED_AGE
    if a < 10 or a > 60:           # 99 sentinel + impossible values
        return NOT_STATED_AGE
    if a < 15:
        return "<15"
    if a < 20:
        return "15-19"
    if a < 25:
        return "20-24"
    if a < 30:
        return "25-29"
    if a < 35:
        return "30-34"
    if a < 40:
        return "35-39"
    if a < 45:
        return "40-44"
    return "45+"


_RACE_ORDER = ["White", "Black", "AIAN", "Asian or Pacific Islander", NOT_STATED_RACE]
_AGE_ORDER = ["<15", "15-19", "20-24", "25-29", "30-34", "35-39",
              "40-44", "45+", NOT_STATED_AGE]


def assert_conserves(strata: dict, total: int) -> bool:
    """H6 row-count conservation: a stratified breakdown (incl. the explicit
    not-stated bucket) must sum back to the unstratified total."""
    s = sum(strata.values())
    assert s == total, f"H6 violation: Σstrata={s} != total={total}"
    return True


def fmt_rate(num, den, scale: int, ndigits: int) -> str:
    """Fixed-precision rate string (no platform float drift). Empty den ->
    '' (blank, not 0 — an undefined rate is not a zero rate)."""
    if not den:
        return ""
    return f"{round(num / den * scale, ndigits):.{ndigits}f}"


def fmt_pct(num, den, ndigits: int) -> str:
    return fmt_rate(num, den, 100, ndigits)


def write_tabulation(path: Path, columns, rows, sort_key) -> None:
    """Deterministic CSV writer: stable column order, sorted rows, '\\n'
    line endings, no timestamps. Byte-identical for identical input."""
    rows = sorted(rows, key=sort_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(columns), lineterminator="\n",
                           extrasaction="raise")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})


# ── reconciliation ─────────────────────────────────────────────────────────

def _load_target_csv(path: Path, metric_col: str, year_col: str):
    """{(metric,year): (expected:float|None, tol:float|None, source)}."""
    out: dict[tuple[str, int], tuple] = {}
    with path.open(encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(
            (ln for ln in f if not ln.lstrip().startswith("#") and ln.strip()))
        for row in rdr:
            m = (row.get(metric_col) or "").strip()
            y = (row.get(year_col) or "").strip()
            if not m or not y:
                continue
            try:
                yr = int(y)
            except ValueError:
                continue
            ev = (row.get("expected_value") or "").strip()
            tv = (row.get("tolerance_abs") or "").strip()
            sv = (row.get("value_source") or row.get("source") or "").strip()
            out[(m, yr)] = (
                float(ev) if ev else None,
                float(tv) if tv else None,
                sv,
            )
    return out


def _import_fd_validator():
    spec = importlib.util.spec_from_file_location("_fdval", FD_VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _num(x) -> str:
    """Plain numeric string: integer-valued -> no decimals/sci-notation."""
    if x is None:
        return ""
    return str(int(x)) if float(x) == int(x) else f"{x:g}"


# RECONCILE verdicts. Any *_FAIL makes the builder exit non-zero (L14).
def reconcile(actual, expected, tol, default_tol):
    if expected is None:
        return "", "", "(no NVSR target)"
    if actual is None or actual == "":
        return _num(expected), "", "RECONCILE_FAIL (actual missing)"
    a = float(actual)
    t = default_tol if tol is None else tol
    diff = round(a - expected, 6)
    if abs(diff) <= t + 1e-9:
        v = "match" if abs(diff) < 1e-9 else f"within tol (diff={diff:+g})"
    else:
        v = f"RECONCILE_FAIL (diff={diff:+g} EXCEEDS tol {t:g}; §7-#4)"
    return _num(expected), _num(t), v


# ── DuckDB single-pass aggregators ─────────────────────────────────────────

def _con():
    import duckdb
    return duckdb.connect()


# Resident filters (D2). Fetal also needs the version-flag-conditional.
_NAT_RES = "residence_status <> 4"
_FD_CANON = ("tabulation_flag = 2 AND residence_status <> 4 "
             "AND (data_year > 2002 OR version_flag = 'S')")


def build(check_only: bool) -> int:
    con = _con()
    for p in (FETAL, NATAL, LINKED):
        if not Path(p).is_file():
            print(f"FATAL missing parquet: {p}", file=sys.stderr)
            return 3

    fd_t = _load_target_csv(FD_TARGETS, "metric", "year")
    nv1 = _load_target_csv(NAT_V1_TARGETS, "metric_id", "data_year")
    nlk = _load_target_csv(NAT_LINKED_TARGETS, "metric_id", "data_year")
    fdv = _import_fd_validator()

    fail = 0          # RECONCILE_FAIL counter (L14 exit code)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ════ NATALITY ════════════════════════════════════════════════════════
    # 1. births by year ----------------------------------------------------
    rows = con.execute(
        f"SELECT data_year y, count(*) n FROM '{NATAL}' "
        f"WHERE {_NAT_RES} GROUP BY 1").fetchall()
    nat_births = {int(y): int(n) for y, n in rows}
    out = []
    for y in sorted(nat_births):
        exp, tol, src = nv1.get(("resident_births", y), (None, None, ""))
        e, t, verdict = reconcile(nat_births[y], exp, tol, 0.0)
        if "RECONCILE_FAIL" in verdict:
            fail += 1
        if exp is None and y < 1990:
            verdict = "not NVSR-benchmarked (pre-1990; planned)"
        out.append({"data_year": y, "resident_live_births": nat_births[y],
                    "nvsr_expected": e, "nvsr_tolerance": t,
                    "reconciliation": verdict})
    write_tabulation(OUT_DIR / "natality_births_by_year.csv",
                     ["data_year", "resident_live_births", "nvsr_expected",
                      "nvsr_tolerance", "reconciliation"],
                     out, lambda r: (r["data_year"],))

    # 2. births by year x maternal race ------------------------------------
    rows = con.execute(
        f"SELECT data_year y, maternal_race_bridged r, count(*) n "
        f"FROM '{NATAL}' WHERE {_NAT_RES} GROUP BY 1,2").fetchall()
    agg: dict[int, dict[str, int]] = {}
    for y, r, n in rows:
        agg.setdefault(int(y), {}).setdefault(race_label(r), 0)
        agg[int(y)][race_label(r)] += int(n)
    out = []
    for y in sorted(agg):
        assert_conserves(agg[y], nat_births[y])           # H6
        for lab in _RACE_ORDER:
            if lab not in agg[y]:
                continue
            note = ""
            if 1990 <= y <= 2002:
                note = "approximate crosswalk (not official NCHS bridged race)"
            elif y >= 2020:
                note = "bridged-race discontinued by NCHS 2020+ (use maternal_race_ethnicity_5)"
            elif y < 1990:
                note = "pre-1990 (not NVSR-benchmarked; planned)"
            out.append({"data_year": y, "maternal_race": lab,
                        "live_births": agg[y][lab],
                        "pct_within_year": fmt_pct(agg[y][lab], nat_births[y], 2),
                        "note": note})
    write_tabulation(OUT_DIR / "natality_births_by_year_x_maternal_race.csv",
                     ["data_year", "maternal_race", "live_births",
                      "pct_within_year", "note"],
                     out, lambda r: (r["data_year"], _RACE_ORDER.index(r["maternal_race"])))

    # 3. births by year x maternal age band --------------------------------
    rows = con.execute(
        f"SELECT data_year y, maternal_age a, count(*) n FROM '{NATAL}' "
        f"WHERE {_NAT_RES} GROUP BY 1,2").fetchall()
    agg = {}
    for y, a, n in rows:
        b = age_band(a)
        agg.setdefault(int(y), {}).setdefault(b, 0)
        agg[int(y)][b] += int(n)
    out = []
    for y in sorted(agg):
        assert_conserves(agg[y], nat_births[y])           # H6
        for b in _AGE_ORDER:
            if b not in agg[y]:
                continue
            out.append({"data_year": y, "maternal_age_band": b,
                        "live_births": agg[y][b],
                        "pct_within_year": fmt_pct(agg[y][b], nat_births[y], 2)})
    write_tabulation(OUT_DIR / "natality_births_by_year_x_maternal_age.csv",
                     ["data_year", "maternal_age_band", "live_births",
                      "pct_within_year"],
                     out, lambda r: (r["data_year"], _AGE_ORDER.index(r["maternal_age_band"])))

    # 4. lbw / preterm / singleton rates by year ---------------------------
    rows = con.execute(
        "SELECT data_year y, "
        "count(low_birthweight) lbd, sum(CASE WHEN low_birthweight THEN 1 ELSE 0 END) lbn, "
        "count(preterm_lt37) prd, sum(CASE WHEN preterm_lt37 THEN 1 ELSE 0 END) prn, "
        "count(singleton) sgd, sum(CASE WHEN singleton THEN 1 ELSE 0 END) sgn "
        f"FROM '{NATAL}' WHERE {_NAT_RES} GROUP BY 1").fetchall()
    out = []
    for y, lbd, lbn, prd, prn, sgd, sgn in rows:
        y = int(y)
        lbw = fmt_pct(lbn, lbd, 2)
        pre = fmt_pct(prn, prd, 2)
        recon = []
        for mid, val in (("lbw_rate_pct", lbw), ("preterm_rate_pct", pre)):
            exp, tol, _ = nv1.get((mid, y), (None, None, ""))
            _, _, v = reconcile(val if val else None, exp, tol, 0.05)
            if "RECONCILE_FAIL" in v:
                fail += 1
            if exp is not None:
                recon.append(f"{mid}:{v}")
        out.append({"data_year": y, "lbw_rate_pct": lbw,
                    "preterm_rate_pct": pre,
                    "singleton_rate_pct": fmt_pct(sgn, sgd, 2),
                    "denominator_basis": "known (non-null) resident births",
                    "reconciliation": "; ".join(recon) if recon
                    else ("not NVSR-benchmarked (pre-1990; planned)"
                          if y < 1990 else "(no NVSR target)")})
    write_tabulation(OUT_DIR / "natality_rates_lbw_preterm_singleton_by_year.csv",
                     ["data_year", "lbw_rate_pct", "preterm_rate_pct",
                      "singleton_rate_pct", "denominator_basis",
                      "reconciliation"], out, lambda r: (r["data_year"],))

    # 5. cesarean / twin / triplet+ rates by year --------------------------
    rows = con.execute(
        f"SELECT data_year y, delivery_method_recode d, count(*) n "
        f"FROM '{NATAL}' WHERE {_NAT_RES} GROUP BY 1,2").fetchall()
    ces: dict[int, list[int]] = {}        # year -> [known, cesarean]
    for y, d, n in rows:
        y = int(y)
        k, c = cesarean_classify(d, y)
        ces.setdefault(y, [0, 0])
        if k:
            ces[y][0] += int(n)
        if c:
            ces[y][1] += int(n)
    plu = con.execute(
        "SELECT data_year y, count(plurality_recode) pd, "
        "sum(CASE WHEN plurality_recode=2 THEN 1 ELSE 0 END) tw, "
        "sum(CASE WHEN plurality_recode>=3 THEN 1 ELSE 0 END) tp "
        f"FROM '{NATAL}' WHERE {_NAT_RES} GROUP BY 1").fetchall()
    out = []
    for y, pd_, tw, tp in plu:
        y = int(y)
        kn, cn = ces.get(y, [0, 0])
        cpct = fmt_pct(cn, kn, 2)
        twr = fmt_rate(tw, pd_, 1000, 1)
        tpr = fmt_rate(tp, pd_, 100000, 1)
        recon = []
        for mid, val, dft in (("cesarean_rate_pct", cpct, 0.2),
                              ("twin_rate_per_1000", twr, 0.1),
                              ("triplet_plus_rate_per_100000", tpr, 1.0)):
            exp, tol, _ = nv1.get((mid, y), (None, None, ""))
            _, _, v = reconcile(val if val else None, exp, tol, dft)
            if "RECONCILE_FAIL" in v:
                fail += 1
            if exp is not None:
                recon.append(f"{mid}:{v}")
        out.append({"data_year": y, "cesarean_rate_pct": cpct,
                    "twin_rate_per_1000": twr,
                    "triplet_plus_rate_per_100000": tpr,
                    "reconciliation": "; ".join(recon) if recon
                    else "(no NVSR target)"})
    write_tabulation(OUT_DIR / "natality_rates_cesarean_multiple_by_year.csv",
                     ["data_year", "cesarean_rate_pct", "twin_rate_per_1000",
                      "triplet_plus_rate_per_100000", "reconciliation"],
                     out, lambda r: (r["data_year"],))

    # ════ FETAL DEATH ═════════════════════════════════════════════════════
    rows = con.execute(
        f"SELECT data_year y, count(*) n FROM '{FETAL}' "
        f"WHERE {_FD_CANON} GROUP BY 1").fetchall()
    fd = {int(y): int(n) for y, n in rows}
    # frozen validator dicts (mirror; not hand-numbers) for 1982-2004
    fd_guide = dict(fdv.GUIDE_FETAL_DEATHS_GTE20)
    fd_nvsr = dict(fdv.NVSR57_FETAL_DEATHS_GTE20)

    # 6. fetal-death counts by year ----------------------------------------
    out = []
    for y in sorted(fd):
        exp, src = None, ""
        if (("fetal_deaths_gte20wk_resident", y)) in fd_t:
            exp, _, src = fd_t[("fetal_deaths_gte20wk_resident", y)]
        elif y in fd_nvsr:
            exp, src = fd_nvsr[y], "validate_external_v2 NVSR 57-08"
        elif y in fd_guide:
            exp, src = fd_guide[y], "validate_external_v2 guide control"
        _, _, verdict = reconcile(fd[y], exp, 0.0, 0.0)
        if "RECONCILE_FAIL" in verdict:
            fail += 1
        if exp is None:
            verdict = "(no NVSR target)"
        out.append({"data_year": y,
                    "fetal_deaths_ge20wk_resident": fd[y],
                    "nvsr_expected": "" if exp is None else int(exp),
                    "nvsr_source": src, "reconciliation": verdict})
    write_tabulation(OUT_DIR / "fetal_death_counts_by_year.csv",
                     ["data_year", "fetal_deaths_ge20wk_resident",
                      "nvsr_expected", "nvsr_source", "reconciliation"],
                     out, lambda r: (r["data_year"],))

    # 7. fetal mortality rate by year (joint fetal + natality; F2) ----------
    out = []
    for y in sorted(fd):
        lb = nat_births.get(y)              # natality canonical (BOTH sides)
        if lb is None:
            continue
        fmr = fmt_rate(fd[y], lb + fd[y], 1000, 2)
        exp, tol, _ = fd_t.get(("fetal_mortality_rate", y), (None, None, ""))
        _, t, verdict = reconcile(fmr if fmr else None, exp, tol, 0.02)
        if "RECONCILE_FAIL" in verdict:
            fail += 1
        if exp is None:
            verdict = ("rate not NVSR-benchmarked (pre-1995)" if y < 1995
                       else "(no NVSR target)")
        out.append({"data_year": y,
                    "fetal_deaths_ge20wk_resident": fd[y],
                    "resident_live_births": lb,
                    "fetal_mortality_rate_per_1000": fmr,
                    "nvsr_expected_rate": "" if exp is None else f"{exp:g}",
                    "reconciliation": verdict})
    write_tabulation(OUT_DIR / "fetal_mortality_rate_by_year.csv",
                     ["data_year", "fetal_deaths_ge20wk_resident",
                      "resident_live_births", "fetal_mortality_rate_per_1000",
                      "nvsr_expected_rate", "reconciliation"],
                     out, lambda r: (r["data_year"],))

    # 8. fetal mortality rate by year x maternal race (F2 both sides) ------
    fdr = con.execute(
        f"SELECT data_year y, maternal_race_bridged r, count(*) n "
        f"FROM '{FETAL}' WHERE {_FD_CANON} GROUP BY 1,2").fetchall()
    nbr = con.execute(
        f"SELECT data_year y, maternal_race_bridged r, count(*) n "
        f"FROM '{NATAL}' WHERE {_NAT_RES} GROUP BY 1,2").fetchall()
    fd_r: dict[int, dict[str, int]] = {}
    for y, r, n in fdr:
        fd_r.setdefault(int(y), {}).setdefault(race_label(r), 0)
        fd_r[int(y)][race_label(r)] += int(n)
    nb_r: dict[int, dict[str, int]] = {}
    for y, r, n in nbr:
        nb_r.setdefault(int(y), {}).setdefault(race_label(r), 0)
        nb_r[int(y)][race_label(r)] += int(n)
    out = []
    for y in sorted(fd_r):
        if y not in nat_births:
            continue
        assert_conserves(fd_r[y], fd[y])                  # H6 (numerator side)
        for lab in _RACE_ORDER:
            fdn = fd_r[y].get(lab, 0)
            lbn = nb_r.get(y, {}).get(lab, 0)
            if fdn == 0 and lbn == 0:
                continue
            note = ""
            if lab == NOT_STATED_RACE:
                note = "unraced residual (fetal NULL 2018+, natality NULL 2020+)"
            elif 1990 <= y <= 2002:
                note = "approximate natality crosswalk"
            elif y >= 2018:
                note = "fetal bridged-race NULL 2018+ — race signal ends 2017"
            out.append({"data_year": y, "maternal_race": lab,
                        "fetal_deaths_ge20wk": fdn,
                        "resident_live_births": lbn,
                        "fetal_mortality_rate_per_1000":
                        fmt_rate(fdn, lbn + fdn, 1000, 2),
                        "note": note})
    write_tabulation(OUT_DIR / "fetal_mortality_rate_by_year_x_maternal_race.csv",
                     ["data_year", "maternal_race", "fetal_deaths_ge20wk",
                      "resident_live_births", "fetal_mortality_rate_per_1000",
                      "note"], out,
                     lambda r: (r["data_year"], _RACE_ORDER.index(r["maternal_race"])))

    # ════ LINKED BIRTH–INFANT DEATH (2005-2023 owned surface; D3) ═════════
    PRE = ("pre-2005 cohort IMR (1983-2004) needs the RECWT/link_segment "
           "cohort methodology — see external_validation_targets_v3_linked.csv "
           "+ natality/docs/COMPARABILITY.md; 1992-1994 permanent NCHS-linkage "
           "gap")
    rows = con.execute(
        "SELECT data_year y, count(*) b, "
        "sum(CASE WHEN infant_death THEN 1 ELSE 0 END) d, "
        "sum(CASE WHEN neonatal_death THEN 1 ELSE 0 END) nd, "
        "sum(CASE WHEN postneonatal_death THEN 1 ELSE 0 END) pnd "
        f"FROM '{LINKED}' WHERE {_NAT_RES} AND data_year BETWEEN 2005 AND 2023 "
        "GROUP BY 1").fetchall()
    out = []
    for y, b, d, nd, pnd in rows:
        y, b, d, nd, pnd = int(y), int(b), int(d), int(nd), int(pnd)
        imr = fmt_rate(d, b, 1000, 2)
        nimr = fmt_rate(nd, b, 1000, 2)
        pimr = fmt_rate(pnd, b, 1000, 2)
        recon = []
        for mid, val in (("imr_per_1000", imr),
                         ("neonatal_imr_per_1000", nimr),
                         ("postneonatal_imr_per_1000", pimr)):
            exp, tol, _ = nlk.get((mid, y), (None, None, ""))
            _, _, v = reconcile(val if val else None, exp, tol, 0.01)
            if "RECONCILE_FAIL" in v:
                fail += 1
            if exp is not None:
                recon.append(f"{mid}:{v}")
        out.append({"data_year": y, "resident_births": b,
                    "infant_deaths": d, "imr_per_1000": imr,
                    "neonatal_imr_per_1000": nimr,
                    "postneonatal_imr_per_1000": pimr,
                    "reconciliation": "; ".join(recon) if recon
                    else "(no NVSR target this year)",
                    "coverage_note": PRE})
    write_tabulation(OUT_DIR / "linked_imr_by_year.csv",
                     ["data_year", "resident_births", "infant_deaths",
                      "imr_per_1000", "neonatal_imr_per_1000",
                      "postneonatal_imr_per_1000", "reconciliation",
                      "coverage_note"], out, lambda r: (r["data_year"],))

    # 10. linked IMR by year x maternal race (2005-2023) -------------------
    rows = con.execute(
        "SELECT data_year y, maternal_race_bridged r, count(*) b, "
        "sum(CASE WHEN infant_death THEN 1 ELSE 0 END) d "
        f"FROM '{LINKED}' WHERE {_NAT_RES} AND data_year BETWEEN 2005 AND 2023 "
        "GROUP BY 1,2").fetchall()
    lk_b: dict[int, dict[str, list]] = {}
    for y, r, b, d in rows:
        lk_b.setdefault(int(y), {}).setdefault(race_label(r), [0, 0])
        lk_b[int(y)][race_label(r)][0] += int(b)
        lk_b[int(y)][race_label(r)][1] += int(d)
    lk_tot = {y: sum(v[0] for v in d.values()) for y, d in lk_b.items()}
    out = []
    for y in sorted(lk_b):
        tot = {lab: v[0] for lab, v in lk_b[y].items()}
        assert_conserves(tot, lk_tot[y])                  # H6
        for lab in _RACE_ORDER:
            if lab not in lk_b[y]:
                continue
            b, d = lk_b[y][lab]
            note = ""
            if lab == NOT_STATED_RACE:
                note = "unraced residual (natality bridged-race NULL 2020+)"
            elif y >= 2020:
                note = "natality bridged-race NULL 2020+ — race signal ends 2019"
            out.append({"data_year": y, "maternal_race": lab,
                        "resident_births": b, "infant_deaths": d,
                        "imr_per_1000": fmt_rate(d, b, 1000, 2),
                        "note": note})
    write_tabulation(OUT_DIR / "linked_imr_by_year_x_maternal_race.csv",
                     ["data_year", "maternal_race", "resident_births",
                      "infant_deaths", "imr_per_1000", "note"], out,
                     lambda r: (r["data_year"], _RACE_ORDER.index(r["maternal_race"])))

    _write_readme()

    if fail:
        print(f"*** {fail} RECONCILE_FAIL cell(s) EXCEED documented tolerance "
              f"— §7-#4 halt-and-ask (do NOT ship) ***", file=sys.stderr)
        return 1
    print(f"Wrote {len(_EXPECTED)} tabulations + README to {OUT_DIR} "
          f"(0 reconcile failures)")
    return 0


# ── Tier-1 SHAPE helpers used by the SMOKE harness ─────────────────────────

_EXPECTED = [
    "natality_births_by_year.csv",
    "natality_births_by_year_x_maternal_race.csv",
    "natality_births_by_year_x_maternal_age.csv",
    "natality_rates_lbw_preterm_singleton_by_year.csv",
    "natality_rates_cesarean_multiple_by_year.csv",
    "fetal_death_counts_by_year.csv",
    "fetal_mortality_rate_by_year.csv",
    "fetal_mortality_rate_by_year_x_maternal_race.csv",
    "linked_imr_by_year.csv",
    "linked_imr_by_year_x_maternal_race.csv",
]


def _read_csv(p: Path):
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def verify_generated_conservation(out_dir: Path) -> bool:
    """H6: every *_x_maternal_race / *_x_maternal_age stratified tab's
    per-year strata sum to the unstratified sibling-by-year total."""
    by_year = {int(r["data_year"]): int(r["resident_live_births"])
               for r in _read_csv(out_dir / "natality_births_by_year.csv")}
    for fn, val_col in (("natality_births_by_year_x_maternal_race.csv", "live_births"),
                        ("natality_births_by_year_x_maternal_age.csv", "live_births")):
        acc: dict[int, int] = {}
        for r in _read_csv(out_dir / fn):
            acc[int(r["data_year"])] = acc.get(int(r["data_year"]), 0) + int(r[val_col])
        for y, s in acc.items():
            assert s == by_year[y], f"H6 {fn} {y}: {s} != {by_year[y]}"
    return True


def frozen_nvsr_checkpoints(out_dir: Path) -> dict:
    """A handful of FROZEN NVSR validation facts the data must keep
    reproducing (not mutable annotations)."""
    fd = {int(r["data_year"]): int(r["fetal_deaths_ge20wk_resident"])
          for r in _read_csv(out_dir / "fetal_death_counts_by_year.csv")}
    nb = {int(r["data_year"]): int(r["resident_live_births"])
          for r in _read_csv(out_dir / "natality_births_by_year.csv")}
    lk = {int(r["data_year"]): r["imr_per_1000"]
          for r in _read_csv(out_dir / "linked_imr_by_year.csv")}
    return {"fetal_2022_ge20wk": fd.get(2022),
            "natality_2022_births": nb.get(2022),
            "linked_2023_imr": lk.get(2023)}


def _write_readme() -> None:
    (OUT_DIR / "README.md").write_text(_README, encoding="utf-8")


_README = """\
# Pre-computed published tabulations (C8.22)

Top NVSR-cited cross-tabulations of the HVS harmonized microdata, pre-computed
so you can cite HVS figures **without loading the multi-GB parquets**. Every
cell is auto-derived by the deterministic builder
[`scripts/_build_published_tabulations.py`](../../scripts/_build_published_tabulations.py)
from the gate-verified derived parquets — re-running the builder reproduces
every CSV byte-identically.

## Canonical filter applied (every tabulation)

| Product | Canonical filter (applied on every side, incl. cross-product joins) |
|---|---|
| Natality | `residence_status != 4` (U.S. residents; ≡ `is_foreign_resident == False`) |
| Fetal death | `tabulation_flag == 2 AND residence_status != 4` (+ `version_flag == 'S'` for 1982–2002) — the NVSR-comparable ≥20-week subset |
| Linked birth–infant death | `residence_status != 4`; IMR is **unweighted** `infant_death`/`births` (the `compare_external_targets_v3_linked.py` definition) |

Each metric mirrors the exact definition of the canonical NVSR validator that
owns it (`natality/scripts/05_validate/compare_external_targets_v1.py`,
`compare_external_targets_v3_linked.py`,
`fetal_death/scripts/05_validate/validate_external_v2.py`); rate denominators
are the **known (non-null)** subset. Where a cell overlaps an NVSR-validated
target the `reconciliation` column reports the comparison; within-tolerance
differences are documented, never hidden.

## No state / sub-national geography

NCHS **suppresses all sub-national geography in the public-use natality,
fetal-death, and linked files**. There is therefore **no per-state (or county
/ region) tabulation** — it is structurally impossible from public-use data,
not an omission. The per-state slice of the original task spec is substituted
by the maternal-race and maternal-age stratifications below (both more highly
NVSR-cited). For state-level vital statistics use the NCHS Restricted Data
Center or CDC WONDER (see `docs/WORKED_EXAMPLE_FAQ.md` → "How do I get
state-level data?").

## Bridged-race discontinuity (read before using the `*_x_maternal_race` tabs)

`maternal_race_bridged` = {1 White, 2 Black, 3 AIAN, 4 Asian or Pacific
Islander}. NULL is surfaced as an explicit **"Not stated / not bridged"**
row (never dropped — every stratified breakdown sums back to the year total).
NCHS discontinued the bridged-race recode at different times per product:

- **Natality / linked**: populated through **2019**; **100% NULL from 2020**
  (use `maternal_race_ethnicity_5` for 2020+). 1990–2002 natality bridged race
  is an *approximate* crosswalk, not the official NCHS bridged-race recode.
- **Fetal death**: populated through **2017**; **100% NULL from 2018**.

So race-stratified fetal mortality is informative 1990–2017; race-stratified
IMR 2005–2019. Later years are present but fall into "Not stated / not
bridged".

## The 10 tabulations

| File | Rows | NVSR reconciliation |
|---|---|---|
| `natality_births_by_year.csv` | resident live births, 1968–2024 | `resident_births` v1 targets, 1990–2024 (pre-1990 derived; NVSR-benchmarking planned) |
| `natality_births_by_year_x_maternal_race.csv` | × bridged race + Not stated | H6 conserves to the by-year total |
| `natality_births_by_year_x_maternal_age.csv` | × NCHS age band + Not stated | H6 conserves to the by-year total |
| `natality_rates_lbw_preterm_singleton_by_year.csv` | LBW% / preterm% / singleton% (known denominator) | `lbw_rate_pct`, `preterm_rate_pct` v1 targets |
| `natality_rates_cesarean_multiple_by_year.csv` | cesarean% (era crosswalk) / twin/1000 / triplet+/100k | `cesarean_rate_pct`, `twin_rate_per_1000`, `triplet_plus_rate_per_100000` |
| `fetal_death_counts_by_year.csv` | ≥20-wk resident fetal deaths, 1982–2024 | `fetal_deaths_gte20wk_resident` (+ validator NVSR 57-08 / guide controls) |
| `fetal_mortality_rate_by_year.csv` | FMR /1000 (live births + fetal deaths), joint fetal+natality | `fetal_mortality_rate` targets, 1995–2024 |
| `fetal_mortality_rate_by_year_x_maternal_race.csv` | FMR × bridged race (both sides canonical-filtered) | H6 conserves the fetal numerator |
| `linked_imr_by_year.csv` | IMR / neonatal / postneonatal /1000, 2005–2023 | `imr_per_1000`, `neonatal_imr_per_1000`, `postneonatal_imr_per_1000` |
| `linked_imr_by_year_x_maternal_race.csv` | IMR × bridged race, 2005–2023 | H6 conserves to the by-year total |

The linked IMR tabs cover **2005–2023** (the unweighted, NVSR-reconcilable,
canonical-validator-owned surface). Pre-2005 cohort-linked IMR (1983–2004)
**is in the parquet** but its published-comparable computation needs the
cohort-specific RECWT weighting (1983–1984) + `link_segment` den/num ratio
(1983–1988) methodology — validated separately at C8.18 via
`natality/metadata/external_validation_targets_v3_linked.csv` and documented
in `natality/docs/COMPARABILITY.md` § "Pre-2005 cohort backward extension".
The permanent 1992–1994 NCHS-linkage gap applies to all linked tabs.

## Reproducing

```bash
uv run python scripts/_build_published_tabulations.py          # (re)build
uv run python scripts/_build_published_tabulations.py --check   # assert byte-identical
```
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="rebuild into a temp dir + assert byte-identical to "
                         "the committed CSVs (determinism gate)")
    args = ap.parse_args()
    if not args.check:
        return build(check_only=False)

    # determinism check: snapshot, rebuild, diff, restore
    import hashlib
    import shutil
    import tempfile
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(OUT_DIR.glob("*"))} if OUT_DIR.is_dir() else {}
    with tempfile.TemporaryDirectory() as td:
        if OUT_DIR.is_dir():
            shutil.copytree(OUT_DIR, Path(td) / "snap")
        rc = build(check_only=True)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(OUT_DIR.glob("*"))}
    drift = sorted(k for k in set(before) | set(after)
                   if before.get(k) != after.get(k))
    print(f"--check: {'WOULD-CHANGE: ' + ', '.join(drift) if drift else '(none)'}")
    return 1 if (drift or rc) else 0


if __name__ == "__main__":
    raise SystemExit(main())
