#!/usr/bin/env python3
"""Compute arrondissement HDI (2020) using UN HDR 2022 geometric-mean methodology."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
OUT = PARIS / "hdi-by-arrondissement.json"
METH = PARIS / "hdi-methodology.md"
RAW = PARIS / "raw" / "life_expectancy_arrondissement.csv"

# Institut Paris Région / ORS-IDF 2021 anchors (years)
LE_ANCHORS = {16: 87.1, 18: 82.5, 7: 86.2, 8: 85.8, 19: 82.8, 20: 82.2, 1: 84.2, 13: 83.1}
PPP_EUR_PER_USD_PPP = 0.738  # OECD France 2021 approx.

DECADES = [str(y) for y in range(1870, 2030, 10)]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def gmean3(a: float, b: float, c: float) -> float:
    return (a * b * c) ** (1 / 3)


def interpolate_le(income: pd.Series) -> dict[int, float]:
    """Fill 20 arrondissements from anchors + income rank."""
    if RAW.exists():
        df = pd.read_csv(RAW)
        return {int(r.arrondissement_num): float(r.life_expectancy) for r in df.itertuples()}
    known = {k: LE_ANCHORS[k] for k in LE_ANCHORS}
    out = {}
    inc = income.set_index("arrondissement_num")["median_income"]
    lo, hi = inc.min(), inc.max()
    for arr in range(1, 21):
        if arr in known:
            out[arr] = known[arr]
        else:
            t = (inc[arr] - lo) / (hi - lo) if hi > lo else 0.5
            out[arr] = 82.0 + t * (87.1 - 82.0)
    return out


def education_indices(income: pd.Series) -> tuple[dict[int, float], dict[int, float]]:
    """MYS/EYS proxies from income rank when diploma tables unavailable."""
    inc = income.set_index("arrondissement_num")["median_income"]
    lo, hi = inc.min(), inc.max()
    mys, eys = {}, {}
    for arr in range(1, 21):
        t = (inc[arr] - lo) / (hi - lo) if hi > lo else 0.5
        mys[arr] = 9 + t * 7  # 9–16 years
        eys[arr] = 12 + t * 4  # 12–16 years proxy
    return mys, eys


def hdi_row(le: float, mys: float, eys: float, income_eur: float) -> dict:
    life_i = clamp((le - 20) / (85 - 20))
    mys_i = clamp(mys / 15)
    eys_i = clamp(eys / 18)
    edu_i = (mys_i + eys_i) / 2
    gni_ppp = income_eur / PPP_EUR_PER_USD_PPP
    inc_i = clamp((math.log(gni_ppp) - math.log(100)) / (math.log(75000) - math.log(100)))
    hdi = gmean3(life_i, edu_i, inc_i)
    return {
        "hdi": round(hdi, 4),
        "life_exp_index": round(life_i, 4),
        "education_index": round(edu_i, 4),
        "income_index": round(inc_i, 4),
        "life_expectancy": round(le, 2),
        "mean_years_schooling": round(mys, 2),
        "expected_years_schooling": round(eys, 2),
        "gni_per_capita_ppp": round(gni_ppp, 0),
    }


def main() -> None:
    income = pd.read_csv(PARIS / "paris_income.csv")
    le = interpolate_le(income)
    mys_map, eys_map = education_indices(income)
    names = {
        i: n for i, n in [
            (1, "1er Louvre"), (2, "2e Bourse"), (3, "3e Temple"), (4, "4e Hôtel-de-Ville"),
            (5, "5e Panthéon"), (6, "6e Luxembourg"), (7, "7e Palais-Bourbon"), (8, "8e Élysée"),
            (9, "9e Opéra"), (10, "10e Entrepôt"), (11, "11e Popincourt"), (12, "12e Reuilly"),
            (13, "13e Gobelins"), (14, "14e Observatoire"), (15, "15e Vaugirard"), (16, "16e Passy"),
            (17, "17e Batignolles"), (18, "18e Buttes-Montmartre"), (19, "19e Buttes-Chaumont"),
            (20, "20e Ménilmontant"),
        ]
    }
    inc_map = {int(r.arrondissement_num): float(r.median_income) for r in income.itertuples()}
    arrondissements = []
    for arr in range(1, 21):
        row2020 = hdi_row(le[arr], mys_map[arr], eys_map[arr], inc_map[arr])
        values = {d: None for d in DECADES}
        values["2020"] = row2020
        values["2010"] = {**row2020, "hdi": round(row2020["hdi"] - 0.02, 4)}  # rough backcast
        arrondissements.append({"name": names[arr], "id": arr, "values": values})

    payload = {
        "title": "Paris Human Development Index",
        "description": "Arrondissement HDI 2020 (2010 rough backcast) via UN HDR 2022 geometric mean.",
        "decades": DECADES,
        "variables": [{"key": "hdi", "label": "HDI", "unit": "index", "higherIsBetter": True, "defaultSelected": True}],
        "arrondissements": arrondissements,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    METH.write_text(
        "# Paris arrondissement HDI methodology\n\n"
        "UN HDR 2022: geometric mean of life expectancy, education, and income indices.\n"
        f"PPP conversion: EUR / {PPP_EUR_PER_USD_PPP} = 2017 intl $ PPP.\n"
        "Life expectancy: ORS-IDF / Institut Paris Région 2021 anchors; others income-interpolated.\n"
        "Education: MYS/EYS proxies from Filosofi income rank (diploma tables not in pipeline).\n",
        encoding="utf-8",
    )
    ranked = sorted([(a["name"], a["values"]["2020"]["hdi"]) for a in arrondissements], key=lambda x: -x[1])
    print("Top:", ranked[:3])
    print("Bottom:", ranked[-3:])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
