import { NavLink } from 'react-router-dom';
import { DatasetKey } from '@/lib/types';

export function TopNav({ dataset, setDataset }: { dataset: DatasetKey; setDataset: (v: DatasetKey) => void }) {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between p-4">
        <h1 className="text-lg font-semibold">Coffee Optimizer</h1>
        <select className="rounded-lg border border-border bg-card px-3 py-2" value={dataset} onChange={(e) => setDataset(e.target.value as DatasetKey)}>
          <option value="aeropress.">AeroPress</option>
          <option value="pourover.">Pour Over</option>
        </select>
      </div>
      <nav className="mx-auto flex max-w-6xl gap-6 px-4 pb-3 text-sm">
        {['/', '/history', '/insights'].map((to, i) => <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'font-semibold underline' : '')}>{['Brew', 'History', 'Insights'][i]}</NavLink>)}
      </nav>
    </header>
  );
}
