---
title: "Summary — Paris Arrondissements GeoJSON"
sources:
  - raw/Paris/spatial/paris-arrondissements.geojson
related:
  - "[[iris-and-ageb]]"
  - "[[spatial-displacement]]"
  - "[[third-place-test]]"
last_updated: 2026-04-18
tags:
  - paris
  - spatial
  - geojson
  - basemap
---

# Summary — Paris Arrondissements GeoJSON

A polygon GeoJSON `FeatureCollection` of Paris arrondissement boundaries. ~213 KB, single-line file, originally from the Paris Open Data portal (`opendata.paris.fr`).

## What it is

The base map layer for every Paris choropleth in the project. Each feature is a Polygon (or MultiPolygon) representing one of the twenty arrondissements in EPSG:4326 (longitude / latitude in WGS 84). The geometry alone is what the project needs; the file's property fields are minimal and any required attributes (arrondissement number, name, area) can be joined in from INSEE Filosofi or Demographia tables by feature order or centroid lookup.

## Use in the project

- Background polygon layer for arrondissement-level choropleths: 1865 indigent share, 1851→1872 population change, present-day median income, real estate price divergence, green space per capita.
- Spatial join target for IRIS-level data (each IRIS is nested within an arrondissement; see [[iris-and-ageb]]) when one needs to aggregate up.
- The spatial input for [[spatial-displacement]] visualizations of center-emptying and periphery-filling 1851 → 1872, and for [[third-place-test]] overlays with `paris-espaces-verts.geojson`.

## Notes / caveats

- Modern boundaries. The file reflects post-1860 arrondissement geometry (the current 20-arrondissement scheme created during the Haussmann period itself). Pre-1860 Paris had only 12 arrondissements with different boundaries; for any pre-1860 comparison use the Demographia "pre-1860" series and a different boundary file rather than this one.
- The 1860 boundary expansion (annexation of communes such as Belleville, Montmartre, Vaugirard) is itself part of the Haussmann story and should be flagged in any 1851-vs-1872 figure that uses these polygons.

## Sources

- `raw/Paris/spatial/paris-arrondissements.geojson` (Paris Open Data, current arrondissement boundaries)
