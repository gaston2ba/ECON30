---
title: "Summary — Paris Espaces Verts GeoJSON"
sources:
  - raw/Paris/present-day-data/paris-espaces-verts.geojson
related:
  - "[[third-place-test]]"
  - "[[haussmannization]]"
  - "[[iris-and-ageb]]"
last_updated: 2026-04-18
tags:
  - paris
  - present-day
  - geojson
  - green-space
---

# Summary — Paris Espaces Verts GeoJSON

A polygon GeoJSON `FeatureCollection` of every public park, square, garden, and promenade managed by the City of Paris. ~12 MB, single-line file, originally from `opendata.paris.fr/explore/dataset/espaces_verts/`.

## What it is

The geometry of present-day public green space in Paris, in EPSG:4326. Each feature is one named green space with its polygon footprint. This is the contemporary state of a network whose backbone — the squares, the redesigned Bois de Boulogne and Bois de Vincennes, the *promenades plantées*, the small *squares* between Haussmann blocks — was deliberately built out under Haussmann and Adolphe Alphand as the "park for every neighborhood" promise of the renovation.

## Use in the project

- The numerator of the [[third-place-test]]: green-space surface area (or count of features) per capita by arrondissement or IRIS, cross-referenced with median income from INSEE Filosofi.
- Direct evidence for whether Haussmann's universal-parks rhetoric holds up at present-day income resolution: do the wealthy western arrondissements (6th, 7th, 8th, 16th) and the eastern ones (19th, 20th) actually have comparable per-capita green-space provision?
- Overlay candidate for any historical-vs-present interactive map: which present-day green spaces date to the Second Empire vs. later additions.

## Notes / caveats

- This file covers only spaces managed by the City of Paris itself. The two large peripheral *bois* (Boulogne, Vincennes) and any state- or RATP-managed green space need to be checked for inclusion before per-capita totals are computed.
- Polygon-only geometry; per-capita computations require population denominators from INSEE at the matching geographic resolution (arrondissement or IRIS — see [[iris-and-ageb]]).
- The file is large (~12 MB); for static maps, a simplification step (e.g. Mapshaper, `topojson-simplify`) is advisable before web display.

## Sources

- `raw/Paris/present-day-data/paris-espaces-verts.geojson` (Paris Open Data, *Espaces verts*)
