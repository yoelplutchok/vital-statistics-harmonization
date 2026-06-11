#!/usr/bin/env python3
"""C8.20 — per-variable CODEBOOK historical-evidence appendix builder.

DESIGN: deterministic / read-only / idempotent. Re-running on the same gate-
verified parquets writes byte-identical CODEBOOK.md / FAQ.md content (the
§15.D VERIFY criterion; NEXT_STEPS.md §9-#2 / L6 — every number is parquet-
derived, no wall-clock, era boundaries are cited documented constants).

For each documented harmonized variable it renders the three §15.D subsections:
  (i)   per-era value-distribution panel,
  (ii)  sentinel-code disambiguation table,
  (iii) era-by-era coding-scheme diff.
The hand-authored CODEBOOK body is never touched: the appendix is spliced
between `<!-- C8.20-GENERATED:BEGIN … -->` / `<!-- C8.20-GENERATED:END -->`
markers (2026-05-23T11:00:00Z).

Memory-safe: era-major streaming scan with predicate pushdown + per-batch
`pc.value_counts` (never materialises a multi-GB parquet — soft-flag (kk)).

Run:  uv run python scripts/_build_codebook_extensions.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds

REPO = Path(__file__).resolve().parents[1]

# ── Canonical gate-verified parquet paths (2026-05-23T11:00:00Z:
#    fetal-death canonical = the -build/output/harmonized/ tree, NOT the stale
#    flat ~/Desktop/fetal-death-harmonization/ build). Env-overridable; read-only.
FETAL = os.environ.get("HVS_FETAL_DERIVED", os.path.expanduser(
    "~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet"))
NATAL = os.environ.get("HVS_NATAL_DERIVED", os.path.expanduser(
    "~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet"))
LINKED = os.environ.get("HVS_LINKED_DERIVED", os.path.expanduser(
    "~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet"))

# ── Documented era partitions (NOT data-derived — an NCHS layout-era boundary
#    is a documentation fact). Cited inline in the rendered provenance header.
ERAS_FETAL = [  # COMPARABILITY §"Era Structure" + V3b/V3a/V2.1/C8.2 receipts
    ("1982-1988", 1982, 1988), ("1989-1991", 1989, 1991),
    ("1992-2002", 1992, 2002), ("2003-2004", 2003, 2004),
    ("2005-2013", 2005, 2013), ("2014-2017", 2014, 2017),
    ("2018-2024", 2018, 2024),
]
ERAS_NATAL = [  # natality/docs/COMPARABILITY.md "Record layout eras" + C8.17
    ("1968-1971", 1968, 1971), ("1972-1977", 1972, 1977),
    ("1978-1988", 1978, 1988), ("1989-2002", 1989, 2002),
    ("2003-2013", 2003, 2013), ("2014-2024", 2014, 2024),
]
ERAS_LINKED = [  # natality/docs/CODEBOOK.md "Record layout eras (linked)" (C8.18)
    ("1983-1988", 1983, 1988), ("1989-2004", 1989, 2004),
    ("2005-2013", 2005, 2013), ("2014-2015", 2014, 2015),
    ("2016-2023", 2016, 2023),
]

# Sentinel/"unknown" code candidates documented across the products' CODEBOOKs
# (99/999/9999 numeric "not stated"; 9 single-digit unknown; 99.9 BMI; U; blank).
GLOBAL_SENTINELS = {"9", "99", "999", "9999", "98", "999.9", "99.9", "9998", "U", "X"}

BEGIN = ("<!-- C8.20-GENERATED:BEGIN (do not hand-edit; regenerate via "
         "scripts/_build_codebook_extensions.py) -->")
END = "<!-- C8.20-GENERATED:END -->"
_MARKER_RE = re.compile(r"<!-- C8\.20-GENERATED:BEGIN.*?<!-- C8\.20-GENERATED:END -->", re.S)

# value-share floor for the era-diff "code frame" (drops <0.05%-of-era noise)
_FRAME_FLOOR = 0.0005


# ── pure helpers (SMOKE Tier 0 exercises these with synthetic fixtures) ──────

def splice_marker_block(text: str, block: str) -> str:
    """Idempotently replace the C8.20 marker region with `block`.

    If the markers are absent, append `block` at EOF (first run). Re-running
    is byte-identical: the regex swaps exactly the prior block for the new one.
    """
    if _MARKER_RE.search(text):
        return _MARKER_RE.sub(lambda _m: block, text, count=1)
    return text.rstrip() + "\n\n" + block + "\n"


def _fmt_val(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def _pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.2f}%" if d else "0.00%"


def _slug(product: str, var: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "-", f"c820-{product}-{var}".lower())


def _frame(counter: Counter) -> set[str]:
    """The code set of an era at ≥_FRAME_FLOOR share (excludes null/blank)."""
    tot = sum(counter.values())
    if not tot:
        return set()
    return {k for k, c in counter.items()
            if k not in ("", None) and (c / tot) >= _FRAME_FLOOR}


def _float_summary(rawc: Counter):
    """Exact per-era descriptive statistics from a raw {value: count} multiset.

    `rawc` keys are python floats plus possibly None / "" (null/blank). For a
    *continuous* (floating-point) variable a top-N frequency table is the wrong
    representation (and the 6-sig-fig key format was lossy — the C8.20 fresh-eyes
    audit finding); a per-era five-number summary + mean is correct and exact.

    Returns dict(n, nonnull, nullblank, distinct, min, p25, p50, p75, mean, max)
    or None if the era has zero rows. `n` keeps the era total (incl. null/blank)
    so the audit's per-variable n-conservation invariant still holds. Quantiles
    use the nearest-rank (lower) method on the weighted ECDF: rank = ceil(p·N),
    1-indexed, clamped to [1, N] — deterministic, exact, no interpolation.
    """
    n = sum(rawc.values())
    if not n:
        return None
    nullblank = sum(c for k, c in rawc.items() if k is None or k == "")
    vals = sorted((float(k), c) for k, c in rawc.items()
                  if not (k is None or k == ""))
    nn = sum(c for _, c in vals)
    if nn == 0:
        return dict(n=n, nonnull=0, nullblank=nullblank, distinct=0,
                    min=None, p25=None, p50=None, p75=None, mean=None, max=None)

    def _q(p: float) -> float:
        rank = max(1, min(nn, math.ceil(p * nn)))
        acc = 0
        for v, c in vals:
            acc += c
            if acc >= rank:
                return v
        return vals[-1][0]

    return dict(
        n=n, nonnull=nn, nullblank=nullblank, distinct=len(vals),
        min=vals[0][0], p25=_q(0.25), p50=_q(0.50), p75=_q(0.75),
        mean=sum(v * c for v, c in vals) / nn, max=vals[-1][0])


def _fmt_stat(x) -> str:
    """Format one scalar descriptive statistic. `%.6g` is the conventional
    precision for summary statistics; a scalar aggregate has no key-collision
    semantics (the audited defect was distinct *value keys* merging), so the
    L6/H8 precision class does not recur here."""
    return "—" if x is None else f"{x:.6g}"


def render_appendix(*, product, var_order, var_stats, schema_notes,
                    sentinel_candidates, eras, provenance,
                    float_cols=frozenset(), float_summaries=None) -> str:
    """Render the marker-delimited generated appendix (deterministic).

    `float_cols` (a frozenset of variable names whose parquet dtype is
    floating-point) get a per-era SUMMARY-STATISTICS panel in (i) and a
    "continuous numeric — no discrete code frame" line in (iii); their (ii)
    sentinel table is unchanged. All other variables are byte-identical to the
    pre-auditfix render (the C8.20 fresh-eyes audit verified that contract).
    """
    float_summaries = float_summaries or {}
    era_labels = [e[0] for e in eras]
    L: list[str] = [BEGIN, ""]
    L.append(f"## Appendix C8.20 — Per-variable historical evidence (auto-generated)")
    L.append("")
    L.append("> Auto-generated by `scripts/_build_codebook_extensions.py` — "
             "do **not** hand-edit; regenerate. Every count below is derived "
             "from the gate-verified parquet; era boundaries are documented "
             "NCHS layout constants (see `COMPARABILITY.md` + the layout-source "
             "CSVs + the C8.16/C8.17/C8.18/C8.2 receipts).")
    L.append(f">")
    L.append(f"> Provenance: {provenance}")
    L.append(f">")
    L.append("> Era partition: " + " · ".join(f"`{x}`" for x in era_labels))
    L.append("")
    L.append("**Variable index:** "
             + " · ".join(f"[`{v}`](#{_slug(product, v)})" for v in var_order))
    L.append("")
    for v in var_order:
        stats = var_stats.get(v, {})
        L.append(f'### `{v}` <a id="{_slug(product, v)}"></a>')
        L.append("")
        note = (schema_notes.get(v) or "").strip()
        if note:
            short = note if len(note) <= 240 else note[:237] + "…"
            L.append(f"_Schema note:_ {short}")
            L.append("")
        is_float = v in float_cols
        # (i) Historical-value distribution
        if is_float:
            # Continuous numeric → per-era summary statistics (exact). A top-N
            # frequency table is the wrong representation for a continuous
            # variable and its 6-sig-fig keys were lossy (C8.20 audit finding).
            L.append("**(i) Historical-value distribution (per era)** — "
                     "_continuous numeric: per-era summary statistics over raw "
                     "non-null values (quantiles = nearest-rank on the weighted "
                     "ECDF, rank ⌈p·N⌉; values formatted `%.6g`); documented "
                     "sentinel codes are listed in (ii) and are **not** trimmed "
                     "here_")
            L.append("")
            L.append("| Era | n | non-null | null/blank | distinct | min | "
                     "p25 | median | mean | p75 | max |")
            L.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
            fs = float_summaries.get(v) or {}
            for era in era_labels:
                s = fs.get(era)
                if not s:
                    L.append(f"| `{era}` | 0 | 0 | — | 0 | — | — | — | — | — | — |")
                    continue
                L.append(
                    f"| `{era}` | {s['n']:,} | {s['nonnull']:,} | "
                    f"{_pct(s['nullblank'], s['n'])} | {s['distinct']:,} | "
                    f"{_fmt_stat(s['min'])} | {_fmt_stat(s['p25'])} | "
                    f"{_fmt_stat(s['p50'])} | {_fmt_stat(s['mean'])} | "
                    f"{_fmt_stat(s['p75'])} | {_fmt_stat(s['max'])} |")
            L.append("")
        else:
            L.append("**(i) Historical-value distribution (per era)**")
            L.append("")
            L.append("| Era | n | Top values (`code`: count, %) | null/blank |")
            L.append("|---|--:|---|--:|")
            for era in era_labels:
                c = stats.get(era) or Counter()
                n = sum(c.values())
                if not n:
                    L.append(f"| `{era}` | 0 | — _(no records)_ | — |")
                    continue
                nullblank = sum(cnt for k, cnt in c.items() if k in ("", None))
                ranked = sorted(((k, cnt) for k, cnt in c.items() if k not in ("", None)),
                                key=lambda kv: (-kv[1], str(kv[0])))
                top = ranked[:8]
                cell = "; ".join(f"`{k}`: {cnt:,} ({_pct(cnt, n)})" for k, cnt in top)
                if len(ranked) > 8:
                    cell += f"; _(+{len(ranked) - 8} more codes)_"
                L.append(f"| `{era}` | {n:,} | {cell or '—'} | {_pct(nullblank, n)} |")
            L.append("")
        # (ii) Sentinel-code disambiguation
        L.append("**(ii) Sentinel-code disambiguation**")
        L.append("")
        srows: list[str] = []
        for era in era_labels:
            c = stats.get(era) or Counter()
            n = sum(c.values())
            if not n:
                continue
            for s in sorted(sentinel_candidates):
                if c.get(s):
                    srows.append(f"| `{era}` | `{s}` | {c[s]:,} | {_pct(c[s], n)} |")
            nb = sum(cnt for k, cnt in c.items() if k in ("", None))
            if nb:
                srows.append(f"| `{era}` | _null/blank_ | {nb:,} | {_pct(nb, n)} |")
        if srows:
            L.append("| Era | sentinel | count | % of era |")
            L.append("|---|---|--:|--:|")
            L.extend(srows)
            if note:
                L.append("")
                L.append("_Documented meaning: see the schema note above "
                         "(`harmonized_schema.csv` `notes`/`allowed_values`)._")
        else:
            L.append("_No documented sentinel candidate or null/blank observed "
                     "in any era._")
        L.append("")
        # (iii) Era-by-era coding-scheme diff
        L.append("**(iii) Era-by-era coding-scheme diff**")
        L.append("")
        if is_float:
            L.append("- Continuous numeric variable — no discrete code frame; "
                     "see the per-era summary statistics in (i). (A "
                     "frequency/code-frame diff is not meaningful for a "
                     "continuous measurement.)")
            L.append("")
            continue
        frames = {era: _frame(stats.get(era) or Counter()) for era in era_labels}
        diffs: list[str] = []
        prev = None
        for era in era_labels:
            cur = frames[era]
            if prev is not None and (prev[1] or cur):
                added = sorted(cur - prev[1], key=str)
                dropped = sorted(prev[1] - cur, key=str)
                if added or dropped:
                    a = ("added {" + ", ".join(f"`{x}`" for x in added) + "}") if added else ""
                    d = ("dropped {" + ", ".join(f"`{x}`" for x in dropped) + "}") if dropped else ""
                    diffs.append(f"- `{prev[0]}`→`{era}`: "
                                 + "; ".join(p for p in (a, d) if p)
                                 + f" _(codes ≥{_FRAME_FLOOR:.2%} of an era)_")
            if cur or (stats.get(era)):
                prev = (era, cur)
        if diffs:
            L.extend(diffs)
        else:
            L.append("- Stable code frame across all populated eras "
                     f"(no add/drop ≥{_FRAME_FLOOR:.2%} of an era).")
        L.append("")
    L.append(END)
    return "\n".join(L)


# ── real-data path (SMOKE Tier 1/2 + DO) ────────────────────────────────────

def _sha12(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def _read_schema_csv(path: Path):
    """Return (ordered harmonized_name list, {name: note-text})."""
    order, notes = [], {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            name = row.get("harmonized_name")
            if not name:
                continue
            order.append(name)
            bits = []
            for col in ("allowed_values", "notes"):
                if row.get(col):
                    bits.append(row[col].strip())
            notes[name] = " — ".join(b for b in bits if b)
    return order, notes


def scan_product(parquet_path: str, var_names, eras, year_col="data_year"):
    """Era-major streaming value_counts (predicate pushdown, bounded memory).

    Returns (out, cols, float_cols, float_summaries):
      out   — {var: {era: Counter(_fmt_val-key)}} (drives (ii) + non-float (i)/(iii);
              byte-identical to the pre-auditfix path for every variable)
      float_cols — frozenset of floating-point columns (pyarrow dtype)
      float_summaries — {float_var: {era: _float_summary(...) | None}} computed
              exactly from the raw per-era value multiset (no key formatting).
    """
    dset = ds.dataset(parquet_path, format="parquet")
    have = set(dset.schema.names)
    cols = [v for v in var_names if v in have]
    float_cols = frozenset(
        v for v in cols if pa.types.is_floating(dset.schema.field(v).type))
    out = {v: {e[0]: Counter() for e in eras} for v in cols}
    rawf = {v: {e[0]: Counter() for e in eras} for v in float_cols}
    for label, lo, hi in eras:
        flt = (ds.field(year_col) >= lo) & (ds.field(year_col) <= hi)
        scanner = dset.scanner(columns=cols, filter=flt, batch_size=1 << 19)
        for batch in scanner.to_batches():
            for v in cols:
                vc = pc.value_counts(batch.column(v))
                isf = v in float_cols
                for s, cnt in zip(vc.field("values"), vc.field("counts")):
                    py = s.as_py()
                    k = cnt.as_py()
                    out[v][label][_fmt_val(py)] += k
                    if isf:
                        rawf[v][label][py] += k
    float_summaries = {v: {e[0]: _float_summary(rawf[v][e[0]]) for e in eras}
                       for v in float_cols}
    return out, cols, float_cols, float_summaries


def _write_doc(doc_path: Path, block: str) -> tuple[str, str]:
    before = doc_path.read_text()
    after = splice_marker_block(before, block)
    doc_path.write_text(after)
    return before, after


_FAQ_BLOCK = (
    BEGIN
    + "\n\n## Per-variable historical distributions (C8.20)\n\n"
    "**Q: How do I see how a variable's codes/sentinels behaved in each era?**\n\n"
    "See the auto-generated **Appendix C8.20 — Per-variable historical "
    "evidence** at the end of the CODEBOOK. For every harmonized variable it "
    "gives, per documented layout era: the value distribution, a sentinel-code "
    "disambiguation table, and an era-by-era coding-scheme diff. Every number "
    "is derived from the shipped parquet by "
    "`scripts/_build_codebook_extensions.py` (deterministic; regenerate to "
    "reproduce byte-identically).\n\n" + END
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", choices=["fetal_death", "natality", "all"],
                    default="all")
    ap.add_argument("--check", action="store_true",
                    help="render + report would-change, do not write")
    args = ap.parse_args()

    targets = []

    if args.product in ("fetal_death", "all"):
        sch_order, sch_notes = _read_schema_csv(REPO / "fetal_death" / "harmonized_schema.csv")
        prov = (f"fetal-death derived `{os.path.basename(FETAL)}` "
                f"sha256[:12]=`{_sha12(FETAL)}` · "
                f"{ds.dataset(FETAL).count_rows():,} rows · builder "
                "`scripts/_build_codebook_extensions.py`")
        stats, cols, fcols, fsum = scan_product(FETAL, sch_order, ERAS_FETAL)
        block = render_appendix(
            product="fetal_death", var_order=cols, var_stats=stats,
            schema_notes=sch_notes, sentinel_candidates=GLOBAL_SENTINELS,
            eras=ERAS_FETAL, provenance=prov,
            float_cols=fcols, float_summaries=fsum)
        targets.append((REPO / "fetal_death" / "CODEBOOK.md", block,
                        REPO / "fetal_death" / "FAQ.md"))

    if args.product in ("natality", "all"):
        sch_order, sch_notes = _read_schema_csv(
            REPO / "natality" / "metadata" / "harmonized_schema.csv")
        nat_have = set(ds.dataset(NATAL).schema.names)
        lnk_have = set(ds.dataset(LINKED).schema.names)
        nat_vars = [v for v in sch_order if v in nat_have]
        lnk_only = [v for v in sch_order if v in lnk_have and v not in nat_have]
        prov = (
            f"natality v3.0.0 derived `{os.path.basename(NATAL)}` "
            f"sha256[:12]=`{_sha12(NATAL)}` · {ds.dataset(NATAL).count_rows():,} rows; "
            f"linked v4.0.0 derived `{os.path.basename(LINKED)}` "
            f"sha256[:12]=`{_sha12(LINKED)}` · {ds.dataset(LINKED).count_rows():,} rows "
            "(1992-1994 permanent NCHS-linkage gap) · builder "
            "`scripts/_build_codebook_extensions.py`")
        nstats, ncols, nfcols, nfsum = scan_product(NATAL, nat_vars, ERAS_NATAL)
        nat_block = render_appendix(
            product="natality", var_order=ncols, var_stats=nstats,
            schema_notes=sch_notes, sentinel_candidates=GLOBAL_SENTINELS,
            eras=ERAS_NATAL, provenance=prov + " — natality columns (1968-2024)",
            float_cols=nfcols, float_summaries=nfsum)
        lstats, lcols, lfcols, lfsum = scan_product(LINKED, lnk_only, ERAS_LINKED)
        lnk_block = render_appendix(
            product="natality-linked", var_order=lcols, var_stats=lstats,
            schema_notes=sch_notes, sentinel_candidates=GLOBAL_SENTINELS,
            eras=ERAS_LINKED,
            provenance=prov + " — linked-v4 death-side columns (1983-2023; "
            "1992-1994 gap)",
            float_cols=lfcols, float_summaries=lfsum)
        block = (nat_block.replace(END, "").rstrip() + "\n\n"
                 + lnk_block.replace(BEGIN, "").lstrip())
        targets.append((REPO / "natality" / "docs" / "CODEBOOK.md", block,
                        REPO / "natality" / "docs" / "FAQ.md"))

    changed = []
    for codebook, block, faq in targets:
        cur = codebook.read_text()
        new = splice_marker_block(cur, block)
        faq_cur = faq.read_text()
        faq_new = splice_marker_block(faq_cur, _FAQ_BLOCK)
        if args.check:
            if new != cur:
                changed.append(str(codebook))
            if faq_new != faq_cur:
                changed.append(str(faq))
            continue
        codebook.write_text(new)
        faq.write_text(faq_new)
        print(f"[C8.20] wrote {codebook.relative_to(REPO)} "
              f"({len(block.splitlines())} block lines) + "
              f"{faq.relative_to(REPO)} pointer")
    if args.check:
        print("WOULD-CHANGE: " + (", ".join(changed) if changed else "(none)"))
        return 1 if changed else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
