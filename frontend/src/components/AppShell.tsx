import { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useThemeStore } from '../shared/config/themeStore';
import { HomeIcon, LogoMark, LogoutIcon, MoonIcon, SunIcon, TrophyIcon, UserIcon } from './icons';

interface Props { children: ReactNode }

interface NavEntry {
  to: string;
  label: string;
  icon: (props: { size?: number; className?: string }) => JSX.Element;
}

const navEntries: NavEntry[] = [
  { to: '/optimizer', label: 'Optimizer', icon: HomeIcon },
  { to: '/leaderboard', label: 'Leaderboard', icon: TrophyIcon },
  { to: '/account', label: 'Account', icon: UserIcon },
];

function NavItem({ to, label, icon: Icon }: NavEntry) {
  const location = useLocation();
  const active = location.pathname.startsWith(to);

  return (
    <Link to={to} className={active ? 'nav-item active' : 'nav-item'}>
      <Icon size={16} />
      <span>{label}</span>
    </Link>
  );
}

export function AppShell({ children }: Props) {
  const { darkMode, toggle } = useThemeStore();
  const navigate = useNavigate();
  const token = localStorage.getItem('coffee_token');

  return (
    <div className={darkMode ? 'app dark' : 'app'}>
      <div className="ambient-glow" aria-hidden="true" />
      <header className="topbar glass-panel">
        <div className="brand">
          <LogoMark />
          <div>
            <h1>Coffee Optimizer</h1>
            <p>Dial in each brew with premium precision.</p>
          </div>
        </div>

        <nav className="nav-links" aria-label="Main navigation">
          {navEntries.map((entry) => <NavItem key={entry.to} {...entry} />)}
        </nav>

        <div className="actions">
          <button onClick={toggle} className="btn btn-secondary icon-btn" type="button">
            {darkMode ? <SunIcon size={16} /> : <MoonIcon size={16} />}
            <span>{darkMode ? 'Light' : 'Dark'}</span>
          </button>
          {token ? (
            <button
              className="btn btn-ghost icon-btn"
              onClick={() => {
                localStorage.removeItem('coffee_token');
                navigate('/login');
              }}
              type="button"
            >
              <LogoutIcon size={16} />
              <span>Logout</span>
            </button>
          ) : null}
        </div>
      </header>
      <main className="content page-transition">{children}</main>
    </div>
  );
}
