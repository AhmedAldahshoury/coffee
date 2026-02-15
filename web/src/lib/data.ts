import { DataRow, DatasetKey, LoadedDataset, MetaRow } from './types';

const FILES: Record<DatasetKey, { data: string; meta: string }> = {
  'aeropress.': { data: '/data/aeropress.data.csv', meta: '/data/aeropress.meta.csv' },
  'pourover.': { data: '/data/pourover.data.csv', meta: '/data/pourover.meta.csv' },
};

const numberOrString = (input: string): string | number | null => {
  const v = input.trim();
  if (!v) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : v;
};

export const parseCsv = async (path: string): Promise<DataRow[]> => {
  const text = await fetch(path).then((r) => {
    if (!r.ok) throw new Error(`Could not load ${path}`);
    return r.text();
  });
  const [header, ...lines] = text.split(/\r?\n/).filter(Boolean);
  const headers = header.split(',').map((h) => h.trim());
  return lines.map((line) => {
    const cols = line.split(',');
    return Object.fromEntries(headers.map((h, i) => [h, numberOrString(cols[i] ?? '')]));
  });
};

export const loadData = async (dataset: DatasetKey): Promise<LoadedDataset> => {
  const { data, meta } = FILES[dataset];
  const [dataRows, metaRowsRaw] = await Promise.all([parseCsv(data), parseCsv(meta)]);
  const metaRows = metaRowsRaw as MetaRow[];
  const parameterMeta = metaRows.filter((r) => r.type === 'parameter');
  const scoreMeta = metaRows.filter((r) => r.type === 'score');

  return {
    dataset,
    dataRows,
    metaRows,
    parameterMeta,
    scoreMeta,
    parameterKeys: parameterMeta.map((x) => x.name),
    personNames: scoreMeta.map((x) => x.name),
  };
};
