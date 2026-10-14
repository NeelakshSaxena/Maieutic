import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    const apiUrl = (process.env.API_INTERNAL_URL || "http://api:8000").replace(/\/+$/, "");
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: "/health/:path*",
        destination: `${apiUrl}/health/:path*`,
      },
    ];
  },
};

export default nextConfig;
