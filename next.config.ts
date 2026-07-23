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
        // todd-call.arcs.care/teardown + /logictree → todd-teardown.html / todd-logictree.html
        // FIX HISTORY, read before touching this host's rules again:
        // 2026-07-13: exact "/teardown" + wildcard both matched `/teardown`;
        // fixed by excluding "teardown" from the wildcard's regex.
        // 2026-07-23: added a third exact rule ("/logictree", tried as
        // "/build-spec" first too) alongside root "/" + wildcard = 4 total rule
        // objects sharing an identical `has:[{host:todd-call.arcs.care}]`
        // condition. That combination reproducibly resolved wrong on Vercel's
        // edge (x-matched-path: /todd-call.html) despite the regex compiling
        // provably correctly locally every time (fresh `next build` +
        // .next/routes-manifest.json inspection), on genuine cache MISSes, and
        // after 60s+ of propagation wait. The file itself deployed fine (served
        // correctly from a different host with no competing wildcard). Root
        // cause never fully confirmed, but every host on this config with a
        // reliable single exact-path exception (jeben/debrief, julia/runtime,
        // thetrueai/proposal) has exactly 2 rule objects sharing its `has`
        // condition, never 3+. Fix: merged the two exact paths into one rule
        // via a capture group + dynamic destination, and dropped the separate
        // root "/" rule (the wildcard's `.*` already matches empty/root) —
        // back down to 2 rule objects total for this host, matching the only
        // proven-reliable shape. If a THIRD path is ever needed here, do not
        // just add a third rule object; extend this capture group instead
        // (e.g. `/:seg(teardown|logictree|newpath)` -> `/todd-:seg.html`) and
        // keep the filename convention (`todd-<seg>.html`) so the dynamic
        // destination keeps working without a 1:1 lookup table.
        { source: "/:seg(teardown|logictree)", destination: "/todd-:seg.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        { source: "/:path((?!.*teardown|.*logictree).*)", destination: "/todd-call.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
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
        // joe.arcs.care → public/joe.html (Joe Kim / HypeLab 6-month decision map, pw-gated "joe")
        { source: "/:path*", destination: "/joe.html", has: [{ type: "host", value: "joe.arcs.care" }] },
        // joe-war.arcs.care → public/joe-war.html (Joe INTERNAL multi-call recoil war-room, pw-gated "cartography" — NEVER share)
        { source: "/:path*", destination: "/joe-war.html", has: [{ type: "host", value: "joe-war.arcs.care" }] },
        // joe-ext.arcs.care → public/joe-ext.html (Joe-facing forward recoil, generated, pw-gated "joe" — safe to share)
        { source: "/:path*", destination: "/joe-ext.html", has: [{ type: "host", value: "joe-ext.arcs.care" }] },
        // yuri-war.arcs.care → public/yuri-war.html (Yuri Kleban / Google INTERNAL pre-call war-room, pw-gated "sextant" — NEVER share)
        { source: "/:path*", destination: "/yuri-war.html", has: [{ type: "host", value: "yuri-war.arcs.care" }] },
        // yuri-ext.arcs.care → public/yuri-ext.html (Yuri-facing capability seed — parallel-tracking taste, pw-gated "yuri" — safe to share)
        { source: "/:path*", destination: "/yuri-ext.html", has: [{ type: "host", value: "yuri-ext.arcs.care" }] },
        // ahmed.arcs.care → public/ahmed.html (Ahmed Elsamadisi / Polyform AI reconnect brief, pw-gated "ahmed")
        { source: "/:path*", destination: "/ahmed.html", has: [{ type: "host", value: "ahmed.arcs.care" }] },
        // ahmed-ext.arcs.care → public/ahmed-ext.html (sanitized Ahmed-facing recoil demo — safe to share)
        { source: "/:path*", destination: "/ahmed-ext.html", has: [{ type: "host", value: "ahmed-ext.arcs.care" }] },
        // jeben.arcs.care/debrief → public/jeben-debrief.html (Jul 15 call recoil, pw-gated)
        // Same shape as the julia.arcs.care/runtime fix above: exact-path rule first,
        // wildcard's source excludes "debrief" via negative-lookahead regex so the two
        // rules can never both match the same request.
        { source: "/debrief", destination: "/jeben-debrief.html", has: [{ type: "host", value: "jeben.arcs.care" }] },
        // jeben.arcs.care root/anything-else (except /debrief) → public/jeben.html (Louisville Brands Thread Book, pw-gated)
        { source: "/:path((?!.*debrief).*)", destination: "/jeben.html", has: [{ type: "host", value: "jeben.arcs.care" }] },
        // resume.arcs.care/google (+ /google-gtm) → public/resume-google-gtm.html (Google Principal GTM AI Tools variant)
        // Same exact-path-vs-wildcard shape as todd/teardown, julia/runtime, jeben/debrief above.
        // NOTE: /google is the primary share path. /google-gtm was the original slug but its edge
        // routing-decision cache got poisoned (requested before its rule went live, during deploy
        // propagation) and Vercel's CDN has no purge API + redeploys don't clear it; kept here so it
        // resolves correctly once that stale entry finally expires. The wildcard below excludes BOTH
        // via a single "starts-with-google" negative-lookahead so neither can collide with the wildcard.
        { source: "/google", destination: "/resume-google-gtm.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        { source: "/google-gtm", destination: "/resume-google-gtm.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        // resume.arcs.care root/anything-else (except /google*) → public/resume.html
        // NOTE: this rule previously existed ONLY inside the live deployment (deployed from a
        // dirty tree, never committed) — verified 2026-07-09 via x-matched-path. Committed here
        // so a clean redeploy from main cannot drop resume.arcs.care routing.
        { source: "/:path((?!google).*)", destination: "/resume.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        // lewoof.arcs.care → public/lewoof.html (Hila / Le Woof Faire setup call recoil, pw-gated "hila")
        { source: "/:path*", destination: "/lewoof.html", has: [{ type: "host", value: "lewoof.arcs.care" }] },
        // danny.arcs.care → public/danny.html (Danny Quick / Kiko pre-call brief + teardown, pw-gated "quick")
        { source: "/:path*", destination: "/danny.html", has: [{ type: "host", value: "danny.arcs.care" }] },
        // kiko.arcs.care → public/kiko.html (external-facing Kiko teardown + gift, addressed to Danny, pw-gated "danny")
        { source: "/:path*", destination: "/kiko.html", has: [{ type: "host", value: "kiko.arcs.care" }] },
        // jalaja.arcs.care → public/jalaja.html (Jalaja Padma / theTrueAI pre-call brief, internal, pw-gated "padma")
        { source: "/:path*", destination: "/jalaja.html", has: [{ type: "host", value: "jalaja.arcs.care" }] },
        // thetrueai.arcs.care/proposal → public/thetrueai-proposal.html (post-call content-strategy sprint proposal, pw-gated "jalaja")
        { source: "/proposal", destination: "/thetrueai-proposal.html", has: [{ type: "host", value: "thetrueai.arcs.care" }] },
        // thetrueai.arcs.care root/anything-else (except /proposal) → public/thetrueai.html (external-facing theTrueAI teardown, addressed to Jalaja, pw-gated "jalaja")
        { source: "/:path((?!.*proposal).*)", destination: "/thetrueai.html", has: [{ type: "host", value: "thetrueai.arcs.care" }] },
        // chan.arcs.care → public/chan.html (ARCS product mission/architecture/roadmap hub for Prophet CDO show-and-tell, ungated)
        { source: "/:path*", destination: "/chan.html", has: [{ type: "host", value: "chan.arcs.care" }] },
        // status.arcs.care → public/status.html (standalone ARCS build-status fork of chan, no Prophet/presentation, ungated)
        { source: "/:path*", destination: "/status.html", has: [{ type: "host", value: "status.arcs.care" }] },
        // ayesha.arcs.care → public/ayesha-ext.html (sanitized external recap, addressed to Ayesha, pw-gated "ayesha")
        // public/ayesha.html (internal Recoil Report) is committed but deliberately NOT routed to any domain.
        { source: "/:path*", destination: "/ayesha-ext.html", has: [{ type: "host", value: "ayesha.arcs.care" }] },
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
