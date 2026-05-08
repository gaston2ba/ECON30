# One-off helper: rewrite timeline thumbnails to reliable CDN URLs.
import re
from pathlib import Path

path = Path(__file__).resolve().parent / "index.html"
text = path.read_text(encoding="utf-8")

paris = [
    "https://images.unsplash.com/photo-1502602898536-47ad22581b52?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1431274172761-fca4d90d7fd7?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1549144511-f096e968c793?auto=format&fit=crop&w=900&q=80",
]
mexico = [
    "https://images.unsplash.com/photo-1512813195389-67cf89d322aa?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1585464231875-d72289b0c75a?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1518655048521-f130bcd039f9?auto=format&fit=crop&w=900&q=80",
]

matches = list(re.finditer(r"https://upload\.wikimedia\.org[^\"]+", text))
PARIS_EVENTS = 9
if len(matches) != PARIS_EVENTS + len(mexico):  # 9 + 8 = 17
    if len(matches) != PARIS_EVENTS + 8:
        print("warning: expected 17 commons URLs, got", len(matches))


def amp(u):
    return u.replace("&", "&amp;")


repls = []
pi = mi = 0
for idx, _m in enumerate(matches):
    if idx < PARIS_EVENTS:
        u = amp(paris[pi % len(paris)])
        pi += 1
    else:
        u = amp(mexico[mi % len(mexico)])
        mi += 1
    repls.append(u)

parts = []
last = 0
for idx, m in enumerate(matches):
    parts.append(text[last : m.start()])
    parts.append(repls[idx])
    last = m.end()
parts.append(text[last:])
path.write_text("".join(parts), encoding="utf-8")
print("replaced", len(matches), "wikimedia URLs")
