import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import { pageViewerAllowed } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// jobs.arcs.care/scan — the Target-Role Scan HUD (the rubric, archetypes, fit
// filter, and value shape behind every score on the board). It is the internal
// targeting instrument, so it is served from _ARTIFACTS through the same admin
// gate as the board, never from public/ (which is world-readable). The file is
// traced into this route's bundle via next.config.ts outputFileTracingIncludes.
export async function GET(req: NextRequest) {
  const ok = await pageViewerAllowed()
  if (!ok) return NextResponse.redirect(new URL("/compass?next=/jobs/scan", req.url), 307)
  const p = path.join(process.cwd(), "_ARTIFACTS", "target-role-scan-hud.html")
  let html: string
  try { html = fs.readFileSync(p, "utf8") } catch { return new NextResponse("scan HUD not found in this build", { status: 404 }) }
  // A small back-link into the board, injected without touching the artifact file.
  html = html.replace("</body>", '<a href="/jobs" style="position:fixed;left:16px;bottom:16px;font-family:\'JetBrains Mono\',monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#00F0FF;background:#0d1117;border:1px solid #1e293b;padding:8px 12px;border-radius:4px;text-decoration:none">← board</a></body>')
  return new NextResponse(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "private, no-store", "x-robots-tag": "noindex" } })
}
