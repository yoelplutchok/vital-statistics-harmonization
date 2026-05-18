"""DESIGN: tracks-current-state

C8.18 DO step 6a SMOKE — the pre-2005 cohort **parse-driver year->zip
mapping extension** + the **§7-fixed CHUNKED ``run_parse``** at the
keyless 1983-1988 den->num segment boundary, on real data, at SMOKE
scale (cheap-before-expensive BEFORE the full-file DO step 6a parse of
the 19 pre-2005 cohort zips).

Why this harness exists (the gap it closes):

  * ``parse_all_linked_years.py`` hard-codes the ``LinkCO{yy}US.zip``
    1995+ naming (correct 1995-2015; WRONG for 1983-1991 which is
    ``LinkCO{yy}.zip``, no ``US`` suffix). DO step 6a additively adds
    ``_zip_name_for_year(year)`` (the 1995-2015 path byte-preserved;
    §9-#7-safe). Tier-0 below pins the era mapping + the 1992-1994
    permanent-gap fail-closed.

  * The 5c-iii ``test_tier1_run_parse_preserves_numerator_section``
    verified the §7 ``run_parse`` fix on the **single-list** path
    (``max_rows=300`` -> ``chunk_rows=None``). The 5c-iii receipt
    self-check #2 explicitly flagged the **chunked production path**
    (``chunk_rows`` set; ``ParquetWriter`` created on the first chunk
    with the explicit ``_expected_parsed_schema``; the den->num
    heterogeneous-key boundary crossed mid-stream) as the residual
    risk routed to DO step 6. Tier-1 below crosses that boundary on
    real ``LinkCO83.zip`` with a small ``chunk_rows`` — the SMOKE-scale
    rehearsal of the DO-step-6a full-file §7 end-to-end gate (HALT 7).

SHAPE-not-VALUE (Convention 1): asserts structural invariants
(era->zip mapping; the den/num union schema columns survive the
chunked parquet round-trip; link_segment ∈ {den,num}; den+num
row-count conservation under the test-controlled ``max_rows``; num
rows carry the ICD-9 mortality section, den rows null it; the
homogeneous denominator-plus years carry NO synthetic link_segment),
NOT release-pinned counts. DESIGN: tracks-current-state — the era
mapping + the §7 chunked invariant track the current parser/driver;
they are updated only under an authorized parser change.

Sub-step-isolated: imports ``_zip_name_for_year`` (NEW at DO step 6a)
so the harness fails collection (RED) against the un-extended driver
(§9-#9 / L3 — proves it genuinely exercises the 6a code).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

_IMPORT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "01_import"
if str(_IMPORT_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPORT_DIR))

# ``_zip_name_for_year`` is NEW at DO step 6a (the additive pre-2005
# year->zip mapping extension). Importing it BEFORE the DO makes this
# harness fail collection (RED), proving it genuinely requires the 6a
# code (§9-#9 / L3, not a rubber-stamp).
from parse_all_linked_years import _zip_name_for_year  # noqa: E402
from parse_linked_year import _expected_parsed_schema, run_parse  # noqa: E402

LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"


# --------------------------------------------------------------------------
# Tier 0 — the pre-2005 cohort year->zip mapping (the (H) finding)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "year,expected",
    [
        (1983, "LinkCO83.zip"),   # 1983-1991: NO US suffix
        (1988, "LinkCO88.zip"),
        (1991, "LinkCO91.zip"),
        (1995, "LinkCO95US.zip"),  # 1995-2004: US suffix
        (2000, "LinkCO00US.zip"),
        (2004, "LinkCO04US.zip"),
        (2005, "LinkCO05US.zip"),  # 2005-2015: US suffix (byte-preserved)
        (2015, "LinkCO15US.zip"),
    ],
)
def test_tier0_zip_name_for_year_era_mapping(year, expected):
    assert _zip_name_for_year(year) == expected


@pytest.mark.parametrize("gap_year", [1992, 1993, 1994])
def test_tier0_zip_name_for_year_1992_1994_gap_failclosed(gap_year):
    """The permanent NCHS linkage gap has NO source file — the mapping
    MUST fail closed (§2), not fabricate a name."""
    with pytest.raises(ValueError):
        _zip_name_for_year(gap_year)


@pytest.mark.parametrize("pre_year", [1982, 1900])
def test_tier0_zip_name_for_year_pre1983_failclosed(pre_year):
    """Pre-1983 is out of the C8.18 cohort envelope — fail closed."""
    with pytest.raises(ValueError):
        _zip_name_for_year(pre_year)


# --------------------------------------------------------------------------
# Tier 1 — the §7-fixed CHUNKED run_parse at the keyless 1983-1988
# den->num boundary, on real data (the DO-step-6a HALT 7 gate rehearsed
# at SMOKE scale; the gap 5c-iii self-check #2 routed here)
# --------------------------------------------------------------------------

def _skip_if_absent(name: str) -> Path:
    zp = LINKED_RAW_DIR / name
    if not zp.exists():
        pytest.skip(f"raw cohort zip {name} absent (gitignored)")
    return zp


def test_tier1_chunked_run_parse_1983_1988_preserves_numerator_section(tmp_path):
    """The §7 CHUNKED end-to-end: ``run_parse`` with a small
    ``chunk_rows`` forces the ``ParquetWriter`` to be created on the
    first den chunk (den-only keys) and the den->num heterogeneous-key
    boundary to be crossed across multiple chunks. Under the §7 fix the
    writer is fixed to the explicit den∪num ``_expected_parsed_schema``,
    so the numerator ICD-9 section (UCOD/UCODR61/AGER5) MUST survive the
    chunked round-trip — den rows null there, num rows valued. A
    pre-fix chunked write would CRASH at the boundary or drop the
    section."""
    zp = _skip_if_absent("LinkCO83.zip")
    out = tmp_path / "linked_1983_denomplus.parquet"
    # max_rows caps EACH segment independently (parser docstring), so
    # 200 den + 200 num = 400 rows; chunk_rows=64 < 200 forces the
    # writer-on-first-chunk + the den->num boundary mid-stream.
    n = run_parse(zp, 1983, out, max_rows=200, chunk_rows=64)
    assert n == 400 and out.exists()

    pf = pq.ParquetFile(out)
    schema_names = list(pf.schema_arrow.names)
    expected = _expected_parsed_schema(1983)
    assert expected is not None, "1983 must use the explicit den∪num schema"
    assert schema_names == expected.names, (
        "chunked run_parse schema drifted from _expected_parsed_schema "
        "(the §7 chunked-path defect — the fix did not take)"
    )
    for col in ("UCOD", "UCODR61", "AGER5", "link_segment"):
        assert col in schema_names, (
            f"chunked run_parse DROPPED {col} (the §7 chunked defect)"
        )

    tbl = pf.read()
    seg = tbl.column("link_segment").to_pylist()
    ucod = tbl.column("UCOD").to_pylist()
    assert seg.count("den") == 200 and seg.count("num") == 200, (
        "den+num row-count conservation broke under the chunked path"
    )
    num_ucod = [u for u, s in zip(ucod, seg) if s == "num" and u and u.strip()]
    den_ucod = [u for u, s in zip(ucod, seg) if s == "den"]
    assert num_ucod, "num rows lost their ICD-9 UCOD (the §7 chunked defect)"
    # 1983-1988 cohort birth-year <=1998 -> ICD-9 numeric (no alpha prefix)
    assert all(not u[:1].isalpha() for u in num_ucod), (
        "1983-1988 UCOD must be ICD-9 numeric (the §15.D DO-step-1 shape)"
    )
    assert all(u in (None, "") for u in den_ucod), (
        "den rows must null the numerator ICD-9 section"
    )


def test_tier1_chunked_run_parse_1988_boundary(tmp_path):
    """Sibling-year (1988) chunked §7 round-trip — guards against a
    per-year regression at the other end of the keyless era (the
    soft-flag (ll) per-year concern, SMOKE-scale)."""
    zp = _skip_if_absent("LinkCO88.zip")
    out = tmp_path / "linked_1988_denomplus.parquet"
    n = run_parse(zp, 1988, out, max_rows=150, chunk_rows=50)
    assert n == 300 and out.exists()
    tbl = pq.ParquetFile(out).read()
    seg = tbl.column("link_segment").to_pylist()
    assert seg.count("den") == 150 and seg.count("num") == 150
    ucod = tbl.column("UCOD").to_pylist()
    assert any(
        u and u.strip() for u, s in zip(ucod, seg) if s == "num"
    ), "1988 num rows lost their ICD-9 UCOD (the §7 chunked defect)"


# --------------------------------------------------------------------------
# Tier 1 — the homogeneous denominator-plus years (1989-1991, 1995-2004)
# via the extended driver: single-member, NO synthetic link_segment;
# _expected_parsed_schema is None -> the byte-identical 2005+ path
# (§9-#7-safe: the (H) extension must not perturb the den-plus parse)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("year", [1989, 1995])
def test_tier1_denomplus_year_no_link_segment(tmp_path, year):
    """1989-1991 + 1995-2004 are single-member denominator-plus: the
    parser yields NO ``link_segment`` and ``_expected_parsed_schema``
    is None (the homogeneous from_pylist path, byte-identical to the
    shipped 2005+ pattern). The 6a driver extension must route these
    correctly and the §7 fix must NOT touch them."""
    zp = _skip_if_absent(_zip_name_for_year(year))
    assert _expected_parsed_schema(year) is None
    out = tmp_path / f"linked_{year}_denomplus.parquet"
    n = run_parse(zp, year, out, max_rows=100)
    assert n == 100 and out.exists()
    names = list(pq.ParquetFile(out).schema_arrow.names)
    assert "link_segment" not in names, (
        f"{year} is single-member denominator-plus — no synthetic "
        "link_segment expected"
    )
    assert "year" in names and len(names) > 10
