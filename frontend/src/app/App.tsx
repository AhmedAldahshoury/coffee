import { Navigate, Route, Routes } from 'react-router-dom';
import { OptimizerPage } from '../features/optimizer/components/OptimizerPage';
import { AppShell } from '../components/AppShell';
import { AuthPage } from '../features/auth/AuthPage';
import { LeaderboardPage } from '../features/leaderboard/LeaderboardPage';

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
        <Route path="/leaderboard" element={<Protected><LeaderboardPage /></Protected>} />
        <Route path="*" element={<Navigate to="/optimizer" replace />} />
      </Routes>
    </AppShell>
  );
}
