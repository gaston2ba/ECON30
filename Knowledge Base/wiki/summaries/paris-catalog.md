---
title: "Summary — Paris / Haussmannization Source Catalog"
sources:
  - raw/Paris/catalog.md
related:
  - "[[haussmannization]]"
  - "[[paris-class-structure-1865]]"
  - "[[sanitation-as-pretext]]"
  - "[[spatial-displacement]]"
  - "[[third-place-test]]"
  - "[[iris-and-ageb]]"
  - "[[comparative-mechanism]]"
last_updated: 2026-04-18
tags:
  - paris
  - catalog
  - haussmann
---

# Summary — Paris / Haussmannization Source Catalog

`raw/Paris/catalog.md` is a curated meta-source: it does not itself contain primary data, but inventories the literary, historical, and present-day datasets the project will use for the Paris side of the comparison.

## What the catalog contains

- **French literature for the Haussmann period.** Baudelaire's "Les Yeux des Pauvres" (*Paris Spleen*, 1869); Zola's *L'Assommoir* (1877) and *Au Bonheur des Dames* (1883); Hugo's *Les Misérables* (1862). These are the period-eye primary sources.
- **Historical datasets (1851–1921).** INSEE arrondissement censuses (1851/1856/1861/1866/1872/1876), the 1865 Paris social class snapshot (42% indigent, 17% lower-middle, 32% upper-middle, 3% wealthy), the Demographia pre/post-1860 series, ICPSR digitized French census data, and cholera mortality data from the *Journal de la Société Statistique de Paris* (1865, via Numdam).
- **Present-day inequality datasets.** INSEE Filosofi income data at IRIS resolution (~2,500 inhabitants/unit), Paris Open Data green spaces and arrondissement boundaries, social housing locations, real estate transactions, the Notaires-INSEE property price index back to 1992, the Préteceille IRIS-level segregation dataset (1990–2015), and the Banque de France long-run regional income series (1960–2018).
- **Spatial / GIS sources.** David Rumsey georeferenced historical maps (1850s–1870s); Charles Marville's pre- and post-demolition photographs (BnF Gallica); OpenStreetMap Paris for current third-place density.
- **Key academic literature.** Freemark, Bliss & Vale (2022); da Costa Meyer (2022); Harvey (2003); Préteceille (2021); Rosenthal (Caltech) on cholera; Métropolitiques (2012); Renault (Medium) on inequality geography.

## Argument the catalog is built to support

The Paris dossier is organized to demonstrate four linked claims, each backed by the listed datasets:

1. **Pre-Haussmann Paris was poor and centralized.** The 1865 snapshot and ICPSR occupational data establish the class structure of the city Haussmann was about to remake.
2. **Cholera mortality concentrated in poor central neighborhoods.** The *Journal de la Société Statistique* data lets one overlay disease maps with the actual demolition zones — evidence for the [[sanitation-as-pretext]] reading.
3. **Renovation displaced the working class outward.** INSEE 1851–1872 censuses and the Demographia series make population shift visible at arrondissement resolution — see [[spatial-displacement]].
4. **The Haussmann geography persists in present-day inequality.** INSEE Filosofi (IRIS), Notaires-INSEE prices, and Préteceille's segregation analysis show the western/eastern divergence continuing through 2015–2024.

## Suggested figure pipeline (per the catalog)

1. Bar chart of the 1865 class structure.
2. Choropleth of arrondissement population change 1851 → 1872.
3. IRIS-level median income choropleth today.
4. Scatter of green space per capita vs. median income by arrondissement.
5. Line chart of real estate price divergence, west vs. east, 1992–present.
6. Interactive historical/modern slider map.

## Pairings with Mexico City

Each dataset has a Mexico City counterpart documented in [[mexicocity-catalog]]: INSEE↔INEGI censuses, IRIS↔AGEB inequality units, Marville↔Casasola photographs, David Rumsey↔Mapoteca Orozco y Berra. The 1865 Paris class structure pairs with the c. 1900 Federal District occupational structure.

## Sources

- `raw/Paris/catalog.md`
