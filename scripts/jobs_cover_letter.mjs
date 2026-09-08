#!/usr/bin/env node
// jobs_cover_letter.mjs — tailored cover letters, one per role, in Zach's voice.
// For a built bundle it reads the role's JD (bundle jd-full.txt if present, else
// fetch by jobid) and the bundle resume text, uses the platinum reference cover
// as the voice model, and POSTs to /api/jobs/cover-letter. Writes cover-<slug>.md
// (full + short) and renders cover-<slug>.pdf into the bundle, then mirrors to
// iCloud beside the resumes. The personal medical note is never auto-included.
//   node scripts/jobs_cover_letter.mjs --jobid <id>
//   node scripts/jobs_cover_letter.mjs --pursue          # every built PURSUE bundle
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE.
import fs from "node:fs"; import path from "node:path"; import { execSync } from "node:child_process"
const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN; if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const ICLOUD = process.env.ICLOUD_RESUMES || `${process.env.HOME}/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes`
const SEED = fs.readFileSync("_ARTIFACTS/resume-blacksmith/cover-letter-blacksmith.md", "utf8")
const strip = (h) => { const m = h.match(/<div class="show-more-less-html__markup[^"]*">([\s\S]*?)<\/div>/); const b = m ? m[1] : h; return b.replace(/<[^>]+>/g, "\n").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim() }
async function fetchJD(jobid, url) {
  try { if (/^\d+$/.test(jobid)) { const x = await fetch(`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/${jobid}`, { headers: { "user-agent": "Mozilla/5.0" } }); if (x.ok) { const t = strip(await x.text()); if (t.length > 200) return t } } } catch {}
  try { if (url) { const x = await fetch(url, { headers: { "user-agent": "Mozilla/5.0" } }); if (x.ok) { const t = strip(await x.text()); if (t.length > 200) return t } } } catch {}
  return null
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
  const resp = await fetch(`${BASE}/api/jobs/cover-letter`, { method: "POST", headers: H, body: JSON.stringify({ jobid: row.jobid, title: row.title, company: row.company, jd, seedCover: SEED, resumeText }) })
  if (!resp.ok) { console.log(`FAIL ${b.slug}: ${resp.status} ${(await resp.text()).slice(0, 120)}`); return false }
  const e = await resp.json()
  const md = `# Cover letter — ${row.company} · ${row.title}\n_Draft. Plain text below is paste-ready. Add any personal availability note by hand._\n\n---\n\n${e.coverMd}\n\n---\n\n## Short version (form-field, ~180 words)\n\n${e.coverShort}\n\n---\n_Hook: ${e.hook || ""}_\n`
  fs.writeFileSync(path.join(dir, `cover-${b.slug}.md`), md)
  // render a simple print-clean PDF from the full cover
  const html = `<!doctype html><meta charset=utf-8><style>@page{size:letter;margin:1in}body{font:11pt/1.5 Georgia,serif;color:#111}p{margin:0 0 11pt}</style><body>${e.coverMd.split(/\n\n+/).map((p) => `<p>${esc(p).replace(/\n/g, "<br>")}</p>`).join("")}</body>`
  const hp = path.join(dir, `cover-${b.slug}.html`); fs.writeFileSync(hp, html)
  try {
    const chrome = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"].find((c) => fs.existsSync(c))
    execSync(`"${chrome}" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="${path.resolve(dir, `cover-${b.slug}.pdf`)}" "file://${path.resolve(hp)}"`, { stdio: "ignore" })
  } catch (err) { console.log(`  pdf render skipped: ${err.message}`) }
  // mirror to iCloud
  const out = path.join(ICLOUD, b.slug); fs.mkdirSync(path.join(out, "_bundle"), { recursive: true })
  for (const f of [`cover-${b.slug}.pdf`, `cover-${b.slug}.md`]) { const src = path.join(dir, f); if (fs.existsSync(src)) fs.copyFileSync(src, path.join(out, f.startsWith("cover") && f.endsWith(".pdf") ? `Zach-Harris-Cover-${b.slug}.pdf` : f)) }
  console.log(`OK ${b.slug} · hook: ${(e.hook || "").slice(0, 70)} · tokens in=${e.usage?.input} out=${e.usage?.output}`)
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
  for (const r of targets) { if (await one(r, man)) ok++ }
  console.log(`\ncovers written: ${ok}/${targets.length}`)
}
main().catch((e) => { console.error(e); process.exit(1) })
