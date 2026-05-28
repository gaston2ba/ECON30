# REFOCUS Audit (Phase 1)

Date: 2026-05-27  
Project root: `c:/Users/gba09/OneDrive/Bureau/ECON 30 PROJECT`

## 1) Mexico workbook audit (`data/mexico/workbook/DataMexCity.xlsx`)

Workbook found and readable.

### Sheets, dimensions, and variable meaning

- `Contents` — rows=21, cols=3 (sheet index/metadata)
- `1. Population` — rows=32, cols=18 (alcaldia population by decade)
- `2. Density` — rows=31, cols=18 (population density by decade)
- `3. Transit access` — rows=37, cols=18 (transit access proxy by decade)
- `4. Persons per dwelling` — rows=32, cols=18 (crowding proxy by decade)
- `5. Dwellings` — rows=29, cols=18 (housing stock by decade)
- `6. % Electricity` — rows=31, cols=18 (housing infrastructure coverage)
- `7. % Piped water` — rows=30, cols=18 (housing infrastructure coverage)
- `8. % Drainage` — rows=29, cols=18 (housing infrastructure coverage)
- `9. Hospital access` — rows=33, cols=18 (service access proxy)
- `10. Green space` — rows=32, cols=18 (green space metric by decade)
- `11. Third spaces` — rows=32, cols=18 (libraries/museums proxy by decade)

### Key sheets requested in prompt: decade coverage and completeness

For each key sheet (`1. Population`, `2. Density`, `4. Persons per dwelling`, `6. % Electricity`, `7. % Piped water`, `8. % Drainage`):

- Decades present: `1860, 1870, 1880, 1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020`
- Non-null counts per decade: `16` in every decade (full alcaldia coverage in current workbook values)

### Color-coding audit (green/gold/orange provenance)

- Attempted to inspect cell fills using `openpyxl` (`fgColor` on solid fills).
- Result: no explicit fill-color metadata was detected in the parsed cells for the key sheets.
- Implication: the workbook currently available to scripts does not expose provenance coloring programmatically (either colors are absent, theme-based in a way not exposed by `openpyxl`, or saved in a way not read as direct fill colors).
- Action for Phase 2+: treat provenance labels (direct vs aggregate split vs reconstructed) as **not machine-verifiable** from this file alone; if needed, manual workbook inspection in Excel is required.

## 2) Paris data audit (`data/paris/`)

Paris data exists and is non-trivial. CSVs found:

- `paris_air_quality.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,year,pm25_annual_mean,source`
- `paris_green_space.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,total_m2,m2_per_capita`
- `paris_income.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,median_income,filosofi_year`
- `paris_population.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,year,population,density,persons_per_dwelling`
- `paris_third_spaces.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,libraries,museums,total_per_100k`
- `paris_transit.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,decade,stations_cumulative`
- `paris_uqi_panel.csv`  
  Columns: `arrondissement_num,insee_code,arrondissement,year,population,density,persons_per_dwelling,green_space_m2,green_space_m2_per_capita,transit_stations_cumulative,transit_access_per_100k,libraries,museums,third_spaces_per_100k,pm25_annual_mean,median_income_eur,planning_index`

Specific files named in prompt:

- `paris_uqi_2020.csv` was **not found**.
- Existing closest equivalents are `paris_uqi_panel.csv` and `paris_index_2022.json`.

## 3) `index.html` section structure audit

Current chapter section IDs:

- `opening`
- `timeline`
- `index`
- `map`
- `monuments`
- `time-series`
- `findings`
- `debates`
- `sources`

Prose lives inline within each corresponding `<section class="chapter" id="...">` block in `index.html`.

## 4) Data quality / consistency concerns

- **Workbook provenance coding not machine-readable:** can’t automatically separate direct INEGI vs reconstructed values from color fills in current scripted pipeline.
- **Paris PM2.5 variance issue likely remains:** prior pipeline stores citywide PM2.5 for all arrondissements (potential zero-variance component risk).
- **Paris persistence horizon shorter than CDMX:** historical panel available from 1968 onward in `paris_population.csv`, not 1900.
- **Legacy duplicate/transition files exist:** both `data/analysis/regression_results.json` and `data/regression_results.json` appear in tree (possible stale artifact); verify canonical path before Phase 3+ outputs.
- **Map/monument assets recently added:** good for UI, but not central to empirical persistence tests; keep computation scripts decoupled from presentation assets.

## 5) Phase 1 conclusion

Minimum data needed to proceed with persistence and UQI verification is available:

- CDMX: yes (full decade panel through 2020 on key measures).
- Paris: yes for 1968->2020 style persistence and current cross-section regressions.

Main caveat entering Phase 2/3: provenance reconstruction coding in CDMX workbook is not currently script-extractable by fill color and must be acknowledged transparently in methods text.
