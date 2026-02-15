import { loadData } from '@/lib/data';
import { DatasetKey } from '@/lib/types';
import { DatasetOption, DatasetService } from './types';

const DATASETS: DatasetOption[] = [
  { key: 'aeropress.', label: 'AeroPress' },
  { key: 'pourover.', label: 'Pour Over' },
];

export const datasetService: DatasetService = {
  listDatasets: () => DATASETS,
  load: async (dataset: DatasetKey) => {
    try {
      const loaded = await loadData(dataset);
      return { ok: true, data: loaded };
    } catch (error) {
      return { ok: false, message: error instanceof Error ? error.message : 'Could not load dataset.' };
    }
  },
};
