#!/usr/bin/env node
// jobs_sources.mjs: intake beyond LinkedIn alerts. Polls public job boards
// (Greenhouse boards-api, Lever postings API, Ashby posting-api, YC public job
// pages, the HN "Who is hiring?" thread via the public Algolia HN API), keeps
// titles and locations that fit runtime/specs/job-sources.json, and posts the
// new ones to the board UNSCORED. Scoring stays in scripts/jobs_score_sweep.mjs,
// which imports atsJD() from here to read these rows' JDs from the same APIs.
// Public JSON only: no logins, no Getro (its robots.txt disallows the API).
// Boards = the spec's own slugs plus every verified board in the employer index (spec employer_index).
//
//   node scripts/jobs_sources.mjs --dry-run                 # print new matches, write nothing
//   node scripts/jobs_sources.mjs --dry-run --source ashby  # one adapter
//   node scripts/jobs_sources.mjs --probe                   # one live board per adapter, raw counts
//   node scripts/jobs_sources.mjs --selftest                # offline fixtures for every adapter
//   node scripts/jobs_sources.mjs                           # post new rows, complete IngestRequests
//   node scripts/jobs_sources.mjs --import rows.json --source fonzi [--dry-run]
//        rows an agent read from an MCP-only source (Fonzi search_companies): [{id,title,company,location,url,salary?}].
//        Same title/location filter, dedupe and post as the adapters; read-only on Fonzi, never save interest.
//        --source jackandjill: matches read from Jack & Jill emails in Gmail (the app is never driven); url = the ATS twin when found.
// Env: JOBS_PIPELINE_TOKEN (falls back to ~/.arcs/jobs-pipeline.env), JOBS_BASE.

import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"

const HERE = path.dirname(fileURLToPath(import.meta.url))
export const SPEC = JSON.parse(fs.readFileSync(path.join(HERE, "..", "runtime", "specs", "job-sources.json"), "utf8"))
const UA = { "user-agent": "arcs-jobs-sources/1.0 (+https://jobs.arcs.care)", accept: "application/json" }
const SOURCE_KEY = { greenhouse: "greenhouse_board", lever: "lever_board", ashby: "ashby_board", yc: "yc_jobs", hn: "hn_whoishiring", fonzi: "fonzi", jackandjill: "jackandjill_match" }

// ---------- filters (pure) ----------
const rx = (p) => new RegExp(p, "i")
const INCLUDE = SPEC.titles.include.map((t) => ({ lane: t.lane, re: rx(t.pattern) }))
const EXCLUDE = rx(SPEC.titles.exclude)
const L = Object.fromEntries(["nymetro", "remote", "us_only", "drop_region"].map((k) => [k, rx(SPEC.location[k])]))

export function laneFor(title) {
  if (!title || EXCLUDE.test(title)) return null
  return INCLUDE.find((t) => t.re.test(title))?.lane ?? null
}
// true = some part is NY metro, US remote, or a US-wide label with no city; empty location is kept (the scorer reads logistics).
export function locationOk(loc, isRemote = false, title = "") {
  if (L.drop_region.test(title)) return false
  const s = String(loc || "").trim()
  if (!s) return true
  const remoteOk = !L.drop_region.test(s) || L.us_only.test(s) // "Berlin / Remote" is not a US remote role
  const parts = s.split(/;|\||\/| or |\n/i).map((p) => p.trim()).filter(Boolean)
  return parts.some((p) => {
    if (L.nymetro.test(p)) return true
    if (L.drop_region.test(p)) return false
    if (L.remote.test(p)) return remoteOk
    const bare = p.replace(new RegExp(SPEC.location.us_only, "gi"), "").replace(/[^a-z]/gi, "")
    return bare === ""
  }) || (isRemote && !L.drop_region.test(s))
}
const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim()
export const dupKey = (company, title) => `${norm(company)}|${norm(title)}`
const text = (html) => String(html || "").replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16))).replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'").replace(/&amp;/g, "&")
  .replace(/<\/(p|li|div|h\d)>|<br\s*\/?>/gi, "\n").replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n\n").trim()

function row(src, { id, title, company, location, url, salary = null, posted = null, jd = null }) {
  return { jobid: `${src}-${id}`, title, company, location: location || null, url, salary, source: SOURCE_KEY[src], alertQuery: laneFor(title), firstSeen: posted || new Date().toISOString(), atsName: src, contactType: "portal", contactUrl: url, hmKind: "unknown", jd }
}

// ---------- adapters: (slug) -> raw list; normalize(raw, slug) -> rows (pure, fixture-tested) ----------
export const ADAPTERS = {
  greenhouse: {
    url: (b) => `https://boards-api.greenhouse.io/v1/boards/${b}/jobs`,
    normalize: (d, b) => (d.jobs || []).map((j) => row("greenhouse", { id: `${b}-${j.id}`, title: j.title, company: d.meta?.name || b, location: j.location?.name, url: j.absolute_url, posted: j.first_published || j.updated_at })),
  },
  lever: {
    url: (o) => `https://api.lever.co/v0/postings/${o}?mode=json`,
    normalize: (d, o) => (Array.isArray(d) ? d : []).map((j) => {
      const loc = [j.categories?.location, ...(j.categories?.allLocations || [])].filter(Boolean).join("; ")
      const sal = j.salaryRange ? `${j.salaryRange.currency || ""} ${j.salaryRange.min}-${j.salaryRange.max}`.trim() : null
      return { ...row("lever", { id: `${o}-${j.id}`, title: j.text, company: o, location: loc || j.country, url: j.hostedUrl, salary: sal, posted: j.createdAt ? new Date(j.createdAt).toISOString() : null }), _remote: j.workplaceType === "remote" }
    }),
  },
  ashby: {
    url: (o) => `https://api.ashbyhq.com/posting-api/job-board/${o}?includeCompensation=true`,
    normalize: (d, o) => (d.jobs || []).filter((j) => j.isListed !== false).map((j) => {
      const loc = [j.location, ...(j.secondaryLocations || []).map((x) => x.location)].filter(Boolean).join("; ")
      return { ...row("ashby", { id: `${o}-${j.id}`, title: j.title, company: d.organizationName || o, location: loc, url: j.jobUrl, salary: j.compensation?.compensationTierSummary || null, posted: j.publishedAt, jd: j.descriptionPlain || null }), _remote: j.workplaceType === "Remote" } // isRemote is true for Hybrid roles; trust workplaceType only
    }),
  },
  yc: {
    url: (p) => `https://www.ycombinator.com${p}`,
    html: true,
    parse: (h) => JSON.parse(text(h.match(/data-page="([^"]*)"/)?.[1] || "{}").replace(/\n/g, " ")),
    normalize: (d) => (d.props?.jobPostings || []).map((j) => row("yc", { id: j.id, title: j.title, company: `${j.companyName}${j.companyBatchName ? ` (YC ${j.companyBatchName})` : ""}`, location: j.location, url: `https://www.ycombinator.com${j.url}`, salary: j.salaryRange || null })),
  },
  hn: {
    // slug = the story id; the CLI resolves the latest story first.
    url: (id) => `https://hn.algolia.com/api/v1/items/${id}`,
    normalize: (d) => (d.children || []).filter((c) => c.text && c.author).flatMap((c) => {
      const body = text(c.text)
      const head = body.split("\n")[0]
      const parts = head.split("|").map((s) => s.trim()).filter(Boolean)
      if (parts.length < 2) return []
      // HN posts often list several roles in one header segment; take the first segment that matches a lane.
      const roles = parts.slice(1).flatMap((p) => p.split(/,|;| and | \/ /).map((s) => s.trim())).filter((s) => s.length < 90)
      const hit = roles.find((s) => laneFor(s))
      if (!hit) return []
      const title = hit.replace(/^.*\.\s+/, "").replace(/:.*$/, "").trim() // "...location. Lead PM: works with" -> "Lead PM"
      // No recognisable place: hand the rest of the header to the location filter so "Malibu, CA | ONSITE" is dropped, not kept as unknown.
      const location = parts.find((p) => L.nymetro.test(p) || L.remote.test(p) || L.drop_region.test(p))
        || parts.slice(1).filter((p) => !p.includes(title) && !/https?:/i.test(p)).join(" | ").slice(0, 120) || null
      return [row("hn", { id: c.id, title, company: parts[0].replace(/\s*\(.*?\)\s*$/, ""), location, url: `https://news.ycombinator.com/item?id=${c.id}`, posted: c.created_at, jd: body })]
    }),
  },
}

async function getJSON(url, html = false) {
  const r = await fetch(url, { headers: html ? { ...UA, accept: "text/html" } : UA, signal: AbortSignal.timeout(20000) })
  if (!r.ok) throw new Error(`${r.status} ${url}`)
  return html ? r.text() : r.json()
}
async function latestHnStory() {
  const d = await getJSON(`https://hn.algolia.com/api/v1/search_by_date?${SPEC.hn.story_query}&hitsPerPage=5`)
  return (d.hits || []).find((h) => /who is hiring/i.test(h.title))?.objectID
}
// Boards from the curated employer index (family-friendly / best-workplaces lists resolved by
// scripts/bridge_index_scan.py probe + verify). Only verify "ok" boards; spec slugs win on overlap.
export function indexSlugs(index, ats) {
  return Object.values(index || {}).filter((m) => m && m.ats === ats && m.verify === "ok" && m.slug).map((m) => m.slug)
}
let INDEX = null
function employerIndex() {
  if (INDEX) return INDEX
  try { INDEX = JSON.parse(fs.readFileSync(path.join(HERE, "..", SPEC.employer_index.path), "utf8")) } catch { INDEX = {} }
  return INDEX
}
function slugsFor(name) {
  if (name === "yc") return SPEC.yc.pages
  const own = SPEC[name] || []
  if (!SPEC.employer_index || !["greenhouse", "lever", "ashby"].includes(name)) return own
  return [...new Set([...own, ...indexSlugs(employerIndex(), name)])]
}

// Fetch one adapter across its slugs; returns { rows, raw, errors }.
export async function pull(name, { slugs } = {}) {
  const a = ADAPTERS[name]
  const list = slugs || (name === "hn" ? [await latestHnStory()].filter(Boolean) : slugsFor(name))
  let raw = 0; const out = []; const errors = []
  for (const s of list) {
    try {
      const body = await getJSON(a.url(s), a.html)
      const rows = a.normalize(a.html ? a.parse(body) : body, s)
      raw += rows.length; out.push(...rows)
    } catch (e) { errors.push(`${name}:${s} ${e.message}`) }
    await new Promise((z) => setTimeout(z, 250))
  }
  const kept = out.filter((r) => r.alertQuery && locationOk(r.location, r._remote, r.title))
  return { rows: kept, raw, errors }
}

// JD for a row this module produced (used by jobs_score_sweep.mjs). null when not one of ours.
const ashbyCache = new Map()
export async function atsJD(r) {
  const m = String(r.jobid).match(/^(greenhouse|lever|ashby|yc|hn)-(.+)$/)
  if (!m) return null
  const [, src, rest] = m
  try {
    if (src === "greenhouse") { const i = rest.lastIndexOf("-"); const d = await getJSON(`https://boards-api.greenhouse.io/v1/boards/${rest.slice(0, i)}/jobs/${rest.slice(i + 1)}`); return text(d.content) }
    if (src === "lever") { const i = rest.indexOf("-"); const d = await getJSON(`https://api.lever.co/v0/postings/${rest.slice(0, i)}/${rest.slice(i + 1)}`); return [d.descriptionPlain, ...(d.lists || []).map((l) => `${l.text}\n${text(l.content)}`), d.additionalPlain].filter(Boolean).join("\n\n") }
    if (src === "ashby") {
      const i = rest.indexOf("-"); const org = rest.slice(0, i), id = rest.slice(i + 1)
      if (!ashbyCache.has(org)) ashbyCache.set(org, await getJSON(ADAPTERS.ashby.url(org)))
      return ashbyCache.get(org).jobs?.find((j) => j.id === id)?.descriptionPlain || null
    }
    if (src === "hn") { const d = await getJSON(`https://hn.algolia.com/api/v1/items/${rest}`); return text(d.text) }
    if (src === "yc") { const h = await getJSON(r.url, true); const t = text(h.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, "")); return t.length > 200 ? t : null }
  } catch { return null }
  return null
}

// ---------- LinkedIn rows: never fetched (robots.txt "User-agent: * / Disallow: /", checked 2026-11-16) ----------
// A LinkedIn alert row carries title, company and location from the email only. Its JD is read from the SAME role on
// the company's own public ATS board (Greenhouse / Ashby / Lever JSON APIs), found through the employer index or a
// slug probe. No match = the row stays UNSCORED with a reason (human-paste path); a LinkedIn page is never requested.
// app.jackandjill.ai and talent.fonzi.ai are signed-in app pages, never a JD: fetching them would score page chrome.
export const NO_FETCH_HOST = /(^|\.)linkedin\.com$|^app\.jackandjill\.ai$|^talent\.fonzi\.ai$/i
export function fetchAllowed(url) { try { return !NO_FETCH_HOST.test(new URL(url).hostname) } catch { return false } }
// Words inside brackets count (WRITER "AI deployment engineer (East)" is not "(Central)", 2026-11-16). City names are
// normalized, not dropped: "(NYC)", "- New York" and "NY" are one token and "SF" / "San Francisco" another, so
// OpenAI "FDE - NYC" never matches "FDE - SF". Work-mode words carry no role meaning and are stop words.
const STOP = new Set(["the", "a", "an", "and", "or", "of", "for", "to", "in", "at", "with", "us", "usa", "remote", "hybrid", "onsite", "on", "site", "sr", "senior"])
const cities = (s) => String(s).replace(/new york city|new york|\bnyc\b|\bny\b/gi, " cityNYC ").replace(/san francisco|\bsf\b|bay area/gi, " citySF ")
const toks = (s) => norm(cities(s)).split(" ").filter((w) => w && !STOP.has(w))
// Same-role score: Jaccard overlap of distinctive title words (order-free), 0 when seniority differs.
// A twin must clear 0.7 AND be the best-scoring posting on the board, so "AI Builder - Research (Global)"
// never stands in for "AI Builder - FDE, Research, & Product (NYC)" when the exact posting exists (2026-11-16).
export function roleScore(a, b) {
  const A = new Set(toks(a)), B = new Set(toks(b))
  if (!A.size || !B.size) return 0
  const sen = (s) => (/\b(staff|principal|lead|head|director|vp|chief|founding)\b/i.exec(s) || [""])[0].toLowerCase()
  if (sen(a) !== sen(b)) return 0
  let hit = 0; for (const w of A) if (B.has(w)) hit++
  const small = Math.min(A.size, B.size)
  if (hit < small || small < Math.min(2, Math.max(A.size, B.size))) return 0
  return hit / (A.size + B.size - hit)
}
export const sameRole = (a, b) => roleScore(a, b) >= 0.7
const slugGuesses = (company) => {
  const base = norm(company).replace(/\b(inc|llc|ltd|corp|co|technologies|technology|labs|ai|hq|group)\b/g, " ").trim()
  const full = norm(company)
  return [...new Set([full.replace(/ /g, ""), base.replace(/ /g, ""), full.replace(/ /g, "-"), base.replace(/ /g, "-")].filter((x) => x.length > 1))]
}
const boardCache = new Map()
async function boardRows(ats, slug) {
  const k = `${ats}:${slug}`
  if (!boardCache.has(k)) {
    let rows = null
    try { const a = ADAPTERS[ats]; rows = a.normalize(await getJSON(a.url(slug)), slug) } catch { rows = null }
    boardCache.set(k, rows)
  }
  return boardCache.get(k)
}
// -> { jobid, url, jd, board } for the ATS twin of a LinkedIn row, else null.
export async function linkedinToAts(r) {
  const idx = employerIndex()
  const hit = Object.entries(idx).find(([k, m]) => m && m.verify === "ok" && (norm(k) === norm(r.company) || norm(m.display) === norm(r.company)))
  const cands = hit ? [[hit[1].ats, hit[1].slug]] : slugGuesses(r.company).flatMap((s) => [["greenhouse", s], ["ashby", s], ["lever", s]])
  for (const [ats, slug] of cands) {
    const rows = await boardRows(ats, slug)
    if (!rows || !rows.length) continue
    // Ties (a city-less title against "FDE - NYC" and "FDE - SF") go to the posting whose location matches the row's.
    const city = (l) => (/new york|nyc|\bny\b/i.test(l || "") ? "nyc" : /san francisco|\bsf\b/i.test(l || "") ? "sf" : "")
    const here = city(r.location)
    const twin = rows.map((x) => [roleScore(r.title, x.title) + (here && city(x.location) === here ? 0.001 : 0), x]).filter(([sc]) => sc >= 0.7).sort((p, q) => q[0] - p[0])[0]?.[1]
    if (!twin) { if (hit) return null; continue }
    const jd = await atsJD(twin)
    if (jd && jd.length > 200) return { jobid: twin.jobid, url: twin.url, jd, board: `${ats}:${slug}` }
  }
  return null
}

// ---------- employer candidate-AI policies (runtime/specs/candidate-ai-policies.json) ----------
// A company whose careers page forbids AI-drafted application material gets no generated resume or cover letter.
let AIPOL = null
export function aiPolicyFor(company) {
  if (!AIPOL) { try { AIPOL = JSON.parse(fs.readFileSync(path.join(HERE, "..", "runtime", "specs", "candidate-ai-policies.json"), "utf8")).policies || [] } catch { AIPOL = [] } }
  return AIPOL.find((p) => new RegExp(p.company_pattern, "i").test(String(company || ""))) || null
}

// Rows handed in by an agent from an MCP-only source. id must be stable per posting (e.g. company id + title slug).
export function importRows(file, src) {
  const list = JSON.parse(fs.readFileSync(file, "utf8"))
  const rows = (Array.isArray(list) ? list : []).filter((r) => r && r.id && r.title && r.company && r.url)
    .map((r) => row(src, { id: r.id, title: r.title, company: r.company, location: r.location, url: r.url, salary: r.salary ?? null }))
  return { rows: rows.filter((r) => r.alertQuery && locationOk(r.location, false, r.title)), raw: rows.length, errors: [] }
}

// ---------- offline fixtures: each adapter must normalize, filter and keep/drop as expected ----------
function selftest() {
  const t = (name, ok) => { if (!ok) { console.error(`FAIL ${name}`); process.exitCode = 1 } else console.log(`ok   ${name}`) }
  t("lane: Senior Product Engineer", laneFor("Senior Product Engineer") === "product engineer")
  t("lane: Product Engineer, AI", laneFor("Product Engineer, AI") === "product engineer")
  t("lane: Founding Product Engineer", laneFor("Founding Product Engineer") === "product engineer")
  t("lane: AI Product Engineer", laneFor("AI Product Engineer") === "product engineer")
  t("lane: Forward Deployed Engineer", laneFor("Forward Deployed Engineer") === "forward deployed")
  t("lane: Founding Forward Deployment Engineer", laneFor("Founding Forward Deployment Engineer") === "forward deployed")
  t("lane: Staff Product Manager, AI", laneFor("Staff Product Manager, AI") === "product manager")
  t("drop: Product Engineering Intern", laneFor("Product Engineering Intern") === null)
  t("drop: Product Marketing Manager", laneFor("Product Marketing Manager") === null)
  t("drop: Engineering Manager, Product", laneFor("Engineering Manager, Product") === null)
  t("drop: Associate Product Manager", laneFor("Associate Product Manager") === null)
  t("drop: Backend Engineer", laneFor("Backend Engineer") === null)
  t("loc: New York, NY", locationOk("New York, NY"))
  t("loc: Remote (US)", locationOk("Remote (US)"))
  t("loc: San Francisco + isRemote", locationOk("San Francisco, CA", true))
  t("loc drop: Remote - EMEA", !locationOk("Remote - EMEA"))
  t("loc drop: London", !locationOk("London, UK"))
  t("loc drop: San Francisco on-site", !locationOk("San Francisco, CA"))
  t("loc drop: Oakland, California, United States", !locationOk("Oakland, California, United States"))
  t("loc keep: United States", locationOk("United States"))
  t("loc drop: Berlin / Remote", !locationOk("Berlin, BE, DE / Remote"))
  t("loc keep: Remote - US; London", locationOk("Remote - US; London"))
  t("drop: Design Engineer", laneFor("Design Engineer") === null)
  t("loc keep: SF; New York", locationOk("San Francisco; New York"))
  t("loc drop: Abu Dhabi, UAE even if remote", !locationOk("Abu Dhabi, UAE", true))
  t("loc drop: region in title", !locationOk("New York City", false, "Forward Deployed, Asset Management (EMEA)"))
  t("drop: Manager, Applied AI Engineering", laneFor("Manager, Applied AI Engineering") === null)
  t("drop: GTM Strategy & Operations, FDE", laneFor("GTM Strategy & Operations, FDE") === null)
  const gh = ADAPTERS.greenhouse.normalize({ meta: { name: "Acme" }, jobs: [{ id: 42, title: "Product Engineer", location: { name: "New York, NY" }, absolute_url: "https://x/42", updated_at: "2026-11-01T00:00:00Z" }] }, "acme")
  t("greenhouse normalize", gh[0].jobid === "greenhouse-acme-42" && gh[0].company === "Acme" && gh[0].alertQuery === "product engineer" && gh[0].source === "greenhouse_board")
  const lv = ADAPTERS.lever.normalize([{ id: "u-1", text: "Forward Deployed Engineer", categories: { location: "Remote" }, workplaceType: "remote", hostedUrl: "https://l/1", createdAt: 1793000000000 }], "acme")
  t("lever normalize", lv[0].jobid === "lever-acme-u-1" && lv[0]._remote && lv[0].alertQuery === "forward deployed")
  const ab = ADAPTERS.ashby.normalize({ organizationName: "Acme AI", jobs: [{ id: "a-1", title: "AI Product Engineer", location: "San Francisco", isRemote: true, jobUrl: "https://a/1", descriptionPlain: "Build it", publishedAt: "2026-11-01" }, { id: "a-2", title: "Product Engineer", isListed: false }] }, "acme")
  t("ashby normalize + unlisted dropped", ab.length === 1 && ab[0].jd === "Build it" && ab[0].company === "Acme AI")
  const yc = ADAPTERS.yc.normalize(ADAPTERS.yc.parse(`<div data-page="{&quot;props&quot;:{&quot;jobPostings&quot;:[{&quot;id&quot;:7,&quot;title&quot;:&quot;Founding Product Engineer&quot;,&quot;url&quot;:&quot;/companies/acme/jobs/7&quot;,&quot;location&quot;:&quot;New York, NY, US&quot;,&quot;companyName&quot;:&quot;Acme&quot;,&quot;companyBatchName&quot;:&quot;W25&quot;,&quot;salaryRange&quot;:&quot;$150K - $200K&quot;}]}}"></div>`))
  t("yc parse + normalize", yc[0].jobid === "yc-7" && yc[0].company === "Acme (YC W25)" && yc[0].salary === "$150K - $200K")
  const hn = ADAPTERS.hn.normalize({ children: [
    { id: 9, author: "a", created_at: "2026-11-02T17:00:00Z", text: "Acme | Senior Product Engineer, Backend Engineer | New York, NY | ONSITE<p>We build agents." },
    { id: 10, author: "b", text: "Beta | Data Engineer | Remote" },
    { id: 11, author: "c", text: "no pipes here, just chat" },
    { id: 12, author: "d", text: "Gamma | Malibu, CA | ONSITE | Founding Product Engineer" },
  ] })
  const idx = { A: { ats: "ashby", slug: "acme", verify: "ok" }, B: { ats: "ashby", slug: "bad", verify: "REVIEW" }, C: { ats: "greenhouse", slug: "gh", verify: "ok" } }
  t("employer index: verified boards for one ats only", JSON.stringify(indexSlugs(idx, "ashby")) === '["acme"]' && indexSlugs(null, "lever").length === 0)
  const hnKept = hn.filter((r) => locationOk(r.location, false, r.title))
  t("hn drops a header with an off-target city", hn.length === 2 && hnKept.length === 1)
  t("linkedin host never fetched", !fetchAllowed("https://www.linkedin.com/jobs/view/1/") && fetchAllowed("https://jobs.ashbyhq.com/x/1"))
  t("candidate AI policy: Anthropic blocks generated drafts", aiPolicyFor("Anthropic")?.rule === "candidate-drafts-first" && aiPolicyFor("anthropic") && !aiPolicyFor("Ramp"))
  t("platform app pages never fetched", !fetchAllowed("https://app.jackandjill.ai/jobs/x/post") && !fetchAllowed("https://talent.fonzi.ai/companies/x"))
  t("sameRole: word order and brackets", sameRole("Forward Deployed Engineer (NYC)", "Forward Deployed Engineer - New York"))
  t("sameRole: seniority kept apart", !sameRole("Staff Product Manager", "Product Manager") && !sameRole("Senior Product Manager", "Product Designer"))
  t("sameRole: extra qualifier on one side ok", sameRole("Applied AI Engineer", "Applied AI Engineer, Agents"))
  t("cities normalize, never drop", !sameRole("Forward Deployed Engineer (FDE) - NYC", "Forward Deployed Engineer (FDE) - SF") && sameRole("Forward Deployed Engineer (NYC)", "Forward Deployed Engineer - New York"))
  t("bracketed region qualifiers stay distinct", !sameRole("AI deployment engineer (East)", "AI deployment engineer (Central)") && sameRole("AI deployment engineer (East)", "AI deployment engineer (East)"))
  t("twin picks the closest title, not the first subset", roleScore("AI Builder - FDE, Research, & Product (NYC)", "AI Builder - FDE, Research, & Product (NYC)") > roleScore("AI Builder - FDE, Research, & Product (NYC)", "AI Builder - Research (Global)"))
  t("a thin subset is not a twin", !sameRole("AI Builder - FDE, Research, & Product (NYC)", "AI Builder - Research (Global)"))
  t("hn normalize keeps only lane matches", hnKept[0].title === "Senior Product Engineer" && hnKept[0].location === "New York, NY" && hnKept[0].jd.includes("agents"))
}

// ---------- CLI ----------
function loadToken() {
  if (process.env.JOBS_PIPELINE_TOKEN) return process.env.JOBS_PIPELINE_TOKEN
  try {
    const env = fs.readFileSync(path.join(os.homedir(), ".arcs", "jobs-pipeline.env"), "utf8")
    return env.match(/^\s*(?:export\s+)?JOBS_PIPELINE_TOKEN=["']?([^"'\n]+)/m)?.[1] ?? null
  } catch { return null }
}

async function main() {
  const has = (k) => process.argv.includes(k)
  const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? d) : d }
  if (has("--selftest")) return selftest()
  const names = arg("--source", null) ? [arg("--source")] : Object.keys(ADAPTERS)
  if (names.some((n) => !ADAPTERS[n] && !(has("--import") && SOURCE_KEY[n]))) { console.error(`unknown --source; one of ${Object.keys(SOURCE_KEY).join(", ")} (fonzi needs --import)`); process.exit(2) }

  if (has("--probe")) {
    const one = { greenhouse: ["anthropic"], lever: ["palantir"], ashby: ["openai"], yc: [SPEC.yc.pages[0]], hn: undefined }
    for (const n of names) {
      const r = await pull(n, { slugs: one[n] })
      console.log(`${n.padEnd(10)} raw ${String(r.raw).padStart(4)} · kept ${String(r.rows.length).padStart(3)}${r.errors.length ? ` · ERR ${r.errors.join("; ")}` : ""}`)
      if (r.raw === 0 && !r.errors.length) process.exitCode = 1
    }
    return
  }

  const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
  const TOKEN = loadToken()
  if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required (env or ~/.arcs/jobs-pipeline.env)"); process.exit(2) }
  const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
  const DRY = has("--dry-run")

  const board = (await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()).rows || []
  const haveId = new Set(board.map((r) => String(r.jobid)))
  const haveKey = new Set(board.map((r) => dupKey(r.company, r.title)))
  const { sources = [] } = await (await fetch(`${BASE}/api/jobs/lane`, { headers: H })).json()
  const known = new Set(sources.map((s) => s.key))

  const imported = arg("--import", null)
  for (const n of names) {
    const { rows, raw, errors } = imported ? importRows(imported, n) : await pull(n)
    const seen = new Set(); const fresh = []
    let dupBoard = 0
    for (const r of rows) {
      const k = dupKey(r.company.replace(/ \(YC .*\)$/, ""), r.title)
      if (haveId.has(r.jobid) || haveKey.has(k)) { dupBoard++; continue }
      if (seen.has(k)) continue
      seen.add(k); fresh.push(r)
    }
    console.log(`\n== ${n}: ${raw} postings · ${rows.length} fit title+location · ${dupBoard} already on board · ${fresh.length} new${errors.length ? ` · ${errors.length} errors` : ""}`)
    for (const e of errors) console.log(`   ERR ${e}`)
    for (const r of fresh) console.log(`   [${r.alertQuery}] ${r.title} · ${r.company} · ${r.location ?? "?"}${r.salary ? ` · ${r.salary}` : ""}\n      ${r.url}`)
    if (DRY || !fresh.length) continue

    const payload = fresh.map((r) => { const p = { ...r, band: "UNSCORED", unscoredWhy: `ingested from ${r.source}; scorer not yet run` }; delete p.jd; delete p._remote; return p })
    const w = await fetch(`${BASE}/api/jobs`, { method: "POST", headers: H, body: JSON.stringify(payload) })
    console.log(`   posted: ${w.status} ${JSON.stringify(await w.json())}`)
    payload.forEach((r) => { haveId.add(r.jobid); haveKey.add(dupKey(r.company, r.title)) })
    // Record the run on the lane when the source exists there (yc_jobs / hn_whoishiring need a Source row first).
    const key = SOURCE_KEY[n]
    if (known.has(key)) {
      const q = await (await fetch(`${BASE}/api/jobs/lane`, { method: "POST", headers: H, body: JSON.stringify({ sourceKey: key, toDate: new Date().toISOString().slice(0, 10) }) })).json()
      if (q.request?.id) await fetch(`${BASE}/api/jobs/lane`, { method: "PATCH", headers: H, body: JSON.stringify({ requestId: q.request.id, status: errors.length && !fresh.length ? "failed" : "done", rowsAdded: fresh.length, watermark: new Date().toISOString(), error: errors.join("; ") || undefined }) })
    } else console.log(`   note: no Source row "${key}" on the lane yet; rows posted, run not recorded`)
  }
  if (!DRY) console.log("\nnext: node scripts/jobs_score_sweep.mjs   # scores the new UNSCORED rows")
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch((e) => { console.error(e); process.exit(1) })
