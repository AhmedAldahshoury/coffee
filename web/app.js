const recommendationEl = document.getElementById("recommendation");
const topTrialsEl = document.getElementById("topTrials");
const summaryEl = document.getElementById("summary");
const weightInput = document.getElementById("weightInput");
const weightLabel = document.getElementById("weightLabel");

weightInput.addEventListener("input", () => {
  weightLabel.textContent = Number(weightInput.value).toFixed(2);
});

const parseCsv = async (path) => {
  const text = await fetch(path).then((r) => r.text());
  return Papa.parse(text, { header: true, dynamicTyping: true, skipEmptyLines: true }).data;
};

const getScore = (row, scoreKeys, method) => {
  const vals = scoreKeys.map((k) => row[k]).filter((v) => typeof v === "number" && !Number.isNaN(v));
  if (!vals.length) return null;
  if (method === "mean") return vals.reduce((a, b) => a + b, 0) / vals.length;
  if (method === "highest") return Math.max(...vals);
  if (method === "lowest") return Math.min(...vals);
  const sorted = vals.slice().sort((a, b) => a - b);
  const m = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2;
};

const recommend = async () => {
  const prefix = document.getElementById("datasetSelect").value;
  const method = document.getElementById("methodSelect").value;
  const weight = Number(weightInput.value);

  const [dataRows, metaRows] = await Promise.all([
    parseCsv(`./data/${prefix}data.csv`),
    parseCsv(`./data/${prefix}meta.csv`),
  ]);

  const parameterMeta = metaRows.filter((r) => r.type === "parameter");
  const scoreMeta = metaRows.filter((r) => r.type === "score");
  const parameterKeys = parameterMeta.map((r) => r.name);
  const scoreKeys = scoreMeta.map((r) => r.name);

  const historical = dataRows
    .filter((row) => parameterKeys.every((k) => row[k] !== null && row[k] !== "" && row[k] !== undefined))
    .map((row) => ({ ...row, objective: getScore(row, scoreKeys, method) }))
    .filter((row) => row.objective !== null)
    .sort((a, b) => b.objective - a.objective);

  const eliteCount = Math.max(3, Math.floor(historical.length * 0.25));
  const elite = historical.slice(0, eliteCount);

  const next = {};
  for (const meta of parameterMeta) {
    const key = meta.name;
    const values = elite.map((x) => x[key]).filter((x) => x !== null && x !== undefined && x !== "");
    if (!values.length) continue;

    if (meta["parameter type"] === "category") {
      const counts = values.reduce((acc, v) => ({ ...acc, [v]: (acc[v] || 0) + 1 }), {});
      next[key] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    } else {
      const avg = values.reduce((a, b) => a + Number(b), 0) / values.length;
      const best = Number(historical[0][key]);
      let value = weight * avg + (1 - weight) * best;

      const step = Number(meta.step || 1);
      const low = Number(meta.low);
      const high = Number(meta.high);
      value = Math.max(low, Math.min(high, value));
      value = Math.round((value - low) / step) * step + low;
      next[key] = meta["parameter type"] === "int" ? Math.round(value) : Number(value.toFixed(2));
    }
  }

  summaryEl.textContent = `Computed from ${historical.length} historical brews using ${method} scoring.`;
  recommendationEl.innerHTML = parameterMeta
    .map((m) => `<article class="card"><div class="title">${m.name}</div><div class="value">${next[m.name]} ${m.unit || ""}</div></article>`)
    .join("");

  const topRows = historical.slice(0, 5).map((row, idx) => {
    const cells = parameterKeys.slice(0, 4).map((k) => `<td>${row[k]}</td>`).join("");
    return `<tr><td>#${idx + 1}</td><td>${row.objective.toFixed(2)}</td>${cells}</tr>`;
  });
  topTrialsEl.innerHTML = `
    <table>
      <thead><tr><th>Rank</th><th>Score</th>${parameterKeys.slice(0, 4).map((k) => `<th>${k}</th>`).join("")}</tr></thead>
      <tbody>${topRows.join("")}</tbody>
    </table>
  `;
};

document.getElementById("runButton").addEventListener("click", () => {
  recommend().catch((err) => {
    summaryEl.textContent = `Failed to compute recommendation: ${err.message}`;
  });
});

recommend();
