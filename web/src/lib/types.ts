export type DatasetKey = 'aeropress.' | 'pourover.';

export type ParameterType = 'int' | 'float' | 'category';

export type DataCell = string | number | null;

export type CsvRow = Record<string, DataCell>;

export type MetaRow = CsvRow & {
  type: 'parameter' | 'score';
  name: string;
  unit?: string;
  low?: number;
  high?: number;
  step?: number;
  'parameter type'?: ParameterType;
};

export type DataRow = CsvRow;

export interface LoadedDataset {
  dataset: DatasetKey;
  dataRows: DataRow[];
  metaRows: MetaRow[];
  parameterMeta: MetaRow[];
  scoreMeta: MetaRow[];
  parameterKeys: string[];
  personNames: string[];
}

export type ScoringMethod = 'median' | 'mean' | 'highest' | 'lowest';

export type ChartToggles = {
  history: boolean;
  importance: boolean;
  scores: boolean;
  edf: boolean;
  slice: boolean;
};

export type HistoricalRow = DataRow & {
  _index: number;
  objective: number;
};

export interface OptimizerState {
  method: ScoringMethod;
  selectedPersons: string[];
  scoreKeys: string[];
  parameterKeys: string[];
  historical: HistoricalRow[];
  fixedParameters: Record<string, string | number>;
}
