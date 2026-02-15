import { LoadedDataset } from '@/lib/types';
import { Card } from './ui/card';

export function RecipeCard({ loaded, fixedParameters, recommendation }: { loaded: LoadedDataset; fixedParameters: Record<string, string | number>; recommendation: Record<string, string | number> }) {
  return (
    <Card>
      <h2 className="mb-4 text-2xl font-semibold">Next Recipe</h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {loaded.parameterMeta.map((m) => {
          const val = m.name in fixedParameters ? fixedParameters[m.name] : recommendation[m.name];
          return <div key={m.name} className="rounded-xl bg-stone-100 p-3"><p className="text-xs uppercase text-stone-500">{m.name}</p><p className="text-xl font-semibold">{val ?? '—'} <span className="text-sm">{m.unit || ''}</span></p></div>;
        })}
      </div>
    </Card>
  );
}
