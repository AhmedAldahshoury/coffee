import { OptimizerState } from '@/lib/types';
import { EmptyState } from './shared/States';

export function HistoryTable({ state }: { state: OptimizerState }) {
  if (!state.historical.length) {
    return <EmptyState title="No historical brews" description="Log brew results to populate this table." />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-card">
      <table className="w-full min-w-[720px] text-sm">
        <thead className="bg-muted/60 text-left">
          <tr>
            <th className="px-4 py-3">Rank</th>
            <th className="px-4 py-3">Score</th>
            {state.parameterKeys.slice(0, 6).map((key) => (
              <th key={key} className="px-4 py-3">
                {key}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {state.historical.slice(0, 12).map((row, index) => (
            <tr key={row._index} className="border-t border-border">
              <td className="px-4 py-3">#{index + 1}</td>
              <td className="px-4 py-3 font-medium">{row.objective.toFixed(2)}</td>
              {state.parameterKeys.slice(0, 6).map((key) => (
                <td key={key} className="px-4 py-3">
                  {String(row[key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
