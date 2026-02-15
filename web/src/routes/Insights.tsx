import { Dispatch, SetStateAction } from 'react';
import { EdfChart } from '@/components/charts/EdfChart';
import { ImportanceChart } from '@/components/charts/ImportanceChart';
import { OptimizationHistoryChart } from '@/components/charts/OptimizationHistoryChart';
import { ScoresBoxChart } from '@/components/charts/ScoresBoxChart';
import { SliceChart } from '@/components/charts/SliceChart';
import { EmptyState } from '@/components/shared/States';
import { SectionCard } from '@/components/shared/SectionCard';
import { correlation } from '@/lib/optimizer';
import { ChartToggles, LoadedDataset, OptimizerState } from '@/lib/types';

const TOGGLE_KEYS: Array<keyof ChartToggles> = ['history', 'importance', 'scores', 'edf', 'slice'];

export function InsightsRoute({ loaded, state, toggles, setToggles, sliceParam, setSliceParam }: {
  loaded: LoadedDataset;
  state: OptimizerState;
  toggles: ChartToggles;
  setToggles: Dispatch<SetStateAction<ChartToggles>>;
  sliceParam: string;
  setSliceParam: (s: string) => void;
}) {
  if (!state.historical.length) {
    return <EmptyState title="No insights yet" description="Add historical brew data to unlock charts." />;
  }

  const numerical = loaded.parameterMeta.filter((meta) => meta['parameter type'] !== 'category').map((meta) => meta.name);
  const importance = numerical.map((key) => {
    const pairs = state.historical.map((row) => ({ x: Number(row[key]), y: row.objective })).filter((pair) => Number.isFinite(pair.x));
    return Math.abs(correlation(pairs.map((pair) => pair.x), pairs.map((pair) => pair.y)));
  });
  const slice = sliceParam || numerical[0] || '';

  return (
    <div className="space-y-6">
      <SectionCard title="Insight controls" description="Toggle charts to focus on the signals you need.">
        <div className="flex flex-wrap gap-4 text-sm">
          {TOGGLE_KEYS.map((key) => (
            <label key={key} className="flex items-center gap-2">
              <input
                checked={toggles[key]}
                onChange={(event) => setToggles((prev) => ({ ...prev, [key]: event.target.checked }))}
                type="checkbox"
              />
              {key}
            </label>
          ))}
        </div>
      </SectionCard>

      {toggles.history ? <SectionCard title="Optimization history"><OptimizationHistoryChart objective={state.historical.slice().sort((a, b) => a._index - b._index).map((row, i) => ({ idx: i + 1, value: row.objective }))} /></SectionCard> : null}
      {toggles.importance ? <SectionCard title="Parameter importance"><ImportanceChart labels={numerical} values={importance} /></SectionCard> : null}
      {toggles.scores ? <SectionCard title="Score spread"><ScoresBoxChart data={state.scoreKeys.map((key) => ({ name: key, values: loaded.dataRows.map((row) => row[key]).filter((value): value is number => typeof value === 'number') }))} /></SectionCard> : null}
      {toggles.edf ? <SectionCard title="Empirical distribution"><EdfChart values={state.historical.map((row) => row.objective)} /></SectionCard> : null}
      {toggles.slice ? (
        <SectionCard title="Parameter slice">
          <label className="block text-sm font-medium">
            Parameter
            <select className="mt-2 h-10 rounded-lg border border-border bg-background px-3" onChange={(event) => setSliceParam(event.target.value)} value={slice}>
              {numerical.map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
          </label>
          <SliceChart x={state.historical.map((row) => Number(row[slice]))} y={state.historical.map((row) => row.objective)} param={slice} />
        </SectionCard>
      ) : null}
    </div>
  );
}
