#!/usr/bin/env node
// jobs_posting_liveness.mjs — is each posting still accepting applications?
// Reads lines of "<jobid> <url>" (file arg or stdin) and prints "<verdict>\t<jobid>".
// LinkedIn: the guest endpoint marks a closed posting with
// <figure class="closed-job"> / figcaption.closed-job__flavor--closed. Ashby: HTTP 200 = open.
// Read-only. Run from a residential path (the guest API blocks datacenter IPs).
// Closed rows are excluded from the lane Send queue by laneStatus = 'posting-closed'.
import { readFileSync } from "node:fs"

const src = process.argv[2] ? readFileSync(process.argv[2], "utf8") : readFileSync(0, "utf8")
const rows = src.trim().split("\n").filter(Boolean).map((l) => l.trim().split(/\s+/))
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

for (const [jobid, url = ""] of rows) {
  let verdict = "unknown"
  try {
    if (/^\d+$/.test(jobid) || url.includes("linkedin.com")) {
      const r = await fetch(`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/${jobid}`, { headers: { "user-agent": "Mozilla/5.0" } })
      const t = r.status === 200 ? await r.text() : ""
      verdict = r.status === 404 || r.status === 410 ? "gone"
        : r.status !== 200 ? `http-${r.status}`
        : /closed-job__flavor--closed/.test(t) ? "closed" : "open"
    } else if (url.includes("ashbyhq.com")) {
      const r = await fetch(url, { redirect: "manual" })
      verdict = r.status === 200 ? "open" : `http-${r.status}`
    }
  } catch (e) { verdict = `error-${e.message}` }
  console.log(`${verdict}\t${jobid}`)
  await sleep(1500)
}
