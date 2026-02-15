import { createContext, useContext, useMemo, useState } from 'react';

type Toast = { id: string; title: string; tone: 'success' | 'error' };

const ToastContext = createContext<{ push: (title: string, tone: Toast['tone']) => void } | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const value = useMemo(
    () => ({
      push: (title: string, tone: Toast['tone']) => {
        const id = crypto.randomUUID();
        setToasts((prev) => [...prev, { id, title, tone }]);
        window.setTimeout(() => setToasts((prev) => prev.filter((toast) => toast.id !== id)), 3000);
      },
    }),
    [],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`rounded-xl border p-3 text-sm shadow-lg ${toast.tone === 'success' ? 'border-emerald-500/40 bg-emerald-50 text-emerald-950 dark:bg-emerald-950 dark:text-emerald-100' : 'border-red-500/40 bg-red-50 text-red-950 dark:bg-red-950 dark:text-red-100'}`}
          >
            {toast.title}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};
