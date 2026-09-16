import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("tutorset_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refresh = localStorage.getItem("tutorset_refresh_token");
    if (
      error.response?.status !== 401 ||
      !refresh ||
      originalRequest?._retry ||
      originalRequest?.url?.includes("/auth/token")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    try {
      const { data } = await axios.post(
        `${apiClient.defaults.baseURL}/auth/token/refresh/`,
        { refresh },
      );
      localStorage.setItem("tutorset_access_token", data.access);
      if (data.refresh) localStorage.setItem("tutorset_refresh_token", data.refresh);
      originalRequest.headers.Authorization = `Bearer ${data.access}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      localStorage.removeItem("tutorset_access_token");
      localStorage.removeItem("tutorset_refresh_token");
      return Promise.reject(refreshError);
    }
  },
);

export default apiClient;
