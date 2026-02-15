import { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useThemeStore } from '../shared/config/themeStore';

interface Props { children: ReactNode }

export function AppShell({ children }: Props) {
  const { darkMode, toggle } = useThemeStore();
  const navigate = useNavigate();

  return (
    <div className={darkMode ? 'app dark' : 'app'}>
      <header className="topbar">
        <h1>Coffee Optimizer</h1>
        <nav className="nav-links">
          <Link to="/optimizer">Optimizer</Link>
          <Link to="/leaderboard">Leaderboard</Link>
          <Link to="/login">Login</Link>
        </nav>
        <div>
          <button onClick={toggle} className="btn btn-secondary" type="button">{darkMode ? 'Light' : 'Dark'}</button>
          <button className="btn btn-secondary" onClick={() => { localStorage.removeItem('coffee_token'); navigate('/login'); }}>Logout</button>
        </div>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}
