import { LoadedDataset } from '@/lib/types';
import { SectionCard } from './shared/SectionCard';

export function RecipeCard({ loaded, fixedParameters, recommendation }: { loaded: LoadedDataset; fixedParameters: Record<string, string | number>; recommendation: Record<string, string | number> }) {
  return (
    <SectionCard title="Next recipe" description="Recommended values generated from your top-performing brews.">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {loaded.parameterMeta.map((meta) => {
          const value = meta.name in fixedParameters ? fixedParameters[meta.name] : recommendation[meta.name];
          return (
            <div key={meta.name} className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">{meta.name}</p>
              <p className="mt-2 text-2xl font-semibold">
                {value ?? '—'} <span className="text-sm font-normal text-muted-foreground">{meta.unit || ''}</span>
              </p>
            </div>
          );
        })}
      </div>
    </SectionCard>
  );
}
