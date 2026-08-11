import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyGate, GATE_COOKIE } from '@/lib/statusgate'

const SUBDOMAIN_MAP: Record<string, string> = {
  'token':        '/token.html',
  'cj-brief':     '/cj-brief.html',
  'chase-intro':  '/chase-intro.html',
  'chris-intro':  '/chris-intro.html',
  'fanatics':     '/fanatics.html',
  'resume':       '/resume.html',
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
  'todd-call': { '/teardown': '/todd-teardown.html', default: '/todd-call.html' },
  'julia':     { '/runtime': '/julia-runtime.html', default: '/julia.html' },
  'ahmed-ext': { '/evening': '/ahmed-evening.html', '/seed': '/ahmed-seed.html', default: '/ahmed-ext.html' },
}

// Paths that must stay reachable on status.arcs.care even while veiled — the
// cover page, its unlock/logout routes, framework/asset paths, and the live
// telemetry endpoints the page polls (telemetry is numbers, not the honest
// prose the gate protects; /api/pulse is already public + consumed by chan).
function isStatusOpenPath(pathname: string): boolean {
  return (
    pathname === '/status-gate.html' ||
    pathname.startsWith('/api/gate') ||
    pathname.startsWith('/api/pulse') ||
    pathname.startsWith('/api/field') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname === '/favicon.ico' ||
    pathname === '/robots.txt'
  )
}

// JTBD: veil status.arcs.care from passersby + indexers WITHOUT veiling the 40
//   other *.arcs.care subtenants that share this one Vercel project.
// TOOL-FIT: host-scoped middleware cookie gate over native Vercel Deployment
//   Protection — the native option is project-scoped, so it would gate every
//   subtenant too; a per-domain veil is only reachable in middleware.
// EX-ANTE: predict this fits — same shape as the proven /recoil + /warroom
//   per-surface server gates already in this file (fractal-similar job; scored ex-post).
//   (Decision-provenance receipt; convention in AGENTS.md gotcha 9.)
//
// The passcode gate for status.arcs.care. INTERIM (until the MCP veil): a coarse
// "no passersby, no indexers, not machine-readable" door, not per-person auth.
// Server-side by design — an unauthenticated request (every bot) is rewritten to
// the cover page and NEVER receives status.html, which is what actually makes the
// content machine-unreadable. Fail-closed in prod, pass-through in dev (matches
// the /recoil + /warroom gate convention). Cookie verified with Web Crypto at the
// edge (src/lib/statusgate.ts) — no Node crypto, no npm dep. Delete this whole
// block + the statusgate module when the MCP veil replaces it.
async function statusGate(request: NextRequest): Promise<NextResponse | null> {
  const { pathname } = request.nextUrl
  if (isStatusOpenPath(pathname)) return null
  if (process.env.NODE_ENV === 'development') return null

  const cookie = request.cookies.get(GATE_COOKIE)?.value
  if (await verifyGate(cookie)) return null

  const url = request.nextUrl.clone()
  url.pathname = '/status-gate.html'
  const res = NextResponse.rewrite(url)
  res.headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive, nosnippet')
  return res
}

export default async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  const hostForGate = request.headers.get('host') || ''
  if (hostForGate.split('.')[0] === 'status') {
    const gated = await statusGate(request)
    if (gated) return gated
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
    if (pathname.startsWith('/_next') || pathname.startsWith('/api')) {
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

  const dest = SUBDOMAIN_MAP[sub]

  if (dest) {
    const { pathname } = request.nextUrl
    if (
      pathname.startsWith(dest) ||
      pathname.startsWith('/_next') ||
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
