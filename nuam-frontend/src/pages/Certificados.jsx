import React, { useState, useEffect } from "react";
import api from "../api/axios";


const Certificados = () => {
    const [empresas, setEmpresas] = useState([]);
    const [propietarios, setPropietarios] = useState([]);
    const [selectedEmpresa, setSelectedEmpresa] = useState("");
    const [selectedPropietario, setSelectedPropietario] = useState("");
    const [anio, setAnio] = useState(new Date().getFullYear() - 1);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [generatedCert, setGeneratedCert] = useState(null);

    useEffect(() => {
        fetchEmpresas();
    }, []);

    useEffect(() => {
        if (selectedEmpresa) {
            fetchPropietarios(selectedEmpresa);
        } else {
            setPropietarios([]);
        }
    }, [selectedEmpresa]);

    const fetchEmpresas = async () => {
        try {
            const res = await api.get("/empresas/");
            setEmpresas(res.data);
        } catch (err) {
            console.error("Error fetching empresas", err);
        }
    };

    const fetchPropietarios = async (empresaId) => {
        try {
            // Assuming backend supports filtering propietarios by empresa
            // If not, we might need to filter client-side or add a filter to the API
            // For now, let's assume we fetch all and filter client side if API doesn't support it
            // Or better, check the API implementation. 
            // PropietarioViewSet has search_fields but not explicit empresa filter in the plan.
            // I'll assume I can filter or I'll just fetch all for now.
            const res = await api.get("/propietarios/");
            const filtered = res.data.filter(p => p.empresa === parseInt(empresaId));
            setPropietarios(filtered);
        } catch (err) {
            console.error("Error fetching propietarios", err);
        }
    };

    const handleGenerate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        setGeneratedCert(null);

        try {
            const res = await api.post("/certificados70/generar/", {
                empresa_id: selectedEmpresa,
                propietario_id: selectedPropietario,
                anio: anio
            });
            setGeneratedCert(res.data);
            setMessage("Certificado generado exitosamente.");
        } catch (err) {
            console.error(err);
            setMessage("Error al generar el certificado.");
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        if (!generatedCert) return;
        try {
            const response = await api.get(`/certificados70/${generatedCert.id}/descargar/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Cert70_${generatedCert.id}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (err) {
            console.error("Error downloading PDF", err);
            setMessage("Error al descargar el PDF.");
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-8">Emisión de Certificados N°70</h1>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                <form onSubmit={handleGenerate} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Empresa</label>
                            <select
                                value={selectedEmpresa}
                                onChange={(e) => setSelectedEmpresa(e.target.value)}
                                className="w-full p-2 border border-gray-300 rounded focus:ring-red-500 focus:border-red-500"
                                required
                            >
                                <option value="">Seleccione Empresa</option>
                                {empresas.map((emp) => (
                                    <option key={emp.id} value={emp.id}>
                                        {emp.razon_social} ({emp.rut})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Propietario</label>
                            <select
                                value={selectedPropietario}
                                onChange={(e) => setSelectedPropietario(e.target.value)}
                                className="w-full p-2 border border-gray-300 rounded focus:ring-red-500 focus:border-red-500"
                                required
                                disabled={!selectedEmpresa}
                            >
                                <option value="">Seleccione Propietario</option>
                                {propietarios.map((prop) => (
                                    <option key={prop.id} value={prop.id}>
                                        {prop.nombre} ({prop.rut})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Año Comercial</label>
                            <input
                                type="number"
                                value={anio}
                                onChange={(e) => setAnio(e.target.value)}
                                className="w-full p-2 border border-gray-300 rounded focus:ring-red-500 focus:border-red-500"
                                required
                            />
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 transition-colors disabled:opacity-50"
                        >
                            {loading ? "Generando..." : "Generar Certificado"}
                        </button>
                    </div>
                </form>

                {message && (
                    <div className={`mt-4 p-4 rounded ${message.includes("Error") ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
                        {message}
                    </div>
                )}

                {generatedCert && (
                    <div className="mt-8 border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Certificado Generado</h3>
                        <div className="bg-gray-50 p-4 rounded border flex justify-between items-center">
                            <div>
                                <p className="font-medium">Folio: {generatedCert.id}</p>
                                <p className="text-sm text-gray-600">Fecha Emisión: {generatedCert.fecha_emision}</p>
                            </div>
                            <button
                                onClick={handleDownload}
                                className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
                            >
                                Descargar PDF
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Certificados;
