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

# Handoff — v3.41.0 (2026-08-19)

> **Active pickup point — the loaf-cooling handoff.** Caps the v3.40.0 session's second arc:
> design-system unification across 8 surfaces, the page factory, ADR-066, and the live-culture
> naming. Oracle-numbered (41). Read v3.40.0 below for the open bugs — they are STILL the next
> session's first work.

## What landed after v3.40.0 (all pushed, all verified live)
- **One design system, 8 surfaces, zero exceptions:** prl.arcs.care root = Overview (masked
  todd-call content); /status/{progress,crm,troubleshooting,tidio,atlas,build}. Sticky pill nav
  (Overview-first) + identical global footer on every page; 916px wrap; glass panels, no hard
  dividers; balanced h1s; every mobile/layout defect fixed live (~20) — each now a rule in the
  factory SKILL.md. Mechanical audit script proves conformance (in-session pattern, re-runnable).
- **prl-page-factory skill** (`.claude/skills/prl-page-factory/`): atoms.css extracted from the
  live reference page + zero-dep generator; new page = ~20-line spec.json. Smoke-tested.
- **ADR-066 Generative Recoil** minted from a witnessed naming moment (witness stub GREEN,
  promoted): recoil is bidirectional — audit AND compose session residue into instance → class →
  invariant. Falsifiable: next PRL page must cost a spec, not a session. Build.html ADR stat
  61 (tripwire caught its own mint again, fixed the surface, never --no-verify).
- **Live-culture / ancient-starter doctrine** (Zach's naming): feed artifacts from the deployed
  instance, never parallel-maintain. Both claude.ai artifacts (atlas + ssot) rebuilt
  instance-first from the deployed page and republished to their same URLs.
- **Apex spine v15** added (generative-recoil-live-culture). **Seeds planted:**
  `live-culture-artifacts`, `page-factory-from-session` (+ earlier: `engagement-universe-doll`).
  **Memory minted:** [[generative-recoil-live-culture]] incl. 3 tao proverbs.
  **Parked for Aug-24 close-loop:** evidence-anchored re-pricing of 1.3–1.5 (1.4 highest
  exposure — attribution is ground-truth-verification work, the category that ran 3x).
- **Reading-room candidates (Alexandria):** ADR-066 + the starter framing join apex-spine as
  center-room candidates — placement idea only, not integrated.

## Register decision made and to hold
No src/ UIKit for PRL — the factory IS the UIKit at the right weight; React-ification only on a
third interactive surface family (rule of three). Don't blur into the app's FieldOS system.

## Next session (unchanged from v3.40.0, plus)
1. Co-pilot Task 1: empty-email filter + Roger Lamarre repair (CRITICAL, before more demo traffic).
2. Test-lead cleanup · rep notification · SLA sweep · baseline pull (briefs/meta-prompts ready).
3. UAT selector debug run · SEM template Phase 0 (fill 2 node schemas via export).
4. Aug-24 1.2 close-loop: expected-vs-actual + the parked re-pricing conversation with Todd.

# Handoff — v3.40.0 (2026-08-18, late)

> **Active pickup point — PRL 1.1/1.2 wrap session, part 2.** Continuation of v3.39.0's landing:
> the delivery leg went from "published" to genuinely verified, shared with Todd, and then two
> real bugs surfaced and one got fixed live. Numbered by oracle (40).

## Headline: chatbot→Sugar delivery VERIFIED end-to-end and shipped to Todd; two live bugs found after

- **Real WP-staging conversation → sandbox Sugar Lead confirmed** (`435cee66-9b40-...`, correct
  name split, location_c=CT, audit trail). Dual bar-raiser protocol with Zapier co-pilot worked:
  independent Sugar reads caught a name-split regression, a missing email1 mapping, AND a
  double-firing old Zap before publish. Zap `376827315` (Tidio → Code → ZoomInfo enrich →
  dedup-search → Paths A/B) is the live pipeline; old `series_376761228` superseded/off.
- **Todd-facing surfaces shipped:** `prl.arcs.care/status/progress` (pilot-checklist style, +25%
  type scale, viewport meta fixed on all 3 status pages, mobile card-stacking for the workaround
  table, click-to-load live chatbot embed, Recommended section w/ 30-min weekly check-in booking
  link + parallel 1.2-A kickoff). Root pages: Progress nav button, footer status links, phase
  table 1.2=Paid + 1.2-A row w/ live invoice button, mid-phase ex-ante receipt update (effort
  past the 12-30h band, cap holds), 1.1 re-tagged done-in-staging, 1.2 itemized per DoD recon.
  **Email to Todd SENT** (progress link + calendar link).
- **Tidio trigger fixed LIVE via claude-in-chrome:** root cause of the mobile-shows-Lyro bug was
  the flow's "Visitor returns to the site" trigger (fresh visitors got nothing → fell to Lyro's
  email ask). Replaced with "Visitor clicks on chat icon", activated, confirmed. Verified mobile
  1-1 with desktop afterward.

## OPEN BUGS (next session's first work)
1. **CRITICAL — empty-email dedup false-positive:** Zach's latest progress-page submission
   UPDATED a real 2021 lead (Roger A Lamarre/ROBE, id `ea77a7d2-1b0b-11ec-...`) because the
   payload email was empty and Find-Record matched arbitrarily. Fix in co-pilot: Filter step
   (email non-empty) before the search; empty-email → Path B create. Also debug WHY email was
   empty despite flow validation. **Repair owed:** clear Roger's description suffix
   ("— Updated via Chatbot") + title/industry "Not specified" back to blank.
2. **Test-lead cleanup** still owed (now ~8+ synthetic/test leads incl. 3x Zach).
3. **Lyro races the flow** for conversations with existing history (resumes Lyro convo instead
   of flow). Scope Lyro engagement or accept; also pre-chat email card duplicates the flow ask.
4. **"Read more here" links:** no toggle exists (checked Configure/Guidance/Data sources). It's
   website-source citation behavior. Recommended: convert ONLY the /contact/ source to manual
   Q&A (it currently cites the broken contact form — content bug), park rest for 1.3.

## DoD reconciliation (the honesty ledger — read before any "done" claim to Todd)
`_ARTIFACTS/prl-1-1-evidence/2026-08-18-dod-reconciliation.md`: every 1.1/1.2 gate is met /
waived-in-writing / re-baselined. Still open: Mailgun rep-notification (decision: bypass via
Zap email step + Barracuda allow-list precedent; prospect autoresponder deferred to DNS window),
baseline report (UNBLOCKED — Zapier MCP raw GET = the Postman Zach thought he needed), Layer 1
Lyro eval run (harness exists; Playwright automation sketched in `runtime/recoil/generated/
prl-lyro/uat/README.md`), business-email enrichment fill, 2 more state tests + dedup live test.
UAT skeleton authored: `uat/staging_chat_e2e.mjs` + fixtures (selector TODOs, not yet run).
Quota discipline documented (Playground ≠ Lyro quota; live chats burn Zapier tasks + ZoomInfo
credits; Lyro 11/50 used).

## Comms / money state
Invoice #NYQRTJPQ-0004 ($2,070, 1.2-A web forms) still OPEN/unpaid — work stays payment-gated
(staging exploration OK, no live webhook). Todd emailed the progress page + check-in booking
link (calendar.app.google/crDeY8HyJQvH4ahH6). Bill routing call still pending. Prod cutover
still explicitly gated (enum + auth repoint + Bill + Todd's go).

## Ideas parked for 1.3 (fits its literal name "Smarter lead recognition")
Fewer-questions flow + Zap backfill from Sugar/ZoomInfo reverse lookup (caveats logged: state
drives routing so never auto-fill it from HQ data; ZoomInfo hit-rate < 100% + location_c
hard-required = blank-field rejection risk).

## Parked for the Aug-24 1.2 close-loop: evidence-anchored re-pricing of 1.3–1.5
Zach's call (2026-08-19, explicitly not-right-now): recalibrate 1.3–1.5 toward worst-case-
anchored pricing using the ACTUAL actual-vs-expected multiplier from 1.1+1.2 (both overran
their bands on coordination, not build). Highest exposure = 1.4 ($6K): its real JTBD includes
end-to-end attribution/goal-mapping, which is almost entirely ground-truth-verification work —
the exact category that stretched 3x this engagement. The receipt mechanism already promises
"numbers re-checked against reality before each kickoff"; make that re-check compute the
multiplier from the banked receipts rather than re-guessing. Do this AT the close-loop, with
Todd, not unilaterally — it is a trust move ("we price from our own track record") when done
in the open.

## Idea parked for 1.4 ("Your paid landing pages") — template pair, and it's a REPAIR not a feature
Template unit = one Unbounce page + one Tidio onramp flow per product family, all sharing the
proven Zap-376827315 backbone. The 5 SEM Onramp drafts are hand-built instances of this pattern.
Key mechanics: "Visitor opens a specific page" trigger per landing URL (no collisions with the
chat-icon flow), Tidio flow Import/Export = JSON template with placeholder swap, campaign tag in
payload = per-page attribution for the baseline. KEY FRAMING: the legacy Unbounce->Sugar Zaps
(other Zapier account, 6801141) are partly broken — the template RETIRES them rather than fixing
N brittle connectors; each migrated page is one less broken legacy Zap. Zero new delivery work
per page. Cheap non-gated prep: author the template JSON from the AI-Handoff export + the 5
drafts' vocabulary before 1.4 kicks, so kickoff is stamping, not building. Quota check before
scaling: each active flow draws from visitors-reached (26/2000 now, fine for pilot).


> _v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
