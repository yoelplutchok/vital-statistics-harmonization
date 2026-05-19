"""DESIGN: tracks-current-state — C8.20 CODEBOOK-extensions builder SMOKE.

SHAPE-not-VALUE (NEXT_STEPS.md §4.2.1 / Convention 1): asserts STRUCTURAL
invariants of the generated appendix (the three §15.D subsections present per
variable; idempotent byte-identical render; well-formed cross-link anchors;
marker-delimited block) that survive authorized canonical drift — NOT mutable
cell counts pinned at authoring time (those grow when the envelope grows).

§9-#9: this harness (the fixture the builder must pass) is authored BEFORE the
builder is wired to real parquets. Tier 0 runs the pure render path on a
hand-built synthetic counter fixture (no parquet I/O); Tiers 1/2 are exercised
by the DO builder run on the real gate-verified parquets + re-asserted here.
"""
from __future__ import annotations

import importlib.util
import re
from collections import Counter
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_BUILDER = _REPO / "scripts" / "_build_codebook_extensions.py"


def _load():
    spec = importlib.util.spec_from_file_location("_cbx", _BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cbx():
    assert _BUILDER.exists(), f"builder missing: {_BUILDER}"
    return _load()


# ── Tier 0: synthetic fixture, pure render, no parquet I/O ──────────────────

def _synthetic_var_stats():
    """One variable, two eras, a known sentinel ('9') + a code-frame change.

    Era A observes {1,2,9}; Era B observes {1,2,3} (code 3 added, 9 dropped) —
    so the era-diff subsection MUST report an added+dropped code, and the
    sentinel subsection MUST surface '9'.
    """
    return {
        "demo_var": {
            "1992-2002": Counter({"1": 700, "2": 250, "9": 50}),
            "2014-2024": Counter({"1": 600, "2": 380, "3": 20}),
        }
    }


def test_tier0_render_has_three_subsections_per_variable(cbx):
    md = cbx.render_appendix(
        product="fetal_death",
        var_order=["demo_var"],
        var_stats=_synthetic_var_stats(),
        schema_notes={"demo_var": "9=Unknown sentinel"},
        sentinel_candidates={"9"},
        eras=[("1992-2002", 1992, 2002), ("2014-2024", 2014, 2024)],
        provenance="SMOKE-FIXTURE (synthetic; not a real parquet)",
    )
    assert isinstance(md, str) and md.strip()
    # marker-delimited block (idempotent regeneration contract)
    assert "<!-- C8.20-GENERATED:BEGIN" in md and "<!-- C8.20-GENERATED:END" in md
    # the three §15.D subsections, per variable
    assert "demo_var" in md
    assert re.search(r"(?i)historical[- ]value[- ]distribution", md)
    assert re.search(r"(?i)sentinel", md)
    assert re.search(r"(?i)era[- ]by[- ]era|coding[- ]scheme diff|era diff", md)
    # distribution panel is per-era (both era labels rendered)
    assert "1992-2002" in md and "2014-2024" in md
    # sentinel '9' surfaced; era-diff reports the added (3) + dropped (9) codes
    assert "9" in md and "3" in md


def test_tier0_idempotent_byte_identical(cbx):
    kw = dict(
        product="fetal_death", var_order=["demo_var"],
        var_stats=_synthetic_var_stats(), schema_notes={"demo_var": "9=Unknown"},
        sentinel_candidates={"9"},
        eras=[("1992-2002", 1992, 2002), ("2014-2024", 2014, 2024)],
        provenance="SMOKE-FIXTURE",
    )
    assert cbx.render_appendix(**kw) == cbx.render_appendix(**kw), "render not deterministic"


def test_tier0_no_wallclock_in_output(cbx):
    md = cbx.render_appendix(
        product="fetal_death", var_order=["demo_var"],
        var_stats=_synthetic_var_stats(), schema_notes={}, sentinel_candidates=set(),
        eras=[("1992-2002", 1992, 2002), ("2014-2024", 2014, 2024)],
        provenance="SMOKE-FIXTURE",
    )
    # determinism: no ISO date / year-like timestamp injected by the renderer
    assert not re.search(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}", md), "wall-clock leaked into output"


def test_tier0_marker_block_replacement_is_idempotent(cbx, tmp_path):
    doc = tmp_path / "CODEBOOK.md"
    doc.write_text("# Codebook\n\nHand-authored body — must survive.\n")
    block = "<!-- C8.20-GENERATED:BEGIN x -->\nAAA\n<!-- C8.20-GENERATED:END -->"
    once = cbx.splice_marker_block(doc.read_text(), block)
    twice = cbx.splice_marker_block(once, block)
    assert once == twice, "marker splice not idempotent"
    assert "Hand-authored body — must survive." in once
    # replacing with new content swaps only between markers
    block2 = "<!-- C8.20-GENERATED:BEGIN x -->\nBBB\n<!-- C8.20-GENERATED:END -->"
    swapped = cbx.splice_marker_block(once, block2)
    assert "BBB" in swapped and "AAA" not in swapped
    assert "Hand-authored body — must survive." in swapped


# ── Tier 1/2: real generated CODEBOOK appendices (post-DO structural re-assert)

@pytest.mark.parametrize("doc", [
    _REPO / "fetal_death" / "CODEBOOK.md",
    _REPO / "natality" / "docs" / "CODEBOOK.md",
])
def test_real_codebook_has_marker_block_and_subsections(doc):
    if not doc.exists():
        pytest.skip(f"{doc} absent")
    text = doc.read_text()
    if "<!-- C8.20-GENERATED:BEGIN" not in text:
        pytest.skip("C8.20 appendix not yet rendered into this CODEBOOK (pre-DO)")
    b = text.index("<!-- C8.20-GENERATED:BEGIN")
    e = text.index("<!-- C8.20-GENERATED:END")
    assert e > b, "END marker before BEGIN"
    block = text[b:e]
    assert re.search(r"(?i)historical[- ]value[- ]distribution", block)
    assert re.search(r"(?i)sentinel", block)
    assert re.search(r"(?i)era[- ]by[- ]era|coding[- ]scheme diff|era diff", block)
    # cross-link anchors well-formed: every [..](#anchor) target is a slug
    for anchor in re.findall(r"\]\(#([^)]+)\)", block):
        assert re.fullmatch(r"[a-z0-9\-_]+", anchor), f"malformed anchor: {anchor}"
