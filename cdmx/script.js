const CFG = {
  cityTag: "CDMX",
  entitiesKey: "alcaldias",
  entityLabel: "alcaldía",
  entityCount: 16,
  uqiUrl: "../data/cdmx/uqi-by-alcaldia.json",
  geoUrl: "../data/cdmx/alcaldias.geojson",
  hdiUrl: "../data/cdmx/hdi-by-alcaldia.json",
  hdiEarliest: "2000",
  pathClass: "alcaldia-path"
};

const state = {
  decade: "2020",
  data: null,
  hdiData: null,
  boundaries: null,
  selectedVariables: new Set(),
  scores: new Map(),
  hdiScores: new Map(),
  playing: false,
  timer: null
};

const aliases = new Map([
  ["magdalena_contreras", "la_magdalena_contreras"],
  ["cuajimalpa", "cuajimalpa_de_morelos"]
]);

const tooltip = document.getElementById("tooltip");
const palette = ["#d95f59", "#e79262", "#f1d36b", "#9cc77b", "#5aac72"];
const lineColors = ["#314f9f", "#b85c45", "#5e8c61", "#8763a8", "#c79335", "#4b8a99", "#a34f78", "#6f7d44", "#485b75", "#d07a42", "#6c5aa8", "#40876f", "#b34c4c", "#4774b5", "#8a6f38", "#5e7180"];

function slug(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "");
}

function matchSlug(value) {
  const s = slug(value);
  return aliases.get(s) || s;
}

function entities() {
  return state.data[CFG.entitiesKey] || [];
}

Promise.all([
  fetch(CFG.uqiUrl).then(response => response.json()),
  fetch(CFG.geoUrl).then(response => response.json()),
  fetch(CFG.hdiUrl).then(response => response.json())
]).then(([data, boundaries, hdi]) => {
  state.data = data;
  state.hdi = hdi;
  state.boundaries = boundaries;
  state.decade = data.decades[data.decades.length - 1];
  data.variables.filter(variable => variable.defaultSelected).forEach(variable => state.selectedVariables.add(variable.key));
  buildControls();
  renderAll();
}).catch(error => {
  document.getElementById("methodSummary").textContent = `Could not load visualization data: ${error.message}`;
});

function buildControls() {
  const slider = document.getElementById("decadeSlider");
  const mapSlider = document.getElementById("mapDecadeSlider");
  const ticks = document.getElementById("decadeTicks");
  const lastIndex = state.data.decades.length - 1;

  [slider, mapSlider].forEach(input => {
    input.max = lastIndex;
    input.value = lastIndex;
    input.addEventListener("input", event => {
      setDecadeByIndex(Number(event.target.value));
      stopPlayback();
    });
  });

  ticks.innerHTML = state.data.decades
    .map((decade, index) => index % 4 === 0 || index === lastIndex ? `<span>${decade}</span>` : "<span></span>")
    .join("");

  const controls = document.getElementById("variableControls");
  controls.innerHTML = state.data.variables.map(variable => {
    const note = state.data.sourceNotes?.[variable.key] || variable.description;
    return `
      <label class="variable-toggle">
        <input type="checkbox" value="${variable.key}" ${state.selectedVariables.has(variable.key) ? "checked" : ""}>
        <span>${variable.label}
          <small>${variable.description}</small>
          <em class="method-note">* ${note}</em>
        </span>
      </label>
    `;
  }).join("");

  controls.addEventListener("change", event => {
    if (!event.target.matches("input[type='checkbox']")) return;
    if (event.target.checked) state.selectedVariables.add(event.target.value);
    else state.selectedVariables.delete(event.target.value);
    renderAll();
  });

  document.getElementById("resetVariables").addEventListener("click", () => {
    state.selectedVariables = new Set(state.data.variables.filter(variable => variable.defaultSelected).map(variable => variable.key));
    controls.querySelectorAll("input[type='checkbox']").forEach(input => {
      input.checked = state.selectedVariables.has(input.value);
    });
    renderAll();
  });

  document.getElementById("playButton").addEventListener("click", () => {
    state.playing ? stopPlayback() : startPlayback();
  });

  syncDecadeLabels();
}

function setDecadeByIndex(index) {
  state.decade = state.data.decades[Math.max(0, Math.min(index, state.data.decades.length - 1))];
  syncDecadeLabels();
  renderAll();
}

function syncDecadeLabels() {
  const index = state.data.decades.indexOf(state.decade);
  document.getElementById("decadeLabel").textContent = state.decade;
  document.getElementById("mapStatus").textContent = `${state.decade} · CDMX UQI`;
  document.getElementById("decadeSlider").value = index;
  document.getElementById("mapDecadeSlider").value = index;
}

function startPlayback() {
  state.playing = true;
  document.getElementById("playButton").textContent = "Pause";
  state.timer = window.setInterval(() => {
    const current = state.data.decades.indexOf(state.decade);
    const next = current >= state.data.decades.length - 1 ? 0 : current + 1;
    setDecadeByIndex(next);
  }, 900);
}

function stopPlayback() {
  state.playing = false;
  document.getElementById("playButton").textContent = "Play";
  if (state.timer) window.clearInterval(state.timer);
  state.timer = null;
}

function selectedVariables() {
  return state.data.variables.filter(variable => state.selectedVariables.has(variable.key));
}

function valuesForDecade(variableKey, decade = state.decade) {
  return entities()
    .map(entity => entity.values?.[decade]?.[variableKey])
    .filter(value => typeof value === "number" && Number.isFinite(value));
}

function normalize(value, variable, decade = state.decade) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  const values = valuesForDecade(variable.key, decade);
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) return 0.5;
  const rawScore = (value - min) / (max - min);
  return variable.higherIsBetter ? rawScore : 1 - rawScore;
}

function scoreEntity(entity, decade = state.decade) {
  const parts = selectedVariables()
    .map(variable => normalize(entity.values?.[decade]?.[variable.key], variable, decade))
    .filter(value => value !== null);
  return parts.length ? parts.reduce((sum, value) => sum + value, 0) / parts.length : null;
}

function computeScores(decade = state.decade) {
  const bySlug = new Map();
  entities().forEach(entity => {
    bySlug.set(matchSlug(entity.name), { entity, score: scoreEntity(entity, decade), selected: selectedVariables() });
  });
  if (decade === state.decade) state.scores = bySlug;
  return bySlug;
}

const hdiPalette = ["#e8eaf6", "#c5cae9", "#9fa8da", "#5c6bc0", "#3949ab"];

function colorHdi(hdi) {
  if (typeof hdi !== "number" || !Number.isFinite(hdi)) return "#c9c9c9";
  const t = Math.max(0, Math.min(1, (hdi - 0.75) / 0.2));
  return hdiPalette[Math.min(4, Math.floor(t * 5))];
}

function computeHdiScores(decade = state.decade) {
  const bySlug = new Map();
  if (!state.hdi) return bySlug;
  (state.hdi[CFG.entitiesKey] || []).forEach(entity => {
    const hdi = entity.values?.[decade]?.hdi;
    bySlug.set(matchSlug(entity.name), { entity, hdi: typeof hdi === "number" ? hdi : null });
  });
  if (decade === state.decade) state.hdiScores = bySlug;
  return bySlug;
}

function colorFor(score) {
  if (score === null || score === undefined) return "#c9c9c9";
  if (score < 0.2) return palette[0];
  if (score < 0.4) return palette[1];
  if (score < 0.6) return palette[2];
  if (score < 0.8) return palette[3];
  return palette[4];
}

function featureName(feature) {
  return feature.properties?.alcaldia || feature.properties?.NOMGEO || feature.properties?.nomgeo || "";
}

function getAllPoints(geometry) {
  const points = [];
  const visit = coords => {
    if (!Array.isArray(coords)) return;
    if (typeof coords[0] === "number" && typeof coords[1] === "number") points.push(coords);
    else coords.forEach(visit);
  };
  visit(geometry.coordinates);
  return points;
}

function geoBounds(features) {
  const points = features.flatMap(feature => getAllPoints(feature.geometry));
  return {
    minX: Math.min(...points.map(point => point[0])),
    maxX: Math.max(...points.map(point => point[0])),
    minY: Math.min(...points.map(point => point[1])),
    maxY: Math.max(...points.map(point => point[1]))
  };
}

function projector(bounds, width, height, padding) {
  const scale = Math.min((width - padding * 2) / (bounds.maxX - bounds.minX), (height - padding * 2) / (bounds.maxY - bounds.minY));
  const usedWidth = (bounds.maxX - bounds.minX) * scale;
  const usedHeight = (bounds.maxY - bounds.minY) * scale;
  const offsetX = (width - usedWidth) / 2;
  const offsetY = (height - usedHeight) / 2;
  return ([lon, lat]) => [offsetX + (lon - bounds.minX) * scale, height - offsetY - (lat - bounds.minY) * scale];
}

function ringPath(ring, project) {
  return ring.map((point, index) => {
    const [x, y] = project(point);
    return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ") + " Z";
}

function geometryPath(geometry, project) {
  if (geometry.type === "Polygon") return geometry.coordinates.map(ring => ringPath(ring, project)).join(" ");
  if (geometry.type === "MultiPolygon") return geometry.coordinates.flatMap(poly => poly.map(ring => ringPath(ring, project))).join(" ");
  return "";
}

function geometryCentroid(geometry, project) {
  const projected = getAllPoints(geometry).map(project);
  return [projected.reduce((sum, point) => sum + point[0], 0) / projected.length, projected.reduce((sum, point) => sum + point[1], 0) / projected.length];
}

function renderAll() {
  computeScores();
  computeHdiScores();
  renderMap();
  renderHDIMap();
  renderLineChart();
  renderHDILineChart();
  renderScatter();
  updateMethodSummary();
  updateRanking();
}

function renderMap() {
  const width = 960;
  const height = 560;
  const bounds = geoBounds(state.boundaries.features);
  const project = projector(bounds, width, height, 34);
  const scores = state.scores;
  const paths = state.boundaries.features.map(feature => {
    const name = featureName(feature);
    const record = scores.get(matchSlug(name));
    const scoreLabel = record?.score === null || record?.score === undefined ? "n/a" : Math.round(record.score * 100);
    return `<path class="${CFG.pathClass}" d="${geometryPath(feature.geometry, project)}" fill="${colorFor(record?.score)}" data-name="${name}" data-score="${scoreLabel}"></path>`;
  }).join("");
  const labels = state.boundaries.features.map(feature => {
    const [x, y] = geometryCentroid(feature.geometry, project);
    const name = featureName(feature).replace("La Magdalena Contreras", "Magdalena C.").replace("Gustavo A. Madero", "G.A. Madero").replace("Venustiano Carranza", "V. Carranza").replace("Cuajimalpa de Morelos", "Cuajimalpa");
    return `<text class="map-label" x="${x.toFixed(1)}" y="${y.toFixed(1)}">${name}</text>`;
  }).join("");

  document.getElementById("map").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Mexico City UQI by alcaldía">
      <rect width="${width}" height="${height}" fill="#f1f3f0"></rect>
      <g>${paths}</g>
      <g>${labels}</g>
    </svg>
  `;

  document.querySelectorAll(`.${CFG.pathClass}`).forEach(path => {
    path.addEventListener("mousemove", event => showTooltip(event, path.dataset.name, path.dataset.score));
    path.addEventListener("mouseleave", hideTooltip);
  });
}

function showTooltip(event, name, score) {
  const record = state.scores.get(matchSlug(name));
  const lines = record?.selected.slice(0, 5).map(variable => {
    const value = record.entity.values?.[state.decade]?.[variable.key];
    return `${variable.label}: ${formatValue(value, variable.unit)}`;
  }).join("<br>") || "No selected variables";
  tooltip.innerHTML = `<strong>${name}</strong>${state.decade} UQI: ${score}/100<br>${lines}`;
  tooltip.style.display = "block";
  tooltip.style.left = `${event.clientX + 14}px`;
  tooltip.style.top = `${event.clientY + 14}px`;
}

function hideTooltip() {
  tooltip.style.display = "none";
}

function renderLineChart() {
  const width = 960;
  const height = 360;
  const margin = { top: 24, right: 26, bottom: 44, left: 48 };
  const decades = state.data.decades;
  const x = index => margin.left + index * ((width - margin.left - margin.right) / (decades.length - 1));
  const y = score => margin.top + (1 - score) * (height - margin.top - margin.bottom);
  const grid = [0, 0.25, 0.5, 0.75, 1].map(value => `
    <line class="grid" x1="${margin.left}" x2="${width - margin.right}" y1="${y(value)}" y2="${y(value)}"></line>
    <text class="axis-label" x="${margin.left - 10}" y="${y(value) + 4}" text-anchor="end">${Math.round(value * 100)}</text>
  `).join("");
  const xLabels = decades.map((decade, index) => index % 4 === 0 || index === decades.length - 1 ? `<text class="axis-label" x="${x(index)}" y="${height - 16}" text-anchor="middle">${decade}</text>` : "").join("");
  const lines = entities().map((entity, entityIndex) => {
    const points = decades.map((decade, index) => {
      const score = scoreEntity(entity, decade);
      return score === null ? null : [x(index), y(score), score, decade];
    }).filter(Boolean);
    const d = points.map((point, index) => `${index === 0 ? "M" : "L"}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ");
    const active = points.find(point => point[3] === state.decade);
    const dot = active ? `<circle class="chart-dot" cx="${active[0]}" cy="${active[1]}" r="4" fill="${lineColors[entityIndex % lineColors.length]}"></circle>` : "";
    return `<path class="chart-line" d="${d}" stroke="${lineColors[entityIndex % lineColors.length]}" data-name="${entity.name}"></path>${dot}`;
  }).join("");

  document.getElementById("lineChart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="UQI score by decade for each alcaldía">
      <rect width="${width}" height="${height}" fill="#fff"></rect>
      ${grid}
      <line class="axis" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${xLabels}
      <text class="axis-label" x="${margin.left}" y="16">UQI score</text>
      <g>${lines}</g>
    </svg>
  `;

  document.querySelectorAll(".chart-line").forEach(line => {
    line.addEventListener("mousemove", event => {
      tooltip.innerHTML = `<strong>${line.dataset.name}</strong>Line shows UQI score from 1860 to 2020 for the selected variables.`;
      tooltip.style.display = "block";
      tooltip.style.left = `${event.clientX + 14}px`;
      tooltip.style.top = `${event.clientY + 14}px`;
    });
    line.addEventListener("mouseleave", hideTooltip);
  });
}

function formatValue(value, unit) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "n/a";
  const formatted = value >= 100 ? Math.round(value).toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  return `${formatted} ${unit || ""}`.trim();
}

function updateMethodSummary() {
  const selected = selectedVariables().map(variable => variable.label);
  document.getElementById("methodSummary").textContent = selected.length
    ? `${state.decade}: equal-weight UQI using ${selected.join(", ")}. Variables are min-max normalized across the ${CFG.entityCount} ${CFG.entityLabel}s within each decade.`
    : "Select at least one variable to calculate the UQI.";
}

function updateRanking() {
  const ranking = [...state.scores.values()]
    .filter(record => typeof record.score === "number")
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);
  document.getElementById("rankingList").innerHTML = ranking
    .map(record => `<li>${record.entity.name}: <strong>${Math.round(record.score * 100)}</strong></li>`)
    .join("");
}

function renderHDIMap() {
  const el = document.getElementById("hdiMap");
  if (!el) return;
  const row = state.hdi?.[CFG.entitiesKey]?.[0]?.values?.[state.decade];
  if (!row || typeof row.hdi !== "number") {
    el.innerHTML = `<p class="hdi-unavailable">HDI not available for ${state.decade}. Earliest published value: ${CFG.hdiEarliest}.</p>`;
    return;
  }
  const width = 960;
  const height = 560;
  const bounds = geoBounds(state.boundaries.features);
  const project = projector(bounds, width, height, 34);
  const scores = state.hdiScores;
  const paths = state.boundaries.features.map(feature => {
    const name = featureName(feature);
    const record = scores.get(matchSlug(name));
    const hdi = record?.hdi;
    const label = hdi == null ? "n/a" : hdi.toFixed(3);
    return `<path class="${CFG.pathClass}" d="${geometryPath(feature.geometry, project)}" fill="${colorHdi(hdi)}" data-name="${name}" data-score="${label}"></path>`;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="HDI map"><rect width="${width}" height="${height}" fill="#f1f3f0"></rect><g>${paths}</g></svg>`;
}

function renderHDILineChart() {
  const el = document.getElementById("hdiLineChart");
  if (!el || !state.hdi) return;
  const decades = state.data.decades;
  const width = 960;
  const height = 300;
  const margin = { top: 24, right: 26, bottom: 44, left: 48 };
  const x = index => margin.left + index * ((width - margin.left - margin.right) / (decades.length - 1));
  const y = v => margin.top + (1 - (v - 0.75) / 0.2) * (height - margin.top - margin.bottom);
  const lines = (state.hdi[CFG.entitiesKey] || []).map((entity, i) => {
    const pts = decades.map((decade, idx) => {
      const h = entity.values?.[decade]?.hdi;
      return typeof h === "number" ? [x(idx), y(h), decade] : null;
    }).filter(Boolean);
    if (pts.length < 2) return "";
    const d = pts.map((p, j) => `${j ? "L" : "M"}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(" ");
    return `<path class="chart-line" d="${d}" stroke="${lineColors[i % lineColors.length]}" data-name="${entity.name}"></path>`;
  }).join("");
  el.innerHTML = lines ? `<svg viewBox="0 0 ${width} ${height}"><rect width="${width}" height="${height}" fill="#fff"></rect><g>${lines}</g></svg>` : `<p class="hdi-unavailable">No HDI time series for this city.</p>`;
}

function renderScatter() {
  const el = document.getElementById("scatterChart");
  if (!el) return;
  const pts = [];
  state.scores.forEach((rec, slug) => {
    const h = state.hdiScores.get(slug)?.hdi;
    if (typeof rec.score === "number" && typeof h === "number") pts.push({ name: rec.entity.name, x: rec.score, y: h });
  });
  const width = 960;
  const height = 320;
  const margin = { top: 24, right: 26, bottom: 44, left: 48 };
  if (!pts.length) {
    el.innerHTML = `<p class="hdi-unavailable">UQI × HDI scatter needs HDI for ${state.decade}.</p>`;
    return;
  }
  const x = v => margin.left + v * (width - margin.left - margin.right);
  const y = v => margin.top + (1 - (v - 0.75) / 0.2) * (height - margin.top - margin.bottom);
  const meanX = pts.reduce((s, p) => s + p.x, 0) / pts.length;
  const meanY = pts.reduce((s, p) => s + p.y, 0) / pts.length;
  let num = 0, denX = 0, denY = 0;
  pts.forEach(p => { num += (p.x - meanX) * (p.y - meanY); denX += (p.x - meanX) ** 2; denY += (p.y - meanY) ** 2; });
  const r2 = denX && denY ? (num ** 2) / (denX * denY) : 0;
  const slope = denX ? num / denX : 0;
  const x0 = 0, x1 = 1, y0 = meanY + slope * (x0 - meanX), y1 = meanY + slope * (x1 - meanX);
  const dots = pts.map(p => `<circle cx="${x(p.x)}" cy="${y(p.y)}" r="5" fill="#506fb2" data-name="${p.name}"></circle>`).join("");
  el.innerHTML = `<svg viewBox="0 0 ${width} ${height}"><rect width="${width}" height="${height}" fill="#fff"></rect><line x1="${x(x0)}" y1="${y(y0)}" x2="${x(x1)}" y2="${y(y1)}" stroke="#9fa8da" stroke-width="2"/><text x="${width-120}" y="24" class="axis-label">R² = ${r2.toFixed(2)}</text>${dots}</svg>`;
}
