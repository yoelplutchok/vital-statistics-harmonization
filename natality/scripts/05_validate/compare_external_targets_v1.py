#!/usr/bin/env python3
"""
Compare selected yearly metrics from the V1 derived Parquet to externally-sourced targets.

Targets:
- metadata/external_validation_targets_v1.csv

Outputs:
- output/validation/external_validation_v1_comparison.csv
- output/validation/external_validation_v1_comparison.md

This is intentionally lightweight: it computes a small set of rate/percentage metrics in a
single streaming pass over the derived Parquet, then compares them to user-entered target
values (with tolerances) and prints a pass/fail summary.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


@dataclass(frozen=True)
class Target:
    metric_id: str
    year: int
    universe: str
    expected_value: float | None
    tolerance_abs: float | None
    value_source: str
    notes: str


SUPPORTED_METRICS: set[str] = {
    "resident_births",
    "revised_resident_births",
    "lbw_rate_pct",
    "preterm_rate_pct",
    "singleton_rate_pct",
    "male_rate_pct",
    "twin_rate_per_1000",
    "triplet_plus_rate_per_100000",
    "cesarean_rate_pct",
    "smoking_rate_pct",
    "medicaid_pct",
}

SUPPORTED_UNIVERSES: set[str] = {"resident", "resident_revised"}


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet",
        help="Input derived Parquet path",
    )
    p.add_argument(
        "--targets",
        type=Path,
        default=repo_root / "metadata" / "external_validation_targets_v1.csv",
        help="CSV of external target values",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write outputs",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=750_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _parse_float(s: str) -> float | None:
    s = (s or "").strip()
    if not s:
        return None
    return float(s)


def load_targets(path: Path) -> list[Target]:
    if not path.is_file():
        raise FileNotFoundError(path)

    targets: list[Target] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        # Skip comment lines starting with "#"
        rows = (line for line in f if not line.lstrip().startswith("#") and line.strip())
        r = csv.DictReader(rows)
        for row in r:
            metric_id = (row.get("metric_id") or "").strip()
            universe = (row.get("universe") or "").strip()
            year_s = (row.get("year") or "").strip()

            if not metric_id or not universe or not year_s:
                continue
            if metric_id not in SUPPORTED_METRICS:
                raise ValueError(f"Unsupported metric_id={metric_id!r}. Supported: {sorted(SUPPORTED_METRICS)}")
            if universe not in SUPPORTED_UNIVERSES:
                raise ValueError(f"Unsupported universe={universe!r}. Supported: {sorted(SUPPORTED_UNIVERSES)}")

            targets.append(
                Target(
                    metric_id=metric_id,
                    year=int(year_s),
                    universe=universe,
                    expected_value=_parse_float(row.get("expected_value", "")),
                    tolerance_abs=_parse_float(row.get("tolerance_abs", "")),
                    value_source=(row.get("value_source") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    return targets


def _count_true(arr: pa.Array) -> int:
    return int(pc.sum(pc.cast(pc.equal(arr, True), pa.int64())).as_py() or 0)


def _count_not_null(arr: pa.Array) -> int:
    return int(pc.sum(pc.cast(pc.invert(pc.is_null(arr)), pa.int64())).as_py() or 0)


def main() -> None:
    args = parse_args()
    targets = load_targets(args.targets)
    if not targets:
        raise RuntimeError(f"No targets found in {args.targets}")

    years_needed = sorted({t.year for t in targets})
    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    cols = set(pf.schema_arrow.names)
    required = {
        "year",
        "is_foreign_resident",
        "certificate_revision",
        "low_birthweight",
        "preterm_lt37",
        "singleton",
        "infant_sex",
        "plurality_recode",
    }
    missing = sorted(required - cols)
    if missing:
        raise RuntimeError(f"Missing required columns in input: {missing}")

    # Accumulators (year -> value), by universe
    universes = ["resident", "resident_revised"]
    births: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    lbw_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    lbw_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    pre_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    pre_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    sing_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    sing_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    male_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    male_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    plur_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    twin_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    trip_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    # Cesarean — year-dependent crosswalk:
    #   1990-2004 (DELMETH5-style codes): cesarean = codes 3 or 4; known = codes 1-4.
    #   2005+     (DMETH_REC: 1=vaginal, 2=cesarean, 9=unknown): cesarean = code 2;
    #              known = codes 1-2.
    # See per-year implementation at ~line 285 below.
    ces_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    ces_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    # Smoking (smoking_any_during_pregnancy: True among known)
    smk_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    smk_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    # Medicaid (payment_source_recode: 1=Medicaid among known 1-4)
    med_den: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}
    med_num: dict[str, dict[int, int]] = {u: {y: 0 for y in years_needed} for u in universes}

    # Check which optional columns exist
    _optional_new = {
        "delivery_method_recode": "delivery_method_recode" in cols,
        "smoking_any_during_pregnancy": "smoking_any_during_pregnancy" in cols,
        "payment_source_recode": "payment_source_recode" in cols,
    }

    revised_s = pa.scalar("revised_2003", type=pa.string())

    batch_columns = [
        "year",
        "is_foreign_resident",
        "certificate_revision",
        "low_birthweight",
        "preterm_lt37",
        "singleton",
        "infant_sex",
        "plurality_recode",
    ] + [c for c in _optional_new if _optional_new[c]]

    for batch in pf.iter_batches(
        batch_size=args.batch_rows,
        columns=batch_columns,
    ):
        year = batch.column("year")
        foreign = batch.column("is_foreign_resident")
        cert_rev = batch.column("certificate_revision")
        lbw = batch.column("low_birthweight")
        pre = batch.column("preterm_lt37")
        singleton = batch.column("singleton")
        sex = batch.column("infant_sex")
        plur = batch.column("plurality_recode")

        # Resident mask (boolean; treat null as nonresident if ever present)
        res_mask = pc.fill_null(pc.and_(pc.is_valid(foreign), pc.invert(foreign)), False)
        rev_mask = pc.fill_null(pc.and_(pc.is_valid(cert_rev), pc.equal(cert_rev, revised_s)), False)
        res_rev_mask = pc.fill_null(pc.and_(res_mask, rev_mask), False)

        present_years = [int(y) for y in pc.unique(year).to_pylist() if int(y) in births["resident"]]
        for y in present_years:
            is_y = pc.equal(year, y)

            m_res = pc.and_(res_mask, is_y)
            m_res_rev = pc.and_(res_rev_mask, is_y)

            # births
            births["resident"][y] += int(pc.sum(pc.cast(m_res, pa.int64())).as_py() or 0)
            births["resident_revised"][y] += int(pc.sum(pc.cast(m_res_rev, pa.int64())).as_py() or 0)

            # LBW
            lbw_res = pc.filter(lbw, m_res)
            lbw_den["resident"][y] += _count_not_null(lbw_res)
            lbw_num["resident"][y] += _count_true(lbw_res)

            lbw_res_rev = pc.filter(lbw, m_res_rev)
            lbw_den["resident_revised"][y] += _count_not_null(lbw_res_rev)
            lbw_num["resident_revised"][y] += _count_true(lbw_res_rev)

            # Preterm
            pre_res = pc.filter(pre, m_res)
            pre_den["resident"][y] += _count_not_null(pre_res)
            pre_num["resident"][y] += _count_true(pre_res)

            pre_res_rev = pc.filter(pre, m_res_rev)
            pre_den["resident_revised"][y] += _count_not_null(pre_res_rev)
            pre_num["resident_revised"][y] += _count_true(pre_res_rev)

            # Singleton
            sing_res = pc.filter(singleton, m_res)
            sing_den["resident"][y] += _count_not_null(sing_res)
            sing_num["resident"][y] += _count_true(sing_res)

            sing_res_rev = pc.filter(singleton, m_res_rev)
            sing_den["resident_revised"][y] += _count_not_null(sing_res_rev)
            sing_num["resident_revised"][y] += _count_true(sing_res_rev)

            # Male share
            sex_res = pc.filter(sex, m_res)
            male_den["resident"][y] += _count_not_null(sex_res)
            male_num["resident"][y] += int(pc.sum(pc.cast(pc.equal(sex_res, "M"), pa.int64())).as_py() or 0)

            sex_res_rev = pc.filter(sex, m_res_rev)
            male_den["resident_revised"][y] += _count_not_null(sex_res_rev)
            male_num["resident_revised"][y] += int(pc.sum(pc.cast(pc.equal(sex_res_rev, "M"), pa.int64())).as_py() or 0)

            # Plurality-based rates (twin per 1,000; triplet+ per 100,000)
            plur_res = pc.filter(plur, m_res)
            plur_den["resident"][y] += _count_not_null(plur_res)
            twin_num["resident"][y] += int(pc.sum(pc.cast(pc.equal(plur_res, 2), pa.int64())).as_py() or 0)
            trip_num["resident"][y] += int(pc.sum(pc.cast(pc.greater_equal(plur_res, 3), pa.int64())).as_py() or 0)

            plur_res_rev = pc.filter(plur, m_res_rev)
            plur_den["resident_revised"][y] += _count_not_null(plur_res_rev)
            twin_num["resident_revised"][y] += int(pc.sum(pc.cast(pc.equal(plur_res_rev, 2), pa.int64())).as_py() or 0)
            trip_num["resident_revised"][y] += int(pc.sum(pc.cast(pc.greater_equal(plur_res_rev, 3), pa.int64())).as_py() or 0)

            # Cesarean rate
            # 1990-2004 (DELMETH5-style): 1=vaginal, 2=VBAC, 3=primary CS, 4=repeat CS, 5+=unknown
            #   → cesarean = codes 3 or 4; known = codes 1-4
            # 2005+ (DMETH_REC): 1=vaginal, 2=cesarean, 9=unknown
            #   → cesarean = code 2; known = codes 1-2
            # Note: 2003-2004 files label the field "DMETH_REC" but it actually
            # contains DELMETH5-style codes (1-5) because they are dual-certificate
            # transition years where position 401 stores the unrevised delivery method.
            if _optional_new["delivery_method_recode"]:
                dmr = batch.column("delivery_method_recode")
                dmr_res = pc.filter(dmr, m_res)
                if y <= 2004:
                    known = pc.and_(pc.is_valid(dmr_res), pc.less_equal(dmr_res, pa.scalar(4, type=pa.int8())))
                    is_ces = pc.or_(
                        pc.equal(dmr_res, pa.scalar(3, type=pa.int8())),
                        pc.equal(dmr_res, pa.scalar(4, type=pa.int8())),
                    )
                else:
                    known = pc.and_(pc.is_valid(dmr_res), pc.less_equal(dmr_res, pa.scalar(2, type=pa.int8())))
                    is_ces = pc.equal(dmr_res, pa.scalar(2, type=pa.int8()))
                ces_den["resident"][y] += int(pc.sum(pc.cast(known, pa.int64())).as_py() or 0)
                ces_num["resident"][y] += int(pc.sum(pc.cast(is_ces, pa.int64())).as_py() or 0)

                dmr_rev = pc.filter(dmr, m_res_rev)
                if y <= 2004:
                    known_rev = pc.and_(pc.is_valid(dmr_rev), pc.less_equal(dmr_rev, pa.scalar(4, type=pa.int8())))
                    is_ces_rev = pc.or_(
                        pc.equal(dmr_rev, pa.scalar(3, type=pa.int8())),
                        pc.equal(dmr_rev, pa.scalar(4, type=pa.int8())),
                    )
                else:
                    known_rev = pc.and_(pc.is_valid(dmr_rev), pc.less_equal(dmr_rev, pa.scalar(2, type=pa.int8())))
                    is_ces_rev = pc.equal(dmr_rev, pa.scalar(2, type=pa.int8()))
                ces_den["resident_revised"][y] += int(pc.sum(pc.cast(known_rev, pa.int64())).as_py() or 0)
                ces_num["resident_revised"][y] += int(pc.sum(pc.cast(is_ces_rev, pa.int64())).as_py() or 0)

            # Smoking rate (smoking_any_during_pregnancy: bool)
            if _optional_new["smoking_any_during_pregnancy"]:
                smk = batch.column("smoking_any_during_pregnancy")
                smk_res = pc.filter(smk, m_res)
                smk_den["resident"][y] += _count_not_null(smk_res)
                smk_num["resident"][y] += _count_true(smk_res)

                smk_rev = pc.filter(smk, m_res_rev)
                smk_den["resident_revised"][y] += _count_not_null(smk_rev)
                smk_num["resident_revised"][y] += _count_true(smk_rev)

            # Medicaid share (payment_source_recode: 1=Medicaid among valid 1-4)
            if _optional_new["payment_source_recode"]:
                pay = batch.column("payment_source_recode")
                pay_res = pc.filter(pay, m_res)
                med_den["resident"][y] += _count_not_null(pay_res)
                med_num["resident"][y] += int(pc.sum(pc.cast(pc.equal(pay_res, pa.scalar(1, type=pa.int8())), pa.int64())).as_py() or 0)

                pay_rev = pc.filter(pay, m_res_rev)
                med_den["resident_revised"][y] += _count_not_null(pay_rev)
                med_num["resident_revised"][y] += int(pc.sum(pc.cast(pc.equal(pay_rev, pa.scalar(1, type=pa.int8())), pa.int64())).as_py() or 0)

    # Helper to get metric value
    def metric_value(metric_id: str, year: int, universe: str) -> float | int | None:
        if metric_id == "resident_births":
            return births["resident"][year]
        if metric_id == "revised_resident_births":
            return births["resident_revised"][year]
        if metric_id == "lbw_rate_pct":
            d = lbw_den[universe][year]
            return (lbw_num[universe][year] / d * 100.0) if d else None
        if metric_id == "preterm_rate_pct":
            d = pre_den[universe][year]
            return (pre_num[universe][year] / d * 100.0) if d else None
        if metric_id == "singleton_rate_pct":
            d = sing_den[universe][year]
            return (sing_num[universe][year] / d * 100.0) if d else None
        if metric_id == "male_rate_pct":
            d = male_den[universe][year]
            return (male_num[universe][year] / d * 100.0) if d else None
        if metric_id == "twin_rate_per_1000":
            d = plur_den[universe][year]
            return (twin_num[universe][year] / d * 1000.0) if d else None
        if metric_id == "triplet_plus_rate_per_100000":
            d = plur_den[universe][year]
            return (trip_num[universe][year] / d * 100000.0) if d else None
        if metric_id == "cesarean_rate_pct":
            d = ces_den[universe][year]
            return (ces_num[universe][year] / d * 100.0) if d else None
        if metric_id == "smoking_rate_pct":
            d = smk_den[universe][year]
            return (smk_num[universe][year] / d * 100.0) if d else None
        if metric_id == "medicaid_pct":
            d = med_den[universe][year]
            return (med_num[universe][year] / d * 100.0) if d else None
        raise ValueError(metric_id)

    out_csv = args.out_dir / "external_validation_v1_comparison.csv"
    out_md = args.out_dir / "external_validation_v1_comparison.md"

    rows_out: list[dict[str, str]] = []
    n_pass = 0
    n_fail = 0
    n_missing = 0

    for t in targets:
        actual = metric_value(t.metric_id, t.year, t.universe)
        actual_s = "" if actual is None else (str(actual) if isinstance(actual, int) else f"{actual:.6f}")

        expected_s = "" if t.expected_value is None else f"{t.expected_value:.6f}"
        tol_s = "" if t.tolerance_abs is None else f"{t.tolerance_abs:.6f}"

        status = "missing_expected"
        diff_s = ""
        pass_s = ""

        if t.expected_value is None or actual is None:
            n_missing += 1
        else:
            diff = float(actual) - float(t.expected_value)
            diff_s = f"{diff:.6f}"
            tol = t.tolerance_abs
            if tol is None:
                # Default tolerances: exact for counts; 0.05 pct-pt for rates.
                tol = 0.0 if "births" in t.metric_id else 0.05
            ok = abs(diff) <= tol
            status = "pass" if ok else "fail"
            pass_s = "1" if ok else "0"
            if ok:
                n_pass += 1
            else:
                n_fail += 1

        rows_out.append(
            {
                "metric_id": t.metric_id,
                "year": str(t.year),
                "universe": t.universe,
                "actual_value": actual_s,
                "expected_value": expected_s,
                "tolerance_abs": tol_s,
                "diff_actual_minus_expected": diff_s,
                "status": status,
                "pass": pass_s,
                "value_source": t.value_source,
                "notes": t.notes,
            }
        )

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "metric_id",
                "year",
                "universe",
                "actual_value",
                "expected_value",
                "tolerance_abs",
                "diff_actual_minus_expected",
                "status",
                "pass",
                "value_source",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(rows_out)

    out_md.write_text(
        "\n".join(
            [
                "# External validation comparison (V1)",
                "",
                f"Computed from `{args.in_path}` (resident-only universes use `is_foreign_resident == false`).",
                "",
                f"- Targets: `{args.targets}`",
                f"- Output CSV: `{out_csv}`",
                "",
                "## Summary",
                "",
                f"- pass: {n_pass}",
                f"- fail: {n_fail}",
                f"- missing expected or actual: {n_missing}",
                "",
                "Notes:",
                "- For many V1 variables (e.g., education/smoking in 2009–2013), the recommended comparison universe is `resident_revised`.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")

    if n_fail > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

