# REBUILD_PROGRESS.md

| Phase | Status | Notes |
|-------|--------|-------|
| 1 | done | `REBUILD_AUDIT.md` |
| 2 | done | `build_mexico_uqi.py`, `build_mexico_hdi.py`; PNUD HDI transcribed to `data/mexico/raw/hdi_mexico_pnud.csv` |
| 3 | done | `build_paris_uqi_capstone.py`; air quality flat at 9 µg/m³ (citywide proxy) |
| 4 | done | `build_paris_hdi_capstone.py`; UN HDR 2022 geometric mean; education proxy when INSEE diplomas missing |
| 5 | done | `index.html`, `css/capstone.css`, `js/capstone.js`, `capstone_bundle.json` |
| 6 | done | Global `hoverState` + `.hovered` on four maps; 200ms mouseleave debounce |
| 7 | done | Layout/centering in CSS; full browser QA recommended before submission |
| 8 | done | Branch `parallel-rebuild`, commit `611266e`, pushed for Vercel preview |

## Fallbacks logged

- CDMX HDI: hand-transcribed PNUD municipal 2020 (not live API).
- Paris infrastructure: Airparif PM₂.₅ uniform across arrondissements.
- Paris education (HDI): income-rank proxy for MYS/EYS when diploma scrape incomplete.
- Timeline images: Unsplash placeholders (`image_credits.md`).

## Correlations (2020 CDMX / 2022 Paris)

- CDMX UQI–HDI: r ≈ 0.661
- Paris UQI–HDI: r ≈ 0.467
