---
title: "IRIS and AGEB — Sub-Municipal Geographic Units"
sources:
  - raw/Paris/catalog.md
  - raw/MexicoCity/catalog.md
related:
  - "[[spatial-displacement]]"
  - "[[third-place-test]]"
  - "[[comparative-mechanism]]"
last_updated: 2026-04-18
tags:
  - data
  - geography
  - method
  - concept
---

# IRIS and AGEB — Sub-Municipal Geographic Units

The two sub-municipal statistical geographies the project uses to make Paris and Mexico City inequality measurements directly comparable: France's **IRIS** (Îlots Regroupés pour l'Information Statistique) and Mexico's **AGEB** (Área Geoestadística Básica).

## Why the choice of unit matters

Arrondissement / alcaldía-level data systematically *understates* spatial inequality because each unit averages over very large internal heterogeneity. The 11th arrondissement has both the rue de Charonne and parts adjacent to the Marais; Iztapalapa contains both relatively serviced colonias and severely deprived ones. Sub-municipal units make the actual income gradient visible.

Both IRIS and AGEB were designed for census reporting at populations of roughly 1,500–2,500 inhabitants per unit. That target population was chosen specifically to balance statistical reliability (large enough sample) against geographic resolution (small enough to capture neighborhood-scale variation). The two systems are not identical but are operationally close enough that comparable choropleths can be built.

## IRIS (France, INSEE)

- **Definition.** Îlots Regroupés pour l'Information Statistique. Established by INSEE in the late 1990s as the standard sub-municipal census unit for communes of 10,000+ inhabitants.
- **Scale.** ~2,500 inhabitants per IRIS, by design.
- **Types.** *Habitat* (residential), *activité* (job-concentrated), *divers* (parks, cemeteries, rail yards). For inequality work, only *habitat* IRIS carry meaningful income data.
- **Project use.** INSEE Filosofi disposable income, poverty rate, and Gini coefficient at IRIS resolution. Préteceille (2021) uses IRIS occupational data for 1990–2015 segregation analysis. INSEE provides 1990↔1999 IRIS correspondence tables for historical comparability.
- **Catalog source.** `raw/Paris/catalog.md` datasets 6 and 10.

## AGEB (Mexico, INEGI)

- **Definition.** Área Geoestadística Básica. The basic statistical area used by INEGI for census operations.
- **Scale.** ~1,500–2,500 inhabitants per urban AGEB.
- **Types.** *Urbano* (the relevant type for Mexico City inequality work) and *rural*.
- **Project use.** INEGI Censo 2020 income quintiles and deprivation indices at AGEB resolution; CONEVAL multidimensional poverty index (ITER 2020) at AGEB resolution; INEGI Encuesta Intercensal 2015 / Censo 2020 indigenous-population data by AGEB (the empirical handle on [[racial-stratification-mexico-city]]).
- **Catalog source.** `raw/MexicoCity/catalog.md` datasets 6, 7, 11.

## Practical comparability notes

- **Population denominators are roughly aligned** (~2,500 each), so per-capita measures (income, green space, café density) are directly comparable in their intuition.
- **Geometry is not.** IRIS polygons and AGEB polygons differ in shape, density, and definition rules. Comparisons should be visualized in parallel choropleths, not in a single combined raster, and any quantitative claim about "Mexico City has X times the inequality of Paris" needs to be made at a higher geographic level (alcaldía vs. arrondissement) where the units are more obviously analogous.
- **Modern boundaries only.** Neither IRIS nor AGEB existed in the 19th century. Historical census data must be aggregated to coarser units (arrondissement, cuartel, delegación) for any pre-1950 comparison.

## Why this concept gets its own article

Because the comparability of the modern Paris / Mexico City inequality story depends entirely on the existence of these two parallel sub-municipal statistical systems. Without them the project would be limited to arrondissement / alcaldía choropleths, which would substantially underplay both the magnitude and the spatial pattern of the inequality the project is trying to document.

## Sources

- `raw/Paris/catalog.md` (datasets 6, 10)
- `raw/MexicoCity/catalog.md` (datasets 6, 7, 11)
