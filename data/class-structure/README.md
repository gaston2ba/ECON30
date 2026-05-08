# `data/class-structure/` — provenance and caveats

These CSVs are **derived data**, not primary sources. They are transcribed from the catalog summaries in `Knowledge Base/raw/Paris/catalog.md` and `Knowledge Base/raw/MexicoCity/catalog.md`. They are *not* in `Knowledge Base/raw/` because the cursorrules reserve `raw/` for original source documents.

## Files

### `paris-1865.csv`

- **Provenance.** Catalog entry: Paris dataset 2 — "Paris 1865 Social Class Census (via Wikipedia / Second Empire)." The catalog cites a census conducted by the City of Paris in 1865.
- **What's in it.** Four named class buckets (Indigent / Lower-middle / Upper-middle / Wealthy), their shares (42 / 17 / 32 / 3), defining criteria (untaxed status or annual rent bracket), and the two population point estimates the catalog gives (~780,000 indigent, ~50,000 wealthy).
- **Caveat 1.** The four shares sum to 94%, not 100%. The CSV records the 6% residual explicitly as an `Unattributed` row. Likely explanations (transients, institutionalized populations, household members not classified under the rent-bracket scheme) need to be checked against the underlying primary source before publication.
- **Caveat 2.** The ~780,000 / 42% and ~50,000 / 3% implied populations are not perfectly consistent (~1.86M vs. ~1.67M). Both numbers are reproduced as given in the catalog, but a publication-quality figure should reconcile them against the 1866 INSEE census.
- **Caveat 3.** "Indigent" is an administrative category (untaxed), not a modern poverty line. Direct comparison to current INSEE poverty rates is suggestive, not exact.

### `mexico-city-c1895.csv`

- **Provenance.** Catalog entry: Mexico City dataset 2 — "Porfirian Social Class / Occupational Structure (~1895–1900)," based on the INEGI 1895 census, the first methodologically modern Mexican census.
- **What's in it.** One filled bucket (Jornaleros + domestic servants, 60–65%) and three placeholder rows (Artisans / Middle-clerical / Elite) for categories the project still needs to extract from the INEGI 1895 PDF tables.
- **Caveat 1.** Only one number is currently available. The CSV is intentionally sparse so that downstream code (`code/figure_01_class_structure.py`) can render the data gap explicitly rather than concealing it.
- **Caveat 2.** The catalog gives a *range* (60–65%), not a point estimate, because the underlying classification of "domestic servants" varies in the published summaries. Both endpoints are stored.
- **Caveat 3.** "Federal District" boundaries in 1895 differ from the modern 16-alcaldía CDMX. Population shares from 1895 are not directly comparable across the 1928 and 2016 boundary changes.
- **Action.** Filling the empty rows is **Priority 1.2** in `Knowledge Base/outputs/data-acquisition-checklist.md`. Source PDF: `https://internet.contenidos.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/historicos/2104/702825427952/702825427952.pdf`.

## Conventions

- All percentages are **shares of total enumerated population**, not of households or of taxpayers.
- `share_pct_low` / `share_pct_high` are used when the source gives a range; `share_pct` (no suffix) is used when the source gives a point estimate.
- Empty cells are real data gaps, not zeros. Downstream code must treat empty differently from zero.

## Used by

- `code/figure_01_class_structure.py` → `figures/figure-01-paris-1865-mexico-city-1895-class-structure.png`
- Wiki articles: `Knowledge Base/wiki/concepts/paris-class-structure-1865.md`, `Knowledge Base/wiki/concepts/mexico-city-class-structure-1900.md`, `Knowledge Base/wiki/outputs/figure-01-class-structure.md`.
