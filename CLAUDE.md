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

# Handoff — v3.16.0 (2026-07-22)

> **For Claude Code:** active pickup point. Version jumped to 3.16.0 to clear the known
> v3.13–v3.14 cross-branch numbering drift (flagged in prior handoffs) — do not read into the gap.

## What shipped (this thread, 2026-07-22)

**Ahmed Elsamadisi / Polyform AI — full reconnect-call loop, then mechanized the air gap.**

- **Internal war-room** `ahmed.arcs.care` (pw `ahmed`), 6 tabs: Pre-Call · Ex-Ante receipt ·
  **Forge** (ROM #6 Exogenous Forge pressure-test via claims-skeptic, struck "not a sales
  call") · **Recoil** (post-call, Granola transcript `e8648395`, belief-update ledger +
  **Belief Log v2** using confidence × conviction, NOT per-belief NCI) · **War Game**
  (kinematic manifold now **MEASURED** via `arcs_kinematics.py v1.3` — D1–D3 valid, D5–D12
  honestly labeled coherence-zone, not fabricated) · **Defensibility** (5-verb × 4-proofing +
  Activity-Schema Rosetta).
- **External counterpart-facing twin** `ahmed-ext.arcs.care` (open link, sanitized). Iterated
  from exec-summary → deep technical appendix → **competitor-safe strip** (architecture-not-
  weights; dropped schema DDL, mechanics, kinematics derivatives, `sqrt` sampling formula).
  Send-ready; draft note (LinkedIn + email) is in this session's transcript.
- **Air gap mechanized:** SSOT `runtime/recoil/generated/2026-07-22-elsamadisi.json` +
  `scripts/recoil_brief.py` — computes kinematics reproducibly and projects internal-vs-external
  by dropping `audience`-tagged fields (external run drops 14 fields + prints a redaction report).
- **2 memories banked:** `confidence-conviction-nci-operational-definitions` (confidence/conviction
  for beliefs, NCI for decisions only) and `internal-external-artifact-air-gap` (3 rules:
  own-updates-not-their-scores · method-crosses-subject-doesn't · architecture-not-weights).

## Open / next

1. **Ahmed (Zach-owned, not blocked):** set the pilot price (a number, once a customer is
   picked) + name one Polyform customer, then send `ahmed-ext.arcs.care`. Optionally take the
   Robert (decision-ROI) intro.
2. **Optional build:** render the `ahmed` HTML pages FROM the SSOT JSON so editing = editing
   data (full loop closure; deliberately not done this session).
3. Prior open items untouched: Todd Hotes post-Wednesday reply; v3.11.0 ledger-management +
   authenticated `/recoil` index.

## Blocking

NONE (waiting on Zach's send decision + price).

## Next session starts at

`/handoff-pickup` → if Zach has picked a customer + price, send the ext page; else the SSOT→HTML
render is the next build-ready item.

---

# Handoff — v3.17.0 (2026-07-23)

> **For Claude Code:** active pickup point. The recoil pipeline matured into a reusable system this
> session; three live engagements (Ahmed, Joe, Yuri) run on it.

## What shipped (2026-07-23)

**The recoil pipeline is now a closed-loop, self-contained, parameterized system.**
- **4 composable skills** (`.claude/skills/recoil-{new,prep,close,ship}`) over one SSOT-per-counterpart
  JSON; `scripts/recoil` (zero-dep bash wrapper, needs only python3) renders; `--format html` +
  per-audience password gate + `meta.doc_title`.
- **6-tab war-room parameterized** as `runtime/recoil/templates/war-room-6tab.template.json`
  (Pre-Call/Ex-Ante/Forge/Recoil/War Game/Defensibility; self-documenting `_METHOD` + per-block `_doc`).
  New generic blocks: `receipt`, `keyvalue`, `table`; tabbed layout with empty-tab auto-hide.
- **Yuri Kleban / Google** (warm first call, Jul 23 1pm EST) — first live run of the skills. `yuri-war`
  (pw `sextant`) + `yuri-ext` "Intel Brief" (pw `yuri`): parallel-tracking capability seed with the
  handoff-tax, the north star (each datapoint sharpens not blurs), serialization-in-a-continuous-vector-
  space, notetaker-injection immunity, a hyperstition champion-kit, and an "answered before you ask"
  deal-breaker band (LLM-agnostic / runs-on-Gemini-via-gateway is the key lever). See
  [[project_yuri_kleban_google]].
- **Memories:** [[active-listening-over-magical-thinking]], [[project_yuri_kleban_google]] added.
  Ahmed + Joe engagements from earlier this session remain (Ahmed Gmail draft unsent; Joe joe-war/joe-ext).

## Open / next

1. **Yuri:** post-call, `/recoil-close` on `2026-07-23-kleban.json` (score the ex-ante); share the Intel
   Brief only if he pulled. Do not over-pursue (he said "nothing to sell").
2. **Ahmed:** Gmail draft still unsent (his call, set pilot price first).
3. **Joe:** joe-ext ready if wanted; joe-war internal-only.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → check for post-call follow-through on Yuri/Ahmed/Joe. The recoil skills are the
reusable path for any new counterpart: `/recoil-new` → `/recoil-prep` → [call] → `/recoil-close` → `/recoil-ship`.

---

# Handoff — v3.18.0 (2026-07-24)

> **For Claude Code:** active pickup point. This was a security/IP-hardening session, not a
> counterpart engagement. Full detail in the three new memories linked below.

## What shipped (2026-07-24) — IP-leak hardening, all merged to main (PRs #128, #129)

**The problem:** everything in `public/` was world-readable by filename on every arcs.care
host (verified live: `www.arcs.care/yuri-war.html` → 200 with full internal content). The JS
password gates were theater (pw in plaintext source).

- **9 internal docs moved out of `public/`** → `runtime/warroom/`, served by the new
  admin-gated `src/app/warroom/[slug]/route.ts` (Auth.js session + `ADMIN_EMAILS`, fail-closed,
  404-not-redirect to unauth). Host rewrites in `next.config.ts` repointed;
  `outputFileTracingIncludes` ships the files. (yuri-war, joe-war, ahmed, danny, ayesha,
  jalaja, labella, peter, kelly-interview). CISO-reviewed: mechanism PASS.
- **Repo flipped PRIVATE** — closed the raw.githubusercontent.com exposure that app gating
  can't touch. See [[arcs-v9-repo-now-private-status-links-broken]].
- **Preview deployments SSO-gated** (were public to anyone with the URL).
- **Analytics coverage:** was live but 21 counterpart pages shipped uninstrumented. All 34
  public pages now carry the WA snippet + an inlined section-dwell tracker (page_dwell +
  top-5 section_dwell custom events); `recoil_brief.py` + call-brief template emit both;
  J24 `leak_check.sh` now hard-fails any public page missing analytics. Identity = subdomain.
- **Generator provenance leak fixed:** `generated by recoil_brief.py` comment is now
  internal-audience-only + stripped from ext pages + gated in leak_check.sh.
- **Deploy-waste fixed:** stale `arcs` Vercel project unlinked (was building every push, 0
  domains); ignored-build-step skips docs-only commits; Vercel Agent auto-code-review toggled
  OFF (the credit burn). See [[vercel-deploy-efficiency-rules]], [[vercel-config-via-cli-token-rest-api]].

## Open / next

1. **Showcase mirror** for status.arcs.care — its commit links now 404 (repo private).
   Needs Zach's curation call on what code becomes public. Parked.
2. **"Investigate Anomalies Automatically"** still ON in Vercel Team Settings → Agent (same
   on-demand billing as code review); toggle if zero-surprise Agent spend is wanted.
3. Counterpart passwords are decorative now (identity-gated) but sit in git history — treat
   as disclosed; rotate meaning to zero.
4. Prior open items untouched: Todd Hotes post-Wednesday; ledger-management + authenticated
   `/recoil` index; Yuri/Ahmed/Joe post-call follow-through.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memories: [[static-public-files-worldreadable-client-gates-theater]],
[[arcs-v9-repo-now-private-status-links-broken]], [[vercel-config-via-cli-token-rest-api]].

---

# Handoff — v3.23.0 (2026-08-01)

> **Primary pickup is NOT this repo** — the session's build lives in `~/arcs-mini`
> (private, `flashesofbrilliance/arcs-mini`). Start at **`~/arcs-mini/HANDOFF.md`**.

## What shipped (2026-08-01)
Built the **arcs-mini estate**: 4 live surfaces — tripwire · meeting-vector · grader ·
corpus.arcs.care (all HTTP 200), each 3 faces (UI/REST/MCP) on a shared receipt spine.
**Zero-trust BYO corpus** (`storeFor(req)`, no key custody), **Kairos + wave-spotter + Atlas**,
and `@arcs/kit` PLG trio (built, unwired). Deployed via Vercel Hobby (free; concurrentBuilds:1 →
deploy sequentially).

**arcs-v9 canon this session** (branch `claude/elastic-rubin-f22a6e`, HEAD `3515757`):
ADR-039 (refusal-to-overclaim IS the product), DEWY receipt `2026-08-01-brand-promise-dewy.json`,
Tao **cellar** (3 RC-grade candidates awaiting front-of-house lock), `scripts/serialize_grade.py`
+ delaney forkgrade ledger (adversarially audited).

## Open / next (see arcs-mini/HANDOFF.md for JIT tasks)
1. Wire `PlgFooter` into the 4 surfaces (batched, sequential deploy).
2. Build the **B2B/Vault sister app** — circle-of-trust + multisig + KYC/KYB/KYT/KYR, regtech
   WORM/10yr durability bar. Hedge: B2C short + B2B long, one substrate.

## Waiting on Zach
Stripe link (`NEXT_PUBLIC_STRIPE_LINK` → $99 live) · Fri **2026-08-07** omakase re-check
(cloud routine `trig_01HXQpweUrnFNxMeUvzifPT8`) · lock the 3 Tao verses to front-of-house.

## Blocking
NONE.

## Next session starts at
`~/arcs-mini/HANDOFF.md` (JIT anchor). New memories: build-reusable-decomposable-interoperable-default,
brand-promise-refusal-to-overclaim, hedged-parallel-path-b2c-b2b, plan-generalize-omakase-site.
