# Paris HDI methodology

UN Human Development Report 2022 goalposts (Technical Notes).

**Life expectancy:** ORS-IDF / Institut Paris Région (2021), arrondissement table anchors; see `life_expectancy_arrondissement.csv`.

**Education:** MYS from INSEE diploma distribution where available in dossier JSON; else income-rank proxy. EYS proxy = 12 + 6 × share with ≥ bac. Indices: EYS/18, MYS/15, education = mean.

**Income:** Filosofi 2021 median disposable income → USD-PPP via factor 0.738 EUR/USD-PPP (OECD).

**HDI** = (life × education × income)^(1/3). **Geometric mean**, not arithmetic.

Interpretation: within-city relative HDI using HDR logic; not directly comparable to national UN HDI levels.
