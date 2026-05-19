"""DESIGN: tracks-current-state

C8.18 DO step 6b SMOKE — the **FULL canonical re-harmonize linked
1983-2023 → v4** (the FIRST canonical parquet/``harmonized_schema.csv``
mutation in C8.18; Anti-Pattern #6 version bump).

What 6b mutates (and what this harness defends, SHAPE-not-VALUE):

  * ``harmonize_linked_v3.main()`` gains a permanent-linkage-gap skip
    (1992-1994) + a default ``--years 1983-2023`` so the canonical
    one-command rebuild reproduces the v4 envelope. The 2005-2023
    canonical path stays byte-identical (``_cohort_era(y) is None`` for
    y>=2005 — the §9-#7 behaviour-preservation invariant).
  * ``natality/metadata/harmonized_schema.csv`` HALT-6(a)-(f): the
    death-side rows' ``years_available`` widen 2005-2023 → 1983-2023
    (1992-1994 gap); NEW rows for ``underlying_cause_icd9`` /
    ``cause_recode_61`` / ``link_segment`` (present in ``OUT_SCHEMA``
    since 5c-i/5c-iii but absent from the schema CSV until 6b); the
    linked logical version bump v3 → v4.

SHAPE-not-VALUE (Convention 1 / §4.2.1): this harness asserts
STRUCTURAL invariants that survive the authorized v4 re-harmonize —
the linkage-gap constant + its 38-valid-year span, the schema-CSV ⊇
every-harmonized-column completeness invariant (the L13 defense), the
new rows' dtype == ``OUT_SCHEMA``, the widened death-side
``years_available``, the ``link_segment`` den/num/NULL discriminator,
and the v4 derived-parquet schema/coverage shape. It pins NO value
that legitimately evolves under v4 (no row count, no SHA, no IMR).

§9-#9: authored BEFORE the DO. Against the pre-6b tree the Tier-0
``_LINKAGE_GAP`` import is RED (ImportError — the constant does not yet
exist) and the schema-completeness / widened-years assertions are RED
(the 3 new rows absent; death-side years still 2005-2023) → GREEN after
the 6b DO. Tier-1/Tier-2 skip until the cohort zips / v4 parquet exist.
"""

import csv
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pytest

_IMPORT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
_HARM_DIR = Path(__file__).resolve().parents[1] / "scripts" / "03_harmonize"
for _d in (_IMPORT_DIR, _HARM_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from parse_linked_year import iter_parsed_records  # noqa: E402
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _harmonize_batch,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
LINKED_OUT_DIR = Path.home() / "Desktop/natality-harmonization/output/linked"
_HARM_DERIVED = (
    Path.home()
    / "Desktop/natality-harmonization/output/harmonized"
)
_V4_DERIVED = _HARM_DERIVED / "natality_v3_linked_harmonized_derived.parquet"
_V3_BASELINE = (
    _HARM_DERIVED / "natality_v3_linked_harmonized_derived.v3_baseline.parquet"
)
_SCHEMA_CSV = (
    Path(__file__).resolve().parents[1]
    / "metadata" / "harmonized_schema.csv"
)

# The 16 derived columns appended by derive_linked_v3.py (lines 164-183;
# 13 birth-side derived shared with natality V2 + 3 death-side derived).
# `tracks-current-state`: if derive_linked_v3 adds/renames a derived
# column, update this list in the SAME commit (Convention 2).
_DERIVE_NAMES = [
    "gestational_age_weeks_clean", "birthweight_grams_clean", "apgar5_clean",
    "low_birthweight", "very_low_birthweight", "preterm_lt37",
    "very_preterm_lt32", "singleton", "maternal_age_cat", "father_age_cat",
    "diabetes_any_bool", "hypertension_chronic_bool",
    "hypertension_gestational_bool",
    "neonatal_death", "postneonatal_death", "cause_group",
]

# The cohort envelope (gap-aware): 1983-1991 + 1995-2023 = 38 valid years
# (1992-1994 is the permanent NCHS linkage gap).
_EXPECTED_VALID_YEARS = sorted(
    set(range(1983, 2024)) - {1992, 1993, 1994}
)


def _schema_rows():
    with _SCHEMA_CSV.open() as fh:
        return list(csv.DictReader(fh))


def _schema_names():
    return {r["harmonized_name"] for r in _schema_rows()}


# ==========================================================================
# Tier 0 (metadata/dispatch only, always runs) — SMOKE-first RED→GREEN.
# ==========================================================================

def test_tier0_linkage_gap_constant_and_span():
    """6b adds ``harmonize_linked_v3._LINKAGE_GAP`` (the permanent
    1992-1994 NCHS linkage gap) so ``main()`` skips it instead of
    crashing on the missing ``_raw``. RED pre-6b (ImportError)."""
    from harmonize_linked_v3 import _LINKAGE_GAP  # noqa: E402

    assert set(_LINKAGE_GAP) == {1992, 1993, 1994}
    span = sorted(set(range(1983, 2024)) - set(_LINKAGE_GAP))
    assert span == _EXPECTED_VALID_YEARS
    assert len(span) == 38


def test_tier0_schema_csv_covers_every_harmonized_column():
    """L13 schema-completeness invariant: every ``OUT_SCHEMA`` column +
    every derive_linked_v3 derived column has a ``harmonized_name`` row
    in harmonized_schema.csv. RED pre-6b — ``underlying_cause_icd9`` /
    ``cause_recode_61`` / ``link_segment`` live in OUT_SCHEMA (5c-i /
    5c-iii) but are absent from the schema CSV until HALT-6(b)/(e)."""
    have = _schema_names()
    need = {f.name for f in OUT_SCHEMA} | set(_DERIVE_NAMES)
    missing = sorted(need - have)
    assert not missing, (
        f"harmonized_schema.csv is missing rows for shipped columns: "
        f"{missing} (HALT-6(b)/(e): add underlying_cause_icd9/"
        f"cause_recode_61/link_segment rows)"
    )


def test_tier0_new_schema_rows_dtype_matches_out_schema():
    """The 3 NEW rows' ``type`` cell must equal the OUT_SCHEMA pyarrow
    dtype (so the C8.1 dtype-parity test PASSes on v4). RED pre-6b."""
    expected = {
        "underlying_cause_icd9": "string",
        "cause_recode_61": "int16",
        "link_segment": "string",
    }
    by_name = {r["harmonized_name"]: r for r in _schema_rows()}
    for name, want in expected.items():
        assert name in by_name, f"{name} row absent (HALT-6(b)/(e))"
        assert by_name[name]["type"] == want, (
            f"{name}: schema type={by_name[name]['type']!r}, "
            f"expected {want!r} (== OUT_SCHEMA {OUT_SCHEMA.field(name).type})"
        )


def test_tier0_death_side_years_available_widened():
    """HALT-6(a): the linked-only death-side rows widen
    ``years_available`` 2005-2023 → 1983-2023. SHAPE: the cell must
    reference 1983 (not the bare pre-6b 2005-2023). RED pre-6b."""
    by_name = {r["harmonized_name"]: r for r in _schema_rows()}
    # the always-present-on-deaths cohort-extended death-side rows
    for name in ("infant_death", "age_at_death_recode5"):
        ya = by_name[name]["years_available"]
        assert "1983" in ya, (
            f"{name}.years_available={ya!r} — HALT-6(a) widening to "
            f"1983-2023 (1992-1994 gap) not applied"
        )


def test_tier0_2005plus_canonical_path_untouched():
    """§9-#7 behaviour-preservation regression-lock: every year >=2005
    routes to the canonical path (``_cohort_era is None``) so the v4
    re-harmonize leaves the shipped 2005-2023 product byte-identical;
    the cohort branch fires ONLY for the pre-2005 envelope."""
    for y in range(2005, 2024):
        assert _cohort_era(y) is None, f"{y} must stay the canonical path"
    for y in (1983, 1988, 1991, 1995, 2002, 2003, 2004):
        assert _cohort_era(y) is not None, f"{y} must route to a cohort era"
    for y in (1992, 1993, 1994):
        with pytest.raises(ValueError):
            _cohort_era(y)  # §2 fail-closed — never the 2005+ body


# ==========================================================================
# Tier 1 (real cohort zip, skip if the gitignored zip is absent) — the
# link_segment den/num discriminator survives a real parse+harmonize.
# ==========================================================================

def _real_harmonize(zip_name: str, year: int, max_rows=400):
    zp = LINKED_RAW_DIR / zip_name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {zip_name} absent (gitignored)")
    rows = list(iter_parsed_records(zp, year, max_rows=max_rows))
    assert rows
    names = list(dict.fromkeys(
        n for r in rows for n in r.keys()
        if n not in ("year", "link_segment")
    ))
    cols = [
        pa.array([str(r.get(n, "")) for r in rows], type=pa.string())
        for n in names
    ]
    cols.append(pa.array([int(r["year"]) for r in rows], type=pa.int64()))
    has_seg = any("link_segment" in r for r in rows)
    if has_seg:
        cols.append(pa.array(
            [r.get("link_segment") for r in rows], type=pa.string()
        ))
        names2 = names + ["year", "link_segment"]
    else:
        names2 = names + ["year"]
    batch = pa.RecordBatch.from_arrays(cols, names=names2)
    out = _harmonize_batch(batch, year)
    assert out.schema.equals(OUT_SCHEMA)
    return out.to_pydict()


def test_tier1_link_segment_den_num_1985():
    """A real 1985 cohort sample carries link_segment ∈ {den,num};
    BOTH segments are present (the keyless two-file 5c-iii model)."""
    d = _real_harmonize("LinkCO85.zip", 1985)
    seg = set(d["link_segment"])
    assert seg <= {"den", "num"} and "den" in seg, (
        f"1985 link_segment domain {seg} — expected den/num"
    )


def test_tier1_link_segment_null_2005():
    """A real 2005 canonical sample harmonizes with link_segment NULL
    (the 2005+ path is single-segment — link_segment 'not applicable';
    the v3→v4 ADDITIVE column does not perturb the shipped product)."""
    pqp = LINKED_OUT_DIR / "linked_2005_denomplus.parquet"
    if not pqp.exists():
        pytest.skip("linked_2005_denomplus.parquet absent (gitignored _raw)")
    batch = next(pq.ParquetFile(pqp).iter_batches(batch_size=300))
    d = _harmonize_batch(batch, 2005).to_pydict()
    assert all(s is None for s in d["link_segment"]), (
        "2005 link_segment must be NULL (canonical path; not a cohort era)"
    )


# ==========================================================================
# Tier 2 (the v4 derived parquet, skip if absent — created at the 6b DO).
# ==========================================================================

def test_tier2_v4_derived_schema_and_coverage():
    """The v4 derived parquet carries every OUT_SCHEMA column + the 16
    derived columns, and covers the gap-aware 1983-2023 envelope."""
    if not _V4_DERIVED.exists():
        pytest.skip("v4 derived parquet absent (built at the 6b DO)")
    pf = pq.ParquetFile(_V4_DERIVED)
    names = set(pf.schema_arrow.names)
    need = {f.name for f in OUT_SCHEMA} | set(_DERIVE_NAMES)
    assert need <= names, f"v4 derived missing: {sorted(need - names)}"
    yrs = pq.read_table(_V4_DERIVED, columns=["data_year"]).column("data_year")
    seen = sorted(set(yrs.to_pylist()))
    assert seen == _EXPECTED_VALID_YEARS, (
        f"v4 year coverage {seen[:3]}..{seen[-3:]} "
        f"!= gap-aware 1983-2023 (1992-1994 gap)"
    )


def test_tier2_v3_baseline_preserved():
    """The pre-6b v3 derived parquet is preserved as the
    ``.v3_baseline`` forward-stability anchor (the 2005-2023
    byte-clean-regression reference for the §15.D VERIFY)."""
    if not _V4_DERIVED.exists():
        pytest.skip("v4 not yet built — baseline check deferred to the DO")
    assert _V3_BASELINE.exists(), (
        "natality_v3_linked_harmonized_derived.v3_baseline.parquet must be "
        "preserved before the v4 overwrite (§15.D DO step 6b)"
    )
