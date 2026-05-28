#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data" / "analysis" / "web_embeds.json").read_text(encoding="utf-8"))


def fmt_series(name: str, rows: list) -> str:
    items = ", ".join(f"{{ year: {r['year']}, value: {r['value']} }}" for r in rows)
    return f"  {name}: [{items}]"


story = "const STORY_SERIES = {\n" + fmt_series("paris", d["paris_story"]) + ",\n" + fmt_series("mexico", d["mexico_story"]) + "\n};"
sparks = "const COMPONENT_SPARKS = " + json.dumps(d["sparks"], ensure_ascii=False) + ";"

html = (ROOT / "index.html").read_text(encoding="utf-8")
html = re.sub(r"const STORY_SERIES = \{.*?\};", story, html, count=1, flags=re.S)
if "COMPONENT_SPARKS" not in html:
    html = html.replace("const STORY_EVENTS =", sparks + "\n\nconst STORY_EVENTS =")
else:
    html = re.sub(r"const COMPONENT_SPARKS = \{.*?\};", sparks, html, count=1, flags=re.S)

(ROOT / "index.html").write_text(html, encoding="utf-8")
print("OK")
