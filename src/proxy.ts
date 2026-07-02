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
