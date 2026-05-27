#!/usr/bin/env python3
"""Run cross-section regressions and export JSON + regression scatter page."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
OUT_JSON = ROOT / "data" / "regression_results.json"
OUT_HTML = ROOT / "figures" / "regression-laps.html"
OUT_PARIS_JS = ROOT / "data" / "paris" / "paris_index_2022.json"

# Spiral layout centroids (match index.html LAYOUTS paris)
PARIS_XY = {
    1: (300, 240),
    2: (330, 215),
    3: (360, 235),
    4: (355, 275),
    5: (325, 300),
    6: (280, 285),
    7: (240, 265),
    8: (235, 215),
    9: (295, 185),
    10: (355, 175),
    11: (415, 230),
    12: (430, 295),
    13: (370, 355),
    14: (285, 365),
    15: (200, 340),
    16: (140, 240),
    17: (185, 155),
    18: (280, 120),
    19: (400, 120),
    20: (475, 185),
}

MEXICO_XY = {
    1: (200, 300),
    2: (285, 160),
    3: (300, 265),
    4: (300, 340),
    5: (115, 240),
    6: (300, 215),
    7: (380, 140),
    8: (380, 255),
    9: (430, 310),
    10: (175, 355),
    11: (225, 215),
    12: (340, 445),
    13: (430, 400),
    14: (260, 410),
    15: (380, 200),
    16: (380, 380),
}


def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or lo == hi:
        out = pd.Series(50.0, index=series.index)
    else:
        out = (s - lo) / (hi - lo) * 100
    if invert:
        out = 100 - out
    return out.round(1)


def zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=0)
    if sd == 0:
        return np.zeros_like(x)
    return (x - x.mean()) / sd


def ols(y: np.ndarray, X: np.ndarray) -> dict:
    """OLS with HC1 robust SEs (simple sandwich)."""
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = max(n - k, 1)
    s2 = (resid @ resid) / df
    XtX_inv = np.linalg.pinv(X.T @ X)
    cov = s2 * XtX_inv @ X.T @ X @ XtX_inv
    # HC1
    meat = X.T @ (X * (resid**2)[:, None])
    scale = n / df
    cov_rob = scale * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.maximum(np.diag(cov_rob), 0))
    t = beta / np.where(se > 0, se, np.nan)
    from scipy import stats

    p = 2 * (1 - stats.t.cdf(np.abs(t), df))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) ** 2).sum()
    return {
        "beta": beta.tolist(),
        "se": se.tolist(),
        "p": p.tolist(),
        "r2": float(r2),
        "n": int(n),
    }


def pct_from_log_beta(b: float) -> float:
    return round((math.exp(b) - 1) * 100, 1)


def corr(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(num / (dx * dy), 2) if dx and dy else 0.0


def dist_center(ids: list[int], xy: dict[int, tuple[float, float]], center_id: int) -> list[float]:
    cx, cy = xy[center_id]
    return [math.hypot(xy[i][0] - cx, xy[i][1] - cy) for i in ids]


def build_paris_rows() -> list[dict]:
    panel = pd.read_csv(PARIS / "paris_uqi_panel.csv")
    cross = panel[panel["year"] == 2022].copy()
    cross["parks"] = minmax(cross["green_space_m2_per_capita"])
    cross["transit"] = minmax(cross["transit_access_per_100k"])
    cross["density"] = minmax(cross["density"])
    cross["thirdspace"] = minmax(cross["third_spaces_per_100k"])
    cross["infrastructure"] = minmax(cross["pm25_annual_mean"], invert=True)
    cross["pedestrian"] = ((cross["parks"] + cross["thirdspace"]) / 2).round(1)
    cross["income"] = minmax(cross["median_income_eur"])
    rows = []
    for _, r in cross.sort_values("arrondissement_num").iterrows():
        rows.append(
            {
                "id": int(r["arrondissement_num"]),
                "name": r["arrondissement"],
                "parks": float(r["parks"]),
                "transit": float(r["transit"]),
                "density": float(r["density"]),
                "thirdspace": float(r["thirdspace"]),
                "pedestrian": float(r["pedestrian"]),
                "infrastructure": float(r["infrastructure"]),
                "income": float(r["income"]),
                "median_income_eur": float(r["median_income_eur"]),
                "population": float(r["population"]),
            }
        )
    return rows


def build_mexico_rows() -> tuple[list[dict], dict[str, float]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from export_mexico_data import ALCADIAS, WORKBOOK, build_rows, read_alc_sheet

    labels = [label for label, _ in ALCADIAS]
    var_sheets = {
        "parks": "10. Green space",
        "transit": "3. Transit access",
        "density": "2. Density",
        "thirdspace": "11. Third spaces",
        "elec": "6. % Electricity",
        "water": "7. % Piped water",
        "drain": "8. % Drainage",
        "hosp": "9. Hospital access",
    }
    pop = read_alc_sheet(WORKBOOK, "1. Population")
    raw = {var: read_alc_sheet(WORKBOOK, sheet) for var, sheet in var_sheets.items()}
    crowd = read_alc_sheet(WORKBOOK, "4. Persons per dwelling")
    rows2020, _ = build_rows(2020, labels, raw, crowd, pop)
    raw_crowd = {alc: crowd[alc][2020] for alc in crowd if 2020 in crowd[alc]}
    return rows2020, raw_crowd


def region_index(row: dict) -> float:
    keys = ["parks", "transit", "density", "thirdspace", "pedestrian", "infrastructure"]
    return sum(row[k] for k in keys) / len(keys)


def run_city_regression(
    city: str,
    rows: list[dict],
    y_key: str,
    center_id: int,
    xy: dict[int, tuple[float, float]],
) -> dict:
    ids = [r["id"] for r in rows]
    y = np.log(np.array([r[y_key] for r in rows], dtype=float))
    index = np.array([region_index(r) for r in rows])
    pop = np.log(np.array([r["population"] for r in rows], dtype=float))
    dist = np.array(dist_center(ids, xy, center_id))

    z_idx = zscore(index)
    z_pop = zscore(pop)
    z_dist = zscore(dist)
    X = np.column_stack([np.ones(len(rows)), z_idx, z_pop, z_dist])
    fit = ols(y, X)
    beta_idx = fit["beta"][1]
    return {
        "city": city,
        "n": fit["n"],
        "r2": round(fit["r2"], 3),
        "beta_index": round(beta_idx, 3),
        "beta_index_se": round(fit["se"][1], 3),
        "p_index": round(fit["p"][1], 4),
        "pct_change_per_sd": pct_from_log_beta(beta_idx),
        "correlation_r": corr(index.tolist(), y.tolist()),
        "y_label": y_key,
        "points": [
            {
                "id": r["id"],
                "name": r["name"],
                "index": round(region_index(r), 1),
                "y": float(r[y_key]),
                "log_y": float(math.log(r[y_key])),
            }
            for r in rows
        ],
    }


def scatter_svg(points: list[dict], city: str, accent: str) -> str:
    w, h, pad = 520, 360, 48
    xs = [p["index"] for p in points]
    ys = [p["log_y"] for p in points]
    xmin, xmax = min(xs) - 5, max(xs) + 5
    ymin, ymax = min(ys) - 0.1, max(ys) + 0.1

    def sx(x):
        return pad + (x - xmin) / (xmax - xmin) * (w - 2 * pad)

    def sy(y):
        return h - pad - (y - ymin) / (ymax - ymin) * (h - 2 * pad)

    dots = "\n".join(
        f'<circle cx="{sx(p["index"]):.1f}" cy="{sy(p["log_y"]):.1f}" r="5" fill="{accent}" opacity="0.85"><title>{p["name"]}</title></circle>'
        for p in points
    )
    return f"""<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{city} regression scatter">
  <rect width="100%" height="100%" fill="#f8f2e4"/>
  <text x="{pad}" y="24" font-family="Georgia, serif" font-size="14" fill="#2a2218">{city}: log outcome vs planning index</text>
  <line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#6b5d48"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="#6b5d48"/>
  <text x="{w/2:.0f}" y="{h-12}" text-anchor="middle" font-size="11" fill="#4a3f30">Planning index (0–100)</text>
  <text transform="translate(16 {h/2:.0f}) rotate(-90)" font-size="11" fill="#4a3f30">log(median income / proxy)</text>
  {dots}
</svg>"""


def write_laps_html(paris: dict, mexico: dict) -> None:
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ECON 30 · Regression laps</title>
  <style>
    body {{ margin:0; padding:2rem; background:#f1e9d6; color:#2a2218; font-family:Georgia,serif; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; max-width:1100px; margin:0 auto; }}
    @media (max-width:800px) {{ .grid {{ grid-template-columns:1fr; }} }}
    .card {{ border:1px solid #6b5d48; padding:1rem; background:rgba(255,255,255,.25); }}
    .stat {{ font-size:1.4rem; margin:0.4rem 0; }}
    a {{ color:#2a2218; }}
  </style>
</head>
<body>
  <h1>Regression laps · 2020 cross-section</h1>
  <p>log(outcome) ~ standardized index + population + distance to map center. <a href="../index.html#findings">Back to main story</a></p>
  <div class="grid">
    <div class="card">
      <h2>Paris (Filosofi 2021 median income)</h2>
      <p class="stat">β = {paris['beta_index']:+.3f} · ≈ {paris['pct_change_per_sd']:+.1f}% per 1 SD index · R² = {paris['r2']}</p>
      {scatter_svg(paris['points'], 'Paris', '#7a1f2b')}
    </div>
    <div class="card">
      <h2>Mexico City (inverse crowding proxy)</h2>
      <p class="stat">β = {mexico['beta_index']:+.3f} · ≈ {mexico['pct_change_per_sd']:+.1f}% per 1 SD · r = {mexico['correlation_r']:+.2f}</p>
      {scatter_svg(mexico['points'], 'Mexico City', '#2d5a3d')}
    </div>
  </div>
</body>
</html>"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(body, encoding="utf-8")


def main() -> None:
    paris_rows = build_paris_rows()
    OUT_PARIS_JS.write_text(
        json.dumps(paris_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    mexico_rows, raw_crowd = build_mexico_rows()
    sys.path.insert(0, str(ROOT / "scripts"))
    from export_mexico_data import WORKBOOK, read_alc_sheet

    pop = read_alc_sheet(WORKBOOK, "1. Population")
    for r in mexico_rows:
        r["crowding"] = raw_crowd[r["name"]]
        r["crowding_proxy"] = 1.0 / max(r["crowding"], 0.01)
    for r in mexico_rows:
        r["population"] = pop[r["name"]][2020]

    paris_fit = run_city_regression(
        "paris",
        paris_rows,
        "median_income_eur",
        center_id=1,
        xy=PARIS_XY,
    )
    mexico_fit = run_city_regression(
        "mexico",
        mexico_rows,
        "crowding_proxy",
        center_id=6,
        xy=MEXICO_XY,
    )

    results = {
        "paris": paris_fit,
        "mexico": mexico_fit,
        "paris_data_rows": [
            {k: v for k, v in r.items() if k not in ("median_income_eur", "population")}
            for r in paris_rows
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_laps_html(paris_fit, mexico_fit)

    print("Paris beta", paris_fit["beta_index"], "pct", paris_fit["pct_change_per_sd"])
    print("Mexico beta", mexico_fit["beta_index"], "r", mexico_fit["correlation_r"])
    print("Wrote", OUT_JSON, OUT_HTML, OUT_PARIS_JS)


if __name__ == "__main__":
    main()
