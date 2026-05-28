# ECON 30 Project

## Folder layout

| Path | Purpose |
|------|---------|
| `course-materials/` | Syllabus, handouts, assignment prompts, and other course documents |
| `data/` | All project datasets — see `data/README.md` |
| `data/mexico/` | CDMX workbook, sources zip, historical CSVs, exports |
| `data/paris/` | Arrondissement CSVs, `raw/` caches, historical CSVs |
| `data/analysis/` | Regression results, web embed JSON |
| `scripts/` | Data pipelines (`build_paris_data`, `export_mexico_data`, …) |
| `code/` | Figure scripts and analysis code |
| `figures/` | Charts, plots, interactive prototypes, and the live `index.html` site assets |
| `index.html` | Main capstone webpage (deployed via Vercel) |
| `Knowledge Base/` | Research notes and literature (Obsidian) |

## Current course-materials setup

- `course-materials/preliminary-reading-list.md` tracks the first reading shortlist.
- `course-materials/source-bank.md` tracks what readings, maps, and images to collect.
- `course-materials/readings/` is for PDFs and article files.
- `course-materials/maps/` is for historical maps and plans.
- `course-materials/images/` is for photos, postcards, and visual references.

## Live draft webpage

- Current public draft (Vercel): `https://econ30url.vercel.app/`
- Use this URL as the shareable "latest build" for feedback and class submissions.

## Deploy on Vercel

This is a **static site** (HTML/JS/CSS at the repo root), not a Python app.

| Setting | Value |
|---------|--------|
| Root Directory | `.` (repo root) |
| Framework Preset | **Other** |
| Build Command | `npm run build` |
| Output Directory | `.` |
| Install Command | `npm install` |

Python data scripts live in `scripts/` — install locally with `pip install -r scripts/requirements.txt`.

Update this readme as the project grows.
