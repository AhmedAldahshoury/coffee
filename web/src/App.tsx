import { useEffect, useMemo, useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { PageShell } from '@/components/layout/PageShell';
import { ErrorState, SkeletonBlock } from '@/components/shared/States';
import { ChartToggles, DatasetKey, LoadedDataset, ScoringMethod } from '@/lib/types';
import { BrewRoute } from '@/routes/Brew';
import { HistoryRoute } from '@/routes/History';
import { InsightsRoute } from '@/routes/Insights';
import { datasetService } from '@/services/datasetService';
import { recommendationService } from '@/services/recommendationService';

const initialToggles: ChartToggles = { history: true, importance: true, scores: true, edf: false, slice: false };

const routeTitles: Record<string, string> = {
  '/': 'Brew',
  '/history': 'History',
  '/insights': 'Insights',
};

export default function App() {
  const [dataset, setDataset] = useState<DatasetKey>('aeropress.');
  const [cache, setCache] = useState<Partial<Record<DatasetKey, LoadedDataset>>>({});
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [method, setMethod] = useState<ScoringMethod>('median');
  const [weight, setWeight] = useState(0.5);
  const [best, setBest] = useState(false);
  const [selectedPersons, setSelectedPersons] = useState<string[]>([]);
  const [toggles, setToggles] = useState<ChartToggles>(initialToggles);
  const [sliceParam, setSliceParam] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('coffee:theme') === 'dark');

  const location = useLocation();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('coffee:theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const fetchDataset = async (selected: DatasetKey) => {
    setLoading(true);
    setLoadError(null);
    const result = await datasetService.load(selected);
    if (!result.ok) {
      setLoadError(result.message);
      setLoading(false);
      return;
    }
    setCache((prev) => ({ ...prev, [selected]: result.data }));
    setLoading(false);
  };

  useEffect(() => {
    if (!cache[dataset]) {
      fetchDataset(dataset);
    }
  }, [dataset]);

  const loaded = cache[dataset];

  const recommendationResult = useMemo(() => {
    if (!loaded) return null;
    return recommendationService.generate(loaded, { method, weight, best, selectedPersons });
  }, [loaded, method, weight, best, selectedPersons]);

  const title = routeTitles[location.pathname] ?? 'Coffee Optimizer';

  return (
    <PageShell
      title={title}
      collapsed={sidebarCollapsed}
      onToggleSidebar={() => setSidebarCollapsed((prev) => !prev)}
      dataset={dataset}
      datasets={datasetService.listDatasets()}
      onDatasetChange={setDataset}
      darkMode={darkMode}
      onToggleTheme={() => setDarkMode((prev) => !prev)}
    >
      {loadError ? <ErrorState title="Couldn’t load dataset" message={loadError} /> : null}
      {!loaded ? <SkeletonBlock className="h-72 w-full" /> : null}
      {loaded && recommendationResult && !recommendationResult.ok ? (
        <ErrorState title="Recommendation validation failed" message={recommendationResult.message} />
      ) : null}

      {loaded && recommendationResult?.ok ? (
        <Routes>
          <Route
            path="/"
            element={
              <BrewRoute
                loaded={loaded}
                state={recommendationResult.data.state}
                recommendation={recommendationResult.data.recommendation}
                method={method}
                setMethod={setMethod}
                weight={weight}
                setWeight={setWeight}
                best={best}
                setBest={setBest}
                selectedPersons={selectedPersons}
                setSelectedPersons={setSelectedPersons}
                refresh={() => fetchDataset(dataset)}
                loading={loading}
              />
            }
          />
          <Route path="/history" element={<HistoryRoute state={recommendationResult.data.state} />} />
          <Route
            path="/insights"
            element={
              <InsightsRoute
                loaded={loaded}
                state={recommendationResult.data.state}
                toggles={toggles}
                setToggles={setToggles}
                sliceParam={sliceParam}
                setSliceParam={setSliceParam}
              />
            }
          />
        </Routes>
      ) : null}
    </PageShell>
  );
}
