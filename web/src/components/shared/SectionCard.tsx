import { Card } from '@/components/ui/card';

export function SectionCard({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <Card className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {children}
    </Card>
  );
}
