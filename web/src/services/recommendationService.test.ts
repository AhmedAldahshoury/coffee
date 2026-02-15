import { describe, expect, it } from 'vitest';
import { recommendationService } from './recommendationService';
import { LoadedDataset } from '@/lib/types';

const dataset: LoadedDataset = {
  dataset: 'aeropress.',
  dataRows: [
    { grind: 18, temp: 90, nick: 8, tom: 7 },
    { grind: 20, temp: 92, nick: 9, tom: 8 },
    { grind: 16, temp: 88, nick: 6, tom: 7 },
  ],
  metaRows: [
    { type: 'parameter', name: 'grind', 'parameter type': 'int', low: 10, high: 30, step: 1 },
    { type: 'parameter', name: 'temp', 'parameter type': 'int', low: 80, high: 100, step: 1 },
    { type: 'score', name: 'nick' },
    { type: 'score', name: 'tom' },
  ],
  parameterMeta: [
    { type: 'parameter', name: 'grind', 'parameter type': 'int', low: 10, high: 30, step: 1 },
    { type: 'parameter', name: 'temp', 'parameter type': 'int', low: 80, high: 100, step: 1 },
  ],
  scoreMeta: [
    { type: 'score', name: 'nick' },
    { type: 'score', name: 'tom' },
  ],
  parameterKeys: ['grind', 'temp'],
  personNames: ['nick', 'tom'],
};

describe('recommendationService', () => {
  it('validates weight range', () => {
    const result = recommendationService.generate(dataset, {
      method: 'median',
      best: false,
      selectedPersons: [],
      weight: 1.5,
    });

    expect(result.ok).toBe(false);
  });

  it('returns recommendation payload', () => {
    const result = recommendationService.generate(dataset, {
      method: 'mean',
      best: false,
      selectedPersons: ['nick'],
      weight: 0.5,
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.data.state.historical.length).toBeGreaterThan(0);
    }
  });
});
