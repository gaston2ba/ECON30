#!/usr/bin/env python3
"""Build Mexico City UQI panel (5 components) from DataMexCity.xlsx → data/analysis/."""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "mexico" / "workbook" / "DataMexCity.xlsx"
OUT = ROOT / "data" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

ALCADIAS = [
    "Álvaro Obregón",
    "Azcapotzalco",
    "Benito Juárez",
    "Coyoacán",
    "Cuajimalpa de Morelos",
    "Cuauhtémoc",
    "Gustavo A. Madero",
    "Iztacalco",
    "Iztapalapa",
    "La Magdalena Contreras",
    "Miguel Hidalgo",
    "Milpa Alta",
    "Tláhuac",
    "Tlalpan",
    "Venustiano Carranza",
    "Xochimilco",
]


def norm(s: str) -> str:
    s = str(s).strip().lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def match_alc(name: str) -> str | None:
    n = norm(name)
    for label in ALCADIAS:
        if n == norm(label) or n.startswith(norm(label).split()[0]):
            keys = {
                "alvaro obregon": "Álvaro Obregón",
                "cuajimalpa": "Cuajimalpa de Morelos",
                "gustavo a. madero": "Gustavo A. Madero",
                "gustavo a madero": "Gustavo A. Madero",
                "magdalena contreras": "La Magdalena Contreras",
                "la magdalena contreras": "La Magdalena Contreras",
            }
            if n in keys:
                return keys[n]
            if norm(label) in n or n in norm(label):
                return label
    return None


def read_sheet(sheet: str) -> dict[str, dict[int, float]]:
    df = pd.read_excel(WORKBOOK, sheet_name=sheet, header=None)
    hdr = next(i for i in range(20) if isinstance(df.iloc[i, 0], str) and norm(df.iloc[i, 0]) == "alcaldia")
    years = [int(float(df.iloc[hdr, j])) for j in range(1, df.shape[1]) if pd.notna(df.iloc[hdr, j])]
    out: dict[str, dict[int, float]] = {}
    for i in range(hdr + 1, len(df)):
        name = df.iloc[i, 0]
        if pd.isna(name):
            continue
        alc = match_alc(str(name))
        if not alc:
            continue
        out[alc] = {
            years[j]: float(df.iloc[i, j + 1])
            for j in range(len(years))
            if pd.notna(df.iloc[i, j + 1])
        }
    return out


def score_higher(vals: dict[str, float]) -> dict[str, float]:
    lo, hi = min(vals.values()), max(vals.values())
    return {k: round((v - lo) / (hi - lo) * 100, 2) if hi > lo else 50.0 for k, v in vals.items()}


def score_density(vals: dict[str, float]) -> dict[str, float]:
    lo, hi = min(vals.values()), max(vals.values())
    out = {}
    for k, v in vals.items():
        t = (v - lo) / (hi - lo) if hi > lo else 0.5
        out[k] = round((1 - 2 * abs(t - 0.5)) * 100, 2)
    return out


def main() -> None:
    parks_raw = read_sheet("10. Green space")
    transit_raw = read_sheet("3. Transit access")
    density_raw = read_sheet("2. Density")
    third_raw = read_sheet("11. Third spaces")
    elec = read_sheet("6. % Electricity")
    water = read_sheet("7. % Piped water")
    drain = read_sheet("8. % Drainage")
    hosp = read_sheet("9. Hospital access")

    years = sorted({y for d in parks_raw.values() for y in d})
    rows = []
    for year in years:
        alcs = [a for a in ALCADIAS if all(year in d.get(a, {}) for d in [parks_raw, transit_raw, density_raw, third_raw, elec, water, drain, hosp])]
        if len(alcs) < 12:
            continue
        parks = score_higher({a: parks_raw[a][year] for a in alcs})
        transit = score_higher({a: transit_raw[a][year] for a in alcs})
        density = score_density({a: density_raw[a][year] for a in alcs})
        third = score_higher({a: third_raw[a][year] for a in alcs})
        infra_raw = {a: (elec[a][year] + water[a][year] + drain[a][year] + hosp[a][year]) / 4 for a in alcs}
        infra = score_higher(infra_raw)
        for i, alc in enumerate(ALCADIAS, 1):
            if alc not in alcs:
                continue
            uqi = round((parks[alc] + transit[alc] + density[alc] + third[alc] + infra[alc]) / 5, 2)
            rows.append(
                {
                    "alcaldia_id": i,
                    "alcaldia_name": alc,
                    "year": year,
                    "parks": parks[alc],
                    "transit": transit[alc],
                    "density": density[alc],
                    "thirdspace": third[alc],
                    "infrastructure": infra[alc],
                    "uqi": uqi,
                }
            )

    panel = pd.DataFrame(rows)
    panel.to_csv(OUT / "uqi_mexico_panel.csv", index=False)
    snap = panel[panel["year"] == 2020].copy()
    snap.to_csv(OUT / "uqi_mexico_2020.csv", index=False)
    print("wrote", OUT / "uqi_mexico_panel.csv", len(panel), "rows")
    print("2020 UQI range", snap["uqi"].min(), "-", snap["uqi"].max())


if __name__ == "__main__":
    main()
