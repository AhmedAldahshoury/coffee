import { beforeEach, describe, expect, it, vi } from 'vitest';
import { brewLogService } from './brewLogService';

const storage = new Map<string, string>();

beforeEach(() => {
  storage.clear();
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => {
      storage.set(key, value);
    },
  });
});

describe('brewLogService', () => {
  it('rejects invalid score', () => {
    const result = brewLogService.create({ score: 11, dataset: 'aeropress.' });
    expect(result.ok).toBe(false);
  });

  it('creates and lists logs', () => {
    const result = brewLogService.create({ score: 8.5, dataset: 'aeropress.', notes: 'sweet cup' });
    expect(result.ok).toBe(true);

    const logs = brewLogService.list();
    expect(logs).toHaveLength(1);
  });
});
