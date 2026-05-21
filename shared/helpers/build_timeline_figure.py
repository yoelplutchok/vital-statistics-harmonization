"""DESIGN: tracks-current-state

Build the cross-product coverage-timeline figure shipped at
`figures/fig1_coverage_timeline.{pdf,png}`. Three horizontal bars
(fetal-death 1982-2024; natality 1990-2024; linked 2005-2023) with
era-band coloring + vertical guidelines marking the 1989, 2003, 2014,
and 2018 certificate-revision / layout-reformat boundaries.

Run from the repo root:
    python shared/helpers/build_timeline_figure.py

Era boundaries sourced from each subproject's COMPARABILITY.md:
- fetal_death/COMPARABILITY.md §Era Structure
- natality/docs/COMPARABILITY.md §Known structural breaks + Linked-file
  format-transition + Bridged race dropped in 2020

This helper is the canonical source for the figure; re-running it
regenerates both PDF and PNG byte-deterministically (modulo matplotlib
version differences).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "figures"

# Era specification: (start_year, end_year, label, color)
# Colors picked so adjacent bands are visually distinct without relying on
# saturation tricks; revision-boundary lines (overlaid) reinforce the breaks.
FETAL_BANDS = [
    (1982, 1988, "V3b: 1978-rev", "#a8d8ea"),
    (1989, 1991, "V3a: early 1989-rev", "#aa96da"),
    (1992, 2002, "V2: 1989-rev uniform", "#fcbad3"),
    (2003, 2004, "V2.1: transition", "#ffd3b6"),
    (2005, 2017, "V1: 2003-rev transition (state phase-in)", "#ffaaa5"),
    (2018, 2024, "V1+: 2003-rev uniform", "#a8e6cf"),
]

NAT_BANDS = [
    (1968, 1989, "1968-rev era (natality)", "#f6e2b3"),
    (1990, 2002, "1989-rev uniform", "#fcbad3"),
    (2003, 2013, "2003-rev transition (state phase-in)", "#ffaaa5"),
    (2014, 2019, "2014-reformat, revised-only", "#a8e6cf"),
    (2020, 2024, "Bridged race dropped", "#dcedc1"),
]

LINKED_BANDS = [
    (1983, 1988, "Keyless two-file cohort (linked)", "#7fb3d5"),
    (1989, 1991, "Denominator-plus cohort (linked)", "#c8b6e2"),
    # 1992–1994: permanent NCHS-linkage gap (no band)
    (1995, 2004, "Denominator-plus cohort (linked)", "#c8b6e2"),
    (2005, 2015, "Denominator-plus cohort (linked)", "#c8b6e2"),
    (2016, 2019, "Period-cohort merged format (linked)", "#b5d8eb"),
    (2020, 2023, "Period-cohort, MBRACE dropped (linked)", "#dcedc1"),
]

# Three discrete NCHS publication windows; 1995–1997 is a subset of 1995–2000,
# so coverage collapses to two non-overlapping blocks (the 1995–1997 sub-window
# is a file-generation detail noted in the manuscript text + Table 1).
MATCHED_MULTIPLES_BANDS = [
    (1995, 2000, "1995–2000 windows (matched multiples)", "#f6c1c1"),
    (2016, 2020, "2016–2020 window (matched multiples)", "#cde6d0"),
]

REVISION_BOUNDARIES = [
    (1989, "1989 cert. revision"),
    (2003, "2003 cert. revision"),
    (2014, "2014 NCHS reformat"),
    (2018, "MBRACE dropped (FD)"),
    (2020, "MBRACE dropped (Nat/Linked)"),
]

PRODUCTS = [
    ("Natality", NAT_BANDS, 1968, 2024),
    ("Linked birth–infant death", LINKED_BANDS, 1983, 2023),
    ("Fetal death", FETAL_BANDS, 1982, 2024),
    ("Matched multiples", MATCHED_MULTIPLES_BANDS, 1995, 2020),
]


def verify_band_coverage() -> None:
    """Assert each product's bands span [lo, hi] with no overlaps. Documented
    internal gaps are permitted (the linked 1992-1994 NCHS-linkage gap; the
    matched-multiples inter-window gap 2001-2015)."""
    for name, bands, lo, hi in PRODUCTS:
        bands_sorted = sorted(bands, key=lambda b: b[0])
        assert bands_sorted[0][0] == lo, f"{name}: first band starts {bands_sorted[0][0]} != {lo}"
        assert bands_sorted[-1][1] == hi, f"{name}: last band ends {bands_sorted[-1][1]} != {hi}"
        for prev, curr in zip(bands_sorted, bands_sorted[1:]):
            assert curr[0] > prev[1], (
                f"{name}: band overlap between {prev[:2]} and {curr[:2]}"
            )


def build() -> None:
    verify_band_coverage()

    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=150)

    y_positions = [3, 2, 1, 0]
    bar_height = 0.62
    label_color = "#222222"

    # Render era bands per product
    for y_pos, (product_name, bands, _, _) in zip(y_positions, PRODUCTS):
        for start, end, _, color in bands:
            ax.barh(
                y_pos,
                width=(end - start + 1),
                left=start - 0.5,
                height=bar_height,
                color=color,
                edgecolor="#444444",
                linewidth=0.4,
            )

    # Revision-boundary vertical guidelines (drawn behind the bars by zorder)
    for year, _ in REVISION_BOUNDARIES:
        ax.axvline(year - 0.5, color="#444444", linestyle="--", linewidth=0.6, alpha=0.5, zorder=0)

    # Top-axis revision-boundary labels
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    boundary_years = [y - 0.5 for y, _ in REVISION_BOUNDARIES]
    boundary_labels = [f"{y}" for y, _ in REVISION_BOUNDARIES]
    ax2.set_xticks(boundary_years)
    ax2.set_xticklabels(boundary_labels, fontsize=7, color="#666666")
    ax2.tick_params(axis="x", which="both", pad=2)

    # Product labels on y-axis
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [name for name, _, _, _ in PRODUCTS],
        fontsize=10,
        color=label_color,
    )
    ax.set_ylim(-0.6, 3.6)

    # X-axis: years
    ax.set_xlim(1966.5, 2025.5)
    ax.set_xticks(list(range(1968, 2026, 4)))
    ax.tick_params(axis="x", labelsize=9, colors=label_color)
    ax.set_xlabel("Data year", fontsize=10, color=label_color)

    # Title + grid + spines
    ax.set_title(
        "Cross-product coverage of the U.S. Harmonized Vital Statistics resource",
        fontsize=11,
        color=label_color,
        pad=14,
    )
    ax.grid(axis="x", color="#cccccc", linewidth=0.3, alpha=0.4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")

    # Legend — collapse era labels per product to a per-product micro-legend.
    # Use one Patch per distinct band-color across all products to avoid
    # cluttering; group by product in the caption.
    legend_handles = []
    seen_colors: set[str] = set()
    for product_name, bands, _, _ in PRODUCTS:
        for _, _, label, color in bands:
            if color not in seen_colors:
                legend_handles.append(Patch(facecolor=color, edgecolor="#444444", linewidth=0.4, label=label))
                seen_colors.add(color)
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=3,
        fontsize=7.5,
        frameon=False,
    )

    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig1_coverage_timeline.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig1_coverage_timeline.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    build()
    print(f"Wrote {OUT_DIR / 'fig1_coverage_timeline.pdf'}")
    print(f"Wrote {OUT_DIR / 'fig1_coverage_timeline.png'}")
