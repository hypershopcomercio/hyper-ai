import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Dev: proxy /api para o Flask local. Em produção o nginx intercepta /api
  // antes de chegar ao Next; se chegar, localhost:5000 é o mesmo destino.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: "http://127.0.0.1:5000/api/:path*" },
    ];
  },
};

export default nextConfig;
