#!/usr/bin/env python3
"""Compute historical persistence charts and summary stats for CDMX and Paris."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress, rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
MEXICO_XLSX = ROOT / "data" / "mexico" / "workbook" / "DataMexCity.xlsx"
PARIS_POP = ROOT / "data" / "paris" / "paris_population.csv"
FIG_DIR = ROOT / "figures"
OUT_JSON = ROOT / "data" / "persistence_results.json"


def _norm_name(x: str) -> str:
    return str(x).strip()


def read_mexico_sheet(sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(MEXICO_XLSX, sheet_name=sheet, header=None)
    hdr = None
    for i in range(min(20, len(raw))):
        v = raw.iloc[i, 0]
        if isinstance(v, str) and v.strip().lower().replace("í", "i") == "alcaldia":
            hdr = i
            break
    if hdr is None:
        raise ValueError(f"Could not find 'Alcaldia' header in {sheet}")

    years: list[int] = []
    cols: list[int] = []
    for j in range(1, raw.shape[1]):
        v = raw.iloc[hdr, j]
        try:
            y = int(float(v))
            years.append(y)
            cols.append(j)
        except Exception:
            continue

    rows = []
    for i in range(hdr + 1, raw.shape[0]):
        name = raw.iloc[i, 0]
        if pd.isna(name):
            continue
        name = _norm_name(name)
        if not name:
            continue
        rec = {"name": name}
        for y, j in zip(years, cols):
            val = raw.iloc[i, j]
            rec[y] = float(val) if pd.notna(val) else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def choose_earliest_year(df: pd.DataFrame, floor: int) -> int:
    years = sorted(c for c in df.columns if isinstance(c, int))
    valid = [y for y in years if y >= floor and df[y].notna().sum() >= 10]
    if not valid:
        raise ValueError(f"No valid year found >= {floor}")
    return valid[0]


def persistence_stats(
    df: pd.DataFrame,
    hist_year: int,
    curr_year: int,
    city: str,
    metric: str,
) -> dict:
    tmp = df[["name", hist_year, curr_year]].dropna().copy()
    tmp["rank_hist"] = rankdata(tmp[hist_year], method="average")
    tmp["rank_curr"] = rankdata(tmp[curr_year], method="average")
    sp = spearmanr(tmp[hist_year], tmp[curr_year])
    reg = linregress(tmp[hist_year], tmp[curr_year])
    return {
        "city": city,
        "metric": metric,
        "historical_year": int(hist_year),
        "current_year": int(curr_year),
        "n": int(len(tmp)),
        "spearman_r": float(sp.statistic),
        "spearman_p": float(sp.pvalue),
        "regression_beta": float(reg.slope),
        "regression_intercept": float(reg.intercept),
        "regression_r2": float(reg.rvalue**2),
        "regression_p": float(reg.pvalue),
        "points": tmp.to_dict(orient="records"),
    }


def plot_rank_scatter(result: dict, out_png: Path, out_svg: Path) -> None:
    pts = pd.DataFrame(result["points"])
    n = len(pts)
    plt.rcParams["font.family"] = "serif"
    fig, ax = plt.subplots(figsize=(9, 7), facecolor="#f1e9d6")
    ax.set_facecolor("#fbf7eb")
    ax.scatter(pts["rank_hist"], pts["rank_curr"], color="#2a2218", s=45, alpha=0.85)
    lim = [0.5, n + 0.5]
    ax.plot(lim, lim, linestyle="--", color="#7a1f2b", linewidth=1.5, alpha=0.8)
    for _, r in pts.iterrows():
        ax.text(r["rank_hist"] + 0.08, r["rank_curr"] + 0.08, str(r["name"]), fontsize=8)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel(f"Historical rank ({result['historical_year']})")
    ax.set_ylabel(f"Current rank ({result['current_year']})")
    ax.set_title(
        f"{result['city']} persistence: {result['metric']} rank\n"
        f"Spearman r={result['spearman_r']:.2f}, p={result['spearman_p']:.3g}"
    )
    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    fig.savefig(out_svg)
    plt.close(fig)


def plot_rank_slope(result: dict, out_png: Path, out_svg: Path) -> None:
    pts = pd.DataFrame(result["points"]).sort_values("rank_hist")
    plt.rcParams["font.family"] = "serif"
    fig, ax = plt.subplots(figsize=(10, 8), facecolor="#f1e9d6")
    ax.set_facecolor("#fbf7eb")
    x0, x1 = 0, 1
    for _, r in pts.iterrows():
        ax.plot([x0, x1], [r["rank_hist"], r["rank_curr"]], color="#6b5d48", alpha=0.55, linewidth=1.2)
        ax.scatter([x0, x1], [r["rank_hist"], r["rank_curr"]], color=["#7a1f2b", "#2d5a3d"], s=28)
        ax.text(x1 + 0.03, r["rank_curr"], str(r["name"]), va="center", fontsize=7.5)
    ax.set_xlim(-0.15, 1.7)
    ax.set_xticks([x0, x1], [str(result["historical_year"]), str(result["current_year"])])
    n = len(pts)
    ax.set_ylim(n + 0.5, 0.5)  # rank 1 at top
    ax.set_ylabel("Rank (1 = least crowded / best)")
    ax.set_title(f"{result['city']} rank shifts: {result['metric']}")
    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    fig.savefig(out_svg)
    plt.close(fig)


def mexico_results() -> dict:
    ppd = read_mexico_sheet("4. Persons per dwelling")
    drainage = read_mexico_sheet("8. % Drainage")
    pop = read_mexico_sheet("1. Population")

    hist_ppd = choose_earliest_year(ppd, 1900)
    curr_ppd = 2020 if 2020 in ppd.columns else max(c for c in ppd.columns if isinstance(c, int))
    r_ppd = persistence_stats(ppd, hist_ppd, curr_ppd, "Mexico City", "persons_per_dwelling")

    # Drainage fallback rule
    hist_drain = 1900 if 1900 in drainage.columns and drainage[1900].notna().sum() >= 10 else 1950
    curr_drain = 2020 if 2020 in drainage.columns else max(c for c in drainage.columns if isinstance(c, int))
    r_drain = persistence_stats(drainage, hist_drain, curr_drain, "Mexico City", "percent_drainage")

    pop_pair = pop[["name", hist_ppd, curr_ppd]].dropna().rename(columns={hist_ppd: "pop_hist", curr_ppd: "pop_curr"})
    r_ppd["population_context"] = {
        "historical_year": hist_ppd,
        "current_year": curr_ppd,
        "rows": int(len(pop_pair)),
        "mean_hist": float(pop_pair["pop_hist"].mean()),
        "mean_curr": float(pop_pair["pop_curr"].mean()),
    }
    return {"persons_per_dwelling": r_ppd, "drainage": r_drain}


def paris_results() -> dict:
    pop = pd.read_csv(PARIS_POP)
    crowd = (
        pop[["arrondissement", "year", "persons_per_dwelling"]]
        .dropna()
        .pivot(index="arrondissement", columns="year", values="persons_per_dwelling")
    )
    hist = 1968 if 1968 in crowd.columns else min(crowd.columns)
    curr = 2020 if 2020 in crowd.columns else (2022 if 2022 in crowd.columns else max(crowd.columns))
    tmp = crowd.reset_index().rename(columns={"arrondissement": "name"})
    return persistence_stats(tmp, int(hist), int(curr), "Paris", "persons_per_dwelling")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    mexico = mexico_results()
    paris = paris_results()

    plot_rank_scatter(
        mexico["persons_per_dwelling"],
        FIG_DIR / "persistence_cdmx.png",
        FIG_DIR / "persistence_cdmx.svg",
    )
    plot_rank_slope(
        mexico["persons_per_dwelling"],
        FIG_DIR / "persistence_cdmx_slope.png",
        FIG_DIR / "persistence_cdmx_slope.svg",
    )

    # Paris figure (if usable)
    plot_rank_scatter(
        paris,
        FIG_DIR / "persistence_paris.png",
        FIG_DIR / "persistence_paris.svg",
    )
    plot_rank_slope(
        paris,
        FIG_DIR / "persistence_paris_slope.png",
        FIG_DIR / "persistence_paris_slope.svg",
    )

    out = {"mexico": mexico, "paris": paris}
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        "Persistence finding: in Mexico City, rank correlation between "
        f"{mexico['persons_per_dwelling']['historical_year']} and "
        f"{mexico['persons_per_dwelling']['current_year']} persons-per-dwelling is "
        f"r = {mexico['persons_per_dwelling']['spearman_r']:.2f} "
        f"(p = {mexico['persons_per_dwelling']['spearman_p']:.3g}). "
        "In Paris, "
        f"{paris['historical_year']} -> {paris['current_year']} gives "
        f"r = {paris['spearman_r']:.2f} (p = {paris['spearman_p']:.3g})."
    )


if __name__ == "__main__":
    main()
