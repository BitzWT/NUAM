import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const CorredorDashboard = () => {
    const [corredor, setCorredor] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCorredorData();
    }, []);

    const fetchCorredorData = async () => {
        try {
            const response = await api.get("/corredores/me/");
            setCorredor(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar perfil de corredor");
            setLoading(false);
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Panel de Corredor</h1>
                    <p className="text-gray-600">{corredor.empresa_corredora}</p>
                </div>
                <div className="text-sm text-gray-500">
                    Usuario: {corredor.username}
                </div>
            </div>

            <h2 className="text-xl font-bold mb-4 text-gray-800">Empresas Asociadas</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {corredor.empresas && corredor.empresas.length > 0 ? (
                    corredor.empresas.map((empresaId) => (
                        <CompanyCard key={empresaId} id={empresaId} />
                    ))
                ) : (
                    <p className="text-gray-500 col-span-3">No tienes empresas asociadas.</p>
                )}
            </div>
        </div>
    );
};

const CompanyCard = ({ id }) => {
    const [empresa, setEmpresa] = useState(null);

    useEffect(() => {
        const fetchEmpresa = async () => {
            try {
                const res = await api.get(`/empresas/${id}/`);
                setEmpresa(res.data);
            } catch (err) {
                console.error("Error fetching company", id);
            }
        };
        fetchEmpresa();
    }, [id]);

    if (!empresa) return <div className="animate-pulse bg-gray-200 h-32 rounded-xl"></div>;

    return (
        <Link to={`/corredor/empresas/${id}`} className="block group">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all">
                <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center text-red-600 font-bold text-lg">
                        {empresa.razon_social.charAt(0)}
                    </div>
                    <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {empresa.rut}
                    </span>
                </div>
                <h3 className="text-lg font-bold text-gray-800 mb-1 group-hover:text-red-600 transition-colors">
                    {empresa.razon_social}
                </h3>
                <p className="text-sm text-gray-500">{empresa.tipo_sociedad}</p>
            </div>
        </Link>
    );
};

export default CorredorDashboard;
