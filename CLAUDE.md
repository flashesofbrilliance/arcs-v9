@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
  into the CLAUDE.md block and marks the ledger claimed; the global SessionStart hook flags any
  worktree whose trail was never claimed. Compaction never writes CLAUDE.md anymore.
- **Open work lives in `_QUEUE/induced-backlog.jsonl`** — items carry route/gates/trigger; execute
  from there without replanning. Dense multi-domain sessions: run `/fold` to spawn composed sessions.
- **On-demand only** (do NOT read to orient — open only when the task actually needs them):
  `MEMORY.md`, `SKILL.md`, `_ARCHIVE/handoffs.md`, `_ARCHIVE/memory-archive.md`, `_STATE/*`.
- There is no "read MEMORY→SKILL→WORLD→AGENTS in order" chain anymore. That mandate cost ~40k
  tokens per session and was retired 2026-07-19; open a specific file only when a task points to it.

# Project Map (read this before exploring)

## Stack
- Next.js 16 App Router · Prisma 7 + SQLite (`dev.db`) · Auth.js v5 magic link · Anthropic SDK

## Routes
| Path | File | Purpose |
|------|------|---------| 
| `/` | `src/app/page.tsx` | Home / entry |
| `/dashboard` | `src/app/dashboard/page.tsx` | **Main compass UI** — question input, prep form, result |
| `/compass` | `src/app/compass/page.tsx` | Magic-link login form |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | Cartography brief (two-column) |

## API Routes
| Endpoint | File | Purpose |
|----------|------|---------| 
| `POST /api/compass` | `src/app/api/compass/route.ts` | L0–L5 Claude pipeline → Receipt |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession |
| `GET /api/brief/[receiptId]` | `src/app/api/brief/[receiptId]/route.ts` | Generate/fetch Brief |

## Lib
- `src/lib/db.ts` — Prisma client singleton
- `src/lib/auth.ts` — Auth.js v5 config (Resend magic link)
- `src/lib/ygate.ts` — Y gate computation (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT)
- `src/lib/env.ts` — env validation

## Schema (prisma/schema.prisma)
Core models: `User` · `PrepSession` · `Receipt` (DEWY + Y gate + kinematic + lineage) · `Brief` · `Outcome`
All JSON arrays stored as TEXT (SQLite). Enums as plain strings.

## Design tokens (inline style objects, no CSS framework)
```
bg: #020408 | surface: #0d1117 | border: #1e293b
text: #e2e8f0 | muted: #475569 | dimmed: #64748b
cyan: #00F0FF | green: #00FF9D | gold: #FFD700 | red: #FF4D6D
```

## Y states → render resolution
GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN

# ARCS v9 Architecture (governing law)

## ROM Primitives — constitutional, never violate
1. **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures; show the break and the gold
7. **WRITE-LOCK** — one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. When a new handoff
  lands, move the oldest live one into `_ARCHIVE/handoffs.md`.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.66.1 (2026-09-26)

> **Off-repo thinking session: falsifiable criteria for a public Farcaster debate, shipped as a pre-registered
> bet + a phone card; then memory consolidated.** No product code touched. Deliverables banked on branch
> `claude/falsifiable-position-criteria-inltlk` (not merged; nothing deployed).

## Shipped
- **The Loop-Closing Wager** (private Artifact, v2): https://claude.ai/artifact/ApVz1HbRKh575HTSBDEZZY.
  @six vs @czar, 7 sub-claims with kill conditions, crux test (>50% keep default-on proactive agent after
  90 days), adoption x attention 2x2, ground rules, sign-by-reply. Wrap-lint clean after a measure fix.
- **Settle-the-debate card** (PNG, 1170x2898): plain-language 3-test version for posting from a phone.
- Sources: `_ARTIFACTS/2026-09-26-loop-closing-wager/` (page html, card html, png).
- **Memory consolidated:** MEMORY.md live window = September; v3.46.0 and older moved verbatim to archive.

## Open (next session)
1. Zach to share the Artifact (Share menu; it is private, the tagged people hit a sign-in wall otherwise),
   post the card, and collect "agreed" replies. Two blanks await the parties: six's diffusion deadline, a referee.
2. If both agree: file a decision receipt for the wager (ex-ante, horizon `1-3y`) and set a 2028-09-26 check.
3. Backfill gap: v3.66.0 has no MEMORY.md entry.
4. Carried from v3.66.0: visual-slop brand allowlist awaits Zach landing the design-system branch; cold-recon
   redaction doubled-article fix.

# Handoff — v3.66.0 (2026-09-26)

> **Cold-reconstruction public good: CLI + a published NFTT trilogy + a warm-vs-cold experiment,
> then the AI-slop safeguard back-propped and wired into the FE ship-gate.** Opt-in build forked to
> its own session; ran daylight-first with a bless gate at every publish. All shipped to main and
> LIVE on good.arcs.care. Five PRs merged (#505, #506 sibling, #507, #509 sibling, #510).

## Shipped + LIVE (verified on prod, 200 + content + PII-clean)
- **`tools/cold-recon/`** — stdlib-only CLI (recoil-report shape). `gather` (git+files, ZERO
  transcript, coldness enforced structurally) → `prompt` (cold-agent contract) → `validate` /
  `leakmap` / `render`. Leak map = observability audit (reconstructability as a measurable
  property). Hardened by a sibling session (#506): em-dash normalization + in-tool `--redact` +
  `selftest` 4/4. NOT claimed patentable; only as good as commit-as-you-go discipline.
- **NFTT trilogy on good.arcs.care** (all own index cards): `the-cold-reconstruction` (method +
  real PoC run, reconstructability 0.895), `the-control-and-the-experiment` (warm-vs-cold, n=1),
  `receipts-or-it-didnt-happen` (the diptych). Plus 4 redacted companion reports at `/report`
  depth-ladder routes (unredacted renders stay internal — int/ext air-gap).
- **The experiment finding** (witnessed GREEN): warmth does not corrupt WHAT you ground, it changes
  WHETHER you ground at all; coldness's value is structural (no memory → can't narrate from memory).
  4-run table: cold 0.90/0.84, warm-relaxed 0.26, warm-matched 1.00 — the collapse was the cite
  instruction (confound), controlled. Running the control corrected my flattering first explanation.
- **Record hygiene** — committed the previously-untracked incident RCA + witness stubs (the live
  leak the tool surfaced; insight #2 demonstrated on itself).
- **AI-slop safeguard wired into the FE ship-gate** (#510): `slop_lint` landed on main via a sibling
  session (#509, single source). I wired it into `scripts/nftt-gates.sh` — mechanical cliché/em-dash
  = HARD FAIL, burstiness+specificity = ADVISORY in `--mode essay` (evidence-aware, 10% floor the
  sibling calibrated to real essays, correcting my 20-25% which would have false-failed the genre).
  Proven fails-on-bad AND passes-on-good.

## Open (next session)
1. **Visual-slop half (Adaptation 2) — brand-visual allowlist for the NFTT pages: BUILT + A/B-verified,
   awaiting merge.** The design-system-normalization session (branch `worktree-agent-a9c05965613c705e2`,
   local, unmerged) built the brand profile against my relayed spec and verified it: brand false-positives
   drop to 0 on all 3 posts (cold-reconstruction 41→16, control-and-experiment 35→11, diptych 56→27),
   real debt fully retained (undersized-ui-text, low-contrast, tiny-text). Exempted set (8, all
   verified-firing): design-system-{font,font-size,color,radius}, all-caps-body, wide-tracking,
   hero-eyebrow-chip, dark-glow. Note: `tiny-numbered-labels` + `border-accent-on-rounded` from my spec
   fire 0 times (absorbed by all-caps-body/wide-tracking + design-system-radius) so they were omitted, not
   added dead. **Gate: lands on main only when Zach reviews + lands the design-system branch (7-wave
   migration plan needs his review).** Then: re-run the detector to confirm 0 brand-false-positives, add
   the detector step to `nftt-gates.sh` beside the slop_lint step (#510).
2. **cold-recon redaction phrasing** — the doubled-article artifact ("a a candidate role candidate
   bundle") in the live warm-relaxed report; handed to the hardening session `[42a0ec]` as a test case.
3. Carried: `_STATE/night-moves/2026-09-26.md` is the day's ledger (on main).

## Lessons (in the record, not re-derived here)
Witness GREEN 2026-09-25 (coldness removes the option of dishonesty-by-fluency). Decision receipts:
`2026-09-25--cold-reconstruction-publish--ZH`, `2026-09-26--receipts-diptych-publish--ZH`. Specificity
floors are mode-relative — forcing an essay to a marketing floor is Goodhart (the diptych's own lesson,
applied to the tool by the sibling session that measured before asserting).
