#!/usr/bin/env python3
"""Build data/paris/uqi-by-arrondissement.json (CDMX-compatible shape, 11 variables)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS = ROOT / "data" / "paris"
CDMX_REF = ROOT / "data" / "cdmx" / "uqi-by-alcaldia.json"
OUT = PARIS / "uqi-by-arrondissement.json"

DECADES = [str(y) for y in range(1870, 2030, 10)]

ARR_AREA_KM2 = {
    1: 1.826, 2: 0.992, 3: 1.171, 4: 1.601, 5: 2.541, 6: 2.154, 7: 4.088, 8: 3.881,
    9: 2.179, 10: 2.892, 11: 3.666, 12: 6.377, 13: 7.146, 14: 5.621, 15: 8.502, 16: 7.846,
    17: 5.669, 18: 6.005, 19: 6.786, 20: 5.984,
}

ARR_NAMES = {
    1: "1er Louvre", 2: "2e Bourse", 3: "3e Temple", 4: "4e Hôtel-de-Ville",
    5: "5e Panthéon", 6: "6e Luxembourg", 7: "7e Palais-Bourbon", 8: "8e Élysée",
    9: "9e Opéra", 10: "10e Entrepôt", 11: "11e Popincourt", 12: "12e Reuilly",
    13: "13e Gobelins", 14: "14e Observatoire", 15: "15e Vaugirard", 16: "16e Passy",
    17: "17e Batignolles", 18: "18e Buttes-Montmartre", 19: "19e Buttes-Chaumont",
    20: "20e Ménilmontant",
}

# City-wide infrastructure shares (documented estimates; flat across arrondissements pre-1930)
ELECTRICITY = {1870: 0.02, 1880: 0.05, 1890: 0.10, 1900: 0.30, 1910: 0.60, 1920: 0.85, 1930: 1.0,
               1940: 1.0, 1950: 1.0, 1960: 1.0, 1970: 1.0, 1980: 1.0, 1990: 1.0, 2000: 1.0, 2010: 1.0, 2020: 1.0}
PIPED_WATER = {1870: 0.15, 1880: 0.25, 1890: 0.40, 1900: 0.70, 1910: 0.90, 1920: 0.98, 1930: 1.0,
               1940: 1.0, 1950: 1.0, 1960: 1.0, 1970: 1.0, 1980: 1.0, 1990: 1.0, 2000: 1.0, 2010: 1.0, 2020: 1.0}
DRAINAGE = {1870: 0.20, 1880: 0.35, 1890: 0.55, 1900: 0.85, 1910: 0.95, 1920: 0.99, 1930: 1.0,
            1940: 1.0, 1950: 1.0, 1960: 1.0, 1970: 1.0, 1980: 1.0, 1990: 1.0, 2000: 1.0, 2010: 1.0, 2020: 1.0}

# Major hospitals: (arrondissement, founding_year) — cumulative per 100k by decade
HOSPITALS = [
    (4, 651), (5, 1253), (13, 1613), (14, 1613), (12, 1634), (18, 1784), (15, 1794),
    (19, 1867), (20, 1890), (7, 1900), (16, 1905), (11, 1926), (10, 1936), (17, 1958),
]

# Major parks m² by arrondissement and opening decade (cumulative green m² / resident)
PARKS_M2 = [
    (1, 1564, 46000), (4, 1607, 25000), (6, 1612, 230000), (8, 1778, 85000),
    (12, 1869, 150000), (19, 1867, 250000), (14, 1869, 22000), (15, 1878, 8500),
    (16, 1860, 840000), (7, 1878, 25000), (19, 1987, 550000), (15, 1992, 14000),
    (12, 1997, 140000), (13, 1998, 35000),
]

# Third spaces cumulative openings (arr, year) libraries+museums
THIRD_PLACES = [
    (4, 1537), (5, 1750), (1, 1793), (6, 1800), (7, 1800), (8, 1850), (16, 1880),
    (3, 1890), (9, 1900), (11, 1920), (18, 1930), (19, 1960), (20, 1970), (12, 1980),
    (13, 1985), (17, 1990), (10, 2000), (14, 2005), (2, 2010),
]


def nearest_year(target: int, years: list[int]) -> int:
    return min(years, key=lambda y: abs(y - target))


def load_population() -> pd.DataFrame:
    long_path = PARIS / "historical" / "paris_population_long.csv"
    if long_path.exists():
        df = pd.read_csv(long_path)
    else:
        df = pd.read_csv(PARIS / "paris_population.csv")
    return df


def decade_population(df: pd.DataFrame, decade: str) -> dict[int, float]:
    target = int(decade)
    years = sorted(df["year"].unique())
    use = nearest_year(target, years)
    sub = df[df["year"] == use]
    return {int(r.arrondissement_num): float(r.population) for r in sub.itertuples()}


def decade_ppd(df: pd.DataFrame, decade: str) -> dict[int, float | None]:
    target = int(decade)
    if target < 1968:
        return {i: None for i in range(1, 21)}
    years = [y for y in df["year"].unique() if y >= 1968]
    use = nearest_year(target, years)
    sub = df[df["year"] == use]
    out = {i: None for i in range(1, 21)}
    for r in sub.itertuples():
        v = getattr(r, "persons_per_dwelling", None)
        if pd.notna(v):
            out[int(r.arrondissement_num)] = float(v)
    return out


def transit_access(arr: int, decade: str, pop: float, transit: pd.DataFrame) -> float:
    d = int(decade)
    sub = transit[(transit["arrondissement_num"] == arr) & (transit["decade"] <= d)]
    if sub.empty or pop <= 0:
        return 0.0
    stations = float(sub.sort_values("decade").iloc[-1]["stations_cumulative"])
    return stations / pop * 100_000


def hospital_per_100k(arr: int, decade: str, pop: float) -> float:
    d = int(decade)
    n = sum(1 for a, y in HOSPITALS if a == arr and y <= d)
    return (n / pop * 100_000) if pop > 0 else 0.0


def green_m2_per_capita(arr: int, decade: str, pop: float, green_2020: dict[int, float]) -> float:
    d = int(decade)
    if d >= 2020:
        return green_2020.get(arr, 0.0)
    cum = sum(m2 for a, y, m2 in PARKS_M2 if a == arr and y <= d)
    return cum / pop if pop > 0 else 0.0


def third_per_100k(arr: int, decade: str, pop: float, snap_2020: dict[int, float]) -> float:
    d = int(decade)
    if d >= 2020:
        return snap_2020.get(arr, 0.0)
    n = sum(1 for a, y in THIRD_PLACES if a == arr and y <= d)
    return (n / pop * 100_000) if pop > 0 else 0.0


def main() -> None:
    ref = json.loads(CDMX_REF.read_text(encoding="utf-8"))
    variables = ref["variables"]
    source_notes = {
        "population": "Demographia 1861–1999; INSEE dossier complet 1968–2022.",
        "density": "Population ÷ fixed post-1860 arrondissement area (km²).",
        "transit_access": "Wikidata/OSM métro openings; cumulative stations per 100k (build_paris_data.py).",
        "persons_per_dwelling": "INSEE FAM G1, 1968+; null earlier.",
        "dwellings": "Population ÷ persons_per_dwelling where available.",
        "electricity": "City-wide historical electrification curve (Musée / literature); 100% from 1930.",
        "piped_water": "City-wide piped-water curve; near-universal from 1920.",
        "drainage": "Haussmann sewer network; ~100% from 1900.",
        "hospital_access": "Major hospitals by founding year (Wikipedia / AP-HP); per 100k.",
        "green_space": "opendata.paris.fr espaces verts 2020; historical from dated major parks.",
        "third_spaces": "Libraries + museums cumulative by founding year; 2022 from Open Data.",
    }

    pop_df = load_population()
    transit = pd.read_csv(PARIS / "paris_transit.csv")
    green = pd.read_csv(PARIS / "paris_green_space.csv")
    third = pd.read_csv(PARIS / "paris_third_spaces.csv")
    green_2020 = {int(r.arrondissement_num): float(r.m2_per_capita) for r in green.itertuples()}
    third_2020 = {int(r.arrondissement_num): float(r.total_per_100k) for r in third.itertuples()}

    arrondissements = []
    for arr in range(1, 21):
        values = {}
        for decade in DECADES:
            pops = decade_population(pop_df, decade)
            pop = pops.get(arr, 0.0)
            ppd = decade_ppd(pop_df, decade).get(arr)
            dwellings = (pop / ppd) if ppd and ppd > 0 else None
            values[decade] = {
                "population": pop,
                "density": pop / ARR_AREA_KM2[arr] if pop else 0.0,
                "transit_access": transit_access(arr, decade, pop, transit),
                "persons_per_dwelling": ppd,
                "dwellings": dwellings,
                "electricity": ELECTRICITY[int(decade)],
                "piped_water": PIPED_WATER[int(decade)],
                "drainage": DRAINAGE[int(decade)],
                "hospital_access": hospital_per_100k(arr, decade, pop),
                "green_space": green_m2_per_capita(arr, decade, pop, green_2020),
                "third_spaces": third_per_100k(arr, decade, pop, third_2020),
            }
        arrondissements.append({"name": ARR_NAMES[arr], "id": arr, "slug": ARR_NAMES[arr].lower().replace(" ", "_"), "values": values})

    payload = {
        "title": "Paris Urban Quality Index",
        "description": "Arrondissement-level UQI components by decade, from INSEE, opendata.paris.fr, OSM, and historical census.",
        "decades": DECADES,
        "variables": variables,
        "sourceNotes": source_notes,
        "arrondissements": arrondissements,
        "method": ref["method"],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, len(arrondissements), "arrondissements", len(DECADES), "decades")


if __name__ == "__main__":
    main()
