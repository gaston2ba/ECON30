# Paris historical data (post-1860 boundaries)

Arrondissement-level population from the **second half of the 19th century** through today, for the Paris UQI map (`paris/`).

## Files

| File | Description |
|------|-------------|
| `demographia_paris_arr.html` | Cached copy of [Demographia Paris arrondissements](http://demographia.com/db-paris-arr1999.htm) |
| `paris_population_demographia_1861_1999.csv` | Parsed census population (20 arrondissements × 23 years) |
| `paris_population_long.csv` | Full merged panel: Demographia 1861–1962 + INSEE 1968–2022 |
| `paris_population_decadal.csv` | Map export: nearest census year to each decade 1860–2020 |
| `paris_population_sources.json` | Metadata and citations |
| `paris-1865.csv` | 1865 social-class shares (city-wide, not by arrondissement) |

## Coverage

- **1861–1999:** French census via Demographia (population + computed density).
- **1968–2022:** INSEE dossier complet (`../paris_population.csv`) — preferred where years overlap.
- **Persons per dwelling:** INSEE only, **1968+**.
- **Green space, third places, income:** 2022 snapshots only in the web export.
- **Metro access:** Decadal cumulative stations from `../paris_transit.csv` (1860–2020).

## Regenerate

```powershell
python scripts/collect_paris_historical.py
python scripts/export_paris_uqi_web.py
```

Then open `http://127.0.0.1:8080/paris/` (with `python -m http.server 8080` from the repo root).
