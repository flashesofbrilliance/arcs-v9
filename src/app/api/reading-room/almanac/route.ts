// GET /api/reading-room/almanac  - serves the committed Almanac render
// (_ARTIFACTS/atlas/atlas-almanac.html) into the Desk's tenant frame. Gated exactly like
// /recoil (Auth.js session + ADMIN_EMAILS, fail-closed in prod). 404 when the render is absent.
// Seam (brief §7): the render is a LOCAL step (scripts/research_render.py); this route serves
// whatever is committed, it never regenerates.
import fs from "node:fs"
import path from "node:path"
import { Readable } from "node:stream"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

export const dynamic = "force-dynamic"

const RENDER = path.join(process.cwd(), "_ARTIFACTS", "atlas", "atlas-almanac.html")

export async function GET() {
  // Always session + admin (isAdmin is the only place a dev pass-through lives). 404, not 401:
  // the room is not revealed to non-admins.
  const session = await auth()
  if (!session?.user?.email || !isAdmin(session)) return new Response("Not found", { status: 404 })

  let stat: fs.Stats
  try {
    stat = fs.statSync(RENDER)
    if (!stat.isFile()) throw new Error("not a file")
  } catch {
    return new Response("Not found", { status: 404 })
  }

  const body = Readable.toWeb(fs.createReadStream(RENDER)) as ReadableStream
  return new Response(body, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": String(stat.size),
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
