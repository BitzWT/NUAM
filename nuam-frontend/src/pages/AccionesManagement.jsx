import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";

const AccionesManagement = () => {
    const { id } = useParams();
    const [empresa, setEmpresa] = useState(null);
    const [socios, setSocios] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [selectedSocio, setSelectedSocio] = useState(null);

    // Form state
    const [formData, setFormData] = useState({
        cantidad_acciones: "",
        valor_nominal: "",
        fecha_adquisicion: "",
        tipo_propiedad: "pleno"
    });

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const [empresaRes, sociosRes] = await Promise.all([
                api.get(`/empresas/${id}/`),
                api.get(`/empresas/${id}/socios-con-participacion/`)
            ]);
            setEmpresa(empresaRes.data);
            setSocios(sociosRes.data);
            setLoading(false);
        } catch (err) {
            setError("Error al cargar datos");
            setLoading(false);
        }
    };

    const handleOpenModal = (socio) => {
        setSelectedSocio(socio);
        // If socio has shares, fetch details or pre-fill (simplified: assuming 1 action record per socio for now or just creating new)
        // Ideally we should fetch the specific action record if it exists.
        // For now, let's reset form or pre-fill if we had the data in socios list (we have cantidad_acciones)
        setFormData({
            cantidad_acciones: socio.cantidad_acciones || "",
            valor_nominal: empresa.valor_nominal || "",
            fecha_adquisicion: new Date().toISOString().split('T')[0],
            tipo_propiedad: socio.tipo_propiedad || "pleno"
        });
        setShowModal(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Check if we are creating or updating.
            // Since we don't have the action ID in the socio list easily (unless we add it), 
            // we might need to query actions first or assume create.
            // But wait, the requirement says "Permitir editar acciones".
            // I should probably fetch the action for this socio if it exists.

            // Let's try to find if there is an existing action for this socio
            const actionsRes = await api.get(`/empresas/${id}/acciones/?search=${selectedSocio.rut}`);
            const existingAction = actionsRes.data.find(a => a.socio === selectedSocio.id);

            const payload = {
                empresa: id,
                socio: selectedSocio.id,
                cantidad_acciones: formData.cantidad_acciones,
                valor_nominal: formData.valor_nominal,
                fecha_adquisicion: formData.fecha_adquisicion,
                tipo_propiedad: formData.tipo_propiedad
            };

            if (existingAction) {
                await api.put(`/acciones/${existingAction.id}/`, payload);
            } else {
                await api.post("/acciones/", payload);
            }

            setShowModal(false);
            fetchData(); // Refresh data
        } catch (err) {
            alert("Error al guardar acciones: " + (err.response?.data?.detail || err.message));
        }
    };

    if (loading) return <div>Cargando...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    const totalAsignadas = socios.reduce((acc, s) => acc + (s.cantidad_acciones || 0), 0);
    const totalEmpresa = empresa.total_acciones || 0;
    const disponible = totalEmpresa - totalAsignadas;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Gestión de Acciones</h1>
                    <p className="text-gray-600">{empresa.razon_social}</p>
                </div>
                <Link to="/empresas" className="text-gray-600 hover:text-gray-900">
                    Volver
                </Link>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500">Total Acciones</h3>
                    <p className="text-2xl font-bold text-gray-900">{totalEmpresa}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500">Asignadas</h3>
                    <p className="text-2xl font-bold text-blue-600">{totalAsignadas}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500">Disponibles</h3>
                    <p className={`text-2xl font-bold ${disponible < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {disponible}
                    </p>
                </div>
            </div>

            {/* Socios Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Socio</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RUT</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">% Participación</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo Propiedad</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {socios.map((socio) => (
                            <tr key={socio.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{socio.nombre}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{socio.rut}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{socio.cantidad_acciones || 0}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{socio.porcentaje_participacion}%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{socio.tipo_propiedad || "-"}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => handleOpenModal(socio)}
                                        className="text-blue-600 hover:text-blue-900"
                                    >
                                        {socio.cantidad_acciones ? "Editar" : "Asignar"}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {socios.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No hay socios registrados en esta empresa.
                    </div>
                )}
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
                        <h2 className="text-xl font-bold mb-4">
                            {selectedSocio.cantidad_acciones ? "Editar Acciones" : "Asignar Acciones"}
                        </h2>
                        <p className="text-sm text-gray-500 mb-4">Socio: {selectedSocio.nombre}</p>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad Acciones</label>
                                <input
                                    type="number"
                                    value={formData.cantidad_acciones}
                                    onChange={(e) => setFormData({ ...formData, cantidad_acciones: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Valor Nominal</label>
                                <input
                                    type="number"
                                    value={formData.valor_nominal}
                                    onChange={(e) => setFormData({ ...formData, valor_nominal: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Adquisición</label>
                                <input
                                    type="date"
                                    value={formData.fecha_adquisicion}
                                    onChange={(e) => setFormData({ ...formData, fecha_adquisicion: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo Propiedad</label>
                                <select
                                    value={formData.tipo_propiedad}
                                    onChange={(e) => setFormData({ ...formData, tipo_propiedad: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="pleno">Pleno Propietario</option>
                                    <option value="nudo">Nudo Propietario</option>
                                    <option value="usufructo">Usufructuario</option>
                                </select>
                            </div>

                            <div className="flex justify-end space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    Guardar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AccionesManagement;
