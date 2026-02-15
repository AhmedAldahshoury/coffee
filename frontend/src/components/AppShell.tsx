import { ReactNode } from 'react';
import { useThemeStore } from '../shared/config/themeStore';

interface Props {
  children: ReactNode;
}

export function AppShell({ children }: Props) {
  const { darkMode, toggle } = useThemeStore();

  return (
    <div className={darkMode ? 'app dark' : 'app'}>
      <header className="topbar">
        <h1>Coffee Optimizer</h1>
        <button onClick={toggle} className="btn btn-secondary" type="button">
          {darkMode ? 'Light mode' : 'Dark mode'}
        </button>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}
