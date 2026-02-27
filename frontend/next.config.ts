/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // In Docker: INTERNAL_API_URL=http://backend:8000
        // Locally:   INTERNAL_API_URL=http://127.0.0.1:8000  (or leave unset)
        destination: `${process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000'}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig