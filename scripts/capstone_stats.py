import pandas as pd
from pathlib import Path

A = Path(__file__).resolve().parents[1] / "data" / "analysis"

m = pd.read_csv(A / "uqi_mexico_2020.csv")
h = pd.read_csv(A / "hdi_mexico_2020.csv")
mx = m.merge(h, on="alcaldia_id")
r_mx = mx["uqi"].corr(mx["hdi"])

p = pd.read_csv(A / "uqi_paris_2022.csv")
hp = pd.read_csv(A / "hdi_paris_2022.csv")
px = p.merge(hp, on="arrondissement_num")
r_p = px["uqi"].corr(px["hdi"])

print("CDMX UQI-HDI r", round(r_mx, 3))
print("Paris UQI-HDI r", round(r_p, 3))
print("Paris HDI", hp["hdi"].min(), "-", hp["hdi"].max())
print("Paris top", hp.nlargest(3, "hdi")[["arrondissement", "hdi"]].values.tolist())
print("Paris bottom", hp.nsmallest(3, "hdi")[["arrondissement", "hdi"]].values.tolist())
