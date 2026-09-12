#!/usr/bin/env node
// forge_render.mjs — the render engine for forge bundles (résumé + cover letter).
// One canonical print stylesheet (runtime/specs/forge-render/resume-print.css) and one
// cover template (cover-print.html) so every bundle reads as one system, and a QC gate
// that fails the bundle instead of shipping a defect.
//
// Résumé pass, per bundle:
//   1. swap the résumé HTML's <style> block for the canonical stylesheet
//   2. strip internal identifiers the editor sometimes leaks into the target chip
//      (board jobids like bridge-ramp-815eb8e2) and restore the archetype tagline the
//      seed carried (the headline names an archetype, never the req)
//   3. make the contact lines real links
//   4. render PDF (headless Chrome) + page PNGs + ATS text
//   5. QC: exactly 2 pages, no em-dashes, no scoring vocabulary, no internal ids
//   6. mirror to iCloud beside the résumés
// Cover pass: renderCover() fills cover-print.html and renders it (used by jobs_cover_letter.mjs).
//
//   node scripts/forge_render.mjs --bundle forge-ramp-ai-solutions-strategist
//   node scripts/forge_render.mjs --bridge           # every bundle carrying jobid.txt (the bridge lane) + the seed
//   node scripts/forge_render.mjs --all              # every forge-* bundle with a résumé HTML
//   node scripts/forge_render.mjs --bundle <dir> --no-mirror
import fs from "node:fs"
import path from "node:path"
import { execSync } from "node:child_process"
import { fileURLToPath } from "node:url"

const ROOT = process.cwd()
const CSS = fs.readFileSync(path.join(ROOT, "runtime", "specs", "forge-render", "resume-print.css"), "utf8")
const COVER_TPL = fs.readFileSync(path.join(ROOT, "runtime", "specs", "forge-render", "cover-print.html"), "utf8")
const ICLOUD = process.env.ICLOUD_RESUMES || `${process.env.HOME}/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes`
const CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"].find((c) => fs.existsSync(c))

// Archetype taglines by cluster. The edit worker is told to keep the seed headline verbatim,
// but it drifts; the render pass restores it so the headline never re-points to a req title.
export const TAGLINE_BY_CLUSTER = {
  Bridge: "Revenue and GTM systems operator who builds",
  PM: "AI-native product builder · expert-user workflows",
}
const INTERNAL_ID = /\s*·?\s*\b(bridge|manual|eval)-[a-z0-9]+-[0-9a-f]{6,}\b/gi
const SCORING = /\b(tier|band|composite|pursue)\b/i
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

export function clusterOf(dir) {
  const notes = path.join(dir, "TAILOR-NOTES.md")
  if (fs.existsSync(notes)) { const m = fs.readFileSync(notes, "utf8").match(/cluster (\w+)/); if (m) return m[1] }
  return null
}

export function restyleResume(html, cluster) {
  let out = html.replace(/<style>[\s\S]*?<\/style>/, `<style>\n${CSS}</style>`)
  out = out.replace(/(<div class="target">)([^<]*)(<\/div>)/, (_, a, t, z) => `${a}${t.replace(INTERNAL_ID, "").replace(/\s*·\s*$/, "").trim()}${z}`)
  out = out.replace(INTERNAL_ID, "")
  const tag = cluster && TAGLINE_BY_CLUSTER[cluster]
  if (tag) out = out.replace(/(<div class="tagline">)[^<]*(<\/div>)/, `$1${esc(tag)}$2`)
  out = out.replace(/<b>zach\.harris@gmail\.com<\/b>/, `<a href="mailto:zach.harris@gmail.com"><b>zach.harris@gmail.com</b></a>`)
  out = out.replace(/linkedin\.com\/in\/<b>zharris<\/b>/, `<a href="https://www.linkedin.com/in/zharris">linkedin.com/in/<b>zharris</b></a>`)
  return out
}

export function pdf(htmlPath, pdfPath) {
  if (!CHROME) throw new Error("no headless Chrome found")
  execSync(`"${CHROME}" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="${path.resolve(pdfPath)}" "file://${path.resolve(htmlPath)}"`, { stdio: "ignore" })
  const pages = Number(execSync(`pdfinfo "${path.resolve(pdfPath)}" | awk '/^Pages/{print $2}'`).toString().trim())
  return pages
}
export function pngs(pdfPath, prefix) { try { execSync(`pdftoppm -png -r 110 "${path.resolve(pdfPath)}" "${path.resolve(prefix)}"`, { stdio: "ignore" }) } catch { /* optional */ } }
export const atsText = (html) => html.replace(/<style[\s\S]*?<\/style>/g, "").replace(/<[^>]+>/g, "\n").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&[a-z]+;/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()

export function qc(html, pages, expectPages) {
  const fails = []
  if (expectPages && pages !== expectPages) fails.push(`pages=${pages} (want ${expectPages})`)
  if (html.includes("—")) fails.push("em-dash")
  if (SCORING.test(atsText(html))) fails.push("scoring vocabulary")
  if (INTERNAL_ID.test(html)) fails.push("internal id")
  INTERNAL_ID.lastIndex = 0
  return fails
}

export function mirror(dir, slug, files) {
  const out = path.join(ICLOUD, slug); fs.mkdirSync(path.join(out, "_bundle"), { recursive: true })
  for (const [src, dst] of files) { const s = path.join(dir, src); if (fs.existsSync(s)) fs.copyFileSync(s, path.join(out, dst)) }
  for (const f of fs.readdirSync(dir)) { try { fs.copyFileSync(path.join(dir, f), path.join(out, "_bundle", f)) } catch { /* */ } }
}

export function renderResume(dir, { mirrorToCloud = true } = {}) {
  const file = fs.readdirSync(dir).find((f) => /^resume-.*\.html$/.test(f) && !f.includes("-ats"))
  if (!file) return { ok: false, fails: ["no résumé html"] }
  const slug = file.replace(/^resume-/, "").replace(/\.html$/, "")
  const cluster = clusterOf(dir)
  const html = restyleResume(fs.readFileSync(path.join(dir, file), "utf8"), cluster)
  fs.writeFileSync(path.join(dir, file), html)
  const pdfPath = path.join(dir, `resume-${slug}.pdf`)
  const pages = pdf(path.join(dir, file), pdfPath)
  pngs(pdfPath, path.join(dir, `resume-${slug}-page`))
  fs.writeFileSync(path.join(dir, `resume-${slug}-ats.txt`), atsText(html))
  const fails = qc(html, pages, 2)
  if (!fails.length && mirrorToCloud) mirror(dir, slug, [[`resume-${slug}.pdf`, `Zach-Harris-Resume-${slug}.pdf`], [`resume-${slug}-ats.txt`, `Zach-Harris-Resume-${slug}-ATS.txt`]])
  return { ok: !fails.length, fails, pages, slug, cluster }
}

// Cover letter: coverMd is plain paragraphs (blank-line separated). The last block that starts
// with "Zach" becomes the signature. Returns { pages, fails }.
export function renderCover(dir, slug, { title, company, coverMd, cluster, mirrorToCloud = true }) {
  const paras = String(coverMd).split(/\n\s*\n+/).map((p) => p.trim()).filter(Boolean)
  const body = paras.map((p, i) => {
    const isSign = i === paras.length - 1 && /^zach\b/i.test(p)
    if (isSign) { const [name, ...rest] = p.split("\n"); return `    <p class="sign">${esc(name)}${rest.length ? `<small>${esc(rest.join(" · "))}</small>` : ""}</p>` }
    return `    <p>${esc(p).replace(/\n/g, "<br>")}</p>`
  }).join("\n")
  const html = COVER_TPL.replace(/{{TITLE}}/g, esc(`Zach Harris · Cover letter · ${title} · ${company}`))
    .replace(/{{TAGLINE}}/g, esc(TAGLINE_BY_CLUSTER[cluster] || "Revenue and GTM systems operator who builds"))
    .replace(/{{ROLE}}/g, esc(title)).replace(/{{COMPANY}}/g, esc(company)).replace(/{{YEAR}}/g, String(new Date().getFullYear()))
    .replace("{{BODY}}", body)
  const hp = path.join(dir, `cover-${slug}.html`); fs.writeFileSync(hp, html)
  const pdfPath = path.join(dir, `cover-${slug}.pdf`)
  const pages = pdf(hp, pdfPath)
  pngs(pdfPath, path.join(dir, `cover-${slug}-page`))
  const fails = qc(html, pages, 1)
  if (!fails.length && mirrorToCloud) mirror(dir, slug, [[`cover-${slug}.pdf`, `Zach-Harris-Cover-${slug}.pdf`], [`cover-${slug}.md`, `cover-${slug}.md`]])
  return { ok: !fails.length, fails, pages }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
  const has = (k) => process.argv.includes(k)
  const mirrorToCloud = !has("--no-mirror")
  let dirs = []
  if (arg("--bundle", null)) dirs = [String(arg("--bundle"))]
  else if (has("--bridge")) dirs = ["forge-bridge-operator-seed", ...fs.readdirSync("_ARTIFACTS").filter((d) => d.startsWith("forge-") && fs.existsSync(path.join("_ARTIFACTS", d, "jobid.txt")))]
  else if (has("--all")) dirs = fs.readdirSync("_ARTIFACTS").filter((d) => d.startsWith("forge-") && fs.readdirSync(path.join("_ARTIFACTS", d)).some((f) => /^resume-.*\.html$/.test(f)))
  else { console.error("pass --bundle <dir> | --bridge | --all"); process.exit(2) }
  let ok = 0
  for (const d of dirs) {
    const dir = path.join("_ARTIFACTS", d)
    const r = renderResume(dir, { mirrorToCloud })
    if (r.ok) ok++
    console.log(`${r.ok ? "OK  " : "FAIL"} ${d} · ${r.pages ?? "-"}p · ${r.cluster ?? "-"}${r.fails.length ? ` · ${r.fails.join(", ")}` : ""}`)
  }
  console.log(`\nrendered ${ok}/${dirs.length}`)
  process.exit(ok === dirs.length ? 0 : 1)
}
