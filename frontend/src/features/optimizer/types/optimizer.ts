export interface OptimizationRequest {
  dataset_prefix: string;
  method: 'mean' | 'median' | 'lowest' | 'highest';
  persons?: string[];
  best_only: boolean;
  prior_weight: number;
}

export interface SuggestedParameter {
  name: string;
  value: string | number;
  unit?: string;
  fixed: boolean;
}

export interface OptimizationResponse {
  score: number | null;
  suggested_parameters: SuggestedParameter[];
}
