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
 * Reads backend URL from environment variable NEXT_PUBLIC_BACKEND_URL
 * Set this in your .env.local file:
 *   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  (for local development)
 *   NEXT_PUBLIC_BACKEND_URL=https://chatdb-backend.fly.dev  (for production)
 */
const config: Config = {
  // Read from .env.local or .env file
  // NEXT_PUBLIC_ prefix makes it available in the browser
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
