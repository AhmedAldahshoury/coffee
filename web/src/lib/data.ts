import { CsvRow, DataCell, DataRow, DatasetKey, LoadedDataset, MetaRow } from './types';

const FILES: Record<DatasetKey, { data: string; meta: string }> = {
  'aeropress.': { data: 'data/aeropress.data.csv', meta: 'data/aeropress.meta.csv' },
  'pourover.': { data: 'data/pourover.data.csv', meta: 'data/pourover.meta.csv' },
};

export const resolveCsvUrl = (relativePath: string): string => new URL(relativePath, import.meta.env.BASE_URL).toString();

const numberOrString = (input: string): DataCell => {
  const v = input.trim();
  if (!v) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : v;
};

export const parseCsv = async <T extends CsvRow>(path: string): Promise<T[]> => {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`Could not load ${path} (HTTP ${response.status})`);
  }

  const text = await response.text();
  console.info('[csv] raw text', { path, status: response.status, preview: text.slice(0, 400) });

  const [header, ...lines] = text.split(/\r?\n/).filter(Boolean);
  const headers = header.split(',').map((h) => h.trim());

  const parsed = lines.map((line) => {
    const cols = line.split(',');
    const row = Object.fromEntries(headers.map((h, i) => [h, numberOrString(cols[i] ?? '')]));
    return row as T;
  });

  console.info('[csv] parsed rows', {
    path,
    rowCount: parsed.length,
    firstRows: parsed.slice(0, 2),
  });

  return parsed;
};

export const loadData = async (dataset: DatasetKey): Promise<LoadedDataset> => {
  const { data, meta } = FILES[dataset];
  const dataUrl = resolveCsvUrl(data);
  const metaUrl = resolveCsvUrl(meta);

  console.info('[csv] loading dataset files', { dataset, dataUrl, metaUrl });

  const [dataRows, metaRows] = await Promise.all([parseCsv<DataRow>(dataUrl), parseCsv<MetaRow>(metaUrl)]);
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
