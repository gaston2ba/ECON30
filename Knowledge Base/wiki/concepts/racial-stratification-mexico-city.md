---
title: "Racial Stratification in Mexico City"
sources:
  - raw/MexicoCity/catalog.md
related:
  - "[[porfiriato-urbanism]]"
  - "[[mexico-city-class-structure-1900]]"
  - "[[spatial-displacement]]"
  - "[[comparative-mechanism]]"
last_updated: 2026-04-18
tags:
  - mexico-city
  - race
  - mechanism
  - concept
---

# Racial Stratification in Mexico City

The dimension of Mexico City's spatial inequality that has no Paris counterpart, and which the project treats as the single most important *modification* the Haussmann template has to absorb when it is exported across the Atlantic.

## The claim

Mexico City's class geography under the Porfiriato (and persisting today) is not separable from its racial geography. The same neighborhoods that concentrate poverty also concentrate indigenous-identifying populations; the same neighborhoods that concentrate wealth concentrate non-indigenous populations and were Europeanizing in their architectural and cultural language by design. Paris's class divide in the same period was not racially layered in this way.

## Empirical handle: indigenous population by AGEB

`raw/MexicoCity/catalog.md` (dataset 11) names the central modern data source:

- **INEGI Encuesta Intercensal 2015** and **Censo 2020** record indigenous status (self-identification, indigenous-language speaker) at AGEB resolution.
- The catalog's intended figure: scatter of indigenous population share vs. median income by alcaldía (or by AGEB for finer resolution). The expected and well-documented finding (Aguilar & Ward 2003, Duhau & Giglia 2008) is a strong negative correlation.

This figure is item 5 in the Mexico City figure pipeline and is the empirical claim the project makes about the racial layer.

## Why the Porfirian period is the relevant origin

Per Tenorio-Trillo (1996) and Johns (1997), Porfirian urbanism was explicitly Europeanizing:

- The new western *colonias* (Juárez, Roma, Condesa) were architecturally modeled on Paris.
- The cultural production of the period (Gutiérrez Nájera's *Cuentos frágiles*, the World's Fair displays Tenorio-Trillo documents) celebrated a European-coded modernity.
- Indigenous-coded street life — the markets, the *barrios*, the *pulquerías* Ángel de Campo wrote about — was the explicit *negative* against which the Porfirian project defined modernity.

The Porfiriato did not invent racial stratification in Mexico City — that goes back to colonial *castas* and earlier — but it *spatialized* the existing racial hierarchy in a way that maps onto the urban geometry the project is studying. The Porfirian colonia system encoded race into ZIP-code-resolution geography in a way the colonial city had not.

## Why this matters for the comparative argument

The project's central comparative claim (see [[comparative-mechanism]]) is that the same template — universalizing modernization rhetoric, sanitation pretext, spatial reorganization, persistent inequality — operated in both Haussmann's Paris and Díaz's Mexico City. But the template did not produce identical outputs:

- **Paris:** clean class gradient, west / east axis, center → periphery displacement.
- **Mexico City:** mosaic of enclaves (per Duhau & Giglia 2008), class gradient *plus* racial gradient, with the racial gradient making the spatial pattern more fragmented than a simple radial one.

Saying "the Porfiriato was Mexico's Haussmann" without naming the racial layer would be a misreading. The project's contribution is to show both the parallel mechanism *and* this specific divergence.

## Use in the project

- **Figure 5 of the Mexico City pipeline.** Indigenous population share vs. income scatter.
- **Discussion section / written argument.** The single most important point of qualitative divergence between the two cities.
- **Limit on visualization symmetry.** Any comparative figure that uses the same color ramp and axis on both Paris and Mexico City data should be accompanied by a note that one of the underlying variables (race) exists in only one of the two cases.

## Sources

- `raw/MexicoCity/catalog.md` (dataset 11; academic literature section, Aguilar & Ward, Duhau & Giglia, Tenorio-Trillo)
