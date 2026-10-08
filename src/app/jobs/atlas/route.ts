import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import { pageViewerAllowed } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// jobs.arcs.care/atlas: the Atlas Loader HUD. It ships no data: the page takes an
// arcs.atlas.v1 JSON object from the viewer's own disk (FileReader, nothing fetched or
// stored) and draws the ziggurat. Served from _ARTIFACTS through the same admin gate as
// the board, never from public/. Traced into this route's bundle via next.config.ts.
export async function GET(req: NextRequest) {
  const ok = await pageViewerAllowed()
  if (!ok) return NextResponse.redirect(new URL("/compass?next=/jobs/atlas", req.url), 307)
  const p = path.join(process.cwd(), "_ARTIFACTS", "atlas-loader-hud.html")
  let html: string
  try { html = fs.readFileSync(p, "utf8") } catch { return new NextResponse("atlas loader not found in this build", { status: 404 }) }
  return new NextResponse(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-store", "x-robots-tag": "noindex" } })
}
