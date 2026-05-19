#!/usr/bin/env python3
"""C8.19 — perinatal-record (fetal-death <-> linked-infant *sibling*) join feasibility analysis.

DESIGN: deterministic / read-only / reproducible. Re-running on the same input
parquets produces byte-identical stdout (the doc cites these numbers with an
inline provenance pointer to this script — NEXT_STEPS.md §9-#2 / L6).

Purpose
-------
Quantify whether a *record-level* "perinatal record" — one row per linked-file
infant with its fetal-death **sibling** (a fetal death to the same mother)
flagged — is constructible from NCHS **public-use** microdata. It is not, and
this script measures by how far: NCHS public-use files carry no maternal /
household / pregnancy identifier and no sub-national geography, so the only
join substrate is coarse demographic strata. The script reports, per year,
the join-key entropy, the per-fetal-death candidate-birth ambiguity, and the
expected unique-sibling match rate (the §15.D C8.19 Tier-0 metric; the 5%
threshold below which the task off-ramps per §7.13 / Sub-Q42).

This backs `docs/PERINATAL_RECORD_FEASIBILITY.md` (C8.19, re-scoped 2026-05-23
per the §11 [plan-update]). It mutates nothing: it only reads the shipped
derived parquets.

Run:  uv run python scripts/perinatal_feasibility_analysis.py
"""
from __future__ import annotations

import argparse
import math
import os

import numpy as np
import pandas as pd
import pyarrow.dataset as ds

# Canonical settled-envelope derived parquets (C8.18 close; gitignored, reproducible).
# Overridable via env for a different build tree (read-only either way).
LINKED = os.environ.get(
    "HVS_LINKED_DERIVED",
    os.path.expanduser(
        "~/Desktop/natality-harmonization/output/harmonized/"
        "natality_v3_linked_harmonized_derived.parquet"
    ),
)
FETAL = os.environ.get(
    "HVS_FETAL_DERIVED",
    os.path.expanduser(
        "~/Desktop/fetal-death-harmonization-build/output/harmonized/"
        "fetal_death_derived.parquet"
    ),
)

# Representative years spanning every linked-product era + the bridged-race
# availability boundary, so the finding is shown year-invariant (not a 2020
# artifact): 2000 = pre-2005 cohort denominator-plus era; 2007 + 2015 = modern
# period era WITH bridged race; 2020 = modern era, bridged race 100% NULL
# (post-2018 NCHS discontinuation).
YEARS = (2000, 2007, 2015, 2020)

# 4-category education harmonization across the two products' differing label
# vocabularies (linked maternal_education_cat4 vs fetal-death education_cat4).
_EDU = {
    "ba_plus": "BA", "some_college": "SC", "hs_grad": "HS", "lt_hs": "LT",
    "BA+": "BA", "Some college": "SC", "HS grad": "HS", "< HS": "LT",
}


def _load_year(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filtered + projected read-only load of one year from both products."""
    link = (
        ds.dataset(LINKED)
        .to_table(
            columns=[
                "data_year", "residence_status", "maternal_age",
                "maternal_race_bridged", "hispanic_origin",
                "maternal_education_cat4", "infant_sex", "infant_death",
            ],
            filter=(ds.field("data_year") == year),
        )
        .to_pandas()
    )
    link = link[link["residence_status"] != 4].copy()

    fd = (
        ds.dataset(FETAL)
        .to_table(
            columns=[
                "data_year", "tabulation_flag", "residence_status",
                "maternal_age", "maternal_race_bridged", "hispanic_origin",
                "education_cat4", "fetal_sex", "ga_gte20wks",
            ],
            filter=(ds.field("data_year") == year),
        )
        .to_pandas()
    )
    fd = fd[
        (fd["tabulation_flag"] == 2)
        & (fd["residence_status"] != 4)
        & (fd["ga_gte20wks"].astype(str) == "1")
    ].copy()
    return link, fd


def _key_frame(df: pd.DataFrame, age, race, his, edu, sex) -> pd.DataFrame:
    a = pd.to_numeric(df[age], errors="coerce")
    a = a.where((a >= 10) & (a <= 60))
    return pd.DataFrame({
        "a": a,
        "r": pd.to_numeric(df[race], errors="coerce").astype("Int64").astype(str),
        "h": pd.to_numeric(df[his], errors="coerce").astype("Int64").astype(str),
        "e": df[edu].map(lambda v: _EDU.get(str(v).strip(), "NA")),
        "s": df[sex].astype(str).str.upper().str[0],
    })


def _entropy_bits(counts: pd.Series) -> float:
    p = (counts / counts.sum()).to_numpy()
    return float(-(p * np.log2(p)).sum())


def _analyze_year(year: int) -> dict:
    link, fd = _load_year(year)
    LK = _key_frame(link, "maternal_age", "maternal_race_bridged",
                     "hispanic_origin", "maternal_education_cat4", "infant_sex")
    FK = _key_frame(fd, "maternal_age", "maternal_race_bridged",
                     "hispanic_origin", "education_cat4", "fetal_sex")
    # Drop only the genuine age sentinel (implausible / 99). "Missing" on a
    # categorical proxy (education NA, race/hispanic <NA>) is KEPT as its own
    # stratum level — era-sparse harmonized items make the proxy join *worse*
    # (lower entropy, more collisions), not artificially fewer strata; dropping
    # those rows would mis-collapse pre-~2014 years. Exact maternal age is a
    # generous UPPER bound on key specificity (the true sibling key is looser:
    # a mother's age differs between her stillbirth and her live-birth
    # pregnancies) — if even this over-specific key yields ~0 unique matches
    # with huge ambiguity, the methodologically-correct key is strictly worse.
    LK = LK[LK["a"].notna()].copy()
    FK = FK[FK["a"].notna()].copy()
    LK["a"] = LK["a"].astype(int)
    FK["a"] = FK["a"].astype(int)

    race_ok = (LK["r"] != "<NA>").any() and (FK["r"] != "<NA>").any()

    def metrics(cols: list[str]) -> dict:
        lk = list(zip(*[LK[c] for c in cols]))
        fk = list(zip(*[FK[c] for c in cols]))
        vL = pd.Series(lk).value_counts()
        vF = pd.Series(fk).value_counts()
        sL, sF = set(vL.index), set(vF.index)
        both = sL & sF
        amb = np.array([vL.get(k, 0) for k in fk], dtype=float)
        uniq = sum(
            1 for k in fk if vF.get(k, 0) == 1 and vL.get(k, 0) == 1
        )
        flagged = sum(vL.get(k, 0) for k in both)
        n_link = len(LK)
        return {
            "strata_link": int(vL.size),
            "strata_fd": int(vF.size),
            "overlap": int(len(both)),
            "entropy_bits": round(_entropy_bits(vF), 2),
            "eff_strata": int(round(2 ** _entropy_bits(vF))),
            "amb_mean": int(round(amb.mean())) if amb.size else 0,
            "amb_median": int(np.median(amb)) if amb.size else 0,
            "amb_max": int(amb.max()) if amb.size else 0,
            "uniq_sib_cells": int(uniq),
            "expected_match_pct": round(100.0 * uniq / n_link, 5)
            if n_link else 0.0,
            "flag_true_pct": round(100.0 * flagged / n_link, 1)
            if n_link else 0.0,
        }

    out = {
        "year": year,
        "n_link_births": int(len(link)),
        "n_link_infant_deaths": int(pd.Series(link["infant_death"]).fillna(False).sum()),
        "n_fd_ge20wk": int(len(fd)),
        "key4": metrics(["a", "h", "e", "s"]),
        "race_available": bool(race_ok),
        "key5": metrics(["a", "r", "h", "e", "s"]) if race_ok else None,
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--years", type=int, nargs="*", default=list(YEARS))
    args = ap.parse_args()

    print("=" * 78)
    print("C8.19 PERINATAL-RECORD JOIN FEASIBILITY (public-use NCHS microdata)")
    print("=" * 78)
    print(f"linked-derived : {LINKED}")
    print(f"fetal-derived  : {FETAL}")
    print("sibling key    : maternal {age, hispanic, education4 [, race]} + sex")
    print("                 (NO geography, NO maternal/household/pregnancy ID —")
    print("                  both suppressed in NCHS public-use; bridged race")
    print("                  100% NULL post-2018)")
    print("§15.D Tier-0 decision threshold: expected unique-sibling match >= 5%")
    print("-" * 78)
    rows = [_analyze_year(y) for y in sorted(args.years)]
    hdr = (f"{'year':>4} {'births':>10} {'infdth':>7} {'fd>=20w':>8} "
           f"{'key':>5} {'eff_str':>7} {'cand/fd(mean)':>13} {'cand/fd(max)':>12} "
           f"{'uniq':>5} {'match%':>9} {'flag%':>6}")
    print(hdr)
    print("-" * 78)
    for r in rows:
        for kname in ("key4", "key5"):
            k = r[kname]
            if k is None:
                continue
            tag = "a/h/e/s" if kname == "key4" else "+race"
            print(
                f"{r['year']:>4} {r['n_link_births']:>10,} "
                f"{r['n_link_infant_deaths']:>7,} {r['n_fd_ge20wk']:>8,} "
                f"{tag:>5} {k['eff_strata']:>7,} {k['amb_mean']:>13,} "
                f"{k['amb_max']:>12,} {k['uniq_sib_cells']:>5} "
                f"{k['expected_match_pct']:>8.5f}% {k['flag_true_pct']:>5.1f}%"
            )
    print("-" * 78)
    worst = max(
        max(r["key4"]["expected_match_pct"],
            (r["key5"] or {}).get("expected_match_pct", 0.0))
        for r in rows
    )
    verdict = "BELOW 5% (record-level public-use join INFEASIBLE)" \
        if worst < 5 else "ABOVE 5%"
    print(f"max expected unique-sibling match rate across all years/keys "
          f"= {worst:.5f}%  ->  {verdict}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
