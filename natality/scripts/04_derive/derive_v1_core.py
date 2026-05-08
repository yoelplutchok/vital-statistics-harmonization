#!/usr/bin/env python3
"""
Derive common analysis-ready indicators from the harmonized V1 stack.

Input:
- output/harmonized/natality_v1_harmonized.parquet

Output (default):
- output/harmonized/natality_v1_harmonized_derived.parquet
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v2_harmonized.parquet",
        help="Input harmonized Parquet path",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=repo_root
        / "output"
        / "harmonized"
        / "natality_v2_harmonized_derived.parquet",
        help="Output derived Parquet path",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=500_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _null_if_equal(arr: pa.Array, value: int) -> pa.Array:
    # Keep dtype; replace sentinel with null.
    return pc.if_else(pc.equal(arr, pa.scalar(value, type=arr.type)), pa.nulls(len(arr), type=arr.type), arr)


def _age_cat(age: pa.Array) -> pa.Array:
    """
    Maternal age categories as strings:
    - <20
    - 20-24
    - 25-29
    - 30-34
    - 35-39
    - 40+
    Null when age is null.
    """
    # Build nested if_else. Comparisons with null yield null, so we need to explicitly guard.
    is_null = pc.is_null(age)
    out = pc.if_else(is_null, pa.scalar(None, type=pa.string()), pa.scalar("40+", type=pa.string()))
    out = pc.if_else(pc.less(age, 40), pa.scalar("35-39", type=pa.string()), out)
    out = pc.if_else(pc.less(age, 35), pa.scalar("30-34", type=pa.string()), out)
    out = pc.if_else(pc.less(age, 30), pa.scalar("25-29", type=pa.string()), out)
    out = pc.if_else(pc.less(age, 25), pa.scalar("20-24", type=pa.string()), out)
    out = pc.if_else(pc.less(age, 20), pa.scalar("<20", type=pa.string()), out)
    return out


def main() -> None:
    args = parse_args()
    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    in_schema = pf.schema_arrow

    required = [
        "year",
        "is_foreign_resident",
        "maternal_age",
        "father_age",
        "father_hispanic",
        "plurality_recode",
        "gestational_age_weeks",
        "birthweight_grams",
        "apgar5",
        "diabetes_any",
        "hypertension_chronic",
        "hypertension_gestational",
    ]
    missing = [c for c in required if c not in in_schema.names]
    if missing:
        raise RuntimeError(f"Missing required columns in input: {missing}")

    out_fields = list(in_schema)
    out_fields.extend(
        [
            pa.field("gestational_age_weeks_clean", pa.int16()),
            pa.field("birthweight_grams_clean", pa.int32()),
            pa.field("apgar5_clean", pa.int16()),
            pa.field("low_birthweight", pa.bool_()),
            pa.field("very_low_birthweight", pa.bool_()),
            pa.field("preterm_lt37", pa.bool_()),
            pa.field("very_preterm_lt32", pa.bool_()),
            pa.field("singleton", pa.bool_()),
            pa.field("maternal_age_cat", pa.string()),
            pa.field("father_age_cat", pa.string()),
            pa.field("diabetes_any_bool", pa.bool_()),
            pa.field("hypertension_chronic_bool", pa.bool_()),
            pa.field("hypertension_gestational_bool", pa.bool_()),
        ]
    )
    out_schema = pa.schema(out_fields)

    writer: pq.ParquetWriter | None = None
    try:
        for batch in pf.iter_batches(batch_size=args.batch_rows):
            bw = batch.column(batch.schema.get_field_index("birthweight_grams"))
            ga = batch.column(batch.schema.get_field_index("gestational_age_weeks"))
            apgar = batch.column(batch.schema.get_field_index("apgar5"))
            plur = batch.column(batch.schema.get_field_index("plurality_recode"))
            age = batch.column(batch.schema.get_field_index("maternal_age"))
            fage = batch.column(batch.schema.get_field_index("father_age"))

            # Sentinel handling per NCHS conventions in these files.
            bw_clean = _null_if_equal(bw, 9999)
            ga_clean = _null_if_equal(ga, 99)
            apgar_clean = _null_if_equal(apgar, 99)

            lbw = pc.less(bw_clean, 2500)
            vlbw = pc.less(bw_clean, 1500)
            preterm = pc.less(ga_clean, 37)
            vpreterm = pc.less(ga_clean, 32)
            singleton = pc.equal(plur, pa.scalar(1, type=plur.type))

            age_cat = _age_cat(age)
            fage_cat = _age_cat(fage)

            # Medical risk factors: convert 1/2/9 coding to nullable bool
            # 1=yes→True, 2=no→False, 9=unknown→null, null→null
            diab = batch.column(batch.schema.get_field_index("diabetes_any"))
            chyp = batch.column(batch.schema.get_field_index("hypertension_chronic"))
            ghyp = batch.column(batch.schema.get_field_index("hypertension_gestational"))

            def _int129_to_bool(arr: pa.Array) -> pa.Array:
                return pc.if_else(
                    pc.equal(arr, pa.scalar(1, type=arr.type)),
                    pa.scalar(True),
                    pc.if_else(
                        pc.equal(arr, pa.scalar(2, type=arr.type)),
                        pa.scalar(False),
                        pa.scalar(None, type=pa.bool_()),
                    ),
                )

            diab_bool = _int129_to_bool(diab)
            chyp_bool = _int129_to_bool(chyp)
            ghyp_bool = _int129_to_bool(ghyp)

            # Build output batch: original columns + derived columns.
            out_arrays = list(batch.columns)
            out_arrays.extend(
                [
                    ga_clean,
                    bw_clean,
                    apgar_clean,
                    lbw,
                    vlbw,
                    preterm,
                    vpreterm,
                    singleton,
                    age_cat,
                    fage_cat,
                    diab_bool,
                    chyp_bool,
                    ghyp_bool,
                ]
            )
            out_batch = pa.RecordBatch.from_arrays(out_arrays, schema=out_schema)
            out_tbl = pa.Table.from_batches([out_batch], schema=out_schema)

            if writer is None:
                writer = pq.ParquetWriter(str(args.out), out_schema)
            writer.write_table(out_tbl)
    finally:
        if writer is not None:
            writer.close()

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

