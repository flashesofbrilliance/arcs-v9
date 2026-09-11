#!/usr/bin/env node
// jobs_rescore_split.mjs — driver for the v1.1 -> v1.2 rubric split migration.
// Pulls every scored row off the board and posts it in batches to
// POST /api/jobs/rescore-dims, which decomposes the retired `strength_leverage`
// dim into `rare_combination` + `domain_breadth` and recomputes composite against
// the live v1.2 spec (the v1.1 Score row is preserved by version, so reversible).
// No JD fetch — decomposition runs from title/company/assessment/old-score.
//
//   node scripts/jobs_rescore_split.mjs --dry-run        # list what would re-score
//   node scripts/jobs_rescore_split.mjs --limit 10       # proof batch
//   node scripts/jobs_rescore_split.mjs                  # migrate the whole board
// Env: JOBS_PIPELINE_TOKEN, JOBS_BASE (default https://jobs.arcs.care).

const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const has = (k) => process.argv.includes(k)
const DRY = has("--dry-run")
const LIMIT = Number(arg("--limit", 0)) || 0
const BATCH = Number(arg("--batch", 10))
const BASE = process.env.JOBS_BASE || "https://jobs.arcs.care"
const TOKEN = process.env.JOBS_PIPELINE_TOKEN
if (!TOKEN) { console.error("JOBS_PIPELINE_TOKEN required"); process.exit(2) }
const H = { "x-jobs-token": TOKEN, "content-type": "application/json" }
const parse = (s, fb) => { try { return s ? JSON.parse(s) : fb } catch { return fb } }

async function main() {
  const { rows, spec } = await (await fetch(`${BASE}/api/jobs`, { headers: H })).json()
  if (!spec?.rubric?.dims?.some((d) => d.key === "rare_combination")) {
    console.error(`live spec is v${spec?.version} — not v1.2 yet. Deploy the split first.`); process.exit(1)
  }
  let scored = rows.filter((r) => r.dims && r.composite != null && r.band !== "UNSCORED")
  // skip rows already migrated (dims already carry the new keys, not the old one)
  const pending = scored.filter((r) => { const d = parse(r.dims, {}); return d.strength_leverage != null || d.rare_combination == null })
  if (LIMIT) pending.splice(LIMIT)
  console.log(`scored rows: ${scored.length} · pending migration: ${pending.length}${DRY ? " (DRY)" : ""}`)
  if (DRY) { pending.slice(0, 12).forEach((r) => console.log(`  ${r.composite} ${r.company} — ${r.title}`)); return }
  if (!pending.length) { console.log("nothing to migrate."); return }

  let done = 0, inTok = 0, outTok = 0, cacheRead = 0
  const moves = []
  for (let i = 0; i < pending.length; i += BATCH) {
    const batch = pending.slice(i, i + BATCH).map((r) => ({ jobid: r.jobid, title: r.title, company: r.company, assessment: r.assessment ?? null, dims: parse(r.dims, {}), gates: parse(r.gates, []), compBand: r.compBand ?? null }))
    const before = Object.fromEntries(pending.slice(i, i + BATCH).map((r) => [r.jobid, { c: r.composite, co: r.company, t: r.title }]))
    const resp = await fetch(`${BASE}/api/jobs/rescore-dims`, { method: "POST", headers: H, body: JSON.stringify({ rows: batch }) })
    if (!resp.ok) { console.error(`batch ${i}: ${resp.status} ${await resp.text()}`); continue }
    const d = await resp.json()
    done += d.scored; inTok += d.usage?.input || 0; outTok += d.usage?.output || 0; cacheRead += d.usage?.cache_read || 0
    for (const r of d.results) { const b = before[r.jobid]; if (b) moves.push({ ...r, before: b.c, co: b.co, t: b.t, delta: +(r.composite - b.c).toFixed(3) }) }
    console.log(`re-scored ${Math.min(i + BATCH, pending.length)}/${pending.length}`)
    await new Promise((z) => setTimeout(z, 300))
  }
  moves.sort((a, b) => b.delta - a.delta)
  console.log(`\nDONE. migrated ${done}. biggest gainers (rare_combination · domain_breadth):`)
  moves.slice(0, 8).forEach((m) => console.log(`  ${m.before} -> ${m.composite}  (${m.delta >= 0 ? "+" : ""}${m.delta})  rc${m.rare_combination}·db${m.domain_breadth}  ${m.co} — ${m.t}`))
  console.log("biggest fallers:")
  moves.slice(-5).reverse().forEach((m) => console.log(`  ${m.before} -> ${m.composite}  (${m.delta})  rc${m.rare_combination}·db${m.domain_breadth}  ${m.co} — ${m.t}`))
  console.log(`tokens in=${inTok} out=${outTok} cache_read=${cacheRead}`)
}
main().catch((e) => { console.error(e); process.exit(1) })
