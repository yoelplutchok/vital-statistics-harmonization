"""DESIGN: tracks-current-state

C8.18 DO step 6a-RECWT SMOKE — the **bounded 1983-1984 RECWT
root-cause fix** in ``harmonize_linked_v3._harmonize_cohort_1983_1988``.

Background (the §7/§8-satisfied Option-A from the 6a addendum;
2026-05-21T12:00:00Z + 2026-05-22T02:00:00Z):

  * The 1983 and 1984 cohort-linked DENOMINATOR public-use file is a
    documented 50%-of-births-in-5-non-VSCP-areas (DC/AZ/CA/DE/GA)
    weighted sample (LinkCO83Guide.pdf p4). Even-numbered non-VSCP
    birth records carry ``RECWT=2`` (represent two births);
    odd-numbered linked + the bias-adjusted records carry ``RECWT=1``.
    Σ(RECWT) over the denominator == the guide "By occurrence" total.
  * 5c-iii NULL'd ``record_weight`` for ALL 1983-1988 on the (A′)
    Convention-3 head-sample finding "RECWT@91 era-unstable". The
    6a-RECWT re-derivation FALSIFIED that: LinkCO83Guide.pdf p13
    (coordinate-aligned "List of Data Elements and Locations") places
    ``1.f Record weight`` at Denominator byte **91** (the 3a
    transcription is correct); empirically Σ(RECWT@91 over the full
    parsed 1983 den) == guide "By occurrence" 3,643,001 byte-exact.
    The head-sample artifact: the den file is ordered by
    State-of-occurrence (p4) → the first N records are all VSCP-area
    weight-1; the weight-2 non-VSCP records are clustered later.
  * Fix: ``record_weight`` = ``_to_float_or_null(RECWT@91)`` for year
    ∈ {1983,1984} ONLY (mirrors the 1995-2002/2003-2004 RECWT
    pattern). 1985-1988 stay NULL — full files (Record count ==
    by-occurrence; no sampling); the 1988 trailing-byte anomaly is
    real (soft-flag (ll)) but harmless (no weighting needed). The
    5c-iii ``record_weight``=NULL decision is SUPERSEDED for 1983-1984,
    correct for 1985-1988.

SHAPE-not-VALUE (Convention 1 / §4.2.1): this harness asserts
STRUCTURAL invariants — the per-era-year ``record_weight``
population/NULL pattern, the float64 dtype, the {1.0,2.0} weight
domain, and the parser-conservation identity Σ(record_weight) ==
the NCHS guide "By occurrence"/"By residence" control total READ FROM
``external_validation_targets_v3_linked.csv`` at test time (the test
tracks the state-on-disk validation CSV, not a hardcoded literal). It
does NOT pin any value that evolves under an authorized v3→v4
re-harmonize.

§9-#9: authored BEFORE the DO; against the un-modified harmonizer the
Tier-0 ``record_weight`` assertions for 1983/1984 are RED (currently
the 5c-iii dict-default NULL) → GREEN after the bounded fix.
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

from field_specs import (  # noqa: E402
    LINKED_BIRTH_1983_1988_FIELDS,
    LINKED_NUM_DEATH_1983_1988_FIELDS,
)
from parse_linked_year import iter_parsed_records  # noqa: E402
from harmonize_linked_v3 import (  # noqa: E402
    OUT_SCHEMA,
    _cohort_era,
    _harmonize_batch,
    _harmonize_cohort_1983_1988,
)

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
LINKED_OUT_DIR = Path.home() / "Desktop/natality-harmonization/output/linked"
_VAL_CSV = (
    Path(__file__).resolve().parents[1]
    / "metadata" / "external_validation_targets_v3_linked.csv"
)

_BIRTH_NAMES = [f[0] for f in LINKED_BIRTH_1983_1988_FIELDS]
_DEATH_NAMES = [f[0] for f in LINKED_NUM_DEATH_1983_1988_FIELDS]


# --------------------------------------------------------------------------
# synthetic batch builder — identical shape to the 5c-iii harness (the
# parser's 1983-1988 two-file output: birth fields locs 1-91 BOTH
# segments + numerator death fields + int year + str link_segment).
# --------------------------------------------------------------------------

def _two_file_batch(planted) -> pa.RecordBatch:
    names = _BIRTH_NAMES + _DEATH_NAMES
    cols: dict[str, list] = {n: [] for n in names}
    years: list[int] = []
    segs: list[str] = []
    for row in planted:
        for n in names:
            cols[n].append(row.get(n, ""))
        years.append(int(row["year"]))
        segs.append(row["link_segment"])
    arrays = [pa.array(cols[n], type=pa.string()) for n in names]
    arrays.append(pa.array(years, type=pa.int64()))
    arrays.append(pa.array(segs, type=pa.string()))
    return pa.RecordBatch.from_arrays(
        arrays, names=names + ["year", "link_segment"]
    )


def _den_row(year=1983, **over):
    base = {
        "year": str(year), "link_segment": "den",
        "MATCHS": "3", "BIRYR": str(year), "RESSTAT": "1",
        "DMRACE": "1", "ORMOTH": "88", "DMAGE": "24", "DMEDUC": "12",
        "DMAR": "1", "DGEST": "40", "CSEX": "1", "DBIRWT": "3500",
        "DPLURAL": "1", "APGAR5": "09", "PLDEL": "1", "BIRATTND": "1",
        "RECWT": "1", "DFAGE": "28", "DFEDUC": "16", "DLIVORD": "01",
        "LIVORD9": "1", "DTOTORD": "01", "TOTORD9": "1", "DMPCB": "02",
        "NPREVIS": "11",
    }
    base.update(over)
    return base


def _num_row(year=1983, **over):
    base = {
        "year": str(year), "link_segment": "num",
        "MATCHS": "1", "BIRYR": str(year), "RESSTAT": "1",
        "DMRACE": "2", "ORMOTH": "00", "DMAGE": "19", "DMEDUC": "10",
        "DMAR": "2", "DGEST": "30", "CSEX": "2", "DBIRWT": "1100",
        "DPLURAL": "1", "APGAR5": "06", "PLDEL": "1", "BIRATTND": "1",
        "RECWT": "1", "DFAGE": "22", "DFEDUC": "12", "DLIVORD": "02",
        "LIVORD9": "2", "DTOTORD": "02", "TOTORD9": "2", "DMPCB": "05",
        "NPREVIS": "03",
        "YOD": str(year), "AGER5": "3", "UCOD": "7980", "UCODR61": "054",
    }
    base.update(over)
    return base


def _val_target(metric_id: str, year: int, universe: str) -> float:
    """Read an expected value off the state-on-disk validation CSV
    (the test tracks the CSV, not a hardcoded literal — SHAPE-not-VALUE).
    """
    with _VAL_CSV.open() as fh:
        for r in csv.DictReader(
            (ln for ln in fh if not ln.lstrip().startswith("#"))
        ):
            if (
                r["metric_id"] == metric_id
                and r["data_year"] == str(year)
                and r["universe"] == universe
            ):
                return float(r["expected_value"]), float(r["tolerance_abs"])
    raise AssertionError(
        f"{metric_id},{year},{universe} not in {_VAL_CSV.name}"
    )


# ==========================================================================
# Tier 0 (synthetic, always runs) — the bounded 1983-1984 RECWT fix:
# record_weight = float(RECWT) for year ∈ {1983,1984}; NULL 1985-1988.
# ==========================================================================

def test_tier0_recwt_scope_is_exactly_1983_1984():
    """The era-gate is EXACTLY {1983,1984}; 1985-1988 stay the
    5c-iii conservative NULL (the §7-scoped decision)."""
    for y in (1983, 1984):
        assert _cohort_era(y) == "1983_1988"
    for y in (1985, 1986, 1987, 1988):
        assert _cohort_era(y) == "1983_1988"


@pytest.mark.parametrize("year", [1983, 1984])
@pytest.mark.parametrize(
    "recwt,expect", [("1", 1.0), ("2", 2.0)]
)
def test_tier0_den_recwt_populated_1983_1984(year, recwt, expect):
    """DEN segment, 1983/1984: record_weight = float(RECWT@91)
    (1.0 for VSCP/odd-linked, 2.0 for the even-numbered non-VSCP
    50%-sample inflation) — the 6a-RECWT root-cause fix."""
    out = _harmonize_batch(
        _two_file_batch([_den_row(year, RECWT=recwt)]), year
    )
    assert out.schema.equals(OUT_SCHEMA)
    d = out.to_pydict()
    assert d["record_weight"] == [pytest.approx(expect)]
    assert d["link_segment"] == ["den"]
    # the birth-side + den infant_death=NULL contract is unperturbed
    assert d["data_year"] == [year]
    assert d["infant_death"] == [None]


@pytest.mark.parametrize("year", [1983, 1984])
def test_tier0_num_recwt_populated_1983_1984(year):
    """NUM segment, 1983/1984: the numerator is NOT 50%-sampled
    (Record count == by-occurrence) → RECWT uniformly "1" →
    record_weight 1.0; infant_death True; ICD-9 within_era unperturbed."""
    out = _harmonize_batch(
        _two_file_batch([_num_row(year, RECWT="1")]), year
    )
    d = out.to_pydict()
    assert d["record_weight"] == [pytest.approx(1.0)]
    assert d["link_segment"] == ["num"]
    assert d["infant_death"] == [True]
    assert d["underlying_cause_icd9"] == ["7980"]   # 5c-iii shape intact


@pytest.mark.parametrize("year", [1985, 1986, 1987, 1988])
def test_tier0_recwt_stays_null_1985_1988(year):
    """1985-1988 are full files (Record count == by-occurrence; no
    50%-sampling) → record_weight conservatively NULL (the §7-scoped
    1983-1984-ONLY decision; the 1988 trailing-byte anomaly is real
    but harmless — soft-flag (ll))."""
    out = _harmonize_batch(
        _two_file_batch([_den_row(year, RECWT="2"), _num_row(year)]),
        year,
    )
    d = out.to_pydict()
    assert d["record_weight"] == [None, None], (
        f"{year}: record_weight must stay NULL (full file; 6a-RECWT "
        "scope = 1983-1984 ONLY; 5c-iii decision holds here)"
    )


def test_tier0_record_weight_dtype_is_float64():
    """record_weight is float64 (schema continuity with the
    1995-2002/2003-2004/2005+ RECWT mapping; H7)."""
    f = OUT_SCHEMA.field("record_weight")
    assert f.type == pa.float64()
    out = _harmonize_cohort_1983_1988(
        _two_file_batch([_den_row(1983, RECWT="2")]), 1983
    )
    assert out.schema.field("record_weight").type == pa.float64()


def test_tier0_mixed_1983_batch_den_weighted_num_unweighted():
    """A mixed den+num 1983 batch: den RECWT 2.0 (non-VSCP sample),
    num RECWT 1.0 (unsampled) — the keyless weighted-IMR shape
    (weighted denominator, unweighted numerator)."""
    batch = _two_file_batch([
        _den_row(1983, RECWT="2"),
        _den_row(1983, RECWT="1"),
        _num_row(1983, RECWT="1"),
    ])
    d = _harmonize_batch(batch, 1983).to_pydict()
    assert d["record_weight"] == [
        pytest.approx(2.0), pytest.approx(1.0), pytest.approx(1.0)
    ]
    assert d["link_segment"] == ["den", "den", "num"]
    assert d["infant_death"] == [None, None, True]


# ==========================================================================
# Tier 1 (real, skip if the gitignored cohort zip is absent) — bounded
# parse+harmonize: 1983/1984 record_weight non-null float ∈ {1.0,2.0};
# 1988 (out of scope) record_weight all-NULL.
# ==========================================================================

def _real_parse_harmonize(zip_name: str, year: int, max_rows=500):
    zp = LINKED_RAW_DIR / zip_name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {zip_name} absent (gitignored)")
    rows = list(iter_parsed_records(zp, year, max_rows=max_rows))
    assert rows and all(
        r.get("link_segment") in ("den", "num") for r in rows
    )
    names = list(dict.fromkeys(
        n for r in rows for n in r.keys()
        if n not in ("year", "link_segment")
    ))
    cols = [
        pa.array([str(r.get(n, "")) for r in rows], type=pa.string())
        for n in names
    ]
    cols.append(pa.array([int(r["year"]) for r in rows], type=pa.int64()))
    cols.append(pa.array([r["link_segment"] for r in rows], type=pa.string()))
    batch = pa.RecordBatch.from_arrays(
        cols, names=names + ["year", "link_segment"]
    )
    out = _harmonize_batch(batch, year)
    assert out.schema.equals(OUT_SCHEMA)
    return out.to_pydict()


@pytest.mark.parametrize("zip_name,year", [
    ("LinkCO83.zip", 1983), ("LinkCO84.zip", 1984),
])
def test_tier1_real_1983_1984_recwt_nonnull(zip_name, year):
    d = _real_parse_harmonize(zip_name, year)
    rw = d["record_weight"]
    assert all(w is not None for w in rw), (
        f"{year}: record_weight must be non-NULL (the 6a-RECWT fix; "
        "the head sample is all weight-1 VSCP — RECWT@91 ordered by "
        "State-of-occurrence)"
    )
    assert set(rw) <= {1.0, 2.0}, f"{year}: RECWT domain must be {{1,2}}"


def test_tier1_real_1988_recwt_stays_null():
    """1988 is out of the 6a-RECWT scope (full file) → record_weight
    all-NULL (the 5c-iii decision holds; the 1988 byte-91 anomaly is
    harmless because 1988 needs no weighting)."""
    d = _real_parse_harmonize("LinkCO88.zip", 1988)
    assert all(w is None for w in d["record_weight"]), (
        "1988: record_weight must stay NULL (§7 scope = 1983-1984 ONLY)"
    )


# ==========================================================================
# Tier 2 (real _raw parquet, skip if absent) — the parser-conservation
# identity: Σ(record_weight | den) == guide "By occurrence"; Σ(... |
# den ∧ RESSTAT≠4) == guide "By residence"; weighted IMR == published
# (all READ from the state-on-disk validation CSV — SHAPE-not-VALUE).
# This is the published-comparability gate that the §7 finding required.
# ==========================================================================

@pytest.mark.parametrize("year", [1983, 1984])
def test_tier2_weighted_den_equals_guide_control_totals(year):
    pq_path = LINKED_OUT_DIR / f"linked_{year}_denomplus.parquet"
    if not pq_path.exists():
        pytest.skip(f"{pq_path.name} absent (gitignored _raw)")
    t = pq.read_table(
        pq_path, columns=["link_segment", "RECWT", "RESSTAT"]
    )
    den = t.filter(pc.equal(t.column("link_segment"), pa.scalar("den")))
    rw = pc.cast(pc.cast(den.column("RECWT"), pa.string()), pa.int64())
    sum_all = pc.sum(rw).as_py()
    res_mask = pc.not_equal(
        pc.cast(den.column("RESSTAT"), pa.int64()), pa.scalar(4, pa.int64())
    )
    sum_res = pc.sum(
        pc.if_else(res_mask, rw, pa.scalar(0, pa.int64()))
    ).as_py()

    occ_exp, occ_tol = _val_target("cohort_den_file_records", year, "file")
    # cohort_den_file_records is the (unweighted) record count; the
    # weighted by-occurrence == record count + Σ(RECWT-1); we assert the
    # published by-residence weighted denominator + the IMR instead
    # (the canonical-filter, published-comparable gate).
    rb_exp, rb_tol = _val_target("resident_births", year, "resident")
    assert abs(sum_res - rb_exp) <= max(rb_tol, 1), (
        f"{year}: Σ(record_weight|den,RESSTAT≠4)={sum_res} vs guide "
        f"resident_births {rb_exp} (the weighted-sample published total)"
    )
    # the unweighted record count is the H6 parser-conservation gate
    assert den.num_rows == int(occ_exp), (
        f"{year}: den rows {den.num_rows} vs guide Record count {occ_exp}"
    )
    # weighted IMR == published (resident infant deaths / weighted den)
    id_exp, id_tol = _val_target(
        "resident_infant_deaths", year, "resident"
    )
    imr_exp, imr_tol = _val_target("imr_per_1000", year, "resident")
    imr = id_exp / sum_res * 1000.0
    assert abs(imr - imr_exp) <= imr_tol + 0.01, (
        f"{year}: weighted IMR {imr:.3f} vs published {imr_exp} "
        f"(±{imr_tol}); the §7 bias is resolved"
    )
