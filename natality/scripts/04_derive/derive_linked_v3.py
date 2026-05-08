#!/usr/bin/env python3
"""
Derive analysis-ready indicators from the V3 linked harmonized file.

Adds the same birth-side derived columns as the natality V2 derive script,
plus death-side derived columns: neonatal_death, postneonatal_death.

Input:
  output/harmonized/natality_v3_linked_harmonized.parquet

Output (default):
  output/harmonized/natality_v3_linked_harmonized_derived.parquet
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
        "--in", dest="in_path", type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v3_linked_harmonized.parquet",
    )
    p.add_argument(
        "--out", type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v3_linked_harmonized_derived.parquet",
    )
    p.add_argument("--batch-rows", type=int, default=500_000)
    return p.parse_args()


def _null_if_equal(arr: pa.Array, value: int) -> pa.Array:
    return pc.if_else(
        pc.equal(arr, pa.scalar(value, type=arr.type)),
        pa.nulls(len(arr), type=arr.type),
        arr,
    )


def _cause_group(ucod: pa.Array) -> pa.Array:
    """Map ICD-10 underlying cause of death to NCHS standard infant cause groups.

    Based on the leading causes of infant death as reported in NCHS annual
    infant mortality statistics (e.g., NVSR "Infant Mortality Statistics").
    Null for survivors (ucod is null).

    Groups:
      congenital_anomalies     Q00-Q99
      short_gestation_lbw      P07
      sids                     R95
      maternal_complications   P01
      placenta_cord_membranes  P02
      unintentional_injuries   V01-X59
      bacterial_sepsis         P36
      respiratory_distress     P22
      nec                      P77
      circulatory              I00-I99
      assault                  X85-Y09
      other_perinatal          P00, P03-P06, P08-P21, P23-P35, P37-P76, P78-P96
      other                    everything else
    """
    n = len(ucod)
    null_str = pa.scalar(None, type=pa.string())
    result = pa.nulls(n, type=pa.string())

    # Convert to Python for prefix matching (vectorized regex not worth it for
    # a column that's >98% null — only deaths have values)
    codes = ucod.to_pylist()
    labels: list[str | None] = [None] * n
    for i, code in enumerate(codes):
        if code is None:
            continue
        c = code.strip()
        if not c:
            continue
        ch = c[0]
        # Congenital anomalies Q00-Q99
        if ch == "Q":
            labels[i] = "congenital_anomalies"
        # Circulatory I00-I99
        elif ch == "I":
            labels[i] = "circulatory"
        # Unintentional injuries V01-X59
        elif ch == "V" or ch == "W":
            labels[i] = "unintentional_injuries"
        elif ch == "X":
            # X00-X59 = unintentional; X85-X99 = assault
            num = c[1:3] if len(c) >= 3 else ""
            if num.isdigit() and int(num) <= 59:
                labels[i] = "unintentional_injuries"
            elif num.isdigit() and int(num) >= 85:
                labels[i] = "assault"
            else:
                labels[i] = "other"
        elif ch == "Y":
            # Y00-Y09 = assault; rest = other
            num = c[1:3] if len(c) >= 3 else ""
            if num.isdigit() and int(num) <= 9:
                labels[i] = "assault"
            else:
                labels[i] = "other"
        elif ch == "R":
            if c.startswith("R95"):
                labels[i] = "sids"
            else:
                labels[i] = "other"
        elif ch == "P":
            # Specific perinatal conditions
            sub = c[1:3] if len(c) >= 3 else c[1:]
            if sub.isdigit():
                sn = int(sub)
                if sn == 7:  # P07
                    labels[i] = "short_gestation_lbw"
                elif sn == 1:  # P01
                    labels[i] = "maternal_complications"
                elif sn == 2:  # P02
                    labels[i] = "placenta_cord_membranes"
                elif sn == 36:  # P36
                    labels[i] = "bacterial_sepsis"
                elif sn == 22:  # P22
                    labels[i] = "respiratory_distress"
                elif sn == 77:  # P77
                    labels[i] = "nec"
                else:
                    labels[i] = "other_perinatal"
            else:
                labels[i] = "other_perinatal"
        else:
            labels[i] = "other"

    return pa.array(labels, type=pa.string())


def _age_cat(age: pa.Array) -> pa.Array:
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

    # Build output schema: input + derived birth + derived death columns
    out_fields = list(in_schema)
    out_fields.extend([
        # Birth-side derived (same as V2)
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
        # Death-side derived
        pa.field("neonatal_death", pa.bool_()),
        pa.field("postneonatal_death", pa.bool_()),
        pa.field("cause_group", pa.string()),
    ])
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
            infant_death = batch.column(batch.schema.get_field_index("infant_death"))
            aged_days = batch.column(batch.schema.get_field_index("age_at_death_days"))
            ucod = batch.column(batch.schema.get_field_index("underlying_cause_icd10"))

            # Birth-side derived
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

            # Medical risk factor booleans (1=yes→True, 2=no→False, 9/null→null)
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

            # Death-side derived (AUDIT D11):
            # - Survivors (infant_death == False) are always False for both neonatal and
            #   postneonatal — their aged_days is null but they are definitely not deaths.
            # - Deaths (infant_death == True) with non-null aged_days get the comparison.
            # - Deaths with null aged_days remain null (unknown neonatal status) — NOT
            #   forced to False, to avoid misclassifying a death whose age is missing.
            is_survivor = pc.equal(infant_death, pa.scalar(False))
            neonatal_for_deaths = pc.less(aged_days, pa.scalar(28, type=pa.int16()))
            postneonatal_for_deaths = pc.greater_equal(aged_days, pa.scalar(28, type=pa.int16()))
            neonatal = pc.if_else(is_survivor, pa.scalar(False), neonatal_for_deaths)
            postneonatal = pc.if_else(is_survivor, pa.scalar(False), postneonatal_for_deaths)

            cause_grp = _cause_group(ucod)

            out_arrays = list(batch.columns) + [
                ga_clean, bw_clean, apgar_clean,
                lbw, vlbw, preterm, vpreterm, singleton, age_cat, fage_cat,
                diab_bool, chyp_bool, ghyp_bool,
                neonatal, postneonatal, cause_grp,
            ]
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
