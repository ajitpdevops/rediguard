import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone', // Enable standalone output for Docker
  experimental: {
    turbo: {
      // Enable Turbopack optimizations for faster builds
    }
  }
};

export default nextConfig;
