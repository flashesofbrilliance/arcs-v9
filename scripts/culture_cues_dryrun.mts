// culture_cues_dryrun.mts — Job Factory slice 1 proof run. READ-ONLY: lists the
// culture phrases the scorer would quote for the top-N scored rows, and which
// rows the guard rail would cap and gate, before any writeback. No model call,
// no POST. Writes a markdown report for a human to eyeball.
//
//   set -a; . ~/.arcs/jobs-pipeline.env; set +a
//   node --experimental-strip-types scripts/culture_cues_dryrun.mts [--limit 20] [--out path.md]
import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { dirname } from "node:path"
import { extractCultureCues, applyCultureGuard, type CultureCues } from "../src/lib/culture-cues.ts"

const argv = process.argv.slice(2)
const arg = (k: string, d: string) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d }
const LIMIT = Number(arg("--limit", "20"))
const OUT = arg("--out", `_STATE/job-search/culture-dryrun-${new Date().toISOString().slice(0, 10)}.md`)
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }

const CUES: CultureCues = JSON.parse(readFileSync("runtime/specs/target-role-scan.json", "utf8")).rubric.culture_cues

// Same fetch path as scripts/jobs_score_sweep.mjs (LinkedIn guest API needs a residential IP).
const strip = (html: string) => {
  const m = html.match(/<div class="show-more-less-html__markup[^"]*">([\s\S]*?)<\/div>/)
  return (m ? m[1] : html).replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()
}
async function fetchJD(row: { jobid: string; url?: string }): Promise<string | null> {
  try {
    if (/^\d+$/.test(row.jobid)) {
      const r = await fetch(`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/${row.jobid}`, { headers: { "user-agent": "Mozilla/5.0" } })
      if (r.ok) { const t = strip(await r.text()); if (t.length > 200) return t }
    }
    if (row.url) { const r = await fetch(row.url, { headers: { "user-agent": "Mozilla/5.0" } }); if (r.ok) { const t = strip(await r.text()); if (t.length > 200) return t } }
  } catch { /* fall through */ }
  return null
}

type Row = { jobid: string; title: string; company: string; url?: string; band: string; composite: number | null; dims: string | null }
const { rows } = (await (await fetch(`${BASE}/api/jobs`, { headers: { "x-jobs-token": TOKEN } })).json()) as { rows: Row[] }
const top = rows.filter((r) => r.band !== "UNSCORED" && r.composite != null).sort((a, b) => (b.composite ?? 0) - (a.composite ?? 0)).slice(0, LIMIT)

const lines: string[] = [`# Culture cues dry run (${new Date().toISOString().slice(0, 10)})`, "", `Top ${top.length} scored rows. Read-only: nothing written back. cap_neg=${CUES.cap_neg}, cap_value=${CUES.cap_value}.`, ""]
let fetched = 0, capped = 0, posRows = 0, negRows = 0, none = 0
for (const r of top) {
  const jd = await fetchJD(r); await new Promise((z) => setTimeout(z, 700))
  if (!jd) { lines.push(`## ${r.company} · ${r.title}`, "", "JD did not fetch; skipped.", ""); continue }
  fetched++
  const hits = extractCultureCues(jd, CUES)
  const dims = (() => { try { return JSON.parse(r.dims ?? "{}") } catch { return {} } })()
  const g = applyCultureGuard(dims, [], hits, CUES)
  const cap = g.gates.length > 0
  if (cap) capped++
  if (hits.pos.length) posRows++
  if (hits.neg.length) negRows++
  if (!hits.pos.length && !hits.neg.length) none++
  lines.push(`## ${r.company} · ${r.title}`, "", `composite ${r.composite} · culture now ${dims.culture ?? "?"}${cap ? ` → **capped to ${g.dims.culture}, grind gate fires (row would go to PASS)**` : ""}`, "")
  for (const h of hits.pos) lines.push(`- \\+ ${h}`)
  for (const h of hits.neg) lines.push(`- \\- ${h}`)
  if (!hits.pos.length && !hits.neg.length) lines.push("- no culture signal in the posting")
  lines.push("")
}
lines.splice(3, 0, `Fetched ${fetched}/${top.length}. Rows with positives: ${posRows}. With negatives: ${negRows}. No signal: ${none}. **Would cap + gate: ${capped}.**`, "")
mkdirSync(dirname(OUT), { recursive: true })
writeFileSync(OUT, lines.join("\n"))
console.log(lines[3]); console.log(`report: ${OUT}`)
