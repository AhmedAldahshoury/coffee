import { DatasetKey, LoadedDataset, OptimizerState, ScoringMethod } from '@/lib/types';

export interface DatasetOption {
  key: DatasetKey;
  label: string;
}

export interface OptimizerPreferences {
  method: ScoringMethod;
  weight: number;
  best: boolean;
  selectedPersons: string[];
}

export interface RecommendationResponse {
  state: OptimizerState;
  recommendation: Record<string, string | number>;
}

export interface LogBrewPayload {
  score: number;
  notes?: string;
  dataset: DatasetKey;
}

export interface BrewLogEntry extends LogBrewPayload {
  id: string;
  createdAt: string;
}

export type ServiceResult<T> =
  | { ok: true; data: T }
  | { ok: false; message: string };

export interface DatasetService {
  listDatasets: () => DatasetOption[];
  load: (dataset: DatasetKey) => Promise<ServiceResult<LoadedDataset>>;
}
