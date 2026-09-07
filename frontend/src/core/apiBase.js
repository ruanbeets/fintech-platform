// Public deployment configuration; the localhost fallback exists only in Vite dev mode.
export const apiBaseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");
