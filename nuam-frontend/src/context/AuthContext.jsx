import { createContext, useState, useEffect } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // Check if user is logged in (e.g., validate token or check localStorage)
        const token = localStorage.getItem("access_token");
        if (token) {
            // TODO: Validate token or fetch user profile from backend
            // For now, we simulate a logged-in user to allow access
            // Ideally, we should decode the token or call /api/me/
            setUser({ username: "Usuario", role: "admin" });
        }
        setLoading(false);
    }, []);

    const login = async (username, password, otp = null, tempToken = null) => {
        try {
            let response;
            if (otp && tempToken) {
                // Step 2: Verify OTP
                response = await api.post("/auth/login/verify/", { temp_token: tempToken, code: otp });
            } else {
                // Step 1: Initial Login
                response = await api.post("/auth/login/", { username, password });
            }

            if (response.data.mfa_required) {
                return response.data; // Return to component to handle UI switch
            }

            localStorage.setItem("access_token", response.data.access);
            localStorage.setItem("refresh_token", response.data.refresh);

            // In a real app, you'd decode the token or use the user data from response
            setUser(response.data.user || { username: username, role: "admin" });

            navigate("/dashboard");
            return response.data;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
        navigate("/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
