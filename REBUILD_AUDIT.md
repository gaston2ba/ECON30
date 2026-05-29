# REBUILD_AUDIT.md — Phase 1 (read-only audit)

**Date:** 2026-05-29  
**Branch at audit:** `paris-twin`  
**Target rebuild branch:** `parallel-rebuild` (to be created in Phase 8)

## Current `index.html` (88 lines)

Not the original capstone. It is a **minimal comparison shell** (`compare-shell`) with:

| Block | Content |
|-------|---------|
| Masthead | Research question + short intro |
| Toolbar | Shared decade slider, play, 11-variable toggles |
| Row 1 | UQI choropleth (Paris \| CDMX) |
| Row 2 | HDI choropleth |
| Row 3 | UQI × HDI scatter |
| Row 4 | UQI line trajectories |
| Footer | Links to `/paris/`, `/cdmx/` |

**Fetch paths (`script.js`):**

- `data/paris/uqi-by-arrondissement.json`
- `data/paris/hdi-by-arrondissement.json`
- `data/paris/arrondissements.geojson`
- `data/cdmx/uqi-by-alcaldia.json`
- `data/cdmx/hdi-by-alcaldia.json`
- `data/cdmx/alcaldias.geojson`

**Missing vs. rebuild spec:** timelines, opening prose, 5-component UQI toggles, synchronized 4-map hover, banded over-time charts, glossary inline, newsprint CSS.

## Archived capstone (`docs/archive-capstone-index.html`, ~2584 lines)

Full **newsprint** site: masthead, timelines, maps, regressions, persistence interactives, glossary (`.gloss-pair` / `.gloss-trigger` / `.gloss-pop`), embedded CSS variables (`--paper`, `--ink`, wine/verdigris accents).

**Fetch paths (representative):**

- `data/maps/paris_arrondissements.geojson`, `data/maps/mexico_alcaldias.geojson`
- `data/monuments/paris.json`, `data/monuments/mexico.json`
- `data/analysis/web_embeds.json`, `data/analysis/regression_results.json`
- `data/analysis/persistence_interactives.json`
- D3 CDN, `js/geo-maps.js`, `js/map-utils.js`, inline `DATA` / `state`

**Reuse for rebuild:** visual tokens, glossary pattern, timeline HTML structure, masthead copy patterns.

## `js/geo-maps.js`

- Loads GeoJSON from `data/maps/*`, monuments JSON, uses D3 + `CityMapUtils`.
- Tied to old capstone `state.city`, `DATA`, layer buttons (`.map-layer-btn`).
- **Reuse:** projection/choropleth patterns; **adapt** for dual-city parallel + `hoverState` (Phase 6).

## Mexico data — `data/mexico/workbook/DataMexCity.xlsx`

**Path note:** Prompt cites `data/Info for index Mex City/`; repo has `data/mexico/workbook/DataMexCity.xlsx`. Root also has `DataMexCity - Copy.xlsx`.

**Sheets present (all required):**

1. Population  
2. Density  
3. Transit access  
4. Persons per dwelling  
5. Dwellings  
6. % Electricity  
7. % Piped water  
8. % Drainage  
9. Hospital access  
10. Green space  
11. Third spaces  

Plus `Contents`. **Ready for Phase 2.**

**Existing derivatives:**

- `data/cdmx/uqi-by-alcaldia.json` — Andres 11-variable decade panel (different UQI definition than rebuild spec)
- `data/mexico/raw/hdi_mexico_pnud.csv` — transcribed PNUD municipal HDI
- `data/cdmx/hdi-by-alcaldia.json` — 2000/2010/2020 decades

## Paris data — `data/paris/`

| File | Status |
|------|--------|
| `paris_population.csv` | INSEE 1968–2022 |
| `paris_uqi_panel.csv` | Prior UQI panel |
| `paris_green_space.csv`, `paris_transit.csv`, `paris_third_spaces.csv`, `paris_income.csv`, `paris_air_quality.csv` | Present |
| `historical/paris_population_long.csv` | Demographia + INSEE |
| `arrondissements.geojson`, `uqi-by-arrondissement.json`, `hdi-by-arrondissement.json` | Web-export shape (11 vars) |
| `raw/insee_751*.json` | Dossier scrapes — **check for diploma tables for HDI education** |

**Maps:** `data/maps/paris_arrondissements.geojson` (also `data/paris/arrondissements.geojson`).

**Gaps for rebuild spec:**

- `data/analysis/uqi_paris_2022.csv` — 5 components (parks, transit, density, thirdspace, infrastructure/air quality)
- `data/analysis/hdi_paris_2022.csv` — UN HDR geometric mean with documented raw CSVs
- `data/paris/raw/life_expectancy_arrondissement.csv`, `education_arrondissement.csv`, `income_arrondissement_ppp.csv` — partial/missing

## Scripts — reuse vs. retire

| Script | Verdict |
|--------|---------|
| `build_paris_data.py` | **Reuse** — INSEE, Wikidata transit, green space |
| `collect_paris_historical.py` | **Reuse** — pre-1968 population |
| `export_mexico_data.py` | **Reuse** — Excel parsing patterns |
| `build_paris_uqi.py` (current) | **Replace** — new 5-component spec + `data/analysis/` outputs |
| `build_paris_hdi.py` (current) | **Extend/replace** — add raw CSVs + `data/analysis/hdi_paris_2022.csv` |
| `build_cdmx_hdi.py` | **Replace** → `build_mexico_hdi.py` per spec |
| `sync_cdmx_from_main.py`, `export_paris_uqi_web.py` | **Keep** for `/cdmx/` `/paris/` subsites; not capstone root |
| `compute_persistence.py`, `build_persistence_interactives.py` | **Retire** from main capstone (out of scope) |
| `patch_index_embeds.py`, `recompute_uqi.py` | **Review** — may inform Mexico normalization |

## Figures / other

- `figures/` — regression HTML, old interactives; not required for parallel rebuild spine.
- `cdmx/`, `paris/` — Andres-style single-city apps; keep, not the capstone homepage.

## Phase 1 conclusion

**Present:** GeoJSON both cities, Mexico Excel, Paris CSV panel, archived capstone HTML/CSS/glossary, partial HDI/UQI JSON, `geo-maps.js`.

**Must build:** Phase 2–4 analysis CSVs, new `index.html` + `js/capstone.js` + capstone CSS, synchronized hover, 5-component UQI, timelines, banded line charts, `methodology_mexico.md`, `data/analysis/hdi_paris_methodology.md`.

**No files modified in Phase 1.**
