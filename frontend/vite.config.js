import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import process from "node:process";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const api = env.VITE_API_BASE_URL || env.VITE_API_URL;
  if (command === "build") {
    if (!api) throw new Error("Set VITE_API_BASE_URL to the backend URL before building FinTrack.");
    const url = new URL(api);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) {
      throw new Error("VITE_API_BASE_URL must be an HTTP(S) URL without credentials.");
    }
    if (process.env.RENDER === "true" && (url.protocol !== "https:" || ["localhost", "127.0.0.1"].includes(url.hostname))) {
      throw new Error("Render requires VITE_API_BASE_URL to be the deployed HTTPS backend URL.");
    }
  }
  return { plugins: [react()] };
});
