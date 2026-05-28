/**
 * GeoJSON choropleth maps + monument then/now explorer.
 * Expects global: DATA, state, COMPONENTS, regionIndex, colorFor, selectRegion
 */
const GeoMap = {
  geo: { paris: null, mexico: null },
  monuments: { paris: [], mexico: [] },
  ready: false,
  layer: 'index',
  selectedMonument: null,
  projection: null,
  path: null,
  width: 720,
  height: 560,

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

  render() {
    if (!this.ready || typeof d3 === 'undefined') return;

    const city = state.city;
    const geojson = this.geo[city];
    const svg = d3.select('#map-svg');
    svg.selectAll('*').remove();
    svg.attr('viewBox', `0 0 ${this.width} ${this.height}`);

    const pad = 28;
    this.projection = d3.geoMercator().fitExtent(
      [[pad, pad], [this.width - pad, this.height - pad]],
      geojson
    );
    this.path = d3.geoPath().projection(this.projection);

    const gBase = svg.append('g').attr('class', 'geo-base');
    const gRegions = svg.append('g').attr('class', 'geo-regions');
    const gLabels = svg.append('g').attr('class', 'geo-labels');
    const gMon = svg.append('g').attr('class', 'geo-monuments');

    gBase.append('path')
      .datum({ type: 'Sphere' })
      .attr('d', d3.geoPath().projection(this.projection))
      .attr('fill', 'rgba(212,195,145,0.15)')
      .attr('stroke', 'none');

    const features = geojson.features;
    gRegions.selectAll('path')
      .data(features)
      .join('path')
      .attr('d', this.path)
      .attr('fill', (d) => {
        const id = this.featureId(d.properties);
        const score = this.scoreForId(id);
        return score === null ? '#cbbfa2' : colorFor(score, city);
      })
      .attr('stroke', '#2a2218')
      .attr('stroke-width', (d) => (state.selectedRegion === this.featureId(d.properties) ? 2.5 : 0.9))
      .attr('opacity', () => (this.layer === 'monuments' ? 0.55 : 1))
      .attr('class', 'map-region-geo')
      .style('cursor', this.layer === 'index' ? 'pointer' : 'default')
      .on('click', (event, d) => {
        if (this.layer !== 'index') return;
        const id = this.featureId(d.properties);
        state.selectedRegion = id;
        selectRegion(id);
        this.render();
      });

    if (this.layer === 'index') {
      gLabels.selectAll('text')
        .data(features)
        .join('text')
        .attr('transform', (d) => {
          const c = this.path.centroid(d);
          return `translate(${c[0]},${c[1]})`;
        })
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('font-family', 'Special Elite, monospace')
        .attr('font-size', city === 'paris' ? 10 : 8)
        .attr('fill', (d) => {
          const score = this.scoreForId(this.featureId(d.properties));
          return score !== null && score > 55 ? '#f1e9d6' : '#2a2218';
        })
        .attr('pointer-events', 'none')
        .text((d) => {
          const id = this.featureId(d.properties);
          return city === 'paris' ? id : id;
        });
    }

    const mons = this.monuments[city];
    gMon.selectAll('circle')
      .data(mons)
      .join('circle')
      .attr('cx', (d) => this.projection([d.lon, d.lat])[0])
      .attr('cy', (d) => this.projection([d.lon, d.lat])[1])
      .attr('r', (d) => (this.selectedMonument === d.id ? 9 : 6))
      .attr('fill', city === 'paris' ? '#7a1f2b' : '#2d5a3d')
      .attr('stroke', '#f1e9d6')
      .attr('stroke-width', 2)
      .attr('opacity', this.layer === 'monuments' ? 1 : 0.35)
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
