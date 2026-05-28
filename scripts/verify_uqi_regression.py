#!/usr/bin/env python3
"""Verify UQI regressions and export machine-readable + figure outputs."""

from __future__ import annotations

import json
import math
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data" / "uqi_regression_results.json"
OUT_HTML = ROOT / "figures" / "regression-laps.html"
OUT_SVG = ROOT / "figures" / "regression_uqi.svg"

PARIS_DATA_JSON = ROOT / "data" / "paris" / "paris_index_2022.json"
MEXICO_DATA_JSON = ROOT / "data" / "mexico" / "exports" / "mexico_alcaldias_2020.json"
PARIS_DATA_CSV = ROOT / "data" / "paris" / "paris_uqi_2020.csv"
MEXICO_DATA_CSV = ROOT / "data" / "mexico" / "exports" / "cdmx_uqi_2020.csv"
MEXICO_XLSX = ROOT / "data" / "mexico" / "workbook" / "DataMexCity.xlsx"

PARIS_XY = {
    1: (300, 240), 2: (330, 215), 3: (360, 235), 4: (355, 275), 5: (325, 300),
    6: (280, 285), 7: (240, 265), 8: (235, 215), 9: (295, 185), 10: (355, 175),
    11: (415, 230), 12: (430, 295), 13: (370, 355), 14: (285, 365), 15: (200, 340),
    16: (140, 240), 17: (185, 155), 18: (280, 120), 19: (400, 120), 20: (475, 185),
}
MEXICO_XY = {
    1: (200, 300), 2: (285, 160), 3: (300, 265), 4: (300, 340), 5: (115, 240),
    6: (300, 215), 7: (380, 140), 8: (380, 255), 9: (430, 310), 10: (175, 355),
    11: (225, 215), 12: (340, 445), 13: (430, 400), 14: (260, 410), 15: (380, 200),
    16: (380, 380),
}


def zscore(v: np.ndarray) -> np.ndarray:
    sd = v.std(ddof=0)
    if sd == 0:
        return np.zeros_like(v)
    return (v - v.mean()) / sd


def ols_hc1(y: np.ndarray, X: np.ndarray) -> dict:
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = max(1, n - k)
    xtx_inv = np.linalg.pinv(X.T @ X)
    meat = X.T @ (X * (resid**2)[:, None])
    cov = (n / df) * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    t = beta / np.where(se > 0, se, np.nan)
    p = 2 * (1 - stats.t.cdf(np.abs(t), df))
    r2 = 1 - (resid @ resid) / np.sum((y - y.mean()) ** 2)
    return {"beta": beta, "se": se, "p": p, "r2": float(r2), "n": int(n)}


def read_mexico_sheet(sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(MEXICO_XLSX, sheet_name=sheet, header=None)
    hdr = None
    for i in range(min(20, len(raw))):
        v = raw.iloc[i, 0]
        if isinstance(v, str) and v.strip().lower().replace("í", "i") == "alcaldia":
            hdr = i
            break
    if hdr is None:
        raise ValueError(f"Missing alcaldia header in {sheet}")
    years = []
    cols = []
    for j in range(1, raw.shape[1]):
        v = raw.iloc[hdr, j]
        try:
            years.append(int(float(v)))
            cols.append(j)
        except Exception:
            continue
    rows = []
    for i in range(hdr + 1, raw.shape[0]):
        name = raw.iloc[i, 0]
        if pd.isna(name):
            continue
        rec = {"name": str(name).strip()}
        for y, j in zip(years, cols):
            val = raw.iloc[i, j]
            rec[y] = float(val) if pd.notna(val) else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def norm_name(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s).strip().lower())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")


def match_name(name: str, lookup: dict[str, float]) -> float:
    n = norm_name(name)
    if n in lookup:
        return lookup[n]
    for k, v in lookup.items():
        if n in k or k in n:
            return v
    raise KeyError(name)


def city_distance(ids: list[int], coords: dict[int, tuple[float, float]], center: int) -> np.ndarray:
    cx, cy = coords[center]
    return np.array([math.hypot(coords[i][0] - cx, coords[i][1] - cy) for i in ids], dtype=float)


def run_city(city: str) -> dict:
    if city == "paris":
        if PARIS_DATA_CSV.exists():
            rows = pd.read_csv(PARIS_DATA_CSV).to_dict(orient="records")
            uqi = np.array([r["uqi_corrected"] for r in rows], dtype=float)
            components_used = "parks,transit,density,thirdspace"
        else:
            rows = json.loads(PARIS_DATA_JSON.read_text(encoding="utf-8"))
            uqi = np.array([(r["parks"] + r["transit"] + r["density"] + r["thirdspace"] + r["pedestrian"] + r["infrastructure"]) / 6 for r in rows], dtype=float)
            components_used = "parks,transit,density,thirdspace,pedestrian,infrastructure"
        ids = [r["id"] for r in rows]
        y_raw = np.array([r["median_income_eur"] for r in rows], dtype=float)
        pop = np.array([r["population"] for r in rows], dtype=float)
        dist = city_distance(ids, PARIS_XY, center=1)
        y_label = "median_income_eur"
        city_label = "Paris"
    else:
        if MEXICO_DATA_CSV.exists():
            rows = pd.read_csv(MEXICO_DATA_CSV).to_dict(orient="records")
            uqi = np.array([r["uqi_corrected"] for r in rows], dtype=float)
            components_used = "parks,transit,density,thirdspace,infrastructure"
        else:
            rows = json.loads(MEXICO_DATA_JSON.read_text(encoding="utf-8"))
            uqi = np.array([(r["parks"] + r["transit"] + r["density"] + r["thirdspace"] + r["pedestrian"] + r["infrastructure"]) / 6 for r in rows], dtype=float)
            components_used = "parks,transit,density,thirdspace,pedestrian,infrastructure"
        ids = [r["id"] for r in rows]
        crowd = read_mexico_sheet("4. Persons per dwelling")
        pop_df = read_mexico_sheet("1. Population")
        crowd_map = {norm_name(k): float(v) for k, v in zip(crowd["name"], crowd[2020])}
        pop_map = {norm_name(k): float(v) for k, v in zip(pop_df["name"], pop_df[2020])}
        y_raw = np.array([1.0 / match_name(r["name"], crowd_map) for r in rows], dtype=float)
        pop = np.array([match_name(r["name"], pop_map) for r in rows], dtype=float)
        dist = city_distance(ids, MEXICO_XY, center=6)
        y_label = "inverse_persons_per_dwelling"
        city_label = "Mexico City"

    y = np.log(y_raw)
    z_uqi = zscore(uqi)
    z_pop = zscore(np.log(pop))
    z_dist = zscore(dist)

    # controlled
    Xc = np.column_stack([np.ones(len(y)), z_uqi, z_pop, z_dist])
    fit_c = ols_hc1(y, Xc)
    # bivariate
    Xb = np.column_stack([np.ones(len(y)), z_uqi])
    fit_b = ols_hc1(y, Xb)

    return {
        "city": city,
        "city_label": city_label,
        "outcome": y_label,
        "uqi_components_used": components_used,
        "n": fit_c["n"],
        "controlled": {
            "term": "std_uqi",
            "beta": float(fit_c["beta"][1]),
            "se": float(fit_c["se"][1]),
            "p": float(fit_c["p"][1]),
            "r2": float(fit_c["r2"]),
        },
        "bivariate": {
            "term": "std_uqi",
            "beta": float(fit_b["beta"][1]),
            "se": float(fit_b["se"][1]),
            "p": float(fit_b["p"][1]),
            "r2": float(fit_b["r2"]),
        },
        "points": [
            {
                "id": int(ids[i]),
                "name": rows[i]["name"],
                "uqi": float(uqi[i]),
                "log_outcome": float(y[i]),
            }
            for i in range(len(rows))
        ],
    }


def write_plotly_html(paris: dict, mexico: dict) -> None:
    def js_pts(d: dict) -> str:
        return json.dumps(d["points"], ensure_ascii=False)

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>UQI regression laps</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>body{{font-family:Georgia,serif;background:#f1e9d6;color:#2a2218;margin:0;padding:1.2rem}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}@media (max-width:820px){{.grid{{grid-template-columns:1fr}}}}.card{{border:1px solid #6b5d48;background:#fbf7eb;padding:0.8rem}}</style></head>
<body><h2>UQI vs log(outcome)</h2><div class="grid"><div class="card"><div id="p"></div></div><div class="card"><div id="m"></div></div></div>
<script>
const paris={js_pts(paris)}, mexico={js_pts(mexico)};
function panel(el, pts, title, color){{
 const x=pts.map(d=>d.uqi), y=pts.map(d=>d.log_outcome), t=pts.map(d=>d.name);
 const n=x.length, mx=x.reduce((a,b)=>a+b,0)/n, my=y.reduce((a,b)=>a+b,0)/n;
 let num=0, den=0; for(let i=0;i<n;i++){{ num+=(x[i]-mx)*(y[i]-my); den+=(x[i]-mx)*(x[i]-mx); }}
 const b=num/den, a=my-b*mx;
 const xline=[Math.min(...x), Math.max(...x)], yline=xline.map(v=>a+b*v);
 Plotly.newPlot(el,[{{x,y,text:t,mode:'markers',type:'scatter',marker:{{color,size:8}}}},{{x:xline,y:yline,mode:'lines',line:{{color:'#2a2218'}}}}],{{title,xaxis:{{title:'UQI'}},yaxis:{{title:'log(outcome)'}},paper_bgcolor:'#fbf7eb',plot_bgcolor:'#fbf7eb',margin:{{t:50,l:50,r:20,b:50}}}},{{displayModeBar:false}});
}}
panel('p',paris,'Paris','#7a1f2b'); panel('m',mexico,'Mexico City','#2d5a3d');
</script></body></html>"""
    OUT_HTML.write_text(html, encoding="utf-8")


def write_static_svg(paris: dict, mexico: dict) -> None:
    plt.rcParams["font.family"] = "serif"
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor="#f1e9d6")
    for ax, d, col in [(axes[0], paris, "#7a1f2b"), (axes[1], mexico, "#2d5a3d")]:
        pts = pd.DataFrame(d["points"])
        x, y = pts["uqi"].values, pts["log_outcome"].values
        ax.set_facecolor("#fbf7eb")
        ax.scatter(x, y, color=col, alpha=0.85)
        m, b = np.polyfit(x, y, 1)
        xx = np.linspace(x.min(), x.max(), 100)
        ax.plot(xx, m * xx + b, color="#2a2218", linewidth=1.5)
        ax.set_title(d["city_label"])
        ax.set_xlabel("UQI")
        ax.set_ylabel("log(outcome)")
    fig.tight_layout()
    fig.savefig(OUT_SVG)
    plt.close(fig)


def main() -> None:
    paris = run_city("paris")
    mexico = run_city("mexico")
    out = {"paris": paris, "mexico": mexico}
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    write_plotly_html(paris, mexico)
    write_static_svg(paris, mexico)

    print(
        f"Across {paris['n']} Paris arrondissements, controlled beta={paris['controlled']['beta']:.3f} "
        f"(p={paris['controlled']['p']:.3f}), R2={paris['controlled']['r2']:.2f}. "
        f"Across {mexico['n']} CDMX alcaldías, controlled beta={mexico['controlled']['beta']:.3f} "
        f"(p={mexico['controlled']['p']:.3f}), R2={mexico['controlled']['r2']:.2f}."
    )


if __name__ == "__main__":
    main()
