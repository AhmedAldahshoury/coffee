import { ScoringMethod } from '@/lib/types';
import { Card } from './ui/card';
import { PersonsSelector } from './PersonsSelector';

export function AdvancedControls(props: {
  method: ScoringMethod;
  setMethod: (m: ScoringMethod) => void;
  weight: number;
  setWeight: (n: number) => void;
  best: boolean;
  setBest: (v: boolean) => void;
  persons: string[];
  selectedPersons: string[];
  setSelectedPersons: (p: string[]) => void;
}) {
  return (
    <Card className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">Optimizer controls</h3>
        <p className="text-sm text-muted-foreground">Tune how recommendations are generated from historical brews.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="block text-sm font-medium">
          Scoring method
          <select
            className="mt-2 h-10 w-full rounded-lg border border-border bg-background px-3"
            value={props.method}
            onChange={(event) => props.setMethod(event.target.value as ScoringMethod)}
          >
            <option value="median">Median</option>
            <option value="mean">Mean</option>
            <option value="highest">Highest</option>
            <option value="lowest">Lowest</option>
          </select>
        </label>

        <label className="block text-sm font-medium">
          Elite averaging weight ({props.weight.toFixed(2)})
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={props.weight}
            onChange={(event) => props.setWeight(Number(event.target.value))}
            className="mt-3 w-full"
          />
        </label>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={props.best} onChange={(event) => props.setBest(event.target.checked)} />
        Use best historical trial only
      </label>

      <PersonsSelector persons={props.persons} selected={props.selectedPersons} onChange={props.setSelectedPersons} />
    </Card>
  );
}
