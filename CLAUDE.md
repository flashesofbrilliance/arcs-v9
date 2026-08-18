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

# Handoff — v3.37.0 (2026-08-18)

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

# Handoff — v3.36.0 (2026-08-17)

> **Active pickup point.** Family public-surface reconcile: good / build / lab / playground are
> now four renders of one `_SEEDS` bank, guarded by a drift tripwire wired into pre-push. On
> `main` (head `704a9be`), deployed + curl-verified live. Separate track from v3.35.0 (PRL/Todd).

## Headline: one seed bank, four family surfaces, a tripwire that won't let them drift

good.arcs.care and build.arcs.care had drifted from the repo roster and from each other (build
omitted rosetta-shell/resume-tailor that good featured; ADR count frozen at 55). Reconciled both,
then made the fix structural instead of cosmetic:

- **good.arcs.care** — added the family install band (the invisible-until-now `arcs-skills`
  marketplace one-liner + `brew tap flashesofbrilliance/tap` + npm). Tightened "coming soon" to the
  honest "repo public · package install pending" — blindsat/linkedin pip is genuinely not live
  (verified in `distribution.jsonl`); the earlier "not yet published" read as drift but wasn't.
- **build.arcs.care** — goods rail reconciled to 9 (added rosetta-shell + resume-tailor, tier-A
  first); ADR 55→59, goods 7→9; new live **"Board"** band (shipped / in-progress / next / blocked)
  rendered from the *existing* `/api/pulse` issues payload — zero new backend — plus a latest-
  decisions ADR strip (ADRs named, not linked: arcs-v9 is private).
- **Playground folded into the bank** — the 4 performers (12d-orbital / knowledge-lattice /
  alexandria / moire) are now `seed_type=performer` rows in `_SEEDS/index.jsonl` (+ledger receipts).
  Playground was the one surface living *outside* `_SEEDS`; now germinate's seed format is the shared
  substrate across all four. `seedbank_drift_check.py` counts `seed_type==repo`, so these don't skew it.
- **`scripts/sync_family_roster.py`** — the four-surface tripwire. `--check` exits 1 when any surface
  disagrees with the bank, the playground routing enum (`next.config.ts`), or the ADR/goods/lab counts.
  Emits `public/family-roster.json`. **Wired into `.git/hooks/pre-push`** before the build (fail-fast,
  guarded to no-op on branches without it). Negative-tested — it does fail on injected drift.

## Architecture to carry forward
One bank → four renders: **good/build** = published goods (`distribution.jsonl`, live channels); **lab**
= `lab_candidate ∈ {ripe,maybe,poc}` (`index.jsonl`); **playground** = `seed_type=performer` (cross-checked
vs the next.config routing enum). The pages are still hand-authored HTML *audited against* the bank —
NOT yet *rendering from* `family-roster.json` at runtime. A client-side fetch would be swallowed by the
subdomain host-catch-all rewrites (same trap `sync_family_tokens.py` notes). So "single source" today =
single-source-of-truth-for-the-auditor, not literal render. Closing that is an open loop below.

## Next / open flags (all verified this session)
- **`resume-tailor-skill` is in `distribution.jsonl` but NOT in `index.jsonl`** as a repo seed — the
  reference connector tool is missing from the seed index. The two catalogs disagree; add the row.
- **Coverage-gap, 5 uncatalogued** (`distribution.jsonl`): `resume-tailor-skill`, `arcs-skills` (the
  marketplace), `homebrew-tap` (the tap), `arcs-career-fit`, `arcs-memory-pipeline`. Profile repo = legit skip.
- **`arcs-memory-pipeline` + `arcs-career-fit` are PUBLIC but described "Private pending review."** Desc
  claims "synthetic fixtures, no personal data," yet visibility contradicts the description. Confirm
  intended-public and fix the stale clause, or flip private. Honesty/privacy loop, given this session's theme.
- **lab.arcs.care has no route** — lab is a build.html section marked "not yet" (intentional). A real
  lab.arcs.care (the lab-mint factory) is unbuilt.
- **Make the pages render from `family-roster.json`** to go from audited-consistency to literal single-
  source — but solve the host-rewrite-swallow first (an `app.arcs.care/api/roster` endpoint, like `/api/pulse`).

## Blocking
NONE for this track. (v3.35.0 PRL track remains blocked on Todd — unrelated.)

## Deploy note
Commit `704a9be` pushed straight to `main` from this worktree; pre-push hook ran the new tripwire +
`npm run build` (no `--no-verify`). Both surfaces confirmed live via `curl` (good marketplace band; build
"9 goods live" + Board + `x-matched-path: /build.html`, cache HIT) before reporting done — the
verification bar for static-route changes.

---

> _v3.35.0 (PRL routing ground-truth) and earlier relocated to `_ARCHIVE/handoffs.md` on 2026-08-18._
