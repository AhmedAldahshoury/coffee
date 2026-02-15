import { HistoryTable } from '@/components/HistoryTable';
import { OptimizerState } from '@/lib/types';

export function HistoryRoute({ state }: { state: OptimizerState }) {
  return <div className="space-y-3"><h2 className="text-2xl font-semibold">History</h2><p className="text-sm text-stone-600">Top ranked historical brews.</p><HistoryTable state={state} /></div>;
}
