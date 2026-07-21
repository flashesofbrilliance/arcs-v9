# ARCS v9 — Handoff Archive (v0.1.0 → v3.5.0)

> **Archived 2026-07-19.** These handoff sections were relocated out of `CLAUDE.md` to end the
> per-session token tax of loading dead history on every session. Nothing is deleted — full history
> is preserved here and in git. The two most recent handoffs (v3.6.0, v3.7.0) remain live in
> `CLAUDE.md`. See `_PATTERNS/2026-07-19-token-efficiency-audit.md` for the rationale.
>
> To read older context: open this file. To resume a specific thread, find its handoff section here.

---

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

---

# Handoff — v3.1.0 — 2026-06-23

> **For Claude Code:** active pickup point. v3.0.0 above is preserved for history. This
> entry covers the back half of the same 2026-06-23 session — full detail is in `MEMORY.md`
> `[v3.1.0]`, not repeated here to avoid the two-logs-disagree problem this exact handoff
> chain has already caught itself doing once today.

## What changed since v3.0.0

10 commits (`7f1df53`..`3474d10`). Headlines: a real `CANON_COLLISION` found and resolved
(`BAR`/`KKL` meant two different things in two canon files — see `MEMORY.md`); a new
ROM Candidate landed (`operators/arcs_inchworm_echo.py`, `RC-OPS-001` — Golden Inchworm +
Orthogonal Echo Detector, gated behind an Observatory period, NOT yet ROM); an 8-item
governance roadmap with full dependency graph, pathogen taxonomy, and pre-mortem
(`_PATTERNS/2026-06-23-governance-roadmap.md`); a per-task S-tier plan
(`_PATTERNS/2026-06-23-s-tier-execution-plan.md`) that includes a withdrawn citation
(caught the same session — verify-before-commit applied to this document's own claims,
not just to code); and a cross-reference against `RECOIL-PROTOCOL.pdf` (the ARCS corpus's
own retrospective self-audit), which independently flagged the same gap this session found
by other means.

## File status

```
_PATTERNS/2026-06-23-governance-roadmap.md      ✅ EXISTS — dependency graph + pathogen catalog
_PATTERNS/2026-06-23-s-tier-execution-plan.md   ✅ EXISTS — per-task plan, NOT in canonical
                                                    Section 1-7 format yet (task #8)
operators/arcs_inchworm_echo.py                 ✅ EXISTS — RC-OPS-001, gated, not ROM
operators/README.md                             ✅ Updated — new "ROM Candidates" section
_STATE/cold-start-v3.1.0.md                     🔴 CREATE THIS SESSION — zero-context pickup prompt
```

## Open backlog (8 items — see TaskList for live status, this is a snapshot)

#1 backup repo (ready) · #2 password rotation (blocked on Zach) · #3 consolidate 3 logs
(ready, sequencing point) · #4 drift-sensor (design done, build not started — long pole) ·
#5 prose-rule audit (ready) · #6 DEWY commit stamp (ready after #3+#5) · #7 Observatory
cherry-pick (ready) · #8 canonical S-tier reformat (deferred this session)

## Blocking

None for the next session to start work. #2 is blocked on Zach specifically, not on any
session. #4 and #6 have internal sequencing dependencies, documented in the roadmap doc.

## Next session starts at

`/handoff-pickup`, then read `_STATE/cold-start-v3.1.0.md` for a fuller zero-context
briefing before picking a task. Recommended first move: any of #1/#5/#7 (no dependencies,
no human blocker, genuinely startable cold).

---

# Handoff — v3.2.0 (2026-06-23)

> **For Claude Code:** active pickup point. v3.1.0 above is preserved for history. This
> session worked on branch `observatory-cherry-pick` (pushed to origin, no PR yet).

## What changed since v3.1.0

- **Critical production fix, live regardless of git/merge state**: Supabase project
  `xbbpiryokswwvcrcutge` had `public.SageTrace` fully exposed (RLS disabled, anon
  read/write/delete via PostgREST). Found via a real alert email, verified and fixed via
  the `supabase` CLI (the Supabase **MCP connection cannot see this project** — wrong
  org; use the CLI). Fixed with the ADR-008 deny-all pattern; 27 of 31 follow-up WARNs
  also cleared. 4 left deliberately — see Open backlog #13/#14 below.
- **Backlog #5 (prose-rule audit) DONE** — `_PATTERNS/2026-06-23-prose-rule-enforcement-audit.md`.
  Zero of 6 in-scope `SKILL.md` rules have real enforcement. Headline: "inline styles
  only, no Tailwind, no className" has been violated at `src/app/layout.tsx` since the
  first commit — independently re-verified, not just trusted from the audit.
- **Backlog #7 (Observatory cherry-pick) DONE** — turned out to already be on this
  branch before the session started; the genuinely-missing piece (dead `/observatory`
  rewrite removal from `next.config.ts`) is done and build-verified.
- **Trust contract v1.0 → v1.1** — `_CANON/trust-contract.md` §8 added, answering Zak's
  "how will you catch people at the fork" feedback. Zach's call: new canonical section.
- Full detail: `MEMORY.md` `[v3.2.0]`, `.claude/arcs-session-state.md`,
  `_STATE/branch-observatory-cherry-pick.json` (per-branch state file — this branch's
  work was NOT written into the shared `_STATE/snapshot.json`, per the documented
  serialization protocol for feature branches).

## Open backlog (revised — #5 and #7 done, #13/#14 new)

#1 backup repo (done, prior session) · #2 password rotation (blocked on Zach) · #3
consolidate 3 logs (ready, sequencing point) · #4 drift-sensor (design done, build not
started — long pole) · ~~#5 prose-rule audit~~ **DONE** · #6 DEWY commit stamp (ready
after #3+#5 — #5 now satisfied) · ~~#7 Observatory cherry-pick~~ **DONE** · #8 canonical
S-tier reformat (still deferred) · **#13 NEW** — orphaned Supabase tables
(`meeting_cards`/`risks`/`raci`/`dependencies`/`drift_signals`/`immune_sessions`/
`immune_turns`/`pathogen_log`), no owning app found anywhere, needs Zach's input · **#14
NEW** — 4 remaining Supabase advisor WARNs, left unfixed deliberately (ownership/intent
unconfirmed), not urgent.

## Blocking

None for the next session to start cold on #3, #4(design), or #13. #2 and the separate
`xbbpiryokswwvcrcutge` `DATABASE_URL` rotation risk (ADR-005 amendment — a *different*
password than #2's, don't conflate) both need Zach directly.

## Next session starts at

`/handoff-pickup` → `.claude/arcs-session-state.md` for the fullest current detail.
Recommended: #3 (log consolidation, unblocks #6's retrofit) or #13 (orphaned tables,
just needs Zach to glance at the Supabase dashboard).

---

# Handoff — v3.3.0 (2026-06-30)

> **For Claude Code:** active pickup point. v3.2.0 above is preserved for history.

## What changed since v3.2.0

- **MASSIVE MERGE: sleepy-booth → main SHIPPED** — commit `5db496b`
  - 170 files changed, 42K+ insertions
  - EyebrowToast breadcrumb/drawer (NCI:120-125) — renders covenant drawer, 3 depths, dismiss, responsive
  - Trust/Privacy/Terms pages (NCI:119) — `/trust`, `/privacy`, `/terms` routes + legal links in footer
  - Observatory full page (1174 LOC) — interactive replay theater, dataset switcher, GitHub event ingest
  - Operators library consolidation — 34 files, 16.6K LOC (LAB, BAR, SAGE, CURATOR, KAIROS, CONTRACT, OPERATOR20, KINTSUGI, etc.)
  - Canon documents — ARCS-Canon v1.1 + v2.0, Litepaper, Manifesto, Phenomenology, Yellow Paper, Glossary
  - New ADRs — ADR-025 through ADR-030 (sage signal, debrief delivery, observatory substrate, scan staging, onboarding, nested threads)
  - Prisma migrations — 4 new migrations (debrief sent_at, debrief optin, profile upload, ATG tributaries)
  - Git worktree confusion resolved — initial merge landed on `claude/arcs-care-outstanding-tasks-a6mwaz` (wrong branch); re-merged via `frosty-kepler-b69f51` worktree to proper main
- **Production deploy triggered** — `app.arcs.care` (+ aliases `arcs.care`, `www.arcs.care`, `resume.arcs.care`) now serving commit `5db496b` with breadcrumb/drawer live
- **Dev server running** — port 3000, installed `@vercel/analytics` (dependency brought in by merge), autoPort enabled for future conflicts
- **Missing dependency fix** — `@vercel/analytics@next` was referenced but not installed; added `--save` to package.json

## File status

```
src/ui/EyebrowToast.tsx                    ✅ New — breadcrumb drawer component (383 LOC)
src/ui/StickyFooter.tsx                    ✅ New — sticky footer with legal links fade
src/ui/ToastDrawerContext.tsx              ✅ New — context for drawer state
src/app/trust/page.tsx                     ✅ New — 192 LOC trust contract page
src/app/privacy/page.tsx                   ✅ New — 204 LOC privacy policy page
src/app/terms/page.tsx                     ✅ New — 212 LOC terms of service page
src/app/observatory/page.tsx               ✅ New — 1174 LOC interactive replay theater
operators/                                 ✅ All 34 files committed (arcs_api, arcs_backup, arcs_hc, arcs_lte, arcs_trace, etc.)
_CANON/                                    ✅ All canon documents committed (6 core + glossary + index)
_DECISIONS/index.json                      ✅ New — ADR registry (272 entries)
prisma/migrations/                         ✅ 4 new migrations committed
```

## Compass Kit Phase 2 readiness

Next session begins Compass Kit Phase 2 — promoting the static kit (`public/compass-kit/`) into the real app. Phase 2 handoff exists at `_STATE/compass-kit-phase2-handoff.md`. Immediate next actions:
1. Write ADR deciding DS reconciliation (Option A: extend existing `src/ui/`, Option B: namespace as `src/ui/compass-kit/`)
2. Port atoms to `src/ui/*.tsx` (30+ components)
3. Wire `/dashboard` to real `/api/compass` pipeline
4. Verify preview-deploy parity vs. `/compass-kit` mock
5. Merge to main

This session did NOT touch Compass Kit Phase 2 — all work was merging sleepy-booth (breadcrumb/drawer features) to unblock production.

## Open items

- ADR-015 case study approval gate — Dan Pascone confirmation still pending (blocks NEXT_PUBLIC_CASE_STUDY_APPROVED flip on arcs-care)
- Compass Kit Phase 2 ADR — to be written next session (DS reconciliation choice)
- Production deploy verification — check app.arcs.care/arcs.care for breadcrumb/drawer visibility (should be live within 1–3 min of this session)

## Blocking

NONE for Compass Kit Phase 2 start. All prerequisites are met (main is clean, features merged, dev server running).

## Last confirmed commits

```
arcs-v9: 5db496b — Merge sleepy-booth → main for production breadcrumb/drawer features
```

## Next session starts at

`/handoff-pickup` → Compass Kit Phase 2 ADR + Phase 2 kickoff. Proceed directly to "Write DS reconciliation ADR" unless production verification reveals unexpected issues.


---

# Handoff — v3.4.0 (2026-07-02)

> **For Claude Code:** active pickup point. v3.3.0 above is preserved for history.
> Recovered 2026-07-15 — this section was written in worktree `inspiring-margulis-b8d8b4`
> (branch `claude/inspiring-margulis-b8d8b4`) and never landed on `main`, leaving a gap in
> the handoff chain between v3.3.0 and v3.5.0. The code it describes was already live
> (`1ea5e8a` is an ancestor of `main`); only this documentation was missing. Ported verbatim
> during the worktree-cleanup audit.

## What changed this session

### PRL Resins / Todd Hotes — Phase 1 Proposal SHIPPED

- `src/ui-kit/recoil-report/todd-prl-resins-recoil.html` — 5-section standalone proposal:
  - Header ("Fix the Instrument Panel First"), load-bearing quote (verbatim from call close), Phase 1 sprint card (3×90-min sessions, $1,500 fixed), dimmed on-deck sketch (Phase 2–5), one ask + stop-loss
  - Aviation framing throughout ("flying IFR without instruments") — Todd is an ATP/PC-24 type rated
  - ARCS design tokens, no external deps
- `public/todd-call.html` — copy for static serving
- `next.config.ts` (main) — `beforeFiles` entry added for `todd-call.arcs.care`
- `1ea5e8a` committed and pushed to main; domain live at https://todd-call.arcs.care

### Subdomain HTML hosting workflow — now documented in memory

See memory: `subdomain-html-hosting-workflow.md`

Key lessons:
- `vercel.json` rewrites are overridden by `src/app/page.tsx` — use `beforeFiles` in `next.config.ts`
- Changes must be on `main` (not a worktree branch) — commit via `frosty-kepler-b69f51` worktree
- New subdomains must be explicitly assigned to arcs-v9 in Vercel dashboard if `alias_conflict` error

### Resend MCP plugin — stale API key

`mcp__plugin_resend_resend__send-email` returns 400 `API key is invalid`. Key needs rotation in Resend dashboard → update MCP plugin config. Workaround this session: Zach sent email manually.

## Last confirmed commit (arcs-v9 main)

`1ea5e8a` — fix(routing): todd-call.arcs.care → proposal page [NCI:182]

## Open items

- Resend MCP API key needs rotation (blocks automated email from Claude sessions) — **still unresolved as of 2026-07-15**, confirmed live this session (`plugin:resend:resend` still requires authentication)
- Compass Kit Phase 2 ADR still unwritten (from v3.3.0)
- ADR-015 case study gate — Dan Pascone approval still pending

## Next session starts at

(no further notes captured in the original section)

---

# Handoff — v3.5.0 (2026-07-07)

> **For Claude Code:** active pickup point. v3.3.0 above is preserved for history.

## What changed since v3.3.0

### fanatics.arcs.care — LED + layout sprint COMPLETE

- **LED refactor**: Pulsing LEDs moved from vertical left-rail dots to horizontal SVG waveform timeline circles. Each of the 5 timeline circles has a color-matched `filter: drop-shadow()` animation with staggered timing (`2s`, `2.3s`, `1.9s`, `2.5s`, `2.1s`). Vertical `signal-wire` element and `beat-node` div structure removed entirely.
- **Beat card LED restored** [NCI:209]: `.beat-led` CSS re-added (6px dot, `position: absolute; top: 14px; left: 14px`) for visual color differentiation between beat cards — both card dot AND SVG timeline pulse coexist.
- **Layout regression fixed** [NCI:210]: `signal-sequence` `padding-left` was 44px (left over from the removed vertical rail). Set to `0` on both desktop and mobile breakpoint — provenance beat cards now flush with all other page sections.
- **Subdomain QA**: All 13 deployed subdomains confirmed 200 OK, zero 404s.

### Security constraint (permanent, do not gate these)

fanatics.arcs.care, chris.arcs.care, cj-debrief.arcs.care, chase-intro.arcs.care, token.arcs.care, kelly-interview.arcs.care, todd-call.arcs.care — ungated, no password protection.

## Commits this session (arcs-v9 main)

```
0246df6 — fix(fanatics): remove orphaned signal-sequence indent, align beats with page layout [NCI:210]
(prior commits NCI:205–209 from same session — LED refactor + deploy-prod.sh)
```

## Last production deploy

`dpl_4ANhwAxWA3cG6gHVF5MBh3LXBR2k` — READY, aliased to app.arcs.care + all subdomain aliases.

## Open items

All v3.2.0 open items (#2–14) carried forward unchanged. See `.claude/arcs-session-state.md` for full list.

## Next session starts at

`/handoff-pickup` → julia.arcs.care drill feature (pre-call checklist → verbal drills; clarify interaction model + who are Jack, Jill, Boardy) OR governance backlog #3 (log consolidation).

---



---

# Handoff — v3.6.0 (2026-07-08)

> **For Claude Code:** active pickup point. v3.5.0 above is preserved for history.

## What changed since v3.5.0

### Consolidation audit — arcs-decision-receipts → arcs-v9 COMPLETE

Two commits on main:

**`cf8b084`** — initial consolidation:
- `runtime/specs/field-os/` — 9 field OS spec files from arcs-decision-receipts (artifacts 01–07, jtbd-master-map, arcs-thread-master-report, DRIFT_LOG)
- `next.config.ts` — added missing fanatics.arcs.care and token.arcs.care subdomain rewrites
- `public/templates/call-brief-template.html` — canonical parameterized template with `{{PLACEHOLDERS}}` and authoring workflow comment header
- `_STATE/snapshot.json` — added `ui_artifacts` section (13 active call briefs + ui-kit inventory) and `memory_shards` section

**`b7883fb`** — bar-raiser corrections (3 flags resolved):
- `scripts/kryptonite_scorer.py` → `operators/kryptonite_scorer.py` (atomic decision component, not utility; operator contract header added)
- `scripts/waveform_optimizer.py` → `operators/waveform_optimizer.py` (same)
- `_CANON/arcs-v9-additional/{4 docs}` → `_CANON/living/` (primary doctrine promoted out of supplement folder)
- `_MEMORY/` created with 5 git-tracked product intelligence shards (replaces `~/.claude/projects/` which is machine-local / invisible to cloud sessions)

### Decisions locked (bar-raiser review)

- **monomath-compiler** + **gold-coast**: separate standalone repos, NOT arcs-v9 (different products, would balloon monorepo scope)
- **index.html / deep-activate.html**: audit provenance before porting — unknown active use case
- **field-os specs**: `runtime/specs/field-os/` (not `_ARCHIVE/`) — still-relevant reference spec, not dead history
- **arcs-decision-receipts**: do NOT archive yet — confirm nothing missed first

## File status

```
public/templates/call-brief-template.html       ✅ NEW — canonical template with {{PLACEHOLDERS}}
runtime/specs/field-os/                          ✅ NEW — 9 field OS spec files
_CANON/living/ARCS-v9-Canon-Operational.md      ✅ PROMOTED (was arcs-v9-additional/)
_CANON/living/ARCS-Codex-v8.5.md               ✅ PROMOTED
_CANON/living/ARCS-Positioning-JTBD.md          ✅ PROMOTED
_CANON/living/ARCS-Technical-Overview-April2026.md ✅ PROMOTED
_MEMORY/                                         ✅ NEW — 5 git-tracked intelligence shards
operators/kryptonite_scorer.py                   ✅ MOVED from scripts/
operators/waveform_optimizer.py                  ✅ MOVED from scripts/
_STATE/snapshot.json                             ⚠️ 6 DAYS STALE — run /init-state-sync
```

## Last confirmed commits (arcs-v9 main)

```
b7883fb — chore(consolidation): bar-raiser corrections — operators/, _CANON/living/, _MEMORY/ [NCI:SKIP]
cf8b084 — chore(consolidation): port arcs-decision-receipts unique content [NCI:SKIP]
```

## Next session starts at

`/handoff-pickup` → `/init-state-sync` to refresh stale snapshot → then: julia.arcs.care drill feature OR governance backlog #3 (log consolidation, unblocks #6).


---

# Handoff — v3.7.0 (2026-07-17)

> **For Claude Code:** active pickup point. v3.6.0 above is preserved for history.

## What changed since v3.6.0

### chan.arcs.care built end-to-end — Prophet/Chan Suh discovery-call artifact

Iterated across ~20 commits in one session, starting from an `/ultrareview`-style audit of
the existing page against the Mike Lemon recoil report:

- **Player/Coach/Pacecar** identity frame + prior-terrain (pre-ARCS) résumé receipts, visually
  separated from the ARCS-build era
- **Instrument-panel section** — 12 design principles (traceability, anti-hallucination,
  anti-sycophancy, provenance, etc.), each stating where it's actually enforced, plus a
  hand-authored SVG of the real compounding architecture loop (question → L0–L5 pipeline →
  receipt → outcome → calibration → sharper next decision)
- **Conductor-lane telemetry** — real git-trailer data (which Claude model authored each
  week's commits) as a tabbed view against commit cadence, with click-to-unlock narrative
  cards (the 5 quiet design weeks; "building at the edge" model-rotation story)
- **16-slide presentation mode** — SEEN/HEARD/VIBE-CHECK discovery structure, provenance-graded
  per slide (glow = confidence, using the canonical `--glow-*` tokens), Maya Lin-style
  pointer-terraformed moiré topography, 2.5D isometric floor, a left-edge "fathom" progress
  rail, chrome that auto-hides after 2.6s idle, right-click on the closing slide as an escape
  hatch back to slide 1. A wireframe Möbius-strip opening flight was built, then **removed**
  on explicit budget-conscious direction — land-the-plane took priority over the animation.
- **Full design-system conformance pass** — pulled the canonical token file
  (`colors_and_type.css`) live from the "ARCS OS - Design System" Claude Design project via
  `DesignSync`, migrated all 81 freehand font-sizes onto the canonical 8-step `--text-*`
  scale, swapped fonts to Inter + JetBrains Mono (the only two the project's own adherence
  linter permits), tokenized radii to the canonical 3/6/10/16/999 scale
- **Progressive disclosure** — FOCUS-mode-by-default (only section 1 open, rest collapsed to
  headline + one-line TL;DR), EXPAND ALL as the alternate control
- **PII removed** (email + phone from the footer); `noindex, nofollow` confirmed already
  present, no `robots.txt` override exists on either domain

### status.arcs.care — standalone fork

Forked from `chan.html` via anchor-based excision (not hand-editing): Prophet-specific
content (echo-map, Player/Coach/Pacecar frame, prior-terrain creds) and the entire
presentation deck (~250 lines of JS/DOM/CSS) surgically removed; sections renumbered 01–07.
Routed via `next.config.ts`. **Gotcha:** the deploy script's domain pre-flight reported
`status.arcs.care` already assigned when it wasn't — had to attach it to the Vercel project
directly via the API (`POST /v10/projects/{id}/domains`) before it would resolve.

### Two real mobile bugs — found only from actual device photos, not simulator resizing

The user sent 3 HEIC screenshots from a real iPhone. **The Read tool cannot render HEIC
directly** (returns raw container metadata) — converted via `sips -s format png` first, every
time, before they could actually be viewed.

1. `.echo-mid`'s mobile rule used `transform: rotate(90deg)` on a full-width flex box to turn
   "↔" into "↕" on the stacked single-column mobile layout. **CSS transforms repaint an
   element in its rotated orientation but do not change its layout footprint** — the rotated
   glyph + its border lines visually overflowed above/below the short-wide box they still
   occupied, reading as a disconnected floating icon with odd gaps. Fixed by dropping the
   rotation entirely and swapping the glyph via `font-size:0` + `::after` content instead.
2. The architecture-loop SVG diagram is legitimately wider than a phone screen and
   horizontally scrollable (`overflow-x: auto`), but mobile Safari hides scrollbars until an
   active drag, so the hard-truncated right edge read as broken content. Added a right-edge
   fade mask + explicit "SWIPE FOR THE FULL LOOP" hint, mobile-only, gated so it only shows
   when the container is actually scrollable.

Also fixed in the same pass (caught from a desktop screenshot, before the mobile-photo
round): presentation chrome (top/bottom bars) was drifting left/right slide-to-slide because
`flex; justify-content: space-between` centers the middle block *relative to the width of its
flanking siblings*, not true viewport center — act-labels and chips vary a lot in text length
slide to slide, so the centered readout visibly jumped. Converted both bars to CSS grid
(`1fr auto 1fr`) with **explicit `grid-column` pins** — required because mobile hides some
children via `display:none`, and grid auto-placement would otherwise shove the survivors into
the wrong column. Verified across all 16 slides: identical center x-coordinate every time.
Also: the isometric floor's `perspective(560px)` was a fixed px value that broke down on an
ultrawide monitor and at high browser zoom (a fixed focal length against a much-wider element
swings the far edges out past the frame) — changed to `perspective(70vh)` so it scales with
viewport height regardless of width or zoom.

## Session pattern worth repeating

Every fix in this session was verified against the **live production domain** via direct
`curl` grep for the specific CSS rule / string that changed — not just "deploy succeeded."
Several deploys landed on a stale `main` mid-session because another concurrent session
pushed commits in between fetch and merge; the fix each time was `git fetch origin main -q
&& git rebase origin/main` on the feature branch before re-attempting the fast-forward merge,
never a force-push over the other session's work.

## File status

```
public/chan.html    ✅ ~20 commits, fully verified live on chan.arcs.care
public/status.html  ✅ NEW — forked from chan.html, verified live on status.arcs.care
next.config.ts      ✅ status.arcs.care route added
```

## Last confirmed commit (arcs-v9 main)

`c536792` — fix(chan): mobile echo-mid connector no longer overflows its row; scroll cue on
the architecture diagram [NCI:SKIP]

## Blocking

NONE. Two untracked files sit in the main worktree from unrelated prior work
(`_DECISIONS/ADR-026-debrief-calendar-invite-vs-email.md`, `test_prisma_direct.js`) — not
touched this session, flagged for whoever owns that thread to commit or discard.

## Next session starts at

`/handoff-pickup` → no open thread on chan/status.arcs.care (last ask was mobile QA, verified
live). Otherwise: julia.arcs.care drill feature OR governance backlog #3 (log consolidation,
unblocks #6 DEWY commit stamp) remain open from prior sessions.

---

---

# Handoff — v3.8.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.7.0 above is preserved for history; v3.6.0 and older were
> relocated to `_ARCHIVE/handoffs.md` per the lean-file policy this session established.
> Branch `claude/token-efficiency-audit-ip3l3x` — **MERGED to main** (verified 2026-07-19: main contains
> the lean CLAUDE.md ≈3.7k tok + MEMORY.md ≈6.5k tok; branch is an ancestor of `main`).

## What this session did (17 commits, `c2eaf80`..`117fcf0`)

A token/budget efficiency audit that turned into a fix chain. Full narrative in `MEMORY.md [v3.8.0]`;
per-topic detail in the `_PATTERNS/2026-07-19-*` docs.

- **Audit + Fix #1/#2:** the real #1 token drain was the append-forever CLAUDE.md/MEMORY.md loaded every
  session (~24.6k–39k tok), not the Sentinel. Split dead history to `_ARCHIVE/`; CLAUDE.md 19.8k→3.6k,
  MEMORY.md 14.8k→5.8k; amended the append-only policy to lean-working-file + archive.
- **ADR-035:** ratified the real Commit-NCI rubric (5 lenses); wired `nci-scoring` skill + `/nci-commit` +
  `/drift-check`. Added `/rca` (triage-gated root-cause command).
- **Tech-debt batch** (`_PATTERNS/2026-07-19-tech-debt-batch.md`): A1 console cleanup, A5/A6 fixes, B1
  diagnosed clean, A2/A3/A4 triaged out. **B4** build-red root-caused to shell `NODE_ENV=development` →
  pinned `NODE_ENV=production` in the build script (use `npm run build`, not bare `npx next build`).
- **B2:** implemented the spec 5-lens `nci_by_lens`/`nci_grade` (additive), surfaced weak-lens in the brief,
  added a `stop_reason` truncation guard.
- **Security:** `_PATTERNS/2026-07-19-threat-assessment.md` + `src/lib/sanitize.ts` (unit-tested 8/8) —
  trust boundary at every recursive rung against injection cascade.

## Open items (also in `_QUEUE/PENDING.md`)

- ~~**Merge this branch to main**~~ ✅ DONE 2026-07-19 — merged; lean CLAUDE.md/MEMORY.md confirmed on main.
- **Out-of-band** (`_PATTERNS/2026-07-19-out-of-band-actions.md`): Sentinel — DISABLED 2026-07-19; rebuild
  **report-only** from the `arcs-decision-receipts` env using the full recipe in
  `_PATTERNS/sentinel-rebuild-spec.md`. Also: SageTrace RLS (Supabase CLI), connector/env/DNS/key items,
  Dan Pascone gate.
- **In-repo follow-ups:** cadence lens from time-ROM; HOLD gate at NCI<40 (overlaps the Calibrate HOLD gap).

## Honesty flag

All compass-side changes are build + typecheck + unit-tested, but **NOT driven via a live compass call**
(no `ANTHROPIC_API_KEY` in the cloud session). Verify end-to-end after merge/deploy.

## Last confirmed commit

`117fcf0` — feat(security): trust boundary at every recursive rung.

## Next session starts at

`/handoff-pickup` → merge is done; pick an out-of-band item (Sentinel rebuild, SageTrace RLS) or the
B2 cadence/HOLD-gate follow-up.

---

# Handoff — v3.9.0 (2026-07-19)

> Relocated from CLAUDE.md 2026-07-20 (lean-file policy). Detail: `MEMORY.md [v3.9.0]`.
> Two feature PRs shipped to main this session (both MERGED).

## What shipped

- **Token-efficiency audit (PR #62) - MERGED.** Detail: `MEMORY.md [v3.8.0]` + `_PATTERNS/2026-07-19-*`.
  CLAUDE.md/MEMORY.md lean split; ADR-035 Commit-NCI rubric + `nci-scoring` skill + `/nci-commit` +
  `/drift-check` + `/rca`; tech-debt batch; B4 NODE_ENV build fix; B2 5-lens `nci_by_lens`; recursive
  trust-boundary sanitizer (`src/lib/sanitize.ts`).
- **Stateless anonymous brief sharing (PR #100, ADR-037) - MERGED.** Detail: `MEMORY.md [v3.9.0]`. Anon
  bearings shareable via URL-fragment payload (zero server write); recipient recomposes client-side;
  one-view localStorage gate -> `/compass?shared=1` onramp. `src/lib/shareLink.ts` (sanitizes the
  attacker-controllable payload), `/brief/share`, receipt-page "Share" (ephemeral only). Trust-contract
  **v1.3** amended canonical-first (`_CANON/trust-contract.md`), then derived /trust + /privacy. A
  `privacy-review` agent gated it (caught that the canonical doc hadn't been amended - fixed before merge).
- **Branded receipt error/fallback page** (part of #100) - replaced bare red text with Wordmark + card +
  adaptive CTAs (anon-not-here vs load failure).

## Honesty flag (carry forward — CLOSED by v3.11.0 persist fix `403d109`)

Compass-side changes (B2 5-lens, sanitizer, anon-share) are build + typecheck + unit-tested but **NOT driven
via a live compass call** (no `ANTHROPIC_API_KEY` in the cloud session). **Verify after deploy:** run the
compass anonymously -> Share -> open the link in another browser -> confirm one-time recompose -> onramp.

## Open items (also in `_QUEUE/PENDING.md`)

- **Out-of-band** (`_PATTERNS/2026-07-19-out-of-band-actions.md`): Drift Sentinel disabled by operator
  2026-07-19, rebuild report-only (`_PATTERNS/sentinel-rebuild-spec.md`); SageTrace RLS (Supabase CLI);
  **Vercel platform toolbar** -> disable in dashboard (Settings -> Toolbar); connector/env/key hygiene.
- **In-repo:** B2 cadence lens from time-ROM; HOLD gate at NCI<40 (overlaps Calibrate HOLD gap); the
  Receipt-save-prompt PLG gap.

## Concurrency note

A second session ran on main this whole session (J-items: leak-check gate, watchdog, status board, VOICE
rules). The ADR namespace is lock-free - `ls _DECISIONS/` right before claiming a number (035=commit-nci,
036=repo-split, 037=anon-share). Rebase on origin/main before any push.

## Next session starts at

`/handoff-pickup` -> live-verify the anon-share flow on the deployed site; then an out-of-band item or the
B2 cadence / HOLD-gate follow-up.

---

# Handoff — v3.10.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.9.0 above preserved; v3.8.0 relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy. (A tracker drift observed mid-session —
> CLAUDE.md at v3.8.0 while MEMORY.md was at v3.9.0 — was healed concurrently by the
> v3.9.0 session's own handoff; noted here because it is a live receipt of the exact
> pathogen this session codified.) Full detail: `MEMORY.md [v3.10.0]`.

## What changed (this thread, 2026-07-17→19)

**The serialization pathogen family** — codified, ratified, enforced:

- **ADR-033 DECIDED** (`_DECISIONS/ADR-033-serialization-pathogen-family.md`,
  GREEN/HIGH/REVISIT, ratified by Zach 2026-07-19). One axiom: a serialized belief is a
  tuple (claim, time, scope, warrant, obligations, dictionary); each family member is one
  coordinate silently dropped. time→chronos-sequencer · scope→inductive-overfit ·
  obligation→open-loop decay · warrant→epistemic-sequencer · dictionary→etymology-sequencer.
  4-part admission gate stops taxonomy sprawl.
- **`runtime/specs/recoil-modes-v1.md` → v0.4.0** — readOrder + `[SUPERSEDED]` markers +
  always-current cover (chronos); `validityBounds` {n, conditions, stationarity} with the
  n-aware regime ladder, tails/edges excepted at any n (inductive-overfit); riskFlags
  `status` OPEN/DONE/WAIVED — closure is an explicit write, never silence (open-loop).
- **`runtime/specs/call-brief-hooks-v1.md` → v1.1.0** — read current state first; never
  quote a stratum without a superseded-marker check.
- **Detective** (`scripts/receipt_lookup.py`): superseded-skip, n-aware Read,
  validityBounds surfacing, and **`--sweep`** — first run: **52 open obligations across
  20 reports, zero ever closed** (oldest 18d; incl. a 10-day-old HIGH).
- **First documented closure:** enforcement-parity ledger (stranded unmerged 3 days;
  memory had it serialized as live law) merged as **ADR-034** (PR #63), renumbered per
  ADR-033's own rule. Jurisdictions: ADR-034 ledger = repo/audit findings; `--sweep` =
  call-ledger obligations.

## Open from this thread

1. **Sweep backlog** — 52 open riskFlags await owner `DONE`/`WAIVED` writes.
2. **ADR-032 duplicate** — two files share the number; dedupe/renumber.
3. **Epistemic + etymology members** — partial mechanisms only; dedicated enforcement
   (warrant field on banked claims; rename tombstones) not yet built.

## Last confirmed commits (this thread)

`9748048` · `15d71d8` · `9ce0dfc` · `09bb14b` · `5f181fc` (+ this handoff commit)

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → live-verify anon-share (v3.9.0 honesty flag) or run
`python3 scripts/receipt_lookup.py --sweep` and start closing the oldest flags.


---

# Handoff — v3.11.0 (2026-07-20)

> **For Claude Code:** archived 2026-07-21 per lean-file policy — superseded by v3.12.1's
> closure of the standby auth-loop test. Full detail: `MEMORY.md [v3.11.0]`.
> Interactive (local Claude Code) session — deployed live, unlike the prior cloud sessions.

## What shipped (this thread, 2026-07-20)

- **Anon-share "Sign in to keep" persist fix (PR #121, `403d109`).** The v3.9.0 honesty-flag
  follow-up: the shared bearing was recomposed one-time but NOT carried through sign-in — "keep"
  kept nothing. Now the onramp writes `arcs_pending_save` and `ClaimAnonymousReceipts` claims it
  post-auth → user lands on `/receipt/<id>` with the bearing saved. (One-time link + recompose
  verified live by operator; the full magic-link auth leg is the standby test below.)
- **Design-system glow tuning, two passes** (`8429f2e` then `cfbc483`). Operator feedback: glow
  too hot across the board. Pass 1 — `signalGlow()` alphas halved (.55–.6 → ~.28) + bloom blur
  cut ~33% (Gauge 16→11px, Card/Badge 12→8px, recoil `_tokens.css` 12→5px). Pass 2 (eyeball) —
  gauge bloom eased back 11→13px, accent card glow reduced, `TrueNorthPanel` given real
  glassmorphism (`backdrop-filter: blur(14px)` + translucent blue fill), Field/select left as-is
  (operator confirmed correct). Every change verified against **live computed styles**, not by eye.

## Open items (operator-approved, not started)

1. **Ledger management** — give users archive + reset-reflection before hard-delete. Build order
   confirmed: **archive/reset first, hard-delete last** (WORLD.md: receipts are frozen positions;
   soft-retire preserves Observatory/lineage, true erasure is the explicit escalation).
2. **Authenticated `/recoil` index** — a ledger of internal recoil/precall briefs behind OAuth.
   Build order confirmed: **index the existing brief documents first** (data already in
   `snapshot.json → ui_artifacts`), DB-backed entities later. Also improves security posture over
   the current per-name password gates.

## Standby (needs operator go) — RESOLVED 2026-07-21, see v3.12.1

- **Production auth-loop test** — drive "Sign in to keep" end-to-end via the Gmail connector
  (read the magic-link email, click it, confirm `/receipt/<id>`). Closes the v3.9.0 honesty flag.
  Needs explicit go + confirm `zach.harris@gmail.com`. Authenticates a session + writes one
  `EPHEMERAL_SAVE` test receipt.
- **Glow strays** — sweep hardcoded glows the tokens didn't reach (neutral `∞` gauge still at
  rgba(160,180,210,.35), observatory page, receipt widget, loaders) for full consistency.

## Concurrency note

Another thread committed on main during/after this session (`4bf8043` sentry inchworm, `efc836a`
meta-audit) plus two untracked strays (`_DECISIONS/ADR-026-*.md`, `test_prisma_direct.js`) — NOT
this session's, left untouched. `ls _DECISIONS/` + rebase on origin/main before any push.

## Blocking

NONE.

---

# Handoff — v3.12.0 (2026-07-20)

> **For Claude Code:** archived 2026-07-21 per lean-file policy (superseded by v3.12.1/v3.12.2 in
> CLAUDE.md). Full detail: `MEMORY.md [v3.12.0]` and `project_todd_hotes_prl_resins.md`.

## What shipped (this thread, 2026-07-20 evening)

**Todd Hotes / PRL Resins — Phase 1 chatbot proposal build-out.** Todd verbally agreed to
the $1,500 chatbot on a Jul 20 call and answered the sales-manager discovery questions
himself by email that evening ("I know the answers lol"). This thread turned that into a
buy-in-ready proposal page, while explicitly NOT starting the actual bot build:

- Sanitized + rewrote `public/todd-call.html` / `public/todd-teardown.html`: plain-English,
  chatbot-foregrounded, zero em-dashes (new standing rule, see `writing-avoid-emdashes-plain-language`
  memory).
- **Discovery section** — Todd's own answers folded under each question ("TODD →"), plus a
  gold "Still needed from your sales manager" box (exact form fields, territory map, resin
  nomenclature) with its own copy-as-plain-text button.
- **How It Works section** (new) — plain-language 3-step client-facing flow, built
  specifically so Todd has something concrete for his internal sales-team buy-in
  conversation before Wednesday.
- **Live Stripe buy button** embedded top of page (`$1,500 · Pay Invoice`), iterated 3x on
  visual feedback into a 2-column deal+payment lockup with a full-width "to start" bar below.
  Todd says by text he'll likely call the payment in instead.
- **Branch-logic tree v1** (the actual Tidio conversation design) drafted from Todd's
  answers and preserved in three places: git spec
  (`runtime/recoil/generated/2026-07-20-todd-chatbot-branch-logic-v1.md`), the live How It
  Works section, and a published Claude Artifact
  (`https://claude.ai/code/artifact/e459357f-af02-4c0a-b58d-e9d1b4d7fe13`, private).
- Drafted + sent the sales-manager discovery-questions email to Todd (Gmail).

**Explicit distinction held throughout:** "on hold" means don't touch Todd's
WordPress/SugarCRM and don't start the Tidio build — it does NOT mean stop updating the
proposal page. The page keeps getting built out for his internal buy-in use; the actual
bot build waits for his go **and** payment.

## Open from this thread

1. **Awaiting Todd** — his Wednesday sales-manager ("Imagine") meeting for internal buy-in,
   then he "reaches back out." Tentative cadence: Wed SM call (Zach may join, busy
   10:30–11 / 2:30–3) → Thursday ~10am regroup.
2. **SM identity unconfirmed** — possibly William Galla (VP Sales, Polymer Resources); kept
   off the live page, only briefly used in an early (superseded) email draft.
3. **Payment method** — Todd prefers to call in a card rather than click Stripe; may want a
   secure upload link for W-9/tax info later.
4. **Do not start the build** (WordPress/SugarCRM access, Tidio flow) until Todd's go +
   payment land.

## Blocking

NONE (waiting on the client, not internally blocked).
