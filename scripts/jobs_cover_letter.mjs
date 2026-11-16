#!/usr/bin/env node
// jobs_cover_letter.mjs — tailored cover letters, one per role, in Zach's voice.
// For a built bundle it reads the role's JD (bundle jd-full.txt if present, else
// fetch by jobid) and the bundle resume text, uses the platinum reference cover
// as the voice model, and POSTs to /api/jobs/cover-letter. Writes cover-<slug>.md
// (full + short) and renders cover-<slug>.pdf into the bundle, then mirrors to
// iCloud beside the resumes. The personal medical note is never auto-included.
// Job Factory slice 7: files ex-ante.json (the board's prediction) before writing,
// runs scripts/jobs_prose_gate.py on every draft, and mirrors to iCloud ONLY drafts
// the gate marks READY; HELD drafts stay in the bundle with <draft>.gate.json.
//   node scripts/jobs_cover_letter.mjs --jobid <id>
//   node scripts/jobs_cover_letter.mjs --pursue          # every built PURSUE bundle
//   ... --questions q.txt   # also answer application questions (one per line)
//   ... --waive-gauntlet "<reason>"   # Zach's explicit waiver, recorded in the gate print
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE.
import { aiPolicyFor, priorVerdict } from "./jobs_sources.mjs"
import fs from "node:fs"; import path from "node:path"; import { execSync, spawnSync } from "node:child_process"
const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN; if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const ICLOUD = process.env.ICLOUD_RESUMES || `${process.env.HOME}/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes`
const SEED = fs.readFileSync("_ARTIFACTS/resume-blacksmith/cover-letter-blacksmith.md", "utf8")
const strip = (h) => { const m = h.match(/<div class="show-more-less-html__markup[^"]*">([\s\S]*?)<\/div>/); const b = m ? m[1] : h; return b.replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim() }
async function fetchJD(jobid, url) {
  // linkedin.com is never fetched (robots.txt disallows all paths, 2026-11-16); a LinkedIn row needs its JD pasted or an ATS twin.
  try { if (url && !/(^|\.)linkedin\.com\//i.test(url.replace(/^https?:\/\//, ""))) { const x = await fetch(url, { headers: { "user-agent": "Mozilla/5.0" } }); if (x.ok) { const t = strip(await x.text()); if (t.length > 200) return t } } } catch {}
  return null
}
// Run the prose gate; returns "READY" | "HELD". Never throws: a gate that cannot run HOLDS.
function proseGate(dir, file) {
  const args = ["scripts/jobs_prose_gate.py", "--bundle", dir, "--draft", path.join(dir, file)]
  const w = arg("--waive-gauntlet", null); if (typeof w === "string") args.push("--waive-gauntlet", w)
  const r = spawnSync("python3", args, { encoding: "utf8" })
  console.log(`  gate: ${(r.stdout || r.stderr || "").trim().split("\n").pop()}`)
  return r.status === 0 ? "READY" : "HELD"
}
// The ex-ante receipt: what the board predicted for this row, filed before any draft exists.
function fileExAnte(dir, row) {
  const p = path.join(dir, "ex-ante.json"); if (fs.existsSync(p)) return
  fs.writeFileSync(p, JSON.stringify({ jobid: row.jobid, company: row.company, title: row.title, composite: row.composite ?? null, band: row.band ?? null, assessment: row.assessment ?? null, scoredAt: row.scoredAt ?? null, filedAt: new Date().toISOString(), source: "jobs.arcs.care /api/jobs row at draft time" }, null, 2))
}
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

async function one(row, man) {
  const b = man[row.jobid]; if (!b) { console.log(`skip ${row.jobid}: no bundle`); return false }
  const dir = path.join("_ARTIFACTS", b.dir)
  let jd = null; const jf = path.join(dir, "jd-full.txt")
  if (fs.existsSync(jf)) jd = fs.readFileSync(jf, "utf8"); else jd = await fetchJD(row.jobid, row.url)
  if (!jd) { console.log(`skip ${b.slug}: no JD`); return false }
  const rt = fs.readdirSync(dir).find((f) => /^resume-.*\.txt$/.test(f))
  const resumeText = rt ? fs.readFileSync(path.join(dir, rt), "utf8") : ""
  fileExAnte(dir, row)
  const qf = arg("--questions", null)
  const questions = typeof qf === "string" ? fs.readFileSync(qf, "utf8").split("\n").map((q) => q.trim()).filter(Boolean).slice(0, 8) : []
  const resp = await fetch(`${BASE}/api/jobs/cover-letter`, { method: "POST", headers: H, body: JSON.stringify({ jobid: row.jobid, title: row.title, company: row.company, jd, seedCover: SEED, resumeText, questions }) })
  if (!resp.ok) { console.log(`FAIL ${b.slug}: ${resp.status} ${(await resp.text()).slice(0, 120)}`); return false }
  const e = await resp.json()
  const md = `# Cover letter: ${row.company} · ${row.title}\n_Draft. Plain text below is paste-ready. Add any personal availability note by hand._\n\n---\n\n${e.coverMd}\n\n---\n\n## Short version (form-field, ~180 words)\n\n${e.coverShort}\n\n---\n_Hook: ${e.hook || ""}_\n`
  fs.writeFileSync(path.join(dir, `cover-${b.slug}.md`), md)
  // render a simple print-clean PDF from the full cover
  const html = `<!doctype html><meta charset=utf-8><style>@page{size:letter;margin:1in}body{font:11pt/1.5 Georgia,serif;color:#111}p{margin:0 0 11pt}</style><body>${e.coverMd.split(/\n\n+/).map((p) => `<p>${esc(p).replace(/\n/g, "<br>")}</p>`).join("")}</body>`
  const hp = path.join(dir, `cover-${b.slug}.html`); fs.writeFileSync(hp, html)
  try {
    const chrome = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"].find((c) => fs.existsSync(c))
    execSync(`"${chrome}" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="${path.resolve(dir, `cover-${b.slug}.pdf`)}" "file://${path.resolve(hp)}"`, { stdio: "ignore" })
  } catch (err) { console.log(`  pdf render skipped: ${err.message}`) }
  const files = [`cover-${b.slug}.md`]
  if (Array.isArray(e.answers) && e.answers.length) {
    const amd = `# Application answers: ${row.company} · ${row.title}\n_Draft. Each answer uses only claims in the resume text for this role._\n\n${e.answers.map((a) => `## ${a.question}\n\n${a.answer}\n`).join("\n")}`
    fs.writeFileSync(path.join(dir, `answers-${b.slug}.md`), amd); files.push(`answers-${b.slug}.md`)
  }
  const verdicts = Object.fromEntries(files.map((f) => [f, proseGate(dir, f)]))
  // mirror to iCloud: READY drafts only, so nothing HELD looks send-ready on the phone
  const out = path.join(ICLOUD, b.slug); fs.mkdirSync(path.join(out, "_bundle"), { recursive: true })
  const mirror = verdicts[`cover-${b.slug}.md`] === "READY" ? [`cover-${b.slug}.pdf`, `cover-${b.slug}.md`] : []
  if (verdicts[`answers-${b.slug}.md`] === "READY") mirror.push(`answers-${b.slug}.md`)
  for (const f of mirror) { const src = path.join(dir, f); if (fs.existsSync(src)) fs.copyFileSync(src, path.join(out, f.startsWith("cover") && f.endsWith(".pdf") ? `Zach-Harris-Cover-${b.slug}.pdf` : f)) }
  console.log(`${Object.values(verdicts).every((v) => v === "READY") ? "READY" : "HELD"} ${b.slug} · ${Object.entries(verdicts).map(([f, v]) => `${f}=${v}`).join(" ")} · tokens in=${e.usage?.input} out=${e.usage?.output}`)
  return true
}

async function main() {
  const man = JSON.parse(fs.readFileSync("runtime/specs/forge-bundles.json", "utf8")).bundles
  const { rows } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  const byId = Object.fromEntries(rows.map((r) => [String(r.jobid), r]))
  let targets = []
  const jid = arg("--jobid", null)
  if (jid) targets = [byId[String(jid)]].filter(Boolean)
  else if (has("--pursue")) targets = rows.filter((r) => man[r.jobid] && r.band === "PURSUE")
  else { console.error("pass --jobid <id> or --pursue"); process.exit(2) }
  let ok = 0
  for (const r of targets) {
    const pol = aiPolicyFor(r.company)
    if (pol) { console.error(`${r.jobid}: REFUSED, ${r.company} forbids AI-drafted applications (${pol.source}). Zach drafts first; Claude may only refine.`); process.exitCode = 3; continue }
    const prior = priorVerdict(r.company, r.title)
    if (prior?.level === "block" && !process.argv.includes("--override-prior")) { console.error(`${r.jobid}: REFUSED, ${prior.reason} (runtime/specs/prior-applications.json; --override-prior on Zach's say-so)`); process.exitCode = 3; continue }
    if (prior && prior.level !== "block") console.error(`${r.jobid}: NOTE ${prior.level}, ${prior.reason}`)
    if (await one(r, man)) ok++
  }
  console.log(`\ncovers written: ${ok}/${targets.length}`)
}
main().catch((e) => { console.error(e); process.exit(1) })
