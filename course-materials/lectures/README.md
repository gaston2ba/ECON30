# `course-materials/lectures/`

Cleaned markdown versions of each ECON 30 lecture slide deck, with the original HTML kept alongside for provenance.

## Naming convention

- `lecture-NN-short-title.md` — the human-readable markdown version. This is the file to read and to cite in notes and memos.
- `lecture-NN-short-title.source.html` — the raw upstream HTML (or raw extraction) of the same lecture. Kept so that anything lost in the cleanup pass can be recovered, and so that the exact source-URL provenance is auditable.

Example for this folder:

- `lecture-01-progress-and-inequality.md`
- `lecture-01-progress-and-inequality.source.html`

## What the cleanup pass does

For each lecture we strip the slide-runtime scaffolding (inline CSS, iframes pointing at interactive widgets on the course website, `<script>` tags for classroom timers, `remark.js` slide-class directives like `class: agenda`) and keep the prose, quotes, bullet lists, and the figure-reference list. The goal is a file that:

1. Reads cleanly in Obsidian / Cursor / any markdown viewer.
2. Preserves every factual claim and every direct quote exactly as stated in the slides.
3. Lists the figures the slides reference (with their relative paths on `lukasalthoff.com`) so they can be fetched into `../images/` later if they become relevant.

## When to add images

If a figure referenced in the lecture becomes directly useful to the capstone project, fetch it from the course site and save it under `course-materials/images/` following the naming pattern in `../source-bank.md` (e.g. `paris_reversal_ajr_2002.png`). Add a one-line reference in the lecture markdown pointing at the saved local copy.

## Upstream source

Slides are published by the instructor at `https://lukasalthoff.com/slides/teaching/undergraduate/slides/` and are referenced with the canonical URL in the YAML frontmatter of each lecture file.
