# Paris UQI Interactive Map

Paris counterpart to Andres's CDMX UQI map. Same layout and interactions: year slider, variable toggles, choropleth map, line chart, play/pause.

## Open locally

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/paris/`

## Files

- `index.html`, `styles.css`, `script.js` — static app
- `data/uqi-by-arrondissement.json` — panel data (1968–2022 census years)
- `data/arrondissements.geojson` — 20 arrondissement boundaries

Regenerate JSON: `python scripts/export_paris_uqi_web.py`

## Data note

Paris panel years are **1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022** (INSEE census). Green space, third spaces, and median income are available for **2022** only; historical years use population, density, crowding, and metro access.
