#!/usr/bin/env python3
"""Build CDMX HDI 2020 from PNUD municipal CSV → data/analysis/."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "mexico" / "raw" / "hdi_mexico_pnud.csv"
OUT = ROOT / "data" / "analysis"
METH = ROOT / "methodology_mexico.md"

ALCADIAS = [
    "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán", "Cuajimalpa de Morelos",
    "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco", "Iztapalapa", "La Magdalena Contreras",
    "Miguel Hidalgo", "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco",
]


def main() -> None:
    df = pd.read_csv(RAW)
    rows = []
    for i, name in enumerate(ALCADIAS, 1):
        row = df[df["alcaldia"] == name].iloc[0]
        hdi = float(row["2020"])
        rows.append(
            {
                "alcaldia_id": i,
                "alcaldia_name": name,
                "hdi": hdi,
                "life_exp_index": None,
                "education_index": None,
                "income_index": None,
                "year": 2020,
                "source": "PNUD México municipal HDI (transcribed to hdi_mexico_pnud.csv); 2020 column",
            }
        )
    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "hdi_mexico_2020.csv", index=False)
    METH.write_text(
        "# Mexico City HDI methodology\n\n"
        "Source: PNUD México *Informe sobre Desarrollo Humano Municipal* (municipal IDH series).\n"
        "Raw transcription: `data/mexico/raw/hdi_mexico_pnud.csv`.\n"
        "Values used: **2020** municipal HDI for the 16 CDMX alcaldías.\n"
        "Reference: https://hdr.undp.org/data-center/specific-country-data and PNUD Mexico municipal reports.\n"
        "Sub-indices (life, education, income) are not published per alcaldía in this extract; only composite HDI.\n",
        encoding="utf-8",
    )
    print("wrote", OUT / "hdi_mexico_2020.csv", "HDI", out["hdi"].min(), "-", out["hdi"].max())


if __name__ == "__main__":
    main()
