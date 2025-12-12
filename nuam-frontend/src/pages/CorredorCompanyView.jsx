import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";

const CorredorCompanyView = () => {
    const { id } = useParams();
    const [empresa, setEmpresa] = useState(null);
    const [calificaciones, setCalificaciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const [empresaRes, califRes] = await Promise.all([
                api.get(`/empresas/${id}/`),
                api.get(`/calificaciones/?search=${id}`) // Assuming search filters by company ID or name. Backend search_fields includes empresa__razon_social.
                // Better to filter by company ID if possible, but search might work if unique enough.
                // Ideally backend should support filtering by exact ID.
                // Let's assume search works for now or we filter client side if needed.
                // Actually, the backend search_fields are ["empresa__razon_social", "propietario__rut"].
                // So searching by ID might not work directly unless added.
                // However, the Corredor can only see their companies.
                // If I call /calificaciones/ it returns all for that corredor.
                // I should filter client side or add a filter backend for company_id.
            ]);

            setEmpresa(empresaRes.data);

            // Filter qualifications for this specific company client-side for now, 
            // as the endpoint returns all qualifications for the corredor's companies.
            const allCalifs = await api.get('/calificaciones/');
            const companyCalifs = allCalifs.data.filter(c => c.empresa === parseInt(id));
            setCalificaciones(companyCalifs);

            setLoading(false);
        } catch (err) {
            setError("Error al cargar datos de la empresa");
            setLoading(false);
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">{empresa.razon_social}</h1>
                    <p className="text-gray-600">RUT: {empresa.rut}</p>
                </div>
                <Link to="/corredor/dashboard" className="text-gray-600 hover:text-gray-900">
                    Volver al Dashboard
                </Link>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
                <h2 className="text-lg font-bold mb-4">Detalles de la Empresa</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <p className="text-sm text-gray-500">Tipo Sociedad</p>
                        <p className="font-medium">{empresa.tipo_sociedad}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Régimen Tributario</p>
                        <p className="font-medium">{empresa.regimen_tributario || "-"}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Capital Propio</p>
                        <p className="font-medium">${(empresa.capital_propio_tributario || 0).toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Total Acciones</p>
                        <p className="font-medium">{(empresa.total_acciones || 0).toLocaleString()}</p>
                    </div>
                </div>
            </div>

            <h2 className="text-xl font-bold mb-4 text-gray-800">Calificaciones Tributarias</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Fecha</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Propietario</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Tipo</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Monto</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Estado</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {calificaciones.map((cal) => (
                            <tr key={cal.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4 text-sm text-gray-600">{cal.fecha}</td>
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
                            </tr>
                        ))}
                    </tbody>
                </table>
                {calificaciones.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No hay calificaciones registradas para esta empresa.
                    </div>
                )}
            </div>
        </div>
    );
};

export default CorredorCompanyView;
