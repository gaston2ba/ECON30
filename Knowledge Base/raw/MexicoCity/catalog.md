# Mexico City / Porfiriato — Raw Source Knowledge Base

Source document: `ECON 30 (1).pdf` (Mexico City reading and dataset catalogue).

This file collects the literature, historical datasets, present-day inequality data, spatial/GIS sources, and key academic articles we will use for the Mexico City side of the project. Wherever relevant, pairings with Paris are noted so the comparative mechanism argument stays visible.

## Mexican literature

1. **Federico Gamboa — *Santa* (1903).** The canonical Porfirian realist novel. A working-class woman from Chimalistac is displaced to Mexico City's brothel economy — the spatial logic of Porfirian "modernization" narrated from below. The closest equivalent to Zola's *L'Assommoir*.
2. **Ángel de Campo ("Micrós") — *La Semana Alegre* / *Ocios y apuntes* (1890s–1900s).** Newspaper chronicles of Porfirian street life. Campo wrote obsessively about the poor barrios that Díaz's grand boulevards were designed to erase. Essential texture for the inequality argument.
3. **Manuel Gutiérrez Nájera — *Cuentos frágiles* (1883).** Modernista prose that celebrates Porfirian elegance and European aesthetics — the ideological counterpart to dispossession. Useful as the voice of the elite that Díaz was building for.
4. **Guillermo Prieto — *Memorias de mis tiempos* (1876).** Pre-Porfiriato memoir of Mexico City's neighborhoods before the transformation — our "before" document, equivalent to the 1865 Paris social class snapshot.

## Datasets

### Historical — The Porfiriato period itself

1. **INEGI Historical Census Data 1895–1910.** The single most important historical dataset for the Porfirian period. The Díaz government conducted modern censuses in 1895, 1900, and 1910 — the first in Mexican history with standardized methodology. Contains population by municipio and occupation data across the Federal District.
   - URL: inegi.org.mx/programas/ccpv/1910/
   - Download format: PDF tables (digitizable) and some Excel via INEGI's microdata portal.
   - Figures you can make: Population change by cuartel / municipio from 1895 to 1910, showing the growth of western elite colonias (Santa María la Ribera, Juárez, Roma) against the stagnation of eastern working-class barrios. The directional equivalent of the Paris center/periphery split.

2. **Porfirian Social Class / Occupational Structure (~1895–1900).** The 1895 census was the first to systematically record occupation. It found that roughly 60–65% of the Federal District's population were *jornaleros* (day laborers) and domestic servants. Extract figures from INEGI's published census summaries to build a class structure chart parallel to the 1865 Paris snapshot.
   - URL: internet.contenidos.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/historicos/2104/702825427952/702825427952.pdf
   - Figures you can make: Pie or bar chart of occupational class structure in the Federal District c. 1900 — direct counterpart to the Paris 1865 class breakdown.

3. **Cuarteles Population Data (Pre- and Post-Porfiriato).** Mexico City was divided into *cuarteles* (municipal quarters) with population records going back to the colonial period. The shift from this system to modern colonias during the Porfiriato is itself evidence of spatial reorganization.
   - Source: *Estadísticas Históricas de México*, INEGI (vol. 1, Chapter 1: Population).
   - URL: inegi.org.mx/app/biblioteca/ficha.html?upc=702825006883
   - Figures you can make: Side-by-side bar chart of cuartel populations 1857 vs. 1910, showing which zones gained (western colonias) and which were displaced (central indigenous barrios).

4. **Typhus and Cholera Mortality Data by Barrio.** Pre-Porfirian epidemic deaths were concentrated in the poor eastern and central barrios — exactly the neighborhoods Díaz's *obras públicas* targeted for demolition. The *Boletín del Consejo Superior de Salubridad* (1880s–1900s) recorded mortality by neighborhood. This is the same sanitation-as-pretext argument as Paris, but applied to a racially stratified city.
   - Source: *Boletín del Consejo Superior de Salubridad*, Archivo Histórico de la Secretaría de Salud.
   - URL: archivos.salud.gob.mx/ahssa/
   - Figures you can make: Map of 1890s typhus mortality by barrio overlaid with Porfirian demolition / renovation zones, showing that "sanitation" infrastructure targeted indigenous and working-class neighborhoods specifically.

5. **Porfirian Public Works Investment Records (*Memorias de Obras Públicas*).** The Secretaría de Fomento published annual *Memorias* documenting all public investment by neighborhood — boulevards, drainage, paving, parks. This is the primary evidence that investment was geographically concentrated in western elite zones.
   - Source: Biblioteca Nacional / Hemeroteca Nacional Digital de México.
   - URL: hndm.unam.mx
   - Figures you can make: Bar chart of public works pesos per neighborhood 1880 to 1910, showing the west/east investment gap in the infrastructure that Díaz called universal progress.

### Present-Day — The Porfiriato legacy today

6. **INEGI AGEB-Level Income and Poverty Data (ENIGH / Censo 2020).** Disposable income, poverty rates, and Gini coefficients at the sub-alcaldía level. Mexico's equivalent of the French IRIS data — our primary modern inequality dataset.
   - URL: inegi.org.mx/programas/ccpv/2020/
   - The geographic unit is the AGEB (Área Geoestadística Básica) — roughly 1,500–2,500 inhabitants, similar to IRIS. The 2020 Census includes income quintiles and deprivation indices at this level.
   - Figures you can make: Income gradient choropleth across Mexico City showing the west/east divide at AGEB resolution — Polanco and Las Lomas vs. Iztapalapa and Tláhuac. This is the Porfiriato geography still legible today.

7. **CONEVAL Urban Poverty Index (ITER 2020).** CONEVAL's municipal and AGEB-level multidimensional poverty index, including income poverty, educational lag, healthcare access, and housing quality.
   - URL: coneval.org.mx/Medicion/IRS/Paginas/Indice-de-Rezago-social-2020.aspx
   - Figures you can make: Choropleth of social deprivation index by alcaldía — showing Iztapalapa, Milpa Alta, and Tláhuac at the bottom vs. Miguel Hidalgo and Benito Juárez at the top.

8. **Datos Abiertos CDMX — Green Spaces / Áreas Verdes.** Every public park, garden, and green space managed by the city, with geometry.
   - Direct download: datos.cdmx.gob.mx/dataset/areas-verdes
   - Figures you can make: Map overlaying green space per capita with income by alcaldía — testing whether the Porfirian parks (Chapultepec, Alameda expansion, Parque México) actually serve low-income residents today. Our empirical third-place test.

9. **Datos Abiertos CDMX — Full Portal.** Beyond green spaces, directly relevant datasets include:
   - Alcaldía and colonia boundaries GeoJSON (base map layer).
   - *Equipamiento urbano* (schools, health centers, cultural facilities) by location.
   - *Vivienda de interés social* — shows where subsidized housing is concentrated today.
   - *Valor catastral* (assessed property values) by colonia.
   - All downloadable at: datos.cdmx.gob.mx

10. **Real Estate Price Data by Colonia (Sociedad Hipotecaria Federal / Propiedades.com).** Property price per m² by colonia going back to 2005 (SHF), with richer neighborhood-level data from private sources.
    - SHF URL: shf.gob.mx/transparencia/Documents/indice_precios_vivienda.pdf
    - Figures you can make: Line chart of real estate price divergence between wealthy western colonias (Polanco, Condesa, Roma Norte) and eastern ones (Iztapalapa, Ecatepec) since 2005, showing the Porfiriato geography hardening over time.

11. **INEGI Encuesta Intercensal 2015 + Census 2020 — Indigenous Population by AGEB.** A crucial dataset with no Paris equivalent. Mexico City's inequality is racially stratified in ways Paris is not. Indigenous population concentration correlates strongly with low income and eastern location. This is our evidence for the racial / colonial layer of spatial inequality that distinguishes Mexico City's geometry from Paris's clean class split.
    - URL: inegi.org.mx/programas/intercensal/2015/
    - Figures you can make: Scatter of indigenous population share vs. income by alcaldía — demonstrates the racial dimension of spatial inequality that Díaz's Europeanizing urbanism encoded and deepened.

### Spatial / GIS — For your maps

12. **Mapoteca Digital Orozco y Berra (SAGARPA / SIAP).** Mexico's equivalent of the David Rumsey collection. Georeferenced historical maps of Mexico City including 1850s (pre-Porfiriato), 1890s–1900s (during the Díaz transformation), and 1920s (immediately after). Overlayable in Python / Folium.
    - URL: mapoteca.siap.gob.mx
    - Search: "Plano General de la Ciudad de México 1900" or "Carta de la Ciudad de México 1891."
    - Figures you can make: Side-by-side or slider map showing pre-Porfirian Mexico City vs. post-1910 street layout, with demolished barrios and new western colonias highlighted.

13. **Casasola Archive Photographs (INAH Fototeca Nacional).** Thousands of photographs of Mexico City streets, markets, and demolition zones from 1895 to 1920 — our visual primary source, equivalent to the Marville photographs for Paris.
    - URL: mediateca.inah.gob.mx
    - Figures you can make: A "then vs. now" panel embedded in the interactive map — click a location to see a Casasola photograph from the Porfiriato alongside a current street view.

14. **OpenStreetMap Mexico City.** Current café, market, and public space density by neighborhood, downloadable via Overpass API or via download.geofabrik.de
    - Figures you can make: Third-place density map (cafés, parks, mercados per capita) cross-referenced with income — empirical test of whether Porfirian public spaces are equitably distributed today, or concentrated in the western alcaldías.

## Key academic articles

### For the historical argument

- **Johns, Michael (1997)** — *The City of Mexico in the Age of Díaz*, University of Texas Press. Our primary book-length historical source. Argues that the Porfiriato remade Mexico City's spatial order explicitly along class and racial lines, concentrating infrastructure investment in the western districts.
- **Tenorio-Trillo, Mauricio (1996)** — *Mexico at the World's Fairs: Crafting a Modern Nation*, University of California Press. Shows how Díaz explicitly modeled Mexican urbanism on Haussmann's Paris — the rhetoric of universal progress deployed to legitimate elite spatial restructuring.
- **Piccato, Pablo (2001)** — *City of Suspects: Crime in Mexico City, 1900–1931*, Duke University Press. Uses neighborhood-level crime and poverty data to reconstruct the Porfirian geography of exclusion. Essential for the sanitation / social-control argument.
- **Rodríguez Kuri, Ariel (1996)** — *La experiencia olvidada: El Ayuntamiento de México: política y gobierno, 1876–1912*, UAM / Colegio de México. Archival study of Porfirian municipal governance and public works allocation. Documents the political economy of who decided which neighborhoods got paved streets, drainage, and parks.

### For the modern inequality argument

- **Aguilar, Adrián Guillermo & Ward, Peter M. (2003)** — "Rethinking the City in Mexico," *Latin American Perspectives*. Spatial analysis of income segregation in Mexico City using census AGEB data — shows how colonial and Porfirian geographies persist in present-day inequality maps.
- **Duhau, Emilio & Giglia, Angela (2008)** — *Las reglas del desorden: habitar la metrópoli*, UAM / Siglo XXI. The canonical study of Mexico City's fragmented spatial order. Argues that the city's inequality is not center/periphery (like Paris) but a mosaic of enclaves shaped by colonial race structure — exactly our comparative mechanism claim.
- **CONEVAL (2021)** — *Pobreza urbana y de las zonas metropolitanas en México*. Official poverty mapping at AGEB level. coneval.org.mx

### Connecting history to present

- **Davis, Diane E. (1994)** — *Urban Leviathan: Mexico City in the Twentieth Century*, Temple University Press. Traces how Porfirian spatial choices locked in political and economic arrangements that shaped the city's 20th-century inequality trajectory. Our connection between the 1900 geography and today's income maps.
- **Leal, Tomás et al. (2019)** — "Segregation and Inequality in Mexico City," *Urban Studies*. Uses AGEB-level census data to track spatial income segregation 1990 to 2015. Finds a persistent and growing west/east divide — our modern data argument.

## Suggested figure pipeline

From simplest to most ambitious:

1. Bar chart: Mexico City occupational class structure c. 1900 (jornaleros / artisans / middle / elite). Simple, striking, sets up the whole argument and pairs directly with the Paris 1865 chart.
2. Choropleth (static): Population change by cuartel / delegación 1895 to 1910. Shows the westward shift of elite colonias and the relative stagnation of eastern barrios.
3. Choropleth (static): Multidimensional poverty index (CONEVAL) or median income by AGEB today. Shows the Porfiriato west/east geography persisting.
4. Scatter plot: Green space per capita vs. median income by alcaldía. Empirical Chapultepec test.
5. Scatter plot: Indigenous population share vs. income by alcaldía. Shows the racial / colonial layer that distinguishes Mexico City's geometry from Paris's class split.
6. Line chart: Real estate price divergence, western (Polanco, Condesa) vs. eastern (Iztapalapa, Ecatepec) alcaldías, 2005 to 2024.
7. Interactive map: Historical Porfirian investment zones + modern income / poverty layers, with a slider. Capstone visualization.
