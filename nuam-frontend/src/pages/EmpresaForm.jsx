import { useState, useEffect, useContext } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/axios";
import { formatRut, validateRut } from "../utils/validators";
import AuthContext from "../context/AuthContext";

const EmpresaForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const isEditing = !!id;

    const [formData, setFormData] = useState({
        rut: "",
        razon_social: "",
        regimen_tributario: "",
        capital_propio_tributario: "",
        inicio_actividades: "",
        tipo_sociedad: "Ltda",
        total_acciones: "",
        valor_nominal: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (user?.role === 'tributario' || user?.role === 'corredor') {
            alert("Acceso restringido: No tiene permisos para crear o editar empresas.");
            navigate("/empresas");
            return;
        }

        if (isEditing) {
            fetchEmpresa();
        }
    }, [id, user]);

    const fetchEmpresa = async () => {
        try {
            const response = await api.get(`/empresas/${id}/`);
            setFormData(response.data);
        } catch (err) {
            setError("Error al cargar la empresa");
        }
    };

    const handleChange = (e) => {
        let { name, value } = e.target;

        if (name === "rut") {
            value = formatRut(value);
        }

        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (!validateRut(formData.rut)) {
                setError("El RUT ingresado no es válido.");
                setLoading(false);
                return;
            }

            if (formData.capital_propio_tributario && formData.capital_propio_tributario < 0) {
                setError("El Capital Propio Tributario debe ser positivo.");
                setLoading(false);
                return;
            }

            if (isSpAorSA) {
                if (formData.total_acciones && formData.total_acciones < 0) {
                    setError("El Total de Acciones debe ser positivo.");
                    setLoading(false);
                    return;
                }
                if (formData.valor_nominal && formData.valor_nominal < 0) {
                    setError("El Valor Nominal debe ser positivo.");
                    setLoading(false);
                    return;
                }
            }

            // Prepare data: convert empty strings to null for optional fields
            const dataToSend = { ...formData };
            const optionalFields = ["capital_propio_tributario", "inicio_actividades", "total_acciones", "valor_nominal", "regimen_tributario"];

            optionalFields.forEach(field => {
                if (dataToSend[field] === "") {
                    dataToSend[field] = null;
                }
            });

            if (isEditing) {
                await api.put(`/empresas/${id}/`, dataToSend);
            } else {
                await api.post("/empresas/", dataToSend);
            }
            navigate("/empresas");
        } catch (err) {
            console.error(err);
            setError(err.response?.data ? JSON.stringify(err.response.data) : "Error al guardar la empresa");
            setLoading(false);
        }
    };

    const isSpAorSA = formData.tipo_sociedad === "SpA" || formData.tipo_sociedad === "SA";

    return (
        <div className="max-w-2xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">
                    {isEditing ? "Editar Empresa" : "Nueva Empresa"}
                </h1>
                {isEditing && isSpAorSA && (
                    <button
                        onClick={() => navigate(`/empresas/${id}/acciones`)}
                        className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
                    >
                        Gestionar Acciones
                    </button>
                )}
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">Razón Social</label>
                        <input
                            type="text"
                            name="razon_social"
                            value={formData.razon_social}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo Sociedad</label>
                        <select
                            name="tipo_sociedad"
                            value={formData.tipo_sociedad || "Ltda"}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        >
                            <option value="Ltda">Limitada</option>
                            <option value="EIRL">EIRL</option>
                            <option value="SpA">SpA</option>
                            <option value="SA">S.A.</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Régimen Tributario</label>
                        <input
                            type="text"
                            name="regimen_tributario"
                            value={formData.regimen_tributario}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Capital Propio Tributario</label>
                        <input
                            type="number"
                            name="capital_propio_tributario"
                            value={formData.capital_propio_tributario}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Inicio Actividades</label>
                        <input
                            type="date"
                            name="inicio_actividades"
                            value={formData.inicio_actividades}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                        />
                    </div>
                </div>

                {isSpAorSA && (
                    <div className="border-t pt-6 mt-6">
                        <h3 className="text-lg font-medium text-gray-800 mb-4">Detalles de Acciones</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Total Acciones</label>
                                <input
                                    type="number"
                                    name="total_acciones"
                                    value={formData.total_acciones}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                                    required={isSpAorSA}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Valor Nominal</label>
                                <input
                                    type="number"
                                    name="valor_nominal"
                                    value={formData.valor_nominal}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
                                />
                            </div>
                        </div>
                    </div>
                )}

                <div className="flex justify-end space-x-3 pt-4 border-t mt-6">
                    <button
                        type="button"
                        onClick={() => navigate("/empresas")}
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

export default EmpresaForm;
