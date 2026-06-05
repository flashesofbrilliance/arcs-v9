import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const hostname = request.headers.get('host') || ''

  // resume.arcs.care → rewrite all paths to /resume.html
  if (hostname.startsWith('resume.')) {
    const { pathname } = request.nextUrl
    if (
      pathname.startsWith('/resume.html') ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/api')
    ) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = '/resume.html'
    return NextResponse.rewrite(url)
  }

  return NextResponse.next()
}

export const proxyConfig = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
