const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const isDev = window.location.hostname === "dev-app.realwin.ai";
const isProduction = window.location.hostname === "app.realwin.ai";

// Check for environment variable from Vercel
const deployedBackendUrl = import.meta.env.VITE_BACKEND_URL;

export const config = {
  API_BASE_URL: deployedBackendUrl
    ? deployedBackendUrl
    : isLocalhost
      ? "http://localhost:8000"
      : isDev
        ? "https://dev-api.realwin.ai"
        : isProduction
          ? "https://api.realwin.ai"
          : "https://lid-homeland-stunning-another.trycloudflare.com", // Final MAX backend with live data
  TOKEN_EXPIRY_HOURS: 1,
} as const;

export default config;
