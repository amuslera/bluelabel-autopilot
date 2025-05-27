/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Ensure client-side routing works correctly
  trailingSlash: false,
  // Enable static exports for the standalone output
  output: 'standalone',
  // Handle 404s properly
  async rewrites() {
    return [
      {
        source: '/dag/:path*',
        destination: '/dag/:path*',
      },
    ];
  },
  // Handle API routes if needed
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dag/example-run-123',
        permanent: false,
      },
    ];
  },
  // Enable source maps in development
  productionBrowserSourceMaps: false,
  // Configure webpack
  webpack: (config, { isServer }) => {
    // Important: return the modified config
    return config;
  },
};

module.exports = nextConfig;
