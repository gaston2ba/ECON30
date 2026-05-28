#!/usr/bin/env python3
"""Build shared JSON payload used by persistence interactives."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MEXICO_XLSX = ROOT / "data" / "mexico" / "workbook" / "DataMexCity.xlsx"
MEXICO_REF = ROOT / "data" / "mexico" / "exports" / "mexico_alcaldias_2020.json"
PARIS_POP = ROOT / "data" / "paris" / "paris_population.csv"
OUT = ROOT / "data" / "analysis" / "persistence_interactives.json"


def read_mexico_ppd() -> pd.DataFrame:
    raw = pd.read_excel(MEXICO_XLSX, sheet_name="4. Persons per dwelling", header=None)
    hdr = None
    for i in range(min(20, len(raw))):
        v = raw.iloc[i, 0]
        if isinstance(v, str) and v.strip().lower().replace("í", "i") == "alcaldia":
            hdr = i
            break
    if hdr is None:
        raise ValueError("Could not locate alcaldia header in persons-per-dwelling sheet")

    years = []
    cols = []
    for j in range(1, raw.shape[1]):
        v = raw.iloc[hdr, j]
        try:
            years.append(int(float(v)))
            cols.append(j)
        except Exception:
            continue

    rows = []
    for i in range(hdr + 1, raw.shape[0]):
        n = raw.iloc[i, 0]
        if pd.isna(n):
            continue
        n = str(n).strip()
        if not n:
            continue
        rec = {"name": n}
        for y, j in zip(years, cols):
            val = raw.iloc[i, j]
            rec[y] = float(val) if pd.notna(val) else None
        rows.append(rec)
    return pd.DataFrame(rows)


def norm_name(s: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFD", str(s).strip().lower())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")


def match_name(name: str, id_map: dict[str, int]) -> tuple[str, int] | tuple[None, None]:
    n = norm_name(name)
    for k, v in id_map.items():
        kn = norm_name(k)
        if n == kn:
            return k, v
    for k, v in id_map.items():
        kn = norm_name(k)
        if n in kn or kn in n:
            return k, v
    return None, None


def rank_payload(df: pd.DataFrame, name_col: str, years: list[int], id_map: dict[str, int], city: str) -> dict:
    data_by_year: dict[str, list[dict]] = {}
    for y in years:
        tmp = df[[name_col, y]].dropna().copy()
        tmp = tmp.sort_values(y, ascending=True).reset_index(drop=True)
        tmp["rank"] = tmp.index + 1
        mapped = tmp[name_col].apply(lambda s: match_name(s, id_map))
        tmp["mapped_name"] = mapped.apply(lambda x: x[0])
        tmp["id"] = mapped.apply(lambda x: x[1])
        tmp = tmp.dropna(subset=["id"])
        tmp["id"] = tmp["id"].astype(int)
        data_by_year[str(y)] = [
            {
                "id": int(r["id"]),
                "name": str(r["mapped_name"]),
                "value": float(r[y]),
                "rank": int(r["rank"]),
            }
            for _, r in tmp.iterrows()
        ]

    latest = str(max(years))
    latest_ranks = {r["id"]: r["rank"] for r in data_by_year[latest]}
    shift_counter = {}
    for y in years:
        curr = {r["id"]: r["rank"] for r in data_by_year[str(y)]}
        common = sorted(set(curr) & set(latest_ranks))
        shift_counter[str(y)] = {
            "year": int(y),
            "n_total": len(common),
            "changed_gt5": int(sum(1 for i in common if abs(curr[i] - latest_ranks[i]) > 5)),
        }

    trajectories = {}
    for y in years:
        for r in data_by_year[str(y)]:
            trajectories.setdefault(str(r["id"]), {"id": r["id"], "name": r["name"], "series": []})
            trajectories[str(r["id"])]["series"].append({"year": int(y), "rank": int(r["rank"]), "value": float(r["value"])})

    return {
        "city": city,
        "years": years,
        "latest_year": int(max(years)),
        "data_by_year": data_by_year,
        "shift_counter_vs_latest": shift_counter,
        "trajectories": list(trajectories.values()),
    }


def main() -> None:
    mexico_df = read_mexico_ppd()
    mexico_ref = json.loads(MEXICO_REF.read_text(encoding="utf-8"))
    mexico_id_map = {r["name"]: int(r["id"]) for r in mexico_ref}
    mexico_years = [y for y in sorted(c for c in mexico_df.columns if isinstance(c, int)) if 1900 <= y <= 2020]

    paris_pop = pd.read_csv(PARIS_POP)
    paris_pivot = paris_pop[["arrondissement", "year", "persons_per_dwelling"]].pivot(
        index="arrondissement", columns="year", values="persons_per_dwelling"
    ).reset_index()
    paris_years = [int(y) for y in sorted(c for c in paris_pivot.columns if isinstance(c, (int, float)))]
    paris_years = [y for y in paris_years if y >= 1968]
    # arrondissement names in paris_index_2022.json include id prefix, map by numeric prefix
    paris_id_map = {}
    for n in paris_pivot["arrondissement"]:
        prefix = str(n).split("e")[0].replace("er", "1")
        digits = "".join(ch for ch in prefix if ch.isdigit())
        if digits:
            paris_id_map[n] = int(digits)

    payload = {
        "mexico": rank_payload(mexico_df, "name", mexico_years, mexico_id_map, "Mexico City"),
        "paris": rank_payload(paris_pivot, "arrondissement", paris_years, paris_id_map, "Paris"),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)
    print("mex years", payload["mexico"]["years"])
    print("paris years", payload["paris"]["years"])


if __name__ == "__main__":
    main()
