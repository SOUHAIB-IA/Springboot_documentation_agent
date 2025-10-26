/** @type {import('next').NextConfig} */
const nextConfig = {
  
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'export',
   swcMinify: true,
  
  // Clear cache on each build
  cleanDistDir: true,
  
  // Webpack configuration
  webpack: (config, { isServer }) => {
    // Fix module resolution issues
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    
    // Disable caching if issues persist
    config.cache = false;
    
    return config;
  },
  
}

export default nextConfig
