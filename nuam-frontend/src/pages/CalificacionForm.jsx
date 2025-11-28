import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/axios";

const CalificacionForm = () => {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEdit = !!id;

    const [formData, setFormData] = useState({
        empresa: "",
        propietario: "",
        fecha: "",
        tipo: "retiro",
        monto_original: "",
        imputacion: "",
        estado: "vigente",
    });

    const [empresas, setEmpresas] = useState([]);
    const [propietarios, setPropietarios] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDependencies();
        if (isEdit) {
            fetchCalificacion();
        }
    }, [id]);

    const fetchDependencies = async () => {
        try {
            const [empRes, propRes] = await Promise.all([
                api.get("/empresas/"),
                api.get("/propietarios/"),
            ]);
            setEmpresas(empRes.data);
            setPropietarios(propRes.data);
        } catch (err) {
            console.error("Error loading dependencies", err);
        }
    };

    const fetchCalificacion = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/calificaciones/${id}/`);
            setFormData(response.data);
        } catch (err) {
            setError("Error al cargar la calificación");
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            if (isEdit) {
                await api.put(`/calificaciones/${id}/`, formData);
            } else {
                await api.post("/calificaciones/", formData);
            }
            navigate("/calificaciones");
        } catch (err) {
            setError("Error al guardar la calificación");
            setLoading(false);
        }
    };

    if (loading && isEdit) return <div>Cargando...</div>;

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
                {isEdit ? "Editar Calificación" : "Nueva Calificación"}
            </h2>

            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Empresa</label>
                        <select
                            name="empresa"
                            value={formData.empresa}
                            onChange={handleChange}
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">Propietario</label>
                        <select
                            name="propietario"
                            value={formData.propietario}
                            onChange={handleChange}
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                            required
                        >
                            <option value="">Seleccione Propietario</option>
                            {propietarios.map((prop) => (
                                <option key={prop.id} value={prop.id}>
                                    {prop.nombre || prop.rut}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
                        <input
                            type="date"
                            name="fecha"
                            value={formData.fecha}
                            onChange={handleChange}
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                        <select
                            name="tipo"
                            value={formData.tipo}
                            onChange={handleChange}
                            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                            required
                        >
                            <option value="retiro">Retiro</option>
                            <option value="remesa">Remesa</option>
                            <option value="dividendo">Dividendo</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Monto Original</label>
                    <input
                        type="number"
                        name="monto_original"
                        value={formData.monto_original}
                        onChange={handleChange}
                        className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Imputación (Opcional)</label>
                    <input
                        type="text"
                        name="imputacion"
                        value={formData.imputacion || ""}
                        onChange={handleChange}
                        placeholder="Ej: RAI, DDAN"
                        className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                    <button
                        type="button"
                        onClick={() => navigate("/calificaciones")}
                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
                    >
                        {loading ? "Guardando..." : "Guardar"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CalificacionForm;
