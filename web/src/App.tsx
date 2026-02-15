import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { TopNav } from '@/components/TopNav';
import { loadData } from '@/lib/data';
import { getState, recommendationFromHistorical } from '@/lib/optimizer';
import { ChartToggles, DatasetKey, LoadedDataset, ScoringMethod } from '@/lib/types';
import { BrewRoute } from '@/routes/Brew';
import { HistoryRoute } from '@/routes/History';
import { InsightsRoute } from '@/routes/Insights';

const initialToggles: ChartToggles = { history: true, importance: true, scores: true, edf: false, slice: false };
const DATASETS: DatasetKey[] = ['aeropress.', 'pourover.'];

export default function App() {
  const [dataset, setDataset] = useState<DatasetKey>('aeropress.');
  const [cache, setCache] = useState<Partial<Record<DatasetKey, LoadedDataset>>>({});
  const [loadError, setLoadError] = useState<string | null>(null);
  const [method, setMethod] = useState<ScoringMethod>('median');
  const [weight, setWeight] = useState(0.5);
  const [best, setBest] = useState(false);
  const [selectedPersons, setSelectedPersons] = useState<string[]>([]);
  const [toggles, setToggles] = useState<ChartToggles>(initialToggles);
  const [sliceParam, setSliceParam] = useState('');

  useEffect(() => {
    let cancelled = false;

    const hydrateCsvData = async () => {
      try {
        const results = await Promise.all(DATASETS.map(async (key) => [key, await loadData(key)] as const));
        if (cancelled) return;

        const nextCache = Object.fromEntries(results) as Record<DatasetKey, LoadedDataset>;
        setCache(nextCache);
        setLoadError(null);
        console.info('[csv] React state cache set', nextCache);
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : 'Unknown CSV load error';
        console.error('[csv] failed to load datasets', error);
        setLoadError(`Failed to load CSV data: ${message}`);
      }
    };

    hydrateCsvData();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    console.info('[csv] cache updated', cache);
  }, [cache]);

  const loaded = cache[dataset];

  if (loadError) {
    return (
      <div>
        <TopNav dataset={dataset} setDataset={setDataset} />
        <main className="mx-auto max-w-6xl p-4">
          <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700">
            <p className="font-semibold">Data load error</p>
            <p className="text-sm">{loadError}</p>
          </div>
        </main>
      </div>
    );
  }

  if (!loaded) return <div className="p-8">Loading CSV data…</div>;

  const state = getState(loaded, method, selectedPersons);
  const recommendation = recommendationFromHistorical(loaded, state.historical, state.fixedParameters, weight, best);

  console.info('[csv] final rendered counts', {
    selectedDataset: dataset,
    dataRows: loaded.dataRows.length,
    metaRows: loaded.metaRows.length,
    historicalRows: state.historical.length,
  });

  return (
    <div>
      <TopNav dataset={dataset} setDataset={setDataset} />
      <main className="mx-auto max-w-6xl p-4">
        <Routes>
          <Route path="/" element={<BrewRoute loaded={loaded} state={state} recommendation={recommendation} method={method} setMethod={setMethod} weight={weight} setWeight={setWeight} best={best} setBest={setBest} selectedPersons={selectedPersons} setSelectedPersons={setSelectedPersons} refresh={() => setDataset((d) => d)} />} />
          <Route path="/history" element={<HistoryRoute state={state} />} />
          <Route path="/insights" element={<InsightsRoute loaded={loaded} state={state} toggles={toggles} setToggles={setToggles} sliceParam={sliceParam} setSliceParam={setSliceParam} />} />
        </Routes>
      </main>
    </div>
  );
}
