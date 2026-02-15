import { DataRow, ScoringMethod } from './types';

export const median = (vals: number[]): number => {
  const sorted = vals.slice().sort((a, b) => a - b);
  const m = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2;
};

export const getScore = (row: DataRow, scoreKeys: string[], method: ScoringMethod): number | null => {
  const vals = scoreKeys.map((k) => row[k]).filter((v): v is number => typeof v === 'number' && !Number.isNaN(v));
  if (!vals.length) return null;
  if (method === 'mean') return vals.reduce((a, b) => a + b, 0) / vals.length;
  if (method === 'highest') return Math.max(...vals);
  if (method === 'lowest') return Math.min(...vals);
  return median(vals);
};
