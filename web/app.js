const els = {
  dataset: document.getElementById('datasetSelect'),
  method: document.getElementById('methodSelect'),
  weight: document.getElementById('weightInput'),
  weightLabel: document.getElementById('weightLabel'),
  best: document.getElementById('bestToggle'),
  persons: document.getElementById('personsContainer'),
  selectAllPersons: document.getElementById('selectAllPersons'),
  clearPersons: document.getElementById('clearPersons'),
  run: document.getElementById('runButton'),
  summary: document.getElementById('summary'),
  recommendation: document.getElementById('recommendation'),
  fixed: document.getElementById('fixedParams'),
  topTrials: document.getElementById('topTrials'),
  charts: document.getElementById('charts'),
  activeDataset: document.getElementById('activeDataset'),
  activePersons: document.getElementById('activePersons'),
  activeHistory: document.getElementById('activeHistory'),
  presetBalanced: document.getElementById('presetBalanced'),
  presetAggressive: document.getElementById('presetAggressive'),
};

const vizIds = ['vizTime', 'vizRelations', 'vizEdf', 'vizImportance', 'vizSlice', 'vizScores'];
let loaded = null;
let resizeTimer = null;

const parseCsv = async (path) => {
  const text = await fetch(path).then((r) => {
    if (!r.ok) throw new Error(`Could not load ${path}`);
    return r.text();
  });
  return Papa.parse(text, { header: true, dynamicTyping: true, skipEmptyLines: true }).data;
};

const median = (vals) => {
  const sorted = vals.slice().sort((a, b) => a - b);
  const m = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2;
};

const getScore = (row, scoreKeys, method) => {
  const vals = scoreKeys.map((k) => row[k]).filter((v) => typeof v === 'number' && !Number.isNaN(v));
  if (!vals.length) return null;
  if (method === 'mean') return vals.reduce((a, b) => a + b, 0) / vals.length;
  if (method === 'highest') return Math.max(...vals);
  if (method === 'lowest') return Math.min(...vals);
  return median(vals);
};

const getSelectedPersons = () => Array.from(document.querySelectorAll('[data-person]:checked')).map((x) => x.value);

const renderPersons = (names) => {
  els.persons.innerHTML = names
    .map((name) => `<label class="chip"><input type="checkbox" data-person value="${name}" checked /> ${name}</label>`)
    .join('');
};

const loadData = async () => {
  const prefix = els.dataset.value;
  const [dataRows, metaRows] = await Promise.all([
    parseCsv(`./data/${prefix}data.csv`),
    parseCsv(`./data/${prefix}meta.csv`),
  ]);

  const parameterMeta = metaRows.filter((r) => r.type === 'parameter');
  const scoreMeta = metaRows.filter((r) => r.type === 'score');
  loaded = {
    dataset: prefix,
    dataRows,
    metaRows,
    parameterMeta,
    scoreMeta,
    parameterKeys: parameterMeta.map((x) => x.name),
    personNames: scoreMeta.map((x) => x.name),
  };

  renderPersons(loaded.personNames);
};

const correlation = (x, y) => {
  const n = x.length;
  if (!n) return 0;
  const mx = x.reduce((a, b) => a + b, 0) / n;
  const my = y.reduce((a, b) => a + b, 0) / n;
  let num = 0;
  let dx = 0;
  let dy = 0;
  for (let i = 0; i < n; i += 1) {
    const vx = x[i] - mx;
    const vy = y[i] - my;
    num += vx * vy;
    dx += vx * vx;
    dy += vy * vy;
  }
  if (!dx || !dy) return 0;
  return num / Math.sqrt(dx * dy);
};

const getState = () => {
  const method = els.method.value;
  const selectedPersons = getSelectedPersons();
  const scoreKeys = selectedPersons.length ? selectedPersons : loaded.personNames;
  const parameterKeys = loaded.parameterKeys;

  const fixedRows = loaded.dataRows.filter((r) => !parameterKeys.every((k) => r[k] !== null && r[k] !== '' && r[k] !== undefined));
  const fixedParameters = fixedRows.length
    ? Object.fromEntries(Object.entries(fixedRows[0]).filter(([k, v]) => parameterKeys.includes(k) && v !== null && v !== ''))
    : {};

  const historical = loaded.dataRows
    .filter((r) => parameterKeys.every((k) => r[k] !== null && r[k] !== '' && r[k] !== undefined))
    .map((r, idx) => ({ ...r, _index: idx, objective: getScore(r, scoreKeys, method) }))
    .filter((r) => r.objective !== null)
    .sort((a, b) => b.objective - a.objective);

  return { method, selectedPersons, scoreKeys, parameterKeys, historical, fixedParameters };
};

const recommendationFromHistorical = (historical, fixedParameters) => {
  if (!historical.length) return {};
  if (els.best.checked) return { ...historical[0] };

  const eliteCount = Math.max(3, Math.floor(historical.length * 0.25));
  const elite = historical.slice(0, eliteCount);
  const next = {};

  for (const meta of loaded.parameterMeta) {
    const key = meta.name;
    if (key in fixedParameters) continue;
    const values = elite.map((x) => x[key]).filter((x) => x !== null && x !== undefined && x !== '');
    if (!values.length) continue;

    if (meta['parameter type'] === 'category') {
      const counts = values.reduce((acc, v) => ({ ...acc, [v]: (acc[v] || 0) + 1 }), {});
      next[key] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    } else {
      const avg = values.reduce((a, b) => a + Number(b), 0) / values.length;
      const best = Number(historical[0][key]);
      const weight = Number(els.weight.value);
      let value = weight * avg + (1 - weight) * best;
      const low = Number(meta.low);
      const high = Number(meta.high);
      const step = Number(meta.step || 1);
      value = Math.max(low, Math.min(high, value));
      value = Math.round((value - low) / step) * step + low;
      next[key] = meta['parameter type'] === 'int' ? Math.round(value) : Number(value.toFixed(2));
    }
  }

  return next;
};

const mobileParamColumns = () => (window.innerWidth <= 560 ? 2 : 5);

const drawCharts = (state) => {
  els.charts.innerHTML = '';
  const on = (id) => document.getElementById(id).checked;
  const { historical } = state;
  if (!historical.length) return;

  const addChart = (title) => {
    const d = document.createElement('div');
    d.className = 'chart';
    els.charts.appendChild(d);
    return { div: d, title };
  };

  if (on('vizTime')) {
    const sortedByTime = historical.slice().sort((a, b) => a._index - b._index);
    let running = -Infinity;
    const bestLine = sortedByTime.map((r) => {
      running = Math.max(running, r.objective);
      return running;
    });
    const c = addChart('Optimization History');
    Plotly.newPlot(c.div, [{ x: sortedByTime.map((_, i) => i + 1), y: bestLine, mode: 'lines+markers', name: 'Best so far' }], { title: c.title, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
  }

  if (on('vizEdf')) {
    const vals = historical.map((r) => r.objective).sort((a, b) => a - b);
    const y = vals.map((_, i) => (i + 1) / vals.length);
    const c = addChart('Empirical Distribution Function');
    Plotly.newPlot(c.div, [{ x: vals, y, mode: 'lines', name: 'EDF' }], { title: c.title, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
  }

  if (on('vizImportance')) {
    const labels = [];
    const values = [];
    for (const meta of loaded.parameterMeta) {
      const key = meta.name;
      if (meta['parameter type'] === 'category') continue;
      const x = historical.map((r) => Number(r[key]));
      const y = historical.map((r) => Number(r.objective));
      labels.push(key);
      values.push(Math.abs(correlation(x, y)));
    }
    const c = addChart('Parameter Importance (|correlation| approximation)');
    Plotly.newPlot(c.div, [{ x: labels, y: values, type: 'bar' }], { title: c.title, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
  }

  if (on('vizSlice')) {
    for (const meta of loaded.parameterMeta) {
      if (meta['parameter type'] === 'category') continue;
      const key = meta.name;
      const c = addChart(`Slice: ${key} vs objective`);
      Plotly.newPlot(c.div, [{ x: historical.map((r) => Number(r[key])), y: historical.map((r) => r.objective), mode: 'markers', type: 'scatter' }], { title: c.title, xaxis: { title: key }, yaxis: { title: 'objective' }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
    }
  }

  if (on('vizRelations')) {
    const numeric = loaded.parameterMeta.filter((m) => m['parameter type'] !== 'category').slice(0, 4).map((m) => m.name);
    if (numeric.length >= 2) {
      const c = addChart('Relations (first numeric params)');
      Plotly.newPlot(c.div, numeric.map((k) => ({ x: historical.map((r) => Number(r[k])), y: historical.map((r) => r.objective), mode: 'markers', type: 'scatter', name: k })), { title: c.title, xaxis: { title: 'parameter value' }, yaxis: { title: 'objective' }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
    }
  }

  if (on('vizScores')) {
    const boxData = state.scoreKeys.map((k) => ({ y: loaded.dataRows.map((r) => r[k]).filter((v) => typeof v === 'number' && !Number.isNaN(v)), type: 'box', name: k }));
    const c = addChart('Scores distribution per person');
    Plotly.newPlot(c.div, boxData, { title: c.title, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#e9ecf7' } });
  }
};

const updateHeroMetrics = (state) => {
  els.activeDataset.textContent = els.dataset.selectedOptions[0].textContent;
  els.activePersons.textContent = `${state.scoreKeys.length}`;
  els.activeHistory.textContent = `${state.historical.length}`;
};

const render = async () => {
  if (!loaded || loaded.dataset !== els.dataset.value) {
    await loadData();
  }

  const state = getState();
  const next = recommendationFromHistorical(state.historical, state.fixedParameters);

  els.summary.textContent = `Computed from ${state.historical.length} historical brews using ${state.method} scoring and ${state.scoreKeys.length} selected person(s).`;

  els.fixed.innerHTML = Object.entries(state.fixedParameters)
    .map(([k, v]) => `<article class="card fixed"><div class="title">[FIXED] ${k}</div><div class="value">${v}</div></article>`)
    .join('');

  els.recommendation.innerHTML = loaded.parameterMeta
    .map((m) => {
      const val = m.name in state.fixedParameters ? state.fixedParameters[m.name] : next[m.name];
      return `<article class="card"><div class="title">${m.name}</div><div class="value">${val ?? '—'} ${m.unit || ''}</div></article>`;
    })
    .join('');

  const visibleColumns = state.parameterKeys.slice(0, mobileParamColumns());
  const topRows = state.historical.slice(0, 8).map((row, idx) => {
    const cells = visibleColumns.map((k) => `<td>${row[k]}</td>`).join('');
    return `<tr><td>#${idx + 1}</td><td>${row.objective.toFixed(2)}</td>${cells}</tr>`;
  }).join('');
  els.topTrials.innerHTML = `<table><thead><tr><th>Rank</th><th>Score</th>${visibleColumns.map((k) => `<th>${k}</th>`).join('')}</tr></thead><tbody>${topRows}</tbody></table>`;

  updateHeroMetrics(state);
  drawCharts(state);
};

const applyPreset = (type) => {
  if (type === 'balanced') {
    els.method.value = 'median';
    els.weight.value = '0.67';
    els.best.checked = false;
  } else {
    els.method.value = 'highest';
    els.weight.value = '0.35';
    els.best.checked = true;
  }
  els.weightLabel.textContent = Number(els.weight.value).toFixed(2);
  render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; });
};

els.weight.addEventListener('input', () => { els.weightLabel.textContent = Number(els.weight.value).toFixed(2); });
els.dataset.addEventListener('change', async () => { loaded = null; await render(); });
els.run.addEventListener('click', () => render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; }));
els.selectAllPersons.addEventListener('click', () => {
  document.querySelectorAll('[data-person]').forEach((x) => {
    x.checked = true;
  });
  render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; });
});
els.clearPersons.addEventListener('click', () => {
  document.querySelectorAll('[data-person]').forEach((x) => {
    x.checked = false;
  });
  render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; });
});
els.presetBalanced.addEventListener('click', () => applyPreset('balanced'));
els.presetAggressive.addEventListener('click', () => applyPreset('aggressive'));
vizIds.forEach((id) => document.getElementById(id).addEventListener('change', () => render()));

window.addEventListener('resize', () => {
  if (resizeTimer) clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; });
  }, 150);
});

render().catch((e) => { els.summary.textContent = `Error: ${e.message}`; });
