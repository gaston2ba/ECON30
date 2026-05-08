"""
Figure 1 — Paired class structure: Paris 1865 vs. Mexico City c. 1895.

Reads the transcribed CSVs in ../data/class-structure/ and writes a two-panel
horizontal bar chart to ../figures/. The Mexico City panel is intentionally
sparse where data is still missing; the script renders the gap explicitly so
downstream readers can see what still needs to be transcribed from the INEGI
1895 PDF tables.

Run:
    python code/figure_01_class_structure.py
from the project root.

Data provenance: see data/class-structure/README.md.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "class-structure"
FIGURES_DIR = PROJECT_ROOT / "figures"
OUTPUT_PATH = (
    FIGURES_DIR / "figure-01-paris-1865-mexico-city-1895-class-structure.png"
)

PARIS_CSV = DATA_DIR / "paris-1865.csv"
MEXICO_CSV = DATA_DIR / "mexico-city-c1895.csv"

PARIS_COLOR = "#3b6ea5"
MEXICO_COLOR = "#a04545"
GAP_COLOR = "#dddddd"


def load_paris() -> pd.DataFrame:
    df = pd.read_csv(PARIS_CSV)
    return df


def load_mexico() -> pd.DataFrame:
    df = pd.read_csv(MEXICO_CSV)
    df["share_pct_mid"] = df[["share_pct_low", "share_pct_high"]].mean(axis=1)
    df["share_pct_err"] = (df["share_pct_high"] - df["share_pct_low"]) / 2
    return df


def plot_paris(ax: plt.Axes, df: pd.DataFrame) -> None:
    classes = df["class"].tolist()
    shares = df["share_pct"].tolist()
    colors = [
        GAP_COLOR if cls == "Unattributed" else PARIS_COLOR for cls in classes
    ]
    y_pos = range(len(classes))[::-1]
    ax.barh(list(y_pos), shares, color=colors, edgecolor="black", linewidth=0.4)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(classes)
    ax.set_xlabel("Share of Paris population (%)")
    ax.set_xlim(0, 70)
    ax.set_title(
        "Paris, 1865\nCity of Paris municipal census (rent-bracket classification)",
        fontsize=11,
        loc="left",
    )
    for y, value in zip(y_pos, shares):
        ax.text(value + 0.6, y, f"{value:g}%", va="center", fontsize=9)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)


def plot_mexico(ax: plt.Axes, df: pd.DataFrame) -> None:
    classes = df["class"].tolist()
    mids = df["share_pct_mid"].tolist()
    errs = df["share_pct_err"].tolist()
    y_pos = list(range(len(classes)))[::-1]
    bar_values = []
    bar_colors = []
    bar_errs = []
    for mid, err in zip(mids, errs):
        if pd.isna(mid):
            bar_values.append(0)
            bar_colors.append(GAP_COLOR)
            bar_errs.append(0)
        else:
            bar_values.append(mid)
            bar_colors.append(MEXICO_COLOR)
            bar_errs.append(err)
    ax.barh(
        y_pos,
        bar_values,
        color=bar_colors,
        edgecolor="black",
        linewidth=0.4,
        xerr=bar_errs,
        error_kw={"ecolor": "black", "elinewidth": 0.7, "capsize": 3},
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(classes)
    ax.set_xlabel("Share of Federal District population (%)")
    ax.set_xlim(0, 70)
    ax.set_title(
        "Mexico City, c. 1895\nINEGI census (occupational classification)",
        fontsize=11,
        loc="left",
    )
    for y, value, err, mid in zip(y_pos, bar_values, bar_errs, mids):
        if pd.isna(mid):
            ax.text(
                1.5,
                y,
                "(data not yet transcribed — see acquisition checklist 1.2)",
                va="center",
                fontsize=8,
                style="italic",
                color="#666666",
            )
        else:
            label = f"{value - err:g}–{value + err:g}%" if err else f"{value:g}%"
            ax.text(value + err + 0.6, y, label, va="center", fontsize=9)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    paris_df = load_paris()
    mexico_df = load_mexico()

    fig, axes = plt.subplots(
        nrows=1, ncols=2, figsize=(11, 4.5), sharey=False
    )
    plot_paris(axes[0], paris_df)
    plot_mexico(axes[1], mexico_df)

    fig.suptitle(
        "Class structure on the eve of and during 19th-century urban renovation",
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )
    fig.text(
        0.5,
        -0.06,
        (
            "Sources: City of Paris municipal census, 1865 (via Knowledge Base/raw/Paris/catalog.md, dataset 2);\n"
            "INEGI 1895 census, Federal District (via Knowledge Base/raw/MexicoCity/catalog.md, dataset 2). "
            "See data/class-structure/README.md for caveats."
        ),
        ha="center",
        fontsize=8,
        color="#444444",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
