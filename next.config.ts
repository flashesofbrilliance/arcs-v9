import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
    return [
      // Subdomain root routing: token.arcs.care/ → /token.html, etc.
      { source: "/", destination: "/token.html",    has: [{ type: "host", value: "token.arcs.care" }] },
      { source: "/", destination: "/cj-brief.html", has: [{ type: "host", value: "cj-brief.arcs.care" }] },
      { source: "/", destination: "/resume.html",   has: [{ type: "host", value: "resume.arcs.care" }] },
      { source: "/compass-kit", destination: "/compass-kit/index.html" },
    ];
  },
};

export default nextConfig;
