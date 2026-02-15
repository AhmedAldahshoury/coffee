import { Button } from './ui/button';
import { SectionCard } from './shared/SectionCard';

export function BrewInputsCard({ onGetRecipe, onLogResult, loading }: { onGetRecipe: () => void; onLogResult: () => void; loading: boolean }) {
  return (
    <SectionCard title="Brew actions" description="Refresh recommendations or log your latest cup.">
      <div className="grid gap-3 sm:grid-cols-2">
        <Button onClick={onGetRecipe} disabled={loading}>
          {loading ? 'Refreshing…' : 'Get next recipe'}
        </Button>
        <Button variant="outline" onClick={onLogResult}>
          Log result
        </Button>
      </div>
    </SectionCard>
  );
}
