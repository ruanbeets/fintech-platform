// src/core/apiClient.js

import axios from "axios";
import { useAuthStore } from "./authStore";
import { apiBaseURL } from "./apiBase";

export const apiClient = axios.create({
  baseURL: apiBaseURL,
});

// Attach token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Optional: global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Auto logout on invalid token
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
