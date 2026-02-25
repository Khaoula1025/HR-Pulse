/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        // This matches all routes starting with /api and sends them to FastAPI
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/:path*', 
      },
    ]
  },
}

module.exports = nextConfig