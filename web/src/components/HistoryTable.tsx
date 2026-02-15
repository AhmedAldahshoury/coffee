import { OptimizerState } from '@/lib/types';

export function HistoryTable({ state }: { state: OptimizerState }) {
  return <div className="overflow-x-auto rounded-2xl border border-border bg-card p-3"><table className="w-full min-w-[640px] text-sm"><thead><tr><th>Rank</th><th>Score</th>{state.parameterKeys.slice(0,5).map((k) => <th key={k}>{k}</th>)}</tr></thead><tbody>{state.historical.slice(0,8).map((r,i) => <tr key={r._index} className="border-t"><td>#{i+1}</td><td>{r.objective.toFixed(2)}</td>{state.parameterKeys.slice(0,5).map((k)=><td key={k}>{String(r[k])}</td>)}</tr>)}</tbody></table></div>;
}
