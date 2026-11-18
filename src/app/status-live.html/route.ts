import fs from "node:fs"
import path from "node:path"
import { NextResponse } from "next/server"
import { GET as pulse } from "@/app/api/pulse/route"
import { fillPulse, type PulseLike } from "@/lib/status-ssr"

// status.arcs.care: public/status.html with the live pulse written into the HTML (src/lib/status-ssr.ts),
// so readers that do not run JavaScript see numbers instead of "loading…". next.config.ts rewrites the
// status host here; the file is traced into the bundle via outputFileTracingIncludes. Same 10-minute
// window as /api/pulse, so this adds no GitHub reads beyond the pulse's own cache.
export const revalidate = 600

export async function GET() {
  const html = fs.readFileSync(path.join(process.cwd(), "public", "status.html"), "utf8")
  let p: PulseLike | null = null
  try {
    p = (await (await pulse()).json()) as PulseLike
  } catch {
    p = null
  }
  return new NextResponse(fillPulse(html, p), {
    headers: { "content-type": "text/html; charset=utf-8" },
  })
}
