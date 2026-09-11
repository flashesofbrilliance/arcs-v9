// GET /api/reading-room/almanac  - serves the committed Almanac render
// (_ARTIFACTS/atlas/atlas-almanac.html) into the Desk's tenant frame. Gated exactly like
// /recoil (Auth.js session + ADMIN_EMAILS, fail-closed in prod). 404 when the render is absent.
// Seam (brief §7): the render is a LOCAL step (scripts/research_render.py); this route serves
// whatever is committed, it never regenerates.
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

export const dynamic = "force-dynamic"

const RENDER = path.join(process.cwd(), "_ARTIFACTS", "atlas", "atlas-almanac.html")

export async function GET() {
  // Always session + admin, fail-closed with NO NODE_ENV bypass (isAdmin() itself has no dev
  // pass-through: ADMIN_EMAILS unset -> nobody is admin, even in dev). 404, not 401: the room
  // is not revealed to non-admins.
  const session = await auth()
  if (!session?.user?.email || !isAdmin(session)) return new Response("Not found", { status: 404 })

  // Read once as a string, and derive Content-Length from those same bytes (Buffer.byteLength),
  // so the header always matches the body (no statSync/stream TOCTOU: a truncated or swapped file
  // surfaces as a clean 404 before any header is sent, never a mismatched-length 200). The render
  // is a committed ~230KB file, trivially read whole.
  let html: string
  try {
    const stat = fs.statSync(RENDER)
    if (!stat.isFile()) throw new Error("not a file")
    html = fs.readFileSync(RENDER, "utf-8")
  } catch {
    return new Response("Not found", { status: 404 })
  }

  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": String(Buffer.byteLength(html)),
      "X-Frame-Options": "SAMEORIGIN",
      // frame-ancestors supersedes X-Frame-Options in modern browsers; the render's inline
      // scripts need 'unsafe-inline' (self-contained document, data inlined, no network).
      "Content-Security-Policy": "frame-ancestors 'self'; default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:",
      "Referrer-Policy": "no-referrer",
      "X-Content-Type-Options": "nosniff",
      "Cache-Control": "no-store",
    },
  })
}
