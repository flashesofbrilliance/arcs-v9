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

# Handoff — v3.23.0 (2026-08-07)

> **For Claude Code:** active pickup point. PRL chatbot session: daily status routine shipped, Tidio
> Lyro/Flows architecture confirmed in writing, client + vendor emails sent, prl.arcs.care updated.

## What shipped (2026-08-07)
- **Daily exec-status routine** (scheduled task `prl-daily-status`, weekdays 9:31 local + jitter): reads a
  status-board SSOT, drafts an exec email to Todd **only when the board changed**. Draft-only (the Gmail
  connector has create_draft but **no send API**; true auto-send needs the Resend connector authorized, which
  would send from a verified domain, not Zach's Gmail). SSOT = `~/.claude/scheduled-tasks/prl-daily-status/
  board.json` (stable path); versioned copy `runtime/recoil/generated/prl-status/`. First run **Mon 2026-08-10**
  — hit "Run now" once to pre-approve the Gmail tool + confirm headless can reach it.
- **Tidio Lyro/Flows architecture CONFIRMED** (support, in writing): order is **Flows -> Lyro -> Human**,
  sequential, **never nested**; **no Lyro node inside a Flow**; only **"Visitor Says" flows conflict**
  (button/attribute flows coexist); **Simple Actions** is the only in-Lyro logic (legacy, plan-gated). Banked
  into `2026-08-06-lyro-config-plan.md` + `prl-lyro/handoff-policy.md` (resolves gauntlet #2/#6). 1.5 design:
  capture = a **non-input-triggered Flow** (runs first), Lyro = free-text fallback.
- **Tidio email config = Tidio-support, not IT.** Domain + info@ complete in Tidio; dashboard still says
  "contact support" -> Zach emailed support w/ screenshots. Site IT block + task doc reframed (IT only confirms
  SPF/DKIM/DMARC + M365 forwarding + info@ monitoring).
- **Emails sent:** weekend recap to Todd (w/ Stripe 1.2 kickoff link); Lyro clarification to Daniel
  (d.triana@tidio.net) CC support — support confirmed our finding.
- **prl.arcs.care:** added "For your team" copy-paste blocks (site maintainer + IT), reframed IT/Tidio split,
  1.5 callout now notes the confirmed Flows->Lyro->Human order.

## Open / next
1. **First status-routine run Mon 9:31** — verify it drafts; "Run now" to pre-approve the Gmail tool.
2. **Todd decisions:** specs-vs-route (rec: route), after-hours handoff fix (rec: yes), safe CRM test path
   (sandbox or one labeled test lead), phone_work required-vs-placeholder, add "Chatbot" lead source. Nothing
   internally blocked.
3. **Tidio email-config** awaiting a human at Tidio support (screenshots sent).
4. **On Todd's greenlight:** wire Tidio flow -> Zapier Catch Hook -> SugarCRM Create Record (Leads, full state
   names, status New, assign Bill Galla, email1). Do NOT write to Sugar before Todd approves.
5. Optional: authorize **Resend** to flip the status routine from draft to true auto-send.

## Blocking
NONE.

## Next session starts at
`/handoff-pickup`. Status routine SSOT = `~/.claude/scheduled-tasks/prl-daily-status/board.json`. Full PRL
detail in machine-local memory `project_todd_hotes_prl_resins.md` (2026-08-07 entries).

---

# Handoff — v3.24.0 (2026-08-09)

> **For Claude Code:** active pickup point. PRL chatbot 1.5 experience-design session. Confirmed Tidio account
> capabilities end to end, grounded the two-ICP audience design in Todd's calls, set the build sequence.
> **NO live Tidio account changes were made** - all research/design, committed to `runtime/recoil/generated/prl-lyro/`.

## What landed (research/design only; nothing on the live Tidio account changed)
- **Account capabilities CONFIRMED (in-app + docs):** base tier + paid **Flows (2,000 visitors/mo)** + paid
  **Lyro (50 AI conversations/mo)**; **NOT Plus** ("PRO" badge is cosmetic). **Audience-scoping of Lyro data
  sources IS available** ("Set audience" in each source's Manage menu, not Plus-gated) -> the dual-experience
  design is a GO. **Lyro Tasks + immediate-handoff are quota-free.** No native Tidio<->Sugar/ZoomInfo (Zapier in
  the middle). No doc-backed native A/B. Tidio help docs read ONLY via the built-in Browser pane (WebFetch 403s;
  claude-in-chrome is policy-blocked on help.tidio.com). Full ref: `prl-lyro/tidio-capabilities-research.md`.
- **Two-ICP audience design (from Todd's Granola calls):** **Molder** (knows the grade, transactional -> fast
  lane to a territory rep) vs **OEM/engineer** (has an application, consultative -> the 2 dedicated OEM reps).
  Both route + never-fabricate; differ by destination + tone. Opening qualification question stamps a contact
  property and branches. Doc: `prl-lyro/icp-audiences-molder-vs-oem.md`. Markets page = separate application axis.
- **Confirmed live fabrication risk:** the Product Catalog is exploded into **150 active "specifications" Q&A
  pairs** in Lyro (+4 spec PDFs), all audience=Everyone. Universal fix = set the spec PDFs **Copilot-only**.
- **Lyro flow JSON regenerated** (`prl-chatbot-flow.json`, onFirstVisit + phone required-by-construction); phone
  decision **LOCKED = required** (Todd). Import blocked by Tidio's native OS file picker (browser automation
  cannot drive it); staged for manual import at `~/Downloads/prl-chatbot-flow.json`.
- **Full orphaned-lead review** enumerated for Todd: **37 genuine / 28 orphaned (20 HIGH)**. Local PII sheet
  `~/Downloads/prl-orphaned-leads-FULL-2026-08-07.md` (not committed).
- **info@prlresins.com shows GREEN on the dashboard** (mailbox connected) - may be resolved since the "contact
  support" state; re-verify before telling Todd IT still needs it. **1,696 unassigned tickets** (mailbox-sync
  backlog) - triage parked.

## Next session - sequence set by Zach (B -> checkpoint -> A)
1. **B: map + /impeccable the CURRENT chatbot journey** (read-only baseline).
2. **CHECKPOINT: Zach reviews design spec + product requirements + implementation plan** before any build.
3. **A: build the two-experience audience routing** on staging (create Molder/OEM audiences; qualification
   branch; spec PDFs -> Copilot-only; per-persona handoff) - ONLY after checkpoint approval. Backup-first,
   reversible. No live change has Zach's go yet.

Parked: 1,696-ticket triage (Tidio auto-Spam folder helps; best = mailbox export for offline analysis like the
GF data, or search-driven surface; dedupe vs the 37 GF genuine). info@ re-verify. Manual Tidio flow import.
CRM delivery (1.1/1.2) still gated on Todd's safe test path.

## Blocking
NONE internally. Zach checkpoint-gates the build (A).
