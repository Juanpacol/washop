import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoginPage from '../features/auth/LoginPage';

function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();
  if (loading) return null;
  if (!session) return <Navigate to="/login" replace />;
  return children;
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <div>Dashboard (próximamente)</div>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
