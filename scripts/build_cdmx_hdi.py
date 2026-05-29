#!/usr/bin/env python3
"""Build data/cdmx/hdi-by-alcaldia.json from PNUD municipal HDI table."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "mexico" / "raw" / "hdi_mexico_pnud.csv"
OUT = ROOT / "data" / "cdmx" / "hdi-by-alcaldia.json"
METH = ROOT / "data" / "cdmx" / "hdi-methodology.md"
UQI = ROOT / "data" / "cdmx" / "uqi-by-alcaldia.json"

DECADES = [str(y) for y in range(1860, 2030, 10)]
HDI_YEARS = {2000: "2000", 2005: "2000", 2010: "2010", 2015: "2010", 2020: "2020"}


def main() -> None:
    df = pd.read_csv(RAW)
    uqi = json.loads(UQI.read_text(encoding="utf-8"))
    name_map = {a["name"]: a for a in uqi["alcaldias"]}
    alcaldias = []
    for _, row in df.iterrows():
        name = row["alcaldia"]
        values = {d: None for d in DECADES}
        for col in ("2000", "2005", "2010", "2015", "2020"):
            if col not in row or pd.isna(row[col]):
                continue
            decade = HDI_YEARS[int(col)]
            values[decade] = {"hdi": float(row[col])}
        alcaldias.append({"name": name, "values": values})
    payload = {
        "title": "CDMX Human Development Index",
        "description": "Municipal HDI from PNUD México municipal series (transcribed to CSV).",
        "decades": DECADES,
        "variables": [{"key": "hdi", "label": "HDI", "unit": "index", "higherIsBetter": True, "defaultSelected": True}],
        "alcaldias": alcaldias,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    METH.write_text(
        "# CDMX alcaldía HDI\n\nSource: PNUD México municipal HDI (`data/mexico/raw/hdi_mexico_pnud.csv`), "
        "Informe sobre Desarrollo Humano Municipal. Years mapped to decades 2000, 2010, 2020.\n",
        encoding="utf-8",
    )
    vals = [(a["name"], a["values"]["2020"]["hdi"]) for a in alcaldias if a["values"].get("2020")]
    vals.sort(key=lambda x: -x[1])
    print("Top:", vals[:3], "Bottom:", vals[-3:])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
