import { NextRequest, NextResponse } from "next/server"
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

// Serves standalone HTML recoil reports from src/ui-kit/recoil-report/.
// Self-gated (Auth.js session + ADMIN_EMAILS), same as /recoil/[reportId] and
// /warroom/[slug]. Was previously trusting the shared RECOIL_PASSWORD proxy
// gate, which was removed; this route now enforces identity itself.
// 404-not-redirect for outsiders: don't confirm the route exists.
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  if (process.env.NODE_ENV !== "development") {   // fail-closed: unset/test/preview/staging all gate (matches /warroom)
    const session = await auth()
    if (!session?.user?.email || !isAdmin(session)) {
      return new NextResponse("Not found", { status: 404 })
    }
  }
  const { slug } = await params
  const safe = slug.replace(/[^a-zA-Z0-9_-]/g, "")
  const file = path.join(process.cwd(), "src", "ui-kit", "recoil-report", `${safe}.html`)

  if (!fs.existsSync(file)) {
    return new NextResponse("Not found", { status: 404 })
  }

  const html = fs.readFileSync(file, "utf-8")
  return new NextResponse(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  })
}
