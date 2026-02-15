export function EmptyState({ title, description, action }: { title: string; description: string; action?: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-card p-8 text-center">
      <h3 className="text-lg font-medium">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ title, message, action }: { title: string; message: string; action?: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-950 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-1 text-sm">{message}</p>
      {action ? <div className="mt-3">{action}</div> : null}
    </div>
  );
}

export function SkeletonBlock({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-muted ${className}`} aria-hidden />;
}
