/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.infocasas.com.py',
      },
      {
        protocol: 'https',
        hostname: 'images.infocasas.com.py',
      },
    ],
  },
}

module.exports = nextConfig
