#!/usr/bin/env python3
"""Prepare web-friendly GeoJSON for Paris and Mexico City maps."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "data" / "maps"
PARIS_RAW = ROOT / "data" / "paris" / "raw" / "arrondissements.geojson"

MEXICO_URLS = [
    "https://raw.githubusercontent.com/JuveCampos/Shapes_Resiliencia_CDMX_CIDE/master/Shape%20Ciudad%20de%20M%C3%A9xico/CDMX_mpal.geojson",
    "https://raw.githubusercontent.com/JuanPinedaSoto/alcaldias_CDMX/master/Alcaldias_CDMX.geojson",
]

ALC_DISPLAY = {
    1: "Álvaro Obregón",
    2: "Azcapotzalco",
    3: "Benito Juárez",
    4: "Coyoacán",
    5: "Cuajimalpa de Morelos",
    6: "Cuauhtémoc",
    7: "Gustavo A. Madero",
    8: "Iztacalco",
    9: "Iztapalapa",
    10: "La Magdalena Contreras",
    11: "Miguel Hidalgo",
    12: "Milpa Alta",
    13: "Tláhuac",
    14: "Tlalpan",
    15: "Venustiano Carranza",
    16: "Xochimilco",
}

ALC_NAME_TO_ID = {
    "alvaro obregon": 1,
    "azcapotzalco": 2,
    "benito juarez": 3,
    "coyoacan": 4,
    "cuajimalpa": 5,
    "cuajimalpa de morelos": 5,
    "cuauhtemoc": 6,
    "gustavo a madero": 7,
    "iztacalco": 8,
    "iztapalapa": 9,
    "la magdalena contreras": 10,
    "magdalena contreras": 10,
    "miguel hidalgo": 11,
    "milpa alta": 12,
    "tlahuac": 13,
    "tlalpan": 14,
    "venustiano carranza": 15,
    "xochimilco": 16,
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def match_alc(name: str) -> int | None:
    n = norm(name)
    for key, aid in ALC_NAME_TO_ID.items():
        if key in n or n in key:
            return aid
    return None


def prepare_paris() -> None:
    geo = json.loads(PARIS_RAW.read_text(encoding="utf-8"))
    out_features = []
    for feat in geo["features"]:
        props = feat["properties"]
        num = int(props["c_ar"])
        out_features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": num,
                    "insee": str(props["c_arinsee"]),
                    "name": f"{num}e — {props.get('l_aroff', props.get('l_ar', ''))}",
                },
                "geometry": feat["geometry"],
            }
        )
    out = {"type": "FeatureCollection", "features": out_features}
    (MAPS / "paris_arrondissements.geojson").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8"
    )
    print("Paris features", len(out_features))


def prepare_mexico() -> None:
    raw = None
    for url in MEXICO_URLS:
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "ECON30/1.0"})
            if r.status_code == 200 and r.text.strip().startswith("{"):
                raw = r.json()
                print("Fetched", url)
                break
        except Exception as exc:
            print("fail", url, exc)
    if raw is None:
        raise RuntimeError("Could not download Mexico alcaldías GeoJSON")

    out_features = []
    for feat in raw["features"]:
        props = feat["properties"]
        name = (
            props.get("ALCALDIA")
            or props.get("NOMGEO")
            or props.get("nombre")
            or props.get("NOMBRE")
            or props.get("alcaldia")
            or props.get("name")
            or ""
        )
        aid = match_alc(name)
        if aid is None:
            for k, v in props.items():
                if isinstance(v, str) and match_alc(v):
                    aid = match_alc(v)
                    name = v
                    break
        if aid is None:
            print("skip", props)
            continue
        out_features.append(
            {
                "type": "Feature",
                "properties": {"id": aid, "name": ALC_DISPLAY.get(aid, name or f"Alcaldía {aid}")},
                "geometry": feat["geometry"],
            }
        )
    out = {"type": "FeatureCollection", "features": out_features}
    (MAPS / "mexico_alcaldias.geojson").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8"
    )
    print("Mexico features", len(out_features))


def main() -> None:
    MAPS.mkdir(parents=True, exist_ok=True)
    prepare_paris()
    prepare_mexico()


if __name__ == "__main__":
    main()
