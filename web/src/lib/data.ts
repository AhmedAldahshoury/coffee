import { DataCell, DataRow, DatasetKey, LoadedDataset, MetaRow } from './types';

const FILES: Record<DatasetKey, { data: string; meta: string }> = {
  'aeropress.': { data: '/data/aeropress.data.csv', meta: '/data/aeropress.meta.csv' },
  'pourover.': { data: '/data/pourover.data.csv', meta: '/data/pourover.meta.csv' },
};

const numberOrString = (input: string): DataCell => {
  const v = input.trim();
  if (!v) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : v;
};

export const parseCsv = async <T extends Record<string, DataCell>>(path: string): Promise<T[]> => {
  const text = await fetch(path).then((r) => {
    if (!r.ok) throw new Error(`Could not load ${path}`);
    return r.text();
  });
  const [header, ...lines] = text.split(/\r?\n/).filter(Boolean);
  const headers = header.split(',').map((h) => h.trim());

  return lines.map((line) => {
    const cols = line.split(',');
    const row = Object.fromEntries(headers.map((h, i) => [h, numberOrString(cols[i] ?? '')]));
    return row as T;
  });
};

export const loadData = async (dataset: DatasetKey): Promise<LoadedDataset> => {
  const { data, meta } = FILES[dataset];
  const [dataRows, metaRows] = await Promise.all([parseCsv<DataRow>(data), parseCsv<MetaRow>(meta)]);
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
