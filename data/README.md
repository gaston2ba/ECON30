# Project data layout

All datasets for the capstone live under `data/`, split by city and purpose.

```
data/
├── analysis/          # Cross-city outputs (regressions, web embeds)
├── mexico/            # Mexico City (CDMX alcaldías)
│   ├── workbook/      # Main panel workbook (DataMexCity.xlsx)
│   ├── sources/       # Raw source bundles (zip, component spreadsheets)
│   ├── historical/    # Baseline class-structure CSVs
│   └── exports/       # Generated CSV/JSON from scripts
└── paris/             # Paris arrondissements
    ├── *.csv          # Processed panel (population, transit, income, …)
    ├── historical/    # Baseline class-structure CSVs
    └── raw/           # Cached API downloads (INSEE, OSM, Open Data)
```

## Scripts

| Script | Reads | Writes |
|--------|-------|--------|
| `scripts/export_mexico_data.py` | `mexico/workbook/DataMexCity.xlsx` | stdout / `mexico/exports/` |
| `scripts/build_paris_data.py` | APIs + caches in `paris/raw/` | `paris/*.csv` |
| `scripts/export_web_embeds.py` | Both cities | `analysis/web_embeds.json` |
| `scripts/run_regressions.py` | Paris + Mexico panels | `analysis/regression_results.json` |
