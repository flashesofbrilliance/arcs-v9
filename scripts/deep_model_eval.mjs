#!/usr/bin/env node
// deep_model_eval: replay compass COURT inputs through the current `deep` model and a
// candidate, same SYSTEM prompt, and score both. Evidence for a role switch in
// src/lib/claude-models.ts; it never switches anything.
//
//   node scripts/deep_model_eval.mjs --inputs <file.jsonl> --out <dir> [--limit N] [--candidate-role writer]
//   node scripts/deep_model_eval.mjs --self-test
//
// Inputs: one JSON object per line {id, question, horizon, stakes, prep?:{stakes,horizon,
// protecting[],confidence,entity,adversarialInput,outcomeHorizon}}. Keep inputs and outputs
// OUT of the repo (they are user decisions); write them to a scratch dir.
//
// Baseline call = prod COURT today (temperature 0.5, max_tokens 4096). Candidate call is the
// Sonnet 5.5 shape from writerCall: no temperature (non-default is a 400), adaptive thinking
// counted against max_tokens (so 8192), depth via output_config.effort.
// Model ids come from claude-models.ts (the one registry), never from this file.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..")

export function readModels(text) {
  const block = text.match(/export const MODELS = \{([\s\S]*?)\} as const/)
  if (!block) throw new Error("no MODELS block in claude-models.ts")
  return Object.fromEntries([...block[1].matchAll(/^\s*(\w+):\s*"(claude-[\w.-]+)"/gm)].map((m) => [m[1], m[2]]))
}

export function readSystem(text, today) {
  const m = text.match(/const SYSTEM = `([\s\S]*?)`\n/)
  if (!m) throw new Error("no SYSTEM template in compass/route.ts")
  return m[1].replace(/\$\{new Date\(\)\.toISOString\(\)\.slice\(0, 10\)\}/g, today)
}

// Mirrors the route's userMsg for mode COURT (no SAGE block: the eval isolates the model).
export function userMsg(x) {
  const p = x.prep
  const prep = p
    ? `\nCALIBRATION CONTEXT (from prep session):
STAKES: ${p.stakes ?? x.stakes}
HORIZON: ${p.horizon ?? x.horizon}
PROTECTING: ${p.protecting?.length ? p.protecting.join(", ") : "not specified"}
CONFIDENCE ENTERING: ${p.confidence ?? "not specified"}/5
ENTITY: ${p.entity ?? "not named"}
ADVERSARIAL VECTOR (user's strongest counter): ${(p.adversarialInput ?? "not provided").slice(0, 2000)}
OUTCOME_HORIZON: ${p.outcomeHorizon ?? "not specified"}`
    : ""
  return `DECISION: ${x.question.slice(0, 4000)}
HORIZON: ${x.horizon}
STAKES: ${x.stakes}
MODE: COURT
DOOR: ${x.door ?? "ONE_WAY"}
CLARITY: SIMPLE${prep}

Run the L0–L5 pipeline. Return only the JSON object.`
}

// Mechanical checks only; quality judgment is the blind A/B file, read by a human.
export function score(raw, stop) {
  const s = { stop, json: false, tributaries3: false, tributaryTypes: false, lensSumOk: false, emDashes: 0, selfGradeAllTrue: false, nci: null }
  if (stop === "refusal" || stop === "max_tokens") return s
  let j
  try { j = JSON.parse(raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()) } catch { return s }
  s.json = true
  const t = Array.isArray(j.tributaries) ? j.tributaries : []
  s.tributaries3 = t.length === 3
  s.tributaryTypes = t.map((x) => x?.type).join(",") === "meta,challenge,adjacent"
  s.nci = typeof j.nci_score === "number" ? j.nci_score : null
  const l = j.nci_by_lens ?? {}
  const sum = ["clarity", "conviction", "coherence", "consequence", "cadence"].reduce((a, k) => a + (Number(l[k]) || 0), 0)
  s.lensSumOk = s.nci !== null && Math.abs(sum - s.nci) <= 10
  const prose = [j.true_north, ...(Array.isArray(j.why) ? j.why : []), ...t.map((x) => x?.prompt)].filter((v) => typeof v === "string").join(" ")
  s.emDashes = (prose.match(/—/g) ?? []).length
  const g = j.nci_self_grade ?? {}
  s.selfGradeAllTrue = ["factual", "sources", "honesty", "action"].every((k) => g[k] === true)
  s.parsed = j
  return s
}

async function call(key, body) {
  const t0 = Date.now()
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify(body),
  })
  const j = await r.json()
  const ms = Date.now() - t0
  if (!r.ok) return { ok: false, ms, error: `${r.status} ${j?.error?.type}: ${j?.error?.message}` }
  const raw = (j.content ?? []).filter((c) => c.type === "text").map((c) => c.text).join("")
  return { ok: true, ms, raw, stop: j.stop_reason, usage: j.usage }
}

function arms(models, candRole, system) {
  const sys = [{ type: "text", text: system, cache_control: { type: "ephemeral" } }]
  return {
    baseline: (msg) => ({ model: models.deep, max_tokens: 4096, temperature: 0.5, system: sys, messages: [{ role: "user", content: msg }] }),
    candidate: (msg) => ({ model: models[candRole], max_tokens: 8192, output_config: { effort: "medium" }, system: sys, messages: [{ role: "user", content: msg }] }),
  }
}

function summarize(rows, arm) {
  const ok = rows.map((r) => r[arm]).filter((x) => x.ok)
  const n = rows.length
  const pct = (f) => `${ok.filter((x) => f(x.score)).length}/${n}`
  const med = (a) => { const b = [...a].sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : null }
  return {
    calls_ok: `${ok.length}/${n}`,
    json: pct((s) => s.json),
    tributaries3_typed: pct((s) => s.tributaries3 && s.tributaryTypes),
    lens_sum_within_10: pct((s) => s.lensSumOk),
    zero_em_dashes: pct((s) => s.json && s.emDashes === 0),
    refusals: ok.filter((x) => x.stop === "refusal").length,
    truncated: ok.filter((x) => x.stop === "max_tokens").length,
    median_ms: med(ok.map((x) => x.ms)),
    median_nci: med(ok.map((x) => x.score.nci).filter((v) => v !== null)),
    tokens_in: ok.reduce((a, x) => a + (x.usage?.input_tokens ?? 0) + (x.usage?.cache_read_input_tokens ?? 0) + (x.usage?.cache_creation_input_tokens ?? 0), 0),
    tokens_out: ok.reduce((a, x) => a + (x.usage?.output_tokens ?? 0), 0),
    errors: rows.map((r) => r[arm]).filter((x) => !x.ok).map((x) => x.error),
  }
}

function blindFile(rows) {
  const key = []
  const out = ["# Blind A/B: compass COURT, deep role", "", "For each item pick A, B, or tie on: is the bearing right, are the reasons specific, are the tributaries useful. Key is in key.json; read it after.", ""]
  rows.forEach((r, i) => {
    const flip = Math.random() < 0.5
    const [A, B] = flip ? [r.candidate, r.baseline] : [r.baseline, r.candidate]
    key.push({ item: i + 1, id: r.id, A: flip ? "candidate" : "baseline", B: flip ? "baseline" : "candidate" })
    const show = (x) => {
      const j = x.ok ? x.score.parsed : null
      if (!j) return `_(no usable output: ${x.ok ? x.stop : x.error})_`
      return [`**True north:** ${j.true_north}`, ...(j.why ?? []).map((w) => `- ${w}`), "", "Tributaries:", ...(j.tributaries ?? []).map((t) => `- (${t.type}) ${t.prompt}`), "", `Score shown to user: ${j.nci_score}`].join("\n")
    }
    out.push(`## ${i + 1}. ${r.question.slice(0, 160).replace(/\n/g, " ")}`, "", "### A", show(A), "", "### B", show(B), "", "Pick: ___", "")
  })
  return { md: out.join("\n"), key }
}

function selfTest() {
  const good = JSON.stringify({ true_north: "Do it.", why: ["a"], nci_score: 50, nci_by_lens: { clarity: 10, conviction: 10, coherence: 10, consequence: 10, cadence: 10 },
    nci_self_grade: { factual: true, sources: true, honesty: true, action: true }, tributaries: [{ type: "meta", prompt: "q" }, { type: "challenge", prompt: "q" }, { type: "adjacent", prompt: "q" }] })
  const a = score(good, "end_turn")
  const b = score("```json\n" + good.replace("Do it.", "Do it — now.") + "\n```", "end_turn")
  const c = score("{bad", "end_turn"), d = score(good, "refusal")
  const m = readModels('export const MODELS = {\n  deep: "claude-x-1", // c\n  writer: "claude-y-2",\n} as const')
  const sys = readSystem("const SYSTEM = `hi ${new Date().toISOString().slice(0, 10)}`\n", "2026-01-01")
  const ok = a.json && a.tributaries3 && a.tributaryTypes && a.lensSumOk && a.emDashes === 0 && a.selfGradeAllTrue &&
    b.json && b.emDashes === 1 && !c.json && !d.json && m.deep === "claude-x-1" && m.writer === "claude-y-2" && sys === "hi 2026-01-01" &&
    userMsg({ question: "q", horizon: "this-week", stakes: "high" }).includes("MODE: COURT")
  console.log(`deep_model_eval self-test: ${ok ? "PASS" : "FAIL"}`)
  return ok ? 0 : 1
}

async function main(argv) {
  if (argv.includes("--self-test")) return selfTest()
  const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d }
  const inputs = arg("--inputs"), outDir = arg("--out"), limit = Number(arg("--limit", "20")), candRole = arg("--candidate-role", "writer")
  if (!inputs || !outDir) { console.error("usage: deep_model_eval.mjs --inputs <jsonl> --out <dir> [--limit N] [--candidate-role writer] | --self-test"); return 2 }
  const key = process.env.ANTHROPIC_API_KEY
  if (!key) { console.error("ANTHROPIC_API_KEY not set"); return 2 }
  const models = readModels(fs.readFileSync(path.join(ROOT, "src/lib/claude-models.ts"), "utf8"))
  if (!models.deep || !models[candRole]) { console.error(`missing role deep or ${candRole} in claude-models.ts`); return 2 }
  const system = readSystem(fs.readFileSync(path.join(ROOT, "src/app/api/compass/route.ts"), "utf8"), new Date().toISOString().slice(0, 10))
  const A = arms(models, candRole, system)
  const items = fs.readFileSync(inputs, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).slice(0, limit)
  fs.mkdirSync(outDir, { recursive: true })
  console.log(`eval: ${items.length} COURT inputs · baseline=${models.deep} · candidate=${models[candRole]} (role ${candRole})`)
  const rows = []
  for (const [i, x] of items.entries()) {
    const msg = userMsg(x)
    const [b, c] = await Promise.all([call(key, A.baseline(msg)), call(key, A.candidate(msg))])
    for (const r of [b, c]) if (r.ok) r.score = score(r.raw, r.stop)
    rows.push({ id: x.id, question: x.question, baseline: b, candidate: c })
    const tag = (r) => (r.ok ? `${r.score.json ? "json" : r.stop} ${r.ms}ms` : `ERR ${r.error}`)
    console.log(`  ${i + 1}/${items.length} baseline ${tag(b)} · candidate ${tag(c)}`)
    if (!b.ok && !c.ok && /usage limit|credit|authentication/i.test(`${b.error} ${c.error}`)) { console.error("stopping: account-level error"); break }
  }
  const summary = { at: new Date().toISOString(), baseline_model: models.deep, candidate_model: models[candRole], n: rows.length, baseline: summarize(rows, "baseline"), candidate: summarize(rows, "candidate") }
  const blind = blindFile(rows)
  fs.writeFileSync(path.join(outDir, "rows.json"), JSON.stringify(rows, null, 2))
  fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 2))
  fs.writeFileSync(path.join(outDir, "blind-ab.md"), blind.md)
  fs.writeFileSync(path.join(outDir, "key.json"), JSON.stringify(blind.key, null, 2))
  console.log(JSON.stringify(summary, null, 2))
  return 0
}

process.exitCode = await main(process.argv.slice(2))
