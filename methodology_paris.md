# Paris UQI methodology (capstone)

Five components (2022 census year):
- **Parks:** m² green per capita (`paris_green_space.csv`, opendata.paris.fr espaces verts).
- **Transit:** cumulative métro stations per 100k (`paris_transit.csv`, Wikidata/OSM).
- **Density:** INSEE 2022 population / fixed arrondissement area; U-shaped score (middle best).
- **Third spaces:** libraries + museums per 100k (`paris_third_spaces.csv`).
- **Infrastructure:** inverse PM₂.₅ (`paris_air_quality.csv`, Airparif citywide proxy 9 µg/m³ all arrondissements — no arrondissement breakdown; scores tie at 100).

UQI = mean of five component scores (0–100).
