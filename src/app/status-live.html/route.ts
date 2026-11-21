import fs from "node:fs"
import path from "node:path"
import { NextResponse } from "next/server"
import { GET as pulse } from "@/app/api/pulse/route"
import { fillPulse, type PulseLike } from "@/lib/status-ssr"

// status.arcs.care: public/status.html with the live pulse written into the HTML (src/lib/status-ssr.ts),
// so readers that do not run JavaScript see numbers instead of "loading…". next.config.ts rewrites the
// status host here; the file is traced into the bundle via outputFileTracingIncludes. Same 10-minute
// window as /api/pulse, so this adds no GitHub reads beyond the pulse's own cache.
//
// No `export const revalidate` (ISR) here, 2026-11-21: on an ISR route handler, Next 16 on Vercel caches
// the auto-implemented OPTIONS reply (204, no body) as an empty buffer and rebuilds it with
// `new Response(buffer, { status: 204 })`, which throws "Invalid response status code 204", so every
// OPTIONS on status.arcs.care crashed the function (2 hits, 2026-11-20). As a plain (on-demand) route
// handler OPTIONS gets its normal 204, and the Cache-Control header below keeps the same 10-minute CDN
// window for GET. The pulse's GitHub fetches keep their own `next: { revalidate: 600 }` data cache.
const CACHE_CONTROL = "public, s-maxage=600, stale-while-revalidate=600"

export async function GET() {
  const html = fs.readFileSync(path.join(process.cwd(), "public", "status.html"), "utf8")
  let p: PulseLike | null = null
  try {
    p = (await (await pulse()).json()) as PulseLike
  } catch {
    p = null
  }
  return new NextResponse(fillPulse(html, p), {
    headers: { "content-type": "text/html; charset=utf-8", "Cache-Control": CACHE_CONTROL },
  })
}
