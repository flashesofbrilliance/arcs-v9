import type { NextConfig } from "next";
import path from "path";

// Resolve the actual project root from the main checkout (not worktree)
// Get the git worktree root
const { execSync } = require("child_process");
let projectRoot: string;
try {
  // --git-common-dir returns the shared .git dir, which lives in the main checkout
  // even when running from a worktree. --show-toplevel returns the worktree path,
  // which has no node_modules — this was the source of the Turbopack root error.
  const gitCommonDir = execSync("git rev-parse --git-common-dir", {
    encoding: "utf-8",
    stdio: ["pipe", "pipe", "pipe"],
  }).trim();
  projectRoot = path.resolve(path.dirname(gitCommonDir));
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
        // kelly-interview.arcs.care → public/kelly-interview.html
        { source: "/:path*", destination: "/kelly-interview.html", has: [{ type: "host", value: "kelly-interview.arcs.care" }] },
        // cj-brief.arcs.care → public/cj-brief.html
        { source: "/:path*", destination: "/cj-brief.html", has: [{ type: "host", value: "cj-brief.arcs.care" }] },
        // chase-intro.arcs.care → public/chase-intro.html
        { source: "/:path*", destination: "/chase-intro.html", has: [{ type: "host", value: "chase-intro.arcs.care" }] },
        // chris.arcs.care → public/chris-intro.html (canonical); chris-intro.arcs.care kept as alias
        { source: "/:path*", destination: "/chris-intro.html", has: [{ type: "host", value: "chris.arcs.care" }] },
        { source: "/:path*", destination: "/chris-intro.html", has: [{ type: "host", value: "chris-intro.arcs.care" }] },
        // growth-intel.arcs.care → public/growth-intel.html
        { source: "/:path*", destination: "/growth-intel.html", has: [{ type: "host", value: "growth-intel.arcs.care" }] },
        // todd-call.arcs.care → public/todd-call.html
        { source: "/:path*", destination: "/todd-call.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        // julia.arcs.care → public/julia.html
        { source: "/:path*", destination: "/julia.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        // julia-ext.arcs.care → public/julia-ext.html (sanitized external version for Johnny)
        { source: "/:path*", destination: "/julia-ext.html", has: [{ type: "host", value: "julia-ext.arcs.care" }] },
      ],
      afterFiles: [
        { source: "/compass-kit", destination: "/compass-kit/index.html" },
      ],
      fallback: [],
    };
  },
};

export default nextConfig;
