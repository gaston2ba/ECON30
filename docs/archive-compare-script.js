/* Parallel comparison — shared toolbar drives Paris and CDMX */
const palette = ["#d95f59", "#e79262", "#f1d36b", "#9cc77b", "#5aac72"];
const hdiPalette = ["#e8eaf6", "#c5cae9", "#9fa8da", "#5c6bc0", "#3949ab"];
const lineColors = ["#314f9f", "#b85c45", "#5e8c61", "#8763a8", "#c79335", "#4b8a99", "#a34f78", "#6f7d44", "#485b75", "#d07a42", "#6c5aa8", "#40876f", "#b34c4c", "#4774b5", "#8a6f38", "#5e7180"];

const cities = {
  paris: {
    label: "Paris",
    entitiesKey: "arrondissements",
    uqiUrl: "data/paris/uqi-by-arrondissement.json",
    hdiUrl: "data/paris/hdi-by-arrondissement.json",
    geoUrl: "data/paris/arrondissements.geojson",
    nameProp: "name",
    hdiEarliest: "2010",
    aliases: new Map()
  },
  cdmx: {
    label: "CDMX",
    entitiesKey: "alcaldias",
    uqiUrl: "data/cdmx/uqi-by-alcaldia.json",
    hdiUrl: "data/cdmx/hdi-by-alcaldia.json",
    geoUrl: "data/cdmx/alcaldias.geojson",
    nameProp: "alcaldia",
    hdiEarliest: "2000",
    aliases: new Map([["magdalena_contreras", "la_magdalena_contreras"], ["cuajimalpa", "cuajimalpa_de_morelos"]])
  }
};

const state = { decade: "2020", decades: [], selected: new Set(), paris: {}, cdmx: {}, playing: false, timer: null };

function slug(v) {
  return String(v || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}
function matchSlug(city, name) {
  const s = slug(name);
  return cities[city].aliases.get(s) || s;
}
function ents(city) {
  return state[city].uqi[cities[city].entitiesKey];
}
function fname(city, f) {
  const p = cities[city].nameProp;
  return f.properties?.[p] || f.properties?.name || "";
}

function getAllPoints(geometry) {
  const points = [];
  const visit = c => {
    if (!Array.isArray(c)) return;
    if (typeof c[0] === "number") points.push(c);
    else c.forEach(visit);
  };
  visit(geometry.coordinates);
  return points;
}
function geoBounds(features) {
  const pts = features.flatMap(f => getAllPoints(f.geometry));
  return { minX: Math.min(...pts.map(p => p[0])), maxX: Math.max(...pts.map(p => p[0])), minY: Math.min(...pts.map(p => p[1])), maxY: Math.max(...pts.map(p => p[1])) };
}
function projector(bounds, w, h, pad) {
  const sc = Math.min((w - pad * 2) / (bounds.maxX - bounds.minX), (h - pad * 2) / (bounds.maxY - bounds.minY));
  const uw = (bounds.maxX - bounds.minX) * sc, uh = (bounds.maxY - bounds.minY) * sc;
  const ox = (w - uw) / 2, oy = (h - uh) / 2;
  return ([lon, lat]) => [ox + (lon - bounds.minX) * sc, h - oy - (lat - bounds.minY) * sc];
}
function ringPath(ring, project) {
  return ring.map((pt, i) => { const [x, y] = project(pt); return `${i ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`; }).join(" ") + " Z";
}
function geometryPath(g, project) {
  if (g.type === "Polygon") return g.coordinates.map(r => ringPath(r, project)).join(" ");
  if (g.type === "MultiPolygon") return g.coordinates.flatMap(p => p.map(r => ringPath(r, project))).join(" ");
  return "";
}

function selectedVars() {
  return state.paris.uqi.variables.filter(v => state.selected.has(v.key));
}
function valuesFor(city, key, decade) {
  return ents(city).map(e => e.values?.[decade]?.[key]).filter(v => typeof v === "number" && Number.isFinite(v));
}
function normalize(city, value, variable, decade) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  const vals = valuesFor(city, variable.key, decade);
  const min = Math.min(...vals), max = Math.max(...vals);
  if (min === max) return 0.5;
  const raw = (value - min) / (max - min);
  return variable.higherIsBetter ? raw : 1 - raw;
}
function scoreEntity(city, entity, decade) {
  const parts = selectedVars().map(v => normalize(city, entity.values?.[decade]?.[v.key], v, decade)).filter(x => x !== null);
  return parts.length ? parts.reduce((a, b) => a + b, 0) / parts.length : null;
}
function computeUqiScores(city, decade) {
  const m = new Map();
  ents(city).forEach(e => m.set(matchSlug(city, e.name), { entity: e, score: scoreEntity(city, e, decade) }));
  return m;
}
function computeHdiScores(city, decade) {
  const m = new Map();
  (state[city].hdi[cities[city].entitiesKey] || []).forEach(e => {
    const h = e.values?.[decade]?.hdi;
    m.set(matchSlug(city, e.name), { entity: e, hdi: typeof h === "number" ? h : null });
  });
  return m;
}
function colorUqi(s) {
  if (s == null) return "#c9c9c9";
  if (s < 0.2) return palette[0];
  if (s < 0.4) return palette[1];
  if (s < 0.6) return palette[2];
  if (s < 0.8) return palette[3];
  return palette[4];
}
function colorHdi(h) {
  if (typeof h !== "number") return "#c9c9c9";
  const t = Math.max(0, Math.min(1, (h - 0.75) / 0.2));
  return hdiPalette[Math.min(4, Math.floor(t * 5))];
}

function renderChoropleth(city, elId, scores, colorFn, scoreKey) {
  const el = document.getElementById(elId);
  const geo = state[city].geo;
  const w = 480, h = 400, pad = 28;
  const bounds = geoBounds(geo.features);
  const project = projector(bounds, w, h, pad);
  const paths = geo.features.map(f => {
    const name = fname(city, f);
    const rec = scores.get(matchSlug(city, name));
    const val = scoreKey === "score" ? rec?.score : rec?.hdi;
    const label = scoreKey === "score" ? (val == null ? "n/a" : Math.round(val * 100)) : (val == null ? "n/a" : val.toFixed(3));
    return `<path d="${geometryPath(f.geometry, project)}" fill="${colorFn(val)}" stroke="#2f3c4f" stroke-width="1.2" data-name="${name}" data-score="${label}"></path>`;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#f1f3f0"></rect><g>${paths}</g></svg>`;
}

function renderScatter(city, elId, uqiScores, hdiScores) {
  const el = document.getElementById(elId);
  const pts = [];
  uqiScores.forEach((rec, slug) => {
    const h = hdiScores.get(slug)?.hdi;
    if (typeof rec.score === "number" && typeof h === "number") pts.push({ x: rec.score, y: h });
  });
  if (!pts.length) {
    el.innerHTML = `<p class="hdi-unavailable">HDI not available for ${state.decade}. Earliest: ${cities[city].hdiEarliest}.</p>`;
    return;
  }
  const w = 480, h = 260, m = { t: 20, r: 20, b: 36, l: 44 };
  const x = v => m.l + v * (w - m.l - m.r);
  const y = v => m.t + (1 - (v - 0.75) / 0.2) * (h - m.t - m.b);
  const mx = pts.reduce((s, p) => s + p.x, 0) / pts.length, my = pts.reduce((s, p) => s + p.y, 0) / pts.length;
  let num = 0, dx = 0, dy = 0;
  pts.forEach(p => { num += (p.x - mx) * (p.y - my); dx += (p.x - mx) ** 2; dy += (p.y - my) ** 2; });
  const r2 = dx && dy ? (num ** 2) / (dx * dy) : 0;
  const sl = dx ? num / dx : 0;
  const dots = pts.map(p => `<circle cx="${x(p.x)}" cy="${y(p.y)}" r="4" fill="#506fb2"></circle>`).join("");
  el.innerHTML = `<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"></rect><line x1="${x(0)}" y1="${y(my + sl * (0 - mx))}" x2="${x(1)}" y2="${y(my + sl * (1 - mx))}" stroke="#9fa8da"/><text x="${w - 70}" y="18" class="axis-label">R²=${r2.toFixed(2)}</text>${dots}</svg>`;
}

function renderLines(city, elId) {
  const el = document.getElementById(elId);
  const decades = state.decades;
  const w = 480, h = 260, m = { t: 20, r: 16, b: 36, l: 44 };
  const x = i => m.l + i * ((w - m.l - m.r) / (decades.length - 1));
  const y = s => m.t + (1 - s) * (h - m.t - m.b);
  const lines = ents(city).map((e, i) => {
    const pts = decades.map((d, idx) => { const s = scoreEntity(city, e, d); return s == null ? null : [x(idx), y(s)]; }).filter(Boolean);
    if (pts.length < 2) return "";
    const d = pts.map((p, j) => `${j ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
    return `<path d="${d}" fill="none" stroke="${lineColors[i % lineColors.length]}" stroke-width="1.5" opacity=".75"></path>`;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"></rect><g>${lines}</g></svg>`;
}

function renderAll() {
  const d = state.decade;
  document.getElementById("decadeLabel").textContent = d;
  document.getElementById("parisUqiStatus").textContent = d;
  document.getElementById("cdmxUqiStatus").textContent = d;
  ["paris", "cdmx"].forEach(city => {
    const uqi = computeUqiScores(city, d);
    const hdi = computeHdiScores(city, d);
    const pre = city === "paris" ? "paris" : "cdmx";
    renderChoropleth(city, `${pre}UqiMap`, uqi, colorUqi, "score");
    const hdiRow = state[city].hdi[cities[city].entitiesKey]?.[0]?.values?.[d];
    if (hdiRow && typeof hdiRow.hdi === "number") renderChoropleth(city, `${pre}HdiMap`, hdi, colorHdi, "hdi");
    else document.getElementById(`${pre}HdiMap`).innerHTML = `<p class="hdi-unavailable">HDI not available for ${d}. Earliest: ${cities[city].hdiEarliest}.</p>`;
    renderScatter(city, `${pre}Scatter`, uqi, hdi);
    renderLines(city, `${pre}Lines`);
  });
}

function buildControls() {
  const slider = document.getElementById("decadeSlider");
  slider.max = state.decades.length - 1;
  slider.value = state.decades.length - 1;
  slider.addEventListener("input", e => {
    state.decade = state.decades[Number(e.target.value)];
    renderAll();
  });
  document.getElementById("decadeTicks").innerHTML = state.decades.map((d, i) => i % 3 === 0 || i === state.decades.length - 1 ? `<span>${d}</span>` : "<span></span>").join("");
  const vars = state.paris.uqi.variables;
  document.getElementById("variableControls").innerHTML = vars.map(v => `
    <label class="variable-toggle"><input type="checkbox" value="${v.key}" ${state.selected.has(v.key) ? "checked" : ""}>
    <span>${v.label}<small>${v.description}</small></span></label>`).join("");
  document.getElementById("variableControls").addEventListener("change", e => {
    if (!e.target.matches("input")) return;
    if (e.target.checked) state.selected.add(e.target.value);
    else state.selected.delete(e.target.value);
    renderAll();
  });
  document.getElementById("playButton").addEventListener("click", () => {
    if (state.playing) {
      state.playing = false;
      clearInterval(state.timer);
      document.getElementById("playButton").textContent = "Play";
      return;
    }
    state.playing = true;
    document.getElementById("playButton").textContent = "Pause";
    state.timer = setInterval(() => {
      const i = state.decades.indexOf(state.decade);
      state.decade = state.decades[i >= state.decades.length - 1 ? 0 : i + 1];
      slider.value = state.decades.indexOf(state.decade);
      renderAll();
    }, 900);
  });
}

Promise.all([
  fetch(cities.paris.uqiUrl).then(r => r.json()),
  fetch(cities.paris.hdiUrl).then(r => r.json()),
  fetch(cities.paris.geoUrl).then(r => r.json()),
  fetch(cities.cdmx.uqiUrl).then(r => r.json()),
  fetch(cities.cdmx.hdiUrl).then(r => r.json()),
  fetch(cities.cdmx.geoUrl).then(r => r.json())
]).then(([pu, ph, pg, cu, ch, cg]) => {
  state.paris = { uqi: pu, hdi: ph, geo: pg };
  state.cdmx = { uqi: cu, hdi: ch, geo: cg };
  state.decades = pu.decades.filter(d => cu.decades.includes(d));
  state.decade = state.decades[state.decades.length - 1];
  pu.variables.filter(v => v.defaultSelected).forEach(v => state.selected.add(v.key));
  buildControls();
  renderAll();
}).catch(err => console.error(err));
