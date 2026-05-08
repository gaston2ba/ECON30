---
title: "Knowledge Base Index"
last_updated: 2026-04-18
tags:
  - index
---

# Knowledge Base Index

Master navigation for the ECON 30 comparative-urbanism wiki: Haussmann's Paris (1853–1870) and Díaz's Mexico City (1876–1911), with present-day inequality as the persistence test.

## Central thesis

- [[comparative-mechanism]] — The project's core claim: Haussmann's Paris and Díaz's Mexico City instantiate the same five-step modernization mechanism, the parallel is empirically auditable on matched datasets, and its class geography is still legible in 2020-resolution data — with race as the structural divergence Mexico City forces the model to absorb.

## Paris

### Concepts
- [[haussmannization]] — The Second Empire transformation of Paris (1853–1870): demolition, boulevards, parks, and the produced class-visible street.
- [[paris-class-structure-1865]] — The mid-renovation class snapshot (42% indigent, 17% lower-middle, 32% upper-middle, 3% wealthy) used as the project's Paris baseline.

### Source summaries
- [[paris-catalog]] — Inventory of every Paris-side literary, historical, present-day, spatial, and academic source the project will use, with figure pipeline.
- [[hugo-les-miserables]] — Pre-Haussmann central Paris and the political reading of boulevard width via the 1832 barricade chapters.
- [[zola-lassommoir]] — Naturalist record of the post-Haussmann periphery (Goutte-d'Or, 18th arr.) that absorbed displaced central workers.
- [[zola-au-bonheur-des-dames]] — The new Haussmannian boulevard read as a retail apparatus and engine of bourgeois consumption.
- [[baudelaire-paris-spleen]] — Source of "The Eyes of the Poor," the project's literary anchor for the failure of universal public space on the new boulevard.
- [[paris-arrondissements-geojson]] — Polygon GeoJSON of the twenty modern arrondissements; base-map layer for every Paris choropleth.
- [[paris-espaces-verts-geojson]] — Polygon GeoJSON of every City of Paris-managed green space; numerator for the third-place test.

## Mexico City

### Concepts
- [[porfiriato-urbanism]] — Díaz's remaking of Mexico City explicitly modeled on Haussmann, with the western *colonias* as the receiving end of investment.
- [[mexico-city-class-structure-1900]] — The c. 1895 occupational baseline (~60–65% jornaleros and domestic servants) used as the project's Mexico City counterpart to the 1865 Paris snapshot.
- [[racial-stratification-mexico-city]] — The dimension with no Paris equivalent: indigenous-population-share by AGEB as the empirical handle on a class-and-race-stratified geography.

### Source summaries
- [[mexicocity-catalog]] — Inventory of every Mexico City-side literary, historical, present-day, spatial, and academic source the project will use, with figure pipeline and Paris pairings.

## Cross-cutting mechanisms

- [[sanitation-as-pretext]] — The recurring move by which real epidemic mortality data legitimates demolitions whose actual footprint tracks class (and race) more closely than disease.
- [[spatial-displacement]] — The empirical core: 1851–1872 Paris and 1895–1910 Mexico City census evidence that "modernization" reorganized residential geography in ways still visible at IRIS / AGEB resolution today.
- [[third-place-test]] — Operational test of whether the parks, squares, and cafés produced by 19th-century renovation are equitably distributed today, or whether their official universalism masks a class-skewed allocation.

## Methods

- [[iris-and-ageb]] — INSEE's IRIS and INEGI's AGEB as the parallel sub-municipal statistical units that make modern Paris / Mexico City inequality measurements directly comparable.

## Outputs

- [[data-acquisition-checklist]] — Priority-ordered list of catalog-named datasets not yet in `raw/`, with exact URLs, target paths, and a table of which wiki claims each download would unlock.
- [[figure-01-class-structure]] — Paired bar chart of Paris 1865 vs. Mexico City c. 1895 class structure. Paris panel fully rendered; Mexico City panel deliberately shows the 60–65% jornaleros bar alongside explicit blanks for the categories still gated on acquisition-checklist priority 1.2. Output image at `figures/figure-01-paris-1865-mexico-city-1895-class-structure.png`.

## Coverage map

Raw sources currently in `raw/` and how each is covered in the wiki:

| Raw source | Summary | Concepts citing it |
|---|---|---|
| `raw/Paris/catalog.md` | [[paris-catalog]] | [[haussmannization]], [[paris-class-structure-1865]], [[sanitation-as-pretext]], [[spatial-displacement]], [[third-place-test]], [[iris-and-ageb]], [[comparative-mechanism]] |
| `raw/MexicoCity/catalog.md` | [[mexicocity-catalog]] | [[porfiriato-urbanism]], [[mexico-city-class-structure-1900]], [[sanitation-as-pretext]], [[spatial-displacement]], [[third-place-test]], [[iris-and-ageb]], [[racial-stratification-mexico-city]], [[comparative-mechanism]] |
| `raw/Paris/literature/baudelaire-paris-spleen-en.txt` | [[baudelaire-paris-spleen]] | [[haussmannization]], [[third-place-test]] |
| `raw/Paris/literature/zola-lassommoir-fr.txt` | [[zola-lassommoir]] | [[haussmannization]], [[paris-class-structure-1865]], [[spatial-displacement]] |
| `raw/Paris/literature/zola-au-bonheur-des-dames-fr.txt` | [[zola-au-bonheur-des-dames]] | [[haussmannization]] |
| `raw/Paris/literature/hugo-miserables-*` (4 files) | [[hugo-les-miserables]] | [[haussmannization]], [[paris-class-structure-1865]] |
| `raw/Paris/spatial/paris-arrondissements.geojson` | [[paris-arrondissements-geojson]] | [[third-place-test]], [[spatial-displacement]] |
| `raw/Paris/present-day-data/paris-espaces-verts.geojson` | [[paris-espaces-verts-geojson]] | [[third-place-test]] |

## Known gaps

For the full priority-ordered list with URLs and target paths, see [[data-acquisition-checklist]]. Short version:

- **Priority 1** (unlocks the most wiki claims): INSEE Filosofi at IRIS resolution (Paris present-day); INEGI 1895 occupational tables (Mexico City baseline detail); INEGI Censo 2020 + CONEVAL at AGEB (Mexico City present-day).
- **Priority 2** (unlocks specific concept articles): cholera mortality 1865 JSSP; INSEE / Demographia historical Paris population 1851–1921; INEGI historical population by cuartel; Datos Abiertos CDMX boundary and green-space GeoJSONs.
- **Priority 3** (fills the literature asymmetry): Gamboa *Santa*, Prieto *Memorias de mis tiempos*, Campo chronicles, Gutiérrez Nájera *Cuentos frágiles*.
- **Priority 4** (long-tail): Notaires-INSEE price index, SHF price index, Banque de France WP832, OSM amenities extracts, Marville / Casasola photo indexes, David Rumsey / Mapoteca historical map indexes, *Memorias de Obras Públicas*.

Once any of these arrive in `raw/`, follow the cursorrules processing sequence: summarize → identify concepts → create or update concept articles → update related backlinks → update this index.
