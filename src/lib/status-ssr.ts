// status.arcs.care, server-rendered pulse (2026-11-17). The page's four live-pulse cells ship as
// "loading…" and are filled by client JavaScript, so an agent or crawler that does not run scripts
// read a page that looked broken (an outside audit did, 2026-11-17). fillPulse writes the same
// values into the HTML on the server. Client JS still repaints them, and its degraded path is
// unchanged. A section the pulse could not read keeps the page's floor and never shows a false zero.

export type PulseLike = {
  ok?: boolean
  updated?: string
  commit?: { sha: string; date: string } | null
  commitsTotal?: number | null
  prsOpen?: number | null
  deploy?: { state: string; date: string } | null
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
// Absolute time, not "3m ago": a server-rendered relative time is wrong the moment it is cached.
const stamp = (iso: string) => {
  const t = Date.parse(iso)
  return Number.isNaN(t) ? "" : new Date(t).toISOString().slice(0, 16).replace("T", " ") + " UTC"
}

function setText(html: string, id: string, text: string): string {
  const re = new RegExp(`(<div class="[^"]*" id="${id}">)[^<]*(</div>)`)
  return html.replace(re, (_m, a: string, b: string) => a + esc(text) + b)
}

export function fillPulse(html: string, p: PulseLike | null): string {
  let out = html
  if (p && p.ok !== false) {
    if (p.commit) {
      out = setText(out, "pl-commit", p.commit.sha)
      out = setText(out, "pl-commit-when", stamp(p.commit.date))
    }
    if (typeof p.commitsTotal === "number" && p.commitsTotal > 0) {
      const n = p.commitsTotal.toLocaleString("en-US")
      out = setText(out, "pl-count", n)
      out = setText(out, "sv-commits", n)
    }
    if (typeof p.prsOpen === "number") {
      out = setText(out, "pl-prs", String(p.prsOpen))
      out = setText(out, "pl-prs-sub", "open on main")
    }
    if (p.deploy) {
      out = setText(out, "pl-deploy", p.deploy.state.toUpperCase())
      out = setText(out, "pl-deploy-when", stamp(p.deploy.date))
    }
    const anyLive = !!p.commit || !!p.deploy || typeof p.prsOpen === "number"
    if (p.updated && anyLive) out = setText(out, "pulse-foot", `server-rendered from /api/pulse · data as of ${stamp(p.updated)} · refreshes live in the browser`)
  }
  // Any cell the pulse did not fill says so plainly, the same text the client's degraded path uses.
  for (const id of ["pl-commit", "pl-deploy", "pl-prs", "pl-count"]) {
    out = out.replace(new RegExp(`(id="${id}">)loading…(</div>)`), "$1n/a$2")
  }
  return out
}
