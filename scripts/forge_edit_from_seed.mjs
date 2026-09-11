#!/usr/bin/env node
// forge_edit_from_seed.mjs — clear queued roles CHEAPLY by editing a built
// bundle's resume instead of a fresh forge. For a target role it finds the
// highest-scoring BUILT bundle in the same shape cluster (the seed), reads that
// seed's resume HTML locally, fetches the target JD, and posts both to
// POST /api/jobs/edit-from-seed (holds the key; edits, does not regenerate).
// It then renders the edited resume to a 2-page PDF + ATS text locally, writes a
// resume-only bundle, registers it, marks the row built, and mirrors to iCloud.
// No landing page (resume is the deliverable; a role that advances gets a full
// forge). ~1/3 the tokens of a full forge.
//
//   node scripts/forge_edit_from_seed.mjs --jobid <id> [--seed <slug>]
//   node scripts/forge_edit_from_seed.mjs --auto            # top queued in a seeded cluster
//   node scripts/forge_edit_from_seed.mjs --jobid <id> --dry-run   # pick seed + fetch JD, no model
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE.

import fs from "node:fs"
import path from "node:path"
import { execSync } from "node:child_process"

const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const DRY = has("--dry-run")
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const ICLOUD = process.env.ICLOUD_RESUMES || `${process.env.HOME}/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes`

const shape = (r) => {
  const t = `${r.title} ${r.company}`.toLowerCase()
  if (/forward deployed|deployment|solutions? eng|field eng|\bfde\b/.test(t)) return "FDE"
  if (/applied ai|ai engineer|ml engineer|research eng|technical staff/.test(t)) return "Applied-AI"
  if (/product manager|product lead|\bpm\b|product owner/.test(t)) return "PM"
  if (/product engineer|founding eng|full stack/.test(t)) return "Product-Eng"
  return "Other"
}
const slugify = (r) => `${r.company} ${r.title}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40).replace(/-$/, "")
const strip = (html) => { const m = html.match(/<div class="show-more-less-html__markup[^"]*">([\s\S]*?)<\/div>/); const b = m ? m[1] : html; return b.replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim() }
async function fetchJD(r) {
  try { if (/^\d+$/.test(r.jobid)) { const x = await fetch(`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/${r.jobid}`, { headers: { "user-agent": "Mozilla/5.0" } }); if (x.ok) { const t = strip(await x.text()); if (t.length > 200) return t } } } catch { /* */ }
  try { if (r.url) { const x = await fetch(r.url, { headers: { "user-agent": "Mozilla/5.0" } }); if (x.ok) { const t = strip(await x.text()); if (t.length > 200) return t } } } catch { /* */ }
  return null
}
const readSeedHtml = (dir) => {
  const d = path.join("_ARTIFACTS", dir)
  const files = fs.readdirSync(d).filter((f) => /^resume-.*\.html$/.test(f))
  const pick = files.find((f) => f.includes("-ats")) || files[0]
  return pick ? { html: fs.readFileSync(path.join(d, pick), "utf8"), file: pick } : null
}

async function main() {
  const man = JSON.parse(fs.readFileSync("runtime/specs/forge-bundles.json", "utf8")).bundles
  const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  const built = rows.filter((r) => r.forge && (r.forge.status === "built" || r.forge.status === "live"))
  // seed per shape = highest-composite built bundle whose jobid is in the manifest
  const seedByShape = {}
  for (const r of built.sort((a, b) => (b.composite || 0) - (a.composite || 0))) {
    const s = shape(r); if (!seedByShape[s] && man[r.jobid]) seedByShape[s] = { slug: man[r.jobid].slug, dir: man[r.jobid].dir, jobid: r.jobid }
  }

  let targets
  const jid = arg("--jobid", null)
  if (jid) targets = rows.filter((r) => r.jobid === String(jid))
  else if (has("--auto")) {
    const queued = rows.filter((r) => r.forge && r.forge.status === "queued" && seedByShape[shape(r)]).sort((a, b) => (b.composite || 0) - (a.composite || 0))
    targets = queued.slice(0, 1)
  } else { console.error("pass --jobid <id> or --auto"); process.exit(2) }
  if (!targets.length) { console.error("no matching target (no seed for its cluster?)"); process.exit(1) }

  for (const t of targets) {
    const sh = shape(t); const seed = arg("--seed", null) ? Object.values(seedByShape).find((s) => s.slug === arg("--seed", null)) : seedByShape[sh]
    if (!seed) { console.error(`${t.jobid}: no seed for cluster ${sh}`); continue }
    const slug = slugify(t)
    console.log(`target ${t.jobid} [${sh}] ${t.company} · ${t.title}\n  seed: ${seed.slug} (${seed.dir})`)
    const seedHtml = readSeedHtml(seed.dir); if (!seedHtml) { console.error("  seed has no resume HTML"); continue }
    const jd = await fetchJD(t); if (!jd) { console.error("  JD fetch failed"); continue }
    if (DRY) { console.log(`  DRY: would edit seed ${seedHtml.file} (${seedHtml.html.length} chars) against JD (${jd.length} chars) into forge-${slug}/`); continue }

    const resp = await fetch(`${BASE}/api/jobs/edit-from-seed`, { method: "POST", headers: H, body: JSON.stringify({ jobid: t.jobid, title: t.title, company: t.company, jd, seedSlug: seed.slug, seedResumeHtml: seedHtml.html }) })
    if (!resp.ok) { console.error(`  edit failed: ${resp.status} ${(await resp.text()).slice(0, 200)}`); continue }
    const e = await resp.json()
    // apply the PATCH to the seed HTML locally (pay for the delta, not the document)
    let html = seedHtml.html, applied = 0, missed = []
    for (const ed of e.edits || []) {
      if (typeof ed.find === "string" && html.includes(ed.find)) { html = html.replace(ed.find, String(ed.replace ?? "")); applied++ }
      else missed.push((ed.find || "").slice(0, 40))
    }
    if (applied === 0) { console.error(`  no edits applied (all ${(e.edits||[]).length} find-strings missed the seed) — skipped`); continue }
    if (missed.length) console.log(`  applied ${applied}/${(e.edits||[]).length} edits (${missed.length} find-strings not located)`)
    const d = path.join("_ARTIFACTS", `forge-${slug}`); fs.mkdirSync(d, { recursive: true })
    fs.writeFileSync(path.join(d, `resume-${slug}.html`), html)
    fs.writeFileSync(path.join(d, "jd-full.txt"), jd)
    fs.writeFileSync(path.join(d, "TAILOR-NOTES.md"), `# ${t.company} · ${t.title}\n\nEDIT-FROM-SEED of \`${seed.slug}\` (cluster ${sh}). ${new Date().toISOString()}\n\n${e.tailorDelta || ""}\n\nAssessment: ${e.assessment || ""}\n`)
    fs.writeFileSync(path.join(d, "hiring-manager.json"), JSON.stringify(e.hiringManager || { kind: "unknown", text: null }, null, 1))
    fs.writeFileSync(path.join(d, "contact.json"), JSON.stringify(e.contact || { type: "unverified", detail: null }, null, 1))
    fs.writeFileSync(path.join(d, "cost.json"), JSON.stringify({ mode: "edit-from-seed", seed: seed.slug, usage: e.usage }, null, 1))
    // render locally: HTML -> PDF + page PNGs (headless Chrome), + ATS text
    let pages = 0
    try {
      const chrome = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"].find((c) => fs.existsSync(c))
      const abs = path.resolve(d, `resume-${slug}.html`), pdf = path.resolve(d, `resume-${slug}.pdf`)
      execSync(`"${chrome}" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="${pdf}" "file://${abs}"`, { stdio: "ignore" })
      execSync(`pdftoppm -png -r 110 "${pdf}" "${path.resolve(d, `resume-${slug}-page`)}" 2>/dev/null || true`, { stdio: "ignore" })
      pages = Number(execSync(`pdfinfo "${pdf}" | awk '/^Pages/{print $2}'`).toString().trim())
      // ATS text
      const txt = html.replace(/<style[\s\S]*?<\/style>/g, "").replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()
      fs.writeFileSync(path.join(d, `resume-${slug}-ats.txt`), txt)
    } catch (err) { console.error("  render error:", err.message) }
    // air-gap on the resume HTML
    const em = html.includes("—"), sv = /\b(tier|band|composite|pursue)\b/i.test(html)
    if (pages !== 2 || em || sv) { console.error(`  QC FAIL: pages=${pages} em=${em} sv=${sv} — left in bundle, NOT marked built`); continue }
    // register + mark built + mirror
    const p = "runtime/specs/forge-bundles.json"; const m = JSON.parse(fs.readFileSync(p, "utf8"))
    m.bundles[t.jobid] = { dir: `forge-${slug}`, slug, resume: `resume-${slug}.pdf`, resume_pdf: `resume-${slug}.pdf`, resume_txt: `resume-${slug}-ats.txt` }
    fs.writeFileSync(p, JSON.stringify(m, null, 2))
    await fetch(`${BASE}/api/jobs/forge`, { method: "PATCH", headers: H, body: JSON.stringify({ jobid: t.jobid, status: "built", url: `/jobs/${t.jobid}/forge`, resumeUrl: `/jobs/${t.jobid}/forge?file=resume-${slug}.pdf&dl=1`, notes: `edit-from-seed of ${seed.slug} (${sh} cluster). Resume-only cut.` }) })
    const out = path.join(ICLOUD, slug); fs.mkdirSync(path.join(out, "_bundle"), { recursive: true })
    fs.copyFileSync(path.join(d, `resume-${slug}.pdf`), path.join(out, `Zach-Harris-Resume-${slug}.pdf`))
    if (fs.existsSync(path.join(d, `resume-${slug}-ats.txt`))) fs.copyFileSync(path.join(d, `resume-${slug}-ats.txt`), path.join(out, `Zach-Harris-Resume-${slug}-ATS.txt`))
    for (const f of fs.readdirSync(d)) { try { fs.copyFileSync(path.join(d, f), path.join(out, "_bundle", f)) } catch { /* */ } }
    fs.appendFileSync("_STATE/job-search/forge-cost-ledger.jsonl", JSON.stringify({ date: new Date().toISOString().slice(0, 10), target: slug, stage: "edit-from-seed", seed: seed.slug, in_tokens: e.usage?.input, out_tokens: e.usage?.output, metered: true }) + "\n")
    console.log(`  BUILT (edit-from-seed): 2 pages, air-gap clean, mirrored. tokens in=${e.usage?.input} out=${e.usage?.output}`)
  }
}
main().catch((e) => { console.error(e); process.exit(1) })
