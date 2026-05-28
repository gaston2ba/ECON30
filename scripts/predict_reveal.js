async function initPredictReveal() {
  const svg = document.getElementById('predict-svg');
  const btn = document.getElementById('predict-reveal-btn');
  const scoreText = document.getElementById('predict-score-text');
  if (!svg || !btn || !scoreText) return;
  try {
    const data = await fetch('data/uqi_regression_results.json').then(r => r.json());
    const pts = (data.paris?.points || []).map(p => ({ ...p }));
    if (!pts.length) return;
    const w = 760, h = 330, m = { l: 52, r: 18, t: 20, b: 42 };
    const xMin = Math.min(...pts.map(p => p.uqi)), xMax = Math.max(...pts.map(p => p.uqi));
    const yMin = Math.min(...pts.map(p => p.log_outcome)), yMax = Math.max(...pts.map(p => p.log_outcome));
    const x = v => m.l + ((v - xMin) / (xMax - xMin)) * (w - m.l - m.r);
    const y = v => h - m.b - ((v - yMin) / (yMax - yMin)) * (h - m.t - m.b);
    const yRand = pts.map((_, i) => m.t + 22 + (i * (h - m.t - m.b - 44) / Math.max(1, pts.length - 1)));
    pts.forEach((p, i) => { p._x = x(p.uqi); p._y0 = yRand[i]; p._y1 = y(p.log_outcome); p._cy = p._y0; });

    const NS = 'http://www.w3.org/2000/svg';
    svg.innerHTML = '';
    const axisX = document.createElementNS(NS, 'line');
    axisX.setAttribute('x1', m.l); axisX.setAttribute('x2', w - m.r); axisX.setAttribute('y1', h - m.b); axisX.setAttribute('y2', h - m.b); axisX.setAttribute('stroke', '#6b5d48');
    svg.appendChild(axisX);
    const axisY = document.createElementNS(NS, 'line');
    axisY.setAttribute('x1', m.l); axisY.setAttribute('x2', m.l); axisY.setAttribute('y1', m.t); axisY.setAttribute('y2', h - m.b); axisY.setAttribute('stroke', '#6b5d48');
    svg.appendChild(axisY);
    const xlabel = document.createElementNS(NS, 'text');
    xlabel.setAttribute('x', w / 2); xlabel.setAttribute('y', h - 12); xlabel.setAttribute('text-anchor', 'middle'); xlabel.setAttribute('font-size', '11'); xlabel.setAttribute('fill', '#4a3f30');
    xlabel.textContent = 'UQI score';
    svg.appendChild(xlabel);
    const ylabel = document.createElementNS(NS, 'text');
    ylabel.setAttribute('x', 14); ylabel.setAttribute('y', h / 2); ylabel.setAttribute('transform', `rotate(-90 14 ${h / 2})`); ylabel.setAttribute('font-size', '11'); ylabel.setAttribute('fill', '#4a3f30');
    ylabel.textContent = '(hidden until reveal)';
    svg.appendChild(ylabel);

    const circles = [];
    const labels = [];
    pts.forEach(p => {
      const c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', p._x); c.setAttribute('cy', p._cy); c.setAttribute('r', 6); c.setAttribute('fill', '#7a1f2b'); c.setAttribute('opacity', '0.82');
      const t = document.createElementNS(NS, 'text');
      t.setAttribute('x', p._x + 7); t.setAttribute('y', p._cy - 8); t.setAttribute('font-size', '9'); t.setAttribute('fill', '#2a2218');
      t.style.display = 'none'; t.textContent = p.name;
      svg.appendChild(c); svg.appendChild(t);
      circles.push(c); labels.push(t);
    });

    btn.addEventListener('click', () => {
      let step = 0; const steps = 40;
      const timer = setInterval(() => {
        step += 1;
        const t = Math.min(1, step / steps);
        pts.forEach((p, i) => {
          p._cy = p._y0 + (p._y1 - p._y0) * t;
          circles[i].setAttribute('cy', p._cy);
          labels[i].setAttribute('y', p._cy - 8);
        });
        if (t >= 1) {
          clearInterval(timer);
          ylabel.textContent = 'log(median income)';
          labels.forEach(l => l.style.display = 'block');
          const top3 = pts.slice().sort((a, b) => b.log_outcome - a.log_outcome).slice(0, 3).map(p => p.name);
          pts.forEach((p, i) => {
            if (top3.includes(p.name)) {
              circles[i].setAttribute('fill', '#2d5a3d');
              circles[i].setAttribute('r', '7');
            }
          });
          const corr = data.paris?.controlled?.beta ?? 0;
          scoreText.innerHTML = `Revealed: the highest-income arrondissements are shown in green. Controlled Paris coefficient is β ≈ ${corr.toFixed(3)} — weaker than most readers expect.`;
          btn.disabled = true;
        }
      }, 22);
    }, { once: true });
  } catch (err) {
    scoreText.textContent = 'Could not load reveal data.';
  }
}
