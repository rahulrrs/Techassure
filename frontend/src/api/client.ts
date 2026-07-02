import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("techassure_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function demoLogin() {
  const email = "admin@techassure.local";
  const password = "ChangeMe123!";
  try {
    await api.post("/auth/bootstrap-admin", { email, password, full_name: "TechAssure Admin", role: "Admin" });
  } catch {
    // Existing admin is fine for demo bootstrap.
  }
  const { data } = await api.post("/auth/login", { email, password });
  localStorage.setItem("techassure_token", data.access_token);
  return data;
}
