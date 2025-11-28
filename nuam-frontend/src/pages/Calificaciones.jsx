import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const Calificaciones = () => {
    const { user } = useContext(AuthContext);
    const [calificaciones, setCalificaciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({ search: "", ordering: "-fecha" });

    useEffect(() => {
        fetchCalificaciones();
    }, [filters]);

    const fetchCalificaciones = async () => {
        try {
            const params = new URLSearchParams();
            if (filters.search) params.append("search", filters.search);
            if (filters.ordering) params.append("ordering", filters.ordering);

            const response = await api.get(`/calificaciones/?${params.toString()}`);
            setCalificaciones(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar calificaciones");
            setLoading(false);
        }
    };

    const handleExport = async (type) => {
        try {
            const response = await api.get(`/calificaciones/export_${type}/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `calificaciones.${type === 'pdf' ? 'pdf' : 'xlsx'}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Error exporting", err);
            setError("Error al exportar archivo");
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Calificaciones Tributarias</h1>
                {["admin", "analista", "editor"].includes(user?.role) && (
                    <Link
                        to="/calificaciones/nueva"
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center"
                    >
                        <span className="mr-2">+</span> Nueva Calificación
                    </Link>
                )}
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-wrap gap-4">
                <input
                    type="text"
                    placeholder="Buscar por empresa..."
                    value={filters.search}
                    onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
                />
                <select
                    value={filters.ordering}
                    onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
                >
                    <option value="-fecha">Más recientes</option>
                    <option value="fecha">Más antiguas</option>
                    <option value="-monto_original">Mayor monto</option>
                    <option value="monto_original">Menor monto</option>
                </select>

                <button onClick={() => handleExport('pdf')} className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                    PDF
                </button>
                <button onClick={() => handleExport('excel')} className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
                    Excel
                </button>
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Fecha</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Empresa</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Propietario</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Tipo</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Monto</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Estado</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {calificaciones.map((cal) => (
                            <tr key={cal.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4 text-sm text-gray-600">{cal.fecha}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-800">{cal.empresa_nombre}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">{cal.propietario_nombre}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">
                                    <span className="px-2 py-1 bg-red-50 text-red-600 rounded-full text-xs font-medium">
                                        {cal.tipo}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-800">
                                    ${cal.monto_original.toLocaleString()}
                                </td>
                                <td className="px-6 py-4 text-sm">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${cal.estado === 'aprobada' ? 'bg-green-50 text-green-600' :
                                        cal.estado === 'rechazada' ? 'bg-red-50 text-red-600' :
                                            'bg-yellow-50 text-yellow-600'
                                        }`}>
                                        {cal.estado}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm">
                                    {["admin", "editor"].includes(user?.role) ? (
                                        <Link
                                            to={`/calificaciones/${cal.id}`}
                                            className="text-red-600 hover:text-red-800 font-medium"
                                        >
                                            Editar
                                        </Link>
                                    ) : (
                                        <span className="text-gray-400 cursor-not-allowed">Ver</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {calificaciones.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No hay calificaciones registradas.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Calificaciones;
