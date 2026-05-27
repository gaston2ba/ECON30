"""Export normalized 2020 Mexico alcaldía scores from DataMexCity.xlsx."""
import json
import math
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "DataMexCity.xlsx"

ALCADIAS = [
    ("Álvaro Obregón", ["alvaro obregon"]),
    ("Azcapotzalco", ["azcapotzalco"]),
    ("Benito Juárez", ["benito juarez"]),
    ("Coyoacán", ["coyoacan"]),
    ("Cuajimalpa", ["cuajimalpa", "cuajimalpa de morelos"]),
    ("Cuauhtémoc", ["cuauhtemoc"]),
    ("Gustavo A. Madero", ["gustavo a. madero", "gustavo a madero"]),
    ("Iztacalco", ["iztacalco"]),
    ("Iztapalapa", ["iztapalapa"]),
    ("La Magdalena Contreras", ["magdalena contreras", "la magdalena contreras"]),
    ("Miguel Hidalgo", ["miguel hidalgo"]),
    ("Milpa Alta", ["milpa alta"]),
    ("Tláhuac", ["tlahuac"]),
    ("Tlalpan", ["tlalpan"]),
    ("Venustiano Carranza", ["venustiano carranza"]),
    ("Xochimilco", ["xochimilco"]),
]


def norm(s: str) -> str:
    s = str(s).strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def match_alc(name: str) -> str | None:
    n = norm(name)
    if len(n) > 40:
        return None
    for label, keys in ALCADIAS:
        label_n = norm(label)
        if n == label_n:
            return label
        for key in keys:
            if n == key or n.startswith(key + " "):
                return label
    return None


def read_alc_sheet(path: Path, sheet: str) -> dict[str, dict[int, float]]:
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    hdr = next(
        i
        for i in range(15)
        if isinstance(df.iloc[i, 0], str) and norm(df.iloc[i, 0]) == "alcaldia"
    )
    years = [
        int(float(df.iloc[hdr, j]))
        for j in range(1, df.shape[1])
        if pd.notna(df.iloc[hdr, j])
    ]
    out: dict[str, dict[int, float]] = {}
    for i in range(hdr + 1, len(df)):
        name = df.iloc[i, 0]
        if pd.isna(name):
            continue
        alc = match_alc(name)
        if not alc:
            continue
        vals = {
            years[j]: float(df.iloc[i, j + 1])
            for j in range(len(years))
            if pd.notna(df.iloc[i, j + 1])
        }
        out[alc] = vals
    return out


def minmax(vals: dict[str, float], invert: bool = False) -> dict[str, float]:
    lo, hi = min(vals.values()), max(vals.values())
    out = {}
    for key, value in vals.items():
        t = (value - lo) / (hi - lo) if hi > lo else 0.5
        if invert:
            t = 1 - t
        out[key] = round(t * 100, 1)
    return out


def build_rows(
    year: int,
    labels: list[str],
    raw: dict,
    crowd: dict,
    pop: dict,
) -> tuple[list[dict] | None, list[str] | None]:
    alcs = [
        alc
        for alc in labels
        if all(year in raw[var].get(alc, {}) for var in raw)
        and year in crowd.get(alc, {})
        and year in pop.get(alc, {})
    ]
    if len(alcs) < 12:
        return None, None

    comp = {var: minmax({alc: raw[var][alc][year] for alc in alcs}) for var in raw}
    income = minmax({alc: crowd[alc][year] for alc in alcs}, invert=True)

    rows = []
    for i, alc in enumerate(labels, 1):
        if alc not in alcs:
            continue
        infra = round(
            sum(comp[v][alc] for v in ("elec", "water", "drain", "hosp")) / 4, 1
        )
        ped = round((comp["parks"][alc] + comp["thirdspace"][alc]) / 2, 1)
        rows.append(
            {
                "id": i,
                "name": alc,
                "parks": comp["parks"][alc],
                "transit": comp["transit"][alc],
                "density": comp["density"][alc],
                "thirdspace": comp["thirdspace"][alc],
                "pedestrian": ped,
                "infrastructure": infra,
                "income": income[alc],
            }
        )
    return rows, alcs


def corr(rows: list[dict]) -> float:
    xs = [
        (
            r["parks"]
            + r["transit"]
            + r["density"]
            + r["thirdspace"]
            + r["pedestrian"]
            + r["infrastructure"]
        )
        / 6
        for r in rows
    ]
    ys = [r["income"] for r in rows]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy)


def main() -> None:
    labels = [label for label, _ in ALCADIAS]
    var_sheets = {
        "parks": "10. Green space",
        "transit": "3. Transit access",
        "density": "2. Density",
        "thirdspace": "11. Third spaces",
        "elec": "6. % Electricity",
        "water": "7. % Piped water",
        "drain": "8. % Drainage",
        "hosp": "9. Hospital access",
    }
    pop = read_alc_sheet(WORKBOOK, "1. Population")
    raw = {var: read_alc_sheet(WORKBOOK, sheet) for var, sheet in var_sheets.items()}
    crowd = read_alc_sheet(WORKBOOK, "4. Persons per dwelling")

    rows2020, _ = build_rows(2020, labels, raw, crowd, pop)
    assert rows2020

    years = sorted({year for vals in pop.values() for year in vals})
    series = []
    for year in years:
        if year % 10 != 0 and year != 2020:
            continue
        rows, alcs = build_rows(year, labels, raw, crowd, pop)
        if not rows or not alcs:
            continue
        idx = {
            r["name"]: (
                r["parks"]
                + r["transit"]
                + r["density"]
                + r["thirdspace"]
                + r["pedestrian"]
                + r["infrastructure"]
            )
            / 6
            for r in rows
        }
        sorted_alcs = sorted(alcs, key=lambda alc: idx[alc])
        cutoff = idx[sorted_alcs[3]]
        low = sum(pop[alc][year] for alc in alcs if idx[alc] <= cutoff)
        total = sum(pop[alc][year] for alc in alcs)
        series.append({"year": year, "value": round(low / total * 100, 1)})

    print("correlation", round(corr(rows2020), 2))
    print("story_series", json.dumps(series))
    print("data_rows", json.dumps(rows2020, ensure_ascii=False))


if __name__ == "__main__":
    main()
