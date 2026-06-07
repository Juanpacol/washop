import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './features/auth/LoginPage';
import AppShell from './shared/components/AppShell';

// Páginas (implementar en features/<dominio>/<Nombre>Page.jsx)
// import DashboardPage  from './features/dashboard/DashboardPage';
// import CustomersPage  from './features/customers/CustomersPage';
// import ServicesPage   from './features/services/ServicesPage';
// import PaymentsPage   from './features/payments/PaymentsPage';
// import ReportsPage    from './features/reports/ReportsPage';

function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();
  if (loading) return null;
  if (!session) return <Navigate to="/login" replace />;
  return <AppShell>{children}</AppShell>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={
        <ProtectedRoute>
          {/* Reemplazar el placeholder con las páginas reales */}
          <p style={{ padding: 24 }}>Bienvenido a WASHOPS</p>
        </ProtectedRoute>
      } />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
