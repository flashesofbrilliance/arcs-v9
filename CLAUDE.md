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

# Handoff — v3.38.0 (2026-08-18)

> **Active pickup point.** The self-cataloging arc, end to end in one thread:
> inchworm → catalog → atlas → dolls → doctrine. The corpus now indexes itself,
> renders itself, polices itself, and travels.

## Headline: the memory corpus became a self-cataloging, navigable, portable system — and canonized how it stores itself

- **Self-cataloging index** — `scripts/memory_index_sync.py` (session-start hook, `--append`):
  orphan memory files auto-catalog into an "Uncurated (auto)" band rendered from their own
  frontmatter `description` (the SSOT inversion). Fixed the old inline check's regex bug
  (dotted filenames false-positived ORPHAN forever). Dead links + byte budget stay
  receipt-only. Index consolidated 20.9→17.4KB, 0 dropped, 0 dead links.
- **Catalog emitter** — `scripts/memory_catalog_emit.py`: mechanical, declared-edges-only
  backfill (183 nodes, 590 `[[wiki-link]]` edges, 22 dangling counted honestly).
- **Terrain Atlas** — `_ARTIFACTS/terrain-atlas.html`: 2.5D ziggurat where **stratum = echo
  weight** (base uncited → apex canon 10+), fog = staleness, district = azimuth; arrow-key
  traversal climbs the strongest declared edge; full camera (orbit/tilt/track, presets);
  per-node **russian-doll nested-ticket export** (cycles = `@ref`, never invented hierarchy).
  The apex self-identified: `cut-not-add-provable-architecture`, cited ×21.
- **Dolls (User0 → UserN+1)** — `scripts/doll_export.py` + `doll_sprout.py`: epoch-stamped
  declared-closure bundles, `--bodies` for true tenant bootstrap, **fail-closed air-gap gate**
  (`audience:` absent = internal; external cuts name what they held). Sprout never overwrites;
  the tenant's inchworm self-catalogs. Round-trip tested (96 shells w/ bodies).
- **ADR-065 minted via oracle** (+ **tao-249**, aspect C): corpus = SSOT, storage = induced
  projection, 4 serialization invariants, namespace isolation, **Infra Compass = ROM CANDIDATE**
  ("Induced Projection"; Y-map evidenced by this session's own FORK/PARADOX/DRIFT).
- **Merge reconcile**: 27 commits behind main resolved; three-way v3.35.0 handoff collision
  renumbered honestly (ours → v3.37.0); PII repos (`arcs-memory-pipeline`, `arcs-career-fit`)
  **re-privatized** per their own "pending review" descriptions (a live PARADOX, closed).
  30-day sweep ran; gauntlet-sampling-engine + dollar-compression minted to memory.
- **The system ratified itself**: the pre-push tripwire rejected the ADR-065 push because
  build.html still said 59 ADRs — the drift the mint itself created. Fixed the surface
  (never `--no-verify`), pushed clean. The Infra Compass worked before it was built.

## Wisdom receipt (the durable lessons, distilled)

1. **Invert the index**: when a file's frontmatter IS the SSOT for its index line, cataloging
   becomes mechanical and new knowledge can never silently fall out of the index.
2. **Declared-only edges are the honesty floor for provenance**: absent ancestry stays absent;
   a guessed edge is the propaganda version of lineage. (Held everywhere: catalog, atlas,
   tickets, dolls, ADR-065 invariant 3.)
3. **The NOTOMATION split scales every inchworm**: mechanical countables automate
   (append, emit, count); judgment (curation, canon, RED response) stays human. The same
   cut worked for the index, the seedbank, the snapshot, and the compass design.
4. **Let the data make the shape**: the ziggurat's pyramid wasn't designed — it emerged from
   the citation distribution, and its apex independently surfaced the corpus's own governing
   goal (`cut-not-add`, ×21). Render the structure; don't impose it.
5. **Fail closed at every boundary**: `audience:` absent = internal; PARADOX resolves to the
   restrictive assertion + a receipt (the ROM RC). The air-gap gate refused 100% on first
   run — that's the gate working, not failing.
6. **Dollar compression in practice**: ~350 lines of stdlib authored once, zero LLM in any
   runtime path — export/sprout/emit/check run free forever.
7. **A gate that catches its own minting commit is the proof the gate is real** (tripwire vs
   ADR-065's own drift).

## Next / open flags
- Roll `audience:` frontmatter onto any memory that would ever be cut externally (gate is
  fail-closed until then — correct but total).
- pg/pgvector migration (**ask-first** per ADR-065); `--emit-sql` on the emitter is the seam.
- ROM ratification of "Induced Projection" when earned; Infra Compass L1–L5 synthesis unbuilt.
- Origin-session / cross-session echo enrichment (`Activation` rows) — designed, not built.
- lattice-drift still fires (ADR count 57 vs 60; epoch stale) — regenerate is human-owned.
- Sweep leftovers unminted: CWO pattern, status-URL gotcha, F33 panel-as-plan-breaker,
  family token-SSOT, marketplace-as-channel, release runbook.
- **Apex Spine → Alexandria**: `_ARTIFACTS/apex-spine.html` (the S4 canon stratum as a print
  spine, 14 vertebrae) is a candidate resident for the **center reading room of the Library
  of Alexandria** performer (`_ARTIFACTS/arcs-alexandria.html`) — the corpus's load-bearing
  canon displayed at the library's heart. Placement idea, not yet integrated.

## Blocking
NONE this track. (PRL remains blocked on Todd — see snapshot `blocking_v3350_prl`.)

## Deploy note
All work pushed to `claude/plugin-marketplace-arcs-skills-9622bd` (head `b12349f` pre-handoff);
one public-surface content change (build.html ADR stat 59→60) rode the tripwire-gated push.
No product deploy. Comet application: SENT (see v3.37.0).

---

> _v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
