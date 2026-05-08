# Paris / Haussmannization — Raw Source Knowledge Base

Source document: `ECON 30 .pdf` (Paris reading and dataset catalogue).

This file collects the literature, historical datasets, present-day inequality data, spatial/GIS sources, and key academic articles we will use for the Paris side of the project.

## French literature

1. Baudelaire — "Les Yeux des Pauvres" (The Eyes of the Poor), from *Paris Spleen* (1869).
2. Zola — *L'Assommoir* (1877).
3. Zola — *Au Bonheur des Dames* (1883).
4. Victor Hugo — *Les Misérables* (1862).

## Datasets

### Historical — The Haussmann period itself

1. **INSEE Historical Census Data 1851–1921.** The single most important historical dataset. Contains population by arrondissement for every census during and after Haussmannization: 1851, 1856, 1861, 1866, 1872, 1876, and beyond.
   - URL: insee.fr/fr/statistiques/2653233?sommaire=2591397
   - Download format: Excel / dBase
   - Figures you can make: Animated choropleth of population shift by arrondissement from 1851 to 1872, showing the center emptying and the periphery filling in real time. This makes displacement visually undeniable.

2. **Paris 1865 Social Class Census (via Wikipedia / Second Empire).** A remarkable snapshot: according to a census made by the City of Paris in 1865, 42% of Parisians (780,000 people) were classified as indigent and too poor to be taxed; 17% were lower-middle class paying rents under 250 francs; 32% were upper-middle class; and just 3% (50,000 people) were wealthy, paying over 1,500 francs in rent. This is the class distribution during Haussmann's renovation.
   - No download needed. Extract the numbers and build a simple pie or bar chart showing the class structure of the city being "beautified."

3. **Demographia Paris Arrondissement Data (Pre- and Post-1860).** Historical population and density by arrondissement across multiple periods.
   - URL (post-1860): demographia.com/db-paris-arr1999.htm
   - URL (pre-1860): demographia.com/db-paris-arrondpre1860.htm
   - Figures you can make: Side-by-side bar chart of arrondissement populations 1851 vs. 1872 to show which neighborhoods gained and which lost.

4. **ICPSR French Historical Census 1833–1925.** Digitized census data including occupation, education, and demographics by department and arrondissement across the 19th century.
   - URL: icpsr.umich.edu/web/ICPSR/studies/7529
   - Contains occupation data that lets you track working-class vs. bourgeois population share over time.

5. **Cholera Mortality Data by Arrondissement.** Pre-Haussmann cholera deaths were heavily concentrated in working-class central neighborhoods — this is the "before" that justified the renovation. Data is available in the *Journal de la Société Statistique de Paris* (1865), digitized via Numdam.
   - URL: numdam.org/article/JSFS_1865__6__320_0.pdf
   - Figure you can make: Map of 1832 / 1849 cholera deaths by arrondissement overlaid with Haussmann demolition zones, showing that the "sanitation" argument targeted poor neighborhoods specifically.

### Present-Day — The Haussmann legacy today

6. **INSEE Filosofi Income Data (IRIS level).** Disposable income, poverty rates, and Gini coefficient at sub-arrondissement level. This is our primary modern inequality dataset.
   - URL: insee.fr/fr/statistiques/7758862?geo=ARR-751
   - The geographic unit is IRIS — infra-municipality units of about 2,500 inhabitants. INSEE provides a correspondence table to match 1990 data with 1999 IRIS codes for comparability over time.
   - Figure you can make: Income gradient choropleth across Paris showing the west/east divide at IRIS resolution, far sharper than arrondissement-level maps.

7. **Paris Data — Green Spaces GeoJSON.** Every public park, square, and promenade managed by the city, with geometry.
   - Direct download: opendata.paris.fr/explore/dataset/espaces_verts/download/?format=geojson
   - Figure you can make: Map overlaying green space distribution with income by IRIS — testing whether Haussmann's "park for every neighborhood" promise actually holds across income levels today.

8. **Paris Data — Full Portal (opendata.paris.fr).** Beyond green spaces, directly relevant datasets include:
   - Arrondissement boundaries GeoJSON (base map layer).
   - Cultural facilities (theaters, museums, libraries) by location.
   - Social housing (HLM) locations — shows where low-income housing is concentrated today.
   - Real estate transactions — current price per m² by neighborhood.
   - All downloadable as GeoJSON or CSV at opendata.paris.fr/explore/

9. **Notaires-INSEE Property Price Index.** Historical apartment prices in Paris back to 1992 by arrondissement, with some indicators back to the 19th century.
   - URL: igedd.developpement-durable.gouv.fr/house-prices-in-france-property-price-index-french-a1117.html
   - Figure you can make: Line chart of real estate price divergence between wealthy western arrondissements (6th, 7th, 8th, 16th) and eastern ones (19th, 20th) since 1992, showing the Haussmann geography hardening over time.

10. **Income Inequality and Segregation in the Paris Metro Area (1990–2015).** Full spatial dataset underlying the Springer academic chapter, using IRIS-level occupational data from the French census.
    - The eastern departments of Seine-Saint-Denis and Val-de-Marne concentrate bottom occupational groups, while neighborhoods in the Paris metro area are characterized more by the concentration of affluence than by the concentration of disadvantage.
    - Access via chapter: link.springer.com/chapter/10.1007/978-3-030-64569-4_17
    - Underlying INSEE census data downloadable directly from insee.fr

11. **Regional Income Distributions in France 1960–2018 (Banque de France).** Long-run income series by region and sub-region, including Paris.
    - URL: banque-france.fr/system/files/2023-01/wp832.pdf
    - The median monthly income in Seine-Saint-Denis, the poorest sub-region of Paris, was €1,257 per consumption unit in 2010 — a number that sits in stark contrast to the western arrondissements.
    - Figure you can make: Long-run income divergence between Paris center/west vs. banlieue from 1960 to present.

### Spatial / GIS — For your maps

12. **David Rumsey Map Collection.** Georeferenced historical maps of Paris including 1850s, 1860s (during Haussmann), and 1870s (immediately after). Overlayable on modern maps in Python / Folium.
    - URL: davidrumsey.com (search "Paris 1860" or "Paris Haussmann")
    - Figure you can make: Side-by-side or slider map showing pre-Haussmann vs. post-Haussmann street layout, with demolished neighborhoods highlighted.

13. **Charles Marville Photographs (BnF Gallica).** Not a dataset, but a visual primary source — hundreds of photographs of streets before demolition and after reconstruction, all geolocatable.
    - URL: gallica.bnf.fr (search "Marville Paris")
    - Figure you can make: A "then vs. now" panel embedded in the interactive map — click a location, see Marville's 1860s photo alongside a current street view.

14. **OpenStreetMap Paris.** Current café, restaurant, and public space density by neighborhood, downloadable via Overpass API or via download.geofabrik.de
    - Figure you can make: Third-place density map (cafés, parks, public squares per capita) cross-referenced with income — our empirical test of whether "public" spaces are equitably distributed.

## Key academic articles

### For the historical argument

- **Freemark, Bliss & Vale (2022)** — "Housing Haussmann's Paris: the politics and legacy of Second Empire redevelopment," *Planning Perspectives*. The most rigorous recent spatial analysis of Haussmannization's housing consequences. Uses archival data from the Paris Municipal Archives. tandfonline.com/doi/abs/10.1080/02665433.2021.1937293
- **da Costa Meyer (2022)** — *Dividing Paris: Urban Renewal and Social Inequality 1852–1870*, Princeton University Press. Our primary book-length historical source.
- **Harvey (2003)** — *Paris, Capital of Modernity*. Our theoretical spine.

### For the modern inequality argument

- **Préteceille (2021)** — "Income Inequality and Segregation in the Paris Metro Area (1990–2015)," *Springer Urban Book Series*. Uses IRIS-level data to track how Haussmann's geography compounds over time.
- **Métropolitiques (2012)** — "Are Socio-Spatial Inequalities Increasing in the Paris Region?" Free online, excellent summary of the divergence between wealthy western suburbs and Seine-Saint-Denis. metropolitiques.eu/Are-socio-spatial-inequalities.html
- **Rosenthal (Caltech)** — research on cholera mortality in Paris as an economic history dataset. Connects pre-Haussmann public health to class geography.

### Connecting history to present

- **Medium / Clement Renault** — "The Geography of Inequality: A Case Study on Paris." A readable data visualization piece that shows the income gradient clearly and links to the underlying INSEE data. Good model for our own figures. medium.com/perspective-critique/the-geography-of-inequality-30d738139340

## Suggested figure pipeline

From simplest to most ambitious:

1. Bar chart: Paris class structure in 1865 (poor / lower middle / upper middle / wealthy). Simple, striking, sets up the whole argument.
2. Choropleth (static): Population change by arrondissement 1851 to 1872. Shows displacement.
3. Choropleth (static): Median income by IRIS today. Shows the Haussmann geography persisting.
4. Scatter plot: Green space per capita vs. median income by arrondissement. Empirical third-place test.
5. Line chart: Real estate price divergence, western vs. eastern arrondissements, 1992 to 2024.
6. Interactive map: Historical and modern layers with a slider. Capstone visualization.
