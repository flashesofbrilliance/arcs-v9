#!/usr/bin/env node
// jobs_prior_check.mjs: before a batch is drafted, list board rows at companies where Zach already
// applied, interviewed or was declined (runtime/specs/prior-applications.json, harvested from Gmail).
// Read-only. Born 2026-11-16 after two AssemblyAI roles were drafted although AssemblyAI had
// interviewed and declined him in July.
//
//   node scripts/jobs_prior_check.mjs                 # open rows: unswiped or right-swiped, not applied or closed
//   node scripts/jobs_prior_check.mjs --lane qualify  # only rows in one lane (a prepared batch)
//   node scripts/jobs_prior_check.mjs --jobids a,b    # specific rows
//   node scripts/jobs_prior_check.mjs --mark          # stamp BLOCK rows on the board: applied -> apply lane, declined -> skip note
//   node scripts/jobs_prior_check.mjs --selftest      # the lookup's fixtures live in jobs_sources.mjs --selftest
// Env: JOBS_PIPELINE_TOKEN (scripts/jobs_wt.sh loads it), JOBS_BASE.
import { priorVerdict, priorSpec, roleScore } from "./jobs_sources.mjs"
const roleScoreSafe = (a, b) => { try { return roleScore(a, b) >= 0.7 } catch { return false } }

const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? d) : d }
if (process.argv.includes("--selftest")) { console.log("run: node scripts/jobs_sources.mjs --selftest (prior: tests)"); process.exit(0) }
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required (run via scripts/jobs_wt.sh)"); process.exit(2) }

const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: { "x-jobs-token": TOKEN } })).json()
const ids = arg("--jobids", null), lane = arg("--lane", null)
let pool = rows
if (ids) { const set = new Set(String(ids).split(",")); pool = rows.filter((r) => set.has(r.jobid)) }
else if (lane) pool = rows.filter((r) => r.laneStage === lane)
else pool = rows.filter((r) => r.swipe?.direction !== "l" && !["apply", "interview", "outcome"].includes(r.laneStage) && !/^skip:/.test(r.laneStatus || "") && r.band !== "PASS")

const spec = priorSpec()
const hits = pool.map((r) => ({ r, v: priorVerdict(r.company, r.title, spec) })).filter((x) => x.v)
const order = { block: 0, warn: 1, info: 2 }
hits.sort((a, b) => order[a.v.level] - order[b.v.level] || (b.r.composite || 0) - (a.r.composite || 0))
console.log(`prior-application check: ${spec.applications?.length || 0} known applications · ${pool.length} rows checked · ${hits.filter((h) => h.v.level === "block").length} block · ${hits.filter((h) => h.v.level === "warn").length} warn · ${hits.filter((h) => h.v.level === "info").length} info`)
for (const { r, v } of hits) console.log(`${v.level.toUpperCase().padEnd(5)} ${(r.composite || 0).toFixed(2)} ${r.jobid.slice(0, 34).padEnd(34)} ${r.company.slice(0, 18).padEnd(18)} ${r.title.slice(0, 44).padEnd(44)} ${r.laneStage || "-"} | ${v.reason}`)

if (process.argv.includes("--mark")) {
  let n = 0
  for (const { r, v } of hits.filter((h) => h.v.level === "block")) {
    const a = v.apps.find((x) => x.role && roleScoreSafe(r.title, x.role)) || v.apps[0]
    const declined = a.outcome === "rejected"
    const body = declined
      ? { jobid: r.jobid, laneStage: "research", laneStatus: `skip: declined ${a.outcome_date || ""} for this role per Gmail (${a.role}); do not reapply`.replace("  ", " ") }
      : { jobid: r.jobid, laneStage: "apply", laneStatus: `applied ${a.applied || ""} per Gmail (${a.role})${a.outcome === "interviewing" ? ", interviewing" : ""}` }
    const res = await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: { "x-jobs-token": TOKEN, "content-type": "application/json" }, body: JSON.stringify(body) })
    if (res.ok) n++; else console.error(`mark failed ${r.jobid}: ${res.status}`)
  }
  console.log(`marked ${n} BLOCK rows on the board`)
}
