import api from "./axios";

export const requestPasswordReset = async (email) => {
    return api.post("/auth/password-reset/", { email });
};

export const confirmPasswordReset = async (uid, token, password) => {
    return api.post("/auth/password-reset/confirm/", { uid, token, password });
};
