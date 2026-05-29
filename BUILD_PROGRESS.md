# Build progress — Paris twin & comparison site

| Phase | Status | Notes |
|-------|--------|-------|
| 0 | done | `data/cdmx/`; `cdmx/script.js` → `../data/cdmx/` |
| 1 | done | `data/paris/arrondissements.geojson` normalized (20 features) |
| 2 | done | `scripts/build_paris_uqi.py` → `data/paris/uqi-by-arrondissement.json` |
| 3 | done | `cdmx/`, `paris/` link `../styles.css`; shared `js/uqi-core.js` |
| 4 | partial | HDI built; Paris LE from ORS anchors + income gradient; CDMX from PNUD-style municipal table |
| 5 | done | Root `index.html` comparison page |
| 6 | done | `vercel.json` static routes |
| 7 | pending | Manual browser QA |
