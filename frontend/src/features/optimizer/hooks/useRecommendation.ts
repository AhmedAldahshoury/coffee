import { useMutation } from '@tanstack/react-query';
import { fetchRecommendation } from '../api/optimizerApi';

export function useRecommendation() {
  return useMutation({
    mutationFn: fetchRecommendation,
  });
}
