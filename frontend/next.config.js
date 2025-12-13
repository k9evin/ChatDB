/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  turbopack: {
    resolveAlias: {
      canvas: '',
    },
  },
};

module.exports = nextConfig;
