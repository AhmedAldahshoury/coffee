import { Moon, PanelLeftClose, PanelLeftOpen, Sun } from 'lucide-react';
import { DatasetKey } from '@/lib/types';
import { DatasetOption } from '@/services/types';
import { Button } from '@/components/ui/button';

export function AppHeader(props: {
  title: string;
  collapsed: boolean;
  onToggleSidebar: () => void;
  dataset: DatasetKey;
  datasets: DatasetOption[];
  onDatasetChange: (value: DatasetKey) => void;
  darkMode: boolean;
  onToggleTheme: () => void;
}) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-background px-4 md:px-6">
      <div className="flex items-center gap-3">
        <Button aria-label="Toggle sidebar" variant="ghost" onClick={props.onToggleSidebar} className="hidden md:inline-flex">
          {props.collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
        </Button>
        <div>
          <h1 className="text-lg font-semibold">{props.title}</h1>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <select
          className="h-10 rounded-lg border border-border bg-card px-3 text-sm"
          value={props.dataset}
          onChange={(event) => props.onDatasetChange(event.target.value as DatasetKey)}
          aria-label="Dataset"
        >
          {props.datasets.map((option) => (
            <option key={option.key} value={option.key}>
              {option.label}
            </option>
          ))}
        </select>
        <Button aria-label="Toggle theme" variant="outline" onClick={props.onToggleTheme}>
          {props.darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </Button>
      </div>
    </header>
  );
}
