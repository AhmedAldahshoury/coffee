export type DatasetKey = 'aeropress.' | 'pourover.';

export type ParameterType = 'int' | 'float' | 'category';

export interface MetaRow {
  type: 'parameter' | 'score';
  name: string;
  unit?: string;
  low?: number;
  high?: number;
  step?: number;
  'parameter type'?: ParameterType;
}

export type DataCell = string | number | null;

export type DataRow = Record<string, DataCell>;

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

export interface OptimizerState {
  method: ScoringMethod;
  selectedPersons: string[];
  scoreKeys: string[];
  parameterKeys: string[];
  historical: Array<DataRow & { _index: number; objective: number }>;
  fixedParameters: Record<string, string | number>;
}
