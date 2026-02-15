import { ScoringMethod } from '@/lib/types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';
import { Card } from './ui/card';
import { PersonsSelector } from './PersonsSelector';

export function AdvancedControls(props: {
  method: ScoringMethod; setMethod: (m: ScoringMethod) => void; weight: number; setWeight: (n: number) => void; best: boolean; setBest: (v: boolean) => void;
  persons: string[]; selectedPersons: string[]; setSelectedPersons: (p: string[]) => void;
}) {
  return (
    <Card>
      <Accordion type="single" collapsible>
        <AccordionItem value="advanced">
          <AccordionTrigger className="w-full text-left font-semibold">Advanced optimizer settings</AccordionTrigger>
          <AccordionContent className="space-y-3 pt-3">
            <label className="block text-sm">Scoring method
              <select className="mt-1 w-full rounded-lg border border-border p-2" value={props.method} onChange={(e) => props.setMethod(e.target.value as ScoringMethod)}>
                <option value="median">Median</option><option value="mean">Mean</option><option value="highest">Highest</option><option value="lowest">Lowest</option>
              </select>
            </label>
            <label className="block text-sm">Elite averaging weight ({props.weight.toFixed(2)})
              <input type="range" min={0} max={1} step={0.01} value={props.weight} onChange={(e) => props.setWeight(Number(e.target.value))} className="w-full" />
            </label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={props.best} onChange={(e) => props.setBest(e.target.checked)} />Use best historical trial only</label>
            <PersonsSelector persons={props.persons} selected={props.selectedPersons} onChange={props.setSelectedPersons} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </Card>
  );
}
