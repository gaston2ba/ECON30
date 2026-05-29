#!/usr/bin/env python3
"""Export Paris arrondissement panel JSON for the interactive UQI map (Andres-style)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
OUT_DIR = ROOT / "paris" / "data"
GEO_SRC = ROOT / "data" / "maps" / "paris_arrondissements.geojson"

YEARS = [1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022]

VARIABLES = [
    {
        "key": "population",
        "label": "Population",
        "unit": "residents",
        "higherIsBetter": False,
        "defaultSelected": False,
        "description": "INSEE census population by arrondissement.",
    },
    {
        "key": "density",
        "label": "Population density",
        "unit": "people/km²",
        "higherIsBetter": False,
        "defaultSelected": True,
        "description": "Residents per km²; higher density scores as more pressure in the default UQI.",
    },
    {
        "key": "persons_per_dwelling",
        "label": "Persons per dwelling",
        "unit": "persons",
        "higherIsBetter": False,
        "defaultSelected": True,
        "description": "Household crowding proxy from INSEE housing tables.",
    },
    {
        "key": "transit_access",
        "label": "Metro access",
        "unit": "stations/100k",
        "higherIsBetter": True,
        "defaultSelected": True,
        "description": "Cumulative metro stations opened by decade (Wikidata/OSM), per 100k residents.",
    },
    {
        "key": "green_space",
        "label": "Green space",
        "unit": "m²/resident",
        "higherIsBetter": True,
        "defaultSelected": True,
        "description": "Public green m² per resident (Paris Open Data, 2022 snapshot applied where available).",
    },
    {
        "key": "third_spaces",
        "label": "Third spaces",
        "unit": "per 100k",
        "higherIsBetter": True,
        "defaultSelected": False,
        "description": "Libraries + museums per 100k residents (2022 snapshot).",
    },
    {
        "key": "median_income",
        "label": "Median income",
        "unit": "€/year",
        "higherIsBetter": True,
        "defaultSelected": False,
        "description": "Filosofi 2021 median disposable income (2022 panel year only).",
    },
]


def transit_for_year(transit: pd.DataFrame, year: int) -> pd.DataFrame:
    """Nearest decade at or before census year."""
    decades = sorted(transit["decade"].unique())
    use = max(d for d in decades if d <= year)
    return transit[transit["decade"] == use][["arrondissement_num", "stations_cumulative"]]


def main() -> None:
    pop = pd.read_csv(PARIS / "paris_population.csv")
    transit = pd.read_csv(PARIS / "paris_transit.csv")
    green = pd.read_csv(PARIS / "paris_green_space.csv")
    third = pd.read_csv(PARIS / "paris_third_spaces.csv")
    income = pd.read_csv(PARIS / "paris_income.csv")

    green = green.rename(columns={"m2_per_capita": "green_space"})
    third = third.rename(columns={"total_per_100k": "third_spaces"})
    income = income.rename(columns={"median_income": "median_income_eur"})

    arrondissements = []
    for arr_name in pop["arrondissement"].unique():
        rec = {"name": arr_name, "values": {}}
        for year in YEARS:
            y = str(year)
            prow = pop[(pop["arrondissement"] == arr_name) & (pop["year"] == year)]
            if prow.empty:
                continue
            row = prow.iloc[0]
            trow = transit_for_year(transit[transit["arrondissement"] == arr_name], year)
            stations = float(trow.iloc[0]["stations_cumulative"]) if not trow.empty else None
            pop_n = float(row["population"])
            transit_access = (stations / pop_n * 100_000) if stations is not None and pop_n else None

            gmatch = green[green["arrondissement"] == arr_name]
            green_val = float(gmatch.iloc[0]["green_space"]) if not gmatch.empty and year == 2022 else None

            tmatch = third[third["arrondissement"] == arr_name]
            third_val = float(tmatch.iloc[0]["third_spaces"]) if not tmatch.empty and year == 2022 else None

            imatch = income[income["arrondissement"] == arr_name]
            income_val = float(imatch.iloc[0]["median_income_eur"]) if not imatch.empty and year == 2022 else None

            rec["values"][y] = {
                "population": float(row["population"]),
                "density": float(row["density"]),
                "persons_per_dwelling": float(row["persons_per_dwelling"]),
                "transit_access": transit_access,
                "green_space": green_val,
                "third_spaces": third_val,
                "median_income": income_val,
            }
        arrondissements.append(rec)

    payload = {
        "city": "Paris",
        "decades": [str(y) for y in YEARS],
        "variables": VARIABLES,
        "arrondissements": arrondissements,
        "sourceNotes": {
            "population": "INSEE dossier complet, arrondissement tables.",
            "transit_access": "Metro opening years from Wikidata/OSM; cumulative stations by decade.",
            "green_space": "opendata.paris.fr espaces verts, 2022 only.",
            "third_spaces": "Libraries + museums per 100k, 2022 only.",
            "median_income": "INSEE Filosofi 2021, 2022 panel year only.",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "uqi-by-arrondissement.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    shutil.copy2(GEO_SRC, OUT_DIR / "arrondissements.geojson")
    print("wrote", OUT_DIR / "uqi-by-arrondissement.json")
    print("decades", payload["decades"])
    print("arrondissements", len(arrondissements))


if __name__ == "__main__":
    main()
