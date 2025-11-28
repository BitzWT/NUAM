import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const Users = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await api.get("/users/");
            setUsers(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar usuarios");
            setLoading(false);
        }
    };

    const handleDeactivate = async (id, isActive) => {
        if (!window.confirm(`¿Estás seguro de ${isActive ? 'desactivar' : 'activar'} este usuario?`)) return;
        try {
            await api.patch(`/users/${id}/`, { is_active: !isActive });
            fetchUsers();
        } catch (err) {
            alert("Error al actualizar estado");
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Gestión de Usuarios</h1>
                <Link to="/users/nueva" className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                    + Nuevo Usuario
                </Link>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Usuario</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Email</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Rol</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Estado</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {users.map((u) => (
                            <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4 text-sm font-medium text-gray-800">{u.username}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">{u.email}</td>
                                <td className="px-6 py-4 text-sm text-gray-600 capitalize">{u.role}</td>
                                <td className="px-6 py-4 text-sm">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${u.is_active ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
                                        }`}>
                                        {u.is_active ? 'Activo' : 'Inactivo'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm space-x-3">
                                    <Link to={`/users/${u.id}`} className="text-red-600 hover:text-red-800 font-medium">
                                        Editar
                                    </Link>
                                    <button
                                        onClick={() => handleDeactivate(u.id, u.is_active)}
                                        className={`${u.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'} font-medium`}
                                    >
                                        {u.is_active ? 'Desactivar' : 'Activar'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Users;
