---
title: "Data Acquisition Checklist (Priority-Ordered)"
last_updated: 2026-04-18
related:
  - "[[index]]"
  - "[[paris-catalog]]"
  - "[[mexicocity-catalog]]"
  - "[[comparative-mechanism]]"
  - "[[iris-and-ageb]]"
tags:
  - data-acquisition
  - checklist
  - methods
---

# Data Acquisition Checklist (Priority-Ordered)

A working checklist of the datasets named in `raw/Paris/catalog.md` and `raw/MexicoCity/catalog.md` that are *not yet present* in `raw/`, in the order they unlock the most thesis content per unit of effort. Each entry names the source, the exact URL from the catalog, the file format to expect, and the target path inside `raw/`.

The cursorrules processing sequence applies to every download: read → write a `wiki/summaries/` summary → identify or update concept articles → update `wiki/index.md`.

## Priority 1 — unlocks the most blocked claims

These three downloads turn the largest number of currently-promised wiki claims into demonstrated ones.

### 1.1 INSEE Filosofi at IRIS resolution (Paris present-day income)

- **Why first.** Single download. Unlocks the present-day half of [[spatial-displacement]], the income axis of [[third-place-test]], and the empirical basis of [[comparative-mechanism]]'s persistence claim for Paris.
- **Source.** INSEE Filosofi, IRIS resolution, Paris (geo code ARR-751).
- **URL.** `https://www.insee.fr/fr/statistiques/7758862?geo=ARR-751`
- **Format.** CSV / XLSX (download the IRIS-level disaggregated file, not the commune-level summary).
- **Target path.** `raw/Paris/present-day-data/insee-filosofi-iris-paris.csv` (and `.xlsx` if both are offered).
- **Companion file needed.** The 1990↔1999 IRIS correspondence table from INSEE, for any historical comparability work. Save as `raw/Paris/present-day-data/insee-iris-correspondence-1990-1999.csv`.
- **Wiki follow-up.** New summary `wiki/summaries/insee-filosofi-iris.md`; update `spatial-displacement`, `third-place-test`, `iris-and-ageb`, `comparative-mechanism`.

### 1.2 INEGI 1895 occupational structure tables (Mexico City baseline)

- **Why first.** Currently the wiki has only one number for the Mexico City c. 1900 class structure (~60–65% jornaleros + servants). Without the finer breakdown, the paired Paris/Mexico City class-structure bar chart cannot be honestly built.
- **Source.** INEGI digitized 1895 census, Federal District section.
- **URL.** `https://internet.contenidos.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/historicos/2104/702825427952/702825427952.pdf`
- **Format.** PDF (tables — will require digitization, either manual transcription or a tabular-PDF tool such as `tabula-py` or `camelot-py`).
- **Target path.** `raw/MexicoCity/historical/inegi-census-1895-fd-occupations.pdf`. Once transcribed, store the table as `raw/MexicoCity/historical/inegi-census-1895-fd-occupations.csv` with a transcription note.
- **Wiki follow-up.** Update `mexico-city-class-structure-1900.md` with a real table; new summary `wiki/summaries/inegi-census-1895.md`.

### 1.3 INEGI Censo 2020 + CONEVAL (Mexico City present-day)

- **Why first.** The Mexico City equivalent of 1.1. Together with 1.1, makes the symmetric present-day persistence figure (paired AGEB / IRIS choropleths) possible.
- **Sources.** INEGI Censo 2020 income / poverty at AGEB; CONEVAL Índice de Rezago Social 2020 at AGEB / municipal level.
- **URLs.**
  - INEGI: `https://www.inegi.org.mx/programas/ccpv/2020/`
  - CONEVAL: `https://www.coneval.org.mx/Medicion/IRS/Paginas/Indice-de-Rezago-social-2020.aspx`
- **Format.** CSV / XLSX (INEGI provides downloadable AGEB-level files; CONEVAL provides Excel with sheet per geography).
- **Target paths.**
  - `raw/MexicoCity/present-day-data/inegi-censo-2020-ageb-cdmx.csv`
  - `raw/MexicoCity/present-day-data/coneval-rezago-social-2020-cdmx.xlsx`
- **Wiki follow-up.** New summaries for both; update `spatial-displacement`, `iris-and-ageb`, `racial-stratification-mexico-city` (the indigenous-population variable lives in the same Censo 2020 release), `comparative-mechanism`.

## Priority 2 — unlocks specific concept articles

### 2.1 Cholera mortality by Paris arrondissement, 1832 / 1849

- **Source.** *Journal de la Société Statistique de Paris* 1865, via Numdam.
- **URL.** `http://www.numdam.org/article/JSFS_1865__6__320_0.pdf`
- **Format.** PDF (table inside an article).
- **Target path.** `raw/Paris/historical/jssp-1865-cholera-mortality.pdf`. Transcribe the table to `raw/Paris/historical/jssp-1865-cholera-mortality.csv`.
- **Unlocks.** The Paris half of [[sanitation-as-pretext]] becomes empirically demonstrable.

### 2.2 INSEE / Demographia historical population by arrondissement, 1851–1921

- **Source.** INSEE historical census; Demographia mirror tables.
- **URLs.**
  - INSEE: `https://www.insee.fr/fr/statistiques/2653233?sommaire=2591397`
  - Demographia post-1860: `https://www.demographia.com/db-paris-arr1999.htm`
  - Demographia pre-1860: `https://www.demographia.com/db-paris-arrondpre1860.htm`
- **Format.** Excel / dBase / HTML tables.
- **Target paths.**
  - `raw/Paris/historical/insee-paris-arr-population-1851-1921.xlsx`
  - `raw/Paris/historical/demographia-paris-arr-pre1860.html`
  - `raw/Paris/historical/demographia-paris-arr-post1860.html`
- **Unlocks.** The Paris half of [[spatial-displacement]] becomes demonstrable; enables the 1851→1872 choropleth (figure 2 in the catalog's pipeline).
- **Caveat.** The 1860 boundary expansion needs to be handled — see the note in [[paris-arrondissements-geojson]].

### 2.3 INEGI Censo 1895 / 1900 / 1910 historical population by cuartel

- **Source.** *Estadísticas Históricas de México*, INEGI vol. 1 (Population).
- **URL.** `https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=702825006883`
- **Format.** PDF / Excel (depends on the chapter).
- **Target path.** `raw/MexicoCity/historical/inegi-estadisticas-historicas-vol1-poblacion.pdf` (then transcribed CSVs per table).
- **Unlocks.** The Mexico City half of [[spatial-displacement]]; figure 2 of the Mexico City pipeline.

### 2.4 Paris Open Data — arrondissement boundaries (verify)

- **Note.** `raw/Paris/spatial/paris-arrondissements.geojson` is already present, but its property fields are minimal. If the source dataset has been updated to include `c_ar`, `l_ar`, `surface`, `perimetre`, etc., re-download to get a version with attached attributes. Otherwise these can be joined in from a small CSV.
- **URL.** `https://opendata.paris.fr/explore/dataset/arrondissements/`
- **Target.** Replace `raw/Paris/spatial/paris-arrondissements.geojson` only if a richer property schema is available.

### 2.5 Datos Abiertos CDMX — alcaldía / colonia boundaries + áreas verdes

- **Source.** Datos Abiertos CDMX.
- **URLs.**
  - Áreas verdes: `https://datos.cdmx.gob.mx/dataset/areas-verdes`
  - Alcaldía / colonia boundaries: `https://datos.cdmx.gob.mx` (search "alcaldías", "colonias")
- **Format.** GeoJSON / Shapefile.
- **Target paths.**
  - `raw/MexicoCity/spatial/cdmx-alcaldias.geojson`
  - `raw/MexicoCity/spatial/cdmx-colonias.geojson`
  - `raw/MexicoCity/present-day-data/cdmx-areas-verdes.geojson`
- **Unlocks.** The Mexico City half of [[third-place-test]]; symmetric spatial joins for any side-by-side Paris/Mexico City visualization.

## Priority 3 — fills the literature asymmetry

The current `raw/` has four Hugo files but zero Mexican literary works. The Mexican literature catalog names four primary texts; at least one should be added to balance the dossier.

### 3.1 Federico Gamboa, *Santa* (1903)

- **Source.** Wikisource / Project Gutenberg–equivalent (the Spanish Wikisource has the full text).
- **URL.** `https://es.wikisource.org/wiki/Santa` (or any Spanish-language plain-text source).
- **Target path.** `raw/MexicoCity/literature/gamboa-santa-es.txt`.
- **Wiki follow-up.** New summary `wiki/summaries/gamboa-santa.md`; cross-link from `porfiriato-urbanism`, `mexico-city-class-structure-1900`, `spatial-displacement`.

### 3.2 Guillermo Prieto, *Memorias de mis tiempos* (1876) — pre-Porfirian baseline

- **URL.** Search the Biblioteca Virtual Miguel de Cervantes (`https://www.cervantesvirtual.com`) for the full text.
- **Target path.** `raw/MexicoCity/literature/prieto-memorias-de-mis-tiempos-es.txt`.

### 3.3 Ángel de Campo, chronicles

- **URL.** Hemeroteca Nacional Digital de México (`https://hndm.unam.mx`) for the original *Semana Alegre* and *Ocios y apuntes* serials, or any digitized anthology.
- **Target path.** `raw/MexicoCity/literature/campo-chronicles-selected-es.txt`.

### 3.4 Manuel Gutiérrez Nájera, *Cuentos frágiles* (1883)

- **URL.** Wikisource / cervantesvirtual.com.
- **Target path.** `raw/MexicoCity/literature/gutierrez-najera-cuentos-fragiles-es.txt`.

## Priority 4 — long-tail and capstone-figure inputs

These are listed here so they don't get forgotten; they are not blocking the early figures.

- **Notaires-INSEE property price index** (catalog Paris #9). Target: `raw/Paris/present-day-data/notaires-insee-price-index.xlsx`.
- **Banque de France WP832 long-run regional income series** (catalog Paris #11). Target: `raw/Paris/present-day-data/banque-de-france-wp832.pdf`.
- **SHF Mexico City property price index** (catalog MX #10). Target: `raw/MexicoCity/present-day-data/shf-indice-precios-vivienda.pdf`.
- **OpenStreetMap extracts for Paris and Mexico City** for café / mercado / public-square density. Use Geofabrik or Overpass API. Targets: `raw/Paris/present-day-data/osm-paris-amenities.geojson`, `raw/MexicoCity/present-day-data/osm-cdmx-amenities.geojson`.
- **Marville / Casasola photograph metadata.** The images themselves are not strictly needed in `raw/` (large, copyrighted versions exist on Gallica / Mediateca INAH); a CSV of geolocated photographs with stable URLs is enough. Targets: `raw/Paris/spatial/marville-photo-index.csv`, `raw/MexicoCity/spatial/casasola-photo-index.csv`.
- **David Rumsey + Mapoteca Orozco y Berra historical maps.** Same pattern — store an index CSV with georeferencing parameters and stable URLs rather than the high-resolution images themselves.
- **Memorias de Obras Públicas (Porfirian public-works investment).** Source: Hemeroteca Nacional Digital de México (`https://hndm.unam.mx`). Annual volumes; transcription will be substantial. Target: `raw/MexicoCity/historical/memorias-obras-publicas/`.

## Conventions for any new download

So that future wiki passes don't have to reverse-engineer provenance:

- **One file per URL.** Do not bundle multiple downloads into a single archive in `raw/`.
- **Record the access date.** Either rename the file with a date suffix (`-2026-04-18`) or place a sibling `.url` or `.txt` file with the URL and date.
- **No transcriptions in `raw/`.** Transcribed CSVs from PDF tables go in `data/` at the project root, with a clear note in the file or a sibling README pointing back to the `raw/` PDF they were transcribed from.
- **Update `wiki/index.md` after every new source.** Per the cursorrules, this is non-optional.

## Sources

- `raw/Paris/catalog.md`
- `raw/MexicoCity/catalog.md`
