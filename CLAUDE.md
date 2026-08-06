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

# Handoff — v3.24.0 (2026-08-06)

> **For Claude Code:** active pickup. Long Robin-family polish session — consolidates the v3.23.0
> sprawl (which had contradictions from incremental edits). 9 builds shipped + live; 4 memories
> banked; one big coherent fresh-budget pass queued. v3.22.0 (Todd/PRL) preserved below;
> v3.21.0 relocated to `_ARCHIVE/handoffs.md`.

## Shipped this session — 9 builds, all live on `main`
- `271ad83` remove non-working Present button (codex)
- `51f71b9` fix lopsided right-gutter — stripped `ch` max-width caps on all 4 pages (verified live)
- `dfb1dd0` persistent gate: `sessionStorage`→`localStorage` (robin.html + codex; per-origin sticky)
- `3986397` home index = clean 3-read triad → the three subdomains (dropped the 4th belief-log read)
- `47f8b40` #1 read = pulsing green LED beacon, "start here" text dropped
- `1f9a97e` triad markers = green/orange/red pulsing LEDs (7px, top-aligned, `--rgb` var + 1 keyframe)
- `ec49e63` read rows obviously clickable — trailing ↗ arrow (brightens/slides on hover) + pointer
- `d3e835f` hide codex flat jump-chip `.subnav` (`display:none`, markup preserved) pending refactor
- `4e3199b` full analytics coverage — script on receipt (was untracked) + `profile_click` events on profile

Robin family = **5 live surfaces**: `robin.arcs.care` (studio, gated, sticky) · `robin-profile` (open) ·
`robin-codex` (gated, sticky) · `robin-receipt` (open) + in-studio ledger. All domains attached/verified.
Home index is the clean triad: ● green Profile · ● orange Recoil · ● red Receipt, each an ↗ link.

## Memories banked this session
- [[sprezzatura-studied-carelessness-buoyant-flow]] — prepaid effort → effortless surface = the buoyant
  water carrying the harmonic narrative; looseness is structural, not a distraction.
- [[scandinavian-business-banter-is-carrier-wave]] — banter = compressed resolution / carrier wave; the
  carrier's STATE is itself a signal into the codex. N=2 Danish natural experiment (Robin held→landed;
  Peter Espersen skipped→crashed).
- [[comparative-recoil-orthogonal-echo-inward]] — Orthogonal Echo Detector turned inward = comparative
  recoil; two species of wuwei (breathe vs aikido). QUEUED (below).
- [[arcs-is-an-active-listening-aid]] — positioning: derives MEANING from signal, not amplification
  (hearing aid); the problem is rarely too little signal, it's too little meaning. NOTOMATION-clean.

## THE fresh-budget pass — `/impeccable` global write-lock + polish (ONE coherent build)
Heavy/token-intensive; deferred on purpose. Do NOT half-run across 4 live pages. Bundles:
- **(a) Codex subnav → tab-scoped jumps.** `.subnav` currently hidden (`d3e835f`). RE-ENABLE split per
  tab (panes toggle via `.tabpane.on`): Read = THE LINE(`s-line`)·VIBE/VEER(`s-beats`)·THE OFFER(`s-offer`);
  Instrument = HOW IT WORKS(`s-inst`)·THE BRIEFING(`s-brief`). Move each group inside its pane; chips only
  scroll (drop cross-tab `data-tab`). Keep the two-tab `.tabs` selector.
- **(b) Chip + row affordance** — reuse the SAME ↗-arrow + hover grammar shipped on the triad rows
  (`ec49e63`) so every clickable thing signals identically.
- **(c) Global fixed nav strip, all 4 pages** — ◆ studio (parent) + ①Profile ②Recoil ③Receipt,
  current active. Shared markup. Gates are `z-index:100` → strip `z-index:50` (tucks behind) + spacer-div
  offset (not body padding). Inject after `<body>`. One row, mono ~10-11px, fits 375px. Bump anchor
  `scroll-margin-top` 14→~52px so sections snap below the strip.
- **(d) Verify tooltips FIRE.** Machinery INTACT live (studio 16 `[data-tip]`+JS; codex 13+JS) — nothing
  deleted; it's a runtime issue (JS error halting the IIFE? z-index/position? touch vs hover?). Console-check
  + hover-test a hotspot.
- **(e) Visually verify** the shipped-but-gated changes: the triad + G/O/R LEDs on `robin.arcs.care` (enter
  pw `robin`) — colors/alignment/reduced-motion. (Gutter fix already confirmed live on the profile page.)
- **(f) Profile-card enrichment — 5 quiet signals** (5-verb loop; tag grounded/inferred ON the card; never
  overclaim N=3). Ship #1/#2/#3 (one story: earn the floor, keep the human channel open, reflect his thesis
  back); #4 tagged interpretation; #5 a small accent. Net-new dataviz — use the `dataviz` skill.
  1. Asymmetric altitude flex — ground BEFORE sky (grounded). Viz: gated ladder (SKY dim until GROUND locks).
  2. Humor = leading indicator of conviction (grounded). Viz: humor-beats overlaid on the conviction wave.
  3. Gift→return loop — buy signal = his own thesis reflected back (grounded). Viz: small closed loop.
  4. Focus↔Epic self-tension (inferred). Viz: tension axis; mark as interpretation.
  5. Bimodal conviction, no middle gear (grounded). Viz: two-peak vs faded bell.
- **(g) 3-call waveform picker + overlay** — `[Call 1][Call 2][Call 3][Overlay]`. Data exists in
  `robin.html`'s combined SVG. KEY: overlay normalizes x to call-PROGRESS (0→100%), not time (calls differ
  in length/beat-count). Lives on codex/studio, NOT receipt. 3 CVD-safe series colors (validate), direct-
  label, keep per-beat tooltips. = the comparative-recoil idea previewed within Robin's own 3 calls.

## QUEUED separately: first comparative recoil surface (Robin × Justin × Peter)
Three-way carrier-state diff: Robin (Danish, held→landed) vs Justin/Louisville (let-it-breathe/stillness)
vs Peter Espersen (Danish, skipped carrier→crashed). Robin-vs-Peter = matched Danish pair. Steps: pull
Peter's transcript (Granola/Fathom) + reverse-listen for where the carrier flatlined (confirm vs retrofit;
check altitude/fit too); normalize Justin + Peter into the manifold; run the structural diff. Framing:
[[comparative-recoil-orthogonal-echo-inward]] + [[scandinavian-business-banter-is-carrier-wave]].
**Home = admin-gated `/warroom/` index** (a "Comparative Recoil — Robin × Justin" entry linking the jeben
book + the Robin internal seed), NEVER a counterpart's studio (cross-counterpart leak,
[[internal-external-artifact-air-gap]]). The Robin internal seed likely needs moving into `runtime/warroom/`.

## OPEN DECISION for Zach: jeben.arcs.care
NOT a bug — the 404 is the security fix working as designed (admin-gated `/warroom/jeben`, fail-closed, per
`e321e3d`). The Justin-safe redacted "THE KEY" public copy exists on branch
`claude/louisville-brands-report-3ksoq9` but was never merged to main. (A) leave fail-closed admin-only
[current], or (B) promote the redacted public copy to main — if B, re-verify the redaction (plant-closing/
jobs/financials/"invent something" framing actually stripped, not div-hidden like the original leak).

## Housekeeping
- v3.21.0 relocated to `_ARCHIVE/handoffs.md` this session.
- Inert `#present*` CSS in `robin-codex.html` left for a later sweep.

## Blocking
NONE.

## Next session starts at
`/handoff-pickup`, then **THE fresh-budget `/impeccable` pass** above (nav re-enable + strip + card
enrichment + waveform picker + tooltip/LED visual-verify — one build). The comparative-recoil diff
(Robin × Justin × Peter) is the separate second track.
