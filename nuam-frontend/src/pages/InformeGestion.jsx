import { useState, useEffect, useContext } from "react";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const InformeGestion = () => {
    const { user } = useContext(AuthContext);
    const [empresas, setEmpresas] = useState([]);

    // Default dates: First and last day of current year
    const currentYear = new Date().getFullYear();
    const [filters, setFilters] = useState({
        empresa_id: "",
        start_date: `${currentYear}-01-01`,
        end_date: `${currentYear}-12-31`
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchEmpresas();
    }, []);

    const fetchEmpresas = async () => {
        try {
            const response = await api.get("/empresas/");
            setEmpresas(response.data);
            if (response.data.length > 0) {
                // Pre-select first company
                setFilters(prev => ({ ...prev, empresa_id: response.data[0].id }));
            }
        } catch (err) {
            console.error("Error loading empresas", err);
        }
    };

    const handleChange = (e) => {
        setFilters({
            ...filters,
            [e.target.name]: e.target.value
        });
    };

    const handleGenerate = async () => {
        if (!filters.empresa_id) {
            setError("Debe seleccionar una empresa.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await api.get("/reports/gestion/", {
                params: filters,
                responseType: 'blob' // Important for PDF download
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            // Try to extract filename from header or build one
            const empName = empresas.find(e => e.id == filters.empresa_id)?.rut || "reporte";
            link.setAttribute('download', `Informe_${empName}_${filters.start_date}.pdf`);

            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);

        } catch (err) {
            console.error("Error generating report", err);
            setError("Hubo un error al generar el informe. Verifique que existan datos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Informe de Gestión Tributaria</h1>
            <p className="text-gray-500 mb-8">Genera un reporte consolidado de la situación tributaria, incluyendo resumen de participaciones y rentas.</p>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                {error && (
                    <div className="mb-6 bg-red-50 text-red-600 p-4 rounded-lg flex items-center">
                        <span className="mr-2">⚠️</span> {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {/* Empresa Selector */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Empresa</label>
                        <select
                            name="empresa_id"
                            value={filters.empresa_id}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                        >
                            <option value="">Seleccione una empresa...</option>
                            {empresas.map(emp => (
                                <option key={emp.id} value={emp.id}>{emp.razon_social} ({emp.rut})</option>
                            ))}
                        </select>
                    </div>

                    {/* Date Range - Start */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Fecha Inicio</label>
                        <input
                            type="date"
                            name="start_date"
                            value={filters.start_date}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                        />
                    </div>

                    {/* Date Range - End */}
                    <div className="md:col-start-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Fecha Fin</label>
                        <input
                            type="date"
                            name="end_date"
                            value={filters.end_date}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                        />
                    </div>
                </div>

                <div className="border-t pt-6 flex justify-end">
                    <button
                        onClick={handleGenerate}
                        disabled={loading || !filters.empresa_id}
                        className={`
                            px-6 py-3 rounded-lg text-white font-medium flex items-center
                            ${loading || !filters.empresa_id ? 'bg-gray-400 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700 shadow-lg hover:shadow-xl transition-all'}
                        `}
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Generando PDF...
                            </>
                        ) : (
                            <>
                                <span className="mr-2">📄</span> Generar Informe de Gestión
                            </>
                        )}
                    </button>
                </div>
            </div>

            <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-6">
                <h3 className="text-blue-800 font-semibold mb-2">¿Qué incluye este informe?</h3>
                <ul className="text-blue-700 text-sm space-y-1 ml-4 list-disc">
                    <li>Resumen ejecutivo con totales de retiros y dividendos.</li>
                    <li>Listado de Declaraciones Juradas (DJs) procesadas en el periodo.</li>
                    <li>Consolidado de rentas por tipo de imputación (RAI, REX, etc.).</li>
                    <li>Detalle cronológico de participaciones y movimientos.</li>
                    <li>Observaciones automatizadas sobre inconsistencias detectadas.</li>
                </ul>
            </div>
        </div>
    );
};

export default InformeGestion;
