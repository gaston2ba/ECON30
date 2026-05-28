#!/usr/bin/env python3
"""Recompute UQI with methodology fixes and export canonical cross-sections."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARIS_JSON = ROOT / "data" / "paris" / "paris_index_2022.json"
MEXICO_JSON = ROOT / "data" / "mexico" / "exports" / "mexico_alcaldias_2020.json"

OUT_PARIS = ROOT / "data" / "paris" / "paris_uqi_2020.csv"
OUT_MEXICO = ROOT / "data" / "mexico" / "exports" / "cdmx_uqi_2020.csv"


def main() -> None:
    paris = pd.DataFrame(json.loads(PARIS_JSON.read_text(encoding="utf-8")))
    mexico = pd.DataFrame(json.loads(MEXICO_JSON.read_text(encoding="utf-8")))

    # Fix 1: remove circular walkability (pedestrian = avg of parks + thirdspace)
    # Fix 2: Paris infrastructure has near-zero variance (citywide PM2.5 proxy),
    # so drop infrastructure for Paris.
    paris_components = ["parks", "transit", "density", "thirdspace"]
    mexico_components = ["parks", "transit", "density", "thirdspace", "infrastructure"]

    paris["uqi_corrected"] = paris[paris_components].mean(axis=1)
    mexico["uqi_corrected"] = mexico[mexico_components].mean(axis=1)

    paris["uqi_components_used"] = ",".join(paris_components)
    mexico["uqi_components_used"] = ",".join(mexico_components)

    OUT_PARIS.parent.mkdir(parents=True, exist_ok=True)
    OUT_MEXICO.parent.mkdir(parents=True, exist_ok=True)
    paris.to_csv(OUT_PARIS, index=False)
    mexico.to_csv(OUT_MEXICO, index=False)

    print("Wrote", OUT_PARIS)
    print("Wrote", OUT_MEXICO)
    print("Paris infrastructure std:", float(paris["infrastructure"].std(ddof=0)))


if __name__ == "__main__":
    main()
