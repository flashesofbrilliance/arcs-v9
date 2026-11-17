#!/usr/bin/env node
// jobs_posting_liveness.mjs: is each posting still accepting applications?
//
// Two modes.
//   1. Lines: reads "<jobid> <url> [<company>|<title>]" lines (file arg or stdin), prints "<verdict>\t<jobid>".
//   2. Queue: `--queue` reads the lane Send queue from /api/jobs (right-swiped or qualify-staged, scored, packet
//      built, no laneStatus; mirrors src/app/jobs/lane/page.tsx), checks each posting and prints a dry-run table.
//      `--write` PATCHes laneStatus = 'posting-closed' on rows whose posting is GONE. Nothing else is written.
//
// Verdicts. Only "gone" is ever written, and only on a definite answer from the employer's public ATS API:
//   greenhouse/lever: HTTP 404 or 410 for the job; ashby: the board answers and the job id is absent.
//   open      the ATS still lists it
//   open-ats  a LinkedIn / Jack & Jill / Fonzi row whose same role is live on the company's ATS (linkedinToAts)
//   unknown   no public ATS twin; never written
// linkedin.com is never fetched (robots.txt disallows every path, checked 2026-11-16). This queue mode folds in
// an unfinished 2026-11 branch (claude/jobs-liveness-wire) that did the same through LinkedIn's guest pages.
// Env for --queue / --write: JOBS_PIPELINE_TOKEN (~/.arcs/jobs-pipeline.env, or run via scripts/jobs_wt.sh), JOBS_BASE.
import { readFileSync, existsSync } from "node:fs"
import { homedir } from "node:os"
import { fileURLToPath } from "node:url"
import path from "node:path"
import { linkedinToAts } from "./jobs_sources.mjs"

const args = process.argv.slice(2)
const QUEUE = args.includes("--queue"), WRITE = args.includes("--write"), JSON_OUT = args.includes("--json")
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const UA = { "user-agent": "arcs-jobs-liveness/1.0 (+https://jobs.arcs.care)", accept: "application/json" }
const ashbyBoards = new Map()

export async function verdictFor(row) {
  const jobid = String(row.jobid), url = row.url || ""
  const m = jobid.match(/^(greenhouse|lever|ashby)-(.+)$/)
  try {
    if (m && m[1] === "greenhouse") {
      const rest = m[2], i = rest.lastIndexOf("-")
      const r = await fetch(`https://boards-api.greenhouse.io/v1/boards/${rest.slice(0, i)}/jobs/${rest.slice(i + 1)}`, { headers: UA })
      return r.status === 404 || r.status === 410 ? "gone" : r.ok ? "open" : `http-${r.status}`
    }
    if (m && m[1] === "lever") {
      const rest = m[2], i = rest.indexOf("-")
      const r = await fetch(`https://api.lever.co/v0/postings/${rest.slice(0, i)}/${rest.slice(i + 1)}`, { headers: UA })
      return r.status === 404 || r.status === 410 ? "gone" : r.ok ? "open" : `http-${r.status}`
    }
    if (m && m[1] === "ashby") {
      const rest = m[2], i = rest.indexOf("-"), org = rest.slice(0, i), id = rest.slice(i + 1)
      if (!ashbyBoards.has(org)) {
        const r = await fetch(`https://api.ashbyhq.com/posting-api/job-board/${org}`, { headers: UA })
        ashbyBoards.set(org, r.ok ? (await r.json()).jobs || [] : null)
      }
      const jobs = ashbyBoards.get(org)
      if (!jobs) return "unknown"
      return jobs.some((j) => j.id === id) ? "open" : "gone"
    }
    if (/^(\d+$|fonzi-|jackandjill-)/.test(jobid) || url.includes("linkedin.com")) {
      if (!row.company || !row.title) return "unknown"
      const tw = await linkedinToAts(row)
      return tw ? "open-ats" : "unknown"
    }
    return "unknown"
  } catch (e) { return `error-${e.message}` }
}

function loadEnv() {
  const p = `${homedir()}/.arcs/jobs-pipeline.env`
  if (process.env.JOBS_PIPELINE_TOKEN || !existsSync(p)) return
  for (const line of readFileSync(p, "utf8").split("\n")) {
    const mm = line.match(/^\s*(?:export\s+)?([A-Z_]+)=(.*)$/)
    if (mm && !process.env[mm[1]]) process.env[mm[1]] = mm[2].replace(/^["']|["']$/g, "")
  }
}

// Mirrors the Send queue in src/app/jobs/lane/page.tsx. Keep the two in step.
export function sendQueue(rows) {
  const derived = (r) => (r.band === "UNSCORED" ? "research" : r.swipe?.direction === "r" ? "qualify" : "research")
  const stageOf = (r) => r.laneStage ?? derived(r)
  return rows.filter((r) => stageOf(r) === "qualify" && r.forge?.status === "built" && !!r.forge.resumeUrl && !r.laneStatus)
}

async function runLines() {
  const src = args[0] && !args[0].startsWith("--") ? readFileSync(args[0], "utf8") : readFileSync(0, "utf8")
  for (const line of src.trim().split("\n").filter(Boolean)) {
    const [jobid, url = "", ...rest] = line.trim().split(/\s+/)
    const meta = rest.join(" ").split("|")
    const v = await verdictFor({ jobid, url, company: meta.length === 2 ? meta[0] : null, title: meta.length === 2 ? meta[1] : null })
    console.log(`${v}\t${jobid}`)
    await sleep(500)
  }
}

async function runQueue() {
  loadEnv()
  const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
  const TOKEN = process.env.JOBS_PIPELINE_TOKEN
  if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required (~/.arcs/jobs-pipeline.env)"); process.exit(2) }
  const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
  const res = await fetch(`${BASE}/api/jobs`, { headers: H })
  if (!res.ok) { console.error(`GET /api/jobs -> ${res.status}`); process.exit(2) }
  const queue = sendQueue((await res.json()).rows)
  const out = []
  for (const r of queue) {
    const v = await verdictFor(r)
    let wrote = null
    if (WRITE && v === "gone") {
      const p = await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: H, body: JSON.stringify({ jobid: r.jobid, laneStage: r.laneStage ?? null, laneStatus: "posting-closed" }) })
      wrote = p.status
    }
    out.push({ jobid: r.jobid, company: r.company, title: r.title, verdict: v, wrote })
    await sleep(300)
  }
  const tally = out.reduce((a, o) => ((a[o.verdict] = (a[o.verdict] || 0) + 1), a), {})
  if (JSON_OUT) { console.log(JSON.stringify({ queue: queue.length, tally, rows: out, write: WRITE })); return }
  // Zach, 2026-11-16: unknown is not open. Confirmed rows print first; unknown rows (no public ATS twin) print in
  // their own UNCONFIRMED block, to be checked by hand before anyone recommends them.
  const line = (o) => `${o.verdict}\t${o.jobid}\t${o.company ?? ""}\t${(o.title ?? "").slice(0, 60)}${o.wrote ? `\twrote ${o.wrote}` : ""}`
  for (const o of out.filter((o) => o.verdict !== "unknown")) console.log(line(o))
  const unc = out.filter((o) => o.verdict === "unknown")
  if (unc.length) { console.log(`# UNCONFIRMED (${unc.length}): no public ATS twin, open the posting by hand before recommending`); for (const o of unc) console.log(line(o)) }
  console.log(`# send queue ${queue.length} · ${Object.entries(tally).map(([k, n]) => `${k} ${n}`).join(" · ") || "empty"} · ${WRITE ? "WRITE (gone -> posting-closed)" : "dry run (add --write to mark gone rows posting-closed)"}`)
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await (QUEUE ? runQueue() : runLines())
}
