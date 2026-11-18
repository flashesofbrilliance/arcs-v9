#!/usr/bin/env node
// jobs_posting_liveness.mjs: is each posting still accepting applications?
//
// Two modes.
//   1. Lines: reads "<jobid> <url> [<company>|<title>]" lines (file arg or stdin), prints "<verdict>\t<jobid>[\t<age>]".
//   2. Queue: `--queue` reads the lane Send queue from /api/jobs (right-swiped or qualify-staged, scored, packet
//      built, no laneStatus; mirrors src/app/jobs/lane/page.tsx), checks each posting and prints a dry-run table.
//      `--write` PATCHes laneStatus = 'posting-closed' on rows whose posting is GONE. Nothing else is written.
//   `--self-test` runs offline with a fake fetch: a dead network must fail the run, a board without the job must not.
//
// Verdicts. Only "gone" is ever written, and only on a definite answer from the employer's public ATS API:
//   greenhouse/lever: HTTP 404 or 410 for the job; ashby: the board answers and the job id is absent.
//   open      the ATS still lists it; age in days since it was posted follows (ashby publishedAt, greenhouse
//             first_published or updated_at, lever createdAt), marked "stale" at STALE_DAYS or more
//   open-ats  a LinkedIn / Jack & Jill / Fonzi row whose same role is live on the company's ATS (linkedinToAts)
//   unknown   no public ATS twin; never written
// linkedin.com is never fetched (robots.txt disallows every path, checked 2026-11-16). This queue mode folds in
// an unfinished 2026-11 branch (claude/jobs-liveness-wire) that did the same through LinkedIn's guest pages.
//
// Network failure is not "unknown" (2026-11-17: Node's fetch ignored HTTPS_PROXY in a cloud shell, all 38 rows came
// back unknown with no error, and a closed posting was recommended). A lookup that threw or got a non-404 status is
// counted; when more than half the run's lookups failed the script exits 3 and prints no table. Behind a proxy
// (HTTPS_PROXY set) the script re-runs itself once with NODE_USE_ENV_PROXY=1, which Node 22.21+ honors.
// Env for --queue / --write: JOBS_PIPELINE_TOKEN (~/.arcs/jobs-pipeline.env, or run via scripts/jobs_wt.sh), JOBS_BASE.
import { readFileSync, existsSync } from "node:fs"
import { homedir } from "node:os"
import { fileURLToPath } from "node:url"
import { spawnSync } from "node:child_process"
import path from "node:path"
import { linkedinToAts, netStats } from "./jobs_sources.mjs"

const IS_MAIN = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
if (IS_MAIN && (process.env.HTTPS_PROXY || process.env.https_proxy) && !process.env.NODE_USE_ENV_PROXY) {
  const r = spawnSync(process.execPath, ["--disable-warning=UNDICI-EHPA", ...process.execArgv, ...process.argv.slice(1)], { stdio: "inherit", env: { ...process.env, NODE_USE_ENV_PROXY: "1" } })
  process.exit(r.status ?? 1)
}

const args = process.argv.slice(2)
const QUEUE = args.includes("--queue"), WRITE = args.includes("--write"), JSON_OUT = args.includes("--json")
const STALE_DAYS = 60
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const UA = { "user-agent": "arcs-jobs-liveness/1.0 (+https://jobs.arcs.care)", accept: "application/json" }
const get = (url) => fetch(url, { headers: UA, signal: AbortSignal.timeout(20000) })
const ageDays = (t) => (t ? Math.floor((Date.now() - new Date(t).getTime()) / 864e5) : null)
const ashbyBoards = new Map()

async function probe(row) {
  const jobid = String(row.jobid), url = row.url || ""
  const m = jobid.match(/^(greenhouse|lever|ashby)-(.+)$/)
  try {
    if (m && (m[1] === "greenhouse" || m[1] === "lever")) {
      const rest = m[2], i = m[1] === "greenhouse" ? rest.lastIndexOf("-") : rest.indexOf("-")
      const r = await get(m[1] === "greenhouse"
        ? `https://boards-api.greenhouse.io/v1/boards/${rest.slice(0, i)}/jobs/${rest.slice(i + 1)}`
        : `https://api.lever.co/v0/postings/${rest.slice(0, i)}/${rest.slice(i + 1)}`)
      if (r.status === 404 || r.status === 410) return { verdict: "gone" }
      if (!r.ok) return { verdict: `http-${r.status}` }
      const j = await r.json()
      return { verdict: "open", age: ageDays(j.first_published || j.updated_at || j.createdAt) }
    }
    if (m && m[1] === "ashby") {
      const rest = m[2], i = rest.indexOf("-"), org = rest.slice(0, i), id = rest.slice(i + 1)
      if (!ashbyBoards.has(org)) {
        const r = await get(`https://api.ashbyhq.com/posting-api/job-board/${org}`)
        ashbyBoards.set(org, r.ok ? (await r.json()).jobs || [] : r.status)
      }
      const jobs = ashbyBoards.get(org)
      if (typeof jobs === "number") return { verdict: jobs === 404 ? "unknown" : `http-${jobs}` }
      const j = jobs.find((x) => x.id === id)
      return j ? { verdict: "open", age: ageDays(j.publishedAt) } : { verdict: "gone" }
    }
    if (/^(\d+$|fonzi-|jackandjill-)/.test(jobid) || url.includes("linkedin.com")) {
      if (!row.company || !row.title) return { verdict: "unknown" }
      const tw = await linkedinToAts(row)
      return { verdict: tw ? "open-ats" : "unknown" }
    }
    return { verdict: "unknown" }
  } catch (e) { return { verdict: `error-${e.message}` } }
}

// { verdict, age, netError }. netError: the answer came from a failed lookup, not from the ATS.
export async function check(row) {
  const before = netStats.errors
  const res = await probe(row)
  res.netError = /^(error|http)-/.test(res.verdict) || (res.verdict === "unknown" && netStats.errors > before)
  return res
}
export const verdictFor = async (row) => (await check(row)).verdict

// The Frustration Gate for this script: a message when more than half the lookups failed, else null.
export function netFailure(results) {
  const bad = results.filter((x) => x.netError).length
  return bad * 2 > results.length ? `network unreachable: ${bad} of ${results.length} lookups failed; in a proxied cloud shell set NODE_USE_ENV_PROXY=1` : null
}

async function scan(rows, delay) {
  const out = []
  for (const r of rows) { out.push({ row: r, ...(await check(r)) }); if (delay) await sleep(delay) }
  const fail = netFailure(out)
  if (fail) { console.error(fail); process.exit(3) }
  return out
}

const ageCol = (a) => (a == null ? "" : `\t${a}d${a >= STALE_DAYS ? " stale" : ""}`)

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
  const rows = src.trim().split("\n").filter(Boolean).map((line) => {
    const [jobid, url = "", ...rest] = line.trim().split(/\s+/)
    const meta = rest.join(" ").split("|")
    return { jobid, url, company: meta.length === 2 ? meta[0] : null, title: meta.length === 2 ? meta[1] : null }
  })
  for (const o of await scan(rows, 500)) console.log(`${o.verdict}\t${o.row.jobid}${ageCol(o.age)}`)
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
  for (const { row: r, verdict: v, age } of await scan(queue, 300)) {
    let wrote = null
    if (WRITE && v === "gone") {
      const p = await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: H, body: JSON.stringify({ jobid: r.jobid, laneStage: r.laneStage ?? null, laneStatus: "posting-closed" }) })
      wrote = p.status
    }
    out.push({ jobid: r.jobid, company: r.company, title: r.title, verdict: v, age: age ?? null, wrote })
  }
  const tally = out.reduce((a, o) => ((a[o.verdict] = (a[o.verdict] || 0) + 1), a), {})
  if (JSON_OUT) { console.log(JSON.stringify({ queue: queue.length, tally, rows: out, write: WRITE })); return }
  // Zach, 2026-11-16: unknown is not open. Confirmed rows print first; unknown rows (no public ATS twin) print in
  // their own UNCONFIRMED block, to be checked by hand before anyone recommends them.
  const line = (o) => `${o.verdict}\t${o.jobid}\t${o.company ?? ""}\t${(o.title ?? "").slice(0, 60)}${ageCol(o.age)}${o.wrote ? `\twrote ${o.wrote}` : ""}`
  for (const o of out.filter((o) => o.verdict !== "unknown")) console.log(line(o))
  const unc = out.filter((o) => o.verdict === "unknown")
  if (unc.length) { console.log(`# UNCONFIRMED (${unc.length}): no public ATS twin, open the posting by hand before recommending`); for (const o of unc) console.log(line(o)) }
  console.log(`# send queue ${queue.length} · ${Object.entries(tally).map(([k, n]) => `${k} ${n}`).join(" · ") || "empty"} · ${WRITE ? "WRITE (gone -> posting-closed)" : "dry run (add --write to mark gone rows posting-closed)"}`)
}

async function selfTest() {
  const t = (name, ok) => { if (!ok) { console.error(`FAIL ${name}`); process.exitCode = 1 } else console.log(`ok   ${name}`) }
  const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } })
  const run = async (rows) => { const res = []; for (const r of rows) res.push(await check(r)); return res }
  // Distinct company and org names per case: board lookups are cached for the life of the process.
  const rowsFor = (k) => [
    { jobid: `greenhouse-gh${k}-1`, url: "" },
    { jobid: `lever-lv${k}-abc`, url: "" },
    { jobid: `ashby-ab${k}-job1`, url: "" },
    { jobid: "4300000001", url: "https://www.linkedin.com/jobs/view/4300000001", company: `Zzselftest Nowhere ${k}`, title: "Forward Deployed Engineer" },
  ]

  globalThis.fetch = async () => { throw new TypeError("fetch failed") }
  let res = await run(rowsFor("a"))
  t("dead network: every lookup flagged", res.every((x) => x.netError))
  t("dead network: the run fails", /network unreachable: 4 of 4 lookups failed/.test(netFailure(res) || ""))

  globalThis.fetch = async () => json({}, 503)
  res = await run(rowsFor("b"))
  t("503 everywhere: the run fails", netFailure(res) !== null)

  const board = { jobs: [{ id: "other", title: "Barista", publishedAt: "2026-01-01T00:00:00Z" }] }
  globalThis.fetch = async () => json(board)
  res = await run(rowsFor("c").slice(2))
  t("board without the job: ashby row is gone", res[0].verdict === "gone" && !res[0].netError)
  t("board without the job: linkedin row is unknown, not an error", res[1].verdict === "unknown" && !res[1].netError)
  t("board without the job: the run passes", netFailure(res) === null)

  globalThis.fetch = async () => json({}, 404)
  res = await run(rowsFor("d"))
  t("404 everywhere: gone or unknown, never an error", res.every((x) => !x.netError) && netFailure(res) === null)

  globalThis.fetch = async (u) => json(String(u).includes("ashbyhq") ? { jobs: [{ id: "job1", publishedAt: new Date(Date.now() - 90 * 864e5).toISOString() }] } : { first_published: new Date(Date.now() - 3 * 864e5).toISOString() })
  res = await run(rowsFor("e").slice(0, 3))
  t("open rows carry posting age", res[0].verdict === "open" && res[0].age === 3 && res[2].verdict === "open" && res[2].age === 90)
  t("age column marks stale", ageCol(90).endsWith("stale") && !ageCol(3).includes("stale"))
}

if (IS_MAIN) await (args.includes("--self-test") ? selfTest() : QUEUE ? runQueue() : runLines())
