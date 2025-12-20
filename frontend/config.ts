interface Config {
  backendUrl: string;
  api: {
    upload: string;
    sampleQueries: string;
    naturalLanguageQuery: string;
    executeQuery: string;
  };
  maxUploadSize: number; // in bytes
}

/**
 * Application configuration
 *
 * Backend URL Configuration:
 * - Local Development: Set NEXT_PUBLIC_BACKEND_URL in .env.local (defaults to http://localhost:8000)
 * - Production: Set NEXT_PUBLIC_BACKEND_URL as an environment variable in your deployment platform
 *   (e.g., Vercel: https://chatdb-backend.fly.dev)
 *
 * The NEXT_PUBLIC_ prefix makes this variable available in the browser.
 * .env.local is gitignored and only used for local development.
 */
const config: Config = {
  // Read from environment variable (set in .env.local for local dev, or deployment env vars for production)
  // Falls back to http://localhost:8000 if not set (useful for local development)
  backendUrl: (
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
  ).replace(/\/$/, ""),
  api: {
    upload: "/api/upload",
    sampleQueries: "/api/sample-queries",
    naturalLanguageQuery: "/api/natural-language-query",
    executeQuery: "/api/execute-query",
  },
  maxUploadSize: 10485760, // 10MB in bytes
};

export default config;
