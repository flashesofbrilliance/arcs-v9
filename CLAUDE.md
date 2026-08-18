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

# Handoff — v3.35.0 (2026-08-17)

> **Active pickup point.** PRL 1.1 landing session — Sugar routing ground-truth investigation,
> web-form delivery diagnosis, and a new prl.arcs.care/status/<seg> URL family for cross-workstream
> client-facing findings. Nothing merged to main via PR — this worktree's commits were pushed
> straight to `main` (fast-forward, build-verified each time) per existing repo convention for this
> track.

## Headline: half of Sugar's routing doesn't match the CSV, and it's not new

Before wiring chatbot delivery, ran a full 43-state sandbox sweep (create tagged lead → read
assigned rep → delete) against the territory-map CSV that's been the working source of truth.
**~49% mismatch.** Four distinct failure patterns, not one: wrong-rep (consistent, not a fluke),
"Distribution" corresponds to no real Sugar rule (every Distribution-tagged state routed
elsewhere), 2 active reps (Dan Damas, Tim Mulcahy) missing from the CSV roster entirely, and 6
states plus all 7 states outside Sugar's `location_c` enum land **unassigned** — worse than
misrouted, no queue catches it. Cross-checked against real prod `lead_source: "Web Site"` records:
same pattern, so this is already live on real leads, not a risk the chatbot introduces.

Resolved a real contradiction along the way: `location_c` wants abbreviations, not full names — an
Aug-11 doc's "full names" finding was a sampling artifact (91% manual/"Other" records in its
sample), re-verified live against the enum schema + the 2 real automated-path records that exist.

**Also found and merged in:** an unmerged branch (`claude/chatbot-1-1-jtbd-blockers-edda33`)
already had a capture-first Tidio flow design + a Layer-0 recognizer test suite (22,500 cases, all
pass) built and tested. Selectively checked out just that path (56 files, not a full branch merge —
117 vs 192 commits of unrelated drift since fork) rather than rebuilding leg 1 from scratch.

**Web forms:** Gravity Forms was never wired to create Sugar leads at all (separate from the
Barracuda email-quarantine issue Jorge partially fixed Aug 14 — that only affects notification
email, not CRM delivery). Recommended fix: Sugar's native Web-to-Lead form, already proven working
today for the small number of real "Web Site" leads. Not yet sent to Jorge/Josh — Todd needs to
approve the approach first, since it's a different mechanism than what Jorge has partial context on.

## Client-facing surfaces shipped

New URL family: **`prl.arcs.care/status/<seg>`**, pilot-checklist style (BLUF → status rows →
one-line ask → collapsed full detail). Live: `/status/crm` (routing findings + Bill-email draft +
Todd's calendar link), `/status/troubleshooting` (web-form plan, pre-decision). Reserved, not yet
built: `tidio`, `wp`, `build`. Both pages carry Vercel Web Analytics (added manually — `public/`
static files bypass `layout.tsx`'s `<Analytics/>` entirely, a gap that also exists on the older
`todd-call.html`/`prl-chatbot.html` and wasn't previously noticed).

**Hit and fixed the documented `beforeFiles` re-catch bug class** (same one already named in this
file's comments for `todd-call`/`julia`) on the first `/status/crm` attempt: excluded on the
*original* request path (`status/`) instead of the *rewritten destination* (`prl-status-crm.html`,
which contains `status-` not `status/`), so the fallback wildcard silently re-caught it on Vercel's
second `beforeFiles` pass. Caught via curl header inspection (`x-nextjs-rewritten-query` showed the
correct match; `x-matched-path` showed the wrong one — a clean build log gave zero signal). Fixed
both ways per the proven shape: `proxy.ts` `MULTI_PATH_MAP` as primary, `next.config.ts` regex
corrected to match the destination substring as backstop.

## Comms state (as of 2026-08-17, end of session)

Todd sent both emails (CRM routing + web forms) and a follow-up text to Bill during the session.
Two Gmail drafts created (not sent by us): Todd→Bill (routing call ask, his calendar link
embedded) already sent by Todd; a Todd-facing summary email for each status page, both sent by
Todd. Nothing sent to Jorge or Josh yet — correctly gated on Todd's approval.

## Captured

DEWY: `_STATE/2026-08-17-prl-1-1-session-decisions.dewy.json` (5 receipts — routing ground-truth
gap, location_c resolution, selective-merge decision, web-form-fix sequencing, status-URL-family +
re-catch-bug fix). No new ADR this session (PRL-track decisions, not ARCS-wide canon). Evidence:
`_ARTIFACTS/prl-1-1-evidence/` (full state-by-state sweep tables, flow JSON exports).

## Next / open flags

- **Blocking on Todd**: (1) nod + Bill call on CRM routing, (2) go-ahead on the Web-to-Lead fix
  before Jorge/Josh are looped in, (3) the negative-keyword/anti-ICP list he still owes (lower
  urgency, flagged in the same text).
- Once approved: generate the Web-to-Lead snippet from Sugar Studio, sandbox-test before touching
  the live site, then draft the Jorge/Josh handoff (not yet written).
- Once Bill's call happens: the per-state fix list is already scoped in `/status/crm`'s collapsed
  detail (4 rows, pattern → proposed fix) — implement whatever he confirms, no separate re-scoping
  needed.
- `tidio` / `wp` / `build` status-page segments are reserved (in both `proxy.ts` and
  `next.config.ts`'s enum) but not built — trivial to add later, one file + one map entry.

## Blocking

Todd's response on both status pages — no further PRL build work until he replies.

## Deploy note

All commits this session pushed straight to `main` from this worktree
(`claude/prl-chatbot-sugarcrm-605dbe`), build-verified via the pre-push `npm run build` hook each
time (no `--no-verify` used). Two production routing changes (the `/status/crm` fix, the
`/status/troubleshooting` addition) were each confirmed live via direct `curl` header checks before
being reported done, not assumed from a successful build/push alone — worth carrying forward as
the verification bar for any future static-file routing change.

---

> _v3.34.0 (ADR-namespace oracle + forensic remap) and earlier relocated to `_ARCHIVE/handoffs.md` on 2026-08-17._
