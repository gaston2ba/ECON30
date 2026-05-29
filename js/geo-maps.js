/**
 * GeoJSON choropleth maps + monument then/now explorer.
 */
const GeoMap = {
  geo: { paris: null, mexico: null },
  monuments: { paris: [], mexico: [] },
  ready: false,
  layer: 'index',
  selectedMonument: null,
  projection: null,
  path: null,

  async init() {
    try {
      const [parisGeo, mexicoGeo, parisMon, mexicoMon] = await Promise.all([
        fetch('data/maps/paris_arrondissements.geojson').then((r) => r.json()),
        fetch('data/maps/mexico_alcaldias.geojson').then((r) => r.json()),
        fetch('data/monuments/paris.json').then((r) => r.json()),
        fetch('data/monuments/mexico.json').then((r) => r.json()),
      ]);
      this.geo.paris = parisGeo;
      this.geo.mexico = mexicoGeo;
      this.monuments.paris = parisMon;
      this.monuments.mexico = mexicoMon;
      this.ready = true;
      this.bindLayerControls();
      window.addEventListener('resize', () => this.render());
      this.render();
      if (typeof buildMonumentGrid === 'function') buildMonumentGrid();
    } catch (err) {
      console.warn('GeoMap: falling back to bubble map', err);
      this.ready = false;
      if (typeof renderMap === 'function') renderMap();
    }
  },

  bindLayerControls() {
    document.querySelectorAll('.map-layer-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.layer = btn.dataset.mapLayer;
        document.querySelectorAll('.map-layer-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        this.selectedMonument = null;
        this.render();
        this.renderMonumentDetail(null);
      });
    });
  },

  featureId(props) {
    return Number(props.id);
  },

  scoreForId(id) {
    const region = DATA[state.city].find((r) => r.id === id);
    if (!region) return null;
    return regionIndex(region, state.active);
  },

  mapDimensions() {
    const stage = document.querySelector('.map-stage');
    const maxW = stage ? Math.min(760, stage.clientWidth - 24) : 720;
    const width = Math.max(320, maxW);
    const height = state.city === 'paris' ? Math.round(width * 0.82) : Math.round(width * 0.72);
    return { width, height };
  },

  render() {
    if (!this.ready || typeof d3 === 'undefined' || typeof CityMapUtils === 'undefined') return;

    const city = state.city;
    const geojson = this.geo[city];
    const { width, height } = this.mapDimensions();
    const svg = d3.select('#map-svg');

    const { projection, path } = CityMapUtils.renderChoropleth({
      svg: '#map-svg',
      geojson,
      width,
      height,
      opacity: this.layer === 'monuments' ? 0.5 : 1,
      getFill: (d) => {
        const id = this.featureId(d.properties);
        const score = this.scoreForId(id);
        if (score === null) return '#cbbfa2';
        return CityMapUtils.colorForScore(score, city);
      },
      strokeWidth: (d) => (state.selectedRegion === this.featureId(d.properties) ? 2.2 : 0.85),
      onClick: this.layer === 'index'
        ? (d) => {
            const id = this.featureId(d.properties);
            state.selectedRegion = id;
            selectRegion(id);
            this.render();
          }
        : null,
      labels: this.layer === 'index',
      labelText: (d) => {
        const id = this.featureId(d.properties);
        return city === 'paris' ? String(id) : String(id);
      },
      labelFill: (d) => {
        const score = this.scoreForId(this.featureId(d.properties));
        return score !== null && score > 55 ? '#f1e9d6' : '#2a2218';
      },
    });

    this.projection = projection;
    this.path = path;

    const gMon = svg.append('g').attr('class', 'geo-monuments');
    const mons = this.monuments[city];
    gMon.selectAll('circle')
      .data(mons)
      .join('circle')
      .attr('cx', (d) => projection([d.lon, d.lat])[0])
      .attr('cy', (d) => projection([d.lon, d.lat])[1])
      .attr('r', (d) => (this.selectedMonument === d.id ? 8 : 5.5))
      .attr('fill', city === 'paris' ? '#7a1f2b' : '#2d5a3d')
      .attr('stroke', '#f1e9d6')
      .attr('stroke-width', 1.8)
      .attr('opacity', this.layer === 'monuments' ? 1 : 0.4)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        this.selectedMonument = d.id;
        this.render();
        this.renderMonumentDetail(d);
      });
  },

  renderMonumentDetail(mon) {
    const panel = document.getElementById('monument-detail');
    if (!panel) return;
    if (!mon) {
      panel.innerHTML = '<p class="monument-placeholder">Select a pin on the map to compare the monument <strong>then</strong> and <strong>now</strong>, with planning context.</p>';
      return;
    }
    panel.innerHTML = `
      <header class="monument-detail-head">
        <h3>${mon.name}</h3>
        <p class="monument-meta">${mon.year} · ${mon.planner}</p>
      </header>
      <div class="monument-then-now">
        <figure>
          <img src="${mon.imageThen}" alt="${mon.name} historical view" loading="lazy" />
          <figcaption><span class="tag">Then</span> ${mon.thenCaption}<br><small>${mon.creditThen}</small></figcaption>
        </figure>
        <figure>
          <img src="${mon.imageNow}" alt="${mon.name} today" loading="lazy" />
          <figcaption><span class="tag now">Now</span> ${mon.nowCaption}<br><small>${mon.creditNow}</small></figcaption>
        </figure>
      </div>
      <div class="monument-prose">
        <p>${mon.summary}</p>
        <p><strong>Planning role:</strong> ${mon.planningRole}</p>
        <p><strong>Inequality angle:</strong> ${mon.inequalityAngle}</p>
      </div>
    `;
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  },
};

function renderMap() {
  if (GeoMap.ready) {
    GeoMap.render();
    return;
  }
  const regions = document.getElementById('map-regions');
  const labels = document.getElementById('map-labels');
  if (!regions || !labels) return;
  regions.innerHTML = '';
  labels.innerHTML = '';
  const cityData = DATA[state.city];
  const layout = LAYOUTS[state.city];
  cityData.forEach((region) => {
    const pos = layout.find((l) => l.id === region.id);
    if (!pos) return;
    const score = regionIndex(region, state.active);
    const fill = score === null ? '#cbbfa2' : colorFor(score, state.city);
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', pos.cx);
    circle.setAttribute('cy', pos.cy);
    circle.setAttribute('r', pos.r);
    circle.setAttribute('fill', fill);
    circle.classList.add('map-region');
    circle.dataset.id = region.id;
    if (state.selectedRegion === region.id) circle.classList.add('selected');
    circle.addEventListener('click', () => selectRegion(region.id));
    regions.appendChild(circle);
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', pos.cx);
    text.setAttribute('y', pos.cy + 4);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-family', 'Special Elite, monospace');
    text.setAttribute('font-size', '11');
    text.setAttribute('fill', score !== null && score > 60 ? '#f1e9d6' : '#2a2218');
    text.setAttribute('pointer-events', 'none');
    text.textContent = state.city === 'paris' ? region.id : region.name.split(' ').map((w) => w[0]).join('').slice(0, 3);
    labels.appendChild(text);
  });
}
