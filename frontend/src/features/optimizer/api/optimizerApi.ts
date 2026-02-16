import { apiBaseUrl, httpClient } from '../../../shared/api/httpClient';

export interface OptimizerRun {
  id: string;
  status: string;
  best_score: number | null;
  best_params: Record<string, unknown> | null;
  trial_count: number;
  n_trials: number;
  method: string;
  selected_persons: string[];
  latest_trial: {
    id: number;
    trial_number: number;
    parameters: Record<string, unknown>;
    score: number | null;
    state: string;
  } | null;
}

export async function fetchRecommendation(payload: any) {
  const { data } = await httpClient.post('/optimizer/recommendation', payload);
  return data;
}

export async function startRun(payload: { selected_persons: string[]; method: string; n_trials: number }) {
  const { data } = await httpClient.post<OptimizerRun>('/optimizer/runs/start', payload);
  return data;
}

export async function getRun(runId: string) {
  const { data } = await httpClient.get<OptimizerRun>(`/optimizer/runs/${runId}`);
  return data;
}

export async function listRuns() {
  const { data } = await httpClient.get<OptimizerRun[]>('/optimizer/runs');
  return data;
}

export async function submitScore(runId: string, trialId: number, score: number) {
  const { data } = await httpClient.post<OptimizerRun>(`/optimizer/runs/${runId}/submit_score`, { trial_id: trialId, score });
  return data;
}

export function createRunEvents(runId: string, token: string) {
  const encoded = encodeURIComponent(token);
  return new EventSource(`${apiBaseUrl}/optimizer/runs/${runId}/events?token=${encoded}`);
}
