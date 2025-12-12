import { useState, useEffect } from "react";
import api from "../api/axios";

const Historial = () => {
    const [auditoria, setAuditoria] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedId, setExpandedId] = useState(null);
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    useEffect(() => {
        fetchAuditoria();
    }, [startDate, endDate]); // Refresh when filters change? Or add "Filter" button? Refreshing implies many API calls. Better add "Filtrar" button?
    // User requested "filter of date". Live update is nicer usually if cheap.
    // Let's stick to live update but maybe debounce or just let it trigger.

    const fetchAuditoria = async () => {
        setLoading(true);
        try {
            let query = "/auditoria/?";
            if (startDate) query += `start_date=${startDate}&`;
            if (endDate) query += `end_date=${endDate}&`;

            const response = await api.get(query);
            setAuditoria(response.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar el historial");
            setLoading(false);
        }
    };

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const handleExport = async (type) => {
        try {
            let query = `/auditoria/export_${type}/?`;
            if (startDate) query += `start_date=${startDate}&`;
            if (endDate) query += `end_date=${endDate}&`;

            const response = await api.get(query, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `auditoria.${type === 'pdf' ? 'pdf' : 'xlsx'}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Error exporting", err);
            setError("Error al exportar archivo");
        }
    };

    if (loading && auditoria.length === 0) return <div>Cargando historial...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                <h1 className="text-3xl font-bold text-gray-800">Historial de Cambios</h1>

                <div className="flex items-center space-x-4 bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <div className="flex flex-col">
                        <label className="text-xs text-gray-500 font-semibold uppercase">Desde</label>
                        <input
                            type="date"
                            className="text-sm bg-white border border-gray-300 rounded px-2 py-1 outline-none focus:border-blue-500"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col">
                        <label className="text-xs text-gray-500 font-semibold uppercase">Hasta</label>
                        <input
                            type="date"
                            className="text-sm bg-white border border-gray-300 rounded px-2 py-1 outline-none focus:border-blue-500"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />
                    </div>
                    {(startDate || endDate) && (
                        <button
                            onClick={() => { setStartDate(""); setEndDate(""); }}
                            className="text-xs text-red-500 hover:underline"
                        >
                            Limpiar
                        </button>
                    )}
                </div>

                <div className="space-x-2">
                    <button onClick={() => handleExport('pdf')} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors shadow-sm font-medium">
                        <i className="fas fa-file-pdf mr-2"></i> PDF
                    </button>
                    <button onClick={() => handleExport('excel')} className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors shadow-sm font-medium">
                        <i className="fas fa-file-excel mr-2"></i> Excel
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entidad</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalle</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {auditoria.map((log) => (
                            <>
                                <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {new Date(log.fecha).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {log.usuario ? `User #${log.usuario}` : "Sistema"}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${log.accion === 'crear' ? 'bg-green-100 text-green-800' :
                                            log.accion === 'modificar' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {log.accion}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.entidad}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{log.entidad_id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 cursor-pointer hover:underline" onClick={() => toggleExpand(log.id)}>
                                        {expandedId === log.id ? "Ocultar" : "Ver Detalle"}
                                    </td>
                                </tr>
                                {expandedId === log.id && (
                                    <tr className="bg-gray-50 animate-fadeIn">
                                        <td colSpan="6" className="px-6 py-4">
                                            <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-60 border border-gray-200">
                                                {JSON.stringify(log.detalle, null, 2)}
                                            </pre>
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
                {auditoria.length === 0 && !loading && (
                    <div className="p-8 text-center text-gray-500">
                        No hay registros de auditoría {startDate || endDate ? "para las fechas seleccionadas" : ""}.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Historial;
