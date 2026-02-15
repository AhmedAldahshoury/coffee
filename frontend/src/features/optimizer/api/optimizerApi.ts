import { httpClient } from '../../../shared/api/httpClient';
import { OptimizationRequest, OptimizationResponse } from '../types/optimizer';

export async function fetchRecommendation(payload: OptimizationRequest): Promise<OptimizationResponse> {
  const { data } = await httpClient.post<OptimizationResponse>('/optimizer/recommendation', payload);
  return data;
}
