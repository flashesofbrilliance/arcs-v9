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

# Handoff — v3.21.0 (2026-08-01)

> **For Claude Code:** active pickup point. Short, surgical session: closed a Vercel
> build-cost leak, generalized it, and formalized it as ADR-039. No counterpart work.

## What shipped (2026-08-01)

**Vercel deploy-cost leak closed + generalized + ADR'd.**

- **Root cause:** every commit to `main` was building — including docs-only. Logic was NOT
  inverted this time (that was the Jul-25 incident); the `commandForIgnoringBuildStep` exclude
  list was just **incomplete**. `docs(handoff)` commits touch `.claude/arcs-session-state.md`,
  and `.claude/` wasn't excluded (confirmed: `953effc docs(handoff): v3.20.0` built READY).
- **Fix:** added `":(exclude).claude"` to the ignore-step via `PATCH /v9/projects`. Full
  excludes now: `_MEMORY _PATTERNS _ARCHIVE _STATE .claude CLAUDE.md MEMORY.md AGENTS.md WORLD.md`.
- **Verified live:** docs-only commit `a1fed75` (`_PATTERNS/` only) → deployment **CANCELED**
  (skipped, no build); `public/` changes still build **READY**. Kept path-based, not
  `[NCI:SKIP]`-based — a `[NCI:SKIP]` polish commit can still touch shippable `public/`.
- **Vercel Agent audit:** both on-demand billing burners already OFF, read via
  `GET /v2/teams/<id>`: `agent.codeReview.auto.enabled=false`, `alertInvestigation.enabled=false`
  ("Investigate Anomalies Automatically" — the v3.18.0 "still ON" flag is now stale/corrected).
- **Generalized** into the impeccable skill as cost-discipline (SKILL.md → Cost discipline,
  v4.1.0; reference/init.md captures deploy-cost into PRODUCT.md; reference/live.md frames local
  iteration as the cost-correct loop).
- **ADR-039** (DECIDED, GREEN) — path-based ignored-build-step guardrail; index.json updated.
- **Memories consolidated** (updated, not duplicated): [[vercel-ignored-build-step-was-inverted]]
  (added the `.claude/` incident + live verification), [[vercel-config-via-cli-token-rest-api]]
  (agent toggles ARE API-readable — corrected "dashboard-only"), [[cost-efficiency-global-goal]]
  (path-not-message rule + local-iteration rule).

## Also cleaned up (leftover main-worktree working state, 2026-08-01)

Reviewed the three uncommitted items that had been sitting in the `main` worktree:
- **`ADR-026-debrief-calendar-invite-vs-email.md`** (untracked DRAFT, collided with tracked
  ADR-026 Debrief Delivery Fix) → renumbered to **ADR-040**, cross-linked, added to index. Still
  DRAFT (Decision pending Zach; calendar-invite-vs-email-only for the debrief close-the-loop).
- **`_ARTIFACTS/arcs-meta-audit-roadmap.html`** (+93 lines) → committed: a print-only "silkscreen
  on paper" stylesheet (inverts the dark cockpit to ink densities that survive a laser printer,
  forces SHARP fidelity on paper). Extends [[souvenir-ship-ritual]] to the roadmap deck.
- **`.impeccable/critique/…omakase.md`** (dual-agent critique, 18/36) → durable lesson banked as
  [[author-cosmology-over-guest-design-risk]]; its P0/P1 items were already resolved in the
  v3.20.0 omakase distillation. Critique file committed as the dated record.

## Also built this session (skills + code-verified ADR)

- **`/meta-audit` skill** (`.claude/skills/meta-audit/SKILL.md`) — codifies the 8-section Drift
  Sentry protocol from `_STATE/meta-audit-roadmap-v1.md` so any session runs one epoch
  consistently (Recoil → code-verified parity → gauntlets → Chi/Ma/Wuwei → stack-rank → append
  §8). Bakes in the hard-won non-negotiables (main-reachable epoch anchor, honesty gauge,
  weekly-and-small, verify-parity-from-code). Chose skill only; routine/workflow deferred.
- **Omakase critique → assembly rules.** Folded the omakase dual-agent critique into
  `.claude/skills/omakase-pipeline/SKILL.md` as a "Composition & assembly rules (the guest test)"
  section + wired into Step 4 (assemble against them) and Step 7 (guest-test lens) + anti-goal.
  The critique is now reusable rules, not a one-off. See [[author-cosmology-over-guest-design-risk]].
- **ADR-040 code-verified.** The debrief close-the-loop JTBD is **already shipped** (Option C,
  Stage 1): in-app `/debrief/[receiptId]` + `/api/receipts/[receiptId]/outcome` + scheduled
  Resend send (compass-time + long-horizon cron, loud logging, opt-in). NOT built: `.ics`,
  Google Calendar API. ADR-040 corrected to reflect this — the live question is only whether to
  add a calendar mechanism on top, at lower urgency than the original framing.

## Open / next

1. **Tao hosting work** — now safe to iterate; the leak that made every push a build is closed.
2. **ADR-040 is DRAFT** — the loop already closes via email+in-app; decide whether a calendar
   mechanism (.ics or Google Calendar) is worth adding, once there are ≥20 real (non-dev-test)
   debrief opportunities to measure against.
3. **Optional: schedule `/meta-audit` as a weekly routine** — deferred (needs a human toggle;
   a prior claude.ai "Drift Sentinel" routine was DECIDED-disabled; scheduled runs add spend).
3. Prior untouched: Louisville let-it-breathe (no follow-up unless Justin replies); Todd Hotes
   Zapier (blocked on Tidio plan); Ahmed ext send; showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New: ADR-039 (deploy cost guardrail). The ignored-build-step exclude list is
path-based — add a path when a new non-shipping file class enters the repo.

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

# Handoff — v3.25.0 (2026-08-07)

> **Active pickup point.** Supersedes v3.22.0 (Todd) as the current thread. The counterpart
> artifact family (Robin, Yuri) is now ready to be **parameterized into a CLI forge**. This
> session hand-built Yuri and it drifted from Robin's crispness bar; the fix is generation, not
> more hand-patching.

## Next session starts at — build + run the parameterized counterpart-forge CLI

**Read first:** `_PATTERNS/forge-pipeline-handoff.md`, then `_PATTERNS/counterpart-artifact-family-blueprint.md` (§1-11). Those are the full spec; do not re-derive.

**The order of work (from the handoff):**
1. **True up the UI kit first** — canonical tokens `src/ui-kit/recoil-report/_tokens.css` == `src/document/tokens.ts` (ADR-009/031, one DS). Regenerate `public/robin-receipt.html` off its omakase drift onto canon; make the `#tip` data-vis hover/tap tooltip a canonical kit component.
2. **Extract Robin's 4 surfaces** (`public/robin{,-profile,-codex,-receipt}.html`) as parameterized templates; the crispness rules are generation constraints (lead with the real-call STORY not a diagram; dual Read+Instrument codex; receipt-close first-class; clean 3-read triad).
3. **Build** `scripts/forge_counterpart.py` (SSOT->render) + the `/forge` skill (gather->synth->generate->verify->deploy), reusing recoil-new/prep/close/ship.
4. **Gates:** verify (impeccable detector, 0 em-dashes, fabrication/attribution Me=Zach/Them=counterpart) + honesty (insufficient signal -> flag `additional enrichment source inputs required`, never fabricate).
5. **Acceptance test:** regenerate Yuri to Robin's bar (add `yuri-receipt` from ex-ante `kleban.json` scored vs `kleban-recoil.json`; lead `yuri.html` with the real belief-flip story; re-tier codex+demo; single-call, no arc).

**Deploy:** main worktree only; Vercel CLI auto-refreshes its token (`vercel domains add <domain>`, project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`). Run model-efficiently.

## Shipped this session (2026-08-07) — all live
Robin the platinum master (one-door + profile + codex + receipt); `robin-profile` quiet-signals polish.
Yuri suite live + sequenced at `yuri.arcs.care`: one-door rebuild, `yuri-profile` (regrounded on a
net-new web scan, honest public-only caveat), `yuri-recoil`, `yuri-codex` (+ "08 · synchronization tax"
anti-Brooks's-Law beat), `yuri-demo`; `yuri-ext`/`yuri-sample` decluttered (redirect to the door). The
anti-Brooks's-Law roadmap suite (auditor/composer/sage/gauntlet-casting) banked in the blueprint §8.

## Blocking
NONE. The forge task `task_56561b51` predates blueprint §7-11 — restart it or have it re-read the blueprint.
Gmail reply draft to Yuri sits in Drafts awaiting Zach's send.
