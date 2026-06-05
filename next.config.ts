import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // /observatory → the static Observatory kit (forensic build-trajectory observability)
  async rewrites() {
    return [{ source: "/observatory", destination: "/observatory/index.html" }];
  },
};

export default nextConfig;
