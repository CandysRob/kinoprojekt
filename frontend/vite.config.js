import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

// Arenduses suunab Vite /api päringud Djangole, nii et CORS-i pole vaja.
// Dockeris on sihtmärk http://backend:8000 (docker-compose.yml).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.API_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [vue()],
    server: {
      port: Number(env.FRONTEND_PORT || 5173),
      watch: env.WATCH_POLLING === "true" ? { usePolling: true, interval: 300 } : undefined,
      proxy: {
        "/api": { target: apiTarget },
      },
    },
  };
});
