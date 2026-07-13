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
}

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

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
