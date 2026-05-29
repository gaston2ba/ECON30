/**
 * ECON 30 capstone — parallel Paris / Mexico City maps, hover sync, scatter link.
 */
const Capstone = {
  bundle: null,
  geo: { paris: null, mexico: null },
  activeComponent: "all",
  hover: null,
  hoverTimer: null,
  pathSel: { parisUqi: null, parisHdi: null, mexicoUqi: null, mexicoHdi: null },

  mexicoById: new Map(),
  parisById: new Map(),
  mexicoPanel: [],
  parisPanel: [],

  async init() {
    const [bundle, parisGeo, mexicoGeo] = await Promise.all([
      fetch("data/analysis/capstone_bundle.json").then((r) => r.json()),
      fetch("data/maps/paris_arrondissements.geojson").then((r) => r.json()),
      fetch("data/maps/mexico_alcaldias.geojson").then((r) => r.json()),
    ]);
    this.bundle = bundle;
    this.geo.paris = parisGeo;
    this.geo.mexico = mexicoGeo;
    bundle.mexico.snap2020.forEach((r) => this.mexicoById.set(r.alcaldia_id, { ...r }));
    bundle.mexico.hdi2020.forEach((r) => {
      const p = this.mexicoById.get(r.alcaldia_id) || {};
      this.mexicoById.set(r.alcaldia_id, { ...p, hdi: r.hdi });
    });
    bundle.paris.snap2022.forEach((r) => this.parisById.set(r.arrondissement_num, { ...r }));
    bundle.paris.hdi2022.forEach((r) => {
      const p = this.parisById.get(r.arrondissement_num) || {};
      this.parisById.set(r.arrondissement_num, { ...p, hdi: r.hdi });
    });
    this.mexicoPanel = bundle.mexico.panel;
    this.parisPanel = bundle.paris.panel;

    this.bindGlossary();
    this.bindComponents();
    this.renderMaps();
    this.renderScatters();
    this.renderLineCharts();
  },

  bindGlossary() {
    document.querySelectorAll(".gloss-trigger").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const pop = btn.parentElement.querySelector(".gloss-pop");
        const open = pop.classList.contains("visible");
        document.querySelectorAll(".gloss-pop").forEach((p) => p.classList.remove("visible"));
        document.querySelectorAll(".gloss-trigger").forEach((b) => b.classList.remove("open"));
        if (!open) {
          pop.classList.add("visible");
          btn.classList.add("open");
        }
      });
    });
    document.addEventListener("click", () => {
      document.querySelectorAll(".gloss-pop").forEach((p) => p.classList.remove("visible"));
      document.querySelectorAll(".gloss-trigger").forEach((b) => b.classList.remove("open"));
    });
  },

  bindComponents() {
    document.querySelectorAll(".comp-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".comp-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeComponent = btn.dataset.component;
        this.renderMaps();
        this.renderScatters();
      });
    });
  },

  scoreMexico(id) {
    const r = this.mexicoById.get(id);
    if (!r) return null;
    if (this.activeComponent === "all") return r.uqi;
    return r[this.activeComponent];
  },

  scoreParis(id) {
    const r = this.parisById.get(id);
    if (!r) return null;
    if (this.activeComponent === "all") return r.uqi;
    return r[this.activeComponent];
  },

  hdiMexico(id) {
    return this.mexicoById.get(id)?.hdi ?? null;
  },

  hdiParis(id) {
    return this.parisById.get(id)?.hdi ?? null;
  },

  renderMaps() {
    this.renderOneMap("paris", "uqi", "#map-paris-uqi", false);
    this.renderOneMap("mexico", "uqi", "#map-mexico-uqi", false);
    this.renderOneMap("paris", "hdi", "#map-paris-hdi", true);
    this.renderOneMap("mexico", "hdi", "#map-mexico-hdi", true);
  },

  renderOneMap(city, layer, selector, isHdi) {
    const geo = this.geo[city];
    const el = document.querySelector(selector);
    if (!el || typeof d3 === "undefined") return;
    const w = el.clientWidth || 480;
    const h = 380;
    const scoreFn =
      city === "paris"
        ? (id) => (isHdi ? this.hdiParis(id) : this.scoreParis(id))
        : (id) => (isHdi ? this.hdiMexico(id) : this.scoreMexico(id));
    const getFill = (d) => {
      const id = Number(d.properties.id);
      const v = scoreFn(id);
      if (v == null) return "#d8d0c0";
      if (isHdi) {
        const t = Math.max(0, Math.min(1, (v - 0.75) / 0.2));
        return d3.interpolateRgb("#e8e4dc", "#2a3f5c")(t);
      }
      return CityMapUtils.colorForScore(v, city);
    };
    const svg = el.querySelector("svg") || d3.select(el).append("svg").node();
    CityMapUtils.renderChoropleth({
      svg,
      geojson: geo,
      width: w,
      height: h,
      getFill,
      strokeWidth: 0.9,
      onClick: (d) => this.selectRegion(city, Number(d.properties.id)),
    });
    const paths = d3.select(svg).selectAll("path.region");
    paths
      .attr("data-city", city)
      .attr("data-id", (d) => d.properties.id)
      .on("mouseenter", (event, d) => this.onEnter(city, Number(d.properties.id), event))
      .on("mousemove", (event) => this.movePanel(event))
      .on("mouseleave", () => this.onLeave());
    this.pathSel[`${city}_${layer}`] = paths;
  },

  onEnter(city, id, event) {
    clearTimeout(this.hoverTimer);
    this.hover = { city, id };
    this.applyHover();
    this.movePanel(event);
    this.updatePanel(city, id);
  },

  onLeave() {
    this.hoverTimer = setTimeout(() => {
      this.hover = null;
      this.applyHover();
      document.getElementById("hover-panel").style.display = "none";
    }, 200);
  },

  movePanel(event) {
    const panel = document.getElementById("hover-panel");
    panel.style.display = "block";
    let x = event.clientX + 16;
    let y = event.clientY + 16;
    if (x + 280 > window.innerWidth) x = event.clientX - 296;
    if (y + 120 > window.innerHeight) y = event.clientY - 130;
    panel.style.left = `${x}px`;
    panel.style.top = `${y}px`;
  },

  applyHover() {
    const h = this.hover;
    Object.values(this.pathSel).forEach((sel) => {
      if (!sel) return;
      sel
        .classed("hovered", function () {
          if (!h) return false;
          return d3.select(this).attr("data-city") === h.city && Number(d3.select(this).attr("data-id")) === h.id;
        })
        .classed("dimmed", function () {
          if (!h) return false;
          return !(d3.select(this).attr("data-city") === h.city && Number(d3.select(this).attr("data-id")) === h.id);
        });
    });
  },

  updatePanel(city, id) {
    const panel = document.getElementById("hover-panel");
    const name = city === "paris" ? this.parisById.get(id)?.arrondissement : this.mexicoById.get(id)?.alcaldia_name;
    const uqi = city === "paris" ? this.scoreParis(id) : this.scoreMexico(id);
    const hdi = city === "paris" ? this.hdiParis(id) : this.hdiMexico(id);
    const uqiRank = this.rank(city, "uqi", id);
    const hdiRank = this.rank(city, "hdi", id);
    panel.innerHTML = `<strong>${name || ""}</strong>
      UQI: ${uqi != null ? uqi.toFixed(1) : "n/a"} (rank ${uqiRank} in city)
      <br>HDI: ${hdi != null ? hdi.toFixed(3) : "n/a"} (rank ${hdiRank} in city)`;
  },

  rank(city, metric, id) {
    const ids = city === "paris" ? [...this.parisById.keys()] : [...this.mexicoById.keys()];
    const vals = ids.map((i) => ({
      i,
      v: metric === "hdi" ? (city === "paris" ? this.hdiParis(i) : this.hdiMexico(i)) : city === "paris" ? this.scoreParis(i) : this.scoreMexico(i),
    }));
    vals.sort((a, b) => (b.v ?? 0) - (a.v ?? 0));
    return vals.findIndex((x) => x.i === id) + 1;
  },

  selectRegion(city, id) {
    this.hover = { city, id };
    this.applyHover();
    this.renderScatters();
  },

  renderScatters() {
    this.renderScatter("paris", "#scatter-paris");
    this.renderScatter("mexico", "#scatter-mexico");
  },

  renderScatter(city, sel) {
    const el = document.querySelector(sel);
    if (!el || typeof d3 === "undefined") return;
    const w = el.clientWidth || 480;
    const h = 320;
    const m = { t: 28, r: 20, b: 44, l: 52 };
    const ids = city === "paris" ? [...this.parisById.keys()] : [...this.mexicoById.keys()];
    const pts = ids
      .map((id) => ({
        id,
        name: city === "paris" ? this.parisById.get(id).arrondissement : this.mexicoById.get(id).alcaldia_name,
        x: city === "paris" ? this.scoreParis(id) : this.scoreMexico(id),
        y: city === "paris" ? this.hdiParis(id) : this.hdiMexico(id),
      }))
      .filter((p) => p.x != null && p.y != null);
    const svg = d3.select(el).selectAll("svg").data([1]).join("svg").attr("viewBox", `0 0 ${w} ${h}`);
    svg.selectAll("*").remove();
    svg.append("rect").attr("width", w).attr("height", h).attr("fill", "#faf6ee");
    const x = d3.scaleLinear().domain([0, 100]).range([m.l, w - m.r]);
    const y = d3.scaleLinear().domain([0.75, 0.95]).range([h - m.b, m.t]);
    const xbar = d3.mean(pts, (p) => p.x);
    const ybar = d3.mean(pts, (p) => p.y);
    let num = 0,
      dx = 0,
      dy = 0;
    pts.forEach((p) => {
      num += (p.x - xbar) * (p.y - ybar);
      dx += (p.x - xbar) ** 2;
      dy += (p.y - ybar) ** 2;
    });
    const r2 = dx && dy ? (num ** 2) / (dx * dy) : 0;
    const slope = dx ? num / dx : 0;
    svg
      .append("line")
      .attr("x1", x(0))
      .attr("y1", y(ybar + slope * (0 - xbar)))
      .attr("x2", x(100))
      .attr("y2", y(ybar + slope * (100 - xbar)))
      .attr("stroke", city === "paris" ? "var(--accent-paris)" : "var(--accent-mexico)")
      .attr("stroke-width", 1.5);
    svg
      .append("text")
      .attr("x", w - m.r - 80)
      .attr("y", m.t + 12)
      .attr("font-size", 11)
      .text(`R² = ${r2.toFixed(2)}`);
    svg
      .selectAll("circle")
      .data(pts)
      .join("circle")
      .attr("cx", (p) => x(p.x))
      .attr("cy", (p) => y(p.y))
      .attr("r", (p) => (this.hover && this.hover.city === city && this.hover.id === p.id ? 7 : 4))
      .attr("fill", (p) => (this.hover && this.hover.city === city && this.hover.id === p.id ? "var(--accent-gold)" : city === "paris" ? "#7a1f2b" : "#2d5a3d"))
      .style("cursor", "pointer")
      .on("click", () => this.selectRegion(city, p.id));
    svg.append("text").attr("x", m.l).attr("y", h - 8).attr("font-size", 11).text("UQI (0–100)");
    svg.append("text").attr("x", 8).attr("y", m.t).attr("font-size", 11).attr("transform", `rotate(-90,12,${m.t})`).text("HDI");
  },

  renderLineCharts() {
    this.renderLines("mexico", "#lines-mexico", this.mexicoPanel, "year");
    this.renderLines("paris", "#lines-paris", this.parisPanel, "year");
  },

  renderLines(city, sel, panel, yearKey) {
    const el = document.querySelector(sel);
    if (!el || !panel.length) return;
    const w = el.clientWidth || 480;
    const h = 320;
    const years = [...new Set(panel.map((r) => r[yearKey]))].sort((a, b) => a - b);
    const ids = city === "paris" ? [...this.parisById.keys()] : [...this.mexicoById.keys()];
    const lastYear = Math.max(...years);
    const ranked = ids
      .map((id) => ({ id, uqi: panel.find((r) => r[yearKey] === lastYear && (r.arrondissement_num || r.alcaldia_id) === id)?.uqi }))
      .filter((x) => x.uqi != null)
      .sort((a, b) => b.uqi - a.uqi);
    const top = new Set(ranked.slice(0, 5).map((x) => x.id));
    const bot = new Set(ranked.slice(-5).map((x) => x.id));
    const mid = new Set(ids.filter((i) => !top.has(i) && !bot.has(i)));
    const svg = d3.select(el).selectAll("svg").data([1]).join("svg").attr("viewBox", `0 0 ${w} ${h}`);
    svg.selectAll("*").remove();
    const m = { t: 24, r: 16, b: 40, l: 48 };
    const x = d3.scalePoint().domain(years.map(String)).range([m.l, w - m.r]);
    const y = d3.scaleLinear().domain([0, 100]).range([h - m.b, m.t]);
    const bandMean = (set) =>
      years.map((yr) => {
        const vals = panel.filter((r) => r[yearKey] === yr && set.has(r.arrondissement_num || r.alcaldia_id)).map((r) => r.uqi);
        return { yr, v: vals.length ? d3.mean(vals) : null };
      });
    [["top", top, "#7a1f2b"], ["mid", mid, "#8a6a1f"], ["bot", bot, "#2d5a3d"]].forEach(([label, set, color]) => {
      const series = bandMean(set);
      const line = d3
        .line()
        .defined((d) => d.v != null)
        .x((d) => x(String(d.yr)))
        .y((d) => y(d.v));
      svg.append("path").attr("d", line(series)).attr("fill", "none").attr("stroke", color).attr("stroke-width", 2.5);
    });
    ids.forEach((id) => {
      const pts = years.map((yr) => panel.find((r) => r[yearKey] === yr && (r.arrondissement_num || r.alcaldia_id) === id)).filter(Boolean);
      const line = d3
        .line()
        .defined((r) => r && r.uqi != null)
        .x((r) => x(String(r[yearKey])))
        .y((r) => y(r.uqi));
      svg.append("path").attr("d", line(pts)).attr("fill", "none").attr("stroke", "#999").attr("stroke-width", 0.6).attr("opacity", 0.35);
    });
  },
};

document.addEventListener("DOMContentLoaded", () => Capstone.init().catch(console.error));
