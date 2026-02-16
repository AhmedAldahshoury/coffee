import { Navigate, Route, Routes } from 'react-router-dom';
import { OptimizerPage } from '../features/optimizer/components/OptimizerPage';
import { AppShell } from '../components/AppShell';
import { AuthPage } from '../features/auth/AuthPage';
import { LeaderboardPage } from '../features/leaderboard/LeaderboardPage';
import { AccountPage } from '../features/auth/AccountPage';
import { BrewSessionPage } from '../features/optimizer/components/BrewSessionPage';

function Protected({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem('coffee_token');
  return token ? children : <Navigate to="/login" replace />;
}

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route path="/optimizer" element={<Protected><OptimizerPage /></Protected>} />
        <Route path="/brew" element={<Protected><BrewSessionPage /></Protected>} />
        <Route path="/leaderboard" element={<Protected><LeaderboardPage /></Protected>} />
        <Route path="/account" element={<Protected><AccountPage /></Protected>} />
        <Route path="*" element={<Navigate to="/brew" replace />} />
      </Routes>
    </AppShell>
  );
}
