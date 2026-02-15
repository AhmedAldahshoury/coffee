import { Button } from './ui/button';
import { Card } from './ui/card';

export function OnboardingEmptyState({ onUseDemo }: { onUseDemo: () => void }) {
  return (
    <Card className="space-y-3 text-center">
      <h2 className="text-xl font-semibold">Start your first optimization</h2>
      <p className="text-sm text-stone-600">No usable history yet for this dataset/person selection.</p>
      <div className="flex flex-wrap justify-center gap-2">
        <Button onClick={onUseDemo}>Use demo data</Button>
        <Button variant="outline">Import CSV</Button>
        <Button variant="outline">Add first brew</Button>
      </div>
    </Card>
  );
}
