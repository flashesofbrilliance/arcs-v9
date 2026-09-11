import { NextRequest, NextResponse } from "next/server"
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"

// The library index: one gated place that lists every war room. Same admin gate
// and same source dir as [slug]/route.ts — no new machinery, just a catalog over
// runtime/warroom/*.html. Your eyes only (Auth.js session + ADMIN_EMAILS; prod
// fail-closed, dev pass-through).
export async function GET(_req: NextRequest) {
  if (process.env.NODE_ENV !== "development") {
    const session = await auth()
    if (!isAdmin(session)) {
      return new NextResponse("Not found", { status: 404 })
    }
  }

  const dir = path.join(process.cwd(), "runtime", "warroom")
  let slugs: string[] = []
  try {
    slugs = fs.readdirSync(dir)
      .filter((f) => f.endsWith(".html"))
      .map((f) => f.replace(/\.html$/, ""))
      .sort()
  } catch {
    slugs = []
  }

  const rows = slugs
    .map((s) => {
      const name = s.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
      return `<a class="room" href="/warroom/${s}"><span class="nm">${name}</span><span class="sl">/${s}</span></a>`
    })
    .join("")

  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>War rooms</title>
<style>
  :root{color-scheme:dark;--bg:#020408;--surface:#0d1117;--surface2:#0a0f16;--border:#1e293b;
    --text:#e2e8f0;--muted:#64748b;--dimmed:#475569;--cyan:#00F0FF;
    --sans:"Inter",system-ui,-apple-system,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,monospace}
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5;padding:56px 24px 72px;
    -webkit-font-smoothing:antialiased}
  .wrap{max-width:640px;margin:0 auto}
  .ey{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--dimmed)}
  h1{font-weight:800;letter-spacing:-.02em;font-size:34px;margin:12px 0 6px}
  .sub{color:var(--muted);font-size:14px;margin-bottom:28px}
  .rooms{display:grid;gap:9px}
  a.room{display:flex;align-items:baseline;justify-content:space-between;gap:14px;text-decoration:none;
    border:1px solid var(--border);border-radius:11px;background:var(--surface);padding:15px 18px;
    transition:border-color .15s,background .15s}
  a.room:hover{border-color:var(--cyan);background:var(--surface2)}
  .nm{font-weight:650;font-size:16px;color:var(--text)}
  .sl{font-family:var(--mono);font-size:11px;color:var(--dimmed)}
  .foot{margin-top:26px;font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--dimmed)}
</style></head><body>
<div class="wrap">
  <div class="ey">ARCS &middot; private</div>
  <h1>War rooms</h1>
  <p class="sub">${slugs.length} rooms. Your eyes only. Each one is a counterpart&rsquo;s read.</p>
  <div class="rooms">${rows || '<p class="sub">No rooms yet.</p>'}</div>
  <div class="foot">runtime/warroom/ &middot; admin-gated &middot; noindex</div>
</div>
</body></html>`

  return new NextResponse(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "private, no-store",
      "X-Robots-Tag": "noindex, nofollow",
    },
  })
}
