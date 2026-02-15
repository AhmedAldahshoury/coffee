import { EdfChart } from '@/components/charts/EdfChart';
import { ImportanceChart } from '@/components/charts/ImportanceChart';
import { OptimizationHistoryChart } from '@/components/charts/OptimizationHistoryChart';
import { ScoresBoxChart } from '@/components/charts/ScoresBoxChart';
import { SliceChart } from '@/components/charts/SliceChart';
import { correlation } from '@/lib/optimizer';
import { LoadedDataset, OptimizerState } from '@/lib/types';

export function InsightsRoute({ loaded, state, toggles, setToggles, sliceParam, setSliceParam }: { loaded: LoadedDataset; state: OptimizerState; toggles: Record<string, boolean>; setToggles: (t: Record<string, boolean>) => void; sliceParam: string; setSliceParam: (s: string) => void }) {
  const numerical = loaded.parameterMeta.filter((m) => m['parameter type'] !== 'category').map((m) => m.name);
  const importance = numerical.map((k) => Math.abs(correlation(state.historical.map((r) => Number(r[k])), state.historical.map((r) => r.objective))));
  const slice = sliceParam || numerical[0] || '';
  return <div className="space-y-4"><h2 className="text-2xl font-semibold">Insights</h2><div className="flex flex-wrap gap-3 text-sm">{['history','importance','scores','edf','slice'].map((k)=> <label key={k}><input type="checkbox" checked={toggles[k]} onChange={(e)=>setToggles({...toggles,[k]:e.target.checked})} /> {k}</label>)}</div>
    {toggles.history && <OptimizationHistoryChart objective={state.historical.slice().sort((a,b)=>a._index-b._index).map((r,i)=>({ idx:i+1, value:r.objective }))} />}
    {toggles.importance && <ImportanceChart labels={numerical} values={importance} />}
    {toggles.scores && <ScoresBoxChart data={state.scoreKeys.map((k)=>({ name:k, values:loaded.dataRows.map((r)=>r[k]).filter((v): v is number => typeof v === 'number') }))} />}
    {toggles.edf && <EdfChart values={state.historical.map((r)=>r.objective)} />}
    {toggles.slice && <div><select className="mb-2 rounded border p-2" value={slice} onChange={(e)=>setSliceParam(e.target.value)}>{numerical.map((k)=><option key={k} value={k}>{k}</option>)}</select><SliceChart x={state.historical.map((r)=>Number(r[slice]))} y={state.historical.map((r)=>r.objective)} param={slice} /></div>}
  </div>;
}
