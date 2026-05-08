---
title: "Third-Place Test"
sources:
  - raw/Paris/catalog.md
  - raw/MexicoCity/catalog.md
  - raw/Paris/literature/baudelaire-paris-spleen-en.txt
  - raw/Paris/present-day-data/paris-espaces-verts.geojson
related:
  - "[[haussmannization]]"
  - "[[porfiriato-urbanism]]"
  - "[[iris-and-ageb]]"
  - "[[comparative-mechanism]]"
last_updated: 2026-04-18
tags:
  - mechanism
  - public-space
  - concept
---

# Third-Place Test

The project's empirical test of whether "public" spaces produced by 19th-century modernization — parks, squares, boulevards, cafés — are actually equitably distributed today, or whether their official universalism masks a class-skewed allocation that follows the same west/east axis as income and property prices.

## Why "third place"

The term refers to the sociological category of public, semi-public, and quasi-commercial spaces that are neither home (first place) nor workplace (second place): cafés, parks, public squares, libraries, mercados. Both Haussmann's "park for every neighborhood" rhetoric and Díaz's monumental boulevards and parks were defended in third-place language — that they would belong to all citizens of the modern city.

## The test, operationally

For each city, compute a per-capita measure of third-place provision at the finest geographic resolution available, regress it against median income at the same resolution, and look at the slope and the residuals.

**Paris (operational):**

- *Numerator:* green-space surface area from `raw/Paris/present-day-data/paris-espaces-verts.geojson` aggregated by arrondissement or IRIS; café/restaurant/public-space density from OpenStreetMap (Overpass API) at the same resolution.
- *Denominator:* INSEE population by arrondissement or IRIS.
- *Income variable:* INSEE Filosofi median disposable income at IRIS resolution. See [[iris-and-ageb]].
- *Boundary layer:* `raw/Paris/spatial/paris-arrondissements.geojson` (or an IRIS GeoJSON, not yet in `raw/`).

**Mexico City (operational):**

- *Numerator:* green-space surface area from Datos Abiertos CDMX *áreas verdes*; café / mercado / public-square density from OpenStreetMap.
- *Denominator:* INEGI population by AGEB or alcaldía.
- *Income variable:* INEGI 2020 income or CONEVAL deprivation index by AGEB.
- *Boundary layer:* alcaldía / colonia GeoJSON from Datos Abiertos CDMX (not yet in `raw/`).

The two scatter plots — green space per capita vs. median income, by arrondissement (Paris) and by alcaldía (Mexico City) — are the catalog's items 4 in both figure pipelines.

## Literary anchor

Baudelaire's "The Eyes of the Poor" (see [[baudelaire-paris-spleen]]) is the project's best 19th-century articulation of the failure of universal public space: the new boulevard café is physically open, gas-lit, visible from the street — and experienced by the poor family across the road as a threshold they cannot cross. The empirical third-place test is the modern numerical version of that scene.

## What the test is supposed to show

The project's hypothesis is that:

1. In both cities, raw per-capita green space is *not* dramatically west-skewed — the historical investment did spread parks across the city.
2. But once one weights by *quality, accessibility, and adjacent retail density*, and once one looks at café / mercado / restaurant density rather than parks alone, a clear west-skew emerges that tracks income closely.
3. The Marville (Paris) and Casasola (Mexico City) photographs supply the qualitative complement to the quantitative scatter.

If the data instead show flat or counter-axis distributions, that is itself an interesting and reportable finding — the project's frame should not predetermine the empirical result.

## Sources

- `raw/Paris/catalog.md` (datasets 7, 8, 14)
- `raw/MexicoCity/catalog.md` (datasets 8, 9, 14)
- `raw/Paris/present-day-data/paris-espaces-verts.geojson`
- `raw/Paris/literature/baudelaire-paris-spleen-en.txt`
