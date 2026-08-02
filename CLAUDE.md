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

# Handoff — v3.19.0 (2026-07-31)

> **For Claude Code:** active pickup point. Louisville Brands engagement universe shipped end to
> end this session (pitch suite + persistence + security + recoil + skill), then gauntlet-hardened.

## What shipped (2026-07-31)

**Louisville Brands (Justin Delaney / Stanley / Jeben) — the full three-surface universe.**

- **`louisville.arcs.care`** — target-tuned pitch suite, one file (`public/louisville.html`,
  7 inlined subpages): 4 two-sided cards w/ segmented side-toggle, The Offer as 4th card,
  Test→Pilot→Scale (scoped pricing, no fixed dollar figures), foil-seal CTAs, kanji top-right,
  global PRESENT mode (fullscreen, arrows/Enter, `~` eggs, up/down side-toggle), 1.25x screen-share
  scale, ultrawide fixes, Vercel Analytics + section-dwell. Builder lives in session scratchpad.
- **Phase 2 persistence:** `SessionReceipt` (Prisma + Supabase, RLS enabled, tenant-pinned
  `louisville_app` role, tenant=jeben/brand=louisvillebrands), hardened
  `/api/louisville/receipts` (Zod, 32KB body cap, 100-row session cap, IP throttle, lineage
  check), auth-gated `/api/louisville/agenda`. Proven live end to end.
- **RUIN leak closed (the big one):** `www.arcs.care/jeben.html` was 200 to anyone behind
  client-side pw theater — full thread book incl. plant closing, ~20 jobs, third-party
  financials, candid Jeben-on-Justin reads. Moved to `runtime/warroom/` (admin-gated
  `/warroom/[slug]`), verified 404 live. Omakase appendix (15 files) same. Open cellar no
  longer names what is withheld. `leak_check.sh` + client-gate-theater + redaction-disclosure
  regression gates. `RECOIL_PASSWORD` cookie gate removed; all recoil gates fail-closed.
- **Recoil on the Jul 31 Justin/Jeben call:** SSOT `runtime/recoil/generated/2026-07-31-delaney.json`
  (load-bearing quote, 7-step call walk, kairos memory bookmarks, kinematic manifold) +
  `scripts/gen_recoil_artifact.py` renderer + **ADR-038** (bookmark peak/park/probe primitive,
  RC-PROPOSED). Socialize artifact (Justin/Jeben/Stanley blended register) in scratchpad.
- **Pipeline codified:** `.claude/skills/omakase-pipeline/SKILL.md` — jeben (back of house) →
  omakase (cellar) → louisville (front of house) lifted instance→class: 3 surfaces × 3 dials,
  5 lossless invariants (honestly labeled grep-backstop vs mechanical), 6-operator cutting crew,
  7-step pipeline, anti-goals.
- **Hardening:** two full multi-agent gauntlets + lens gauntlet applied; inline Funhouse pass
  (dead cellar links → locked labels; skill "mechanically" overclaim corrected, `7df645a`);
  fanned multi-agent Funhouse launched once spend limit lifted (end of session).

## Open / next

1. **Funhouse survivors** (if any) from run `wf_2b23bfca-d19` → apply, commit, deploy.
2. **justin-war SSOT** (6-tab war-room loop for Justin) — pattern exists, not instantiated.
3. **justin-ext sanitized recoil twin** — decided, not built. ADR-038 renderer on gated
   `/recoil/[id]` page — bookmarks/manifold in JSON + artifact, not on the page.
4. Pre-call brief/ex-ante for Justin deferred by Zach ("separate project, after the call").
5. Prior open items untouched: Todd Hotes Zapier (blocked on Tidio plan), showcase mirror,
   Yuri/Ahmed follow-through.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → check Funhouse workflow results first; then justin-war SSOT or the ADR-038
renderer are the build-ready items.

---

# Handoff — v3.20.0 (2026-08-01)

> **For Claude Code:** active pickup point. Louisville build is DONE and the email is SENT.
> Default posture now is STOP, not continue. Read [[deploy-antipattern-grep-verified-ui]].

## What shipped (2026-08-01) — Louisville universe complete + follow-up sent

Full three-surface family, self-hosted on arcs.care (main @ `47b5700`):
- **L1** louisville.arcs.care (pitch suite) → **L2** /omakase (the evening, 9 courses) →
  **L3** /omakase/atom ("The Seed, Told Whole", 7 chapters). Host-agnostic rewrites; also
  omakase.arcs.care. Navigable both directions; leak_check orphan-gate enforces it.
- Tea house: 序 foreword (acknowledgement, not thank-you), Justin's milled live receipt +
  JSON download, seal-before-October CTA. Scroll+arrows (present mode removed).
- Evening: tea offered after dessert (the one open door), receipt in the take-home box.
- Suite eggs distilled to 🧧 + 🧾. Broker figures milled; canon-manifest pulled off public
  (RUIN leak, earlier commit); seed sentence consonant across surfaces.
- **Email SENT** to Justin, subject "One evening" (Zach edited a variant + sent). Deep-listen
  golden thread = "Lonely Mouth Social Club" P.S. (kuchisabishii). **Justin accepted the
  LinkedIn invite within minutes.**

`leak_check.sh` now carries ~13 gates, each a scar from a real incident this session
(withholding-vocab, decoded-payload, dead-anchor, orphan, seed-sentence, etc.).

## Open / next

1. **Louisville: let it breathe.** No follow-up assigned. If Justin replies / proposes a time,
   /recoil-close the ex-ante at the session. Do NOT pursue or self-assign polish.
2. Prior untouched: Todd Hotes Zapier (blocked on Tidio plan), Ahmed ext send, showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memory: [[deploy-antipattern-grep-verified-ui]] (screenshot
before push; stop when done; don't build verification machinery for what one look answers).

---

# Handoff — v3.21.0 (2026-08-01)

> **For Claude Code:** active pickup point. This was a STRATEGY session (positioning + one recoil
> report), not product code. On branch `claude/decision-geometry-logo-81fb56`, not main — the one
> commit + this handoff ride into main on merge. Default posture: STOP (Shannon is a do-not-pursue).
> **Housekeeping debt:** CLAUDE.md now carries 6 live handoff blocks (v3.16–v3.21); policy is 1–2,
> so next session should relocate v3.16–v3.19 into `_ARCHIVE/handoffs.md` (deferred this session to
> keep the edit low-risk).

## What happened (2026-08-01) — positioning crystallized + Shannon recoil

**A Logo-origin question turned into a coherent GTM spine, then got field-tested by a real call.**

- **Positioning (3 auto-memories banked, in `~/.claude/projects/.../memory/`):**
  - [[arcs-logo-lineage-positioning]] — decision-geometry frame may seed from learning Logo (turtle
    = navigator node on the manifold). "ARCS — Logo for the AI Era" = the *recognition* line;
    "you learn the terrain by moving through it and leaving a trace" = the *public promise*. Widened
    to the whole legible-machine era (Oregon Trail / Pong / HyperCard / BASIC / TI-99 / Apple //e) —
    nostalgia is the *aesthetic*, legibility-restored is the *substance*. Graded with a skeptic's
    caveat (could be an Orthogonal-Echo retrofit, not a true seed).
  - [[icp-is-a-state-not-a-segment-catch-in-caught-breath]] — the ICP is a STATE, not a demographic:
    same high-agency person is unreachable in-the-fire (horizon=0, files you as "vendor") vs
    receptive in caught-breath. In acute survival mode **remove one unit of noise, don't add
    horizon**. Catching the window is a **Kairos problem** — the unbuilt ARCS primitive.
  - ICP framing: high-agency, 20+yr (often corporate) careers, golden-handcuff/calendar-vice-grip,
    seeking a self-sovereignty escape hatch; early-adopters for whom Logo is a felt memory. Small-
    batch specificity is the moat, not a limit. (Corrects an earlier wrong "audience decay" flag.)

- **Shannon recoil** — ran `/recoil-report` on the Jul 31 10:30 AM "Shannon x Zach // Catch up"
  Granola call (Shannon = product lead at Usersnap; known Zach from the BlaBlaCar/Blake era).
  Committed `runtime/recoil/generated/2026-07-31-shannon.json` (`b6cc871`). **YELLOW/DEGRADED, NCI
  60**: clean soft-no, timing miss not fit miss. She recited every ICP symptom then said she has
  zero bandwidth ("I don't have time to pilot") — the grounding case for the ICP-state memory.
  Stopped before Gamma draft / Vercel deploy / email per cost (Zach chose "stop here").

- **Memory hygiene:** compacted the auto-memory index (verbose entries → one line each; was near
  its read limit), flagged LaBella + AssemblyAI projects **dormant** (dates passed, silent weeks).

## Open / next

1. **Shannon: do NOT pursue.** Active-listening alarm — she stated a disqualifying fact. Only move
   is her one bounded offer: post something substantive on LinkedIn so she can repost. Re-approach
   ~September when her horizon reopens, leading with a load-removing hook, not the ARCS architecture.
2. **The deep thread:** catching the caught-breath window is a Kairos/timing detection problem =
   the same engine the compass needs. Product implication, not just positioning. Sit with it.
3. **Housekeeping:** relocate v3.16–v3.19 handoff blocks to `_ARCHIVE/handoffs.md`.
4. Prior untouched: Todd Hotes Zapier (blocked on Tidio plan), Ahmed ext send, showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. Load-bearing new memories: [[arcs-logo-lineage-positioning]],
[[icp-is-a-state-not-a-segment-catch-in-caught-breath]].

---

# Handoff — v3.22.0 (2026-08-01)

> **For Claude Code:** active pickup point. A single marathon thread that ran from a Logo-origin
> question all the way to a formalized brand system + a compounding proverb engine. On branch
> `claude/decision-geometry-logo-81fb56` (not main); everything rides in on merge. All ADRs
> **RC-PROPOSED** (need Zach's ACCEPT). **Housekeeping debt persists:** CLAUDE.md now carries 7 live
> handoff blocks (v3.16–v3.22); policy is 1–2. Relocate v3.16–v3.20 to `_ARCHIVE/handoffs.md` next
> session (deferred here to keep the edit low-risk).

## What shipped (2026-08-01) — the ARCS "house" architecture + brand, one thread

A conversation that started at "did learning Logo seed the decision-geometry frame?" became a full
coherent architecture. All committed (`3c8bee5` → `fdc1fcf`).

- **Build spine (instance→class):** **ADR-039** (instance→class self-promotion as the preferred
  build loop) + **`tool-forge`** skill (micro: one CLI) → **`tools/recoil-report/`** (the first
  self-contained CLI cast: deps/args/passthrough/schema/README) → **`forge-kit`** skill (macro: the
  4-station engagement construction — food/experience/tuned-explanation/gift — with an intake
  front-door and a fish-finder mode classifier: deep-sea / fly / spear).
- **The decision amplifier:** **ADR-040** (Kairos detector / attractor-basin **condenser** + **blower**
  = a decision amplifier; **recoil** is the middle: gain-stage + resistor + circuit-breaker for global
  serializability; Tesla-discharge at peak conversion potential; recipe→receipt bridge; control rods =
  overfit multi-stream guard + gain-staging + custody). Grounds the recurring "unbuilt Kairos
  primitive." Rich; **due a considered molt-pass once its concrete cures** (it accreted 5 metaphor
  layers).
- **Honesty + growth:** **ADR-041** (atomic **GAAP/non-GAAP** belief reconciliation: tilde=label,
  custody=reconcile, gain-staging=prominence; the **considered molt**: strip formwork after the
  concrete sets, considered not generic; **recapitulate = deep-KAIROS scan/audit/distill**; and the
  **5×5 proverb grid** — aspects **D/R/W/C/H** × verbs **Analyze/Assess/Evaluate/Synthesize/
  Recapitulate**, anti-padding = tilde empty cells).
- **Brand formalized (via `/impeccable`):** **DESIGN.md** + **.impeccable/design.json** — North Star
  **"Render Through the Fog"**, the mark documented as **the tilde extruded → Möbius/fog/horizon**,
  named rules (Semantic Color · One Voice · Glow-Not-Shadow · Three-Voice · Graded-Legend), the
  render-scale as the signature. (PRODUCT.md already existed; DESIGN.md was the missing half.)
- **The oral history + its engine:** **the Tao of ARCS** front-of-house (`_ARTIFACTS/arcs-tao.html`,
  32 verses, public-safe) → **`tao-mint`** skill + **`runtime/tao/proverbs.json`** SSOT (compounding,
  custody-tagged, net-new dedup, feeds visual engineering) → **first mint: 25 net-new ADR-040
  proverbs** (full grid, no padding). SSOT now 40 proverbs.
- **~7 auto-memories** added/edited: [[arcs-logo-lineage-positioning]], [[icp-is-a-state-not-a-segment-catch-in-caught-breath]],
  [[reflexiveness-is-prepaid-prep-as-enrichment]], [[arcs-core-function-opportunity-sizing-prep-shaping]],
  [[arcs-logo-mobius-horizon-mark]] (Möbius = tilde extruded; ARCS = instrument/vessel/substrate),
  [[arcs-product-architecture-not-a-fork]] (Mañana's logo IS the tilde; tomorrow = non-GAAP).

## Open / next

1. **Phase 2 brand→marketing:** render the 40 proverbs into S-tier visual cards through the
   DESIGN.md grammar (first real visual-engineering artifact). Then Phase 3 (motion/video via
   Figma/Canva export + content marketing off the codex; honest video-production limits flagged).
2. **Mint the remaining ADR grids:** `/tao-mint ADR-039` (rich, full grid), `ADR-041` (will honestly
   come back partial — silent on Horizon — proving the anti-padding rule).
3. **Ratify** ADR-039/040/041 (RC-PROPOSED → ACCEPT, the two-way door at dawn).
4. **ADR-040 considered molt-pass** once its concrete cures. Optional: wire a `tao-mint` hook on new
   `_DECISIONS/ADR-*.md`.
5. Prior untouched: Shannon do-not-pursue (LinkedIn repost only); Todd Zapier (Tidio plan); Ahmed
   ext send; showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memories: [[reflexiveness-is-prepaid-prep-as-enrichment]],
[[arcs-core-function-opportunity-sizing-prep-shaping]], [[arcs-logo-mobius-horizon-mark]]. New skills:
`forge-kit`, `tao-mint`, `tool-forge`. New docs: DESIGN.md, ADR-039/040/041.

---

# Handoff — v3.23.0 (2026-08-01, Saturday PM)

> **For Claude Code:** active pickup point. Same marathon thread, afternoon/evening: the Tao became
> a full deployed visual family + a complete oral history + a product plan. Branch
> `claude/decision-geometry-logo-81fb56`. **Housekeeping debt persists** (8 live handoff blocks
> v3.16–v3.23; policy 1–2). Relocate v3.16–v3.20 to `_ARCHIVE/handoffs.md` next session.

## What shipped (2026-08-01 PM) — the Tao, visualized, deployed, and planned

- **Oral history completed:** back-propagated proverbs to **ALL ADRs 001–038** via 7 parallel
  agents (+165, anti-padding honored — thin infra ADRs minted 1–2, rich governance filled grids).
  **SSOT `runtime/tao/proverbs.json` now 241 proverbs**, all custody-tagged, no em-dashes, unique.
- **4 visual surfaces, SSOT-generated (the microservices):** `scripts/gen_tao_views.py`,
  `gen_tao_corpus.py`, `gen_tao_alchemist.py` → **Amplifier grid** (one ADR, 5×5), **Views of the
  Corpus** (Hokusai + ma: 40 grid-faces, density = weight, empty cells = intentional negative
  space), **The Tao entire** (browsable 241, filter by aspect/verb/source), **The Alchemist**
  (drag-drop reaction chamber; resonance vs transmutation; deep synthesis honestly `~`-stubbed as
  the offstage enricher). Plus verse cards (accent moved left→top per Zach). All in `_ARTIFACTS/`.
- **All 4 deployed** as private Claude Artifacts: Amplifier `5e505614`, Views `93f9a41c`, Corpus
  `170b3ed3`, Alchemist `2e97f776`.
- **North-star seed banked:** [[tao-as-object-level-taxonomy-of-problem-space]] — the Tao (D/R/W/C/H
  × verbs) as a coordinate system for a problem's field-shape; tag an artifact by its cells, the
  cell's proverbs are the lenses. The bridge from wisdom-corpus to product. Graded a SEED, kept an
  open folksonomy (orphans = net-new aspects).
- **Implementation plan:** `_STATE/tao-implementation-plan-v1.md` — 3 phases (in-app `/tao` routes ·
  live `POST /api/alchemist` enricher · taxonomy bridge). **DEFERRED to reserve budget for Todd.**
  Spec = the shipped artifacts (a port, not a redesign).

## Open / next

1. **Todd/PRL — the next sitting (separate).** Zapier lead delivery is blocked on the Tidio plan
   upgrade (paid webhooks); verify the plan was upgraded before sinking time. Master state:
   `runtime/recoil/generated/2026-07-30-todd-MASTER-HANDOFF.md`.
2. **Tao is parked**, fully spec'd by the plan. When resumed, Phase 2 (live Alchemist API) is the
   high-value piece.
3. **Ratify** ADR-039/040/041 (RC-PROPOSED). Validate the taxonomy seed on real artifacts.
4. Housekeeping: relocate v3.16–v3.20 handoffs to `_ARCHIVE/handoffs.md`.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memory: [[tao-as-object-level-taxonomy-of-problem-space]].
New generators: `scripts/gen_tao_{views,corpus,alchemist}.py`. Plan: `_STATE/tao-implementation-plan-v1.md`.

---

# Handoff — v3.24.0 (2026-08-01, Sat night)

> **For Claude Code:** active pickup point. This was a **philosophy → product → purpose marathon**,
> banked almost entirely into **user-level auto-memory** (`~/.claude/projects/-Users-zharris-arcs-v9/memory/`,
> NOT repo-visible from a cloud session). Two small repo commits + one in-chat design prompt. Branch
> `claude/decision-geometry-logo-81fb56`. **Housekeeping debt persists** (now 9 handoff blocks
> v3.16–v3.24; policy 1–2 — relocate v3.16–v3.20 to `_ARCHIVE/handoffs.md` next session).

## What happened (2026-08-01 PM/night) — the spine of the whole thing

A Logo-origin question ("did the turtle seed the decision-geometry frame?") unspooled into a coherent
**philosophy → product → purpose spine**, banked across ~9 auto-memories. The three pillars:

- **Design north-star — [[met-at-your-level-onramp-design-principle]]:** *met at your level → suspend
  disbelief → transported by your own interactivity → flow.* Doorway not tutorial; never render above
  altitude; sensor-suite (lidar/radar/sonar = match modality to fog); *sine ira et studio* + non-dual
  (verdict dropped, gravity kept); firm-footing-in-fog; rock-balancing/cairn; boat-sail-compass-wind
  harbor-to-harbor. **The TELOS: reflect the geometry, "say it without saying it."** Apophatic def =
  *helps shape without saying / being / pushing / pulling.* Symbol lineage **~ → Mañana → Ark → ARCS**
  (`~` not `=`). Universal span: pre-K ↔ wise luddite elder (accessibility == inheritability).
- **Architecture/moat — [[context-manifold-as-model-agnostic-attractor-basin]]:** the manifold is an
  **authored (not learned) state space** = a model-agnostic attractor basin; any predictor (LLM/JEPA)
  plugs in. **Falsifiability is the invariant fulcrum for both FMs** (failure-modes FP/FN *and*
  foundation-models). Self-correcting gospel = **custody not clergy** (secular-monk/annalist role);
  Tao-vs-Tetragrammaton fork (authorless-by-truth vs by-holiness); Ark = **recovered-not-invented**,
  vessel-not-reliquary; net-new is **DEEMED not CLAIMED** via a Librarian/Alchemist/Skeptic/Loki
  judging panel (a buildable `tao-mint` gate). A decision is a **point**; horizon + orientation
  promote it to a **vector**.
- **Purpose (the WHY under it all) — [[arcs-purpose-inherit-tacit-wisdom-first-author-not-last]]:**
  make tacit wisdom portable so it's **inherited**; Zach = **first author, not last**; the son picks up
  the pen at the page left off, after death. **Unify the 3 severed legacies** (digital/physical/
  generational) into one openable custody-welded vessel **by subtraction** (bonsai of a life), not a
  sealed archive. **Knowledge work = a compounding CRAFT, not a commodity** (AI commoditizes the typing,
  not the taste). Concrete vault feature: the **opportunity-cost investment bank** (bank the tuition;
  reweight on process not outcome; opportunity cost is `~` not `=`; heir gets the calibration + the
  right to re-weigh it). Keystone image: *"the turtle, like the redwood, is still walking far after I am
  not."*

## What shipped to the repo (small; the heavy work was memory)

- `3a80376` — **meta-audit** `_PATTERNS/2026-08-01-nonlinear-thread-meta-audit.md` (why deductive
  taxonomies can't hold a live synthesis thread) + minted the **"white water" proverb** to the Tao SSOT
  (`field-2026-08-01-R-assess`, corpus now **242**).
- `7e56a7b` — **Views of the Corpus upgrade:** every cell (lit + empty) reveals its state-space
  coordinate on hover/focus; lit = the proverb, empty = its *ma* ("intentionally silent"); styled
  tooltip + full **keyboard walk** (Tab + arrows across faces). `scripts/gen_tao_views.py`. Verified
  local (DOM + computed styles), **no deploy** (JIT loop).

## Delivered in-chat, not filed

A ready-to-paste **Claude-design prompt** for a 60–75s **product-marketing video** of the three-planes /
legacy-vault (fog→sharp "snap into focus", brand grammar, no-narration telos). It's in this session's
transcript. Build a storyboard/Gamma from it only on Zach's go (budget-gated for the Todd week).

## Open / next

1. **Cost-leak fix** (separate session): version the Vercel build-skip as `vercel.json` `ignoreCommand`
   (PATH-based, NOT `[NCI:SKIP]`) + a tripwire.
2. **Todd/PRL** — Zapier lead delivery blocked on the Tidio plan upgrade (verify before sinking time).
3. **New build-ready from tonight:** the **legacy-vault + opportunity-cost investment bank** (Outcome
   handler + recoil loop + portfolio/risk view over receipt history). And the marketing video (prompt
   in transcript).
4. Tao hosting at `tao.arcs.care` via the JIT loop; ratify ADR-039/040/041.
5. Housekeeping: relocate v3.16–v3.20 handoffs to `_ARCHIVE/handoffs.md`. Two auto-memories are large
   (`context-manifold-basin` ~22KB, `met-at-your-level` ~20KB) — split if they near the 24.4KB read cap.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memories: [[met-at-your-level-onramp-design-principle]],
[[context-manifold-as-model-agnostic-attractor-basin]], [[arcs-purpose-inherit-tacit-wisdom-first-author-not-last]],
[[fight-or-flight-inverts-signal-noise-classifier]], [[arcs-assumes-stateful-human-memory-needs-rewarming]].
