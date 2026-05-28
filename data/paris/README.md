# Paris data

| Path | Description |
|------|-------------|
| `paris_*.csv` | Processed 2022 cross-section + population history (INSEE, Open Data, Filosofi) |
| `paris_uqi_panel.csv` | Long panel (1968–2022) |
| `paris_data_sources.json` | Source metadata |
| `historical/paris-1865.csv` | 1865 class-structure baseline for Figure 1 |
| `raw/` | Cached downloads (INSEE JSON, OSM metro, green space, Filosofi zip) |

Rebuild: `python scripts/build_paris_data.py`
