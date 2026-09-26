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

# Handoff — v3.67.0 (2026-09-26)

> **NFTT contrast debt repaired + the whole NFTT corpus brought into head-meta conformance, behind
> two Frustration Gates. All merged to main and prod-verified live on good.arcs.care.** Follow-up to
> v3.66.0's call-C low-contrast ratchet: paid down the genuine debt the ratchet deferred, then swept
> the gap-class it revealed across all 38 NFTT pages. Draft-first throughout; merged only on Zach's
> explicit go.

## Shipped + LIVE (verified on prod)
- **take-home-trap-dossier genuine WCAG fix** (`3fbefb74`, `b235654c` -> `daf3fbad`): the `--dimmed`
  token failed AA on its real dark surfaces (`#64748b` = 3.63:1 on `#161b22`) and in light mode. Raised
  dark -> kit-canonical `#748699` (AA, from `45fd49a5`), light -> `#5e6b78`. Detector low-contrast
  **111 -> 81**; the 81 residue is all VERIFIED artifacts (cross-theme `#ffffff` fallback + unresolved
  `#000000` default — every flagged dark token passes on its real surface). Ratchet baseline dropped
  111 -> 81 per its own provenance, so it no longer exempts the repaired debt. Also brought
  `nftt-gates.sh` to PASS: `· NFTT` title suffix, description + robots meta, and defanged the two live
  IOC emails to `[.]com` (matches the page's own convention; correct threat-intel hygiene, clears the
  blanket PII scan). Redaction/PII discipline intact (only color tokens + meta changed).
- **Whole-corpus head-meta conformance** (`ce2b504b` -> `ef4282ee`): 9 nonconforming `blog-nftt-*.html`
  given the `· NFTT` title suffix + a faithful description (from each page's own lede/h1). `robots=index`
  added to the 4 public standalone posts; the 4 recon-report fragments + the HUD KEEP `robots=noindex`
  (redacted companion reports — int/ext air-gap; verified still noindex live). `blog-nftt-index.html`
  exempt (listing page, deliberate `· ARCS` title). Fixed a pre-existing en-dash (`L0–L7` -> `L0-L7`).
- **New Frustration Gate** `scripts/nftt_meta_gate.py` (stdlib-only; per-file for pre-commit ADDED+MODIFIED
  + `--all` sweep; exempts index; `--self-test` proves fail-on-bad + pass-on-good) wired into
  `scripts/git-hooks/pre-commit`. `--all` sweep GREEN (38 files, only index exempt). Root cause it closes:
  `nftt-gates.sh` checks head-meta ONE FILE AT A TIME, so legacy posts drifted until touched.
- Receipts: `2026-09-26--nftt-dossier-contrast-and-gate-merge--ZH`,
  `2026-09-26--nftt-headmeta-conform-all-plus-gate--ZH` (both fully confirmed against live prod).

## Open (next session)
1. **Carried from v3.66.0**: visual-slop half — wire the design-detector step into `nftt-gates.sh` once
   the design-system brand-profile branch lands on main (gated on Zach's 7-wave-migration review).
2. **Local main checkout is parked on another branch**, so ITS `git-hooks/pre-commit` won't run the new
   NFTT block until it next lands on main; everyone via origin/main already has it.
3. Carried: cold-recon redaction phrasing test case (`[42a0ec]`); `_STATE/night-moves/2026-09-26.md`.

## Lessons (in the record)
- **The "legacy page predates the gate" class**: a per-file gate that only fires on touch lets whole
  corpora drift silently. The fix is a batch `--all` gate wired to the always-run path (Frustration
  Gate, AGENTS.md #15) — fire it on round 2, not round 15.
- **Detector bg-inference is not ground truth**: classify artifact-vs-real by computing contrast on the
  ACTUAL rendered surface read from the CSS, not the detector's `#ffffff`/`#000000` fallback.
- **Robots gate checks presence, not value** — so a conformance sweep can add the tag to `noindex`
  fragments without ever pushing them to `index`; the air-gap survives the sweep.


# Handoff — v3.66.1 (2026-09-26)

> **Off-repo thinking session: falsifiable criteria for a public Farcaster debate, shipped as a pre-registered
> bet + a phone card; then memory consolidated.** No product code touched. Deliverables banked on branch
> `claude/falsifiable-position-criteria-inltlk` (not merged; nothing deployed).

## Shipped
- **The Loop-Closing Wager** (private Artifact, v2): https://claude.ai/artifact/ApVz1HbRKh575HTSBDEZZY.
  @six vs @czar, 7 sub-claims with kill conditions, crux test (>50% keep default-on proactive agent after
  90 days), adoption x attention 2x2, ground rules, sign-by-reply. Wrap-lint clean after a measure fix.
- **Ahmed-order re-cut + ARCS phone card** (local session, `4fba4f5`): verdict + one big number (50%) first,
  depth behind disclosure; `settle-card.png` (1170x2013) replaces the old off-brand card. All gates incl.
  Impeccable; 1 low-contrast false positive exempted and booked in `_PATTERNS/kintsugi-visual-grammar-seams.md`.
- Sources: `_ARTIFACTS/2026-09-26-loop-closing-wager/` (page html, card html, png).
- **Memory consolidated:** MEMORY.md live window = September; v3.46.0 and older moved verbatim to archive.

## Open (next session)
1. Zach to share the Artifact (Share menu; it is private, the tagged people hit a sign-in wall otherwise),
   post the card, and collect "agreed" replies. Two blanks await the parties: the oracle and the stake.
2. If both agree: file a decision receipt for the wager (ex-ante, horizon `1-3y`) and set a 2028-09-26 check.
3. Backfill gap: v3.66.0 has no MEMORY.md entry.
4. Carried from v3.66.0: visual-slop brand allowlist awaits Zach landing the design-system branch; cold-recon
   redaction doubled-article fix.
