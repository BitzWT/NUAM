import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const Empresas = () => {
    const [empresas, setEmpresas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchEmpresas();
    }, []);

    const fetchEmpresas = async () => {
        try {
            const response = await api.get("/empresas/");
            setEmpresas(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar empresas");
            setLoading(false);
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Empresas</h1>
                <Link to="/empresas/nueva" className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors">
                    + Nueva Empresa
                </Link>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Razón Social</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RUT</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Régimen</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {empresas.map((empresa) => (
                            <tr key={empresa.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{empresa.razon_social}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{empresa.rut}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{empresa.tipo_sociedad || '-'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{empresa.regimen_tributario}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <Link to={`/empresas/${empresa.id}`} className="text-red-600 hover:text-red-900 mr-4">Editar</Link>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {empresas.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No hay empresas registradas.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Empresas;
