# CDMX UQI Interactive Map

This folder is a portable static website for the Mexico City Urban Quality Index map. The map is locked to Mexico City, uses OpenStreetMap street tiles, and draws a clear 16-alcaldía choropleth from the workbook variables.

## Open Locally
Because the site loads local JSON files, run a tiny local server from this folder:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## What Is Included
- `index.html`, `styles.css`, `script.js`: the Leaflet/OpenStreetMap website.
- `data/uqi-by-alcaldia.json`: workbook-derived UQI component data by alcaldía and decade.
- `data/alcaldias.geojson`: clean 16-feature alcaldía boundary polygons matched to the workbook names.
- `data/DataMexCity.xlsx`: source workbook copy for handoff.
- `docs/CDMX_UQI_context.pdf`: consolidated context PDF.
- `docs/CDMX_UQI_context.md` and `docs/CDMX_UQI_context.html`: editable source versions of the PDF.

## Deploy As A Small URL
Use any static host:

1. Create a GitHub repository.
2. Upload the contents of this folder.
3. Enable GitHub Pages from the repository settings.
4. Share the generated GitHub Pages URL.

Netlify and Vercel also work: drag this folder into Netlify Drop or import the repo in Vercel.

## UQI Calculation
The browser calculates UQI live. It min-max normalizes each selected variable within the active decade, reverse-scores variables where lower values are better, and averages the selected variables equally. Users can toggle variables in the left panel and use the decade slider from 1860 to 2020.

## Boundary Note
Boundary layer: open-mexico/mexico-geojson 09-Cdmx.geojson. For production, replace with official INEGI/CDMX alcaldia GeoJSON if desired.
