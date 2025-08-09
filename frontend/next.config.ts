import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone', // Enable standalone output for Docker
  turbopack: {
    // Enable Turbopack optimizations for faster builds
  },
  webpack: (config) => {
    // Add alias for @ path mapping
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, './src'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/app': path.resolve(__dirname, './src/app'),
    };
    
    // Ensure proper module resolution
    config.resolve.modules = [
      ...config.resolve.modules,
      path.resolve(__dirname, './src'),
    ];
    
    return config;
  },
};

export default nextConfig;
