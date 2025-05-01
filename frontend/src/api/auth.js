import api from "./axios";

export const authAPI = {
  register: async (email, password, role) => {
    return api.post("/auth/register", { email, password, role });
  },

  verifyEmail: async (token) => {
    return api.get(`/auth/verify-email?token=${token}`);
  },

  login: async (email, password) => {
    const response = await api.post("/auth/login", {
      username: email,
      password,
    });
    localStorage.setItem("access_token", response.data.access_token);
    localStorage.setItem("refresh_token", response.data.refresh_token);
    return response;
  },

  requestPasswordReset: async (email) => {
    return api.post("/auth/request-password-reset", { email });
  },

  resetPassword: async (token, newPassword) => {
    return api.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
};