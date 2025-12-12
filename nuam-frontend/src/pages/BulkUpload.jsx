import { useState } from "react";
import api from "../api/axios";

const BulkUpload = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [extractedData, setExtractedData] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setResult(null);
        setError(null);
        setExtractedData(null);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setError(null);

        try {
            let endpoint = "/calificaciones/upload/";
            if (file.name.toLowerCase().endsWith(".pdf")) {
                endpoint = "/calificaciones/upload-pdf/";
            }

            const response = await api.post(endpoint, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            if (file.name.toLowerCase().endsWith(".pdf")) {
                setExtractedData(response.data);
            } else {
                setResult(response.data);
            }
        } catch (err) {
            setError(err.response?.data?.error || "Error al subir el archivo");
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.post("/calificaciones/create-bulk/", {
                data: extractedData
            });
            setResult(response.data);
            setExtractedData(null);
            setFile(null);
        } catch (err) {
            setError(err.response?.data?.error || "Error al guardar datos");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Carga Masiva (DJ1948 / PDF)</h1>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                {!extractedData ? (
                    <>
                        <div className="mb-6">
                            <p className="text-gray-600 mb-4">
                                Sube un archivo Excel (.xlsx), CSV o <strong>PDF (Certificados)</strong>.
                            </p>
                            <ul className="list-disc list-inside text-sm text-gray-500 bg-gray-50 p-4 rounded-lg">
                                <li>Excel/CSV: Columnas requeridas (rut_empresa, razon_social, etc.)</li>
                                <li>PDF: Se extraerán los datos automáticamente para revisión.</li>
                            </ul>
                        </div>

                        <form onSubmit={handleUpload} className="space-y-6">
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-red-500 transition-colors">
                                <input
                                    type="file"
                                    accept=".xlsx, .xls, .csv, .pdf"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    id="file-upload"
                                />
                                <label
                                    htmlFor="file-upload"
                                    className="cursor-pointer flex flex-col items-center"
                                >
                                    <span className="text-4xl mb-2">📂</span>
                                    <span className="text-red-600 font-medium hover:underline">
                                        {file ? file.name : "Seleccionar archivo"}
                                    </span>
                                </label>
                            </div>

                            <button
                                type="submit"
                                disabled={!file || loading}
                                className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 font-medium"
                            >
                                {loading ? "Procesando..." : "Subir y Procesar"}
                            </button>
                        </form>
                    </>
                ) : (
                    <div className="space-y-6">
                        <h2 className="text-xl font-semibold text-gray-800">Revisión de Datos Extraídos</h2>

                        <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">RUT Empresa</label>
                                <input
                                    type="text"
                                    value={extractedData.rut_empresa || ''}
                                    onChange={(e) => setExtractedData({ ...extractedData, rut_empresa: e.target.value })}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">RUT Propietario</label>
                                <input
                                    type="text"
                                    value={extractedData.rut_propietario || ''}
                                    onChange={(e) => setExtractedData({ ...extractedData, rut_propietario: e.target.value })}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Monto</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {extractedData.calificaciones?.map((cal, idx) => (
                                        <tr key={idx}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cal.fecha}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cal.tipo}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{cal.monto}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="flex space-x-4">
                            <button
                                onClick={() => setExtractedData(null)}
                                className="flex-1 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleConfirm}
                                disabled={loading}
                                className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-medium"
                            >
                                {loading ? "Guardando..." : "Confirmar y Guardar"}
                            </button>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="mt-6 bg-red-50 text-red-600 p-4 rounded-lg">
                        {error}
                    </div>
                )}

                {result && (
                    <div className="mt-6">
                        <div className="bg-green-50 text-green-700 p-4 rounded-lg mb-4">
                            <p className="font-bold">Proceso completado</p>
                            <p>Registros creados: {result.created}</p>
                        </div>

                        {result.errors && result.errors.length > 0 && (
                            <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-4">
                                <p className="font-bold text-yellow-800 mb-2">Errores encontrados:</p>
                                <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1 max-h-40 overflow-y-auto">
                                    {result.errors.map((err, idx) => (
                                        <li key={idx}>{err}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default BulkUpload;
