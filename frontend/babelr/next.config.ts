import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: "/",
        destination: "pages/login",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
