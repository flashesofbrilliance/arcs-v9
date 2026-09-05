#!/usr/bin/env node
// Seed / refresh the jobs board tables from the working files:
//   runtime/job-search/opportunities-scored.jsonl   (scored rows, main checkout)
//   runtime/job-search/sweep-*.jsonl                 (unscored net-new rows)
//   <dbdump>/swipes/*.json, <dbdump>/forge/*.json    (export of the artifact store, optional)
// Usage: node scripts/jobs_seed.mjs [--scored <path>] [--sweep <glob-dir>] [--dbdump <dir>] [--api <base> --token <t>]
// With --api it POSTs through /api/jobs (works against prod without DATABASE_URL);
// without it, it writes via Prisma directly using DATABASE_URL from .env.local.
import fs from "node:fs"
import path from "node:path"

const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, arr) => (x.startsWith("--") ? [...a, [x.slice(2), arr[i + 1]]] : a), []))
const scoredPath = args.scored ?? "/Users/zharris/arcs-v9/runtime/job-search/opportunities-scored.jsonl"
const sweepDir = args.sweep ?? "runtime/job-search"
const dbdump = args.dbdump ?? null

const readJsonl = (p) => (fs.existsSync(p) ? fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : [])
const rows = new Map()
for (const r of readJsonl(scoredPath)) {
  rows.set(r.jobid, {
    jobid: r.jobid, title: r.title, company: r.company, location: r.location ?? null, url: r.url,
    alertQuery: r.alert_query ?? null, alertLocation: r.alert_location ?? null, source: r.source ?? "linkedin_alert_digest",
    firstSeen: r.first_seen_date, seenCount: r.seen_count ?? 1,
    composite: r.composite ?? null, band: r.band ?? "UNSCORED", dims: r.dimensions ?? null, gates: r.hard_gates ?? null,
    assessment: r.assessment ?? null, compBand: r.comp_band ?? null, workLocation: r.work_location ?? null,
    unscoredWhy: r.band === "UNSCORED" ? "8/31 run stopped before reading this JD" : null,
    scoredAt: r.band && r.band !== "UNSCORED" ? "2026-08-31T13:31:00Z" : null,
  })
}
if (fs.existsSync(sweepDir)) {
  for (const f of fs.readdirSync(sweepDir).filter((f) => f.startsWith("sweep-") && f.endsWith(".jsonl"))) {
    for (const r of readJsonl(path.join(sweepDir, f))) {
      if (rows.has(r.jobid)) continue
      rows.set(r.jobid, {
        jobid: r.jobid, title: r.title, company: r.company, location: r.location ?? null, url: r.url,
        alertQuery: r.alert_query ?? null, alertLocation: r.alert_location ?? null, source: r.source ?? "linkedin_alert_digest",
        firstSeen: r.first_seen_date, seenCount: r.seen_count ?? 1, band: "UNSCORED",
        unscoredWhy: "net-new in the 9/1 to 9/4 sweep, scorer not yet run",
      })
    }
  }
}
// Board-only enrichments that never made it into the scored file (ATS, company type, contact, hand grades).
const enrich = {
  "4420203328": { atsClass: "old", atsName: "Workday", companyType: "enterprise", contactType: "portal", contactDetail: "Workday re-key, then find the practice lead on LinkedIn", hmKind: "implicit", hmText: "Head of the GenAI practice (hands-on lead, mentors 3 to 4)", nextStep: "Find the practice lead on LinkedIn before the Workday re-key. Cover note leads with embed-with-clients." },
  "4459454074": { atsClass: "old", atsName: "Workday", companyType: "enterprise", contactType: "portal", contactDetail: "Workday", nextStep: "Identify the existing co-lead. Platform-enablement framing, not customer-embed." },
  "4450095632": { atsClass: "old", atsName: "Workday + Eightfold", companyType: "enterprise", contactType: "portal", contactDetail: "Eightfold front end over Workday", nextStep: "People-management scope is explicit. Decide if you want headcount before spending a cut." },
  "4266778287": { atsClass: "new", atsName: "Ashby", companyType: "startup", contactType: "form", contactDetail: "Ashby board", contactUrl: "https://jobs.ashbyhq.com/norm-ai", nextStep: "One PDF upload, fast loop. Warm intro beats cold here; check 2nd-degree first." },
  "4450628250": { atsClass: "new", atsName: "Greenhouse", companyType: "scaleup", contactType: "form", contactDetail: "Greenhouse on aircall.io/careers", nextStep: "Two-hires-in-one pitch fits exactly. Reuse the recruithaus positioning page." },
  "4441207605": { atsClass: "unk", atsName: "likely Workday", companyType: "enterprise", nextStep: "Resolve ATS. A second Bain PM role landed 9/1, same org, bundle the read." },
  "4460193996": { atsClass: "unk", atsName: "likely Comeet", companyType: "enterprise", nextStep: "Comp is under target. Only worth it as a foot in the door for the FDE req." },
  "4460592986": { atsClass: "unk", atsName: "unverified", companyType: "startup", hmKind: "implicit", hmText: "Founder / CEO (founding hire)", nextStep: "Founding role means the founder reads it. A teardown of their product beats a resume." },
  "4460560416": { atsClass: "unk", atsName: "likely Comeet", companyType: "enterprise", nextStep: "Pair with the Deployment Architect row. One application, ask which req fits." },
  "4460555968": { atsClass: "unk", atsName: "unverified", companyType: "startup", hmKind: "implicit", hmText: "Founder (stealth, small)", nextStep: "Scientist title is a stretch on role-shape. Confirm applied, not research, before a cut." },
  "4454311856": { atsClass: "unk", atsName: "unverified", companyType: "scaleup", nextStep: "Culture screen scored 0 on JD wording. Right only if you want to test that read." },
  "4450636067": { atsClass: "unk", atsName: "unverified", companyType: "startup", nextStep: "Re-read the JD. Sits on the cutoff edge." },
}
for (const [id, e] of Object.entries(enrich)) if (rows.has(id)) Object.assign(rows.get(id), e)
rows.set("bjak-7629ca49", {
  jobid: "bjak-7629ca49", title: "Technical Product Lead, AI Neobank", company: "Bjak", location: "Remote, SEA time zones",
  url: "https://jobs.ashbyhq.com/bjakcareer/7629ca49-05c4-46ab-8b10-95a78eaa320f", alertQuery: "manual", source: "manual",
  firstSeen: "2026-09-04", composite: 0.625, band: "CONSIDER",
  dims: { role_shape: 2, ai_native: 2, strength_leverage: 3, scope_authority: 3, culture: 0, comp_level: 1, logistics: 2, warm_path: 0 }, gates: [],
  assessment: "Regulated, high-consequence product with an explicit when-not-to-use-AI bar. PM-shaped rather than forward-deployed; culture wording and unlisted comp are the swing.",
  atsClass: "new", atsName: "Ashby", companyType: "startup", hmKind: "explicit", hmText: "CEO (final round per JD)",
  contactType: "form", contactDetail: "Ashby; assessment first, CEO final round", contactUrl: "https://jobs.ashbyhq.com/bjakcareer/7629ca49-05c4-46ab-8b10-95a78eaa320f",
  nextStep: "Two swing dims: reviews and comp. Tips to 0.72 if both clear. Your call, not the rubric's.", scoredAt: "2026-09-04T17:00:00Z",
})

const swipes = [], forges = []
if (dbdump) {
  for (const f of fs.existsSync(path.join(dbdump, "swipes")) ? fs.readdirSync(path.join(dbdump, "swipes")) : []) {
    const d = JSON.parse(fs.readFileSync(path.join(dbdump, "swipes", f), "utf8")); const body = d.data ?? d
    swipes.push({ jobid: f.replace(/\.json$/, ""), direction: body.v, why: body.why ?? null, at: new Date(body.t).toISOString() })
  }
  for (const f of fs.existsSync(path.join(dbdump, "forge")) ? fs.readdirSync(path.join(dbdump, "forge")) : []) {
    const d = JSON.parse(fs.readFileSync(path.join(dbdump, "forge", f), "utf8")); const body = d.data ?? d
    forges.push({ jobid: f.replace(/\.json$/, ""), status: body.status, url: body.url ?? null, resumeUrl: body.resume_url ?? null,
      hm: body.hm ?? null, contact: body.contact ?? null, notes: body.notes ?? null, requestedAt: body.requested ? new Date(body.requested).toISOString() : null })
  }
}
console.log(`rows ${rows.size} · swipes ${swipes.length} · forges ${forges.length}`)

if (args.api) {
  const H = { "content-type": "application/json", "x-jobs-token": args.token ?? "" }
  const r = await fetch(`${args.api}/api/jobs`, { method: "POST", headers: H, body: JSON.stringify([...rows.values()]) })
  console.log("upsert", r.status, await r.text())
  for (const s of swipes) console.log("swipe", s.jobid, (await fetch(`${args.api}/api/jobs/swipe`, { method: "POST", headers: H, body: JSON.stringify(s) })).status)
  for (const f of forges) console.log("forge", f.jobid, (await fetch(`${args.api}/api/jobs/forge`, { method: "PATCH", headers: H, body: JSON.stringify(f) })).status)
  process.exit(0)
}

// Direct Prisma path (needs DATABASE_URL; same adapter wiring as src/lib/db.ts).
const { PrismaClient } = await import("@prisma/client")
const { PrismaPg } = await import("@prisma/adapter-pg")
const { Pool } = await import("pg")
const { config } = await import("dotenv"); config({ path: ".env.local" }); config({ path: ".env" })
const u = new URL(process.env.DATABASE_URL)
const prisma = new PrismaClient({ adapter: new PrismaPg(new Pool({ host: u.hostname, port: Number(u.port) || 6543, database: u.pathname.slice(1), user: decodeURIComponent(u.username), password: decodeURIComponent(u.password), ssl: { rejectUnauthorized: false } })) })
for (const r of rows.values()) {
  const data = { ...r, firstSeen: new Date(r.firstSeen), scoredAt: r.scoredAt ? new Date(r.scoredAt) : null,
    dims: r.dims ? JSON.stringify(r.dims) : null, gates: r.gates ? JSON.stringify(r.gates) : null }
  const { jobid, ...rest } = data
  await prisma.jobOpportunity.upsert({ where: { jobid }, create: { jobid, ...rest }, update: rest })
}
for (const s of swipes) await prisma.jobSwipe.upsert({ where: { jobid: s.jobid }, create: { jobid: s.jobid, direction: s.direction, why: s.why, at: new Date(s.at) }, update: { direction: s.direction, why: s.why, at: new Date(s.at) } })
for (const f of forges) {
  const d = { status: f.status, url: f.url, resumeUrl: f.resumeUrl, hmKind: f.hm?.kind ?? null, hmText: f.hm?.text ?? null, contactType: f.contact?.type ?? null, contactDetail: f.contact?.detail ?? null, contactUrl: f.contact?.url ?? null, notes: f.notes }
  await prisma.forgeRun.upsert({ where: { jobid: f.jobid }, create: { jobid: f.jobid, ...d, requestedAt: f.requestedAt ? new Date(f.requestedAt) : new Date() }, update: d })
}
await prisma.jobBoardSetting.upsert({ where: { key: "cap" }, create: { key: "cap", value: "5" }, update: {} })
console.log("seeded via prisma")
await prisma.$disconnect()
