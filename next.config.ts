import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next 16 / Turbopack: pin the workspace root explicitly. Without this,
  // root inference can resolve to src/app and fail to find next/package.json.
  turbopack: { root: __dirname },
  // /compass-kit → the static Compass UI kit preview (cosmetic; mock pipeline, no backend)
  //
  // /observatory used to rewrite here too, to a static demo at public/observatory/index.html.
  // That entry is removed: src/app/observatory/page.tsx now exists as a real App Router page,
  // and per Next.js's documented rewrite order (plain-array rewrites are applied "after
  // checking the filesystem (pages and /public files) and before dynamic routes" —
  // node_modules/next/dist/docs/01-app/03-api-reference/05-config/01-next-config-js/rewrites.md),
  // the real page route is matched first and the rewrite was already dead/unreachable code.
  // Removed for clarity rather than left as misleading dead config.
  async rewrites() {
    return [{ source: "/compass-kit", destination: "/compass-kit/index.html" }];
  },
};

export default nextConfig;
