import { Navigate, Route, Routes } from 'react-router-dom';
import { OptimizerPage } from '../features/optimizer/components/OptimizerPage';
import { AppShell } from '../components/AppShell';

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/optimizer" element={<OptimizerPage />} />
        <Route path="*" element={<Navigate to="/optimizer" replace />} />
      </Routes>
    </AppShell>
  );
}
