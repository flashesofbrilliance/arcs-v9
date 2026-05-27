# ARCS v9 — Memory Log

> **Versioning convention:** append new entries at top; never delete prior versions.
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v0.8.0] 2026-05-27 — Housekeeping: stale Part IV draft deleted, exports/ gitignored, GitHub Projects board created

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: FleetView / Claude Code
- Session goal: Clean repo state, scaffold GitHub Projects board

### Artifacts landed

| Action | Detail |
|---|---|
| Deleted | `_CANON/book-ii/part-iv-sessions-api.md` — stale DO NOT COMMIT draft; canonical Part IV already exists |
| Updated | `.gitignore` — added `exports/` to suppress scan output files |
| Created | GitHub Projects board — `https://github.com/users/flashesofbrilliance/projects/1` |

### GitHub Projects board structure
- **Title:** ARCS v9 — Canon & Product
- **Stage field:** Not Started → Research → Receipt → Build → Refine → QA → Done
- **Issues linked:** #1–#5 (all Done)
- **Book II Part cards:** Parts I–VI (all Done)
- **Use:** Add new sprint issues/cards and move them forward as work progresses; `/handoff` can update card stages

### No blocking question

---

## [v0.7.0] 2026-05-27 — Book II Parts V & VI promoted to CANONICAL; Issue #5 COMPLETE; dual-bar-raiser skill registered

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) — drift detection / memory repair session
- Session goal: Reconcile MEMORY.md drift (v0.5.0 → v0.7.0); close Issue #5

### Artifacts landed (not previously logged)

| Commit SHA | File | What it is |
|---|---|---|
| `087ef22` | `_CANON/book-ii/part-v-the-accumulation-protocol.md` | CONDITIONAL CLEAR applied — 10 upstream audit findings addressed (§5.1–§5.6); three-state receipt taxonomy, constitutional range formally defined, mandatory debrief scoped to lineage-citing sessions |
| `087ef22` | `_CANON/book-ii/part-vi-the-shared-court.md` | CONDITIONAL CLEAR applied — 9 findings addressed (§6.1–§6.5); L5 presence rule for co-signing, gate-refusal→HOLD→Arbitration routing, formal declaration mechanism |
| `b6e59e4` | Both Part V + VI | **Promoted to CANONICAL v1.0.0** — Architect ratification received 2026-05-26; no further structural changes required |
| `05312cb` | `.claude/arcs-dual-bar-raiser.md` | Dual-bar-raiser skill — two-agent workflow (Claude Code owns edits/commits; Architect/Bar-Raiser owns canon structure + upstream audits) |

### Sprint closure

| Issue | Status |
|---|---|
| #2 DEWY Receipt Schema | ✅ DONE |
| #3 Time ROM | ✅ DONE |
| #4 Compass → DEWY Flow | ✅ DONE |
| #5 Book II Canon | ✅ DONE — All 6 Parts CANONICAL |

**Issue #1 (P0 Backlog Sprint 1) — COMPLETE.** All sub-issues resolved.

### Book II canon final status

| Part | Title | Status |
|---|---|---|
| I | From Firehose to Compass | ✅ CANONICAL |
| II | Core ROM Axioms | ✅ CANONICAL |
| III | Constitutional Court & Agency | ✅ CANONICAL |
| IV | (held — see v0.4.0) | ✅ CONDITIONAL CLEAR → CANONICAL |
| V | The Accumulation Protocol | ✅ CANONICAL v1.0.0 |
| VI | The Shared Court | ✅ CANONICAL v1.0.0 |

### Open gaps (carry forward)

```
globals.css                     🟡 DECISION NEEDED — Tailwind import vs. WORLD.md inline-styles-only rule
.env.example                    🟡 LOW — stale FastAPI/Railway refs (ARCS_API_URL, ARCS_API_KEY)
P4: arcs-v9 → Vercel preview    🟡 IN PROGRESS — blocked on DATABASE_URL + Supabase keys
NCI progressive grading         📋 BACKLOG — cross-session tracking not yet implemented
```

### Next move for next session
1. Decide next sprint: P4 Vercel deploy unblock OR new canon/feature sprint
2. If deploy: Supabase dashboard → Settings → Database → Connection strings → set on Vercel → `prisma db push` → `vercel deploy`
3. If canon: new sprint scoping needed (Book III? Observatory? ATG?)

---

## [v0.6.0] 2026-05-26 — Book II Part VI drafted (The Shared Court); dual-bar-raiser workflow established

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main)
- Session goal: Draft Book II Part VI; establish two-agent workflow protocol

### Artifacts landed this session

| Commit SHA | File | What it is |
|---|---|---|
| `6fece14` | `_CANON/book-ii/part-vi-the-shared-court.md` | Part VI v0.1.0 DRAFT — §6.0–§6.6, The Shared Court |
| `05312cb` | `.claude/arcs-dual-bar-raiser.md` | Two-agent workflow skill (INFRA) |
| `94f04b6` | `.claude/arcs-session-state.md` | Session handoff v0.6.0 |

### Part VI architecture decisions (locked before drafting)
- Witness = receipt annotation only; two standing roles: Initiator + Respondent
- Quorum = unanimity of being bound (not agreement)
- Refusal to accept bound dissent → HOLD or Arbitration Session
- §6.3 quorum paragraph ratified verbatim

### Part VI section summary
- §6.0: single-agent ceiling — structural gap, not edge case
- §6.1: Initiator / Respondent standing (binary); witnesses as annotation
- §6.2: Dissent Record as first-class receipt field; bound dissent requires name + scope + acknowledgment
- §6.3: deliberation protocol — L1 framing, L3 stakes, L4 dissent acknowledgment; quorum rule
- §6.4: co-signed delta gates — same quorum; no veto on gate values, only bound dissent; L5 presence rule
- §6.5: Arbitration Session — 3 preconditions; narrow jurisdiction; no retroactive lineage alteration
- §6.6: hard boundaries — power asymmetry (scope limit), bad-faith (auditable only), scope capture (party discipline)

### Upstream audit status at handoff
Parts V and VI DRAFT held — pending upstream ARCS audit (audit subsequently completed; see v0.7.0).

---

## [v0.5.0] 2026-05-26 — Book II Part V drafted (The Accumulation Protocol); §5.7 Calibrate/HOLD cross-link; not yet committed

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) — canon drafting session
- Session goal: Draft Book II Part V; integrate JTBD D / Calibrate connection into §5.7

### Artifacts landed this session

| File | Status | Notes |
|---|---|---|
| `_CANON/book-ii/part-v-the-accumulation-protocol.md` | 🟡 Written, not committed | §5.0–§5.7, v0.1.0, DRAFT held |

### Key decisions

- **Part V scope locked:** The Accumulation Protocol — the signal layer that prevents the Frozen Court Problem
- **Three primitive chain:** delta gates → kairos detection → accumulation loop (5-step, 3 modes)
- **Two guard layers:** drift detection (CLEAR/WATCH/DRIFT → Part III escalation) + debrief session (first-class session type, calibration receipt)
- **Boundary section (§5.7):** Three failure modes accumulation cannot fix: value drift, scope creep, malformed original question
- **§5.7 Calibrate note:** Malformed-question failure mode linked to JTBD D / Calibrate surface / HOLD gate / anticipatory probing — Part V handles what survives the HOLD check; was never designed to substitute for it
- **`signal layer` casing:** lowercase throughout §5.2–§5.7; standardize before v0.2.0 (copyedit only)

### Cross-repo connection confirmed

Part V §5.7 → `arcs-field-os/jtbd/jtbd-master-map.md` (JTBD D→A→C→B = Calibrate→Orient→Chart→Detect loop). Part V is architecturally downstream of the Calibrate surface.

### Upstream audit status

Part V is DRAFT held pending upstream ARCS audit. Same protocol as Parts I–IV. When packet returns, translate to section-keyed annotations (§5.x sentence-anchored).

### Next session first action

```bash
git add _CANON/book-ii/part-v-the-accumulation-protocol.md
git commit -m "feat(canon): Book II Part V — The Accumulation Protocol v0.1.0 [NCI:DRAFT]"
```

Then submit for upstream audit.


---

## [v0.4.0] 2026-05-26 — Book II Parts I–III canonical; Issue #4 flow doc; upstream audit protocol updated; Part IV draft held

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main) + arcs-intel-protocol
- Session goal: Run upstream audit protocol review, close Issue #4, complete Book II Parts I–III canon sprint

### Artifacts landed this session

**arcs-v9:**

| Commit SHA | File | What it is |
|---|---|---|
| `f722c05` | `runtime/flows/question-compass-to-dewy.md` | Issue #4 — L0–L5 spec-vs-impl flow doc with HOLD/REJECT branch map and 9-item implementation debt register |
| `4db431a` | `_CANON/book-ii/part-i-firehose-to-compass.md` | Book II Part I — CANONICAL (2 upstream patches: PARADOX definition, DELTA rate-of-change framing) |
| `ff72993` | `_CANON/book-ii/part-ii-rom-axioms.md` | Book II Part II — CANONICAL (3 upstream patches: NOTOMATION verbatim, genome table L4 scoped, RC-II-003 EMPIRICAL) |
| `24c2ad3` | `_CANON/book-ii/part-iii-constitutional-court.md` | Book II Part III — CANONICAL (4 upstream patches: H/H/W stubbing rule, relief heuristic observational, causal chains on cost receipt) |

**arcs-intel-protocol (remote):**

| Commit SHA | File | What it is |
|---|---|---|
| `a461d60` | `prompts/arcs-upstream-audit-v1.md` | Updated to reference MEMORY.md v4.0 (was v3); Stage 2E boot sim updated to §9 |
| `f82195e` | `CHANGELOG.md` | v3 retired; two-gate pipeline documented; open gaps listed |

### Open gaps

```
_CANON/book-ii/part-iv-sessions-api.md      🟡 DRAFT — held for upstream audit (untracked, not committed)
_CANON/book-ii/part-v-pilots-receipts.md    🔴 NOT STARTED — depends on Part IV commit
prompts/debrief-session-invocation.md       🔴 NOT EXISTS — referenced this session, create next time arcs-intel-protocol in scope
prompts/one-shot-claude-code-cold-start.md  🔴 NOT CREATED (arcs-intel-protocol)
_MARKETING/arcs-positioning.md              🔴 NOT CREATED (arcs-intel-protocol)
globals.css Tailwind import                 🟡 DECISION NEEDED
NCI <40 HOLD gate (compass/route.ts)        🔴 CRITICAL impl debt (Issue #4)
W-field HOLD gate (compass/route.ts)        🔴 CRITICAL impl debt (Issue #4)
```

### Protocol decisions this session

- MEMORY.md v4.0 = canonical cold-start seed; v3 retired (never committed, superseded)
- Two-gate pipeline (Perplexity/Comet → Claude Code) = canonical Book II authoring protocol
- Issue #4 two-column SPEC/IMPL format = canonical pattern for all `runtime/flows/` docs

### Next move
1. Read `SESSION-HANDOFF-2026-05-26.md` (cold-start seed for this session's work)
2. Run upstream ARCS audit on `_CANON/book-ii/part-iv-sessions-api.md`
3. Apply patches → update status to CANONICAL → commit Part IV
4. Draft Part V — Pilots and Receipts

---

## [v0.3.0] 2026-05-26 — Issues #2 + #3 complete; Y-gate enum alignment; staleness audit

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Claude Code (`arcs-v9` main)
- Session goal: close Issues #2 and #3, run full staleness audit, align implementation to canonical DEWY schema

### Artifacts landed this session

| Commit SHA | File | What it is |
|---|---|---|
| `38aa0f6` | `runtime/specs/dewy-receipt-schema-v1.md` | Human-readable DEWY receipt schema companion (Issue #2) |
| `38aa0f6` | `prisma/schema.prisma` | 15+ canonical DEWY fields added; legacy fields preserved with mapping comments (Issue #2) |
| `ac4af35` | `runtime/specs/time-quality-attribution-rom.json` | Time Quality Attribution ROM — W-field inference, DRIFT Sentinel, Kairos Lock, macro triggers (Issue #3) |
| `9d2909a` | `.claude/commands/handoff.md` + `handoff-pickup.md` | Slash commands added by Zach |
| `22cac6e` | `SKILL.md` v0.3.0 | Domain #7 (Session Commands) registered; priority queue updated |
| `61095c5` | `src/lib/ygate.ts` | Y-gate rewritten to canonical enums (polarity×conviction×stability); driftState + yGateScore added |
| `61095c5` | `src/app/dashboard/page.tsx` + `brief/page.tsx` + `history/page.tsx` | Stale enum labels replaced with canonical values |
| `61095c5` | `.claude/arcs-canon.md` | Y-gate table corrected to canonical polarity enum |

### Staleness audit findings (all resolved)

| Item | Status |
|---|---|
| `ygate.ts` polarity/conviction/stability enums | ✅ Fixed — canonical schema enums |
| `dashboard.tsx` + `brief/page.tsx` + `history/page.tsx` stale labels | ✅ Fixed |
| Root scan artifacts (6 files + `arcs@0.1.0`) | ✅ Deleted (were gitignored, now gone from tree) |
| `arcs-canon.md` EPHEMERAL/RED in Y-gate table | ✅ Fixed |
| `CLAUDE.md` + `MEMORY.md` stale sprint status | ✅ Updated (this entry) |
| `globals.css` Tailwind import | 🟡 OPEN — font vars may be load-bearing; Zach to decide purge vs. keep |
| `.env.example` FastAPI/Railway stale refs | 🟡 LOW — cosmetic; `ARCS_API_URL`/`ARCS_API_KEY` not wired to anything |

### Open gaps

```
runtime/flows/question-compass-to-dewy.md   🔴 CREATE — Issue #4 (NEXT, unblocked)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — Issue #5 (blocked on #4)
arcs-field-os/specs/hold-reject-gate.md     🔴 NOT YET WRITTEN — orient-prd.md §2.2 authoritative
globals.css                                 🟡 DECISION NEEDED — Tailwind import vs. WORLD.md rule
```

### Next move for next session
1. Read `CLAUDE.md` → Handoff v0.3.0 (active pickup point)
2. Start Issue #4: `runtime/flows/question-compass-to-dewy.md`
3. Governing spec: `arcs-field-os/specs/orient-prd.md` §3 L0–L5 pipeline

---

## [v0.2.0] 2026-05-26 — Perplexity session: Orient PRD, DEWY schema, handoff v0.2.0 + post-handoff Claude Code commits

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: push Orient PRD (Kairos Lock), DEWY receipt JSON schema, updated handoff file, MEMORY v0.2.0
- Kairos Lock declared on `arcs-field-os/specs/orient-prd.md` — breaking changes require v0.2.0 + PR

### Artifacts pushed this session

#### arcs-field-os
| Commit SHA | File | What it is |
|---|---|---|
| `618022004033d72b` | `specs/orient-prd.md` v0.1.0 | Governing authority for Orient surface. Kairos Lock active. L0–L5 pipeline fully specced with worked examples. NULL/OM/UNDEFINED coverage at every stage gate. |
| `79b7261` (prior) | `jtbd/jtbd-master-map.md` v0.1.0 | Canonical four-surface architecture (Calibrate → Orient → Chart Course → Detect) |
| (prior) | `specs/index.md` | Spec registry with authoring priority queue |

#### arcs-v9
| Commit SHA | File | What it is |
|---|---|---|
| `20916740` | `runtime/specs/dewy-receipt-schema-v1.json` | Machine-readable JSON Schema Draft 07. Full field coverage from orient-prd.md §3 L5. Source of truth for Receipt model. Prisma schema must conform. |
| `20916740` | `CLAUDE.md` (appended) | Handoff v0.2.0 section appended. v0.1.0 preserved verbatim above it. |
| `35d32da6` (prior) | `MEMORY.md` v0.1.0 | Initial memory log — baseline audit |
| `35d32da6` (prior) | `SKILL.md` v0.1.0 | Skill contract, priority queue, ROM primitives |
| `55009d62` (prior) | `CLAUDE.md` (appended) | Handoff v0.1.0 section appended |

### Post-handoff Claude Code commits (landed after our last push)
| Commit SHA | Date | What it does |
|---|---|---|
| [`a38d7f2`](https://github.com/flashesofbrilliance/arcs-v9/commit/a38d7f2acf29133732a2eae4a266eb8e06059631) | 2026-05-26 17:11 | Versioned output tree — `exports/{domain}/YYYY-MM-DD/` + `exports/receipts/` auto-write on `arcs_cli.py run`. `arcs_core.py` gains `versioned_out_dir(domain)` + `receipts_dir()` helpers. [NCI:75] |
| [`fa8c54d`](https://github.com/flashesofbrilliance/arcs-v9/commit/fa8c54df9d1676bfd27155dbc1adae916bba103a) | 2026-05-26 17:32 | `.gitignore` updated — `exports/` and local scan outputs excluded (personal data, not source) |

### Cross-repo dependency state
- `arcs-field-os/specs/orient-prd.md` is the governing authority for arcs-v9 Issues #2, #3, #4
- `arcs-v9/runtime/specs/dewy-receipt-schema-v1.json` is the source of truth for the Receipt Prisma model
- Any Prisma schema changes to `Receipt` must be validated against the JSON schema before commit
- `arcs-field-os` spec changes require a `MEMORY.md` entry in arcs-v9

### Open gaps (updated status)
```
runtime/specs/dewy-receipt-schema-v1.json   ✅ EXISTS — wire into Prisma (Issue #2 active)
runtime/specs/dewy-receipt-schema-v1.md     🔴 CREATE — human-readable companion (Issue #2)
runtime/specs/time-quality-attribution-rom.json  🔴 CREATE (Issue #3)
runtime/flows/question-compass-to-dewy.md   🔴 CREATE (Issue #4)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — after #3 (Issue #5)
arcs-field-os/specs/hold-reject-gate.md     🔴 NOT YET WRITTEN — HOLD/REJECT logic lives in orient-prd.md §2.2 for now
```

### Next move for next session
1. Read `CLAUDE.md` → Handoff v0.2.0 section (active pickup point)
2. Read `arcs-field-os/specs/orient-prd.md` before touching Issues #2–4
3. Start Issue #2: validate `prisma/schema.prisma` Receipt model against `runtime/specs/dewy-receipt-schema-v1.json`
4. Note: `exports/` directory now exists locally (gitignored) — do not recreate or commit scan output files

---

## [v0.1.0] 2026-05-26 — Perplexity ARCS session baseline

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: audit what landed post-timeout, create HOLD/REJECT validation layer, scaffold `arcs-field-os` spec structure, produce Claude Code handoff files

### What was confirmed landed (arcs-v9)
| Commit SHA | Date | Artifact |
|---|---|---|
| `471d57396` | 2026-04-09 | Day 1 scaffold — Next.js 16 + Prisma 7 + Auth.js v5 |
| `a61d492ed` | 2026-05-18 | DEWY pipeline, Y-gate, CLAUDE.md, WORLD.md |
| `752739d42` | 2026-05-18 | AGENTS.md — full agents/devops handbook |
| `62de74e1f` | 2026-05-25 | Forensic scan suite (network, archetype, apollo, forensic) |
| `0f082768b` | 2026-05-25 | `score_me.py` — single-contact forensic receipt CLI |
| `a3123963b` | 2026-05-25 | Vercel CI fix — postinstall `prisma generate` |
| `0f24bab70` | 2026-05-26 | Personal Intelligence Suite — 4 scanners + `arcs_core.py` [NCI:79] |
| `e66d4de99` | 2026-05-26 | `arcs_cli.py` — 5-verb decomposable pipeline + apex spine DEWY receipt [NCI:81] |

### Open sprint issues (arcs-v9)
- `#1` `[SPRINT]` ARCS v9 Canon Migration — P0 Backlog Sprint 1 (parent)
- `#2` `[SPEC]` DEWY Receipt Schema → `runtime/specs/dewy-receipt-schema-v1.md`
- `#3` `[SPEC]` Time Quality Attribution ROM → `runtime/specs/time-quality-attribution-rom.json`
- `#4` `[FLOW]` Question Compass → DEWY runtime wire-up → `runtime/flows/question-compass-to-dewy.md`
- `#5` `[CANON]` Book II narrative chapter: Time / Firmware / Modes → `canon/book-ii-time-firmware-modes.md`

### Files present at root
- `CLAUDE.md` (3.1KB) — project map, ROM primitives, L0–L5 stack
- `WORLD.md` (9.3KB) — physics spec
- `AGENTS.md` (5.8KB) — agents/devops handbook
- `.claude/` — directory present; contents not yet audited
- `scripts/` — all Python scan suite scripts
- `src/` — Next.js App Router
- `prisma/` — schema + migrations

### Gaps confirmed (not yet created)
- `runtime/specs/dewy-receipt-schema-v1.md` (Issue #2)
- `runtime/specs/time-quality-attribution-rom.json` (Issue #3)
- `runtime/flows/question-compass-to-dewy.md` (Issue #4)
- `canon/book-ii-time-firmware-modes.md` (Issue #5)
- `arcs-field-os` specs/, jtbd/, roadmap/ stubs

### Decisions made this session
- **Canonical home for design spec / PRD / impl plan:** `arcs-field-os` (not `arcs-v9`, not `arcs-hq`)
- **`arcs-v9`** owns: canon, runtime primitives, DEWY schema, Time ROM, scan suite, Claude Code app
- **`arcs-field-os`** owns: product surface specs, JTBD map, design system, roadmap cross-links
- **HOLD/REJECT gate logic** defined in this session; implementation plan pending
- Versioning policy: MEMORY.md entries append-only (never delete prior versions)

### Next move for Claude Code
1. Read `SKILL.md` for the contract of what you can operate on
2. Read `CLAUDE.md` → `WORLD.md` → `AGENTS.md` in that order
3. Start with Issue #2 (`[SPEC] DEWY Receipt Schema`) as the dependency unblock
4. Do not create `runtime/specs/` or `canon/` directories without first checking `WORLD.md` for naming conventions
