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
ATG · Kairos detection · Observatory/replay · Blockchain registry · L6–L7 engine · Python Vector Collision microservice

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
