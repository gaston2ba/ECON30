# CDMX Urban Quality Index (Andres’s map)

Portable copy of the Mexico City interactive map from `origin/main` on GitHub (`gaston2ba/ECON30`), synced from Andres’s `index.html`, `script.js`, `styles.css`, and workbook export.

## Open locally

From the **repository root**:

```powershell
python -m http.server 8080
```

Then open: **http://127.0.0.1:8080/cdmx/**

(Use `127.0.0.1`, not `localhost`, if the browser has trouble.)

## Files

| File | Role |
|------|------|
| `index.html` | Layout: sidebar controls, choropleth map, line chart |
| `script.js` | UQI scoring, D3 map/chart, play/pause |
| `styles.css` | Styling |
| `data/uqi-by-alcaldia.json` | 16 alcaldías × 17 decades (1860–2020) |
| `data/alcaldias.geojson` | Boundary polygons |

Source workbook on `main`: `DataMexCity.xlsx` (repo root). Processed exports also live under `data/mexico/`.

## Refresh from GitHub

```powershell
python scripts/sync_cdmx_from_main.py
```

Or manually: `git fetch origin` then re-run that script.
