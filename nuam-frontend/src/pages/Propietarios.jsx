import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const Propietarios = () => {
    const { user } = useContext(AuthContext);
    const [propietarios, setPropietarios] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchPropietarios();
    }, []);

    const fetchPropietarios = async () => {
        try {
            const response = await api.get("/propietarios/");
            setPropietarios(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar propietarios");
            setLoading(false);
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Propietarios</h1>
                {user?.role !== 'tributario' && (
                    <Link to="/propietarios/nueva" className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors">
                        + Nuevo Propietario
                    </Link>
                )}
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RUT</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Calidad</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">% Part.</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {propietarios.map((propietario) => (
                            <tr key={propietario.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{propietario.nombre}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{propietario.rut}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{propietario.empresa}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{propietario.calidad}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{propietario.porcentaje_participacion ? `${propietario.porcentaje_participacion}%` : '-'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    {user?.role !== 'tributario' && (
                                        <Link to={`/propietarios/${propietario.id}`} className="text-red-600 hover:text-red-900 mr-4">Editar</Link>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {propietarios.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No hay propietarios registrados.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Propietarios;
