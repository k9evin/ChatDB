interface Config {
  backendUrl: string;
  api: {
    upload: string;
    explore: string;
    sampleData: string;
    sampleQueries: string;
    naturalLanguageQuery: string;
    executeQuery: string;
  };
  maxUploadSize: number; // in bytes
}

const config: Config = {
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  api: {
    upload: '/upload',
    explore: '/explore',
    sampleData: '/sample-data',
    sampleQueries: '/sample-queries',
    naturalLanguageQuery: '/natural-language-query',
    executeQuery: '/execute-query',
  },
  maxUploadSize: 10485760, // 10MB in bytes
};

export default config;
