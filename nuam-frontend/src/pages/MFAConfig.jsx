import { useState, useEffect } from "react";
import api from "../api/axios";

const MFAConfig = () => {
    const [qrCode, setQrCode] = useState(null);
    const [code, setCode] = useState("");
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchQRCode();
    }, []);

    const fetchQRCode = async () => {
        try {
            const response = await api.get("/mfa/setup/");
            setQrCode(response.data.qr_code);
        } catch (err) {
            setError("Error al generar código QR");
        }
    };

    const handleVerify = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            await api.post("/mfa/verify/", { code });
            setMessage("MFA activado exitosamente");
            setQrCode(null); // Hide QR after success
        } catch (err) {
            setError("Código inválido");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white rounded-xl shadow-sm border border-gray-100 p-8 mt-10">
            <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">Configurar MFA</h1>

            {message && (
                <div className="bg-green-50 text-green-600 p-4 rounded-lg mb-6 text-center">
                    {message}
                </div>
            )}

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-center">
                    {error}
                </div>
            )}

            {qrCode && !message && (
                <div className="flex flex-col items-center space-y-6">
                    <p className="text-gray-600 text-center">
                        Escanea este código QR con tu aplicación de autenticación (Google Authenticator, Authy, etc).
                    </p>
                    <img src={qrCode} alt="QR Code" className="border p-2 rounded-lg" />

                    <form onSubmit={handleVerify} className="w-full space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Código de Verificación</label>
                            <input
                                type="text"
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-center tracking-widest text-lg"
                                placeholder="000000"
                                maxLength="6"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                        >
                            {loading ? "Verificando..." : "Activar MFA"}
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default MFAConfig;
