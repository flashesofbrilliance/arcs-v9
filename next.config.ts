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
    return {
      beforeFiles: [
        // vishal.arcs.care → public/vishal-combined.html
        { source: "/:path*", destination: "/vishal-combined.html", has: [{ type: "host", value: "vishal.arcs.care" }] },
        // kelly-interview.arcs.care → public/kelly-interview.html
        { source: "/:path*", destination: "/kelly-interview.html", has: [{ type: "host", value: "kelly-interview.arcs.care" }] },
        // todd-call.arcs.care/teardown → public/todd-teardown.html
        // FIX 2026-07-13: this rule and the wildcard below previously both
        // matched `/teardown` (same host, overlapping `/:path*` source) with
        // this one declared first on the theory that beforeFiles respects
        // array order. Verified live in production that it does NOT reliably
        // — the wildcard was winning (x-matched-path: /todd-call.html on a
        // fresh, uncached request). Fixed structurally instead of by
        // reordering: the wildcard's source now excludes "teardown" via a
        // negative-lookahead regex, so only one rule can ever match a given
        // path — no ambiguity for the router to resolve either way. See
        // MEMORY.md and the identical fix below for julia.arcs.care/runtime,
        // the only other host with this specific-path+wildcard shape.
        { source: "/teardown", destination: "/todd-teardown.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        // todd-call.arcs.care root → public/todd-call.html
        { source: "/", destination: "/todd-call.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        // todd-call.arcs.care/anything-else (except /teardown) → public/todd-call.html
        { source: "/:path((?!.*teardown).*)", destination: "/todd-call.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        // labella.arcs.care → public/labella.html
        { source: "/:path*", destination: "/labella.html", has: [{ type: "host", value: "labella.arcs.care" }] },
        // labelle.arcs.care → public/labella.html (common misspelling alias — same content)
        { source: "/:path*", destination: "/labella.html", has: [{ type: "host", value: "labelle.arcs.care" }] },
        // peter.arcs.care → public/peter.html
        { source: "/:path*", destination: "/peter.html", has: [{ type: "host", value: "peter.arcs.care" }] },
        // julia.arcs.care/runtime → public/julia-runtime.html
        // FIX 2026-07-13: same shape as the todd-call.arcs.care/teardown fix
        // above — the wildcard was winning over this exact-path rule despite
        // declaration order (verified live, fresh/uncached request). Fixed
        // structurally: the wildcard's source excludes "runtime" via regex.
        { source: "/runtime", destination: "/julia-runtime.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        // julia.arcs.care root → public/julia.html
        { source: "/", destination: "/julia.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        // julia.arcs.care/anything-else (except /runtime) → public/julia.html
        { source: "/:path((?!.*runtime).*)", destination: "/julia.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        // julia-ext.arcs.care → public/julia-ext.html (sanitized external version)
        { source: "/:path*", destination: "/julia-ext.html", has: [{ type: "host", value: "julia-ext.arcs.care" }] },
        // daniel.arcs.care → public/daniel.html (Crabtree recoil + fractional.city teardown)
        { source: "/:path*", destination: "/daniel.html", has: [{ type: "host", value: "daniel.arcs.care" }] },
        // jeben.arcs.care/debrief → public/jeben-debrief.html (Jul 15 call recoil, pw-gated)
        // Same shape as the julia.arcs.care/runtime fix above: exact-path rule first,
        // wildcard's source excludes "debrief" via negative-lookahead regex so the two
        // rules can never both match the same request.
        { source: "/debrief", destination: "/jeben-debrief.html", has: [{ type: "host", value: "jeben.arcs.care" }] },
        // jeben.arcs.care root/anything-else (except /debrief) → public/jeben.html (Louisville Brands Thread Book, pw-gated)
        { source: "/:path((?!.*debrief).*)", destination: "/jeben.html", has: [{ type: "host", value: "jeben.arcs.care" }] },
        // resume.arcs.care → public/resume.html
        // NOTE: this rule previously existed ONLY inside the live deployment (deployed from a
        // dirty tree, never committed) — verified 2026-07-09 via x-matched-path. Committed here
        // so a clean redeploy from main cannot drop resume.arcs.care routing.
        { source: "/:path*", destination: "/resume.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        // lewoof.arcs.care → public/lewoof.html (Hila / Le Woof Faire setup call recoil, pw-gated "hila")
        { source: "/:path*", destination: "/lewoof.html", has: [{ type: "host", value: "lewoof.arcs.care" }] },
        // danny.arcs.care → public/danny.html (Danny Quick / Kiko pre-call brief + teardown, pw-gated "quick")
        { source: "/:path*", destination: "/danny.html", has: [{ type: "host", value: "danny.arcs.care" }] },
        // danny-ext.arcs.care → public/danny-ext.html (external-facing Kiko teardown + gift, addressed to Danny, pw-gated "danny")
        { source: "/:path*", destination: "/danny-ext.html", has: [{ type: "host", value: "danny-ext.arcs.care" }] },
      ],
      afterFiles: [
        { source: "/compass-kit", destination: "/compass-kit/index.html" },
      ],
      fallback: [],
    };
  },
  // Retired Fanatics-engagement subdomains — 301 to arcs.care rather than a bare 404.
  // A redirect rule is evaluated per-request (unlike the static-file rewrites above,
  // which Vercel's edge CDN can serve from a stale cache even after a new deploy)
  // and gives anyone with an old link a graceful landing instead of a dead page.
  async redirects() {
    const retiredFanaticsHosts = [
      "fanatics.arcs.care",
      "chase-intro.arcs.care",
      "chris.arcs.care",
      "chris-intro.arcs.care",
      "cj-brief.arcs.care",
      "growth-intel.arcs.care",
      "token.arcs.care",
    ];
    return retiredFanaticsHosts.map((value) => ({
      source: "/:path*",
      has: [{ type: "host" as const, value }],
      destination: "https://arcs.care",
      permanent: true,
    }));
  },
};

export default nextConfig;
