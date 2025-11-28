import { useState } from "react";
import api from "../api/axios";

const BulkUpload = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setResult(null);
        setError(null);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        setLoading(true);
        setError(null);

        try {
            const response = await api.post("/calificaciones/upload/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.error || "Error al subir el archivo");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Carga Masiva (DJ1948)</h1>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                <div className="mb-6">
                    <p className="text-gray-600 mb-4">
                        Sube un archivo Excel (.xlsx) o CSV con las siguientes columnas:
                    </p>
                    <ul className="list-disc list-inside text-sm text-gray-500 bg-gray-50 p-4 rounded-lg">
                        <li>rut_empresa</li>
                        <li>razon_social</li>
                        <li>rut_propietario</li>
                        <li>nombre_propietario</li>
                        <li>fecha (YYYY-MM-DD)</li>
                        <li>tipo_calificacion</li>
                        <li>monto</li>
                    </ul>
                </div>

                <form onSubmit={handleUpload} className="space-y-6">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-red-500 transition-colors">
                        <input
                            type="file"
                            accept=".xlsx, .xls, .csv"
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
