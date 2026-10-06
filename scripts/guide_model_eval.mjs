#!/usr/bin/env node
// guide_model_eval: replay /api/guide inputs through the current `guide` model and a
// candidate, same GUIDE_SYSTEM prompt, and score both against the route's own rules.
// Evidence for a role switch in src/lib/claude-models.ts; it never switches anything.
//
//   node scripts/guide_model_eval.mjs --inputs <file.jsonl> --out <dir> --candidate-model <id> [--limit N]
//   node scripts/guide_model_eval.mjs --self-test
//
// The candidate id is passed on the command line, never written here, so claude-models.ts
// stays the only file that names a model. Inputs: one JSON object per line, a Receipt row
// {id, decision, trueNorth, entity, mode, nciScore, yState, fated, protecting, prep?} plus
// guideMode RECON|ACTIVE|LEAD. Keep inputs and outputs OUT of the repo (user decisions).
//
// Baseline = prod today (max_tokens 3000, no temperature). Candidate = 5.x shape: adaptive
// thinking counts toward max_tokens (8192), depth via output_config.effort.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { readModels, call } from "./deep_model_eval.mjs"

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..")

export function readGuideSystem(text) {
  const m = text.match(/const GUIDE_SYSTEM = `([\s\S]*?)`\n/)
  if (!m) throw new Error("no GUIDE_SYSTEM template in guide route")
  return m[1]
}

// Mirrors buildContext() in src/app/api/guide/[receiptId]/route.ts.
export function context(r) {
  const parts = [`Decision: ${r.decision}`, `True North: ${r.trueNorth}`, `Entity: ${r.entity ?? "Unknown"}`, `Mode: ${r.mode}`, `NCI Score: ${r.nciScore}`, `Y State: ${r.yState}`]
  if (r.fated) {
    try {
      const f = JSON.parse(r.fated)
      parts.push(`FATED - Facts: ${f.facts ?? ""} | Assumptions: ${f.assumptions ?? ""} | Tradeoffs: ${f.tradeoffs ?? ""} | Direction: ${f.direction ?? ""}`)
    } catch { /* ignore */ }
  }
  try {
    const p = JSON.parse(r.protecting ?? "[]")
    if (p.length) parts.push(`Protecting: ${p.join(", ")}`)
  } catch { /* ignore */ }
  if (r.prep) {
    const p = r.prep
    if (p.stakes) parts.push(`Stakes: ${p.stakes}`)
    if (p.horizon) parts.push(`Horizon: ${p.horizon}`)
    if (p.confidence) parts.push(`Confidence (1-5): ${p.confidence}`)
    if (p.adversarialInput) parts.push(`Adversarial input: ${p.adversarialInput}`)
  }
  return `Generate a ${r.guideMode} field guide for this decision context:\n\n${parts.join("\n")}`
}

const STAGE_FIELDS = ["id", "title", "shortLabel", "spineLabel", "questionCompass", "stageJTBD", "testingAboutThem", "agenda", "preWork", "kycLens", "midcurveTripwire", "writesIntoNextTable", "artifacts"]
const words = (s) => String(s).trim().split(/\s+/).filter(Boolean).length
const strings = (v) => (typeof v === "string" ? [v] : Array.isArray(v) ? v.flatMap(strings) : v && typeof v === "object" ? Object.values(v).flatMap(strings) : [])

// Mechanical rule checks, straight from GUIDE_SYSTEM. Content quality is a human read.
export function score(raw, stop, mode) {
  const s = { stop, json: false, stageCount: false, fields: false, counts: false, wordCap: false, tripwire: false, kycPrefix: false, outcomeTarget: false, emDashes: 0, stages: 0 }
  if (stop === "refusal" || stop === "max_tokens") return s
  let j
  try { j = JSON.parse(raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()) } catch { return s }
  s.json = true
  const st = Array.isArray(j.stages) ? j.stages : []
  s.stages = st.length
  s.stageCount = mode === "RECON" ? st.length === 1 : mode === "ACTIVE" ? st.length === 2 : st.length >= 3 && st.length <= 5
  s.fields = st.length > 0 && st.every((x) => STAGE_FIELDS.every((k) => x?.[k] !== undefined && x[k] !== ""))
  const len = (x, k) => (Array.isArray(x?.[k]) ? x[k].length : -1)
  s.counts = st.length > 0 && st.every((x) =>
    mode === "RECON" ? len(x, "agenda") === 2 && len(x, "preWork") === 2 && len(x, "artifacts") === 1
      : mode === "ACTIVE" ? len(x, "agenda") === 3 && len(x, "artifacts") === 2
        : true)
  s.wordCap = st.every((x) => [...(x?.agenda ?? []), ...(x?.preWork ?? [])].every((i) => words(i) <= 75))
  s.tripwire = st.length > 0 && st.every((x) => typeof x?.midcurveTripwire === "string" && /^If I\b/.test(x.midcurveTripwire.trim()))
  s.kycPrefix = st.length > 0 && st.every((x) => Array.isArray(x?.kycLens) && x.kycLens.length > 0 && x.kycLens.every((k) => /^KY[CTBI]:/.test(String(k).trim())))
  const ot = j.outcome_target ?? {}
  s.outcomeTarget = ["outcome_statement", "leading_indicator", "kpi_label", "failure_signal"].every((k) => typeof ot[k] === "string" && ot[k]) && words(ot.kpi_label) <= 8
  s.emDashes = strings(j).join(" ").match(/—/g)?.length ?? 0
  s.parsed = j
  return s
}

function summarize(rows, arm) {
  const ok = rows.map((r) => r[arm]).filter((x) => x.ok)
  const n = rows.length
  const pct = (f) => `${ok.filter((x) => f(x.score)).length}/${n}`
  const med = (a) => { const b = [...a].sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : null }
  return {
    calls_ok: `${ok.length}/${n}`,
    json: pct((s) => s.json),
    stage_count_matches_mode: pct((s) => s.stageCount),
    all_stage_fields: pct((s) => s.fields),
    item_counts_match_mode: pct((s) => s.counts),
    items_under_75_words: pct((s) => s.json && s.wordCap),
    tripwire_starts_if_i: pct((s) => s.tripwire),
    kyc_prefixed: pct((s) => s.kycPrefix),
    outcome_target_ok: pct((s) => s.outcomeTarget),
    zero_em_dashes: pct((s) => s.json && s.emDashes === 0),
    refusals: ok.filter((x) => x.stop === "refusal").length,
    truncated: ok.filter((x) => x.stop === "max_tokens").length,
    median_ms: med(ok.map((x) => x.ms)),
    max_ms: ok.length ? Math.max(...ok.map((x) => x.ms)) : null,
    tokens_in: ok.reduce((a, x) => a + (x.usage?.input_tokens ?? 0), 0),
    tokens_out: ok.reduce((a, x) => a + (x.usage?.output_tokens ?? 0), 0),
    errors: rows.map((r) => r[arm]).filter((x) => !x.ok).map((x) => x.error),
  }
}

function selfTest() {
  const stage = (n) => Array.from({ length: n }, (_, i) => ({ id: `T${i}`, title: "t", shortLabel: "s", spineLabel: "x", questionCompass: "Is it?", stageJTBD: "j", testingAboutThem: "t",
    agenda: ["a", "b"], preWork: ["p", "q"], kycLens: ["KYC: x"], midcurveTripwire: "If I drift.", writesIntoNextTable: { yes: "y", no: "n" }, artifacts: [{ title: "d", abstract: "a" }] }))
  const g = (n) => JSON.stringify({ guide_title: "g", bet_label: "b", total_prep_hours: "1", outcome_target: { outcome_statement: "o", leading_indicator: "l", kpi_label: "short label", failure_signal: "Asks" }, stages: stage(n) })
  const a = score(g(1), "end_turn", "RECON"), b = score(g(2), "end_turn", "RECON"), c = score(g(1).replace('"t"', '"t — x"'), "end_turn", "RECON")
  const d = score(g(3), "end_turn", "LEAD"), e = score(g(1), "max_tokens", "RECON")
  const sys = readGuideSystem("const GUIDE_SYSTEM = `hello`\n")
  const ctx = context({ decision: "d", trueNorth: "t", entity: "E", mode: "COURT", nciScore: 50, yState: "FORK", fated: null, protecting: '["Cash"]', guideMode: "ACTIVE" })
  const ok = a.json && a.stageCount && a.fields && a.counts && a.tripwire && a.kycPrefix && a.outcomeTarget && a.emDashes === 0 &&
    !b.stageCount && c.emDashes === 1 && d.stageCount && !e.json && sys === "hello" && ctx.startsWith("Generate a ACTIVE field guide") && ctx.includes("Protecting: Cash")
  console.log(`guide_model_eval self-test: ${ok ? "PASS" : "FAIL"}`)
  return ok ? 0 : 1
}

async function main(argv) {
  if (argv.includes("--self-test")) return selfTest()
  const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d }
  const inputs = arg("--inputs"), outDir = arg("--out"), cand = arg("--candidate-model"), limit = Number(arg("--limit", "50"))
  if (!inputs || !outDir || !cand) { console.error("usage: guide_model_eval.mjs --inputs <jsonl> --out <dir> --candidate-model <id> [--limit N] | --self-test"); return 2 }
  const key = process.env.ANTHROPIC_API_KEY
  if (!key) { console.error("ANTHROPIC_API_KEY not set"); return 2 }
  const models = readModels(fs.readFileSync(path.join(ROOT, "src/lib/claude-models.ts"), "utf8"))
  const system = readGuideSystem(fs.readFileSync(path.join(ROOT, "src/app/api/guide/[receiptId]/route.ts"), "utf8"))
  const items = fs.readFileSync(inputs, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).slice(0, limit)
  fs.mkdirSync(outDir, { recursive: true })
  console.log(`guide eval: ${items.length} inputs · baseline=${models.guide} · candidate=${cand}`)
  const rows = []
  for (const [i, x] of items.entries()) {
    const msg = [{ role: "user", content: context(x) }]
    const [b, c] = await Promise.all([
      call(key, { model: models.guide, max_tokens: 3000, system, messages: msg }),
      call(key, { model: cand, max_tokens: 8192, output_config: { effort: "medium" }, system, messages: msg }),
    ])
    for (const r of [b, c]) if (r.ok) r.score = score(r.raw, r.stop, x.guideMode)
    rows.push({ id: x.id, guideMode: x.guideMode, decision: x.decision, baseline: b, candidate: c })
    const tag = (r) => (r.ok ? `${r.score.json ? `json ${r.score.stages}st` : r.stop} ${r.ms}ms` : `ERR ${r.error}`)
    console.log(`  ${i + 1}/${items.length} ${x.guideMode.padEnd(6)} baseline ${tag(b)} · candidate ${tag(c)}`)
    if (!b.ok && !c.ok && /usage limit|credit|authentication/i.test(`${b.error} ${c.error}`)) { console.error("stopping: account-level error"); break }
  }
  const summary = { at: new Date().toISOString(), baseline_model: models.guide, candidate_model: cand, n: rows.length, baseline: summarize(rows, "baseline"), candidate: summarize(rows, "candidate") }
  fs.writeFileSync(path.join(outDir, "rows.json"), JSON.stringify(rows, null, 2))
  fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 2))
  console.log(JSON.stringify(summary, null, 2))
  return 0
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) process.exitCode = await main(process.argv.slice(2))
