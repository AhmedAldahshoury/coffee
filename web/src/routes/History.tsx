import { useMemo, useState } from 'react';
import { HistoryTable } from '@/components/HistoryTable';
import { FilterBar } from '@/components/shared/FilterBar';
import { SectionCard } from '@/components/shared/SectionCard';
import { OptimizerState } from '@/lib/types';

export function HistoryRoute({ state }: { state: OptimizerState }) {
  const [query, setQuery] = useState('');

  const filteredState = useMemo(() => {
    if (!query.trim()) return state;
    const q = query.toLowerCase();
    const historical = state.historical.filter((row) =>
      state.parameterKeys.some((key) => String(row[key]).toLowerCase().includes(q)),
    );
    return { ...state, historical };
  }, [query, state]);

  return (
    <SectionCard title="History" description="Top ranked historical brews from your dataset.">
      <FilterBar>
        <label className="text-sm font-medium">
          Filter rows
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="mt-2 h-10 rounded-lg border border-border bg-background px-3"
            placeholder="Search parameter value"
          />
        </label>
      </FilterBar>
      <HistoryTable state={filteredState} />
    </SectionCard>
  );
}
