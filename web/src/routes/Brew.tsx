import { useMemo, useState } from 'react';
import { AdvancedControls } from '@/components/AdvancedControls';
import { BrewInputsCard } from '@/components/BrewInputsCard';
import { OnboardingEmptyState } from '@/components/OnboardingEmptyState';
import { RecipeCard } from '@/components/RecipeCard';
import { Button } from '@/components/ui/button';
import { DialogClose, DialogContent, DialogDescription, DialogOverlay, DialogPortal, DialogRoot, DialogTitle } from '@/components/ui/dialog';
import { LoadedDataset, OptimizerState, ScoringMethod } from '@/lib/types';

export function BrewRoute(props: {
  loaded: LoadedDataset;
  state: OptimizerState;
  recommendation: Record<string, string | number>;
  method: ScoringMethod; setMethod: (m: ScoringMethod) => void;
  weight: number; setWeight: (n: number) => void;
  best: boolean; setBest: (b: boolean) => void;
  selectedPersons: string[]; setSelectedPersons: (p: string[]) => void;
  refresh: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [score, setScore] = useState('');
  const [notes, setNotes] = useState('');
  const hasData = props.state.historical.length > 0;

  const summary = useMemo(() => `Computed from ${props.state.historical.length} brews using ${props.state.method} scoring and ${props.state.scoreKeys.length} selected person(s).`, [props.state]);

  return (
    <div className="space-y-4 pb-20">
      {!hasData ? <OnboardingEmptyState onUseDemo={props.refresh} /> : <RecipeCard loaded={props.loaded} fixedParameters={props.state.fixedParameters} recommendation={props.recommendation} />}
      <p className="text-sm text-stone-600">{summary}</p>
      <AdvancedControls method={props.method} setMethod={props.setMethod} weight={props.weight} setWeight={props.setWeight} best={props.best} setBest={props.setBest} persons={props.loaded.personNames} selectedPersons={props.selectedPersons} setSelectedPersons={props.setSelectedPersons} />
      <div className="fixed bottom-0 left-0 right-0 border-t border-border bg-background p-3 sm:static sm:border-0 sm:p-0"><BrewInputsCard onGetRecipe={props.refresh} onLogResult={() => setOpen(true)} /></div>
      <DialogRoot open={open} onOpenChange={setOpen}><DialogPortal><DialogOverlay className="fixed inset-0 bg-black/40" /><DialogContent className="fixed left-1/2 top-1/2 w-[90%] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-card p-5"><DialogTitle className="mb-2 text-lg font-semibold">Log result</DialogTitle><DialogDescription className="mb-2 text-sm text-stone-600">Record your score and optional notes for this brew.</DialogDescription><input className="mb-2 w-full rounded border p-2" placeholder="Overall score" value={score} onChange={(e)=>setScore(e.target.value)} /><textarea className="mb-3 w-full rounded border p-2" placeholder="Notes (optional)" value={notes} onChange={(e)=>setNotes(e.target.value)} /><Button onClick={() => { localStorage.setItem('coffee:last-log', JSON.stringify({ score, notes, timestamp: new Date().toISOString() })); setOpen(false); }}>Save</Button> <DialogClose asChild><button className="ml-2">Close</button></DialogClose></DialogContent></DialogPortal></DialogRoot>
    </div>
  );
}
