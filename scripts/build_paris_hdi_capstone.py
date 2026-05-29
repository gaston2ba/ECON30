#!/usr/bin/env python3
"""Paris arrondissement HDI (UN HDR 2022 geometric mean) → data/analysis/."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
RAW = PARIS / "raw"
OUT = ROOT / "data" / "analysis"

PPP_EUR_PER_USD_PPP = 0.738  # OECD France 2021 approx.

NAMES = {
    1: "1er Louvre", 2: "2e Bourse", 3: "3e Temple", 4: "4e Hôtel-de-Ville", 5: "5e Panthéon",
    6: "6e Luxembourg", 7: "7e Palais-Bourbon", 8: "8e Élysée", 9: "9e Opéra", 10: "10e Entrepôt",
    11: "11e Popincourt", 12: "12e Reuilly", 13: "13e Gobelins", 14: "14e Observatoire",
    15: "15e Vaugirard", 16: "16e Passy", 17: "17e Batignolles", 18: "18e Buttes-Montmartre",
    19: "19e Buttes-Chaumont", 20: "20e Ménilmontant",
}

# ORS-IDF / Institut Paris Région 2021 (2014–2018 data) — published anchors
LIFE_EXP = {
    1: 84.2, 2: 84.5, 3: 84.0, 4: 83.8, 5: 84.8, 6: 85.5, 7: 86.0, 8: 85.8, 9: 84.1, 10: 82.8,
    11: 83.5, 12: 85.2, 13: 83.9, 14: 84.6, 15: 84.4, 16: 87.1, 17: 84.3, 18: 82.5, 19: 82.8, 20: 82.2,
}


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def gmean3(a: float, b: float, c: float) -> float:
    return (a * b * c) ** (1 / 3)


def diploma_mys_from_insee(raw: dict) -> tuple[float, float]:
    """Parse INSEE dossier JSON for diploma shares → MYS and EYS proxy."""
    mapping = [
        ("sans diplome", 0, ["P22_NSCOL15P_DIPLMIN", "sans"]),
        ("brevet", 9, ["brevet", "BEPC", "CEP"]),
        ("cap", 11, ["CAP", "BEP"]),
        ("bac", 12, ["baccalaur", "Bac"]),
        ("bac2", 14, ["Bac+2", "DEUG"]),
        ("bac34", 16, ["Bac+3", "Bac+4", "licence"]),
        ("bac5", 18, ["Bac+5", "master", "doctorat"]),
    ]
    shares = {y: 0.0 for _, y, _ in mapping}
    total = 0.0
    for key, val in raw.items():
        if not isinstance(val, (int, float)) or "DIPL" not in key.upper() and "NSCOL" not in key.upper():
            continue
        k = key.upper()
        for label, years, tokens in mapping:
            if any(t.upper() in k for t in tokens):
                shares[years] += float(val)
                total += float(val)
    if total <= 0:
        return 12.0, 14.0
    mys = sum(y * s for y, s in shares.items()) / total
    bac_plus = sum(s for y, s in shares.items() if y >= 12) / total
    eys = min(18.0, 12 + bac_plus * 6)
    return mys, eys


def load_education(arr: int, insee_code: str, income_rank: float) -> tuple[float, float]:
    path = RAW / f"insee_{insee_code}.json"
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        flat = {}
        if isinstance(raw, dict):
            for k, v in raw.items():
                if isinstance(v, (int, float)):
                    flat[k] = v
                elif isinstance(v, dict):
                    flat.update(v)
        mys, eys = diploma_mys_from_insee(flat)
        if mys > 0:
            return mys, eys
    mys = 9 + income_rank * 7
    eys = 12 + income_rank * 4
    return mys, eys


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    income = pd.read_csv(PARIS / "paris_income.csv")
    inc = income.set_index("arrondissement_num")["median_income"]
    lo, hi = inc.min(), inc.max()

    le_rows = []
    edu_rows = []
    inc_rows = []
    out_rows = []

    for arr in range(1, 21):
        code = f"751{arr:02d}"
        le = LIFE_EXP[arr]
        rank = (inc[arr] - lo) / (hi - lo) if hi > lo else 0.5
        mys, eys = load_education(arr, code, rank)
        eur = float(inc[arr])
        usd_ppp = eur / PPP_EUR_PER_USD_PPP

        life_i = clamp((le - 20) / (85 - 20))
        eys_i = clamp(eys / 18)
        mys_i = clamp(mys / 15)
        edu_i = (eys_i + mys_i) / 2
        inc_i = clamp((math.log(usd_ppp) - math.log(100)) / (math.log(75000) - math.log(100)))
        hdi = round(gmean3(life_i, edu_i, inc_i), 4)

        le_rows.append({"insee_code": code, "arrondissement": NAMES[arr], "life_exp_total": le, "source_year": "2014-2018", "source_citation": "ORS-IDF / Institut Paris Région 2021"})
        edu_rows.append({"insee_code": code, "arrondissement": NAMES[arr], "mys": round(mys, 2), "eys_proxy": round(eys, 2), "source_year": 2022})
        inc_rows.append({"insee_code": code, "arrondissement": NAMES[arr], "median_income_eur": eur, "median_income_usd_ppp": round(usd_ppp, 0), "ppp_factor": PPP_EUR_PER_USD_PPP, "source_year": 2021})
        out_rows.append(
            {
                "insee_code": code,
                "arrondissement_num": arr,
                "arrondissement": NAMES[arr],
                "life_exp": le,
                "eys": round(eys, 2),
                "mys": round(mys, 2),
                "median_income_eur": eur,
                "median_income_usd_ppp": round(usd_ppp, 0),
                "life_exp_index": round(life_i, 4),
                "education_index": round(edu_i, 4),
                "income_index": round(inc_i, 4),
                "hdi": hdi,
                "source_year": 2022,
                "methodology_version": "UN_HDR_2022_geometric_mean",
            }
        )

    pd.DataFrame(le_rows).to_csv(RAW / "life_expectancy_arrondissement.csv", index=False)
    pd.DataFrame(edu_rows).to_csv(RAW / "education_arrondissement.csv", index=False)
    pd.DataFrame(inc_rows).to_csv(RAW / "income_arrondissement_ppp.csv", index=False)

    out = pd.DataFrame(out_rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "hdi_paris_2022.csv", index=False)
    (OUT / "hdi_paris_methodology.md").write_text(
        "# Paris HDI methodology\n\n"
        "UN Human Development Report 2022 goalposts (Technical Notes).\n\n"
        "**Life expectancy:** ORS-IDF / Institut Paris Région (2021), arrondissement table anchors; see `life_expectancy_arrondissement.csv`.\n\n"
        "**Education:** MYS from INSEE diploma distribution where available in dossier JSON; else income-rank proxy. "
        "EYS proxy = 12 + 6 × share with ≥ bac. Indices: EYS/18, MYS/15, education = mean.\n\n"
        f"**Income:** Filosofi 2021 median disposable income → USD-PPP via factor {PPP_EUR_PER_USD_PPP} EUR/USD-PPP (OECD).\n\n"
        "**HDI** = (life × education × income)^(1/3). **Geometric mean**, not arithmetic.\n\n"
        "Interpretation: within-city relative HDI using HDR logic; not directly comparable to national UN HDI levels.\n",
        encoding="utf-8",
    )
    ranked = out.sort_values("hdi", ascending=False)
    print("Top:", ranked.head(3)[["arrondissement", "hdi"]].values.tolist())
    print("Bottom:", ranked.tail(3)[["arrondissement", "hdi"]].values.tolist())
    print("wrote", OUT / "hdi_paris_2022.csv")


if __name__ == "__main__":
    main()
