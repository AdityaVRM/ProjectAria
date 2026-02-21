/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Avoid 404s when "too many open files" breaks the file watcher (dev only)
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        ignored: ['**/node_modules', '**/.git'],
      };
    }
    return config;
  },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://127.0.0.1:8000/:path*' },
    ];
  },
};

module.exports = nextConfig;
