import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  withCredentials: true,
});

const refreshAuthToken = async () => {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }
  const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
    refresh_token: refreshToken
  });
  return response.data;
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && 
        !originalRequest._retry &&
        !originalRequest.url.includes('/auth/refresh')) {
      originalRequest._retry = true;
      
      try {
        const tokens = await refreshAuthToken();
        localStorage.setItem("access_token", tokens.access_token);
        localStorage.setItem("refresh_token", tokens.refresh_token);
        originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
        return api(originalRequest);
      } catch (err) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        
        if (!originalRequest.url.includes('/login')) {
          window.location.href = "/login";
        }
        
        return Promise.reject(err);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;