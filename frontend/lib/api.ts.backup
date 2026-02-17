import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";
import type { SignupRequest, LoginRequest, AuthResponse, Task, TaskCreate, TaskListResponse } from "@/types";

// API base URL
// - For local development: use http://localhost:8000
// - For Vercel serverless: use empty string for same-origin requests
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL ? `${API_URL}/api` : "/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: any) => {
    // Handle errors with clear messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as { detail?: string | Array<{ msg?: string }> };

      if (status === 401) {
        const message = typeof data?.detail === "string" ? data.detail : "Invalid email or password.";
        return Promise.reject(new Error(message));
      }

      if (status === 400) {
        let message = "Validation error.";
        if (typeof data?.detail === "string") {
          message = data.detail;
        } else if (Array.isArray(data?.detail)) {
          message = data.detail.map((d: any) => d.msg || "Validation error").join(", ");
        }
        return Promise.reject(new Error(message));
      }

      if (status === 409) {
        return Promise.reject(new Error("An account with this email already exists."));
      }

      if (status === 404) {
        return Promise.reject(new Error("Resource not found."));
      }

      const message = typeof data?.detail === "string" ? data.detail : `Request failed (${status})`;
      return Promise.reject(new Error(message));
    }

    if (error.code === "ECONNABORTED") {
      return Promise.reject(new Error("Request timed out. Please try again."));
    }

    return Promise.reject(new Error("Unable to connect to the server. Please check your connection."));
  }
);

// Auth API
export const authApi = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/signup", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/login", data);
    return response.data;
  },

  me: async (): Promise<{ id: number; email: string; name: string }> => {
    const response = await api.get("/auth/me");
    return response.data;
  },
};

// Task API
export const taskApi = {
  listTasks: async (userId: number): Promise<TaskListResponse> => {
    const response = await api.get<TaskListResponse>(`/${userId}/tasks`);
    return response.data;
  },

  getTask: async (userId: number, taskId: number): Promise<Task> => {
    const response = await api.get<Task>(`/${userId}/tasks/${taskId}`);
    return response.data;
  },

  createTask: async (userId: number, data: TaskCreate): Promise<Task> => {
    const response = await api.post<Task>(`/${userId}/tasks`, data);
    return response.data;
  },

  updateTask: async (userId: number, taskId: number, data: Partial<TaskCreate>): Promise<Task> => {
    const response = await api.put<Task>(`/${userId}/tasks/${taskId}`, data);
    return response.data;
  },

  toggleComplete: async (userId: number, taskId: number): Promise<Task> => {
    const response = await api.patch<Task>(`/${userId}/tasks/${taskId}/complete`);
    return response.data;
  },

  deleteTask: async (userId: number, taskId: number): Promise<void> => {
    await api.delete(`/${userId}/tasks/${taskId}`);
  },
};

export default api;
