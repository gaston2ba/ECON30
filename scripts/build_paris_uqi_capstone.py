#!/usr/bin/env python3
"""Paris 5-component UQI for capstone → data/analysis/uqi_paris_2022.csv (+ optional panel)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
OUT = ROOT / "data" / "analysis"

ARR_AREA = {
    1: 1.826, 2: 0.992, 3: 1.171, 4: 1.601, 5: 2.541, 6: 2.154, 7: 4.088, 8: 3.881,
    9: 2.179, 10: 2.892, 11: 3.666, 12: 6.377, 13: 7.146, 14: 5.621, 15: 8.502, 16: 7.846,
    17: 5.669, 18: 6.005, 19: 6.786, 20: 5.984,
}

NAMES = {
    1: "1er Louvre", 2: "2e Bourse", 3: "3e Temple", 4: "4e Hôtel-de-Ville", 5: "5e Panthéon",
    6: "6e Luxembourg", 7: "7e Palais-Bourbon", 8: "8e Élysée", 9: "9e Opéra", 10: "10e Entrepôt",
    11: "11e Popincourt", 12: "12e Reuilly", 13: "13e Gobelins", 14: "14e Observatoire",
    15: "15e Vaugirard", 16: "16e Passy", 17: "17e Batignolles", 18: "18e Buttes-Montmartre",
    19: "19e Buttes-Chaumont", 20: "20e Ménilmontant",
}


def score_higher(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    return series.apply(lambda v: round((v - lo) / (hi - lo) * 100, 2) if hi > lo else 50.0)


def score_density(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    return series.apply(lambda v: round((1 - 2 * abs(((v - lo) / (hi - lo) if hi > lo else 0.5) - 0.5)) * 100, 2))


def score_lower_pm(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    return series.apply(lambda v: round((hi - v) / (hi - lo) * 100, 2) if hi > lo else 50.0)


def main() -> None:
    pop = pd.read_csv(PARIS / "paris_population.csv")
    pop22 = pop[pop["year"] == 2022]
    green = pd.read_csv(PARIS / "paris_green_space.csv")
    transit = pd.read_csv(PARIS / "paris_transit.csv")
    transit20 = transit[transit["decade"] == 2020]
    third = pd.read_csv(PARIS / "paris_third_spaces.csv")
    air = pd.read_csv(PARIS / "paris_air_quality.csv")

    rows = []
    for arr in range(1, 21):
        p = float(pop22.loc[pop22["arrondissement_num"] == arr, "population"].iloc[0])
        dens = p / ARR_AREA[arr]
        g = float(green.loc[green["arrondissement_num"] == arr, "m2_per_capita"].iloc[0])
        st = float(transit20.loc[transit20["arrondissement_num"] == arr, "stations_cumulative"].iloc[0])
        transit_per_100k = st / p * 100_000
        t = float(third.loc[third["arrondissement_num"] == arr, "total_per_100k"].iloc[0])
        pm = float(air.loc[air["arrondissement_num"] == arr, "pm25_annual_mean"].iloc[0])
        rows.append(
            {
                "arrondissement_num": arr,
                "insee_code": f"751{arr:02d}",
                "arrondissement": NAMES[arr],
                "population_2022": p,
                "density_raw": dens,
                "parks_raw": g,
                "transit_raw": transit_per_100k,
                "thirdspace_raw": t,
                "pm25_raw": pm,
            }
        )

    df = pd.DataFrame(rows)
    df["parks"] = score_higher(df["parks_raw"])
    df["transit"] = score_higher(df["transit_raw"])
    df["density"] = score_density(df["density_raw"])
    df["thirdspace"] = score_higher(df["thirdspace_raw"])
    df["infrastructure"] = score_lower_pm(df["pm25_raw"])
    df["uqi"] = df[["parks", "transit", "density", "thirdspace", "infrastructure"]].mean(axis=1).round(2)

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "uqi_paris_2022.csv", index=False)

    panel_rows = []
    hist = pd.read_csv(PARIS / "historical" / "paris_population_long.csv") if (PARIS / "historical" / "paris_population_long.csv").exists() else pop
    for year in sorted(hist["year"].unique()):
        if year < 1968:
            continue
        sub = hist[hist["year"] == year]
        d = {int(r.arrondissement_num): float(r.population) / ARR_AREA[int(r.arrondissement_num)] for r in sub.itertuples()}
        dens_s = score_density(pd.Series(d))
        for arr in range(1, 21):
            base = df[df["arrondissement_num"] == arr].iloc[0]
            panel_rows.append(
                {
                    "arrondissement_num": arr,
                    "arrondissement": NAMES[arr],
                    "year": int(year),
                    "parks": base["parks"],
                    "transit": base["transit"],
                    "density": dens_s[arr],
                    "thirdspace": base["thirdspace"],
                    "infrastructure": base["infrastructure"],
                    "uqi": round((base["parks"] + base["transit"] + dens_s[arr] + base["thirdspace"] + base["infrastructure"]) / 5, 2),
                }
            )
    pd.DataFrame(panel_rows).to_csv(OUT / "uqi_paris_panel.csv", index=False)

    meth = ROOT / "methodology_paris.md"
    meth.write_text(
        "# Paris UQI methodology (capstone)\n\n"
        "Five components (2022 census year):\n"
        "- **Parks:** m² green per capita (`paris_green_space.csv`, opendata.paris.fr espaces verts).\n"
        "- **Transit:** cumulative métro stations per 100k (`paris_transit.csv`, Wikidata/OSM).\n"
        "- **Density:** INSEE 2022 population / fixed arrondissement area; U-shaped score (middle best).\n"
        "- **Third spaces:** libraries + museums per 100k (`paris_third_spaces.csv`).\n"
        "- **Infrastructure:** inverse PM₂.₅ (`paris_air_quality.csv`, Airparif citywide proxy 9 µg/m³ all arrondissements — no arrondissement breakdown; scores tie at 100).\n\n"
        "UQI = mean of five component scores (0–100).\n",
        encoding="utf-8",
    )
    print("wrote", OUT / "uqi_paris_2022.csv", "UQI", df["uqi"].min(), "-", df["uqi"].max())


if __name__ == "__main__":
    main()
