import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/axios";

const PropietarioForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEditing = !!id;

    const [formData, setFormData] = useState({
        empresa: "",
        rut: "",
        nombre: "",
        calidad: "",
        porcentaje_participacion: "",
    });
    const [empresas, setEmpresas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchEmpresas();
        if (isEditing) {
            fetchPropietario();
        }
    }, [id]);

    const fetchEmpresas = async () => {
        try {
            const response = await api.get("/empresas/");
            setEmpresas(response.data);
        } catch (err) {
            console.error("Error loading empresas", err);
        }
    };

    const fetchPropietario = async () => {
        try {
            const response = await api.get(`/propietarios/${id}/`);
            setFormData({
                ...response.data,
                empresa: response.data.empresa // Assuming backend returns ID or we need to handle object vs ID
            });
        } catch (err) {
            setError("Error al cargar el propietario");
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (isEditing) {
                await api.put(`/propietarios/${id}/`, formData);
            } else {
                await api.post("/propietarios/", formData);
            }
            navigate("/propietarios");
        } catch (err) {
            setError("Error al guardar el propietario");
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">
                {isEditing ? "Editar Propietario" : "Nuevo Propietario"}
            </h1>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Empresa</label>
                    <select
                        name="empresa"
                        value={formData.empresa}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        required
                    >
                        <option value="">Seleccione Empresa</option>
                        {empresas.map((emp) => (
                            <option key={emp.id} value={emp.id}>
                                {emp.razon_social}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">RUT</label>
                    <input
                        type="text"
                        name="rut"
                        value={formData.rut}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                    <input
                        type="text"
                        name="nombre"
                        value={formData.nombre}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Calidad</label>
                    <input
                        type="text"
                        name="calidad"
                        value={formData.calidad}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        placeholder="Ej: Accionista, Usufructuario"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">% Participación (Manual)</label>
                    <input
                        type="number"
                        step="0.01"
                        name="porcentaje_participacion"
                        value={formData.porcentaje_participacion}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        placeholder="Ej: 50.00"
                    />
                    <p className="text-xs text-gray-500 mt-1">Solo para empresas Ltda/EIRL. Para SpA/SA se calcula automáticamente.</p>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                    <button
                        type="button"
                        onClick={() => navigate("/propietarios")}
                        className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                    >
                        {loading ? "Guardando..." : "Guardar"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default PropietarioForm;
