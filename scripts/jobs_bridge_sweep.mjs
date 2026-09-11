#!/usr/bin/env node
// jobs_bridge_sweep.mjs — BRIDGE-lane JD read + score driver.
// The bridge lane (source=bridge_scan) is ranked by shoot-to-win (fit x
// win-probability) against runtime/specs/bridge-scan.json, NOT by FDE fit.
// Bridge rows point at first-party ATS postings (Greenhouse / Ashby / Lever),
// whose JSON APIs expose the full JD — so unlike the LinkedIn sweep this fetch
// works from anywhere. Each row's JD is fetched here, then posted in batches to
// POST /api/jobs/score with spec:"bridge-scan"; the route holds the model key,
// writes composite/band/dims/gates back, and records a Score row keyed
// "bridge-1.0" (the FDE v1.x Score rows are untouched).
//
//   node scripts/jobs_bridge_sweep.mjs --proof                 # fails-on-bad / passes-on-good gate (no DB write)
//   node scripts/jobs_bridge_sweep.mjs --dry-run [--limit N]   # fetch JDs only, no model
//   node scripts/jobs_bridge_sweep.mjs --limit 5               # proof run on live rows
//   node scripts/jobs_bridge_sweep.mjs                         # drain every UNSCORED bridge row
//   node scripts/jobs_bridge_sweep.mjs --all                   # re-score every bridge row (re-runnable)
//   node scripts/jobs_bridge_sweep.mjs --report                # rank what is already scored, no fetch/model
//   node scripts/jobs_bridge_sweep.mjs --jobid bridge-x-1234   # re-score one row
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE (default https://jobs.arcs.care).

import fs from "node:fs"
import path from "node:path"

const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const DRY = has("--dry-run"), PROOF = has("--proof"), ALL = has("--all"), REPORT = has("--report")
const LIMIT = Number(arg("--limit", 0)) || 0
const BATCH = Number(arg("--batch", 8))
const TOP = Number(arg("--top", 20))
const ONLY = arg("--jobid", null)
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const SPEC = "bridge-scan"
const specFile = JSON.parse(fs.readFileSync(path.join(process.cwd(), "runtime", "specs", "bridge-scan.json"), "utf8"))
const COMP_READ = specFile.rubric.competition_read
const UA = { "user-agent": "Mozilla/5.0 (jobs.arcs.care bridge sweep)" }
const sleep = (ms) => new Promise((z) => setTimeout(z, ms))
const parse = (s, fb) => { try { return typeof s === "string" ? JSON.parse(s) : (s ?? fb) } catch { return fb } }

// --- JD extraction -----------------------------------------------------------
const ENT = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", "#39": "'", "#x27": "'", "#160": " " }
const decode = (s) => s.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (m, e) => {
  if (ENT[e] != null) return ENT[e]
  if (/^#x/i.test(e)) return String.fromCodePoint(parseInt(e.slice(2), 16))
  if (/^#/.test(e)) return String.fromCodePoint(parseInt(e.slice(1), 10))
  return " "
})
const strip = (html) => decode(decode(html || "")).replace(/<(script|style)[\s\S]*?<\/\1>/gi, " ").replace(/<br\s*\/?>/gi, "\n").replace(/<\/(p|div|li|h\d|tr|section)>/gi, "\n").replace(/<[^>]+>/g, " ").replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()

// Greenhouse: first-party career pages carry ?gh_jid=<id>; the board slug is the
// company's boards-api tenant. Known hosts map directly; unknown hosts fall back
// to slug guesses from the company name, then to the raw page.
const GH_SLUG_BY_HOST = {
  "www.betterment.com": "betterment", "www.squarespace.com": "squarespace", "careers.datadoghq.com": "datadog",
  "www.mongodb.com": "mongodb", "careers.onepeloton.com": "peloton", "www.hioscar.com": "oscar",
}
const slugGuesses = (company) => { const b = String(company || "").toLowerCase().replace(/[^a-z0-9]+/g, ""); return [...new Set([b, b.replace(/inc$|corp$|health$/, ""), b + "inc"])].filter(Boolean) }
async function ghJob(slug, id) {
  const r = await fetch(`https://boards-api.greenhouse.io/v1/boards/${slug}/jobs/${id}?questions=false`, { headers: UA })
  if (!r.ok) return null
  const j = await r.json()
  if (!j?.content) return null
  const pay = Array.isArray(j.pay_input_ranges) && j.pay_input_ranges.length ? j.pay_input_ranges.map((p) => `${p.title ? p.title + ": " : ""}${p.min_cents != null ? "$" + Math.round(p.min_cents / 100).toLocaleString() : ""}-${p.max_cents != null ? "$" + Math.round(p.max_cents / 100).toLocaleString() : ""}`).join("; ") : null
  const head = [`Title: ${j.title}`, j.location?.name ? `Location: ${j.location.name}` : "", j.updated_at ? `Updated: ${j.updated_at}` : "", pay ? `Pay ranges: ${pay}` : ""].filter(Boolean).join("\n")
  return { jd: `${head}\n\n${strip(j.content)}`, salary: pay, ats: "greenhouse" }
}
const ashbyBoards = new Map()
async function ashbyJob(org, id) {
  if (!ashbyBoards.has(org)) {
    const r = await fetch(`https://api.ashbyhq.com/posting-api/job-board/${org}?includeCompensation=true`, { headers: UA })
    ashbyBoards.set(org, r.ok ? (await r.json()).jobs || [] : [])
  }
  const j = ashbyBoards.get(org).find((x) => x.id === id)
  if (!j) return null
  const comp = j.compensation?.compensationTierSummary || null
  const head = [`Title: ${j.title}`, j.department ? `Department: ${j.department}` : "", j.team ? `Team: ${j.team}` : "", j.location ? `Location: ${j.location}` : "", j.isRemote != null ? `Remote: ${j.isRemote}` : "", j.publishedAt ? `Published: ${j.publishedAt}` : "", comp ? `Compensation: ${comp}` : ""].filter(Boolean).join("\n")
  return { jd: `${head}\n\n${strip(j.descriptionHtml || j.descriptionPlain || "")}`, salary: comp, ats: "ashby" }
}
async function leverJob(org, id) {
  const r = await fetch(`https://api.lever.co/v0/postings/${org}/${id}`, { headers: UA })
  if (!r.ok) return null
  const j = await r.json()
  const lists = (j.lists || []).map((l) => `${l.text}\n${strip(l.content)}`).join("\n\n")
  const head = [`Title: ${j.text}`, j.categories?.team ? `Team: ${j.categories.team}` : "", j.categories?.location ? `Location: ${j.categories.location}` : "", j.categories?.commitment ? `Commitment: ${j.categories.commitment}` : "", j.salaryRange ? `Salary: ${j.salaryRange.min}-${j.salaryRange.max} ${j.salaryRange.currency || ""}` : ""].filter(Boolean).join("\n")
  return { jd: `${head}\n\n${strip(j.descriptionBody || j.description || "")}\n\n${lists}\n\n${strip(j.additional || "")}`, salary: j.salaryRange ? `${j.salaryRange.min}-${j.salaryRange.max}` : null, ats: "lever" }
}
async function fetchJD(row) {
  let u; try { u = new URL(row.url) } catch { return null }
  try {
    const ghid = u.searchParams.get("gh_jid") || (/greenhouse\.io$/.test(u.host) ? u.pathname.match(/\/jobs\/(\d+)/)?.[1] : null)
    if (ghid) {
      const slugs = /greenhouse\.io$/.test(u.host) ? [u.pathname.split("/").filter(Boolean)[0]] : [GH_SLUG_BY_HOST[u.host], ...slugGuesses(row.company)].filter(Boolean)
      for (const s of slugs) { const j = await ghJob(s, ghid); if (j) return j }
    }
    if (u.host === "jobs.ashbyhq.com") { const [org, id] = u.pathname.split("/").filter(Boolean); if (org && id) { const j = await ashbyJob(org, id); if (j) return j } }
    if (u.host === "jobs.lever.co") { const [org, id] = u.pathname.split("/").filter(Boolean); if (org && id) { const j = await leverJob(org, id); if (j) return j } }
    const r = await fetch(row.url, { headers: UA }); if (r.ok) { const t = strip(await r.text()); if (t.length > 800) return { jd: t, salary: null, ats: "html" } }
  } catch { /* fall through */ }
  return null
}

// --- scoring -------------------------------------------------------------------
async function score(batch) {
  const resp = await fetch(`${BASE}/api/jobs/score`, { method: "POST", headers: H, body: JSON.stringify({ spec: SPEC, rows: batch }) })
  if (!resp.ok) throw new Error(`score ${resp.status}: ${await resp.text()}`)
  return resp.json()
}
const compRead = (dims) => COMP_READ[String(dims?.competition_density ?? "")] || "?"
const tierOf = (c) => { const t = specFile.rubric.tiers; return c == null ? null : c >= t.t1 ? 1 : c >= t.t2 ? 2 : c >= t.t3 ? 3 : null }
function printRank(rows, n) {
  const ranked = rows.filter((r) => r.composite != null).sort((a, b) => b.composite - a.composite)
  console.log(`\nBRIDGE LANE — top ${Math.min(n, ranked.length)} of ${ranked.length} by winnability (${SPEC} v${specFile.version})`)
  console.log("rank  comp   band      tier  compete   req  lvl  shape  stab  edge  company — title")
  ranked.slice(0, n).forEach((r, i) => {
    const d = parse(r.dims, {}); const g = parse(r.gates, [])
    console.log(`${String(i + 1).padStart(3)}   ${r.composite.toFixed(3)}  ${r.band.padEnd(8)}  T${tierOf(r.composite) ?? "-"}    ${compRead(d).padEnd(8)}  ${d.req_reality ?? "-"}    ${d.level_fit ?? "-"}    ${d.shape_fit ?? "-"}      ${d.stability_parent_signal ?? "-"}     ${d.edge_rewarded ?? "-"}     ${r.company} — ${r.title}${g.length ? `  [gate: ${g.join("; ")}]` : ""}`)
  })
  const bands = {}; for (const r of ranked) bands[r.band] = (bands[r.band] || 0) + 1
  console.log(`bands: ${JSON.stringify(bands)}`)
}

// --- proof: the scorer must fail the phantom + the stampede and pass the real one
const PROOF_ROWS = [
  { jobid: "eval-bridge-good", title: "Senior Manager, Revenue Operations & GTM Systems", company: "Steadfast Insurance Co.", jd: `Title: Senior Manager, Revenue Operations & GTM Systems\nLocation: New York, NY (hybrid, 3 days)\nUpdated: 2026-09-09\nPay ranges: $175,000-$210,000 base + bonus\n\nAbout the role\nSteadfast is a 30-year-old, profitable, publicly traded specialty insurer. You will report to the VP, Revenue Operations and own the GTM systems stack (Salesforce, CPQ, marketing automation) for a 400-person commercial org. In your first year you will: (1) stand up a deal desk and quote-to-cash process; (2) bring AI-assisted automation into pipeline hygiene, forecasting, and rep enablement — we are actively adopting LLM tooling across operations and want someone who can build and ship it, not just buy it; (3) partner with Compliance to keep every workflow inside our regulated perimeter. You have 10+ years in RevOps / business systems, have led cross-functional programs in a regulated industry, and have hands-on experience building automation. Team of 4 direct reports.` },
  { jobid: "eval-bridge-bad-phantom", title: "Future Opportunities — Business Operations & Strategy", company: "Bigbrand Sports", jd: `Title: Future Opportunities — Business Operations & Strategy\nLocation: Various\n\nJoin our talent community! We are always looking for exceptional people across business operations, strategy, product, and more. This is not a specific opening; by submitting your profile you will be considered for future roles as they become available across our global businesses. Responsibilities will vary based on the role. We will reach out if there is a match.` },
  { jobid: "eval-bridge-bad-stampede", title: "Member of Technical Staff, Applied Research", company: "Frontier AI Lab", jd: `Title: Member of Technical Staff, Applied Research\nLocation: San Francisco, CA (on-site)\nPay ranges: $350,000-$550,000\n\nWe are looking for exceptional researchers and engineers to push the frontier of large language models. You have a PhD or equivalent research record in machine learning, first-author publications at NeurIPS/ICML/ICLR, and experience training large models at scale. You will design and run experiments on pretraining, RL, and evaluation. We hire the top fraction of a percent of applicants.` },
]
async function proof() {
  const d = await score(PROOF_ROWS)
  const by = Object.fromEntries(d.results.map((r) => [r.jobid, r]))
  const checks = [
    ["passes-on-good", by["eval-bridge-good"], (r) => r && ["PURSUE", "CONSIDER"].includes(r.band) && !r.gates.length],
    ["fails-on-bad (phantom req)", by["eval-bridge-bad-phantom"], (r) => r && r.band === "PASS" && (r.gates.length > 0 || (r.dims.req_reality ?? 3) <= 1)],
    ["fails-on-bad (AI-lab stampede)", by["eval-bridge-bad-stampede"], (r) => r && r.band === "PASS" && (r.gates.length > 0 || (r.dims.competition_density ?? 3) === 0)],
  ]
  let ok = true
  for (const [name, r, fn] of checks) {
    const pass = fn(r); ok = ok && pass
    console.log(`${pass ? "PASS" : "FAIL"}  ${name}: ${r ? `${r.composite} ${r.band} gates=${JSON.stringify(r.gates)} dims=${JSON.stringify(r.dims)}\n      ${r.assessment}` : "no result"}`)
  }
  console.log(`\nproof ${ok ? "OK" : "FAILED"} · spec=${d.spec} score_version=${d.score_version} · tokens in=${d.usage.input} out=${d.usage.output} cache_read=${d.usage.cache_read}`)
  process.exit(ok ? 0 : 1)
}

async function main() {
  if (PROOF) return proof()
  const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  const bridge = rows.filter((r) => r.source === "bridge_scan")
  if (REPORT) return printRank(bridge, TOP)
  let todo = ONLY ? bridge.filter((r) => r.jobid === ONLY) : ALL ? bridge : bridge.filter((r) => r.band === "UNSCORED")
  if (LIMIT) todo = todo.slice(0, LIMIT)
  console.log(`bridge rows: ${bridge.length} · to score: ${todo.length}${DRY ? " (DRY)" : ""}`)

  let fetched = 0; const failed = []; const byAts = {}
  for (const r of todo) { const j = await fetchJD(r); if (j) { Object.assign(r, j); fetched++; byAts[j.ats] = (byAts[j.ats] || 0) + 1 } else failed.push(r); await sleep(250) }
  console.log(`JDs fetched: ${fetched} ${JSON.stringify(byAts)} · fetch-failed: ${failed.length}`)
  failed.forEach((r) => console.log(`  no-fetch ${r.jobid} ${r.url}`))
  const scorable = todo.filter((r) => r.jd)
  if (DRY) { scorable.slice(0, 3).forEach((r) => console.log(`\n--- ${r.jobid} (${r.jd.length} chars, ${r.ats})\n${r.jd.slice(0, 500)}`)); console.log(`\nDRY: would score ${scorable.length} in ${Math.ceil(scorable.length / BATCH)} batches.`); return }

  let scored = 0, inTok = 0, outTok = 0, cacheRead = 0; const out = []
  for (let i = 0; i < scorable.length; i += BATCH) {
    const batch = scorable.slice(i, i + BATCH).map((r) => ({ jobid: r.jobid, title: r.title, company: r.company, jd: r.jd, salary: r.salary ?? null }))
    try {
      const d = await score(batch)
      scored += d.scored; inTok += d.usage?.input || 0; outTok += d.usage?.output || 0; cacheRead += d.usage?.cache_read || 0
      for (const res of d.results) { const r = scorable.find((x) => x.jobid === res.jobid); out.push({ ...r, ...res }) }
      console.log(`scored ${Math.min(i + BATCH, scorable.length)}/${scorable.length}`)
    } catch (e) { console.error(`batch ${i}: ${e.message}`) }
  }
  console.log(`\nDONE. scored ${scored}. tokens in=${inTok} out=${outTok} cache_read=${cacheRead}`)
  printRank(out, TOP)
}
main().catch((e) => { console.error(e); process.exit(1) })
