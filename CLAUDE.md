@AGENTS.md
@WORLD.md

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
- Inline styles only — no CSS files, no Tailwind, no className.
- No new dependencies without asking.

# Handoff — v0.1.0 (2026-05-26)

> **For Claude Code:** this section is your pickup point. Read in order below.

## Orientation chain
1. `MEMORY.md` — versioned context log; what happened before you arrived
2. `SKILL.md` — your contract: what you can do, what you must not do, priority queue
3. `WORLD.md` — physics spec; governing law (already referenced above)
4. `AGENTS.md` — agents/workers map, DEWY pipeline, Y-gate states

## Open sprint (Issue #1 — P0 Backlog Sprint 1)
All four sub-issues are unblocked and ready to start. Dependency order:

```
#2 DEWY Receipt Schema
  └─ #3 Time ROM (embed into #2)
       └─ #4 Compass → DEWY flow
            └─ #5 Book II Canon chapter
```

## File targets to create
```
runtime/specs/dewy-receipt-schema-v1.md     ← Issue #2
runtime/specs/dewy_receipt.schema.json      ← Issue #2 (machine-readable companion)
runtime/specs/time-quality-attribution-rom.json ← Issue #3
runtime/flows/question-compass-to-dewy.md   ← Issue #4
canon/book-ii-time-firmware-modes.md        ← Issue #5
```

## Versioning policy (enforced)
- `MEMORY.md` — append-only; new entries at top; never delete prior versions
- `SKILL.md` — update in place; increment version header; keep changelog
- `CLAUDE.md` — append new `## Handoff — vX.Y.Z` sections only; never overwrite
- Spec files — use front-matter `version` field; `*-v2.md` only on breaking schema change
- Python scripts — never overwrite; create `*_v2.py` for breaking changes

## Last confirmed commit
`e66d4de` — 2026-05-26 16:15 — `arcs_cli.py` 5-verb pipeline + apex spine DEWY receipt [NCI:81]

---

# Handoff — v0.2.0 (2026-05-26)

> **For Claude Code:** this is the active handoff. v0.1.0 above is preserved for history. Read from here.

## What changed since v0.1.0

- `arcs-field-os/specs/orient-prd.md` v0.1.0 is now live — **Kairos Lock active**
  This is the governing authority for Issues #2, #3, #4. Read it before touching any of them.
  URL: https://github.com/flashesofbrilliance/arcs-field-os/blob/main/specs/orient-prd.md

- `arcs-field-os/jtbd/jtbd-master-map.md` v0.1.0 is live — canonical four-surface architecture (Calibrate → Orient → Chart Course → Detect)
  URL: https://github.com/flashesofbrilliance/arcs-field-os/blob/main/jtbd/jtbd-master-map.md

- `arcs-field-os/specs/index.md` is live — spec registry with authoring priority queue
  URL: https://github.com/flashesofbrilliance/arcs-field-os/blob/main/specs/index.md

- `MEMORY.md`, `SKILL.md` pushed to this repo (arcs-v9) — read before starting

- `runtime/specs/dewy-receipt-schema-v1.json` is now live in this repo
  Machine-readable JSON Schema (Draft 07). Full field coverage from orient-prd.md §3 L5.
  This is the source of truth for the Receipt model. Prisma schema must conform to it.

## Orientation chain (updated)
1. `MEMORY.md` — versioned context log; full audit of what landed and what didn't
2. `SKILL.md` — your contract, priority queue, ROM primitives
3. `WORLD.md` — physics spec; governing law
4. `AGENTS.md` — pipeline map
5. `arcs-field-os/specs/orient-prd.md` — governing authority for Issues #2–4 (**NEW — read this**)

## Open sprint — revised priority queue

```
#2 DEWY Receipt Schema  ← SCHEMA FILE NOW EXISTS (dewy-receipt-schema-v1.json)
   └─ Your job: wire it into Prisma (prisma/schema.prisma) and validate
      the existing Receipt model conforms. If fields are missing or
      mistyped, add a migration. Do NOT rename existing fields.
   └─ Then: write runtime/specs/dewy-receipt-schema-v1.md (human-readable
      companion doc — see orient-prd.md §3 L5 for field descriptions)

  └─ #3 Time Quality Attribution ROM
       Your job: write runtime/specs/time-quality-attribution-rom.json
       Governing spec: orient-prd.md §3 L2 (W-field inference rules)
       and §3 L1 (UNDEFINED W-field HOLD behavior)
       ROM defines: how window inference confidence degrades over time,
       what triggers a W-field HOLD vs. default, and the cadence NCI lens score.

       └─ #4 Compass → DEWY Flow
            Your job: write runtime/flows/question-compass-to-dewy.md
            Governing spec: orient-prd.md §3 L0–L5 full pipeline
            This is a flow doc — trace the full state transformation
            from raw question string → DEWY receipt, with decision points
            and HOLD/REJECT branches annotated.

            └─ #5 Book II Canon — Time Firmware Modes
                 Your job: write canon/book-ii-time-firmware-modes.md
                 Depends on: #3 Time ROM must exist first
                 This is the canonical prose chapter — not a spec, a world document.
                 Tone: WORLD.md register (Myst / Hitchhiker's Guide). Not documentation.
```

## File status (updated)
```
runtime/specs/dewy-receipt-schema-v1.json   ✅ EXISTS — wire into Prisma (Issue #2)
runtime/specs/dewy-receipt-schema-v1.md     🔴 CREATE — human-readable companion (Issue #2)
runtime/specs/time-quality-attribution-rom.json  🔴 CREATE (Issue #3)
runtime/flows/question-compass-to-dewy.md   🔴 CREATE (Issue #4)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — after #3 (Issue #5)
```

## Cross-repo dependency
Both repos must stay in sync. When you push to arcs-v9, check if arcs-field-os needs a corresponding update:
- arcs-v9 Prisma schema changes → may require orient-prd.md amendment (open PR, do not push directly)
- arcs-v9 new ROM files → SKILL.md changelog entry required
- arcs-field-os spec changes → MEMORY.md entry required in arcs-v9

## Versioning policy (unchanged)
- `MEMORY.md` — append-only; new entries at top; never delete prior versions
- `SKILL.md` — update in place; increment version header; keep changelog
- `CLAUDE.md` — append new `## Handoff — vX.Y.Z` sections only; never overwrite prior
- Spec files — version field in front-matter; `*-v2.json` only on breaking schema change
- Python scripts — never overwrite; create `*_v2.py` for breaking changes

## Last confirmed commit (as of this handoff)
`618022004033d72bb56e23420658b6074fe4adeb` — arcs-field-os — Orient PRD v0.1.0, Kairos Lock
`35d32da60cd0a32ef348b8f42554c27a7374199a` — arcs-v9 — MEMORY.md + SKILL.md initial push
`55009d62be52f25281648f9c34be1709f77c3540` — arcs-v9 — CLAUDE.md Handoff v0.1.0 appended

---

# Handoff — v0.3.0 (2026-05-26)

> **For Claude Code:** active pickup point. v0.2.0 above is preserved for history.

## What changed since v0.2.0

- **Issue #2 COMPLETE** — `runtime/specs/dewy-receipt-schema-v1.md` written; `prisma/schema.prisma` Receipt model aligned to JSON schema (15+ canonical DEWY fields added, legacy fields preserved with mapping comments)
- **Issue #3 COMPLETE** — `runtime/specs/time-quality-attribution-rom.json` written; W-field inference rules, DRIFT Sentinel, Kairos Lock, cadence NCI modifiers, macro trigger conditions (LAB/BAR/KKL/ATG) all ROM-pinned
- **Y-gate enum alignment** — `src/lib/ygate.ts` rewritten to canonical polarity×conviction×stability enums; `driftState` and `yGateScore` JSON added; `yState` kept as mirror of `yPolarity` for backward compat
- **UI consumers updated** — dashboard, brief, history pages: stale EPHEMERAL/COLLAPSED/VOLATILE/RED/DRIFT labels replaced with canonical values
- **Slash commands registered** — `/handoff` + `/handoff-pickup` in `.claude/commands/`; `SKILL.md` Domain #7 added
- **Stale root artifacts removed** — 6 scan output files + `arcs@0.1.0` deleted from root
- **`arcs-canon.md` corrected** — Y-gate table aligned to canonical polarity enum

## File status

```
runtime/specs/dewy-receipt-schema-v1.json   ✅ EXISTS (Kairos Locked)
runtime/specs/dewy-receipt-schema-v1.md     ✅ EXISTS
runtime/specs/time-quality-attribution-rom.json  ✅ EXISTS
runtime/flows/question-compass-to-dewy.md   🔴 CREATE — Issue #4 (NEXT, unblocked)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — Issue #5 (blocked on #4)
```

## Open sprint — revised

```
Issue #4 (NEXT)  Compass → DEWY Flow   runtime/flows/question-compass-to-dewy.md
  └─ Issue #5    Book II Canon          canon/book-ii-time-firmware-modes.md
```

## Last confirmed commits (arcs-v9)

```
61095c5 — refactor(ygate): align Y-gate enums to canonical DEWY schema [NCI:82]
22cac6e — chore(skill): register /handoff + /handoff-pickup, update sprint status [NCI:79]
38aa0f6 — feat(spec): Time Quality Attribution ROM v0.1.0 [NCI:84]
```

## Blocking question

NONE — Issue #4 is fully unblocked. Start with `runtime/flows/question-compass-to-dewy.md`.

---

# Handoff — v0.5.0 (2026-05-26)

> **For Claude Code:** active pickup point. v0.4.0 above is preserved for history.

## What changed since v0.4.0

- **Book II Part V drafted** — `_CANON/book-ii/part-v-the-accumulation-protocol.md` (§5.0–§5.7, v0.1.0, DRAFT held). File exists locally, **not yet committed**.
- **Part V content:** The Accumulation Protocol — delta gates, kairos detection, the 5-step accumulation loop (silent/flagged/override modes), drift detection (CLEAR/WATCH/DRIFT), debrief session as first-class session type, boundary section (value drift / scope creep / malformed question).
- **§5.7 Calibrate connection:** Malformed-question failure mode explicitly linked to JTBD D / Calibrate surface / HOLD gate / anticipatory probing from arcs-field-os JTBD architecture.
- **Cross-repo link confirmed:** Part V is architecturally downstream of the Calibrate surface. Canonical JTBD sequence D→A→C→B (Calibrate→Orient→Chart→Detect) documented in `arcs-field-os/jtbd/jtbd-master-map.md`.

## File status

```
_CANON/book-ii/part-v-the-accumulation-protocol.md   🟡 WRITTEN — commit pending
runtime/flows/question-compass-to-dewy.md             ✅ EXISTS (v0.4.0)
runtime/specs/dewy-receipt-schema-v1.md               ✅ EXISTS
runtime/specs/time-quality-attribution-rom.json       ✅ EXISTS
```

## Open sprint — revised

```
Issue #5  Book II Canon — Part V written, needs commit + upstream audit
```

## Immediate next action

```bash
git add _CANON/book-ii/part-v-the-accumulation-protocol.md
git commit -m "feat(canon): Book II Part V — The Accumulation Protocol v0.1.0 [NCI:DRAFT]"
```

Then submit Part V for upstream ARCS audit. When packet returns, translate to section-keyed annotations same as Part IV CONDITIONAL CLEAR.

## Blocking question

NONE.

---

# Handoff — v0.6.0 (2026-05-26)

> **For Claude Code:** active pickup point. v0.5.0 above is preserved for history.

## What changed since v0.5.0

- **Book II Part VI drafted and committed** — `_CANON/book-ii/part-vi-the-shared-court.md` (§6.0–§6.6, v0.1.0, DRAFT held, 6fece14)
- **Part VI architecture decisions locked before drafting:**
  - Witness = receipt annotation only (not a protocol role); two standing roles: Initiator and Respondent
  - Quorum rule = unanimity of being bound (not agreement); refusal → HOLD or Arbitration
  - §6.3 quorum paragraph ratified verbatim before any drafting began
- **Part VI content:** The Shared Court — extends constitutional court to multi-party sessions. New primitives: Initiator/Respondent standing, witnesses annotation, Dissent Record (first-class receipt field), deliberation protocol (3 pipeline modifications at L1/L3/L4), co-signed delta gates, Arbitration Session (3 preconditions, narrow jurisdiction, no retroactive lineage alteration). Three hard boundaries: power asymmetry, bad-faith participation, scope capture.

## File status

```
_CANON/book-ii/part-i-from-firehose-to-compass.md      ✅ CANONICAL
_CANON/book-ii/part-ii-core-rom-axioms.md               ✅ CANONICAL
_CANON/book-ii/part-iii-constitutional-court-agency.md  ✅ CANONICAL
_CANON/book-ii/part-iv-*.md                             ✅ DRAFT held — CONDITIONAL CLEAR pending
_CANON/book-ii/part-v-the-accumulation-protocol.md      ✅ DRAFT held — audit pending (60c048c)
_CANON/book-ii/part-vi-the-shared-court.md              ✅ DRAFT held — audit pending (6fece14)
```

## Audit protocol reminder

Parts V and VI are forward spec only. Weight: CONSISTENCY + CANON_COLLISION > IMPL_GAP.
Same annotation format as Part IV CONDITIONAL CLEAR: section-keyed, sentence-anchored.

## Last confirmed commit (arcs-v9)

`6fece14` — feat(canon): Book II Part VI — The Shared Court v0.1.0 [NCI:DRAFT]

## Blocking question

NONE — submit Parts V and VI for upstream audit.

---

# Handoff — v0.7.0 (2026-05-27)

> **For Claude Code:** active pickup point. v0.6.0 above is preserved for history.

## What changed since v0.6.0

- **Book II Parts V & VI promoted to CANONICAL** — both at v1.0.0, commit `b6e59e4`
- **Upstream audit completed** — 21 findings across Parts V & VI; all must-fix + high-value precision applied at `087ef22`; Architect ratification received same session
- **Key architectural decisions locked:**
  - Constitutional range = governance-configured per-axis intervals grounded in ROM axioms; CLEAR/WATCH/DRIFT are positional categories relative to those intervals, not numeric values in Part V
  - Standing is non-transferable in v1.0.0; absent Respondent → HOLD or rescope
- **Dual-bar-raiser skill wired** — `arcs/.claude/arcs-dual-bar-raiser.md` + `~/.claude/commands/dual-bar-raiser.md`; `/handoff-pickup` now surfaces the two-agent protocol reminder

## File status

```
_CANON/book-ii/part-i-from-firehose-to-compass.md      ✅ CANONICAL
_CANON/book-ii/part-ii-core-rom-axioms.md               ✅ CANONICAL
_CANON/book-ii/part-iii-constitutional-court-agency.md  ✅ CANONICAL
_CANON/book-ii/part-iv-*.md                             ✅ CANONICAL (CONDITIONAL CLEAR applied)
_CANON/book-ii/part-v-the-accumulation-protocol.md      ✅ CANONICAL v1.0.0 (b6e59e4)
_CANON/book-ii/part-vi-the-shared-court.md              ✅ CANONICAL v1.0.0 (b6e59e4)
```

## Open sprint

```
Book II Parts I–VI: CANONICAL — Book II is complete.
Next: decide whether to begin Part VII, start a new Book, or pivot to product work (P4 deploy).
```

## Blocking question

NONE.

---

# Handoff — v0.9.0 (2026-05-27)

> **For Claude Code:** active pickup point. v0.7.0 above is preserved for history.

## What changed since v0.7.0 / v0.8.0

- **Housekeeping committed (04c57cb):**
  - Deleted stale `_CANON/book-ii/part-iv-sessions-api.md`
  - Added `exports/` to `.gitignore`
  - MEMORY.md updated to v0.8.0
- **GitHub Projects board live:** https://github.com/users/flashesofbrilliance/projects/1
  - Stage columns: Not Started → Research → Receipt → Build → Refine → QA → Done
  - All Sprint 1 issues + Book II Part cards backfilled as Done
- **Global slash commands:** `/arcs-handoff` + `/arcs-handoff-pickup` available from any directory

## Current canon state

```
Book II Parts I–VI   ✅ ALL CANONICAL
Sprint 1 (#1–#5)     ✅ COMPLETE
```

## Open sprint

NONE — next sprint unscoped. Candidates: P4 Vercel deploy / Book III / product sprint.

## Last confirmed commit

`04c57cb` — chore(housekeeping)

## Blocking question

NONE.

---

# Handoff — v0.9.1 (2026-05-27)

> **For Claude Code:** active pickup point. v0.9.0 above is preserved for history.

## What changed since v0.9.0

- **ARCS Data Science Suite COMPLETE** — all scripts committed and pushed:
  - `scripts/arcs_core.py` — kernel with DEWY, Folksonomist, `DomainConfig.strand_a_fn` hook, versioned output tree
  - `scripts/calendar_scan.py` — intent-based Strand A, `om_composite_min=130`, 750 real events tested
  - `scripts/listening_scan.py` — listening-domain Strand A, multi-format timestamp parser
  - `scripts/reader_scan.py` — reader-domain Strand A, 12-domain concept taxonomy
  - `scripts/arcs_cli.py` — 5-verb pipeline (scan/assess/cluster/spine/run), apex receipt auto-write
- **Google Calendar restructured via MCP** — 5 recurring anchor blocks live from 2026-06-01:
  - 🔴 Deep Work: Mon–Fri 06:00–09:00 | 🟢 Morning Stack: Daily 05:30–06:00
  - 🟠 Revenue Block: Tue+Thu 10:00–12:00 | 🟡 Weekly Review: Fri 16:00–17:00
  - 🔴 Shutdown Ritual: Mon–Fri 17:30–17:45
- **Calendar audit findings:** 2.3% revenue/external, 0% recurring pre-restructure, peak maker window 06:00–09:00 ET
- **Spotify:** No real data in repo — user must request extended history at spotify.com/account/privacy

## Data science scan state

```
exports/calendar/2026-05-26/   ✅ Real (750 events via MCP)
exports/listening/2026-05-26/  🟡 Synthetic — awaiting Spotify extended export
exports/reader/2026-05-26/     🟡 Synthetic — awaiting Kindle My Clippings.txt
exports/receipts/              ✅ Apex receipt written
```

## Open gaps

```
P4 Vercel deploy     🟡 IN PROGRESS — blocked on Supabase DATABASE_URL + DIRECT_URL + SERVICE_ROLE_KEY
Spotify export       📋 WAITING — request at spotify.com/account/privacy (extended history, up to 30 days)
Kindle clippings     📋 WAITING — USB connect Kindle or check ~/Library for Kindle Mac app
Calendar Phase 2     📋 OPEN — find/rename existing morning routine event (avoid duplicate with 🟢 Morning Stack)
```

## Last confirmed commits (arcs-v9)

`04c57cb` — chore(housekeeping): stale draft deleted, exports/ gitignored
`b0ddeb1` — chore(handoff): session handoff v0.7.0 (pushed this session)

## Blocking question

NONE — pick next sprint: P4 deploy / Spotify+Kindle data / Calendar Phase 2 / new canon.

---

# Handoff — v0.10.0 (2026-05-27)

> **For Claude Code:** active pickup point. v0.9.x above is preserved for history.

## What changed since v0.9.1

- **ADR-001 + ADR-002 reviewed and pushed** — `_DECISIONS/` directory is now live on GitHub (`abe1989`)
  - ADR-001: App-level auth gating (not Supabase RLS) — GREEN/HIGH/STABLE
  - ADR-002: SQLite dev / Supabase prod split — P4 unblock checklist is the authoritative deploy sequence
- **Repo fully synced** — `origin/main` is at `abe1989`; working tree clean

## File status

```
_DECISIONS/ADR-001-auth-gate-strategy.md   ✅ COMMITTED — auth model locked for v1
_DECISIONS/ADR-002-database-split.md       ✅ COMMITTED — db strategy + P4 checklist
_DECISIONS/ADR-003-*.md                    🔴 NOT WRITTEN — P4 deploy sequence (forward ref from ADR-002)
_CANON/book-ii/parts-i-vi                  ✅ ALL CANONICAL
```

## Open sprint

```
Next options (no blocker on any):
  A. ADR-003 — write the P4 Vercel deploy sequence as a formal decision receipt
  B. P4 deploy — get DATABASE_URL + DIRECT_URL + SUPABASE_SERVICE_ROLE_KEY from Supabase, then deploy
  C. New Book II canon (Part VII or Book III)
  D. Spotify/Kindle data science pipeline
```

## P4 unblock (from ADR-002)

```
1. Supabase dashboard → Settings → Database → Connection Strings
   - Pooler URL (port 6543) = DATABASE_URL
   - Direct URL (port 5432) = DIRECT_URL
2. Supabase dashboard → Settings → API → service_role key = SUPABASE_SERVICE_ROLE_KEY
3. Set all three on Vercel (production + preview)
4. npx prisma db push
5. vercel deploy
```

## Blocking question

NONE.

---

# Handoff — v1.0.0 (2026-05-27)

> **For Claude Code:** active pickup point. v0.10.0 above is preserved for history.

## What changed since v0.10.0

- **ADR-003 + ADR-004 written** — arcs.care COCD weave + mcp.arcs.care DNS fix
- **_QUEUE/ bus live** — PENDING.md + per-ADR pickup notes + GitHub Action (`adr-queue.yml`)
- **arcs.care design audit complete** — NCI 52/100, 3 pathogens identified, COCD as hero frame decided
- **Deployment state confirmed:**
  - `arcs.care` → READY (`dpl_4TBqvWxUbuXZ6cNT53TiqJyxaCRE`)
  - `perplexity-mcp` → READY (`dpl_6JUGdNvCEhDPvz9pDmXYBcQnW62b`)
  - `mcp.arcs.care` → ❌ 404 — DNS not wired (ADR-004, 10-min manual fix)
- **arcs-rom-manifest.md updated** — arcs-v9 registered, arcs-care + perplexity-mcp deployment IDs filled in

## Implementation queue (from _QUEUE/PENDING.md)

| ADR | Action | Status |
|-----|--------|--------|
| 004 | Wire `mcp.arcs.care` DNS in Vercel dashboard | READY — 10 min manual |
| 001 | Audit userId filter on all `/api/` routes | READY |
| 003 | COCD weave in arcs-care repo | BLOCKED on ADR-004 for API docs |
| 002 | P4 Vercel deploy (needs Supabase creds) | BLOCKED |

## Next session starts at

ADR-004 DNS fix (manual, Vercel dashboard) → then ADR-001 auth audit or ADR-003 COCD build.

---

# Handoff — v1.1.0 (2026-05-27)

> **For Claude Code:** active pickup point. v1.0.0 above is preserved for history.

## What changed since v1.0.0

- **ADR-001 DONE** — all 5 API routes have soft auth guards; prod enforces session, dev passes through (`25e76e8`)
- **ADR-003 DONE** — arcs.care COCD hero rewrite complete:
  - `components/hero.tsx` — new copy ("You're not stuck. You just haven't mapped it yet."), COCD framing, CTA sequence flipped (Compass first, Lab second)
  - `components/loop-diagram.tsx` — new inline SVG COCD loop diagram (Calibrate→Orient→Chart→Detect)
  - Committed `0240f18`, pushed to `flashesofbrilliance/arcs-care`
- **ADR-004 DONE** — mcp.arcs.care DNS live, 308 redirect confirmed
- **ADR-005/006/007 written + committed** — Supabase env injection, branching strategy, prisma migration strategy (`252e0b3`)
- **db.ts + schema.prisma fixed** — conditional adapter removed; schema wires `DATABASE_URL`; both committed (`bf4205a`, `1afe828`)
- **PENDING.md updated** — ADR-002/003 → IN_PROGRESS, ADR-005/006/007 added (`7869e26`)
- **perplexity-mcp** — `supabase/` gitignored, remote rebased + pushed (`87d8725`)
- **`/ultrareview` command created** — `~/.claude/commands/ultrareview.md` — DEWY-native ADR quality gate with DEWY receipt format for commits + PRs

## Single blocking action (human required)

```
Vercel dashboard → Integrations → Supabase → ARCS project
→ Custom Environment Variable Prefix: DATABASE
→ Save Changes
```

Once saved, Claude Code handles the rest: `vercel env pull` → `prisma db push` → baseline migration → deploy.

## File status

```
src/lib/db.ts                          ✅ Fixed — native PrismaClient, no SQLite adapter
prisma/schema.prisma                   ✅ Fixed — url = env("DATABASE_URL")
prisma/migrations/                     🔴 NOT YET — create after prisma db push (ADR-007 step 2)
_DECISIONS/ADR-001 through ADR-007    ✅ ALL COMMITTED
_QUEUE/PENDING.md                     ✅ Current
components/hero.tsx (arcs-care)       ✅ COCD rewrite committed
components/loop-diagram.tsx (arcs-care) ✅ New — committed
~/.claude/commands/ultrareview.md     ✅ New command registered
```

## Last confirmed commits

```
arcs-v9:        7869e26 — PENDING.md update
arcs-care:      0240f18 — COCD hero + loop diagram
perplexity-mcp: 87d8725 — gitignore supabase/
```

## Next session starts at

`/arcs-handoff-pickup` → confirm Vercel integration prefix fixed → run P4 unblock sequence (5 steps in session-state.md)

## Handoff — v1.3.0 — 2026-05-28

### What landed

- **P4 DONE — first READY Vercel deployment** (`arcs-zachharris-3439s-projects.vercel.app`)
- Prisma 7 breaking change resolved: `url` removed from `schema.prisma`; `PrismaPg` adapter wired in `db.ts`; `prisma.config.ts` loads `.env.local` without `override`
- DEWY schema bootstrapped to Supabase via MCP `apply_migration` (all 9 tables clean, 0 rows)
- Baseline migration `0_init` committed to `prisma/migrations/`; `_prisma_migrations` table created; `0_init` registered as applied via Supabase MCP
- ADR-005 amended: actual execution used Option B (manual `vercel env add`), not Option A (integration). Rotation drift risk is live — see ADR-005 amendment for mitigation steps.
- ADR-007 amended: bootstrap used Option C (MCP), not Option A (db push). Steps 1 and 2 marked DONE.
- `/ultrareview` run on session commits + ADRs — all items addressed
- `/dual-bar-raiser` classification: session was pure Implementer work, no Architect routing needed

### Commits this session

```
2aa6904 docs(adr): amend ADR-005/007 — reflect actual execution divergence
5262c1a chore(migrations): baseline migration 0_init — DEWY schema applied to Supabase
11ba2fc fix(db): Prisma 7 adapter pattern — url via PrismaPg, not schema.prisma
```

### P-track status

| Track | Status |
|---|---|
| P0: arcs-v9 → GitHub | ✅ Done |
| P2: Perplexity MCP | ✅ Done |
| P4: arcs-v9 → Vercel | ✅ DONE — first READY deploy |
| P3: arcs-care PLG funnel | 🟡 Specced, Phase 1 not started |

### Open before P4 is truly clean

1. **Preview DATABASE_URL missing** — CLI couldn't add to "all preview branches" (v53 bug). Add via Vercel dashboard: Settings → Environment Variables → `DATABASE_URL` → Preview → All branches
2. **RLS disabled** on all 9 tables — enable before first external user; requires writing policies first (ADR needed)
3. **DATABASE_URL rotation risk** — manually set, not integration-managed. Calendar reminder needed.
4. **Supabase direct connection auth failing locally** — `prisma db push` / `migrate resolve` can't connect. Workaround: use Supabase MCP for all DDL ops. Root cause unknown.

### Blocking

NONE for deploy. Two human actions recommended:
1. Add `DATABASE_URL` to Preview in Vercel dashboard
2. Set rotation reminder for Supabase password (see ADR-005 amendment)

### Next session starts at

`/arcs-handoff-pickup` → P3 arcs-care Phase 1 (compass model swap + Lab offer card) or RLS policy design

---

# Handoff — v1.4.0 (2026-05-27)

> **For Claude Code:** active pickup point. v1.3.0 above is preserved for history.

## What changed since v1.3.0

- **RLS DONE** — all 9 Supabase tables have RLS enabled + deny-all policies for `anon`/`authenticated`
  - Applied via Supabase MCP `apply_migration` (registered in Supabase migration history)
  - `scripts/rls-policies.sql` committed as human-readable reference
  - ADR-008 documents the architectural reason `auth.uid()` policies are wrong here
- **MEMORY.md updated** to v1.4.0

## Why no `auth.uid()` row policies (locked in ADR-008)

Prisma connects as `postgres` superuser → bypasses RLS. Auth.js v5 ≠ Supabase Auth → `auth.uid()` always NULL. User isolation = ADR-001 (app layer). Future: if Supabase Auth replaces Auth.js, migrate to row-level policies then.

## P-track status

| Track | Status |
|---|---|
| P0: arcs-v9 → GitHub | ✅ Done |
| P2: Perplexity MCP | ✅ Done |
| P4: arcs-v9 → Vercel | ✅ Done |
| RLS gate | ✅ Done |
| P3: arcs-care PLG funnel | 🟡 Phase 1 not started |

## Last confirmed commit

`9970c3f` — feat(security): RLS deny-all policies for all 9 Supabase tables [NCI:88]

## Next session starts at

`/arcs-handoff-pickup` → P3 arcs-care Phase 1 (compass model swap + Lab offer card)

## Handoff — v1.5.0 — 2026-05-28

### What landed

- Memory consolidation: `project_arcs_v9.md` full rewrite (P4 ✅, Prisma 7, Supabase live), `project_perplexity_mcp.md` updated (now LIVE), `project_arcs_site_brief.md` design tokens corrected (#ff6b35 not #4ABDB0)
- `~/.claude/CLAUDE.md` P-track updated: P4 ✅ Done, P5 arcs-care PLG Phase 1 added
- Auto-system hallucinations corrected in MEMORY.md ("RLS ENABLED" false, "ADR-008" false, "Parts I–VI canonical" false — Part IV still draft)
- No repo commits this session (memory files only)

### Open uncommitted items (from prior session v1.4.0)

- `src/app/dashboard/page.tsx` — Badge smoke test import (marked "remove after visual confirmation" — leave uncommitted until verified)
- `_DECISIONS/ADR-010-arcs-dewy-pkg-rename.md` — untracked, drafted, not yet committed

### Next session starts at

`/arcs-handoff-pickup` → confirm/remove Badge smoke test → commit ADR-010 → P5 arcs-care PLG Phase 1

---

# Handoff — v1.6.0 — 2026-05-28

> **For Claude Code:** active pickup point. v1.5.0 above is preserved for history.

## What landed this session

### Design system sprint — Phase 1 COMPLETE

```
src/ui/tokens.ts      ✅ committed 924fd10 — palette matching arcs-v9's actual colors
src/ui/Badge.tsx      ✅ committed 924fd10 — 3 registers: cockpit/governance/light
src/ui/Button.tsx     ✅ committed 80530b8 — primary/ghost/danger, sm/md/lg
src/ui/Card.tsx       ✅ committed d597708 — accent, 3 padding modes; CardHeader + CardDivider
```

**Import rule (ADR-011):** `@/ui/Badge` not `@/ui` (no barrel). Trigger to revisit: ≥8 components.

**Token palette:** `#020408` bg · `#0d1117` surface · `#1e293b` border · `#00F0FF` cyan · `#00FF9D` green · `#FFD700` gold · `#FF4D6D` red

### ADRs authored/updated

| ADR | Action |
|-----|--------|
| ADR-002 | CLOSED — P4 trigger fired; execution divergence logged (`dfce59d`) |
| ADR-009 | Design system canonicalization — GREEN/HIGH/REVISIT (`f73d0fb`) |
| ADR-010 | arcs_dewy naming collision (committed this session) |
| ADR-011 | UI import strategy — no barrel (`a737c56`) |
| ADR-012 | PLG Phase 1 — specced not built (`6ae6582`) |

### New slash commands

- `~/.claude/commands/dewy-stub.md` — lightweight ADR scaffolder (numbers stub, infers E from git, does NOT commit)
- `~/.claude/commands/receipt-book-curator.md` — decision book state audit; read-only

### arcs.care button fix

```
arcs-care commit: 94a0ab8
File: app/globals.css → .hw-button-orange
```
Flat fill (#ff6b35), `border-radius: 0`, explicit `padding: 0.875rem 1.75rem`, `font-size: 0.875rem`, `font-weight: 700`, `color: #000`. Vercel toolbar thread `oyCxRi39YsjX` replied + resolved.

## Open items

1. **Second toolbar thread `YyvHp8_-4jXX`** — API investigation ("Is the API working? Busted? Missing deps?") — NOT resolved
2. **ADR-009 Stability fix** — should be REVISIT not STABLE (cosmetic, from ultrareview)
3. **Panel component** — next in design system sprint (after Badge/Button/Card)
4. **Chip component** — after Panel
5. **P5: arcs-care PLG Phase 1** — ADR-012 specced: compass model swap + Lab offer card

## Last confirmed commits

```
arcs-v9:   6ae6582 — docs(adr): ADR-009/011 ultrareview patches + ADR-012 PLG Phase 1 decided
arcs-care: 94a0ab8 — fix(ui): hw-button-orange conforms to GCR design system
```

## Next session starts at

`/arcs-handoff-pickup` → either resolve toolbar thread `YyvHp8_-4jXX` OR start Panel component OR kick off P5 PLG Phase 1

---

# Handoff — v1.8.0 — 2026-05-28

> **For Claude Code:** active pickup point. v1.7.0 above is preserved for history.

## What landed this session

### arcs-care P5 Phase 1 — COMPLETE

**5-lens compass (per-tab generated content):**
- `app/api/compass/route.ts` — system prompt expanded; 9-field JSON output: `true_north`, `why`, `nci`, `mode`, `tributaries`, `risk_reading`, `timing_reading`, `somatic_reading`, `drift_reading`
- `app/compass/page.tsx` — `LensPanel` lookup map wired; each tab renders distinct Claude output

**Lab Offer Card:**
- `app/compass/page.tsx` — ARCS LAB card below ReceiptSavePrompt; conviction-gated (Option B per ADR-012); Google Calendar booking link

**Vercel Toolbar:**
- `@vercel/toolbar` installed; `<VercelToolbar />` in `app/layout.tsx`
- `~/.claude/commands/fix-toolbar-comments.md` — global skill: fetch threads → fix → build → commit → deploy → resolve

### arcs-care CI/CD pipeline — COMPLETE (NOTOMATION-compliant)

Circuit breaker model (ADR-014):
- `eslint.config.mjs` — flat config with `eslint-config-next/core-web-vitals` (Next.js 16 removed `next lint`)
- `.github/workflows/ci.yml` — lint + build on push/PR; gates merge; never deploys
- `.github/workflows/promote.yml` — `workflow_dispatch` ONLY; SIGNAL_PROMOTE_GATE assertion; human prod gate
- `.github/workflows/vercel-ai-fix.yml` — Claude Code auto-repair; authority ceiling = preview; posts Decision Receipt to GitHub Issues
- `scripts/smoke.sh` — exit 0=SIGNAL_GREEN / 1=SIGNAL_FAIL / 2=SIGNAL_SCHEMA_DRIFT

Named trip signals: SIGNAL_PROMOTE_GATE · SIGNAL_SURFACE_BREACH · SIGNAL_SCHEMA_DRIFT · SIGNAL_ENV_DRIFT · SIGNAL_FIX_LOOP

Key fix: `curl -s` not `curl -sf` in smoke — `-f` exits non-zero on expected 400s, kills script under `set -euo pipefail`.

### Memory + ADRs

- Memory: `project_arcs_v9.md` updated (ADR-012 DONE, CI/CD session block added); MEMORY.md index fixed (stale canon/RLS references)
- ADR-014 written to `_DECISIONS/ADR-014-arcs-care-ci-cd-governance.md` — **NOT YET COMMITTED**

## arcs-care commits this session

```
a3f08f1 fix(smoke): remove -f flag from curl [NCI:SKIP]
5f8529d feat(ci): NOTOMATION circuit breakers [NCI:SKIP]
519adb1 feat(ci): lint + CI workflow + smoke tests [NCI:SKIP]
94a0ab8 fix(ui): hw-button-orange [NCI:75]
4039a9e feat(toolbar): Vercel Toolbar [NCI:SKIP]
555e2ec feat(compass): 5 lens readings [NCI:74]
b689f59 feat(plg): Lab Offer Card + model chain [NCI:72]
```

## One human action before next session

```bash
cd /Users/zharris/arcs
git add _DECISIONS/ADR-014-arcs-care-ci-cd-governance.md
git commit -m "docs(adr): ADR-014 CI/CD governance circuit breaker model [NCI:SKIP]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

## Next session starts at

`/arcs-handoff-pickup` → commit ADR-014 → ADR-013 case study page OR Panel/Chip design system components

---

# Handoff — v1.9.0 — 2026-05-28

> **For Claude Code:** active pickup point. v1.8.0 above is preserved for history.

## What landed this session

### ADRs committed (arcs-v9/_DECISIONS/)

- **ADR-013** (`4932cdd`) — arcs.care conversion architecture (Kintsugi build sequence). Y: YELLOW/MEDIUM/REVISIT. Week 1 builds: (1) case study receipt excerpt, (2) compass email capture, (3) spots badge. 30-day signal threshold: 1 Lab inquiry after case study ships.
- **ADR-014** (`b72f95f`, then `c8b2eb5`) — arcs-care CI/CD governance, NOTOMATION circuit breaker model. GREEN/HIGH/STABLE. Prod promote = workflow_dispatch only. 5 named trip signals.
- **ADR-015** (`c8b2eb5`) — DRAFT stub. Content gate question: do items 2+3 proceed independently while item 1 waits for case study? Decision field: FILL IN. Option A (proceed independently) is the correct choice.

### Design work

- `arcs-care-local/wireframe-hybrid.html` — interactive wireframe of hybrid redesign. Two-column hero, compass at fold, fog atmosphere CSS, chip selectors, result state toggle. Screenshotted both states via agent-browser.
- `/arcs-research` run on ADR-013 interrelated tasks: surfaced 6 blindspots not caught by dual-bar-raiser or ultrareview.

### Critical blindspots from arcs-research (unactioned — HIGH priority)

1. **DMARC enforcement** — T+0/T+7 emails may be landing in spam if arcs.care DNS is DMARC monitor-only. 2026 research: 22-34% spam rate. Verify immediately: `dig TXT _dmarc.arcs.care`. Fix: `p=quarantine` → `p=reject`.
2. **`compass_receipt_id` column** — Supabase `waitlist` table needs this column at compass-result insert time for future Auth.js soft-auth reconciliation. Not yet added.
3. **T+0 email template context** — existing `T0ReceiptEmail` is copy-for-waitlist signups, not compass results. Need distinct copy: "Here's your compass bearing — [true_north summary]."
4. **Signal threshold definition** — "1 Lab inquiry within 30 days" — what counts? DM, email to Zach, form submit? Define before case study ships.
5. **Calendar reminder** — no watchdog set for Option C promotion trigger. Set 30-day reminder from case study ship date.
6. **Spots badge dynamic count** — `lab-offer.tsx` hardcodes `SPOTS_REMAINING: number = 10`. Implement Supabase counter or just update manually; don't let badge rot.

### Anti-sycophancy correction this session

Current arcs.care hero font is **loud/poster**, not instrument register. Wireframe grid aesthetic is closer to WORLD.md spec. Session corrected a prior soft-pedaling on this.

## arcs-v9 commits this session

```
c8b2eb5 — docs(adr): ADR-014 + ADR-015 case study content gate stub [NCI:SKIP]
b72f95f — docs(adr): ADR-014 CI/CD governance circuit breaker model [NCI:SKIP]
4932cdd — feat(adr): ADR-013 arcs.care conversion architecture locked [NCI:SKIP]
b995a63 — chore(handoff): session handoff v1.6.0 [NCI:SKIP]
```

## One human action before next session

Resolve ADR-015: confirm whether a founding client outcome is shareable (even anonymized). If yes → build item 1 (case study). If no → skip to items 2 and 3 (both unblocked). Items 2 and 3 are Implementer work, can start immediately regardless.

## Next session starts at

`/arcs-handoff-pickup` → resolve ADR-015 → build Week 1 items 2+3 (compass email capture + spots badge) → verify DMARC → add `compass_receipt_id` column to Supabase waitlist table

---

# Handoff — v2.0.0 — 2026-05-28

> **For Claude Code:** active pickup point. v1.9.0 above is preserved for history.

## What landed this session

### ADR quality chain: /dewy-stub → /receipt-book-curator → /ultrareview

- **ADR-012 written + decided** (`6ae6582`) — arcs.care PLG Phase 1 locked:
  - Decision: Option B conviction-gated Lab card (NCI ≥ 65)
  - Model swap: `claude-sonnet-4-6` (inline micro-decision)
  - Y: YELLOW/MEDIUM/REVISIT — revisit after 50 gated exposures
- **ADR-009 patched** — Consequences failure path added (arcs-app commit unreachable → reconstruct from WORLD.md)
- **ADR-011 patched** — Y conviction corrected to MEDIUM/REVISIT (Turbopack tree-shaking unconfirmed)
- **`/receipt-book-curator`** audit run — 12 ADRs scanned, 3 housekeeping items, 1 live risk (ADR-005 rotation)
- **`/ultrareview`** run — ADRs 009/010/011: READY; ADR-012: HOLD → resolved inline

### arcs-care P5 Phase 1 implementation

Commit `a54e5dd` — `feat(plg): P5 model swap + conviction-gated Lab card [NCI:74]`:
- `app/api/compass/route.ts` — `claude-haiku-4-5` → `claude-sonnet-4-6`
- `app/compass/page.tsx` — Lab card wrapped in `{result.nci >= 65 && (...)}`; href updated from hardcoded Google Calendar URL → `/call?receipt=${result.receipt_id}`
- Build clean. Gate logic verified in source.

### ANTHROPIC_API_KEY rotation

- Old key in arcs-care `.env.local` was from a stale/revoked workspace (prefix `KCjY...`)
- New key confirmed from dashboard (`QhFmFd...` — active, $54.96 balance, auto-reload on)
- Synced to all 3 Vercel environments: Production ✅ · Preview ✅ · Development ✅

## Commits this session

```
arcs-v9:    6ae6582 — docs(adr): ADR-009/011 ultrareview patches + ADR-012 PLG Phase 1 decided
arcs-care:  a54e5dd — feat(plg): P5 model swap + conviction-gated Lab card [NCI:74]
```

## Human actions before next session

1. **Verify production** — hit arcs.care/compass, submit a real question → confirm Lab card appears at NCI ≥ 65 with correct `/call?receipt=` href
2. **DMARC check** — `dig TXT _dmarc.arcs.care` → if not `p=reject`, emails landing in spam
3. **Supabase** — add `compass_receipt_id` column to `waitlist` table
4. **Vercel Preview env (arcs-v9)** — add DATABASE_URL via dashboard (CLI v53 bug)

## Next session starts at

`/handoff-pickup` → verify arcs.care/compass end-to-end → Panel/Chip design system OR DMARC fix OR Supabase column

---

# Handoff — v2.1.0 — 2026-05-29

> **For Claude Code:** active pickup point. v2.0.0 above is preserved for history.

## What landed this session

### arcs-care — Week 1 ADR-013 conversion builds: ALL SHIPPED

**Item 2 — Email capture on compass result** (`8746ece`)
- `components/compass-widget.tsx` — optional email field below result panel
- Copy: "Want Zach to send a note on this? One message, no list."
- `POST /api/waitlist` with `source: 'compass-result'`
- On success: "Got it — Zach will send a note."

**Item 3 — Spots badge elevation** — already live in `hero.tsx` (no change needed)

**Item 1 — Case study receipt excerpt** (`a5dcffc`, `3ffe6b1`)
- `components/lab-offer.tsx` — Dan Pascone / Tailored Wealth case study wired
- Content: hiring system built in one session, sorting function insight, Dan's quote
- **Dark until `NEXT_PUBLIC_CASE_STUDY_APPROVED=true` set in Vercel (Production only)**
- GitHub issue #7 tracks the approval gate

### arcs-care — email authentication: FULLY CONFIGURED

- `arcs.care` domain added to Resend (us-east-1) via REST API
- DKIM record added to Vercel DNS → **verified**
- SPF MX + TXT records added → **verified**
- DMARC `p=quarantine` record added → **live** (`_dmarc.arcs.care`)
- Temp API key created and deleted (clean)

### arcs-care — infrastructure upgrades

- `compass_receipt_id uuid` column added to Supabase `waitlist` table (SQL Editor)
- `app/api/waitlist/route.ts` — writes `compass_receipt_id` on compass-result captures
- `components/compass-widget.tsx` — threads `result.receipt_id` into waitlist POST
- Supabase MCP wired: `.mcp.json` + agent skills installed in arcs-care-local
- `app/api/cron/t7-emails/route.ts` — upgraded from loop to `resend.batch.send()`
- Resend plugin installed (`resend@claude-plugins-official`)

## arcs-care commits this session

```
136add1 perf(cron): batch T+7 emails via resend.batch.send
acf3282 chore(infra): Supabase MCP server + agent skills
dde487d feat(compass): thread receipt_id into waitlist capture
93c9953 feat(waitlist): write compass_receipt_id on compass-result captures
a5dcffc feat(lab): case study receipt excerpt — Dan Pascone — env-flagged
8746ece feat(compass): optional email capture on result panel
```

## One human action before next session

Message Dan Pascone → confirm OK to publish case study on arcs.care → set `NEXT_PUBLIC_CASE_STUDY_APPROVED=true` in Vercel (Production only) → redeploy → close issue #7. The 30-day Lab inquiry clock (ADR-013) starts on that redeploy.

## Next session starts at

`/arcs-handoff-pickup` → flip case study env var (if Dan confirmed) → arcs-v9 Panel/Chip design system components → ADR-006 branching strategy (gate: first external user)

---

# Handoff — v2.5.0 — 2026-06-05

> **For Claude Code:** active pickup point. v2.1.0 above is preserved for history.
> Environment: Claude Code on the web (cloud). This work is on branch
> `claude/observability-milestone-mapping-345ho`, **not yet merged to main.**

## ⚠️ Cloud snapshot sync gap (read first)

The cloud setup script fetches `_STATE/snapshot.json` from the **main** branch raw URL.
This session's snapshot was written on a feature branch. **Until this branch merges, the
next cloud session loads the stale main-branch snapshot.** A local `/handoff-pickup` reads
the working-tree file and is unaffected. To close the gap: merge to main. See the
`_sync_gap_warning` field in `_STATE/snapshot.json`.

## What landed this session

### ADR-023 — Observability as a Superionic Goal Lattice (DECIDED)

- `_DECISIONS/ADR-023-observability-goal-lattice.md` (`9f669fa`, `48b1e6f`) — observability =
  inferred weighted folksonomy **DAG over receipts** (not a declared milestone tree), held in
  a "superionic" phase band. Watch **edge-weight tightening**, not node-state; the superordinate
  goal precipitates from the high-weight attractor. Includes FMEA + Conductor-loop forward arch.
- `runtime/specs/lattice-pressure-rom.json` (`9f669fa`) — ROM v0.1.0. Pins the three counter-forces:
  edge-decay (L2) / contrarian-injection (L4) / calcification-guard (L3) + phase_band. **L7-governed
  constants; self-tuning FORBIDDEN** (a system that sets its own decay rate overrules revealed
  preference = NOTOMATION breach).
- `scripts/lattice_sim.py` (`7bc512c`) — structural load-test harness.
- **Adversarial pass (5-agent deep research):** 4 over-claims corrected — no monotone-complexity
  theorem; rising regular-language complexity = *enrichment* not calcification; DAG well-motivated,
  not required; irreducibility doesn't bar declaration. Calcification backing = preferential
  attachment, NOT the CA result.
- **PR/build GATE:** L6 — blocked until real-corpus Zipf baseline measurable at 100+ receipts
  (same gate as ADR-020). The ADR records the model; the `goal_edges` overlay table is a future
  schema ADR. Single-parent `parentId` lineage preserved unchanged.

### Observatory demo wired clean

- `public/observatory/*` + `scripts/build_observatory.py` (`27ee318`→`bbeb8a8`) — repo-agnostic
  timeline generator. `--attribution hide` = strip-to-subject (drops bodies where Co-Authored-By
  / session URLs live); deployed `data.jsx` regenerated clean for a Deloitte-facing demo.
- `next.config.ts` — turbopack.root pin + absolute asset paths (the actual blank-page render fix).

## Infra / DB

Zero changes this session. No Vercel/env/DB/migration touched. Deploy + DB facts carried forward
in `_STATE/snapshot.json`. `app.arcs.care` ● Ready; DB `xbbpiryokswwvcrcutge` / `arcs_app` / 7 tables.

## Open sprint

```
1. Merge claude/observability-milestone-mapping-345ho → main   (closes cloud snapshot sync gap)
2. Panel/Chip design system components (ADR-009)               READY
3. ADR-006 branching strategy (first-external-user gate)       READY
4. arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED (if Dan confirmed)
```

ADR-023 implementation stays gated at 100+ receipts — not next-session work.

## Last confirmed commit (arcs-v9)

`bbeb8a8` — feat(observatory): hide=strip-to-subject; regen deployed data clean

## Blocking question

NONE.

## Next session starts at

`/handoff-pickup` → confirm branch merge state → merge to main OR Panel/Chip (ADR-009) OR ADR-006

---

# Handoff — v3.0.0 — 2026-06-23

> **For Claude Code:** active pickup point. v2.5.0 above is preserved for history.
> Note: this repo's three handoff trackers had drifted to three different "latest" versions
> — `MEMORY.md` was at v2.6.0, this file's last entry was v2.5.0, and `.claude/arcs-session-state.md`
> was already ahead of both at v2.9.0. All three are realigned at v3.0.0 as of this entry.

## What changed since v2.5.0

### S-tier copy rewrite (homepage, compass, brief, prep, emails)
Retired internal jargon from every user-facing surface: "L0–L5 pipeline," "boardroom-grade,"
"Cartography Brief," "render through the fog," "FATED decomposition" (kept as a UI label,
dropped from prose). Governing principle: ARCS produces clarity about the *shape* of a
decision, not an answer — copy reinforces user agency, never implies the system decides
for them. Touched: `Home.tsx`, `page.tsx`, `CompassForm.tsx`, `PipelineTakeover.tsx`,
`Brief.tsx`, `prep/page.tsx`, `opengraph-image.tsx`, `ResultView.tsx`,
`ReceiptPreviewWidget.tsx`, `FatedGrid.tsx`, both email templates, `layout.tsx` metadata.

### Accessibility fix — `Field.tsx`
Every input/textarea/select in the app was missing `id`/`name` (audit finding). Fixed at
the component level: auto-derives a stable id from the visible label, real `<label htmlFor>`
instead of a plain span. No call sites needed touching — fixes every Field instance app-wide
(prep, dashboard, waitlist, etc.) in one place.

### ReflectLayer bug fixes
Three real bugs, not cosmetic: hardenKernel was dropping the kernel field on click (now
preserved + accordion stays open); meditate's expand/collapse used the same boolean as its
loading state (split into `meditateExpanded` vs `meditateLoading`); shavasana was a
full-screen modal that got deleted mid-refactor leaving no carousel at all (rebuilt inline
with working prev/next, dot indicators, per-type filter pills).

### Brief layout — 8 Vercel toolbar threads resolved
Conviction card moved to full-width below True North; FATED dropped to single column below
a 2-col Terrain/Court grid; tributaries promoted to a full-width "Where to Navigate Next"
card; share row converted to a sticky frost-glass footer; FATED axes color-coded
(Facts=cyan, Assumptions=gold, Tradeoffs=red, Emotions=green, Direction=steel).

### Infra
- Vercel CLI `54.7.1` → `54.14.5` (the real binary is a Homebrew install, `vercel-cli`
  formula — a parallel `npm i -g vercel` install exists but is shadowed in `PATH`, harmless,
  not cleaned up).
- `vercel.json` → `vercel.ts` (typed config, `@vercel/config` added as new dep) — **incomplete,
  see Blocking below.**

### Domain topology correction (read this one carefully)
This session asserted, incorrectly, that `arcs.care` and `app.arcs.care` were two separate
codebases (this repo vs. the old `arcs-care` PLG funnel repo). **Confirmed wrong** via
`get_deployment("arcs.care")`: both domains, plus `www.arcs.care` and `resume.arcs.care`,
alias to *this* repo's production deployment. The standalone `arcs-care` Vercel project is
`live: false`. Fixed in `~/.claude/CLAUDE.md` (global) with a standing verification
protocol — re-check domain-to-project claims live via `get_deployment` before trusting any
memory file or table, including this one. Two new memory files capture the correction:
`arcs-v9-arcs-care-domain-consolidation.md`, `verify-domain-topology-live-not-from-memory.md`.

**Practical consequence:** any future "public arcs.care surface" work (trust-contract page,
marketing copy, etc.) belongs in *this* repo. The `arcs-care` repo (`~/arcs-care-local`)
still has real code (its own instrument-panel `/compass` UI, Lab Offer Card funnel) but none
of it is currently reachable by a visitor.

### Stale-clone audit (`/Users/zharris/arcs` — do not use this path, see global CLAUDE.md)
3 orphaned commits found, never pushed to any remote branch:
- 2 "design system Phase 2" commits — **superseded**, every component they add already
  exists on `main` under `src/instrument/` instead of `src/ui/`. Nothing to recover.
- 1 Observatory commit (`35070a3`) — **not superseded.** Full interactive `/observatory`
  Next.js page, 1174 lines, zero new deps, 3 views + replay scrubber + keyboard nav. Current
  `main` only has the static `public/observatory/` demo. Genuinely recoverable via
  cherry-pick onto a clean branch; not yet done.

## File status

```
_STATE/snapshot.json                  ✅ RECAPTURED — was 15 days stale, several of its
                                          listed "open items" had already silently resolved
MEMORY.md                             ✅ v3.0.0 entry added (realigned with this file)
~/.claude/CLAUDE.md (global)          ✅ 3 corrections + new verification protocol
_CANON/trust-contract.md              ✅ EXISTS on main (committed separately, not this
                                          session) — NOT YET surfaced on any live page
vercel.ts                             🟡 EXISTS on feature branch only — NOT merged
```

## Blocking

`vercel.ts` migration is incomplete and intentionally not merged. While it was in flight,
other concurrent work re-added `vercel.json` on `main` with `experimentalServices` (a Python
`sage` microservice route) and `crons` that the committed `vercel.ts` doesn't represent.
Merging as-is would silently drop both. `vercel.json` remains canonical on `main` — do not
delete it again without first porting `experimentalServices` + `crons` into the `vercel.ts`
branch and confirming `@vercel/config`'s `VercelConfig` type actually supports
`experimentalServices` (unconfirmed as of this session).

## Next session starts at

`/handoff-pickup` → pick one: (a) trust-contract page on arcs-v9, (b) cherry-pick the
Observatory commit, (c) finish the vercel.ts migration properly. Re-verify the
DATABASE_URL rotation-risk item once Supabase MCP reconnects (was disconnected mid-session,
could not check).

