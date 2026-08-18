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

---

# Handoff — v3.40.0 (2026-08-18)

> **Active pickup point.** Oracle-numbered (`next handoff` → 40; collision class closed).
> The Investment-Bank half of the self-cataloging session: five airgapped sweeps, the bank,
> the cheap-fix batch, a live GREEN witness, and a consolidated memory index (1-1 OK).

## Shipped this half
- **Opportunity-Cost Investment Bank v1** — `_ARTIFACTS/investment-bank-v1.md` (5-desk synthesis:
  drift-book + clients + jobs + product/OSS + bottom-up folksonomy counter-pass) + `drift-book.json`.
  Headlines: two-column north star (internal echo × external landing); secondary yield inversely
  correlated with primary landings (Yuri = negative P&L, positive R&D); evaluator-visibility gate
  (Meridian's unseen tier); consumability is the loop-killer (60-Second Read = top unshipped);
  `[NCI:SKIP]` = blind-spot generator (~70% of commits); falsification ledger is a scar log
  (33/33 FALSIFIED — no ex-ante rows); W5 law candidate: "the gate's first true positive is
  always the author."
- **Scars now priced**: falsification entries are catalog nodes (`kind: scar`) with declared
  scar-ref edges; 0/33 carry tuition figures (log cost at write time from now on).
- **Cheap-fix batch executed (F1/F2/F4/F5/F7 + lattice)**: scaffold repo → private (PII flag);
  germinate PARADOX reconciled (index status → live, receipt in provenance); stale kelly
  rewrites cut from vercel.json; Prophet memory → STALLED; clinical-AI loop memory minted
  (`project_altitude_clinical_ai`); observatory branch **KILLED** (tip `03e2439` preserved in
  `_STATE/branch-observatory-cherry-pick.json`); lattice countables regenerated 57→60.
- **Merged to main + deployed**: `/scan/[scanId]` live; atlases admin-gated at
  `app.arcs.care/warroom/{terrain-atlas,louisville-atlas}` (404 anon, verified).
- **Witness (GREEN, live)**: "A corpus with a falsifier discipline produces cleaner data than
  most companies' actual telemetry, because it never let itself lie." (`_STATE/witness/2026-08-18.jsonl`)
- **Memory index consolidated**: 1-1 OK, under byte budget, entries merged not dropped.

## Open queue (all in `_ARTIFACTS/investment-bank-v1.md`, approval-gated)
- **F3** (Zach's minutes): review `USER_PROFILE.md` in now-private scaffold → 2 CI secrets +
  3 tags ships the ready-not-live trio (8/11 → 11/11 live).
- **F6** job-loops.jsonl ledger · **F8** capability-parity inchworm (the Folksonomist-class
  safeguard: named faculties must carry TOOL-FIT receipts on their claimed domain).
- **M1–M13** mints incl. W5 law, NCI:SKIP practice change, ex-ante ledger rows, 60-Second Read,
  demote-don't-delete, counter-sweep into /meta-audit, M13 connect engagement lineage → seed bank.
- Standing ask-firsts: `audience:` rollout, pg/pgvector migration (ADR-065).
- **Field-notes draft** running in its own session (pseudonym + register gates in its brief).

## Blocking
NONE this track. PRL = blocked on Todd (see v3.39.0 / snapshot).

---

# Handoff — v3.39.0 (2026-08-18)

> Minted on main as v3.37.0; renumbered at merge — the SECOND v3.37.0 collision
> (Comet holds v3.37.0 on this branch). Handoff numbers are now oracle-governed
> (`scripts/oracle.py next handoff`) to end this collision class.

> **Active pickup point.** Continuation of PRL 1.1: Todd approved the web-forms approach in
> writing (Aug 17, 19:32 reply — "Makes total sense... it's how the leads from the PPC landing
> pages are supposed to work"), a $2,070 CWO (Addendum 1.2-A, invoice #NYQRTJPQ-0004) is live and
> payable at prl.arcs.care/status/troubleshooting, and mid-session a major access discovery
> changed the build plan. **Not yet paid as of this handoff.**

## Headline: real Sugar Studio access exists via Claude-in-Chrome, confirmed live, changes the plan

Spent significant effort earlier this session assuming no direct Sugar/WordPress access existed
(the sandboxed `Claude_Browser` tool showed login screens for both). **That assumption was wrong**
— Zach corrected it: he's logged into both in his real Chrome, reachable via the `claude-in-chrome`
MCP surface (real browser, real sessions), not the sandboxed preview browser used for Tidio
earlier. Confirmed live:
- **prlresins.sugarondemand.com (production)** authenticated and open (screenshotted the real
  revenue dashboard).
- **prlresinstest.sugarondemand.com (sandbox)** also open, in a separate tab, **with admin access**
  — Administration panel reachable at `prlresinstest.sugarondemand.com/#Administration`, where
  Zapier's connection to Sugar's API is visible/manageable.
- The `zapier.chatbot` sandbox account has real read/write access, not just API-level (already
  proven all session via the Zapier MCP connection).

**Process lesson, said plainly because Zach asked directly why I didn't try this first:** I
defaulted to the tool I'd already been using all session (sandboxed browser) out of habit rather
than checking which surface actually holds live credentials, even though the system prompt is
explicit that Claude-in-Chrome is for exactly this. When a task's question is literally "do you
have a live session," check the surface that can have one before the sandboxed one that never
does.

**What this unlocks for next session:** Sugar Studio's native Web-to-Lead Wizard is now directly
reachable and buildable, in both sandbox and prod, with admin-level access to the sandbox's
Administration panel. This likely replaces (or at least should be weighed against) the bridge
architecture sketched below, which assumed no direct UI access and built around that constraint.

**Also confirmed this session, separately:** the Zapier MCP surface has no tool to create a
standing webhook Zap (trigger + public URL + action) — `create_zapier_skill`, `write_code_action`,
and `execute_zapier_write_action` all run only when explicitly invoked in a live conversation, none
of them are unattended infrastructure that fires when a real site visitor submits a form later.
That's a genuine capability gap (not a process miss like the browser one), and it's the reason the
bridge architecture below leaned on a Zapier Catch Hook as a manual one-time setup step rather than
something buildable headlessly.

## In-progress, uncommitted — resume or revert

`prisma/schema.prisma` has an **uncommitted** addition: a `PrlWebLead` model (staging table for web
form submissions, holds first/last name, company, phone, raw + normalized state, forward status).
Migration was never run — `npx prisma migrate dev` failed with `"The datasource.url property is
required in your Prisma config file"`, not yet debugged. **This may no longer be the right
approach** now that direct Sugar Studio access exists — the native Web-to-Lead form doesn't need
our own DB staging layer. Decide next session: finish the bridge (debug the migrate error, build
the JS snippet + `/api/prl-lead` route, forward via a manually-built Zapier Catch Hook) or use the
newly-confirmed Sugar Studio + Administration access to generate Sugar's own native Web-to-Lead
HTML directly, which was the originally-recommended, already-proven mechanism (real "Web
Site"-sourced leads already arrive this way). Leaning toward the latter now that it's reachable.

## Everything else shipped and verified this session (all live)

- `prl.arcs.care/status/{crm,troubleshooting}` — both restructured to pilot-checklist style;
  troubleshooting page is now a formal CWO (**Addendum 1.2-A**, $2,070, in-scope/out-of-scope,
  best/base/worst, live Stripe invoice #NYQRTJPQ-0004 wired as a pay button).
- Vercel Web Analytics added to both static pages (gap: `layout.tsx`'s `<Analytics/>` never
  reaches `public/` files — same gap likely exists on other older static PRL pages, not audited).
- Two concurrent-session merges handled cleanly this session (another session independently
  shipped `/status/tidio`, `/status/build`, and a `_SEEDS`-driven family-roster sync — merged with
  `git merge origin/main`, zero conflicts both times, always build-verified before push).
- DEWY receipts + prior handoff (v3.35.0, now archived) cover the routing ground-truth finding,
  location_c resolution, and the beforeFiles re-catch bug — see `_STATE/2026-08-17-prl-1-1-session-
  decisions.dewy.json` and `_ARTIFACTS/prl-1-1-evidence/`.

## Comms state (as of 2026-08-18)

Todd approved the web-forms approach in writing (Aug 17, 19:32). CRM-routing / Bill-call ask still
awaiting his reply. Negative-keyword list started (he sent "sheet resin" as the first term, Aug 17
19:53). Invoice #NYQRTJPQ-0004 ($2,070) sent/live but **not yet paid** as of this handoff — check
before assuming the CWO is greenlit to start building.

## Next / open flags

- **Decide the web-forms build path** given the new Sugar Studio + Administration access (see
  above) before writing more code — don't finish the bridge architecture on the old assumption if
  the native form is now the better path.
- **Debug or abandon** the `prisma migrate dev` datasource.url error if the bridge path is chosen.
- Check whether invoice #NYQRTJPQ-0004 has been paid before starting build work under Addendum 1.2-A.
- CRM routing: still waiting on Todd's nod for the Bill call; nothing to build there until then.
- Real Chrome / Claude-in-Chrome now confirmed as a live-session surface for this project — default
  to checking it first for any "is there an existing login" question, not the sandboxed browser.

## Blocking

None hard-blocking, but two real decisions await: web-forms build path (architecture), and whether
Todd's invoice payment should gate starting Addendum 1.2-A work.

---

> _v3.38.0 + v3.37.0 (Comet) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18 (same day); v3.36.0 and earlier previously._
