import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def hdi_rank(path, key):
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = [(a["name"], a["values"]["2020"]["hdi"]) for a in d[key] if a["values"].get("2020")]
    rows.sort(key=lambda x: -x[1])
    return rows

paris = hdi_rank(ROOT / "data/paris/hdi-by-arrondissement.json", "arrondissements")
cdmx = hdi_rank(ROOT / "data/cdmx/hdi-by-alcaldia.json", "alcaldias")
print("Paris", paris[0], paris[-1], "top3", paris[:3], "bot3", paris[-3:])
print("CDMX", cdmx[0], cdmx[-1], "top3", cdmx[:3], "bot3", cdmx[-3:])
