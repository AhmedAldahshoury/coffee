import { LoadedDataset, OptimizerState, ScoringMethod } from './types';
import { getScore } from './scoring';

export const correlation = (x: number[], y: number[]): number => {
  const n = x.length;
  if (!n) return 0;
  const mx = x.reduce((a, b) => a + b, 0) / n;
  const my = y.reduce((a, b) => a + b, 0) / n;
  let num = 0; let dx = 0; let dy = 0;
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

export const getState = (loaded: LoadedDataset, method: ScoringMethod, selectedPersons: string[]): OptimizerState => {
  const scoreKeys = selectedPersons.length ? selectedPersons : loaded.personNames;
  const parameterKeys = loaded.parameterKeys;

  const fixedRows = loaded.dataRows.filter((r) => !parameterKeys.every((k) => r[k] !== null && r[k] !== '' && r[k] !== undefined));
  const fixedParameters = fixedRows.length
    ? Object.fromEntries(Object.entries(fixedRows[0]).filter(([k, v]) => parameterKeys.includes(k) && v !== null && v !== ''))
    : {};

  const historical = loaded.dataRows
    .filter((r) => parameterKeys.every((k) => r[k] !== null && r[k] !== '' && r[k] !== undefined))
    .map((r, idx) => ({ ...r, _index: idx, objective: getScore(r, scoreKeys, method) }))
    .filter((r): r is OptimizerState['historical'][number] => r.objective !== null)
    .sort((a, b) => b.objective - a.objective);

  return { method, selectedPersons, scoreKeys, parameterKeys, historical, fixedParameters };
};

export const recommendationFromHistorical = (
  loaded: LoadedDataset,
  historical: OptimizerState['historical'],
  fixedParameters: Record<string, string | number>,
  weight: number,
  best: boolean,
): Record<string, string | number> => {
  if (!historical.length) return {};
  if (best) return { ...historical[0] };

  const eliteCount = Math.max(3, Math.floor(historical.length * 0.25));
  const elite = historical.slice(0, eliteCount);
  const next: Record<string, string | number> = {};

  for (const meta of loaded.parameterMeta) {
    const key = meta.name;
    if (key in fixedParameters) continue;
    const values = elite.map((x) => x[key]).filter((x) => x !== null && x !== undefined && x !== '');
    if (!values.length) continue;

    if (meta['parameter type'] === 'category') {
      const counts = values.reduce<Record<string, number>>((acc, v) => ({ ...acc, [String(v)]: (acc[String(v)] || 0) + 1 }), {});
      next[key] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    } else {
      const avg = values.reduce((a, b) => a + Number(b), 0) / values.length;
      const bestValue = Number(historical[0][key]);
      let value = weight * avg + (1 - weight) * bestValue;
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
