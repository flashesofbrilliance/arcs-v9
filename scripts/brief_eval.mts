// brief_eval: eval-first harness for the brief-writer prompt (_PATTERNS/slop-free-rubric.md).
// Generates Situation Framing for a fixed fixture set with two prompts (the one on a git ref
// vs the working tree's src/lib/briefPrompt.ts), counts the mechanical tells per output, and
// writes every output so slop_lint / slop_eval can grade them. Same model + max_tokens as
// /api/brief. Fixtures are receipt contexts in the route's baseContext format; keep real
// user decisions OUT of the repo (pass a path to a local file).
//
// Usage: ANTHROPIC_API_KEY=... node --experimental-strip-types scripts/brief_eval.mts <fixtures.json> <out_dir> [--base origin/main]
import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { execSync } from "node:child_process"
import { BRIEF_SYSTEM as NEW_PROMPT } from "../src/lib/briefPrompt.ts"
import { scrubProse } from "../src/lib/prose.ts"

const [fixturesPath, outDir] = process.argv.slice(2)
const baseRef = process.argv.includes("--base") ? process.argv[process.argv.indexOf("--base") + 1] : "origin/main"
if (!fixturesPath || !outDir) { console.error("usage: brief_eval.mts <fixtures.json> <out_dir> [--base ref]"); process.exit(2) }
const key = process.env.ANTHROPIC_API_KEY
if (!key) { console.error("ANTHROPIC_API_KEY not set"); process.exit(2) }

function promptAt(ref: string): string {
  for (const f of ["src/lib/briefPrompt.ts", "src/app/api/brief/[receiptId]/route.ts"]) {
    try {
      const src = execSync(`git show '${ref}:${f}'`, { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] })
      const m = src.match(/BRIEF_SYSTEM = `([\s\S]*?)`/)
      if (m) return m[1]
    } catch { /* not at this ref */ }
  }
  throw new Error(`no BRIEF_SYSTEM at ${ref}`)
}

const TELLS: Record<string, RegExp> = {
  dash: /[–—―]/g,
  standing_opener: /\byou are standing\b|\bstands at\b|\bis standing at\b/gi,
  two_forces: /\btwo forces\b|\bforces (are )?(at work|operating|in (motion|tension))\b/gi,
  contrast: /\bnot [^.;:]{1,60}[,;] (it|they|this|that)('s| is| are)\b|\bis not [^.;]{1,60}\bbut\b|\bnot (about|a|an|the) [^.;]{1,60}\bbut\b|, not [a-z ]{1,40}[.;]/gi,
  kicker: /(?:^|[.!?]\s+)(?:That|This|It) (?:matters|is structural|is certain|is the tell)\./gi,
  labeled_parts: /\bwhat is (pushing|pulling|holding)\b|\bwhat you do not (yet )?know\b|\bthe unknown that matters most\b/gi,
  meta_comment: /\b(that|this|the) question is doing\b|\basking the right question\b/gi,
  internal_code: /\b(NCI|SATOSHI|SAGE|Y STATE|QUICKMOVE|COURT|ONE_WAY|TWO_WAY|PARADOX|FORK)\b/g,
  landscape: /\b(terrain|threshold|fork|momentum|gravitational|centrifugal|landscape)\b/gi,
}
const count = (t: string) => Object.fromEntries(Object.entries(TELLS).map(([k, re]) => [k, (t.match(re) ?? []).length]))

async function gen(system: string, ctx: string): Promise<string> {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": key!, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({ model: "claude-sonnet-4-6", max_tokens: 600, system, messages: [{ role: "user", content: `${ctx}\n\nWrite the Situation Framing section.` }] }),
  })
  const j = await r.json() as { content?: { type: string; text: string }[]; error?: unknown }
  if (!r.ok || !j.content) throw new Error(JSON.stringify(j.error ?? j))
  return j.content.filter((c) => c.type === "text").map((c) => c.text).join("").trim()
}

const fixtures = JSON.parse(readFileSync(fixturesPath, "utf8")) as string[]
const arms = { base: promptAt(baseRef), candidate: NEW_PROMPT }
mkdirSync(outDir, { recursive: true })
const summary: Record<string, unknown> = { base_ref: baseRef, n: fixtures.length, model: "claude-sonnet-4-6", arms: {} }
for (const [arm, system] of Object.entries(arms)) {
  const outs = await Promise.all(fixtures.map((ctx) => gen(system, ctx)))
  const totals: Record<string, number> = {}
  const perOutput = outs.map((raw, i) => {
    const shown = arm === "candidate" ? scrubProse(raw) : raw // candidate ships with the render-time scrub
    writeFileSync(`${outDir}/${arm}-${String(i + 1).padStart(2, "0")}.txt`, shown + "\n")
    const c = count(shown)
    for (const [k, v] of Object.entries(c)) totals[k] = (totals[k] ?? 0) + v
    return { i: i + 1, words: shown.split(/\s+/).length, raw_dashes: (raw.match(TELLS.dash) ?? []).length, ...c }
  })
  const withTell = Object.fromEntries(Object.keys(TELLS).map((k) => [k, perOutput.filter((o) => (o as Record<string, number>)[k] > 0).length]))
  ;(summary.arms as Record<string, unknown>)[arm] = { totals, outputs_with_tell: withTell, per_output: perOutput }
  writeFileSync(`${outDir}/${arm}-all.txt`, outs.map((o, i) => `### ${i + 1}\n${arm === "candidate" ? scrubProse(o) : o}`).join("\n\n") + "\n")
}
// Template detector: a 3-word sentence opener shared by >= 40% of an arm's outputs is a
// template, whatever its words (catches templates the named tells do not know about).
for (const arm of Object.keys(arms)) {
  const byOpener = new Map<string, Set<number>>()
  for (let i = 1; i <= fixtures.length; i++) {
    const t = readFileSync(`${outDir}/${arm}-${String(i).padStart(2, "0")}.txt`, "utf8")
    for (const m of t.matchAll(/(?:^|[.!?]\s+)([A-Z][a-z']*(?: [a-z']+){2})/g)) {
      const k = m[1].toLowerCase(); if (!byOpener.has(k)) byOpener.set(k, new Set()); byOpener.get(k)!.add(i)
    }
  }
  const floor = Math.max(2, Math.ceil(fixtures.length * 0.4))
  const templates = [...byOpener].filter(([, s]) => s.size >= floor).map(([k, s]) => `${k} (${s.size})`)
  ;((summary.arms as Record<string, Record<string, unknown>>)[arm]).template_openers = templates
  console.log(arm.padEnd(10), "template openers (>=" + floor + " outputs):", templates.join(", ") || "none")
}
writeFileSync(`${outDir}/summary.json`, JSON.stringify(summary, null, 2))
for (const [arm, v] of Object.entries(summary.arms as Record<string, { outputs_with_tell: Record<string, number> }>))
  console.log(arm.padEnd(10), "outputs (of", fixtures.length + ") with each tell:", JSON.stringify(v.outputs_with_tell))
