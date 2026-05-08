#!/usr/bin/env python3
"""
Generate figures for the Scientific Data data descriptor paper.

Reads only from metadata CSVs and validation outputs (no large Parquet files needed).

Output: figures/ directory with PDF and PNG versions of each figure.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

REPO = Path(__file__).resolve().parents[2]
FIG_DIR = REPO / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Consistent style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


# ---------------------------------------------------------------------------
# Figure 1: Pipeline architecture
# ---------------------------------------------------------------------------
def fig1_pipeline():
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    box_style = dict(boxstyle="round,pad=0.3", facecolor="#dbe9f6", edgecolor="#2171b5", lw=1.2)
    out_style = dict(boxstyle="round,pad=0.3", facecolor="#e5f5e0", edgecolor="#238b45", lw=1.2)
    val_style = dict(boxstyle="round,pad=0.3", facecolor="#fee0d2", edgecolor="#cb181d", lw=1.2)

    # Boxes
    boxes = [
        (0.8, 2.0, "NCHS raw files\n35 natality zips\n19 linked zips", box_style),
        (3.0, 2.0, "Parsing\n5 record layouts\nfield_specs.py", box_style),
        (5.2, 2.0, "Harmonization\n3 certificate eras\ncommon schema", box_style),
        (7.4, 2.0, "Derivation\nLBW, preterm,\ncause groups", box_style),
        (7.4, 0.5, "Validation\n183 + 35 targets\n41 invariants", val_style),
        (5.2, 0.5, "Outputs\nV2: 84 cols\nV3: 94 cols", out_style),
    ]

    for x, y, text, style in boxes:
        ax.text(x, y, text, ha="center", va="center", fontsize=7.5,
                bbox=style, transform=ax.transData)

    # Arrows (horizontal pipeline)
    arrow_kw = dict(arrowstyle="->,head_width=0.15,head_length=0.1",
                    color="#666666", lw=1.5)
    for x1, x2 in [(1.55, 2.25), (3.75, 4.45), (5.95, 6.65)]:
        ax.annotate("", xy=(x2, 2.0), xytext=(x1, 2.0), arrowprops=arrow_kw)

    # Validation arrow (down from derivation)
    ax.annotate("", xy=(7.4, 1.05), xytext=(7.4, 1.5), arrowprops=arrow_kw)
    # Output arrow (down from harmonization)
    ax.annotate("", xy=(5.2, 1.05), xytext=(5.2, 1.5), arrowprops=arrow_kw)

    # Metadata annotation
    ax.text(5.2, 3.4, "metadata/harmonized_schema.csv", ha="center", va="center",
            fontsize=7, fontstyle="italic", color="#666666")
    ax.annotate("", xy=(5.2, 2.6), xytext=(5.2, 3.15),
                arrowprops=dict(arrowstyle="->", color="#999999", lw=1, ls="--"))

    fig.savefig(FIG_DIR / "fig1_pipeline.pdf")
    fig.savefig(FIG_DIR / "fig1_pipeline.png")
    plt.close(fig)
    print("Figure 1: pipeline architecture")


# ---------------------------------------------------------------------------
# Figure 2: Timeline of record layouts and certificate revisions
# ---------------------------------------------------------------------------
def fig2_timeline():
    fig, ax = plt.subplots(figsize=(7, 2.8))

    eras = [
        (1990, 2002, "350 bytes\nUnrevised 1989 cert.", "#dbe9f6"),
        (2003, 2003, "1350 B\n(transition)", "#c6dbef"),
        (2004, 2004, "1500 B", "#c6dbef"),
        (2005, 2013, "775 bytes\nDual certificate", "#9ecae1"),
        (2014, 2024, "1345 bytes\nRevised 2003 cert. only", "#4292c6"),
    ]

    y_bar = 1.5
    bar_h = 0.7

    for start, end, label, color in eras:
        width = end - start + 1
        rect = plt.Rectangle((start, y_bar - bar_h / 2), width, bar_h,
                              facecolor=color, edgecolor="white", lw=1.5)
        ax.add_patch(rect)
        cx = start + width / 2
        ax.text(cx, y_bar, label, ha="center", va="center", fontsize=6.5,
                color="black" if color != "#4292c6" else "white", weight="bold")

    # Annotation arrows for key breaks
    breaks = [
        (2003, "Certificate\nrevision begins", 0.65),
        (2014, "Obstetric estimate\ngestation adopted", 0.65),
    ]
    for yr, text, y_off in breaks:
        ax.annotate(text, xy=(yr, y_bar - bar_h / 2),
                    xytext=(yr, y_bar - bar_h / 2 - y_off),
                    ha="center", va="top", fontsize=6.5, color="#cb181d",
                    arrowprops=dict(arrowstyle="->", color="#cb181d", lw=1))

    ax.set_xlim(1988, 2026)
    ax.set_ylim(0, 2.5)
    ax.set_xlabel("Year")
    ax.set_xticks(range(1990, 2025, 5))
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    fig.savefig(FIG_DIR / "fig2_timeline.pdf")
    fig.savefig(FIG_DIR / "fig2_timeline.png")
    plt.close(fig)
    print("Figure 2: timeline")


# ---------------------------------------------------------------------------
# Figure 3: Variable availability heatmap
# ---------------------------------------------------------------------------
def fig3_availability():
    schema_path = REPO / "metadata" / "harmonized_schema.csv"
    rows = []
    with open(schema_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    # Select representative variables (skip derived)
    keep = [
        "maternal_age", "marital_status", "maternal_education_cat4",
        "maternal_race_bridged4", "maternal_hispanic",
        "smoking_any_during_pregnancy", "prenatal_care_start_month",
        "diabetes_any", "hypertension_chronic",
        "birthweight_grams", "gestational_age_weeks", "infant_sex",
        "delivery_method_recode", "apgar5", "plurality_recode",
        "bmi_prepregnancy", "payment_source_recode", "prior_cesarean",
        "father_age", "father_education_cat4",
        "ca_anencephaly", "infection_gonorrhea",
        "nicu_admission", "induction_of_labor", "breastfed_at_discharge",
        "weight_gain_pounds",
    ]

    comp_colors = {"full": "#238b45", "partial": "#f4a582", "within-era": "#4292c6"}
    years = list(range(1990, 2025))

    var_data = []
    for name in keep:
        match = [r for r in rows if r["harmonized_name"] == name]
        if not match:
            continue
        r = match[0]
        avail = r["years_available"]
        comp = r["comparability_class"]
        label = r["harmonized_label"]

        # Parse year availability
        avail_set = set()
        for part in avail.split(","):
            part = part.strip()
            if "-" in part:
                lo, hi = part.split("-")
                try:
                    avail_set.update(range(int(lo.strip()), int(hi.strip()) + 1))
                except ValueError:
                    pass
            else:
                try:
                    avail_set.add(int(part))
                except ValueError:
                    pass

        var_data.append((name, label, avail_set, comp))

    fig, ax = plt.subplots(figsize=(7, 5.5))

    for i, (name, label, avail_set, comp) in enumerate(var_data):
        color = comp_colors.get(comp, "#cccccc")
        for j, yr in enumerate(years):
            if yr in avail_set:
                ax.add_patch(plt.Rectangle((j, len(var_data) - 1 - i), 1, 0.85,
                                           facecolor=color, edgecolor="white", lw=0.3))

    ax.set_xlim(0, len(years))
    ax.set_ylim(0, len(var_data))
    ax.set_xticks([y - 1990 + 0.5 for y in range(1990, 2025, 5)])
    ax.set_xticklabels([str(y) for y in range(1990, 2025, 5)])
    ax.set_yticks([len(var_data) - 1 - i + 0.42 for i in range(len(var_data))])
    ax.set_yticklabels([d[1][:35] for d in var_data], fontsize=6.5)
    ax.set_xlabel("Year")

    # Legend
    legend_patches = [
        mpatches.Patch(facecolor="#238b45", label="Full comparability"),
        mpatches.Patch(facecolor="#f4a582", label="Partial comparability"),
        mpatches.Patch(facecolor="#4292c6", label="Within-era only"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=7, framealpha=0.9)

    ax.set_title("Variable availability and comparability class, 1990-2024")
    fig.savefig(FIG_DIR / "fig3_availability.pdf")
    fig.savefig(FIG_DIR / "fig3_availability.png")
    plt.close(fig)
    print("Figure 3: variable availability heatmap")


# ---------------------------------------------------------------------------
# Figure 4: External validation — computed vs published
# ---------------------------------------------------------------------------
def fig4_validation():
    val_path = REPO / "output" / "validation" / "external_validation_v1_comparison.csv"
    metrics = defaultdict(list)

    with open(val_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            mid = r["metric_id"]
            try:
                actual = float(r["actual_value"])
                expected = float(r["expected_value"])
            except (ValueError, KeyError):
                continue
            metrics[mid].append((actual, expected))

    # Select rate-based metrics for a scatter (skip birth counts — too large for same axis)
    rate_metrics = {
        "lbw_rate_pct": ("LBW rate (%)", "#2171b5", "o"),
        "preterm_rate_pct": ("Preterm rate (%)", "#cb181d", "s"),
        "cesarean_rate_pct": ("Cesarean rate (%)", "#238b45", "^"),
        "twin_rate_per_1000": ("Twin rate (per 1,000)", "#f768a1", "D"),
        "smoking_rate_pct": ("Smoking rate (%)", "#e6550d", "v"),
    }

    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5))

    # Panel a: rate metrics scatter
    ax = axes[0]
    for mid, (label, color, marker) in rate_metrics.items():
        if mid in metrics:
            data = metrics[mid]
            actual = [d[0] for d in data]
            expected = [d[1] for d in data]
            ax.scatter(expected, actual, s=14, c=color, marker=marker,
                       label=label, alpha=0.8, edgecolors="none")

    lo = min(ax.get_xlim()[0], ax.get_ylim()[0])
    hi = max(ax.get_xlim()[1], ax.get_ylim()[1])
    ax.plot([lo, hi], [lo, hi], "--", color="gray", lw=0.8, alpha=0.5)
    ax.set_xlabel("Published value (NCHS)")
    ax.set_ylabel("Computed from dataset")
    ax.set_title("a) Rate metrics (V2)", fontsize=9)
    ax.legend(fontsize=6, loc="upper left", framealpha=0.9)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

    # Panel b: residuals histogram
    ax2 = axes[1]
    all_diffs = []
    for mid in rate_metrics:
        if mid in metrics:
            for actual, expected in metrics[mid]:
                if expected != 0:
                    all_diffs.append(actual - expected)

    ax2.hist(all_diffs, bins=40, color="#4292c6", edgecolor="white", lw=0.5, alpha=0.85)
    ax2.axvline(0, color="gray", lw=0.8, ls="--")
    ax2.set_xlabel("Computed - Published")
    ax2.set_ylabel("Count")
    ax2.set_title("b) Residual distribution", fontsize=9)
    ax2.grid(True, alpha=0.2)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig4_validation.pdf")
    fig.savefig(FIG_DIR / "fig4_validation.png")
    plt.close(fig)
    print("Figure 4: external validation")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    fig1_pipeline()
    fig2_timeline()
    fig3_availability()
    fig4_validation()
    print(f"\nAll figures saved to {FIG_DIR}/")
