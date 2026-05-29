#!/usr/bin/env python3
"""Normalize Paris arrondissement boundaries to data/paris/arrondissements.geojson."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "maps" / "paris_arrondissements.geojson"
OUT = ROOT / "data" / "paris" / "arrondissements.geojson"

NAMES = {
    1: "1er Louvre",
    2: "2e Bourse",
    3: "3e Temple",
    4: "4e Hôtel-de-Ville",
    5: "5e Panthéon",
    6: "6e Luxembourg",
    7: "7e Palais-Bourbon",
    8: "8e Élysée",
    9: "9e Opéra",
    10: "10e Entrepôt",
    11: "11e Popincourt",
    12: "12e Reuilly",
    13: "13e Gobelins",
    14: "14e Observatoire",
    15: "15e Vaugirard",
    16: "16e Passy",
    17: "17e Batignolles",
    18: "18e Buttes-Montmartre",
    19: "19e Buttes-Chaumont",
    20: "20e Ménilmontant",
}


def main() -> None:
    geo = json.loads(SRC.read_text(encoding="utf-8"))
    features = []
    for f in geo["features"]:
        p = f.get("properties") or {}
        num = int(p.get("id") or p.get("arrondissement_num") or 0)
        if not num and "insee" in p:
            num = int(str(p["insee"])[-2:])
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": num,
                    "arrondissement_num": num,
                    "insee": p.get("insee", f"751{num:02d}"),
                    "name": NAMES.get(num, p.get("name", f"{num}e")),
                    "slug": NAMES.get(num, "").lower().replace(" ", "_").replace("é", "e"),
                },
                "geometry": f["geometry"],
            }
        )
    features.sort(key=lambda x: x["properties"]["id"])
    out = {"type": "FeatureCollection", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    assert len(features) == 20
    coords = features[0]["geometry"]["coordinates"][0][0]
    print(f"wrote {OUT} ({len(features)} features); sample lon={coords[0]:.2f} lat={coords[1]:.2f}")


if __name__ == "__main__":
    main()
