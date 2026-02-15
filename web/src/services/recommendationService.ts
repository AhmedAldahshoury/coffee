import { getState, recommendationFromHistorical } from '@/lib/optimizer';
import { LoadedDataset } from '@/lib/types';
import { OptimizerPreferences, RecommendationResponse, ServiceResult } from './types';

const isValidWeight = (weight: number) => Number.isFinite(weight) && weight >= 0 && weight <= 1;

export const recommendationService = {
  generate: (
    loaded: LoadedDataset,
    preferences: OptimizerPreferences,
  ): ServiceResult<RecommendationResponse> => {
    if (!isValidWeight(preferences.weight)) {
      return { ok: false, message: 'Elite averaging weight must be between 0 and 1.' };
    }

    const unknownPerson = preferences.selectedPersons.find((person) => !loaded.personNames.includes(person));
    if (unknownPerson) {
      return { ok: false, message: `Unknown person selection: ${unknownPerson}.` };
    }

    const state = getState(loaded, preferences.method, preferences.selectedPersons);
    const recommendation = recommendationFromHistorical(
      loaded,
      state.historical,
      state.fixedParameters,
      preferences.weight,
      preferences.best,
    );

    return { ok: true, data: { state, recommendation } };
  },
};
