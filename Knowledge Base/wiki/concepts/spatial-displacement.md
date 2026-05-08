---
title: "Spatial Displacement"
sources:
  - raw/Paris/catalog.md
  - raw/MexicoCity/catalog.md
  - raw/Paris/literature/zola-lassommoir-fr.txt
related:
  - "[[haussmannization]]"
  - "[[porfiriato-urbanism]]"
  - "[[paris-class-structure-1865]]"
  - "[[mexico-city-class-structure-1900]]"
  - "[[iris-and-ageb]]"
  - "[[comparative-mechanism]]"
last_updated: 2026-04-18
tags:
  - mechanism
  - census
  - concept
---

# Spatial Displacement

The empirical core of the project: the claim that 19th-century "modernizing" urban interventions reorganized the residential geography of Paris and Mexico City in measurable, persistent ways, with working-class (and in Mexico City, indigenous) residents systematically pushed out of central renovation zones.

## Paris: center to periphery

Per `raw/Paris/catalog.md` (datasets 1, 3, 4):

- **INSEE Historical Census Data 1851–1921** gives population by arrondissement for every census during and after Haussmann's renovation (1851, 1856, 1861, 1866, 1872, 1876).
- **Demographia** provides parallel pre- and post-1860 series.
- **ICPSR French Historical Census 1833–1925** adds occupational composition.

The expected pattern, visible in any 1851→1872 choropleth: central arrondissements (1st through 6th, especially around the Île de la Cité and Les Halles) lose population in absolute terms; peripheral arrondissements — particularly the post-1860 northern and eastern annexed communes (18th, 19th, 20th) — gain. Zola's *L'Assommoir* is the literary record of the receiving end of that flow, set in the Goutte-d'Or (18th).

The 1860 boundary expansion complicates raw arrondissement-level comparisons across the break — any 1851-vs-1872 figure must use a consistent geometry (typically the post-1860 boundaries with 1851 population reaggregated, or area-weighted reallocation).

## Mexico City: center / east displaced, west attracts

Per `raw/MexicoCity/catalog.md` (datasets 1, 3):

- **INEGI Historical Census Data 1895 / 1900 / 1910** is the modern-methodology record.
- **Cuarteles Population Data** from *Estadísticas Históricas de México* (INEGI, vol. 1) gives the pre-Porfirian baseline and the spatial reorganization into the new colonia system.

The expected pattern: indigenous central barrios and eastern working-class zones stagnate relative to the rapid growth of the new western *colonias* (Juárez, Roma, Condesa, San Rafael, Santa María la Ribera). Unlike Paris, the dominant signal is not central expulsion alone but the *creation* of an elite western zone on land that had previously had a different occupation.

## Persistence to today

The reason this concept matters as more than a 19th-century historical claim is that the displacement geometry is still legible in present-day data:

- Paris: INSEE Filosofi median income at IRIS resolution shows the western arrondissements (6th, 7th, 8th, 16th) at the top and the eastern / northern ones (19th, 20th) at the bottom. The Notaires-INSEE price index since 1992 shows the divergence widening.
- Mexico City: AGEB-level CONEVAL deprivation and INEGI 2020 income show Polanco / Las Lomas at the top and Iztapalapa / Tláhuac / Milpa Alta at the bottom. SHF prices since 2005 show the divergence persisting.

This persistence — the same axis surviving more than a century of subsequent change — is the project's central empirical finding and the basis for [[comparative-mechanism]].

## Sources

- `raw/Paris/catalog.md` (datasets 1, 3, 4, 6, 9)
- `raw/MexicoCity/catalog.md` (datasets 1, 3, 6, 7, 10)
- `raw/Paris/literature/zola-lassommoir-fr.txt`
