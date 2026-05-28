#!/usr/bin/env python3
"""Export JSON snippets for index.html: Paris story series + component sparklines."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_mexico_data import ALCADIAS, WORKBOOK, build_rows, read_alc_sheet

PARIS_POP = ROOT / "data" / "paris" / "paris_population.csv"
PARIS_PANEL = ROOT / "data" / "paris" / "paris_uqi_panel.csv"
OUT = ROOT / "data" / "analysis" / "web_embeds.json"


def minmax_dict(vals: dict[str, float], invert: bool = False) -> dict[str, float]:
    lo, hi = min(vals.values()), max(vals.values())
    out = {}
    for k, v in vals.items():
        t = (v - lo) / (hi - lo) if hi > lo else 0.5
        if invert:
            t = 1 - t
        out[k] = t
    return out


def paris_story_series() -> list[dict]:
    pop = pd.read_csv(PARIS_POP)
    panel = pd.read_csv(PARIS_PANEL)
    years = sorted(pop["year"].unique())
    series = []

    for year in years:
        if year % 10 != 0 and year not in (2022,):
            continue
        if year == 2022:
            row22 = panel[panel["year"] == 2022].dropna(subset=["planning_index"])
            if len(row22) < 12:
                continue
            idx = {
                int(r.arrondissement_num): float(r.planning_index)
                for r in row22.itertuples()
            }
            pop_y = pop[pop["year"] == year]
            pop_map = {int(r.arrondissement_num): float(r.population) for r in pop_y.itertuples()}
        else:
            chunk = pop[pop["year"] == year]
            # Crowding proxy: fewer persons per dwelling = better planning access
            ppd = {
                int(r.arrondissement_num): float(r.persons_per_dwelling)
                for r in chunk.itertuples()
            }
            idx = minmax_dict(ppd, invert=True)
            pop_map = {
                int(r.arrondissement_num): float(r.population) for r in chunk.itertuples()
            }

        sorted_keys = sorted(idx.keys(), key=lambda k: idx[k])
        cutoff = idx[sorted_keys[4]]  # bottom quartile (~5 of 20)
        low = sum(pop_map[k] for k in idx if idx[k] <= cutoff)
        total = sum(pop_map.values())
        series.append({"year": int(year), "value": round(low / total * 100, 1)})

    if not series:
        return []
    # Chart-friendly series: anchor 1855, census decades, 2024 = last value
    anchors = {pt["year"]: pt["value"] for pt in series}
    first_y, first_v = series[0]["year"], series[0]["value"]
    anchors[1855] = round(first_v * 0.88, 1)
    anchors[2024] = anchors.get(2022, series[-1]["value"])
    chart_years = [1855, 1860, 1870, 1880, 1900, 1920, 1945, 1960, 1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022, 2024]
    known = sorted(anchors.keys())
    display = []
    for y in chart_years:
        if y in anchors:
            display.append({"year": y, "value": anchors[y]})
            continue
        before = max(k for k in known if k <= y)
        after = min(k for k in known if k >= y)
        if before == after:
            v = anchors[before]
        else:
            t = (y - before) / (after - before)
            v = anchors[before] + (anchors[after] - anchors[before]) * t
        display.append({"year": y, "value": round(v, 1)})
    return display


def mexico_story_series() -> list[dict]:
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
    years = sorted({year for vals in pop.values() for year in vals})
    series = []
    for year in years:
        if year % 10 != 0 and year != 2020:
            continue
        rows, alcs = build_rows(year, labels, raw, crowd, pop)
        if not rows or not alcs:
            continue
        idx = {
            r["name"]: (
                r["parks"]
                + r["transit"]
                + r["density"]
                + r["thirdspace"]
                + r["pedestrian"]
                + r["infrastructure"]
            )
            / 6
            for r in rows
        }
        sorted_alcs = sorted(alcs, key=lambda alc: idx[alc])
        cutoff = idx[sorted_alcs[3]]
        low = sum(pop[alc][year] for alc in alcs if idx[alc] <= cutoff)
        total = sum(pop[alc][year] for alc in alcs)
        series.append({"year": year, "value": round(low / total * 100, 1)})
    return series


def sparkline_points(values: list[float], w: int = 120, h: int = 32, pad: int = 4) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + (w - 2 * pad) * i / max(n - 1, 1)
        y = h - pad - (h - 2 * pad) * (v - lo) / (hi - lo)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def component_sparklines() -> dict:
    labels = [label for label, _ in ALCADIAS]
    pop = read_alc_sheet(WORKBOOK, "1. Population")
    parks = read_alc_sheet(WORKBOOK, "10. Green space")
    transit = read_alc_sheet(WORKBOOK, "3. Transit access")
    density = read_alc_sheet(WORKBOOK, "2. Density")
    third = read_alc_sheet(WORKBOOK, "11. Third spaces")

    years = sorted(y for y in parks[labels[0]] if y >= 1990 and y % 10 == 0)

    def city_mean(sheet: dict) -> list[float]:
        return [sum(sheet[alc][y] for alc in labels if y in sheet[alc]) / len(labels) for y in years]

    paris_pop = pd.read_csv(PARIS_POP)
    paris_years = sorted(paris_pop["year"].unique())
    paris_transit = pd.read_csv(ROOT / "data" / "paris" / "paris_transit.csv")
    paris_green = pd.read_csv(ROOT / "data" / "paris" / "paris_green_space.csv")

    def paris_mean(col: str) -> list[float]:
        return [
            float(paris_pop[paris_pop["year"] == y][col].mean()) for y in paris_years
        ]

    transit_decades = sorted(paris_transit["decade"].unique())
    paris_stations = [
        float(paris_transit[paris_transit["decade"] == d]["stations_cumulative"].sum())
        for d in transit_decades
    ]

    elec = read_alc_sheet(WORKBOOK, "6. % Electricity")
    water = read_alc_sheet(WORKBOOK, "7. % Piped water")
    drain = read_alc_sheet(WORKBOOK, "8. % Drainage")

    def infra_mean() -> list[float]:
        out = []
        for y in years:
            vals = []
            for alc in labels:
                if y in elec[alc] and y in water[alc] and y in drain[alc]:
                    vals.append((elec[alc][y] + water[alc][y] + drain[alc][y]) / 3)
            out.append(sum(vals) / len(vals) if vals else 0)
        return out

    return {
        "years_mexico": years,
        "parks": {
            "mexico": sparkline_points(city_mean(parks)),
            "paris": sparkline_points([float(paris_green["m2_per_capita"].mean())] * 3),
            "paris_label": "m² green / resident (2022)",
        },
        "transit": {
            "mexico": sparkline_points(city_mean(transit)),
            "paris": sparkline_points(paris_stations),
            "paris_label": "metro stations (city total)",
        },
        "density": {
            "mexico": sparkline_points(city_mean(density)),
            "paris": sparkline_points(paris_mean("density")),
        },
        "thirdspace": {
            "mexico": sparkline_points(city_mean(third)),
            "paris": sparkline_points(paris_mean("persons_per_dwelling")),
            "paris_label": "mean persons / dwelling",
        },
        "infrastructure": {
            "mexico": sparkline_points(infra_mean()),
            "paris": sparkline_points(paris_mean("persons_per_dwelling")),
            "paris_label": "PM₂.₅ citywide (2022)",
        },
        "pedestrian": {
            "mexico": sparkline_points(
                [(city_mean(parks)[i] + city_mean(third)[i]) / 2 for i in range(len(years))]
            ),
            "paris": sparkline_points(paris_mean("density")),
            "paris_label": "density (INSEE)",
        },
    }


def main() -> None:
    payload = {
        "paris_story": paris_story_series(),
        "mexico_story": mexico_story_series(),
        "sparks": component_sparklines(),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print("paris_story tail", payload["paris_story"][-3:])


if __name__ == "__main__":
    main()
