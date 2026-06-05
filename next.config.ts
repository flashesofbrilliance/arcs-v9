import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next 16 / Turbopack: pin the workspace root explicitly. Without this,
  // root inference can resolve to src/app and fail to find next/package.json.
  turbopack: { root: __dirname },
  // /observatory → the static Observatory kit (forensic build-trajectory observability)
  async rewrites() {
    return [{ source: "/observatory", destination: "/observatory/index.html" }];
  },
};

export default nextConfig;
