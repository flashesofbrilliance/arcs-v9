#!/usr/bin/env node
// jobs_posting_liveness.mjs — is each posting still accepting applications?
// Reads lines of "<jobid> <url> [<company>|<title>]" (file arg or stdin) and prints "<verdict>\t<jobid>".
// LinkedIn: never fetched; resolved to its public ATS twin (open-ats) or unknown-no-fetch. Ashby: HTTP 200 = open.
// Read-only. Run from a residential path (the guest API blocks datacenter IPs).
// Closed rows are excluded from the lane Send queue by laneStatus = 'posting-closed'.
import { readFileSync } from "node:fs"
import { linkedinToAts } from "./jobs_sources.mjs"

const src = process.argv[2] ? readFileSync(process.argv[2], "utf8") : readFileSync(0, "utf8")
const rows = src.trim().split("\n").filter(Boolean).map((l) => l.trim().split(/\s+/))
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

for (const [jobid, url = "", ...rest] of rows) {
  let verdict = "unknown"
  try {
    if (/^\d+$/.test(jobid) || url.includes("linkedin.com")) {
      // linkedin.com is never fetched (robots.txt disallows all paths, 2026-11-16). With company + title given
      // ("<jobid> <url> <company>|<title>"), a live twin on the company's public ATS board reads as open.
      const meta = rest.join(" ").split("|")
      const tw = meta.length === 2 ? await linkedinToAts({ jobid, company: meta[0], title: meta[1] }) : null
      verdict = tw ? `open-ats\t${tw.url}` : "unknown-no-fetch"
    } else if (url.includes("ashbyhq.com")) {
      const r = await fetch(url, { redirect: "manual" })
      verdict = r.status === 200 ? "open" : `http-${r.status}`
    }
  } catch (e) { verdict = `error-${e.message}` }
  console.log(`${verdict}\t${jobid}`)
  await sleep(1500)
}
