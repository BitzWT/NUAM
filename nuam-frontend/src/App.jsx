import { useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AuthContext from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Calificaciones from "./pages/Calificaciones";
import CalificacionForm from "./pages/CalificacionForm";
import Empresas from "./pages/Empresas";
import EmpresaForm from "./pages/EmpresaForm";
import AccionesManagement from "./pages/AccionesManagement";
import Propietarios from "./pages/Propietarios";
import PropietarioForm from "./pages/PropietarioForm";
import Historial from "./pages/Historial";
import Certificados from "./pages/Certificados";
import MFAConfig from "./pages/MFAConfig";
import BulkUpload from "./pages/BulkUpload";
import Signup from "./pages/Signup";
import Users from "./pages/Users";
import UserForm from "./pages/UserForm";
import Layout from "./components/Layout";
import CorredorDashboard from "./pages/CorredorDashboard";
import CorredorCompanyView from "./pages/CorredorCompanyView";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Corredores from "./pages/Corredores";
import InformeGestion from "./pages/InformeGestion";

// Protected Route Component
const ProtectedRoute = () => {
  const { user, loading } = useContext(AuthContext);

  if (loading) return <div className="flex h-screen items-center justify-center">Cargando...</div>;

  return user ? <Outlet /> : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />

              <Route path="/calificaciones" element={<Calificaciones />} />
              <Route path="/calificaciones/nueva" element={<CalificacionForm />} />
              <Route path="/calificaciones/:id" element={<CalificacionForm />} />

              <Route path="/empresas" element={<Empresas />} />
              <Route path="/empresas/nueva" element={<EmpresaForm />} />
              <Route path="/empresas/:id" element={<EmpresaForm />} />
              <Route path="/empresas/:id/acciones" element={<AccionesManagement />} />

              <Route path="/propietarios" element={<Propietarios />} />
              <Route path="/propietarios/nueva" element={<PropietarioForm />} />
              <Route path="/propietarios/:id" element={<PropietarioForm />} />

              <Route path="/historial" element={<Historial />} />
              <Route path="/certificados" element={<Certificados />} />
              <Route path="/mfa-setup" element={<MFAConfig />} />
              <Route path="/carga-masiva" element={<BulkUpload />} />
              <Route path="/informe-gestion" element={<InformeGestion />} />

              <Route path="/users" element={<Users />} />
              <Route path="/users/nueva" element={<UserForm />} />
              <Route path="/users/:id" element={<UserForm />} />
              <Route path="/users/:id" element={<UserForm />} />

              {/* Corredor Routes */}
              <Route path="/corredores" element={<Corredores />} />
              <Route path="/corredor/dashboard" element={<CorredorDashboard />} />
              <Route path="/corredor/empresas/:id" element={<CorredorCompanyView />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
