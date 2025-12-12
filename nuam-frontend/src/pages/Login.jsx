import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import AuthContext from "../context/AuthContext";

const Login = () => {
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [otp, setOtp] = useState("");
    const [error, setError] = useState("");
    const [mfaRequired, setMfaRequired] = useState(false);
    const [tempToken, setTempToken] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (mfaRequired) {
                // Step 2: Verify OTP
                await login(null, null, otp, tempToken);
                // Navigation handled in AuthContext on success
            } else {
                // Step 1: Initial Login
                const response = await login(username, password);
                if (response?.mfa_required) {
                    setMfaRequired(true);
                    setTempToken(response.temp_token);
                }
            }
        } catch (err) {
            setError(mfaRequired ? "Código inválido" : "Credenciales inválidas");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-xl shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
                    {mfaRequired ? "Verificación MFA" : "Iniciar Sesión"}
                </h2>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!mfaRequired ? (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
                                    required
                                    autoFocus
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none"
                                    required
                                />
                            </div>
                            <div className="text-right">
                                <Link to="/forgot-password" className="text-sm text-red-600 hover:underline">
                                    ¿Olvidaste tu contraseña?
                                </Link>
                            </div>
                        </>
                    ) : (
                        <div>
                            <p className="text-sm text-gray-600 mb-4 text-center">
                                Ingresa el código de 6 dígitos de tu aplicación de autenticación.
                            </p>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Código OTP</label>
                            <input
                                type="text"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-center tracking-widest text-lg"
                                placeholder="000000"
                                maxLength="6"
                                required
                                autoFocus
                            />
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50"
                    >
                        {loading ? "Procesando..." : (mfaRequired ? "Verificar" : "Ingresar")}
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-gray-600">
                    ¿No tienes cuenta?{" "}
                    <Link to="/signup" className="text-red-600 hover:underline font-medium">
                        Regístrate aquí
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Login;
