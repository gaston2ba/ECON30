#!/usr/bin/env python3
"""Copy Andres's CDMX map assets from origin/main into cdmx/."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CDMX = ROOT / "cdmx"
DATA = CDMX / "data"

FILES = [
    ("index.html", "index.html"),
    ("script.js", "script.js"),
    ("styles.css", "styles.css"),
    ("uqi-by-alcaldia.json", "data/uqi-by-alcaldia.json"),
]


def git_bytes(rev_path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"origin/main:{rev_path}"])


def main() -> None:
    subprocess.run(["git", "fetch", "origin"], check=False, cwd=ROOT)
    DATA.mkdir(parents=True, exist_ok=True)
    for src, dst in FILES:
        (CDMX / dst).write_bytes(git_bytes(src))
    size = int(subprocess.check_output(["git", "cat-file", "-s", "origin/main:alcaldias.geojson"]).strip())
    if size > 1000:
        (DATA / "alcaldias.geojson").write_bytes(git_bytes("alcaldias.geojson"))
    else:
        fallback = ROOT / "data" / "maps" / "mexico_alcaldias.geojson"
        if not fallback.exists():
            raise SystemExit(f"Missing {fallback}")
        (DATA / "alcaldias.geojson").write_bytes(fallback.read_bytes())
    print("Synced cdmx/ from origin/main")


if __name__ == "__main__":
    main()
