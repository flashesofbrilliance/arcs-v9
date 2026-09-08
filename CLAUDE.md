@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). A full interactive Next.js page exists but was never pushed — recoverable via cherry-pick
from a stale local clone, see `_STATE/snapshot.json` → `observatory.status`.

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.


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

# Handoff — v3.22.0 (2026-08-03)

> **For Claude Code:** active pickup point. v3.21.0 above preserved; v3.20.0 relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy. Full detail:
> `~/.claude/projects/-Users-zharris-arcs-v9/memory/project_todd_hotes_prl_resins.md`
> (machine-local, PRL section, entries dated 2026-08-03).

## Headline: Zapier MCP gives direct read/write on PRL's live SugarCRM

`inspect_zapier_actions` exposes three of the client's own systems: **SugarCRM**
(`SugarCRMCLIAPI`, connection "SugarCRM 7+ Importer"), **Unbounce**, **LeadConnector**.
Create/Update/Find Record plus raw API requests are all available. **This removes the
long-standing "we need a SugarCRM login from Todd" blocker entirely.** No new credentials
needed. Treat writes to that instance as production changes to a *client's* system.

## Read-only config audit (Leads schema + 100 live records). Nothing was written.

- `phone_work` is **required**, filled 100/100. The chatbot treats phone as optional, so any
  lead skipping it currently fails to create. Unresolved.
- `lead_source` is a fixed picklist with **no chatbot value** ("Other" 91/100, "Web Site" 8/100).
- **Correction:** `location_c` declares state abbreviations in schema but every live record uses
  **full state names**. Earlier guidance in artifacts saying "use MI not Michigan" was wrong and
  has been superseded. The existing Unbounce->Sugar zaps are correct.
- **95% of existing leads have no email address.** The bot captures it every time. Strongest
  value proof available for this engagement.
- 92/100 assigned to Bill Galla, status "New" 100/100 (confirms MVP routing design).
- All records on team **"Global"**: no record-level privacy, so a test lead cannot be hidden.

## Direct Tidio -> SugarCRM was researched and rejected

Sugar cloud REST is OAuth2 `password`/`refresh_token` only (1h token, no static key, no native
inbound webhook), so a single fire-and-forget flow node cannot authenticate. The one
unauthenticated path (legacy Web-to-Lead entry point) is license-gated to editions including
Campaigns and needs a form-encoded body Tidio may not send. **Keep Zapier in the middle** for
retry + visible task history.

## todd-call.arcs.care restructured (`736f9c0`) — read before editing that file

`/impeccable distill`: 11 nav tabs -> 6, **section ids changed**. Live: hero / `#status` /
`#tradeoffs` (new) / `#crmcheck` / `#roadmap` / `#howitworks` / `#progress`. All pre-sale
sections (`#reverse` `#recall` `#chatbot` `#mvp` `#protocol` `#sm-questions` `#stack`, quote,
stop-loss) moved inside a collapsed `<details class="bg">` at `#background`. Nothing deleted.
Fixed: nav was `display:none` under 768px (client reads on iOS), and the page still opened with
a price box 10 days after payment.

**Two traps if you script against this file:** "LOAD-BEARING QUOTE" appears as both a CSS comment
(~line 167) and an HTML comment (~line 756) — matching the first swallows the whole document head.
And `#howitworks` carries the `.page`-closing `</div>` plus the scroll-spy `<script>`, so slicing
to it naively closes the container early and later sections render full-bleed.

## Tooling status

Gmail MCP `search_threads` **is broken** (every query errors) though other Gmail MCP tools work;
use claude-in-chrome on mail.google.com instead. iMessage MCP times out even with Automation
granted. claude-in-chrome rejects `file://` (prefixes https://) so serve locally for visual QA.

## Blocking

NONE. Three client decisions outstanding (phone required vs placeholder; add a "Chatbot" lead
source; approve one labelled test lead or confirm a sandbox), but nothing is internally blocked.

## Next session starts at

Wire the Tidio flow's API call node -> Zapier Catch Hook -> SugarCRM Create Record (module Leads,
full state names, status "New", assign Bill Galla, details into `description`), then send one real
test lead end to end. Do not write to SugarCRM before Todd approves.

---

# Handoff — v3.23.0 (2026-08-05)

> **For Claude Code:** active pickup point. v3.22.0 above preserved; v3.21.0 relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy. This session mechanized the counterpart
> artifact family (the "instance #2" move). Nothing deployed; all changes staged in the
> `clever-jones-895d60` worktree for review.

## Headline: the counterpart-artifact-family FORGE pipeline is built

Extracted + generalized the live Yuri suite (`public/yuri{,-recoil,-codex,-demo}.html`) into a
deterministic, re-runnable generator triggered by a recoil seed. Same SSOT in -> same 4 HTML
surfaces out. This is the mechanized instance #2 of [[build-reusable-decomposable-interoperable-default]].
Blueprint it implements: `_PATTERNS/counterpart-artifact-family-blueprint.md`. New durable memory:
[[counterpart-forge-pipeline]].

## What shipped (all staged, uncommitted)

- **`partials/`** (10 fragments + README) — single source of truth for the shared grammar: ARCS
  dark-cockpit tokens, `.said` speaker quote, confidence meter, conviction chip, headline+lede+
  `<details>` progressive disclosure, sub-nav + IntersectionObserver scroll-spy, presentation mode
  (keyboard nav, G=go deeper), two-band inference ledger, JSON export, pw-gate, dwell analytics.
  Edit a partial -> every counterpart re-renders next run.
- **`scripts/forge_counterpart.py`** — deterministic `<name>-forge.json` -> `public/<name>{,-recoil,
  -codex,-demo}.html`, mirroring the `recoil_brief.py` SSOT->render pattern. Has an **overwrite
  guard**: refuses to clobber a non-forged file (marker `<!-- forged by scripts/forge_counterpart.py
  -->`) unless `--force` — this is what protects the live hand-authored `public/yuri.html`.
  `FORGE_SCHEMA_DOC` documents the SSOT schema.
- **`scripts/forge_verify.py`** — pre-deploy gate (exit nonzero blocks): impeccable detector
  (`~/.claude/skills/impeccable/scripts/detect.mjs`), 0-em-dash scan, attribution+labeling
  (said.speaker in {zach,counterpart}; every demo read has clue+inference; reserved reads have a
  disclosure), noindex + gate topology, password=first-name. Soft-surfaces the semantic checks
  (transcript attribution, role-archetype) for a human.
- **`.claude/skills/counterpart-forge/SKILL.md`** — `/forge <name>` orchestration (gather ->
  synthesize one SSOT -> generate -> verify -> deploy -> poll), reusing recoil-new/prep +
  omakase-pipeline. Carries the full deploy recipe (4 next.config.ts wildcard rewrites mirroring
  yuri-*, Vercel subdomain adds, from the MAIN worktree only).
- **`.claude/hooks/forge-suggest.sh`** (wired into settings.json PostToolUse Write) — suggests the
  forge when a new `runtime/recoil/generated/*-enriched-profile.json` lands.
- **`runtime/recoil/generated/kleban-forge.json`** — worked example / regression fixture. Renders
  to a scratch dir only (name=yuri collides with the live suite). All 4 surfaces verified in the
  in-app browser: gate admits on first-name, demo ledger (3 public + 1 reserved reads, color-by-
  value meters, conviction chips, chain expansion, JSON export), codex (5 altitudes, 3 disclosure
  sections, presentation mode keyboard nav 1/3->2/3). Detector clean on all 4, 0 em-dashes, verify PASS.

## Deliberately NOT done (rule-compliant)

- **No deploy, no `next.config.ts` edit.** Per the non-negotiables: never deploy from a feature
  worktree; deploy is per-real-counterpart from main. The kleban fixture also collides with the
  live yuri.arcs.care namespace, so it must never be written to `public/` or routed.

## Open / next

1. **Commit + review the staged pipeline** from this worktree (or cherry-pick to main). Files:
   `partials/`, `scripts/forge_counterpart.py`, `scripts/forge_verify.py`,
   `.claude/skills/counterpart-forge/`, `.claude/hooks/forge-suggest.sh`, `.claude/settings.json`,
   `runtime/recoil/generated/kleban-forge.json`.
2. **First real use:** run `/forge <name>` on the next live counterpart (Robin already has a
   5-surface family; a fresh counterpart with a clean namespace is the cleanest first deploy).
3. Prior untouched: Todd Tidio->Zapier->SugarCRM wire (v3.22.0 next-step); Louisville breathe;
   Ahmed ext send; ADR-040 calendar-vs-email decision.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New capability: `/forge <name>`. To render an existing counterpart, edit its
`<name>-forge.json` and re-run `forge_counterpart.py` (the marker lets it overwrite its own output),
then re-verify before any redeploy.
