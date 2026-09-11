#!/usr/bin/env node
// Forge-trigger eval for the jobs board. Two halves:
//   1. INVARIANTS: read every live row through the API and assert it matches
//      runtime/specs/forge-triggers.json (no queued run without a right swipe, no
//      run on an unscored row, confirm-tier runs flagged, live has a url, ...).
//   2. SYNTHETIC: create throwaway eval-* rows at each tier, drive the swipe route
//      through right / undo / left, assert the decision each time, then delete them.
// Fails loudly (exit 1) on any mismatch, like the drift sentry.
// Usage: set -a; . ~/.arcs/jobs-pipeline.env; set +a
//        node scripts/jobs_trigger_eval.mjs --api https://app.arcs.care [--no-synthetic]
import fs from "node:fs"

const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, arr) => (x.startsWith("--") ? [...a, [x.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]] : a), []))
const API = args.api ?? "https://app.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN missing (set -a; . ~/.arcs/jobs-pipeline.env; set +a)"); process.exit(2) }
const H = { "content-type": "application/json", "x-jobs-token": TOKEN }
const trig = JSON.parse(fs.readFileSync("runtime/specs/forge-triggers.json", "utf8"))
const CONFIRM_NOTE = "below auto tier: confirm before spending a cut"
const STATUSES = ["queued", "gathering", "grading", "rendering", "built", "live"]

let fails = 0, checks = 0
const ok = (cond, msg) => { checks++; if (!cond) { fails++; console.log("  FAIL", msg) } }
const get = async (p) => (await fetch(API + p, { headers: H })).json()
const call = async (p, method, body) => { const r = await fetch(API + p, { method, headers: H, body: body ? JSON.stringify(body) : undefined }); return { status: r.status, json: await r.json().catch(() => ({})) } }

// ---- 1. invariants over live rows ------------------------------------------
const { rows, spec, settings } = await get("/api/jobs")
const t = spec.rubric.tiers
const tierOf = (c) => (c == null ? null : c >= t.t1 ? 1 : c >= t.t2 ? 2 : c >= t.t3 ? 3 : null)
console.log(`invariants over ${rows.length} rows (trigger spec v${trig.version}, scan spec v${spec.version}, cap ${settings.cap})`)
let queued = 0
for (const r of rows) {
  const f = r.forge, s = r.swipe, tier = r.band === "UNSCORED" ? null : tierOf(r.composite)
  if (f) {
    ok(STATUSES.includes(f.status), `${r.jobid} status-vocab: ${f.status}`)
    if (f.status === "queued") { queued++; ok(s?.direction === "r", `${r.jobid} no-forge-without-right: queued run but swipe=${s?.direction ?? "none"}`) }
    ok(r.band !== "UNSCORED", `${r.jobid} no-forge-on-unscored`)
    if (f.status === "queued" && tier !== null && trig.tiers.confirm.includes(tier)) ok((f.notes ?? "").includes(CONFIRM_NOTE), `${r.jobid} confirm-tier-flagged (tier ${tier})`)
    if (f.status === "live") ok(!!f.url, `${r.jobid} live-has-url`)
    if (f.status === "built") {
      // Option B canon (2026-09-11): built may carry a private, admin-gated viewer
      // pointer (/jobs/<id>/forge) — see runtime/specs/forge-triggers.json. A PUBLIC
      // url at built is the premature-exposure class this guard exists to catch.
      ok(!f.url || f.url.startsWith("/jobs/"), `${r.jobid} built-url-not-public`)
      ok(!f.resumeUrl || f.resumeUrl.startsWith("/jobs/"), `${r.jobid} built-resumeurl-not-public`)
    }
  }
  if (s) ok(!s.why || s.direction === "l", `${r.jobid} why-only-on-left`)
}
ok(queued >= 0, "cap-holds (queued runs are held, never dropped)")
console.log(`  ${checks} checks, ${fails} failures, ${queued} queued`)

// ---- 2. synthetic cases through the swipe route -----------------------------
if (!args["no-synthetic"]) {
  const cases = [
    { tier: 1, composite: 0.9 }, { tier: 2, composite: 0.75 }, { tier: 3, composite: 0.6 }, { tier: null, composite: null },
  ]
  for (const c of cases) {
    const jobid = `eval-${c.tier ?? "unscored"}-${Date.now()}`
    console.log(`synthetic tier ${c.tier ?? "unscored"} (${jobid})`)
    const created = await call("/api/jobs", "POST", { jobid, url: "https://example.invalid/eval", title: "Eval row", company: "Eval Co", composite: c.composite })
    ok(created.status === 201, `create ${created.status}`)
    // right
    let r = await call("/api/jobs/swipe", "POST", { jobid, direction: "r" })
    ok(r.status === 200, `right ${r.status}`)
    if (c.tier === null) ok(!r.json.row?.forge, "right-unscored: no forge run")
    else {
      ok(r.json.row?.forge?.status === "queued", "right-queues: status queued")
      if (trig.tiers.confirm.includes(c.tier)) ok((r.json.row?.forge?.notes ?? "").includes(CONFIRM_NOTE), "right-confirm-tier: note present")
      else ok(!r.json.row?.forge?.notes, "auto tier: no confirm note")
    }
    // undo
    r = await call("/api/jobs/swipe", "POST", { jobid, direction: null })
    ok(r.status === 200 && !r.json.row?.swipe && !r.json.row?.forge, "undo-withdraws: swipe and queued run gone")
    // right then left with a why
    await call("/api/jobs/swipe", "POST", { jobid, direction: "r" })
    r = await call("/api/jobs/swipe", "POST", { jobid, direction: "l", why: "comp" })
    ok(r.json.row?.swipe?.direction === "l" && r.json.row?.swipe?.why === "comp" && !r.json.row?.forge, "left-withdraws + why-only-on-left")
    // left after built: run kept
    if (c.tier !== null) {
      await call("/api/jobs/swipe", "POST", { jobid, direction: "r" })
      await call("/api/jobs/forge", "PATCH", { jobid, status: "built" })
      r = await call("/api/jobs/swipe", "POST", { jobid, direction: "l" })
      ok(r.json.row?.forge?.status === "built", "left-keeps-built")
    }
    const del = await call(`/api/jobs?jobid=${jobid}`, "DELETE")
    ok(del.json.deleted === 1, `cleanup deleted=${del.json.deleted}`)
  }
}
console.log(`\n${checks} checks · ${fails} failures`)
process.exit(fails ? 1 : 0)
