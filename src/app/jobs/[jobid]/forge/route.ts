import fs from "node:fs"
import path from "node:path"
import { NextResponse, type NextRequest } from "next/server"
import { pageViewerAllowed } from "@/lib/jobs"

export const dynamic = "force-dynamic"

// jobs.arcs.care/<jobid>/forge — the PRIVATE viewer for a staged forge bundle.
// A swipe-right builds a bundle into _ARTIFACTS/forge-<slug>/ (two-page cut,
// tailor notes, red-team, kintsugi, a landing page on the Blacksmith base).
// Hosting that page publicly is a separate human-approved step; until then the
// bundle was reachable only on disk. This route serves it behind the same admin
// gate as the board: the staged page itself, or ?file=<name> for any bundle
// file on the allowlist. Never from public/ (world-readable). The jobid->bundle
// map is runtime/specs/forge-bundles.json; both are traced into this route's
// bundle via next.config.ts outputFileTracingIncludes.

type Bundle = { dir: string; slug: string; resume: string }
const OK_EXT: Record<string, string> = {
  ".pdf": "application/pdf", ".png": "image/png", ".html": "text/html; charset=utf-8",
  ".md": "text/plain; charset=utf-8", ".txt": "text/plain; charset=utf-8", ".json": "application/json; charset=utf-8",
}
const NO_STORE = { "cache-control": "private, no-store", "x-robots-tag": "noindex" }

function bundleFor(jobid: string): Bundle | null {
  try {
    const m = JSON.parse(fs.readFileSync(path.join(process.cwd(), "runtime", "specs", "forge-bundles.json"), "utf8"))
    return (m.bundles ?? {})[jobid] ?? null
  } catch { return null }
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ jobid: string }> }) {
  const { jobid } = await ctx.params
  const self = `/jobs/${encodeURIComponent(jobid)}/forge`
  const ok = await pageViewerAllowed()
  if (!ok) return NextResponse.redirect(new URL(`/compass?next=${encodeURIComponent(self)}`, req.url), 307)
  const b = bundleFor(jobid)
  if (!b) return new NextResponse("no staged forge bundle for this row", { status: 404, headers: NO_STORE })
  const root = path.join(process.cwd(), "_ARTIFACTS", b.dir)

  const file = req.nextUrl.searchParams.get("file")
  if (file) {
    // basename only: no traversal, no subdirs, allowlisted extensions
    const name = path.basename(file)
    const ext = path.extname(name).toLowerCase()
    if (name !== file || !OK_EXT[ext]) return new NextResponse("not allowed", { status: 400, headers: NO_STORE })
    const p = path.join(root, name)
    if (!p.startsWith(root + path.sep) || !fs.existsSync(p)) return new NextResponse("not in bundle", { status: 404, headers: NO_STORE })
    const body = new Uint8Array(fs.readFileSync(p))
    return new NextResponse(body, { headers: { ...NO_STORE, "content-type": OK_EXT[ext], "content-disposition": `inline; filename="${name}"` } })
  }

  let html: string
  try { html = fs.readFileSync(path.join(root, "page.html"), "utf8") } catch {
    // No staged landing page (e.g. a resume-only cut): a plain index of the bundle.
    const rows = fs.readdirSync(root).filter((n) => OK_EXT[path.extname(n).toLowerCase()]).sort()
      .map((n) => `<li><a href="${self}?file=${encodeURIComponent(n)}" target="_blank" rel="noopener" style="color:#00F0FF;text-decoration:none">${n}</a></li>`).join("")
    html = `<!doctype html><html><head><meta charset="utf-8"><title>Forge bundle · ${b.slug}</title></head><body style="margin:0;background:#020408;color:#e2e8f0;font:14px/1.5 Inter,system-ui,sans-serif"><main style="max-width:64ch;margin:0 auto;padding:24px 16px"><h1 style="font-size:18px;font-weight:600;margin:0 0 4px">${b.slug}</h1><p style="color:#94a3b8;margin:0 0 16px">Resume-only cut. No landing page was staged for this row.</p><ul style="padding-left:18px">${rows}</ul></main></body></html>`
  }
  // The staged page links its assets at site-root paths meant for public hosting
  // (/forge-<slug>-resume.pdf). Point them at this route's file endpoint instead.
  const files = new Set(fs.readdirSync(root))
  html = html.replace(new RegExp(`href="/forge-${b.slug}-([^"]+)"`, "g"), (_m, rest: string) => {
    const want = rest.replace(/^resume/, `resume-${b.slug}`)
    const alt = want.replace(/\.(txt|pdf)$/, "-ats.$1")
    const name = files.has(want) ? want : files.has(alt) ? alt : want
    return `href="${self}?file=${encodeURIComponent(name)}"`
  })
  // Private top bar: the bundle's working files, one click each. Injected, not in the artifact.
  const link = (n: string, label: string) => files.has(n) ? `<a href="${self}?file=${encodeURIComponent(n)}" target="_blank" rel="noopener">${label}</a>` : ""
  const bar = `<div style="position:sticky;top:0;z-index:9999;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center;padding:8px 16px;background:#0d1117;border-bottom:1px solid #1e293b;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#94a3b8">
<a href="/jobs" style="color:#00F0FF;text-decoration:none">← board</a><span>private bundle · not hosted</span>
<span style="display:flex;gap:14px;margin-left:auto">${[link(b.resume, "resume pdf"), link("TAILOR-NOTES.md", "tailor notes"), link("red-team.md", "red-team"), link("kintsugi.json", "kintsugi"), link("cost.json", "cost"), link("hiring-manager.json", "hiring manager"), link("contact.json", "contact")].filter(Boolean).join("")}</span>
<style>div[style*="z-index:9999"] a{color:#00F0FF;text-decoration:none}</style></div>`
  html = html.replace(/<body([^>]*)>/i, (m) => `${m}${bar}`)
  return new NextResponse(html, { headers: { ...NO_STORE, "content-type": "text/html; charset=utf-8" } })
}
