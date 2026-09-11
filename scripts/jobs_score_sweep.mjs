#!/usr/bin/env node
// jobs_score_sweep.mjs — JD read + score worker (driver half).
// Fetches each UNSCORED row's JD as plain text locally (LinkedIn guest API is
// blocked from datacenter IPs, so the fetch must run from a residential path),
// then posts batches to POST /api/jobs/score, which holds the prod key and does
// the model call + writeback. Cost: Haiku, temp 0, cached rubric prefix, batched.
//
//   node scripts/jobs_score_sweep.mjs --dry-run [--limit N]   # fetch only, no model
//   node scripts/jobs_score_sweep.mjs --limit 5               # proof run
//   node scripts/jobs_score_sweep.mjs                         # drain the backlog
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE (default https://jobs.arcs.care).

const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const DRY = has("--dry-run")
const LIMIT = Number(arg("--limit", 0)) || 0
const BATCH = Number(arg("--batch", 8))
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }

const strip = (html) => {
  const m = html.match(/<div class="show-more-less-html__markup[^"]*">([\s\S]*?)<\/div>/)
  const body = m ? m[1] : html
  return body.replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()
}
async function fetchJD(row) {
  try {
    if (/^\d+$/.test(row.jobid)) {
      const r = await fetch(`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/${row.jobid}`, { headers: { "user-agent": "Mozilla/5.0" } })
      if (r.ok) { const t = strip(await r.text()); if (t.length > 200) return t }
    }
    if (row.url) { const r = await fetch(row.url, { headers: { "user-agent": "Mozilla/5.0" } }); if (r.ok) { const t = strip(await r.text()); if (t.length > 200) return t } }
  } catch { /* fall through */ }
  return null
}

async function main() {
  const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  let unscored = rows.filter((r) => r.band === "UNSCORED")
  if (LIMIT) unscored = unscored.slice(0, LIMIT)
  console.log(`unscored to process: ${unscored.length}${DRY ? " (DRY)" : ""}`)

  let fetched = 0, nofetch = 0
  for (const r of unscored) { r.jd = await fetchJD(r); if (r.jd) fetched++; else nofetch++; await new Promise(z=>setTimeout(z,700)) }
  const scorable = unscored.filter((r) => r.jd)
  console.log(`JDs fetched: ${fetched} · fetch-failed: ${nofetch}`)
  if (DRY) { console.log(`DRY: would score ${scorable.length} in ${Math.ceil(scorable.length / BATCH)} batches.`); return }

  let scored = 0, inTok = 0, outTok = 0, cacheRead = 0, top = []
  for (let i = 0; i < scorable.length; i += BATCH) {
    const batch = scorable.slice(i, i + BATCH).map((r) => ({ jobid: r.jobid, title: r.title, company: r.company, jd: r.jd, salary: r.salary ?? null }))
    const resp = await fetch(`${BASE}/api/jobs/score`, { method: "POST", headers: H, body: JSON.stringify({ rows: batch }) })
    if (!resp.ok) { console.error(`batch ${i}: ${resp.status} ${await resp.text()}`); continue }
    const d = await resp.json()
    scored += d.scored; inTok += d.usage?.input || 0; outTok += d.usage?.output || 0; cacheRead += d.usage?.cache_read || 0
    top.push(...d.results)
    console.log(`scored ${Math.min(i + BATCH, scorable.length)}/${scorable.length}`)
  }
  top.sort((a, b) => b.composite - a.composite)
  console.log(`\nDONE. scored ${scored}. top:`)
  for (const t of top.slice(0, 8)) console.log(`  ${t.composite} ${t.band}  ${t.jobid}`)
  console.log(`tokens in=${inTok} out=${outTok} cache_read=${cacheRead}`)
}
main().catch((e) => { console.error(e); process.exit(1) })
