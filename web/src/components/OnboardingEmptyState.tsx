import { Button } from './ui/button';
import { EmptyState } from './shared/States';

export function OnboardingEmptyState({ onUseDemo }: { onUseDemo: () => void }) {
  return (
    <EmptyState
      title="No optimization data available"
      description="Adjust filters or switch datasets to see recommendations."
      action={<Button onClick={onUseDemo}>Refresh data</Button>}
    />
  );
}
