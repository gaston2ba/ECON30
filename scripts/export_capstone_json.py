#!/usr/bin/env python3
"""Export analysis CSVs to data/analysis/capstone_bundle.json for the capstone site."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "data" / "analysis"


def df_records(path: Path) -> list[dict]:
    return json.loads(pd.read_csv(path).to_json(orient="records"))


def main() -> None:
    bundle = {
        "mexico": {
            "panel": df_records(A / "uqi_mexico_panel.csv"),
            "snap2020": df_records(A / "uqi_mexico_2020.csv"),
            "hdi2020": df_records(A / "hdi_mexico_2020.csv"),
        },
        "paris": {
            "snap2022": df_records(A / "uqi_paris_2022.csv"),
            "panel": df_records(A / "uqi_paris_panel.csv") if (A / "uqi_paris_panel.csv").exists() else [],
            "hdi2022": df_records(A / "hdi_paris_2022.csv"),
        },
        "components": ["parks", "transit", "density", "thirdspace", "infrastructure"],
    }
    out = A / "capstone_bundle.json"
    out.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out, "bytes", out.stat().st_size)


if __name__ == "__main__":
    main()
