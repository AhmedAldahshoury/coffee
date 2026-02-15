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

export default function App() {
  const [dataset, setDataset] = useState<DatasetKey>('aeropress.');
  const [cache, setCache] = useState<Partial<Record<DatasetKey, LoadedDataset>>>({});
  const [method, setMethod] = useState<ScoringMethod>('median');
  const [weight, setWeight] = useState(0.5);
  const [best, setBest] = useState(false);
  const [selectedPersons, setSelectedPersons] = useState<string[]>([]);
  const [toggles, setToggles] = useState<ChartToggles>(initialToggles);
  const [sliceParam, setSliceParam] = useState('');

  useEffect(() => {
    if (!cache[dataset]) {
      loadData(dataset).then((d) => setCache((c) => ({ ...c, [dataset]: d })));
    }
  }, [dataset, cache]);

  const loaded = cache[dataset];
  if (!loaded) return <div className="p-8">Loading…</div>;

  const state = getState(loaded, method, selectedPersons);
  const recommendation = recommendationFromHistorical(loaded, state.historical, state.fixedParameters, weight, best);

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
