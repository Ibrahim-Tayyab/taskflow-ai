/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Required for Docker deployment
  images: {
    unoptimized: true
  },
  async rewrites() {
    // Use INTERNAL_API_URL for server-side requests (Docker network), fallback to public URL
    // CRITICAL: Do NOT use NEXT_PUBLIC_API_URL here as it may point to localhost which fails inside the pod
    const apiUrl = process.env.INTERNAL_API_URL || 'http://todo-backend:8000';
    console.log('Rewrite rule: Proxying /api/* to', apiUrl);
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ]
  }
}

module.exports = nextConfig