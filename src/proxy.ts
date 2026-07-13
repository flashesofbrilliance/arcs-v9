import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

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
// next.config.ts + vercel.json rewrites, both of which proved unreliable for
// this exact host+specific-path-vs-wildcard shape (verified live across three
// separate fix attempts: reordering, a regex-excluded wildcard, a forced
// no-cache rebuild — all still resolved to the default destination). This
// middleware is the one mechanism already proven to reliably route the six
// hosts above, and it runs earliest in the request lifecycle, so it owns the
// decision directly instead of leaving it to a platform-config layer.
const MULTI_PATH_MAP: Record<string, Record<string, string>> = {
  'todd-call': { '/teardown': '/todd-teardown.html', default: '/todd-call.html' },
  'julia':     { '/runtime': '/julia-runtime.html', default: '/julia.html' },
}

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const hostnameDebug = request.headers.get('host') || ''
  const subDebug = hostnameDebug.split('.')[0]
  // TEMP diagnostic (2026-07-13) — confirms whether this middleware runs at
  // all for a given host/path, decoupled from any routing-logic bugs.
  // Remove once todd-call/teardown + julia/runtime are confirmed fixed.
  const debugHeaders = { 'x-proxy-ran': '1', 'x-proxy-sub': subDebug, 'x-proxy-path': pathname }

  // Recoil cookie gate — private alpha, single user
  if (pathname.startsWith('/recoil') && pathname !== '/recoil/unlock') {
    const session = request.cookies.get('recoil_session')?.value
    const secret = process.env.RECOIL_PASSWORD
    if (!secret || session !== secret) {
      const url = request.nextUrl.clone()
      url.pathname = '/recoil/unlock'
      url.searchParams.set('next', pathname)
      return NextResponse.redirect(url)
    }
  }

  const hostname = request.headers.get('host') || ''
  const sub = hostname.split('.')[0]

  const multiPaths = MULTI_PATH_MAP[sub]
  if (multiPaths) {
    if (pathname.startsWith('/_next') || pathname.startsWith('/api')) {
      const res = NextResponse.next()
      Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
      return res
    }
    const dest = multiPaths[pathname] ?? multiPaths.default
    if (pathname.startsWith(dest)) {
      const res = NextResponse.next()
      Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
      return res
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    const res = NextResponse.rewrite(url)
    Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
    return res
  }

  const dest = SUBDOMAIN_MAP[sub]

  if (dest) {
    const { pathname } = request.nextUrl
    if (
      pathname.startsWith(dest) ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/api')
    ) {
      const res = NextResponse.next()
      Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
      return res
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    const res = NextResponse.rewrite(url)
    Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
    return res
  }

  const res = NextResponse.next()
  Object.entries(debugHeaders).forEach(([k, v]) => res.headers.set(k, v))
  return res
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
