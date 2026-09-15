import { NextRequest, NextResponse } from "next/server"
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

// /prep/[slug]: alias of /warroom/[slug]. Serves INTERNAL pre-call cards from runtime/warroom/ — files that must never
// be world-readable (they were moved out of public/ 2026-07-24 after the audit
// showed everything in public/ is fetchable by filename on every domain).
// Identity gate, not the recoil cookie gate: Auth.js session + ADMIN_EMAILS
// allowlist, same doctrine as src/lib/admin.ts (prod fail-closed, dev
// pass-through for local QA).
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  // Inverted (skip only in explicit dev) so an unset/odd NODE_ENV fails closed.
  if (process.env.NODE_ENV !== "development") {
    const session = await auth()
    if (!isAdmin(session)) {
      // 404, not a sign-in redirect: don't confirm to outsiders that a
      // war-room exists for a guessable counterpart name.
      return new NextResponse("Not found", { status: 404 })
    }
  }

  const { slug } = await params
  const safe = slug.replace(/[^a-zA-Z0-9_-]/g, "")
  const file = path.join(process.cwd(), "runtime", "warroom", `${safe}.html`)

  if (!fs.existsSync(file)) {
    return new NextResponse("Not found", { status: 404 })
  }

  const html = fs.readFileSync(file, "utf-8")
  return new NextResponse(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "private, no-store",
      "X-Robots-Tag": "noindex, nofollow",
    },
  })
}
