import type { NextConfig } from "next";

// Shared app icon set (src/app/icon.svg, apple-icon.png, manifest.webmanifest,
// opengraph-image.png, public/icon-192/512.png). Every host-wide `/:path((?!...).*)`
// catch-all below would otherwise answer these with its default HTML page, after
// src/proxy.ts (SHARED_ICON_PATH) already let them through. Added 2026-10-05.
const SHARED_ICON_EXCLUDE = "icon\\.svg|icon-192\\.png|icon-512\\.png|apple-icon\\.png|manifest\\.webmanifest|opengraph-image\\.png|";
function withSharedIcons<T extends { source: string }>(rules: T[]): T[] {
  return rules.map((r) =>
    r.source.startsWith("/:path((?!") ? { ...r, source: r.source.replace("/:path((?!", "/:path((?!" + SHARED_ICON_EXCLUDE) } : r,
  );
}

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    // jobs.arcs.care: the rubric + trigger specs are read at request time; the scan HUD is served from _ARTIFACTS.
    "/api/jobs": ["./runtime/specs/*.json"],
    "/api/jobs/swipe": ["./runtime/specs/*.json"],
    "/api/jobs/forge": ["./runtime/specs/*.json"],
    "/jobs": ["./runtime/specs/*.json"],
    "/jobs/scan": ["./_ARTIFACTS/target-role-scan-hud.html", "./runtime/specs/*.json"],
    "/jobs/profile": ["./_ARTIFACTS/profile-scan-hud.html"],
    "/jobs/atlas": ["./_ARTIFACTS/atlas-loader-hud.html"],
    "/jobs/[jobid]": ["./runtime/specs/*.json"],
    "/jobs/lane": ["./runtime/specs/*.json"],
    "/api/jobs/lane": ["./runtime/specs/*.json"],
    // champions lane (gated PII: read server-side only, never emitted to a static/public path)
    "/api/champions": ["./runtime/data/*.tsv"],
    "/api/champions/swipe": ["./runtime/data/*.tsv"],
    "/api/jobs/score": ["./runtime/specs/*.json"],
    "/api/jobs/edit-from-seed": ["./runtime/specs/*.json"],
    "/api/jobs/cover-letter": ["./runtime/specs/*.json"],
    "/jobs/[jobid]/forge": ["./runtime/specs/forge-bundles.json", "./_ARTIFACTS/forge-*/**"],
    "/warroom/[slug]": ["./runtime/warroom/**"],
    "/prep/[slug]": ["./runtime/warroom/**"],
    "/recoil/[reportId]": ["./runtime/recoil/generated/**"],
    // reading room (ADR-075 / desk brief v1.3): the desk manifest + cache manifest are read at
    // request time; the Almanac render is streamed by the gated handler. Without these the
    // standalone Vercel bundle omits the files and the routes 404/500 in prod.
    "/reading-room": ["./runtime/specs/reading-room-manifest.json", "./_ARTIFACTS/atlas/cache-manifest.json"],
    "/reading-room/[tenant]": ["./runtime/specs/reading-room-manifest.json", "./_ARTIFACTS/atlas/cache-manifest.json"],
    "/api/reading-room/almanac": ["./_ARTIFACTS/atlas/atlas-almanac.html"],
    "/api/reading-room/chronicle": ["./_ARTIFACTS/atlas/chronicle.html"],
  },
  async headers() {
    return [
      // wing.arcs.care is unlisted-by-URL: header-level no-crawl backs up the page's
      // robots meta (host-scoped, so the mothership domains stay indexable).
      {
        source: "/:path*",
        has: [{ type: "host", value: "wing.arcs.care" }],
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" }],
      },
      {
        source: "/:path*",
        has: [{ type: "host", value: "scott-cut.arcs.care" }],
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" }],
      },
      // pitch-us counterpart micro-sites are unlisted: never index a live pitch strategy.
      {
        source: "/:path*",
        has: [{ type: "host", value: "sentilink.arcs.care" }],
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" }],
      },
      {
        source: "/:path*",
        has: [{ type: "host", value: "mercury.arcs.care" }],
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" }],
      },
      // zach.md: agent-readable profile (Markdown, AGENTS.md convention). Served as text/markdown at
      // /, /index.md and /llms.txt; indexable on purpose. /proof is HTML (the proof ledger), so the
      // markdown type is scoped to the three markdown paths only.
      ...["/", "/index.md", "/llms.txt"].map((source) => ({
        source,
        has: [{ type: "host" as const, value: "zach.md" }],
        headers: [{ key: "Content-Type", value: "text/markdown; charset=utf-8" }],
      })),
      {
        source: "/index.md",
        has: [{ type: "host", value: "resume.arcs.care" }],
        headers: [{ key: "Content-Type", value: "text/markdown; charset=utf-8" }],
      },
      // self-hosted fonts are content-stable: cache them hard for instant repeat loads.
      {
        source: "/fonts/:path*",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ];
  },
  async rewrites() {
    return {
      beforeFiles: withSharedIcons([
        { source: "/", destination: "/zach.md", has: [{ type: "host", value: "zach.md" }] },
        { source: "/index.md", destination: "/zach.md", has: [{ type: "host", value: "zach.md" }] },
        { source: "/llms.txt", destination: "/zach.md", has: [{ type: "host", value: "zach.md" }] },
        // zach.md/proof: the proof ledger (scripts/proof_emit.py), its data, and the host's own robots + sitemap.
        { source: "/proof", destination: "/proof.html", has: [{ type: "host", value: "zach.md" }] },
        { source: "/proof/claims.json", destination: "/proof-claims.json", has: [{ type: "host", value: "zach.md" }] },
        { source: "/robots.txt", destination: "/zach-robots.txt", has: [{ type: "host", value: "zach.md" }] },
        { source: "/sitemap.xml", destination: "/zach-sitemap.xml", has: [{ type: "host", value: "zach.md" }] },
        { source: "/forge", destination: "/blacksmith-observatory.html", has: [{ type: "host", value: "blacksmith.arcs.care" }] },
        { source: "/observatory", destination: "/blacksmith-observatory.html", has: [{ type: "host", value: "blacksmith.arcs.care" }] },
        { source: "/resume", destination: "/blacksmith-resume-viewer.html", has: [{ type: "host", value: "blacksmith.arcs.care" }] },
        { source: "/:path((?!.*observatory|.*resume|.*\\.woff2|.*\\.png|.*\\.pdf|.*_vercel).*)", destination: "/blacksmith.html", has: [{ type: "host", value: "blacksmith.arcs.care" }] },
        // pitch-us counterpart micro-sites (opportunity at /, operator at /operator). noindex, unlisted.
        { source: "/operator", destination: "/sentilink-operator.html", has: [{ type: "host", value: "sentilink.arcs.care" }] },
        { source: "/:path((?!.*operator|.*\\.woff2|.*\\.png|.*\\.pdf|.*\\.ico|.*_vercel).*)", destination: "/sentilink.html", has: [{ type: "host", value: "sentilink.arcs.care" }] },
        { source: "/operator", destination: "/mercury-operator.html", has: [{ type: "host", value: "mercury.arcs.care" }] },
        { source: "/:path((?!.*operator|.*\\.woff2|.*\\.png|.*\\.pdf|.*\\.ico|.*_vercel).*)", destination: "/mercury.html", has: [{ type: "host", value: "mercury.arcs.care" }] },
        { source: "/forge", destination: "/growth-ai-observatory.html", has: [{ type: "host", value: "growth-ai.arcs.care" }] },
        { source: "/observatory", destination: "/growth-ai-observatory.html", has: [{ type: "host", value: "growth-ai.arcs.care" }] },
        { source: "/resume", destination: "/growth-ai-resume-viewer.html", has: [{ type: "host", value: "growth-ai.arcs.care" }] },
        { source: "/:path((?!.*observatory|.*resume|.*\\.woff2|.*\\.png|.*\\.pdf|.*\\.ico|.*_vercel).*)", destination: "/growth-ai.html", has: [{ type: "host", value: "growth-ai.arcs.care" }] },
        { source: "/:seg(12d-orbital|knowledge-lattice|alexandria|moire|decision-geometry)", destination: "/pf-:seg.html", has: [{ type: "host", value: "playground.arcs.care" }] },
        // api / _next / _vercel excluded (2026-10-06): the decision-geometry explorer fetches /api/geometry on
        // this host, and without the exclusion the catch-all served playground.html to the fetch (same
        // class as the good.arcs.care catch-all bug found 2026-09-13).
        { source: "/:path((?!fonts/|api|_next|_vercel|.*12d-orbital|.*knowledge-lattice|.*alexandria|.*moire|.*decision-geometry).*)", destination: "/playground.html", has: [{ type: "host", value: "playground.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/monolith.html", has: [{ type: "host", value: "monolith.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/forge-pattern.html", has: [{ type: "host", value: "forge.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/forge-cut.html", has: [{ type: "host", value: "forge-cut.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-cut.html", has: [{ type: "host", value: "scott-cut.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/rayan.html", has: [{ type: "host", value: "rayan.arcs.care" }] },
        { source: "/", destination: "/omakase/index.html", has: [{ type: "host", value: "omakase.arcs.care" }] },
        { source: "/atom", destination: "/omakase/atom.html", has: [{ type: "host", value: "omakase.arcs.care" }] },
        { source: "/:path((?!omakase).*)", destination: "/omakase/:path", has: [{ type: "host", value: "omakase.arcs.care" }] },
        { source: "/omakase/atom", destination: "/omakase/atom.html" },
        { source: "/omakase", destination: "/omakase/index.html" },
        { source: "/:path((?!fonts/).*)", destination: "/vishal-combined.html", has: [{ type: "host", value: "vishal.arcs.care" }] },
        { source: "/:seg(teardown|logictree)", destination: "/todd-:seg.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        { source: "/:path((?!.*teardown|.*logictree).*)", destination: "/todd-call.html", has: [{ type: "host", value: "todd-call.arcs.care" }] },
        { source: "/status/:seg(crm|tidio|troubleshooting|build|progress|atlas|receipt|catchup|runbook)", destination: "/prl-status-:seg.html", has: [{ type: "host", value: "prl.arcs.care" }] },
        { source: "/checkpoint", destination: "/prl-checkpoint.html", has: [{ type: "host", value: "prl.arcs.care" }] },
        { source: "/checkpoint.pdf", destination: "/prl-checkpoint.pdf", has: [{ type: "host", value: "prl.arcs.care" }] },
        { source: "/:path((?!.*prl-status-|.*prl-checkpoint).*)", destination: "/todd-call.html", has: [{ type: "host", value: "prl.arcs.care" }] },
        { source: "/runtime", destination: "/julia-runtime.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        { source: "/", destination: "/julia.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        { source: "/:path((?!fonts/|.*runtime).*)", destination: "/julia.html", has: [{ type: "host", value: "julia.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/julia-ext.html", has: [{ type: "host", value: "julia-ext.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/daniel.html", has: [{ type: "host", value: "daniel.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/joe.html", has: [{ type: "host", value: "joe.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/warroom/lyndon-war", has: [{ type: "host", value: "lyndon-war.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/joe-ext.html", has: [{ type: "host", value: "joe-ext.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri.html", has: [{ type: "host", value: "yuri-ext.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri.html", has: [{ type: "host", value: "yuri-sample.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri.html", has: [{ type: "host", value: "yuri-recoil.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri-codex.html", has: [{ type: "host", value: "yuri-codex.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri-diamond.html", has: [{ type: "host", value: "yuri-diamond.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/kam-codex.html", has: [{ type: "host", value: "kam-codex.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/robin-codex.html", has: [{ type: "host", value: "robin-codex.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/robin.html", has: [{ type: "host", value: "robin.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/robin-profile.html", has: [{ type: "host", value: "robin-profile.arcs.care" }] },
        { source: "/:path((?!api/).*)", destination: "/robin-receipt.html", has: [{ type: "host", value: "robin-receipt.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott.html", has: [{ type: "host", value: "scott.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-signal.html", has: [{ type: "host", value: "scott-signal.arcs.care" }] },
        { source: "/signal", destination: "/scott-signal.html", has: [{ type: "host", value: "scott-profile.arcs.care" }] },
        { source: "/:path((?!signal).*)", destination: "/scott-profile.html", has: [{ type: "host", value: "scott-profile.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-codex.html", has: [{ type: "host", value: "scott-codex.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-receipt.html", has: [{ type: "host", value: "scott-receipt.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-teardown.html", has: [{ type: "host", value: "scott-teardown.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scottwitt-cc-teardown.html", has: [{ type: "host", value: "serialized-teardown.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-attraction-field.html", has: [{ type: "host", value: "scott-attraction.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri.html", has: [{ type: "host", value: "yuri-demo.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri.html", has: [{ type: "host", value: "yuri.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/yuri-profile.html", has: [{ type: "host", value: "yuri-profile.arcs.care" }] },
        { source: "/:path((?!api/).*)", destination: "/yuri-receipt.html", has: [{ type: "host", value: "yuri-receipt.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/warroom/brooks", has: [{ type: "host", value: "brooks.arcs.care" }] },
        { source: "/evening", destination: "/ahmed-evening.html", has: [{ type: "host", value: "ahmed-ext.arcs.care" }] },
        { source: "/seed", destination: "/ahmed-seed.html", has: [{ type: "host", value: "ahmed-ext.arcs.care" }] },
        { source: "/report", destination: "/ahmed-ext.html", has: [{ type: "host", value: "ahmed-ext.arcs.care" }] },
        { source: "/:path((?!.*ahmed).*)", destination: "/ahmed.html", has: [{ type: "host", value: "ahmed-ext.arcs.care" }] },
        { source: "/:path((?!api/|omakase).*)", destination: "/louisville.html", has: [{ type: "host", value: "louisville.arcs.care" }] },
        // resume.arcs.care/index.md: the no-JavaScript text copy, generated by scripts/resume_static_emit.mjs.
        { source: "/index.md", destination: "/resume-index.txt", has: [{ type: "host", value: "resume.arcs.care" }] },
        { source: "/google", destination: "/resume-google-gtm.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        { source: "/google-gtm", destination: "/resume-google-gtm.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        { source: "/:path((?!google|proof|resume-index|.*llms|index\\.md|robots\\.txt|sitemap\\.xml).*)", destination: "/resume.html", has: [{ type: "host", value: "resume.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/kiko.html", has: [{ type: "host", value: "kiko.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/warroom/jack-rain", has: [{ type: "host", value: "jack-rain.arcs.care" }] },
        { source: "/:path((?!jack-rain-resume).*)", destination: "/jack-rain-ext.html", has: [{ type: "host", value: "rain.arcs.care" }] },
        { source: "/proposal", destination: "/thetrueai-proposal.html", has: [{ type: "host", value: "thetrueai.arcs.care" }] },
        { source: "/:path((?!.*proposal).*)", destination: "/thetrueai.html", has: [{ type: "host", value: "thetrueai.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/chan.html", has: [{ type: "host", value: "chan.arcs.care" }] },
        { source: "/beliefs", destination: "/belief-log.html", has: [{ type: "host", value: "status.arcs.care" }] },
        { source: "/gauntlets", destination: "/gauntlet-log.html", has: [{ type: "host", value: "status.arcs.care" }] },
        // Exclude the rewrite DESTINATIONS too (belief-log.html, gauntlet-log.html): beforeFiles rewrites
        // chain, so "/beliefs" -> "/belief-log.html" was re-caught here and served status.html.
        // Agent-readable files (2026-10-29): /llms.txt is the host's own; machine paths are excluded from the
        // catch-all so an unknown one 404s instead of answering with the HTML page (tests/unit/llms-routes.test.ts).
        { source: "/llms.txt", destination: "/status-llms.txt", has: [{ type: "host", value: "status.arcs.care" }] },
        { source: "/:path((?!.*belief|.*gauntlet|.*llms|index\\.md|robots\\.txt|sitemap\\.xml).*)", destination: "/status.html", has: [{ type: "host", value: "status.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/resume-tailor.html", has: [{ type: "host", value: "resume-tailor.arcs.care" }] },
        { source: "/blog/nftt", destination: "/blog-nftt-index.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/blog/nftt/:slug/:tier(brief|full)", destination: "/blog-nftt-:slug-:tier.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/blog/nftt/:slug", destination: "/blog-nftt-:slug-exec.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/instruments", destination: "/good-instruments.html", has: [{ type: "host", value: "good.arcs.care" }] },
        // playable cases + the audit offer (2026-09-26). Mirrored in src/proxy.ts 'good'; the page
        // filenames are also excluded from the catch-all below so the proxy's rewrite is not re-swallowed.
        { source: "/audit", destination: "/good-agent-receipts-audit.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/fears", destination: "/good-fears.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/copypasta", destination: "/good-copypasta.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/cases", destination: "/good-case-six-week-outage.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/cases/six-week-outage", destination: "/good-case-six-week-outage.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/cases/reader-who-remembered", destination: "/good-case-reader-who-remembered.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/series/receipts", destination: "/good-series-receipts.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/series/lore", destination: "/good-series-lore.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/series/lore/the-gap", destination: "/good-series-lore-the-gap.html", has: [{ type: "host", value: "good.arcs.care" }] },
        // good.arcs.care catch-all. The negative lookahead MUST also exclude api / _next / _vercel /
        // robots.txt / sitemap.xml: beforeFiles rewrites run after the proxy's passthrough, so without
        // these exclusions every /api/* call (and the NFTT robots/sitemap) on this host was rewritten to
        // good.html (GET 200 HTML, POST 405). Found 2026-09-13 when /api/probe went live.
        { source: "/:path((?!blog|series|good-series-|good-instruments|good-case-|good-agent-receipts-audit|good-agents|good-fears|good-copypasta|api|_next|_vercel|fonts/|.*llms|index\\.md|robots\\.txt|sitemap\\.xml).*)", destination: "/good.html", has: [{ type: "host", value: "good.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/rosetta-shell.html", has: [{ type: "host", value: "rosetta-shell.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/germinate.html", has: [{ type: "host", value: "germinate.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/arcs-field-scan.html", has: [{ type: "host", value: "arcs-field-scan.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/ayesha-ext.html", has: [{ type: "host", value: "ayesha.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/build.html", has: [{ type: "host", value: "build.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/scott-arcs-demo.html", has: [{ type: "host", value: "scott-arcs-demo.arcs.care" }] },
        { source: "/:path((?!fonts/).*)", destination: "/wing.html", has: [{ type: "host", value: "wing.arcs.care" }] },
        // surfaces.arcs.care: the generated catalog of every host above (scripts/surface_catalog_emit.py;
        // --check fails the build when a host here is missing from runtime/specs/surface-catalog.json).
        { source: "/:path((?!fonts/).*)", destination: "/warroom/surfaces", has: [{ type: "host", value: "surfaces.arcs.care" }] },
      ]),
      afterFiles: [
        { source: "/compass-kit", destination: "/compass-kit/index.html" },
        // app.arcs.care/decision-geometry: the same explorer file as playground, but on the app host the
        // Auth.js session cookie (host-only) reaches /api/geometry, so a signed-in owner sees their own
        // receipts at full fidelity; on playground the feed is text-free (public fidelity).
        { source: "/decision-geometry", destination: "/pf-decision-geometry.html" },
        // arcs.care/case-study: neutral (counterpart-agnostic) Ideal Protein case study, forked from conduit-case-study.html 2026-09-28.
        { source: "/case-study", destination: "/case-study.html" },
      ],
      fallback: [],
    };
  },
  async redirects() {
    const retiredFanaticsHosts = [
      "fanatics.arcs.care",
      "chase-intro.arcs.care",
      "chris.arcs.care",
      "chris-intro.arcs.care",
      "cj-brief.arcs.care",
      "growth-intel.arcs.care",
      "token.arcs.care",
      // Retired 2026-10-07 (host prune draft, group A): admin-gated war rooms that already 404'd for
      // everyone but Zach. The pages stay at app.arcs.care/warroom/<slug>; only the hosts go.
      "yuri-war.arcs.care",
      "peter.arcs.care",
      "labelle.arcs.care",
      "labella.arcs.care",
      "kelly-interview.arcs.care",
      "joe-war.arcs.care",
      "jalaja.arcs.care",
      "danny.arcs.care",
      "ahmed.arcs.care",
      "jeben.arcs.care",
    ];
    return [
      { source: "/go-live", destination: "/status/runbook#go-live", permanent: false, has: [{ type: "host", value: "prl.arcs.care" }] },
      ...retiredFanaticsHosts.map((value) => ({
        source: "/:path*",
        has: [{ type: "host" as const, value }],
        destination: "https://arcs.care",
        permanent: true,
      })),
      // surfaces.arcs.care: the admin session cookie is host-only (app.arcs.care), so the
      // gated /warroom/surfaces route 404s on this host. Redirect to where the session lives;
      // redirects run before rewrites, so the surfaces.arcs.care rewrite above stays only so
      // surface_catalog_emit.py keeps the host catalogued as gated.
      {
        source: "/:path*",
        has: [{ type: "host" as const, value: "surfaces.arcs.care" }],
        destination: "https://app.arcs.care/warroom/surfaces",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
