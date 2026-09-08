import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { AMMO_COOKIE, ammoUnlocked } from '@/lib/ammo-gate'

const SUBDOMAIN_MAP: Record<string, string> = {
  'resume':       '/resume.html',
  'lewoof':       '/lewoof-intake.html',
  // NOTE: 'recruithaus' is handled explicitly below (it has a gated /ammo
  // sub-surface), so it is intentionally NOT in this simple one-to-one map.
}

// Hosts with more than one static destination (a reserved sub-path plus a
// default). Checked before SUBDOMAIN_MAP. Added 2026-07-13: todd-call.arcs.care
// /teardown and julia.arcs.care /runtime were previously declared only in
// next.config.ts + vercel.json rewrites. Root cause of the bug this fixes:
// platform-level rewrites are re-applied AFTER this middleware runs, and the
// host's wildcard rule was re-catching the REWRITTEN destination filename
// (e.g. "/todd-teardown.html" contains "teardown" but doesn't start with it,
// so a prefix-only exclusion let the wildcard re-match it on the second pass
// and overwrite this middleware's rewrite back to the default page) — fixed
// in next.config.ts by excluding the substring anywhere, not just as a
// prefix. This middleware entry is kept as the primary, deterministic
// mechanism; next.config.ts's fix is the belt-and-suspenders backstop.
const MULTI_PATH_MAP: Record<string, Record<string, string>> = {
  // saul.arcs.care — interview bundle (2026-09-03): root = prep, /followup = forked battle cards, /resume = viewer.
  // Asset paths are mapped to themselves so the default-page rewrite does not swallow the PDFs/txt.
  'saul':      { '/followup': '/saul-followup.html', '/resume': '/saul-resume-viewer.html', '/saul-resume.pdf': '/saul-resume.pdf', '/saul-cover.pdf': '/saul-cover.pdf', '/saul-resume-ats.txt': '/saul-resume-ats.txt', default: '/saul.html' },
  'todd-call': { '/teardown': '/todd-teardown.html', default: '/todd-call.html' },
  'julia':     { '/runtime': '/julia-runtime.html', default: '/julia.html' },
  'ahmed-ext': { '/report': '/ahmed-ext.html', '/evening': '/ahmed-evening.html', '/seed': '/ahmed-seed.html', default: '/ahmed.html' },
  // prl.arcs.care/status/<seg> status-page family (2026-08-17).
  'prl':       { '/status/catchup': '/prl-status-catchup.html', '/status/crm': '/prl-status-crm.html', '/status/troubleshooting': '/prl-status-troubleshooting.html', '/status/build': '/prl-status-build.html', '/status/tidio': '/prl-status-tidio.html', '/status/progress': '/prl-status-progress.html', '/status/atlas': '/prl-status-atlas.html', '/status/receipt': '/prl-status-receipt.html', default: '/todd-call.html' }, // root = overview (masked); status pages ride under /status/<seg>
  // good.arcs.care/blog/nftt/<slug> — Notes from the Trenches long-form posts (2026-08-18).
  // Rendered via scripts/blog_render.py from _ARTIFACTS/blog/*.md; default stays the goods gallery.
  // Three depth tiers per post, water-fountain first: bare slug = 90-second exec (default depth),
  // /brief = operational, /full = surgical. Firehose is opt-in, one click deeper.
  'good':      { '/blog/nftt/post-1': '/blog-nftt-post-1.html', '/blog/nftt/post-1/brief': '/blog-nftt-post-1.html', '/blog/nftt/post-1/full': '/blog-nftt-post-1.html', '/blog/nftt/post-2/full': '/blog-nftt-post-2.html', '/blog/nftt/post-2': '/blog-nftt-post-2.html', '/blog/nftt/post-3/full': '/blog-nftt-post-3.html', '/blog/nftt/post-3': '/blog-nftt-post-3.html', '/blog/nftt/post-4/full': '/blog-nftt-post-4.html', '/blog/nftt/post-4': '/blog-nftt-post-4.html', '/blog/nftt/take-home-trap': '/blog-nftt-take-home-trap.html', '/blog/nftt/take-home-trap/full': '/blog-nftt-take-home-trap.html', '/blog/nftt/take-home-trap/dossier': '/blog-nftt-take-home-trap-dossier.html', '/blog/nftt/confirmed-not-my-bug': '/blog-nftt-confirmed-not-my-bug.html', '/blog/nftt/confirmed-not-my-bug/full': '/blog-nftt-confirmed-not-my-bug.html', '/blog/nftt/assets-and-liabilities': '/blog-nftt-assets-and-liabilities.html', '/blog/nftt/assets-and-liabilities/full': '/blog-nftt-assets-and-liabilities.html', '/blog/nftt/cheapest-edit-is-a-diff': '/blog-nftt-cheapest-edit-is-a-diff.html', '/blog/nftt/cheapest-edit-is-a-diff/full': '/blog-nftt-cheapest-edit-is-a-diff.html', '/instruments': '/good-instruments.html', '/blog/nftt/the-loop-closes': '/blog-nftt-the-loop-closes.html', '/blog/nftt/the-loop-closes/full': '/blog-nftt-the-loop-closes.html', '/blog/nftt/the-factory-on-itself': '/blog-nftt-the-factory-on-itself.html', '/blog/nftt/the-factory-on-itself/full': '/blog-nftt-the-factory-on-itself.html', '/blog/nftt/schematic-scaffolds': '/blog-nftt-schematic-scaffolds.html', '/blog/nftt/schematic-scaffolds/full': '/blog-nftt-schematic-scaffolds.html', '/blog/nftt': '/blog-nftt-index.html', default: '/good.html' },
}

export default async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // --- Recruiter ammo-tier gate (host-independent) ---------------------------
  // Any /recruithaus-ammo* asset (the gated viewer + PDFs holding comp logic and
  // the founder-lens objection-handling battle cards) requires the unlock cookie
  // on EVERY host. This is deliberate: the recruithaus subdomain rewrite alone is
  // not a gate, because a public/ file is directly fetchable via app.arcs.care/<file>.
  // Checking the cookie here, before host routing, closes that bypass. The gate
  // page itself (/recruithaus-gate.html) uses a different prefix, so it stays open.
  if (pathname.startsWith('/recruithaus-ammo')) {
    const ok = await ammoUnlocked(
      request.cookies.get(AMMO_COOKIE)?.value,
      process.env.RECRUITHAUS_AMMO_PASSWORD,
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/recruithaus-gate.html'
      return NextResponse.rewrite(url)
    }
    return NextResponse.next()
  }

  // Recoil identity gate is now enforced per-route via Auth.js session +
  // ADMIN_EMAILS (src/lib/admin.ts) on every /recoil surface:
  //   /recoil, /recoil/[reportId], /recoil/figma-r001 (server-wrapped),
  //   /recoil/html/[slug]. That is the real gate: per-user, revocable,
  //   fail-closed. The old shared RECOIL_PASSWORD cookie gate was a coarser
  //   second lock (and sat disclosed in git history), so it was removed here,
  //   along with the now-dead /recoil/unlock + /api/recoil/unlock endpoints.
  //   Gates are fail-closed (NODE_ENV !== "development"), matching /warroom.

  const hostname = request.headers.get('host') || ''
  const sub = hostname.split('.')[0]

  const multiPaths = MULTI_PATH_MAP[sub]
  if (multiPaths) {
    if (
      pathname.startsWith('/_next') ||
      pathname.startsWith('/api') ||
      // AEO discovery files must serve the real public/ static files on these
      // hosts, not the host's catch-all `default` page. Without this passthrough
      // good.arcs.care/robots.txt and /sitemap.xml were being rewritten to
      // /good.html (200, but garbage as robots/sitemap), so the sitemap the
      // NFTT robots.txt advertises was unreachable on its own host.
      pathname === '/robots.txt' ||
      pathname === '/sitemap.xml'
    ) {
      return NextResponse.next()
    }
    const dest = multiPaths[pathname] ?? multiPaths.default
    if (pathname.startsWith(dest)) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    return NextResponse.rewrite(url)
  }

  // --- recruithaus.arcs.care ------------------------------------------------
  // Root = the open candidate-positioning pitch (recruithaus.html). /ammo = the
  // gated tier: unlocked -> the ammo viewer; locked -> the passcode gate page.
  // Everything else on the host collapses to the pitch. Asset files under
  // /recruithaus-ammo* are already gated by the host-independent check above.
  if (sub === 'recruithaus') {
    if (
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api')
    ) {
      return NextResponse.next()
    }
    if (pathname === '/ammo' || pathname === '/ammo/') {
      const ok = await ammoUnlocked(
        request.cookies.get(AMMO_COOKIE)?.value,
        process.env.RECRUITHAUS_AMMO_PASSWORD,
      )
      const url = request.nextUrl.clone()
      url.pathname = ok ? '/recruithaus-ammo.html' : '/recruithaus-gate.html'
      return NextResponse.rewrite(url)
    }
    if (pathname.startsWith('/recruithaus-gate.html') || pathname.startsWith('/recruithaus.html')) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = '/recruithaus.html'
    return NextResponse.rewrite(url)
  }

  // --- jobs.arcs.care ------------------------------------------------------
  // The Alert Swipe Board, an app route (src/app/jobs) rather than a static
  // page: the host collapses to /jobs, while the API, auth, and the magic-link
  // sign-in page (/compass, where the gated page redirects) pass through so the
  // sign-in round trip does not loop back into the rewrite.
  if (sub === 'jobs') {
    if (
      pathname.startsWith('/jobs') ||
      pathname.startsWith('/compass') ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api')
    ) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = '/jobs'
    return NextResponse.rewrite(url)
  }

  const dest = SUBDOMAIN_MAP[sub]

  if (dest) {
    const { pathname } = request.nextUrl
    if (
      pathname.startsWith(dest) ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api')
    ) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    return NextResponse.rewrite(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
