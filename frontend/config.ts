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

const config: Config = {
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
  api: {
    upload: "/api/upload",
    sampleQueries: "/api/sample-queries",
    naturalLanguageQuery: "/api/natural-language-query",
    executeQuery: "/api/execute-query",
  },
  maxUploadSize: 10485760, // 10MB in bytes
};

export default config;
