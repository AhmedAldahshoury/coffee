import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { DatasetKey } from '@/lib/types';
import { DatasetOption } from '@/services/types';

export function PageShell(props: {
  title: string;
  children: React.ReactNode;
  collapsed: boolean;
  onToggleSidebar: () => void;
  dataset: DatasetKey;
  datasets: DatasetOption[];
  onDatasetChange: (value: DatasetKey) => void;
  darkMode: boolean;
  onToggleTheme: () => void;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <AppSidebar collapsed={props.collapsed} />
      <div className="flex min-w-0 flex-1 flex-col">
        <AppHeader
          title={props.title}
          collapsed={props.collapsed}
          onToggleSidebar={props.onToggleSidebar}
          dataset={props.dataset}
          datasets={props.datasets}
          onDatasetChange={props.onDatasetChange}
          darkMode={props.darkMode}
          onToggleTheme={props.onToggleTheme}
        />
        <main className="flex-1 p-4 md:p-6">{props.children}</main>
      </div>
    </div>
  );
}
