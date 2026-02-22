/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        ignored: ['**/node_modules', '**/.git'],
      };
    }
    return config;
  },
};

module.exports = nextConfig;
