import { auth } from "@/lib/auth"
import { NextResponse } from "next/server"

const PROTECTED = ["/dashboard", "/receipts"]

export default auth(function proxy(req) {
  const { pathname } = req.nextUrl
  const isProtected = PROTECTED.some((p) => pathname.startsWith(p))
  if (isProtected && !req.auth) {
    const url = req.nextUrl.clone()
    url.pathname = "/compass"
    return NextResponse.redirect(url)
  }
  return NextResponse.next()
})

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
