#!/usr/bin/env python3
"""Fetch Paris arrondissement panel data and write CSVs mirroring DataMexCity.xlsx."""

from __future__ import annotations

import io
import json
import re
import zipfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from bs4 import BeautifulSoup
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "paris"
RAW = OUT / "raw"

USER_AGENT = "ECON30ParisDataBot/1.0 (Stanford ECON30 research project)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

ARRONDISSEMENTS = [
    (1, "75101", "1er — Louvre"),
    (2, "75102", "2e — Bourse"),
    (3, "75103", "3e — Temple"),
    (4, "75104", "4e — Hôtel-de-Ville"),
    (5, "75105", "5e — Panthéon"),
    (6, "75106", "6e — Luxembourg"),
    (7, "75107", "7e — Palais-Bourbon"),
    (8, "75108", "8e — Élysée"),
    (9, "75109", "9e — Opéra"),
    (10, "75110", "10e — Entrepôt"),
    (11, "75111", "11e — Popincourt"),
    (12, "75112", "12e — Reuilly"),
    (13, "75113", "13e — Gobelins"),
    (14, "75114", "14e — Observatoire"),
    (15, "75115", "15e — Vaugirard"),
    (16, "75116", "16e — Passy"),
    (17, "75117", "17e — Batignolles"),
    (18, "75118", "18e — Buttes-Montmartre"),
    (19, "75119", "19e — Buttes-Chaumont"),
    (20, "75120", "20e — Ménilmontant"),
]

POP_YEARS = [1968, 1975, 1982, 1990, 1999, 2006, 2011, 2016, 2022]
DECADES = list(range(1860, 2030, 10))

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
PARIS_API = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets"
INSEE_DOSSIER = "https://www.insee.fr/fr/statistiques/2011101?geo=COM-{code}"
FILO_ZIP = (
    "https://www.insee.fr/fr/statistiques/fichier/7756855/"
    "indic-struct-distrib-revenu-2021-COMMUNES_csv.zip"
)


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)


def parse_french_number(value) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text in {"-", "s", "nd", "N/A"}:
        return None
    text = text.replace("\xa0", "").replace(" ", "").replace(",", ".")
    text = re.sub(r"[^\d.\-]", "", text)
    if not text:
        return None
    return float(text)


def arr_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "arrondissement_num": [a[0] for a in ARRONDISSEMENTS],
            "insee_code": [a[1] for a in ARRONDISSEMENTS],
            "arrondissement": [a[2] for a in ARRONDISSEMENTS],
        }
    )


def fetch_arrondissement_boundaries() -> gpd.GeoDataFrame:
    cache = RAW / "arrondissements.geojson"
    if not cache.exists():
        url = f"{PARIS_API}/arrondissements/exports/geojson"
        resp = SESSION.get(url, timeout=120)
        resp.raise_for_status()
        cache.write_bytes(resp.content)

    gdf = gpd.read_file(cache)
    gdf = gdf.rename(columns={"c_arinsee": "insee_code", "c_ar": "arrondissement_num"})
    gdf["insee_code"] = gdf["insee_code"].astype(str)
    gdf["arrondissement_num"] = gdf["arrondissement_num"].astype(int)
    names = arr_frame()[["arrondissement_num", "arrondissement"]]
    gdf = gdf.merge(names, on="arrondissement_num", how="left")
    return gdf.to_crs(4326)


def _parse_insee_table(soup: BeautifulSoup, caption_pattern: str) -> pd.DataFrame | None:
    for caption in soup.find_all(string=re.compile(caption_pattern)):
        table = caption.find_parent("table")
        if table is None:
            continue
        df = pd.read_html(io.StringIO(str(table)))[0]
        return df
    return None


def fetch_population_for_code(insee_code: str) -> list[dict]:
    cache_file = RAW / f"insee_{insee_code}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    url = INSEE_DOSSIER.format(code=insee_code)
    last_error = None
    for attempt in range(4):
        try:
            resp = SESSION.get(url, timeout=90)
            resp.raise_for_status()
            break
        except requests.RequestException as exc:
            last_error = exc
            print(f"INSEE retry {attempt + 1}/4 for {insee_code}: {exc}")
            time.sleep(2 * (attempt + 1))
    else:
        raise RuntimeError(f"INSEE fetch failed for {insee_code}") from last_error

    soup = BeautifulSoup(resp.text, "html.parser")

    pop_table = _parse_insee_table(soup, r"POP T1")
    fam_table = _parse_insee_table(soup, r"FAM G1")

    if pop_table is None:
        raise ValueError(f"POP T1 table not found for {insee_code}")

    pop_table.columns = [str(c).strip() for c in pop_table.columns]
    year_cols = [c for c in pop_table.columns if re.search(r"\d{4}", str(c))]
    year_map = {}
    for col in year_cols:
        m = re.search(r"(\d{4})", str(col))
        if m:
            year_map[int(m.group(1))] = col

    pop_row = pop_table.iloc[0]
    dens_row = pop_table.iloc[1]

    ppd_by_year: dict[int, float | None] = {}
    if fam_table is not None:
        fam_table.columns = [str(c).strip() for c in fam_table.columns]
        fam_year_cols = [c for c in fam_table.columns if re.search(r"\d{4}", str(c))]
        fam_map = {}
        for col in fam_year_cols:
            m = re.search(r"(\d{4})", str(col))
            if m:
                fam_map[int(m.group(1))] = col
        fam_row = fam_table.iloc[0]
        for year, col in fam_map.items():
            raw = parse_french_number(fam_row[col])
            ppd_by_year[year] = raw / 100 if raw is not None else None

    rows = []
    arr_num = int(insee_code[-2:])
    arr_name = next(a[2] for a in ARRONDISSEMENTS if a[1] == insee_code)
    for year in POP_YEARS:
        if year not in year_map:
            continue
        population = parse_french_number(pop_row[year_map[year]])
        density = parse_french_number(dens_row[year_map[year]])
        rows.append(
            {
                "arrondissement_num": arr_num,
                "insee_code": insee_code,
                "arrondissement": arr_name,
                "year": year,
                "population": population,
                "density": density,
                "persons_per_dwelling": ppd_by_year.get(year),
            }
        )
    cache_file.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def fetch_population() -> pd.DataFrame:
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(fetch_population_for_code, code): code
            for _, code, _ in ARRONDISSEMENTS
        }
        for fut in as_completed(futures):
            rows.extend(fut.result())
    df = pd.DataFrame(rows).sort_values(["arrondissement_num", "year"])
    df.to_csv(OUT / "paris_population.csv", index=False)
    return df


def run_sparql(query: str) -> list[dict]:
    resp = SESSION.post(
        WIKIDATA_SPARQL,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["results"]["bindings"]


def fetch_metro_stations_wikidata() -> pd.DataFrame:
    """Try Wikidata; returns empty DataFrame if no matches."""
    query = """
    SELECT ?station ?stationLabel ?inception ?lat ?lon WHERE {
      ?line wdt:P31/wdt:P279* wd:Q50708 ; wdt:P131 wd:Q90 .
      ?station wdt:P81 ?line ; wdt:P625 ?coord .
      BIND(geof:latitude(?coord) AS ?lat)
      BIND(geof:longitude(?coord) AS ?lon)
      OPTIONAL { ?station wdt:P571 ?inception . }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
    }
    """
    bindings = run_sparql(query)
    rows = []
    for b in bindings:
        inception = b.get("inception", {}).get("value")
        year = int(inception[:4]) if inception else None
        rows.append(
            {
                "name": b["stationLabel"]["value"],
                "year_opened": year,
                "lat": float(b["lat"]["value"]),
                "lon": float(b["lon"]["value"]),
                "source": "wikidata",
            }
        )
    return pd.DataFrame(rows)


def _parse_overpass_elements(payload: list[dict]) -> pd.DataFrame:
    rows = []
    for el in payload:
        tags = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue
        start = tags.get("start_date") or tags.get("opening_date")
        year = int(re.findall(r"\d{4}", str(start))[0]) if start and re.findall(r"\d{4}", str(start)) else None
        rows.append(
            {
                "name": tags.get("name"),
                "year_opened": year,
                "lat": float(lat),
                "lon": float(lon),
                "source": "overpass",
            }
        )
    return pd.DataFrame(rows)


def fetch_metro_stations_overpass() -> pd.DataFrame:
    cache = RAW / "metro_stations_overpass.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
        return _parse_overpass_elements(payload)

    query = """
    [out:json][timeout:90];
    area["wikidata"="Q90"]->.paris;
    node["railway"="station"]["station"="subway"](area.paris);
    out center;
    """
    last_error = None
    payload = []
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = SESSION.post(endpoint, data=query, timeout=180)
            resp.raise_for_status()
            payload = resp.json().get("elements", [])
            cache.write_text(json.dumps(payload), encoding="utf-8")
            break
        except requests.RequestException as exc:
            last_error = exc
            print(f"Overpass failed on {endpoint}: {exc}")
    else:
        raise RuntimeError("All Overpass endpoints failed") from last_error

    return _parse_overpass_elements(payload)


def assign_points_to_arrondissement(points: pd.DataFrame, boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
    if points.empty:
        return points.assign(arrondissement_num=pd.NA, insee_code=pd.NA, arrondissement=pd.NA)

    gdf = gpd.GeoDataFrame(
        points,
        geometry=[Point(lon, lat) for lon, lat in zip(points["lon"], points["lat"])],
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(gdf, boundaries[["arrondissement_num", "insee_code", "arrondissement", "geometry"]], how="left", predicate="within")
    return pd.DataFrame(joined.drop(columns="geometry", errors="ignore"))


def fetch_transit(boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
    stations = fetch_metro_stations_wikidata()
    if stations.empty:
        print("Wikidata returned no metro stations; falling back to OpenStreetMap Overpass.")
        stations = fetch_metro_stations_overpass()

    stations = stations.dropna(subset=["lat", "lon"]).drop_duplicates(subset=["name", "lat", "lon"])
    assigned = assign_points_to_arrondissement(stations, boundaries)
    assigned = assigned[assigned["insee_code"].notna()].copy()
    assigned["year_opened"] = assigned["year_opened"].fillna(1900).astype(int)

    rows = []
    base = arr_frame()
    for _, ar in base.iterrows():
        in_arr = assigned[assigned["insee_code"] == ar["insee_code"]]
        for decade in DECADES:
            cumulative = in_arr[in_arr["year_opened"] <= decade]["name"].nunique()
            rows.append(
                {
                    "arrondissement_num": ar["arrondissement_num"],
                    "insee_code": ar["insee_code"],
                    "arrondissement": ar["arrondissement"],
                    "decade": decade,
                    "stations_cumulative": cumulative,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "paris_transit.csv", index=False)
    assigned.to_csv(RAW / "metro_stations_assigned.csv", index=False)
    return df


def fetch_green_space(population: pd.DataFrame) -> pd.DataFrame:
    url = f"{PARIS_API}/espaces_verts/exports/csv"
    resp = SESSION.get(url, params={"delimiter": ";"}, timeout=180)
    resp.raise_for_status()
    raw_path = RAW / "espaces_verts.csv"
    raw_path.write_bytes(resp.content)

    greens = pd.read_csv(raw_path, sep=";", low_memory=False)
    greens["surface_m2"] = pd.to_numeric(greens.get("surface_totale_reelle"), errors="coerce")
    postal = pd.to_numeric(greens.get("adresse_codepostal"), errors="coerce")
    greens["arrondissement_num"] = (postal % 100).astype("Int64")
    greens = greens.dropna(subset=["arrondissement_num", "surface_m2"])
    greens = greens[(greens["arrondissement_num"] >= 1) & (greens["arrondissement_num"] <= 20)]
    greens["arrondissement_num"] = greens["arrondissement_num"].astype(int)

    totals = greens.groupby("arrondissement_num", as_index=False)["surface_m2"].sum()
    totals = totals.rename(columns={"surface_m2": "total_m2"})

    pop_2022 = population[population["year"] == 2022][["arrondissement_num", "population"]]
    df = arr_frame().merge(totals, on="arrondissement_num", how="left").merge(pop_2022, on="arrondissement_num", how="left")
    df["total_m2"] = df["total_m2"].fillna(0)
    df["m2_per_capita"] = df["total_m2"] / df["population"]
    df = df[["arrondissement_num", "insee_code", "arrondissement", "total_m2", "m2_per_capita"]]
    df.to_csv(OUT / "paris_green_space.csv", index=False)
    return df


def fetch_libraries(boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
    """Paris Data public computer posts, grouped by library site."""
    rows = []
    offset = 0
    while True:
        resp = SESSION.get(
            f"{PARIS_API}/postes-publics-des-bibliotheques/records",
            params={"limit": 100, "offset": offset},
            timeout=60,
        )
        resp.raise_for_status()
        batch = resp.json().get("results", [])
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        if len(batch) < 100:
            break

    libs = []
    for row in rows:
        pos = row.get("position") or {}
        if not pos.get("lat") or not pos.get("lon"):
            continue
        libs.append(
            {
                "library_site": row.get("localisation"),
                "lat": pos["lat"],
                "lon": pos["lon"],
            }
        )
    lib_df = pd.DataFrame(libs).drop_duplicates(subset=["library_site", "lat", "lon"])
    assigned = assign_points_to_arrondissement(lib_df, boundaries)
    counts = (
        assigned.dropna(subset=["insee_code"])
        .groupby(["arrondissement_num", "insee_code", "arrondissement"], as_index=False)
        .agg(libraries=("library_site", "nunique"))
    )
    return counts


def fetch_museums_wikipedia() -> pd.DataFrame:
    url = "https://en.wikipedia.org/wiki/List_of_museums_in_Paris"
    resp = SESSION.get(url, timeout=60)
    resp.raise_for_status()
    tables = pd.read_html(io.StringIO(resp.text))
    museums = tables[1].copy()
    museums = museums.rename(columns=str)
    museums = museums[museums["Arrondissement"].notna()].copy()

    def parse_arr(text: str) -> int | None:
        m = re.search(r"(\d{1,2})", str(text))
        return int(m.group(1)) if m else None

    museums["arrondissement_num"] = museums["Arrondissement"].map(parse_arr)
    counts = museums.groupby("arrondissement_num", as_index=False).agg(museums=("Name", "nunique"))
    return counts


def fetch_third_spaces(boundaries: gpd.GeoDataFrame, population: pd.DataFrame) -> pd.DataFrame:
    lib_counts = fetch_libraries(boundaries)
    mus_counts = fetch_museums_wikipedia()
    pop_2022 = population[population["year"] == 2022][["arrondissement_num", "population"]]

    df = arr_frame().merge(lib_counts.drop(columns=["insee_code", "arrondissement"], errors="ignore"), on="arrondissement_num", how="left")
    df = df.merge(mus_counts, on="arrondissement_num", how="left")
    df = df.merge(pop_2022, on="arrondissement_num", how="left")
    df["libraries"] = df["libraries"].fillna(0).astype(int)
    df["museums"] = df["museums"].fillna(0).astype(int)
    df["total_per_100k"] = (df["libraries"] + df["museums"]) / df["population"] * 100_000
    df = df[["arrondissement_num", "insee_code", "arrondissement", "libraries", "museums", "total_per_100k"]]
    df.to_csv(OUT / "paris_third_spaces.csv", index=False)
    return df


def fetch_air_quality() -> pd.DataFrame:
    """Airparif via Paris Open Data (intramuros urban background PM2.5)."""
    resp = SESSION.get(
        f"{PARIS_API}/qualite-de-lair-concentration-moyenne-no2-pm25-pm10-o3-a-partir-de-2015/records",
        params={"limit": 1, "order_by": "annee desc"},
        timeout=60,
    )
    resp.raise_for_status()
    latest = resp.json()["results"][0]
    year = int(latest["annee"])
    pm25 = float(latest["pm2_5_fond_urbain_moyenne_annuelle_airparif"])

    df = arr_frame().copy()
    df["year"] = year
    df["pm25_annual_mean"] = pm25
    df["source"] = "airparif_via_opendata_paris_fond_urbain_intramuros"
    df = df[["arrondissement_num", "insee_code", "arrondissement", "year", "pm25_annual_mean", "source"]]
    df.to_csv(OUT / "paris_air_quality.csv", index=False)
    return df


def fetch_income() -> pd.DataFrame:
    resp = SESSION.get(FILO_ZIP, timeout=180)
    resp.raise_for_status()
    zip_path = RAW / "filo2021_communes.zip"
    zip_path.write_bytes(resp.content)

    with zipfile.ZipFile(zip_path) as zf:
        csv_name = "FILO2021_DISP_COM.csv"
        filo = pd.read_csv(zf.open(csv_name), sep=";", encoding="latin-1", low_memory=False)

    filo["CODGEO"] = filo["CODGEO"].astype(str)
    paris = filo[filo["CODGEO"].str.match(r"^751\d{2}$")].copy()
    paris["median_income"] = paris["Q221"].map(parse_french_number)

    df = arr_frame().merge(
        paris[["CODGEO", "median_income"]].rename(columns={"CODGEO": "insee_code"}),
        on="insee_code",
        how="left",
    )
    df["filosofi_year"] = 2021
    df = df[["arrondissement_num", "insee_code", "arrondissement", "median_income", "filosofi_year"]]
    df.to_csv(OUT / "paris_income.csv", index=False)
    return df


def minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or lo == hi:
        out = pd.Series(50.0, index=series.index)
    else:
        out = (s - lo) / (hi - lo) * 100
    if invert:
        out = 100 - out
    return out.round(1)


def build_panel(
    population: pd.DataFrame,
    transit: pd.DataFrame,
    green: pd.DataFrame,
    third: pd.DataFrame,
    air: pd.DataFrame,
    income: pd.DataFrame,
) -> pd.DataFrame:
    pop_hist = population.copy()
    pop_hist.to_csv(OUT / "paris_population.csv", index=False)

    cross = arr_frame().copy()
    cross = cross.merge(green, on=["arrondissement_num", "insee_code", "arrondissement"], how="left")
    cross = cross.merge(third, on=["arrondissement_num", "insee_code", "arrondissement"], how="left")
    cross = cross.merge(air.drop(columns=["arrondissement"], errors="ignore"), on=["arrondissement_num", "insee_code"], how="left")
    cross = cross.merge(income.drop(columns=["arrondissement"], errors="ignore"), on=["arrondissement_num", "insee_code"], how="left")
    cross = cross.drop_duplicates(subset=["arrondissement_num", "insee_code", "arrondissement"], keep="first")

    pop_2022 = population[population["year"] == 2022][["arrondissement_num", "population", "density", "persons_per_dwelling"]]
    cross = cross.merge(pop_2022, on="arrondissement_num", how="left", suffixes=("", "_2022"))

    transit_2020 = transit[transit["decade"] == 2020][["arrondissement_num", "stations_cumulative"]]
    cross = cross.merge(transit_2020, on="arrondissement_num", how="left")
    cross["transit_access_per_100k"] = cross["stations_cumulative"] / cross["population"] * 100_000

    cross["parks_score"] = minmax(cross["m2_per_capita"])
    cross["transit_score"] = minmax(cross["transit_access_per_100k"])
    cross["density_score"] = minmax(cross["density"])
    cross["thirdspace_score"] = minmax(cross["total_per_100k"])
    cross["air_score"] = minmax(cross["pm25_annual_mean"], invert=True)
    cross["income_score"] = minmax(cross["median_income"])

    score_cols = ["parks_score", "transit_score", "density_score", "thirdspace_score", "air_score"]
    cross["planning_index_2022"] = cross[score_cols].mean(axis=1).round(1)

    panel_rows = []
    for _, row in cross.iterrows():
        panel_rows.append(
            {
                "arrondissement_num": row["arrondissement_num"],
                "insee_code": row["insee_code"],
                "arrondissement": row["arrondissement"],
                "year": 2022,
                "population": row["population"],
                "density": row["density"],
                "persons_per_dwelling": row["persons_per_dwelling"],
                "green_space_m2": row["total_m2"],
                "green_space_m2_per_capita": row["m2_per_capita"],
                "transit_stations_cumulative": row["stations_cumulative"],
                "transit_access_per_100k": row["transit_access_per_100k"],
                "libraries": row["libraries"],
                "museums": row["museums"],
                "third_spaces_per_100k": row["total_per_100k"],
                "pm25_annual_mean": row["pm25_annual_mean"],
                "median_income_eur": row["median_income"],
                "planning_index": row["planning_index_2022"],
            }
        )

    for _, row in pop_hist[pop_hist["year"] != 2022].iterrows():
        panel_rows.append(
            {
                "arrondissement_num": row["arrondissement_num"],
                "insee_code": row["insee_code"],
                "arrondissement": row["arrondissement"],
                "year": row["year"],
                "population": row["population"],
                "density": row["density"],
                "persons_per_dwelling": row["persons_per_dwelling"],
                "green_space_m2": None,
                "green_space_m2_per_capita": None,
                "transit_stations_cumulative": None,
                "transit_access_per_100k": None,
                "libraries": None,
                "museums": None,
                "third_spaces_per_100k": None,
                "pm25_annual_mean": None,
                "median_income_eur": None,
                "planning_index": None,
            }
        )

    panel = pd.DataFrame(panel_rows).sort_values(["arrondissement_num", "year"])
    panel.to_csv(OUT / "paris_uqi_panel.csv", index=False)

    meta = {
        "sources": {
            "population": "INSEE dossier complet COM-751XX (POP T1, FAM G1)",
            "transit": "Wikidata SPARQL with OpenStreetMap Overpass fallback",
            "green_space": "opendata.paris.fr/espaces_verts",
            "libraries": "opendata.paris.fr/postes-publics-des-bibliotheques",
            "museums": "Wikipedia List of museums in Paris",
            "air_quality": "Airparif via opendata.paris.fr (intramuros urban background PM2.5)",
            "income": "INSEE Filosofi 2021 FILO2021_DISP_COM (Q221 median)",
        }
    }
    (OUT / "paris_data_sources.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return panel


def main() -> None:
    ensure_dirs()
    print("Loading arrondissement boundaries...")
    boundaries = fetch_arrondissement_boundaries()

    with ThreadPoolExecutor(max_workers=6) as pool:
        pop_future = pool.submit(fetch_population)
        income_future = pool.submit(fetch_income)
        air_future = pool.submit(fetch_air_quality)
        transit_future = pool.submit(fetch_transit, boundaries)

        population = pop_future.result()
        income = income_future.result()
        air = air_future.result()
        transit = transit_future.result()

        green_future = pool.submit(fetch_green_space, population)
        third_future = pool.submit(fetch_third_spaces, boundaries, population)
        green = green_future.result()
        third = third_future.result()

    results = {
        "population": population,
        "transit": transit,
        "green": green,
        "third": third,
        "air": air,
        "income": income,
    }

    print("Building panel...")
    panel = build_panel(
        results["population"],
        results["transit"],
        results["green"],
        results["third"],
        results["air"],
        results["income"],
    )
    print(f"Wrote {len(panel)} rows to {OUT / 'paris_uqi_panel.csv'}")
    print("Done.")


if __name__ == "__main__":
    main()
