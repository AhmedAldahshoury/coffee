import { NavLink } from 'react-router-dom';
import { BarChart3, History, Coffee } from 'lucide-react';

const ITEMS = [
  { to: '/', label: 'Brew', icon: Coffee },
  { to: '/history', label: 'History', icon: History },
  { to: '/insights', label: 'Insights', icon: BarChart3 },
];

export function AppSidebar({ collapsed }: { collapsed: boolean }) {
  return (
    <aside className={`border-r border-border bg-card transition-all ${collapsed ? 'w-[72px]' : 'w-60'} hidden md:block`}>
      <div className="p-4 text-sm font-semibold text-muted">Coffee Optimizer</div>
      <nav className="space-y-1 px-2">
        {ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm outline-none transition hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring ${isActive ? 'bg-muted text-foreground' : 'text-muted-foreground'}`
            }
          >
            <item.icon size={16} />
            {!collapsed && item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
