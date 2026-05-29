/**
 * Shared D3 choropleth helpers for Paris and CDMX administrative boundaries.
 */
const CityMapUtils = {
  colorscale: [
    '#f6edd8', '#e8d9bc', '#d6c3a0', '#b99b78', '#8a6c4d', '#2a2218',
  ],

  colorForRank(rank, maxRank) {
    const t = (rank - 1) / Math.max(1, maxRank - 1);
    const idx = Math.min(this.colorscale.length - 1, Math.floor(t * (this.colorscale.length - 1)));
    return this.colorscale[idx];
  },

  colorForScore(score, city) {
    const t = Math.max(0, Math.min(100, score)) / 100;
    const idx = Math.min(this.colorscale.length - 1, Math.floor(t * (this.colorscale.length - 1)));
    return this.colorscale[idx];
  },

  renderChoropleth({
    svg,
    geojson,
    width,
    height,
    getFill,
    stroke = '#2a2218',
    strokeWidth = 0.85,
    onClick,
    labels = false,
    labelText,
    labelFill,
    opacity = 1,
  }) {
    const pad = 24;
    const projection = d3.geoMercator().fitExtent(
      [[pad, pad], [width - pad, height - pad]],
      geojson
    );
    const path = d3.geoPath(projection);
    const root = d3.select(svg);
    root.selectAll('*').remove();
    root.attr('viewBox', `0 0 ${width} ${height}`);

    root.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', '#fbf8f1');

    const g = root.append('g').attr('class', 'choropleth-layer');

    g.selectAll('path.region')
      .data(geojson.features)
      .join('path')
      .attr('class', 'region')
      .attr('d', path)
      .attr('fill', (d) => getFill(d))
      .attr('stroke', stroke)
      .attr('stroke-width', typeof strokeWidth === 'function' ? (d) => strokeWidth(d) : strokeWidth)
      .attr('stroke-linejoin', 'round')
      .attr('opacity', opacity)
      .style('cursor', onClick ? 'pointer' : 'default')
      .on('click', (event, d) => onClick && onClick(d));

    if (labels) {
      g.selectAll('text.label')
        .data(geojson.features)
        .join('text')
        .attr('class', 'label')
        .attr('transform', (d) => {
          const c = path.centroid(d);
          return `translate(${c[0]},${c[1]})`;
        })
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('font-family', 'Georgia, serif')
        .attr('font-size', 10)
        .attr('fill', (d) => (labelFill ? labelFill(d) : '#2a2218'))
        .attr('pointer-events', 'none')
        .text((d) => (labelText ? labelText(d) : ''));
    }

    return { projection, path };
  },
};
