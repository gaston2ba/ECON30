from pathlib import Path

s = Path("cdmx/script.js").read_text(encoding="utf-8")
repls = [
    ('cityTag: "CDMX"', 'cityTag: "Paris"'),
    ('entitiesKey: "alcaldias"', 'entitiesKey: "arrondissements"'),
    ('entityLabel: "alcaldía"', 'entityLabel: "arrondissement"'),
    ("entityCount: 16", "entityCount: 20"),
    ("../data/cdmx/", "../data/paris/"),
    ("uqi-by-alcaldia", "uqi-by-arrondissement"),
    ("alcaldias.geojson", "arrondissements.geojson"),
    ("hdi-by-alcaldia", "hdi-by-arrondissement"),
    ('hdiEarliest: "2000"', 'hdiEarliest: "2010"'),
    ('pathClass: "alcaldia-path"', 'pathClass: "arrondissement-path"'),
    ("CDMX UQI", "Paris UQI"),
    ("feature.properties?.alcaldia", "feature.properties?.name"),
    (
        'const aliases = new Map([\n  ["magdalena_contreras", "la_magdalena_contreras"],\n  ["cuajimalpa", "cuajimalpa_de_morelos"]\n]);',
        "const aliases = new Map();",
    ),
    (
        '.replace("La Magdalena Contreras", "Magdalena C.").replace("Gustavo A. Madero", "G.A. Madero").replace("Venustiano Carranza", "V. Carranza").replace("Cuajimalpa de Morelos", "Cuajimalpa")',
        "",
    ),
    ("Mexico City UQI by alcaldía", "Paris UQI by arrondissement"),
    ("for each alcaldía", "for each arrondissement"),
    ("from 1860 to 2020", "from 1870 to 2020"),
]
for a, b in repls:
    s = s.replace(a, b)
Path("paris/script.js").write_text(s, encoding="utf-8")
print("wrote paris/script.js")
