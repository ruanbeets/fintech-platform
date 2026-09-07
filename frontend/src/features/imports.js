import axios from "axios";
import { apiBaseURL } from "../core/apiBase";

const key = "fintrack-demo-session";
export const sessionToken = () => sessionStorage.getItem(key);
export const importClient = axios.create({ baseURL: apiBaseURL, timeout: 90000 });
importClient.interceptors.request.use((config) => {
  const token = sessionToken();
  if (token) config.headers["X-Demo-Session"] = token;
  return config;
});
export async function ensureSession() {
  if (!sessionToken()) {
    const { data } = await importClient.post("/imports/session", {});
    sessionStorage.setItem(key, data.token);
  }
}
export async function deleteSession() {
  if (sessionToken()) {
    try { await importClient.delete("/imports/session"); }
    catch (error) { if (error.response?.status !== 401) throw error; }
  }
  sessionStorage.removeItem(key);
  sessionStorage.removeItem("fintrack-import-result");
}
export function errorMessage(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((entry) => entry.msg).join(" ");
  return "The import service could not be reached. Please retry.";
}
