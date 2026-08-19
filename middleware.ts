import { NextRequest, NextResponse } from "next/server";

// Additive host-routing for the Scott counterpart family, kept OUT of next.config.ts
// intentionally (that file's rewrites array was not safely readable in full via
// available tooling at authoring time -- this middleware is a zero-risk alternative
// that runs independently and does not touch any existing rewrite rule).
// Extend HOST_MAP here for future counterparts if this pattern is adopted more broadly;
// otherwise fold into next.config.ts on a future pass once someone can diff it safely.
const HOST_MAP: Record<string, string> = {
  "scott.arcs.care": "/scott.html",
  "scott-profile.arcs.care": "/scott-profile.html",
  "scott-codex.arcs.care": "/scott-codex.html",
  "scott-receipt.arcs.care": "/scott-receipt.html",
};

export function middleware(req: NextRequest) {
  const host = req.headers.get("host") || "";
  const dest = HOST_MAP[host];
  if (dest && req.nextUrl.pathname === "/") {
    const url = req.nextUrl.clone();
    url.pathname = dest;
    return NextResponse.rewrite(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/"],
};
