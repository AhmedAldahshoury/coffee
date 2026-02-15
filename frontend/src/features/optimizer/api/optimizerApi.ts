import { httpClient } from '../../../shared/api/httpClient';

export async function fetchRecommendation(payload: any) {
  const { data } = await httpClient.post('/optimizer/recommendation', payload);
  return data;
}

export async function startRun(payload: { selected_persons: string[]; method: string; n_trials: number }) {
  const { data } = await httpClient.post('/optimizer/runs/start', payload);
  return data;
}

export async function submitScore(runId: string, trialId: number, score: number) {
  const { data } = await httpClient.post(`/optimizer/runs/${runId}/submit_score`, { trial_id: trialId, score });
  return data;
}

export function createRunEvents(runId: string, token: string) {
  const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';
  return new EventSource(`${base}/optimizer/runs/${runId}/events?token=${token}`);
}
