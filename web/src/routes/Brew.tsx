import { useMemo, useState } from 'react';
import { AdvancedControls } from '@/components/AdvancedControls';
import { BrewInputsCard } from '@/components/BrewInputsCard';
import { OnboardingEmptyState } from '@/components/OnboardingEmptyState';
import { RecipeCard } from '@/components/RecipeCard';
import { ErrorState, SkeletonBlock } from '@/components/shared/States';
import { Button } from '@/components/ui/button';
import { DialogClose, DialogContent, DialogOverlay, DialogPortal, DialogRoot } from '@/components/ui/dialog';
import { LoadedDataset, OptimizerState, ScoringMethod } from '@/lib/types';
import { useToast } from '@/components/feedback/ToastProvider';
import { brewLogService } from '@/services/brewLogService';

export function BrewRoute(props: {
  loaded: LoadedDataset;
  state: OptimizerState;
  recommendation: Record<string, string | number>;
  method: ScoringMethod;
  setMethod: (m: ScoringMethod) => void;
  weight: number;
  setWeight: (n: number) => void;
  best: boolean;
  setBest: (b: boolean) => void;
  selectedPersons: string[];
  setSelectedPersons: (p: string[]) => void;
  refresh: () => Promise<void>;
  loading: boolean;
  serviceError?: string;
}) {
  const [open, setOpen] = useState(false);
  const [score, setScore] = useState('');
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const { push } = useToast();
  const hasData = props.state.historical.length > 0;

  const summary = useMemo(
    () =>
      `Computed from ${props.state.historical.length} brews using ${props.state.method} scoring and ${props.state.scoreKeys.length} selected person(s).`,
    [props.state],
  );

  const handleSaveLog = () => {
    const result = brewLogService.create({
      score: Number(score),
      notes,
      dataset: props.loaded.dataset,
    });

    if (!result.ok) {
      setFormError(result.message);
      push(result.message, 'error');
      return;
    }

    setScore('');
    setNotes('');
    setOpen(false);
    setFormError(null);
    push('Brew result logged successfully.', 'success');
  };

  return (
    <div className="space-y-6 pb-8">
      {props.serviceError ? <ErrorState title="Couldn’t prepare recommendation" message={props.serviceError} /> : null}
      {props.loading ? <SkeletonBlock className="h-64 w-full" /> : null}
      {!props.loading && (hasData ? <RecipeCard loaded={props.loaded} fixedParameters={props.state.fixedParameters} recommendation={props.recommendation} /> : <OnboardingEmptyState onUseDemo={props.refresh} />)}

      <p className="text-sm text-muted-foreground">{summary}</p>

      <AdvancedControls
        method={props.method}
        setMethod={props.setMethod}
        weight={props.weight}
        setWeight={props.setWeight}
        best={props.best}
        setBest={props.setBest}
        persons={props.loaded.personNames}
        selectedPersons={props.selectedPersons}
        setSelectedPersons={props.setSelectedPersons}
      />

      <BrewInputsCard onGetRecipe={props.refresh} onLogResult={() => setOpen(true)} loading={props.loading} />

      <DialogRoot open={open} onOpenChange={setOpen}>
        <DialogPortal>
          <DialogOverlay className="fixed inset-0 bg-black/50" />
          <DialogContent className="fixed left-1/2 top-1/2 w-[92%] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold">Log brew result</h3>
            <p className="mt-1 text-sm text-muted-foreground">Score range is 0–10.</p>
            <div className="mt-4 space-y-3">
              <label className="block text-sm font-medium">
                Overall score
                <input className="mt-2 h-10 w-full rounded-lg border border-border bg-background px-3" value={score} onChange={(event) => setScore(event.target.value)} />
              </label>
              <label className="block text-sm font-medium">
                Notes (optional)
                <textarea className="mt-2 min-h-24 w-full rounded-lg border border-border bg-background px-3 py-2" value={notes} onChange={(event) => setNotes(event.target.value)} />
              </label>
              {formError ? <p className="text-sm text-red-600">{formError}</p> : null}
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button onClick={handleSaveLog}>Save</Button>
            </div>
          </DialogContent>
        </DialogPortal>
      </DialogRoot>
    </div>
  );
}
