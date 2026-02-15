import { Button } from './ui/button';
import { Card } from './ui/card';

export function BrewInputsCard({ onGetRecipe, onLogResult }: { onGetRecipe: () => void; onLogResult: () => void }) {
  return (
    <Card className="space-y-3">
      <h3 className="font-semibold">Ready to brew?</h3>
      <Button className="w-full" onClick={onGetRecipe}>Get next recipe</Button>
      <Button className="w-full" variant="outline" onClick={onLogResult}>Log result</Button>
    </Card>
  );
}
