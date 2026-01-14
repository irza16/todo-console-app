/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['pydantic', 'fastapi', 'sqlmodel'],
  },
  // Don't interfere with API routes that are handled by Python serverless functions
  async rewrites() {
    return [
      // Pass through all other routes to Next.js
    ];
  },
};

module.exports = nextConfig;