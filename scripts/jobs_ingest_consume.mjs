#!/usr/bin/env node
// jobs_ingest_consume.mjs — the inbox re-pull consumer. Turns a filed
// IngestRequest into rows on the board. The Gmail read + posting-parse is done
// by the caller (an agent with the Gmail connector, or the scheduled task) and
// handed in as a JSON array of {jobid,title,company,location,url,salary?,firstSeen?}.
// This script does the mechanical half: dedupe against existing rows, POST the
// new ones (unscored), then complete the request and advance the source
// watermark so the next sweep reads only newer mail. Scoring is a separate step
// (scripts/jobs_score_sweep.mjs), kept apart so ingest never blocks on the model.
//
//   node scripts/jobs_ingest_consume.mjs --request <id> --rows parsed.json --watermark 2026-09-07T00:00:00Z
//   node scripts/jobs_ingest_consume.mjs --request <id> --rows parsed.json --fail "reason"
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE.

import fs from "node:fs"
const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const requestId = arg("--request", null)
if (!requestId) { console.error("--request <id> required"); process.exit(2) }

async function main() {
  const fail = arg("--fail", null)
  if (fail) {
    await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: H, body: JSON.stringify({ requestId, status: "failed", error: String(fail) }) })
    console.log(`request ${requestId} marked failed: ${fail}`); return
  }
  const rowsFile = arg("--rows", null)
  const parsed = rowsFile ? JSON.parse(fs.readFileSync(rowsFile, "utf8")) : []
  const incoming = (Array.isArray(parsed) ? parsed : parsed.rows || []).filter((r) => r && r.jobid && r.title && r.company && r.url)

  const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  const have = new Set(rows.map((r) => String(r.jobid)))
  const fresh = incoming.filter((r) => !have.has(String(r.jobid)))
  console.log(`incoming ${incoming.length} · already have ${incoming.length - fresh.length} · new ${fresh.length}`)

  if (fresh.length) {
    const payload = fresh.map((r) => ({ jobid: String(r.jobid), title: r.title, company: r.company, location: r.location ?? null, url: r.url, salary: r.salary ?? null, source: r.source ?? "linkedin_alert_digest", firstSeen: r.firstSeen ?? new Date().toISOString(), band: "UNSCORED", unscoredWhy: "ingested by re-pull; scorer not yet run" }))
    const w = await fetch(`${BASE}/api/jobs`, { method: "POST", headers: H, body: JSON.stringify(payload) })
    console.log("post new rows:", w.status, (await w.json()).count ?? "")
  }

  const watermark = arg("--watermark", new Date().toISOString())
  const done = await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: H, body: JSON.stringify({ requestId, status: "done", rowsAdded: fresh.length, watermark }) })
  console.log(`request ${requestId} -> done (${fresh.length} rows), watermark ${watermark}:`, done.status)
  console.log(fresh.length ? `next: node scripts/jobs_score_sweep.mjs   # score the ${fresh.length} new rows` : "no new rows; nothing to score")
}
main().catch((e) => { console.error(e); process.exit(1) })
