import { useContext } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import AuthContext from "../context/AuthContext";

const Layout = () => {
    const { user, logout } = useContext(AuthContext);
    const location = useLocation();

    const navItems = [
        { path: "/dashboard", label: "Dashboard", icon: "📊", roles: ["admin", "tributario", "auditor"] },
        { path: "/corredor/dashboard", label: "Dashboard Corredor", icon: "📊", roles: ["corredor"] },
        { path: "/calificaciones", label: "Calificaciones", icon: "📝", roles: ["admin", "tributario", "auditor", "corredor"] },
        { path: "/empresas", label: "Empresas", icon: "🏢", roles: ["admin", "tributario", "corredor"] },
        { path: "/propietarios", label: "Propietarios", icon: "👥", roles: ["admin", "tributario"] },
        { path: "/historial", label: "Historial", icon: "⏰", roles: ["admin", "auditor"] },
        { path: "/certificados", label: "Certificados", icon: "📄", roles: ["admin", "tributario"] },
        { path: "/carga-masiva", label: "Carga Masiva", icon: "📤", roles: ["admin", "tributario"] },
        { path: "/users", label: "Gestión Usuarios", icon: "👤", roles: ["admin"] },
        { path: "/informe-gestion", label: "Informe de Gestión", icon: "📄", roles: ["admin", "tributario", "corredor"] },
        { path: "/mfa-setup", label: "Configurar MFA", icon: "🔒", roles: ["admin", "tributario", "auditor", "corredor"] },
        { path: "/corredores", label: "Gestión Corredores", icon: "🤝", roles: ["admin", "tributario"] },
    ];

    const filteredNavItems = navItems.filter(item => item.roles.includes(user?.role));

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex flex-col">
                <div className="p-6 border-b">
                    <h1 className="text-2xl font-bold text-red-600">NUAM</h1>
                    <p className="text-sm text-gray-500">Gestión Tributaria</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {filteredNavItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center px-4 py-3 rounded-lg transition-colors ${location.pathname.startsWith(item.path)
                                ? "bg-red-50 text-red-600 font-medium"
                                : "text-gray-600 hover:bg-gray-50"
                                }`}
                        >
                            <span className="mr-3">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}
                </nav>

                <div className="p-4 border-t">
                    <div className="flex items-center mb-4 px-4">
                        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold mr-3">
                            {user?.username?.[0]?.toUpperCase() || "U"}
                        </div>
                        <div>
                            <p className="text-sm font-medium text-gray-700">{user?.username || "Usuario"}</p>
                            <p className="text-xs text-gray-500">{user?.role || "Rol"}</p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors text-left flex items-center"
                    >
                        <span className="mr-2">🚪</span> Cerrar Sesión
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default Layout;
