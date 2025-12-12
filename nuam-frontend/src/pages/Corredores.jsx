import { useState, useEffect } from "react";
import api from "../api/axios";

const Corredores = () => {
    const [corredores, setCorredores] = useState([]);
    const [empresas, setEmpresas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Modal State
    const [selectedCorredor, setSelectedCorredor] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedEmpresas, setSelectedEmpresas] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [corredoresRes, empresasRes] = await Promise.all([
                api.get("/corredores/"),
                api.get("/empresas/")
            ]);
            setCorredores(corredoresRes.data);
            setEmpresas(empresasRes.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setError("Error al cargar datos");
            setLoading(false);
        }
    };

    const openAssignmentModal = (corredor) => {
        setSelectedCorredor(corredor);
        // Pre-select current companies
        setSelectedEmpresas(corredor.empresas || []);
        setIsModalOpen(true);
    };

    const handleCheckboxChange = (empresaId) => {
        setSelectedEmpresas(prev => {
            if (prev.includes(empresaId)) {
                return prev.filter(id => id !== empresaId);
            } else {
                return [...prev, empresaId];
            }
        });
    };

    const handleSave = async () => {
        try {
            await api.patch(`/corredores/${selectedCorredor.id}/`, {
                empresas: selectedEmpresas
            });
            // Update local state
            setCorredores(prev => prev.map(c =>
                c.id === selectedCorredor.id ? { ...c, empresas: selectedEmpresas } : c
            ));
            setIsModalOpen(false);
            alert("Empresas asignadas correctamente");
        } catch (err) {
            console.error(err);
            alert("Error al guardar asignación");
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Gestión de Corredores</h1>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">ID</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Empresa Corredora</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Usuario</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Email</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Empresas Asignadas</th>
                            <th className="px-6 py-3 text-sm font-semibold text-gray-600">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {corredores.map((corredor) => (
                            <tr key={corredor.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-sm text-gray-600">#{corredor.id}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-800">{corredor.empresa_corredora}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">{corredor.username}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">{corredor.email}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">
                                    <span className="bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded">
                                        {corredor.empresas?.length || 0}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm">
                                    <button
                                        onClick={() => openAssignmentModal(corredor)}
                                        className="text-purple-600 hover:text-purple-800 font-medium"
                                    >
                                        Asignar Empresas
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {corredores.length === 0 && (
                    <div className="p-8 text-center text-gray-500">No hay corredores registrados.</div>
                )}
            </div>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 flex flex-col max-h-[90vh]">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">
                            Asignar Empresas a {selectedCorredor?.empresa_corredora}
                        </h2>

                        <div className="flex-1 overflow-y-auto mb-4 border border-gray-200 rounded p-2">
                            {empresas.length === 0 ? (
                                <p className="text-gray-500">No hay empresas disponibles.</p>
                            ) : (
                                <div className="space-y-2">
                                    {empresas.map(emp => (
                                        <label key={emp.id} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={selectedEmpresas.includes(emp.id)}
                                                onChange={() => handleCheckboxChange(emp.id)}
                                                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                                            />
                                            <span className="text-sm text-gray-700">{emp.razon_social} ({emp.rut})</span>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="flex justify-end gap-3 mt-auto">
                            <button
                                onClick={() => setIsModalOpen(false)}
                                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSave}
                                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                            >
                                Guardar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Corredores;
