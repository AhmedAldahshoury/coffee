import { BrewLogEntry, LogBrewPayload, ServiceResult } from './types';

const STORAGE_KEY = 'coffee:brew-logs';

const parseLogs = (): BrewLogEntry[] => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as BrewLogEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const persistLogs = (entries: BrewLogEntry[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
};

export const brewLogService = {
  list: (): BrewLogEntry[] => parseLogs(),
  create: (payload: LogBrewPayload): ServiceResult<BrewLogEntry> => {
    if (!Number.isFinite(payload.score) || payload.score < 0 || payload.score > 10) {
      return { ok: false, message: 'Score must be a number between 0 and 10.' };
    }

    const entry: BrewLogEntry = {
      ...payload,
      notes: payload.notes?.trim() || undefined,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };

    const existing = parseLogs();
    persistLogs([entry, ...existing].slice(0, 100));
    return { ok: true, data: entry };
  },
};
