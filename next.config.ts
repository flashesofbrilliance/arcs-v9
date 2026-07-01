import type { NextConfig } from "next";
import path from "path";

// Resolve the actual project root from the main checkout (not worktree)
// Get the git worktree root
const { execSync } = require("child_process");
let projectRoot: string;
try {
  const gitRoot = execSync("git rev-parse --show-toplevel", {
    encoding: "utf-8",
    stdio: ["pipe", "pipe", "pipe"],
  }).trim();
  projectRoot = path.resolve(gitRoot);
} catch {
  // Vercel build env has no .git — process.cwd() is already the project root
  projectRoot = process.cwd();
}

const nextConfig: NextConfig = {
  // Next 16 / Turbopack: pin the workspace root explicitly. Without this,
  // root inference can resolve to src/app and fail to find next/package.json.
  // Using git root to handle worktrees correctly.
  turbopack: { root: projectRoot },
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
    return {
      beforeFiles: [
        // cj-brief.arcs.care → public/cj-brief.html
        { source: "/:path*", destination: "/cj-brief.html", has: [{ type: "host", value: "cj-brief.arcs.care" }] },
        // chase-intro.arcs.care → public/chase-intro.html
        { source: "/:path*", destination: "/chase-intro.html", has: [{ type: "host", value: "chase-intro.arcs.care" }] },
        // growth-intel.arcs.care → public/growth-intel.html
        { source: "/:path*", destination: "/growth-intel.html", has: [{ type: "host", value: "growth-intel.arcs.care" }] },
      ],
      afterFiles: [
        { source: "/compass-kit", destination: "/compass-kit/index.html" },
      ],
      fallback: [],
    };
  },
};

export default nextConfig;
